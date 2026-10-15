#!/bin/zsh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/pyencfsgui-venv"
PYTHON_BIN="${PYTHON:-python3}"

cd "$SCRIPT_DIR"

printf '%s\n' "Running pyencfsgui from source. For normal macOS use, launch pyencfsgui.app instead."

if [ ! -x "$VENV_DIR/bin/python" ]; then
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m ensurepip --upgrade >/dev/null 2>&1 || true

if ! "$VENV_DIR/bin/python" -c "import PyQt5; from crypto_compat import AES" >/dev/null 2>&1; then
    "$VENV_DIR/bin/python" -m pip install --disable-pip-version-check --quiet -r "$SCRIPT_DIR/requirements.txt"
fi

source "$VENV_DIR/bin/activate"
exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/encfsgui.py"
