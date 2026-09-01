#!/usr/bin/env bash
# ==============================================================================
# Global Antigravity Flow Skill Suite - Universal Self-Contained Installer
# Deploys 10-Phase Lifecycle, Templates, Hooks, Scripts & GEMINI.md Rules
# ==============================================================================
set -euo pipefail

CONFIG_DIR="${HOME}/.gemini/config"
SKILLS_DIR="${CONFIG_DIR}/skills"
COMPAT_DIR="${HOME}/.gemini/antigravity"
TEMP_DIR=""

# Determine source directory (local vs remote curl execution)
SRC_DIR=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]:-}" ]; then
    LOCAL_CANDIDATE="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || true)"
    if [ -d "${LOCAL_CANDIDATE}/skills" ]; then
        SRC_DIR="${LOCAL_CANDIDATE}"
    fi
fi

# If piped via curl or not running from local repo root, clone latest from GitHub
if [ -z "$SRC_DIR" ]; then
    echo "[+] Remote/Piped execution detected. Fetching latest agy-flow from GitHub..."
    TEMP_DIR="$(mktemp -d /tmp/agy-flow-install-XXXXXX)"
    git clone --depth 1 https://github.com/larya-dot-eu/agy-flow.git "$TEMP_DIR" -q
    SRC_DIR="$TEMP_DIR"
fi

echo "================================================================="
echo " Deploying Antigravity Global Flow Skills Suite"
echo " Target Directory: ${CONFIG_DIR}"
echo "================================================================="

mkdir -p "${CONFIG_DIR}/skills" "${CONFIG_DIR}/rules" "${CONFIG_DIR}/templates" "${CONFIG_DIR}/scripts" "${COMPAT_DIR}"

echo "[+] Copying skills, templates, rules, and scripts..."
cp -r "${SRC_DIR}/skills/"* "${CONFIG_DIR}/skills/"
cp -r "${SRC_DIR}/rules/"* "${CONFIG_DIR}/rules/"
cp -r "${SRC_DIR}/templates/"* "${CONFIG_DIR}/templates/"
cp -r "${SRC_DIR}/scripts/"* "${CONFIG_DIR}/scripts/"
cp "${SRC_DIR}/hooks.json" "${CONFIG_DIR}/hooks.json"
chmod +x "${CONFIG_DIR}/scripts/"*.sh

# If installed as a global plugin, sync plugin copy as well
if [ -d "${CONFIG_DIR}/plugins/agy-flow" ]; then
    echo "[+] Updating global plugin directory: ${CONFIG_DIR}/plugins/agy-flow"
    mkdir -p "${CONFIG_DIR}/plugins/agy-flow/skills" "${CONFIG_DIR}/plugins/agy-flow/templates" "${CONFIG_DIR}/plugins/agy-flow/rules"
    cp -r "${SRC_DIR}/skills/"* "${CONFIG_DIR}/plugins/agy-flow/skills/"
    cp -r "${SRC_DIR}/templates/"* "${CONFIG_DIR}/plugins/agy-flow/templates/"
    cp -r "${SRC_DIR}/rules/"* "${CONFIG_DIR}/plugins/agy-flow/rules/"
fi

if [ -f "${CONFIG_DIR}/rules/GEMINI.md" ]; then
    cp "${CONFIG_DIR}/rules/GEMINI.md" "${CONFIG_DIR}/GEMINI.md"
fi

ln -sfn "${SKILLS_DIR}" "${COMPAT_DIR}/skills"
echo "[✓] Symlinked ${COMPAT_DIR}/skills -> ${SKILLS_DIR}"

# Cleanup temporary clone if used
if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

echo "================================================================="
echo " Installed Skills Inventory in ${SKILLS_DIR}:"
ls -la "${SKILLS_DIR}"
echo "================================================================="
echo " [SUCCESS] Global Antigravity Flow Suite successfully deployed!"
echo "================================================================="
