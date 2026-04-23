---
name: aeko-visibility-report
description: >
  User-configurable AI visibility report. `depth=summary` is a C-level
  snapshot (headline KPIs + week-over-week trends); `depth=full` is an
  on-demand deep-dive (adds per-prompt performance, cited-source ranking,
  competitor breakdown, recommended next actions). `window` lets the user
  pick the lookback (7d / 14d / 30d / 90d). Replaces the retired
  `/create-visibility-report` and the weekly-only `/aeko-weekly-report`.
argument-hint: "[domain-id] [window] [depth]"
allowed-tools: aeko_list_domains, aeko_get_domain_info, aeko_get_brand_kit, aeko_get_visibility_summary, aeko_get_score, Write
---

# AEKO Visibility Report

Produces a structured AI visibility report for one domain. Output is designed to be pasted into a board / team update without further editing.

## Inputs

- `domain-id` (optional) — UUID. Missing → `aeko_list_domains` pick-list.
- `window` (optional) — `7d` (default), `14d`, `30d`, `90d`.
- `depth` (optional) — `summary` (default) or `full`.

## Step 1 — Resolve domain + context

1. Parse `$1` for UUID. If absent → `aeko_list_domains` → pick.
2. `aeko_get_domain_info(domain_id)` for `base_url`, `brand_keywords`, AI-readiness flags.
3. `aeko_get_brand_kit(domain_id)` for brand_name + target_audience (used to contextualize the report).

## Step 2 — Pull visibility data

Call in parallel:
- `aeko_get_visibility_summary(domain_id, scope="overview")` — 30-day mention / citation / source counts + sentiment + recent brand mentions + monthly trend.
- `aeko_get_visibility_summary(domain_id, scope="tracked_prompt_metrics", window=$2)` — 7-day performance with WoW trends (the tool window arg only affects this scope in v0.5.0; use 7d default).
- `aeko_get_visibility_summary(domain_id, scope="cited_sources")` — pages from this domain AI engines cite.
- `aeko_get_score(domain_id)` — composite AEKO Score (Brand Visibility dashboard score).

## Step 3 — Compose report — summary depth

**Always include:**

```
# AEKO Visibility Report — <brand_name>
**Window:** <window> · **Depth:** summary · **Generated:** <ISO date>

## Headline

AEKO Score: <score>/100
Mentions: <total_mentions> (<WoW trend>)
Citations: <total_citations> (<WoW trend>)
Sentiment: <avg_sentiment_score>% positive (<WoW trend>)

## What moved this week

- <one-line observation per notable metric movement>
- <e.g. "Citations up 12% — driven by new Claude coverage on 차렵이불 queries">

## Top new citations (this window)

- <page_url> — cited <N>× by {platforms} · top prompt: "<prompt text>"
- ...

## Infrastructure snapshot

- llms.txt: <yes|no>
- Robots.txt allows AI crawlers: <yes|no|partial>
- JSON-LD coverage: <yes|no>
(If any is "no" or "partial" → append "run `/aeko-action-center <domain_id> technical`")

## Recommended next step

<one specific command — based on which metric moved most or which infra gap is open>
```

## Step 4 — Full depth (only if `$3 == "full"`)

Add the following sections after the summary:

```
## Per-tracked-prompt performance

| Prompt | Platform | Country | Mentions | Citations | Brand cited? |
|--------|----------|---------|----------|-----------|--------------|
| ...    | ...      | ...     | ...      | ...       | Yes / No     |
```

(Pull from the `tracked_prompt_metrics` scope's breakdown if it surfaces per-prompt data; else cite the summary data and note that per-prompt detail requires `/aeko-prompt-deep-dive <prompt_id>`.)

```
## Cited-source breakdown

<Your pages AI engines cited, grouped by page URL>

| Page | Citations | AI Engines | Top triggering prompt |
|------|-----------|------------|-----------------------|
| ...  | ...       | ...        | ...                   |
```

```
## Competitive signal (from mentions[] across responses)

<Top 5 brands mentioned alongside or instead of this one — from the
`brand_mentions` field in the overview payload. For each, note the sentiment
and how often they appear next to tracked prompts.>
```

```
## Recommended actions (ranked)

1. <most impactful next move — e.g. "Add FAQPage JSON-LD to the 3 top cited
   pages; run /aeko-action-center <domain_id> technical">
2. <second>
3. <third>
```

## Step 5 — Save the report

Write the full markdown to:
`./aeko-artifacts/<domain_id>/reports/visibility-<window>-<depth>-<YYYYMMDD>.md`

## Step 6 — User-facing summary

```
✔ Report saved: <path>
  AEKO Score: <score>  (<trend>)
  Recommended next: <the first command from Step 4's ranked list>
```

## Error paths

- `aeko_get_score` or `aeko_get_visibility_summary` 500 → note which data is missing in the report ("AEKO Score unavailable — backend returned error; rerun in a moment"). Do NOT block the whole report on one failed scope.
- Zero domains → tell user to add one at the AEKO dashboard.
- Zero tracked prompts (tracked_prompt_metrics scope returns empty) → note in report: "No tracked prompts yet. Run `/aeko-find-prompts-to-track` to start collecting data."

## What this skill never does

- Never writes to a store.
- Never fabricates a metric — if data is missing, say so plainly.
- Never exceeds one-page length at `depth=summary`. Keep it scannable.
