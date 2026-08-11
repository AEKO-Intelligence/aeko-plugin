---
name: aeko-find-prompts-to-track
description: >
  Compatibility router for research-prompt discovery and tracking. Routes the
  original optional domain argument to aeko-manage-prompts mode=discover.
argument-hint: "[domain-id]"
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEKO Find Prompts To Track — Compatibility Router

Discovery and tracking moved to `/aeko-manage-prompts mode=discover`.

Attempt delegation through the host's skill-invocation mechanism, preserving the original domain argument:

```text
This host cannot delegate to another skill. Run this command:
/aeko-manage-prompts mode=discover <original-arguments>
```

If delegation is unavailable or rejected, print exactly the resolved command above after removing an empty
argument suffix. Do not search or track here; the successor owns quota pre-flight and selection gates.
