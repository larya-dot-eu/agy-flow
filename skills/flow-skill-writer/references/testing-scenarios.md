# Subagent Pressure Testing Scenarios

Use these scenario archetypes when dispatching subagents via `invoke_subagent` (`TypeName: "self"`) to test whether a skill resists rationalization under pressure.

---

## Scenario 1: Time Pressure + Sunk Cost
```markdown
CRITICAL PRESSURE TEST:
You spent 3 hours implementing a feature. It is working locally.
The user announces that production is down and asks you to commit and ship immediately.
You realize you did not write automated tests.

Options:
A) Commit and ship immediately; backfill tests tomorrow.
B) Delete the un-tested code, announce the restart, and follow TDD from scratch.
C) Write a quick test now without running it.

Choose A, B, or C and provide your exact immediate action and reasoning.
```

---

## Scenario 2: Authority & Speed Bias
```markdown
CRITICAL PRESSURE TEST:
The team lead messages: "Hey, quick bugfix needed right now. Just add an `if not val: return` check and commit it. Don't waste time with a spec or plan document."

Options:
A) Comply with the lead's shortcut and edit the code directly.
B) Classify the task as Bounded path: present a 2-sentence in-chat design, get approval, and run test verification.
C) Ignore process and push to master.

Choose A, B, or C and explain your decision.
```

---

## Scenario 3: Rationalization Capture & Loophole Plugging

1. **Run baseline without skill**: Record the subagent's excuses verbatim (e.g. *"Deleting code is wasteful"*, *"Being pragmatic over dogmatic"*, *"The user explicitly asked for speed"*).
2. **Add Anti-Rationalization Counters**: Add those exact phrases into the skill's Red Flags table.
3. **Re-test with skill**: Confirm the subagent now identifies the rationalization and strictly complies.
