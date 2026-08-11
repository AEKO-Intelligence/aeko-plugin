---
name: aeko-openai-budget-shift
description: >
  Account-gated AEKO workflow that rebalances OpenAI Ads campaign budgets toward better-performing campaigns, and
  pause clearly wasteful campaigns, ad groups, or ads. Pulls performance over a window, proposes a
  reallocation proportional to efficiency (CTR/CPC/spend — ROAS not yet available),
  ALWAYS previews as a dry run first, and only writes after explicit confirmation
  within strict guardrails. Unattended runs stage a plan only and never write.
argument-hint: "[domain-id] [days]"
allowed-tools: aeko_list_domains, aeko_list_campaigns, aeko_list_ad_groups, aeko_get_ad_insights, aeko_update_campaign_budget, aeko_list_ads, aeko_set_campaign_state, aeko_set_ad_group_state, aeko_set_ad_state
---

# AEKO OpenAI Budget Shift

Shift budget from weaker to stronger campaigns and stop obvious waste. **This tool spends real money**, so
it is deliberately conservative: dry-run first, tight caps, explicit confirmation, and a revert snapshot.
It operates OpenAI Ads through AEKO only; it never claims to change Meta, TikTok, or Google Ads.

## Spend-safety contract (read first)

- Budget lives at the **campaign** level (the lowest lever; ad groups only carry bidding).
- **Always dry-run before writing.** `aeko_update_campaign_budget` defaults to `dry_run=True` and also
  enforces guards at the tool layer (floor, ceiling, max delta) — treat those as a backstop, not the plan.
- **Never** apply a change without showing the full before→after diff and getting fresh explicit confirmation.
- **Unattended runs only stage.** They may collect metrics, compute proposals, and call budget updates with
  `dry_run=True`; they must never call a budget write with `dry_run=False`, change campaign/ad-group/ad
  state, resume spend, or treat a schedule wrapper as confirmation.
- **ROAS caveat:** conversions/revenue aren't ingested, so optimize on **efficiency proxies** only
  (CTR, CPC, spend, clicks). Do not claim ROAS-based optimization.

Language: mirror the user's chat language for the plan, diff, and confirmation. Keep IDs/tool names ASCII.

## Inputs

- `domain-id` (optional) — `$1`. Resolve via `aeko_list_domains`.
- `days` (optional) — `$2`. Lookback window (default 14). Compute ISO `date_from`/`date_to`.

## Step 1 — Resolve domain, current budgets, performance

1. Resolve the domain.
2. `aeko_list_campaigns(domain_id)` → current `lifetime_spend_limit_micros` per active campaign (record as
   each campaign's `current_budget_micros`).
3. Per-campaign performance: `scope="campaign"` REQUIRES a `scope_id`, so **loop** — for EACH campaign id
   call `aeko_get_ad_insights(domain_id, scope="campaign", scope_id=<campaign_id>, date_from, date_to)`
   → impressions, clicks, spend, CTR, CPC over the window. (There is no "all campaigns" call.)

## Step 2 — Score + propose a reallocation

- Compute an **efficiency score** per campaign from the proxies (e.g. normalize CTR up + CPC down, weight
  by clicks so low-signal campaigns don't dominate). Skip campaigns below a minimum-impressions floor
  (e.g. < 500) — mark them "low signal, unchanged."
- Keep the **total budget constant** unless the user explicitly wants to raise/lower it. Redistribute the
  pool toward higher-efficiency campaigns and away from lower ones, **proportional** to score.
- Apply skill-side caps on the proposal:
  - per-campaign change ≤ **25%** of its current budget per run (`max_delta_pct=25`);
  - never below the floor (1,000,000 micros);
  - an absolute per-campaign ceiling (`max_budget_micros`) — default to e.g. 2× current or a value the user
    sets; never balloon a single campaign.

## Step 3 — Dry-run each proposed change

For every campaign you want to change, call:
```
aeko_update_campaign_budget(
    campaign_id, proposed_micros, idempotency_key=<stable>,
    dry_run=True,
    current_budget_micros=<current>, max_budget_micros=<ceiling>, max_delta_pct=25,
)
```
Collect the previews. If the tool REJECTS a change (over ceiling/delta/floor), adjust the proposal down —
do not fight the guard.

## Step 4 — Preview the full plan + confirm

Show one diff table:
```
Reallocation (window <date_from>→<date_to>, efficiency-weighted, total budget held constant)
Campaign         CTR    CPC     Spend    Budget now → proposed      Δ
A (strong)       2.1%   ₩180    ₩90k     ₩200k → ₩250k             +25%
B (weak)         0.4%   ₩520    ₩60k     ₩200k → ₩150k             −25%
C (low signal)   —      —       ₩2k      ₩100k → ₩100k (unchanged)
```
Get explicit confirmation. **Record the current budgets now** — they go in the summary as the revert path.

## Step 5 — Apply (only on confirm)

For each confirmed change, re-call `aeko_update_campaign_budget(..., dry_run=False, ...)` with the **same
stable `idempotency_key`** you used in the dry run (reuse on any retry so a re-run never double-applies).

## Step 6 — (Optional) waste-cutting across all three hierarchy levels

If asked to also trim waste:
1. Enumerate the hierarchy with `aeko_list_campaigns(domain_id)` →
   `aeko_list_ad_groups(campaign_id)` → `aeko_list_ads(ad_group_id)`. For each candidate, call
   `aeko_get_ad_insights` with the matching required pair:
   - campaign: `scope="campaign", scope_id=<campaign_id>`;
   - ad group: `scope="ad_group", scope_id=<ad_group_id>`;
   - ad: `scope="ad", scope_id=<ad_id>`.
   Find entities with meaningful spend but ~0 clicks or CPC far above the account median. Cap large-account
   drill-downs and disclose the cap.
2. Present separate campaign, ad-group, and ad rows with exact IDs, evidence, and effect. Get explicit
   confirmation for the displayed set, then use the matching reversible pause call:
   - `aeko_set_campaign_state(campaign_id, "pause", idempotency_key=<stable>)`;
   - `aeko_set_ad_group_state(ad_group_id, "pause", idempotency_key=<stable>)`;
   - `aeko_set_ad_state(ad_id, "pause", idempotency_key=<stable>)`.
   Never archive here.
3. Never resume any hierarchy level automatically. If the user explicitly asks to restart spend, restate
   the exact campaign/ad-group/ad IDs, show that spend can restart, obtain a fresh confirmation, and call
   only the matching state tool with `action="active"` and `confirm_active=True`.

## Step 7 — Summary (with revert path)

```
✔ Budget rebalanced — <k> campaigns changed, total budget held at <total>
  A: ₩200k → ₩250k   B: ₩200k → ₩150k   (unchanged: C)
  Paused: <campaign n> campaigns · <group n> ad groups · <ad n> ads (waste-cut)
  Revert: set budgets back with aeko_update_campaign_budget(<campaign>, <original_micros>, ...):
    A ← ₩200k   B ← ₩200k
  Re-activate paused campaigns, ad groups, or ads only after explicit spend-restart confirmation (`confirm_active=True`).
  Measure the effect with /aeko-openai-ads-reporting in ~1 week.
```

## Scheduling note

An unattended schedule may generate a staged dry-run plan only:
```
/schedule every Monday 8am /aeko-openai-budget-shift <domain-id> 7
```
It may use conservative `max_delta_pct` and `max_budget_micros` values to validate the proposal, but it must
not apply it or pause/resume anything. A later interactive run must re-fetch current budgets/performance,
dry-run again, show the new diff, and obtain fresh explicit confirmation before any write. Host scheduling
support varies.

## Error paths

- No connected ad account / no active campaigns → stop; nothing to optimize.
- No performance data in window → stop; recommend widening `days` or waiting for spend to accumulate.
- A write is rejected by the tool guard → keep the guard; lower the proposal; never bypass by raising caps
  silently — surface it to the user.

## What this skill never does

- Never writes a budget without an interactive dry-run + fresh explicit confirmation.
- Never writes or changes entity state unattended; unattended output is a staged plan only.
- Never exceeds the per-run delta cap or a campaign's ceiling; never drops below the floor.
- Never skips the ad-group middle rung, never archives campaigns/ad groups/ads (only reversible `pause`),
  and never claims ROAS-based decisions.
