---
name: aeo-audit
description: >
  Audit any URL or HTML file for AEO readiness. Checks structured data,
  heading hierarchy, entity markup, content citability, and FAQ coverage.
  Produces a weighted composite score with severity-classified fixes.
  Use when analyzing a page for AI engine optimization opportunities.
argument-hint: <url-or-file-path>
allowed-tools: Read, Glob, WebFetch
---

# AEO Audit — AI Engine Optimization Readiness Check

You are performing a comprehensive AEO audit on a URL or local HTML file.

## Step 1: Fetch the page content

- If the input is a **URL**: use `WebFetch` to retrieve the page content.
- If the input is a **file path**: use `Read` to read the local file.

Extract and note:
- Full HTML content
- Any existing `<script type="application/ld+json">` blocks
- Meta tags (title, description, og:tags)
- `<html lang="...">` attribute

### Step 1b: Fetch crawler-access files (URL inputs only)

The page HTML alone can't tell you whether AI crawlers are even *allowed* to read it — that lives in
`robots.txt` and `llms.txt`. Don't classify crawler-blocking or "no llms.txt" as findings unless you
actually fetched them. For a **URL** input, derive the origin (`https://<host>`) and `WebFetch` both,
best-effort:

- `https://<host>/robots.txt` — note whether `GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`,
  `Google-Extended`, and `*` are `Allow`ed or `Disallow`ed. A 404 means "no robots.txt → nothing blocked."
- `https://<host>/llms.txt` — note present (200) or absent (404).

Record `crawler_access = {robots_fetched, llms_present, blocked_bots[]}`.

For a **local file** input there is no origin, so these can't be assessed. Set
`crawler_access = "not assessed (local file)"` and, in every later step, mark robots.txt / llms.txt
findings as **"not assessed — re-run on the live URL"** rather than asserting them. Never claim a
crawler is blocked when you never fetched `robots.txt`.

## Step 2: Analyze — Product Schema & Structured Data (25% of score)

Check for JSON-LD structured data and evaluate:

### Product schema (if applicable)
| Check | Points | Description |
|-------|--------|-------------|
| `@type: Product` present | 10 | Basic product schema exists |
| `name` field | 5 | Product name defined |
| `description` (50+ chars) | 10 | Meaningful description |
| `brand` defined | 5 | Brand entity present |
| `offers` with price | 10 | Price information structured |
| `aggregateRating` | 10 | Review data structured |
| `sku` / `gtin` / `mpn` | 5 | Product identifiers present |
| `image` | 5 | Product image referenced |
| `availability` | 5 | Stock status structured |
| `shippingDetails` | 5 | Shipping info structured |
| `hasMerchantReturnPolicy` | 5 | Return policy structured |
| `speakable` | 3 | Voice assistant extraction markup |
| `sameAs` (2+ links) | 5 | Brand authority links |

### FAQPage schema
| Check | Points | Description |
|-------|--------|-------------|
| `@type: FAQPage` present | 10 | FAQ schema exists |
| 3+ FAQ items | 5 | Sufficient FAQ coverage |
| Answers 50+ chars each | 5 | Meaningful answers |

### Organization / Brand schema
| Check | Points | Description |
|-------|--------|-------------|
| Organization or Brand schema | 5 | Brand entity defined |
| `sameAs` links | 5 | Social profiles linked |

**Normalize this category to 0-100, then weight at 25%.**

## Step 3: Analyze — Content Citability (25% of score)

Evaluate how well the content can be extracted and cited by AI engines. **Score against the same AEO
frameworks AEKO content generation writes to** — BLUF, PREP, and Informational Gain — so an audit finding
maps directly to a fix (a weak BLUF score → "apply BLUF"). The five sub-dimensions below are those
frameworks made measurable; E-E-A-T is scored separately in Step 5. (The canonical framework definitions
live in `skills/aeko-create-content/references/aeo-frameworks.md`; this rubric is self-contained, so the
audit still runs standalone if that file isn't present.)

### BLUF — Bottom Line Up Front (30% of citability)
*Does the content lead with the answer?* AI engines lift the direct answer to a question; a buried answer
has no clean extraction point.
- Does each section open with a 1-2 sentence direct answer (not a topic preamble)?
- Are there definition patterns? ("X is a Y that Z")
- Can the first 40-60 words of each section stand alone?

**Scoring:**
- 90-100: Every section has clear opening answer, "X is..." patterns present
- 70-89: Most sections have identifiable answers
- 50-69: Answers are buried mid-paragraph
- 30-49: Long paragraphs with no clear answer extraction point
- 0-29: No identifiable standalone answers

### PREP — self-contained Point·Reason·Example·Point blocks (25% of citability)
*Is each block a complete, liftable unit?* A passage shaped Point → Reason → Example → Point can be cited
whole and still make sense.
- Does each passage explicitly name its subject (not just pronouns)?
- Can each section be understood without reading surrounding content?
- Is there a visible Point→Reason→Example pattern (claim, then *why*, then a concrete instance)?
- Are passages 50-200 words? (Optimal: 80-167 words for products, 134-167 for blog)

### Structural readability — supports BLUF/PREP extraction (20% of citability)
- Clean heading hierarchy (H1 > H2 > H3, no skipped levels)
- Question-based headings (triggers AI citation)
- Short paragraphs (2-4 sentences)
- Tables for comparisons, lists for features

### Informational Gain — specificity / statistical density (15% of citability)
*Concrete numbers an AI answer can't generate generically.*
- Percentages, dollar amounts, specific numbers with context
- Named sources (research, studies, industry reports)
- Year references for freshness signals

**Scoring:**
- 90-100: 5+ stats per 500 words with named sources
- 70-89: 3-4 stats per 500 words
- 50-69: 1-2 stats per 500 words
- 30-49: <1 stat per 500 words
- 0-29: No quantitative data

### Informational Gain — originality / contrarian / first-party (10% of citability)
*Does the page say something a generic answer can't?* This is the highest-value AEO signal — derivative
content earns no citation.
- First-party data / lived experience ("our research", "we tested", "we found")
- A specific cohort served, or a defensible contrarian/non-obvious claim
- Case studies with specific outcomes; original frameworks or methodologies
- Proprietary product specifications

**Combine sub-scores using the weights above → Citability Score 0-100, weighted at 25%.**

## Step 4: Analyze — Technical Infrastructure (20% of score)

### Heading hierarchy
- H1 present and contains product/brand name
- Logical H2/H3 structure
- No skipped heading levels

### Meta tags
- `<title>` contains product + brand
- `<meta name="description">` is 120-160 chars
- Open Graph tags present
- `<html lang>` matches content language

### Technical signals
- Content is server-rendered (not JS-only)
- Page load is not gated behind login/paywall
- Images have alt text
- Canonical URL is set

**Normalize to 0-100, weight at 20%.**

## Step 5: Analyze — Content Quality & E-E-A-T (20% of score)

### Content depth
- Product description length (aim for 150+ words)
- Entity density — brand/product mentioned naturally 2-3 times
- Benefit-oriented language vs feature-only
- FAQ section present in visible content

### E-E-A-T signals
- **Experience**: First-hand usage details, original photos, "we tested"
- **Expertise**: Technical specifications, industry terminology used correctly
- **Authoritativeness**: Brand mentions, expert attribution, certifications
- **Trust**: Transparent pricing, clear contact info, return policy visible

**Normalize to 0-100, weight at 20%.**

## Step 6: Analyze — Platform Readiness (10% of score)

### Crawler access (from Step 1b — URL inputs only)
- AI crawlers allowed in `robots.txt` (`GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`,
  `Google-Extended`, `*`) — a blocked crawler is the hardest cap on AI visibility (the engine can't read
  the page at all), so weight this heavily within the category.
- `llms.txt` present.
- If `crawler_access == "not assessed (local file)"`, **score Platform Readiness on the remaining signals
  only** and state in the report that crawler access was not assessed — do not assume allowed *or* blocked.

### Extractability
- Is content structured for extraction by ChatGPT, Gemini, Perplexity?
- Are there FAQ blocks that match common AI query patterns?
- Is pricing/shipping/return info extractable?
- Does the brand have sameAs links to knowledge bases?

**Normalize to 0-100, weight at 10%.**

## Step 7: Calculate Composite Score

Compute the weighted composite AEO score:

```
AEO Score = (Schema × 0.25) + (Citability × 0.25) + (Infrastructure × 0.20)
          + (Content Quality × 0.20) + (Platform Readiness × 0.10)
```

### Score interpretation:
| Range | Grade | Assessment |
|-------|-------|------------|
| 90-100 | A | Excellent — well-optimized for AI engines |
| 75-89 | B | Good — strong foundation with room for improvement |
| 60-74 | C | Fair — several areas need attention |
| 40-59 | D | Poor — significant gaps in AI visibility |
| 0-39 | F | Critical — major barriers to AI engine visibility |

## Step 8: Classify issues by severity

Group all findings by severity with fix timelines. **Only list a robots.txt / llms.txt / crawler-blocking
finding when Step 1b actually fetched those files** (URL inputs). For a local-file audit, put a single line
under the relevant tier: "Crawler access (robots.txt, llms.txt) — not assessed; re-run on the live URL."
Never assert a crawler is blocked or llms.txt is missing on evidence you don't have.

### Critical (fix within 1 week)
- All AI crawlers blocked via robots.txt
- No JSON-LD structured data at all
- JS-only rendering with no SSR
- 5xx server errors on key pages
- Brand unrecognized as entity

### High (fix within 2 weeks)
- Key AI crawlers blocked (GPTBot, GoogleOther)
- No llms.txt file
- Missing Product/Organization schema
- No FAQ content
- No author or brand attribution
- No shipping/return policy in structured data

### Medium (fix within 1 month)
- Partial crawler blocking
- Incomplete llms.txt
- Citability score below 50
- Missing aggregateRating
- Thin author bios
- Missing speakable markup

### Low (fix within quarter)
- Minor schema validation errors
- Missing alt text on some images
- Content freshness issues
- Missing Open Graph tags
- Poor heading hierarchy
- Missing sameAs links

## Step 9: Generate the report

Output a structured report:

### Header
```
AEO Audit Report: [page title or URL]
Composite Score: XX/100 (Grade: X)
Date: [today]
```

### Score breakdown
| Category | Weight | Score | Weighted |
|----------|--------|-------|----------|
| Product Schema & Structured Data | 25% | XX/100 | XX |
| Content Citability | 25% | XX/100 | XX |
| Technical Infrastructure | 20% | XX/100 | XX |
| Content Quality & E-E-A-T | 20% | XX/100 | XX |
| Platform Readiness | 10% | XX/100 | XX |
| **Composite Score** | **100%** | | **XX/100** |

### Issues by severity
List all issues grouped by Critical → High → Medium → Low.

### Action plan

**Quick Wins (this week)**
Items that are high impact + low effort. Example:
- Add `<script type="application/ld+json">` Product schema
- Unblock GPTBot in robots.txt

**Medium-Term (this month)**
- Create llms.txt file
- Add FAQ schema with 5+ real customer questions
- Optimize product descriptions for citability

**Strategic (this quarter)**
- Build Wikipedia/Wikidata brand presence
- Create original content with first-party data
- Implement speakable markup for voice assistants

### Top 5 fixes (ranked by composite impact)

For each fix, provide:
1. **What to fix** — specific issue
2. **Why it matters** — how it affects AI engine visibility
3. **How to fix it** — exact code or content change needed
4. **Score impact** — estimated improvement to composite score

## Step 10: Next steps

This skill is standalone — it does not fetch AEKO items or write to a store.

After the audit, point the user at:
- `/aeko-action-center <domain-id>` — if the URL belongs to an AEKO-connected domain and they want to queue fixes as actionable items
- `/aeko-brand-kit <domain-id>` — if missing brand context showed up in the audit (no Organization schema, no persona tone, etc.)
- `/aeko-brand-competitor-analysis <competitor-or-url>` — if the audit surfaced a competitor worth benchmarking against
