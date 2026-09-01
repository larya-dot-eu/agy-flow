---
name: flow-spec
description: >-
  Phase 3 of the 10-phase engineering lifecycle: Spec Writing.
  Generates comprehensive, testable specification documents saved to docs/specs/YYYY-MM-DD-[feature]-spec.md.
  Enforces architectural rigor, precision technical writing, runnable contract schemas, invariants,
  and the 4-Point Spec Self-Review gate. Trigger with /flow-spec.
risk: critical
source: unified-flow
---

# Flow Spec (`/flow-spec`)

Phase 3: Specification Writing.

Transform validated architectural designs from [`/flow-brainstorm`](../flow-brainstorm/SKILL.md) into authoritative, unambiguous, and testable engineering specifications.

```text
  ┌─────────────────────────────────────────────────────────────┐
  │ Input: Validated Brainstorm Design & Understanding Lock     │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Load Canonical Template: templates/spec.md.template         │
  │  - Active Voice & RFC 2119 Normative Language               │
  │  - Quantitative SLAs (Zero Hand-Waving Adjectives)          │
  │  - Runnable Schema Encodings (Structs, Types, Models)       │
  │  - Exact Invariants, Error Enums & Status Codes             │
  │  - Architecture Topology & Mermaid Data Flows               │
  │  - Standardized Section Anchors (<!-- ANCHOR: ... -->)      │
  │  - 💡 Mandatory /flow-adr Hook (Formal Decisions in docs/adr│
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 4-Point Spec Self-Review (Mandatory Inline Audit)           │
  │  [x] Placeholders  [x] Consistency  [x] Scope  [x] Ambiguity│
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ User Sign-Off Gate ──► Handoff to /flow-plan (Phase 04)     │
  └─────────────────────────────────────────────────────────────┘
```

<HARD-GATE>
Do NOT begin implementation planning or coding during Phase 3. A specification MUST be written to disk at docs/specs/YYYY-MM-DD-[feature]-spec.md using templates/spec.md.template, self-reviewed against the 4-point audit, and explicitly approved by the user before proceeding to /flow-plan.
</HARD-GATE>

---

## 1. Canonical Template Usage (`templates/spec.md.template`)

When authoring a specification:
1. **Load Template**: Read [`templates/spec.md.template`](../../templates/spec.md.template) as the strict structural blueprint.
2. **Preserve Section Anchors**: Retain all inline anchor comments (`<!-- ANCHOR: ABSTRACT -->`, `<!-- ANCHOR: NORMATIVE_REQUIREMENTS -->`, etc.) to enable deterministic section mutation.
3. **Save Location**: Write to `docs/specs/YYYY-MM-DD-[feature-name]-spec.md`.

---

## 2. Precision Technical Writing Rules

Every specification produced must strictly obey these technical prose standards:

### A. Ban Weak Modal Verbs (RFC 2119 Normative Standard)
- ❌ **Banned Words**: *"should"*, *"might"*, *"could"*, *"probably"*, *"ideally"*, *"as needed"*, *"etc."*.
- ✅ **Required Terms**: **`MUST`**, **`MUST NOT`**, **`REQUIRED`**, **`EXPLICITLY REJECTS`**.

### B. Quantitative SLAs (Zero Subjective Adjectives)
- ❌ **Banned Fluff**: *"fast"*, *"performant"*, *"scalable"*, *"robust"*, *"lightweight"*, *"secure"*, *"clean"*.
- ✅ **Quantifiable Metrics**: Exact latencies, resource boundaries, throughputs, and timeouts.
  - *Latency*: *"p95 latency MUST be < 50ms; p99 < 150ms under 500 RPS."*
  - *Payload*: *"Maximum payload size is strictly capped at 2MB; larger requests are rejected with `HTTP 413`."*

### C. Concrete Runnable Schema & Type Encodings
Do not write descriptive pseudocode. Output **exact runnable type definitions** matching the target programming language:

```typescript
export interface CreateSessionRequest {
  readonly userId: string;
  readonly role: 'admin' | 'user' | 'guest';
  readonly ttlSeconds: number;
}
```

### D. Active Voice & Explicit Actors
Every requirement must state the exact subject performing the operation.
- ❌ *"Sessions are stored and notifications are sent."*
- ✅ *"The SessionManager writes the session record to Redis and publishes a `session.created` event to RabbitMQ."*

---

## 3. Mandatory ADR Hook (`/flow-adr`)

> [!IMPORTANT]
> **Permanent Architectural Decision Trigger**:
> If this specification introduces or alters major architectural choices (e.g. database/persistence engine, messaging broker, framework adoption, authentication boundary, or service decoupling), you **MUST activate [`/flow-adr`](../flow-adr/SKILL.md)** to author a formal record at `docs/adr/NNNN-[title].md` and link it in the spec.

---

## 4. 4-Point Spec Self-Review (Mandatory Inline Audit)

Before presenting the specification for user sign-off, audit the draft against these 4 rules:
1. **Placeholder Scan**: Eliminate any `TBD`, `TODO`, `later`, or unwritten sections.
2. **Prose Precision Scan**: Check for banned weak words (*"should/might/could/fast"*). Replace with normative RFC 2119 language and exact metrics.
3. **Contract Consistency**: Verify that Mermaid diagrams, function signatures, and struct definitions match verbatim.
4. **Scope Integrity**: Ensure the spec describes a single, cohesive deliverable. Decompose if multiple subsystems are present.

---

## 5. User Sign-Off Gate & Handoff to `/flow-plan`

1. Save the spec file to `docs/specs/YYYY-MM-DD-[feature]-spec.md`.
2. Present the link and brief summary to the user:
   > *"Specification authored and audited at [`docs/specs/YYYY-MM-DD-[feature]-spec.md`](docs/specs/). Please review and confirm your approval before we proceed to [`/flow-plan`](../flow-plan/SKILL.md) (Phase 4)."*
3. **Hard Gate**: Wait for explicit user confirmation before transitioning to `/flow-plan`.
