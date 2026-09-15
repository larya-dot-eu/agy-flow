#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_EXEC="python3"

if ! command -v "$PYTHON_EXEC" &>/dev/null; then
  echo "❌ Error: python3 is required to run flow-init." >&2
  exit 1
fi

exec "$PYTHON_EXEC" "$SCRIPT_DIR/flow_init.py" "$@"
