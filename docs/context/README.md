# Living Module Context (`docs/context/`)

This directory stores persistent, living module documentation for core subsystems mapped in `GEMINI.md` under `## Context Routing Map`.

---

## Conventions & Standards

- **Naming Convention**: `[subsystem-name].md` (e.g. `auth.md`, `billing.md`, `database.md`, `api.md`)
- **Canonical Template**: [`templates/context-module.md.template`](../../templates/context-module.md.template)
- **Zero-Discovery Routing**: Coding agents read these files immediately instead of performing expensive recursive repo searches, eliminating 20%–30% token waste.
- **Diff-to-Context Sync**: Synchronized in **Phase 9 (`/flow-release`)** whenever mapped code changes.
- **Privacy Notice**: Generated project-specific context documents in this directory are gitignored by default.
