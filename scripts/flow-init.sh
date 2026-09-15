#!/usr/bin/env bash
set -euo pipefail

if command -v realpath &>/dev/null; then
  SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
elif command -v readlink &>/dev/null; then
  SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
else
  SCRIPT_SOURCE="${BASH_SOURCE[0]}"
  while [ -L "$SCRIPT_SOURCE" ]; do
    SCRIPT_DIR="$(cd -P "$(dirname "$SCRIPT_SOURCE")" 2>/dev/null && pwd)"
    SCRIPT_SOURCE="$(readlink "$SCRIPT_SOURCE")"
    [[ $SCRIPT_SOURCE != /* ]] && SCRIPT_SOURCE="$SCRIPT_DIR/$SCRIPT_SOURCE"
  done
  SCRIPT_DIR="$(cd -P "$(dirname "$SCRIPT_SOURCE")" 2>/dev/null && pwd)"
fi
PYTHON_EXEC="python3"

if ! command -v "$PYTHON_EXEC" &>/dev/null; then
  echo "❌ Error: python3 is required to run flow-init." >&2
  exit 1
fi

exec "$PYTHON_EXEC" "$SCRIPT_DIR/flow_init.py" "$@"
