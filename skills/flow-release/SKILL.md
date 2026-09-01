---
name: flow-release
description: >-
  Phase 8, 9 & 10 of the 10-phase engineering lifecycle: Post-Implementation Verification, Living Context Sync, and Safe Release.
  Runs comprehensive verification, diff-to-context audits, and executes safe release gates.
  Trigger with /flow-release.
risk: critical
source: unified-flow
---

# Flow Release & Verification (`/flow-release`)

Phase 8, 9 & 10: Post-Implementation, Living Docs & Safe Release.

Ensure production-grade quality, synchronize living documentation, and execute safe deployment gates.

```text
  ┌─────────────────────────────────────────────────────────────┐
  │ Phase 08: Post-Implementation Verification                  │
  │   - Comprehensive Test Suites (Unit, Integration, E2E)      │
  │   - Static Analysis, Typechecks & Security Linters          │
  │   - Blast Radius & Zero-Regression Confirmation             │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Phase 09: Living Context & Living Docs Synchronization       │
  │   - 💡 Diff-to-Context Audit: Sync docs/context/*.md        │
  │   - 💡 ADR Gate: Verify docs/adr/ records & index synced   │
  │   - Update README.md, Architecture Guides, API Docs         │
  │   - Sync docs/specs/ and docs/plans/ to As-Built Reality    │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Phase 10: Safe Release, Dead-Code Pruning & PR Finalization │
  │   - Verify Final Dead-Code & Orphaned Imports Pruning       │
  │   - Draft Changelog & Semantic Version Bump                 │
  │   - Verify Rollback Runbook & Feature Flags                 │
  │   - Generate Pull Request Summary & Verification Evidence   │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Lifecycle Complete ──► Final Sign-Off & Merge Readiness     │
  └─────────────────────────────────────────────────────────────┘
```

---

## 1. Phase 8: Post-Implementation Verification

Execute the complete verification battery across all test boundaries:

### Verification Battery
1. **Unit & Contract Suite**: 100% pass rate.
2. **Integration & E2E Suite**: Confirm end-to-end user journeys pass.
3. **Static Analysis & Linters**: Run project linters, typecheckers, and formatters (e.g. `tsc --noEmit`, `flake8`, `golangci-lint`, `cargo clippy`).
4. **Blast Radius Audit**: Verify that unaffected services, endpoints, and packages remain untouched.

---

## 2. Phase 9: Living Context & Living Docs Synchronization

Keep repository documentation synchronized with codebase changes:

### Living Context Diff-Audit Gate
1. Execute `git diff --name-only <base-branch>...HEAD` to identify all changed files.
2. For each changed file matching a `## Context Routing Map` entry in `GEMINI.md`:
   - Inspect changes in exported functions, HTTP routes, MCP tools, and external services.
   - Synchronize `docs/context/[module].md` interface tables and invariant checkboxes.
   - Update the `Last Verified` date in the document header.
3. If a new subsystem folder was created, prompt the user to register it in `GEMINI.md`.
4. **ADR Gate**: Verify records in `docs/adr/NNNN-[title].md` and `docs/adr/README.md`.
5. **Spec & Plan Archival**: Update `docs/specs/` and `docs/plans/` status to `Status: Implemented` and note any approved delta.

---

## 3. Phase 10: Safe Release & PR Finalization

Prepare the branch for production release or pull request merge:

### Release Gate Checklist
- [ ] **Dead-Code Pruning**: Verify that all orphaned imports, functions, and dead code have been completely removed.
- [ ] **Changelog**: Add entry following [Keep a Changelog](https://keepachangelog.com/) standards.
- [ ] **Semantic Versioning**: Determine version bump (Patch / Minor / Major) according to SemVer rules.
- [ ] **Rollback Runbook**: Confirm clear rollback commands in case of production regression.
- [ ] **Clean Git History**: Verify clean commit history on `feature/YYYY-MM-DD-[feature]`.

---

## 4. Final Release Report Template

Output the completed release summary upon lifecycle closure:

```markdown
# Engineering Lifecycle Completion Report: [Feature Name]

- **Branch**: `feature/YYYY-MM-DD-[feature]`
- **Spec**: `docs/specs/YYYY-MM-DD-[feature]-spec.md` (Status: Implemented)
- **Plan**: `docs/plans/YYYY-MM-DD-[feature]-plan.md` (Status: Implemented)
- **Context Docs**: `docs/context/` (Status: Synced & Verified)
- **ADRs**: `docs/adr/` (Status: Synced)
- **Verification**: ALL PASSED (Unit, Integration, Linters)

---

### Key Deliverables
- [Summary of delivered capabilities]
```
