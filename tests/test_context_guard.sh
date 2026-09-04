#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="/tmp/test-context-guard-$$"
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


echo "Scenario 5: Fallback to AGENTS.md"
git rm -f GEMINI.md -q
cat <<'EOF_AGENTS' > AGENTS.md
# Test Project
## Context Routing Map
- `/src/api/` -> docs/context/api.md
EOF_AGENTS
git add AGENTS.md && git commit -m "use AGENTS.md" -q

touch src/api/handler.js
OUTPUT5=$(./scripts/context-guard.sh --check-stop)
echo "$OUTPUT5" | grep -q '"decision": "continue"' || { echo "Test 5 Failed! Output was: $OUTPUT5"; exit 1; }
echo "Scenario 5 Passed: Fallback to AGENTS.md works."

echo "Scenario 6: Priority of GEMINI.md over AGENTS.md"
cat <<'EOF_GEMINI2' > GEMINI.md
# Test Project
## Context Routing Map
- `/src/api_v3/` -> docs/context/api_v3.md
EOF_GEMINI2
git add GEMINI.md && git commit -m "add GEMINI.md back" -q

mkdir -p src/api_v3
touch src/api_v3/handler.js
rm src/api/handler.js
OUTPUT6=$(./scripts/context-guard.sh --check-stop)
echo "$OUTPUT6" | grep -q '"decision": "continue"' || { echo "Test 6 Failed! Priority not respected. Output was: $OUTPUT6"; exit 1; }

rm src/api_v3/handler.js
touch src/api/handler.js
OUTPUT7=$(./scripts/context-guard.sh --check-stop)
echo "$OUTPUT7" | grep -qv '"decision": "continue"' || { echo "Test 7 Failed! AGENTS.md was read instead of GEMINI.md. Output was: $OUTPUT7"; exit 1; }
echo "Scenario 6 Passed: GEMINI.md prioritized over AGENTS.md."

echo "Scenario 7: Priority of AGENTS.md over .agents/AGENTS.md"
git rm -f GEMINI.md -q
mkdir -p .agents
cat <<'EOF_DOTAGENTS' > .agents/AGENTS.md
# Test Project
## Context Routing Map
- `/src/api_v4/` -> docs/context/api_v4.md
EOF_DOTAGENTS
git add .agents/AGENTS.md && git commit -m "add .agents/AGENTS.md" -q

mkdir -p src/api_v4
# We already have AGENTS.md from Scenario 5 pointing to /src/api/
# And .agents/AGENTS.md pointing to /src/api_v4/

# Test AGENTS.md takes priority (src/api/ is watched, src/api_v4/ is NOT)
mkdir -p src/api
touch src/api/handler.js
OUTPUT8=$(./scripts/context-guard.sh --check-stop)
echo "$OUTPUT8" | grep -q '"decision": "continue"' || { echo "Test 8 Failed! Priority of AGENTS.md not respected. Output was: $OUTPUT8"; exit 1; }

rm src/api/handler.js
touch src/api_v4/handler.js
OUTPUT9=$(./scripts/context-guard.sh --check-stop)
echo "$OUTPUT9" | grep -qv '"decision": "continue"' || { echo "Test 9 Failed! .agents/AGENTS.md was read instead of AGENTS.md. Output was: $OUTPUT9"; exit 1; }
echo "Scenario 7 Passed: AGENTS.md prioritized over .agents/AGENTS.md."

echo "Scenario 8: Fallback to .agents/AGENTS.md"
git rm -f AGENTS.md -q
git commit -m "remove AGENTS.md" -q

# .agents/AGENTS.md pointing to /src/api_v4/ is active
touch src/api_v4/handler.js
OUTPUT10=$(./scripts/context-guard.sh --check-stop)
echo "$OUTPUT10" | grep -q '"decision": "continue"' || { echo "Test 10 Failed! Fallback to .agents/AGENTS.md not respected. Output was: $OUTPUT10"; exit 1; }
echo "Scenario 8 Passed: Fallback to .agents/AGENTS.md works."

# Cleanup
rm -rf "$TEST_DIR"
echo "All context guard tests passed successfully!"
