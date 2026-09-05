# Agent Collaboration Research & Tooling

This document outlines options for improving the feedback loop between human PMs, Claude Code (reviewer), and Jules (async implementer) to minimize round trips and rejected PRs.

## 1. Automating Review Checks (CI Guardrails)

We need to mechanically reject specific failures before a human or Claude reviews the PR.

*   **Failure:** Committed scratch files (e.g., `pr_body.txt`).
    *   **Option:** `tj-actions/changed-files` (MIT, active) can detect modifications to unexpected files in CI.
    *   **URL:** [https://github.com/tj-actions/changed-files](https://github.com/tj-actions/changed-files)
    *   **Recommendation:** Use a simple Bash script hooked into a GitHub Action that fails the build if `pr_body.txt` exists.

*   **Failure:** Out-of-scope files touched.
    *   **Option:** GitHub `CODEOWNERS` combined with required status checks, or Danger JS.
    *   **URL:** [https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
    *   **Recommendation:** Danger JS can read the PR diff and fail if files outside the scoped directory (based on PR title or branch name) are touched.

*   **Failure:** AI-attribution footers in commit messages.
    *   **Option:** `amannn/action-semantic-pull-request` (MIT, active) enforcing Conventional Commits. Alternatively, a custom `commit-msg` git hook via `pre-commit`.
    *   **URL:** [https://github.com/amannn/action-semantic-pull-request](https://github.com/amannn/action-semantic-pull-request)
    *   **URL:** [https://github.com/pre-commit/pre-commit](https://github.com/pre-commit/pre-commit)
    *   **Recommendation:** A lightweight custom GitHub Action running a regex over the PR body and commit messages to reject "Generated with" or "Co-Authored-By".

*   **Failure:** Duplicate test definitions or new xfail markers.
    *   **Option:** Danger JS (MIT, active) or custom `grep` steps in GitHub Actions.
    *   **URL:** [https://github.com/danger/danger-js](https://github.com/danger/danger-js)
    *   **Recommendation:** Danger JS allows writing rules in TypeScript to statically analyze diffs. It can easily grep added lines for `xfail` or check for duplicate block definitions within the PR's scope.

**Shortlist (Highest Leverage First):**
1. Implement Danger JS for diff analysis (catches xfail markers, duplicate tests, scope creep).
2. Custom GitHub Action to explicitly forbid `pr_body.txt` and AI footers.

## 2. Getting Jules's First Pass Right

*   **Task Spec Formatting:** Provide Jules with a strict "Definition of Done" template. Use markdown checkboxes.
*   **Self-Review Checklists:** Require the agent to run a script (e.g. `npm run self-audit`) that executes a local test suite or linter before submitting.
*   **Draft PRs:** Have Jules open a Draft PR initially. A GitHub Action runs the CI checks (Danger JS, etc.). Only if CI is green does Jules (or a bot) mark it "Ready for Review".
*   **Example Tooling:** A template system inside the repo (like the existing `templates/spec.md.template`) specifically for the agent to fill out as a checklist before committing.

## 3. Async Agent + Human-Reviewer Workflows

*   **Pattern:** "Asynchronous Code Generation with CI Feedback".
*   **Mechanism:** Jules pushes a branch. CI runs static analysis and tests. If CI fails, the agent is automatically re-prompted with the CI failure logs to attempt a fix, capping at 3 retries before assigning a human.
*   **Real-time Collaboration:** Note that true "real-time" collaboration (like multiplayer IDE editing) with async agents is currently immature. The most stable pattern is strictly asynchronous handoffs via Git branches and PR comments.
*   **Case Studies:** Unverified examples from the community suggest treating the agent as a junior developer: give it a branch, strict CI guardrails, and review its PRs. If the PR fails basic checks, the automation bounces it back without human intervention.

## 4. Shared Coordination Surface

*   **Tool:** GitHub Projects v2 + Issues.
    *   **URL:** [https://docs.github.com/en/issues/planning-and-tracking-with-projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
*   **Setup:**
    1.  **Backlog:** PM creates issues with strict templates.
    2.  **In Progress (Jules):** Label assigned. Jules reads issue, branches, implements, opens PR.
    3.  **In Review (Claude/Automated):** CI runs. Claude acts via automated review action or manual trigger to leave comments or auto-merge.
    4.  **Done:** Merged.
*   **Decision Log:** An append-only markdown file in the repository (e.g. `ADR` or a specific section in the roadmap doc) is the lightest, most portable way to store architectural decisions for all agents to read.
