---
name: dress-rehearsal
description: >
  The Dress Rehearsal protocol — the final full inspection before the concert (publication),
  and the model for the editing-only path (bring a finished draft, run this). Read and run by
  the Conductor (the lead session), not a subagent. Trigger when the user says "run the dress
  rehearsal," "final pass," "polish the whole book," "is this ready," or hands in a drafted
  manuscript for editing. Two phases: INSPECT (the Principals, the Booth, and the Audience read
  the whole manuscript) then CLEAN UP with the one-fixer-per-PROBLEM discipline that prevents
  whack-a-mole. Every cleanup pass is a git checkpoint.
---

# The Dress Rehearsal

The last full run-through before the audience. Run it when a manuscript is complete — or when
the Composer hands in an already-drafted book to edit (the editing-only path). The Conductor
runs this; it dispatches the passes as subagents and reconciles, exactly as in a wave.

```
INSPECT (read the whole symphony)  →  CLEAN UP (one fixer per problem)  →  CLEAR FOR THE CONCERT
```

---

## Phase 1 — Inspect

Dispatch the whole-manuscript passes (in parallel where they don't conflict) and collect every
finding into one list. Each reads the finished manuscript:

- **Pacing Principal (whole)** — the actual tension curve vs. the target; drag zones; act shape.
- **Payoff Principal** — every thread in the Leitmotif Ledger paid, every payoff set up.
- **the Audience** — the cold cover-to-cover read; engagement curve, drag, confusion, what landed.
- **the Booth** — the deterministic gates across the whole book:
  - Crutch Inspector (`pattern_detector.py`), Rhythm Inspector (`pattern_detector.py`),
  - Redundancy (`redundancy_detector.py`), Seam (`seam_detector.py`).
- **the Concertmaster** — the whole-manuscript voice read (runs the Tuning, Voice Principal,
  Line Editor; rules the ambiguous calls).
- **the Adjudicator** — the hostile read; must clear the opening sample (and ideally the whole).

The output of Phase 1 is a single ranked list of **whole-manuscript problems** — not per-chapter
notes. Examples: *"'exactly' x18 (budget 6)," "Darcy's signet-ring tell x12," "echo seam at
36->37," "'the'-opener at 19% (budget 15%)," "sag across movements 14-17," "promise L9 unpaid."*

---

## Phase 2 — Clean up: ONE fixer per PROBLEM (not per movement)

This is the rule that makes the difference. **Do not send one fixer per chapter.** Per-chapter
fixers reintroduce each other's habits — you ration the gaze tic in movement 3 and the
ring-turn quietly becomes the new tic in movement 9. Whack-a-mole.

Instead:

1. **One fixer owns one whole-manuscript problem** and ranges across *every* movement that
   problem touches — rationing that single tic everywhere at once, to one consistent standard.
2. **Every fixer carries the same Bowing Sheet.** The Librarian writes the canonical ruling
   first (which tics are rationed, to what budget, which anchors to keep). Each fixer reads the
   identical sheet, so no fixer reintroduces a habit another just cured.
3. **Ration, not eliminate.** Keep the flavor; kill the repetition. Bring the ring-tell to its
   3 anchors against a budget of 4 — don't delete it to zero.
4. **Avoid file collisions.** Because a problem-fixer edits across many movement files, fixers
   whose problems touch overlapping movements run **sequentially** — each finishes and commits
   before the next begins, so the later fixer sees the earlier fixes and two agents never write
   the same file at once. Problems that touch disjoint movements may run in parallel.
5. **Each fix is a git checkpoint.** One revert undoes a cleanup pass that made the book worse.

---

## Know when to stop

After the fixes, re-run only the affected gates. If what remains is a few minor clusters, log
them as a **"watch"** and stop — do not thrash another full pass. If a fix would create a new
tic, the shared Bowing Sheet prevents it. If two fixes **oscillate** (cure one, break the other,
repeat), stop and surface it to the Composer — that is a craft decision, not a mechanical one.

The Dress Rehearsal ends when the deterministic gates pass within budget, the Adjudicator would
keep reading, and the Audience found no unintended drag. Then the Composer reads for delight —
the last mile, not the QA line.

---

## What you never do

- **Never dispatch one fixer per chapter for a manuscript-wide tic.** One fixer per *problem*.
- **Never let two fixers edit the same movement at once.** Sequence overlapping problems.
- **Never eliminate a signature move to zero.** Ration to the Bowing Sheet's flavor budget.
- **Never grind past an oscillation or a "watch."** Stop; escalate the real decisions.
- **Never skip the checkpoint.** Every cleanup pass commits.
