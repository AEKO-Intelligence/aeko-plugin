---
name: aeko-brand-competitor-analysis
description: >
  Brand-level competitor positioning analysis. Gathers public signals about
  the competitor via WebSearch / WebFetch, asks Claude for positioning
  interpretation, then cross-references AEKO's tracked-prompt citation data
  to show exactly where the competitor wins AI answers that the user's
  brand doesn't. Replaces the retired `aeko_get_product_analysis` backend
  tool and the legacy `/competitive-research` skill.
argument-hint: "[domain-id] <competitor>"
allowed-tools: aeko_list_domains, aeko_get_domain_info, aeko_get_brand_kit, aeko_search_research_prompts, aeko_get_tracked_prompt, aeko_get_visibility_summary, WebSearch, WebFetch, Write
---

# AEKO Brand Competitor Analysis

Produces a competitor-positioning analysis at the **brand level** (not product level — for that use `/aeko-product-competitor-analysis`). Output: a clear picture of what the competitor stands for publicly, where they win AI answers, and one concrete action the user could take.

## Inputs

- `domain-id` (optional) — UUID. Missing → `aeko_list_domains` pick-list.
- `competitor` (required) — Competitor name OR root domain (e.g. "필리" or "pilly.co.kr"). Passed as `$1` (if no domain arg) or `$2`.

## Step 1 — Resolve user's domain + brand context

1. Parse `$1` / `$2`. If first positional is clearly a UUID → `domain_id`, second is competitor. Else treat the positional as competitor and resolve domain via `aeko_list_domains`.
2. `aeko_get_domain_info(domain_id)` + `aeko_get_brand_kit(domain_id)` to ground the "vs us" comparison.

If competitor is a name (not URL), run a quick `WebSearch` for `"<competitor>" official site` to resolve to a root domain. Confirm with the user if ambiguous.

## Step 2 — Gather public signals on the competitor

Collect in parallel where possible:

1. **Root page crawl** — `WebFetch(<competitor_root>)`. Extract: tagline, hero messaging, top-nav categories, whether llms.txt / structured data is present.
2. **Wikipedia / Wikidata entity check** — `WebSearch("<competitor> site:wikipedia.org")` and `WebSearch("<competitor> site:wikidata.org")`. If results → the competitor has AI-knowledge-graph recognition, which is a load-bearing signal.
3. **Recent news** — `WebSearch("<competitor> news 2026")` (adjust year if needed). Surface any fundraising, product launches, brand refresh.
4. **Press / partnerships** — `WebSearch("<competitor> partnership OR acquired OR launch")` — optional if prose asks for depth.

Record the sources. Do NOT fabricate; if a search returns empty, note that.

## Step 3 — Cross-reference AEKO citation data

This is the AEKO-grounded layer — skip this step and you're just a WebSearch wrapper.

1. `aeko_get_visibility_summary(domain_id, scope="cited_sources")` — surfaces pages from the user's domain AI engines cite.
2. For each of the user's top 5-10 tracked prompts (derive from `brand_kit.brand_keywords[]` + `aeko_search_research_prompts(scope=..., country=...)` if no tracked set yet):
   - Call `aeko_get_tracked_prompt(prompt_id, window="30d")` for forensics.
   - Count how often the competitor's brand name appears in `responses[].mentions`.
   - Count how often the competitor's root domain appears in `responses[].citations[].domain`.
3. Build a comparison matrix:

```
| Prompt | Our mentions | Competitor mentions | Our citations | Competitor citations |
|--------|--------------|---------------------|---------------|----------------------|
| ...    | ...          | ...                 | ...           | ...                  |
```

Rank prompts by `competitor_mentions + competitor_citations - our_mentions - our_citations`. Top rows = prompts where the competitor is winning and the user isn't.

## Step 4 — Write the analysis

Compose a markdown report:

```
# Competitor Analysis: <competitor>
**Against:** <user's brand> (`<domain>`)
**Generated:** <ISO date>

## Public positioning

- **Tagline:** <from hero crawl, or "none found">
- **Top categories:** <from top-nav>
- **Wikipedia entity:** <yes with URL | no>
- **Wikidata entity:** <yes with URL | no>
- **Recent news:** <1-3 headlines, each with date and URL>

## AI visibility footprint vs <user's brand>

(Embed the comparison matrix from Step 3.)

**Interpretation:**
<one paragraph on what the matrix shows — e.g. "The competitor dominates
awareness-stage informational prompts in KR; we're stronger at
recommendation-stage prompts where brand reputation matters. The gap is
most pronounced in the top-3 prompts, where our brand is absent from
AI answers entirely.">

## What the competitor does that we don't

(From Step 2 signals that translate to AEO leverage:)
- Wikipedia entity → AI models have richer embeddings for them
- llms.txt on root → declared AI-readability
- Structured data present → Product / FAQPage / Organization schemas
- Recent news coverage → fresh signal for news-aware AI engines

For each present for competitor but absent for user → flag.

## Recommended action

<one concrete command the user could run to start closing the gap>
```

## Step 5 — Save + summary

Write to `./aeko-artifacts/<domain_id>/competitor-analyses/<competitor-slug>-<YYYYMMDD>.md`.

User-facing summary:

```
✔ Competitor analysis saved: <path>
  Competitor: <competitor>
  Biggest gap: <top row from Step 3 matrix>
  Next: <recommended action command>
```

## Error paths

- Competitor name ambiguous + WebSearch returns multiple candidates → ask user to pick or paste the root URL directly.
- All cross-reference calls fail → still produce the Step 2 / Step 4 public-signals portion; note AEKO forensics missing.
- No tracked prompts + research-prompt fallback returns empty → note the user's domain doesn't have any tracked-prompt coverage yet; suggest `/aeko-find-prompts-to-track` as a prerequisite.

## What this skill never does

- Never compares at the product level — that's `/aeko-product-competitor-analysis`.
- Never fabricates Wikipedia / news findings.
- Never posts anything externally.
- Never mutates tracking state.
