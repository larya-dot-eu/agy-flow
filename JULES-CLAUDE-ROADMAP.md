# Jules & Claude Shared Roadmap

This is a living, shared workflow document to coordinate collaboration between the PM (human), Claude Code (reviewer/fixer), and Jules (async implementer).

## Roles

*   **PM (Human):** Defines task scope, authors specifications, makes architectural decisions, and performs final acceptance.
*   **Claude Code:** Reviews PRs opened by Jules, fixes minor mechanical issues locally, and merges approved PRs.
*   **Jules (Agent):** Operates asynchronously to research, plan, and implement code changes based on PM specifications.

## Handoff Protocol

1.  **Task Spec (PM -> Jules):** The PM provides a task using the `templates/spec.md.template` format, clearly defining the "Definition of Done," explicit assumptions, non-goals, and exactly which directories are in scope.
2.  **Implementation & Self-Review (Jules):** Jules implements the change and MUST verify its work. Jules includes a PR body describing the changes, the specific gate commands run (e.g. `node -v`, `python3 --version`, and test commands), their results, risks, and assumptions. Jules ensures no scratch files are committed.
3.  **Review (Claude):** Claude reviews the PR.
    *   If there are minor mechanical errors (e.g. stray files, formatting), Claude fixes them locally and pushes the fix.
    *   If there are major architectural violations or scope creep, Claude comments on the PR, pushing it back to Jules.
4.  **Merge (Claude/PM):** Once CI is green and the review is passed, Claude merges the PR (or the PM auto-merges on green).

## Phased Backlog of Collaboration Improvements

*Highest leverage items first. Do not implement these in the roadmap PR.*

- [ ] **Automated Guardrails (Phase 1):** Add Danger JS (or similar CI script) to reject PRs containing `pr_body.txt` or modifying files outside the declared scope.
- [ ] **Automated Guardrails (Phase 2):** Add a custom commit-msg hook or CI check to reject AI-attribution footers and ensure `[skip ci]` is used for docs-only PRs.
- [ ] **Automated Guardrails (Phase 3):** Add diff analysis to CI to detect and reject new `xfail` markers or duplicate test definitions.
- [ ] **Agent Workflow (Phase 1):** Standardize a checklist format for Jules's PR body explicitly listing execution gate commands and results.
- [ ] **Coordination (Phase 1):** Set up a GitHub Projects board to track the state of tasks (Backlog, Jules In-Progress, Claude Review, Done).

## Decision Log

*(Append-only log of workflow and architectural decisions)*

*   **2026-09-05:** Adopted strictly asynchronous handoffs for Jules (via Git branches and PRs) rather than attempting real-time concurrent editing.
*   **2026-09-05:** PR descriptions must reside solely in the GitHub PR body; scratch files like `pr_body.txt` are explicitly forbidden.
