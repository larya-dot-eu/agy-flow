#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Running Unit Tests ==="
python3 -m unittest "$SCRIPT_DIR/test_skills_unit.py"

echo "=== Running Repository Integrity Scan with Performance SLA ==="
START_TIME=$(date +%s%N)
python3 "$SCRIPT_DIR/test_skills_integrity.py"
END_TIME=$(date +%s%N)

ELAPSED_MS=$(( (END_TIME - START_TIME) / 1000000 ))
echo "Execution completed in ${ELAPSED_MS}ms (SLA: <= 500ms)"
if [ "$ELAPSED_MS" -gt 500 ]; then
  echo "⚠️ Warning: Performance SLA exceeded (${ELAPSED_MS}ms > 500ms)"
fi
