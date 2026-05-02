#!/usr/bin/env bash
# Installiert comptext-rtx-hook in Termux ~/.bashrc
# Danach: ctr <cmd> | komprimiert Output automatisch

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)"

cat >> ~/.bashrc << EOF

# === CompText RTX Hook ===
export COMPTEXT_RUNTIME_DIR="$REPO_DIR"
ctr() {
    local cmd="\$*"
    (cd "\$COMPTEXT_RUNTIME_DIR" && eval "\$cmd" | python3 -m runtime.cli --cmd "\$cmd")
}
alias ctr-git='ctr git'
alias ctr-pytest='ctr pytest'
alias ctr-log='ctr tail -n 100'
# ==========================
EOF

echo "[comptext-runtime] Hook in ~/.bashrc eingetragen."
echo "Starte neue Shell oder: source ~/.bashrc"
