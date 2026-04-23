---
name: aeko-prompt-deep-dive
description: >
  Citation-forensics deep-dive on one tracked prompt. Pulls per-platform
  responses, citation arrays, and crawled source metadata, then helps the
  user understand which competitors win the prompt, which sources AI
  engines cite, and what those sources do that could be mirrored. This
  skill operationalizes AEKO's unique "citation forensics" value-prop —
  vanilla Claude cannot do it.
argument-hint: "<prompt-id> [window]"
allowed-tools: aeko_get_tracked_prompt, aeko_get_brand_kit, aeko_get_domain_info, WebFetch
---

# AEKO Prompt Deep-Dive

Walks a user through one tracked prompt's full citation footprint. Output: a clear picture of which pages / brands win this prompt across AI engines, plus one concrete action the user could take.

## Input

- `prompt-id` (required) — `$1`. UUID of a tracked prompt (must have a `UserPrompts` row for the current user).
- `window` (optional) — `$2`. `latest` (default), `7d`, `30d`, or `90d`.

If `prompt-id` is missing, tell user to get one from `/aeko-find-prompts-to-track` or `/aeko-action-center`.

## Step 1 — Fetch the forensics payload

Call `aeko_get_tracked_prompt(prompt_id, window=<from $2 or "latest">)`.

On 404 → the user isn't tracking this prompt (or never did). Tell them and suggest `/aeko-find-prompts-to-track` to discover + track candidates.

On success, the payload includes:
- `prompt`: text, language, country, industry, vertical, query_type, funnel_stage, persona.
- `responses`: array of per-platform responses (`ai_platform`, `response_date`, `full_response`, `mention_count`, `citation_count`, `source_count`, `sentiment`, `observed_intent`, `mentions`, `citations[]`, `citations_truncated`).
- Each citation: `source_url`, `domain`, `source_type`, `mention_name`, `position_in_response`, `context_snippet`, `crawl` (or null).
- Each crawl (when non-null): `extracted_text` (may be truncated to 5000 chars, flagged), `meta`, `json_ld[]`, `source_analysis`.

## Step 2 — Summarize per-platform behavior

Print a header block:

```
# Deep-dive: <prompt text, truncated to 100 chars>
- ID:        <prompt_id>
- Window:    <window>
- Prompt context: <country> · <industry> · <query_type> · <persona>
```

Then a per-platform summary table:

```
| Platform | Date | Mentions | Citations | Sentiment | Brand present |
|----------|------|----------|-----------|-----------|---------------|
| Claude   | ...  | 3        | 2         | neutral   | No            |
| GPT      | ...  | 2        | 2         | positive  | Yes (pos 3)   |
| Gemini   | ...  | 1        | 0         | —         | No            |
```

"Brand present" checks whether the user's brand appears in `mentions` (compare against brand kit `brand_name` + `brand_keywords[]`). If yes, show position if derivable from context_snippet.

## Step 3 — Rank cited sources

Aggregate across all platforms in the window. For each unique `domain + canonical_url` pair:
- `total_citations` = sum across responses.
- `avg_position` = mean `position_in_response` (ignore nulls).
- `platforms` = set of AI platforms that cited this source.

Sort by `total_citations` desc, then `avg_position` asc (lower = earlier in AI output = more prominent).

Print top 5-10:

```
## Top cited sources

1. **<domain>** · <source_type> · cited <N>× across {Claude, GPT} · avg pos 2.5
   URL: <source_url>
   Mentioned alongside: <brand names from context_snippet, comma-separated>
   → Why AI cites it: <one-line hypothesis based on crawl data below>

2. ...
```

## Step 4 — Structural analysis of each top source

For each top source with non-null `crawl`, analyze:
- **JSON-LD types present** (from `crawl.json_ld[]` — look at `@type` field). Call out `FAQPage`, `Product`, `Review`, `AggregateRating`, `Article`, `BreadcrumbList`.
- **Source analysis signals** (from `crawl.source_analysis`): citability score if present, heading depth, structural patterns.
- **Content shape** (from first ~500 chars of `crawl.extracted_text`): Q&A format, first-person review, comparison table, listicle, news article, etc.

Print under each top source:

```
   Structure: <content shape>
   JSON-LD:   <types present, or "none">
   Citability: <score if known, else "N/A">
   Takeaway:  <one sentence on what this source does that the user could mirror>
```

If `crawl` is null (source never crawled) and the URL is public, do a light `WebFetch` to get a rough structural read — mark the analysis as "live-fetched, not cached" so the user knows the difference.

## Step 5 — Competitor callout

From the aggregated `mentions` field across responses, build a frequency table of brand names. Flag the user's own brand (brand kit lookup) + the top 3-5 competitors by total mention count:

```
## Who's winning this prompt

- **<competitor>**: mentioned <N>×, cited <M>× — appears in {Claude, GPT}
- **<competitor>**: ...
- **<user's brand>**: mentioned <N>× (target: grow this)
```

If the user's brand is absent, say so plainly: "Your brand isn't surfacing for this prompt yet. That's the gap to close."

## Step 6 — One concrete action

Based on the analysis, propose exactly ONE action the user could take. Pick from:

- **Mirror a winning PDP structure** — "Three top cited sources are retailer PDPs with FAQPage JSON-LD. Your matching PDP <url> doesn't have FAQPage markup. Run `/aeko-action-center <domain_id> pdp` to see if there's a pending PDP action for this product."
- **Write content to match a winning format** — "The top cited source is a Naver 블로그 first-person review. AEKO doesn't have an action item for this, but drafting your own review-style piece could help. Run `/aeko-action-center <domain_id> content` to see pending content items, or tell me to draft one standalone."
- **Close a technical gap** — "Top cited sources all have Organization JSON-LD with `sameAs` pointing to Wikipedia/Wikidata. Your domain's JSON-LD is missing. Run `/aeko-action-center <domain_id> technical` for the matching fix."
- **Track a related prompt** — "This prompt is awareness-stage. The brands winning it also win comparable consideration-stage prompts (e.g. '<related query>'). Run `/aeko-find-prompts-to-track` to add related prompts to your watchlist."

Pick the most specific, load-bearing action. If none fits, pick "run the visibility report for context" (`/aeko-visibility-report <domain_id>`).

## Step 7 — Save the analysis

Write the full analysis markdown to `./aeko-artifacts/<domain_id>/prompt-deep-dives/<prompt_id>-<window>.md` so the user can revisit without re-running. Tell them the path.

## Error paths

- 404 from `aeko_get_tracked_prompt` → suggest `/aeko-find-prompts-to-track`.
- Zero responses in the window → tell user AEKO hasn't collected data for this prompt yet; suggest checking back in 1-3 days OR widening window to `90d`.
- All citations have null crawl → analysis falls back to WebFetch for top 3 sources only; cap to avoid flooding the skill.

## What this skill never does

- Never untracks the prompt or modifies tracking state (that's `/aeko-find-prompts-to-track` for adding, dashboard for removing).
- Never fabricates citation data — if a source URL returns 404 on live fetch, note it and move on.
- Never creates an action item — only suggests commands the user runs.
