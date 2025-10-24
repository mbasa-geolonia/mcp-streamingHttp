#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

echo "Creating virtualenv at: $VENV_DIR"
$PYTHON_BIN -m venv "$VENV_DIR"

echo "Activating virtualenv…"
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

echo "Upgrading pip & installing requirements…"
python -m pip install --upgrade pip
pip install -r requirements.txt

cat <<'EOF'

✅ Done.

Activate the environment:
  source .venv/bin/activate

Run the MCP server:
  uvicorn main:app --host 0.0.0.0 --port 8000

Optional env (examples):
  export GEOCODER_BASE="http://marionomac-mini.local"
  export GEOCODER_PATH="/"
  export CORS_ALLOWED_ORIGINS="http://localhost,http://127.0.0.1"
  export REQUEST_TIMEOUT="10.0"

Claude Desktop MCP URL:
  http://localhost:8000/mcp
EOF

