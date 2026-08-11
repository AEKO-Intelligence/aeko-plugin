---
name: aeko-competitor-analysis
description: >
  Compares competitors at scope=brand or scope=product. The public
  WebSearch/WebFetch stage works without an AEKO account; when connected, the
  skill adds tracked-prompt citations, visibility, domain, and official product
  evidence. Use for brand positioning or PDP comparison matrices.
argument-hint: "scope=brand [domain-id] <competitor> | scope=product <product-id-or-url> [competitor-urls...]"
allowed-tools: aeko_list_domains, aeko_get_domain_info, aeko_get_product_description, aeko_list_store_integrations, aeko_search_research_prompts, aeko_get_tracked_prompts, aeko_get_tracked_prompt, aeko_get_visibility_summary, WebSearch, WebFetch, Write
---

# AEKO Competitor Analysis

Compare either a competitor brand's positioning or one product against comparable PDPs. Always preserve
the public research half when AEKO is absent or returns 401; the connected layer adds private measurement
and official product grounding but is never a prerequisite for public evidence.

Language: mirror the user's chat language for headings, findings, questions, caveats, and next actions.
Keep `scope`, IDs, URLs, paths, schema keys, slash commands, and tool names in English/ASCII. The brand mark
is always `AEKO`.

## Select one scope

- `scope=brand` — accept an optional AEKO domain ID and one competitor name or root domain; read
  `references/brand-mode.md` completely.
- `scope=product` — accept the user's product ID or URL plus optional competitor PDP URLs; read
  `references/product-mode.md` completely.

If `scope` is missing, infer it only from explicit wording or an unmistakable product URL/ID. Otherwise ask
the user to choose `brand` or `product`. Do not run both scopes in one invocation.

## Public-first degradation contract

Run the selected reference's WebSearch/WebFetch evidence stage even when no AEKO connector is exposed.
If an AEKO tool is unavailable, unauthenticated, or returns 401, keep the public report and label only the
connected comparison unavailable. Never convert a missing AEKO account into failure of the public half,
and never invent private metrics to fill it. If the public comparison needs the user's own brand/product
label and AEKO cannot supply one, ask the user for that public name or URL; if they decline, deliver a clearly
labeled competitor-only public section rather than failing.
