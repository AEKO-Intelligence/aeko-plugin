---
name: aeko-openai-ads-reporting
description: >
  Produces an account-gated, client/CMO-ready OpenAI Ads performance report over
  a date window. Ranks top and bottom campaigns, ad groups, ads, and products by
  CTR, CPC, spend, impressions, and clicks; optionally folds in organic AI
  visibility; writes a local Markdown report; and remains read-only and
  schedulable. Use for depth on AEKO-operated OpenAI Ads, not a cross-platform glance.
argument-hint: "[domain-id] [days] [organic=true|false]"
allowed-tools: aeko_list_domains, aeko_list_campaigns, aeko_list_ad_groups, aeko_list_ads, aeko_get_ad_insights, aeko_get_visibility_summary, Write
disallowed-tools: Edit, Bash
---

# AEKO OpenAI Ads Reporting

Use this skill when the user explicitly invokes:

```text
/aeko-openai-ads-reporting [domain-id] [days] [organic=true|false]
```

This is the account-gated depth report for the one ad platform AEKO operates. `/aeko-ads-review` is the
four-platform glance across Meta, TikTok, Google Ads, and OpenAI Ads; this skill drills into OpenAI Ads only.
It is read-only with respect to ads and AEKO state. It may write one client-ready Markdown report locally;
it never changes a budget, campaign, ad group, ad, feed, connector, or account setting.

## Marketer-facing contract

Write for a client or CMO in plain business language: ranked findings and takeaways, not a raw metric dump.
Mirror the user's chat language throughout headings, tables, explanations, and recommendations. Keep IDs,
tool names, metric keys, currencies, and dates in English/ASCII, and keep the brand mark `AEKO` in Latin
characters. Tie every takeaway to a displayed number and label recommendations as proposals.

## Inputs and account boundary

- `domain-id` is optional. When absent, resolve it with `aeko_list_domains`: auto-select one result, ask the
  user to choose among several, and stop plainly when none are available.
- `days` is optional and defaults to `30`. Accept a positive integer, compute `date_to` as today and
  `date_from` as today minus the lookback, and print both ISO dates before fetching.
- `organic` defaults to `true` for a client/CMO report. `organic=false` skips the visibility section without
  changing the paid report.

This skill requires an AEKO account with OpenAI Ads reporting access. Resolve the canonical operations below
against the live capability registry and their schemas; runtime MCP names are
`mcp__<server>__<tool>` and the server segment varies by installation. A missing capability, 401, or tier
error is an account-gated failure for this skill, not evidence that the customer's Meta, Google Ads, or
TikTok connectors are broken. Surface the returned reason and stop or render the partial sections named
below. Never fall back into the cross-platform glance without asking.

## Pull the complete paid hierarchy

The backend returns rows; the skill ranks them. Preserve the scope contract:

- `scope="account"` works without `scope_id`.
- `scope="campaign"`, `scope="ad_group"`, and `scope="ad"` each require the matching `scope_id`.

Fetch independently:

1. Account totals: `aeko_get_ad_insights(domain_id, scope="account", date_from, date_to)` for spend,
   impressions, clicks, account currency, and headline CTR/CPC inputs.
2. Products: `aeko_get_ad_insights(domain_id, scope="account", segment="product", date_from, date_to)`.
3. Geography when the user requests it:
   `aeko_get_ad_insights(domain_id, scope="account", segment="country", date_from, date_to)`.
4. Campaigns: `aeko_list_campaigns(domain_id)`, then one
   `aeko_get_ad_insights(domain_id, scope="campaign", scope_id=<campaign_id>, date_from, date_to)` per
   included campaign.
5. Ad groups: for every included campaign call `aeko_list_ad_groups(campaign_id)`, then one
   `aeko_get_ad_insights(domain_id, scope="ad_group", scope_id=<ad_group_id>, date_from, date_to)` per
   included ad group.
6. Ads: for every included ad group call `aeko_list_ads(ad_group_id)`, then one
   `aeko_get_ad_insights(domain_id, scope="ad", scope_id=<ad_id>, date_from, date_to)` per included ad.

Use the list responses to map every ID to its human name. Do not invent an all-campaign or all-ad call. If
the hierarchy is large, show the counts and ask whether to run the complete drill-down or cap it; if the user
does not choose, cap detailed ad calls at 50 and state exactly what was omitted. Account, product, campaign,
and ad-group sections still run when the ad cap is reached.

One failed scope must not erase successful scopes. Retain the tool, scope, ID, date window, fetch time,
currency, and returned error for every row or omission.

## Compute and rank honestly

Money arrives in micros; divide by `1,000,000` and retain the account currency. For every account,
campaign, ad-group, ad, and product row compute only when denominators exist:

```text
CTR = clicks / impressions
CPC = spend / clicks
```

Guard divide-by-zero. Rank each hierarchy separately:

- engagement leaders: highest CTR with meaningful impressions;
- cost-efficiency leaders: lowest CPC with meaningful clicks;
- scale leaders: highest spend and clicks;
- underperformers: meaningful spend with explicitly zero clicks, or CPC materially above the same-scope
  median.

Use a default minimum of 100 impressions for ranked winners/losers, keep low-signal rows out of the ranking,
and disclose the floor. Do not label a low-signal row waste. Show top and bottom campaigns, ad groups, ads,
and products; never compare different hierarchy scopes as though they were peers.

### Conversion and ROAS caveat

OpenAI Ads conversion and revenue data is not ingested for this report. Do not calculate or print ROAS.
State that rankings use the efficiency proxies CTR, CPC, spend, impressions, and clicks and do not establish
return on spend or incrementality.

## Optional organic AI-visibility fold

When `organic=true`, call `aeko_get_visibility_summary(domain_id)` for mentions and citations across the
available monitored engines. Keep paid and organic metrics in separate sections and preserve the visibility
window returned by the tool; do not imply it matches the ad window when it does not.

Add at most three cross-surface observations grounded in both sections, for example a product with strong
organic citation evidence but weak paid CTR. Label these as hypotheses for creative or targeting review,
not causal proof. If visibility fails or no tracked data exists, complete the paid report and state why the
organic section is unavailable. `organic=false` records `Skipped by user`.

## Render and write the client-ready report

Write `aeko-openai-ads-reporting-<domain-slug>-<date_to>.md` with this order:

```text
# AEKO OpenAI Ads Performance Report — <domain>
Window: <date_from> to <date_to> · Currency: <currency> · Status: <complete|partial>

## Executive summary
<spend, impressions, clicks, CTR, CPC, and one evidence-backed headline>

## Campaigns
<top, scale, and bottom table>

## Ad groups
<top, scale, and bottom table>

## Ads
<winners and underperformers table>

## Products
<best and worst product rows>

## Geography
<only when requested>

## Organic AI visibility
<separate metrics, exact visibility window, and cross-surface observations; or unavailable reason>

## Recommendations
<at most five manual review actions tied to row IDs and numbers>

## Data limits
No conversion revenue or ROAS is available; rankings use CTR/CPC/spend/click efficiency proxies.
<caps, low-signal exclusions, partial scopes, and errors>
```

Return the path and a three-to-five-bullet verbal summary. Recommendations are proposals only. Point any
user-requested budget or state follow-up to `/aeko-openai-budget-shift`; this skill never executes it.

## Scheduling

The skill is read-only and may run on a cadence. Prefer composing a durable schedule through
`/aeko-create-loop`, or use the host's exact schedule UI with this prompt:

```text
/aeko-openai-ads-reporting <domain-id> 7 organic=true
```

Do not claim a schedule exists until the host returns a schedule receipt. Scheduled marketing writes remain
unsupported; this scheduled report only reads and renders.

## Error paths

- No AEKO domain or OpenAI Ads reporting capability: state the account-gated requirement and stop without
  probing customer-owned ad connectors.
- No paid data in the window: write the empty paid sections with the exact reason; still include organic
  visibility when requested and available.
- One hierarchy list or insight call fails: keep every successful section, mark the affected scope partial,
  and include the returned error.
- Currency is missing or mixed: do not combine spend and CPC; retain native row currencies and mark the
  headline partial.
- Visibility fails: finish the paid report and mark only the organic section unavailable.
- Local report write fails: render the complete report in conversation, state that it did not persist, and
  do not claim a file path.

## Never

- Never run this account-gated skill as a side effect of `/aeko-ads-review`.
- Never change budgets, entity states, ads, feeds, connectors, or account settings.
- Never report conversion, revenue, or ROAS values that the source does not provide.
- Never invent numbers; every figure must trace to an `aeko_get_ad_insights` row or an explicitly labeled
  visibility response.
