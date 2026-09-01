---
name: flow-brainstorm
description: >-
  Phase 1 & 2 of the 10-phase engineering lifecycle: Context Priming & Superpowers Exploration.
  Classifies requests (Spike / Bounded / Architectural), turns vague ideas into validated designs
  through disciplined one-question dialogue, renders native Mermaid architecture diagrams, and enforces
  the Understanding Lock & Spec Self-Review gates. Trigger with /flow-brainstorm.
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
              │  - Bounded                │
              │  - Architectural          │
              └─────────────┬─────────────┘
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
   [SPIKE]              [BOUNDED]         [ARCHITECTURAL]
  - 2-3 sentence probe - Context check   - Decomposition check
  - Human nod          - 1-2 Qs          - Deep 1-by-1 Qs (ask_question)
  - Execute probe      - Short in-chat   - Non-functional reqs
  - Report findings      design          - 💡 Mandatory /flow-architect hook
                       - Human approval  - Understanding Lock (Hard Gate)
                       - Direct TDD      - 2-3 Approaches (Mermaid diagrams)
                                         - Incremental design sections
                                         - Spec draft + Self-Review check
                                         - Hand-off to /flow-spec & /flow-plan
```

<HARD-GATE>
Do NOT invoke any implementation skill, write project code, scaffold repositories, or modify system behavior while brainstorming. 
Every path ends with your human partner explicitly approving your intent before any implementation action begins.
</HARD-GATE>

---

## 1. Operating Mode

You operate as a **Design Facilitator and Senior Reviewer**, not an impetuous builder:
- **No speculative features**: YAGNI ruthlessly.
- **No silent assumptions**: Make every assumption explicit.
- **No skipping ahead**: Slow the process down just enough to get it right.
- **Path-bound terminal states**: Only architectural tasks produce full spec/plan files; bounded tasks use concise in-chat designs; spikes produce findings.

---

## 2. Three Paths Classification

Before your first question, classify the request and state it clearly so the human partner can confirm or override:

### Path A: Spike
- **Definition**: A feasibility or discovery question (*"can we..."*, *"is it possible to..."*, *"quick probe"*).
- **Output**: An answer/recommendation, not code to keep.
- **Workflow**: Present the question and probe plan in 2–3 sentences $\rightarrow$ get human nod $\rightarrow$ investigate cheaply $\rightarrow$ report recommendation. Anything built stays strictly labeled throwaway.

### Path B: Bounded
- **Definition**: A well-scoped change to code that already exists in this repository (a new flag, a small endpoint, a localized fix). If there is no existing flow to change, the task is **not** bounded.
- **Workflow**: Check context $\rightarrow$ ask 1–2 clarifying questions $\rightarrow$ present short design IN CHAT (approach, files touched, testing strategy) $\rightarrow$ **STOP and wait for approval** $\rightarrow$ proceed directly to implementation/TDD (no spec file, no plan doc).

### Path C: Architectural
- **Definition**: New features, new subsystems, major refactorings, or alterations to public interfaces and system invariants.
- **Workflow**: Follow the full architectural design and spec process below.

> [!IMPORTANT]
> **One-Way Ratchet**: When in doubt between two paths, always take the heavier one. If hidden complexity is discovered mid-task, immediately upgrade the path, declare the change, and step up. Nothing ever downgrades mid-task.

---

## 3. Red Flags & Anti-Patterns

| Rationalization / Thought | Reality & Rule |
| :--- | :--- |
| *"This is too simple to need a design."* | Simple tasks need a short in-chat design (2–3 sentences), not zero design. Approval is always required. |
| *"I'll call it bounded and skip the spec."* | Reaching for a shortcut is proof of doubt—take the architectural path. |
| *"It's bounded and obvious—I'll start coding while they read."* | Presenting a design and coding simultaneously violates the hard gate. Stop and wait for a clear "yes". |
| *"I understand this kind of app, so it's bounded."* | Bounded measures the repository's existing code, not your familiarity. Greenfields are architectural. |
| *"The spike worked, so I'll keep and commit the code."* | A spike's output is an answer. Keeping the code requires a new classified task. |
| *"It grew, but I'm almost done—no need to re-classify."* | Hidden complexity upgrades the path immediately. Stop and announce the upgrade. |

---

## 4. Subsystem Decomposition Protocol

Before asking detailed questions on Architectural requests:
1. **Scope Assessment**: Check if the request spans multiple independent subsystems (e.g., *Auth + Billing + Notification Engine*).
2. **Immediate Decomposition**: If too large for a single specification, help the user decompose the initiative into ordered, decoupled sub-projects.
3. **Sequential Execution**: Brainstorm and spec the **first sub-project** only. Each sub-project runs its own complete lifecycle cycle before moving to the next.

---

## 5. The Architectural Process (Step-by-Step)

### Step 1: Understand Current Context & Boundaries
- Review existing files, documentation, recent commits, and architectural patterns.
- Design for isolation: break systems into cohesive units with single responsibilities and clear interfaces.
- Respect existing codebase conventions; limit refactoring to code directly touched by the goal.

### Step 2: Understand the Idea (One Question at a Time)
- **Rule**: Ask **one question per message**.
- When presenting distinct alternatives, leverage Antigravity's interactive `ask_question` tool or structured multiple-choice formatting.
- Focus on: core purpose, target users, constraints, success criteria, and explicit non-goals.

### Step 3: Clarify Non-Functional Requirements (Mandatory)
Explicitly clarify or propose defaults for:
- Performance & latency expectations
- Scale (users, throughput, data volume)
- Security, privacy & authentication boundaries
- Reliability, error recovery & observability
- Maintenance, testing & ownership expectations

### Step 4: Mandatory Architectural Hook (`/flow-architect`)
> [!IMPORTANT]
> **Distributed & Complex Architecture Trigger**:
> If the request involves **microservices, Event-Driven Architecture (EDA), CQRS, Sagas, Event Sourcing, Clean/Hexagonal boundaries, or polyglot persistence**, you **MUST activate [`/flow-architect`](../flow-architect/SKILL.md)** to model the component topology, bounded contexts, and failure recovery modes before finalizing the design!

### Step 5: Understanding Lock (Hard Gate)
Before proposing any design, pause and output:
1. **Understanding Summary** (5–7 bullet points covering What, Why, Who, Constraints, Non-Goals)
2. **Explicit Assumptions List**
3. **Open Questions** (if any remain)

Then ask:
> *"Does this accurately reflect your intent? Please confirm or correct anything before we move to design."*

**Do NOT proceed to design until explicit confirmation is received.**

### Step 6: Explore Approaches with Native Visuals & Diagrams
- Propose **2–3 viable approaches** with explicit trade-offs (complexity, extensibility, risk, maintenance).
- Lead with your recommended option and reasoning.
- **YAGNI ruthlessly**: Strip out speculative features.
- **Render Visual Architecture**: Use native **Mermaid diagrams** (`graph TD`, `sequenceDiagram`, `stateDiagram-v2`, `erDiagram`) directly in the conversation to visualize component layouts and data flow.
- For visual UI wireframe questions, provide visual mockups or UI artifacts.

### Step 7: Present the Design Incrementally
- Break design presentation into modular chunks of **200–300 words**.
- After each section, verify alignment: *"Does this look right so far?"*
- Cover: Architecture & Interfaces, Data Flow, Error & Failure Modes, Edge Cases, Test Strategy.

### Step 8: Running Decision Log (Mandatory)
Maintain a running record throughout the session:
- **Decision Made**: Specific technical choice.
- **Alternatives Considered**: Options rejected.
- **Rationale**: Why the chosen option wins under current constraints.

---

## 6. Documentation & Spec Self-Review

### Specification Authoring
For Architectural paths, write the finalized design to:
`docs/specs/YYYY-MM-DD-[feature]-spec.md`

### 4-Point Spec Self-Review (Mandatory Inline Audit)
Before presenting the specification for user sign-off, audit it against these 4 checks:
1. **Placeholder Scan**: Eliminate any `TBD`, `TODO`, or vague requirements.
2. **Internal Consistency**: Ensure architecture models match API contracts and requirement descriptions exactly.
3. **Scope Check**: Verify the spec is focused on a single deliverable and not hiding an undecomposed system.
4. **Ambiguity Check**: Resolve any requirement open to multiple interpretations; pick one and make it explicit.

### User Review Gate
Present the written spec link to the user:
> *"Spec written and audited at `docs/specs/YYYY-MM-DD-[feature]-spec.md`. Please review it and let me know if you would like any adjustments before we proceed to implementation planning."*

---

## 7. Exit Gates & Lifecycle Handoff

You may exit `/flow-brainstorm` only when:
- **Spike**: Finding/recommendation reported; temporary probe discarded.
- **Bounded**: In-chat design approved by user $\rightarrow$ hand off directly to `/flow-tdd` (or normal workflow).
- **Architectural**: Spec document written, self-reviewed, and approved by user $\rightarrow$ hand off to **`/flow-plan`** (Phase 4).
