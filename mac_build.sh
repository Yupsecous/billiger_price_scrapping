#!/bin/bash
set -e

echo "=========================================="
echo "  BilligerPriceChecker — macOS Setup & Build"
echo "=========================================="
echo ""

# ── 1. Check Python ──────────────────────────────────────────────────────────
PY=$(command -v python3 || true)
if [ -z "$PY" ]; then
    echo "ERROR: Python 3 not found."
    echo "  Install via:  brew install python@3.14"
    exit 1
fi
PY_VER=$($PY -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "[OK] Python $PY_VER found at $PY"

# ── 2. Check / install tkinter ───────────────────────────────────────────────
if $PY -c "import tkinter" 2>/dev/null; then
    echo "[OK] tkinter is available"
else
    echo "[!!] tkinter is missing — installing ..."
    if brew install "python-tk@$PY_VER" 2>/dev/null; then
        echo "[OK] tkinter installed via python-tk@$PY_VER"
    else
        echo "     python-tk@$PY_VER not available, trying tcl-tk ..."
        brew install tcl-tk
        brew reinstall "python@$PY_VER"
    fi
    if $PY -c "import tkinter" 2>/dev/null; then
        echo "[OK] tkinter is now available"
    else
        echo "ERROR: tkinter still not working after install."
        echo "  Try: brew install tcl-tk && brew reinstall python@$PY_VER"
        exit 1
    fi
fi

# ── 3. Check / install Google Chrome ─────────────────────────────────────────
if [ -d "/Applications/Google Chrome.app" ]; then
    echo "[OK] Google Chrome found"
else
    echo "[!!] Google Chrome not found — installing via Homebrew ..."
    brew install --cask google-chrome
    if [ -d "/Applications/Google Chrome.app" ]; then
        echo "[OK] Google Chrome installed"
    else
        echo "ERROR: Chrome install failed."
        echo "  Download manually: https://www.google.com/chrome/"
        exit 1
    fi
fi

# ── 4. Create venv if not active ─────────────────────────────────────────────
if [ -z "$VIRTUAL_ENV" ]; then
    if [ ! -d ".venv" ]; then
        echo ""
        echo "Creating virtual environment ..."
        $PY -m venv .venv
    fi
    echo "Activating virtual environment ..."
    source .venv/bin/activate
else
    echo "[OK] Virtual environment active: $VIRTUAL_ENV"
fi

# ── 5. Install dependencies ──────────────────────────────────────────────────
echo ""
echo "Installing Python dependencies ..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pyinstaller -q
echo "[OK] Dependencies installed"

# ── 6. Build ─────────────────────────────────────────────────────────────────
echo ""
echo "Building .app bundle ..."
echo ""
python -m PyInstaller --clean --noconfirm BilligerPriceChecker_mac.spec

echo ""
echo "=========================================="
echo "  BUILD COMPLETE"
echo "=========================================="
echo ""
echo "  Output: dist/BilligerPriceChecker.app"
echo ""
echo "  To install: drag it into /Applications"
echo "  To run:     open dist/BilligerPriceChecker.app"
echo ""
