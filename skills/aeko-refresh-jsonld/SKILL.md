---
name: aeko-refresh-jsonld
description: >
  Compatibility router for surgical review JSON-LD refresh. Routes the original
  product and integration arguments to aeko-update-pdp mode=refresh.
argument-hint: "<product-id> [integration-id]"
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEKO Refresh JSON-LD — Compatibility Router

Review JSON-LD maintenance moved to `/aeko-update-pdp mode=refresh`.

Attempt delegation through the host's skill-invocation mechanism, preserving the original arguments:

```text
This host cannot delegate to another skill. Run this command:
/aeko-update-pdp mode=refresh <original-arguments>
```

If delegation is unavailable or rejected, print exactly the resolved command above. Do not fetch, claim, or
patch here; the successor owns the patch-only fields, byte-preservation check, confirmation, and rollback.
