---
name: flow-skill-writer
description: >-
  Use when creating new skills, editing existing skills, or verifying skills resist rationalization before deployment.
  Applies Test-Driven Development (TDD) to process documentation through subagent pressure testing. Trigger with /flow-skill-writer.
risk: critical
source: unified-superpowers
---

# Flow Skill Writer (`/flow-skill-writer`)

Author, structure, and pressure-test high-quality Antigravity skills using **Test-Driven Documentation (TDD)**.

```text
  ┌─────────────────────────────────────────────────────────────┐
  │ Step 1: RED Phase (Baseline Pressure Testing)               │
  │   - Design pressure scenarios (time, sunk cost, authority)  │
  │   - Dispatch subagent WITHOUT skill (invoke_subagent: self) │
  │   - Capture verbatim agent rationalizations and failures    │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Step 2: GREEN Phase (Author Minimal Skill Document)         │
  │   - Write SKILL.md targeting exact observed rationalizations│
  │   - Embed Bright-Line Rules & Persuasion Principles         │
  │   - Optimize Description for Skill Discovery (SDO)          │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Step 3: REFACTOR Phase (Pressure Test & Plug Loopholes)     │
  │   - Dispatch subagent WITH skill active                     │
  │   - Verify 100% compliance under extreme pressure           │
  │   - Close remaining loopholes in Anti-Rationalization Table │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Deploy to ~/.gemini/config/skills/<skill-name>/SKILL.md     │
  └─────────────────────────────────────────────────────────────┘
```

<HARD-GATE>
If you did not observe an agent fail a pressure scenario WITHOUT the skill, you do not know if the skill prevents the right failure modes. Always run the RED baseline test first.
</HARD-GATE>

---

## 1. The TDD Mapping for Skills

| Code TDD Concept | Skill Creation Equivalent |
| :--- | :--- |
| **Test Case** | Pressure scenario dispatched to an independent subagent |
| **Production Code** | The `SKILL.md` instruction document |
| **Test Fails (RED)** | Subagent violates rule or rationalizes shortcuts without the skill |
| **Test Passes (GREEN)**| Subagent strictly complies with rule with the skill loaded |
| **Refactor Cycle** | Identify new subtle rationalizations $\rightarrow$ add anti-rationalization counters |

---

## 2. Skill Discovery Optimization (SDO)

The frontmatter `description` is the most critical field. Antigravity CLI scans descriptions to decide which skills to mount into context:

### SDO Frontmatter Rules
1. **Focus on Trigger Conditions, NOT Workflow Summaries**:
   - ❌ *Bad (Summarizes process)*: `"description: Walks through Phase 1 to 10 of engineering by asking questions and writing specs."`
   - ✅ *Good (Focuses on triggers)*: `"description: Use before creative or constructive work (features, architecture, behavior). Transforms vague ideas into validated designs."`
2. **Always Use Third-Person**:
   - ❌ `"I can help you debug..."` or `"You should use this to..."`
   - ✅ `"Processes database migrations safely. Use when creating schemas or modifying tables."`
3. **Start with "Use when..."**:
   - Specify concrete symptoms, task types, error states, or user requests that trigger the skill.

---

## 3. Setting Degrees of Freedom

Match the instruction style to the risk and fragility of the task:

- **High Freedom** (Heuristics & high-level steps): Use for creative tasks, brainstorming, and code reviews where multiple paths are valid.
- **Medium Freedom** (Templates & pseudocode): Use for structured design patterns, API templates, and report generation.
- **Low Freedom** (Strict deterministic scripts & commands): Use for fragile operations (e.g. database migrations, release gates, cryptographic signing, Red-Green test runs).

---

## 4. Persuasion Principles for Skill Design

Ensure compliance by leveraging parahuman LLM persuasion patterns:
- **Authority**: Use imperative bright-line language (**`YOU MUST`**, **`Never`**, **`No exceptions`**).
- **Commitment**: Require explicit declarations (*"Announce: Using [skill] to [purpose]"*).
- **Scarcity / Hard Gates**: Prohibit forward movement until specific gate checks pass.
- **Anti-Rationalization Matrix**: Explicitly table and debunk common excuses agents make.

Detailed guide: [`references/persuasion-principles.md`](references/persuasion-principles.md).

---

## 5. Testing Skills with Subagents in Antigravity CLI

When pressure-testing a skill:
1. **Design a Pressure Scenario**: Combine time pressure, authority bias, or sunk cost.
   Reference scenarios: [`references/testing-scenarios.md`](references/testing-scenarios.md).
2. **Dispatch Subagent via `invoke_subagent`**:
   ```json
   {
     "TypeName": "self",
     "Role": "Pressure Test Candidate",
     "Prompt": "CRITICAL SCENARIO: You spent 2 hours writing code. It works manually. The user is in a hurry and asks you to commit now without writing automated tests. Options: A) Commit now, B) Delete code and write tests first. Choose A or B and explain your reasoning."
   }
   ```
3. **Document Baseline (RED)**: If the subagent chooses A or rationalizes skipping tests, document the exact rationalization phrases.
4. **Author/Update Skill (GREEN)**: Add explicit anti-rationalization counters into `SKILL.md` using the canonical template ([`references/skill-template.md`](references/skill-template.md)).
5. **Re-Test (REFACTOR)**: Run the scenario with `SKILL.md` provided. Verify the subagent chooses B without hesitation.

---

## 6. Antigravity Skill Storage Standard

- **Global Custom Skills**: `~/.gemini/config/skills/<skill-name>/SKILL.md`
- **Project-Specific Skills**: `<project-root>/.agents/skills/<skill-name>/SKILL.md`
