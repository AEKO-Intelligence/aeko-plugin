---
name: aeko-source-analysis
description: >
  Analyzes either one tracked prompt's complete AI response and citation
  footprint or one cited page against verified brand, Context, and official
  product evidence. Use for source analysis, citation winners, cited-page claim
  checks, and correction or outreach drafts. Read-only.
argument-hint: "<prompt-id> [window] | domain_id=<uuid> source_id=<uuid>"
allowed-tools: Read, ToolSearch, aeko_fetch_source_content, aeko_get_domain_info, aeko_get_tracked_prompt, aeko_list_contexts, aeko_list_store_products, aeko_get_product_description, WebFetch, Write, aeko_get_active_brand_package, aeko_get_brand_package_version, aeko_read_brand_package_file, aeko_list_brand_wiki_pages, aeko_get_brand_wiki_page
---

# AEKO Source Analysis

Analyze why an AI answer cites a source, or check what one cited page says against evidence the brand
controls. Both modes are read-only: never mutate tracking state, create an ActionItem, change a store,
edit a page, post a draft, or publish.

## User-facing language

Mirror the user's chat language. In English, call this **source analysis**. In Korean user-facing copy,
call it **AI 답변 참고 출처**. Keep IDs, URLs, schema keys, quoted evidence, paths, and tool names in
English/ASCII. The brand mark is always `AEKO`.

## Select one mode

Read `references/brand-execution-contract.md` and `references/brand-output-eval.md`. Preserve the whole
original `task_prompt`, selected mode/window, verified brand/domain and package/eval versions. Defaults
work without a custom package. Prompt ownership alone does not identify a brand in a multi-brand account;
if the current brand is unknown, analyze the prompt generically and do not apply customer rules or claim
which mention is "ours". Only the cited-page mode's verified domain or explicit verified task context
permits that comparison.

Scope rules apply to authored analysis/corrections, never to changing quoted source evidence. Evaluate
the exact report and any outreach draft before saving/accepting them; required failures/unavailable checks
block the affected artifact. Preserve the original task and brand/eval context with any follow-up command;
neither an action recommendation nor an outreach draft is permission to execute or post it.

Retain at most 256 KiB of source text per run (or a lower job limit), within the selected mode's call caps.
If a complete prompt payload cannot fit, report the limit and request a narrower supported window in an
interactive run; unattended runs stop that analysis. Do not silently discard response bodies/citations
and call the report complete. Keep required rules/evals intact, separate from the evidence budget.

1. **Prompt mode** — a positional `<prompt-id>`, optionally followed by `latest`, `7d`, `30d`, or `90d`.
   Also accept `mode=prompt prompt_id=<uuid> [window=<value>]`.
2. **Cited-page mode** — both `domain_id=<uuid>` and `source_id=<uuid>`, optionally with
   `mode=cited-page`.

If both shapes are present, ask which mode the user wants. If neither is complete, show both runnable
forms and stop:

```text
/aeko-source-analysis <prompt-id> [window]
/aeko-source-analysis domain_id=<uuid> source_id=<uuid>
```

Before making any tool call, read the selected reference completely and follow it as the authoritative
workflow:

- prompt mode → `references/prompt-mode.md`
- cited-page mode → `references/cited-page-mode.md`

Do not combine the modes automatically. A cited-page check may use up to five associated prompt payloads
only through its bounded workflow; prompt mode may inspect many citations but must not turn that into an
unbounded product-catalog scan.

## Evidence preservation contract

In prompt mode, retain the complete richness returned by `aeko_get_tracked_prompt`: response bodies;
each citation's `domain`, `source_url`, `position_in_response`, and `context_snippet`; crawl JSON-LD
`@type` values; citability/source-analysis signals; and cited-page extracted text. Never collapse this
payload into counts alone. Preserve backend truncation flags and distinguish cached crawl evidence from
the single-page live fallback.
