#!/usr/bin/env python3
"""Read-only reconciliation between library/papers/ and Zotero.

Produces a report at library/zotero-reconcile.md with:
  - Matched: library folder <-> zotero item <-> proposed BBT citekey
  - Library-only: in library/, missing from Zotero (need manual add to Zotero)
  - Zotero-only: in Zotero, not yet in library/ (next /sync-zotero picks them up)
  - Conflicts: missing DOI, duplicate matches, missing BBT citekey, no PDF, etc.

No writes to library/ or Zotero. Title-similarity is NOT used for auto-matching;
DOI-less library entries are listed as conflicts for manual resolution.
"""
from __future__ import annotations

import re
from pathlib import Path

import httpx
from pyzotero import zotero

REPO_ROOT = Path(__file__).resolve().parent.parent
LIBRARY = REPO_ROOT / "library"
PAPERS = LIBRARY / "papers"
BIB = LIBRARY / "library.bib"
REPORT = LIBRARY / "zotero-reconcile.md"
BBT_RPC = "http://localhost:23119/better-bibtex/json-rpc"


def parse_bib() -> dict[str, dict]:
    """folder_name -> {doi, title}. Folder name == bib key."""
    text = BIB.read_text()
    out: dict[str, dict] = {}
    for m in re.finditer(r"@\w+\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", text, re.DOTALL):
        key, body = m.group(1), m.group(2)
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*[\{\"](.+?)[\}\"]\s*,?\s*\n", body, re.DOTALL):
            fields[fm.group(1).lower()] = fm.group(2).strip()
        out[key] = {"doi": (fields.get("doi") or "").lower().strip(), "title": fields.get("title", "")}
    return out


def fetch_citekeys(zot: zotero.Zotero, item_keys: list[str]) -> dict[str, str]:
    if not item_keys:
        return {}
    r = httpx.post(
        BBT_RPC,
        json={"jsonrpc": "2.0", "method": "item.citationkey", "params": [item_keys], "id": 1},
        timeout=60,
    )
    r.raise_for_status()
    return {k: v for k, v in (r.json().get("result") or {}).items() if v}


def main() -> None:
    zot = zotero.Zotero(library_id=0, library_type="user", api_key="", local=True)
    print("fetching Zotero items...")
    items = zot.everything(zot.top())
    print(f"  {len(items)} items")
    citekey_map = fetch_citekeys(zot, [it["key"] for it in items])

    # Build Zotero side: list of dicts.
    zot_rows: list[dict] = []
    for it in items:
        d = it.get("data", {})
        key = it["key"]
        tags = {t["tag"] for t in d.get("tags", [])}
        zot_rows.append(
            {
                "item_key": key,
                "title": d.get("title", "(untitled)"),
                "doi": (d.get("DOI") or "").lower().strip(),
                "citekey": citekey_map.get(key),
                "lib_skip": "lib:skip" in tags,
            }
        )

    # Library side.
    bib_entries = parse_bib() if BIB.exists() else {}
    folders = sorted(p.name for p in PAPERS.iterdir() if p.is_dir()) if PAPERS.exists() else []

    # Index Zotero by DOI.
    zot_by_doi: dict[str, list[dict]] = {}
    for r in zot_rows:
        if r["doi"]:
            zot_by_doi.setdefault(r["doi"], []).append(r)

    matched: list[tuple[str, dict]] = []
    library_only: list[str] = []
    conflicts: list[str] = []
    matched_zot_keys: set[str] = set()

    for folder in folders:
        bib = bib_entries.get(folder)
        if not bib:
            conflicts.append(f"`{folder}` — no bib entry found in library.bib")
            continue
        doi = bib["doi"]
        if not doi:
            conflicts.append(f"`{folder}` — no DOI in bib entry; cannot auto-match")
            continue
        hits = zot_by_doi.get(doi, [])
        if not hits:
            library_only.append(f"`{folder}` (DOI {doi}) — {bib['title'][:80]}")
            continue
        if len(hits) > 1:
            conflicts.append(
                f"`{folder}` — DOI {doi} matches {len(hits)} Zotero items: "
                + ", ".join(h["item_key"] for h in hits)
            )
            continue
        z = hits[0]
        if not z["citekey"]:
            conflicts.append(
                f"`{folder}` — matched Zotero item {z['item_key']} but it has no BBT citekey"
            )
            continue
        matched.append((folder, z))
        matched_zot_keys.add(z["item_key"])

    # Zotero-only = items not matched to a library folder.
    zotero_only: list[dict] = [
        r for r in zot_rows
        if r["item_key"] not in matched_zot_keys and not r["lib_skip"]
    ]

    # Render report.
    lines = [
        "# Zotero ↔ library/ reconciliation report",
        "",
        "Read-only snapshot. No files were modified.",
        "",
        f"- library folders: {len(folders)}",
        f"- Zotero items: {len(zot_rows)}",
        f"- matched (DOI): {len(matched)}",
        f"- library-only (need to be added to Zotero manually): {len(library_only)}",
        f"- zotero-only (will be picked up by next /sync-zotero): {len(zotero_only)}",
        f"- conflicts (need human review): {len(conflicts)}",
        "",
        "## Matched",
        "",
        "Format: `library folder` → `BBT citekey` (Zotero item key)",
        "",
    ]
    for folder, z in sorted(matched, key=lambda x: x[0]):
        rename_marker = "" if folder == z["citekey"] else " ← RENAME"
        lines.append(f"- `{folder}` → `{z['citekey']}` ({z['item_key']}){rename_marker}")

    lines += ["", "## Library-only (add these to Zotero manually)", ""]
    for line in sorted(library_only):
        lines.append(f"- {line}")

    lines += ["", "## Zotero-only (next /sync-zotero will pull these)", ""]
    for r in sorted(zotero_only, key=lambda x: x["title"]):
        ck = r["citekey"] or "(no BBT citekey)"
        lines.append(f"- `{ck}` ({r['item_key']}) — {r['title'][:80]}")

    lines += ["", "## Conflicts (need human review)", ""]
    for line in conflicts:
        lines.append(f"- {line}")

    REPORT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {REPORT}")
    print(f"  matched: {len(matched)}")
    print(f"  library-only: {len(library_only)}")
    print(f"  zotero-only: {len(zotero_only)}")
    print(f"  conflicts: {len(conflicts)}")


if __name__ == "__main__":
    main()
