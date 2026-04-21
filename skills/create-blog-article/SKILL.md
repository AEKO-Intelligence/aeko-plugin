---
name: create-blog-article
description: >
  Create an AEO-optimized blog article for a specific product and target market.
  Uses AEKO analysis data (competitive advantages, market positioning, consumer
  queries) to write content that AI engines can easily understand and cite.
argument-hint: <product-name-or-analysis-id>
allowed-tools: Read, Glob, WebFetch
---

# Create Blog Article — AEO-Optimized Content

You are creating a blog article optimized for AI Engine visibility for a specific
product in a specific target market.

## Step 1: Identify product & domain

- Parse the user's input for product name, domain, or analysis ID
- Call `aeko_get_domain_info` to get the domain context
- If the user provided a domain_id, use it. Otherwise, ask.

## Step 2: Get content brief

- Call `aeko_get_suggestions` with the domain_id
- Find the `content_blog_*` suggestion matching the product
- Extract the `content_brief` object which contains:
  - `product_title`, `product_url`, `country`, `language`
  - `product_summary`, `market_positioning`
  - `competitive_advantages` — key selling points to highlight
  - `competitive_gaps` — areas to address or differentiate
  - `ai_visibility_notes` — current AI visibility status
  - `competitor_names` — top competitors to position against
  - `comparison_properties` — feature comparison data

## Step 3: Get full analysis

- Call `aeko_get_product_analysis` with the analysis_id (from suggestion's `entity_id`)
- Extract detailed competitor data, pricing info, and market context
- Note the target country and language from the analysis

## Step 4: Load product images

- Call `aeko_list_product_images` to see available product photos
- Call `aeko_read_product_image` for the most relevant images (hero shot, detail shots)
- Use visual context to write accurate product descriptions

## Step 5: Research consumer queries

- Call `aeko_search_research_prompts` with keywords from the product title and the target country
- Identify common consumer questions and search patterns
- These queries become natural section headings and FAQ items in the article

## Step 6: Write the blog article

Using all gathered data, write an AEO-optimized blog article following these principles:

### Structure
- **Title**: Include product name + primary benefit + target market context
- **Introduction**: Address a common consumer question (from research prompts)
- **Body sections**: Each section addresses a competitive advantage or consumer concern
- **Comparison section**: Natural comparison with competitors (using comparison_properties)
- **FAQ section**: 3-5 questions derived from research prompts
- **Conclusion**: Clear recommendation with supporting evidence

### AEO Best Practices
- Write in natural language that AI engines can quote directly
- Include the brand name 3-5 times naturally throughout
- Use structured headings (H2/H3) that match common query patterns
- Include specific data points (prices, specs, ratings) that AI can extract
- Write complete sentences that make sense when quoted out of context
- Address "why this product" and "compared to alternatives" questions directly
- Use the target market's language (from content_brief.language)

### Tone & Style
- Informative and trustworthy, not promotional
- Evidence-based claims with specific details
- Acknowledge limitations honestly (builds EEAT credibility)
- Write for the target market's cultural context

## Step 7: Generate Article JSON-LD

- Call `aeko_prepare_json_ld` with schema_type="Article" and the domain_id
- Generate a complete BlogPosting JSON-LD block for the article

## Step 8: Save & output

- Call `aeko_save_content` with filename like `blog-{product-slug}-{country}.md`
- Present the complete article as copyable markdown
- Include the JSON-LD block separately for the user to add to their page
- Summarize: word count, target market, key themes covered, SEO/AEO elements included

## Step 9: Report completion

- If this task was triggered by an AEKO suggestion, call `aeko_complete_suggestion` with the suggestion's `key` to mark it as done in the dashboard.
- The key follows the pattern `content_blog_{analysis_id}` — use the entity_id from the suggestion.
