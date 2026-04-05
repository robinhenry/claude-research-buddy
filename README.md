# claude-research-buddy

## What?

A lightweight human-in-the-loop AI research assistant, built as composable Claude Code skills. It helps with literature exploration, paper ingestion, research planning, running experiments, drafting theorems, and writing papers.

Nothing fancy! Just Claude skills that turn Claude code into a more useful research assistant, allowing you to move more quickly.

The workflow:

**Setup:**

- Summarize your research context, interests, expertise, available resources, etc. in a single file - **once**. This is the context that turns Claude into an assistant tailored to your research.
- Point to your *paper library* (where you and Claude will save and extract relevant papers)
- Create a new project directory in `projects/`

**Do research, faster:**

- Start a new Claude CLI chat from inside this directory (in your IDE, terminal, or however you currently do it)
- Work alongside your newly upgraded assistant!

## Why?

I made this because I found Claude was amazing at writing code, but not so much at keeping track of my research context, interests, and the state of the broader research field. This meant I was doing a lot of manual steering,
constently giving it the same context over and over. But that was hard, because Claude couldn't read the research papers I had in mind (or ones I didn't know about).

It started as a paper ingestion tool (turning a paper .pdf into an .md file) to give Claude better research context, and eventually evolved into an assistant I spend most of my days talking to in the terminal.


## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Python 3.11+
- (Optional) [Semantic Scholar API key](https://www.semanticscholar.org/product/api#api-key) for faster paper searches - highly recommended

## Quickstart

```bash
git clone https://github.com/robinhenry/claude-research-buddy.git
cd claude-research-buddy
./scripts/setup.sh
```

Setup creates your research context, paper library, and environment. Then edit `research/research-context.md` with your background and interests.

### Starting a project

```bash
# Option 1: start with just a name — you'll get a blank plan.md to fill in
./scripts/init.sh my-project

# Option 2: start from an existing problem statement
./scripts/init.sh my-project path/to/problem-statement.md
```

Each project gets its own git repo inside `projects/`. Open Claude Code in the `claude-research-buddy` directory and go:

```
/lit-review projects/my-project    # survey the literature
/plan projects/my-project          # turn findings into a research plan
/experiment projects/my-project    # run computational experiments
/write projects/my-project         # draft a paper from results
```

## Skills

| Skill | What it does |
|-------|-------------|
| `/lit-review` | Search your library and Semantic Scholar, ingest relevant papers, write a literature review |
| `/ingest-paper` | Read a PDF, extract structured notes, add to your library with bib entry |
| `/plan` | Create a research plan: hypotheses, experiment designs, paper outline |
| `/theory` | Derive, prove, or refine a theoretical result |
| `/experiment` | Write and run computational experiments, capture results |
| `/write` | Draft or revise a research paper from your plan and results |
| `/critique` | Critically review the current state of a project |
| `/reassess` | Step back and evaluate whether the project direction is right |
| `/brainstorm` | Generate research problem statements from literature |
| `/pipeline` | Run the full loop end-to-end (lit review → plan → experiment → write → critique) |

## Architecture

```
research-buddy/              ← this repo (the tool)
├── .claude/skills/          ← 10 research skills
├── scripts/                 ← setup, project init, paper search, pipeline runner
├── research/                ← writing style guide, problem selection criteria
├── library/                 ← your paper library (symlink or local, gitignored)
│   ├── papers/<key>/        ← one dir per paper: paper.pdf, summary.md, extracted.md
│   ├── library.bib          ← all bib entries
│   └── keywords.txt         ← controlled vocabulary for tagging
└── projects/
    └── <name>/              ← independent git repo (gitignored by research-buddy)
        ├── plan.md          ← living document: problem, hypotheses, experiments, outline
        ├── decisions.md     ← append-only decision log
        ├── theory/          ← one .tex file per result
        ├── experiments/     ← numbered experiment directories
        └── paper/           ← manuscript drafts and figures
```

Each project is its own git repo — push it wherever you like. The library can also be a separate repo (or a Dropbox folder, etc.).

## Paper library

The library is a structured collection of research papers that gives Claude persistent knowledge of the literature. It lives in `library/` (created during setup, or symlinked to an existing folder like Dropbox).

### How papers get in

There are two ways:

1. **Manual ingestion** — drop a PDF in `library/inbox/` and run `/ingest-paper`. Claude reads the full paper and creates:
   - `library/papers/<author-YYYY-keyword>/paper.pdf` — the original
   - `library/papers/<author-YYYY-keyword>/summary.md` — structured overview (key contribution, method, results, connections to other papers)
   - `library/papers/<author-YYYY-keyword>/extracted.md` — complete extraction (all sections, equations, figures, tables)
   - A BibTeX entry appended to `library/library.bib`

2. **During literature review** — `/lit-review` uses `scripts/find-papers.py` to search Semantic Scholar and OpenAlex via keyword search, citation graph traversal (references + cited-by), and paper similarity recommendations. Open-access PDFs are downloaded automatically; for paywalled papers, Claude writes Google Scholar links to `decisions.md` so you can grab them manually.

   Downloaded papers are triaged by citation count: highly-cited papers (≥50 citations) go straight to `library/inbox/` for ingestion, while less-cited ones land in `library/inbox/.staging/` for you to review first. After searching, Claude reviews `.staging/`, keeps what looks relevant, and discards the rest — then ingests the survivors.

For batch processing (e.g., ingesting a pile of PDFs), run `scripts/ingest-batch.sh library/inbox/`.

### How the library is used

Once a paper is ingested, Claude can use it in any conversation:
- `/lit-review` searches `library.bib` by keyword before hitting external APIs, and reads `summary.md` files to understand what you already know
- `/ingest-paper` greps for related papers and notes connections in each new summary
- `/write` cites only from `library/library.bib` — no hallucinated references
- `/plan` and `/brainstorm` draw on the library to ground suggestions in real literature

Papers are tagged with keywords from `library/keywords.txt` (a controlled vocabulary that grows as you ingest papers in new areas).

### Structure

```
library/
├── papers/
│   ├── brunton-2016-sindy/
│   │   ├── paper.pdf
│   │   ├── summary.md
│   │   └── extracted.md
│   └── ...
├── inbox/               ← drop PDFs here for ingestion
│   ├── .processed/      ← ingested PDFs are moved/backed up here
│   └── .staging/        ← papers under consideration
├── library.bib          ← all BibTeX entries
├── keywords.txt         ← tags that let Claude search the library more efficiently
├── ingestion-log.md     ← history of what was ingested and when
└── TEMPLATE.md          ← format for summary.md files
```

## Unattended mode

If you're feeling a little wild, you can let your new buddy run for longer periods of time:

```bash
./scripts/run-pipeline.sh projects/my-project
```

This launches Claude Code headless on the full pipeline: lit review → plan → theory → experiment → write → critique loop. Progress is logged to `projects/my-project/logs/`.

## Customization

- **`research/research-context.md`** — your background, lab capabilities, and research interests. Skills use this to filter for relevance.
- **`research/writing-style.md`** — writing conventions. Edit to match your style or venue requirements.
- **`research/problem-selection.md`** — criteria for evaluating research problems. Used by `/brainstorm` and `/reassess`.
- **`research/problem-repository.md`** — running list of problems. Updated automatically during paper ingestion and brainstorming.

## License

MIT
