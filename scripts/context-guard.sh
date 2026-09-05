#!/usr/bin/env bash
# scripts/context-guard.sh - Deterministic Antigravity Lifecycle & Git Context Guard

MODE="${1:---check-stop}"

# If invoked during PreToolUse (--check-commit), inspect stdin payload
if [ "$MODE" = "--check-commit" ]; then
  # Read stdin safely
  PAYLOAD="$(cat 2>/dev/null || true)"
  
  # Check if payload specifies a git commit
  IS_COMMIT="false"
  if [ -n "$PAYLOAD" ]; then
    IS_COMMIT=$(python3 -c '
import sys, json
try:
    data = json.loads(sys.argv[1])
    args = data.get("toolCall", {}).get("args", {})
    cmd = str(args.get("CommandLine") or args.get("commandLine") or "")
    if "git commit" in cmd or "git-commit" in cmd:
        print("true")
    else:
        print("false")
except Exception:
    print("false")
' "$PAYLOAD" 2>/dev/null || echo "false")
  fi

  if [ "$IS_COMMIT" != "true" ]; then
    echo '{"decision": "allow"}'
    exit 0
  fi
fi

# Check if inside a git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if [ "$MODE" = "--check-commit" ]; then
    echo '{"decision": "allow"}'
  else
    echo '{}'
  fi
  exit 0
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
GEMINI_FILE=""

if [ -f "$REPO_ROOT/GEMINI.md" ]; then
  GEMINI_FILE="$REPO_ROOT/GEMINI.md"
elif [ -f "$REPO_ROOT/AGENTS.md" ]; then
  GEMINI_FILE="$REPO_ROOT/AGENTS.md"
elif [ -f "$REPO_ROOT/.agents/AGENTS.md" ]; then
  GEMINI_FILE="$REPO_ROOT/.agents/AGENTS.md"
fi

if [ -z "$GEMINI_FILE" ]; then
  if [ "$MODE" = "--check-commit" ]; then
    echo '{"decision": "allow"}'
  else
    echo '{}'
  fi
  exit 0
fi

# Extract Context Routing Map entries (e.g. "- `/src/api/` -> docs/context/api.md")
MAPPINGS=$(awk '/## Context Routing Map/{flag=1; next} /^## /{flag=0} flag' "$GEMINI_FILE" 2>/dev/null | grep -E '^\s*-\s*`?[^`]+`?\s*->\s*[^ ]+' | sed -E 's/^[ -]*`?([^`]+)`?[ ]*->[ ]*([^ ]+)/\1|\2/' || true)

if [ -z "$MAPPINGS" ]; then
  if [ "$MODE" = "--check-commit" ]; then
    echo '{"decision": "allow"}'
  else
    echo '{}'
  fi
  exit 0
fi

# Inspect git status with -uall so all individual files in directories are listed
CHANGED_FILES=$(git status --porcelain -uall 2>/dev/null | sed 's/^...//' || true)

if [ -z "$CHANGED_FILES" ]; then
  if [ "$MODE" = "--check-commit" ]; then
    echo '{"decision": "allow"}'
  else
    echo '{}'
  fi
  exit 0
fi

STALE_MODULES=""

while IFS='|' read -r SRC_PATH DOC_PATH; do
  [ -z "$SRC_PATH" ] && continue
  SRC_PATH=$(echo "$SRC_PATH" | sed 's|^/||; s|/$||')
  DOC_PATH=$(echo "$DOC_PATH" | sed 's|^/||; s|/$||')
  
  SRC_CHANGED=false
  DOC_CHANGED=false
  
  while IFS= read -r FILE; do
    [ -z "$FILE" ] && continue
    # Exact directory boundary match (e.g. src/api/ or exact file src/api)
    if [[ "$FILE" == "$SRC_PATH/"* || "$FILE" == "$SRC_PATH" ]]; then
      SRC_CHANGED=true
    fi
    if [[ "$FILE" == "$DOC_PATH" ]]; then
      DOC_CHANGED=true
    fi
  done <<< "$CHANGED_FILES"
  
  if [ "$SRC_CHANGED" = true ] && [ "$DOC_CHANGED" = false ]; then
    STALE_MODULES="${STALE_MODULES}\n- Subsystem '/${SRC_PATH}/' was modified but '${DOC_PATH}' was NOT updated."
  fi
done <<< "$MAPPINGS"

if [ -n "$STALE_MODULES" ]; then
  if [ "$MODE" = "--check-commit" ]; then
    DECISION="deny"
    MSG="Context Guard Block: Cannot commit while mapped code is out of sync with living documentation:${STALE_MODULES}\n\nPlease update the relevant docs/context/ file(s) before committing."
  else
    DECISION="continue"
    MSG="⚠️ Context Guard Alert: You modified code in mapped directories without synchronizing their living context documents:${STALE_MODULES}\n\nPlease update the relevant docs/context/ file(s) before completing this turn."
  fi
  
  ESC_MSG=$(printf '%s' "$MSG" | jq -R -s -c '.' 2>/dev/null || printf '"%s"' "$MSG")
  
  cat <<EOF
{
  "decision": "$DECISION",
  "reason": $ESC_MSG
}
EOF
  exit 0
fi

if [ "$MODE" = "--check-commit" ]; then
  echo '{"decision": "allow"}'
else
  echo '{}'
fi
exit 0
