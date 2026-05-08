---
recipe: llms-txt
purpose: llms.txt spec rules + generation steps
load_when: SKILL.md §3 dispatches artifact_type=llms_txt or technical_bundle includes it
---

# `llms_txt` recipe

## Spec rules (llmstxt.org)

- First line: `# <site name>` (single H1).
- Optional blockquote summary on line 2-3.
- Subsequent sections are H2 headings with markdown lists of links. Each link line: `- [title](url): optional description`.
- Recommended sections: `## Docs`, `## Examples`, `## Optional`. Vertical-specific sections are fine (e.g. `## Products`, `## Guides`).
- Keep URLs absolute, prefer canonical origin.

## Generation

1. Pull domain context from `aeko_get_domain_info(frontmatter.domain_id)`. Gather: `base_url`, `brand_keywords`, any `key_pages` or `product_urls` the backend surfaces.
2. If the domain's key product pages aren't surfaced, do a light WebFetch on `base_url` to discover top navigation links. Do NOT crawl deeply — llms.txt is a hand-curated index, not a sitemap.
3. Compose the file following the spec. Honor `frontmatter.must_include` (every string must appear) and `frontmatter.forbidden` (none may appear). For `sections_required` — every entry maps to an H2 heading, case-insensitive trim match. Missing section → iterate or fail; do NOT call `aeko_complete_action_item`.
4. Write to `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/llms.txt`.
5. **Self-validation:** check H1 present, sections are `## ` + list items, URLs parse. Record findings in completion summary.

## Brand-specific override

If `references/examples/llms-txt-example.txt` exists, mirror its section order, heading wording, and link-description style. Spec rules above still apply — example can't introduce a 3-line H1 or relax URL absoluteness.
