---
name: aeko-ads-review
description: >
  Shows Meta, TikTok, Google Ads, and OpenAI Ads in one honest weekly table:
  spend and efficiency for all available rows, platform-claimed conversions
  and ROAS only where ingested, attribution-window inflation, and the gap
  against real store orders. Uses the customer's own official connectors for
  the first three free rows and AEKO for the account-gated OpenAI Ads row.
argument-hint: "[week-of] [platforms=meta,tiktok,google,openai] [domain-id=<id>]"
allowed-tools: Read, aeko_list_domains, aeko_get_ad_insights
disallowed-tools: Write, Edit, Bash
---

# AEKO Ads Review

Answer two questions: **How are my ads doing, and what's wasting money?** The table is the product. Lead with
the cross-platform table, not connector setup or methodology.

This is a read-only four-platform glance. Meta, Google Ads, and TikTok numbers come from the customer's own
official MCP connectors and are free; never check an AEKO account or apply an AEKO tier gate before reading
those three rows. OpenAI Ads comes from AEKO's MCP and needs an AEKO account. Resolve and degrade every row
independently so an absent or unauthorized AEKO connector cannot erase or block the three free rows.

`/aeko-ads-review` owns the collapsed glance. `/aeko-openai-ads-reporting` owns client/CMO-ready depth on the
one platform AEKO actually operates: campaigns, ad groups, ads, products, and optional organic visibility.
Never turn this glance into that hierarchy report implicitly.

## Tier boundary

- Meta, TikTok, and Google Ads: free reads from the customer's own official connectors or validated manual
  exports. AEKO contributes none of those numbers.
- OpenAI Ads: account-gated read from AEKO. When no AEKO account/capability is available, keep the fourth row
  as dashes with `account_gated` and the exact `/aeko-connect` step; never omit it or relabel it zero.

## Marketer-facing output contract

Write for a marketing lead. Mirror the user's chat language for headings, findings, explanations, and
questions. Keep platform names, metric keys, dates, currencies, connector capability labels, and IDs in
English/ASCII. The brand mark is always `AEKO`.

Use the exact meaning of every number:

- `Conv 1d` and `Conv 7d` are conversions the ad platform claims under its attribution window.
- `ROAS 1d` and `ROAS 7d` are platform-claimed conversion value divided by spend for the same window.
- `Delta window` is `Conv 7d - Conv 1d`. It is attribution-window inflation, not incremental orders.
- `Store orders` and store revenue are all-channel business totals supplied by the user, not ad-attributed
  conversions.
- `Claimed total` is a deliberately labeled sum of platform claims. It is not attribution truth and may
  double-count the same order across platforms.

One-day click is the only clean comparable basis across Meta and TikTok. Lead every conclusion with that
basis. Never sum platform conversions into a total presented as real attributed orders.

## Inputs

- `week-of` (optional) — ISO date within the requested week. Normalize to that Monday through Sunday in the
  user's timezone. Default to the last complete Monday-through-Sunday week. If the user explicitly requests
  the current week, label it `partial` and use today as the end date.
- `platforms` (optional) — which sources to query. Default to all four. The table itself always renders
  `Meta`, `TikTok`, `Google Ads`, then `OpenAI Ads`; a source excluded by the user remains a dashed row with
  reason `not requested`, not a missing row.
- `domain-id` (optional) — AEKO domain for the OpenAI Ads row. Resolve it only when pulling that fourth row;
  it is never a prerequisite for the three free rows.
- pasted or local exported totals (optional) — accept them through the manual degradation path after
  validating their dates and attribution settings. Use `Read` only when the user provides a local file.

The four-platform table shape is invariant. Connector availability and query selection control row state,
never row existence.

## Step 1 — fix the comparison window and ground truth

Print the inclusive date range before fetching data. Use the identical start date, end date, timezone, and
currency context for every connector and export.

Ask the user for these store totals for the same inclusive window:

1. actual store order count;
2. actual store revenue and currency.

Order count alone unlocks the primary reconciliation. Revenue adds claimed-value comparison and MER
(`store revenue / total ad spend`), which is a business-efficiency ratio, not ROAS. If the user declines or
does not know either value, continue with the platform rows and mark only the affected reconciliation cells
unavailable. Never fabricate a denominator, convert currency without an evidenced rate, or block the ad
table on missing store truth.

## Step 2 — resolve official connectors by capability

Inspect the live MCP tool registry, including each tool's input schema, output schema, read/write annotation,
provider metadata, and connector authorization metadata. Resolve a connector from capabilities, never from
hardcoded equality, prefix, substring, or regular-expression matching against a tool name or MCP server
name. The server segment in `mcp__<server>__<tool>` varies by installation and is not an identity signal.

Accept only official provider connectors whose metadata identifies Meta, Google Ads, or TikTok and whose
read capability can return account-scoped reporting for an explicit date range. A generic browser, scraper,
web-search tool, analytics warehouse, or similarly named custom tool is not an official ad connector.

Minimum capability evidence:

| Platform | Required read capability |
|---|---|
| Meta | ad-account insights over an explicit date range, with spend, impressions, clicks, purchase conversions/value, and an attribution-window setting or breakdown |
| TikTok | ad-account reporting over an explicit date range, with spend, impressions, clicks, the account's purchase event, conversion value, and an attribution-window setting or breakdown |
| Google Ads | authenticated customer context plus a read-only GAQL search capability |
| OpenAI Ads | AEKO domain resolution plus account-scoped OpenAI Ads insights for an explicit date range |

The official Google Ads MCP server uses stdio and exposes three read-only tools. Confirm that provider and
transport metadata, then select its GAQL search capability by schema and description rather than relying on
any of the three tool names.

The frontmatter pre-approves stable `Read` plus the canonical AEKO reads needed only for the OpenAI Ads row.
Dynamic, namespaced vendor-connector reads may still require host approval; do not hardcode their names
merely to avoid that prompt. `allowed-tools` is pre-approval, not a connector allowlist.

Never invoke a mutation capability. If one connector exposes both reads and writes, call only the discovered
read operation. If more than one official connector satisfies the same platform, list the account identity
from metadata and ask which one to use; do not pick by server name.

Record a capability receipt for all four platform rows:

```text
platform | state | account | capability evidence | auth state | fetched_at
```

Allowed states are `connected`, `partial`, `expired`, `never_connected`, `ambiguous`, `account_gated`,
`not_requested`, and `manual`.

## Step 3 — pull all four rows independently

One connector failure must not stop another platform or remove its row.

### Meta

Request the exact week twice when the connector requires separate attribution settings:

1. one-day click purchase conversions and purchase value, plus impressions and clicks;
2. seven-day click purchase conversions and purchase value, keeping the same delivery totals.

Use the same spend for both columns and record the account currency. Do not combine view-through conversions
with click-through conversions. If the connector reports a blended setting that cannot isolate click-only,
mark the affected cells `partial` and disclose the exact setting.

Where campaign delivery is unexpectedly empty, inspect the read result's delivery/status evidence. Meta
creates new ad objects paused by platform default; when the evidence shows `PAUSED`, note that this can
explain zero delivery. Do not call paused inventory waste and do not change its state.

### TikTok

Request the exact week for the account's primary purchase/complete-payment event under one-day click and
seven-day click windows, including impressions and clicks for efficiency fields. Preserve the connector's
event name in a footnote so different purchase events are not silently combined.

TikTok authorization expires every 30 days. Distinguish auth states using connector registration metadata,
authorization timestamps, expiry timestamps, a non-mutating identity/status check, and structured auth
errors:

- connector record exists and expiry has passed, or a read returns an expired-token/reauthorization error →
  `expired`; show `Expired — reauthorize here: <reauthorization URL or host connector settings path>`
- no saved connector record and no matching capability → `never_connected`; show the connection path
- connector history exists but the registry exposes neither expiry nor an auth error → do not guess;
  `partial` with `authorization state unavailable`

Never label TikTok `never_connected` merely because reporting tools are absent. Use a reauthorization URL
only when connector metadata or the host supplies it; do not invent one.

### Google Ads

Google Ads has no clean query-time one-day/seven-day click toggle. Its official connector is read-only and
exposes GAQL search; use that capability to pull conversions by conversion action and date for the exact
week, including spend/cost and conversion value. Query the conversion-action configuration separately for
each action's click-through lookback window and attribution settings when the capability exposes them.

The semantic GAQL fields needed are:

```text
segments.date
segments.conversion_action
segments.conversion_action_name
metrics.cost_micros
metrics.impressions
metrics.clicks
metrics.conversions
metrics.conversions_value
conversion_action.name
conversion_action.status
conversion_action.primary_for_goal
conversion_action.click_through_lookback_window_days
```

Build valid GAQL for the connector's advertised Google Ads API version; do not send the list above as one
query across incompatible resources. Aggregate only primary purchase actions the user confirms or the
account metadata identifies. Keep other action types separate.

Do not force Google's configured-window conversions into `Conv 1d` or `Conv 7d`:

- when all included actions use exactly one-day click, populate `Conv 1d` only;
- when all included actions use exactly seven-day click, populate `Conv 7d` only;
- for any other or mixed configuration, put a dash in both comparable-window cells and show
  `Configured-window conversions: <N> across <action: days>` in the footnotes.

Always state: `Google's click-through window is configured per conversion action and cannot be selected at
query time.` Google is excluded from the one-day claimed total unless the data proves an exact one-day
basis. Never manufacture a one-day/seven-day split from daily rows.

### OpenAI Ads

After attempting the three free rows, resolve the AEKO slot by capability against the live registry and its
schemas. Do not resolve it by hardcoded runtime MCP name: the loaded operation is namespaced as
`mcp__<server>__<tool>` and the server segment varies by install.

If the AEKO slot or account is absent, unauthorized, or tier-blocked, render the OpenAI Ads row as dashes
with `account_gated` and say: `Run /aeko-connect and fill the AEKO slot, then rerun this same report.` Do not
turn that failure into a generic connector error and do not stop the free rows.

When available, resolve the requested domain or use `aeko_list_domains` only for this row, then call
`aeko_get_ad_insights(domain_id, scope="account", date_from, date_to)`. Map only its documented fields:

```text
impressions, clicks, spend_micros, ctr, cpc_micros, cpm_micros
```

Fill spend, impressions, clicks, CTR, CPC, and CPM from that response. OpenAI Ads conversions and revenue
are not ingested, so `Conv 1d`, `Conv 7d`, `ROAS 1d`, `ROAS 7d`, and `Delta window` are dashes with reason
`OpenAI Ads conversions/ROAS are not yet ingested by AEKO`. Never render zero for any of those cells.

Keep this row at account depth. If the user wants campaign, ad-group, ad, product, or optional organic
AI-visibility analysis, point to `/aeko-openai-ads-reporting`; do not silently perform that deeper workflow.

## Step 4 — degrade without hiding a platform

Apply this ladder independently to Meta, TikTok, and Google Ads:

1. `connected` — use complete official-connector data.
2. `partial` — render available cells; every unavailable cell is a dash with a numbered reason.
3. `manual export` — print the exact checklist below and accept a pasted row or local CSV.
4. `manual analysis` — validate pasted totals, set source to `manual`, and render the row.

A dash means unavailable, never zero. Zero is printed only when the source explicitly reports numeric zero.

### Meta export checklist

- Report: Meta Ads Manager account-level custom report.
- Date: the exact inclusive audit range; account timezone shown.
- Attribution: run once with `1-day click` and once with `7-day click`; exclude view-through.
- Columns: `Amount spent`, impressions, link clicks, purchase-event name, purchases, purchase conversion
  value, attribution setting, account currency.
- Export: CSV; keep the two attribution runs labeled.

### TikTok export checklist

- Report: TikTok Ads Manager custom report at account level.
- Date: the exact inclusive audit range; account timezone shown.
- Attribution: run the primary purchase/complete-payment event once at `1-day click` and once at
  `7-day click`; exclude view-through.
- Columns: `Spend`, impressions, clicks, primary purchase-event name, conversions, total purchase value,
  attribution window, account currency.
- Export: CSV; include the account ID and authorization/connection screen if the report cannot run.

### Google Ads export checklist

- Report: Google Ads Report Editor or GAQL export segmented by day and conversion action.
- Date: the exact inclusive audit range in the account timezone.
- Attribution: do not select a substitute one-day/seven-day window; record each conversion action's configured
  click-through lookback window and attribution model.
- Columns: date, conversion action, primary-for-goal, impressions, clicks, conversions, conversion value,
  cost, currency, click-through lookback-window days.
- Export: CSV; keep purchase actions separate from leads and other goals.

For pasted totals, require this normalized shape before calculation:

```text
platform
date_from
date_to
timezone
currency
spend
impressions
clicks
conversions_1d
conversion_value_1d
conversions_7d
conversion_value_7d
conversion_action_or_event
window_note
source
```

Missing values stay null/unavailable, not zero. Reject a row whose dates differ from the report window or
whose attribution note is missing. Do not interpolate, model, or prorate partial dates.

## Step 5 — calculate comparable and claimed metrics

For each platform:

```text
ctr = clicks / impressions
cpc = spend / clicks
cpm = spend / impressions * 1000
roas_1d = conversion_value_1d / spend
roas_7d = conversion_value_7d / spend
delta_window = conversions_7d - conversions_1d
```

Guard every denominator. CTR, CPC, CPM, and ROAS are unavailable when their required value is missing or the
denominator is zero. Prefer a source-provided OpenAI Ads CTR/CPC/CPM field when documented, but verify its
unit and retain the source value rather than recomputing a conflicting number. When both conversion windows
exist, print `delta_window` as an absolute count and, when `Conv 1d` is nonzero, its relative increase in
parentheses. If one window is missing, the delta is a dash with the reason.

`Claimed total` spend is the sum of every available same-currency spend row, whether or not its conversion
window is comparable. The one-day and seven-day claimed conversion/value totals include only available rows
that match that exact column's window and must carry their included platform list. Claimed ROAS uses the
same included platform set as its conversion-value numerator. Never treat a missing row as zero. When any
declared platform is excluded from a metric, label that metric `partial claimed total`.

OpenAI Ads spend **is included** in `Claimed total` whenever it is available and same-currency. OpenAI Ads
conversions and conversion value **are not included** because AEKO does not ingest them; they are unavailable,
not zero. State both facts next to the total and in the reconciliation note so the comparison against store
orders cannot imply that OpenAI-attributed orders were measured. A claimed-ROAS calculation must use spend
only from the exact same platforms contributing its conversion-value numerator, so it excludes OpenAI Ads
spend even though the separate claimed-total spend cell includes it; print both included-platform lists.

The claimed total is allowed solely for reconciliation and must be followed immediately by:

```text
Claimed total sums what ad platforms claim. It is not attributed order truth and may count the same order
more than once. OpenAI Ads spend is included when available; OpenAI Ads conversions are not ingested and are
excluded rather than counted as zero.
```

Do not sum spend or conversion value across currencies. If platform currencies differ, show each row in its
native currency and render aggregate spend, aggregate ROAS, revenue gap, and MER as unavailable until the
user supplies an evidenced currency normalization.

## Step 6 — reconcile against store truth

When actual order count is available:

```text
gap_1d = claimed_conversions_1d - store_orders
gap_7d = claimed_conversions_7d - store_orders
```

Lead with `gap_1d`. Label positive gaps as platform claims above actual store orders and negative gaps as
actual store orders above platform claims; neither proves incrementality or which platform caused an order.
If a claimed total is partial, label the gap partial too and name the excluded platforms.

When store revenue and same-currency claimed values exist, show the platform-claimed value gap against store
revenue. Show `MER = store revenue / total ad spend` only when total spend is same-currency and complete.
Never label MER as ROAS. Store revenue contains paid, organic, direct, and other sales unless the user says
otherwise.

If the user did not provide ground truth, render all platform rows and print:

```text
Reconciliation unavailable — store order count and revenue were not provided for this window. No denominator
was fabricated.
```

## Step 7 — render the table first

Use this exact column order. Put numbered footnotes after the table for every dash, partial value, Google
configured-window value, TikTok auth state, manual source, mixed currency, or paused-delivery note.

```markdown
| WEEK OF <date> | SPEND | IMPR | CLICKS | CTR | CPC | CPM | CONV 1d | CONV 7d | ROAS 1d | ROAS 7d | Δ WINDOW |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Meta | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| TikTok | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Google Ads | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| OpenAI Ads | ... | ... | ... | ... | ... | ... | — | — | — | — | — |
| **Claimed total** | ... | — | — | — | — | — | ... | ... | ... | ... | — |
| **Store orders (truth)** | — | — | — | — | — | — | <actual orders; all-channel> | — | — | — | — |
| **Gap vs claimed** | — | — | — | — | — | — | <gap_1d> | <gap_7d> | — | — | — |
```

In Markdown, render the same structure as one table. Do not add a status column; attach data-state footnote
markers to the metric cells so the metric layout stays fixed. Every platform keeps its row. The OpenAI Ads
conversion, ROAS, and delta dashes always carry the not-ingested reason when its spend/efficiency data exists.

The `Store orders (truth)` row uses the `Conv 1d` position only as a compact display slot and must carry the
footnote `all-channel actual orders, not a one-day attributed conversion`. Revenue and MER appear in the
reconciliation note, not disguised as ROAS cells.

Before the table, print only:

```text
# AEKO Ads Review
Week: <date_from> to <date_to> · Timezone: <timezone> · Status: <complete|partial>
Comparable basis: 1-day click where the platform supports query-time selection.
```

After the table and its footnotes, print the capability receipt, reconciliation explanation, and waste
findings.

## Step 8 — answer what's wasting money

List at most five findings, each tied to a displayed number and source:

- spend with explicitly reported zero one-day click conversions, only for a platform that ingests that
  conversion metric (never infer this finding for OpenAI Ads);
- the per-platform `Delta window` over-claim signal;
- one-day platform claims above real store orders;
- platform-claimed conversion value above store revenue;
- a reporting/auth gap that prevents the spend from being judged.

Do not call unavailable data zero, call paused Meta inventory waste, infer causation from a claimed/actual
gap, or recommend a budget change unsupported by one-day comparable evidence. Keep this skill read-only;
describe the evidence and a manual next check without changing spend or state.

## Output order

```text
# AEKO Ads Review
<window and comparable-basis lines>

## Cross-platform table
<fixed table>
<numbered footnotes>

## Connector receipt
<all four platforms, including absent/account-gated/not-requested>

## Claimed vs actual
<plain-language reconciliation or unavailable statement>

## What's wasting money
<up to five numbered, evidence-backed findings>

## Manual export checklists
<only the checklists needed for unavailable/partial platforms>

## Platform depth
This table is the cross-platform glance. Use /aeko-openai-ads-reporting for account-gated OpenAI Ads
campaign/ad-group/ad/product depth and an optional organic AI-visibility fold.

Read-only: no campaigns, budgets, ads, connectors, or account settings were changed.
```

## Weekly-report normalized rows

When invoked with `report_mode=weekly`, read
`../aeko-weekly-report/references/arow-contract.md` completely and emit one `ad_metric` `arow/1` block for
**all four platforms** as the machine handoff instead of rendering a second user-facing review. Normal
interactive use still leads with the fixed ads table. Official customer connectors use rung `2` and their
exact namespaced read capability; validated manual exports/pasted truth use rung `3` and
`source.tool: manual_export`. The AEKO OpenAI Ads row uses rung `1`: `status: ok` with the exact AEKO
insights operation when fetched, otherwise `status: unavailable` with `account_gated` or the returned reason.
Carry the exact report window and fetch time.

Map only evidenced numbers to numeric keys such as `spend_micros`, `conv_1d_click`, `conv_7d_click`,
`revenue_1d_click_micros`, `revenue_7d_click_micros`, `roas_1d_click_ratio`, and
`roas_7d_click_ratio`. For OpenAI Ads also map evidenced `impressions`, `clicks`, `ctr_ratio`, `cpc_micros`,
and `cpm_micros`, while omitting conversion/ROAS keys and recording the not-ingested reason. Keep currency
and attribution configuration in `dimensions`. A missing, expired, partial, not-requested, or account-gated
platform still emits its row with empty/partial metrics and non-null
`degraded_because`. Store orders/revenue, when the user supplies them, are a separate `ad_metric` row with
provider `manual`, rung `3`; never merge that truth into a platform row. Do not emit a cross-platform total
row as attribution truth.

## Error paths

- Official connector absent: keep the row, distinguish never connected from known expired auth where
  metadata permits, and print its export checklist.
- Connector returns only part of the week: render available metrics as `partial`, identify missing dates,
  and do not prorate.
- Connector returns an attribution mix that cannot isolate one-day click: keep spend, dash the incomparable
  conversion/ROAS cells, and state the setting.
- Google GAQL capability rejects a field for its advertised API version: inspect that version's schema,
  retry only with an equivalent supported read field, and disclose the omitted field; never substitute a
  modeled window.
- TikTok tool capability disappears: inspect saved connector/auth metadata before choosing `expired` or
  `never_connected`; when history is unavailable, report `authorization state unavailable`.
- User pastes totals with mismatched dates or currencies: show the mismatch and do not combine them.
- Store order count or revenue unavailable: render claimed platform data and leave reconciliation
  unavailable.
- AEKO/OpenAI Ads capability absent, unauthorized, or under-tier: keep the OpenAI Ads row account-gated,
  show `/aeko-connect`, and finish every free row that can run.
- OpenAI Ads insights are partial: retain the returned spend/efficiency fields, dash conversions and ROAS as
  not ingested, and state any additional returned error without inferring zeros.
- All connectors absent: render the full four-platform table of dashes, all relevant vendor export
  checklists, the AEKO connect step, and the
  ground-truth prompt. This is a valid report, not an error.

## What this skill never does

- Never checks for an AEKO account before or as a gate on the free Meta, Google Ads, or TikTok reads.
- Never omits the OpenAI Ads row; its absent account is `account_gated`, not zero and not a reason to block
  the free rows.
- Never puts a zero in OpenAI Ads conversion or ROAS cells; those metrics are not ingested.
- Never performs OpenAI Ads hierarchy depth here; that belongs to `/aeko-openai-ads-reporting`.
- Never resolves a connector by hardcoded MCP tool or server-name matching.
- Never omits a declared platform or treats unavailable as zero.
- Never presents summed platform claims as attributed truth.
- Never invents store orders, revenue, a conversion window, a currency conversion, or a denominator.
- Never changes campaigns, ads, budgets, connectors, or account settings.
- Never writes a local file; this collapsed report renders in conversation and emits normalized rows only
  when the weekly-report contract requests them.
