#!/data/data/com.termux/files/usr/bin/bash
# ============================================================================
# CompText Termux Setup
# Ein-Kommando-Setup für das CompText Triage System auf Android/Termux
#
# Ausführen:
#   bash setup_termux.sh
#
# Option A (Default, empfohlen): llama.cpp via tur-repo
# Option B: Build from Source (~10 Minuten, Fallback)
# ============================================================================
set -euo pipefail

REPO_DIR="$HOME/comptext-termux"
DATA_DIR="$REPO_DIR/data"
MODELS_DIR="$REPO_DIR/models"
MODULES_DIR="$REPO_DIR/modules"
BIN_DIR="$HOME/bin"

echo "╔══════════════════════════════════════╗"
echo "║  CompText Termux Setup v2.1          ║"
echo "╚══════════════════════════════════════╝"
echo ""

# --- System-Pakete ---
echo "[1/5] System-Pakete aktualisieren..."
pkg update -y

echo "[2/5] Basis-Pakete installieren..."
pkg install -y git python python-pip

# --- llama.cpp: Option A (tur-repo, 30 Sekunden) ---
echo "[3/5] llama.cpp via tur-repo installieren (Option A)..."
if command -v llama-server &>/dev/null; then
    echo "  ✓ llama-server bereits installiert: $(which llama-server)"
else
    if pkg install -y tur-repo 2>/dev/null && pkg install -y llama-cpp 2>/dev/null; then
        echo "  ✓ llama.cpp via tur-repo installiert"
    else
        echo "  ⚠ tur-repo nicht verfügbar – Fallback: Build from Source"
        echo "     (dauert ~10 Minuten auf A33)"
        pkg install -y cmake clang make openssl
        LLAMA_DIR="$HOME/llama.cpp"
        if [ ! -d "$LLAMA_DIR/.git" ]; then
            git clone --depth 1 https://github.com/ggml-org/llama.cpp.git "$LLAMA_DIR"
        fi
        cd "$LLAMA_DIR"
        cmake -B build \
            -DCMAKE_BUILD_TYPE=Release \
            -DGGML_OPENMP=OFF \
            -DGGML_LLAMAFILE=OFF \
            -DGGML_NATIVE=OFF \
            -DCMAKE_C_FLAGS="-march=armv8-a" \
            -DCMAKE_CXX_FLAGS="-march=armv8-a"
        cmake --build build --config Release -j$(nproc)
        mkdir -p "$BIN_DIR"
        ln -sf "$LLAMA_DIR/build/bin/llama-server" "$BIN_DIR/llama-server"
        echo "  ✓ llama.cpp from Source gebaut"
    fi
fi

# --- Python-Abhängigkeiten ---
echo "[4/5] Python-Pakete installieren..."
pip install --upgrade \
    textual \
    httpx \
    aiosqlite

# --- Verzeichnisstruktur ---
echo "[5/5] Verzeichnisstruktur einrichten..."
mkdir -p "$DATA_DIR" "$MODELS_DIR" "$MODULES_DIR"
touch "$MODULES_DIR/.gitkeep"

# --- Git initialisieren (wenn noch nicht) ---
cd "$REPO_DIR"
if [ ! -d ".git" ]; then
    git init
    git add .
    git commit -m "Initial commit: CompText Termux v2.1"
    echo "  ✓ Git-Repo initialisiert"
fi

# --- DB testen ---
echo ""
echo "Teste Datenbank-Initialisierung..."
python -c "
import asyncio
from med_db import MedDB
from med_codex import MedCodex

async def test():
    db = MedDB()
    await db.init_schema()
    codex = MedCodex()
    count = codex.count()
    expanded = codex.expand_prompt('MAB+HS, RR↓')
    print(f'  ✓ MedDB OK')
    print(f'  ✓ MedCodex: {count} Einträge')
    print(f'  ✓ Expansion: MAB+HS → {expanded[:60]}...')

asyncio.run(test())
"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║  Setup abgeschlossen!                ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Nächste Schritte:"
echo ""
echo "1. MedGemma GGUF laden (einmalig, ~2.5GB):"
echo "   cd ~/comptext-termux/models"
echo "   wget https://huggingface.co/unsloth/medgemma-1.5-4b-it-GGUF/resolve/main/medgemma-1.5-4b-it-Q4_K_M.gguf"
echo ""
echo "2. Tab 1 – LLM-Server starten:"
echo "   llama-server -m ~/comptext-termux/models/*.gguf --port 8080 -c 2048 -t 4"
echo ""
echo "3. Tab 2 – Triage-App starten:"
echo "   python ~/comptext-termux/comptrage.py"
echo ""
echo "4. GitHub-Push (optional):"
echo "   cd ~/comptext-termux"
echo "   git remote add origin https://github.com/ProfRandom92/comptext-termux.git"
echo "   git push -u origin main"
