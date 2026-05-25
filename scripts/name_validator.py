"""
name_validator.py
-----------------
Checks character names against a blocklist of statistically common AI-generated
names and suggests replacements drawn from period/genre-appropriate pools.

Usage:
    python name_validator.py --names "Marcus Chen, Elena Vasquez, Liam Carter"
    python name_validator.py --file path/to/character-list.txt
    python name_validator.py --interactive
"""

import argparse
import json
import random
import re
import sys

# ── Blocklist ─────────────────────────────────────────────────────────────────
# Names that cluster heavily in AI-generated fiction. Extend this list freely.

AI_CLUSTER_FIRST = {
    # Male
    "marcus", "liam", "ethan", "noah", "aiden", "lucas", "mason", "elijah",
    "oliver", "james", "sebastian", "alexander", "xavier", "nathaniel", "dominic",
    "callum", "declan", "finn", "ryder", "jaxon", "zane", "cole",
    # Female
    "elena", "emma", "sophia", "isabella", "luna", "aria", "aurora", "violet",
    "scarlett", "evelyn", "lyra", "sera", "zara", "isla", "nora", "elara",
    "celeste", "seraphina", "vivienne", "arabella", "amelia",
    # Gender-neutral
    "alex", "riley", "morgan", "avery", "sage", "river", "quinn",
}

AI_CLUSTER_LAST = {
    "chen", "vasquez", "ashford", "whitfield", "carter", "hayes", "blackwood",
    "sterling", "winters", "cross", "stone", "wolfe", "graves", "price",
    "shaw", "brooks", "wells", "ford", "hunt", "pierce", "drake", "voss",
    "mercer", "knight", "dalton", "sinclair", "montgomery", "harrington",
}

# ── Replacement pools by era/genre ────────────────────────────────────────────

REPLACEMENT_POOLS = {
    "regency_female": [
        "Cecily", "Harriet", "Prudence", "Thomasine", "Patience", "Mercy",
        "Cordelia", "Lavinia", "Euphemia", "Constance", "Philippa", "Dorothea",
        "Georgiana", "Millicent", "Rosalind", "Beatrix", "Winifred", "Tabitha",
    ],
    "regency_male": [
        "Tobias", "Crispin", "Alistair", "Barnaby", "Cornelius", "Edmund",
        "Godfrey", "Humphrey", "Jasper", "Peregrine", "Quentin", "Reginald",
        "Thaddeus", "Ulysses", "Valentine", "Aldous", "Bertram", "Clarence",
    ],
    "contemporary_female": [
        "Wren", "Blythe", "Calla", "Delaney", "Fern", "Hollis", "Juniper",
        "Kezia", "Lark", "Maeve", "Nell", "Odette", "Petra", "Rowan",
        "Sable", "Tilda", "Una", "Vesper", "Willa", "Zinnia",
    ],
    "contemporary_male": [
        "Bram", "Cade", "Dex", "Ewan", "Fox", "Grier", "Hal", "Idris",
        "Joss", "Kit", "Leif", "Mack", "Niall", "Orion", "Penn",
        "Reef", "Sawyer", "Tal", "Urie", "Ward",
    ],
    "fantasy_female": [
        "Thessaly", "Bryndis", "Calanthe", "Daeriel", "Eswyn", "Farolyn",
        "Galawen", "Herath", "Ildara", "Jendara", "Kaelith", "Lorwyn",
        "Maevis", "Nyxara", "Odalys", "Pelara", "Quivara", "Riven",
    ],
    "fantasy_male": [
        "Aldric", "Breccan", "Caius", "Dorian", "Edren", "Farran",
        "Gavric", "Halvard", "Invar", "Jorik", "Kestrel", "Lorcan",
        "Malachar", "Neven", "Osian", "Pryce", "Quillan", "Ravin",
    ],
    "last_names_period": [
        "Aldgate", "Bracewell", "Cavendish", "Dunmore", "Elsworth", "Fairfax",
        "Galworthy", "Hartwell", "Ilsley", "Jernigan", "Kincaid", "Lockwood",
        "Mabry", "Northcott", "Overbury", "Padgett", "Quinby", "Radcliff",
        "Salcombe", "Treadwell", "Underhill", "Verney", "Wrotham", "Yardley",
    ],
    "last_names_contemporary": [
        "Aldred", "Bexley", "Corvin", "Dunbar", "Elgin", "Farrow",
        "Grady", "Halsey", "Inwood", "Jurgens", "Kelso", "Lanford",
        "Mabry", "Nolan", "Oakes", "Paget", "Quinlan", "Reston",
        "Strand", "Tilbury", "Vesper", "Wray", "Yates", "Zorn",
    ],
}


# ── Core functions ─────────────────────────────────────────────────────────────

def parse_names(raw: str) -> list[tuple[str, str]]:
    """Parse 'First Last' strings into (first, last) tuples."""
    names = []
    for entry in re.split(r"[,\n]+", raw):
        parts = entry.strip().split()
        if len(parts) == 1:
            names.append((parts[0], ""))
        elif len(parts) >= 2:
            names.append((parts[0], " ".join(parts[1:])))
    return [(f, l) for f, l in names if f]


def check_name(first: str, last: str) -> dict:
    """
    Returns a dict with:
      - flagged: bool
      - first_flagged: bool
      - last_flagged: bool
      - reason: str
      - suggestions: list of replacement strings
    """
    first_lower = first.lower()
    last_lower = last.lower()

    first_hit = first_lower in AI_CLUSTER_FIRST
    last_hit = last_lower in AI_CLUSTER_LAST
    flagged = first_hit or last_hit

    reasons = []
    if first_hit:
        reasons.append(f"'{first}' is a high-frequency AI first name")
    if last_hit:
        reasons.append(f"'{last}' is a high-frequency AI last name")

    suggestions = []
    if flagged:
        # Offer 3 replacement combos from contemporary pool by default
        pool_first = REPLACEMENT_POOLS["contemporary_female"] + REPLACEMENT_POOLS["contemporary_male"]
        pool_last = REPLACEMENT_POOLS["last_names_contemporary"]
        for _ in range(3):
            suggestions.append(f"{random.choice(pool_first)} {random.choice(pool_last)}")

    return {
        "original": f"{first} {last}".strip(),
        "flagged": flagged,
        "first_flagged": first_hit,
        "last_flagged": last_hit,
        "reason": " + ".join(reasons) if reasons else "OK",
        "suggestions": suggestions,
    }


def validate_names(raw_input: str, output_format: str = "text") -> list[dict]:
    """Main entry point. Returns list of result dicts."""
    pairs = parse_names(raw_input)
    results = [check_name(first, last) for first, last in pairs]

    if output_format == "json":
        print(json.dumps(results, indent=2))
    else:
        print("\n── Name Validation Report ─────────────────────────────────\n")
        for r in results:
            status = "⚠  FLAGGED" if r["flagged"] else "✓  OK"
            print(f"  {status}  {r['original']}")
            if r["flagged"]:
                print(f"           Reason: {r['reason']}")
                print(f"           Suggestions: {', '.join(r['suggestions'])}")
            print()

    return results


def get_replacement(genre: str = "contemporary") -> str:
    """Quick helper: get one random replacement name for a given genre."""
    if "regency" in genre.lower():
        first_pool = REPLACEMENT_POOLS["regency_female"] + REPLACEMENT_POOLS["regency_male"]
        last_pool = REPLACEMENT_POOLS["last_names_period"]
    elif "fantasy" in genre.lower():
        first_pool = REPLACEMENT_POOLS["fantasy_female"] + REPLACEMENT_POOLS["fantasy_male"]
        last_pool = REPLACEMENT_POOLS["last_names_period"]
    else:
        first_pool = REPLACEMENT_POOLS["contemporary_female"] + REPLACEMENT_POOLS["contemporary_male"]
        last_pool = REPLACEMENT_POOLS["last_names_contemporary"]

    return f"{random.choice(first_pool)} {random.choice(last_pool)}"


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Validate character names against AI-cluster blocklist.")
    parser.add_argument("--names", type=str, help="Comma-separated list of names to check")
    parser.add_argument("--file", type=str, help="Path to file with one name per line")
    parser.add_argument("--genre", type=str, default="contemporary",
                        help="Genre for replacements: contemporary, regency, fantasy")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    if args.interactive:
        print("Name Validator — interactive mode. Enter names one at a time, blank line to quit.\n")
        while True:
            entry = input("Name: ").strip()
            if not entry:
                break
            validate_names(entry)
        return

    if args.file:
        with open(args.file, "r") as f:
            raw = f.read()
    elif args.names:
        raw = args.names
    else:
        parser.print_help()
        sys.exit(1)

    validate_names(raw, output_format="json" if args.json else "text")


if __name__ == "__main__":
    main()
