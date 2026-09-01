# Global Antigravity Prime Directives: The 10-Phase Engineering Lifecycle

These directives are permanently active across all workspaces, sessions, and repositories on this machine.

---

## 0. The Zero-Discovery Context Routing Law

1. When entering a repository or starting a task on a specific subsystem:
   - Check if the repository's root `GEMINI.md` or `AGENTS.md` defines a `## Context Routing Map`.
   - If a matching path mapping exists, read that context document BEFORE performing broad recursive repository scans.
   - If NO map exists or the target path is unmapped, proceed using standard, minimal directory inspection without creating unrequested files.

---

## 1. The Pre-Flight Skill Invocation Law

<EXTREMELY-IMPORTANT>
If a task involves creative, constructive, architectural, or code modification work, you ABSOLUTELY MUST invoke the relevant /flow-* skill BEFORE proposing unvetted code, creating files, or making modifications.
</EXTREMELY-IMPORTANT>

- **New features / Architecture / Major refactoring**: Invoke `/flow` (or `/flow-brainstorm`).
- **Brownfield / Legacy repo onboarding**: Invoke `/flow-brainstorm` (Path D: Onboarding).
- **Distributed systems / Microservices / CQRS / Clean Arch**: Invoke `/flow-architect`.
- **Architectural decisions (Databases, frameworks, auth, brokers)**: Invoke `/flow-adr`.
- **Authoring / testing new skills**: Invoke `/flow-skill-writer`.

---

## 2. Strict Hard Gates & No-Shortcut Laws

1. **The Understanding Lock Gate (Phase 1 & 2)**:
   - Before presenting design solutions or specs, you MUST pause and present the 5–7 bullet summary, explicit assumptions, and non-goals, and wait for human confirmation.
2. **The Specification Gate (Phase 3)**:
   - Must be authored to `docs/specs/YYYY-MM-DD-[feature]-spec.md` using `templates/spec.md.template` with RFC 2119 language, quantitative SLAs, and runnable schemas. You MUST NOT start planning until the user explicitly approves the spec.
3. **The Implementation Plan Gate (Phase 4 & 5)**:
   - Must be authored to `docs/plans/YYYY-MM-DD-[feature]-plan.md` using `templates/plan.md.template` with bite-sized tasks (2–5 min), explicit `Consumes`/`Produces` interface signatures, copy-pasteable code blocks, and zero placeholders (`TODO`/`TBD`). You MUST NOT code until the plan passes adversarial audit.
4. **The TDD Deletion Rule (Phase 6 & 7)**:
   - **Wrote code before test? DELETE IT. Start over with the test. No exceptions.**
   - Never declare a task complete without running the verification command and verifying green.
5. **The Living Context & ADR Gate (Phase 9)**:
   - Any structural code changes MUST be synchronized to `docs/context/[module].md`, and architectural changes MUST be recorded in `docs/adr/NNNN-[title].md` before release closure.

---

## 3. Antigravity CLI Tooling Discipline

- **Task Tracking**: Track checklists (`- [ ]` / `- [x]`) in conversation and plan artifacts (`docs/plans/`). **Never use `manage_task` for todos** (`manage_task` is for background OS processes only).
- **Architecture Modeling**: Always render component topologies, data flows, and state machines using native **Mermaid diagrams** (`mermaid`).
- **Subagents**: Use `invoke_subagent` with `TypeName: "self"` for independent audits and `TypeName: "research"` for deep read-only codebase exploration.
- **Deterministic Guards**: Respect `hooks.json` lifecycle hooks; maintain synchronized context files before completing sessions or git commits.
