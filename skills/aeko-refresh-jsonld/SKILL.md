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
allowed-tools: aeko_list_action_items, aeko_create_action_item, aeko_claim_action_item, aeko_release_action_item, aeko_get_action_plan, aeko_get_product_description, aeko_update_product_page, aeko_list_store_integrations, aeko_list_store_writes, aeko_revert_store_write, aeko_complete_action_item, WebFetch, Write
---

# AEKO Refresh JSON-LD

Surgical JSON-LD update flow. Reads the full description, patches just the JSON-LD `<script>` blocks (review count, rating, fresh reviews), writes back. Never rewrites the surrounding HTML.

## Marketer-facing output contract

Explain this as "refreshing review facts AI can read" rather than "editing JSON-LD." It can write to the store, so
show Before / After / Risk / Undo before completion. This skill does not refresh price or availability unless a
future backend supplies authoritative current offer fields.

Language: mirror the user's chat language for user-facing steps, summaries, questions, and risk/undo copy.
Keep slash commands, IDs, file paths, schema keys, JSON-LD terms, and tool names in English/ASCII.

## Inputs

- `product-id` (required) — `$1`. External product id (Cafe24 product_no / Shopify product id).
- `integration-id` (optional) — `$2`. UUID of the store integration. If missing, call `aeko_list_store_integrations` and pick. If multiple integrations, ask user.

## Step 1 — Resolve integration

1. Always call `aeko_list_store_integrations`; this is the ownership/capability source of truth.
2. If `$2` is present, select only the exact matching returned integration ID. If it is absent and one row
   exists, auto-pick it; if multiple exist, show the list and ask the user.
3. Parse the selected row's exact `domain_id`; it is required for the ActionItem authorization below. A
   supplied ID that is not returned is invalid—stop rather than trusting it.

Verify the integration has write access (markdown output from `aeko_list_store_integrations` says "Write-back: ✅ Write enabled"). If not → stop; tell user to reconnect with write scope in Settings → Store Integrations.

## Step 1.5 — Reuse/create and claim the JSON-LD ActionItem

Store writes require one owned, tier-checked ActionItem claim. List every page of action items for the resolved
domain using all statuses, and retain exact matches where `artifact_type == "json_ld"` and
`product_id == external_product_id` (and `integration_id` matches when present).

- Reuse the newest `ready` match. If the newest active match is `pending` or `generating_prose`, stop and ask
  the user to retry when it is ready.
- If no active match exists, create one with `artifact_type="json_ld"`, `tab="action"`, the exact product ID,
  and `idempotency_key="jsonld-refresh:<domain_id>:<external_product_id>:after:<newest-terminal-id-or-initial>"`.
- Call `aeko_claim_action_item(item_id)` exactly once and store its returned non-empty `claim_id` as
  `execution_claim_id`. Claims never expire automatically.
- On 409, stop. Never release another run automatically. Forced recovery is allowed only after the user
  explicitly confirms no other run is active and no store mutation occurred; then call
  `aeko_release_action_item(item_id, force=true, confirm_no_active_execution=true)`, end, and ask them to rerun.

After winning the claim, every confirmed no-write failure/cancellation releases with
`aeko_release_action_item(item_id, claim_id=execution_claim_id)`. Never release after a successful or
ambiguous store call.

Call `aeko_get_action_plan(item_id)` and retain its exact `target_url` plus any authoritative review/rating
facts in frontmatter/prose. If this newly created JSON-LD item has no usable target URL, keep the selected
store product as the source of truth and do not invent a public URL. This Plan load is what makes Plan facts
eligible in Step 4.

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
Then release the matching claim and stop.

## Step 4 — Identify patch targets

Typical refresh targets (pick whichever apply based on what's present). Keep this skill scoped to review/rating
freshness:

- `Product.aggregateRating.ratingValue` — current average rating
- `Product.aggregateRating.reviewCount` — total review count
- `Product.review[]` — sample of individual reviews (rotate to latest)
- `Review[]` at root (if Reviews are not nested under Product)
- `AggregateRating` block standalone

Do not refresh `Offer.price`, `Offer.availability`, shipping, or return-policy fields in this skill. Those fields
must come from authoritative store/product data and visible-content parity checks handled by `/aeko-update-pdp` or
a future backend offer-refresh tool.

**Source of truth for the new values** (pick whichever is available, in priority order):
1. **If prose in an Action Item pointed you here** — the Plan.md frontmatter may already carry the new review count / rating. Use it.
2. **Read visible review widgets only** via `WebFetch(<target_url>)` when the current review count/rating is clearly shown in text or review-widget markup. Do not use this path for price, stock, shipping, or returns.
3. **Ask the user** — "I found existing JSON-LD but couldn't detect a fresh review count. Paste the current review count and average rating, or cancel."

Never fabricate values. If you can't find or confirm new values, abort with a clear message.

## Step 5 — Patch JSON-LD

For each parsed schema node with a patch target:
1. Update the specific keys (do NOT touch other keys).
2. Preserve every untouched node and sibling field.
3. Normalize the result into one object:
   `json_ld_payload={"@context":"https://schema.org","@graph":[<all preserved/patched nodes>]}`.
   Do not send a patched full description; a Starter `json_ld` action authorizes only this JSON object.

Emit an inline diff summary (not shown to user yet — for the completion summary):
```
- Product.aggregateRating.ratingValue: 4.6 → 4.7
- Product.aggregateRating.reviewCount: 128 → 143
- Product.review[]: rotated to 5 most recent (was 5 stale)
```

## Step 6 — Validate patched HTML

Before writing back, validate the *content*, not its size:
- **Parses:** every `<script type="application/ld+json">` block parses with `json.loads` (no trailing
  commas, no broken/early-closed `<script>` tags).
- **Schema intact:** `@context: "https://schema.org"` preserved, the block's `@type` is unchanged, and the
  required fields for that type are still present (e.g. an `AggregateRating` still carries `ratingValue` +
  `reviewCount`; a `Review` still carries `author` + `reviewRating`). The patch must not drop sibling fields.
- **Patch landed:** the fields you intended to change (`AggregateRating.ratingValue` / `reviewCount`,
  `review[]`) now hold the *new* values — confirm the edit actually took, not just that JSON is valid.
- **Surgical preview:** emulate the backend replacement locally—replace the first JSON-LD block with
  `json_ld_payload`, remove additional JSON-LD blocks, and confirm everything outside those original blocks
  is byte-identical to `existing_html`. The payload consolidates schema nodes; it never carries visible HTML.

If validation fails → release the matching claim and stop; tell the user the patch produced invalid or non-surgical JSON-LD and dump the diff for debugging.

## Step 7 — Confirm and write back

Before any store call, show the user—in their chat language—the exact Before / After / Risk / Undo summary:
current and proposed review/rating values, confirmation that all non-JSON-LD bytes are unchanged, the public
page mutation risk, and that the returned audit ID can be reverted. Ask for explicit confirmation to update
the current product page. A cancellation releases the matching claim and stops.

Call:
```
aeko_update_product_page(
    integration_id=integration_id,
    external_product_id=external_product_id,
    action_item_id=item_id,
    execution_claim_id=execution_claim_id,
    json_ld=json_ld_payload,
)
```

The backend fetches the current store description inside the write transaction and injects this JSON-LD while
preserving every non-JSON-LD byte. This is exactly one store call and one audit/revert boundary. Parse
`audit_id` + status (`admin_url` may be absent). On a
confirmed no-write 4xx, release the matching claim, surface verbatim, and do not retry automatically. On an
ambiguous timeout/5xx, keep the claim; the backend blocks duplicate retries. Call `aeko_list_store_writes`,
inspect the store, and complete with the matching audit only after reconciliation.

After a confirmed successful write, call
`aeko_complete_action_item(item_id, artifact_summary=..., write_result={"mode":"current_product", "audit_id":...}, execution_claim_id=execution_claim_id)`.

## Step 8 — Confirm + summary

```
✔ JSON-LD refreshed on <product_title or id>
  Platform:   <cafe24 | shopify>
  Audit ID:   <audit_id>
  Changed:    review/rating facts only
  Risk:       store description was updated, but only JSON-LD review blocks changed
  Undo:       aeko_revert_store_write("<audit_id>")
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
- Write-back 4xx with confirmed no mutation → release the matching claim and stop; leave `existing_html` untouched.
- Ambiguous write response → keep the claim; do not retry or force-release.

## What this skill never does

- Never rewrites the non-JSON-LD portion of the description.
- Never creates JSON-LD from scratch (use `/aeko-update-pdp`).
- Never fabricates review counts or ratings.
- Never runs without user confirmation on the first invocation (schedule wrappers can auto-approve).
- Never writes without a matching ActionItem claim token or splits one refresh across multiple store calls.
