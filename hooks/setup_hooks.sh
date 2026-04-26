#!/bin/bash
# setup_hooks.sh - Configure git hooks for this repository
# Run this once after cloning the repository

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
HOOKS_DIR="$REPO_ROOT/.git/hooks"

# Check if hooks directory already has content (non-sample files)
has_custom_hooks=false
if [ -d "$HOOKS_DIR" ]; then
    for f in "$HOOKS_DIR"/*; do
        if [ -f "$f" ] && [ "${f%.sample}" = "$f" ]; then
            has_custom_hooks=true
            break
        fi
    done
fi

if [ "$has_custom_hooks" = false ]; then
    # No custom hooks, remove the sample files directory
    rm -rf "$HOOKS_DIR"
fi

# Create symlink from .git/hooks to the repo's hooks directory
ln -sf "$REPO_ROOT/hooks" "$HOOKS_DIR"

echo "Git hooks configured. Now server commits will remind you to rebuild macOS app."
