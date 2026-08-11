---
name: aeko-compose-ads
description: >
  Compatibility router for the renamed OpenAI Ads composition workflow.
  Routes the original domain and minimum-score arguments to
  aeko-openai-compose-ads.
argument-hint: "[domain-id] [min-score]"
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEKO Compose Ads — Compatibility Router

The review-grounded OpenAI Ads composition workflow moved to `/aeko-openai-compose-ads`.

Attempt delegation through the host's skill-invocation mechanism, preserving the original arguments:

```text
This host cannot delegate to another skill. Run this command:
/aeko-openai-compose-ads <original-arguments>
```

If delegation is unavailable or rejected, print exactly the resolved command above after removing an empty
argument suffix. Do not fetch reviews, cluster products, preview, or create ad structures here; the
successor owns the full paused-by-default flow, confirmation gate, idempotency, and error handling.
