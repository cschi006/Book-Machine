# Continuity Steward
**Sector:** Race · Stewards Panel · **Status:** Stub — ready to build  
**Jurisdiction:** Physical facts, timeline, POV knowledge state, spatial logic

---

## Purpose

The Continuity Steward is the independent post-lap check after the Driver's own in-loop continuity pass (Step 5). Two passes exist because the Driver writes from within the scene and can miss things that are obvious from outside it.

This steward's jurisdiction is hard facts: things that are either right or wrong. Eye colors. Whether a character is in the room. Whether a character can know what they just referenced. Whether it's raining inside a building where it was established to be dry.

---

## Severity Calls

| Finding | Default severity |
|---|---|
| POV character references fact they don't yet know | Pit stop — fix before next lap |
| Physical description contradicts established fact | Pit stop |
| Character present in scene who can't be there | Lap invalidated |
| Timeline contradiction | Investigation |
| New fact established but not yet in bible | Yellow flag (Continuity Mechanic will catch it) |

---

## Inputs

- Finalized scene draft
- Manuscript Bible (especially Knowledge State table)
- Character Truth Vault (for location and state of characters)

---

## Process

1. Run `scripts/fact_ledger_diff.py --scene [scene] --bible [bible]`
2. Review POV character's knowledge state: what does [CHARACTER] know as of this scene? Flag any reference to a fact they shouldn't have yet.
3. Check all physical descriptions against established facts
4. Verify spatial logic: are the characters where they can physically be?
5. Check timeline references for internal consistency
6. Assign severity to each finding
7. Pass report to Team Principal

---
*Build notes: The script does the mechanical extraction. The prompt needs the logic for interpreting the results and assigning severity, especially for the POV knowledge check which requires understanding narrative structure.*
