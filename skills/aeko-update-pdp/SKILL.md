---
name: aeko-update-pdp
description: >
  PDP executor for Action-tab items with `execution_class=store_write_artifact`.
  Fetches a Plan.md, asks image strategy, WebFetches the live product page +
  images, generates responsive HTML with Product/FAQ/Review JSON-LD, writes
  to the connected Cafe24/Shopify store (shadow product by default), and
  marks complete with full audit trail. Splits the PDP branch out of the
  retired `/aeko-run-action`.
argument-hint: "<item-id>"
allowed-tools: aeko_get_action_plan, aeko_get_brand_kit, aeko_get_product_description, aeko_list_store_integrations, aeko_update_product_description, aeko_update_product_tags, aeko_update_product_meta, aeko_revert_store_write, aeko_list_store_writes, aeko_complete_action_item, Read, Write, WebFetch, Bash
---

# AEKO Update PDP

Executes one Action-tab PDP item end-to-end: fetch Plan.md → parse frontmatter + prose → ask image strategy → WebFetch page + images → generate responsive HTML + JSON-LD → write to store (shadow-by-default) → mark complete.

Contract reference: `docs/contracts/action-item-contract.md` §3 (Plan.md), §7 (shadow product), §6 (completion).

## Input

- `item-id` (required) — `$1`. If missing, stop and point user to `/aeko-action-center <domain_id> pdp`.

## Step 1 — Fetch and parse the Plan.md

Call `aeko_get_action_plan(item_id)`. Parse YAML frontmatter + prose body.

**Validate:**
- `contract_version` starts with `2026-04-17.action.v1.` — else stop.
- Pin this skill to contract minor `v1.2`. Greater minor → print advisory + proceed.
- `tab == "action"` — else stop.
- `execution_class == "store_write_artifact"` — else redirect: `technical_artifact` → `/aeko-fix-technical`, `local_content_artifact` → `/aeko-create-content`.
- `status ∈ {pending, ready}` — else stop with appropriate message.
- `write_target` consistency: must pair with `write_mode` per contract §3 — `shadow_product ↔ shadow`, `append_below_existing ↔ live`, `preview_only ↔ local`. Mismatch → stop.
- `tier_required` gate via `aeko_get_brand_kit(...).metadata.account_tier`.

Print header in `target_language`:
1. Action label — KO: "상품 페이지 개선: `<write_mode>`" / EN: "PDP update: `<write_mode>`"
2. Context: domain, product title (resolve via `target_url` inspection), channels.
3. Persona: `persona_label` if present.

Print prose body verbatim. Never echo raw frontmatter.

## Step 2 — Stale brand-kit check

If `frontmatter.requires_brand_kit == true`:
- Call `aeko_get_brand_kit(frontmatter.domain_id)`. Missing / empty → stop with Brand-Kit-missing message.
- Snapshot-version drift: ask user whether to abort or proceed with snapshot.

## Step 3 — Image strategy (ask user)

Ask in `target_language`:

**KO:**
```
이 PDP를 어떻게 구성할까요?

1. 현재 이미지 유지 + 아래에 구조화된 HTML 추가 (가장 안전)
2. 기존 이미지를 재사용해 처음부터 재구성
3. 로컬 컴퓨터의 새 이미지 파일로 처음부터 재구성

번호를 입력하거나 원하는 접근을 자유롭게 설명해 주세요.
```

**EN:**
```
How should we structure this PDP?

1. Keep current images + add AEO-optimized HTML below (safest)
2. Rebuild from scratch using current PDP images
3. Rebuild from scratch using local image files

Reply with a number or describe the approach you want.
```

Store as `image_strategy ∈ {preserve_existing, rebuild_from_existing, rebuild_with_local}`.

**Strategy ↔ write_mode consistency:**

| `image_strategy` | Allowed `write_mode` values |
|---|---|
| `preserve_existing` | `shadow_product`, `append_below_existing`, `preview_only` |
| `rebuild_from_existing` | `shadow_product`, `preview_only` |
| `rebuild_with_local` | `shadow_product`, `preview_only` |

Rebuild on an `append_below_existing` item → stop: "Rebuilding replaces HTML, so appending to the live description doesn't make sense. Pick strategy 1 or ask me to switch to shadow write." Do NOT silently reassign.

For `rebuild_with_local` — prompt for up to 10 local image paths (absolute). Read each with native `Read` to verify. Inline as data-URI for local preview; in the final artifact for write-back, emit `{{LOCAL_IMAGE_N}}` placeholders + surface upload checklist.

## Step 4 — Fetch current page + images (skip for rebuild_with_local)

If `image_strategy != rebuild_with_local`:

1. `WebFetch(frontmatter.target_url)` → parse HTML to extract the product page structure and image URLs. Store the raw HTML in memory; discover `<img src>` attributes.
2. **Image guardrails** (using what WebFetch gives us — HTML attributes only):
   - Skip `<img>` with `width < 400` or `height < 400` (likely decorative).
   - Skip URLs matching thumbnail patterns (`/thumb/`, `_50x50`, `_100x100`, `-small`, `-thumb`).
   - Cap at 12 images per item. Log `skipped_decorative`, `skipped_thumbnail`, `skipped_overflow` counts.
3. For each remaining image index, fetch the binary via WebFetch (or direct URL save via `Bash(curl -o ...)` if the image content-type isn't handled) and save to `./aeko-artifacts/<domain_id>/<item_id>/img/<idx>.<ext>`. Open each with native `Read` for Claude vision to OCR Korean + English text. Preserve paragraph order.
4. **Review detection pass:** scan OCR text + raw HTML for review-shaped blocks (customer quotes, star ratings, "리뷰 N개", structured review widgets). Build `reviews_payload = [{author, rating, text, date_if_present}]` capped at top-10 recent/high-rated. Null if nothing review-shaped.
5. If every image OCR failed → stop. Do NOT hallucinate copy.

## Step 5 — Generate responsive HTML

Read `prose` for voice/structure guidance, `frontmatter.pdp_responsive_contract.*` for hard rules, live brand kit from Step 2, OCR payload from Step 4.

**Citability baseline** (apply even when prose is silent):
- 80-167 word passages per block.
- Name the subject explicitly in every paragraph (no pronoun opens).
- Each section opens with a 1-2 sentence direct answer.
- "X is a Y that Z" structures for core claims.
- Include specific numbers / dimensions / years where possible.

**`[VERIFY: <field>]` markers** — when a factual value is absent from OCR/brand kit/prose, emit `[VERIFY: <field>]` inline in the visible HTML (never in JSON-LD; omit missing JSON-LD keys entirely). Collect all markers for the user summary.

**Strategy branches:**

- **`preserve_existing`:** call `aeko_get_product_description(integration_id, external_product_id)` to fetch the raw editable description HTML. Output = `<existing_html>` + `\n<!-- AEKO structured content -->\n` + `<new_structured_section>`. New section uses the scaffold below. JSON-LD blocks still render inside the new section (not duplicated in the preserved block).
- **`rebuild_from_existing`:** scaffold from scratch. `<img src>` values use the URLs captured in Step 4.
- **`rebuild_with_local`:** scaffold from scratch. Local preview uses base64 data URIs; write-back artifact uses `{{LOCAL_IMAGE_N}}` placeholders + upload checklist.

**Scaffold** (skeletal — adapt per brand voice + prose):
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
  <h2>구매하기</h2>
  <p>...</p>
</section>
<script type="application/ld+json">{...Product schema...}</script>
<script type="application/ld+json">{...FAQPage schema...}</script>
<!-- if reviews_payload non-empty: -->
<script type="application/ld+json">{...Review / AggregateRating...}</script>
```

**Responsive contract** (mandatory — fail the run if violated):
- Mobile-first; no fixed-pixel container widths.
- `<img>` use `style="max-width:100%; height:auto; display:block; margin:0 auto;"` + non-empty `alt`.
- Semantic tags only: `<section>`, `<h2>`, `<h3>`, `<p>`, `<ul>`, `<ol>`, `<li>`.
- No executable JS (no `<script>` without `type` attr, no `on*` handlers, no `javascript:` URLs, no external CSS/`<link>`). Inline styles or single scoped `<style>` only.
- **Product JSON-LD mandatory** when `pdp_responsive_contract.json_ld_required == true`. Minimum: `@context`, `@type: "Product"`, `name`, `description`, `image[]`, `brand.name`. Populate `offers`, `sku`, `mpn`, `aggregateRating` when data is available — omit keys entirely otherwise (never `null` / empty string).
- **FAQPage JSON-LD mandatory** when `pdp_responsive_contract.faq_jsonld_required == true` AND `faq` in `sections_required`. `@type: "FAQPage"` + `mainEntity[]` ≥ 3 Question objects. Every Q&A in JSON-LD must also appear as visible HTML. If prose didn't surface FAQ content, derive 3-5 questions from `frontmatter.prompts_to_rank_on` verbatim.
- **Review JSON-LD** when `pdp_responsive_contract.review_jsonld_when_available == true` AND `reviews_payload` non-empty. Include `aggregateRating` + `review[]` (≤5 top). Tie to Product via `Product.aggregateRating` + `Product.review[]`. Skip silently if reviews are absent or look synthetic — never fabricate.
- All JSON-LD: valid JSON, no trailing commas, no comments. `type="application/ld+json"` exactly.

Honor `frontmatter.must_include` (every string present) + `forbidden` (none present). Acceptance gate for `sections_required`: every entry maps to a `<section>` heading (case-insensitive, trimmed). Missing → iterate or fail; do NOT call `aeko_complete_action_item`.

Write HTML to `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/pdp.html`.

## Step 6 — Local preview

Open the HTML in the default browser for review:
- macOS: `Bash(open ./aeko-artifacts/<domain_id>/<item_id>/pdp.html)`
- Linux: `Bash(xdg-open ./aeko-artifacts/<domain_id>/<item_id>/pdp.html)`

## Step 7 — Write-back per write_mode

**`shadow_product` (default):** the v0.5.0 MCP surface retains only `aeko_update_product_description`, `aeko_update_product_tags`, `aeko_update_product_meta`, `aeko_list_store_writes`, and `aeko_revert_store_write`. If the backend exposes a distinct shadow-product creation endpoint through one of these calls (e.g. `aeko_update_product_description` with a shadow flag in the payload), follow the prose's instructions for that call. Otherwise surface the constraint to the user: "Shadow-product write is not yet exposed via MCP — I'll write to `preview_only` and you can paste into Cafe24 admin under a new draft product." Do NOT silently downgrade without telling the user.

**`append_below_existing`:**
1. `aeko_get_product_description(integration_id, external_product_id)` → existing HTML.
2. `merged = existing_html + "\n<!-- AEKO appended -->\n" + rendered_html`.
3. `aeko_update_product_description(integration_id, external_product_id, merged)`.
4. Parse response for `audit_id` + `admin_url`. If missing, flag in the summary.

**`preview_only`:** no API call. Tell user to paste `pdp.html` into Cafe24 editor themselves.

## Step 8 — Mark complete

```
aeko_complete_action_item(
    item_id=frontmatter.item_id,
    artifact_summary="<one-line: artifact + write mode + audit id if any>",
    artifact_paths=[<absolute paths of pdp.html + any image files>],
    write_result={
        "mode": "<shadow_product | append_below_existing | preview_only>",
        "audit_id": "<from write response; null for preview_only>",
        "admin_url": "<from write response; null otherwise>",
    } if write performed else None,
)
```

Only complete if:
- Artifact written AND (no write-back required OR write-back returned valid response).

## Step 9 — User-facing summary

```
✔ PDP update complete
  Write mode:   <write_mode>
  Audit ID:     <audit_id>         (revert: aeko_revert_store_write("<audit_id>"))
  Admin URL:    <admin_url>
  Artifact:     <pdp.html path>
  OCR:          ingested N, skipped M (decorative / oversize)

[VERIFY] markers to resolve before going live (N):
  - [VERIFY: weight_grams]  — 무게 / weight in grams
  - ...
(Omit the block when no markers were emitted.)

Next: /aeko-action-center <domain_id> pdp
```

## Error paths

- Plan endpoint unavailable / parse error → stop; surface detail.
- Contract mismatch → stop.
- Stale brand kit + user declines → stop.
- All image OCR failed → stop; do NOT fabricate copy.
- Write-back 4xx → stop; do NOT mark complete; surface backend error verbatim.
- Shadow-product endpoint unavailable (v0.5.0 transitional) → ask user before downgrading to preview_only.

## What this skill never does

- Never writes to the live PDP by default; default is shadow/preview.
- Never handles Technical or Content items (redirect to sibling executors).
- Never hallucinates product copy from blank OCR.
- Never omits alt text on an `<img>`.
- Never uses JavaScript in generated HTML.
- Never regenerates the Plan.md; fetch once, follow it.
- Never reads machine values from prose body.
- Never echoes raw frontmatter.
