---
name: aeko-create-external-content
description: >
  Other Media · Content. Drafts content for external media — partner blogs,
  Wikipedia entries, guest posts — based on an AEKO v2 brief. Outputs
  ready-to-paste artifacts; does NOT publish anywhere.
argument-hint: <suggestion-key>
allowed-tools: Read, Write
---

# AEKO · Create External-Media Content

You are executing a single `external_content` suggestion from AEKO v2. The goal is to draft content that will live on someone else's domain (partner blog, Wikipedia, industry press) to earn third-party citations.

## Step 1: Load the brief

Call `aeko_get_content_brief(suggestion_key)`. Verify category is `external_content`. The brief specifies:
- `target_domain` — the external site (e.g. `wikipedia.org`, partner blog domain)
- `content_type` — `guest_post`, `wikipedia`, `partner_media`, `press_release`
- `structure`, `topics`, `persona`, `tone`
- `must_include` — required citations, sameAs links, brand entity mentions
- Competitor evidence — which external sources currently win AI citations

## Step 2: Adapt tone to the target platform

Different platforms have different voice requirements:
- **Wikipedia / Namuwiki / Naver 지식백과** — NPOV (neutral point of view), cite reliable third-party sources, no marketing language, follow notability guidelines. Draft as a **local markdown file the human will paste into the platform's editor** — never try to submit it.
- **Partner media / guest post** — editorial tone, value-first, discreet brand mention, outbound link back to the user's domain.
- **Korean blog targets (Naver 블로그, Tistory, Brunch)** — conversational but informative, bilingual KO/EN optional, tagged for Naver search indexing. These are the highest-leverage targets for CLOVA/HyperCLOVA citations.
- **Press release** — AP style, quote from a named exec, embargo line, boilerplate.

Pick the right tone from `content_type` and (if the brief's `target_domain` is a Korean platform) prefer Korean as the primary language with optional EN translation appended.

## Step 2b: Mirror competitor evidence structure

Before drafting, list the headings from every `source_evidence[].structure` in the brief. **Your draft's H2/H3 spine must be a superset of those headings.** This is the load-bearing step — the brief ships `source_evidence` specifically so you can mirror what is already winning AI citations for these prompts. Do not skip it.

## Step 3: Pull supporting prompt context

Call `aeko_search_research_prompts` to ground the content in real AI queries. The goal is for this external piece to *become* a source AI engines cite when those queries are asked.

## Step 4: Draft

Write the full piece following `brief.structure`. Every factual claim must be supported — cite reputable sources for Wikipedia; include data/quotes for press releases.

## Step 5: Verify brand entity

If the brief mentions the user's brand and `must_include` lists a `sameAs` link, call `aeko_check_brand_entity(brand_name, brand_name_en="<English brand name if known>")` to confirm the brand is recognizable to Wikipedia/Wikidata. If not, warn the user that Wikipedia submission may be rejected for notability.

## Step 6: Save — do NOT publish

**Hard rule**: this skill NEVER publishes anything. Never call `WebFetch`, `curl`, `HTTP POST`, or any tool that could send the draft to a third party. If a future edit adds network tools to `allowed-tools`, refuse to use them for submission. You only write local files.

1. `aeko_save_content("content/external/<target_domain>/<slug>.md", <draft>)`
2. If a pitch email is needed: `aeko_save_content("content/external/<target_domain>/<slug>.pitch.md", <pitch>)`
3. `aeko_complete_suggestion(suggestion_key)` — if this fails (e.g. key invalid, already completed), surface the exact error message to the user.

Report: files saved, what platform they're for, and explicit next steps for the human (submit to editor, file Wikipedia draft, send pitch email). This skill never auto-publishes.
