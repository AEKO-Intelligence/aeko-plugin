---
name: aeko-check-source
description: >
  Compatibility router for cited-page checking. Routes the original domain_id
  and source_id arguments to aeko-source-analysis cited-page mode.
argument-hint: "domain_id=<uuid> source_id=<uuid>"
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEKO Check Source — Compatibility Router

The cited-page workflow moved to `/aeko-source-analysis`.

Attempt delegation through the host's skill-invocation mechanism with the exact original named arguments:

```text
This host cannot delegate to another skill. Run this command:
/aeko-source-analysis domain_id=<uuid> source_id=<uuid>
```

If delegation is unavailable or rejected, print exactly the resolved command above. Do not fetch the source,
scan products, or draft a correction here; the successor owns the complete read-only workflow.
