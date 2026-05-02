#!/usr/bin/env bash
# Installiert comptext-rtx-hook in Git Bash ~/.bashrc (Windows MINGW64)

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)"

cat >> ~/.bashrc << EOF

# === CompText RTX Hook (Git Bash) ===
export COMPTEXT_RUNTIME_DIR="$REPO_DIR"
ctr() {
    local cmd="\$*"
    (cd "\$COMPTEXT_RUNTIME_DIR" && eval "\$cmd" | python -m runtime.cli --cmd "\$cmd")
}
alias ctr-git='ctr git'
alias ctr-pytest='ctr python -m pytest'
alias ctr-log='ctr tail -n 100'
# ====================================
EOF

echo "[comptext-runtime] Hook in ~/.bashrc eingetragen (Git Bash)."
echo "Starte neue Shell oder: source ~/.bashrc"
