---
name: aeko-ad-report
description: >
  Generate a client/CMO-ready OpenAI Ads performance report for a domain over a
  date window: top and bottom campaigns / ad groups / ads / products ranked by
  efficiency (CTR, CPC, spend), with plain-language takeaways. Optionally folds in
  AEKO's ORGANIC AI-visibility (mentions/citations across ChatGPT, Claude, Gemini,
  Perplexity) for a paid + organic cross-surface view. Read-only; schedulable.
argument-hint: "[domain-id] [days]"
allowed-tools: aeko_list_domains, aeko_list_campaigns, aeko_list_ad_groups, aeko_list_ads, aeko_get_ad_insights, aeko_get_visibility_summary, aeko_get_score, Write
---

# AEKO Ad Report

A shareable performance report an agency hands a client, or a marketer hands their CMO. Read-only — it
never changes budgets or ads. AEKO's edge: it can show **paid performance and organic AI-visibility in one
report**, which pure ad tools can't.

## Marketer-facing contract

Plain business language, ranked and interpreted — not a raw metric dump. Round money to the account
currency (values arrive in micros = ×1,000,000). Be honest about what's NOT measured.

Language: mirror the user's chat language throughout the report body. Keep IDs/tool names ASCII.

### ROAS / conversions caveat (state this in the report)

Conversion/revenue data is **not yet ingested**, so there is **no ROAS** in this report. Rank on
efficiency proxies: CTR (engagement), CPC (cost efficiency), spend (scale), clicks (volume). Say this
explicitly so no one over-reads the ranking as return-on-spend.

## Inputs

- `domain-id` (optional) — `$1`. Resolve via `aeko_list_domains`.
- `days` (optional) — `$2`. Lookback window in days (default 30). Compute `date_from`/`date_to` as
  ISO dates (YYYY-MM-DD); `date_to` = today, `date_from` = today − days.

## Step 1 — Resolve domain + window

Resolve the domain and compute `date_from` / `date_to`.

## Step 2 — Pull performance (mind the scope rules)

The API does not rank — you rank. **Only `scope=account` works WITHOUT a `scope_id`;
`scope=campaign|ad_group|ad` REQUIRE a `scope_id`, so you must LOOP over listed ids** (there is no
"all campaigns" call). Pull:

- **Account totals**: `aeko_get_ad_insights(scope="account")` — headline spend/impr/clicks.
- **Products (best/worst)**: `aeko_get_ad_insights(scope="account", segment="product")` — one call, no id.
- **Geo (optional)**: `aeko_get_ad_insights(scope="account", segment="country")`.
- **Per campaign**: `aeko_list_campaigns(domain_id)` → for EACH campaign id,
  `aeko_get_ad_insights(scope="campaign", scope_id=<campaign_id>)`.
- **Per ad (top/bottom performers)**: for each campaign → `aeko_list_ad_groups(campaign_id)` → for each
  ad group → `aeko_list_ads(ad_group_id)` → for EACH ad id,
  `aeko_get_ad_insights(scope="ad", scope_id=<ad_id>)`. (Skip this drill-down if the merchant only wants
  campaign-level; it can be many calls on big accounts — say so and cap it.)

Use the `aeko_list_*` responses to turn ids into human names.

## Step 3 — Rank + compute

For each scope, compute per row: CTR = clicks/impressions, CPC = spend/clicks (guard divide-by-zero),
spend in currency. Rank:
- **Top performers**: highest CTR (with meaningful impressions) and lowest CPC.
- **Scale**: highest spend + clicks.
- **Underperformers / waste**: spend with ~0 clicks, or CPC far above the account median.
Skip rows below a minimum-impressions floor (e.g. < 100) as low-signal, and say you did.

## Step 4 — (Optional) organic cross-surface layer

If the user wants the full picture (or by default for a CMO report), add an **AI-visibility** section:
- `aeko_get_score(domain_id)` — the AEKO Score + grade + components.
- `aeko_get_visibility_summary(domain_id)` — mentions/citations across ChatGPT/Claude/Gemini/Perplexity.
Frame the cross-surface insight, e.g. "Product X wins organically on '민감성' but its paid CTR is low —
worth stronger creative," or "high organic visibility, no ads yet — a proven-winner to promote."

## Step 5 — Compose the report

`Write` a Markdown file (e.g. `aeko-ad-report-<domain>-<date_to>.md`) with:
```
# AEKO Ad Report — <domain>  (<date_from> → <date_to>)

## Summary
- Spend: <total>  ·  Impressions: <n>  ·  Clicks: <n>  ·  Avg CTR: <x%>  ·  Avg CPC: <cur>
- Headline: <one-sentence takeaway>

## Top campaigns / ad groups
| Name | Spend | Impr | Clicks | CTR | CPC |
...

## Top & bottom ads
Winners: ...   |   Underperformers (candidates to pause): ...

## Best / worst products
...

## (optional) Organic AI-visibility
AEKO Score <n>/<grade>; mentions/citations by engine; cross-surface takeaways.

## Recommendations
- Scale: ...   Fix: ...   Pause: ...   (actionable, tied to the numbers)

_Note: ranking uses efficiency proxies (CTR/CPC/spend). Conversion/ROAS data is not yet available._
```

## Step 6 — Deliver

Tell the user the file path and give a 3–5 bullet verbal summary of the biggest findings + recommended
next actions (which map to `/aeko-optimize-budget` for budget moves).

## Scheduling note

Read-only and safe to run on cadence:
```
/schedule every Monday 9am /aeko-ad-report <domain-id> 7
```
(On Claude Code the ScheduleWakeup / CronCreate tools back `/schedule`; other hosts may vary.)

## Error paths

- No connected ad account / no data in window → say so plainly; still emit the organic section if requested.
- Insights error (under-tier, account issue) → surface verbatim; report what you could gather.

## What this skill never does

- Never changes budgets, ads, or campaign state (read-only — that's `/aeko-optimize-budget`).
- Never reports ROAS/revenue (not measured yet) — only efficiency proxies, clearly labeled.
- Never invents numbers — every figure traces to an `aeko_get_ad_insights` row.
