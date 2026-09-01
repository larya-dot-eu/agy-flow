---
name: flow-master
description: >-
  Master orchestrator for the 10-phase engineering lifecycle. Enforces pre-flight skill invocation,
  Antigravity CLI tool mappings, Context-First Routing Law, Canonical Templates, Full vs Quick Tier assessment,
  Blast Radius estimation, and routes tasks through brainstorm, spec, plan, review, TDD, and release phases. Trigger with /flow.
risk: critical
source: unified-flow
---

# Flow Master Orchestrator (`/flow`)

The master orchestrator governing the complete 10-phase engineering lifecycle, canonical templates suite, zero-discovery context routing, and standalone architectural tooling across all repositories, workspaces, and CLI sessions.

```text
                                [Task Ingested]
                                       │
                         ┌─────────────▼─────────────┐
                         │ Mandatory Pre-Flight Gate │ ──► Check /flow-* applicability
                         └─────────────┬─────────────┘
                                       │
     ┌──────────────────┬──────────────┴───────────────────┬─────────────────────┐
     ▼                  ▼                                  ▼                     ▼
 [SPIKE]            [BOUNDED]                       [ARCHITECTURAL]        [ONBOARDING]
    │                  │                                   │                     │
    ▼                  ▼                                   ▼                     ▼
 /flow-brainstorm   /flow-brainstorm         [Tier & Blast Radius]        /flow-brainstorm
 (Cheap Probe)      (In-chat Design)                       │              (4-Stage Scan)
                                                           ▼                     │
                                                     Phase 01-02:                ▼
                                                    /flow-brainstorm       [templates/context-module
                                                     (Context/Lock)         & templates/GEMINI]
                                                           │
                                                           ▼
                                                       Phase 03:
                                                      /flow-spec
                                              (templates/spec.md.template)
                                                           │
                                                           ▼
                                                       Phase 04:
                                                      /flow-plan
                                              (templates/plan.md.template)
                                                           │
                                                           ▼
                                                       Phase 05:
                                                      /flow-review
                                                   (Adversarial Audit)
                                                           │
                                                           ▼
                                                      Phase 06-07:
                                                       /flow-tdd
                                                  (Red-Green-Refactor)
                                                           │
                                                           ▼
                                                      Phase 08-10:
                                                      /flow-release
                                             (Verify, Context Sync, Release)
```

<EXTREMELY-IMPORTANT>
If a task involves creative, constructive, architectural, or modification work, invoke the appropriate /flow skill BEFORE any response or codebase edit. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

---

## 1. Canonical Template Master Registry (`templates/`)

All lifecycle skills must load, follow, and preserve the section anchors in `templates/`:

| Template File | Associated Skill / Phase | Requirement Level | Purpose & When to Use | How to Use |
| :--- | :--- | :--- | :--- | :--- |
| **`templates/spec.md.template`** | `/flow-spec` (Phase 3)<br>`/flow-brainstorm` (Path C) | **Mandatory** for Architectural tasks | **Why**: Guarantees RFC 2119 rigor, quantitative SLAs, and runnable type schemas.<br>**When**: Writing technical specifications before planning. | Read template $\rightarrow$ populate sections preserving anchors $\rightarrow$ write to `docs/specs/YYYY-MM-DD-[feature]-spec.md`. |
| **`templates/plan.md.template`** | `/flow-plan` (Phase 4) | **Mandatory** for Plan authoring | **Why**: Enforces 5 Adversarial Questions, task right-sizing, explicit `Consumes`/`Produces` interface signatures, and zero placeholders.<br>**When**: Authoring test-first implementation plan. | Read template $\rightarrow$ generate bite-sized 2–5 min tasks $\rightarrow$ write to `docs/plans/YYYY-MM-DD-[feature]-plan.md`. |
| **`templates/context-module.md.template`** | `/flow-brainstorm` (Path D)<br>`/flow-release` (Phase 9)<br>`/flow-architect` | **Mandatory** for Mapped Subsystems | **Why**: Eliminates 20%–30% session token waste; stores living contracts, APIs, dependencies, and state invariants.<br>**When**: During brownfield onboarding or when a subsystem is created/updated. | Read template $\rightarrow$ document module contracts $\rightarrow$ write to `docs/context/[module].md`. |
| **`templates/GEMINI.md.template`** | `/flow-brainstorm` (Path D)<br>`/flow` (Master) | **Mandatory** for Project Bootstrap | **Why**: Establishes tech stack, frequent commands, directives, and the `Context Routing Map`.<br>**When**: During initial repository onboarding or bootstrap. | Read template $\rightarrow$ customize commands & map $\rightarrow$ write to `./GEMINI.md`. |

---

## 2. Antigravity CLI Tool Mapping & Runtime Execution

| Workflow Action | Antigravity CLI Tool | Execution Rule |
| :--- | :--- | :--- |
| **Context Routing** | `GEMINI.md` Context Map | Check `## Context Routing Map` before recursive searches. |
| **Task Tracking & Checklists** | **Task Artifacts & Plan Docs** | Maintain `- [ ]` / `- [x]` checklists in conversation, plan docs (`docs/plans/`), or markdown artifacts. ⚠️ **Do NOT use `manage_task` for todos** (`manage_task` is for background OS processes only). |
| **Subagent Dispatch** | `invoke_subagent` | Use `TypeName: "self"` for full-capability subagents or `TypeName: "research"` for read-only codebase/web exploration. |
| **Process Control** | `run_command` & `manage_task` | Use `run_command` with `WaitMsBeforeAsync` for background processes; use `manage_task` (`list`, `kill`, `status`, `send_input`) for process management. |
| **Interactive Selection** | `ask_question` | Use `ask_question` to present structured single/multi-select modals to the user for critical decisions. |
| **Visual Architecture** | Native Mermaid Diagrams | Render system architecture, sequence flows, ERDs, and state diagrams using fenced ````mermaid```` blocks directly in the conversation. |
| **File Operations** | `view_file` / `replace_file_content` / `run_command` | Inspect files with line ranges; perform atomic edits; maintain documentation integrity. |

---

## 3. Pre-Flight Skill Invocation Rules

Before taking any code modification action or proposing unvetted solutions:
1. **Identify the Task Nature**:
   - New feature / Architecture / Refactor $\rightarrow$ `/flow` (or `/flow-brainstorm`)
   - Specification authoring $\rightarrow$ `/flow-spec`
   - Implementation plan authoring $\rightarrow$ `/flow-plan`
   - Adversarial review $\rightarrow$ `/flow-review`
   - TDD implementation $\rightarrow$ `/flow-tdd`
   - Post-implementation & Release $\rightarrow$ `/flow-release`
   - Distributed architecture $\rightarrow$ `/flow-architect`
   - Architectural decisions $\rightarrow$ `/flow-adr`
   - Authoring/testing skills $\rightarrow$ `/flow-skill-writer`
   - In-chat version updates $\rightarrow$ `/flow-version-update`
2. **Announce Skill Activation**: Explicitly state: `"Activating /flow-[phase] to [purpose]..."`
3. **Follow the Active Phase Protocol**: Enforce the phase's input prerequisites, process steps, and exit gates.
