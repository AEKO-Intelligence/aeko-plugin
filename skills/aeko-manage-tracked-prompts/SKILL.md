---
name: aeko-manage-tracked-prompts
description: >
  Compatibility router for reviewing and untracking prompts. Routes the
  original optional domain argument to aeko-manage-prompts mode=review.
argument-hint: "[domain-id]"
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEKO Manage Tracked Prompts — Compatibility Router

Review, organization, and untracking moved to `/aeko-manage-prompts mode=review`.

Attempt delegation through the host's skill-invocation mechanism, preserving the original domain argument:

```text
This host cannot delegate to another skill. Run this command:
/aeko-manage-prompts mode=review <original-arguments>
```

If delegation is unavailable or rejected, print exactly the resolved command above after removing an empty
argument suffix. Do not untrack here; the successor owns the separate `UNTRACK <N>` typed gate.
