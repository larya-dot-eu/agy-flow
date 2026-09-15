---
name: flow-brainstorm
description: >-
  Phase 1 & 2 of the 10-phase engineering lifecycle: Context Priming & Superpowers Exploration.
  Classifies requests (Spike / Bounded / Architectural / Brownfield Onboarding), turns vague ideas into validated designs
  through disciplined one-by-one question dialogue with [Question X/Y] progress counters, renders native Mermaid architecture diagrams,
  and enforces the Understanding Lock & Spec Self-Review gates. Trigger with /flow-brainstorm.
risk: critical
source: unified-superpowers
---

# Flow Brainstorm (`/flow-brainstorm`)

Turn raw ideas into **clear, validated designs and specifications** through structured, collaborative dialogue **before any implementation begins**.

```text
               [/flow-brainstorm Ingestion]
                            │
              ┌─────────────▼─────────────┐
              │ Classify Request Path:    │
              │  - Spike                  │
              │  - Bounded (1-line fixes) │
              │  - Architectural (DEFAULT)│
              │  - Brownfield Onboarding  │
              └─────────────┬─────────────┘
                            │
       ┌────────────────────┼────────────────────┬─────────────────────┐
       ▼                    ▼                    ▼                     ▼
   [SPIKE]              [BOUNDED]         [ARCHITECTURAL]        [ONBOARDING]
  - 2-3 sentence probe - Context check   - Decomposition check  - 4-Stage Repo Scan
  - Human nod          - 1-2 Qs [1/X]    - Deep 1-by-1 Qs [1/X] - Discover Subsystems
  - Execute probe      - Short in-chat   - Non-functional reqs  - Generate docs/context/
  - Report findings      design          - 💡 Mandatory hook     - Build GEMINI.md map
                       - Human approval  - Understanding Lock   - Human Approval
                       - Direct TDD      - Hand-off: /flow-spec
                                           (Phase 03 Spec Gate)
```

<HARD-GATE>
1. **The 1-by-1 Question Hard Gate**: You MUST ask clarifying questions strictly ONE AT A TIME using the explicit progress prefix: `[Question 1/X]`, `[Question 2/X]`, etc.
2. **Turn-Taking Stop Gate**: After outputting a question, you MUST STOP and END YOUR TURN IMMEDIATELY. Never ask multiple questions in a single response. Never ask a question and simultaneously propose designs or solutions.
3. **No Implementation in Brainstorm**: You MUST NOT write project code, modify existing source files, or scaffold components during `/flow-brainstorm`.
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

## 2. Four Paths Classification

Before your first question, classify the request and state it clearly so the human partner can confirm or override. **Default to Architectural** whenever new features, behavior changes, or public contracts are involved.

### Path A: Spike
- **Definition**: A feasibility or discovery question (*"can we..."*, *"is it possible to..."*, *"quick probe"*).
- **Output**: An answer/recommendation, not code to keep.
- **Workflow**: Present probe plan in 2–3 sentences $\rightarrow$ get human nod $\rightarrow$ investigate cheaply $\rightarrow$ report recommendation.

### Path B: Bounded
- **Definition**: Strictly for well-scoped 1-file fixes, minor typos, or trivial maintenance on existing code.
- **Rule**: If the request adds new functionality, alters architecture, or touches multiple components, **it is NOT Bounded — upgrade to Architectural**.
- **Workflow**: Check context $\rightarrow$ ask 1–2 clarifying questions `[Question 1/X]` $\rightarrow$ present short design IN CHAT $\rightarrow$ **STOP and wait for approval** $\rightarrow$ hand off to `/flow-tdd`.

### Path C: Architectural (DEFAULT PATH)
- **Definition**: Any new feature, new subsystem, refactoring, behavior modification, or contract change.
- **Workflow**: Follow the full 5-Round dialogue process below. **MUST author a specification to `docs/specs/YYYY-MM-DD-[feature]-spec.md` using `flow-spec/resources/spec.md.template`.**

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

## 4. The Architectural Process (Step-by-Step Rounds)

### Round 1: Understand Current Context & Boundaries
- Review existing files, documentation, recent commits, and architectural patterns.
- Check `## Context Routing Map` in `GEMINI.md` before broad directory scanning.
- Output: Announce classification (Path C: Architectural) and ask `[Question 1/X]` $\rightarrow$ **STOP / End Turn**.

### Round 2: Disciplined 1-by-1 Questioning Loop
- Receive user answer $\rightarrow$ Ask next question `[Question 2/X]` $\rightarrow$ **STOP / End Turn**.
- Clarify Non-Functional Requirements (latency SLAs, scale, failure modes, security boundaries).
- Continue 1-by-1 until all clarifying questions are answered.

### Round 3: Architectural Approaches & Mermaid Modeling
- Propose **2–3 viable approaches** with explicit trade-offs and your recommended option.
- **Render Native Visuals**: Always model the architecture, component topology, or data flow using native **Mermaid diagrams** (`mermaid`).
- Output: Present the approaches and diagram $\rightarrow$ **STOP and ask the user to pick or refine an approach**.

### Round 4: The Understanding Lock (Hard Gate)
Once the approach is chosen, pause and present the Understanding Lock:
1. **Understanding Summary**: Concise bullet points (What, Why, Who, Constraints, Non-Goals).
2. **Explicit Assumptions List**.
3. Ask:
   > *"Does this accurately reflect your intent? Please confirm before I author the formal specification."*
4. **STOP and wait for explicit human confirmation.** Do NOT write the spec until confirmed.

### Round 5: Specification Gate (`/flow-spec` - Phase 03)
After the Understanding Lock is confirmed by the human partner:
1. Author the authoritative RFC 2119 specification using [`flow-spec/resources/spec.md.template`](../flow-spec/resources/spec.md.template) to:
   `docs/specs/YYYY-MM-DD-[feature]-spec.md`
2. **4-Point Spec Self-Review (Mandatory Inline Audit)**:
   - [x] **Placeholder Scan**: Zero `TBD`, `TODO`, or hand-waving.
   - [x] **Consistency**: Architecture models match API contracts exactly.
   - [x] **Scope**: Single deliverable, appropriately bounded.
   - [x] **Ambiguity**: Unambiguous, quantitative metrics (e.g. `p95 < 50ms`).
3. Present the written specification link for final review:
   > *"Spec authored and self-reviewed at `docs/specs/YYYY-MM-DD-[feature]-spec.md`. Please review and approve before we proceed to Phase 4 implementation planning (`/flow-plan`)."*
4. **STOP and wait for user approval.**

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
