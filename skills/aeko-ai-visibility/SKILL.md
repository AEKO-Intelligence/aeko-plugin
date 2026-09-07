---
name: aeko-ai-visibility
description: >
  Reports AI visibility, Share of Voice, and answer drift for one AEKO domain.
  depth=summary is a C-level snapshot; depth=full adds per-prompt performance,
  cited sources, competitors, and actions. Routes users with no tracked prompts
  to aeko-manage-prompts instead of rendering an empty report.
argument-hint: "[domain-id] [window] [depth]"
allowed-tools: aeko_list_domains, aeko_get_domain_info, aeko_get_tracked_prompts, aeko_get_visibility_summary, aeko_get_share_of_voice, aeko_get_answer_drift, Read, Write
---

# AEKO AI Visibility

Produces a structured AI visibility report for one domain. Output is designed to be pasted into a board / team update without further editing.

## Marketer-facing output contract

Read `references/brand-execution-contract.md` and `references/brand-output-eval.md` before selecting report
evidence. Keep the original `task_prompt`, questions, verified domain, selected package/eval versions,
window/timezone and destination intact; defaults require no custom package. Apply scoped rules to authored
interpretation, not raw metrics, source quotations or metric definitions. Honor the Starter first-line
rule below. Before saving/accepting the exact report, check its task coverage and required brand evals;
failed/unavailable required checks block the affected artifact. Weekly rows keep their schema and carry
relevant limitations in `degraded_because`/`dimensions`, not a second user-facing report.

Default to one call per listed scope, one domain/list resolution and at most 256 KiB of retained evidence;
no automatic retries or follow-up crawl. Honor lower job budgets. If a required payload does not fit, keep
the affected scope unavailable/partial and report the limit rather than silently passing a full report.

Write for a marketing lead or founder. Lead with business meaning, not backend scopes: "Are we being mentioned?",
"Are we being cited?", "What changed?", and "What should we do next?" Keep `depth=summary` to one page.

Language: mirror the user's chat language for user-facing steps, summaries, questions, and next actions.
Keep slash commands, IDs, file paths, channel slugs, schema keys, and tool names in English/ASCII.

## Inputs

- `domain-id` (optional) — UUID. Missing → `aeko_list_domains` pick-list.
- `window` (optional) — `7d` (default), `14d`, `30d`, `90d`.
- `depth` (optional) — `summary` (default) or `full`.

## Step 1 — Resolve domain + prompt context

1. Parse `$1` for UUID. If absent → `aeko_list_domains` → pick.
2. `aeko_get_domain_info(domain_id)` for `base_url`, brand/domain names, domain keywords, AI-readiness
   flags, and any prompt-tracking context metadata surfaced by the backend.
3. Before printing progress, inspect `package`, `tier`, or equivalent plan metadata. When the account is
   Starter, the **first user-visible line** must be:
   - EN: `Starter coverage: only ChatGPT is monitored.`
   - KO: `Starter 범위: ChatGPT만 모니터링합니다.`
   Translate naturally for other languages while keeping `Starter` and `ChatGPT` unchanged. Do not put a
   title, greeting, or setup sentence before this line.
4. Call `aeko_get_tracked_prompts`. If there are no active tracked prompts, stop before pulling report
   scopes or writing a file. Say that visibility needs questions to monitor and route to:

   ```text
   /aeko-manage-prompts mode=discover <domain_id>
   ```

   Do not render an empty report.
5. Use domain and prompt context only for report segmentation and content/PDP recommendations.

The tracked-prompt list is account-wide and its current formatter exposes no `domain_id`. Nonempty account
history does not prove this domain has history. Do not populate `prompt_ids` from the entire account or
semantic similarity: use only IDs explicitly tied to this domain by returned scoped evidence or the
verified job selection; otherwise omit the optional filter and retain the domain-scoped backend results.

## Step 2 — Pull visibility data

Call in parallel when supported and within the remaining budget; otherwise run the same reads sequentially:
- `aeko_get_visibility_summary(domain_id, scope="overview")` — all-time totals, seven-day WoW comparisons
  and a 13-week trend; not totals for the requested report window.
- `aeko_get_visibility_summary(domain_id, scope="tracked_prompt_metrics", window=<requested hint>)` — fixed
  latest seven days and previous seven-day comparison. `window` is compatibility-only and is not forwarded
  to the backend; it cannot select a calendar week or a 14/30/90-day metrics window.
- `aeko_get_visibility_summary(domain_id, scope="cited_sources")` — pages from this domain AI engines cite;
  no selectable date range. Do not label these "new this week" without authoritative event timestamps.
- `aeko_get_share_of_voice(domain_id, prompt_ids=<verified selected ids or omitted>, start_date=<window start>, end_date=<window end>)`
  — the brand's share across tracked-prompt responses for the exact requested dates.
- `aeko_get_answer_drift(domain_id, days=<7|14|30|90>, prompt_ids=<verified selected ids or omitted>)` — which
  monitored answers materially changed over the requested lookback.

Compute ISO dates from the requested window. Do not convert Share of Voice into a made-up score or describe
answer drift as visibility loss; report the backend definitions and denominators returned by each tool.
`days` is a rolling lookback, not an arbitrary historical start/end. Retain each source's actual window,
timezone and fetch time; when exact boundaries are unavailable, say so. A weekly request never relabels
all-time or rolling data as last Monday–Sunday. If exact-window answers are required and cannot be
selected, mark those answers unavailable while keeping separately labeled usable observations.

## Step 3 — Compose report — summary depth

**Always include:**

```
# AEKO Visibility Report — <brand_name>
**Requested window:** <window> · **Depth:** summary · **Generated:** <ISO date>
**Source windows:** <all-time overview; fixed metrics window; SOV dates; drift lookback>

## Headline

AI visibility, all time: <overview total_mentions> mentions · <overview total_citations> citations
Mentions, fixed seven-day metrics: <returned count> (<its WoW trend>)
Citations, fixed seven-day metrics: <returned count> (<its WoW trend>)
Sentiment: <returned value with its actual definition, units and window>
Share of Voice: <backend SOV value + denominator/peer set>
Answer drift: <changed prompts / assessed prompts> changed in <actual drift lookback>

## What moved this week

- <one-line observation per notable metric movement>
- <e.g. "Citations up 12% — driven by new Claude coverage on 차렵이불 queries">
- <largest Share of Voice gain/loss, only when the SOV payload supports a comparison>
- <highest-impact answer drift, naming prompt/platform/date and what changed>

## Top cited pages (source window; not necessarily new)

- <page_url> — cited <N>× by {platforms} · top prompt: "<prompt text>"
- ...

## What AI appears to use from our pages

- <page_url> — inferred from overlapping facts/snippets, not a measured metric: <plain-language summary>
- If there is not enough crawl/response overlap, say "not enough evidence yet" instead of guessing.

## Infrastructure snapshot

- AI search/shopping crawler access: <yes|no|partial>
- llms.txt curated index: <yes|no> (optional)
- JSON-LD coverage: <yes|no>
(If crawler access or JSON-LD is "no" or "partial" → append "run `/aeko-action-center <domain_id> technical`")

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

(Pull from the `tracked_prompt_metrics` scope's breakdown if it surfaces per-prompt data; include
context columns when present. Else cite the summary data and note that per-prompt detail requires
`/aeko-source-analysis <prompt_id>`.)

```
## Cited-source breakdown

<Your pages AI engines cited, grouped by page URL>

| Page | Citations | AI Engines | Top triggering prompt |
|------|-----------|------------|-----------------------|
| ...  | ...       | ...        | ...                   |
```

When a competitor's page outranks yours for a prompt, note *why* in the plugin's AEO vocabulary
(BLUF / PREP / Informational Gain / E-E-A-T — see `references/aeo-frameworks.md`):
"the cited winner leads with the answer (BLUF) and shows lived detail (Informational Gain); your page is
generic." This makes the report's findings map straight to what the executor skills fix — for a single
prompt, hand off to `/aeko-source-analysis <prompt_id>`.
Carry the original task, report question, verified domain/package/eval context, actual evidence windows and
remaining limits with that command. It is a proposed analysis, not permission for an executor to write.

Where response and crawl snippets are available, add a clearly labeled "inferred absorption" note:
"AI appears to reuse these facts from the page..." This is an interpretation from text overlap, not a
platform-provided metric.

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

## Weekly-report normalized rows

When invoked with `report_mode=weekly`, read
`references/arow-contract.md` completely. Emit separate `visibility_summary` `arow/1` rows for scopes with
different windows/definitions, with `source.slot: visibility`, `source.provider: aeko`, rung `1`, each
scope's actual window (null plus an explanatory freshness note when exact dates are unavailable), the
actual fetch time, and only backend-returned numeric metrics. Record the requested window separately in
`dimensions`; incompatible scopes remain partial for that requested comparison. Never combine all-time,
fixed-seven-day, exact-date SOV and rolling drift metrics into one requested-week row.
At full depth, emit one `visibility_prompt` row per prompt,
capped at 50. Emit these rows instead of rendering a second user-facing report; normal interactive mode is
unchanged. Keep metric definitions/denominators and platform scope in `dimensions`; do not convert Share
of Voice or answer drift into a made-up composite.

If the account, tier, prompt history, or every visibility scope is unavailable, emit an unavailable summary
row before routing or stopping. Partial scope failures produce a partial summary row with every missing
scope in `degraded_because`. In weekly mode, do not write a local artifact in Step 5; the composite owns
durable delivery.

## Step 5 — Save the report

Write the full markdown to:
`./aeko-artifacts/<domain_id>/reports/visibility-<window>-<depth>-<YYYYMMDD>.md`

## Step 6 — User-facing summary

```
✔ Report saved: <path>
  Visibility: <total_mentions> mentions · <total_citations> citations
  Recommended next: <the first command from Step 4's ranked list>
```

## Error paths

- `aeko_get_visibility_summary` 500 → note which data is missing in the report ("visibility summary unavailable — backend returned error; rerun in a moment"). Do NOT block the whole report on one failed scope.
- `aeko_get_share_of_voice` fails → mark Share of Voice unavailable with the exact error; keep visibility
  and drift sections.
- `aeko_get_answer_drift` fails → mark answer drift unavailable with the exact error; keep visibility and
  Share of Voice sections.
- Zero domains → tell user to add one at the AEKO dashboard.
- Zero tracked prompts → do not render or save a report; route to `/aeko-manage-prompts mode=discover`.

## What this skill never does

- Never writes to a store.
- Never fabricates a metric — if data is missing, say so plainly.
- Never exceeds one-page length at `depth=summary`. Keep it scannable.
