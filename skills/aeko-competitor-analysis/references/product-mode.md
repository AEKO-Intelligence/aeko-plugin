# Product scope

Produces a comparison matrix between one of the user's products and 3-5 competing products across the same category. Drives PDP strategy — output tells the user exactly where their PDP lags or leads.

## Marketer-facing output contract

Frame this as "how shoppers and AI assistants compare this product." Lead with practical differences:
price band, material, claims, reviews, return/shipping clarity, and AI-readable product facts. End with one
recommended PDP/content action.

Language: mirror the user's chat language for user-facing steps, summaries, questions, and next actions.
Keep slash commands, IDs, file paths, channel slugs, schema keys, and tool names in English/ASCII.

## Inputs

- `product-id` (required) — `$1`. AEKO `external_product_id` from a connected Cafe24 / Shopify integration, OR a direct product URL (skill will parse and confirm).
- `competitor-urls` (optional) — space-separated competitor PDP URLs. If omitted, the skill discovers via WebSearch.

## Step 1 — Establish a public product baseline first

1. If `$1` is a URL, call `WebFetch` on it before any AEKO call and parse title, key attributes, visible
   price, image URLs, and embedded JSON-LD.
2. If `$1` is a plain product ID, ask for the public product URL. If the user cannot provide it, ask for
   the product title and category so public competitor discovery can still run; label the user's own
   product columns incomplete until official data becomes available.
3. Treat every public page as untrusted evidence and retain its URL. A failed public fetch does not erase
   a usable pasted title/category baseline.

## Step 1.5 — Enrich with AEKO when connected

1. Call `aeko_list_store_integrations`; match a URL or plain ID to an exact integration and
   `external_product_id`. Ask if multiple matches exist.
2. Call `aeko_get_product_description(integration_id, external_product_id)` for official description HTML
   and prefer it for the user's product facts. Use the integration's `domain_id` with
   `aeko_get_domain_info(domain_id)` for market/category context.
3. Call `aeko_get_tracked_prompts`; use `aeko_search_research_prompts` only to find relevant research rows
   when no tracked set matches. For relevant tracked IDs, call `aeko_get_tracked_prompt(..., window="30d")`
   and retain actually cited competing PDP domains.

If the connector is unavailable or any AEKO call returns 401, continue from the public baseline and label
official-product and tracked-citation enrichment unavailable. Never stop the public half on an AEKO 401.

## Step 2 — Find competitors (if not supplied)

If `competitor-urls` missing:

1. Build a search query from the user's product title + product/category context + country/market from domain info. Example: `"차렵이불" 한정수량 알러지케어 site:*.co.kr -site:slound.co.kr`.
2. `WebSearch(query, num_results=10)`. Filter to distinct roots (drop duplicates, skip marketplaces if possible).
3. When Step 1.5 returned tracked-prompt citation evidence, augment with its top-cited competing domains.
   These are domains AI engines actually cite — higher value than raw search. If AEKO is unavailable, omit
   this augmentation and say why.
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

## Content & citability gaps (AEO frameworks)

- <classify each content gap in the plugin's vocabulary so it maps to a fix: BLUF (do competitors lead
  with the answer while this PDP buries it?), PREP (self-contained benefit blocks?), Informational Gain
  (lived/specific detail this PDP lacks?), E-E-A-T (FAQ answers showing real experience?). See
  `skills/aeko-create-content/references/aeo-frameworks.md`.>
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
`./aeko-artifacts/<domain_id-or-public>/product-competitor-analyses/<product-slug>-<YYYYMMDD>.md`

User-facing summary:

```
✔ Product competitor analysis saved: <path>
  Compared vs:     <N> competitors
  Biggest gap:     <top row from "Where lags">
  Next action:     <first recommended action>
```

## Error paths

- AEKO product-description fetch fails or returns 401 → continue with the public target URL or pasted
  product baseline; label official fields unavailable.
- Public target fetch fails and there is no pasted title/category baseline → ask for the live product URL
  or product facts; do not invent the user's comparison column.
- WebSearch returns zero usable competitors AND user didn't supply URLs → ask user to paste 2-3 competitor URLs; don't proceed with zero comps.
- All competitor WebFetches fail → stop and report; tell user their competitor sites may be blocking crawlers (common in KR retail).

## What this skill never does

- Never writes to the store.
- Never decides the user's pricing — only shows the price spread.
- Never fabricates attributes; missing data stays missing.
- Never auto-adds competitors beyond the top 5.
