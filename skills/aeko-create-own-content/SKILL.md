---
name: aeko-create-own-content
description: >
  Own Store · Content. Drafts a blog article, FAQ page, or landing content on
  the user's own domain based on an AEKO v2 content brief. Matches the brief's
  structure, persona, tone, and required JSON-LD.
argument-hint: <suggestion-key>
allowed-tools: Read, Write
---

# AEKO · Create Own-Store Content

You are executing a single `own_content` suggestion from AEKO v2.

## Step 1: Load the brief

Call `aeko_get_content_brief(suggestion_key)`. Verify the category is `own_content`. The brief tells you:
- `target_domain` and (optionally) `target_url` — new page URL or existing page to expand
- `content_type` — `article`, `faq`, `landing`, etc.
- `structure` — required section order (e.g. `h1`, `intro`, `h2: Firmness`, `table: comparison`, `h2: FAQ`, `faq_block`)
- `topics`, `persona`, `tone`, `word_count_target`
- `required_jsonld` and `must_include`
- Competitor source evidence — mirror what's already winning citations

## Step 1b: Mirror competitor evidence structure

Before drafting, list the headings from every `source_evidence[].structure` in the brief. **Your draft's H2/H3 spine must be a superset of those headings.** This is the load-bearing differentiator — the brief ships `source_evidence` specifically so you can mirror what is already winning AI citations for these prompts. Do not skip it.

## Step 2: Pull supporting prompt context

Call `aeko_search_research_prompts(scope=<domain scope from aeko_get_domain_info>, keyword=<first topic from brief.topics>)` to see the exact phrasing real users ask AI engines. If a `group_id` was selected in `/aeko-action-center`, prefer narrowing by the group scope. Every major section should answer at least one tracked prompt.

## Step 3: Draft the article

Write the full article in Markdown following `brief.structure` exactly. Rules:
- Answer-block opening for every H2 (the first 2-3 sentences should be directly quotable by an AI engine)
- High statistical density — concrete numbers, comparisons, tables
- Self-contained sections (no "as mentioned above")
- Bilingual (KO + EN) if the domain operates cross-border

## Step 4: Generate JSON-LD

For each type in `brief.required_jsonld` (typically `Article`, `FAQPage`, `BreadcrumbList`), produce complete JSON-LD. Include every field in `brief.must_include`.

## Step 5: Save and complete

1. `aeko_save_content("content/own/<slug>.md", <article markdown>)`
2. `aeko_save_content("content/own/<slug>.jsonld.json", <JSON-LD>)`
3. `aeko_complete_suggestion(suggestion_key)` — if this fails, surface the exact error to the user.

Report the files saved, the prompts the article is designed to capture, and how the user should publish it. Korean-seller platform hints:
- **Shopify blog**: admin → Blog posts → paste markdown
- **Cafe24 게시판**: 상품관리 → 게시판 → 게시글 등록
- **Naver 블로그 / Tistory / Brunch**: paste markdown into the blog editor (these are high-leverage targets for CLOVA/HyperCLOVA citations)
- Generic: paste into the CMS rich-text editor and add JSON-LD via the theme head.

**Note**: if you have both `/aeko-create-own-content` and `/create-blog-article` available, prefer this one — it uses the v2 brief with competitor evidence and persona. `/create-blog-article` is the legacy flow without briefs.
