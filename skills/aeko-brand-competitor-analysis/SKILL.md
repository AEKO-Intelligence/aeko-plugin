---
name: aeko-brand-competitor-analysis
description: >
  Compatibility router for brand competitor analysis. Routes every original
  argument to aeko-competitor-analysis with scope=brand.
argument-hint: "[domain-id] <competitor>"
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEKO Brand Competitor Analysis — Compatibility Router

Brand comparison moved to `/aeko-competitor-analysis scope=brand`.

Attempt delegation through the host's skill-invocation mechanism, preserving the original argument order:

```text
This host cannot delegate to another skill. Run this command:
/aeko-competitor-analysis scope=brand <original-arguments>
```

If delegation is unavailable or rejected, print exactly the resolved command above. Do not search or call
AEKO here; the successor owns both the free public stage and optional connected comparison.
