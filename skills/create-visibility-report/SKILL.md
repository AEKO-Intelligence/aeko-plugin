---
name: create-visibility-report
description: >
  Generate a comprehensive AI visibility report for a domain.
  Aggregates all AEKO data (mentions, citations, page scores,
  suggestions, product analyses) into a professional report.
  Use when a user wants a full overview of their AI engine visibility.
argument-hint: <domain-id>
allowed-tools: aeko_prepare_report, aeko_get_score, aeko_get_metrics, aeko_save_content, Read, Write, Bash(open *), Bash(xdg-open *)
---

# Create Visibility Report — AI Engine Visibility Assessment

You are generating a comprehensive AI visibility report for an AEKO domain. Follow these steps carefully.

## Step 1: Gather all data

Call **`aeko_prepare_report(domain_id)`** to collect all domain data in one call.

This aggregates:
- Domain info & infrastructure status
- Visibility metrics (mentions, citations, sentiment, trends)
- Page analysis scores & issues
- Prioritized suggestions
- Product analyses & competitive insights

Also call:
- **`aeko_get_score(domain_id)`** — composite AEKO Score (0-100, grade A-F) with 5 component breakdown
- **`aeko_get_metrics(domain_id)`** — 7-day performance metrics with week-over-week trends

## Step 2: Generate Executive Summary

Write 2-3 sentences covering:
- **AEKO Score** — the headline number (score/100, grade) from `aeko_get_score`
- **Overall assessment** — is the site well-optimized, needs work, or critical?
- **Key trend** — are metrics improving or declining? (from `aeko_get_metrics`)
- **Biggest win** — what's working well
- **Biggest risk** — what needs immediate attention

Use specific numbers from the data. Avoid vague language.

## Step 3: AI Visibility Metrics Section

Present the core metrics:
- Total mentions across AI platforms
- Citation count & citation rate
- Sentiment score
- Platform breakdown (which AI engines mention/cite this brand)
- Trend direction (improving, declining, stable)

If trend data is available, note whether visibility is growing or shrinking.

## Step 4: Page-by-Page Analysis

For each scanned page:
- AI readiness score (with interpretation: 80+ = strong, 60-79 = needs work, <60 = weak)
- Structured data status (has Product/Article JSON-LD?)
- Top issues identified

Include summary stats:
- Average score across all pages
- Pages with vs without JSON-LD
- Score distribution (how many pages are strong/moderate/weak)

## Step 5: Infrastructure Status

Assess the technical foundation:
- **robots.txt** — are AI crawlers blocked?
- **llms.txt** — does it exist? Is it complete?
- **JSON-LD** — coverage across pages
- **Sitemap** — present and discoverable?

Rate infrastructure as: Ready / Partial / Not Ready.

## Step 6: Prioritized Action Items

Group suggestions by severity:
- **Critical** — blocking AI visibility (e.g., robots.txt blocking crawlers)
- **High** — significant impact fixes (e.g., add Product JSON-LD to key pages)
- **Medium** — improvement opportunities (e.g., add FAQ schema, optimize descriptions)
- **Low** — nice-to-have refinements

For each action item, include:
1. What to do
2. Why it matters
3. Estimated effort (quick / moderate / significant)

## Step 7: Competitive Insights

If product analyses are available:
- Competitor positioning summary
- Competitive advantages to emphasize
- Gaps to address
- Market-specific insights

## Step 8: Save the report

Ask the user what format they prefer:
- **Markdown** (.md) — best for sharing in docs/wikis
- **HTML** (.html) — best for email or web viewing
- **Plain text** (.txt) — simplest format

Save via **`aeko_save_content(file_path, content)`** or the `Write` tool.

Suggested filename: `visibility-report-{domain-name}-{date}.md`

## Step 9: Next steps

After the report, offer:
- `/aeko-action-center <domain-id>` — if the report surfaces prioritized gaps, check whether the web UI has already queued Action items that address them
- `/aeko-brand-kit <domain-id>` — if Brand Kit fields showed up as missing/weak in the report
- `/competitive-research <competitor>` — if the report's competitive section needs deeper per-competitor analysis
