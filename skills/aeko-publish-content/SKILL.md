---
name: aeko-publish-content
description: >
  Interactive publisher and takedown workflow for backend-saved content
  variations. Publishes aeko_shop rows to the public aeko.shop post, creates
  own_store_blog rows as AEKO-owned drafts only, and can unpublish the exact
  item-scoped aeko.shop post. Detects live overwrite risk across every row,
  names the target URL, and requires same-turn human confirmation.
argument-hint: "<item-id>"
allowed-tools: Read, aeko_list_content_variations, aeko_publish_content_variation, aeko_update_content_variation, aeko_unpublish_content, aeko_get_active_brand_package, aeko_get_brand_package_version, aeko_read_brand_package_file, aeko_list_brand_wiki_pages, aeko_get_brand_wiki_page
---

# AEKO Publish Content

Before work, read [the brand execution contract](references/brand-execution-contract.md).
Preserve the exact task prompt and apply only this brand's selected rules, evals, and examples.
Use [the output evaluation rubric](references/brand-output-eval.md) plus the selected brand evals
when checking the exact result; report missing inputs/checks as unavailable.

Publish one backend-saved variation for an exact action `item_id`, or remove that item's aeko.shop post.
Mirror the user's language; keep IDs, URLs, destination slugs, tool names, and commands ASCII.

If invoked from a schedule, routine, cron wrapper, or any context without a present user, stop immediately.
There is no `non_interactive` bypass. Every publish, overwrite, draft creation, and unpublish requires a fresh
same-turn human confirmation after the complete risk block.

## Truth and capability boundaries

- Backend `content_variations` rows—not local artifacts—are the publish source. Their stored title,
  `body_html`/`body_markdown`, and metadata snapshots are sent onward as stored. Product snapshot name,
  price, and availability are **not** re-joined against live store products before publish.
- The list response deliberately omits raw bodies. Say that before confirmation; never imply the human saw
  copy this skill cannot display. Require the user to affirm they reviewed the chosen variation in the
  authoring flow/dashboard.
- `aeko_shop` is a live public post. `own_store_blog` creates/updates an AEKO-owned draft row only and never
  calls Cafe24/Shopify CMS.
- If a required tool is absent from the current session, stop and name it. MCP wrappers return failures as
  strings; do not describe model-side `try/except` or `MethodNotFound` handling.

Require `item-id`. If missing, route to `/aeko-action-center <domain_id> content` or
`/aeko-create-content <item_id>` and stop.

## Step 1 — inspect every relevant row and the live-post state

Call all three, each with `limit=50`:

```text
aeko_list_content_variations(item_id=<item_id>)
aeko_list_content_variations(item_id=<item_id>, destination="aeko_shop", status="published")
aeko_list_content_variations(item_id=<item_id>, destination="own_store_blog", status="published")
```

The destination/status queries prevent a newly saved row from hiding an older published row. Zero rows
stops with `/aeko-create-content <item_id>`. Present selectable saved/failed rows by destination, newest
first, with exact `variation_id`, title, created time, status, and metadata summary. Single-select only.

When **any** aeko.shop row is published, resolve the stored live handle before offering another publish:
call `aeko_publish_content_variation` on that already-published row only. The backend's published-row branch
is an idempotent stored-result lookup and must return its stored `aeko_shop_url` and `post_id` without
rendering. If the row was not already `published`, do not use this lookup. If the URL/post ID is missing or
the lookup fails, block overwrite because the live target cannot be named.

If a selected row itself is already published, offer to show that stored result or enter the unpublish flow;
never pretend re-publishing the same row refreshes the page.

## Step 2 — preview the exact effect

Load this brand's applicable rules/evals before confirmation. A saved row is not proof those
checks passed. The current list API hides raw bodies: do not report a fresh body-level eval
from flags, a title, or an unbound local file. For a required brand check, require an exact-version
validation receipt bound to the selected stored payload or a supported read of that payload.
If neither is available, mark `brand_eval_unverifiable` and stop publication; return to the
authoring flow for a reviewable draft. A user's review affirmation remains required but does
not manufacture an automated validation receipt. Unpublish still follows its separate flow.

Build the plan only from list/lookup responses:

```text
Publish plan
  Variation:       <variation_id> · <title>
  Destination:     <aeko_shop live | own_store_blog AEKO draft>
  Stored body:     HTML=<yes/no> · Markdown=<yes/no>
  Body preview:    unavailable — this MCP release does not expose raw variation bodies
  Hero snapshot:   <yes/no/unknown>
  Requested product snapshots: <metadata count or unknown; not a verified linked count>
```

When the exact requested featured-product count is zero, add:

```text
Catalog side effect
  The publisher will select up to 12 recently updated store products and mark/link them as featured.
  This can change as the catalog changes; a text-only post does not mean zero product links.
```

Offer cancellation and `/aeko-create-content`/draft editing to specify exact products. Do not report this
requested count as the number actually linked: snapshots lacking a name can be dropped, and the publish
response returns no product count. If the requested count is unavailable rather than zero, block publish
until the draft is re-saved with inspectable metadata; never guess whether the 12-product fallback will run.

### First live publish

State that the row becomes a public aeko.shop post and that stored product snapshots may update the public
catalog verbatim. Require both (a) the user says they reviewed the draft and (b) exact confirmation:

```text
PUBLISH <variation_id> TO AEKO.SHOP
```

### Live overwrite

When any row for the item is already live, put this in the confirmation block—not elsewhere:

```text
LIVE OVERWRITE
  Existing URL: <exact aeko_shop_url>
  Existing post ID: <post_id>
  Replacement variation: <variation_id> · <title>
  NO VERSION HISTORY: the prior rendered title, body, hero, slug, and PostProduct links are deleted/
                      overwritten and cannot be recovered through AEKO.
  Body preview unavailable: confirm only if you reviewed this exact variation elsewhere.
```

Require `OVERWRITE <exact_aeko_shop_url> WITH <variation_id>`. A general “yes” is insufficient.

### Own-store draft

State that this writes an AEKO draft, not the live store. Require
`CREATE OWN STORE DRAFT <variation_id>` before the call.

## Step 3 — publish once

Only after the exact same-turn confirmation call:

```text
aeko_publish_content_variation(item_id=<item_id>, variation_id=<variation_id>)
```

The backend row is the payload source, but not an independent truth source for product snapshot fields.
Never fabricate a URL, post ID, draft ID, status, or linked-product count.

## Unpublish — destructive takedown

Use only when the user explicitly asks to remove the exact live post. Start from the tenant-scoped variation
list and stored live-result lookup above. Derive, never accept free-form, `source_content_id` as
`aeko-item:<item_id>`; never unpublish an arbitrary supplied source ID.

Show:

```text
UNPUBLISH PLAN
  Live URL: <exact stored URL>
  Post ID: <post_id>
  Source content ID: aeko-item:<item_id>
  Effect: hides/removes the public aeko.shop post
  Recovery caveat: content_variations.status remains published. Re-publishing the same variation returns
                   the stored (now dead) URL and does not restore the post. Restoration requires saving and
                   publishing a NEW variation for this item.
```

Require `UNPUBLISH aeko-item:<item_id> FROM <exact_url>`, then call
`aeko_unpublish_content(source_content_id="aeko-item:<item_id>", item_id=<item_id>)`. Report only the tool's
result and ask the merchant to verify the URL is no longer public. The backend's missing brand-scope
authorization is a filed security defect; the exact owned-item derivation is an instruction-level
mitigation, not a server guarantee.

## Error handling that matches MCP output

The MCP client now preserves 409/422/429/502/503 labels when the backend does not provide richer detail.
Prefer exact detail text:

- missing tool → stop; reconnect/redeploy the connector, then retry after the tool is present;
- 403/tier detail → aeko.shop requires Pro+; own-store draft does not use that public tier gate;
- 409 `aeko_shop_disabled` → stop and contact support because no self-serve toggle exists;
- 409 inactive publishing-tier detail → the publish route creates/grants entitlement in the same request;
  re-list and retry once. If it repeats, report the exact detail and escalate—do not claim billing ownership;
- 422/missing body or metadata → edit/re-save the draft; do not retry unchanged;
- 429 → wait for the stated window;
- 502 with `Unknown product_source_id` → permanent payload problem; repair exact featured product IDs, do
  not retry unchanged;
- other 502, 500, or network failure → public state may be uncertain because aeko.shop can commit before the
  AEKO response fails. Verify the known URL/storefront before republishing; never say “not recorded”;
- 503/configuration detail → operator deployment issue; do not retry until fixed.

On ambiguous failure, do not claim the variation stayed saved or that the post is absent.

## Success report

For `aeko_shop`, print only structured response values: URL, post ID, variation ID, and status. Print
`Featured products linked: unavailable — publish response does not return a count.` For `own_store_blog`,
print draft ID/variation/status and repeat that it is an AEKO draft only.

## Editing and overwrite semantics

- A saved/failed draft may be edited with `aeko_update_content_variation`; metadata replacement must include
  the complete metadata object. Require a same-turn exact before/after confirmation for that write.
- Published variations are immutable through update. Every variation of one item uses
  `source_content_id=aeko-item:<item_id>`, so publishing a **new** variation overwrites the one live post and
  replaces its title/body/hero/slug and deletes/rebuilds all PostProduct rows.
- Re-publishing the same published variation is a no-op stored-result lookup.
- No version history exists. Save any required prior copy outside this skill before overwrite.

## Never

- Never publishes or unpublishes unattended or from an earlier/synthetic confirmation.
- Never claims the human saw a raw body this MCP cannot return.
- Never calls Cafe24/Shopify live APIs for `own_store_blog`.
- Never fabricates handles/counts or treats requested product snapshots as verified links.
- Never says a failed publish definitely made no public change.
- Never hides the arbitrary-product fallback, overwrite loss, or stale-status behavior after unpublish.
