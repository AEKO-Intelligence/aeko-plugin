---
recipe: pdp-scaffold
purpose: Skeletal HTML scaffold for the AEKO structured PDP description block
load_when: SKILL.md §5 generates HTML for any image_strategy
---

# PDP HTML scaffold

Skeletal — adapt per brand voice + Plan.md prose. Section names should be localized per `frontmatter.target_language`.

```html
<section class="aeko-hero">
  <h2>{{product_name}}</h2>
  <p>{{direct_answer_lead — 1-2 sentences answering "what is this?"}}</p>
</section>
<section class="aeko-benefits">
  <h2>주요 특징</h2> <!-- or i18n equivalent -->
  <ul>...</ul>
</section>
<section class="aeko-usage">
  <h2>사용 방법</h2>
  <p>...</p>
</section>
<section class="aeko-faq">
  <h2>자주 묻는 질문</h2>
  <div>...</div>
</section>
<section class="aeko-cta">
  <h2>구매 안내</h2> <!-- KO; EN: "Purchase info". Section is for price / return / warranty / contact prose. NOT a CTA — see "No action elements" rule in responsive-html-contract.md -->
  <p>...</p>
</section>
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[...every preserved and approved schema node...]}</script>
```

## Strategy branches

- **`preserve_existing`:** call `aeko_get_product_description(integration_id, external_product_id)` to fetch
  the raw editable description HTML. Keep `<new_structured_section_html>` as its own value and validate only
  that new section against the responsive contract. Build the full preview/write value exactly once as
  `<existing_html>` + `\n<!-- AEKO structured content -->\n` + `<new_structured_section_html>`. Never treat
  that full value as the new section or append it to `<existing_html>` again. The live API has no append
  primitive: this is a high-risk full-field replacement and is unavailable unless the saved `before.html`,
  byte-identical prefix, nondecreasing `<img>` count, JSON-LD merge, and stale-base gates all pass. JSON-LD
  is one consolidated `@graph`, carrying forward every existing node.
- **`rebuild_from_existing`:** scaffold from scratch. `<img src>` values use the URLs captured in Step 4.
- **`rebuild_with_local`:** scaffold from scratch. Local preview may use base64 data URIs. Live write-back
  is unavailable until every source is uploaded/resolved to a store-accessible URL; the final payload may
  contain no placeholder, data URI, or local filesystem path.

`aeko-cta` is a legacy class name for informational purchase facts, not an action component. Omit the whole
section when shipping/returns/contact facts already appear visibly in the host shell; record
`already_in_host_shell` instead of duplicating them. Never drop a unique verified fact that exists nowhere
else.

## Brand-specific override

If `references/examples/pdp-html-example.html` exists, use its section ordering, heading copy, and class-name conventions in place of the scaffold defaults. Acceptance gates in `responsive-html-contract.md` still apply on top.
