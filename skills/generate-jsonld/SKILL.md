---
name: generate-jsonld
description: >
  Deprecated. Product / FAQPage / Review JSON-LD are now produced inline
  by /aeko-run-action or, for site-level schema, /aeko-fix-technical.
  This wrapper exists for one release cycle.
argument-hint: "(deprecated)"
allowed-tools: []
---

# generate-jsonld — Deprecated

Retired in the 2026-04 MCP consolidation. JSON-LD generation is no longer a standalone skill.

## Where it lives now

- **Product / FAQPage / Review JSON-LD for a PDP** → produced inline by `aeko-run-action` when the Plan.md's `frontmatter.pdp_responsive_contract.json_ld_required == true`. See `docs/contracts/action-item-contract.md` §3.2 for the expanded Product field set (`offers`, `sku`, `gtin13`, `mpn`, `shippingDetails`, `hasMerchantReturnPolicy`, `speakable`, `sameAs`) and §3.4 for the `[VERIFY: ...]` marker convention that handles missing data without fabrication.
- **Site-level JSON-LD (Organization, WebSite, BreadcrumbList)** → produced by `aeko-fix-technical` when the Plan's `artifact_type == "json_ld"`.

## What to do instead

1. `/aeko-action-center <domain_id>` — pick a pending item.
2. Run the appropriate executor:
   - PDP items → `/aeko-run-action <item_id>`
   - Technical items (site-level schema) → `/aeko-fix-technical <item_id>`

If you need standalone JSON-LD outside any Action/Technical item, describe the schema type and available fields in plain language — I'll produce it without running a retired skill. Do NOT invoke this skill's former tools (`aeko_prepare_json_ld` remains available for the new executors; standalone flows using it have been retired).
