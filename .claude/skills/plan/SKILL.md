---
description: "Create a research plan from a problem statement. Produces hypotheses, experiment designs, and a paper outline. Use when the user says 'plan', 'make a research plan', 'design experiments', or provides a problem statement to work from."
---

# Research Plan

`$ARGUMENTS` — path to a project directory (must contain `plan.md`).

Read `research/writing-style.md` and `research/problem-selection.md` before planning.

## 1. Understand and refine the problem

Read `plan.md`. Critically assess the problem statement against what the literature shows: Has this been solved? Is there a sharper question? Is the gap where we thought it was? If changes are needed, revise `plan.md` and note what changed and why in `decisions.md`. If the problem statement references external repos, read their source.

## 2. Write plan.md

- **Literature** — key papers and gaps (if not already present from /lit-review)
- **Problem formulation** — formal mathematical setup, definitions, assumptions
- **Theoretical results** — one paragraph per result stating the claim, the intuition for why it should hold, and a confidence level: [likely provable], [plausible but uncertain], [speculative]. These are targets for `/theory` to work out — some will survive, some will weaken, some will fail. That's fine.
- **Hypotheses** — numbered (H1, H2, ...), falsifiable, each with status: PENDING. These bridge theory and computation — things the theory predicts that experiments will validate.
- **Experiment plan** — computational experiments that validate, illustrate, or extend the theory. Each with: goal, method, expected outcome, which theoretical result it validates.
- **Paper outline** — section structure
