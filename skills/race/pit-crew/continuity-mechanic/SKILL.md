# Continuity Mechanic
**Sector:** Race · Pit Crew · **Status:** Stub — ready to build  
**Role:** Updates the world-state ledger after every lap. The only agent with write access to the dynamic Manuscript Bible.

---

## Purpose

The Manuscript Bible starts as a static document built in the Garage. But every scene establishes new facts — a character learns something, a door is locked, a character moves from one location to another, a relationship shifts. The Continuity Mechanic is the agent that writes these updates in real time, so the ledger stays current and the Continuity Steward has accurate ground truth to audit against.

**This skill is the reason characters can't know things they haven't been told.** The knowledge-state entries it writes — `known_to: [characters]`, `known_since: [scene]` — are what the Continuity Steward checks when auditing POV.

---

## When to Invoke

- Automatically, after every lap (scene) completes and the Driver's draft is finalized
- Runs in parallel with the Stewards Panel's audit — does not wait for steward results
- Before the next Scene Planner briefing (so scene planning reflects current state)

---

## Inputs

- Finalized scene draft
- Current Manuscript Bible
- Current Promise Register (some scene facts may open or advance promises)

---

## Process

1. **Read the finalized scene carefully for new facts:**
   - New knowledge gained by any character
   - New locations visited or established
   - New objects introduced or moved
   - Relationship state changes
   - Timeline events (what happened, when relative to the story clock)
   - Physical changes to characters (injury, change of clothing, etc.)
   - New promises made to the reader (micro-promises to flag to Team Principal)

2. **Run `scripts/fact_ledger_diff.py --update`** to identify new facts not yet in the bible

3. **Update Manuscript Bible:**
   - Add new rows to Established Facts Log
   - Update Knowledge State table with `known_to` and `known_since` entries
   - Update Timeline if scene establishes or confirms temporal position
   - Update Locations if new space is described

4. **Flag to Team Principal** if any scene fact contradicts an established bible entry (this should have been caught by the Continuity Steward, but this is the second check)

5. **Confirm update complete** so Team Principal can advance to next lap

---

## Outputs

- Updated `books/[title]/state/manuscript-bible.md`
- Update summary (list of what changed) → appended to race-log.md
- Any contradiction flags → passed to Team Principal

---

## Rules

- This agent has WRITE ACCESS to the Manuscript Bible. All other agents have READ-ONLY access.
- Never delete an existing bible entry — only append or annotate
- Knowledge state entries must be granular: "Darcy knows Wickham's history" not "characters know things"
- If unsure whether something is a new fact or an echo of an existing one, flag rather than add — avoid duplicate entries

---

*Build notes: The script integration is the key technical piece. The prompt needs to specify exactly how to read a scene for new facts, the precise format for each type of bible update, and how to handle edge cases (retconned facts, scenes that deliberately mislead the reader vs. the characters).*
