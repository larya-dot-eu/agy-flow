#!/usr/bin/env bash
# ==============================================================================
# Global Antigravity Flow Skill Suite - Universal Self-Contained Installer
# Deploys 10-Phase Lifecycle, Templates, Hooks, Scripts & GEMINI.md Rules
# ==============================================================================
set -euo pipefail

CONFIG_DIR="${HOME}/.gemini/config"
SKILLS_DIR="${CONFIG_DIR}/skills"
COMPAT_DIR="${HOME}/.gemini/antigravity"
SCRIPT_SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || true)"

echo "================================================================="
echo " Deploying Antigravity Global Flow Skills Suite"
echo " Target Directory: ${CONFIG_DIR}"
echo "================================================================="

mkdir -p "${CONFIG_DIR}/skills" "${CONFIG_DIR}/rules" "${CONFIG_DIR}/templates" "${CONFIG_DIR}/scripts" "${COMPAT_DIR}"

if [ -n "$SCRIPT_SRC_DIR" ] && [ -d "$SCRIPT_SRC_DIR/skills" ]; then
    echo "[+] Installing from local repository source: ${SCRIPT_SRC_DIR}"
    cp -r "${SCRIPT_SRC_DIR}/skills/"* "${CONFIG_DIR}/skills/"
    cp -r "${SCRIPT_SRC_DIR}/rules/"* "${CONFIG_DIR}/rules/"
    cp -r "${SCRIPT_SRC_DIR}/templates/"* "${CONFIG_DIR}/templates/"
    cp -r "${SCRIPT_SRC_DIR}/scripts/"* "${CONFIG_DIR}/scripts/"
    cp "${SCRIPT_SRC_DIR}/hooks.json" "${CONFIG_DIR}/hooks.json"
    chmod +x "${CONFIG_DIR}/scripts/"*.sh
fi

if [ -f "${CONFIG_DIR}/rules/GEMINI.md" ]; then
    cp "${CONFIG_DIR}/rules/GEMINI.md" "${CONFIG_DIR}/GEMINI.md"
fi

ln -sfn "${SKILLS_DIR}" "${COMPAT_DIR}/skills"
echo "[✓] Symlinked ${COMPAT_DIR}/skills -> ${SKILLS_DIR}"

echo "================================================================="
echo " Installed Skills Inventory in ${SKILLS_DIR}:"
ls -la "${SKILLS_DIR}"
echo "================================================================="
echo " [SUCCESS] Global Antigravity Flow Suite successfully deployed!"
echo "================================================================="
