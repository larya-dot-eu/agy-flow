---
name: flow-tdd
description: >-
  Phase 6 & 7 of the 10-phase engineering lifecycle: Test-Driven Development Planning & Implementation.
  Enforces isolated branch execution, test scaffolding first, the strict "Code before test = Delete & Restart" rule,
  and verified Red-Green-Refactor cycles. Trigger with /flow-tdd.
risk: critical
source: unified-superpowers
---

# Flow TDD & Implementation (`/flow-tdd`)

Phase 6 & 7: Test-Driven Development Planning & Implementation.

Execute the approved implementation plan from [`/flow-plan`](../flow-plan/SKILL.md) through strict, verifiable **Red-Green-Refactor** cycles in an isolated feature branch.

```text
  ┌─────────────────────────────────────────────────────────────┐
  │ Step 1: Branch Isolation & Clean Working Tree Check         │
  │   - git checkout -b feature/YYYY-MM-DD-[feature]            │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Step 2: Red-Green-Refactor Loop (Per Task in Plan)          │
  │                                                             │
  │   ┌──────────────┐                                          │
  │   │  1. RED      │ Write failing test for spec requirement  │
  │   │              │ Run test -> Verify expected failure!     │
  │   └──────┬───────┘                                          │
  │          │                                                  │
  │   ┌──────▼───────┐                                          │
  │   │  2. GREEN    │ Write minimal clean code to pass test    │
  │   │              │ Run test -> Verify all pass!             │
  │   └──────┬───────┘                                          │
  │          │                                                  │
  │   ┌──────▼───────┐                                          │
  │   │  3. REFACTOR │ Optimize architecture & readability      │
  │   │              │ Run full test suite -> Verify green!     │
  │   └──────────────┘                                          │
  │                                                             │
  │   - Mark task complete (- [x]) in docs/plans/ artifact      │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Step 3: All Tasks Complete ──► Handoff to /flow-release     │
  └─────────────────────────────────────────────────────────────┘
```

<HARD-GATE>
Strict Bright-Line Authority Rule:
Wrote production code before writing the test? DELETE IT. Start over with the test. No exceptions.
Never write a test without running it to verify it fails for the expected reason.
Never declare a task complete without running the verification command and verifying green.
</HARD-GATE>

---

## 1. Branch Isolation & Workspace Setup

Before touching any source files:
1. **Clean Tree Verification**: Run `git status` to verify there are no uncommitted changes.
2. **Baseline Test Suite Run**: Execute the existing test suite to confirm a clean starting baseline.
3. **Create Dedicated Feature Branch**:
   ```bash
   git checkout -b feature/YYYY-MM-DD-[feature-name]
   ```

---

## 2. The Deterministic Red-Green-Refactor Engine

Execute each task defined in `docs/plans/YYYY-MM-DD-[feature]-plan.md` using the exact 3-step discipline:

### Step 1: RED (Test-First Scaffolding)
- Add the test function to the test file exactly as written in the plan.
- **Run the verification command**:
  ```bash
  pytest tests/unit/test_target.py -v
  ```
- **Verify Failure Mode**: Confirm the test fails specifically due to the missing implementation/assertion, **not** due to an unrelated syntax or import error.

### Step 2: GREEN (Minimal Implementation)
- Write the minimal, cleanest production code needed to satisfy the failing test assertion.
- **Run the verification command**:
  ```bash
  pytest tests/unit/test_target.py -v
  ```
- **Verify Success**: Confirm the test passes cleanly (`1 passed`).

### Step 3: REFACTOR (Code Cleanliness & Polish)
- Eliminate duplication, improve naming, ensure type annotations, and preserve documentation.
- **Run the full test suite**: Confirm zero regressions across all existing tests.
- **Commit Atomically**:
  ```bash
  git add <test_files> <source_files>
  git commit -m "feat(scope): implement [task description] with tests"
  ```

---

## 3. Plan & Task Artifact Maintenance

1. After completing each task step, update the checkbox in `docs/plans/YYYY-MM-DD-[feature]-plan.md`:
   ```markdown
   - [x] Task 1.1: Write failing interface contract test (Red)
   - [x] Task 1.2: Implement validator (Green)
   ```
2. Re-read the next task in the plan artifact before starting the next Red-Green cycle to ensure zero context drift.

---

## 4. Exit Gate & Transition to Phase 8, 9 & 10

When all tasks in the plan are marked complete:
1. Run the entire test suite and project linters:
   ```bash
   # Run full project test suite
   pytest
   npm test
   cargo test
   go test ./...
   ```
2. Confirm 100% tests passing and clean git status.
3. Transition directly to **[`/flow-release`](../flow-release/SKILL.md)** (Phase 8, 9 & 10).
