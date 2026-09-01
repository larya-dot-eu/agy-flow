---
name: flow-version-update
description: >-
  Checks GitHub for the latest release/commit of agy-flow, displays release notes,
  and updates local skills, templates, rules, and scripts in ~/.gemini/config/.
  Trigger with /flow-version-update.
risk: medium
source: unified-flow
---

# Flow Version Update (`/flow-version-update`)

Update the local `agy-flow` skill suite, canonical templates, global prime directives, and deterministic lifecycle scripts to the latest official release from GitHub.

```text
               [/flow-version-update Invoked]
                             │
               ┌─────────────▼─────────────┐
               │ 1. Check Remote Version   │ ──► Query GitHub API / Releases
               └─────────────┬─────────────┘
                             │
               ┌─────────────▼─────────────┐
               │ 2. Fetch & Deploy Suite   │ ──► Clone latest & run installer
               └─────────────┬─────────────┘
                             │
               ┌─────────────▼─────────────┐
               │ 3. Verify Local Inventory │ ──► Validate 10+ skills & 4 templates
               └─────────────┬─────────────┘
                             │
               ┌─────────────▼─────────────┐
               │ 4. Output Update Summary  │ ──► Render version upgrade scorecard
               └───────────────────────────┘
```

---

## 1. Automated Update Execution Protocol

When this skill is activated, execute the following automated update procedure:

### Step 1: Check Latest Release on GitHub
Query the GitHub repository to discover the latest published tag and release notes:

```bash
curl -fsSL https://api.github.com/repos/larya-dot-eu/agy-flow/releases/latest 2>/dev/null | grep -E '"(tag_name|name|published_at)"' || echo "Using latest main branch"
```

### Step 2: Fetch and Install Latest Suite
Download and execute the self-contained installer from GitHub to update `~/.gemini/config/`:

```bash
git clone --depth 1 https://github.com/larya-dot-eu/agy-flow.git /tmp/agy-flow-update-$$ && /tmp/agy-flow-update-$$/install-skills.sh && rm -rf /tmp/agy-flow-update-$$
```

### Step 3: Verify Updated Installation
Verify that all skills, templates, and rules are intact:

```bash
ls -la ~/.gemini/config/skills/
ls -la ~/.gemini/config/templates/
ls -la ~/.gemini/config/rules/
```

---

## 2. Update Summary Scorecard Template

Upon successful deployment, output the update confirmation scorecard:

```markdown
# 🚀 agy-flow Update Summary

- **Repository**: [larya-dot-eu/agy-flow](https://github.com/larya-dot-eu/agy-flow)
- **Active Version**: `[vX.Y.Z]`
- **Target Directory**: `~/.gemini/config/`
- **Status**: SUCCESSFULLY UPDATED

---

### Components Synchronized
- [x] **Skills Suite**: All `/flow-*` skills updated in `~/.gemini/config/skills/`
- [x] **Templates Suite**: Canonical templates updated in `~/.gemini/config/templates/`
- [x] **Global Directives**: Prime directives updated in `~/.gemini/config/rules/GEMINI.md`
- [x] **Lifecycle Scripts**: `context-guard.sh` updated in `~/.gemini/config/scripts/`
```
