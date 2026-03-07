#!/bin/bash
# ═══════════════════════════════════════════════════════════
#  PROMETHEUS AI — Setup Script (Linux / macOS)
# ═══════════════════════════════════════════════════════════
set -e

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║        PROMETHEUS AI  v12.0  Setup Script            ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "[ERROR] Python 3 not found. Install from python.org"
  exit 1
fi
echo "[OK] Python: $(python3 --version)"

# Create .env from example if needed
if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "[OK] Created .env from .env.example"
    echo ""
    echo "  ⚠️  IMPORTANT: Edit .env and add your Groq API key"
    echo "     Get it FREE at: https://console.groq.com/keys"
    echo "     Then run this script again."
    echo ""
  fi
fi

# Create virtual environment
if [ ! -d ".venv" ]; then
  echo "[...] Creating virtual environment..."
  python3 -m venv .venv
  echo "[OK] Virtual environment created"
fi

# Activate venv
source .venv/bin/activate
echo "[OK] Virtual environment activated"

# Install dependencies
echo "[...] Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "[OK] Dependencies installed"

# Create directories
mkdir -p outputs built_agents prometheus_memory core_versions
touch outputs/.gitkeep built_agents/.gitkeep prometheus_memory/.gitkeep core_versions/.gitkeep
echo "[OK] Directories ready"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  Setup complete! Start the app:                      ║"
echo "║                                                      ║"
echo "║    source .venv/bin/activate                         ║"
echo "║    python app.py                                     ║"
echo "║                                                      ║"
echo "║  Then open: http://localhost:5000                    ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
