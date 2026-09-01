---
name: flow-release
description: >-
  Phase 8, 9 & 10 of the 10-phase engineering lifecycle: Post-Implementation Verification, Living Docs Updates, and Safe Release.
  Runs comprehensive verification, syncs living documentation, and executes safe release gates.
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
  │ Phase 09: Living Docs Synchronization                       │
  │   - Update README.md, Architecture Guides, API Docs         │
  │   - 💡 ADR Gate: Verify docs/adr/ records & index synced   │
  │   - Sync docs/specs/ and docs/plans/ to As-Built Reality    │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Phase 10: Safe Release & PR Finalization                    │
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

## 2. Phase 9: Living Docs Synchronization

Keep repository documentation synchronized with codebase changes:

### Documentation Sync Checklist
- **`README.md` / Getting Started**: Update CLI usage examples, environment variables, or setup instructions if modified.
- **Architecture Documentation & ADR Gate**: Verify that any architectural decisions or pattern changes introduced in this lifecycle have corresponding records in `docs/adr/NNNN-[title].md` and that `docs/adr/README.md` is updated.
- **API Documentation**: Update OpenAPI/Swagger schemas, GraphQL schemas, or interface reference docs.
- **Spec & Plan Archival**: Update `docs/specs/` and `docs/plans/` status to `Status: Implemented` and note any approved delta.

---

## 3. Phase 10: Safe Release & PR Finalization

Prepare the branch for production release or pull request merge:

### Release Gate Checklist
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
- **ADRs**: `docs/adr/` (Status: Synced)
- **Verification**: ALL PASSED (Unit, Integration, Linters)

---

### Key Deliverables
- [Summary of newly added components / capabilities]
- [Summary of updated tests]
- [Summary of updated documentation]

---

### Pull Request Summary
```markdown
## Summary
[High-level overview of changes]

## Key Changes
- [Component A]: [Change]
- [Component B]: [Change]

## Verification
- Unit Tests: Passed (`[command]`)
- Integration Tests: Passed (`[command]`)
- Linters: Clean (`[command]`)
```
```
