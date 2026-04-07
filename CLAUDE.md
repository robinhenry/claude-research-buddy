# research-buddy

Human-in-the-loop AI research assistant built as composable Claude Code skills.

## Setup

First-time users: run `scripts/setup.sh` to create your research context, library, and environment.

## Structure

- `.claude/skills/` — research skills: lit-review, reassess, plan, theory, experiment, write, critique, brainstorm, pipeline, ingest-paper, ingest-blog, sync-zotero
- **Zotero is the master library.** Add papers to Zotero (manually, via Litmaps sync, browser connector); `/sync-zotero` pulls eligible items into `library/` for full extraction. Tag a Zotero item `lib:skip` to exclude it, `lib:print` to also stage the PDF in `library/to-print/`. `library/papers/<citekey>/` folders use Better BibTeX citekeys for a 1:1 mapping with Zotero.
- `library/` — paper library (symlink or local dir, created during setup). Each paper has `summary.md` (overview) and `extracted.md` (full structured extraction) — read `extracted.md` when you need specific details, equations, or results beyond the summary. Bib entries (with keywords) in `library/library.bib`. Canonical keyword list in `library/keywords.txt`.
- `library/blogs/` — ingested blog posts and essays. Each has `source.md` (fetched markdown) and `summary.md`. Indexed in `library/blogs/blogs.index.md`. **Background reading only** — never cited as references in formal paper writeups, never added to `library.bib`.
- `projects/<name>/` — one folder per research problem. Each is an **independent git repo**.
- `research/research-context.md` — researcher expertise, lab capabilities, problem selection criteria
- `research/problem-repository.md` — running list of important open problems
- `scripts/find-papers.py` — Semantic Scholar search tool
- `scripts/run-pipeline.sh` — unattended pipeline launcher
- `scripts/init.sh` — create a new project

## Usage

**Interactive:** invoke skills in conversation — `/lit-review`, `/plan`, `/experiment`, `/write`, `/brainstorm`.

**Unattended:** `./scripts/run-pipeline.sh projects/<name>` for overnight runs.

**New project:** `./scripts/init.sh <name> path/to/plan.md`

## Conventions

- `plan.md` — the single living document per project: problem, approach, hypotheses, experiments, paper outline
- `theory/` — one `.tex` file per theoretical result. Compile with `latexmk -pdf`. The working space for proofs and derivations.
- `decisions.md` — append-only decision log: every change, pivot, question, with date and reason
- `research/writing-style.md` — writing guide. Skills that produce written output should read it.
- `research/problem-selection.md` — what makes a great problem. Skills that evaluate or choose problems should read it.
- Paper library lives in `library/`. Each paper has `summary.md` and `extracted.md`. Bib entries in `library/library.bib`. Canonical keyword list in `library/keywords.txt`.
