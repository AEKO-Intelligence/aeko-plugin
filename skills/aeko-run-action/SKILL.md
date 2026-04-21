---
name: aeko-run-action
description: >
  Executor for Action-tab items. Fetches a Plan.md for one item,
  dispatches on execution_class, and produces the artifact.
  PDP items (store_write_artifact): OCR-ingest existing product images
  with guardrails, generate responsive HTML against the scaffold, write
  to the store via the plan's write_mode (default shadow_product), and
  mark complete with full provenance. Content items (local_content_artifact):
  produce local markdown (+ JSON-LD if required) and mark complete.
  Enforces responsive HTML contract and stale-brand-kit warning.
argument-hint: "<item-id>"
allowed-tools: aeko_get_action_plan, aeko_get_brand_kit, aeko_get_product_description, aeko_inspect_product_page, aeko_read_product_page_image, aeko_check_ocr_cache, aeko_store_ocr_result, aeko_search_research_prompts, aeko_get_tracked_prompts, aeko_fetch_source_content, aeko_create_shadow_product, aeko_update_product_description, aeko_complete_action_item, Read, Write, WebSearch, WebFetch, Bash(open *), Bash(xdg-open *)
---

# AEKO Run Action

Executes one Action-tab item end-to-end: fetch Plan.md → parse frontmatter + prose → validate contract → dispatch on `execution_class` → produce artifact → (PDP only) write to store → mark complete.

The required MCP tools (`aeko_get_action_plan`, `aeko_complete_action_item`, `aeko_get_brand_kit`, store-write tools) are registered on the hosted AEKO MCP server. Do NOT run a separate tool-availability check before starting — just call the tool; if the server returns an error, surface it verbatim. Only the explicit error cases listed in "Error paths" at the end of this skill cause an abort.

Contract reference: `docs/contracts/action-item-contract.md` §3 (Plan.md format), §3a (OCR cache), §7 (shadow product), §6 (completion).

## Input

- `item-id` (required) — `$1`. If missing, stop and point user to `/aeko-action-center <domain_id> action`.

## Step 1 — Fetch and parse the Plan.md

Call `aeko_get_action_plan(item_id)`. The response is a single markdown string: YAML frontmatter between `---` fences, followed by a Sonnet-authored prose body. Parse both.

- `frontmatter` = YAML block between the opening `---` and the first following `---` alone on a line.
- `prose` = everything after the closing `---` (with the leading blank line trimmed).

Dispatch is driven entirely by `frontmatter`. Prose is narrative guidance for how to write the artifact — never a source of machine values.

Validate frontmatter:
- `contract_version` starts with `2026-04-17.action.v1.` — else stop with explicit mismatch. (Gate on major only; minor bumps are additive and must not break the skill.)
- This skill is pinned to contract minor `v1.1`. If the incoming plan's minor is strictly greater (e.g. `v1.3`), print a one-line advisory above the header: "This plan uses contract v<plan_minor>; this skill is on v1.1 — `/plugin update aeko` for the latest guidance." Then proceed (forward-compat per §11.1).
- `tab == "action"` — else stop with mismatch.
- `execution_class` ∈ {`store_write_artifact`, `local_content_artifact`} — else stop. If it's `technical_artifact`, tell the user to run `/aeko-fix-technical <item_id>`.
- `status ∈ {pending, ready}` — executable states per contract §1. Prose is now templated server-side at create time, so new rows land in `ready` directly; `pending` remains valid for legacy rows. The old `generating_prose` waiting state is retired — the backend does not emit it on new inserts. If an older row is encountered with `status == "generating_prose"`, render the backend's 409 body verbatim ("Plan is still being generated — retry in a moment") and stop. If `status ∈ {completed, failed, dismissed}`, stop with the appropriate message ("already completed" / "previous run failed — use `/aeko-action-center` to regenerate" / "dismissed — pick another").
- `tier_required` gate: if present AND caller tier is known AND caller tier is below `tier_required` → stop with a bilingual message (see §Copy). Caller tier is resolved from `aeko_get_brand_kit(...).metadata.account_tier`; if unresolved, proceed and rely on the backend as authoritative gate (log the fallthrough in the completion summary).
- `write_target` consistency check (if present):
  - If `execution_class == "local_content_artifact"`, `write_target` MUST equal `local` — else stop with exact mismatch.
  - If `execution_class == "store_write_artifact"`, the pairing MUST be one of: `shadow_product ↔ shadow`, `append_below_existing ↔ live`, `preview_only ↔ local`. Any other combination → stop; do NOT guess which side is correct.

Print a plain-language header in `target_language` (fall back per §3.1), then the prose body verbatim.

Header format (3 lines):
1. A one-sentence label for the action. Derive from (`execution_class`, `write_target`, `artifact_type`) via the §Copy mapping. Examples — KO: "상품 섀도우 초안 생성 — 실제 판매 중인 상품은 변경되지 않습니다" / EN: "Creating a shadow draft — your live product will not be changed."
2. Context line: domain, target product title (if resolvable), channels.
3. Persona line: `persona_label` if present, else omitted.

After the header, print a blank line, then the full `prose` body verbatim. Never print the raw frontmatter block.

### Copy (user-facing message templates)

All user-facing strings below are rendered in `target_language` if it's one of the supported languages (`ko`, `en`); otherwise English. Korean templates target B2B Cafe24 sellers; avoid literal translations.

- **Action label** (header line 1) — derived from `(execution_class, write_target)`:
  - `(store_write_artifact, shadow)` — KO: "상품 섀도우 초안 생성 — 실제 판매 중인 상품은 변경되지 않습니다" / EN: "Creating a shadow product draft — your live product will not be changed."
  - `(store_write_artifact, live)` — KO: "기존 상품 설명에 AEKO 콘텐츠를 덧붙입니다 — 실제 상품이 업데이트됩니다" / EN: "Appending AEKO content to your live product description — this will update the live listing."
  - `(store_write_artifact, local)` — KO: "PDP HTML을 로컬로 생성합니다 — 스토어에는 쓰지 않습니다" / EN: "Generating PDP HTML locally — nothing is written to your store."
  - `(local_content_artifact, local)` — KO: "콘텐츠 아티팩트를 로컬로 생성합니다" / EN: "Generating a content artifact locally."

- **Brand Kit missing** (Step 2) — KO: "이 제안을 실행하려면 <domain>의 브랜드 키트가 필요합니다. 브랜드 키트는 톤·페르소나·샘플 문구를 담아 앞으로 모든 제안에 일관된 목소리를 입혀 줍니다. `/aeko-brand-kit`를 먼저 실행해 설정한 뒤 다시 시도해 주세요." / EN: "This suggestion needs a Brand Kit for <domain>. A Brand Kit captures your tone, persona, and sample copy so every future plan speaks in your voice. Run `/aeko-brand-kit` to set it up, then re-run this command."

- **Tier gate** (Step 1) — `<tier>` and `<current>` are the two tier names; `<billing_url>` resolves from `aeko_get_brand_kit(...).metadata.billing_url` when available, else `https://aeko.ai/billing`:
  - KO: "이 제안은 `<tier>` 플랜부터 실행할 수 있습니다 (현재 플랜: `<current>`). `<tier>` 플랜은 <tier_benefit_ko> 기능까지 열어 줍니다. 업그레이드: <billing_url>. 이 아이템은 건너뛰고 다른 제안을 선택할 수도 있습니다."
  - EN: "This item needs the `<tier>` plan (current: `<current>`). `<tier>` unlocks <tier_benefit_en>. Upgrade at <billing_url>, or skip this item and pick another."
  - `tier_benefit_ko` / `tier_benefit_en` lookup:
    - `growth` → `"라이브 스토어 쓰기, FAQ/Review 구조화 데이터" / "live-store writes and FAQ/Review structured data"`
    - `pro` → `"페르소나 추적, 고급 경쟁사 벤치마크, 우선 지원" / "persona tracking, advanced competitor benchmarks, priority support"`
    - `enterprise` → `"다중 도메인 및 SSO" / "multi-domain and SSO"`
    - If tier is unknown to the skill, omit the benefit clause.

- **Minor-version advisory** — KO: "이 제안은 계약 v<plan_minor> 기준입니다. 현재 스킬은 v1.1 — 최신 지침을 받으려면 `/plugin update aeko`를 실행해 주세요." / EN: "This plan uses contract v<plan_minor>; this skill is pinned to v1.1 — run `/plugin update aeko` for the latest guidance."

## Step 2 — Stale brand-kit check

If `frontmatter.requires_brand_kit == true`:
- Call `aeko_get_brand_kit(frontmatter.domain_id)` for the live snapshot.
- If the live Brand Kit is missing or empty (first-time user with no kit), stop with the Brand-Kit-missing message from §Copy (rendered in `target_language`). Do NOT phrase this as a contract breach.
- Verify minimum voice signal: `tone_of_voice` present AND at least one of `{brand_voice_summary, target_audience}` populated. If both voice fields are empty, warn the user in `target_language` that artifact quality will track the thin kit and offer to abort so they can edit the kit first (`/aeko-brand-kit <domain_id> edit`). Default to asking.
- Otherwise, if `frontmatter.brand_kit_snapshot_version` is missing, log it to the completion payload's `artifact_summary` (engineer-readable) and proceed using the live kit. Do not surface as a user-facing warning — backend bug, not a user problem.
- If `frontmatter.brand_kit_snapshot_version` is present and the live `snapshot_version` is newer → warn user plainly in `target_language`: "Plan was generated against kit <v>. Live kit is <v+>. Regenerate plan? (abort / proceed with snapshot)" Default to asking. Do NOT silently proceed with a stale snapshot.

## Step 3 — Dispatch on execution_class

### 3A. `local_content_artifact` (own-site markdown / external-media markdown)

1. Read `prose` for narrative guidance; read `frontmatter` for all machine values.
2. If `frontmatter.requires_brand_kit == true`, enforce brand-kit fields are present in the live snapshot from Step 2 (`tone_of_voice` AND at least one of `{brand_voice_summary, target_audience}` at minimum). Stop if missing.
3. Research phase (optional, guided by prose):
   - If the prose asks for tracked-prompt grounding → `aeko_search_research_prompts(scope="domain", keyword=<keyword from frontmatter.keywords>, country=frontmatter.target_country, ai_platform=None, query_type=None)`.
   - If the prose asks for external research → `WebSearch` / `WebFetch` as instructed. Do not invent URLs.
4. Draft the artifact in the format from `frontmatter.output_artifact_format` (typically `markdown`):
   - Honor `frontmatter.must_include` (every string MUST appear in the artifact) and `frontmatter.forbidden` (no string MAY appear).
   - Acceptance gate for `frontmatter.sections_required`: every entry MUST map to a heading or named section in the artifact (markdown heading text or frontmatter-like label match, case-insensitive, after trimming). If a section is missing, iterate or fail the run — do NOT call `aeko_complete_action_item`.
   - Write to `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/<slug>.md`.
   - If `frontmatter.artifact_type == "own_store_markdown"` and the prose requests JSON-LD, emit it to a sibling `schema.json`.
5. No store write. Move to Step 5.

### 3B. `store_write_artifact` (PDP HTML)

#### 3B.0 — Image & structure strategy (ask the user)

Before OCR or generation, ask the user which strategy to use. Render the question in `target_language`.

**KO template:**
```
이 PDP를 어떻게 구성할까요?

1. 현재 이미지 유지 + 아래 구조화된 HTML 추가
   (가장 안전 · 기존 디자인 그대로, AEO 최적화 콘텐츠를 하단에 추가)
2. 기존 이미지를 재사용해 처음부터 재구성
   (현재 PDP의 이미지 URL을 그대로 써서 구조화된 레이아웃으로 재조립)
3. 로컬 컴퓨터의 새 이미지 파일로 처음부터 재구성
   (새 이미지 경로를 알려주시면 구조화된 HTML을 새로 만듭니다)

번호를 입력하거나 원하는 접근을 자유롭게 설명해 주세요.
```

**EN template:**
```
How should we structure this PDP?

1. Keep current images + add AEO-optimized HTML below
   (safest · preserves your existing design; new structured content goes underneath)
2. Rebuild from scratch using current PDP images
   (re-uses the existing image URLs in a new structured layout)
3. Rebuild from scratch using local image files
   (you provide file paths; we build fresh HTML with those images)

Reply with a number or describe the approach you want.
```

Store the choice as `image_strategy ∈ {preserve_existing, rebuild_from_existing, rebuild_with_local}`.

**Strategy ↔ write_mode consistency** (enforce before proceeding):

| `image_strategy` | Allowed `write_mode` values |
|---|---|
| `preserve_existing` | `shadow_product`, `append_below_existing`, `preview_only` |
| `rebuild_from_existing` | `shadow_product`, `preview_only` |
| `rebuild_with_local` | `shadow_product`, `preview_only` |

If the user picks a rebuild strategy on an item whose plan has `write_mode: append_below_existing`, stop with: "Rebuilding replaces the HTML, so appending to the live description doesn't make sense. Either pick strategy 1 (keep current images) or ask me to switch to shadow write." Do NOT silently reassign the write_mode.

For `rebuild_with_local`, after strategy selection prompt the user for image paths:
```
로컬 이미지 파일 경로를 알려주세요 (한 줄에 하나씩, 최대 10장):
```
Read each path with `Read` (absolute paths). If a path doesn't exist, ask again. Inline each image as a data URI when writing `pdp.html` for local preview; in the final artifact for store write-back, emit placeholder URLs and surface a warning: "Upload these N images to Cafe24 CDN and swap `{{LOCAL_IMAGE_N}}` placeholders with the resulting URLs before making the shadow live."

#### 3B.1 — OCR ingest (existing PDP images)

Skip this entire subsection when `image_strategy == "rebuild_with_local"` (we're not using the live PDP's images).

Otherwise, if `frontmatter.requires_ocr_ingest == true`:

1. If `frontmatter.pdp_ocr_cache_key` is set AND the tool `aeko_check_ocr_cache` is available, call `aeko_check_ocr_cache(frontmatter.pdp_ocr_cache_key)`. If it returns a valid `AekoOcrCacheEntry`, use its `images[].text` and skip to 3B.2. If the tool is not available (Stage 1 did not wire the OCR cache endpoint), skip silently to step 2 — the cache is explicitly optional per the contract.
2. Else, call `aeko_inspect_product_page(product_id=frontmatter.source_product_id)`. The current tool returns per-image `src`, `alt`, `width`, `height` only — NOT filesize. Guardrails below use the fields that actually exist.
3. **OCR guardrails** (hard, using only currently-exposed metadata):
   - Skip any image where `width < 400` OR `height < 400` (likely decorative / icon / spacer). Log `skipped_decorative: N`.
   - Skip any image whose `src` matches common thumbnail patterns (`/thumb/`, `_50x50`, `_100x100`, `-small`, `-thumb`). Log `skipped_thumbnail: N`.
   - Cap OCR loop at 12 images per run; images are processed in document order. Log `skipped_overflow: M` for any beyond the cap.
   - (Future) When `aeko_inspect_product_page` exposes `filesize` and `content_type`, tighten by skipping `filesize < 30_000` — do not assume filesize is available today.
4. For each remaining image index, call `aeko_read_product_page_image(frontmatter.source_product_id, image_index)` — returned as MCP Image. Use Claude vision to extract Korean + English text verbatim. Preserve paragraph order. Also capture the image `src` URL for each successfully read image — these are the URLs `rebuild_from_existing` will reuse and that JSON-LD `image` array will reference.
5. **Review detection pass:** scan the concatenated OCR text + the raw page structure from `aeko_inspect_product_page` for review-shaped blocks. Signals: quoted customer text + author initials/names + star ratings ("⭐", "★", "5/5", "평점"), review count patterns ("리뷰 128개", "128 reviews"), structured review widgets in the DOM. When found, build `reviews_payload = [{author, rating, text, date_if_present}]` — at most 10 entries, prefer the highest-rated recent ones. If nothing review-shaped surfaces, set `reviews_payload = null` and proceed silently.
6. Assemble `ocr_payload = {images: [{index, src, width, height, text, extracted_at}], product_id, reviews: reviews_payload}`. If `aeko_store_ocr_result` is available and `frontmatter.pdp_ocr_cache_key` is set, persist it.
7. If every image failed OCR → stop the run; do NOT hallucinate copy. Tell the user which image indices failed and why.

#### 3B.2 — Generate responsive HTML

1. Read `prose` for voice/structure guidance, `frontmatter.pdp_responsive_contract.*` for hard rules, the live brand kit from Step 2, and the OCR payload from 3B.1 (including `reviews` if present).

**Citability baseline (apply even if prose is silent on these):** 80-167 word passages, name the subject explicitly in every paragraph (no pronoun opens), open each section with a 1-2 sentence direct answer, use "X is a Y that Z" structures for core claims, include specific numbers / dimensions / years where possible. See contract §3.4.

**`[VERIFY: <field>]` marker:** when a factual value is needed and absent from OCR / StoreProducts / Brand Kit / prose, emit `[VERIFY: <field>]` inline in the visible HTML (e.g. `무게는 [VERIFY: weight_grams]g입니다.`). Do NOT fabricate. For JSON-LD, omit the missing key entirely rather than inserting a `[VERIFY]` string (schema validators reject it). Collect every marker emitted in a list for Step 6's user summary.

2. Use the reference scaffold at `aeko_mcp/templates/pdp_responsive_scaffold.html` as the base structure.

**Strategy branch:**

- **`preserve_existing`:** fetch the current editable description via `aeko_get_product_description(frontmatter.integration_id, frontmatter.product_id)`. The rendered artifact is: `<existing_description_html>` + `\n<!-- AEKO structured content -->\n` + `<new_structured_section_built_from_scaffold>`. The scaffold's JSON-LD blocks still appear (at the top of the new structured section). Do NOT inline existing images again — they're in the preserved block. The JSON-LD `image` array references the preserved image URLs for AI crawler coverage.

- **`rebuild_from_existing`:** use the scaffold from scratch. `<img src>` values use the URLs captured from the OCR pass (3B.1 step 4). Inline the OCR-extracted text as the copy source for each section, voiced through the Sonnet prose and brand kit.

- **`rebuild_with_local`:** use the scaffold from scratch. For the local preview (`./aeko-artifacts/.../pdp.html`), inline each local image as a base64 data URI so the browser preview renders immediately. For any artifact destined for write-back (shadow or preview_only copy-paste), replace data URIs with `{{LOCAL_IMAGE_N}}` placeholder tokens and include an upload checklist in the user summary (Step 6).

3. **Responsive HTML contract (mandatory — fail the run if violated):**
   - Mobile-first; no fixed-pixel widths on containers.
   - `<img>` tags use `style="max-width:100%; height:auto; display:block; margin:0 auto;"`.
   - Every `<img>` has a non-empty `alt` attribute (AEO-critical).
   - Semantic tags only: `<section>`, `<h2>`, `<h3>`, `<p>`, `<ul>`, `<ol>`, `<li>`. No `<div>` soup, no tables for layout.
   - No executable JavaScript: no `<script>` WITHOUT a `type` attribute, no `<script type="text/javascript">`, no `on*` event attributes, no `javascript:` URLs, no external CSS, no `<link>` to stylesheets. Inline styles or a single scoped `<style>` block only.
   - **Product JSON-LD is mandatory** when `pdp_responsive_contract.json_ld_required == true`. Exactly one `<script type="application/ld+json">` block with a valid schema.org `Product` object. Minimum: `@context: "https://schema.org"`, `@type: "Product"`, `name`, `description`, `image` (array of image URLs — from OCR payload `images[].src` for preserve/rebuild_from_existing, from the supplied local paths or uploaded CDN URLs for rebuild_with_local), `brand.name`. Populate `offers.price`, `offers.priceCurrency`, `sku`, `mpn` when data is in the StoreProducts row — omit the keys entirely when data is missing (never emit empty strings or `null` inside JSON-LD).
   - **FAQPage JSON-LD is mandatory** when `pdp_responsive_contract.faq_jsonld_required == true` AND `faq` is in `frontmatter.sections_required`. Emit a second `<script type="application/ld+json">` block with `@type: "FAQPage"` and `mainEntity` = an array of ≥3 `Question` objects, each with a non-empty `acceptedAnswer.Answer.text`. Every Q&A pair in the JSON-LD MUST also appear as visible HTML in the FAQ section (same question text, equivalent answer). If the Sonnet prose didn't surface FAQ content, derive 3-5 questions from `frontmatter.prompts_to_rank_on` — these are the exact AI-engine queries we want to rank for, so use them verbatim as the questions and have Claude write the answers.
   - **Review JSON-LD** when `pdp_responsive_contract.review_jsonld_when_available == true` AND `ocr_payload.reviews` is non-empty. Emit a third `<script type="application/ld+json">` block: include an `aggregateRating` object (`@type: "AggregateRating"`, `ratingValue`, `reviewCount`) and a `review` array of up to 5 top `Review` objects (each with `author.name`, `reviewRating.ratingValue`, `reviewBody`, `datePublished` when known). Tie these to the Product via the `Product` block's `aggregateRating` and `review` keys (same schema tree, single JSON-LD if cleaner, or an additional `@graph` block). If review data is absent or clearly synthetic (identical text, obvious bot patterns), skip silently — never fabricate.
   - All JSON-LD: valid JSON (no trailing commas, no comments). Script `type` attribute MUST be exactly `application/ld+json` — the only `type` value permitted on any `<script>` tag in the output.
4. Honor `frontmatter.must_include` (every string MUST appear in the rendered HTML) and `frontmatter.forbidden` (no string MAY appear). Acceptance gate for `frontmatter.sections_required`: every entry MUST map to a `<section>` or heading with matching text/aria-label (case-insensitive, trimmed). Missing sections → iterate or fail the run; do NOT call `aeko_complete_action_item`.
5. Write HTML to `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/pdp.html`.
6. **Local preview** — open the file directly in the default browser:
   - macOS: `Bash(open ./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/pdp.html)`
   - Linux: `Bash(xdg-open ./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/pdp.html)`
   Do NOT call `aeko_preview_optimized_page` for this step — that tool requires `aeo_score_before` / `aeo_score_after` / `original_description` fields that the Action-plan contract does not carry. The browser preview of the generated HTML is sufficient for user review; the shadow-product admin URL is the authoritative diff once write-back completes.

#### 3B.3 — Write back per write_mode

Read `frontmatter.write_mode`:

- `shadow_product` (default): call
  ```
  aeko_create_shadow_product(
      integration_id=frontmatter.integration_id,
      source_product_id=frontmatter.source_product_id or frontmatter.product_id,
      description_html=<rendered HTML>,
      title_suffix="[AEKO Draft]",
  )
  ```
  Parse response as `AekoShadowProductResponse`. All six provenance fields (`created_product_id`, `admin_url`, `selling=false`, `source_product_id`, `audit_id`, `revert_supported`) MUST be present. If any missing → do NOT mark complete; surface the gap and stop.

- `append_below_existing`:
  1. Fetch current editable description via `aeko_get_product_description(integration_id=frontmatter.integration_id, external_product_id=frontmatter.product_id)`. This returns the raw description HTML as stored in Cafe24/Shopify (NOT the rendered page — `aeko_inspect_product_page` is not suitable here because it returns rendered structure, not editable source).
  2. Concatenate: `merged_html = existing_html + "\n<!-- AEKO appended -->\n" + rendered_html`.
  3. Call `aeko_update_product_description(integration_id=frontmatter.integration_id, external_product_id=frontmatter.product_id, description_html=merged_html)`.
  4. **Response handling:** Per the contract (section 7a), Stage 1 upgrades `aeko_update_product_description` to return an `AekoStoreWriteResponse` with `audit_id`, `admin_url`, `revert_supported`. Parse those fields for the completion `write_result` in Step 5. If the tool is still returning markdown-only (pre-upgrade), set `write_result.audit_id = null`, `write_result.admin_url = null` and surface a warning in the user summary: "audit_id unavailable — revert is not supported for this write."
  5. If `aeko_get_product_description` is not yet wired (Stage 1 backend work), ABORT this mode and tell the user: "append_below_existing requires the product-description fetch endpoint, which is not yet live. Re-run with write_mode: shadow_product or preview_only." Do not invent `existing_html`.

- `preview_only`: no API call. Preview already opened in 3B.2.6. Tell user to copy `pdp.html` into Cafe24 editor themselves.

## Step 4 — Artifact paths

Collect all absolute paths written to disk for the completion payload:
- `pdp.html` and/or `<slug>.md`, `schema.json`, OCR debug dump (if written).

## Step 5 — Mark complete

Build payload:

```python
aeko_complete_action_item(
    item_id=frontmatter.item_id,
    artifact_summary="<one-line: what was produced + where it went>",
    artifact_paths=[<absolute paths>],
    write_result={
        "mode": "<shadow_product | append_below_existing | preview_only>",
        "audit_id": "<from shadow response or store_write response; null for preview_only>",
        "admin_url": "<from shadow response; null otherwise>",
        "created_product_id": "<from shadow response; null otherwise>",
    } if frontmatter.execution_class == "store_write_artifact" else None,
)
```

Only call complete if:
- Artifact was written AND (no write-back needed OR write-back response was valid).

If complete() errors, leave item `pending`, surface the error.

## Step 6 — User-facing summary

### For `store_write_artifact` with `shadow_product`:

```
✔ Shadow product created
  Admin URL:         <admin_url>
  New product ID:    <created_product_id>
  Source product ID: <source_product_id>
  Selling:           false  (review in admin, flip live when ready)
  Audit ID:          <audit_id>
  Revert:            aeko_revert_store_write("<audit_id>")

Artifact saved: <pdp.html path>
OCR: ingested N images, skipped M (decorative/oversize)

[VERIFY] markers to resolve before going live (N):
  - [VERIFY: weight_grams]   — 무게 / weight in grams
  - [VERIFY: price]          — 판매가 / price
  - ...                      (render in target_language)
(Omit the entire block when no [VERIFY] markers were emitted.)

Next: /aeko-action-center <domain_id> action
```

### For `append_below_existing`:
Print similar block with `admin_url` (live PDP), `audit_id`, revert command.

### For `preview_only`:
Print preview path + copy-paste instructions.

### For `local_content_artifact`:
Print artifact paths + any sibling JSON-LD + next-item hint.

## Error paths

- Plan endpoint unavailable → stop; suggest retrying later.
- Plan.md frontmatter fails to parse (no opening `---`, YAML syntax error, missing required key) → stop; surface the exact parse error and the first 20 lines of the response for debugging.
- Contract mismatch → stop; exact mismatch surfaced.
- Stale brand kit + user declines → stop; leave pending.
- All OCR images failed → stop; do not hallucinate.
- Shadow response missing required fields → stop; do not mark complete.
- Write-back 4xx → stop; do not mark complete; print backend error verbatim.

## What this skill never does

- Never runs Technical-tab items (reject with message to use `/aeko-fix-technical`).
- Never writes to the LIVE PDP by default. `append_below_existing` requires explicit `write_mode` in the frontmatter.
- Never hallucinates product copy from blank OCR.
- Never omits alt text on any `<img>`.
- Never uses JavaScript in generated HTML.
- Never regenerates the plan. Fetch once; follow it.
- Never reads a machine value from the prose body. If a value is needed, it must come from `frontmatter`. Prose is narrative only.
- Never echoes the raw frontmatter block to the user in chat. Print a short human-friendly header (Step 1) and the prose body only. The full Plan.md is available if the user explicitly asks for it.
