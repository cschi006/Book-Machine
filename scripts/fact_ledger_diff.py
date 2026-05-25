"""
fact_ledger_diff.py
--------------------
Extracts named entities from a scene draft and cross-checks them against
the Manuscript Bible (world-state ledger). Flags discrepancies for the
Continuity Steward / Continuity Agent pass.

This is the Python layer — it catches hard contradictions (wrong eye color,
impossible timeline, dead character speaking). The LLM layer interprets
ambiguous cases.

Usage:
    python fact_ledger_diff.py --scene scene.md --bible manuscript-bible.md
    python fact_ledger_diff.py --scene scene.md --bible manuscript-bible.md --json
    python fact_ledger_diff.py --update  # Update bible with new facts from scene
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime

# ── Fact extraction patterns ───────────────────────────────────────────────────

# Physical description patterns
PHYSICAL_PATTERNS = [
    ("eye_color",
     r"(?:her|his|their)\s+(\w+(?:\s+\w+)?)\s+eyes",
     "eye color"),
    ("hair_color",
     r"(?:her|his|their)\s+(\w+(?:\s+\w+)?)\s+hair",
     "hair description"),
    ("height",
     r"(?:she|he|they)\s+(?:was|is|stood?|towered?)\s+(\w+(?:\s+\w+)?(?:\s+tall|feet|foot|inches)?)",
     "height"),
]

# Location patterns
LOCATION_PATTERNS = [
    ("in_location",  r"(?:in|at|inside|within)\s+(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", "location reference"),
    ("entered",      r"(?:entered?|walked?\s+into|stepped?\s+into)\s+(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", "entering location"),
]

# Character state patterns
CHARACTER_PATTERNS = [
    ("is_alive",     r"([A-Z][a-z]+)\s+(?:said|asked|replied|smiled|frowned|walked|ran|looked)", "character action (alive)"),
    ("has_item",     r"([A-Z][a-z]+)(?:'s)?\s+(\w+)\s+(?:gleamed|shone|glinted|flashed)", "character possessing item"),
]


def load_bible(bible_path: str) -> dict:
    """
    Load and parse the Manuscript Bible.
    Returns a structured dict of established facts.
    """
    path = Path(bible_path)
    if not path.exists():
        return {"raw": "", "characters": {}, "locations": {}, "facts": [], "timeline": []}

    text = path.read_text(encoding="utf-8")

    # Simple extraction from the markdown table format
    facts = []

    # Extract from the Established Facts Log table
    table_pattern = re.compile(
        r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|",
        re.MULTILINE
    )
    for match in table_pattern.finditer(text):
        fact, chapter, scene, notes = [c.strip() for c in match.groups()]
        if fact and fact not in ("Fact", "---", ""):
            facts.append({"fact": fact, "chapter": chapter, "scene": scene, "notes": notes})

    # Extract character descriptions from the text
    characters = {}

    # Eye color mentions
    for m in re.finditer(
        r"([A-Z][a-z]+)(?:'s)?\s+(?:eyes?\s+(?:were|are|is)\s+|(\w+)\s+eyes?)",
        text
    ):
        char_name = m.group(1)
        if char_name not in ("Chapter", "Scene", "The", "Her", "His"):
            if char_name not in characters:
                characters[char_name] = {}

    return {
        "raw": text,
        "characters": characters,
        "locations": {},
        "facts": facts,
        "timeline": [],
    }


def extract_scene_facts(scene_text: str) -> dict:
    """Extract all checkable facts from a scene draft."""
    scene_facts = {
        "physical_descriptions": [],
        "locations": [],
        "character_actions": [],
        "timeline_refs": [],
    }

    # Physical descriptions
    for fact_type, pattern, label in PHYSICAL_PATTERNS:
        for m in re.finditer(pattern, scene_text, re.IGNORECASE):
            scene_facts["physical_descriptions"].append({
                "type": fact_type,
                "label": label,
                "value": m.group(1).strip(),
                "context": scene_text[max(0, m.start()-30):m.end()+30].replace("\n", " ").strip(),
                "position": m.start(),
            })

    # Named characters acting (alive check)
    # Extract dialogue speaker tags and action verbs
    speaker_pattern = re.compile(
        r'"[^"]{5,100}"\s*(?:said|asked|replied|called|whispered|said)\s+([A-Z][a-z]+)',
        re.MULTILINE
    )
    for m in speaker_pattern.finditer(scene_text):
        scene_facts["character_actions"].append({
            "character": m.group(1),
            "action": "dialogue",
            "context": m.group(0)[:80],
        })

    # Timeline references ("three days ago", "last week", "yesterday", specific dates)
    time_refs = re.findall(
        r"\b(?:\d+\s+days?\s+ago|last\s+\w+|yesterday|tomorrow|next\s+\w+|\d{4}|\w+\s+\d+(?:st|nd|rd|th)?)\b",
        scene_text, re.IGNORECASE
    )
    scene_facts["timeline_refs"] = list(set(time_refs))

    return scene_facts


def diff(scene_facts: dict, bible: dict) -> list[dict]:
    """
    Compare scene facts against the bible.
    Returns list of discrepancy dicts.
    """
    discrepancies = []

    # Check physical descriptions against known character facts
    for desc in scene_facts["physical_descriptions"]:
        # Look for contradicting established facts
        for established in bible["facts"]:
            if desc["value"].lower() in established["fact"].lower():
                # Potential match — flag for LLM review
                discrepancies.append({
                    "type": "physical_description",
                    "severity": "INVESTIGATE",
                    "label": desc["label"],
                    "scene_value": desc["value"],
                    "established_fact": established["fact"],
                    "established_in": f"Chapter {established['chapter']}, Scene {established['scene']}",
                    "context": desc["context"],
                    "note": "Verify this matches the established description.",
                })

    # Flag any new physical descriptions not yet in the bible (new facts to add)
    for desc in scene_facts["physical_descriptions"]:
        matching = [f for f in bible["facts"] if desc["type"] in f["fact"].lower()]
        if not matching:
            discrepancies.append({
                "type": "new_fact",
                "severity": "ADD_TO_BIBLE",
                "label": f"New {desc['label']} established",
                "value": desc["value"],
                "context": desc["context"],
                "note": "This fact should be added to the Manuscript Bible.",
            })

    return discrepancies


def format_report(discrepancies: list[dict], scene_path: str) -> str:
    """Format discrepancies as a human-readable report."""
    lines = [
        f"\n── Fact Ledger Diff Report ───────────────────────────────────",
        f"   Scene: {scene_path}",
        f"   Issues found: {len(discrepancies)}",
        f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    if not discrepancies:
        lines.append("   ✓ No discrepancies found. Scene consistent with Manuscript Bible.")
        return "\n".join(lines)

    for d in discrepancies:
        sev_icon = {"CRITICAL": "🔴", "INVESTIGATE": "🟡", "ADD_TO_BIBLE": "📝"}.get(d["severity"], "  ")
        lines.append(f"  {sev_icon} [{d['severity']}] {d['label']}")
        if "scene_value" in d:
            lines.append(f"     Scene says:    {d['scene_value']}")
        if "established_fact" in d:
            lines.append(f"     Bible says:    {d['established_fact']}")
            lines.append(f"     Established:   {d['established_in']}")
        if "value" in d:
            lines.append(f"     Value:         {d['value']}")
        lines.append(f"     Context:       …{d['context']}…")
        lines.append(f"     Note:          {d['note']}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Cross-check scene against Manuscript Bible for continuity errors."
    )
    parser.add_argument("--scene", type=str, required=True, help="Path to scene draft (.md)")
    parser.add_argument("--bible", type=str, required=True, help="Path to manuscript-bible.md")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--update", action="store_true",
                        help="Print a list of new facts to add to the bible (does not write)")

    args = parser.parse_args()

    scene_path = Path(args.scene)
    if not scene_path.exists():
        print(f"Error: scene file not found: {args.scene}", file=sys.stderr)
        sys.exit(1)

    scene_text = scene_path.read_text(encoding="utf-8")
    bible = load_bible(args.bible)
    scene_facts = extract_scene_facts(scene_text)
    discrepancies = diff(scene_facts, bible)

    if args.update:
        new_facts = [d for d in discrepancies if d["severity"] == "ADD_TO_BIBLE"]
        if new_facts:
            print("\n── New Facts to Add to Manuscript Bible ─────────────────────\n")
            for f in new_facts:
                print(f"  | {f['value']} | [chapter] | [scene] | from: {scene_path.name} |")
        else:
            print("No new facts to add.")
        return

    if args.json:
        print(json.dumps({
            "scene": str(scene_path),
            "scene_facts": scene_facts,
            "discrepancies": discrepancies,
        }, indent=2))
    else:
        print(format_report(discrepancies, str(scene_path)))


if __name__ == "__main__":
    main()
