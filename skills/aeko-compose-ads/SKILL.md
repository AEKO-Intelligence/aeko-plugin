---
name: aeko-compose-ads
description: >
  Compose flexible, cross-product OpenAI Ads ad groups from a store's contextual
  reviews. Pulls every contextual review across the domain, clusters them by a
  shared shopper-situation facet (e.g. several products all matching '민감성 피부'
  or occasion '선물'), composes ONE broader context-hint set per cluster, and creates
  an ad group with one ad per product — all PAUSED for review. This is the agentic
  step beyond the dashboard's one-review→one-ad flow.
argument-hint: "[domain-id] [min-score]"
allowed-tools: aeko_list_domains, aeko_list_contextual_reviews, aeko_list_campaigns, aeko_create_ad_group_from_context
---

# AEKO Compose Ads

Turn the review pool into broader, cross-product ad groups. The dashboard does one review → one ad group;
here you *cluster* reviews so a single ad group with a broader hint carries several products' ads.

## Marketer-facing contract

This creates real ad structures in the merchant's OpenAI Ads account (PAUSED — nothing spends until the
merchant activates them in the dashboard/Ads Manager). Always show a **preview** (clusters → hint → products)
and get confirmation before creating. Explain hints as "the shopper need this ad group targets," not
"context_hints."

Language: mirror the user's chat language for questions, previews, summaries. Keep IDs, tool names, and the
composed `context_hints` themselves in the target market's language (they are ad-targeting phrases).

## Inputs

- `domain-id` (optional) — `$1`. Resolve via `aeko_list_domains` if missing.
- `min-score` (optional) — `$2`. Contextual-score floor (default 70). Higher = stronger narratives only.

## Step 1 — Resolve domain + pull the review pool

1. Resolve the domain.
2. Call `aeko_list_contextual_reviews(domain_id, min_context_score=<min-score>, limit=200)`. It returns a
   structured JSON list: each item has `review_id`, `store_product_id`, `external_product_ref`,
   `product_title`, `context_score`, the pre-purchase facets (`customer_state`, `recent_concern`, `occasion`,
   `recipient`, `product_experience`), and precomputed `ad_body` / `ad_context_hints`.
3. If empty → tell the user there are no contextual reviews yet (connect a review source or run
   `/aeko-inject-reviews`, then wait for classification). Stop.

## Step 2 — Cluster by shared shopper situation

Group the reviews by a **shared pre-purchase facet** that spans multiple products. Good clustering axes:
- a shared `customer_state` — e.g. `민감성 피부`, `수분부족형 지성`;
- a shared `recent_concern` — e.g. `모공 관리`, `트러블 진정`;
- a shared `occasion` — e.g. `선물`, `여행`, `계절` (seasonal campaigns);
- a shared `recipient` — e.g. `친구 선물`, `엄마 선물`.

A cluster is worth an ad group when it spans **2+ distinct products** (or is a strong single-product theme
the merchant asked for). Aim for a handful of tight clusters, not one giant bucket. Reviews can appear in
only one cluster — pick the strongest axis for each.

## Step 3 — Compose each cluster into an ad group spec

For each cluster:
- **context_hints** — compose 1–3 SHORT, BROADER pre-purchase seeker phrases that fit ALL products in the
  cluster, in the market language. Broaden past any single review: e.g. mask-pack '자극 없이 순했어요' + serum
  '여름에 끈적임 없이' both grounding on 민감성 → hint `["민감성 피부에 좋은 제품"]`. NEVER use a felt-effect /
  after-state ("피부가 좋아졌어요") as a hint — that describes someone who already bought.
- **ads** — one ad per DISTINCT product in the cluster: `{ store_product_id, source_review_id }`. Leave
  `title`/`body` out to let the backend compose clean creative from that product's review, OR pass a
  `body` you adapted from the product's precomputed `ad_body`. Deduplicate by `store_product_id` (one ad
  per product per group).
- **ad_group_name** — a short human label, e.g. `민감성 피부 - 재생 라인`.

## Step 4 — Choose placement

Ask (or infer): put these ad groups under an EXISTING campaign or a NEW one?
- Existing → call `aeko_list_campaigns(domain_id)`, let the user pick a `campaign_id`.
- New → ask for a campaign name and a lifetime budget in the account currency; convert to micros
  (×1,000,000) for `new_campaign_budget_micros` (min 1,000,000 = 1 unit).

## Step 5 — Preview + confirm

Show a table the merchant can approve:
```
Cluster: 민감성 피부에 좋은 제품
  Hint(s): 민감성 피부에 좋은 제품
  Products (3): 수분 세럼 / 진정 마스크팩 / 재생 크림
Cluster: 친구 선물로 좋은 제품
  Hint(s): 친구 선물로 좋은 스킨케어
  Products (2): 재생 크림 / 립밤
Placement: new campaign "AEKO 컨텍스트 캠페인", budget 300,000 KRW
All ad groups + ads are created PAUSED.
```
Get explicit confirmation (schedule wrappers may auto-approve).

## Step 6 — Create (paused)

For each cluster, call:
```
aeko_create_ad_group_from_context(
    domain_id,
    ad_group_name=<cluster name>,
    context_hints=<composed hints>,
    ads=[{store_product_id, source_review_id}, ...],
    idempotency_key=<stable key>,          # e.g. "compose:<domain_id>:<cluster-slug>" — REUSE on retry
    campaign_id=<id>  OR  new_campaign_name=<name>, new_campaign_budget_micros=<micros>,
)
```
Use a **stable** `idempotency_key` per cluster (reuse the same value if you retry) so a re-run never
double-creates. If placing several clusters in one NEW campaign, create the first with `new_campaign_*`,
then read back the returned `campaign.id` and use `campaign_id=` for the rest so they share the campaign.

## Step 7 — Summary

```
✔ Composed <N> ad groups (<M> product ads) — all PAUSED
  Campaign: <name / id>
  <cluster>: hint "<hint>" → <k> products
  ...
  Next: review + activate in the AEKO dashboard (광고 성과) or OpenAI Ads Manager.
        Measure with /aeko-ad-report; rebalance budget with /aeko-optimize-budget.
```

## Error paths

- No contextual reviews → stop with guidance (inject/connect + wait for classification).
- A cluster's products don't resolve to `store_product_id` → skip that ad, note it.
- `aeko_create_ad_group_from_context` returns an error (e.g. no connected ad account, under-tier) →
  surface it verbatim; do not retry with a new idempotency_key.

## What this skill never does

- Never activates ads — everything is created paused for human review.
- Never uses a felt-effect / after-state as a targeting hint.
- Never invents products or reviews — it only composes from the returned contextual-review pool.
