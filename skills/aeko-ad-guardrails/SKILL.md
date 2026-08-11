---
name: aeko-ad-guardrails
description: >
  Compatibility router for the renamed OpenAI Ads automation guardrails.
  Routes the original domain argument to aeko-openai-guardrails.
argument-hint: "[domain-id]"
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEKO Ad Guardrails — Compatibility Router

The OpenAI Ads automation workflow moved to `/aeko-openai-guardrails`.

Attempt delegation through the host's skill-invocation mechanism, preserving the original argument:

```text
This host cannot delegate to another skill. Run this command:
/aeko-openai-guardrails <original-arguments>
```

If delegation is unavailable or rejected, print exactly the resolved command above after removing an empty
argument suffix. Do not inspect, create, update, arm, disarm, or run a rule here; the successor owns every
threshold, preview, confirmation, broad-match gate, activity path, and account-wide emergency stop.
