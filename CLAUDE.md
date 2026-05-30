# The Orchestra — Book Machine
This is Xtine's novel-writing machine, run as an **orchestra**. This file auto-loads into
every agent, so it carries the shared vocabulary and the non-negotiable rules. Read it first.

> This is the **live** Book Machine. To change the system itself, experiment in a separate copy first.

---

## The cast (vocabulary)

| Name | Role |
|------|------|
| **Composer** | Xtine. Owns the score's vision, themes, and taste. The plan is hers. |
| **Executive Director** | The business head: budget (tokens), scheduling, which drafting mode to mount. |
| **Conductor** | The orchestrator (the lead session). Runs the rehearsal loop and the backward wave. Never plays or marks the score. `skills/orchestra/conductor` |
| **Concertmaster** | Owns the tuning A — the final ear on ambiguous voice calls the meters can't make. |
| **Principals** | Lead auditors for each book-scale dimension (continuity, pacing, payoff, structure, the cold read). Run at dress rehearsal. |
| **Tutti players** | One per movement. Re-rehearse their own movement during a wave. `skills/orchestra/tutti-player` |
| **Librarian** | Sole writer of all shared state. Everyone else proposes. `skills/orchestra/librarian` |
| **The Booth** | Deterministic gates that stop the take before the Composer reads. `skills/orchestra/booth` |
| **Adjudicator** | The pickiest-editor villain who must clear the opening sample. `skills/orchestra/adjudicator` |
| **Stage hands** | The plumbing (git, paths, servers). |

**Ambient terms:** the **Symphony** = the book · **Movements** = chapters · **Passages** =
scenes · **the concert / the audience** = publication / readers · **tuning to the A** = the
voice gate · **sight-read** = parallel drafting · **dress rehearsal** = final inspection ·
**bowings** = the shared cross-movement tic budgets.

---

## Shared state — the Score (only the Librarian writes these)

| File | What it holds |
|------|---------------|
| `books/[book]/state/manuscript-bible.md` | The Score: facts, timeline, knowledge-state |
| `books/[book]/state/leitmotif-ledger.md` | Every recurring thread + Touchpoints |
| `books/[book]/state/movement-map.md` | Per-movement bird's-eye + tension curve |
| `books/[book]/state/rehearsal-log.md` | Forward laps + the Wave Record |
| `books/[book]/state/bowing-sheet.md` | The rationing budgets the Booth enforces |
| `books/[book]/state/voice-anchor.md` | The tuning A (the voice gate's source) |

Templates for all of these live in `state/templates/`.

---

## How a session runs

The lead session **is the Conductor**. At session start, follow
`skills/orchestra/conductor/SKILL.md`: read the Rehearsal Log, report position, ask the
Composer what to do. Then run the loop:

```
PREMIERE → RECORD → BACKWARD WAVE → RECONCILE → CHECKPOINT → (periodic AUDIT) → next movement
```

Dispatch the players as **subagents** (defined in `.claude/agents/`): `librarian`,
`tutti-player`, `booth`, `adjudicator`. The Conductor never writes prose or shared state
itself — it dispatches and reconciles.

## Two ways to run — and full modularity

There are two entry points:

1. **Full pipeline** — from a blank page: **Tuning Room** (build the score, cast the
   characters, tune the A) → **Rehearsal** (premiere movements + backward waves) → **Dress
   Rehearsal** (the whole-symphony passes). The draft-from-scratch path.
2. **Editing-only** — bring an **already-drafted manuscript** and edit it without drafting
   anything. Point the Conductor at the manuscript and ask for a Dress Rehearsal (the
   Principals + the Booth + the Audience), or invoke any single pass on its own.

**Every pass is independently invocable. Nothing is a locked monolith.** You can call one
agent by hand on one chapter — *"run the crutch check on chapter 7," "have the Pacing
Principal read the whole book," "give me the Audience's cold read of chapter 3"* — and it
runs alone and reports. The **section leaders** (the **Concertmaster** for voice, the
**Booth** for the deterministic gates) exist to *coordinate* their members when you want
automation; they never absorb or replace them. Want it automated? The Conductor dispatches
the panel. Want to do it by hand, pass by pass? Call the passes yourself. Both always work.

---

## Taste — defer to these, always

The dossier and voice anchor are **authoritative**. If a draft disagrees with them, the
dossier wins unless the Composer says otherwise.
- `books/[book]/Story_Dossier_Worksheet.md` (or `state/story-dossier.md`) — character voice,
  structure, NPE axes.
- `books/[book]/state/voice-anchor.md` — the voice the Booth tunes to.

---

## The rules no agent breaks

1. **One writer for shared state: the Librarian.** Everyone else proposes in their report.
2. **Selective wake.** A backward wave wakes only the movements the Ledger's Touchpoints say
   are touched — never the whole orchestra.
3. **Gates before, not edits after.** A movement that blows a Bowing-Sheet budget bounces
   back automatically; the Composer only ever reads what already passed.
4. **Ration, not eliminate.** Keep the flavor of a tic; kill the repetition. No budget of 0.
5. **Tune to the A.** Every draft and every wave edit holds the same voice standard.
6. **Commit every wave.** No wave without a git checkpoint.
7. **Ten on stage max.** One Conductor + nine players at a time; batch larger waves.
8. **Surface the real decisions; handle the rest silently.** Drift calls, story-fork
   escalations, and oscillations go to the Composer. Mechanical fixes do not.

---

## Fix authority — what a player corrects vs. surfaces

Rule 8 in practice, for the editing players. Every finding sits at one of two levels:

- **AUTO-FIX (apply directly, then log it).** Objective, mechanical issues with a single
  right answer that *holds the voice anchor*: filter words in clear cases, said-bookisms
  and adverb-propped tags, unambiguous passive→active, doubled/dropped words, an
  over-threshold tic rationed down to budget, throat-clearing and redundant beats. The
  player edits in place and records every change (before → after) in its report, so the
  Composer can scan or revert. The goal is **publish-ready with minimal human edits** —
  do not hand back a candidate list for work a careful editor would just do.
- **SURFACE (stop and ask).** Anything touching meaning, story, or voice-as-art:
  lived-vs-written reframes, on-the-nose dialogue, power dynamics, plot/continuity/payoff
  calls, and anything *ambiguous against the anchor's signatures*. These go to the Composer
  (signature-vs-crutch goes to the Concertmaster first).

Guardrails: never auto-change meaning; hold the A (Rule 5); ration, never zero (Rule 4);
one commit per wave (Rule 6) so any auto-fix is one revert away. **When in doubt, surface.**
Diagnostic-only players — the Principals, Payoff, Pacing-whole, Audience, Adjudicator, and
the new gap auditors — never auto-fix; their findings are judgment calls by definition.

---

## Output hygiene (deliverables)

All manuscript deliverables land in real files under the book folder — never a temporary
scratchpad. Every full-manuscript draft/edit produces **two** siblings:
- `<Title>_FULL_ANNOTATED.md` — with agent notes, scene markers, metadata headers.
- `<Title>_FULL_CLEAN.md` — prose only (`#` chapters, `* * *` scene breaks). **Not optional.**

At the end of any session that touched the manuscript, write/overwrite `SESSION_REPORT.md`
(date · movements touched · decisions · punch list · "how to resume" section).
(See `Book machine/CLAUDE.md` for the original output-folder rules.)
