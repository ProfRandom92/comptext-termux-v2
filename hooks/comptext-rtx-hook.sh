#!/usr/bin/env bash
# CompText RTX Hook
# Schleust Shell-Output durch comptext-runtime bevor er an Claude Code / LLM geht.
# Usage: <cmd> | bash hooks/comptext-rtx-hook.sh --cmd "<cmd>"
#
# Termux-Install:   bash scripts/install_hook_termux.sh
# Git Bash Install:  bash scripts/install_hook_gitbash.sh

CMD="${1:-}"
PROFILE="${2:-}"
RUNTIME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    cat
    exit 0
fi

cd "$RUNTIME_DIR" || exit 0

if [ -n "$PROFILE" ]; then
    $PYTHON -m runtime.cli --cmd "$CMD" --profile "$PROFILE"
else
    $PYTHON -m runtime.cli --cmd "$CMD"
fi
