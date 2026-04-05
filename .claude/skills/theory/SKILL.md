---
description: "Work on a theoretical result: derive, prove, or refine. Use when the user says 'prove', 'derive', 'work on the theory', 'theorem', 'proof', or references a specific theoretical result (e.g., 'T4')."
---

# Theory

`$ARGUMENTS` — a specific result to work on (e.g., "T4 regret bound"), or path to a project directory to work on the next pending result.

Read `plan.md` for the theoretical results and their status. Read `research/writing-style.md` for clarity standards. Read relevant paper extractions from `library/papers/*/extracted.md` for equations and prior results to build on.

## Process

1. **Read the existing work.** Check `theory/` for any prior attempts at this result. Read the plan's statement of the result.
2. **Identify what's new vs what's standard.** Cite standard results (e.g., MLE convergence, IFT, design measure properties) rather than re-deriving them. Only write out the steps that are novel to our setting. Reference specific theorems from the library (e.g., "By Pronzato 2013, Thm 4.10, ...").
3. **Derive.** Write `theory/<result_name>.tex`. Structure: assumptions → statement → proof (novel steps only, citing standard results) → remarks on where assumptions fail. Keep it concise — a working proof, not a textbook chapter.
4. **Compile.** Run `cd <project>/theory && latexmk -pdf <result_name>.tex` and fix any errors.
5. **Self-check.** Is every step justified? Are assumptions stated? Does the result actually say what the plan claims? Are there gaps?
6. **Log.** Append to `agent-log.md` what was derived and any surprises.
