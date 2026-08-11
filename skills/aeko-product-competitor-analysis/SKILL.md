---
name: aeko-product-competitor-analysis
description: >
  Compatibility router for product competitor analysis. Routes every original
  product ID, product URL, and competitor URL to scope=product.
argument-hint: "<product-id> [competitor-urls...]"
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEKO Product Competitor Analysis — Compatibility Router

Product comparison moved to `/aeko-competitor-analysis scope=product`.

Attempt delegation through the host's skill-invocation mechanism, preserving every original argument:

```text
This host cannot delegate to another skill. Run this command:
/aeko-competitor-analysis scope=product <original-arguments>
```

If delegation is unavailable or rejected, print exactly the resolved command above. Do not fetch products
or build a matrix here; the successor owns the free public stage and optional official-product enrichment.
