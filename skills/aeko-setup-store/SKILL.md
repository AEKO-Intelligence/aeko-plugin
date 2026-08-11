---
name: aeko-setup-store
description: >
  Compatibility router for AEKO domain and store setup. Routes the original
  domain URL or argument to aeko-store mode=setup.
argument-hint: "[domain-url]"
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEKO Setup Store — Compatibility Router

Domain and store setup moved to `/aeko-store mode=setup`.

Attempt delegation through the host's skill-invocation mechanism, preserving every original argument:

```text
This host cannot delegate to another skill. Run this command:
/aeko-store mode=setup <original-arguments>
```

If delegation is unavailable or rejected, print exactly the resolved command above after removing an empty
argument suffix. Do not connect, sync, inject products, or accept starter prompts here.
