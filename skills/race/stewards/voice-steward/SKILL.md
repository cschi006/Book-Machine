# Voice Steward
**Sector:** Race · Stewards Panel · **Status:** Stub — ready to build  
**Jurisdiction:** Prose voice — sentence rhythm, vocabulary register, AI-isms, crutch patterns

---

## Purpose

The Voice Steward runs the craft-editor skill in lap-audit mode against the voice anchor. It is the same craft authority the Driver used in Step 6 of the loop; here it is the independent re-check after the lap is finalized, reading from outside the scene rather than within it.

The voice anchor (produced by the Style Auditor) is this steward's primary reference. If the voice anchor doesn't exist, the Voice Steward cannot function — escalate to the Team Principal.

---

## Severity Calls

| Finding | Default severity |
|---|---|
| AI-ism cluster (multiple generic constructions in same passage) | Pit stop |
| Single crutch pattern above chapter density limit | Pit stop |
| Vocabulary register inconsistency (too elevated/too casual for this POV) | Investigation |
| Sentence rhythm flattened across a passage | Yellow flag |
| Single crutch instance within acceptable density | Yellow flag |

---

## Inputs

- Finalized scene draft
- Voice anchor (`books/[title]/state/voice-anchor.md`)
- Crutch list for this manuscript

---

## Process

1. Read scene with voice anchor in context
2. Run mental test: *Does this paragraph read like [Author]?*
3. Check for AI-ism patterns (see `scripts/pattern_detector.py` CONSTRUCTION_PATTERNS)
4. Check crutch density against the manuscript-specific crutch list
5. Note vocabulary register breaks
6. Flag any passage where the prose sounds like no one in particular
7. Assign severity and pass to Team Principal

---
*Build notes: The voice anchor is the key dependency. The prompt needs to explain how to read against it, and how to distinguish a voice pattern from a crutch.*
