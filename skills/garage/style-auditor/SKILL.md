# Style Auditor
**Sector:** Garage · **Status:** Stub — ready to build  
**Role:** Reads the author's prior work to build a voice anchor and manuscript-specific crutch list before the race begins.

---

## Purpose

The Style Auditor exists because AI writing defaults to a competent, flattened voice that sounds like no one in particular. The Voice Steward (during the race) and the Craft Editor (in Parc Fermé) both need something to audit against. That something is the voice anchor this skill produces.

The voice anchor is not a style guide. It is a living document of what this author actually does — sentence rhythms, vocabulary register, signature moves, structural habits, the things that make a paragraph feel like hers and not like anyone else's.

---

## When to Invoke

- In the Garage, after World Engineer and Character Lead have run
- Any time the author wants to update the voice anchor with new work
- Before running the Voice Steward if the voice anchor is more than 6 months old

---

## Inputs

- Author's prior books or writing samples (paths to files in `books/` or uploaded text)
- Book order voice references (titles named in `book-order.md`)
- The manuscript-specific crutch list from `scripts/pattern_detector.py` run on prior work

---

## Process

### Phase 1 — Voice Sample Analysis
1. Read each provided voice reference
2. Run `scripts/pattern_detector.py` on each to identify signature patterns (patterns that appear consistently = voice, not crutch)
3. Identify:
   - **Sentence length distribution** — does she favor short punchy sentences? Long flowing ones? Mixed?
   - **Paragraph structure** — action-beat-reaction? Beat-dialogue-internalization?
   - **POV depth** — deep interiority, filtered, or cinematic?
   - **Vocabulary register** — elevated/literary, conversational, clipped, sensory-heavy?
   - **Signature moves** — recurring structural choices that feel intentional (e.g. ending chapters on a single short sentence, using em-dashes for internal interruption)
   - **What she never does** — constructions absent from her work even when they'd be easy defaults

### Phase 2 — Crutch Baseline
4. Run pattern_detector.py across all samples to find patterns that appear too often (these are crutches to avoid, not voice to emulate)
5. Distinguish: pattern that appears 3× across 3 books = voice. Pattern that appears 30× in one chapter = crutch.

### Phase 3 — Voice Anchor Document
6. Produce `books/[title]/state/voice-anchor.md` with:
   - Voice fingerprint summary (5–7 sentences describing the voice)
   - Sentence rhythm profile
   - Vocabulary register notes
   - Signature moves (do these, they're yours)
   - Crutch list for this manuscript (avoid these, you overuse them)
   - The single "voice check question" the Voice Steward will use: *Does this paragraph read like [Author]?*

---

## Outputs

- `books/[title]/state/voice-anchor.md`
- Updated crutch list appended to `scripts/pattern_detector.py` CONSTRUCTION_PATTERNS

---

## Rules

- Never conflate voice with crutch. Both are recurring patterns; one is intentional, one is not.
- The crutch list is manuscript-specific. A construction that appeared 3× in the last book but 0× so far in this one is not yet a crutch.
- The voice anchor must include negative examples — things the author specifically does NOT do that AI defaults to.

---

*Build notes: Core logic is here. Needs the full prompt instructions for reading and analyzing voice samples, the exact format for the voice-anchor.md output, and how to present findings to the author for ratification.*
