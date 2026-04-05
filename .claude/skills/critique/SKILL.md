---
description: "Critically review the current state of a research project. Use when the user says 'critique', 'review the project', 'what's wrong with this', 'poke holes', or 'sanity check'."
---

# Critique

`$ARGUMENTS` — path to a project directory.

Read `research/writing-style.md` and `research/problem-selection.md` before critiquing.

Read everything the project has so far: `plan.md`, experiment results, `paper/main.tex` (if any).

Be a sharp, constructive critic. Find weaknesses, not praise. For each issue: what's wrong, where, and how to fix it.

Check whichever apply to the current state:
- **Theory**: Are assumptions stated and justified? Are proofs correct and complete? Are bounds tight or loose? Could a stronger result be obtained? Is anything assumed that should be proved?
- **Plan**: Are hypotheses falsifiable? Could the expected results occur even if the hypotheses are wrong? Are simpler approaches being overlooked?
- **Experiments**: Do results validate the theory? Do results actually support the conclusions? Are controls missing? Is anything suspiciously clean or arbitrary?
- **Paper**: Does the story follow OCAR? Are claims supported? Would a skeptical reviewer at a top venue accept this? Is the theoretical contribution clear?
- **Overall**: Is effort being spent where it matters? What's the weakest link?

Append the critique to `plan.md` as a "## Critique (round N)" section. Flag the top 3 issues.
