# Implementation Plans (`docs/plans/`)

This directory stores bite-sized, test-first implementation plans authored during **Phase 4 (`/flow-plan`)** and audited in **Phase 5 (`/flow-review`)** of the `agy-flow` engineering lifecycle.

---

## Conventions & Standards

- **Naming Convention**: `YYYY-MM-DD-[feature-name]-plan.md` (e.g. `2026-09-01-jwt-auth-plan.md`)
- **Canonical Template**: [`templates/plan.md.template`](../../templates/plan.md.template)
- **Task Granularity**: Each task is broken into 2–5 minute atomic TDD steps (Red $\rightarrow$ Green $\rightarrow$ Refactor $\rightarrow$ Commit).
- **Interface Contracts**: Each task explicitly documents its `Consumes` and `Produces` signatures.
- **No Placeholders**: Strict prohibition against `TODO`, `TBD`, or pseudocode.
- **Privacy Notice**: Generated project-specific plans in this directory are gitignored by default.
