"""
redundancy_detector.py
----------------------
The Booth's "sentence-weight" gate. Flags FUNCTIONAL REDUNDANCY: two or three
nearby sentences doing the same job — a duplicated plot point, description, or
sensory/emotional beat — including via synonyms (semantic redundancy).

Deterministic and explainable: it points at the specific sentences and names
exactly what they share (overlapping content words, or a shared concept).
The Python layer finds candidates; the Concertmaster/Booth judges whether each
is genuine overwriting or intentional, earned emphasis.

Usage:
    python redundancy_detector.py --file chapter.md
    python redundancy_detector.py --file chapter.md --window 3
    python redundancy_detector.py --file chapter.md --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "up", "about", "into", "through", "after", "over",
    "is", "was", "are", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "she", "he", "they", "it", "we", "you", "her", "his", "their", "its",
    "this", "that", "these", "those", "what", "which", "who", "not", "no",
    "so", "as", "if", "when", "then", "than", "just", "out", "all", "more",
    "there", "here", "him", "them", "my", "your", "our", "me", "i", "one",
    "had", "back", "down", "off", "now", "like", "only", "even", "still",
    "again", "around", "been", "could", "would", "very", "much", "too",
}

# Concept clusters: synonyms that express the SAME beat. Two sentences hitting
# the same cluster in a small window = likely semantic redundancy.
CONCEPTS = {
    "heartbeat":  {"heart", "pulse", "pounded", "pounding", "raced", "racing",
                   "hammered", "hammering", "thudded", "thumped", "skipped",
                   "lurched", "stuttered", "slammed"},
    "warmth":     {"warmth", "heat", "warm", "hot", "flush", "flushed",
                   "burned", "burning", "heated", "scorched"},
    "cold-fear":  {"cold", "ice", "icy", "chill", "chilled", "dread", "fear",
                   "afraid", "terror", "panic", "froze", "frozen", "frozen"},
    "breath":     {"breath", "breathe", "breathed", "breathing", "exhale",
                   "exhaled", "inhale", "inhaled", "gasped", "panted", "lungs"},
    "tears":      {"tears", "tear", "cried", "crying", "weeping", "sobbed",
                   "wept", "weep"},
    "trembling":  {"trembled", "trembling", "shook", "shaking", "shiver",
                   "shivered", "quaked", "quivered"},
    "stillness":  {"silence", "silent", "quiet", "still", "stillness", "hush",
                   "hushed", "motionless"},
    "smile":      {"smile", "smiled", "smiling", "grin", "grinned", "smirk",
                   "smirked"},
    "gaze":       {"gaze", "stared", "staring", "watched", "watching",
                   "glanced", "glancing", "regarded"},
}


def split_sentences(text):
    # Strip markdown headers and scene-break markers so they don't count as prose.
    cleaned = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        if re.fullmatch(r"[\*\-_\s]{3,}", s):  # * * *, ---, ___ scene breaks
            continue
        cleaned.append(s)
    blob = " ".join(cleaned)
    parts = re.split(r"(?<=[.!?])\s+", blob)
    return [p.strip() for p in parts if len(p.strip()) > 0]


def content_words(sentence):
    words = re.findall(r"[a-z']{3,}", sentence.lower())
    return set(w for w in words if w not in STOPWORDS)


def concepts_in(sentence):
    cw = content_words(sentence)
    return {name for name, syns in CONCEPTS.items() if cw & syns}


def excerpt(sentence, n=70):
    s = sentence.strip()
    return (s[:n] + "...") if len(s) > n else s


def analyze(text, window=3):
    sents = split_sentences(text)
    cw = [content_words(s) for s in sents]
    cc = [concepts_in(s) for s in sents]

    lexical = []   # adjacent sentence pairs that overlap heavily
    semantic = []  # windows where 2+ sentences hit the same concept

    # 1) Lexical redundancy on adjacent pairs.
    for i in range(len(sents) - 1):
        shared = cw[i] & cw[i + 1]
        smaller = min(len(cw[i]), len(cw[i + 1])) or 1
        coef = len(shared) / smaller
        if len(shared) >= 2 and coef >= 0.5:
            lexical.append({
                "sentences": [i + 1, i + 2],  # 1-indexed for humans
                "shared_words": sorted(shared),
                "overlap": round(coef, 2),
                "excerpts": [excerpt(sents[i]), excerpt(sents[i + 1])],
                "severity": "NOTABLE" if coef >= 0.66 else "WATCH",
            })

    # 2) Semantic redundancy: same concept across a sliding window.
    seen = set()
    for i in range(len(sents)):
        win = range(i, min(i + window, len(sents)))
        concept_hits = {}
        for j in win:
            for c in cc[j]:
                concept_hits.setdefault(c, []).append(j)
        for c, idxs in concept_hits.items():
            if len(idxs) >= 2:
                key = (c, tuple(idxs))
                if key in seen:
                    continue
                seen.add(key)
                semantic.append({
                    "concept": c,
                    "sentences": [k + 1 for k in idxs],
                    "excerpts": [excerpt(sents[k]) for k in idxs],
                    "severity": "NOTABLE" if len(idxs) >= 3 else "WATCH",
                })

    return {
        "sentence_count": len(sents),
        "lexical_redundancy": lexical,
        "semantic_redundancy": semantic,
        "summary": {
            "lexical_flags": len(lexical),
            "semantic_flags": len(semantic),
        },
    }


def print_report(r):
    print("\n== Redundancy (sentence-weight) Report ==")
    print("   Sentences: %d  |  Lexical flags: %d  |  Semantic flags: %d\n"
          % (r["sentence_count"], r["summary"]["lexical_flags"],
             r["summary"]["semantic_flags"]))

    if r["lexical_redundancy"]:
        print("-- Lexical redundancy (adjacent sentences repeating content) --")
        for f in r["lexical_redundancy"]:
            print("  [%s] sentences %s share {%s} (overlap %.2f)"
                  % (f["severity"], f["sentences"], ", ".join(f["shared_words"]),
                     f["overlap"]))
            for ex in f["excerpts"]:
                print("       > %s" % ex)
        print()

    if r["semantic_redundancy"]:
        print("-- Semantic redundancy (same beat via synonyms) --")
        for f in r["semantic_redundancy"]:
            print("  [%s] sentences %s all hit the '%s' beat"
                  % (f["severity"], f["sentences"], f["concept"]))
            for ex in f["excerpts"]:
                print("       > %s" % ex)
        print()

    if not r["lexical_redundancy"] and not r["semantic_redundancy"]:
        print("  Clean: no stacked sentences detected.\n")


def main():
    ap = argparse.ArgumentParser(description="Detect functional/semantic redundancy in prose.")
    ap.add_argument("--file", required=True, help="Path to manuscript (.md or .txt)")
    ap.add_argument("--window", type=int, default=3, help="Sentence window for semantic check (default 3)")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.exists():
        print("Error: file not found: %s" % args.file, file=sys.stderr)
        sys.exit(1)

    report = analyze(path.read_text(encoding="utf-8"), window=args.window)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)


if __name__ == "__main__":
    main()
