---
name: aeko-openai-ads-reporting
description: >
  Produces an account-gated, client/CMO-ready OpenAI Ads performance report for one explicit ad
  account over completed account-local days. Ranks top and bottom campaigns, ad groups, ads, and
  products by CTR, CPC, spend, impressions, and clicks; adds stored conversion coverage; optionally
  folds in organic AI visibility; writes a local Markdown report; and remains read-only and
  schedulable. Use for depth on AEKO-operated OpenAI Ads, not a cross-platform glance.
argument-hint: "[domain-id] [days] [organic=true|false]"
allowed-tools: Read, aeko_list_domains, aeko_list_ad_accounts, aeko_list_campaigns, aeko_list_ad_groups, aeko_list_ads, aeko_get_ad_insights, aeko_get_product_insights, aeko_get_conversion_insights, aeko_get_visibility_summary, Write, aeko_get_active_brand_package, aeko_get_brand_package_version, aeko_read_brand_package_file, aeko_list_brand_wiki_pages, aeko_get_brand_wiki_page
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
it never changes a budget, campaign, ad group, ad, feed, connector, or account setting, and never requests a
conversion refresh.

## Marketer-facing contract

Read `references/brand-execution-contract.md` and `references/brand-output-eval.md`. Preserve the original
`task_prompt`, report questions, verified domain, selected ad account, selected package/eval versions,
source window/timezone, limits and destination across direct and scheduled runs. Defaults need no custom
package. Apply scoped brand rules to authored findings and proposals; they cannot change currencies, metric
definitions, evidence, conversion/ROAS caveats or write restrictions. Evaluate the exact report before
saving/accepting it; required failed/unavailable checks block the affected artifact and must not be reported
as a pass.

Write for a client or CMO in plain business language: ranked findings and takeaways, not a raw metric dump.
Mirror the user's chat language throughout headings, tables, explanations, and recommendations. Keep IDs,
tool names, metric keys, currencies, and dates in English/ASCII, and keep the brand mark `AEKO` in Latin
characters. Tie every takeaway to a displayed number and label recommendations as proposals.

## Inputs, account and window

- `domain-id` is optional. When absent, resolve it with `aeko_list_domains`: auto-select one result, ask the
  user to choose among several, and stop plainly when none are available.
- Ad account: use the job's or user's explicit `ad_account_id` when given and confirm it appears in
  `aeko_list_ad_accounts(domain_id)`. Otherwise auto-select only when exactly one account is `connected`.
  With several connected accounts, ask the user; a scheduled run must already carry an explicit account and
  stops with the account list instead of choosing. Never rely on a backend default account.
- Pin that `ad_account_id` on every call that accepts it (`aeko_list_campaigns`, `aeko_get_ad_insights`,
  `aeko_get_product_insights`, `aeko_get_conversion_insights`). Build ad groups and ads only from campaigns
  listed for that account, so the whole hierarchy belongs to it.
- `days` is optional and defaults to `30`. Dates are account-local: take the selected account's `timezone`,
  derive its latest completed local date (yesterday in that zone at run start), set `date_to` to it and
  `date_from=date_to-(N-1)`. Use the same window for delivery, product and conversion reads so they are
  comparable. Explicit job start/end dates take precedence; print both ISO dates and keep the backend's
  actual window. Do not silently convert a last-complete-week request into a rolling seven-day report.
- Missing or unrecognized account timezone: do not guess one (not UTC, not the user's zone). Ask for explicit
  dates, or in a scheduled run mark the report partial; product and conversion sections become unavailable
  with the backend reason.
- The current, incomplete local day is excluded. Only when the user asks for it, add a separately labeled
  partial-day delivery row from `aeko_get_ad_insights`; never merge it into the comparable window, products or
  conversions.
- `organic` defaults to `true` for a client/CMO report. `organic=false` skips the visibility section without
  changing the paid report.

This skill requires an AEKO account with OpenAI Ads reporting access. Resolve the canonical operations below
against the live capability registry and their schemas; runtime MCP names are
`mcp__<server>__<tool>` and the server segment varies by installation. A missing capability, 401, or tier
error is an account-gated failure for this skill, not evidence that the customer's Meta, Google Ads, or
TikTok connectors are broken. Surface the returned reason and stop or render the partial sections named
below. Never fall back into the cross-platform glance without asking. If `aeko_get_product_insights` or
`aeko_get_conversion_insights` is not registered, render that section as unavailable with the reason; do not
substitute other metrics or call an unlisted endpoint.

## Pull a bounded paid hierarchy

The backend returns rows; the skill ranks them. `aeko_get_ad_insights` is delivery only and keeps its scope
contract: `scope="account"` works without `scope_id`; `campaign`, `ad_group` and `ad` each require the matching
`scope_id`.

Fetch independently, all with the pinned `ad_account_id` where accepted:

1. Account totals: `aeko_get_ad_insights(domain_id, scope="account", date_from, date_to, ad_account_id)` for
   spend, impressions, clicks, account currency, and headline CTR/CPC inputs.
2. Products: `aeko_get_product_insights(domain_id, ad_account_id, date_from, date_to, scope="account",
   limit=50)`; see Products below.
3. Stored conversions: `aeko_get_conversion_insights(domain_id, ad_account_id, date_from, date_to)`; see
   Conversions below.
4. Geography when the user requests it:
   `aeko_get_ad_insights(domain_id, scope="account", segment="country", date_from, date_to, ad_account_id)`.
5. Campaigns: `aeko_list_campaigns(domain_id, ad_account_id)`, then one
   `aeko_get_ad_insights(domain_id, scope="campaign", scope_id=<campaign_id>, date_from, date_to, ad_account_id)`
   per included campaign.
6. Ad groups: for every included campaign call `aeko_list_ad_groups(campaign_id)`, then one
   `aeko_get_ad_insights(..., scope="ad_group", scope_id=<ad_group_id>, ...)` per included ad group.
7. Ads: for every included ad group call `aeko_list_ads(ad_group_id)`, then one
   `aeko_get_ad_insights(..., scope="ad", scope_id=<ad_id>, ...)` per included ad.

Use list responses to map IDs to names. Default to five campaigns, ten ad groups, twenty ads and two product
pages total, at most 60 data-read calls and 256 KiB of retained evidence, including account/hierarchy lists,
product pages, conversions and organic data. Use exact job-selected IDs first; otherwise preserve returned
list order and disclose that selection. Prioritize account/product/conversion reads, then campaign, group and
ad detail within the remaining budget. Honor lower job caps; a broader explicit request must still specify
finite limits before fetching. Scheduled runs use these bounded defaults without waiting for a size-choice
question.

Pass `limit=200` (or a lower job cap) to `aeko_get_ad_insights`; that wrapper supports no pagination
cursor/offset. The three hierarchy-list wrappers accept only their parent ID (plus `ad_account_id` for
campaigns): never invent a limit parameter for them. If an unpaged response exceeds the evidence budget, stop
expanding it, mark the affected scope partial, and report the unbounded transport limitation. Exactly
limit-sized insight rows are cap-reached unless the result proves completeness. Rankings describe only the
inspected subset; state omitted counts when known and `unknown` otherwise. No all-account winners, totals or
exact omitted count may be inferred from incomplete daily/segmented data. Do not fill a missing scope by
summing across hierarchy levels.

One failed scope must not erase successful scopes. Retain the tool, scope, ID, account, date window, fetch
time, currency, and returned error for every row or omission.

### Products

Each product page is one call ranked by product impressions. Follow `page.next_cursor` as `after` only while
the product-page and call/evidence budgets allow; stop when `has_more` is false, and treat
`paging_blocked`/`blocked_reason` or remaining pages as an unknown-completeness subset. Say "top products among
the N inspected", never "the account's best products", unless the final page reported `has_more=false`.

Key and display products by `identity.feed_id` + `identity.item_id` (`key`); never merge rows by title, and
list incomplete identities with their `identity.status`. Metrics are nullable: `null` is unreported, not zero,
so CTR/CPC need both non-null inputs and a row with null impressions is excluded from ranking, not ranked last.
`impressions`/`clicks`/`spend_micros` are ordinary product delivery. `carousel_card_impressions`/
`carousel_card_clicks` are separate, non-billable card actions: report them only when `carousel.status` is
`requested`, in their own columns, never added to delivery. When the status is `not_requested` or `rejected`,
state that card-specific metrics are unavailable for this report.

### Conversions

Report the stored conversion `state` (`complete`, `partial`, `stale`, `not_synced`), `state_reasons`,
`blocked_reason`, coverage day counts, `last_refreshed_at`/`oldest_refreshed_at`, and the latest attempt and
success exactly as returned. Per campaign show `coverage`, `reported_days` of `requested_days`, stale days, and
click-through and view-through conversions as separate columns alongside `conversions`. A `null` total means
no reported day carried the metric; `omitted`, `not_confirmed`, `not_synced` and `pending` days are not zeros.

Attribution is limited: the conversion event and click-through window are unknown and stay unknown; the
view-through window is 1 day. Do not name an event, assume a click window, or borrow a campaign's settings.
Do not calculate CPA, conversion rate, ROAS, revenue, or an account conversion total, and do not present a
partial, stale or unsynced report as complete. Do not request a refresh or suggest manual uploads; describe
the returned state and when AEKO last refreshed.

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
and products; never compare different hierarchy scopes as though they were peers. Rankings use efficiency
proxies and do not establish return on spend or incrementality.

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
Account: <account name> (<ad_account_id>) · Window: <date_from> to <date_to> (<account timezone>)
Currency: <currency> · Status: <complete|partial>

## Executive summary
<spend, impressions, clicks, CTR, CPC, conversion state, and one evidence-backed headline>

## Campaigns
<top, scale, and bottom table>

## Ad groups
<top, scale, and bottom table>

## Ads
<winners and underperformers table>

## Products
<best and worst inspected rows with feed/item IDs; subset disclosure; card metrics or their unavailability>

## Conversions
<state, reasons, coverage, freshness, latest attempt/success, per-campaign click/view columns; or unavailable reason>

## Geography
<only when requested>

## Partial current day
<only when requested; delivery only>

## Organic AI visibility
<separate metrics, exact visibility window, and cross-surface observations; or unavailable reason>

## Recommendations
<at most five manual review actions tied to row IDs and numbers>

## Data limits
No revenue, CPA or ROAS is available; conversions are stored counts with the stated coverage.
<caps, product page subset, low-signal exclusions, partial scopes, and errors>
```

Return the path and a three-to-five-bullet verbal summary. Recommendations are proposals only. Point any
user-requested budget or state follow-up to `/aeko-openai-budget-shift`; this skill never executes it.

## Scheduling

The skill is read-only and may run on a cadence. Use a host that can materialize the selected package/evals
and execute this exact job, or hand off to `/aeko-create-loop` only when its supported job schema can retain
this custom report. A six-source weekly recipe is not automatically this hierarchy report. The schedule
handoff must contain the original `task_prompt`, report questions, domain, explicit `ad_account_id`,
package/eval versions and readable text, dates/timezone policy, finite limits, no-input behavior and
destination, alongside this invocation (the command alone is incomplete):

```text
/aeko-openai-ads-reporting <domain-id> 7 organic=true
```

Do not claim a schedule exists until the host returns a schedule receipt. Scheduled marketing writes remain
unsupported; this scheduled report only reads and renders.

## Error paths

- No AEKO domain or OpenAI Ads reporting capability: state the account-gated requirement and stop without
  probing customer-owned ad connectors.
- No connected ad account, or several without an explicit choice in a scheduled run: stop with the account
  list and the reason.
- No paid data in the window: write the empty paid sections with the exact reason; still include organic
  visibility when requested and available.
- One hierarchy list, insight, product or conversion call fails (including date-incomplete or timezone
  errors): keep every successful section, mark the affected section partial or unavailable, and include the
  returned error code.
- Currency is missing or mixed: do not combine spend and CPC; retain native row currencies and mark the
  headline partial.
- Visibility fails: finish the paid report and mark only the organic section unavailable.
- Local report write fails: render the complete report in conversation, state that it did not persist, and
  do not claim a file path.

## Never

- Never run this account-gated skill as a side effect of `/aeko-ads-review`.
- Never change budgets, entity states, ads, feeds, connectors, or account settings, or request a refresh.
- Never report revenue, CPA or ROAS, or conversion values that the stored report does not provide.
- Never invent numbers; every figure must trace to an `aeko_get_ad_insights`, `aeko_get_product_insights` or
  `aeko_get_conversion_insights` response, or an explicitly labeled visibility response.
