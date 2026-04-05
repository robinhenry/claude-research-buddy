#!/usr/bin/env bash
set -euo pipefail

# init.sh — Create a new research project.
# Usage: init.sh <project-name> [plan.md]

BUDDY_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_NAME="${1:?Usage: $0 <project-name> [path/to/plan.md]}"
PROBLEM_FILE="${2:-}"

PROJECT_DIR="$BUDDY_ROOT/projects/$PROJECT_NAME"

[[ ! -d "$PROJECT_DIR" ]] || { echo "Error: Project '$PROJECT_NAME' already exists"; exit 1; }

mkdir -p "$PROJECT_DIR"/{experiments,paper/{figures,drafts},theory}
touch "$PROJECT_DIR/paper/references.bib"

if [[ -n "$PROBLEM_FILE" ]]; then
    [[ -f "$PROBLEM_FILE" ]] || { echo "Error: $PROBLEM_FILE not found"; exit 1; }
    cp "$PROBLEM_FILE" "$PROJECT_DIR/plan.md"
else
    cat > "$PROJECT_DIR/plan.md" << 'EOF'
# Problem Statement

<!-- Describe the research problem you want to work on. -->
<!-- What's the question? Why does it matter? What's the gap in existing work? -->
<!-- This file will evolve into your full research plan via /plan. -->

<!-- Target audience (e.g., "machine learning researchers familiar with optimization -->
<!-- but not with biology"). /write uses this to calibrate the paper's tone and -->
<!-- level of explanation. -->
EOF
fi

cat > "$PROJECT_DIR/decisions.md" << 'EOF'
# Decision Log

<!-- Append-only. Every change, pivot, or question, with date and reason. -->
EOF

cat > "$PROJECT_DIR/.gitignore" << 'EOF'
logs/
experiments/*/results/*.pkl
experiments/*/results/*.npz
experiments/*/results/*.npy
EOF

# Initialize as independent git repo
cd "$PROJECT_DIR"
git init -q
git add -A
git commit -q -m "Init project: $PROJECT_NAME"

echo "Created project: $PROJECT_DIR"
echo "Project is a git repo — push it wherever you like."
echo "Next: open Claude Code and run /lit-review projects/$PROJECT_NAME"
