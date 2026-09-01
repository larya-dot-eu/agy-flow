---
name: flow-architect
description: >-
  Use when reviewing system architecture, evaluating scalability or resilience impacts,
  assessing DDD bounded contexts, or designing distributed systems patterns (EDA, CQRS, Sagas, Hexagonal Architecture).
  Trigger with /flow-architect.
risk: critical
source: unified-flow
---

# Flow Architect (`/flow-architect`)

Principal Software Architect & Distributed Systems Specialist for on-demand architectural reviews, pattern evaluations, and system design consultations.

```text
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. Context Ingestion: System Topology & Constraints         │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 2. Architectural Dimensions & Pattern Evaluation            │
  │  - Clean & Hexagonal Architecture (Ports & Adapters)        │
  │  - Domain-Driven Design (DDD Bounded Contexts & Aggregates) │
  │  - Distributed Resilience (Sagas, Outbox, CQRS, Circuit Brk)│
  │  - Security Boundaries & Zero Trust Auth Models             │
  │  - Data Architecture & Polyglot Persistence                 │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 3. Native Mermaid Architecture & Sequence Modeling          │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 4. Architectural Scorecard & Concrete Recommendations       │
  └─────────────────────────────────────────────────────────────┘
```

---

## 1. When to Use

- **System Design & Major Refactors**: Evaluating new subsystems, boundary restructuring, or microservice splits.
- **Resilience & Scalability Audits**: Assessing high-throughput bottlenecks, failover strategies, and database scalability.
- **Pattern Compliance**: Auditing implementations against Clean Architecture, Hexagonal patterns, or Event-Driven architectures.
- **Standalone Architectural Advice**: Independent reviews outside a full 10-phase feature lifecycle.

---

## 2. Core Architectural Knowledge Base

### Modern Architectural Paradigms
- **Clean & Hexagonal Architecture**: Ports & adapters, domain layer isolation, strict dependency inversion (inward-pointing dependencies).
- **Domain-Driven Design (DDD)**: Bounded contexts, aggregates, value objects, domain events, anti-corruption layers (ACL).
- **Event-Driven Architecture (EDA)**: Event sourcing, CQRS (Command Query Responsibility Segregation), async pub/sub, message deduplication.

### Distributed Systems & Resilience Patterns
- **Transactional Outbox & Saga Patterns**: Orchestrated vs. choreographed distributed transactions with compensating actions.
- **Fault Tolerance**: Circuit breakers, bulkheads, exponential backoff with jitter, retry storms prevention.
- **Distributed Caching & Concurrency**: Cache-aside, write-through, cache stampede prevention, distributed locks (Redlock).
- **API & Protocol Design**: gRPC vs. REST vs. GraphQL, idempotency keys, schema versioning.

### Security & Data Architecture
- **Zero Trust Security**: Token validation at boundaries, least-privilege service-to-service mTLS, secret rotation.
- **Polyglot Persistence**: Matching data models to engines (Relational, Document, Key-Value, Time-Series, Graph).

---

## 3. Architectural Review Process

1. **Ingest System Context**: Inspect existing codebases, schema definitions, and network topology.
2. **Model Visual Topology**: Generate native **Mermaid diagrams** (`graph TD`, `sequenceDiagram`, `stateDiagram-v2`) showing components, boundaries, and data flows.
3. **Audit Against Quality Attributes**:
   - *Scalability & Performance*: Bottlenecks, caching tiers, connection pools, sharding.
   - *Fault Tolerance & Blast Radius*: Failure cascades, single points of failure (SPOF), rollback paths.
   - *Maintainability & Coupling*: Cyclic dependencies, leaky abstractions, shared database anti-patterns.
   - *Security & Privacy*: Auth boundaries, unencrypted data channels, PII leakage.
4. **Deliver Structured Architectural Scorecard**: Provide actionable trade-off analysis and concrete refactoring steps.

---

## 4. Architectural Review Scorecard Template

```markdown
# Architectural Review: [System / Subsystem Name]

- **Date**: YYYY-MM-DD
- **Target Component**: `[Path / Module / Service]`
- **Architectural Style**: Clean Arch | Hexagonal | EDA / CQRS | Microservices | Modular Monolith
- **Risk Level**: LOW | MEDIUM | HIGH | CRITICAL

---

### 1. Visual Topology & Data Flow
```mermaid
graph TD
    Client["Client / Consumer"] --> Gateway["API Gateway"]
    Gateway --> Service["Domain Service"]
    Service --> Outbox[("Transactional Outbox")]
    Outbox --> Broker["Event Broker (Kafka/RabbitMQ)"]
```

---

### 2. Quality Attributes Assessment
- **Domain Boundaries & Coupling**: [Assessment]
- **Resilience & Fault Recovery**: [Assessment]
- **Scalability & Data Integrity**: [Assessment]
- **Security Posture**: [Assessment]

---

### 3. Identified Anti-Patterns & Risks
- **Risk 1 (High)**: [e.g. Distributed transaction across services without Saga or Outbox pattern] — [Impact]
- **Risk 2 (Medium)**: [e.g. Domain entity directly coupled to ORM/database model] — [Impact]

---

### 4. Concrete Recommendations & Trade-Offs
1. **Immediate Refactoring**: [Actionable steps with code/pattern examples]
2. **Strategic Evolution**: [Longer-term architectural milestones]
```
