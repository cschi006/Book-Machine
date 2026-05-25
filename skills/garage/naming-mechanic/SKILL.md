# Naming Mechanic
**Sector:** Garage · **Status:** Stub — ready to build  
**Role:** Generates period/region/genre-appropriate character names with explicit AI-cluster filtering.

---

## Purpose

The Naming Mechanic exists because AI default names are identifiable. Marcus Chen. Elena Vasquez. Liam Carter. They cluster around statistically probable combinations that signal machine authorship. This skill breaks that pattern.

The Naming Mechanic runs after the Character Lead has produced character profiles, and before the Team Principal locks in any name for the manuscript. Names that pass become permanent — the "naming lock-in" is one of the four human ratification gates.

---

## When to Invoke

- After Character Lead produces character roster
- When a new character appears mid-race and needs a name quickly (Backstory Mechanic can call this)
- Whenever the author says "I need a name for [type of character]"

---

## Inputs

- Character profiles from Character Lead (role, gender presentation, era/region, social class)
- Book order genre and setting
- Any name constraints the author specified (e.g. "nothing that starts with R, already have too many")

---

## Process

1. **Run `scripts/name_validator.py`** on any names already proposed (from Author or Character Lead)
2. **Flag all AI-cluster hits** with reason and severity
3. **Generate alternatives** using the script's replacement pools, filtered by:
   - Era/region appropriateness (regency, contemporary, fantasy — see word_injector genre presets)
   - Social class signaling (surname matters here — Aldgate vs. Mabry vs. Harrington)
   - Sound distinctness from other characters in the cast (no Emma and Emmeline in the same book)
   - First-letter spread (avoid casting all names starting with the same letter)
4. **Present a shortlist** of 3–5 options per character, with brief notes on why each fits
5. **Wait for author confirmation** before any name is finalized

---

## Outputs

- Validated name list (flagged / clean / replaced)
- Final approved cast list → written to `books/[title]/cast/cast-list.md`
- Blocklist additions (any rejected AI names found in this manuscript added to script blocklist)

---

## Rules

- Never finalize a name without author ratification
- Never use a name that appears in the AI_CLUSTER_FIRST or AI_CLUSTER_LAST sets in `name_validator.py`
- Flag any two characters whose names could be confused when skimming (similar length, similar first letter, similar sound)
- Surnames should feel period-appropriate, not generically fantasy-medieval unless the book calls for it

---

## Script dependency

```bash
python scripts/name_validator.py --names "[proposed names]" --genre [genre]
```

---
*Build notes: The script is ready. The SKILL.md needs the full prompt instructions for the agent to present options in the right format, ask the right clarifying questions, and handle the naming lock-in gate properly.*
