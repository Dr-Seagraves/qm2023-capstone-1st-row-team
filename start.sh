#!/usr/bin/env bash
# ==========================================================
#  Hurricane x Real-Estate Dashboard – macOS / Linux start
# ==========================================================
set -e
cd "$(dirname "$0")"

# --- Check Python -------------------------------------------
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 is not installed."
    echo "        Install via https://www.python.org/downloads/ or your package manager."
    exit 1
fi

# --- Check / auto-install Node.js ----------------------------
if ! command -v node &>/dev/null; then
    echo "[INFO] Node.js not found — attempting automatic install …"
    if [[ "$(uname)" == "Darwin" ]]; then
        if command -v brew &>/dev/null; then
            brew install node
        else
            echo "[INFO] Homebrew not found — downloading Node.js .pkg …"
            curl -fsSLo /tmp/node.pkg "https://nodejs.org/dist/v22.14.0/node-v22.14.0.pkg"
            sudo installer -pkg /tmp/node.pkg -target /
            rm -f /tmp/node.pkg
        fi
    else
        # Linux
        if command -v apt-get &>/dev/null; then
            sudo apt-get update && sudo apt-get install -y nodejs npm
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y nodejs npm
        else
            echo "[INFO] Installing via nvm …"
            curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
            export NVM_DIR="$HOME/.nvm"
            . "$NVM_DIR/nvm.sh"
            nvm install --lts
        fi
    fi
    # Final check
    if ! command -v node &>/dev/null; then
        echo "[ERROR] Node.js install succeeded but isn't on PATH."
        echo "        Close and reopen your terminal, then try again."
        exit 1
    fi
    echo "[INFO] Node.js $(node --version) installed successfully."
fi

# --- Launch -------------------------------------------------
echo "============================================"
echo "  Starting Hurricane x Real-Estate Dashboard"
echo "============================================"

python3 start.py "$@"
