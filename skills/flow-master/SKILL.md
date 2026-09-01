---
name: flow-master
description: >-
  Master orchestrator for the 10-phase engineering lifecycle. Enforces pre-flight skill invocation,
  Antigravity CLI tool mappings, Full vs Quick Tier assessment, Blast Radius estimation, and routes tasks
  through brainstorm, spec, plan, review, TDD, and release phases. Trigger with /flow.
risk: critical
source: unified-flow
---

# Flow Master Orchestrator (`/flow`)

The master orchestrator governing the complete 10-phase engineering lifecycle and standalone architectural tooling across all repositories, workspaces, and CLI sessions.

```text
                                [Task Ingested]
                                       │
                         ┌─────────────▼─────────────┐
                         │ Mandatory Pre-Flight Gate │ ──► Check /flow-* applicability
                         └─────────────┬─────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
                [SPIKE]            [BOUNDED]        [ARCHITECTURAL]
                   │                  │                   │
                   ▼                  ▼                   ▼
            /flow-brainstorm   /flow-brainstorm   [Tier & Blast Radius Assessment]
            (Cheap Probe)      (In-chat Design)           │
                                      │           ┌───────┴───────┐
                                      │           ▼               ▼
                                      │      Phase 01-02:     Phase 03:
                                      │    /flow-brainstorm  /flow-spec
                                      │    (Context/Lock)   (docs/specs/)
                                      │           │               │
                                      │           ▼               ▼
                                      │       Phase 04:       Phase 05:
                                      │      /flow-plan      /flow-review
                                      │     (docs/plans/)   (Adversarial Audit)
                                      │           │               │
                                      └───────────┼───────────────┘
                                                  │
                                                  ▼
                                             Phase 06-07:
                                              /flow-tdd
                                         (Red-Green-Refactor)
                                                  │
                                                  ▼
                                             Phase 08-10:
                                             /flow-release
                                    (Verify, Living Docs, Release)
```

<EXTREMELY-IMPORTANT>
If a task involves creative, constructive, architectural, or modification work, invoke the appropriate /flow skill BEFORE any response or codebase edit. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

---

## 1. Antigravity CLI Tool Mapping & Runtime Execution

When executing workflow actions, resolve them strictly to the native Antigravity CLI tools below:

| Workflow Action | Antigravity CLI Tool | Execution Rule |
| :--- | :--- | :--- |
| **Task Tracking & Checklists** | **Task Artifacts & Plan Docs** | Maintain `- [ ]` / `- [x]` checklists in conversation, plan docs (`docs/plans/`), or markdown artifacts. ⚠️ **Do NOT use `manage_task` for todos** (`manage_task` is for background OS processes only). |
| **Subagent Dispatch** | `invoke_subagent` | Use `TypeName: "self"` for full-capability subagents or `TypeName: "research"` for read-only codebase/web exploration. |
| **Process Control** | `run_command` & `manage_task` | Use `run_command` with `WaitMsBeforeAsync` for background processes; use `manage_task` (`list`, `kill`, `status`, `send_input`) for process management. |
| **Interactive Selection** | `ask_question` | Use `ask_question` to present structured single/multi-select modals to the user for critical decisions. |
| **Visual Architecture** | Native Mermaid Diagrams | Render system architecture, sequence flows, ERDs, and state diagrams using fenced ````mermaid```` blocks directly in the conversation. |
| **UI Wireframes & Mockups** | `generate_image` / Artifacts | Generate visual UI mockups or structured UI markdown artifacts. |
| **File Operations** | `view_file` / `replace_file_content` / `run_command` | Inspect files with line ranges; perform atomic edits; maintain documentation integrity. |

---

## 2. Pre-Flight Skill Invocation Rules

Before taking any code modification action or proposing unvetted solutions:
1. **Identify the Task Nature**: New feature, bug fix, refactor, architecture review, ADR, or release.
2. **Announce Skill Activation**: Explicitly state: `"Activating /flow-[phase] to [purpose]..."`
3. **Follow the Active Phase Protocol**: Enforce the phase's input prerequisites, process steps, and exit gates.

### Rationalization Red Flags

| Rationalization Thought | Reality & Rule |
| :--- | :--- |
| *"This is just a simple question/fix."* | Simple fixes still require bounded path verification. Check skills first. |
| *"Let me explore the codebase and write code first."* | Skills define HOW to explore and design. Invoke before writing code. |
| *"I can check files quickly without a skill."* | Undisciplined exploration causes context drift. Follow structured phase gates. |
| *"The skill is overkill for this repo."* | Small changes escalate into breaking bugs. Use the appropriate tier path. |

---

## 3. Tier Assessment & Blast Radius Evaluation

For Architectural paths, evaluate tier and blast radius during initiation:

### Tier Classification
- **Full Tier**: Multi-module modifications, public API revisions, schema changes, state/persistence changes, new subsystems, high-risk security surfaces.
- **Quick Tier**: Localized bug fixes, non-breaking configuration updates, self-contained documentation improvements, single-function patches.

### Blast Radius Matrix
- **Level 1 (Isolated)**: Contained strictly within a single internal file/module; zero external consumers.
- **Level 2 (Package-Internal)**: Touches multiple files within a single package; internal interface adjustments.
- **Level 3 (Cross-Module)**: Modifies public APIs, shared services, data models, or cross-cutting configuration.
- **Level 4 (System-Critical)**: Touches core authentication, data persistence, network protocols, or release pipelines.

---

## 4. Phase Execution & Global Skill Registry

### A. The 10-Phase Lifecycle State Machine
| Phase | Identifier | Command | Primary Input | Primary Output / Exit Gate |
| :--- | :--- | :--- | :--- | :--- |
| **01 & 02** | Brainstorm & Superpowers | `/flow-brainstorm` | User requirements / Raw intent | **Understanding Lock** & 3 Core Questions validated |
| **03** | Spec Writing | `/flow-spec` | Validated brainstorm design | `docs/specs/YYYY-MM-DD-[feature]-spec.md` + 4-point self-review |
| **04** | Plan Writing | `/flow-plan` | Validated spec file | `docs/plans/YYYY-MM-DD-[feature]-plan.md` + 5 Adversarial Questions |
| **05** | Adversarial Review | `/flow-review` | Spec + Plan files | Approval Gate or Loop-Back Routing |
| **06 & 07** | TDD & Implementation | `/flow-tdd` | Approved plan tasks | Isolated branch + Verified Red-Green-Refactor cycles |
| **08, 09 & 10** | Release & Living Docs | `/flow-release` | Verified implementation | Full suite pass + Living docs sync + Safe release checklist |

### B. On-Demand Architectural & Meta Tooling
| Utility | Command | Primary Purpose | Deliverable |
| :--- | :--- | :--- | :--- |
| **Architectural Review** | `/flow-architect` | Distributed systems, Clean/Hexagonal patterns, DDD, Sagas, CQRS | Architectural Scorecard & Mermaid Models |
| **Decision Records (ADR)** | `/flow-adr` | Capture, index, and supersede architecture decisions | `docs/adr/NNNN-[title].md` & `docs/adr/README.md` |
| **Skill Author & Test** | `/flow-skill-writer` | Author and pressure-test new skills with subagents | `~/.gemini/config/skills/<skill>/SKILL.md` |

---

## 5. Master Session State Tracking

When orchestrating a full multi-phase lifecycle, maintain the current lifecycle state:

```markdown
### Lifecycle State
- **Active Feature**: [Feature Name]
- **Current Phase**: Phase [X] (`/flow-[name]`)
- **Path / Tier**: [Spike | Bounded | Architectural (Full / Quick Tier)]
- **Blast Radius**: [Level 1 - 4]
- **Active Branch**: `feature/YYYY-MM-DD-[feature]`
- **Spec Artifact**: `docs/specs/YYYY-MM-DD-[feature]-spec.md` (Status: Draft | Approved)
- **Plan Artifact**: `docs/plans/YYYY-MM-DD-[feature]-plan.md` (Status: Draft | Approved)
- **Next Transition**: Phase [Y] (`/flow-[next]`)
```

---

## 6. Exit Gate & Lifecycle Completion

A lifecycle run is complete only when:
1. All planned tasks have verified test coverage (Red-Green-Refactor verified).
2. All regression and integration test suites pass.
3. Living documentation (`README.md`, ADRs, architecture guides) is synchronized.
4. Clean git history is prepared and verified against release gates.
