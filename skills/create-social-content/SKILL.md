---
name: create-social-content
description: >
  Generate platform-specific social media posts for a product targeting a
  specific international market. Uses AEKO analysis data to craft posts that
  highlight competitive advantages and match market preferences.
argument-hint: <product-name-or-analysis-id>
allowed-tools: Read, Glob, WebFetch
---

# Create Social Content — Multi-Platform Posts

You are creating social media content for a specific product targeting
a specific international market.

## Step 1: Identify product and platforms

- Parse the user's input for product name, domain, or analysis ID
- Ask which platforms to target (default: Instagram, Facebook, Twitter/X, LinkedIn)
- Call `aeko_get_domain_info` to get domain context

## Step 2: Get content brief

- Call `aeko_get_suggestions` with the domain_id
- Find the `content_social_*` suggestion matching the product
- Extract the `content_brief` object with:
  - `product_title`, `product_url`, `country`, `language`
  - `product_summary`, `competitive_advantages`
  - `competitor_names`, `market_positioning`

## Step 3: Get full analysis

- Call `aeko_get_product_analysis` with the analysis_id
- Note pricing, key features, and unique selling points
- Understand the target market context

## Step 4: Load product images

- Call `aeko_list_product_images` to see available photos
- Call `aeko_read_product_image` for the best hero/lifestyle shots
- Select images appropriate for each platform:
  - Instagram: visually striking, square/vertical format
  - Facebook: engaging, horizontal or square
  - Twitter/X: attention-grabbing, horizontal
  - LinkedIn: professional, informative

## Step 5: Generate platform-specific posts

Create posts tailored to each platform's format and audience:

### Instagram
- **Caption**: Up to 2,200 chars, but keep core message in first 125 chars (before "more")
- **Hashtags**: 20-30 relevant hashtags (mix of broad + niche + branded)
- **Tone**: Visual-first, lifestyle-oriented, aspirational
- **Include**: Product benefits, lifestyle context, call-to-action
- **Language**: Target market language from content_brief

### Facebook
- **Post**: 100-250 words, conversational tone
- **Include**: Link to product page, key benefit, social proof if available
- **Tone**: Community-oriented, informative
- **CTA**: Clear next step (shop now, learn more, comment)

### Twitter/X
- **Tweet**: 280 characters max
- **Thread option**: 3-5 tweet thread for detailed product story
- **Hashtags**: 2-3 max
- **Tone**: Concise, punchy, newsworthy angle

### LinkedIn
- **Post**: 150-300 words, professional tone
- **Angle**: Industry insight, market trend, business value
- **Include**: Data points, competitive context, thought leadership angle
- **Hashtags**: 3-5 professional/industry tags

## Step 6: Adapt for target market

- All content in the target language (content_brief.language)
- Cultural context appropriate for the target country
- Local platform preferences (e.g., LINE for Japan, WeChat for China)
- Currency and measurement units matching the target market

## Step 7: Save and output

- Call `aeko_save_content` for each platform: `social-{product-slug}-{platform}-{country}.md`
- Present all posts organized by platform
- Include image recommendations for each post
- Note character counts and any platform-specific formatting

## Step 8: Report completion

- If this task was triggered by an AEKO suggestion, call `aeko_complete_suggestion` with the suggestion's `key` to mark it as done in the dashboard.
- The key follows the pattern `content_social_{analysis_id}`.
