---
name: aeko-openai-budget-shift
description: >
  Account-gated AEKO workflow, read-only for budgets, that reads OpenAI Ads campaign
  performance and recommends budget shifts: a ranked list of from → to moves with amounts, reasoning, and
  risks, which the merchant applies in the AEKO dashboard. It never changes a budget;
  AEKO campaign budgets are set only in the dashboard. Scores efficiency proxies
  (CTR/CPC/spend; ROAS not available). Optional waste-cutting pauses clearly wasteful
  campaigns, ad groups, or ads only after explicit confirmation. Unattended runs only
  recommend and never pause or resume anything.
argument-hint: "[domain-id] [days]"
allowed-tools: aeko_list_domains, aeko_list_campaigns, aeko_list_ad_groups, aeko_get_ad_insights, aeko_list_ads, aeko_set_campaign_state, aeko_set_ad_group_state, aeko_set_ad_state
---

# AEKO OpenAI Budget Shift

Recommend where OpenAI Ads budget should move, and optionally stop obvious waste. **This skill does not
change budgets.** AEKO sets campaign budgets only in the AEKO dashboard, when a campaign is created or by
editing it later, and automated rules handle pausing. No AEKO tool changes a campaign budget, so the budget
output is always a recommendation that the merchant applies.
It operates OpenAI Ads through AEKO only; it never claims to change Meta, TikTok, or Google Ads.

## Read-only budget contract (read first)

- Budget lives at the **campaign** level as a lifetime budget (ad groups only carry bidding).
- Never call, search for, or improvise a budget write. Do not try to apply a recommendation another way:
  no other tool, no direct API call, and no driving the dashboard in a browser for the user.
- Never say or imply that a budget was changed, saved, applied, staged, or scheduled. Present every amount
  as recommended, and label the output "not applied" in the user's language.
- The merchant applies a recommendation in the AEKO dashboard: **Marketing → Campaigns → Manage
  campaigns**, then **Edit campaign** on the campaign's card (or click its **Lifetime budget** amount),
  change **Lifetime budget**, and **Save**. Korean UI: **Marketing → 캠페인 → 캠페인 관리 → 캠페인 수정 →
  전체 기간 예산 → 저장**.
- **Unattended runs only recommend.** They may read metrics and render the recommendation; they must never
  change campaign/ad-group/ad state, resume spend, or treat a schedule wrapper as confirmation.
- **ROAS caveat:** conversions/revenue aren't ingested, so rank on **efficiency proxies** only
  (CTR, CPC, spend, clicks). Do not claim ROAS-based optimization.

Language: mirror the user's chat language for the recommendation and any pause confirmation. Keep IDs/tool
names ASCII.

## Inputs

- `domain-id` (optional) — `$1`. Resolve via `aeko_list_domains`.
- `days` (optional) — `$2`. Lookback window (default 14). Compute ISO `date_from`/`date_to`.

## Step 1 — Resolve domain, current budgets, performance

1. Resolve the domain.
2. `aeko_list_campaigns(domain_id)` → `budget_lifetime_micros` per active campaign (record it as each
   campaign's current budget) and `editable`. A campaign with `editable: false` is read-only in AEKO (see
   its `read_only_reasons`), and the dashboard does not offer **Edit campaign** for it: keep it out of the
   moves and list it as read-only.
3. Per-campaign performance: `scope="campaign"` REQUIRES a `scope_id`, so **loop** — for EACH campaign id
   call `aeko_get_ad_insights(domain_id, scope="campaign", scope_id=<campaign_id>, date_from, date_to)`
   → impressions, clicks, spend, CTR, CPC over the window. (There is no "all campaigns" call.)

## Step 2 — Score and build the recommendation

- Compute an **efficiency score** per campaign from the proxies (e.g. normalize CTR up + CPC down, weight
  by clicks so low-signal campaigns don't dominate). Skip campaigns below a minimum-impressions floor
  (e.g. < 500) — mark them "low signal, unchanged."
- Keep the **total budget constant** unless the user explicitly wants to raise/lower it. Move budget toward
  higher-efficiency campaigns and away from lower ones, **proportional** to score.
- Express the result as **moves**: each move takes an amount from one campaign and gives it to another.
  Rank moves by expected benefit (score gap weighted by the signal behind it), largest first.
- Keep each recommendation conservative:
  - per-campaign change ≤ **25%** of its current budget per run;
  - never below 1,000,000 micros (1 unit of account currency);
  - a per-campaign ceiling — default to 2× current or a value the user sets; never balloon one campaign.

## Step 3 — Present the ranked recommendation

Show one block, stating that nothing has been changed:
```
Budget-shift recommendation — not applied (window <date_from>→<date_to>, efficiency-weighted,
total lifetime budget held at <total>)

Rank  Move                     Amount   Why
1     B (weak) → A (strong)    ₩50k     A: CTR 2.1% vs 0.4%, CPC ₩180 vs ₩520 on 1.2k vs 300 clicks

Campaign         CTR    CPC     Spend    Lifetime budget now → recommended   Δ
A (strong)       2.1%   ₩180    ₩90k     ₩200k → ₩250k                        +25%
B (weak)         0.4%   ₩520    ₩60k     ₩200k → ₩150k                        −25%
C (low signal)   —      —       ₩2k      ₩100k (unchanged)
D (read-only)    1.0%   ₩300    ₩40k     ₩100k (not editable in AEKO)
```
Then, for each move, give its reasoning and its risks. Name the risks that apply:
- thin data or a short window (few clicks or impressions behind the score);
- proxies are not revenue: a high-CTR campaign may still convert worse;
- recent creative, targeting, or schedule changes that make the window unrepresentative;
- a recommended lifetime budget close to what the campaign has already spent leaves it little room to
  deliver.

End with the dashboard steps from the contract above, so the merchant can apply the moves they accept.

## Step 4 — (Optional) waste-cutting across all three hierarchy levels

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

## Step 5 — Summary

```
Budget-shift recommendation ready — no budget was changed
  Recommended: A ₩200k → ₩250k   B ₩200k → ₩150k   (unchanged: C · read-only: D)
  Apply in the AEKO dashboard: Marketing → Campaigns → Manage campaigns → Edit campaign →
    Lifetime budget → Save
  Paused: <campaign n> campaigns · <group n> ad groups · <ad n> ads (waste-cut, only if confirmed)
  Re-activate paused campaigns, ad groups, or ads only after explicit spend-restart confirmation (`confirm_active=True`).
  After applying any moves, measure the effect with /aeko-openai-ads-reporting in ~1 week.
```

## Scheduling note

An unattended host job may render the recommendation only. Configure it through the host's
advertised scheduler or `/aeko-create-loop`; no universal `/schedule` command is assumed.
Preserve the exact saved job prompt, brand scope, source window, limits, and destination alongside:
```text
/aeko-openai-budget-shift <domain-id> 7
```
This is a prompt handoff, not an installed schedule or server-side staged change. It must not pause or
resume anything. A later interactive run must re-fetch current budgets and performance before anyone acts
on the numbers, and any pause still needs fresh explicit confirmation. Host scheduling support varies.

## Error paths

- No connected ad account / no active campaigns → stop; nothing to recommend.
- No performance data in window → stop; recommend widening `days` or waiting for spend to accumulate.
- The user asks this skill to apply a budget → explain that AEKO does not change budgets through skills or
  MCP, repeat the exact recommended amounts, and give the dashboard steps. Do not look for another way.
- Every campaign is read-only or low signal → say so; recommend no moves.

## What this skill never does

- Never changes, saves, stages, or schedules a budget, and never says it did.
- Never pauses or changes entity state unattended; unattended output is a recommendation only.
- Never recommends beyond the per-run 25% change, a campaign's ceiling, or below the floor.
- Never skips the ad-group middle rung, never archives campaigns/ad groups/ads (only reversible `pause`),
  and never claims ROAS-based decisions.
