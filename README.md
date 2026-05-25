# The Novel Writing Machine
### A multi-agent agentic system for long-form fiction — organized like a Formula 1 race weekend.

**Version:** 1.0 · All sectors complete  
**Architect:** Elizabeth Ann West  
**Design partner:** Claude (Anthropic)

---

## The Shape of the Thing

Every Formula 1 weekend has three phases. So does a novel.

| Phase | F1 | Novel Machine |
|---|---|---|
| **Sector 01** | Garage | Pre-writing setup — structure, world, characters, voice |
| **Sector 02** | Race | Drafting — one scene (lap) at a time, with stewards watching |
| **Sector 03** | Parc Fermé | Post-draft inspection — patterns, pacing, promises kept |

Two units of measure travel through the whole system. **Scenes are laps** — the atomic unit of story, small enough for one agent to hold complete context. **Chapters are stints** — continuous runs of laps between pit stops.

---

## Repo Structure

```
Book-Machine/
├── book-order.md              ← Lightweight pitch summary
├── docs/                      ← Architecture documentation
├── skills/
│   ├── garage/                ← 4 pre-writing setup skills
│   ├── race/                  ← Team Principal, Driver, Pit Crew, Stewards
│   └── parc-ferme/            ← 6 post-draft inspection skills
├── scripts/                   ← Python utilities
├── state/
│   └── templates/             ← Blank state document templates
└── books/
    └── _template/             ← Copy this for each new book
        ├── book-order.md
        ├── state/             ← Live state docs (dossier, bible, registers, log)
        ├── drafts/            ← Scene files land here
        └── cast/              ← Character truth vault files
```

---

## Starting a New Book

1. Copy `books/_template/` to `books/your-book-title/`
2. Copy `state/templates/story-dossier.md` into `books/your-book-title/state/`
3. Fill in **Section 1 only** of the story dossier — your brain dump, genre, constraints
4. Hand the dossier to the **Team Principal**
5. Team Principal runs Scrutineering, kicks off the Garage agents, then launches the Race

---

## The Agent Roster

### Sector 01 · Garage

| Skill | Status | What it does |
|---|---|---|
| World Engineer | ✅ built | Reads dossier Section 1; fills Sections 2, 5, 9, 11–16; builds tension curve; seeds Manuscript Bible |
| Character Lead | ✅ built | Fills Sections 3, 4, 6, 7; builds Character Truth Vaults for all major characters |
| Naming Mechanic | ✅ built | Validates names against AI-cluster blocklist; locks cast before race |
| Style Auditor | ✅ built | Reads author's prior work; builds voice anchor and manuscript-specific crutch list |

### Sector 02 · Race

| Skill | Status | What it does |
|---|---|---|
| Team Principal | ✅ built | Orchestrates everything. Pre-lap briefs. Post-lap flag routing. Drift decisions. Race log. |
| Driver | ✅ built | Runs one scene through the 7-step loop: gather, inject, plan, draft, repetition pass, continuity pass, craft pass |
| Backstory Mechanic | ✅ built | On-demand Character Truth Vault for minor characters who step forward mid-race |
| Continuity Mechanic | ✅ built | Writes new facts into the Manuscript Bible after every lap |
| Sidethought Catcher | ✅ built | Captures overflow ideas the Driver throws off mid-scene; files to Sidethought Archive |
| Continuity Steward | ✅ built | Flags POV leakage, physical contradictions, spatial logic errors, timeline breaks |
| Voice Steward | ✅ built | Audits prose against voice anchor; catches AI-isms and crutch density overages |
| Character-Truth Steward | ✅ built | Flags behavior inconsistent with Character Truth Vaults |
| Pacing Steward | ✅ built | Checks word count, tension arc, promise advancement against outline targets |

### Sector 03 · Parc Fermé

| Skill | Status | What it does |
|---|---|---|
| Craft Editor | ✅ built | Primary prose sweep — filter words, vague nouns, AI-isms, dialogue subtext, opening/closing lines |
| Grammar Mechanic | ✅ built | Sentence opener variety, chapter opening patterns, rhythm monotony — manuscript scale |
| Crutch Inspector | ✅ built | Crutch frequency and density map across the full manuscript; spike and trend analysis |
| Pacing Inspector | ✅ built | Actual tension curve vs. target curve; drag zones, energy anomalies, act structure check |
| Reader Simulator | ✅ built | Cold first-read engagement report — no outline access, pure reader experience |
| Payoff Auditor | ✅ built | Every promise paid. Every payoff earned. Last gate before delivery. |

---

## The Story Dossier

The story dossier (`state/templates/story-dossier.md`) is the NPE worksheet — the
single document the entire system builds from and runs against.

**Author fills:** Section 1 (`required_data_layer`) — brain dump, genre, word count,
POV, heat level, constraints. Everything else is built by the Garage agents.

**Garage agents fill:**
- World Engineer → Sections 2, 5, 9, 11–16 + tension curve
- Character Lead → Sections 3, 4, 6, 7
- Style Auditor → Section 8
- All agents → Section 17 (continuity check)

**Author ratifies** the completed dossier before the race begins.

---

## Python Scripts

| Script | Purpose |
|---|---|
| `scripts/name_validator.py` | Checks names against AI-cluster blocklist; generates period/genre/class-appropriate alternatives |
| `scripts/word_injector.py` | Generates random seed words for the Driver pre-lap brief |
| `scripts/pattern_detector.py` | Regex + frequency analysis for AI-ism and crutch patterns |
| `scripts/fact_ledger_diff.py` | Diffs scene content against Manuscript Bible |

---

## State Documents

| Template | Owner | Purpose |
|---|---|---|
| `story-dossier.md` | World Engineer + Character Lead | Full NPE planning worksheet — the race's north star |
| `manuscript-bible.md` | Continuity Mechanic | Ground truth for all established facts and knowledge states |
| `promise-register.md` | Team Principal + Continuity Mechanic | Every setup that needs a payoff |
| `race-log.md` | Team Principal | Per-lap record of every call, flag, and resolution |
| `character-truth-vault.md` | Character Lead + Backstory Mechanic | Off-screen interiority — read by Driver, audited by Character-Truth Steward |

---

## The Four Human Gates

The machine runs autonomously except at four points where authorial judgment is irreplaceable:

1. **Scrutineering** — Garage outputs approved before the race starts
2. **Naming lock-in** — Names confirmed before they freeze into the manuscript
3. **Drift = discovery** — The call that updates the outline vs. reverts the scene
4. **Parc Fermé flags** — Every reframe is a candidate, not a command

---

## The Severity Gradient

| Flag | Action |
|---|---|
| 🟡 Yellow flag | Logged. Race continues. |
| 🔶 Investigation | Queued for next chapter break. Race continues provisionally. |
| 🔴 Pit stop | Fix before advancing to next lap. |
| ⬛ Lap invalidated | Scene discarded. Re-run with steward constraint. |
| ⚫ Back to garage | Structural problem. Author decision. Outline updates. Resume from affected scene. |
