---
name: flow-init
description: >-
  Universal 1-shot project initialization and onboarding command. Probes workspace build tools, test runners,
  subsystems, and git/GitHub environments to scaffold GEMINI.md, AGENTS.md, docs/context/, and docs/adr/.
  Trigger with /flow-init.
risk: low
source: unified-flow
---

# Flow Init (`/flow-init`)

Universal 1-shot project memory initialization and repository onboarding.

```text
               [/flow-init Ingestion or Terminal Execution]
                                     │
                       ┌─────────────▼─────────────┐
                       │ 1. Git & GitHub Probe     │ ──► Optional git init & identity check
                       └─────────────┬─────────────┘
                                     │
                       ┌─────────────▼─────────────┐
                       │ 2. Multi-Stack Scanner    │ ──► Detect Python, TS/JS, Rust, Go, Make
                       └─────────────┬─────────────┘
                                     │
                       ┌─────────────▼─────────────┐
                       │ 3. Topology & Routing Map │ ──► Map primary subsystem directories
                       └─────────────┬─────────────┘
                                     │
                       ┌─────────────▼─────────────┐
                       │ 4. Scaffold Documentation │ ──► GEMINI.md, AGENTS.md, docs/context/
                       └───────────────────────────┘
```

<HARD-GATE>
Never overwrite existing `GEMINI.md` or living context modules without explicit user confirmation.
</HARD-GATE>

---

## 1. When to Use & Path Classification
- **Symptoms / Trigger Conditions**:
  - Initializing Antigravity pair programming on a new or existing repository.
  - Missing `GEMINI.md` or `AGENTS.md` context routing map.
  - Setting up structured `docs/context/` and `docs/adr/` folders.
- **When NOT to Use**:
  - The repository is already initialized with an active `GEMINI.md` and `docs/context/` map (use `/flow-brainstorm` instead).

---

## 2. Core Workflow & Step-by-Step Instructions

1. **Step 1 (Run Initialization Engine)**:
   Execute `scripts/flow_init.py` on the target workspace:
   ```bash
   python3 scripts/flow_init.py --dir .
   ```
2. **Step 2 (Inspect Generated Artifacts)**:
   Verify the creation of:
   - `GEMINI.md` (Stack, Context Routing Map, Frequent Commands, Directives)
   - `AGENTS.md` (Symlink pointing to `GEMINI.md`)
   - `docs/context/*.md` (Initial context modules)
   - `docs/adr/README.md` (Architecture decision records index)
3. **Step 3 (Verify Parity & Directives)**:
   Confirm that all discovered source folders have corresponding entries in `## Context Routing Map`.

---

## 3. Verification & Output Standards
- **Verification Command**: `bash tests/test_skills_integrity.sh`
- **Deliverable Path**: `GEMINI.md` and `docs/context/*.md`
