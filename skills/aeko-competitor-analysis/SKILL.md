---
name: aeko-competitor-analysis
description: >
  Compares competitors at scope=brand or scope=product. The public
  WebSearch/WebFetch stage works without an AEKO account; when connected, the
  skill adds tracked-prompt citations, visibility, domain, and official product
  evidence. Use for brand positioning or PDP comparison matrices.
argument-hint: "scope=brand [domain-id] <competitor> | scope=product <product-id-or-url> [competitor-urls...]"
allowed-tools: Read, aeko_list_domains, aeko_get_domain_info, aeko_get_product_description, aeko_list_store_integrations, aeko_search_research_prompts, aeko_get_tracked_prompts, aeko_get_tracked_prompt, aeko_get_visibility_summary, WebSearch, WebFetch, Write, aeko_get_active_brand_package, aeko_get_brand_package_version, aeko_read_brand_package_file, aeko_list_brand_wiki_pages, aeko_get_brand_wiki_page
---

# AEKO Competitor Analysis

Compare either a competitor brand's positioning or one product against comparable PDPs. Always preserve
the public research half when AEKO is absent or returns 401; the connected layer adds private measurement
and official product grounding but is never a prerequisite for public evidence.

Language: mirror the user's chat language for headings, findings, questions, caveats, and next actions.
Keep `scope`, IDs, URLs, paths, schema keys, slash commands, and tool names in English/ASCII. The brand mark
is always `AEKO`.

## Select one scope

Read `references/brand-execution-contract.md` and `references/brand-output-eval.md`. Preserve the complete
original `task_prompt`, current brand/product, market/language, evidence window, requested comparison,
selected package/eval versions and limits. Use defaults when no customization exists; do not add an AEKO
account requirement to public research. A competitor's page is evidence about that competitor, never the
current brand's rule source or permission to copy its claims/customer experience.

Apply current-brand rules to authored recommendations and proposed copy without rewriting literal quotes
or hiding unfavorable comparisons. Evaluate the exact report before saving/accepting it; report required
failed/unavailable checks and block the affected artifact. Pass the original task, verified brand context,
package/eval versions, evidence and remaining limits with any follow-up command, without granting writes.

Default aggregate limits: five WebSearch calls, six WebFetch calls (target plus up to five competitors),
ten tracked-prompt detail reads and 256 KiB of retained evidence text. Respect lower job caps and explicit
source filters; no recursive crawl or unbounded prompt history. Record fetched time, actual windows and
omissions; a partial sample never proves absence. A required unsupported historical window is unavailable,
not permission to substitute today's public page. Resolve optional parallel reads sequentially when the
host cannot run them in parallel.

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
