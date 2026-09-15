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

cleanup() {
    if [ -n "${TEMP_DIR:-}" ] && [ -d "${TEMP_DIR:-}" ]; then
        rm -rf "$TEMP_DIR"
    fi
}
trap cleanup EXIT

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

copy_resources() {
    local dest="$1"
    for dir in skills rules; do
        mkdir -p "${dest}/${dir}"
        cp -r "${SRC_DIR}/${dir}/"* "${dest}/${dir}/"
    done
}

mkdir -p "${CONFIG_DIR}/scripts" "${COMPAT_DIR}"

echo "[+] Copying skills, rules, and scripts..."
copy_resources "${CONFIG_DIR}"
cp -r "${SRC_DIR}/scripts/"* "${CONFIG_DIR}/scripts/"
cp "${SRC_DIR}/hooks.json" "${CONFIG_DIR}/hooks.json"
chmod +x "${CONFIG_DIR}/scripts/"*.sh

# If installed as a global plugin, sync plugin copy as well
if [ -d "${CONFIG_DIR}/plugins/agy-flow" ]; then
    echo "[+] Updating global plugin directory: ${CONFIG_DIR}/plugins/agy-flow"
    copy_resources "${CONFIG_DIR}/plugins/agy-flow"
fi

backup_gemini_md() {
    local config_gemini="${CONFIG_DIR}/GEMINI.md"
    local backup_path="${CONFIG_DIR}/GEMINI.md.bak.$(date +%Y%m%d%H%M%S)_$$"
    cp "$config_gemini" "$backup_path"
    if [ ! -f "$backup_path" ] || { [ -s "$config_gemini" ] && [ ! -s "$backup_path" ]; }; then
        echo "❌ Error: Failed to create verified backup at ${backup_path}"
        return 1
    fi
    echo "[+] Backup created at ${backup_path}"
}

append_gemini_md() {
    local config_gemini="${CONFIG_DIR}/GEMINI.md"
    local rules_gemini="${CONFIG_DIR}/rules/GEMINI.md"
    backup_gemini_md
    printf "\n\n" >> "$config_gemini"
    cat "$rules_gemini" >> "$config_gemini"
    echo "[+] Appended agy-flow directives to ${config_gemini}"
}

configure_gemini_md() {
    local config_gemini="${CONFIG_DIR}/GEMINI.md"
    local rules_gemini="${CONFIG_DIR}/rules/GEMINI.md"

    if [ ! -f "$rules_gemini" ]; then
        return 0
    fi

    if [ ! -f "$config_gemini" ]; then
        cp "$rules_gemini" "$config_gemini"
        echo "[+] Initialized ${config_gemini}"
        return 0
    fi

    if grep -qF "# Global Antigravity Prime Directives" "$config_gemini"; then
        echo "[*] agy-flow directives already present in ${config_gemini}"
        return 0
    fi

    # Interactive execution check (TTY or test override)
    if [ -t 0 ] || [ -n "${AGY_FORCE_INTERACTIVE:-}" ]; then
        echo ""
        echo "[?] Existing ~/.gemini/config/GEMINI.md detected."
        echo "    [P]reserve existing (rules load automatically via rules/GEMINI.md) [Default]"
        echo "    [O]verwrite with agy-flow defaults (creates backup)"
        echo "    [A]ppend agy-flow directives (creates backup)"
        read -r -p "Select [P/o/a]: " choice || choice="P"
        choice="${choice:-P}"
        case "$choice" in
            [oO]*)
                backup_gemini_md
                cp "$rules_gemini" "$config_gemini"
                echo "[+] Overwrote ${config_gemini} with agy-flow defaults"
                ;;
            [aA]*)
                append_gemini_md
                ;;
            *)
                echo "[*] Preserved existing ${config_gemini} (Rules active via ${CONFIG_DIR}/rules/GEMINI.md)"
                ;;
        esac
    else
        # Non-interactive fallback: append with backup
        append_gemini_md
    fi
}

configure_gemini_md

ln -sfn "${SKILLS_DIR}" "${COMPAT_DIR}/skills"
echo "[✓] Symlinked ${COMPAT_DIR}/skills -> ${SKILLS_DIR}"

LOCAL_BIN="${HOME}/.local/bin"
mkdir -p "${LOCAL_BIN}"
ln -sfn "${CONFIG_DIR}/scripts/flow-init.sh" "${LOCAL_BIN}/flow-init"
for f in "${CONFIG_DIR}/scripts/flow-init.sh" "${CONFIG_DIR}/scripts/flow_init.py" "${LOCAL_BIN}/flow-init"; do
    [ -e "$f" ] && chmod +x "$f" || true
done
echo "[✓] Symlinked ${LOCAL_BIN}/flow-init -> ${CONFIG_DIR}/scripts/flow-init.sh"

if [[ ":${PATH:-}:" != *":${LOCAL_BIN}:"* ]]; then
    echo "[!] Notice: ${LOCAL_BIN} is not in your \$PATH. Add 'export PATH=\"\$HOME/.local/bin:\$PATH\"' to your ~/.bashrc or ~/.zshrc."
fi

echo "================================================================="
echo " Installed Skills Inventory in ${SKILLS_DIR}:"
ls -la "${SKILLS_DIR}"
echo "================================================================="
echo " [SUCCESS] Global Antigravity Flow Suite successfully deployed!"
echo "================================================================="
