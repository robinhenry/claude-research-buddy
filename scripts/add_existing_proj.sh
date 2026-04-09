#!/usr/bin/env bash
set -euo pipefail

# add_existing_proj.sh — Symlink an existing local git repo into projects/
# and scaffold any missing research-buddy structure into it.
# Usage: add_existing_proj.sh <path/to/existing-repo> [project-name]

BUDDY_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_PATH="${1:?Usage: $0 <path/to/existing-repo> [project-name]}"
REPO_PATH="$(cd "$REPO_PATH" && pwd)"  # resolve to absolute path

# Derive project name from repo directory name if not provided
PROJECT_NAME="${2:-$(basename "$REPO_PATH")}"
PROJECT_LINK="$BUDDY_ROOT/projects/$PROJECT_NAME"

# --- Validate ---
[[ -d "$REPO_PATH" ]] || { echo "Error: '$REPO_PATH' is not a directory"; exit 1; }
[[ -d "$REPO_PATH/.git" ]] || { echo "Error: '$REPO_PATH' is not a git repository"; exit 1; }
[[ ! -e "$PROJECT_LINK" ]] || { echo "Error: projects/$PROJECT_NAME already exists"; exit 1; }

# --- Symlink ---
mkdir -p "$BUDDY_ROOT/projects"
ln -s "$REPO_PATH" "$PROJECT_LINK"
echo "Symlinked projects/$PROJECT_NAME → $REPO_PATH"

# --- Scaffold missing structure (never overwrites existing files) ---
echo "Scaffolding missing research-buddy structure..."

mkdir -p "$REPO_PATH/experiments"
mkdir -p "$REPO_PATH/paper/figures"
mkdir -p "$REPO_PATH/paper/drafts"
mkdir -p "$REPO_PATH/theory"

[[ -f "$REPO_PATH/paper/references.bib" ]] || touch "$REPO_PATH/paper/references.bib"

if [[ ! -f "$REPO_PATH/plan.md" ]]; then
    cat > "$REPO_PATH/plan.md" << 'EOF'
# Problem Statement

<!-- Describe the research problem you want to work on. -->
<!-- What's the question? Why does it matter? What's the gap in existing work? -->
<!-- This file will evolve into your full research plan via /plan. -->

<!-- Target audience (e.g., "machine learning researchers familiar with optimization -->
<!-- but not with biology"). /write uses this to calibrate the paper's tone and -->
<!-- level of explanation. -->
EOF
    echo "  Created plan.md"
fi

if [[ ! -f "$REPO_PATH/decisions.md" ]]; then
    cat > "$REPO_PATH/decisions.md" << 'EOF'
# Decision Log

<!-- Append-only. Every change, pivot, or question, with date and reason. -->
EOF
    echo "  Created decisions.md"
fi

if [[ ! -f "$REPO_PATH/.gitignore" ]]; then
    cat > "$REPO_PATH/.gitignore" << 'EOF'
logs/
experiments/*/results/*.pkl
experiments/*/results/*.npz
experiments/*/results/*.npy
EOF
    echo "  Created .gitignore"
else
    # Append buddy entries if not already present
    gitignore="$REPO_PATH/.gitignore"
    grep -qF 'experiments/*/results/*.pkl' "$gitignore" || printf '\nlogs/\nexperiments/*/results/*.pkl\nexperiments/*/results/*.npz\nexperiments/*/results/*.npy\n' >> "$gitignore"
    echo "  Updated .gitignore"
fi

echo
echo "Done. Project '$PROJECT_NAME' is ready."
echo "Next: open Claude Code in this directory and run /lit-review projects/$PROJECT_NAME"
