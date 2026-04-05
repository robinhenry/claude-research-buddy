---
description: "Literature review around a research topic. Searches the local paper library and Semantic Scholar. Use when the user says 'lit review', 'find papers about', 'what do we know about', or 'search for papers on'."
---

# Literature Review

`$ARGUMENTS` — a topic description, or a path to a project's `plan.md`.

Read `research/research-context.md` to filter for relevance throughout. Use `scripts/find-papers.py` for all searches (run with `--help` for full usage).

## Strategy — work outward from what you know

1. **Survey papers first.** Search for reviews on the topic — they map the landscape and give a curated bibliography to chase.
2. **Seeds from library.** Grep `library/library.bib` by keyword/title. Read matching `summary.md` files.
3. **Citation graphs.** For each seed: fetch refs and cited-by (limit to top 20 by citation count). For the 2–3 most central papers found, go a second hop. This is the highest-value step.
4. **Recommendations.** Use `similar` (single paper or `--from-bib` with keyword filter) for papers the graph missed.
5. **Keyword search.** Fill remaining gaps. Try diverse formulations — same concept, different names across fields. S2 has better relevance than OpenAlex for niche queries.
6. **Web search.** Use WebSearch for very recent preprints or when API sources come up short.
7. **Ingest and repeat.** For papers that are highly cited (≥50) OR clearly relevant to the review, ingest via `/ingest-paper`. Leave uncertain papers in `library/inbox/.staging/`. Then repeat from step 2 with new seeds. Stop after 3 rounds or when seeing mostly duplicates.

## Triage staging

After searching, review papers in `library/inbox/.staging/`. Read the filenames (they contain author, year, and title slug). For each, judge whether it's relevant. Move relevant ones to `library/inbox/`. Delete the rest. Then ingest remaining papers: `scripts/ingest-batch.sh`

## Output

Write the literature review as a section in `plan.md`. Include: key papers with bib keys, remaining gaps, connections between papers.

Write to `decisions.md`:
- Brief summary of what was found and ingested
- **Papers to acquire** — clickable Google Scholar links for relevant papers that need manual download: `- [Author YYYY — Title](https://scholar.google.com/scholar?q=<url-encoded+title>)`
