---
name: competitive-research
description: >
  Research a competitor's AI visibility strategy. Analyzes competitor
  content, structured data, and citation patterns to identify gaps and
  opportunities. Returns a structured competitive brief with actionable
  recommendations. Use when a user wants to understand how competitors
  are performing in AI engine results.
argument-hint: <competitor-name-or-url> [--domain-id <uuid>]
allowed-tools: aeko_list_action_items, aeko_search_research_prompts, aeko_get_product_analysis, aeko_get_visibility_summary, aeko_get_score, aeko_get_metrics, aeko_get_brand_kit, WebFetch, WebSearch
---

# Competitive Research — AI Visibility Gap Analysis

> ⚠️ **Stage-1 dependencies.** Steps that call `aeko_list_action_items` or `aeko_get_brand_kit` depend on Stage-1 tool stubs (see `docs/contracts/action-item-contract.md`). If those tools are not yet wired, skip those steps silently and continue the research — do NOT dead-end the whole run. The web-research portions (WebSearch / WebFetch) and the legacy AEKO tools (`aeko_get_score`, `aeko_get_visibility_summary`, `aeko_get_metrics`, `aeko_get_product_analysis`, `aeko_search_research_prompts`) work today and should proceed regardless.


You are performing competitive research to help the user understand and outperform a competitor in AI engine visibility.

## Step 1: Parse input

Extract from the user's input:
- **Competitor name** and/or **URL**
- **Domain ID** (optional — if provided, pull AEKO context for the user's own domain)
- **Product category** or **market** (if mentioned)

If only a name is given, construct the likely URL. If only a URL is given, extract the brand name.

## Step 2: Gather AEKO context (if domain-id provided)

If the user provided their own domain-id, gather internal context:

1. Call `aeko_get_score` for the user's domain — establishes baseline AEKO Score
2. Call `aeko_get_metrics` — get 7-day trends to show trajectory
3. Call `aeko_get_visibility_summary` — detailed mentions, citations, sentiment
4. Call `aeko_list_action_items(domain_id, status="pending")` — surface any pending Action-tab items that already reference this competitor or similar market gaps
5. Call `aeko_search_research_prompts` with the competitor name — find prompts where the competitor appears
6. Call `aeko_get_brand_kit(domain_id)` — check whether this competitor already appears in the Brand Kit's `forbidden` list (don't-mention competitor), `must_include` phrases, or `sample_urls` (reference voice source). The Brand Kit has no dedicated `competitors` field; positioning against a competitor lives in `brand_voice_summary` / `target_audience` prose.

This gives you the user's current position, trajectory, existing work in flight, and whether the competitor is already tracked.

## Step 3: Research competitor's web presence

Use `WebSearch` to find:
- Competitor's main website and key product pages
- Competitor mentions in AI engine contexts (e.g., "best [product category]" queries)
- Competitor reviews, press coverage, and third-party mentions
- Competitor's social media presence and authority signals

Use `WebFetch` to analyze the competitor's key pages:

### Homepage / Main product page
- Check for JSON-LD structured data (Product, Organization, FAQ schemas)
- Note content structure: headings, FAQ sections, comparison tables
- Look for `robots.txt` AI crawler directives
- Check for `llms.txt`

### Product pages (2-3 examples)
- Content depth and citability patterns
- Pricing transparency
- Review/rating structured data
- Shipping and return policy structured data

## Step 4: Analyze competitor strengths

Assess the competitor across these dimensions:

| Dimension | What to check |
|-----------|--------------|
| **Structured Data** | JSON-LD types present, completeness, speakable markup |
| **Content Citability** | Answer blocks, self-contained passages, statistical density |
| **Entity Recognition** | Wikipedia/Wikidata presence, brand sameAs links |
| **Infrastructure** | robots.txt AI access, llms.txt, sitemap |
| **Content Strategy** | Blog/resource depth, FAQ coverage, comparison content |
| **Authority Signals** | Third-party mentions, review presence, press coverage |

Rate each dimension: Strong / Moderate / Weak / Not Found

## Step 5: Gap analysis

Compare the competitor's profile against the user's position (if domain-id was provided) or against AEO best practices.

Create a gap table:

```
| Dimension | User | Competitor | Gap | Opportunity |
|-----------|------|------------|-----|-------------|
| Product Schema | Basic | Complete | High | Add shipping, reviews, speakable |
| FAQ Content | None | 8 FAQs | Critical | Generate FAQ schema |
| Blog Content | 2 posts | 15+ posts | High | Content creation campaign |
```

Highlight:
- **Competitor advantages** — where they're ahead and what's working
- **User advantages** — where the user is already stronger
- **Untapped opportunities** — gaps neither party has filled

## Step 6: Structured competitive brief

Present findings as a structured brief:

### Competitor Profile
- Brand, URL, industry positioning
- Estimated content volume and freshness
- Key strengths (2-3 bullet points)

### AI Visibility Assessment
Rate the competitor's overall AEO readiness (A-F scale) with justification.

### Strategic Gaps (prioritized)

For each gap, provide:
1. **Gap**: What the competitor has that the user doesn't
2. **Impact**: How this affects AI engine recommendations (High/Medium/Low)
3. **Effort**: How hard it is to close the gap (Low/Medium/High)
4. **Action**: Specific step to take

### Content Opportunities

Identify 3-5 content pieces the user should create based on:
- Topics where the competitor ranks but the user doesn't
- Questions AI engines ask that neither party answers well
- Comparison queries where the user could win

## Step 7: Suggest follow-up actions

Based on findings, recommend the new AEKO surface:

- `/aeko-brand-kit <domain-id> edit` — encode competitive positioning in the Brand Kit (voice/target_audience prose, `forbidden` phrases to avoid imitating, `must_include` claims that differentiate). There is no dedicated competitors field; positioning lives in voice + guardrails.
- `/aeko-action-center <domain-id>` — check whether backend has already queued Action items that address any gaps found here; if yes, route the user to `/aeko-run-action <item-id>`
- `/aeo-audit <user-url>` — self-audit a key page for comparison against the competitor's structured-data profile

If backend has NOT yet queued items for the gaps identified, flag this to the user: gaps surface in this skill, but items are created by the web UI's Action tab. The user should create Action items for the top gaps there, then run `/aeko-run-action` when ready.

Frame recommendations as a prioritized action plan with estimated impact.
