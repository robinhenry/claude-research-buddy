---
description: "Run computational experiments from a research plan. Executes scripts, captures results, updates the plan. Use when the user says 'run experiments', 'execute the plan', 'test hypothesis', or 'run experiment N'."
---

# Run Experiments

`$ARGUMENTS` — path to a project directory (must contain `plan.md`).

Read `plan.md` to understand the hypotheses and experiment plan. Experiments validate, illustrate, or extend the theoretical or conceptual work. Where theoretical results exist, tie experiments to specific predictions.

## Workflow

1. **Design** — pick the next experiment from `plan.md` (or propose one if none are specified). Be clear about what hypothesis it tests and what outcome you expect.
2. **Implement** — write the code in `experiments/`. Structure however makes sense for the problem.
3. **Run** — use a sub-agent per experiment to keep output out of main context. Launch independent experiments in parallel.
4. **Record** — save results (figures, data, logs) alongside the code. Write a brief summary of findings.
5. **Update plan.md** — update hypothesis statuses based on results. Note surprises or new questions.
6. **Iterate** — run as many experiments as needed. The paper presents only the key ones (typically 3–5).

Log decisions and pivots to `decisions.md`.
