---
name: flow-adr
description: >-
  Write and maintain Architecture Decision Records (ADRs) following standard MADR, Y-Statement, and RFC formats.
  Use when documenting significant technical decisions, reviewing past architectural choices, or managing decision lifecycles in docs/adr/.
  Trigger with /flow-adr.
risk: low
source: unified-flow
---

# Flow Architecture Decision Records (`/flow-adr`)

Capture, index, and manage Architecture Decision Records (ADRs) to preserve the context, trade-offs, and rationale behind critical engineering decisions.

```text
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. Decision Ingestion: Context, Drivers & Options           │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 2. Select ADR Format & Author Record                        │
  │  - MADR Standard Format (Comprehensive)                     │
  │  - Y-Statement Format (Compact & Direct)                    │
  │  - RFC Proposal Format (Collaborative)                      │
  │  - Supersede / Deprecation Format                           │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 3. Save to docs/adr/NNNN-[title-with-dashes].md             │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 4. Update Automated Index in docs/adr/README.md             │
  └─────────────────────────────────────────────────────────────┘
```

---

## 1. When to Write an ADR

| Write an ADR | Skip ADR (Document Inline) |
| :--- | :--- |
| Database / Persistence technology choice | Minor package version upgrades |
| New framework or transport protocol adoption | Localized bug fixes |
| Distributed architecture pattern (EDA, CQRS, Sagas) | Routine refactoring / cosmetic changes |
| Auth & Security boundary architecture | Single-function implementation details |
| Deprecating or replacing a legacy system | Non-breaking configuration tweaks |

---

## 2. Directory Standard & File Naming

- **Target Directory**: `docs/adr/` at the repository root.
- **Filename Convention**: `docs/adr/NNNN-[title-with-dashes].md` (4-digit sequential zero-padded number, e.g. `0001-use-postgresql.md`).
- **Index File**: `docs/adr/README.md` (Maintained automatically as a table of contents).

---

## 3. ADR Lifecycle & Statuses

```text
Proposed ──► Accepted ──► Deprecated ──► Superseded
   │
   └──► Rejected
```

- **`Proposed`**: Under review and stakeholder discussion.
- **`Accepted`**: Formally approved; actively governs current implementation.
- **`Deprecated`**: No longer relevant due to external context changes.
- **`Superseded`**: Formally replaced by a newer ADR (e.g. `Superseded by ADR-0020`).
- **`Rejected`**: Evaluated but deliberately declined (preserved to prevent revisiting failed ideas).

---

## 4. Standard ADR Templates

### Template A: Standard MADR Format (Recommended)

```markdown
# ADR-0001: [Title of Decision]

- **Status**: Proposed | Accepted | Deprecated | Superseded | Rejected
- **Date**: YYYY-MM-DD
- **Deciders**: [Names / Roles]
- **Supersedes**: [Link to older ADR if applicable]
- **Superseded by**: [Link to newer ADR if applicable]

---

## 1. Context & Problem Statement
[2–3 paragraphs describing the business/technical problem, volume, concurrency, or infrastructure constraints].

---

## 2. Decision Drivers
* **Driver 1**: [e.g. Must support ACID transactions for billing]
* **Driver 2**: [e.g. P99 latency must remain < 50ms under 10k RPS]
* **Driver 3**: [e.g. Minimizes operational overhead of external services]

---

## 3. Considered Options

### Option 1: [Chosen Option]
- **Pros**: [Key strengths]
- **Cons**: [Known trade-offs]

### Option 2: [Alternative A]
- **Pros**: [Strengths]
- **Cons**: [Why rejected]

### Option 3: [Alternative B]
- **Pros**: [Strengths]
- **Cons**: [Why rejected]

---

## 4. Decision & Rationale
We will adopt **[Chosen Option]** because [explicit technical reasoning resolving the decision drivers].

---

## 5. Consequences & Trade-Offs

### Positive Consequences
- [Positive outcome 1]
- [Positive outcome 2]

### Negative Consequences & Operational Overhead
- [Trade-off or learning curve]
- [Operational mitigation required]

---

## 6. Implementation Notes & Invariants
- [Specific library, configuration key, or migration step].

---

## 7. Related Decisions & References
- ADR-0002: [Title]
```

### Template B: Y-Statement Format (Compact)

```markdown
# ADR-0002: [Title]

- **Status**: Accepted
- **Date**: YYYY-MM-DD

In the context of **[current technical challenge or architecture requirement]**,  
facing **[specific constraints or operational bottlenecks]**,  
we decided for **[chosen technology/pattern]**  
and against **[rejected alternatives]**,  
to achieve **[primary business and technical benefits]**,  
accepting that **[known operational cost, trade-off, or mitigation]**.
```

---

## 5. ADR Index Management (`docs/adr/README.md`)

Whenever a new ADR is created or an existing ADR's status changes, update `docs/adr/README.md`:

```markdown
# Architecture Decision Records (ADRs)

This directory records all significant architectural and technical decisions made for this repository.

## Decision Index

| ADR | Title | Status | Date |
| :--- | :--- | :--- | :--- |
| [0001](0001-use-postgresql.md) | Use PostgreSQL as Primary Persistence Engine | Accepted | 2026-09-01 |
| [0002](0002-caching-strategy.md) | Redis Cache-Aside Strategy | Accepted | 2026-09-01 |
| [0003](0003-event-broker.md) | Kafka for Async Domain Events | Proposed | 2026-09-01 |
```
