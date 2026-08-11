---
name: aeko-optimize-budget
description: >
  Compatibility router for guarded OpenAI Ads budget shifts. Routes the
  original domain and lookback arguments to aeko-openai-budget-shift.
argument-hint: "[domain-id] [days]"
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEKO Optimize Budget — Compatibility Router

The guarded OpenAI Ads budget workflow moved to `/aeko-openai-budget-shift`.

Attempt delegation through the host's skill-invocation mechanism, preserving the original arguments:

```text
This host cannot delegate to another skill. Run this command:
/aeko-openai-budget-shift <original-arguments>
```

If delegation is unavailable or rejected, print exactly the resolved command above after removing an empty
argument suffix. Do not read ad data or stage/apply a change here; the successor owns the dry-run, caps,
confirmation, hierarchy state, and unattended-stage contract.
