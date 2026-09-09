---
name: flow-review
description: >-
  Phase 5 of the 10-phase engineering lifecycle: Adversarial Review & Loop-back Routing.
  Dispatches an independent subagent auditor to red-team specifications and implementation plans
  for completeness, security, buildability, YAGNI simplicity, and loop-back routing. Trigger with /flow-review.
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
               │   - 💡 YAGNI Simplicity & Dead-Code Pruning Audit      │
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
Do NOT proceed to implementation (/flow-tdd) until all audit categories pass with zero blocking defects.
Only genuine blockers halt progress—advisory recommendations do NOT block approval.
</HARD-GATE>

---

## 1. Review Calibration Law

Auditors must strictly separate **Blockers** from **Advisory Recommendations**:

| Category | Definition | Action |
| :--- | :--- | :--- |
| **BLOCKER (Halts Approval)** | Critical issues causing implementation failure: missing acceptance criteria, placeholder code (`TODO`/`TBD`), contradictory steps, undefined types, security bypasses, unrequested abstractions (YAGNI violations), or tasks too vague to execute. | **Triggers Loop-Back**. Must be resolved before `/flow-tdd`. |
| **ADVISORY (Does NOT Block)** | Minor phrasing preferences, alternate variable naming, stylistic preferences, or non-critical "nice to have" suggestions. | **Recorded in scorecard**, but approval is **GRANTED**. |

---

## 2. The Comprehensive Adversarial Audit Dimensions

The auditor audits the plan by attempting to break it structurally, mechanically, and architecturally:

**Mechanical & Formatting Rigor:**
1. **Completeness & Zero Placeholders**: Zero `TODO`, `TBD`, or `"implement later"`. Every task step must contain actual runnable code blocks and explicit test commands.
2. **Spec-to-Plan Traceability**: Every Acceptance Criterion (`AC-XX`) must be covered by a corresponding test task. Zero orphan tasks (scope creep).
3. **Buildability & Task Granularity**: Tasks must be right-sized (bite-sized tasks under 10 minutes) with clear context.
4. **YAGNI Simplicity & Dead-Code Pruning**: Flag single-use abstractions, speculative config options, or orphaned code/imports as blockers.

**Architectural & Security Rigor:**
5. **Intermediate States & Dependency Graph**: Trace each step's intermediate state. Is the codebase consistent or broken between steps? What must already exist before each step can run?
6. **Absence is not confirmation**: An empty grep, a missing file, or a silent log means "unverified," not "safe." Widen searches and read actual source definitions.
7. **Re-attack the plan's own flagged risks**: Any claim marked "most likely wrong" or "verify on contact" is the first thing to break in this review.
8. **Abuse-case pass (Access Control)**: Attack security. Can a user reach another user's records (IDOR)? Can a protected route be hit unauthenticated? Is any input trusted before server-side validation? Every allowed cell needs a plan step that enforces it.
9. **Scale pass**: Take the Phase 3 numbers and ask what melts at peak ×10. Missing indexes? Unbounded tables? Per-user state in memory?
10. **Reinvention-and-hardcoding pass**: Does any step write logic the codebase already has? Does it hardcode strings, colors, or thresholds?
11. **Concurrency & Rollback**: Are database transactions, mutexes, and rollback steps verified?

---

## 3. Subagent Auditor Dispatch Protocol

To guarantee objectivity, the lead orchestrator dispatches an independent subagent auditor using `invoke_subagent` with `TypeName: "self"`:

```json
{
  "TypeName": "self",
  "Role": "Adversarial Plan Auditor",
  "Prompt": "You are an adversarial document auditor and principal systems architect. Switch from generation mode to review mode. Your goal is to break the plan at docs/plans/YYYY-MM-DD-[feature]-plan.md, not defend it.\n\nAudit Dimensions:\n1. Mechanical Completeness: Zero placeholders (TODO/TBD). Runnable code blocks only.\n2. Traceability: 1-to-1 AC-XX mapping. No orphan tasks.\n3. Buildability: Tasks under 10 min. No missing context.\n4. YAGNI & Dead Code: Flag single-use abstractions and orphaned imports.\n5. Intermediate States & Dependencies: Are states broken between steps? Is the dependency graph valid?\n6. Absence != Confirmation: Do not trust empty greps or missing files. Verify actual source.\n7. Re-attack Risks: Break the plan's flagged 'most likely wrong' claims first.\n8. Abuse-Case Pass: Attack access control (IDOR, auth bypass, missing validation).\n9. Scale Pass: Attack peak load (missing indexes, unbounded growth, in-memory state).\n10. Reinvention Pass: Flag duplicated logic and hardcoded values.\n11. Concurrency & Rollbacks: Validate transactions, mutexes, and rollback commands.\n\nCalibration Rule:\nONLY flag issues that would cause runtime failures, security holes, implementation deadlocks, spec divergence, or architectural decay as BLOCKERS. Phrasing preferences are ADVISORY.\n\nWrite the standard Adversarial Review Scorecard to docs/plans/.tmp/plan-review-[feature].md. Do NOT output the full text in chat; just announce completion and the final Status (APPROVED | REVISION REQUIRED)."
}
```

---

## 4. Standardized Review Scorecard Output

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
5. **YAGNI Simplicity & Anti-Overengineering**: [PASS / FAIL] — [Notes]

---

### Blocking Issues (Require Resolution Before Implementation)
- [Task X.Y / Spec Section Z]: [Specific blocking defect] — [Required Fix]
- [Additional blockers as needed...]
*(If none, state: "None. Zero blocking defects.")*

---

### Advisory Recommendations (Non-Blocking)
- [Suggestion]
- [Additional suggestions as needed...]
*(If none, state: "None.")*

---

### Loop-Back Decision & Routing

| Finding | Action |
|---|---|
| Surface fix — wrong step order, missing verification point | Return to Phase 4 and fix the plan |
| Architectural issue — wrong interface, broken dependency, broken intermediate state | Return to Phase 3 and fix the spec |
| Fundamental problem — wrong approach or wrong problem being solved | Return to Phase 2 and re-explore |

**Rollback rule:** If more than one-third of all steps of the plan need reworking, do not patch. Restart from Phase 3.

- **Decision**: [APPROVED / LOOP-BACK]
- **Next Command**: `/flow-tdd` (or `/flow-plan` / `/flow-spec` / `/flow-brainstorm`)
```

---

## 5. Loop-Back Resolution Protocol (The Surgical Edit Law)

If the scorecard returns `REVISION REQUIRED`, the Lead Orchestrator MUST resolve the blocking issues using the following strict protocol:
1. **Read the Report**: Read the report at `docs/plans/.tmp/plan-review-[feature].md`.
2. **Surgical Inline Edits**: Address the blocking issues one by one using surgical inline edits (e.g., using `replace_file_content` tools, targeted `sed` commands, or Python script replacements).
3. **NO FULL FILE REWRITES**: You **MUST NOT** rewrite, overwrite, or regenerate the entire `plan.md` document in a single write operation. Full file rewrites waste tokens and risk accidentally undoing previously approved tasks.
4. **Resubmit**: After all blockers are resolved via targeted edits, loop back to the Auditor.

---

## 6. User Gate & Authorization

1. Present the completed Review Scorecard to the user.
2. If approved, ask for final confirmation:
   > *"Adversarial audit completed and **APPROVED**. Ready to begin Phase 6 & 7 implementation via [`/flow-tdd`](../flow-tdd/SKILL.md) on branch `feature/YYYY-MM-DD-[feature]`. Please confirm to proceed."*
3. On confirmation, transition directly to **`/flow-tdd`**.
