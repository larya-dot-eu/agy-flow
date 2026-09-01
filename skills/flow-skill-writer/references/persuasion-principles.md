# Persuasion Principles for Skill Design

## Overview
LLMs respond to the same persuasion principles as humans. Meincke et al. (2025) tested 7 persuasion principles across N=28,000 LLM conversations, proving compliance increased from **33% to 72%** (p < .001) when bright-line persuasion techniques were applied.

---

## The Seven Principles

### 1. Authority
- **Mechanism**: Deference to expertise and absolute rules.
- **Language**: Imperative statements (**`YOU MUST`**, **`Never`**, **`No exceptions`**).
- **Rule**: Eliminates decision fatigue and rationalization.
- **Example**:
  - ✅ *"Write code before test? Delete it. Start over. No exceptions."*
  - ❌ *"Consider writing tests first when feasible."*

### 2. Commitment
- **Mechanism**: Consistency with prior public declarations.
- **Language**: Mandatory announcements (*"Announce: Using [skill] to [purpose]"*) and checklist tracking (`- [ ]` / `- [x]`).
- **Rule**: Forces explicit accountability before taking actions.

### 3. Scarcity & Hard Gates
- **Mechanism**: Sequential time-bound barriers.
- **Language**: Hard gates (*"<HARD-GATE> Do NOT proceed until X is approved </HARD-GATE>"*).
- **Rule**: Prevents procrastination (*"I'll do it later"*) and unauthorized execution.

### 4. Social Proof
- **Mechanism**: Highlighting universal norms and common failure modes.
- **Language**: *"Checklists without task tracking = steps get skipped. Every time."*

### 5. Unity
- **Mechanism**: Shared engineering goals and professional identity.
- **Language**: *"We are colleagues engineering robust software together. I need your rigorous technical judgment."*

### 6. Reciprocity & 7. Liking
- **Rule**: AVOID in discipline-enforcing skills. Creates sycophancy or weak compromises.

---

## Combination Matrix by Skill Type

| Skill Type | Principles to Use | Principles to Avoid |
| :--- | :--- | :--- |
| **Discipline & Safety Enforcement** | Authority + Commitment + Scarcity / Hard Gates | Liking, Reciprocity |
| **Technique & Architecture Guidance** | Moderate Authority + Unity | Heavy Dogmatism |
| **Collaborative Ideation** | Unity + Commitment | Heavy Authority |
| **Pure Reference / Syntax** | Clarity & Structure Only | All Persuasion |
