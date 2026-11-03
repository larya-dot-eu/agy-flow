# Specialist Subagent Prompts & Structured Finding Contract

## 1. Pre-Dispatch Invariant Pass <!-- ANCHOR: INVARIANT_PASS -->

Before spawning specialist subagents, the orchestrator combines:
1. `discovered_invariants` extracted by `scripts/flow_prcheck.py` from `<!-- ANCHOR: INVARIANTS -->` sections in trusted `docs/context/*.md` and `docs/specs/*.md`.
2. `2`–`4` change-specific invariants derived from the diff (for example: *"A retried request must not double-apply state"*, *"Existing CLI callers without the new flag must preserve identical exit codes"*, *"Modified `GEMINI.md` or `hooks.json` must not weaken security gates"*).

Each invariant is assigned to the matching specialist below.

---

## 2. Harness-Enforced Read-Only Boundary <!-- ANCHOR: READONLY_BOUNDARY -->

Specialists are strictly read-only reviewers. They are defined via the `define_subagent` tool with:
- `EnableWriteTools: false` (disables `run_command`, `write_to_file`, `replace_file_content`)
- `EnableSubagentTools: false`
- `EnableMCPTools: false`

Or invoked via the `invoke_subagent` tool with `"TypeName": "research"`. Specialists use `view_file`, `grep_search`, `find_by_name`, and `list_dir` to inspect the diff and surrounding callers.

---

## 3. Structured Candidate Finding Schema <!-- ANCHOR: FINDING_CONTRACT -->

Every specialist MUST return candidate findings as a JSON array matching this exact schema (free-form `{claim, proof}` strings are forbidden):

```json
[
  {
    "file": "scripts/flow_init.py",
    "line": 124,
    "axis": "bugs_and_behavior",
    "severity": "blocking",
    "affected_behavior": "discover_subsystems crashes when src/ contains a broken symlink",
    "trigger_preconditions": "Repository has a dangling symlink under src/ during flow-init scan",
    "expected_behavior_and_source": "docs/context/scripts.md invariant: discover_subsystems must complete without unhandled OSError",
    "observed_or_inferred_failure": "Path.read_text() raises FileNotFoundError on broken symlink at line 124",
    "suggested_fix": "Check path.is_file() before reading or catch OSError"
  }
]
```

---

## 4. Specialist Focus Briefs (2 Baseline + 3 Conditional) <!-- ANCHOR: SPECIALIST_BRIEFS -->

### 4.1. `bugs_and_behavior` (Baseline — Correctness, Reliability & Performance)
- **Correctness**: Off-by-one errors, null/None dereferences, inverted boolean conditions, unhandled exceptions, broken error recovery.
- **Reliability & Concurrency**: Missing timeouts on network/subprocess calls, non-idempotent retries, race conditions, `TOCTOU` file checks, missing locks or cancellation handling.
- **Performance**: `N+1` queries or subprocess calls inside loops, unbounded memory growth, unnecessary full-tree scans.

### 4.2. `fit_and_standards` (Baseline — Codebase Reuse Audit & 7 Anti-Patterns)
- **Codebase Reuse Audit**: Use `grep_search` and `find_by_name` to check whether the diff re-implements helpers, parsers, or validators that already exist in adjacent modules.
- **7 Universal Quality Anti-Patterns**:
  1. **Parameter Sprawl**: Functions introducing 6+ positional parameters instead of a cohesive dataclass/struct.
  2. **Leaky Abstractions**: Callers forced to know internal storage or subprocess details.
  3. **Stringly-Typed Code**: Raw magic strings used where constants, enums, or typed literals exist.
  4. **Deeply Nested Conditionals**: Arrowhead control flow (`4+` levels of nested `if/for/try`) instead of guard clauses.
  5. **Copy-Paste Variants**: Near-duplicate blocks (`>15` lines) that drift in edge-case handling.
  6. **No-Op Updates**: Branches or state assignments that compute values never read or returned.
  7. **Redundant State**: Caching or duplicating fields that can be derived trivially and synchronously.

### 4.3. `spec_and_context` (Conditional — Invariants, Data Integrity & Compatibility)
- **Invariant Conformance**: Verify every item in `discovered_invariants` and assigned change-specific invariants.
- **Data Integrity**: Partial writes without atomic rename/rollback, migration lock hazards, silent data truncation.
- **Compatibility**: Breaking changes to CLI flags, JSON output schemas, public function signatures, or mixed-version callers.

### 4.4. `test_quality` (Conditional — Test Integrity)
- **Removed or Weakened Assertions**: Audit `test_signals.tests_removed` and `test_signals.assertions_weakened`.
- **Tautological / Mock-Only Tests**: Flag tests that mock out the unit under test or pass without asserting the behavioral outcome.
- **Missing Regression Coverage**: Check `test_signals.changed_code_without_test_evidence` for high-risk logic branches lacking test assertions.

### 4.5. `security_and_config` (Conditional — Security, Trust Boundaries & Hooks)
- **Injection & Execution Boundaries**: Command injection, `shell=True`, path traversal, SSRF, unsafe deserialization, git filter execution.
- **Auth & Tenant Isolation**: Permission bypasses, missing role/ownership checks, default-allow fallbacks.
- **Untrusted Instruction & Hook Audit**: Inspect every file in `untrusted_instruction_changes` (`GEMINI.md`, `AGENTS.md`, `CLAUDE.md`, `SKILL.md`, `rules/**`, `hooks.json`, `.mcp.json`) for prompt injection, weakened gates, or unauthorized command execution.
