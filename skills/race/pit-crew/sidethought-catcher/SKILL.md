# Sidethought Catcher
**Sector:** Race · Pit Crew · **Status:** Stub — ready to build  
**Role:** Captures the emergent ideas the Driver throws off mid-scene — the things that don't belong in this lap but might be the seed of a future one.

---

## Purpose

This skill exists because of something you described exactly right: when a human writer is sprinting through a scene, a separate thought arrives — a future scene, a better version of an earlier moment, a character detail that belongs somewhere else. The human writes it on a sticky note or in a margin. Most AI pipelines have no equivalent.

The Sidethought Catcher runs parallel to the Driver. It is not editing the scene. It is watching the scene for ideas that overflow it.

---

## When to Invoke

- Automatically, in parallel with the Driver's drafting step
- Can also be called standalone: "Capture this idea for later: [idea]"

---

## Inputs

- The Driver's scene draft (as it completes)
- The current outline (to understand where captured ideas could land)
- The current race log (to avoid duplicating already-captured ideas)

---

## Process

1. **Read the finalized scene draft**
2. **Identify overflow ideas** — things the scene suggests but doesn't need:
   - A detail that belongs in an earlier scene (retroactive setup opportunity)
   - A beat that could deepen a future scene
   - A character moment that surfaces something not yet in any character's truth vault
   - A thematic thread that could be woven through adjacent scenes
   - A line of dialogue that was almost said but wasn't — the thing the character held back
3. **Categorize each idea:**
   - `PLANT_EARLIER` — retroactive setup for this scene
   - `SEED_FUTURE` — belongs in a later scene
   - `CHARACTER_TRUTH` — potential addition to a truth vault
   - `THEMATIC` — pattern that could be woven through the manuscript
   - `AUTHOR_CHOICE` — interesting option the author might want to consider
4. **File to race log** with scene reference
5. **Flag high-value ideas** to Team Principal for possible immediate action

---

## Outputs

- Sidethought entries → appended to `books/[title]/state/race-log.md` Sidethought Archive
- High-value flags → passed to Team Principal

---

## Rules

- This skill does NOT edit the scene. It only captures overflow.
- Ideas that could affect the current scene go to the Continuity Steward or Team Principal, not here.
- `PLANT_EARLIER` ideas may trigger a lap invalidation or pit stop if important enough — flag to Team Principal.
- Every captured idea should have: category, scene reference, brief description, suggested future placement.

---

*Build notes: The parallel-execution aspect is the interesting architectural piece. The prompt needs to make clear that this agent is reading for what the scene suggested rather than what it contained.*
