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
<script type="application/ld+json">{...Product schema...}</script>
<script type="application/ld+json">{...FAQPage schema...}</script>
<!-- if reviews_payload non-empty: -->
<script type="application/ld+json">{...Review / AggregateRating...}</script>
```

## Strategy branches

- **`preserve_existing`:** call `aeko_get_product_description(integration_id, external_product_id)` to fetch the raw editable description HTML. Output = `<existing_html>` + `\n<!-- AEKO structured content -->\n` + `<new_structured_section>`. New section uses the scaffold above. JSON-LD blocks still render inside the new section (not duplicated in the preserved block).
- **`rebuild_from_existing`:** scaffold from scratch. `<img src>` values use the URLs captured in Step 4.
- **`rebuild_with_local`:** scaffold from scratch. Local preview uses base64 data URIs; write-back artifact uses `{{LOCAL_IMAGE_N}}` placeholders + upload checklist.

## Brand-specific override

If `references/examples/pdp-html-example.html` exists, use its section ordering, heading copy, and class-name conventions in place of the scaffold defaults. Acceptance gates in `responsive-html-contract.md` still apply on top.
