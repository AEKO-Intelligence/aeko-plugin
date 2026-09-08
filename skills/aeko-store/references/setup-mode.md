# Store setup mode

Use this for AEKO domain setup, a dashboard-connected store sync, or a credential-less manual catalog.
Mirror the user's language; keep tool names, IDs, country codes, platform values, and JSON keys ASCII.

## Tier and safety contract

Starter may add a domain, maintain a manual catalog, select one market, and accept prompts within quota.
Pro+ is required for review injection/integrations, Context, content recommendations, OpenAI Ads, and
aeko.shop publishing. Backend errors remain authoritative.

This is foreground-only. Stop if invoked from a schedule, routine, cron wrapper, or without a present user.
Never ask for an OAuth/access/refresh token: Cafe24/Shopify connection is dashboard-only because secrets must
not traverse an agent transcript. Store sync is not a private import. It republishes the active catalog and
eligible reviews to the merchant's public aeko.shop storefront and revalidates public discovery surfaces.

## Step 1 — resolve or add the domain

Call `aeko_list_domains`. Resolve an exact existing ID, or ask for the URL and call `aeko_add_domain` after a
fresh same-turn confirmation. Then call `aeko_get_domain_info(domain_id)` and show the selected domain.

## Step 2 — select the store path

Ask whether the store is Cafe24, Shopify, or custom/manual.

### Cafe24 or Shopify

Never request or accept credentials in chat and never call `aeko_connect_store`. Direct the merchant to AEKO
dashboard → Settings → Store Integrations to complete OAuth. After they say it is connected, call
`aeko_list_store_integrations`, match both exact `domain_id` and platform/store identifier, and show the
integration. If none matches, stop with the dashboard connection step.

Before `aeko_sync_store`, show this risk block:

```text
Public sync
  Integration: <integration_id> · <platform/store_identifier>
  Becomes public: every active product (name, price, image, availability, outbound URL)
                  and every eligible review, including agent-injected reviews
  Public surfaces: aeko.shop brand/catalog pages, sitemap.xml, llms.txt, and feed.rss
  Replacement risk: this is a full public snapshot replacement. If the upstream fetch is partial,
                    products omitted from that response can be deleted from the live public catalog.
```

Require the exact fresh phrase `SYNC PUBLIC STOREFRONT <integration_id>` or the natural Korean equivalent
retaining the exact ASCII integration ID. No earlier request or general setup confirmation counts. Then call
`aeko_sync_store(integration_id)` once.

Immediately call `aeko_list_store_integrations` again. Require `last_sync_status` and inspect
`last_sync_error_message`:

- success/complete → continue;
- `partial_failure`, partial, failed, missing, or unknown → stop. State that the public catalog may already be incomplete,
  quote the error, tell the merchant to inspect aeko.shop, and reconnect/escalate the upstream store before
  another sync. Never print “Setup complete.”

### Custom/manual

Ask for a pasted CSV/table with `external_product_id`, `title`, `product_url`, and `public_url`; optional
fields are `description`, `price`, `currency`, `image_url`, and `status`. Never fabricate a row. Preview exact
insert/update counts and require same-turn confirmation before `aeko_inject_products`. Read the returned
`errors` and `batches_completed`; a partial batch result is not complete setup.

## Step 3 — verify products without inventing a total

Call:

```text
aeko_list_store_products(domain_id=<domain_id>, include_citability=false, limit=500, offset=0)
```

The endpoint returns a bare capped list, not a total. Do not page indefinitely. If fewer than 500 rows
return, report that observed count. If 500 return, report `500+ visible (listing capped; total unavailable)`.
Show a compact exact-ID table. Zero rows stops setup; a partial sync stops even when rows are nonzero.

## Step 4 — replace account markets only after a diff

Markets are account-wide, not domain-scoped, and `aeko_update_markets` replaces the whole list. Call
`aeko_get_current_markets`, then show:

```text
Account markets
  Before: <exact selected_markets>
  After:  <complete proposed list>
  Removed: <values removed or none>
  Added:   <values added or none>
  Effect: prompt fan-out for every domain uses this account list
```

Require `REPLACE ACCOUNT MARKETS <comma-separated-complete-list>` or a Korean equivalent retaining the
complete ASCII list. Never send only a newly requested market unless it is intentionally the full final
list. Re-fetch with `aeko_get_current_markets` and verify after the update.

## Step 5 — quota and starter prompts

Call `aeko_get_quota`; do not offer acceptance when full. Generate starter prompts, show the proposals, and
ask which to accept. The generate response uses `prompt_text`; map `prompt_text` to `raw_prompt` **verbatim**
for `aeko_accept_starter_prompts`, while preserving `prompt_kind`, `target_market`, and optional fields.

Immediately re-fetch quota, reconcile platform/country fan-out, show the exact selection, and require a
same-turn confirmation. After acceptance, read the response's `limit_blocked`, `failed`, accepted/tracked
aggregates, and per-row errors. Never infer accepted count from the requested selection count.

## Summary and error paths

Print `Setup complete` only when every requested stage is verified. A capped catalog count carries `+`; a
partial store sync or batch injection is explicitly incomplete. Include the exact domain, integration/path,
observed product count, account market before/after, and verified starter-prompt aggregates.

Never create fake products/reviews, accept secrets, hide public-sync effects, call a token connect tool,
describe a partial sync as success, or claim this mode never publishes.
