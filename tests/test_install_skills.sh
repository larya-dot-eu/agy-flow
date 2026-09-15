#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR=$(mktemp -d)
export HOME="$TEST_DIR/home"
ORIGINAL_PATH="$PATH"

mkdir -p "$HOME"
cd "$TEST_DIR"

# Ensure we're testing the current source
cp -r "$SCRIPT_DIR/"* "$TEST_DIR/"
cd "$TEST_DIR"

echo "Scenario 1: Local Execution"
./install-skills.sh

CONFIG_DIR="${HOME}/.gemini/config"
COMPAT_DIR="${HOME}/.gemini/antigravity"

# Assert directories exist and are populated
for d in skills rules scripts; do
    if [ ! -d "${CONFIG_DIR}/$d" ]; then
        echo "Test 1 Failed: Directory ${CONFIG_DIR}/$d missing"
        exit 1
    fi
    # Check if directory has files (assuming src directories weren't empty)
    if [ -z "$(ls -A ${CONFIG_DIR}/$d)" ]; then
        echo "Test 1 Failed: Directory ${CONFIG_DIR}/$d is empty"
        exit 1
    fi
done

if [ ! -f "${CONFIG_DIR}/hooks.json" ]; then
    echo "Test 1 Failed: hooks.json missing"
    exit 1
fi

if [ ! -L "${COMPAT_DIR}/skills" ] || [ "$(readlink "${COMPAT_DIR}/skills")" != "${CONFIG_DIR}/skills" ]; then
    echo "Test 1 Failed: Symlink ${COMPAT_DIR}/skills incorrect or missing"
    exit 1
fi
if [ ! -L "${HOME}/.local/bin/flow-init" ] || [ "$(readlink "${HOME}/.local/bin/flow-init")" != "${CONFIG_DIR}/scripts/flow-init.sh" ]; then
    echo "Test 1 Failed: Symlink ${HOME}/.local/bin/flow-init incorrect or missing"
    exit 1
fi
if [ ! -x "${HOME}/.local/bin/flow-init" ]; then
    echo "Test 1 Failed: ${HOME}/.local/bin/flow-init is not executable"
    exit 1
fi

# Test executing directly via the symlink
mkdir -p "$TEST_DIR/sample_run"
"${HOME}/.local/bin/flow-init" --dir "$TEST_DIR/sample_run" --yes --no-git > /dev/null
if [ ! -f "$TEST_DIR/sample_run/GEMINI.md" ]; then
    echo "Test 1 Failed: Running ~/.local/bin/flow-init failed to create GEMINI.md"
    exit 1
fi
echo "Scenario 1 Passed: Local execution completed successfully."

echo "Scenario 2: Global Plugin Sync"
rm -rf "$HOME"
mkdir -p "$HOME"
mkdir -p "${HOME}/.gemini/config/plugins/agy-flow"
./install-skills.sh > /dev/null

PLUGIN_DIR="${HOME}/.gemini/config/plugins/agy-flow"
for d in skills rules; do
    if [ ! -d "${PLUGIN_DIR}/$d" ]; then
        echo "Test 2 Failed: Plugin directory ${PLUGIN_DIR}/$d missing"
        exit 1
    fi
    if [ -z "$(ls -A ${PLUGIN_DIR}/$d)" ]; then
        echo "Test 2 Failed: Plugin directory ${PLUGIN_DIR}/$d is empty"
        exit 1
    fi
done
echo "Scenario 2 Passed: Plugin directory sync successful."


echo "Scenario 3: GEMINI.md Sync"
rm -rf "$HOME"
mkdir -p "$HOME"
# Ensure valid rules/GEMINI.md is present
mkdir -p rules
cp "$SCRIPT_DIR/rules/GEMINI.md" rules/GEMINI.md
./install-skills.sh > /dev/null

if [ ! -f "${HOME}/.gemini/config/GEMINI.md" ]; then
    echo "Test 3 Failed: GEMINI.md not synced"
    exit 1
fi
echo "Scenario 3 Passed: GEMINI.md synced successfully."

echo "Scenario 4: Remote Execution via Piped curl"
rm -rf "$HOME"
mkdir -p "$HOME"

# Set up mock git
mkdir -p "$TEST_DIR/bin"
cat << 'MOCK_GIT' | sed 's/exit/exit/g' | sed 's/bash/bash/g' > "$TEST_DIR/bin/git"
#!/usr/bin/env bash
if [[ "$1" == "clone" ]]; then
    # Extract destination dir
    # Remove -q if it is the last argument
    if [[ "${@: -1}" == "-q" ]]; then
        DEST="${@: -2:1}"
    else
        DEST="${@: -1}"
    fi

    # Create dummy structure
    mkdir -p "$DEST/skills" "$DEST/rules" "$DEST/scripts"
    touch "$DEST/skills/dummy.sh" "$DEST/scripts/dummy.sh" "$DEST/hooks.json"
    echo "# Global Antigravity Prime Directives" > "$DEST/rules/GEMINI.md"
    exit 0
fi
echo "Unexpected git command: $@"
exit 1
MOCK_GIT
chmod +x "$TEST_DIR/bin/git"
export PATH="$TEST_DIR/bin:$PATH"

# Pipe execution
cat ./install-skills.sh | bash > /dev/null

# Verify mock clone was used and files were copied
if [ ! -f "${HOME}/.gemini/config/skills/dummy.sh" ]; then
    echo "Test 4 Failed: Remote install didn't copy mock files"
    exit 1
fi
echo "Scenario 4 Passed: Remote execution handled successfully."


echo "Scenario 5: Remote Execution git clone failure cleanup"
rm -rf "$HOME"
mkdir -p "$HOME"

# Set up mock git that fails
mkdir -p "$TEST_DIR/bin2"
echo '#!/usr/bin/env bash' > "$TEST_DIR/bin2/git"
echo 'if [[ "$1" == "clone" ]]; then' >> "$TEST_DIR/bin2/git"
echo '    exit 1' >> "$TEST_DIR/bin2/git"
echo 'fi' >> "$TEST_DIR/bin2/git"
echo 'echo "Unexpected git command: $@"' >> "$TEST_DIR/bin2/git"
echo 'exit 1' >> "$TEST_DIR/bin2/git"

chmod +x "$TEST_DIR/bin2/git"
export PATH="$TEST_DIR/bin2:$PATH"

TMP_BEFORE=$(ls -d /tmp/agy-flow-install-* 2>/dev/null | wc -l || echo 0)

# Run it expecting failure
if cat ./install-skills.sh | bash > /dev/null 2>&1; then
    echo "Test 5 Failed: Script should have failed but exited 0"
    exit 1
fi

TMP_AFTER=$(ls -d /tmp/agy-flow-install-* 2>/dev/null | wc -l || echo 0)
if [ "$TMP_BEFORE" != "$TMP_AFTER" ]; then
    echo "Test 5 Failed: Temp directory was not cleaned up on git failure."
    ls -d /tmp/agy-flow-install-*
    rm -rf /tmp/agy-flow-install-*
    exit 1
fi
export PATH="$ORIGINAL_PATH"
echo "Scenario 5 Passed: Cleanup on failure works correctly."

echo "Scenario 6: Idempotent Execution on existing GEMINI.md with Directives Marker"
rm -rf "$HOME"
mkdir -p "$HOME/.gemini/config"
cat << 'EOF' > "$HOME/.gemini/config/GEMINI.md"
# My Custom Instructions
- Be concise.

# Global Antigravity Prime Directives: The 10-Phase Engineering Lifecycle
- Rule 1
EOF
BEFORE_MD5=$(md5sum "$HOME/.gemini/config/GEMINI.md" | awk '{print $1}')

./install-skills.sh > /dev/null

AFTER_MD5=$(md5sum "$HOME/.gemini/config/GEMINI.md" | awk '{print $1}')
if [ "$BEFORE_MD5" != "$AFTER_MD5" ]; then
    echo "Test 6 Failed: GEMINI.md was mutated even though Directives Marker was present"
    exit 1
fi
BAK_COUNT=$(find "$HOME/.gemini/config" -name "GEMINI.md.bak.*" 2>/dev/null | wc -l)
if [ "$BAK_COUNT" -ne 0 ]; then
    echo "Test 6 Failed: Spurious backup file created for already-configured GEMINI.md"
    exit 1
fi
echo "Scenario 6 Passed: Idempotency verified."

echo "Scenario 7: Non-Interactive Piped Execution Appends with Backup"
rm -rf "$HOME"
mkdir -p "$HOME/.gemini/config"
cat << 'EOF' > "$HOME/.gemini/config/GEMINI.md"
# My Custom Instructions
- Never use emojis.
EOF

# Piped non-interactive execution
cat ./install-skills.sh | bash > /dev/null

if ! grep -qF "# My Custom Instructions" "$HOME/.gemini/config/GEMINI.md"; then
    echo "Test 7 Failed: Original user configuration was lost after non-interactive install"
    exit 1
fi
if ! grep -qF "# Global Antigravity Prime Directives" "$HOME/.gemini/config/GEMINI.md"; then
    echo "Test 7 Failed: agy-flow directives were not appended"
    exit 1
fi
BAK_COUNT=$(find "$HOME/.gemini/config" -name "GEMINI.md.bak.*" 2>/dev/null | wc -l)
if [ "$BAK_COUNT" -ne 1 ]; then
    echo "Test 7 Failed: Expected 1 backup file, found $BAK_COUNT"
    exit 1
fi
echo "Scenario 7 Passed: Non-interactive append with backup verified."

echo "Scenario 8: Interactive Prompt Handling (Preserve, Overwrite, Append)"
# Sub-scenario 8a: Preserve
rm -rf "$HOME"
mkdir -p "$HOME/.gemini/config"
echo "# Original Setup" > "$HOME/.gemini/config/GEMINI.md"
printf "P\n" | AGY_FORCE_INTERACTIVE=1 ./install-skills.sh > /dev/null
if ! grep -qF "# Original Setup" "$HOME/.gemini/config/GEMINI.md" || grep -qF "# Global Antigravity Prime Directives" "$HOME/.gemini/config/GEMINI.md"; then
    echo "Test 8a Failed: Preserve mode modified GEMINI.md"
    exit 1
fi
if [ $(find "$HOME/.gemini/config" -name "GEMINI.md.bak.*" 2>/dev/null | wc -l) -ne 0 ]; then
    echo "Test 8a Failed: Preserve mode should not create backup"
    exit 1
fi

# Sub-scenario 8b: Overwrite
rm -rf "$HOME"
mkdir -p "$HOME/.gemini/config"
echo "# Original Setup" > "$HOME/.gemini/config/GEMINI.md"
printf "O\n" | AGY_FORCE_INTERACTIVE=1 ./install-skills.sh > /dev/null
if grep -qF "# Original Setup" "$HOME/.gemini/config/GEMINI.md" || ! grep -qF "# Global Antigravity Prime Directives" "$HOME/.gemini/config/GEMINI.md"; then
    echo "Test 8b Failed: Overwrite mode failed to replace GEMINI.md"
    exit 1
fi
if [ $(find "$HOME/.gemini/config" -name "GEMINI.md.bak.*" 2>/dev/null | wc -l) -ne 1 ]; then
    echo "Test 8b Failed: Overwrite mode failed to create backup"
    exit 1
fi

# Sub-scenario 8c: Append
rm -rf "$HOME"
mkdir -p "$HOME/.gemini/config"
echo "# Original Setup" > "$HOME/.gemini/config/GEMINI.md"
printf "A\n" | AGY_FORCE_INTERACTIVE=1 ./install-skills.sh > /dev/null
if ! grep -qF "# Original Setup" "$HOME/.gemini/config/GEMINI.md" || ! grep -qF "# Global Antigravity Prime Directives" "$HOME/.gemini/config/GEMINI.md"; then
    echo "Test 8c Failed: Append mode failed to retain original setup or append directives"
    exit 1
fi
if [ $(find "$HOME/.gemini/config" -name "GEMINI.md.bak.*" 2>/dev/null | wc -l) -ne 1 ]; then
    echo "Test 8c Failed: Append mode failed to create backup"
    exit 1
fi
echo "Scenario 8 Passed: Interactive prompt modes verified."

# Cleanup
rm -rf "$TEST_DIR"
echo "All install-skills tests passed successfully!"
