---
description: "Ingest a blog post into the library as background reading. Use when the user says 'ingest this blog', 'add this blog post', 'save this post', or provides a URL to an essay/article."
---

# Ingest Blog

`$ARGUMENTS` — a URL to a blog post or essay.

Blogs are stored as **background / primary-source material**. They are NOT citeable references — never write a blog entry to `library/library.bib`, and never create files under `library/papers/`.

## Steps

1. **Check for duplicates.** Grep `library/blogs/blogs.index.md` for the URL. If found, skip and report.

2. **Fetch the post** with WebFetch. Prompt: "Return the main article body as clean markdown. Strip navigation, sidebars, footers, comments, and ads. Preserve headings, code blocks, equations, and links. Also return the title, author (if any), and published date (if visible)."

3. **Pick a key** of the form `<author-or-site>-YYYY-slug` (e.g., `gwern-2020-scaling-hypothesis`, `distill-2018-building-blocks`). Use the site name if no author is given.

4. **Create `library/blogs/<key>/`** with:
   - `source.md` — the fetched markdown, prefixed with a YAML frontmatter block:
     ```
     ---
     title: ...
     author: ...           # or "unknown"
     url: ...
     published_date: ...   # YYYY-MM-DD or "unknown"
     fetched_date: YYYY-MM-DD
     ---
     ```
   - `summary.md` — follow `library/TEMPLATE.md`. Adapt sections naturally to a blog (e.g., "Method" may become "Argument"). In "Notes & open questions", note any connections to papers in `library/papers/`.

5. **Pick keywords** from `library/keywords.txt`. Always include `blog-post`. Only add a new keyword if nothing existing fits, and append it to `keywords.txt` alphabetically.

6. **Append a row to `library/blogs/blogs.index.md`** (create the file with header if missing):
   ```
   | key | title | author | url | published | keywords |
   ```

7. **Append to `library/ingestion-log.md`**: `- YYYY-MM-DD: <key> — <title> (blog)`

8. **Commit and push:** `cd library && git add blogs/<key>/ blogs/blogs.index.md keywords.txt ingestion-log.md && git commit -m "Ingest blog: <key>" && git push`

## Hard rules

- Never touch `library/library.bib`.
- Never create anything under `library/papers/`.
- If the user asks to cite a blog in a paper, refuse and point them at the underlying primary source instead.
