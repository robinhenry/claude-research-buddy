---
description: "Ingest research paper PDFs into the library. Use when the user says 'ingest this paper', 'add this paper', 'process this PDF', or 'ingest inbox' for batch processing."
---

# Ingest Paper

`$ARGUMENTS` — a PDF path, OR "inbox" to batch-process all PDFs in `library/inbox/`.

**Batch mode:** Run `scripts/ingest-batch.sh` — it launches parallel `claude -p` processes (4 at a time by default). Or run `scripts/ingest-batch.sh library/inbox/ 8` for more parallelism.

## Steps

1. **Check for duplicates.** Grep `library/library.bib` for the paper's DOI or title. If found, skip and report.

2. **Read the PDF** using the Read tool (page chunks for >10 pages). Read the entire paper. **Only extract what is in the PDF** — never reconstruct from training data.

3. **Create `library/papers/<author-YYYY-keyword>/`** (e.g., `brunton-2016-sindy`) with:
   - `paper.pdf` — copy of the original
   - `extracted.md` — complete structured extraction. Paraphrase prose (don't copy verbatim). Preserve equations, tables, figure captions.
   - `summary.md` — following `library/TEMPLATE.md` format. In "Notes & open questions", grep the library for related papers and note connections. If the paper highlights or makes tractable any important open problems (read `research/research-context.md` for what matters to us), append them to `research/problem-repository.md`.

4. **Append bib entry** to `library/library.bib` (key = folder name). Include a `keywords` field — pick from `library/keywords.txt`. Only add a new keyword if nothing existing fits, and append it to `keywords.txt` alphabetically.

5. **Append to `library/ingestion-log.md`**: `- YYYY-MM-DD: <bib-key> — <paper title>`

6. **Clean up:** `mv "<pdf>" library/inbox/.processed/`

7. **Commit and push:** `cd library && git add papers/<bib-key>/ library.bib keywords.txt ingestion-log.md && git commit -m "Ingest: <bib-key>" && git push`
