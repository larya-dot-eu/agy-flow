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

Translate approved specifications from [`/flow-spec`](../flow-spec/SKILL.md) into concrete, bite-sized, test-first implementation plans.

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
  │  - Absolute "No Placeholders" Law (Actual code blocks, no TBDs)          │
  │  - Bite-Sized Atomic Tasks (2–5 min steps: Red Test -> Green -> Commit)  │
  │  - Exact Interface Contracts Consumed & Produced                         │
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
The implementation plan must be authored to disk at docs/plans/YYYY-MM-DD-[feature]-plan.md, self-reviewed against the No-Placeholders Law, and submitted to /flow-review before any coding begins.
</HARD-GATE>

---

## 1. The Plan Authoring Mental Model

When writing implementation plans, assume the downstream implementing engineer:
1. **Has Zero Context**: Knows nothing about our repo tools, conventions, or problem domain.
2. **Has Questionable Taste**: Will take shortcuts, skip edge cases, or write weak assertions if not given exact code and commands.
3. **Needs Bite-Sized Steps**: Reasons best when each step takes **2–5 minutes** and modifies a single focused unit.

---

## 2. The 5 Adversarial Questions Pre-Flight Audit

Before authoring tasks, systematically evaluate and document:
1. **Hidden Assumptions**: What unvalidated assumptions are being made regarding existing APIs, dependencies, environment variables, or database state?
2. **Failure Modes & Edge Cases**: Where is this implementation most fragile under concurrency, network timeouts, invalid inputs, or load spikes?
3. **Rollback & Blast Radius**: If this change fails in production, what is the exact step-by-step rollback strategy that guarantees zero data loss or corruption?
4. **Dependency & Ordering Deadlocks**: Are there circular imports, database schema-versus-code migration ordering locks, or deployment dependencies?
5. **Observability & Debuggability**: What structured logs, metrics, or traces must be emitted to make failures immediately diagnosable?

---

## 3. The Absolute "No Placeholders" Law

Every task step must contain the **exact, complete code** and **exact commands**. The following are strict plan violations:
- ❌ `"TBD"`, `"TODO"`, `"implement later"`, `"fill in details"`.
- ❌ `"Add appropriate validation and error handling"` (Provide the exact validation logic and error classes).
- ❌ `"Write tests for the above"` (Provide the full, runnable test function with exact assertions).
- ❌ `"Similar to Task 1"` (Repeat or specialize the code; executors read tasks independently).
- ❌ Describing actions without showing code blocks.

---

## 4. Implementation Plan Document Template

Plans are saved to: `docs/plans/YYYY-MM-DD-[feature-name]-plan.md`.

````markdown
# Implementation Plan: [Feature Name]

- **Date**: YYYY-MM-DD
- **Spec Reference**: [Specification Link](docs/specs/YYYY-MM-DD-[feature]-spec.md)
- **Status**: Draft | Under Review | Approved | In Implementation
- **Branch Target**: `feature/YYYY-MM-DD-[feature-name]`

---

## 1. 5 Adversarial Questions Assessment
1. **Hidden Assumptions & Validation**: [Explicit findings]
2. **Failure Modes & Defenses**: [Defensive patterns used]
3. **Rollback Strategy**: [Exact rollback runbook]
4. **Ordering & Migration Dependencies**: [Sequencing rules]
5. **Observability & Health Checks**: [Logs and metrics]

---

## 2. Global Constraints & Interfaces
- **Language / Runtime floor**: e.g., Python 3.11+, Node 20+, Go 1.22+
- **Key Dependencies**: Exact packages/libraries to use
- **File Structure Map**: List of all files created or modified with single responsibilities

---

## 3. Milestone Breakdown & Bite-Sized Tasks

### Milestone 1: [Milestone Name]

#### Task 1.1: [Component / Unit Name]
**Files:**
- Create: `src/domain/token_validator.py`
- Test: `tests/unit/test_token_validator.py`

**Interfaces:**
- **Consumes**: `AuthHeader(raw: str) -> TokenPayload`
- **Produces**: `validate_token(token: str) -> Result[UserSession, AuthError]`

- [ ] **Step 1: Write the failing test (Red)**
```python
# tests/unit/test_token_validator.py
import pytest
from src.domain.token_validator import validate_token, AuthError

def test_validate_token_expired_raises_auth_error():
    expired_token = "eyJhbGciOi..."
    with pytest.raises(AuthError) as exc_info:
        validate_token(expired_token)
    assert "token expired" in str(exc_info.value).lower()
```

- [ ] **Step 2: Run test to verify expected failure**
Run: `pytest tests/unit/test_token_validator.py -v`
Expected Output: `FAIL with ImportError or NameError: 'validate_token' is not defined`

- [ ] **Step 3: Write minimal implementation (Green)**
```python
# src/domain/token_validator.py
class AuthError(Exception):
    pass

def validate_token(token: str):
    if not token or is_expired(token):
        raise AuthError("Token expired")
    return UserSession(user_id="u123")
```

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/unit/test_token_validator.py -v`
Expected Output: `1 passed`

- [ ] **Step 5: Commit**
```bash
git add tests/unit/test_token_validator.py src/domain/token_validator.py
git commit -m "feat(auth): implement token expiration validation with tests"
```

---

## 4. Acceptance Criteria Verification Matrix

| Spec Criteria ID | Test File & Function | Verification Command |
| :--- | :--- | :--- |
| **AC-01** | `tests/unit/test_token_validator.py::test_validate_token_expired` | `pytest tests/unit/test_token_validator.py` |
| **AC-02** | `tests/unit/test_token_validator.py::test_valid_token_returns_session` | `pytest tests/unit/test_token_validator.py` |
| **AC-03** | `tests/integration/test_auth_flow.py::test_end_to_end_login` | `pytest tests/integration/test_auth_flow.py` |

---

## 5. Rollback & Contingency Runbook
- **Rollback Command**: `git revert [commit-hash]` or `alembic downgrade -1`
- **Feature Flag Key**: `flags.enable_new_auth` (default: `false`)
````

---

## 5. Plan Self-Review Checklist (Mandatory Inline Audit)

Before saving and submitting to `/flow-review`, the agent must verify:
1. **Spec Coverage**: Is every single Acceptance Criterion (`AC-XX`) in the spec accounted for in a specific task?
2. **Placeholder Scan**: Search the plan text for `TODO`, `TBD`, or missing code blocks.
3. **Type & Signature Consistency**: Do function names and signatures defined in Task 1 match what is consumed in Task 3?
4. **Task Right-Sizing**: Is every step executable in 2–5 minutes with clear pass/fail verification?

---

## 6. Exit Gate & Handoff to `/flow-review`

1. Save the plan to `docs/plans/YYYY-MM-DD-[feature]-plan.md`.
2. Announce readiness:
   > *"Implementation plan authored and audited at [`docs/plans/YYYY-MM-DD-[feature]-plan.md`](docs/plans/). Submitting to [`/flow-review`](../flow-review/SKILL.md) for adversarial review."*
3. Transition directly to **[`/flow-review`](../flow-review/SKILL.md)** (Phase 5).
