# Store setup mode

Use this when a user wants to onboard AEKO end-to-end through the agent, including custom/AWS-built stores that do not have a Cafe24 or Shopify connector.

Language: mirror the user's chat language for user-facing questions and summaries. Keep tool names, IDs, country codes, product keys, and JSON field names in English/ASCII.

## Tier Contract

Starter can:
- add domains within the Starter domain cap
- add/track prompts within the Starter prompt cap
- use one selected market
- use OpenAI as the allowed AI platform
- connect/sync a store or inject products for a manual/custom store
- list products and perform store-write workflows that the backend allows for active subscriptions

Pro+ is required for:
- Context Reviews / review integrations (connect cre.ma/Judge.me/Cafe24 in the AEKO dashboard — review-source
  credentials are deliberately not accepted by the agent; the only agent-side intake is real-review
  injection through `/aeko-store mode=reviews`)
- Context library grounding
- content recommendations/content-plan generation
- OpenAI Ads marketing workspace
- aeko.shop publishing

If the user asks why a core setup action is blocked for Starter, treat that as a bug or quota issue unless the backend error explicitly says the feature is Pro+.

## Step 1 - Resolve or Add Domain

Call `aeko_list_domains`.

If the user passed `$1` and it looks like a URL, add it with:

```
aeko_add_domain(base_url=<url>, display_name=<optional>, scope=<optional>, ko_name=<optional>)
```

If no domains exist, ask for the store/domain URL and then call `aeko_add_domain`.

If multiple domains exist, show the IDs and ask which one to configure. If one domain exists, auto-select it unless the user supplied a different URL.

After selecting/adding, call `aeko_get_domain_info(domain_id)` and summarize the chosen domain.

## Step 2 - Select Store Path

Ask which path applies:

- Cafe24
- Shopify
- Custom/manual store

For Cafe24/Shopify:
- Ask for `store_identifier` and credentials/tokens only if the user already has them available.
- Call `aeko_connect_store(domain_id, platform, store_identifier, access_token, ...)`.
- Then call `aeko_sync_store(integration_id)` from the returned store.
- If the user does not have credentials, say browser OAuth/dashboard connection is required for now and stop store sync cleanly.

For custom/manual:
- Ask the user for product data or a CSV/table they can paste.
- Never fabricate products.
- Require each product to have:
  - `external_product_id`
  - `title`
  - `product_url`
  - `public_url`
- Recommended optional fields:
  - `description`
  - `price`
  - `currency`
  - `image_url`
  - `status` (`selling` by default)
- Call `aeko_inject_products(domain_id, products)`; the backend creates the manual store internally.

## Step 3 - Verify Products

Call:

```
aeko_list_store_products(domain_id=<domain_id>, include_citability=false, limit=50)
```

Show product count and a compact table:

```
| external_product_id | title | status | public URL |
|---|---|---|---|
```

If zero products return after a sync/inject, stop and explain the likely reason from the tool output.

## Step 4 - Markets

Ask which target markets to monitor.

Starter: choose one market. Pro/Enterprise: multiple markets are allowed within backend limits.

Call:

```
aeko_update_markets(["US"])
```

If the backend rejects the market count, surface that message and ask for a smaller set.

## Step 5 - Quota

Call `aeko_get_quota`.

Summarize:
- tracked prompts used
- remaining tracked prompt slots
- domain/market limits if returned

Do not attempt starter prompt acceptance if quota is already full.

## Step 6 - Starter Prompts

Call:

```
aeko_generate_starter_prompts(domain_id)
```

Show the generated prompts with reason/grade if present. Ask which prompts to accept.

After explicit selection, call `aeko_get_quota` again immediately before acceptance. Reconcile the selected
platform/country fan-out with the fresh remaining capacity; narrow the selection if it no longer fits. Then
call:

```
aeko_accept_starter_prompts(domain_id, selections)
```

Selections must preserve the generated prompt fields the backend expects:
- `raw_prompt`
- `prompt_kind`
- `target_market`
- optional `prompt_en`
- optional score/grade fields
- optional `ai_platforms` / `countries`

For Starter, use one allowed market and OpenAI unless the backend/domain data says otherwise.

## Step 7 - Summary

Print:

```
Setup complete
  Domain: <domain_id> · <base_url>
  Store:  <manual/cafe24/shopify> · <integration_id if known>
  Products available: <count>
  Markets: <markets>
  Starter prompts accepted: <count>

Next:
  /aeko-ai-visibility <domain_id>
  /aeko-manage-prompts mode=discover <domain_id>
```

If the user is Pro+, optionally mention review/Context/ads follow-ups. For Starter, do not pitch Pro+ unless they attempted a Pro+ feature and received a backend gate.

## Never

- Never create fake products or reviews.
- Never ask Starter users to use Context Reviews, Context library, ads, content recommendations, or aeko.shop publishing as a setup prerequisite.
- Never publish content.
- Never store credentials outside the MCP call.
