---
description: "Run the full research pipeline end-to-end: literature review, planning, experiments, paper writing. Use when the user says 'run pipeline', 'full research run', 'overnight run', or 'run buddy on this problem'."
---

# Research Pipeline

`$ARGUMENTS` — path to a project directory (must contain `plan.md`).

## First pass

1. **Literature review** — follow `/lit-review`
2. **Reassess** — follow `/reassess`. If it recommends pivot or abandon, stop and write to decisions.md. If sharpen, revise the problem statement before continuing.
3. **Plan** — follow `/plan`
4. **Theory** — follow `/theory` for each pending theoretical result
5. **Experiment** — follow `/experiment` to validate the theory
6. **Write** — follow `/write`

## Iterate

After the first pass, loop:

1. Run `/critique` on the project
2. If the critique finds substantive issues, address them (rerun experiments, revise the plan, rewrite sections — whatever is needed)
3. Repeat (max 3 rounds) until the critique finds no major issues, or diminishing returns are clear

## Blocking on human input

If you hit something you can't resolve alone — missing papers, ambiguous problem scope, a design decision that needs the human's judgment — write what you need to `decisions.md` and stop. Don't keep iterating around a gap you can't fill. The human will read decisions.md and resume.

## Finish

Append progress to `decisions.md` throughout. Write retrospective observations to `decisions.md` when done.
