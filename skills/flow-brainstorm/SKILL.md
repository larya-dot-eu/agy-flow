---
name: flow-brainstorm
description: >-
  Phase 1 & 2 of the 10-phase engineering lifecycle: Context Priming & Socratic Exploration.
  Executes disciplined 1-by-1 question dialogue with [Question X/Y] progress counters, renders native Mermaid architecture diagrams,
  prevents premature low-ceremony assumptions, and enforces the Understanding Lock & Phase 3 Specification gates. Trigger with /flow-brainstorm.
risk: critical
source: unified-superpowers
---

# Flow Brainstorm (`/flow-brainstorm`)

Turn raw ideas into **clear, validated designs and specifications** through structured, collaborative dialogue **before any implementation begins**.

```text
               [/flow-brainstorm Ingestion]
                            │
               ┌────────────▼────────────┐
               │ Context Priming & Scan  │
               │ (Check GEMINI.md Map)   │
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │ Disciplined 1-by-1      │◄─── [Question 1/X]
               │ Questioning Loop        │     [Question 2/X] (End turn after each)
               │ (No Upfront Shortcuts)  │     [Question 3/X]
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │ Approaches & Mermaid    │
               │ Architecture Modeling   │
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │ Understanding Lock Gate │ ──► Scope Confirmed with User
               └────────────┬────────────┘     (Bounded vs Architectural)
                            │
        ┌───────────────────┴───────────────────┐
        ▼                                       ▼
  [Path B: BOUNDED]                       [Path C: ARCHITECTURAL (DEFAULT)]
  - Pure 1-file typo / minor fix          - Full RFC 2119 Spec
  - Approved by user in Lock              - Author to docs/specs/
  - Proceed directly to /flow-tdd         - 4-Point Spec Self-Review
                                          - Hand-off: /flow-spec ──► /flow-plan
```

<HARD-GATE>
1. **Zero Upfront Classification**: You MUST NOT unilaterally classify a task as "Bounded" or assume low ceremony at ingestion. Every engineering task MUST enter the 1-by-1 Questioning Loop first to discover true complexity.
2. **The 1-by-1 Question Hard Gate**: You MUST ask clarifying questions strictly ONE AT A TIME using the explicit progress prefix: `### [Question 1/X]: ...`.
3. **Turn-Taking Stop Gate**: After outputting a single question, you MUST STOP and END YOUR TURN IMMEDIATELY. Never bunch multiple questions in one response. Never ask a question and simultaneously propose designs, specs, or solutions.
4. **No Implementation in Brainstorm**: You MUST NOT write project code, modify existing source files, or scaffold components during `/flow-brainstorm`.
5. **Specification Gate Enforcement**: Architectural tasks (DEFAULT) MUST author a formal specification to `docs/specs/YYYY-MM-DD-[feature]-spec.md` and obtain human approval before Phase 4 (`/flow-plan`).
</HARD-GATE>

---

## 1. Operating Mode & Startup Self-Healing

You operate as a **Design Facilitator and Senior Reviewer**, not an impetuous builder:
- **No speculative features**: YAGNI ruthlessly.
- **No silent assumptions**: Make every assumption explicit.
- **No skipping ahead**: Slow the process down just enough to get it right.
- **Startup Self-Healing Staleness Detection**:
  When opening a mapped context file (`docs/context/[module].md`), compare the `Last Verified` timestamp against the latest git commit affecting the mapped source directory (`git log -1 --format=%ct -- <mapped-path>`). If code is newer than the context doc, inform the user and execute a fast delta-sync of the interface table before planning.

---

## 2. Special Paths

While standard engineering tasks follow the full 5-Round lifecycle below, two specialized scenarios use dedicated protocols:

### Path A: Spike (Feasibility Probe)
- **Definition**: A pure discovery probe (*"is it possible to..."*, *"quick feasibility check"*).
- **Workflow**: Present probe plan in 2–3 sentences $\rightarrow$ get human nod $\rightarrow$ investigate cheaply $\rightarrow$ report recommendation $\rightarrow$ do not retain probe code.

### Path D: Brownfield Onboarding Protocol
- **Definition**: Existing or legacy repository without prior documentation or context routing map.
- **Workflow**: Execute the 4-Stage Onboarding Recipe:
  1. **Stage 1 (Topology Probe)**: Read manifest files (`package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`), discover scripts, and inspect entry points without modifying code.
  2. **Stage 2 (Subsystem Boundaries)**: Identify core modules, data stores, background jobs, external services, and auth/billing integrations.
  3. **Stage 3 (Context Generation)**: Author structured `docs/context/[subsystem].md` files for discovered core modules using `resources/context-module.md.template`.
  4. **Stage 4 (Router Registration)**: Populate `GEMINI.md` with conventions, standard dev/test commands, and the `## Context Routing Map` using `resources/GEMINI.md.template`.

---

## 3. The 1-by-1 Questioning Protocol (`[Question X/Y]`)

When refining requirements during Round 1 and Round 2:

1. **Estimate Question Scope**: Determine the 2–4 critical dimensions that must be clarified (e.g. Total = 3).
2. **Strict Counter Prefix**: Every question message MUST start with the explicit counter:
   - `### [Question 1/3]: Core Purpose & User Context`
   - `### [Question 2/3]: Constraints & Error Handling`
   - `### [Question 3/3]: Non-Functional Requirements & Performance`
3. **Interactive & Multiple-Choice**: Prefer multiple-choice options or leverage Antigravity's interactive `ask_question` tool.
4. **Immediate Turn-End**: Once the single question is presented, **STOP CALLING TOOLS AND END YOUR TURN**. Wait for the human partner's answer before asking the next question or moving to design.

---

## 4. The 5-Round Lifecycle

### Round 1: Context Priming & First Question
- Review relevant mapped context docs and existing interfaces.
- Formulate question sequence and ask `### [Question 1/X]: ...` $\rightarrow$ **STOP / End Turn**.

### Round 2: Disciplined 1-by-1 Questioning Loop
- Receive user response $\rightarrow$ Ask next question `### [Question 2/X]: ...` $\rightarrow$ **STOP / End Turn**.
- Clarify Non-Functional Requirements (latency SLAs, scale, failure modes, security boundaries).
- Continue 1-by-1 until all critical questions are resolved.

### Round 3: Architectural Approaches & Mermaid Modeling
- Propose **2–3 viable approaches** with explicit trade-offs and your recommended option.
- **Render Native Visuals**: Always model the architecture, component topology, or data flow using native **Mermaid diagrams** (`mermaid`).
- Output: Present the approaches and diagram $\rightarrow$ **STOP and ask the user to pick or refine an approach**.

### Round 4: The Understanding Lock & Scope Confirmation (Hard Gate)
Once the approach is selected, formulate the Understanding Lock:
1. **Understanding Summary**: Concise bullet points (What, Why, Who, Constraints, Non-Goals).
2. **Explicit Assumptions List**.
3. **Scope / Ceremony Confirmation**:
   - **Path C: Architectural (DEFAULT)**: Standard for all features, contracts, and refactoring $\rightarrow$ proceeds to Phase 3 `/flow-spec`.
   - **Path B: Bounded**: Permitted *only* if the dialogue proved the task is a trivial 1-file typo/maintenance change with zero architectural impact and the user explicitly agrees.
4. Ask:
   > *"Does this accurately reflect your intent? Please confirm before we proceed to Phase 3 specification writing (`/flow-spec`)."*
5. **STOP and wait for human confirmation.** Do NOT write specs or code until confirmed.

### Round 5: Handoff to Specification Gate (`/flow-spec` - Phase 03)
After the Understanding Lock is confirmed by the human partner:
1. For Architectural tasks (DEFAULT): Transition to **[`/flow-spec`](../flow-spec/SKILL.md)** (Phase 3). `/flow-spec` reads the canonical template from its skill resources (`flow-spec/resources/spec.md.template`), authors `docs/specs/YYYY-MM-DD-[feature]-spec.md`, executes the 4-Point Spec Self-Review, and requests user sign-off.
2. For Bounded tasks: Hand off directly to **[`/flow-tdd`](../flow-tdd/SKILL.md)** (Phase 6).

---

## 5. Exit Gates & Sequential Phase Handoff

The 10-phase engineering lifecycle strictly requires passing each gate before the next unlocks:
1. **Brainstorming Gate (Phase 01-02)**: Complete 1-by-1 dialogue $\rightarrow$ Lock understanding.
2. **Specification Gate (Phase 03 `/flow-spec`)**: Write spec $\rightarrow$ Self-review $\rightarrow$ **Get user sign-off**.
3. **Planning Gate (Phase 04 `/flow-plan`)**: Author bite-sized implementation plan with exact code blocks.
4. **Adversarial Review Gate (Phase 05 `/flow-review`)**: Dispatch subagent auditor to verify Spec + Plan.
5. **Implementation Gate (Phase 06-07 `/flow-tdd`)**: Isolated branch TDD (Red $\rightarrow$ Green $\rightarrow$ Refactor).
6. **Release Gate (Phase 08-10 `/flow-release`)**: Verification, living context sync, safe merge.

<EXTREMELY-IMPORTANT>
NEVER write project implementation code, edit production source files, or run TDD cycles inside `/flow-brainstorm`. 
Every phase must be reviewed and approved sequentially.
</EXTREMELY-IMPORTANT>
