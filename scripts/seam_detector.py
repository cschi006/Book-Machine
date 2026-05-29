"""
seam_detector.py
----------------
The Booth's "scene-seam" gate. Examines the joints between scenes/movements —
how one section closes and the next opens — and flags mechanical seam problems
so chapters actually mesh instead of just sitting next to each other.

Deterministic and explainable. It catches the countable seam signals:
  * cliche time-transition openings ("The next morning...", "Later...")
  * the SAME opening construction repeated across many seams (monotony)
  * closings that fall flat (ending on a dialogue tag)
  * "echo" seams (the close and the next open restate the same beat)

The Concertmaster/Booth judges the rest (does it open/close on the right beat).

Usage:
    python seam_detector.py --file manuscript.md
    python seam_detector.py --file manuscript.md --json
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

# Openings that lean on a time-jump cliche.
TIME_CLICHES = [
    r"^the next (morning|day|night|evening|week)",
    r"^(later|hours later|moments later|minutes later|days later)\b",
    r"^that (night|morning|evening|afternoon)\b",
    r"^the following (morning|day|night|week)",
    r"^by the time\b",
    r"^when (i|she|he|they) (woke|opened)",
    r"^(it was|it had been) \w+ (later|before)",
    r"^(afterward|afterwards)\b",
]

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "is", "was", "were", "be", "she", "he", "they", "it",
    "her", "his", "their", "this", "that", "i", "you", "we", "had", "have",
}


def split_sections(text):
    """Split on scene-break markers and chapter/scene headers."""
    lines = text.splitlines()
    sections = []
    current = []
    for line in lines:
        s = line.strip()
        is_break = bool(re.fullmatch(r"[\*\-_\s]{3,}", s)) or s.startswith("#") \
            or bool(re.match(r"(?i)^(chapter|scene)\s+\d+", s))
        if is_break:
            if current:
                sections.append("\n".join(current).strip())
                current = []
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current).strip())
    return [s for s in sections if s]


def first_sentence(section):
    blob = " ".join(l.strip() for l in section.splitlines() if l.strip())
    parts = re.split(r"(?<=[.!?])\s+", blob)
    return parts[0].strip() if parts else ""


def last_sentence(section):
    blob = " ".join(l.strip() for l in section.splitlines() if l.strip())
    parts = re.split(r"(?<=[.!?])\s+", blob)
    return parts[-1].strip() if parts else ""


def content_words(s):
    return set(w for w in re.findall(r"[a-z']{3,}", s.lower()) if w not in STOPWORDS)


def opener_signature(sentence):
    """First two words, lowercased — used to spot repeated opening constructions."""
    words = re.findall(r"[A-Za-z']+", sentence)
    return " ".join(w.lower() for w in words[:2]) if words else ""


def excerpt(s, n=70):
    s = s.strip()
    return (s[:n] + "...") if len(s) > n else s


def analyze(text):
    sections = split_sections(text)
    seams = []
    opener_sigs = {}

    for i in range(len(sections)):
        opener = first_sentence(sections[i])
        sig = opener_signature(opener)
        if sig:
            opener_sigs.setdefault(sig, []).append(i + 1)

    for i in range(len(sections) - 1):
        close = last_sentence(sections[i])
        open_next = first_sentence(sections[i + 1])
        flags = []

        # Cliche time-transition opening
        for pat in TIME_CLICHES:
            if re.search(pat, open_next.strip(), re.IGNORECASE):
                flags.append("cliche-time-open")
                break

        # Flat close: ends on a dialogue tag
        if re.search(r'(?i)("|”)?\s*(he|she|they|[A-Z][a-z]+)\s+(said|asked|replied|murmured|whispered)\s*\.?$', close):
            flags.append("close-on-dialogue-tag")

        # Echo seam: close and next open restate the same beat
        cw_close = content_words(close)
        cw_open = content_words(open_next)
        shared = cw_close & cw_open
        if len(shared) >= 3:
            flags.append("echo-seam:{%s}" % ", ".join(sorted(shared)))

        if flags:
            seams.append({
                "seam": "section %d -> %d" % (i + 1, i + 2),
                "close": excerpt(close),
                "open": excerpt(open_next),
                "flags": flags,
            })

    repeated_openers = {sig: locs for sig, locs in opener_sigs.items()
                        if len(locs) >= 3 and sig.strip()}

    return {
        "section_count": len(sections),
        "seam_count": max(len(sections) - 1, 0),
        "seam_flags": seams,
        "repeated_opening_constructions": repeated_openers,
        "summary": {
            "flagged_seams": len(seams),
            "repeated_opener_patterns": len(repeated_openers),
        },
    }


def print_report(r):
    print("\n== Scene-Seam Report ==")
    print("   Sections: %d  |  Seams: %d  |  Flagged seams: %d  |  Repeated openers: %d\n"
          % (r["section_count"], r["seam_count"], r["summary"]["flagged_seams"],
             r["summary"]["repeated_opener_patterns"]))

    if r["seam_flags"]:
        print("-- Seam problems --")
        for s in r["seam_flags"]:
            print("  %s  [%s]" % (s["seam"], ", ".join(s["flags"])))
            print("     close: > %s" % s["close"])
            print("     open : > %s" % s["open"])
        print()

    if r["repeated_opening_constructions"]:
        print("-- Repeated opening constructions (monotony across seams) --")
        for sig, locs in sorted(r["repeated_opening_constructions"].items(),
                                key=lambda kv: -len(kv[1])):
            print("  \"%s...\" opens sections %s (%dx)" % (sig, locs, len(locs)))
        print()

    if not r["seam_flags"] and not r["repeated_opening_constructions"]:
        print("  Clean: seams mesh, openings varied.\n")


def main():
    ap = argparse.ArgumentParser(description="Detect scene-seam problems in a manuscript.")
    ap.add_argument("--file", required=True, help="Path to manuscript (.md or .txt)")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.exists():
        print("Error: file not found: %s" % args.file, file=sys.stderr)
        sys.exit(1)

    report = analyze(path.read_text(encoding="utf-8"))
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)


if __name__ == "__main__":
    main()
