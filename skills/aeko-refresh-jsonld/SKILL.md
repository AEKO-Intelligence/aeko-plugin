---
name: aeko-refresh-jsonld
description: >
  Periodic JSON-LD refresh for a product page. Reads the current description
  HTML from the connected store, surgically patches the embedded JSON-LD
  (typically `AggregateRating.ratingValue`, `reviewCount`, `review[]`), and
  writes the updated description back. Designed to be run on cadence via
  `/schedule` to keep review counts / ratings fresh without touching the
  rest of the PDP.
argument-hint: "<product-id> [integration-id]"
allowed-tools: aeko_get_product_description, aeko_update_product_description, aeko_list_store_integrations, aeko_get_brand_kit, aeko_list_store_writes, aeko_revert_store_write, Write
---

# AEKO Refresh JSON-LD

Surgical JSON-LD update flow. Reads the full description, patches just the JSON-LD `<script>` blocks (review count, rating, fresh reviews), writes back. Never rewrites the surrounding HTML.

## Inputs

- `product-id` (required) — `$1`. External product id (Cafe24 product_no / Shopify product id).
- `integration-id` (optional) — `$2`. UUID of the store integration. If missing, call `aeko_list_store_integrations` and pick. If multiple integrations, ask user.

## Step 1 — Resolve integration

1. Parse `$2` if present.
2. Else → `aeko_list_store_integrations`. If one: auto-pick. If multiple: show list, ask user.

Verify the integration has write access (markdown output from `aeko_list_store_integrations` says "Write-back: ✅ Write enabled"). If not → stop; tell user to reconnect with write scope in Settings → Store Integrations.

## Step 2 — Fetch current description

Call `aeko_get_product_description(integration_id, external_product_id)`.

Handle platform errors:
- Cafe24 token refresh failure → tell user to reconnect the store; stop.
- 404 → the product doesn't exist on the platform; stop.
- Other 502 → surface the upstream error verbatim; stop.

Save the raw HTML to memory as `existing_html`.

## Step 3 — Parse JSON-LD blocks

Extract every `<script type="application/ld+json">...</script>` block from `existing_html`. For each block:
1. Parse the JSON content.
2. Classify by `@type`: Product, FAQPage, Review, AggregateRating, BreadcrumbList, etc. Handle `@graph` arrays (multi-type blocks).

If no JSON-LD blocks found → the product description doesn't have structured data yet. Tell user:
```
No JSON-LD blocks found on this product description. This skill refreshes
existing JSON-LD; it does not create it from scratch. To add initial
JSON-LD, run `/aeko-update-pdp <item_id>` or create a new technical item
at the AEKO dashboard.
```
Then stop.

## Step 4 — Identify patch targets

Typical refresh targets (pick whichever apply based on what's present):

- `Product.aggregateRating.ratingValue` — current average rating
- `Product.aggregateRating.reviewCount` — total review count
- `Product.review[]` — sample of individual reviews (rotate to latest)
- `Review[]` at root (if Reviews are not nested under Product)
- `AggregateRating` block standalone

**Source of truth for the new values** (pick whichever is available, in priority order):
1. **If prose in an Action Item pointed you here** — the Plan.md frontmatter may already carry the new review count / rating. Use it.
2. **Scrape the live storefront page** via `WebFetch(<target_url>)` — most storefronts render review widgets with current counts visible in the HTML. Extract from visible text / review-widget markup.
3. **Ask the user** — "I found existing JSON-LD but couldn't detect a fresh review count. Paste the current review count and average rating, or cancel."

Never fabricate values. If you can't find or confirm new values, abort with a clear message.

## Step 5 — Patch JSON-LD

For each block with a patch target:
1. Update the specific keys (do NOT touch other keys).
2. Re-serialize as valid JSON (no trailing commas, no comments).
3. Replace the original `<script>` block's content in `existing_html` with the patched JSON. Preserve the exact `<script type="application/ld+json">` opening and closing tags.

Emit an inline diff summary (not shown to user yet — for the completion summary):
```
- Product.aggregateRating.ratingValue: 4.6 → 4.7
- Product.aggregateRating.reviewCount: 128 → 143
- Product.review[]: rotated to 5 most recent (was 5 stale)
```

## Step 6 — Validate patched HTML

Before writing back:
- Every `<script type="application/ld+json">` block parses as valid JSON.
- Every block has `@context: "https://schema.org"` (preserved from original).
- No `<script>` tags accidentally closed early or broken.
- The patched `existing_html` length is within ±25% of the original (large swings indicate corruption).

If validation fails → stop; tell user the patch produced invalid HTML and dump the diff for debugging.

## Step 7 — Write back

Call:
```
aeko_update_product_description(
    integration_id=integration_id,
    external_product_id=external_product_id,
    description_html=<patched existing_html>,
)
```

Parse response for `audit_id` + `admin_url` + status. On 4xx, surface verbatim; do NOT re-try automatically.

## Step 8 — Confirm + summary

```
✔ JSON-LD refreshed on <product_title or id>
  Platform:   <cafe24 | shopify>
  Audit ID:   <audit_id>
  Admin URL:  <admin_url>
  Changes:
    - Product.aggregateRating.ratingValue: 4.6 → 4.7
    - Product.aggregateRating.reviewCount: 128 → 143
    - Product.review[]: rotated to 5 most recent

Revert: aeko_revert_store_write("<audit_id>")
Next refresh: schedule via `/schedule` if you want this weekly.
```

## Scheduling note

This skill is intentionally small + idempotent. To run it weekly, users can:
```
/schedule every Monday 8am /aeko-refresh-jsonld <product_id>
```

(Check your host's `/schedule` support — on Claude Code the ScheduleWakeup / CronCreate tools cover this; other hosts may vary.)

## Error paths

- Integration missing write scope → stop with reconnect instruction.
- Product not found → stop.
- No JSON-LD present → stop with guidance to create via `/aeko-update-pdp`.
- No fresh values available AND user declines to paste → stop; don't fabricate.
- Validation fails → stop; don't write back.
- Write-back 4xx → stop; leave `existing_html` untouched.

## What this skill never does

- Never rewrites the non-JSON-LD portion of the description.
- Never creates JSON-LD from scratch (use `/aeko-update-pdp`).
- Never fabricates review counts or ratings.
- Never runs without user confirmation on the first invocation (schedule wrappers can auto-approve).
