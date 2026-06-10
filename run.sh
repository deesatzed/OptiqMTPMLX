#!/bin/zsh
# Convenience launcher for the Nex CLI app (multi-model OptiQ + MTP + TUI + MCP)
#
# Recommended modern setup (fastest):
#   uv venv .venv
#   uv pip install -e '.[tui]'   # or just -e . if no TUI
#   ./run.sh chat
#
# Or with the classic venv:
#   python -m venv .venv
#   source .venv/bin/activate
#   pip install -e '.[tui]'
#
# Usage examples:
#   ./run.sh chat --model qwen9b --mtp
#   ./run.sh tui
#   ./run.sh agent "your goal" --enable-mtp
#   ./run.sh mcp

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${(%):-%x}")" && pwd)"
cd "$SCRIPT_DIR"

USE_UV=0
if command -v uv >/dev/null 2>&1; then
    USE_UV=1
fi

if [[ $USE_UV -eq 1 ]]; then
    # Prefer uv for everything (much faster on Apple Silicon)
    if [[ ! -d .venv ]]; then
        echo "Creating .venv with uv (recommended)..."
        uv venv .venv
    fi

    # Activate the uv-managed venv for the subprocess
    source .venv/bin/activate

    # Ensure the package + optional TUI is installed (idempotent + fast with uv)
    if ! python -c "import nex; print('nex ready')" >/dev/null 2>&1; then
        echo "Installing nex + optional TUI with uv (fast path)..."
        uv pip install -e '.[tui]' --quiet
    fi

    exec python -m nex "$@"
else
    # Classic fallback
    if [[ ! -d .venv ]]; then
        echo "Error: .venv not found. Create it with:" >&2
        echo "  python -m venv .venv && source .venv/bin/activate && pip install -e '.[tui]'" >&2
        exit 1
    fi

    source .venv/bin/activate

    if ! python -c "import nex" >/dev/null 2>&1; then
        echo "Installing nex (classic path)..."
        pip install -e '.[tui]' --quiet
    fi

    exec python -m nex "$@"
fi
