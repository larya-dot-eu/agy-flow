---
name: flow-review
description: >-
  Phase 5 of the 10-phase engineering lifecycle: Adversarial Review & Loop-back Routing.
  Dispatches an independent subagent auditor to red-team specifications and implementation plans
  for completeness, security, buildability, and loop-back routing. Trigger with /flow-review.
risk: critical
source: unified-superpowers
---

# Flow Adversarial Review (`/flow-review`)

Phase 5: Adversarial Review & Loop-back Routing.

Perform an independent, calibrated adversarial audit of the Specification (`docs/specs/`) and Implementation Plan (`docs/plans/`) before any code is written.

```text
               ┌────────────────────────────────────────────────────────┐
               │ Phase 05: Ingest Spec & Plan Files                     │
               │   - Spec: docs/specs/YYYY-MM-DD-[feature]-spec.md      │
               │   - Plan: docs/plans/YYYY-MM-DD-[feature]-plan.md      │
               └───────────────────────────┬────────────────────────────┘
                                           │
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │ Dispatch Subagent Auditor (invoke_subagent: self)      │
               │   - Completeness & Zero-Placeholder Audit              │
               │   - Spec-to-Plan Traceability & Invariant Check        │
               │   - Buildability & Concurrency/Security Analysis       │
               │   - Review Calibration (Blockers vs Advisory Notes)    │
               └───────────────────────────┬────────────────────────────┘
                                           │
       ┌───────────────────────────────────┼───────────────────────────────────┐
       ▼                                   ▼                                   ▼
[Major Concept Gap]               [Spec Incompleteness]               [Plan Task Flaws]
       │                                   │                                   │
       ▼                                   ▼                                   ▼
Loop back to:                       Loop back to:                       Loop back to:
/flow-brainstorm                    /flow-spec                          /flow-plan
(Phase 01-02)                       (Phase 03)                          (Phase 04)
                                           │
                                           ▼ [ALL AUDIT GATES PASSED]
                                 ┌───────────────────┐
                                 │ Implementation    │ ──► Unlock /flow-tdd (Phase 06-07)
                                 │ Gate Approved     │
                                 └───────────────────┘
```

<HARD-GATE>
Do NOT proceed to implementation (/flow-tdd) until all 4 audit categories pass with zero blocking defects.
Only genuine blockers halt progress—advisory recommendations do NOT block approval.
</HARD-GATE>

---

## 1. Review Calibration Law

Auditors must strictly separate **Blockers** from **Advisory Recommendations**:

| Category | Definition | Action |
| :--- | :--- | :--- |
| **BLOCKER (Halts Approval)** | Critical issues causing implementation failure: missing acceptance criteria, placeholder code (`TODO`/`TBD`), contradictory steps, undefined types, security bypasses, or tasks too vague to execute. | **Triggers Loop-Back**. Must be resolved before `/flow-tdd`. |
| **ADVISORY (Does NOT Block)** | Minor phrasing preferences, alternate variable naming, stylistic preferences, or non-critical "nice to have" suggestions. | **Recorded in scorecard**, but approval is **GRANTED**. |

---

## 2. The 4 Audit Dimensions

The auditor audits against 4 core categories:

1. **Completeness & Zero Placeholders**:
   - Zero `TODO`, `TBD`, or `"implement later"` statements in spec or plan.
   - Every task step contains actual runnable code blocks and explicit test commands.
2. **Spec-to-Plan Alignment & Traceability**:
   - Every Acceptance Criterion (`AC-XX`) in the spec is covered by a corresponding Red test task in the plan.
   - Zero orphan tasks in the plan (scope creep).
3. **Buildability & Task Granularity**:
   - Could an engineer with zero context follow this plan step-by-step without getting stuck?
   - Tasks are right-sized (2–5 minutes per step).
4. **Security, Concurrency & Blast Radius**:
   - Boundary inputs validated, auth checks in place, zero credentials in fixtures.
   - Database transactions, mutexes, idempotency keys, and rollback steps verified.

---

## 3. Subagent Auditor Dispatch Protocol

To guarantee objectivity, the lead orchestrator dispatches an independent subagent auditor using `invoke_subagent` with `TypeName: "self"`:

```json
{
  "TypeName": "self",
  "Role": "Adversarial Plan Auditor",
  "Prompt": "You are an adversarial document auditor and principal systems architect. Perform a calibrated, ruthless red-team audit of the implementation plan at docs/plans/YYYY-MM-DD-[feature]-plan.md against the specification at docs/specs/YYYY-MM-DD-[feature]-spec.md.\n\nAudit Dimensions:\n1. Completeness & Zero Placeholders (Scan for TODO, TBD, unwritten code blocks)\n2. Spec-to-Plan Traceability (1-to-1 AC-XX mapping, type consistency)\n3. Buildability & Task Granularity (2-5 min steps, no missing context)\n4. Security, Concurrency & Rollback Runbook\n\nCalibration Rule:\nONLY flag issues that would cause runtime failures, security holes, implementation deadlocks, or spec divergence as BLOCKERS. Phrasing preferences and stylistic choices are ADVISORY and must not block approval.\n\nOutput the standard Adversarial Review Scorecard with Status (APPROVED | REVISION REQUIRED), Blocking Issues, and Advisory Recommendations."
}
```

Detailed reference template: [`references/auditor-prompt.md`](references/auditor-prompt.md).

---

## 4. The 3-Way Loop-Back Decision Engine

When blocking defects are discovered, route precisely to the responsible lifecycle phase:

```text
               ┌───────────────────────┐
               │ Adversarial Findings  │
               └───────────┬───────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
[Major Domain /     [Contract / Schema  [Task Scaffolding /
 Architecture Gap]   Ambiguity in Spec]  Missing Code in Plan]
       │                   │                   │
       ▼                   ▼                   ▼
Loop back to:       Loop back to:       Loop back to:
/flow-brainstorm    /flow-spec          /flow-plan
(Phase 01-02)       (Phase 03)          (Phase 04)
```

---

## 5. Standardized Review Scorecard Output

```markdown
# Adversarial Review Scorecard: [Feature Name]

- **Date**: YYYY-MM-DD
- **Spec Audited**: `docs/specs/YYYY-MM-DD-[feature]-spec.md`
- **Plan Audited**: `docs/plans/YYYY-MM-DD-[feature]-plan.md`
- **Status**: APPROVED | REVISION REQUIRED

---

### Audit Category Results
1. **Completeness & Zero Placeholders**: [PASS / FAIL] — [Notes]
2. **Spec-to-Plan Traceability**: [PASS / FAIL] — [Notes]
3. **Buildability & Granularity**: [PASS / FAIL] — [Notes]
4. **Security, Concurrency & Rollback**: [PASS / FAIL] — [Notes]

---

### Blocking Issues (Require Resolution Before Implementation)
- [Task X.Y / Spec Section Z]: [Specific blocking defect and why it causes failure] — [Required Fix]
*(If none, state: "None. Zero blocking defects.")*

---

### Advisory Recommendations (Non-Blocking)
- [Suggestion 1]
- [Suggestion 2]

---

### Decision & Next Phase Transition
- **Decision**: [APPROVED / LOOP-BACK]
- **Next Command**: `/flow-tdd` (or `/flow-plan` / `/flow-spec` / `/flow-brainstorm`)
```

---

## 6. User Gate & Authorization

1. Present the completed Review Scorecard to the user.
2. If approved, ask for final confirmation:
   > *"Adversarial audit completed and **APPROVED**. Ready to begin Phase 6 & 7 implementation via [`/flow-tdd`](../flow-tdd/SKILL.md) on branch `feature/YYYY-MM-DD-[feature]`. Please confirm to proceed."*
3. On confirmation, transition directly to **`/flow-tdd`**.
