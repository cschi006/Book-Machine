"""
word_injector.py
----------------
Generates a set of random seed words for the Driver before a scene draft.
These words are NOT requirements — they are flavoring agents. The Driver
may pull from them, ignore them, or let them spark something unexpected.

The goal is to break AI's pull toward statistically probable next moves.

Usage:
    python word_injector.py                          # 10 random words, mixed corpus
    python word_injector.py --count 12 --genre dark  # 12 words, dark/gothic corpus
    python word_injector.py --scene "tavern fight"   # scene-contextual injection
    python word_injector.py --json                   # output as JSON for agent consumption
"""

import argparse
import json
import random
import sys

# ── Word corpora ───────────────────────────────────────────────────────────────
# Organized by register. Each corpus is curated to be evocative, specific,
# and resistant to AI's tendency toward the generic.

CORPORA = {
    "sensory": [
        "tallow", "brine", "creosote", "lanolin", "turpentine", "camphor",
        "char", "vetiver", "petrichor", "cordite", "mildew", "tallow",
        "resin", "lye", "foxglove", "wormwood", "cloves", "vinegar",
        "woodsmoke", "rust", "marrow", "chalk", "pepper", "anise",
        "iron", "salt", "pine", "clay", "ash", "copper",
    ],
    "texture": [
        "pilled", "slubbed", "granular", "puckered", "scored", "laminate",
        "skeined", "whorled", "furred", "calloused", "felted", "grained",
        "craquelure", "stippled", "pellucid", "tessellated", "honeycombed",
        "ribbed", "napped", "burnished", "matte", "waxy", "crazed", "porous",
    ],
    "motion": [
        "lurch", "skitter", "judder", "cant", "list", "yaw", "scull",
        "spool", "unspool", "ratchet", "cinch", "parse", "furl", "tack",
        "feint", "slew", "coruscate", "oscillate", "eddy", "precess",
        "falter", "arrest", "founder", "lapse", "pitch", "reef",
    ],
    "emotional_specific": [
        "saudade", "hiraeth", "schadenfreude", "liget", "torschlusspanik",
        "mamihlapinatapai", "forelsket", "jayus", "aware", "mono no aware",
        "wabi-sabi", "sehnsucht", "fernweh", "retrouvailles", "vellichor",
        "kenopsia", "onism", "ellipsism", "occhiolism", "rubatosis",
    ],
    "architecture": [
        "lancet", "corbel", "soffit", "clerestory", "quoin", "dentil",
        "rustication", "plinth", "baluster", "finial", "spandrel",
        "transom", "fanlight", "pilaster", "entablature", "pediment",
        "coping", "oriel", "sill", "reveal", "jamb", "lintel",
    ],
    "weather": [
        "virga", "haboob", "foehn", "williwaw", "graupel", "rime",
        "scud", "wrack", "mare's tail", "mackerel sky", "haar",
        "mizzle", "smirr", "drisk", "spume", "spindrift", "squall",
        "frostwork", "hoarfrost", "glaze", "black ice", "pea soup",
    ],
    "body": [
        "sternum", "philtrum", "clavicle", "nape", "hollow", "socket",
        "tendon", "knuckle", "rib", "jaw", "temple", "lobe", "gum",
        "cuticle", "shin", "instep", "heel", "crook", "wrist", "thumb",
    ],
    "light": [
        "penumbra", "umbra", "crepuscular", "aureole", "chiaroscuro",
        "luminal", "phosphene", "cinereous", "ashen", "nacre", "verdigris",
        "patina", "bloom", "corona", "halo", "aureate", "livid", "wan",
        "lambent", "incandescent", "phosphorescent", "iridescent",
    ],
    "dark_gothic": [
        "ossuary", "charnel", "catafalque", "caul", "winding sheet",
        "lich", "wraith", "revenant", "fetch", "barrow", "cairn",
        "gallows", "gibbet", "pyre", "cinder", "hollow", "sere",
        "wither", "blight", "mordant", "acrid", "necrotic",
    ],
    "romance": [
        "threshold", "gravity", "orbit", "current", "undertow",
        "tether", "tension", "charge", "resistance", "yield",
        "breach", "surrender", "forfeit", "concede", "dissolve",
        "unbind", "unravel", "cleave", "anchor", "harbor",
    ],
    "mundane_specific": [
        "stapler", "grout", "coaster", "receipt", "hinge", "gasket",
        "cotter pin", "toggle", "bobbin", "shuttle", "tack", "brad",
        "ferrule", "grommet", "rivet", "shim", "bushing", "cleat",
        "bung", "spigot", "flange", "collar", "fitting", "lug",
    ],
}

GENRE_PRESETS = {
    "romance": ["sensory", "texture", "body", "light", "romance"],
    "dark": ["dark_gothic", "weather", "light", "motion", "emotional_specific"],
    "fantasy": ["architecture", "weather", "motion", "emotional_specific", "sensory"],
    "contemporary": ["sensory", "body", "motion", "mundane_specific", "emotional_specific"],
    "default": ["sensory", "texture", "motion", "body", "weather", "light"],
}


def inject(count: int = 10, genre: str = "default", scene_context: str = "") -> list[str]:
    """
    Generate `count` seed words.
    If scene_context is provided, skew toward contextually relevant corpora.
    """
    preset = GENRE_PRESETS.get(genre.lower(), GENRE_PRESETS["default"])

    # Build weighted pool: words from preset corpora weighted 3x vs. all others
    pool = []
    for corpus_name, words in CORPORA.items():
        weight = 3 if corpus_name in preset else 1
        pool.extend(words * weight)

    # Simple scene context skewing
    if scene_context:
        ctx = scene_context.lower()
        if any(w in ctx for w in ["fight", "battle", "violence", "chase"]):
            pool.extend(CORPORA["motion"] * 4)
        if any(w in ctx for w in ["kiss", "touch", "intimate", "close"]):
            pool.extend(CORPORA["body"] * 4 + CORPORA["romance"] * 4)
        if any(w in ctx for w in ["night", "dark", "shadow", "fear"]):
            pool.extend(CORPORA["dark_gothic"] * 3 + CORPORA["light"] * 2)

    selected = random.sample(pool, min(count, len(set(pool))))
    # Deduplicate while preserving randomness
    seen = set()
    result = []
    for w in selected:
        if w not in seen:
            seen.add(w)
            result.append(w)
        if len(result) == count:
            break

    return result


def format_for_agent(words: list[str], scene_context: str = "") -> str:
    """Format seed words as a prompt injection block for the Driver agent."""
    lines = [
        "── WORD INJECTION ──────────────────────────────────────────────",
        "The following words are available as you draft this scene.",
        "You are not required to use them. They are not instructions.",
        "They are here to flavor, surprise, and interrupt the expected.",
        "Pull from them if something sparks. Ignore them if nothing does.",
        "",
    ]
    if scene_context:
        lines.append(f"Scene context: {scene_context}")
        lines.append("")

    lines.append("  " + "  ·  ".join(words))
    lines.append("")
    lines.append("────────────────────────────────────────────────────────────")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate seed words for Driver scene drafts.")
    parser.add_argument("--count", type=int, default=10, help="Number of words (default: 10)")
    parser.add_argument("--genre", type=str, default="default",
                        help="Genre preset: romance, dark, fantasy, contemporary, default")
    parser.add_argument("--scene", type=str, default="", help="Brief scene description for context skewing")
    parser.add_argument("--json", action="store_true", help="Output as JSON list")
    parser.add_argument("--agent", action="store_true", help="Format as agent prompt injection block")

    args = parser.parse_args()

    words = inject(count=args.count, genre=args.genre, scene_context=args.scene)

    if args.json:
        print(json.dumps({"words": words, "count": len(words), "genre": args.genre}))
    elif args.agent:
        print(format_for_agent(words, scene_context=args.scene))
    else:
        print("\n── Word Injection ──────────────────────────────────────────\n")
        print("  " + "  ·  ".join(words))
        print(f"\n  {len(words)} words · genre: {args.genre}")
        if args.scene:
            print(f"  scene context: {args.scene}")
        print()


if __name__ == "__main__":
    main()
