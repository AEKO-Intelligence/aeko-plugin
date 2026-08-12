# Real-review intake mode

Inject verified customer statements into AEKO's credential-less manual review source. This is an intake
mechanism, never a review generator. Never invent, embellish, merge, or “improve” a review. Drop anything
whose authenticity cannot be verified; stop when no real reviews remain.

This flow is Pro+ and foreground-only. Stop before gathering when the tier preflight fails, or when invoked
from a schedule, routine, cron wrapper, or context without a present user. No unattended confirmation waiver
exists.

The contextual classifier measures richness, **not authenticity**. Dense fabricated copy may score higher
than a real one-line review, so classification is not an anti-fabrication backstop. `source_url` and
`source_method` are optional free text in the backend and are not fetched or validated; this skill's evidence
checks are instruction-level controls.

## Step 1 — preflight tier, sources, and products

1. Resolve the exact domain.
2. Call `aeko_list_review_integrations(domain_id)` first. Its Pro+ gate is the tier preflight. On a 403, stop
   before gathering and explain that manual injection also requires Pro+.
3. If any credentialed integration exists (`platform != manual`), stop manual injection. The same review may
   already be imported under that integration, while backend dedupe is integration-scoped; injecting it
   again under `manual` would create a second public review. Tell the merchant to sync/manage that source in
   the dashboard instead.
4. Call `aeko_list_store_integrations` and require an exact integration for the domain.
5. Call `aeko_list_store_products(domain_id=<domain_id>, limit=500, offset=0, sort="synced_desc")`. Do not
   page a bare list indefinitely. Fewer than 500 rows is the observed set; exactly 500 is a capped set, so
   require the merchant's exact `external_product_ref` or derive it from a supplied product URL and confirm.
   Never guess from title.

## Step 2 — collect real evidence

- `merchant-paste`: preserve verbatim text from the user's paste/file/screenshot plus rating, author, and
  date only when visible. A source URL is optional because the merchant is the source.
- `agent-gather`: retain only a literal customer statement with a locatable public URL. Store copy,
  influencer copy, product descriptions, and model summaries are not reviews.

For each record keep verbatim `body`, exact `external_product_ref`, observed optional fields, `source_url`,
and `source_method` (`web_gather` or `merchant_paste`). Never infer authenticity from prose quality.

## Step 3 — deterministic IDs whose identity does not depend on a volatile URL

For a gathered review, prefer a native review/comment ID and compute
`sha256("web:" + platform + "\n" + native_id + "\n" + external_product_ref)`. If no native ID exists,
compute `sha256("web-fallback:\n" + normalized_verbatim_body + "\n" + author + "\n" + observed_date +
"\n" + external_product_ref)`. Keep the canonicalized URL as provenance, not as the identity input; strip
tracking parameters and fragments.

For merchant paste, compute `sha256("paste:\n" + normalized_verbatim_body + "\n" +
external_product_ref)`. Normalize only whitespace/Unicode for hashing; never change the stored verbatim body.
Deduplicate the proposed batch by this ID.

## Step 4 — preview and same-turn confirmation

Show exact product ID, source/method, each verbatim excerpt, and counts. State plainly:

- the backend does not authenticate the source URL;
- injected rows use the manual integration and may become public on a later `aeko_sync_store` when they meet
  the public eligibility threshold;
- this flow is blocked when a credentialed source exists to avoid duplicate public reviews.

Require `INJECT <N> VERIFIED REVIEWS FOR <external_product_ref>` or a Korean equivalent retaining exact
ASCII values. Anything else means no call. Then call `aeko_inject_reviews` once.

## Step 5 — report actual aggregates

Read `inserted`, `updated`, `skipped_unmatched`, `unmatched_refs`, `batches_completed`, total `batches`, and
`errors` from the returned result. Do not print requested count as inserted. Any error, unfinished batch, or
unmatched ref is partial and must be named; all-unmatched stops. Classification may run afterward, but never
describe its score as proof a review is real.

Never attach to a non-selling product, fabricate, title-match an ID, bypass tier/confirmation, or inject when
a credentialed review integration already covers the domain.
