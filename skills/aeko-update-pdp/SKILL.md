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
allowed-tools: aeko_get_action_plan, aeko_get_product_description, aeko_list_review_integrations, aeko_get_product_reviews, aeko_list_store_integrations, aeko_update_product_description, aeko_update_product_tags, aeko_update_product_meta, aeko_revert_store_write, aeko_list_store_writes, aeko_complete_action_item, Read, Write, WebFetch, Bash
---

# AEKO Update PDP

Executes one Action-tab PDP item end-to-end: fetch Plan.md → parse frontmatter + prose → ask optimization scope → ask image strategy → WebFetch page + images → generate responsive HTML + JSON-LD → write to store (shadow-by-default) → mark complete.

Two optimization scopes the user chooses up front:
- **`content_and_metadata`** — rewrite the product-page copy to AEO standards AND emit structured data / meta. The full pipeline (image strategy, AEO frameworks, copy generation).
- **`metadata_only`** — leave the merchant's existing description copy untouched; only generate/optimize the machine-readable layer (Product / FAQPage / Review JSON-LD + `<meta>` tags + semantic heading fixes) so AI engines can parse and cite the page. No copy rewrite, no image work.

Contract reference: `docs/contracts/action-item-contract.md` §3 (Plan.md), §7 (shadow product), §6 (completion).

## Marketer-facing output contract

Frame this as "improving a product page so AI shopping/search tools can understand and cite it." Open with what
will change, why it matters, and whether the run is preview/shadow/live. Before any store write, show Before /
After / Risk / Undo. Do not show raw Plan frontmatter, `execution_class`, or schema internals unless debugging.

Language: mirror the user's chat language for user-facing steps, summaries, questions, and risk/undo copy.
Keep slash commands, IDs, file paths, channel slugs, schema keys, JSON-LD terms, and tool names in English/ASCII.
When a Plan includes `target_language`, use it for generated PDP content; do not let it override the assistant UI language.

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
- `tier_required` is enforced by backend write tools when applicable; do not resolve legacy identity data here.

Print the header in the user's chat language:
1. Action label — KO: "상품 페이지 개선" / EN: "Product page improvement"
2. Context: domain, product title (resolve via `target_url` inspection), channels.
3. Safety: user-language readout of `write_mode` as one of:
   - `shadow_product` → "Draft/shadow copy first — safest"
   - `append_below_existing` → "Can affect live store description"
   - `preview_only` → "Read-only preview file"

Print prose body verbatim. Never echo raw frontmatter.

## Step 2 — Resolve content context

Do not call legacy identity tools. Extract content/PDP context from
frontmatter + prose: `context`, `use_case`, `buyer_context`, `pain_points`, `desired_outcome`, `tone`,
`positioning`, `must_include`, `forbidden`, and `sections_required`. This is **context-only**. If context is thin, continue with product facts, OCR, reviews, and a neutral
evidence-first voice.

## Step 2.5 — Optimization scope (ask user — FIRST question)

Ask this **before** the image-strategy question. It decides whether we touch the merchant's copy at all.
Ask in the user's chat language; for languages other than KO/EN, translate the EN template naturally while
keeping the option numbers unchanged.

**KO:**
```
이 상품 페이지를 어떻게 최적화할까요?

1. 콘텐츠 + 메타데이터 최적화 — 상품 설명 문구를 AEO 기준으로 다시 쓰고, 구조화 데이터(JSON-LD)·메타태그도 함께 생성
2. 메타데이터만 최적화 — 기존 상품 설명은 그대로 두고, AI 엔진이 읽을 수 있는 구조화 데이터(JSON-LD)·메타태그·제목 구조만 최적화

번호를 입력하거나 원하는 방향을 자유롭게 설명해 주세요.
```

**EN:**
```
How should we optimize this product page?

1. Content + metadata — rewrite the product description copy to AEO standards, and generate structured data (JSON-LD) + meta tags
2. Metadata only — leave the existing description copy as-is; only optimize the machine-readable layer AI engines read: structured data (JSON-LD), meta tags, and heading structure

Reply with a number or describe the direction you want.
```

Store as `optimization_scope ∈ {content_and_metadata, metadata_only}`.

**How the scope changes the rest of the run:**
- `content_and_metadata` → proceed normally: ask image strategy (Step 3), run the full AEO copy generation (Step 5.1), honor `must_include` / `sections_required` in the visible body.
- `metadata_only` → SKIP the image-strategy question (Step 3); force `image_strategy = preserve_existing` internally and never rebuild. In Step 5, do NOT rewrite or reorder the merchant's description copy. Generate only: Product / FAQPage / Review JSON-LD, `<meta>` tags (title/description/OG where the Plan asks), and semantic heading corrections that do not change wording. `must_include` / `forbidden` are validated against the JSON-LD + meta output, not by injecting copy into the visible body. `sections_required` acceptance is waived (no new body sections are authored). The FAQPage / Review JSON-LD may still be built from `context_reviews` (Step 4.5) and on-page reviews, since that is machine-readable structured data, not visible-copy rewriting.

**Scope ↔ write_mode note:** `metadata_only` naturally pairs with `append_below_existing` (append a `<script type="application/ld+json">` block + meta below the existing description) or with `aeko_update_product_meta` for `<meta>` fields. It never replaces the existing description body.

## Step 3 — Image strategy (ask user — content_and_metadata scope only)

**Skip this step when `optimization_scope == metadata_only`** (force `image_strategy = preserve_existing`,
proceed to Step 4). Otherwise ask in the user's chat language. Use the matching KO/EN template below when
applicable; for other languages, translate the EN template naturally while keeping `write_mode` and option
numbers unchanged.

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

## Step 4.5 — Pull product context-reviews (originality source — runs for ALL strategies)

The on-page review detection in Step 4.4 captures whatever the live page already shows. The richer source
of **lived experience** — the thing AI engines reward and a generic description can't fake — is AEKO's
context-mapped reviews. Fetch them (this runs even for `rebuild_with_local`, since it doesn't depend on the
page fetch):

- Resolve the domain's review source with `aeko_list_review_integrations(domain_id)` → `integration_id`
  (skip reviews if none connected), then call `aeko_get_product_reviews(integration_id, <product_source_id>)`
  where `product_source_id` is the store product id (the `external_product_id` resolved for this item /
  from `aeko_list_store_integrations`).
- Build `context_reviews = [{context, shopper, quote, detail}]` — the concrete, situational details
  (numbers, surprises, trade-offs) you'll mine for Originality and for E-E-A-T FAQ answers in Step 5.

**Degrade gracefully:** tool absent/empty → continue. The product copy + specs + Step 4.4 on-page reviews
still carry substance; just note in the Step 9 summary that adding context-reviews would make the PDP more
original. **Anti-fabrication rule (hard):** every experiential claim in the description or FAQ must trace to
a real `context_reviews` entry, an on-page review, or a product spec — never invent a lived experience. With
no reviews, write from honest expertise (correct mechanism, real specs), not a manufactured anecdote.

## Step 5 — Generate responsive HTML

### 5.0 Load references (on-demand)

Before generating, load these reference files in order. Anthropic progressive-disclosure pattern — recipe detail loads only when this step runs.

1. **Always:**
   - `Read references/recipes/pdp-scaffold.md` — HTML scaffold + strategy-branch behavior.
   - `Read references/recipes/responsive-html-contract.md` — hard rules (no JS, no action elements, citability baseline, pending-verification handling).
   - `Read references/recipes/json-ld-schemas.md` — Product / FAQPage / Review requirements + FAQ source priority.

2. **If they exist (silent skip otherwise):**
   - `Read references/examples/pdp-html-example.html` — brand's preferred section order, heading copy, class naming. Mimic structure on top of the scaffold; recipe acceptance gates still apply.
   - `Read references/examples/json-ld-preferences.json` — brand's optional-field preferences for JSON-LD emission. Required keys cannot be overridden.
   - `Read references/style/voice-overrides.md` — domain-scoped overrides; filter to blocks where `domain: <frontmatter.domain_id>` matches.

**Precedence when sources conflict:** `voice-overrides` > `examples/*` > `recipes/*` > Plan/content context > prose body voice cues.

The Step 9 summary must list which reference files were loaded so the user can verify their exemplars are picked up.

### 5.1 Apply

**Scope branch (from Step 2.5):**
- `metadata_only` → do NOT author or rewrite visible description copy. Preserve the merchant's existing
  description HTML verbatim. Produce only the machine-readable layer: Product / FAQPage / Review JSON-LD
  (built from specs + `context_reviews` + on-page reviews) and `<meta>` tags, plus non-destructive semantic
  heading corrections (e.g. fixing heading levels without changing wording). Skip the BLUF/PREP copy-writing
  below, skip `sections_required`, and validate `must_include` / `forbidden` against the JSON-LD + meta output.
  Then continue to Step 5b.
- `content_and_metadata` → run the full generation below.

Read `prose` and Step 2 content context for voice/structure guidance, `frontmatter.pdp_responsive_contract.*`
for hard rules, and OCR payload from Step 4. Apply the loaded recipes (§5.0) — citability baseline,
pending-verification handling, scaffold + strategy branches, responsive contract, JSON-LD schemas all live
in the recipe files.

**Apply the AEO frameworks** — the PDP is the #1 ecommerce surface AI engines cite, so write it to the
same standard as `/aeko-create-content`. Definitions live in
`skills/aeko-create-content/references/aeo-frameworks.md` (the plugin's canonical source); apply them here:
- **BLUF** — the description opens with the bottom-line answer to "what is this and why does it matter for
  *this* buyer," not a feature dump or brand preamble. AI engines lift the direct answer.
- **PREP** — each benefit/feature block is Point → Reason → Example → Point, so each is independently
  citable. The **Example** is where substance lives: a real spec or a concrete detail from `context_reviews`.
- **Informational Gain** — inject specificity and **originality from `context_reviews`** (the lived,
  situational detail a generic PDP can't have); name the specific buyer cohort. This is the AEO differentiator.
- **E-E-A-T in the FAQ** — every FAQ answer (and its `FAQPage` JSON-LD) must show Experience + Expertise +
  specifics + honest trade-offs drawn from real reviews/specs — never a restated marketing line.

This stays within the existing conventions: **no hard CTAs** in the body (`[[feedback_aeko_pdp_is_aeo_content_not_cta]]` — AEKO injects citability content; the store owns the buy button), responsive contract, and the anti-fabrication rule from §4.5.

Honor `frontmatter.must_include` (every string present) + `forbidden` (none present). Acceptance gate for `sections_required`: every entry maps to a `<section>` heading (case-insensitive, trimmed). Missing → iterate or fail; do NOT call `aeko_complete_action_item`.

Keep the draft HTML in memory at this point — do NOT write it to disk yet. Disk write happens at the end of Step 5b after pending verifications are resolved.

## Step 5b — Resolve pending verifications with the user

If `pending_verifications` is empty after Step 5, skip this step.

Otherwise, `Read references/prompts/verification-prompts.md` for the full prompt templates, reply-handling rules, and batch-shortcut behavior. Apply per the user's chat language; keep `frontmatter.target_language` only for the generated PDP content.

After collecting all answers, apply substitutions in-memory. Re-validate `must_include` (every required string still present) and `forbidden` (no banned strings introduced). If a substitution drops a `must_include` string, surface the conflict and re-ask only that item.

The final artifact must contain ZERO `[VERIFY: <field>]` badges in visible HTML and ZERO `.aeko-verify`-style decorations. The only acceptable unresolved-state form is HTML comments produced by the explicit `두기` / `leave` reply.

Write the finalized HTML to `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/pdp.html`.

## Step 6 — Local preview

Open the HTML in the default browser for review:
- macOS: `Bash(open ./aeko-artifacts/<domain_id>/<item_id>/pdp.html)`
- Linux: `Bash(xdg-open ./aeko-artifacts/<domain_id>/<item_id>/pdp.html)`

## Step 7 — Write-back per write_mode

Before any write-back call, print a marketer-facing confirmation block:

```
Before
- Current PDP description stays available through the store audit trail.

After
- Adds AI-readable product facts, review proof, FAQ content, and shopping facts AEKO can verify.

Risk
- <preview_only: none to live store | shadow_product: low | append_below_existing: live PDP changes>

Undo
- <preview_only: delete/ignore the file | write: use aeko_revert_store_write("<audit_id>") after the audit id returns>
```

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
✔ Product page improvement complete
  Scope:         <content_and_metadata: copy rewritten + structured data | metadata_only: structured data + meta only, copy untouched>
  Safety:        <preview file | draft/shadow | live PDP updated>
  Audit ID:      <audit_id>         (revert: aeko_revert_store_write("<audit_id>"))
  Admin URL:     <admin_url>
  Artifact:      <pdp.html path>
  AI-readable:   product facts, review proof, FAQ, shopping facts AEKO could verify
  Refs loaded:   recipes/{pdp-scaffold,responsive-html-contract,json-ld-schemas}.md
                 + examples/pdp-html-example.html  (when present)
                 + examples/json-ld-preferences.json  (when present)
                 + style/voice-overrides.md  (when present, scoped to this domain)
  OCR:           ingested N, skipped M (decorative / oversize)
  Verifications: resolved N items via Step 5b (V values, O omits, L left as HTML comments)

Plan warnings (N):
  - prompts_to_rank_on_missing — re-run /aeko-create-plan with keywords or curated prompt IDs
  - ...
(Omit the block when no plan-level warnings were raised.)

HTML comments left for later fill-in (N):
  - <!-- pending: weight_grams --> in section "사용 방법"
  - ...
(Omit the block when none were left as comments. These are invisible to end users; they exist only for the user to find and fill in via Cafe24 admin.)

Next: /aeko-action-center <domain_id> pdp
```

## Error paths

- Plan endpoint unavailable / parse error → stop; surface detail.
- Contract mismatch → stop.
- Thin/missing content context → continue with product facts, OCR, and reviews; do not block write-back.
- All image OCR failed → stop; do NOT fabricate copy.
- Write-back 4xx → stop; do NOT mark complete; surface backend error verbatim.
- Shadow-product endpoint unavailable (v0.5.0 transitional) → ask user before downgrading to preview_only.

## What this skill never does

- Never writes to the live PDP by default; default is shadow/preview.
- In `metadata_only` scope, never rewrites, reorders, or deletes the merchant's existing description copy — only adds the machine-readable layer (JSON-LD + meta + non-destructive heading fixes).
- Never handles Technical or Content items (redirect to sibling executors).
- Never hallucinates product copy from blank OCR.
- Never omits alt text on an `<img>`.
- Never uses JavaScript in generated HTML.
- Never regenerates the Plan.md; fetch once, follow it.
- Never reads machine values from prose body.
- Never echoes raw frontmatter.
