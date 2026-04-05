#!/usr/bin/env bash
set -euo pipefail

# ingest-batch.sh — Ingest all PDFs in a directory in parallel.
# Usage: ingest-batch.sh [directory]  (default: library/inbox/)

BUDDY_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="${1:-$BUDDY_ROOT/library/inbox}"
MAX_PARALLEL="${2:-4}"

shopt -s nullglob
pdfs=("$DIR"/*.pdf)
shopt -u nullglob

if [[ ${#pdfs[@]} -eq 0 ]]; then
    echo "No PDFs in $DIR"
    exit 0
fi

echo "Ingesting ${#pdfs[@]} papers (${MAX_PARALLEL} parallel)..."

export BUDDY_ROOT
printf '%s\n' "${pdfs[@]}" | xargs -P "$MAX_PARALLEL" -I {} bash -c '
    cd "$BUDDY_ROOT"
    pdf="{}"
    name="$(basename "$pdf")"
    echo "  Starting: $name"
    if env -u CLAUDECODE claude -p "/ingest-paper $pdf" \
        --allowedTools Read,Write,Edit,Grep,Glob,Bash \
        > /dev/null 2>&1; then
        echo "  Done: $name"
    else
        echo "  FAILED: $name"
    fi
'

echo "Batch complete."
