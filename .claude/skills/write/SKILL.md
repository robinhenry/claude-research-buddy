---
description: "Write or revise a research paper from a plan and experiment results. Use when the user says 'write the paper', 'draft the paper', 'revise the paper', or 'write up the results'."
---

# Write Paper

`$ARGUMENTS` — path to a project directory (must contain `plan.md` and experiments).

Read `research/writing-style.md` before drafting.

## Audience

Read `plan.md` to understand the target audience.

## Writing

- Every claim cites an experiment or derivation
- Only cite papers from `library/library.bib`. Cite primary sources. Never fabricate.
- If you believe you're missing key or primary references that should be cited, request them.
- Prioritize simplicity and a clear story.
- Check `plan.md` for target venue or format requirements. If none specified, use a sensible default (e.g., `latexmk -pdf`).
- Save drafts as `paper/drafts/v1.tex`, `v2.tex`, etc. Never overwrite.

