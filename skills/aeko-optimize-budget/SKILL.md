---
name: aeko-optimize-budget
description: >
  Rebalance OpenAI Ads campaign budgets toward better-performing campaigns, and
  pause clearly wasteful ads. Pulls performance over a window, proposes a
  reallocation proportional to efficiency (CTR/CPC/spend — ROAS not yet available),
  ALWAYS previews as a dry run first, and only writes after explicit confirmation
  within strict guardrails. Schedulable, but spend-safety is the headline.
argument-hint: "[domain-id] [days]"
allowed-tools: aeko_list_domains, aeko_list_campaigns, aeko_list_ad_groups, aeko_get_ad_insights, aeko_update_campaign_budget, aeko_list_ads, aeko_set_campaign_state, aeko_set_ad_state
---

# AEKO Optimize Budget

Shift budget from weaker to stronger campaigns and stop obvious waste. **This tool spends real money**, so
it is deliberately conservative: dry-run first, tight caps, explicit confirmation, and a revert snapshot.

## Spend-safety contract (read first)

- Budget lives at the **campaign** level (the lowest lever; ad groups only carry bidding).
- **Always dry-run before writing.** `aeko_update_campaign_budget` defaults to `dry_run=True` and also
  enforces guards at the tool layer (floor, ceiling, max delta) — treat those as a backstop, not the plan.
- **Never** apply a change without showing the full before→after diff and getting explicit confirmation
  (a `/schedule` wrapper may pre-authorize, but then the caps below MUST be set and conservative).
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

## Step 6 — (Optional) waste-cutting: pause dead ads

If asked to also trim waste:
1. `scope="ad"` REQUIRES a `scope_id`, so enumerate ads and loop: `aeko_list_ad_groups(campaign_id)` →
   `aeko_list_ads(ad_group_id)` → for EACH ad id call
   `aeko_get_ad_insights(domain_id, scope="ad", scope_id=<ad_id>, date_from, date_to)`. Find ads with
   meaningful spend but ~0 clicks (or CPC far above the account median). (Cap the drill-down on large
   accounts and say so.)
2. Present them; on confirmation, `aeko_set_ad_state(ad_id, "pause", idempotency_key=<stable>)` each.
   Pausing is reversible in the dashboard; never archive here.
3. Never resume campaigns or ads automatically. If the user explicitly asks to restart spend, restate the
   campaign/ad ids and call the state tool only after confirmation with `confirm_active=True`.

## Step 7 — Summary (with revert path)

```
✔ Budget rebalanced — <k> campaigns changed, total budget held at <total>
  A: ₩200k → ₩250k   B: ₩200k → ₩150k   (unchanged: C)
  Paused ads: <n> (waste-cut)
  Revert: set budgets back with aeko_update_campaign_budget(<campaign>, <original_micros>, ...):
    A ← ₩200k   B ← ₩200k
  Re-activate paused ads only after explicit spend-restart confirmation (`confirm_active=True`).
  Measure the effect with /aeko-ad-report in ~1 week.
```

## Scheduling note

Can run weekly, but only with conservative caps pre-set (it writes budgets):
```
/schedule every Monday 8am /aeko-optimize-budget <domain-id> 7
```
For unattended runs, keep `max_delta_pct` small and set a real `max_budget_micros` per campaign.
(On Claude Code the ScheduleWakeup / CronCreate tools back `/schedule`; other hosts may vary.)

## Error paths

- No connected ad account / no active campaigns → stop; nothing to optimize.
- No performance data in window → stop; recommend widening `days` or waiting for spend to accumulate.
- A write is rejected by the tool guard → keep the guard; lower the proposal; never bypass by raising caps
  silently — surface it to the user.

## What this skill never does

- Never writes a budget without a dry-run + explicit confirmation (schedule wrappers must set caps).
- Never exceeds the per-run delta cap or a campaign's ceiling; never drops below the floor.
- Never archives campaigns/ads (only reversible `pause`); never claims ROAS-based decisions.
