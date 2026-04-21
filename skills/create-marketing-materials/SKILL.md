---
name: create-marketing-materials
description: >
  Meta-skill for generating various marketing materials using AEKO analysis data.
  Supports product descriptions, email newsletters, landing page copy, press
  releases, and ad copy — all optimized for AI engine visibility.
argument-hint: <product-name-or-analysis-id>
allowed-tools: Read, Glob, WebFetch
---

# Create Marketing Materials — AEO-Optimized Content

You are creating marketing materials for a specific product targeting
a specific international market, using AEKO analysis data.

## Step 1: Ask what type of material

Present the user with options:
1. **Product description rewrite** — AEO-optimized product page copy
2. **Email newsletter** — Product announcement or feature spotlight
3. **Landing page copy** — Dedicated product or campaign landing page
4. **Press release** — Product launch or milestone announcement
5. **Ad copy** — Google Ads, Meta Ads, or display advertising

## Step 2: Gather AEKO data

Regardless of material type, gather the same foundation:

- Call `aeko_get_domain_info` for domain context
- Call `aeko_get_suggestions` to find `content_creation` suggestions and extract `content_brief`
- Call `aeko_get_product_analysis` for detailed competitor and market data
- Call `aeko_list_product_images` and `aeko_read_product_image` for visual context
- Call `aeko_search_research_prompts` for consumer query patterns

## Step 3: Generate content by type

### Product Description Rewrite
- Rewrite the product description for AI engine readability
- Include: brand name, key specs, benefits, use cases, comparison context
- Structure: Short summary (1-2 sentences) → detailed description → key features list → FAQ
- AEO focus: Complete sentences AI can quote, natural entity mentions, structured data hints
- Generate matching Product JSON-LD via `aeko_prepare_json_ld`

### Email Newsletter
- Subject line options (3 variants with A/B testing angle)
- Preview text (40-90 chars)
- Body: Hook → product story → key benefits → social proof → CTA
- Include competitive positioning subtly (why this over alternatives)
- Personalization tokens where appropriate

### Landing Page Copy
- Hero section: Headline + subheadline + CTA
- Problem/solution section
- Features & benefits (with competitor comparison context)
- Social proof / testimonials section
- FAQ section (from research prompts)
- Final CTA section
- Generate WebSite or Product JSON-LD as appropriate

### Press Release
- Headline + subheadline
- Dateline + opening paragraph (who, what, when, where, why)
- Quote from company representative
- Product details and market context
- Boilerplate "About [Company]"
- Media contact information placeholder

### Ad Copy
- Google Ads: Headlines (30 chars x3) + Descriptions (90 chars x2)
- Meta Ads: Primary text + Headline + Description + CTA
- Display: Short (25 chars) + Medium (50 chars) + Long (90 chars)
- All variants highlighting different competitive advantages
- Include negative keywords and audience targeting suggestions

## Step 4: AEO optimization pass

For all content types, ensure:
- Brand name appears naturally and consistently
- Key product attributes are stated as complete, quotable sentences
- Competitive advantages are woven in (not just feature lists)
- Content addresses real consumer queries (from research prompts)
- Target market language and cultural context are correct

## Step 5: Save and output

- Call `aeko_save_content` with descriptive filename
- Present the content formatted and ready to use
- Include any structured data (JSON-LD) separately
- Summarize: content type, target market, key themes, word count
