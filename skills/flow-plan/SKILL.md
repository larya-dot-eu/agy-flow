---
name: flow-plan
description: >-
  Phase 4 of the 10-phase engineering lifecycle: Plan Writing.
  Performs the 5 Adversarial Questions check and produces actionable, test-backed implementation plans
  at docs/plans/YYYY-MM-DD-[feature]-plan.md. Enforces bite-sized tasks (2-5 min), explicit code blocks,
  and the absolute "No Placeholders" rule. Trigger with /flow-plan.
risk: critical
source: unified-superpowers
---

# Flow Plan (`/flow-plan`)

Phase 4: Implementation Plan Writing.

Translate approved specifications from [`/flow-spec`](../flow-spec/SKILL.md) into concrete, bite-sized, test-first implementation plans adhering to the canonical template at `templates/plan.md.template`.

```text
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ Input: Approved Specification (docs/specs/YYYY-MM-DD-*.md)               │
  └────────────────────────────────────┬─────────────────────────────────────┘
                                       │
                                       ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ 5 Adversarial Questions Pre-Flight Audit                                 │
  │  1. Hidden Assumptions            4. Dependency & Ordering Deadlocks     │
  │  2. Failure Modes & Edge Cases    5. Observability & Debuggability       │
  │  3. Rollback & Blast Radius                                              │
  └────────────────────────────────────┬─────────────────────────────────────┘
                                       │
                                       ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ Author Plan: docs/plans/YYYY-MM-DD-[feature]-plan.md                     │
  │  - Zero-Context Mental Model ("Zero Context / Questionable Taste")       │
  │  - Standardized Section Anchors (<!-- SECTION: ... -->)                  │
  │  - Task Right-Sizing (Smallest unit carrying independent review gate)    │
  │  - Absolute "No Placeholders" Law (Actual code blocks, zero TBDs)        │
  │  - Bite-Sized Atomic Tasks (2–5 min steps: Red -> Green -> Commit)       │
  │  - Exact Interface Contracts (Consumes & Produces signatures)            │
  │  - Acceptance Criteria Traceability Matrix                               │
  └────────────────────────────────────┬─────────────────────────────────────┘
                                       │
                                       ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ Plan Self-Review Audit & Handoff to /flow-review (Phase 05)              │
  └──────────────────────────────────────────────────────────────────────────┘
```

<HARD-GATE>
Do NOT begin writing production code or modifying existing source files during Phase 4.
The implementation plan must be authored to disk at docs/plans/YYYY-MM-DD-[feature]-plan.md using templates/plan.md.template, self-reviewed against the No-Placeholders Law, and submitted to /flow-review before any coding begins.
</HARD-GATE>

---

## 1. The Plan Authoring Mental Model (Superpowers Discipline)

When writing implementation plans, assume the downstream implementing engineer or subagent:
1. **Has Zero Context**: Knows nothing about our repo tools, conventions, or problem domain.
2. **Has Questionable Taste**: Will take shortcuts, skip edge cases, or write weak assertions if not given exact code and commands.
3. **Needs Bite-Sized Steps**: Reasons best when each step takes **2–5 minutes** and modifies a single focused unit.
4. **Executes in Isolation**: Sees only their assigned task; explicit `Consumes` and `Produces` signatures are strictly required.

---

## 2. The 5 Adversarial Questions Pre-Flight Audit

Before authoring tasks, systematically evaluate and document:
1. **Hidden Assumptions**: What unvalidated assumptions are being made regarding existing APIs, dependencies, environment variables, or database state?
2. **Failure Modes & Edge Cases**: Where is this implementation most fragile under concurrency, network timeouts, invalid inputs, or load spikes?
3. **Rollback & Blast Radius**: If this change fails in production, what is the exact step-by-step rollback strategy that guarantees zero data loss or corruption?
4. **Dependency & Ordering Deadlocks**: Are there circular imports, database schema-versus-code migration ordering locks, or deployment dependencies?
5. **Observability & Debuggability**: What structured logs, metrics, or traces must be emitted to make failures immediately diagnosable?

---

## 3. Task Right-Sizing & Boundary Rules

- **Task Boundary**: A task is the smallest unit that carries its own test cycle and is worth a fresh reviewer's gate.
- **Rule of Thumb**: Fold setup, configuration, scaffolding, and documentation steps into the task whose deliverable needs them; split only where a reviewer could meaningfully reject one task while approving its neighbor.
- **Each Step is One Action (2–5 minutes)**:
  - Step 1: Write the failing test (Red).
  - Step 2: Run it to make sure it fails for the expected reason.
  - Step 3: Implement the minimal code to make the test pass (Green).
  - Step 4: Run the tests to confirm they pass.
  - Step 5: Commit atomically.

---

## 4. The Absolute "No Placeholders" Law

Every task step must contain the **exact, complete code** and **exact commands**. The following are strict plan violations:
- ❌ `"TBD"`, `"TODO"`, `"implement later"`, `"fill in details"`.
- ❌ `"Add appropriate validation and error handling"` (Provide the exact validation logic and error classes).
- ❌ `"Write tests for the above"` (Provide the full, runnable test function with exact assertions).
- ❌ `"Similar to Task 1"` (Repeat or specialize the code; executors read tasks independently).
- ❌ Describing actions without showing code blocks.

---

## 5. Canonical Plan Template Reference

Plans **MUST** adhere to [`templates/plan.md.template`](../../templates/plan.md.template) and maintain standardized **Section Anchors** (`<!-- SECTION: ... -->`).

---

## 6. Plan Self-Review Checklist (Mandatory Inline Audit)

Before saving and submitting to `/flow-review`, the agent must verify:
1. **Spec Coverage**: Is every single Acceptance Criterion (`AC-XX`) in the spec accounted for in a specific task?
2. **Placeholder Scan**: Search the plan text for `TODO`, `TBD`, or missing code blocks.
3. **Type & Signature Consistency**: Do function names and signatures defined in Task 1 match what is consumed in Task 3?
4. **Task Right-Sizing**: Is every step executable in 2–5 minutes with clear pass/fail verification?

---

## 7. Exit Gate & Handoff to `/flow-review`

1. Save the plan to `docs/plans/YYYY-MM-DD-[feature]-plan.md`.
2. Announce readiness:
   > *"Implementation plan authored and audited at [`docs/plans/YYYY-MM-DD-[feature]-plan.md`](docs/plans/). Submitting to [`/flow-review`](../flow-review/SKILL.md) for adversarial review."*
3. Transition directly to **[`/flow-review`](../flow-review/SKILL.md)** (Phase 5).
