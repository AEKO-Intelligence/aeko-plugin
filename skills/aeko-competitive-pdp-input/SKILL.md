---
name: aeko-competitive-pdp-input
description: >
  Competitor-focused PDP research input for one synced product. Uses the
  product's AEKO brief plus web research to identify common competitor PDP
  sections, differentiators, missing proof points, and positioning edges that
  should shape the final product-detail HTML.
argument-hint: <product-id>
allowed-tools: aeko_inspect_product_page, aeko_read_product_page_image, aeko_get_pdp_optimization_brief, WebSearch, WebFetch
---

# AEKO · Competitive PDP Input

Use this skill when the user chose `product_page_web_competitor` depth for a PDP rewrite.

## Step 1: Load AEKO context

Call:

`aeko_get_pdp_optimization_brief(product_id=..., strategy="append_below_images", research_depth="product_page_web_competitor")`

From the brief, extract:
- product title
- product URL
- store/domain context
- current page issues
- any existing competitor evidence already surfaced by AEKO

Then call:

`aeko_inspect_product_page(product_id=...)`

Use the live page structure and extracted image list as the baseline for competitor comparison.
Open the most important live PDP images with `aeko_read_product_page_image(...)` if visual proof, materials, or spec blocks matter to the comparison.

## Step 2: Find direct competitors

Use `WebSearch` to identify 3-5 direct competitor PDPs for the same product type.

Prioritize:
- same product class
- similar target price band
- similar market or use case
- pages with strong merchandising structure

Avoid broad category pages when a real product page is available.

## Step 3: Inspect the competitor PDPs

Use `WebFetch` on the strongest 2-4 competitor pages and capture:
- section structure / heading spine
- proof blocks (materials, certifications, specs, comparison tables)
- differentiation angles
- FAQ patterns
- trust signals

## Step 4: Produce structured input for the rewrite

Return a concise brief with these sections:

### Common competitor sections
- Repeated PDP blocks or heading patterns worth mirroring

### Competitor claims
- Important claims competitors lead with

### User-product edges
- Advantages the user's product appears to have
- Only include defensible edges grounded in the product itself or in reviewed sources

### Missing proof points
- Facts the final PDP should verify or gather before making stronger claims

### Recommended differentiators
- How the rewritten PDP should position the product without copying competitor language

## Step 5: Hand off cleanly

End with a short instruction block telling the caller how to use the output:
- fold the common sections into the PDP structure
- use the differentiators in the benefits/proof sections
- do not copy competitor wording
- keep claims defensible
