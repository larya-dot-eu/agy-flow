# Independent Disproof-First Validator & Sandboxed Probe Protocol

## 1. Validator Role & Independence <!-- ANCHOR: VALIDATOR_ROLE -->

The Validator subagent is invoked via the `invoke_subagent` tool (`"TypeName": "self"`) after all Specialist subagents complete and the orchestrator deduplicates overlapping candidate hypotheses into `docs/plans/.tmp/prcheck-candidates-[target_id].json`.
- **Anti-Sycophancy Rule**: Treat every specialist candidate finding as an **unproven hypothesis**, never an established fact. Your primary duty is to **try to disprove** the claim first using surrounding code, callers, and existing guards before confirming it.
- **Tool & Scratchpad Discipline**: Target directory `docs/plans/.tmp` is pre-verified by the orchestrator. Write the completed 4-part scorecard (`skills/flow-prcheck/resources/prcheck-report.md.template`) directly to `docs/plans/.tmp/prcheck-[target_id].md` using the `write_to_file` tool. You MUST NOT execute shell commands (`mkdir`, `touch`, `bash`) to verify or create directories, and you MUST NOT invoke child subagents.

---

## 2. The 5-Step Disproof-First Validation Sequence <!-- ANCHOR: VALIDATION_SEQUENCE -->

For each deduplicated candidate finding, execute these 5 steps in order:

1. **Step 1 — Neutral Hypothesis Ingestion**:
   - Read the target `file`, `line`, `affected_behavior`, and `trigger_preconditions` without adopting the specialist's rhetorical certainty.
2. **Step 2 — Active Counterevidence & Caller Search**:
   - Use `view_file` and `grep_search` to inspect the surrounding function, upstream callers, type annotations, and validation helpers.
   - Search explicitly for any guard, invariant, or caller constraint that makes the alleged failure impossible (`counterevidence_checked`).
3. **Step 3 — Targeted Sandboxed Probe Execution (Only When Informative)**:
   - Do **not** require a runtime probe for static authorization gaps, race conditions, or contract mismatches that are proven deterministically by code reasoning.
   - When runtime execution adds decisive evidence **and** probes are enabled (`flags.allow_probes == true`), write a minimal probe script inside a temporary path and execute it exclusively via:
     ```bash
     python3 scripts/flow_prcheck.py --run-probe <probe_script_path>
     ```
   - Never execute raw untrusted code outside `--run-probe`, and reuse a single shared test-suite execution snapshot when checking multiple findings against the same test runner.
4. **Step 4 — Base vs. Head Regression Comparison**:
   - Check whether the failure was introduced by this diff or already existed at `eligibility.merge_base` / `eligibility.base_ref`.
5. **Step 5 — 5-State Evidence Classification & Internal Ranking (`0`–`100`)**:
   - Classify each candidate into one of the 5 explicit `evidence_state` values below and assign an internal `ranking_score` (`0`–`100`).

---

## 3. Five-State Evidence Taxonomy & Routing Rules <!-- ANCHOR: EVIDENCE_STATES -->

| `evidence_state` | Definition | Report Destination | Inline GitHub PR Comment? |
| :--- | :--- | :--- | :--- |
| **`reproduced_regression`** | Behavior succeeds at `base_ref`/`merge_base` and fails at `head_ref`/working tree | **1. Confirmed Findings** (when `ranking_score >= threshold`) | **Yes** |
| **`confirmed_by_code_reasoning`** | Failure follows deterministically from inspected code, callers, and explicit contract premises | **1. Confirmed Findings** (when `ranking_score >= threshold`) | **Yes** |
| **`pre_existing`** | Behavior already fails at `base_ref`/`merge_base` prior to this change | **3. Checks Blocked or Skipped** | **No** |
| **`blocked`** | Validation could not complete (probes disabled in PR mode, missing companion PR, or external service unavailable) | **4. High-Impact Questions Requiring Human Review** (when `severity == "blocking"`) | **No** |
| **`rejected`** | Counterevidence in surrounding code, callers, or probe output contradicts the hypothesis | Dropped from report | **No** |

---

## 4. Internal Ranking Rubric (`0`–`100`) <!-- ANCHOR: RANKING_RUBRIC -->

- **`90`–`100` (Deterministic Proof)**: Reproduced via `--run-probe` regression or proven with zero-ambiguity caller trace violating an explicit contract/invariant.
- **`75`–`89` (High-Confidence Defect)**: Concrete input trigger traced through code with no guarding check in callers (`Default cutoff: >= 75`).
- **`50`–`74` (Plausible but Conditional)**: Depends on external configuration or unverified caller input; excluded from Confirmed Findings.
- **`0`–`49` (Disproven / Speculative / Style Nit)**: Contradicted by existing guards or purely stylistic preference (`rejected`).
