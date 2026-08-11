---
name: aeko-inject-reviews
description: >
  Compatibility router for real-review intake. Routes the original domain
  argument to aeko-store mode=reviews without changing review evidence.
argument-hint: "[domain-id]"
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEKO Inject Reviews — Compatibility Router

Real-review intake moved to `/aeko-store mode=reviews`.

Attempt delegation through the host's skill-invocation mechanism, preserving the original domain argument:

```text
This host cannot delegate to another skill. Run this command:
/aeko-store mode=reviews <original-arguments>
```

If delegation is unavailable or rejected, print exactly the resolved command above after removing an empty
argument suffix. Do not gather, normalize, or inject reviews here; the successor owns provenance and preview.
