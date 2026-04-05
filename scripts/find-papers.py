#!/usr/bin/env python3
"""find-papers.py — Search for academic papers via Semantic Scholar and OpenAlex.

Usage:
    find-papers.py search "query" [--download] [--mode both|foundational|recent] [--source s2|openalex|both]
    find-papers.py refs <paper_id_or_doi> [--download] [--limit 100]
    find-papers.py cited-by <paper_id_or_doi> [--download] [--limit 100]
    find-papers.py similar <paper_id_or_doi> [--download] [--limit 20]
    find-papers.py similar --from-bib library/library.bib --keywords "system-identification" [--download]

Set S2_API_KEY env var for higher daily quota.
Rate limit is 1 req/sec regardless of API key — enforced via lockfile.
"""

import argparse
import fcntl
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# --- Config ---

BUDDY_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INBOX = BUDDY_ROOT / "library" / "inbox"
S2_API = "https://api.semanticscholar.org/graph/v1"
S2_REC_API = "https://api.semanticscholar.org/recommendations/v1"
OA_API = "https://api.openalex.org"
S2_FIELDS = "paperId,title,authors,year,abstract,citationCount,isOpenAccess,openAccessPdf,externalIds"
AUTO_INGEST_CITATION_THRESHOLD = 50  # papers above this go to inbox; below go to .staging
MAX_RETRIES = 3

# Set in main() after load_env()
API_KEY = ""
S2_RATE_LIMIT = 1.1  # seconds between S2 API calls (limit is 1 req/sec)
S2_LOCK_FILE = Path("/tmp/research-buddy-s2-ratelimit.lock")
USER_AGENT = "research-buddy/0.2"


def _s2_wait_for_slot():
    """Wait until at least S2_RATE_LIMIT seconds since the last S2 request."""
    S2_LOCK_FILE.touch(exist_ok=True)
    with open(S2_LOCK_FILE, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            last = float(f.read().strip() or "0")
        except ValueError:
            last = 0
        wait = S2_RATE_LIMIT - (time.time() - last)
        if wait > 0:
            time.sleep(min(wait, S2_RATE_LIMIT))  # cap to prevent clock-jump issues


def _s2_record_request():
    """Record that an S2 request was just made. Call while lock is still held."""
    with open(S2_LOCK_FILE, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        f.write(str(time.time()))
        f.truncate()


def load_env():
    env_file = BUDDY_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


# --- HTTP helpers ---

def s2_headers() -> dict[str, str]:
    headers = {"User-Agent": USER_AGENT}
    if API_KEY:
        headers["x-api-key"] = API_KEY
    return headers


def oa_headers() -> dict[str, str]:
    email = os.environ.get("CONTACT_EMAIL", "")
    ua = USER_AGENT
    if email:
        ua += f" (mailto:{email})"
    return {"User-Agent": ua}


def _http_request(url: str, headers: dict, body: dict | None = None, is_s2: bool = False) -> dict | list | None:
    """Shared HTTP helper with retry logic and S2 rate limiting."""
    if is_s2:
        _s2_wait_for_slot()
    if body is not None:
        data = json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, headers={**headers, "Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url, headers=headers)
    for attempt in range(MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                result = json.loads(resp.read())
            if is_s2:
                _s2_record_request()
            return result
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES:
                wait = 5 * (attempt + 1)
                print(f"    Rate limited — waiting {wait}s...")
                time.sleep(wait)
                continue
            print(f"    API error {e.code}: {e.reason}")
            return None
        except Exception as e:
            print(f"    Error: {e}")
            return None
    return None


# --- Display & download ---

def format_authors(authors: list[dict]) -> str:
    if not authors:
        return "Unknown"
    names = [a.get("name", "?") for a in authors[:3]]
    suffix = " et al." if len(authors) > 3 else ""
    return ", ".join(names) + suffix


def make_pdf_filename(paper: dict) -> str:
    first_author = (paper.get("authors") or [{}])[0].get("name", "unknown")
    last_name = first_author.split()[-1].lower() if first_author else "unknown"
    title = paper.get("title", "untitled")
    title_slug = re.sub(r"[^a-z0-9]+", "-", title.lower())[:40].strip("-")
    year = paper.get("year", "unknown")
    return f"{last_name}_{year}_{title_slug}.pdf"


def download_pdf(url: str, filename: str, dest_dir: Path) -> bool:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename
    if dest.exists():
        print(f"      Already exists: {dest.name}")
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
        if not content[:5].startswith(b"%PDF"):
            print(f"      Not a PDF (got HTML redirect?) — skipping")
            return False
        dest.write_bytes(content)
        print(f"      Downloaded: {dest.name}")
        return True
    except Exception as e:
        print(f"      Download failed: {e}")
        return False


def print_paper(i: int, paper: dict, do_download: bool, inbox: Path | None) -> None:
    title = paper.get("title", "Untitled")
    authors = format_authors(paper.get("authors", []))
    year = paper.get("year", "?")
    cites = paper.get("citationCount", 0) or 0
    pdf_url = (paper.get("openAccessPdf") or {}).get("url", "")
    doi = (paper.get("externalIds") or {}).get("DOI", "")

    oa_tag = " [OA]" if paper.get("isOpenAccess") else ""
    pdf_tag = " [PDF]" if pdf_url else ""

    print(f"  {i:2d}. {title}")
    print(f"      {authors} ({year}) — {cites:,} citations{oa_tag}{pdf_tag}")
    if doi:
        print(f"      DOI: {doi}")
    if paper.get("abstract"):
        print(f"      {paper['abstract'][:150].replace(chr(10), ' ')}...")

    if do_download and pdf_url and inbox:
        if cites >= AUTO_INGEST_CITATION_THRESHOLD:
            dest = inbox
            print(f"      → inbox (auto-ingest: {cites:,} citations)")
        else:
            dest = inbox / ".staging"
            print(f"      → staging ({cites:,} citations)")
        download_pdf(pdf_url, make_pdf_filename(paper), dest)
    print()


def print_results(papers: list[dict], label: str, do_download: bool, inbox: Path | None) -> None:
    if not papers:
        print(f"\n  [{label}] No results found.")
        return
    print(f"\n  [{label}] {len(papers)} results:\n")
    for i, p in enumerate(papers, 1):
        print_paper(i, p, do_download, inbox)


def dedup(papers: list[dict], seen: set[str]) -> list[dict]:
    out = []
    for p in papers:
        pid = p.get("paperId", "")
        if pid and pid not in seen:
            seen.add(pid)
            out.append(p)
    return out


# --- S2 API functions ---

def s2_search(query: str, limit: int = 10, year_range: str | None = None) -> list[dict]:
    params: dict[str, str | int] = {"query": query, "limit": limit, "fields": S2_FIELDS}
    if year_range:
        params["year"] = year_range
    data = _http_request(f"{S2_API}/paper/search?{urllib.parse.urlencode(params)}", s2_headers(), is_s2=True)
    return (data or {}).get("data", []) if isinstance(data, dict) else []


def s2_references(paper_id: str, limit: int = 100) -> list[dict]:
    """Papers cited BY the given paper."""
    params = {"fields": S2_FIELDS, "limit": limit}
    data = _http_request(f"{S2_API}/paper/{paper_id}/references?{urllib.parse.urlencode(params)}", s2_headers(), is_s2=True)
    return [r["citedPaper"] for r in (data or {}).get("data", []) if r.get("citedPaper", {}).get("title")]


def s2_citations(paper_id: str, limit: int = 100, year_from: str | None = None) -> list[dict]:
    """Papers that CITE the given paper."""
    params: dict[str, str | int] = {"fields": S2_FIELDS, "limit": limit}
    if year_from:
        params["publicationDateOrYear"] = f"{year_from}-"
    data = _http_request(f"{S2_API}/paper/{paper_id}/citations?{urllib.parse.urlencode(params)}", s2_headers(), is_s2=True)
    return [r["citingPaper"] for r in (data or {}).get("data", []) if r.get("citingPaper", {}).get("title")]


def s2_similar(paper_id: str, limit: int = 20) -> list[dict]:
    """Single-paper recommendations."""
    params = {"fields": S2_FIELDS, "limit": limit}
    data = _http_request(f"{S2_REC_API}/papers/forpaper/{paper_id}?{urllib.parse.urlencode(params)}", s2_headers(), is_s2=True)
    return (data or {}).get("recommendedPapers", [])


def s2_similar_multi(paper_ids: list[str], limit: int = 20) -> list[dict]:
    """Multi-paper recommendations."""
    params = {"fields": S2_FIELDS, "limit": limit}
    body = {"positivePaperIds": paper_ids, "negativePaperIds": []}
    data = _http_request(f"{S2_REC_API}/papers/?{urllib.parse.urlencode(params)}", s2_headers(), body=body, is_s2=True)
    return (data or {}).get("recommendedPapers", [])


# --- OpenAlex ---

def oa_normalize(work: dict) -> dict:
    """Convert OpenAlex work to S2-like dict for unified display."""
    authships = work.get("authorships", [])
    authors = [{"name": a.get("author", {}).get("display_name", "?")} for a in authships]
    oa_url = ""
    oa_status = work.get("open_access", {})
    if oa_status.get("oa_url"):
        oa_url = oa_status["oa_url"]
    return {
        "paperId": work.get("id", ""),
        "title": work.get("title", "Untitled"),
        "authors": authors,
        "year": work.get("publication_year"),
        "abstract": work.get("abstract") or "",  # Only available if abstract_inverted_index is decoded
        "citationCount": work.get("cited_by_count", 0),
        "isOpenAccess": oa_status.get("is_oa", False),
        "openAccessPdf": {"url": oa_url} if oa_url else None,
        "externalIds": {"DOI": work.get("doi", "").replace("https://doi.org/", "") if work.get("doi") else ""},
    }


def oa_search(query: str, limit: int = 10, year_range: str | None = None) -> list[dict]:
    params: dict[str, str | int] = {"search": query, "per_page": min(limit, 50)}
    filters = []
    if year_range:
        # year_range is like "2021-" or "2019-2023"
        filters.append(f"publication_year:{year_range.rstrip('-')}-")
    if filters:
        params["filter"] = ",".join(filters)
    url = f"{OA_API}/works?{urllib.parse.urlencode(params)}"
    data = _http_request(url, oa_headers())
    return [oa_normalize(w) for w in (data or {}).get("results", [])]


# --- Bib parsing ---

def parse_bib_for_seeds(bib_path: str, keywords: list[str] | None = None) -> list[dict]:
    """Extract DOIs and paper IDs from a .bib file, optionally filtered by keywords."""
    text = Path(bib_path).read_text()
    # Split into individual entries
    raw_entries = re.split(r"\n(?=@)", text)
    results = []
    for entry in raw_entries:
        key_m = re.match(r"@\w+\{([^,]+),", entry)
        if not key_m:
            continue
        key = key_m.group(1).strip()
        doi_m = re.search(r"doi\s*=\s*\{([^}]*)\}", entry)
        kw_m = re.search(r"keywords\s*=\s*\{([^}]*)\}", entry)
        doi = doi_m.group(1).strip() if doi_m else ""
        kw = kw_m.group(1).strip() if kw_m else ""
        if keywords:
            entry_kw = {k.strip() for k in kw.split(",")} if kw else set()
            if not any(k in entry_kw for k in keywords):
                continue
        if doi:
            doi = re.sub(r"^https?://doi\.org/", "", doi)
            doi = re.sub(r"^arXiv:", "", doi)
            results.append({"key": key, "doi": doi, "paper_id": f"DOI:{doi}"})
    return results


# --- Subcommands ---

def cmd_search(args, inbox):
    from datetime import datetime

    sources = getattr(args, "source", "s2")
    phases: list[tuple[str, str | None]] = []
    if args.mode in ("both", "foundational"):
        phases.append(("Foundational", None))
    if args.mode in ("both", "recent"):
        phases.append(("Recent", f"{datetime.now().year - 5}-"))

    seen: set[str] = set()
    for label, year_range in phases:
        all_results: list[dict] = []

        for query in args.queries:
            if sources in ("s2", "both"):
                print(f"\n  S2 {label}: \"{query}\"")
                all_results.extend(dedup(s2_search(query, limit=args.limit, year_range=year_range), seen))
            if sources in ("openalex", "both"):
                print(f"\n  OpenAlex {label}: \"{query}\"")
                all_results.extend(dedup(oa_search(query, limit=args.limit, year_range=year_range), seen))

        if label == "Foundational":
            all_results.sort(key=lambda p: p.get("citationCount", 0) or 0, reverse=True)
        else:
            all_results.sort(key=lambda p: (p.get("year", 0) or 0, p.get("citationCount", 0) or 0), reverse=True)
        print_results(all_results, label, args.download, inbox)


def cmd_refs(args, inbox):
    print(f"\n  References of: {args.paper_id}")
    papers = s2_references(args.paper_id, limit=args.limit)
    papers.sort(key=lambda p: p.get("citationCount", 0) or 0, reverse=True)
    print_results(papers, f"References ({len(papers)})", args.download, inbox)


def cmd_cited_by(args, inbox):
    print(f"\n  Citations of: {args.paper_id}")
    papers = s2_citations(args.paper_id, limit=args.limit)
    papers.sort(key=lambda p: p.get("citationCount", 0) or 0, reverse=True)
    print_results(papers, f"Cited by ({len(papers)})", args.download, inbox)


def cmd_similar(args, inbox):
    if getattr(args, "from_bib", None):
        kw = [k.strip() for k in args.keywords.split(",")] if args.keywords else None
        seeds = parse_bib_for_seeds(args.from_bib, kw)
        if not seeds:
            print("No matching papers found in bib file")
            return
        print(f"\n  Multi-paper recommendations from {len(seeds)} seeds:")
        for s in seeds[:10]:
            print(f"    - {s['key']} ({s['doi']})")
        paper_ids = [s["paper_id"] for s in seeds[:20]]  # API limit
        papers = s2_similar_multi(paper_ids, limit=args.limit)
    elif args.paper_id:
        print(f"\n  Similar to: {args.paper_id}")
        papers = s2_similar(args.paper_id, limit=args.limit)
    else:
        print("Error: provide a paper_id or --from-bib")
        return

    papers.sort(key=lambda p: p.get("citationCount", 0) or 0, reverse=True)
    print_results(papers, f"Similar ({len(papers)})", args.download, inbox)


# --- Main ---

def main():
    global API_KEY
    load_env()
    API_KEY = os.environ.get("S2_API_KEY", "")

    parser = argparse.ArgumentParser(description="Search for academic papers")
    parser.add_argument("--download", action="store_true", help="Download open-access PDFs")
    parser.add_argument("--inbox", type=str, default=None, help=f"Download path (default: {DEFAULT_INBOX})")
    sub = parser.add_subparsers(dest="command", required=True)

    # search
    p_search = sub.add_parser("search", help="Keyword search")
    p_search.add_argument("queries", nargs="+", help="Search queries")
    p_search.add_argument("--mode", choices=["both", "foundational", "recent"], default="both")
    p_search.add_argument("--limit", type=int, default=10)
    p_search.add_argument("--source", choices=["s2", "openalex", "both"], default="both")

    # refs
    p_refs = sub.add_parser("refs", help="Papers cited by a given paper")
    p_refs.add_argument("paper_id", help="S2 paper ID, DOI, or DOI:xxx")
    p_refs.add_argument("--limit", type=int, default=100)

    # cited-by
    p_cited = sub.add_parser("cited-by", help="Papers that cite a given paper")
    p_cited.add_argument("paper_id", help="S2 paper ID, DOI, or DOI:xxx")
    p_cited.add_argument("--limit", type=int, default=100)

    # similar
    p_sim = sub.add_parser("similar", help="Find similar papers")
    p_sim.add_argument("paper_id", nargs="?", help="S2 paper ID or DOI")
    p_sim.add_argument("--from-bib", type=str, help="Use papers from a .bib file as seeds")
    p_sim.add_argument("--keywords", type=str, help="Filter bib seeds by keyword (comma-separated)")
    p_sim.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()
    inbox = Path(args.inbox) if args.inbox else DEFAULT_INBOX

    if API_KEY:
        print("Using S2 API key")
    else:
        print("No S2_API_KEY — free tier (1 req/sec)")

    if args.command == "search":
        cmd_search(args, inbox)
    elif args.command == "refs":
        cmd_refs(args, inbox)
    elif args.command == "cited-by":
        cmd_cited_by(args, inbox)
    elif args.command == "similar":
        cmd_similar(args, inbox)

    if args.download and inbox and inbox.exists():
        pdfs = list(inbox.glob("*.pdf"))
        if pdfs:
            print(f"\nPDFs in inbox — ingest with: /ingest-paper <path>")
            for pdf in sorted(pdfs):
                print(f"  {pdf.name}")


if __name__ == "__main__":
    main()
