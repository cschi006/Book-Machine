"""
pattern_detector.py
--------------------
Scans a manuscript for overused sentence constructions, word frequency
anomalies, and repeated physical beats. Produces a report for the
Crutch Inspector / Pattern & Repetition pass in Parc Fermé.

The Python layer detects and counts. The LLM layer judges whether
each instance is overuse or intentional craft. This script is the
Python layer.

Usage:
    python pattern_detector.py --file manuscript.md
    python pattern_detector.py --file manuscript.md --threshold 3
    python pattern_detector.py --file manuscript.md --json
    python pattern_detector.py --file manuscript.md --chapter "Chapter 1"
"""

import argparse
import collections
import json
import re
import sys
from pathlib import Path

# ── Pattern definitions ───────────────────────────────────────────────────────

CONSTRUCTION_PATTERNS = [
    # "It wasn't X, it was Y" / "It wasn't X — it was Y"
    ("not_but",         r"\bit wasn't\b.{3,60}(?:,|—)\s*it was\b",          "It wasn't X, it was Y"),
    ("not_but_2",       r"\b(?:wasn't|isn't|aren't|weren't)\b.{3,40}\bbut\b", "wasn't/isn't X but Y"),
    ("not_x_but_y",     r"\bnot\s+\w+(?:\s+\w+)?\s+but\b",                  "not X but Y"),
    # "Despite X, Y"
    ("despite",         r"\bDespite\b.{3,60},",                              "Despite X, Y (sentence opener)"),
    # "As if X"
    ("as_if",           r"\bas if\b",                                         "as if"),
    # "She/He found herself/himself"
    ("found_self",      r"\b(?:she|he|they)\s+found\s+(?:herself|himself|themselves)\b", "found herself/himself"),
    # "Something in X" constructions
    ("something_in",    r"\bsomething\s+in\s+(?:his|her|their|the)\b",       "something in his/her"),
    # "She/He couldn't help but"
    ("couldnt_help",    r"\bcouldn't help but\b",                            "couldn't help but"),
    # "A part of her/him"
    ("part_of",         r"\ba part of (?:her|him|them)\b",                   "a part of her/him"),
    # "Her/His heart" constructions
    ("heart_verb",      r"\b(?:her|his|their)\s+heart\s+\w+ed\b",            "her/his heart [verbed]"),
    # "She/He realized"
    ("realized",        r"\b(?:she|he|they)\s+realized\b",                   "she/he realized (filter word)"),
    # "She/He noticed"
    ("noticed",         r"\b(?:she|he|they)\s+noticed\b",                    "she/he noticed (filter word)"),
    # "She/He felt"
    ("felt_filter",     r"\b(?:she|he|they)\s+felt\s+(?:a|the|her|his)\b",   "she/he felt [a/the] (filter word)"),
    # "The air" + verb constructions
    ("the_air",         r"\bthe air\s+\w+ed\b",                              "the air [verbed]"),
    # Breath-catching
    ("breath",          r"\b(?:caught|held|lost)\s+(?:her|his|their)\s+breath\b", "caught/held her breath"),
    # "Warmth" as emotion delivery
    ("warmth_spread",   r"\bwarmth\s+(?:spread|bloomed|pooled|curled)\b",    "warmth spread/bloomed/pooled"),
]

# Physical beats that should be rare
PHYSICAL_BEATS = [
    ("hand_hair",   r"\b(?:ran?|raked?|dragged?|shoved?|pushed?)\s+(?:a\s+)?(?:her|his|their|a)\s+hand(?:s)?\s+through\s+(?:her|his|their)\s+hair\b", "ran hand through hair"),
    ("look_mirror", r"\b(?:looked?|glanced?|stared?|caught\s+(?:her|his|their)\s+reflection)\s+in(?:to)?\s+(?:the|a)\s+mirror\b", "looked in mirror"),
    ("jaw_clench",  r"\b(?:jaw|teeth|fist|hands?)\s+(?:clenched?|tightened?|flexed?)\b", "jaw/fist clenched"),
    ("eyes_close",  r"\b(?:closed?|shut|squeezed?)\s+(?:her|his|their)\s+eyes\b", "closed/shut eyes"),
    ("step_back",   r"\btook?\s+a\s+step\s+back\b",                         "took a step back"),
    ("swallow",     r"\b(?:swallowed?)\s+(?:hard|thickly|around\s+(?:the|a)\s+lump)\b", "swallowed hard"),
    ("look_away",   r"\b(?:looked?|glanced?|turned?)\s+away\b",             "looked/turned away"),
]

# Sentence opener tracking
OPENER_WORDS_TO_TRACK = [
    "she", "he", "they", "the", "a", "an", "i", "it", "but", "and",
    "her", "his", "their", "there", "here",
]


# ── Analysis functions ─────────────────────────────────────────────────────────

def split_into_chapters(text: str) -> dict[str, str]:
    """Split manuscript into chapters. Returns {chapter_title: text}."""
    chapters = {}
    pattern = re.compile(r"^(#+\s*Chapter\s*\d+[^\n]*|^Chapter\s+\d+[^\n]*)", re.MULTILINE | re.IGNORECASE)
    splits = pattern.split(text)

    if len(splits) <= 1:
        return {"full_manuscript": text}

    # First chunk before any chapter heading
    if splits[0].strip():
        chapters["preamble"] = splits[0]

    for i in range(1, len(splits), 2):
        title = splits[i].strip() if i < len(splits) else f"Chapter {i // 2}"
        content = splits[i + 1] if (i + 1) < len(splits) else ""
        chapters[title] = content

    return chapters


def detect_constructions(text: str) -> list[dict]:
    """Find all construction pattern matches in text."""
    results = []
    for pattern_id, pattern, label in CONSTRUCTION_PATTERNS:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            results.append({
                "pattern_id": pattern_id,
                "label": label,
                "count": len(matches),
                "instances": [
                    {
                        "context": text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ").strip(),
                        "position": m.start(),
                    }
                    for m in matches[:5]  # Cap at 5 examples per pattern
                ],
            })
    return results


def detect_physical_beats(text: str) -> list[dict]:
    """Find repeated physical beats."""
    results = []
    for beat_id, pattern, label in PHYSICAL_BEATS:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            results.append({
                "beat_id": beat_id,
                "label": label,
                "count": len(matches),
                "instances": [
                    text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ").strip()
                    for m in matches[:5]
                ],
            })
    return results


def word_frequency(text: str, top_n: int = 30) -> list[tuple[str, int]]:
    """Return top N most-frequent content words (excluding stopwords)."""
    STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "up", "about", "into", "through", "after",
        "is", "was", "are", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "will", "would", "could", "should", "may", "might",
        "she", "he", "they", "it", "i", "we", "you", "her", "his", "their", "its",
        "this", "that", "these", "those", "what", "which", "who", "not", "no",
        "so", "as", "if", "when", "then", "than", "just", "out", "all", "more",
        "there", "here", "had", "him", "them", "my", "your", "our", "its",
    }
    words = re.findall(r"\b[a-z]{4,}\b", text.lower())
    counts = collections.Counter(w for w in words if w not in STOPWORDS)
    return counts.most_common(top_n)


def sentence_opener_analysis(text: str) -> dict:
    """Analyze sentence-opening word variety."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    openers = []
    for s in sentences:
        first_word = re.match(r"[A-Za-z]+", s.strip())
        if first_word:
            openers.append(first_word.group(0).lower())

    opener_counts = collections.Counter(openers)
    total = len(openers)
    return {
        "total_sentences": total,
        "top_openers": [
            {"word": w, "count": c, "pct": round(100 * c / total, 1) if total else 0}
            for w, c in opener_counts.most_common(15)
            if w in OPENER_WORDS_TO_TRACK
        ],
    }


def severity_rating(count: int, threshold: int) -> str:
    """Assign severity based on count vs. threshold."""
    if count > threshold * 2:
        return "CRITICAL"
    elif count > threshold:
        return "NOTABLE"
    else:
        return "WATCH"


def analyze(text: str, threshold: int = 3, chapter_filter: str = "") -> dict:
    """Full analysis. Returns structured report dict."""
    if chapter_filter:
        chapters = split_into_chapters(text)
        scope_text = next(
            (v for k, v in chapters.items() if chapter_filter.lower() in k.lower()),
            text
        )
        scope_label = chapter_filter
    else:
        scope_text = text
        scope_label = "full manuscript"

    constructions = detect_constructions(scope_text)
    beats = detect_physical_beats(scope_text)
    freq = word_frequency(scope_text)
    openers = sentence_opener_analysis(scope_text)

    # Apply severity ratings
    for c in constructions:
        c["severity"] = severity_rating(c["count"], threshold)
    for b in beats:
        b["severity"] = severity_rating(b["count"], threshold)

    return {
        "scope": scope_label,
        "word_count": len(scope_text.split()),
        "threshold": threshold,
        "construction_patterns": sorted(constructions, key=lambda x: x["count"], reverse=True),
        "physical_beats": sorted(beats, key=lambda x: x["count"], reverse=True),
        "word_frequency_top30": [{"word": w, "count": c} for w, c in freq],
        "sentence_openers": openers,
        "summary": {
            "critical": sum(1 for c in constructions + beats if c.get("severity") == "CRITICAL"),
            "notable": sum(1 for c in constructions + beats if c.get("severity") == "NOTABLE"),
            "watch": sum(1 for c in constructions + beats if c.get("severity") == "WATCH"),
        },
    }


def print_report(report: dict) -> None:
    """Print human-readable report."""
    print(f"\n── Pattern Detector Report ─────────────────────────────────")
    print(f"   Scope: {report['scope']}  |  Words: {report['word_count']:,}  |  Threshold: {report['threshold']}/instance")
    print(f"   Critical: {report['summary']['critical']}  |  Notable: {report['summary']['notable']}  |  Watch: {report['summary']['watch']}\n")

    if report["construction_patterns"]:
        print("── Construction Patterns ─────────────────────────────────────")
        for p in report["construction_patterns"]:
            if p["count"] > 0:
                sev = {"CRITICAL": "🔴", "NOTABLE": "🟡", "WATCH": "🔵"}.get(p["severity"], "  ")
                print(f"  {sev} {p['label']:50s} × {p['count']}  [{p['severity']}]")
                if p["count"] > 1:
                    print(f"     e.g. …{p['instances'][0]['context']}…")
        print()

    if report["physical_beats"]:
        print("── Physical Beats ────────────────────────────────────────────")
        for b in report["physical_beats"]:
            sev = {"CRITICAL": "🔴", "NOTABLE": "🟡", "WATCH": "🔵"}.get(b["severity"], "  ")
            print(f"  {sev} {b['label']:50s} × {b['count']}  [{b['severity']}]")
        print()

    if report["sentence_openers"]["top_openers"]:
        print("── Sentence Openers (tracked words) ─────────────────────────")
        for o in report["sentence_openers"]["top_openers"][:8]:
            bar = "█" * min(int(o["pct"] / 2), 20)
            print(f"  {o['word']:12s}  {bar:20s}  {o['count']}x  ({o['pct']}%)")
        print()


def main():
    parser = argparse.ArgumentParser(description="Detect crutch patterns in fiction manuscripts.")
    parser.add_argument("--file", type=str, required=True, help="Path to manuscript (.md or .txt)")
    parser.add_argument("--threshold", type=int, default=3,
                        help="Count above which a pattern is flagged (default: 3)")
    parser.add_argument("--chapter", type=str, default="", help="Limit analysis to one chapter")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    report = analyze(text, threshold=args.threshold, chapter_filter=args.chapter)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)


if __name__ == "__main__":
    main()
