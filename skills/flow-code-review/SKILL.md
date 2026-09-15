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
2. **Subagent Isolation & Read-Only Review**: The code review MUST be conducted by an independent subagent (`invoke_subagent` with `TypeName: "self"` and `Role: "Senior Code Reviewer"`). The reviewer operates in strict read-only mode and must not dispatch child subagents.
3. **No Merging / Release on Critical Blockers**: You MUST NOT proceed to `/flow-release` until all Critical/Important blocking defects are resolved and verified green.
</HARD-GATE>

---

## 1. Review Calibration Law

Auditors must categorize findings by actual severity, acknowledging strengths before listing issues:

| Category | Definition | Action |
| :--- | :--- | :--- |
| **Critical (Must Fix)** | Bugs, security vulnerabilities, data loss risks, broken functionality, or unhandled crashes. | **Triggers Revision Loop**. Must be resolved via Red-Green-Refactor before release. |
| **Important (Should Fix)** | Architecture flaws, missing planned features, poor error handling, or test gaps. | **Requires Fix** unless human explicitly overrides. |
| **Minor (Nice to Have)** | Code style, micro-optimizations, or documentation polish. | **Advisory only**. Does not block merge approval. |

---

## 2. What the Code Reviewer Audits

1. **Plan & Requirements Alignment**:
   - Does the implementation match the plan / requirements?
   - Are deviations justified improvements or problematic departures?
   - Is all planned functionality present with zero orphaned tasks?
2. **Code Quality & Separation of Concerns**:
   - Clean architecture and modular boundaries?
   - Strict static typing and proper exception hierarchies?
   - DRY without premature over-abstraction?
3. **Architecture & Defensive Security**:
   - Sound design decisions and reasonable performance?
   - Zero hardcoded secrets, valid authentication/authorization, no IDOR or injection risks.
   - Integrates cleanly with surrounding code.
4. **Test Assertion Rigor**:
   - Tests verify real business behavior, not superficial mocks or tautologies.
   - Negative test cases, timeouts, and edge cases covered.
   - All tests passing.
5. **Production Readiness & YAGNI Simplicity**:
   - Backward compatibility and database migration strategy considered.
   - Zero dead code, orphaned imports, or temporary debug logs.
   - Documentation complete.

---

## 3. Subagent Auditor Dispatch Protocol

The orchestrator dispatches an independent subagent auditor using `invoke_subagent` (`TypeName: "self"`) populated from `references/reviewer-prompt.md`:

```json
{
  "TypeName": "self",
  "Role": "Phase 7.5 Code Reviewer",
  "Prompt": "You are the Phase 7.5 Adversarial Code Reviewer for the Antigravity Flow engineering lifecycle. Switch from generation mode to review mode: your job is to rigorously review the completed implementation against its specification and plan, identifying defects and architectural decay before release.\n\n## Context & Inputs\n- Feature: [FEATURE_NAME]\n- Specification: docs/specs/YYYY-MM-DD-[feature]-spec.md\n- Plan: docs/plans/YYYY-MM-DD-[feature]-plan.md\n- Base Revision: [BASE_REF]\n- Head Revision: [HEAD_REF]\n\n## Inspection Commands\ngit diff --stat [BASE_REF]..[HEAD_REF]\ngit diff [BASE_REF]..[HEAD_REF]\ngit log --oneline [BASE_REF]..[HEAD_REF]\n[TEST_COMMAND]\n\n## Hard Execution Constraints\n1. Strict Read-Only Mode: Do NOT mutate the working tree, index, HEAD, or branch state.\n2. Anti-Recursion Directive: Do NOT invoke child subagents. Perform the review yourself.\n3. Evidence Before Assertions: Every issue MUST include an exact file:line reference.\n\n## The 5 Antigravity Flow Audit Dimensions\n1. Spec & AC Conformance (AC-XX)\n2. Code Quality & Clean Architecture\n3. Defensive Security & Robustness\n4. Test Assertion Rigor\n5. Production Readiness & YAGNI Simplicity\n\n## Severity Calibration\n- Critical (Must Fix): Bugs, security holes, data loss, broken contracts, missing ACs.\n- Important (Should Fix): Architecture flaws, missing error handling, test gaps.\n- Minor (Nice to Have): Code style, micro-optimizations, polish.\n\n## Output Format\nWrite the completed scorecard using skills/flow-code-review/resources/code-review.md.template to docs/plans/.tmp/code-review-[feature].md. Return Strengths, Issues (Critical / Important / Minor), Recommendations, and Assessment (Ready to merge: Yes | No | With fixes)."
}
```

---

## 4. Surgical Resolution & Handoff Protocol

### If `REVISION REQUIRED` (Critical / Important Issues Found):
1. Read the scorecard at `docs/plans/.tmp/code-review-[feature].md`.
2. For each Critical / Important issue:
   - Write a failing test for the defect (Red).
   - Fix the minimal code to resolve it (Green).
   - Refactor & commit atomically.
3. Re-run verification until all blockers are resolved.

### If `APPROVED` (`Ready to merge: Yes`):
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
   > *"Code review completed and **APPROVED**. Ready to merge. Transitioning to Phase 8, 9 & 10 ([`/flow-release`](../flow-release/SKILL.md))."*
4. Transition directly to **[`/flow-release`](../flow-release/SKILL.md)**.
