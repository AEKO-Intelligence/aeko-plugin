---
name: aeko-update-pdp
description: >
  PDP executor for an Action-tab item or a direct domain-and-product handoff.
  Reuses or idempotently creates and exclusively claims a `pdp_html` ActionItem,
  generates responsive HTML plus Product/FAQ/Review JSON-LD, always opens a local
  preview, and applies it only through an explicitly chosen supported store path.
argument-hint: "<item-id> | domain_id=<uuid> product_id=<id>"
allowed-tools: aeko_list_action_items, aeko_create_action_item, aeko_claim_action_item, aeko_release_action_item, aeko_get_action_plan, aeko_get_product_description, aeko_list_review_integrations, aeko_get_product_reviews, aeko_list_store_integrations, aeko_update_product_page, aeko_revert_store_write, aeko_list_store_writes, aeko_complete_action_item, Read, Write, WebFetch, Bash
---

# AEKO Update PDP

Executes one Action-tab PDP item end-to-end: claim the item → fetch Plan.md → ask optimization scope and image
strategy → generate responsive HTML + JSON-LD → show a local preview → ask where it should go → mark complete.
Nothing reaches a connected store before the preview and the user's delivery choice.

Two optimization scopes the user chooses up front:
- **`content_and_metadata`** — rewrite the product-page copy to AEO standards AND emit structured data / meta. The full pipeline (image strategy, AEO frameworks, copy generation).
- **`metadata_only`** — leave the merchant's existing description copy untouched; only generate/optimize the machine-readable layer (eligible Product / FAQPage / Review JSON-LD + `<meta>` tags) so AI engines can parse and cite the page. No copy rewrite, no image work. FAQ/review schema is eligible only when the same facts already appear visibly on the unchanged page.

Contract reference: `docs/contracts/action-item-contract.md` §3 (Plan.md), §6 (completion), and the store-write
audit/revert contract.

## Marketer-facing output contract

Frame this as "improving a product page so AI shopping/search tools can understand and cite it." Say up front
that the first result is a local preview. After the preview, ask one delivery question. Before a live update,
show Before / After / Risk / Undo and ask for a second explicit confirmation. Do not show raw Plan frontmatter,
`execution_class`, or schema internals unless debugging.

Language: mirror the user's chat language for user-facing steps, summaries, questions, and risk/undo copy.
Keep slash commands, IDs, file paths, channel slugs, schema keys, JSON-LD terms, and tool names in English/ASCII.
When a Plan includes `target_language`, use it for generated PDP content; do not let it override the assistant UI language.

## Input

- Existing-item mode: `<item-id>` as `$1`.
- Direct mode: both named arguments `domain_id=<uuid> product_id=<id>` in `$ARGUMENTS`. Treat `product_id`
  as an opaque external store-product ID; do not normalize or truncate it.

If neither complete form is present, stop and show:

```text
/aeko-update-pdp <item-id>
/aeko-update-pdp domain_id=<uuid> product_id=<id>
```

## Step 0 — Load tools and resolve direct mode

Before any tool call, issue exactly one deferred-tool search for the full run:

```text
ToolSearch(query="select:aeko_list_action_items,aeko_create_action_item,aeko_claim_action_item,aeko_release_action_item,aeko_get_action_plan,aeko_get_product_description,aeko_list_review_integrations,aeko_get_product_reviews,aeko_list_store_integrations,aeko_update_product_page,aeko_revert_store_write,aeko_list_store_writes,aeko_complete_action_item,WebFetch", max_results=20)
```

### Existing-item mode

Set `item_id` from `$1` and continue to the atomic claim gate below. Do not list or create ActionItems.

### Direct mode

Direct mode keeps the ActionItem contract because a product-page write needs audit, completion, and rollback
state. Resolve one item before continuing:

1. Call
   `aeko_list_action_items(domain_id, status="pending,generating_prose,ready,completed,failed,dismissed", limit=200, offset=0)`
   exactly with every ActionItem status.
2. If the response says more rows remain, repeat the same call with `offset += 200` until all pages have
   been checked. Parse every returned item and retain only exact matches where `artifact_type == "pdp_html"` and
   `product_id == <input product_id>`. Never match on title or URL. The MCP list includes `product_id` even
   when `target_url` is also present, plus `created_at`; newest rows appear first.
3. If any exact match has `status in {pending, generating_prose, ready}`, reuse the newest one. Set its ID as
   `item_id`. Do not call `aeko_create_action_item`. If it is `pending` or `generating_prose`, stop before
   claiming it; tell the user to retry the same item when it is ready rather than creating another.
4. Otherwise, take the newest exact terminal match in `{completed, failed, dismissed}`, if one exists, and set:

   ```text
   predecessor = <latest terminal item_id> | initial
   idempotency_key = pdp-direct:<domain_id>:<product_id>:after:<predecessor>
   ```

   Use that string byte-for-byte. Then call:

   ```text
   aeko_create_action_item(
     domain_id=<domain_id>,
     artifact_type="pdp_html",
     tab="action",
     product_id=<product_id>,
     idempotency_key=<idempotency_key>
   )
   ```

   Parse the returned `id` as `item_id`. The stable key makes concurrent/retried calls return the same row.

After reuse or creation, continue to the claim gate below. Never execute a completed, failed, or dismissed
predecessor directly. Including every terminal status in the predecessor key prevents a failed or dismissed
idempotent row from trapping later retries on the same row forever.

### Atomic claim gate — required in both modes

Before fetching the Plan or generating anything, call `aeko_claim_action_item(item_id)` exactly once. The
backend creates a permanent, token-fenced execution claim while the ActionItem itself remains `ready`:

- success → parse the non-empty returned `claim_id`, store it as `execution_claim_id`, set
  `execution_claimed=true`, and continue. If the response has no claim token, stop before generation; there
  is no safe way to release, complete, or write without it;
- 409 → stop before Plan fetch, generation, or writing. Explain that another or stale run may own the claim; never release it automatically.
  Offer recovery only after explicit confirmation that no other run is active **and** no store mutation occurred.
  KO: `다른 실행이 진행 중이 아니며 스토어 변경도 없었음을 확인합니다.` EN: `I confirm no other run is active and no store mutation occurred.` Translate naturally for other chat languages.
  Only that unambiguous confirmation permits one
  `aeko_release_action_item(item_id, force=true, confirm_no_active_execution=true)` call; then tell the user
  to rerun the command and end. Do not claim again in the same run.
- 403/404 → surface the backend message and stop.

Claims do not expire automatically. From this point until successful completion, release the claim with
`aeko_release_action_item(item_id, claim_id=execution_claim_id)` only
when failure or cancellation is confirmed to have caused no store mutation. Never release after a successful
or ambiguously completed store call; that could let another host repeat a live write.

## Step 1 — Fetch and parse the Plan.md

Call `aeko_get_action_plan(item_id)`. Parse YAML frontmatter + prose body.

**Validate. Every failure or redirect below happens before a store mutation: release first with
`claim_id=execution_claim_id`, then stop:**
- `contract_version` starts with `2026-04-17.action.v1.` — else stop.
- Pin this skill to contract minor `v1.2`. Greater minor → print advisory + proceed.
- `tab == "action"` — else stop.
- `execution_class == "store_write_artifact"` — else redirect: `technical_artifact` → `/aeko-fix-technical`, `local_content_artifact` → `/aeko-create-content`.
- `status == "ready"` — the claim lives separately, so Plan status remains `ready`; any other status means
  token-matched release and stop.
- `write_target` consistency: must pair with `write_mode` per contract §3 — `shadow_product ↔ shadow`, `append_below_existing ↔ live`, `preview_only ↔ local`. Mismatch → stop.
- `write_mode` is legacy Plan routing metadata, not permission to touch a store. The runtime always starts
  with a local preview and asks the user where to send it in Step 7.
- `tier_required` is enforced by backend write tools when applicable; do not resolve legacy identity data here.

Print the header in the user's chat language:
1. Action label — KO: "상품 페이지 개선" / EN: "Product page improvement"
2. Context: domain, product title (resolve via `target_url` inspection), channels.
3. Safety — KO: "먼저 로컬 미리보기를 만듭니다. 확인 전에는 스토어가 바뀌지 않습니다." / EN:
   "I'll create a local preview first. Nothing changes in the store until you review it."

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
2. 메타데이터만 최적화 — 기존 상품 설명은 그대로 두고, AI 엔진이 읽을 수 있는 구조화 데이터(JSON-LD)와 SEO 메타태그만 최적화

번호를 입력하거나 원하는 방향을 자유롭게 설명해 주세요.
```

**EN:**
```
How should we optimize this product page?

1. Content + metadata — rewrite the product description copy to AEO standards, and generate structured data (JSON-LD) + meta tags
2. Metadata only — leave the existing description copy as-is; only optimize structured data (JSON-LD) and SEO meta tags

Reply with a number or describe the direction you want.
```

Store as `optimization_scope ∈ {content_and_metadata, metadata_only}`.

**How the scope changes the rest of the run:**
- `content_and_metadata` → proceed normally: ask image strategy (Step 3), run the full AEO copy generation (Step 5.1), honor `must_include` / `sections_required` in the visible body.
- `metadata_only` → SKIP the image-strategy question (Step 3); force `image_strategy = preserve_existing` internally and never rebuild. In Step 5, do NOT rewrite or reorder the merchant's description copy or claim to change its headings. Generate Product JSON-LD and SEO meta fields (title/description where the Plan asks). Add FAQPage or Review/AggregateRating only when the exact Q&A/review facts already appear in readable visible content on the unchanged page; Context reviews alone never justify hidden schema. `must_include` / `forbidden` are validated against the eligible JSON-LD + meta output, not by injecting copy into the visible body. `sections_required` acceptance is waived (no new body sections are authored).

For `metadata_only`, the preview and any later live update must keep the existing description body unchanged.
Only the approved JSON-LD and meta fields may differ.

## Step 3 — Image strategy (ask user — content_and_metadata scope only)

**Skip this step when `optimization_scope == metadata_only`** (force `image_strategy = preserve_existing`,
proceed to Step 4). Otherwise ask in the user's chat language. Use the matching KO/EN template below when
applicable; for other languages, translate the EN template naturally while keeping option
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

Every strategy produces a local preview. The delivery choice comes later. If the user eventually chooses a
live update, `preserve_existing` appends the approved layer without deleting existing copy, while either
rebuild strategy replaces the current description and must say that plainly in the live confirmation.

For `rebuild_with_local` — prompt for up to 10 local image paths (absolute). Read each with native `Read` to verify. Inline as data-URI for local preview; in the final artifact for write-back, emit `{{LOCAL_IMAGE_N}}` placeholders + surface upload checklist.

## Step 4 — Resolve the current page evidence

### `metadata_only`

Do **not** download images, run OCR, inspect image binaries, or apply the all-images-failed gate.

1. Require the Plan's exact `integration_id` and `product_id` (the external store-product ID). Call
   `aeko_get_product_description(integration_id, product_id)` and store its raw `description_html` as
   `current_description_html`. This is the source of truth that the preview must preserve.
2. You may call `WebFetch(frontmatter.target_url)` once for readable page text, existing public metadata, and
   text-only review evidence. Do not discover or fetch image URLs in this scope. An unavailable or image-only
   public page does not block metadata generation; continue from the official store description, product
   facts, and Context reviews.
3. Build `reviews_payload` only from readable text/structured data returned by that page fetch. Never infer a
   review or product fact from an uninspected image.

### `content_and_metadata`

If `image_strategy != rebuild_with_local`:

1. `WebFetch(frontmatter.target_url)` → parse HTML to extract the product page structure and image URLs. Store the raw HTML in memory; discover `<img src>` attributes.
2. **Image guardrails** (using what WebFetch gives us — HTML attributes only):
   - Skip `<img>` with `width < 400` or `height < 400` (likely decorative).
   - Skip URLs matching thumbnail patterns (`/thumb/`, `_50x50`, `_100x100`, `-small`, `-thumb`).
   - Cap at 12 images per item. Log `skipped_decorative`, `skipped_thumbnail`, `skipped_overflow` counts.
3. For each remaining image index, fetch the binary via WebFetch (or direct URL save via `Bash(curl -o ...)` if the image content-type isn't handled) and save to `./aeko-artifacts/<domain_id>/<item_id>/img/<idx>.<ext>`. Open each with native `Read` for Claude vision to OCR Korean + English text. Preserve paragraph order.
4. **Review detection pass:** scan OCR text + raw HTML for review-shaped blocks (customer quotes, star ratings, "리뷰 N개", structured review widgets). Build `reviews_payload = [{author, rating, text, date_if_present}]` capped at top-10 recent/high-rated. Null if nothing review-shaped.
5. If the page exposed candidate product images and every attempted image OCR failed, stop. Do NOT hallucinate
   copy. If the page exposed no eligible product images, continue from verified product/context facts and log
   the evidence gap rather than treating zero attempts as an OCR failure.

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
  description HTML byte-for-byte in `current_description_html`. Produce separate values for the
  machine-readable layer: `json_ld_payload` (Product / FAQPage / Review, built from specs +
   existing visible/store facts + text-only on-page reviews), `meta_title`, and `meta_description`. Context
  reviews may help assess positioning but must not create hidden FAQ/review claims in this scope. Do not insert visible
  headings or body copy. For the local preview only, render the unchanged description together with a clearly
  labeled, non-editing inspector block that shows the proposed JSON-LD/meta values; keep the store-write
  payload separate. Skip the BLUF/PREP copy-writing below, skip `sections_required`, and validate
  `must_include` / `forbidden` against JSON-LD + meta. Then continue to Step 5b.
- `content_and_metadata` → run the full generation below.

When emitting more than one schema node, produce one `json_ld_payload` object:
`{"@context":"https://schema.org","@graph":[<Product>,<FAQPage if visibly matched>]}`.
Nest eligible `aggregateRating` and `review` data in Product. The store API accepts one JSON object, not a list
of separate payloads.

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

If `pending_verifications` is empty after Step 5, skip only the question/answer work in this step and continue
directly to Step 5c.

Otherwise, `Read references/prompts/verification-prompts.md` for the full prompt templates, reply-handling rules, and batch-shortcut behavior. Apply per the user's chat language; keep `frontmatter.target_language` only for the generated PDP content.

After collecting all answers, apply substitutions in-memory. Re-validate `must_include` (every required string still present) and `forbidden` (no banned strings introduced). If a substitution drops a `must_include` string, surface the conflict and re-ask only that item.

The final artifact must contain ZERO `[VERIFY: <field>]` badges in visible HTML and ZERO `.aeko-verify`-style decorations. The only acceptable unresolved-state form is HTML comments produced by the explicit `두기` / `leave` reply.

## Step 5c — Finalize and write the preview artifact

Whether or not there were pending verifications, re-run the scope-specific acceptance checks after Step 5b,
then **always** write the finalized preview HTML to
`./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/pdp.html`. Skipping the questions when there
is nothing to verify must never skip this write.

## Step 6 — Local preview

Open the HTML in the default browser for review:
- macOS: `Bash(open ./aeko-artifacts/<domain_id>/<item_id>/pdp.html)`
- Linux: `Bash(xdg-open ./aeko-artifacts/<domain_id>/<item_id>/pdp.html)`

## Step 7 — Ask where the preview should go

First determine whether private-draft creation is genuinely supported. Set `draft_supported=true` only when
the loaded runtime tool schema exposes an explicit private-draft/shadow creation operation and the selected
store connection advertises that capability. The standard `aeko_update_product_page` tool updates the current
product and do not count. Never infer support from Plan `write_mode`, a platform name, or marketing copy. With
the current standard MCP surface, `draft_supported=false`.

Ask exactly one delivery question in the user's chat language. Do not ask a separate write-mode question
elsewhere.

When `draft_supported=true`:

**KO**
```text
미리보기가 준비되었습니다. 어떻게 진행할까요?

1. 미리보기만 유지
2. 비공개 초안 상품으로 저장
3. 현재 상품 페이지에 적용

번호를 하나 선택해 주세요. 3번은 변경 내용과 되돌리기 방법을 먼저 보여드린 뒤 한 번 더 확인합니다.
```

**EN**
```text
The preview is ready. What would you like to do?

1. Keep the preview only
2. Save it as a private draft product
3. Apply it to the current product page

Choose one number. For option 3, I'll show the exact change and undo path before asking you to confirm once more.
```

When `draft_supported=false`, state naturally that this connection cannot create a private draft product,
then offer only the safe choices:

**KO**
```text
미리보기가 준비되었습니다. 현재 연결에서는 비공개 초안 상품 저장을 지원하지 않습니다.

1. 미리보기만 유지
2. 현재 상품 페이지에 적용

번호를 하나 선택해 주세요. 2번은 변경 내용과 되돌리기 방법을 먼저 보여드린 뒤 한 번 더 확인합니다.
```

**EN**
```text
The preview is ready. This store connection cannot create a private draft product.

1. Keep the preview only
2. Apply it to the current product page

Choose one number. For option 2, I'll show the exact change and undo path before asking you to confirm once more.
```

For other chat languages, translate the English template naturally. Keep IDs, paths, and tool names unchanged.

### Keep preview only

Set `delivery_mode="preview_only"`. Make no store call. Continue to Step 8.

### Save as a private draft product — only when supported

Call only the explicit draft-creation operation discovered above, following its actual schema. A normal
product update with a renamed label is not a draft. Require the response to identify a distinct non-public
draft target. Set `delivery_mode="private_draft"` and retain its ID/admin URL for the summary. If the call
fails with a confirmed no-write response, keep the local preview, release the claim with
`claim_id=execution_claim_id`, and stop. Never fall back
to a live update or claim that a draft was created.

### Apply to the current product page — explicit confirmation required

1. Resolve the exact `integration_id` and external product ID. Call
   `aeko_get_product_description(integration_id, external_product_id)` immediately before confirmation.
2. Build the exact proposed payload:
   - `metadata_only` → omit `description_html` entirely. Send only the approved `json_ld_payload`,
     `meta_title`, and `meta_description`; the backend uses the current store description as the JSON-LD base,
     preserving every non-JSON-LD body byte;
   - `preserve_existing` → keep `new_structured_section_html` separate from the full preview. Build
     `proposed_description_html = current_description_html + "\n<!-- AEKO appended -->\n" + new_structured_section_html`
     once, and send that complete proposed value exactly once. Never append `rendered_description_html` when
     it already contains the current description;
   - either rebuild strategy → replace the current description with `rendered_description_html`. Local-image placeholders
     must be resolved to real store-accessible URLs first; otherwise live update is unavailable.
3. In the user's chat language, show:
   - **Before**: product, current description length, and what remains unchanged;
   - **After**: append vs replacement, proposed length, affected sections/meta fields, and preview path;
   - **Risk**: this changes the public product page; name replacement risk when applicable;
   - **Undo**: the write returns an audit ID for `aeko_revert_store_write("<audit_id>")`.
4. Ask a second explicit confirmation. KO: `현재 상품 페이지에 적용` / EN: `Apply to current page`.
   Translate the confirmation phrase for other chat languages and require that exact affirmative intent.
   Any cancellation or ambiguous reply sets `delivery_mode="preview_only"`; make no store call and continue
   to Step 8.
5. Only after confirmation, call `aeko_update_product_page(...)` **exactly once**, passing the exact
   `integration_id`, external product ID, `action_item_id=frontmatter.item_id`, and
   `execution_claim_id=execution_claim_id`, plus every approved description/JSON-LD/tag/meta field in that
   one request. Never split one PDP update across `aeko_update_product_description`,
   `aeko_update_product_tags`, or `aeko_update_product_meta`; the single response must yield one `audit_id`
   and one revert boundary. Parse `audit_id` and `admin_url`, then set `delivery_mode="current_product"`.
   If the result is ambiguous (timeout/5xx after submission), do not release the claim; the write may have
   succeeded and the backend blocks automatic duplicate submission. Call `aeko_list_store_writes`, inspect
   the exact product's latest audit, and compare the store page. If one matching successful audit is confirmed,
   call `aeko_complete_action_item` with that audit ID and the same claim token. Otherwise stop and require
   owner-confirmed reconciliation; never repeat the write blindly.

## Step 8 — Mark complete

```
aeko_complete_action_item(
    item_id=frontmatter.item_id,
    artifact_summary="<one-line: artifact + delivery mode + audit id if any>",
    artifact_paths=[<absolute paths of pdp.html + any image files>],
    write_result={
        "mode": "<private_draft | current_product | preview_only>",
        "audit_id": "<from write response; null for preview_only>",
        "admin_url": "<from write response; null otherwise>",
        "draft_id": "<private draft id; null otherwise>",
    },
    execution_claim_id=execution_claim_id,
)
```

Only complete if:
- Artifact written AND (no write-back required OR write-back returned valid response).
- On successful completion, the backend deletes the separate execution claim.
- If completion fails before any store mutation, release with `claim_id=execution_claim_id`. If a store mutation succeeded or may have
  succeeded, do not release it; report the item ID and audit result so another host cannot repeat the write.

## Step 9 — User-facing summary

```
✔ Product page improvement complete
  Scope:         <content_and_metadata: copy rewritten + structured data | metadata_only: structured data + meta only, copy untouched>
  Safety:        <preview file | private draft product | current product page updated>
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

- Plan endpoint unavailable / parse error → release with the matching `execution_claim_id`, stop, and surface detail.
- Contract mismatch → release with the matching `execution_claim_id` and stop.
- Thin/missing content context → continue with product facts, OCR, and reviews; do not block write-back.
- `content_and_metadata` with attempted candidate images whose OCR all failed → stop; do NOT fabricate copy.
  `metadata_only` never runs image/OCR gates.
- Claim 409 → stop; leave the claim unless the user gives the two-part recovery confirmation, then release once and ask them to rerun.
- Failure before any store mutation → release with the matching `execution_claim_id`, then surface the error.
- Write-back 4xx with confirmed no mutation → release with the matching `execution_claim_id`; do NOT mark complete; surface the backend error.
- Ambiguous store response after submission → keep the claim and inspect the audit trail before retrying.
- Private-draft capability unavailable → say so before the delivery question; never fake it or silently switch modes.

## What this skill never does

- Never creates a second direct PDP item while an exact product match is pending, generating prose, or ready;
  active items are reused, and concurrent execution is resolved only by atomic claim success or 409.
- Never generates without first winning the atomic claim.
- Never relies on claim expiry: claims are permanent until token-matched completion/release or explicitly
  confirmed forced recovery.
- Never writes to a store before showing the local preview.
- Never updates the current product page without the delivery choice plus a second Before/After/Risk/Undo confirmation.
- Never splits one confirmed current-page update into multiple store calls; description, JSON-LD, tags, and
  SEO meta share one audit/revert boundary.
- Never calls a live update a private draft, and never silently downgrades an unavailable draft path.
- In `metadata_only` scope, never rewrites, reorders, or deletes the merchant's existing description copy — only adds the machine-readable layer (JSON-LD + meta).
- Never handles Technical or Content items (redirect to sibling executors).
- Never hallucinates product copy from blank OCR.
- Never omits alt text on an `<img>`.
- Never uses JavaScript in generated HTML.
- Never regenerates the Plan.md; fetch once, follow it.
- Never reads machine values from prose body.
- Never echoes raw frontmatter.
