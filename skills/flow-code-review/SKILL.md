---
name: flow-code-review
description: >-
  Phase 7.5 of the 10-phase engineering lifecycle: Adversarial Code & Implementation Review.
  Dispatches an independent subagent auditor to review branch diffs against specifications and plans
  for correctness, security, test rigor, and YAGNI simplicity before release. Trigger with /flow-code-review.
risk: critical
source: unified-superpowers
---

# Flow Code Review (`/flow-code-review`)

Phase 7.5: Adversarial Code & Implementation Review.

Perform an independent, calibrated adversarial audit of the working branch implementation (`git diff <base-branch>...HEAD`) against the approved specification (`docs/specs/`) and implementation plan (`docs/plans/`) before moving to `/flow-release`.

```text
               [/flow-code-review Invoked or Handoff from /flow-tdd]
                                         │
                           ┌─────────────▼─────────────┐
                           │ 1. Git Diff & Baseline    │ ──► Verify clean tree & green tests
                           └─────────────┬─────────────┘
                                         │
                           ┌─────────────▼─────────────┐
                           │ 2. Dispatch Subagent      │ ──► invoke_subagent (TypeName: "self")
                           │    Code Reviewer          │     using references/reviewer-prompt.md
                           └─────────────┬─────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
        [REVISION REQUIRED]                                 [APPROVED]
                 │                                               │
                 ▼                                               ▼
       Surgical Inline Fixes                           Update Plan: Implemented & Tested
       via Red-Green-Refactor                          Commit & Handoff to /flow-release
```

<HARD-GATE>
1. **Pre-Flight Green Baseline**: You MUST run the full project test suite and linters before dispatching the code reviewer.
2. **Subagent Isolation**: The code review MUST be conducted by an independent subagent (`invoke_subagent` with `TypeName: "self"` and `Role: "Implementation Code Reviewer"`) to guarantee unbiased evaluation.
3. **No Merging / Release on Blockers**: You MUST NOT proceed to `/flow-release` until all blocking defects are resolved and verified green.
</HARD-GATE>

---

## 1. Review Calibration Law

Auditors must strictly categorize findings into **Blockers** vs **Advisory Recommendations**:

| Category | Definition | Action |
| :--- | :--- | :--- |
| **BLOCKER (Halts Approval)** | Runtime bugs, security flaws (secrets, auth bypass, IDOR), missing spec criteria (`AC-XX`), broken typings, unhandled exceptions, or YAGNI bloat. | **Triggers Revision Loop**. Must be fixed via Red-Green-Refactor before release. |
| **ADVISORY (Does NOT Block)** | Non-critical naming suggestions, minor stylistic preferences, or maintainability tips. | **Recorded in Scorecard**, but verdict is **APPROVED**. |

---

## 2. The 5 Core Code Review Dimensions

The auditor performs an adversarial inspection across 5 dimensions:

1. **Spec & AC Conformance (1-to-1 Mapping)**:
   - Verify every Acceptance Criterion (`AC-XX`) in `docs/specs/` is fully implemented and tested.
   - Confirm zero missed error flows or edge cases.
2. **Code Quality, Typings & Architecture**:
   - Verify strict static typing (zero unjustified `any` or loose types).
   - Ensure clean module boundaries and docstring integrity.
3. **Security, Auth & Defensive Programming**:
   - Scan for hardcoded credentials, tokens, or plaintext secrets.
   - Verify server-side input validation and authentication/authorization boundaries.
4. **Test Assertion Rigor & Behavioral Checks**:
   - Confirm tests assert actual business invariants and error responses (zero tautological assertions).
   - Verify negative and edge-case test coverage.
5. **YAGNI Simplicity & Scope Control**:
   - Flag single-use abstractions, dead code, or temporary debug logs (`console.log`, `print`).
   - Confirm no unrequested dependencies were introduced.

---

## 3. Subagent Auditor Dispatch Protocol

The orchestrator dispatches an independent subagent auditor using `invoke_subagent` with `TypeName: "self"`:

```json
{
  "TypeName": "self",
  "Role": "Implementation Code Reviewer",
  "Prompt": "You are an adversarial lead software engineer and code reviewer. Your mission is to perform a rigorous code review of git diff main...HEAD against docs/specs/ and docs/plans/.\n\nRead the prompt instructions at: skills/flow-code-review/references/reviewer-prompt.md.\n\nAudit Dimensions:\n1. Spec & AC Conformance (1-to-1 AC mapping, zero missed criteria)\n2. Code Quality & Typing (strict types, clean errors, docstrings)\n3. Security & Auth (no secrets, validation at boundaries, auth checks)\n4. Test Assertion Rigor (real behavioral checks, negative test cases)\n5. YAGNI & Scope Control (no dead code, no debug logs, no unrequested dependencies)\n\nCalibration Rule:\nOnly flag runtime bugs, security issues, missing criteria, or broken types as BLOCKERS. Phrasing preferences are ADVISORY.\n\nWrite the completed report using skills/flow-code-review/resources/code-review.md.template to docs/plans/.tmp/code-review-[feature].md. Announce your verdict (APPROVED or REVISION REQUIRED) and summary in chat."
}
```

---

## 4. Surgical Resolution & Handoff Protocol

### If `REVISION REQUIRED`:
1. Read the report at `docs/plans/.tmp/code-review-[feature].md`.
2. For each blocking defect:
   - Write a failing test for the defect (Red).
   - Fix the code (Green).
   - Refactor & commit atomically.
3. Re-run verification until all blockers are resolved.

### If `APPROVED`:
1. Update `docs/plans/YYYY-MM-DD-[feature]-plan.md` header:
   ```markdown
   - **Status**: Implemented & Tested
   ```
2. Commit the plan artifact:
   ```bash
   git add docs/plans/
   git commit -m "docs(plan): mark implementation plan as Implemented & Tested"
   ```
3. Announce readiness:
   > *"Code review completed and **APPROVED**. Transitioning to Phase 8, 9 & 10 ([`/flow-release`](../flow-release/SKILL.md))."*
4. Transition directly to **[`/flow-release`](../flow-release/SKILL.md)**.
