#!/usr/bin/env bash
set -euo pipefail

# run-pipeline.sh — Launch the research pipeline unattended.
# Usage: run-pipeline.sh <project-dir>

PROJECT_DIR="$(realpath "${1:?Usage: $0 <project-dir>}")"
[[ -f "$PROJECT_DIR/plan.md" ]] || { echo "Error: No plan.md in $PROJECT_DIR"; exit 1; }

LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

echo "=== Starting pipeline | $(date '+%Y-%m-%d %H:%M') ==="
echo "  Project: $PROJECT_DIR"

problem=$(<"$PROJECT_DIR/plan.md")

cd "$PROJECT_DIR"
echo "Run /pipeline for this project.

## Problem Statement

$problem" | claude -p \
    --verbose \
    --max-turns 200 \
    --allowedTools 'Read,Write,Edit,Bash,Glob,Grep,Agent,WebSearch,WebFetch' \
    2> >(tee "$LOG_DIR/stderr.log" >&2) \
    | tee "$LOG_DIR/raw.jsonl"

echo "=== Pipeline finished | $(date '+%Y-%m-%d %H:%M') ==="
