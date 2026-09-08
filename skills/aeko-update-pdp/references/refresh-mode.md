# Refresh mode — aggregate review facts only

Surgical JSON-LD update flow. Refresh mode patches **ONLY**
`AggregateRating.ratingValue` and `AggregateRating.reviewCount`. It never creates or rotates `review[]`:
the current tool surface does not load authoritative review bodies, authors, and dates, so doing so would
invite fabricated reviews. Every non-JSON-LD byte and every sibling schema field must remain unchanged.

Before any tool call, issue exactly one deferred-tool search:

```text
ToolSearch(query="select:aeko_list_action_items,aeko_create_action_item,aeko_claim_action_item,aeko_release_action_item,aeko_get_action_plan,aeko_get_product_description,aeko_update_product_page,aeko_list_store_integrations,aeko_list_store_writes,aeko_revert_store_write,aeko_complete_action_item,WebFetch", max_results=16)
```

## Marketer-facing contract

Explain this as “refreshing review totals AI can read.” It is a live-store write and always requires a
foreground human confirmation. A scheduled or unattended invocation may prepare a proposal only; it may
never auto-approve or call `aeko_update_product_page`.

Mirror the user's language for questions, summaries, and risk/undo copy. Keep commands, IDs, paths, schema
keys, and tool names in English/ASCII.

## Inputs and integration

- `product-id` (required) — `$1`, the exact external product ID.
- `integration-id` (optional) — `$2`. Always call `aeko_list_store_integrations`; accept `$2` only when it
  exactly matches a returned integration. Auto-pick one returned row or ask when several exist.

Retain the selected row's exact `domain_id` and require “Write enabled.” A missing scope stops the run with
the reconnect step.

## Step 1 — reuse/create and claim one ActionItem

List every page of action items for the domain using all statuses. Retain exact matches where
`artifact_type == "json_ld"`, `product_id == external_product_id`, and `integration_id` matches when present.

- Reuse the newest `ready` match. Stop on a newer `pending`/`generating_prose` match.
- Otherwise create one with `artifact_type="json_ld"`, `tab="action"`, the exact product ID, and
  `idempotency_key="jsonld-refresh:<domain_id>:<external_product_id>:after:<newest-terminal-id-or-initial>"`.
- Call `aeko_claim_action_item(item_id)` exactly once and retain its non-empty `claim_id` as
  `execution_claim_id`. Claims do not expire.
- On 409, stop. Force-release only after the user confirms both that no other run is active and no store
  mutation occurred; then end and ask them to rerun.

Release the matching claim only after a confirmed no-write failure/cancellation. Never release after a
successful or ambiguous store call.

Call `aeko_get_action_plan(item_id)` and retain only explicit source provenance and any review totals marked
as store-authoritative. Plan prose that merely repeats a scraped/public number is not authoritative.

## Step 2 — fetch, snapshot, and parse the source description

Call `aeko_get_product_description(integration_id, external_product_id)`. Strip only the surrounding tool
fence and bind the enclosed bytes as `existing_html`. Handle token, 404, and upstream failures by releasing
the claim only when the response proves no mutation occurred.

Before any mutating store call, write those exact bytes to
`./aeko-artifacts/<domain_id>/<item_id>/before.html`. Re-read the file and require byte equality, exact length,
and the same `<img` count as `existing_html`; otherwise live refresh is unavailable.

Extract JSON-LD using case-insensitive HTML-attribute parsing that recognizes both double- and single-quoted
`type=application/ld+json`, any attribute order, and whitespace. Parse every block and every `@graph` node.
Abort the live path if any block fails. Also abort when a single-quoted JSON-LD block exists: the current
backend only removes double-quoted blocks and would leave the old node beside the replacement. Never write a
duplicate or contradictory Product entity.

If no JSON-LD exists, release the claim and tell the user this mode refreshes existing aggregate facts; use
normal `/aeko-update-pdp` to prepare initial schema.

## Step 3 — choose the two targets and their authoritative source

Patch only existing `Product.aggregateRating` or standalone `AggregateRating` fields:

- `ratingValue`
- `reviewCount`

Do not touch `review[]`, root Review nodes, offers, price, availability, shipping, returns, or any other
field. Preserve all schema nodes and sibling fields.

New values are eligible only from:

1. Plan fields explicitly identified as current store-authoritative aggregate totals; or
2. values the user copied from the store/review admin and explicitly confirms as the full-product aggregate.

`WebFetch` may show advisory public evidence, but a scraped/cached/widget number never authorizes a live
write. A capped result set, selected review sample, or the first N reviews never supplies `reviewCount` or an
average. If authoritative totals are absent, ask once for both values or cancel—never fabricate.

Apply hard plausibility bounds before preview:

- `ratingValue` is within 0..5 and differs from the existing value by no more than 0.5;
- `reviewCount` is a non-negative integer, never decreases, and increases by no more than
  `max(100, ceil(existing_reviewCount * 0.25))` in one run.

Values outside a bound stop the refresh and require store-admin/AEKO support verification; user confirmation
does not waive the bound. Thus 4.7 → 1.2 and 143 → 3 can never pass.

## Step 4 — build and validate the complete graph

Patch the approved fields in place. Preserve every other field/node, then normalize all parsed nodes into
one object:

```text
json_ld_payload={"@context":"https://schema.org","@graph":[<all preserved and patched nodes>]}
```

Show an exact JSON-Pointer diff, for example:

```text
- /@graph/0/aggregateRating/ratingValue: 4.6 → 4.7
- /@graph/0/aggregateRating/reviewCount: 128 → 143
- all other nodes and fields: preserved
```

Validate JSON parsing, type/identity stability, required AggregateRating siblings, both patch targets, and
zero unapproved removals. Emulate the backend locally: replace the first double-quoted JSON-LD block with
the consolidated payload, remove later double-quoted blocks, and require all bytes outside the original
blocks to equal `existing_html`. This is a content/byte check, not a length-only check.

## Step 5 — confirm, stale-base check, and write once

Show Before / After / Risk / Undo in the user's language:

- exact old/new aggregate totals and complete node diff;
- confirmation that non-JSON-LD bytes remain identical;
- public-page mutation risk and `before.html` recovery path;
- successful revert restores the write-time description and would overwrite merchant edits made afterward.

Require the exact explicit live-update confirmation. Ambiguous replies mean preview only and no store call.
There is no auto-approval carve-out.

After confirmation, call `aeko_get_product_description(integration_id, external_product_id)` again. If its
fenced HTML differs byte-for-byte from `before.html`, stop, rebuild the patch, and require a new preview and
confirmation.

Then call exactly once:

```text
aeko_update_product_page(
  integration_id=integration_id,
  external_product_id=external_product_id,
  action_item_id=item_id,
  execution_claim_id=execution_claim_id,
  json_ld=json_ld_payload,
)
```

This remains one store call and one audit boundary. On confirmed success, fetch the source description again
with `aeko_get_product_description` and compare it to the locally emulated expected result; length alone does
not verify it. Then complete the ActionItem with the returned audit ID and matching claim token.

On a confirmed no-write 4xx, release the claim, surface it, and do not retry. On timeout/5xx, keep the claim
and never retry. Call `aeko_list_store_writes(limit=100, offset=0)` and filter to the exact integration and
product when exposed; the shipped tool has no integration filter parameter, so never invent one. Re-fetch
the exact product with `aeko_get_product_description` for comparison. If audit output cannot prove the exact
integration, reconciliation is inconclusive.

A `failed` audit is not revertible even when the platform may have committed, and the claim pins the original
payload. In that state the item is stuck: do not complete or release it. Tell the user recovery requires the
store admin using `before.html` or AEKO support.

## Step 6 — summary

```text
✔ Aggregate review facts refreshed on <product title or id>
  Platform:      <cafe24 | shopify>
  Audit ID:      <audit_id>
  Changed:       ratingValue and reviewCount only
  Recovery copy: <before.html path>
  Risk:          JSON-LD inside the public store description was replaced
  Undo:          aeko_revert_store_write("<audit_id>") — only after checking for later merchant edits
  Changes:
    - ratingValue: 4.6 → 4.7
    - reviewCount: 128 → 143
```

## What refresh mode never does

- Never writes individual `review[]` or Review bodies.
- Never derives aggregate totals from a capped sample or public-page scrape.
- Never changes non-JSON-LD bytes or an unapproved schema field.
- Never writes from a scheduled/unattended run or without fresh foreground confirmation.
- Never writes without the exact snapshot, stale-base check, claim token, and one-call audit boundary.
- Never retries, releases, or promises normal revert after an ambiguous store response.
