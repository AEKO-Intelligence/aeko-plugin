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

- If the input is a **URL**: use `WebFetch` to retrieve the page content
- If the input is a **file path**: use `Read` to read the local file

Extract and note:
- Full HTML content
- Any existing `<script type="application/ld+json">` blocks
- Meta tags (title, description, og:tags)
- `<html lang="...">` attribute

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

Evaluate how well the content can be extracted and cited by AI engines.

### Answer Block Quality (30% of citability)
- Does each section open with a 1-2 sentence direct answer?
- Are there definition patterns? ("X is a Y that Z")
- Can the first 40-60 words of each section stand alone?

**Scoring:**
- 90-100: Every section has clear opening answer, "X is..." patterns present
- 70-89: Most sections have identifiable answers
- 50-69: Answers are buried mid-paragraph
- 30-49: Long paragraphs with no clear answer extraction point
- 0-29: No identifiable standalone answers

### Passage Self-Containment (25% of citability)
- Does each passage explicitly name its subject (not just pronouns)?
- Can each section be understood without reading surrounding content?
- Are passages 50-200 words? (Optimal: 80-167 words for products, 134-167 for blog)
- Are specific facts included rather than vague claims?

### Structural Readability (20% of citability)
- Clean heading hierarchy (H1 > H2 > H3, no skipped levels)
- Question-based headings (triggers AI citation)
- Short paragraphs (2-4 sentences)
- Tables for comparisons, lists for features

### Statistical Density (15% of citability)
- Percentages, dollar amounts, specific numbers with context
- Named sources (research, studies, industry reports)
- Year references for freshness signals

**Scoring:**
- 90-100: 5+ stats per 500 words with named sources
- 70-89: 3-4 stats per 500 words
- 50-69: 1-2 stats per 500 words
- 30-49: <1 stat per 500 words
- 0-29: No quantitative data

### Uniqueness Signals (10% of citability)
- First-party data ("our research", "we found")
- Case studies with specific outcomes
- Original frameworks or methodologies
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

Group all findings by severity with fix timelines:

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
- `/competitive-research <competitor-or-url>` — if the audit surfaced a competitor worth benchmarking against
