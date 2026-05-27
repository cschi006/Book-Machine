# Book Machine — Project Rules

This folder is the persistent home for Xtine's book machine. Any Claude session that opens this folder must follow the rules below. These exist because the first run of the machine lost its outputs to a temporary scratchpad — the SESSION_REPORT, full annotated manuscript, and clean manuscript were generated but never made it here, and were gone when the session ended.

## Output destination — non-negotiable

All manuscript-related outputs MUST be written into this folder (`C:\Users\cschi\OneDrive\Book Machine\Book machine`). Never the session's temporary outputs scratchpad. The OneDrive folder is what syncs and persists; the scratchpad does not.

This applies to:
- Working draft chapters (with Driver / Principal / Editor notes, scene markers, metadata headers)
- The combined annotated full manuscript
- The combined clean manuscript (notes stripped)
- Any SESSION_REPORT.md
- Any dossier updates or worksheets
- Any chapter-summary files

The temp scratchpad may be used for intermediate computation, format conversions, and validation — but the *deliverables* always land here.

## Always produce both versions

Every time the book machine completes a draft or edit pass on the full manuscript, it must produce two sibling files in this folder:

1. **`<Title>_FULL_ANNOTATED.md`** — the working draft with all Driver / Principal / Editor notes, metadata headers (POV / WC / Tension / Seeds / Drift flags), `## Scene N` sub-headers, and chapter-close annotations intact. This is what Xtine reads when she wants to see the machine's reasoning.
2. **`<Title>_FULL_CLEAN.md`** — the same content with every annotation stripped. Title page → chapters as `#` headers → scene breaks as `* * *` → prose only. This is what gets dropped into Word, Vellum, or whatever formatting workflow comes next.

Do not deliver only one. The clean export is not optional — Xtine asked for it explicitly on the first run and needs it every time. If you write the annotated file, write the clean file in the same turn.

## Session report

At the end of any session that touched the manuscript, write a `SESSION_REPORT.md` to this folder. Overwrite the existing one if present (don't pile up dated versions — the current one should reflect current state). The report should include:

- Date of session
- Chapters touched and what changed in each
- Decisions made and why
- Open items / punch list for the next session
- A "How to use this in another chat" section so the next session can come up to speed in one read

## File naming

- Working title for this book: `Paint Me Like Your Fae Prince`
- File name prefix: `Paint_Me_Like_Your_Fae_Prince`
- Version suffix only when needed (`_v2`, `_v3`) — annotated/clean is the primary axis, not version number
- Dossier: `Story_Dossier_Worksheet.md` (already here)
- Don't rename existing files without flagging it

## Before starting any session in this folder

1. Read this file (CLAUDE.md)
2. Read `Story_Dossier_Worksheet.md` for authoritative character voice, story structure, NPE axes
3. Read the most recent `SESSION_REPORT.md` if one exists
4. Then read whichever manuscript file is being worked on

The dossier is authoritative. Disagreements between the dossier and the draft resolve in favor of the dossier unless Xtine says otherwise.
