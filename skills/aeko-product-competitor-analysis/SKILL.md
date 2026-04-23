---
name: aeko-product-competitor-analysis
description: >
  Product-level competitor analysis. Finds comparable products across
  competitor sites via WebSearch, fetches each PDP, builds a
  property-by-property comparison matrix (materials, sizing, claims,
  price, reviews, JSON-LD coverage), and calls out strengths / weaknesses
  relative to the user's product. Replaces the retired aeko_ai backend
  product-analysis service.
argument-hint: "<product-id> [competitor-urls...]"
allowed-tools: aeko_get_domain_info, aeko_get_brand_kit, aeko_get_product_description, aeko_list_store_integrations, aeko_search_research_prompts, aeko_get_tracked_prompt, WebSearch, WebFetch, Write
---

# AEKO Product Competitor Analysis

Produces a comparison matrix between one of the user's products and 3-5 competing products across the same category. Drives PDP strategy — output tells the user exactly where their PDP lags or leads.

## Inputs

- `product-id` (required) — `$1`. AEKO `external_product_id` from a connected Cafe24 / Shopify integration, OR a direct product URL (skill will parse and confirm).
- `competitor-urls` (optional) — space-separated competitor PDP URLs. If omitted, the skill discovers via WebSearch.

## Step 1 — Resolve the user's product

1. If `$1` is a URL → treat as the user's product URL; derive integration + external_product_id via `aeko_list_store_integrations` + lightweight URL matching. If ambiguous, ask user to pick.
2. If `$1` is a plain id → find the integration via `aeko_list_store_integrations` (first match wins; ask user if multiple integrations).
3. Call `aeko_get_product_description(integration_id, external_product_id)` to get the raw description HTML. If this fails (Cafe24 token refresh, etc.), fall back to `WebFetch(target_url)` on the live page.
4. Parse the user's product: title, key attributes, price (if in description), image URLs, any embedded JSON-LD.

## Step 2 — Find competitors (if not supplied)

If `competitor-urls` missing:

1. Build a search query from the user's product title + brand kit `target_audience` / country. Example: `"차렵이불" 한정수량 알러지케어 site:*.co.kr -site:slound.co.kr`.
2. `WebSearch(query, num_results=10)`. Filter to distinct roots (drop duplicates, skip marketplaces if possible).
3. Optionally augment: pull top-cited competing domains from `aeko_get_tracked_prompt` forensics on the user's product-related prompts (if any). These are domains AI engines actually cite — higher value than raw search.
4. Pick top 3-5 competitor URLs. Confirm with the user before proceeding ("Here are the candidates I found — use these, or paste your own?").

## Step 3 — Fetch each competitor PDP

For each competitor URL:
1. `WebFetch(url)` to get the page.
2. Parse: title, key attributes, visible price, image count, embedded JSON-LD types, review presence, FAQ presence.
3. Record the raw extracted text for use in Step 4.

Cap total fetches at 5. Handle failures per-URL — note in output but don't abort the whole run.

## Step 4 — Build comparison matrix

Fields to compare (adapt per category — product-type-aware):

```
| Attribute              | <user's product> | <comp 1> | <comp 2> | <comp 3> | ... |
|------------------------|------------------|----------|----------|----------|-----|
| Title                  | ...              | ...      |          |          |     |
| Price                  | ...              | ...      |          |          |     |
| Material / composition | ...              | ...      |          |          |     |
| Size variants          | ...              | ...      |          |          |     |
| Key claim (hero line)  | ...              | ...      |          |          |     |
| Image count            | ...              | ...      |          |          |     |
| Review count           | ...              | ...      |          |          |     |
| Average rating         | ...              | ...      |          |          |     |
| Product JSON-LD        | ✓ / ✗            | ...      |          |          |     |
| FAQPage JSON-LD        | ✓ / ✗            | ...      |          |          |     |
| Review JSON-LD         | ✓ / ✗            | ...      |          |          |     |
| FAQ on page            | ✓ / ✗            | ...      |          |          |     |
| Comparison table       | ✓ / ✗            | ...      |          |          |     |
| Certifications         | ...              | ...      |          |          |     |
```

Use Claude's reasoning to fill each row from the fetched text. Missing data → `—` not fabrication.

## Step 5 — Strengths + weaknesses + gaps

Compose three sections:

```
## Where <user's product> leads

- <bullet per attribute where user's product is clearly ahead>

## Where <user's product> lags

- <bullet per attribute where at least 2 competitors are ahead>

## Structured-data gaps

- <list of JSON-LD types competitors have that user's product doesn't>
- <list of review / FAQ coverage competitors have that user's product doesn't>
```

## Step 6 — Recommended actions

Rank 3 actions by impact:

```
1. **Add FAQPage JSON-LD** — <N> of <M> competitors have it; your PDP doesn't.
   Run `/aeko-action-center <domain_id> pdp` and look for a pdp_update item
   targeting this product; otherwise tell me to draft one standalone.
2. **Match review depth** — competitors show <N> reviews on average;
   your PDP shows <M>. Consider <specific approach>.
3. ...
```

## Step 7 — Save + summary

Write the full matrix + analysis to:
`./aeko-artifacts/<domain_id>/product-competitor-analyses/<product-slug>-<YYYYMMDD>.md`

User-facing summary:

```
✔ Product competitor analysis saved: <path>
  Compared vs:     <N> competitors
  Biggest gap:     <top row from "Where lags">
  Next action:     <first recommended action>
```

## Error paths

- Product description fetch fails AND WebFetch of target_url also fails → stop; ask user for the live product URL manually.
- WebSearch returns zero usable competitors AND user didn't supply URLs → ask user to paste 2-3 competitor URLs; don't proceed with zero comps.
- All competitor WebFetches fail → stop and report; tell user their competitor sites may be blocking crawlers (common in KR retail).

## What this skill never does

- Never writes to the store.
- Never decides the user's pricing — only shows the price spread.
- Never fabricates attributes; missing data stays missing.
- Never auto-adds competitors beyond the top 5.
