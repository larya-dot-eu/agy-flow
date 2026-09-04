#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$(mktemp -d /tmp/test-context-guard-XXXXXX)"
mkdir -p "$TEST_DIR/src/api" "$TEST_DIR/src/api_v2" "$TEST_DIR/docs/context"
cd "$TEST_DIR"
git init -q
git config user.email "test@example.com"
git config user.name "Test Runner"

cat <<'EOF' > GEMINI.md
# Test Project
## Context Routing Map
- `/src/api/` -> docs/context/api.md
EOF

git add GEMINI.md && git commit -m "init" -q

# Copy guard script dynamically
mkdir -p scripts
cp "$SCRIPT_DIR/scripts/context-guard.sh" scripts/context-guard.sh
chmod +x scripts/context-guard.sh

echo "Scenario 1: Code in /src/api/ changed without context doc (Stop Hook)"
touch src/api/handler.js
OUTPUT1=$(./scripts/context-guard.sh --check-stop)
echo "$OUTPUT1" | grep -q '"decision": "continue"' || { echo "Test 1 Failed! Output was: $OUTPUT1"; exit 1; }
echo "Scenario 1 Passed: Stop blocked."

echo "Scenario 2: Code in /src/api_v2/ changed (Boundary test - should not trigger api.md guard)"
rm src/api/handler.js
touch src/api_v2/handler.js
OUTPUT2=$(./scripts/context-guard.sh --check-stop)
echo "$OUTPUT2" | grep -qv '"decision": "continue"' || { echo "Test 2 Failed (Prefix false positive)! Output was: $OUTPUT2"; exit 1; }
echo "Scenario 2 Passed: Boundary prefix isolated."

echo "Scenario 3: Non-commit command during PreToolUse (e.g. running pytest)"
NON_COMMIT_INPUT='{"toolCall":{"name":"run_command","args":{"CommandLine":"pytest tests/"}}}'
OUTPUT3=$(echo "$NON_COMMIT_INPUT" | ./scripts/context-guard.sh --check-commit)
echo "$OUTPUT3" | grep -qv '"decision": "deny"' || { echo "Test 3 Failed (Blocked non-commit command)!"; exit 1; }
echo "Scenario 3 Passed: Non-commit commands unimpeded."

echo "Scenario 4: Git commit command during PreToolUse with dirty mapped code"
touch src/api/handler.js
COMMIT_INPUT='{"toolCall":{"name":"run_command","args":{"CommandLine":"git commit -m \"feat: api change\""}}}'
OUTPUT4=$(echo "$COMMIT_INPUT" | ./scripts/context-guard.sh --check-commit)
echo "$OUTPUT4" | grep -q '"decision": "deny"' || { echo "Test 4 Failed! Output was: $OUTPUT4"; exit 1; }
echo "Scenario 4 Passed: Git commit blocked on dirty mapped code."

# Cleanup
rm -rf "$TEST_DIR"
echo "All context guard tests passed successfully!"
