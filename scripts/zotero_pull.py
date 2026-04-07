#!/usr/bin/env python3
"""Pull eligible papers from Zotero into library/inbox/ for ingestion.

Zotero is the master library; this script reads it (read-only local API)
and stages PDFs into library/inbox/ named by their Better BibTeX citekey,
with a `.citekey` sidecar so `ingest-paper` adopts the same key.

Tag conventions:
  - (none)    -> eligible
  - lib:skip  -> never ingest
  - lib:print -> also copy PDF to library/to-print/

Requires:
  - Zotero desktop running with local API enabled
  - Better BibTeX plugin installed (for stable citekeys via JSON-RPC)
  - pyzotero
"""
from __future__ import annotations

import sys
from pathlib import Path

import httpx
from pyzotero import zotero

REPO_ROOT = Path(__file__).resolve().parent.parent
LIBRARY = REPO_ROOT / "library"
INBOX = LIBRARY / "inbox"
PAPERS = LIBRARY / "papers"
TO_PRINT = LIBRARY / "to-print"

BBT_RPC = "http://localhost:23119/better-bibtex/json-rpc"


def smoke_test(zot: zotero.Zotero) -> None:
    try:
        zot.items(limit=1)
    except Exception as exc:
        sys.exit(
            f"ERROR: cannot reach Zotero local API. Is Zotero running with "
            f"'Allow other applications to communicate with Zotero' enabled?\n  {exc}"
        )
    try:
        r = httpx.post(
            BBT_RPC,
            json={"jsonrpc": "2.0", "method": "item.citationkey", "params": [["__nope__"]], "id": 1},
            timeout=5,
        )
        r.raise_for_status()
    except Exception as exc:
        sys.exit(
            f"ERROR: Better BibTeX JSON-RPC unreachable at {BBT_RPC}. Install BBT in Zotero.\n  {exc}"
        )


def fetch_citekeys(item_keys: list[str]) -> dict[str, str]:
    """Map Zotero item keys -> BBT citekeys via the JSON-RPC endpoint."""
    if not item_keys:
        return {}
    r = httpx.post(
        BBT_RPC,
        json={"jsonrpc": "2.0", "method": "item.citationkey", "params": [item_keys], "id": 1},
        timeout=30,
    )
    r.raise_for_status()
    result = r.json().get("result") or {}
    return {k: v for k, v in result.items() if v}


def list_candidates(zot: zotero.Zotero) -> list[dict]:
    """Return list of candidate dicts: {item_key, title, citekey, pdf_key, lib_print}."""
    existing = {p.name for p in PAPERS.iterdir() if p.is_dir()} if PAPERS.exists() else set()

    all_items = zot.everything(zot.items())
    tops = [it for it in all_items if not it.get("data", {}).get("parentItem")]
    pdf_by_parent: dict[str, str] = {}
    for it in all_items:
        d = it.get("data", {})
        parent = d.get("parentItem")
        if parent and d.get("itemType") == "attachment" and d.get("contentType") == "application/pdf":
            pdf_by_parent.setdefault(parent, it["key"])

    citekey_map = fetch_citekeys([it["key"] for it in tops])

    candidates = []
    for it in tops:
        key = it["key"]
        data = it.get("data", {})
        tags = {t["tag"] for t in data.get("tags", [])}
        if "lib:skip" in tags:
            continue
        citekey = citekey_map.get(key)
        if not citekey or citekey in existing:
            continue
        pdf_key = pdf_by_parent.get(key)
        if not pdf_key:
            continue
        candidates.append(
            {
                "item_key": key,
                "title": data.get("title", "(untitled)"),
                "citekey": citekey,
                "pdf_key": pdf_key,
                "lib_print": "lib:print" in tags,
            }
        )
    return candidates


def stage(zot: zotero.Zotero, c: dict) -> None:
    INBOX.mkdir(parents=True, exist_ok=True)
    pdf_path = INBOX / f"{c['citekey']}.pdf"
    sidecar = INBOX / f"{c['citekey']}.citekey"
    pdf_bytes = zot.file(c["pdf_key"])
    pdf_path.write_bytes(pdf_bytes)
    sidecar.write_text(c["citekey"] + "\n")
    if c["lib_print"]:
        TO_PRINT.mkdir(parents=True, exist_ok=True)
        (TO_PRINT / f"{c['citekey']}.pdf").write_bytes(pdf_bytes)


def main() -> None:
    dry_run = "--dry-run" in sys.argv[1:]

    zot = zotero.Zotero(library_id=0, library_type="user", api_key="", local=True)
    smoke_test(zot)

    candidates = list_candidates(zot)
    print(f"{len(candidates)} candidate(s) to sync:")
    for c in candidates:
        marker = " [print]" if c["lib_print"] else ""
        print(f"  - {c['citekey']}{marker}  {c['title'][:80]}")

    if dry_run or not candidates:
        return

    print()
    print(f"Staging {len(candidates)} PDF(s) into {INBOX}...")
    for c in candidates:
        stage(zot, c)
        print(f"  staged {c['citekey']}.pdf")
    n_print = sum(1 for c in candidates if c["lib_print"])
    print(f"\nDone. {len(candidates)} staged, {n_print} also copied to {TO_PRINT}.")
    print(f"Next: run `scripts/ingest-batch.sh library/inbox/` to extract.")


if __name__ == "__main__":
    main()
