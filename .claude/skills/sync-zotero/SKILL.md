---
description: "Pull eligible papers from Zotero into library/ for ingestion. Zotero is the master library; this skill stages PDFs into library/inbox/ and runs ingest-batch.sh. Use when the user says 'sync zotero', 'pull from zotero', or '/sync-zotero'."
---

# Sync Zotero

`$ARGUMENTS` — empty to do a full sync, or `--dry-run` to just list candidates without downloading.

## Tag conventions in Zotero (set manually by you)

- *(no tag)* — eligible for ingestion into `library/`.
- `lib:skip` — never ingest.
- `lib:print` — also copy the PDF to `library/to-print/` for physical printing.

All other Zotero tags are ignored. Library keywords are assigned by `ingest-paper` from `library/keywords.txt` as today.

## Steps

1. **Run** `poetry run python scripts/zotero_pull.py $ARGUMENTS`. This script does the full sync: smoke-tests Zotero + Better BibTeX, lists candidates, downloads PDFs (+ `.citekey` sidecars) to `library/inbox/`, copies `lib:print`-tagged PDFs to `library/to-print/`, and prints a summary. On `--dry-run` it only lists candidates.

2. **If the script staged any PDFs** (and not `--dry-run`), invoke `scripts/ingest-batch.sh library/inbox/` to extract them. The existing `ingest-paper` skill picks up the citekey from each `.citekey` sidecar so the resulting `library/papers/<citekey>/` folder matches the Zotero BBT key.

3. **Report** what was synced. The script's stdout already prints a summary; surface it to the user.

## Requirements

- Zotero desktop running with local API enabled (Settings → Advanced → "Allow other applications to communicate with Zotero").
- [Better BibTeX](https://retorque.re/zotero-better-bibtex/) plugin installed (provides stable citekeys via JSON-RPC).
- `pyzotero` installed (`poetry install`).
