# Real-review intake mode

Feed real reviews into the pipeline for merchants who don't use a review app. Injected reviews are
classified automatically (context facets — 고객 상태 / 최근 고민 / 상황 / 대상 / 제품 경험 — plus a precomputed
ad creative), so they immediately power `/aeko-openai-compose-ads`, content, and tracked prompts.

This is the only review intake an agent has. Credentialed cre.ma, Judge.me, Cafe24, and other review-source
connections are dashboard-only; never ask for those credentials or imply this mode can connect them.

## Non-negotiable: real reviews only

This skill is an **intake mechanism, never a review generator.** Every injected review MUST be a real
statement a real customer made. Do not invent, embellish, paraphrase into a "better" review, or merge
several into one. If you cannot find genuine reviews, say so and stop. Fabricated reviews violate AEKO's
anti-manipulation rule and also score low at classification (they get filtered by the ≥60 contextual gate),
so they help no one.

Language: mirror the user's chat language for questions, summaries, and risk copy. Keep IDs, tool names,
`external_product_ref`, and JSON keys in English/ASCII.

## Inputs

- `domain-id` (optional) — `$1`. If missing, call `aeko_list_domains`; one → auto-pick, multiple → ask.

## Step 1 — Resolve domain + confirm a store is connected

1. Resolve the domain (`$1` or `aeko_list_domains`).
2. Call `aeko_list_store_integrations`. Injection binds reviews to **selling store products**, so a store
   integration (including the manual store created by product injection) must exist. If none → stop; tell
   the user to run `/aeko-store mode=setup`, because reviews can only attach to real products.
3. Call `aeko_list_store_products(domain_id=<domain_id>, limit=200, offset=0, sort="synced_desc")` and show
   selling products with exact `external_product_id` values. Page as needed; do not guess from a title.

## Step 2 — Pick a product + method

1. **Get the product's `external_product_ref`** — select the store's exact external product id from Step 1,
   such as Cafe24 `product_no` or a Shopify product id. If the catalog scan was capped or unavailable, ask
   the merchant for the exact ID or derive it from a supplied store product URL and confirm it. Injection
   binds by this ref; never guess it.
2. Ask the user which method (or infer from what they gave you):
   - **merchant-paste** — the user pastes review text / a CSV / a screenshot. `Read` a file if they point
     to one. Extract each distinct review's text, rating (if shown), author (if shown).
   - **agent-gather** — use `WebSearch` + `WebFetch` to find genuine customer reviews for this product on
     public sources (Coupang / Naver Smartstore / marketplace review sections, Naver blog·cafe, YouTube
     comments). Only keep reviews that are clearly real customer statements with a locatable source URL.

## Step 3 — Normalize each review

For every review, build a record:
- `external_review_id` — a **stable, deterministic** id you derive so re-running is idempotent. Use
  `sha256(source_url + "\n" + body)` (hex). For merchant-paste with no URL, use `sha256("paste:" + body)`.
- `external_product_ref` — the product it belongs to (from Step 2).
- `body` — the verbatim review text (required). Do not rewrite it.
- `rating` (1–5 if known), `title`, `author_name`, `lang` (e.g. `ko`), `review_created_at` (ISO8601 if known).
- `source_url` — the page you found it on (agent-gather) — required for provenance when gathered.
- `source_method` — `"web_gather"` or `"merchant_paste"`.

Drop anything you cannot verify as a real review. Deduplicate by `external_review_id`.

## Step 4 — Preview, then inject

Show the user a short preview: N reviews, which product, and the method + sources. Get a go-ahead
(skip the confirm only when running unattended via a schedule wrapper).

Call `aeko_inject_reviews(domain_id, reviews)` with the normalized list. The response reports
`inserted`, `updated`, `skipped_unmatched`, and `unmatched_refs`.

## Step 5 — Report

```
✔ Injected reviews for <product>
  Source:    <web_gather | merchant_paste>  (<n sources>)
  Inserted:  <inserted>   Updated: <updated>   Skipped (no matching product): <skipped_unmatched>
  Unmatched refs: <unmatched_refs or none>
  Next:      classification runs automatically — context facets + ad creative populate in a few minutes,
             then run /aeko-openai-compose-ads or check the Context tab.
```

If `skipped_unmatched > 0`, explain the `external_product_ref` didn't match a selling product — the user
should confirm the product id or that the product is currently selling.

## Error paths

- No store connected → stop (can't bind reviews to products).
- No genuine reviews found (agent-gather) → say so; do NOT fabricate; stop.
- All refs unmatched → stop; surface the unmatched refs and ask the user to confirm the product id.

## What this skill never does

- Never invents, rewrites, or embellishes a review — real customer statements only.
- Never injects a review it can't tie to a real source (URL) or the merchant didn't actually provide.
- Never attaches reviews to a product that isn't currently selling.
