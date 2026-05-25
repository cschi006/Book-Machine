# The Novel Writing Machine
### A multi-agent agentic system for long-form fiction — organized like a Formula 1 race weekend.

**Version:** 0.2 · Race phase implemented, Parc Fermé stubs in progress  
**Architect:** Elizabeth Ann West (Goddess Divine)  
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
├── book-order.md          ← START HERE. Your pitch. The system's north star.
├── docs/                  ← Presentation and architecture documentation
├── skills/
│   ├── garage/            ← 5 skills: pre-writing setup
│   ├── race/              ← Team Principal, Driver, Pit Crew, Stewards
│   └── parc-ferme/        ← 6 post-draft inspection skills
├── scripts/               ← Python utilities (name validator, word injector, etc.)
├── state/
│   └── templates/         ← Blank state document templates
└── books/
    └── _template/         ← Copy this for each new book
        ├── book-order.md
        ├── state/         ← Live state docs for this book
        ├── drafts/        ← Chapter files land here
        └── cast/          ← Character truth vault files
```

---

## Starting a New Book

1. Copy `books/_template/` to `books/your-book-title/`
2. Fill out `books/your-book-title/book-order.md` (your pitch)
3. Hand the book order to the **Team Principal** skill
4. The Team Principal kicks off Scrutineering and, once you approve, the Race

---

## The Agent Roster

### Sector 01 · Garage
| Skill | Status | What it does |
|---|---|---|
| Story Engineer | wraps existing | Dossier, outline, payoffs, tension curve, telemetry |
| World Engineer | built | World-state ledger + knowledge-state machinery |
| Character Lead | built | Off-screen interiority files for every major character |
| Naming Mechanic | stub | Period/region-appropriate names, anti-AI-cluster filtered |
| Style Auditor | stub | Reads author voice samples, builds voice anchor + crutch list |

### Sector 02 · Race
| Skill | Status | What it does |
|---|---|---|
| Team Principal | built | Orchestrates everything. Makes all severity calls. |
| Driver | built | Runs one scene through the 7-step loop |
| Backstory Mechanic | stub | On-demand interiority for minor characters |
| Continuity Mechanic | stub | Updates world-state ledger after every lap |
| Sidethought Catcher | stub | Captures ideas the Driver throws off mid-scene |
| Continuity Steward | stub | Flags POV leakage, physical drift, timeline errors |
| Voice Steward | stub | Audits prose against voice anchor |
| Character-Truth Steward | stub | Flags behavior inconsistent with interiority files |
| Pacing Steward | stub | Reads against tension curve and telemetry |

### Sector 03 · Parc Fermé
| Skill | Status | What it does |
|---|---|---|
| Craft Editor | built | Primary craft sweep — same skill used per-lap by Driver |
| Grammar Mechanic | built | Sentence rhythm and opener variety at book scale |
| Crutch Inspector | built | Crutch frequency and density, book-wide |
| Pacing Inspector | stub | Actual tension vs. target tension curve |
| Reader Simulator | stub | Sequential first-read engagement curve |
| Payoff Auditor | stub | Every setup pays off. Every payoff has its setup. |

---

## Python Scripts

| Script | Purpose |
|---|---|
| `scripts/name_validator.py` | Checks names against AI-cluster blocklist |
| `scripts/word_injector.py` | Generates random seed words for Driver |
| `scripts/pattern_detector.py` | Regex + frequency analysis for crutch patterns |
| `scripts/fact_ledger_diff.py` | Diffs scene content against world-state ledger |

---

## The Four Human Gates

The machine runs autonomously except at four points where authorial judgment is irreplaceable:

1. **Scrutineering** — Garage outputs approved before the race starts
2. **Naming lock-in** — Names confirmed before they freeze into the manuscript
3. **Drift = discovery** — The call that rewrites the outline vs. reverts the scene
4. **Parc Fermé flags** — Every reframe is a candidate, not a command

---

## The Severity Gradient

| Flag | Action |
|---|---|
| 🟡 Yellow flag | Logged. Race continues. |
| 🔶 Investigation | Queued for next pit stop. Race continues provisionally. |
| 🔴 Pit stop | Fix now, then continue. |
| ⬛ Lap invalidated | Re-run scene with steward note as constraint. |
| ⚫ Back to garage | Structural problem. Outline updates. Resume from affected scene. |
