# Backstory Mechanic
**Sector:** Race · Pit Crew · **Status:** Stub — ready to build  
**Role:** Generates on-demand interiority for minor characters who acquire significant page time mid-novel.

---

## Purpose

The Character Lead pre-builds interiority files for major characters. But novels are populated by characters who step forward unexpectedly — the innkeeper who becomes a confidant, the rival who turns out to matter, the childhood friend whose name appears in chapter three and reappears in chapter fourteen with weight behind it.

The Backstory Mechanic is on-call during the race. When the Driver or the Scene Planner flags that a character needs more interior gravity than their stub provides, the Backstory Mechanic spins up, writes the truth document, and files it in the Character Truth Vault before the Driver drafts the scene.

**The key principle:** Everything this skill writes is off-screen. It appears in the manuscript through behavior, not exposition.

---

## When to Invoke

- Driver or Scene Planner flags: "this character needs more depth for this scene"
- A minor character is about to have a scene of emotional significance
- A character's fear, wound, or mask needs a specific history to make a scene land

---

## Inputs

- Character's existing profile stub (from Character Lead or cast-list.md)
- Scene brief: what emotional truth is needed for this scene to work
- Existing Character Truth Vault entries for this character (if any)
- Manuscript Bible (for world context, established facts about this character)

---

## Process

1. **Read the character stub and scene brief carefully**
2. **Identify the specific emotional need** — what does the Driver need to understand about this character to write this scene authentically?
3. **Write the truth document** using the character-truth-vault.md template
4. **Focus on the specific, not the general:**
   - Not "she's afraid of horses"
   - But "she was eight years old, in the stable with the groom's son Petyr, and the gray mare spooked when a rat crossed the straw. Petyr was seventeen and quick, but the kick caught him across the temple. She stood there while he bled. She ran to get her father. By the time they returned, Petyr's left eye would never track right again. She has never told anyone she was the one who dared him to touch the mare's flank. She still sees his face when she smells straw."
5. **File the truth document** to `books/[title]/cast/[character-name]-truth.md`
6. **Pass document path** to the Driver as additional context for the scene

---

## Outputs

- Truth document → `books/[title]/cast/[character-name]-truth.md`
- Confirmation to Team Principal that context is ready

---

## Rules

- The truth document is NEVER quoted in the manuscript. The Driver reads it; the prose shows it.
- Specificity is the entire point. Generic backstory is worse than none — it produces generic behavior.
- The wound must be earned by something the character did or failed to do, not just something that happened to them. Responsibility is more interesting than victimhood.
- Always check the Manuscript Bible first — don't contradict established facts about the character.

---

*Build notes: The architecture is clear. Needs the full prompt that instructs the agent how to ask the right questions, how specific to go, and what the output document must contain to be useful to the Driver.*
