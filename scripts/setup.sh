#!/usr/bin/env bash
set -euo pipefail

# setup.sh — One-time setup for a new research-buddy user.
# Run this after cloning the repo.

BUDDY_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== research-buddy setup ==="
echo

# --- Prerequisites ---
missing=()
command -v python3 >/dev/null 2>&1 || missing+=("python3 (3.11+)")
command -v claude >/dev/null 2>&1  || missing+=("claude (Claude Code CLI)")

if [[ ${#missing[@]} -gt 0 ]]; then
    echo "Missing prerequisites:"
    for m in "${missing[@]}"; do echo "  - $m"; done
    echo
    echo "Install these and re-run setup."
    exit 1
fi

py_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python: $py_version"
echo "Claude CLI: $(command -v claude)"
echo

# --- Research context ---
if [[ ! -f "$BUDDY_ROOT/research/research-context.md" ]]; then
    cp "$BUDDY_ROOT/research/research-context.template.md" \
       "$BUDDY_ROOT/research/research-context.md"
    echo "Created research/research-context.md from template — fill this in with your details."
else
    echo "research/research-context.md already exists, skipping."
fi

if [[ ! -f "$BUDDY_ROOT/research/problem-repository.md" ]]; then
    cp "$BUDDY_ROOT/research/problem-repository.template.md" \
       "$BUDDY_ROOT/research/problem-repository.md"
    echo "Created research/problem-repository.md from template."
else
    echo "research/problem-repository.md already exists, skipping."
fi

echo

# --- Library ---
if [[ -e "$BUDDY_ROOT/library" ]]; then
    echo "library/ already exists, skipping."
else
    echo "No library/ found."
    read -rp "Path to an existing paper library (leave empty to create one here): " lib_path

    if [[ -n "$lib_path" ]]; then
        lib_path="${lib_path/#\~/$HOME}"
        if [[ ! -d "$lib_path" ]]; then
            echo "Error: $lib_path does not exist."
            exit 1
        fi
        ln -s "$lib_path" "$BUDDY_ROOT/library"
        echo "Symlinked library/ → $lib_path"
    else
        mkdir -p "$BUDDY_ROOT/library"/{papers,inbox/.processed,inbox/.staging}
        touch "$BUDDY_ROOT/library/library.bib"
        touch "$BUDDY_ROOT/library/keywords.txt"

        cat > "$BUDDY_ROOT/library/ingestion-log.md" << 'EOF'
# Ingestion Log

<!-- Append-only log of ingested papers. Format: YYYY-MM-DD: bib-key — Title -->
EOF

        cp "$BUDDY_ROOT/library-templates/TEMPLATE.md" "$BUDDY_ROOT/library/TEMPLATE.md"
        echo "Created library/ with empty structure."
    fi
fi

echo

# --- Projects directory ---
mkdir -p "$BUDDY_ROOT/projects"
echo "projects/ directory ready."

# --- Environment ---
if [[ ! -f "$BUDDY_ROOT/.env" ]]; then
    cp "$BUDDY_ROOT/.env.example" "$BUDDY_ROOT/.env"
    echo "Created .env from template — add your Semantic Scholar API key (optional but recommended)."
else
    echo ".env already exists, skipping."
fi

echo
echo "=== Setup complete ==="
echo
echo "Next steps:"
echo "  1. Edit research/research-context.md with your background and capabilities"
echo "  2. (Optional) Add your Semantic Scholar API key to .env"
echo "  3. Create your first project:"
echo "     ./scripts/init.sh my-project path/to/problem-statement.md"
echo "  4. Open Claude Code in this directory and start with:"
echo "     /lit-review projects/my-project"
