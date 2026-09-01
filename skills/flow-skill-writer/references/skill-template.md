# Antigravity Skill Template

Use this canonical structure when authoring a new `SKILL.md`:

```markdown
---
name: [skill-name-hyphenated]
description: >-
  Use when [specific triggering conditions, symptoms, and scenarios].
  Avoid summarizing workflow; focus strictly on when future agents should load this skill.
risk: low | medium | high | critical
source: workspace | global
---

# [Skill Title] (`/[command-name]`)

[Core principle in 1-2 concise sentences].

```text
  [ASCII Architecture or State Flow Diagram]
```

<HARD-GATE>
[Mandatory bright-line rule or prerequisite that halts forward movement until satisfied]
</HARD-GATE>

---

## 1. When to Use & Path Classification
- **Symptoms / Trigger Conditions**: [Bullet points]
- **When NOT to Use**: [Boundaries and exclusions]

---

## 2. Core Workflow & Step-by-Step Instructions
1. **Step 1**: [Action]
2. **Step 2**: [Action]
3. **Step 3**: [Action]

---

## 3. Anti-Rationalization Table (Red Flags)

| Rationalization Thought | Reality & Rule |
| :--- | :--- |
| *"[Common excuse to bypass rule]"* | [Direct bright-line counter-rule] |

---

## 4. Verification & Output Standards
- **Verification Command**: [e.g. `pytest`, `npm test`, linter command]
- **Deliverable Path**: `docs/...` or target source file.
```
