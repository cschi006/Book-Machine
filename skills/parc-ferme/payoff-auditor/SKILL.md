# Payoff Auditor
**Sector:** Parc Fermé · **Status:** Stub — ready to build  
**Role:** Cross-checks every promise in the Promise Register against the manuscript. Every setup pays off. Every payoff has its setup. Last gate before delivery.

---

## Purpose

The Promise Register was seeded in the Garage and maintained throughout the race. The Payoff Auditor reads it against the finished manuscript and verifies: did every promise actually land?

This is not about whether payoffs were good. That's the Reader Simulator's territory. This is about whether they exist at all.

The failure mode: a promise was made in chapter four, the Referee didn't catch it, and the manuscript ends without paying it. The reader feels cheated and doesn't know why.

---

## Inputs

- Full manuscript
- Promise Register (`books/[title]/state/promise-register.md`)
- Book order (the Reader Promise Contract — the load-bearing promises from intake)

---

## Process

1. Read Promise Register: pull every promise, its scene of origin, and its expected payoff
2. For each Reader Promise Contract item: verify the payoff exists and that it earned its resolution
3. For each micro-promise: find the payoff scene, or flag as unpaid
4. Flag any payoff that has no corresponding setup (payoffs that come from nowhere)
5. Categorize each unpaid promise:
   - FORGOTTEN — no attempt at payoff visible
   - DEFERRED — seems intentionally open (possible series hook — flag for author decision)
   - PARTIAL — payoff exists but underpays the setup
6. Produce flagged list for author ratification

---

## Outputs

- Promise audit report
- Open promises flagged as: FORGOTTEN / DEFERRED / PARTIAL
- Payoffs-without-setups flagged for author review

---

## Rules

- A promise that was intentionally left open (series hook) must still be flagged — the author confirms, not the agent
- A partial payoff is flagged even if it's close — close isn't paid
- The Reader Promise Contract items are non-negotiable: if any of the three primary payoffs from the book order are not in the manuscript, that is a back-to-garage call even at this stage

---
*Build notes: The Promise Register format drives this. The prompt needs to explain how to identify a "payoff" vs. an "echo" of a promise — the difference between the scene that resolves the tension and a scene that revisits it without resolving.*
