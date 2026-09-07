---
name: aeko-update-pdp
description: >
  PDP executor for an Action-tab item or a direct domain-and-product handoff,
  plus mode=refresh for surgical review JSON-LD maintenance. Normal mode builds
  previewed responsive HTML and schema; refresh mode patches only ratingValue
  and reviewCount while preserving all non-JSON-LD HTML bytes.
argument-hint: "<item-id> | domain_id=<uuid> product_id=<id> | mode=refresh <product-id> [integration-id]"
allowed-tools: aeko_list_action_items, aeko_create_action_item, aeko_claim_action_item, aeko_release_action_item, aeko_get_action_plan, aeko_get_product_description, aeko_list_review_integrations, aeko_get_product_reviews, aeko_list_store_integrations, aeko_update_product_page, aeko_revert_store_write, aeko_list_store_writes, aeko_complete_action_item, Read, Write, WebFetch, Bash
---

# AEKO Update PDP

Before work, read [the brand execution contract](references/brand-execution-contract.md).
Preserve the exact task prompt and apply only this brand's selected rules, evals, and examples.
Use [the output evaluation rubric](references/brand-output-eval.md) plus the selected brand evals
when checking the exact result; report missing inputs/checks as unavailable.

## Mode routing

If `$ARGUMENTS` contains `mode=refresh`, remove only that mode token, then read
`references/refresh-mode.md` completely and execute it as the authoritative workflow. Do not enter the
normal PDP rewrite/metadata flow below.

Refresh mode surgically patches **ONLY** `AggregateRating.ratingValue`
and `AggregateRating.reviewCount`; it preserves every byte of HTML outside the existing
JSON-LD blocks. It never rewrites visible PDP copy, price, availability, shipping, returns, or any sibling
schema field.

Without `mode=refresh`, continue with the normal executor below. Normal PDP output remains AEO content,
never CTA voice; the store owns purchase actions.

Executes one Action-tab PDP item end-to-end: claim the item → fetch Plan.md → ask optimization scope and image
strategy → generate responsive HTML + JSON-LD → show a local preview → ask where it should go → mark complete.
Nothing reaches a connected store before the preview and the user's delivery choice.

Two optimization scopes the user chooses up front:
- **`content_and_metadata`** — rewrite the product-page copy to AEO standards AND emit structured data / meta. The full pipeline (image strategy, AEO frameworks, copy generation).
- **`metadata_only`** — leave the merchant's visible description copy untouched; consolidate and optimize
  the machine-readable layer (eligible Product / FAQPage / Review JSON-LD + `<meta>` tags) so AI engines can
  parse and cite the page. This is a replacement of the page's JSON-LD layer, not an additive operation:
  every existing schema node must be parsed and carried forward unless the confirmation diff names its
  evidence-backed change. No copy rewrite or image work. FAQ/review schema is eligible only when the same
  facts already appear visibly on the unchanged page.

The inline claim, completion, and store-write rules below are authoritative. The shared contract document
does not yet formalize those sections, so this skill never cites its TODO headings as executable rules.

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
- Accept any `v1.*` minor under that prefix. The backend currently emits later v1 minors; do not pin a
  stale minor or imply that a TODO contract section supplies a gate. An unknown major still stops the run.
- `tab == "action"` — else stop.
- `execution_class == "store_write_artifact"` — else redirect: `technical_artifact` → `/aeko-fix-technical`, `local_content_artifact` → `/aeko-create-content`.
- `status == "ready"` — the claim lives separately, so Plan status remains `ready`; any other status means
  token-matched release and stop.
- `write_target` consistency: must pair with `write_mode` as stamped in the Plan —
  `shadow_product ↔ shadow`, `append_below_existing ↔ live`, `preview_only ↔ local`. Mismatch → stop. This
  is an inline compatibility check, not a claim that the shared contract's TODO section is authoritative.
- `write_mode` is legacy Plan routing metadata, not permission to touch a store. The runtime always starts
  with a local preview and asks the user where to send it in Step 7.
- `shadow_product` / `shadow` may remain in a legacy Plan, but the standard MCP surface has no private-draft
  operation. Treat that combination as preview-only; never relabel a live update as a draft.
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

1. 현재 이미지 유지 + 아래에 구조화된 HTML 추가 준비 (라이브 적용 시 가장 높은 위험)
2. 기존 이미지를 재사용해 처음부터 재구성
3. 로컬 컴퓨터의 새 이미지 파일로 처음부터 재구성

번호를 입력하거나 원하는 접근을 자유롭게 설명해 주세요.
```

**EN:**
```
How should we structure this PDP?

1. Keep current images + prepare AEO-optimized HTML below (highest risk for a live update)
2. Rebuild from scratch using current PDP images
3. Rebuild from scratch using local image files

Reply with a number or describe the approach you want.
```

Store as `image_strategy ∈ {preserve_existing, rebuild_from_existing, rebuild_with_local}`.

Every strategy produces a local preview. The delivery choice comes later. The store API has **no append
primitive**: every description write replaces the whole field. For a live `preserve_existing` delivery, the
skill therefore has to resend the current HTML plus the approved new section. That is the highest-risk
choice because any truncation or normalization could delete merchant images; it is permitted only behind
the byte-prefix, image-count, snapshot, and stale-base gates in Step 7. Either rebuild strategy also replaces
the current description and must say that plainly in the live confirmation.

For `rebuild_with_local` — prompt for up to 10 local image paths. Read each with native `Read` to verify.
Inline as data-URI for the local preview only. Before any live update, upload/resolve every image to a real
store-accessible URL and reject the payload if any placeholder, data URI, or local filesystem path remains.

## Step 4 — Resolve the current page evidence

### Source-of-truth description — all scopes and strategies

Before inspecting the public page, resolve the Plan's exact `integration_id` and external `product_id`, then
call `aeko_get_product_description(integration_id, product_id)`. Strip only the tool's surrounding markdown
fence; bind the enclosed bytes as `current_description_html`. Never bind this variable from `WebFetch`, the
rendered live page, or Plan prose. Record `current_description_length` and `current_description_img_count`
from this exact value.

Extract every JSON-LD script from the source description with case-insensitive HTML-attribute parsing that
recognizes both `type="application/ld+json"` and `type='application/ld+json'`, regardless of attribute order
or whitespace. Parse every block and flatten each root / `@graph` into an ordered `existing_schema_nodes`
ledger with its source-block anchor. If any block fails JSON parsing, a live JSON-LD update is unavailable:
show the parse error and stop before a write rather than deleting the malformed or unknown block. If any
single-quoted JSON-LD script is present, also block the live JSON-LD update: the current backend only removes
double-quoted blocks and would otherwise leave the old node beside the new one. A preview/manual remediation
may continue, but `aeko_update_product_page` must not be called with `json_ld` in that state.

### `metadata_only`

Do **not** download images, run OCR, inspect image binaries, or apply the all-images-failed gate.

1. Use the already-bound `current_description_html` as the source of truth the preview must preserve.
2. You may call `WebFetch(frontmatter.target_url)` once for readable page text and text-only review evidence;
   never use it to replace the source-description or JSON-LD ledger. The head and scripts are not reliably
   present in converted WebFetch output.
3. Do not discover or fetch image URLs in this scope. An unavailable or image-only public page does not
   block metadata generation; continue from the official store description, product facts, and Context
   reviews.
4. Build `reviews_payload` only from readable text/structured data returned by that page fetch. Sort
   deterministically by `review_created_at` descending, then stable review/source ID ascending. Never use
   this capped sample to compute `reviewCount` or `ratingValue`, and never infer a review or product fact
   from an uninspected image.

### `content_and_metadata`

If `image_strategy != rebuild_with_local`:

1. `WebFetch(frontmatter.target_url)` → inspect readable product-page structure and image URLs. Treat it as
   content evidence only; it is not `current_description_html` and must never be sent to the store.
2. **Image guardrails** (using the available HTML attributes):
   - Skip an `<img>` only when an explicitly present width or height is below 400. A missing width/height
     is unknown, not small, and remains eligible; this is the common Cafe24 detail-image shape.
   - Skip URLs matching thumbnail patterns (`/thumb/`, `_50x50`, `_100x100`, `-small`, `-thumb`).
   - Cap at 12 images per item. Log `skipped_decorative`, `skipped_thumbnail`, `skipped_overflow` counts.
3. For each remaining image index, fetch the binary via WebFetch (or direct URL save via `Bash(curl -o ...)` if the image content-type isn't handled) and save to `./aeko-artifacts/<domain_id>/<item_id>/img/<idx>.<ext>`. Open each with native `Read` for Claude vision to OCR Korean + English text. Preserve paragraph order.
4. **Review detection pass:** scan OCR text + readable HTML for review-shaped blocks (customer quotes, star
   ratings, "리뷰 N개", structured review widgets). Build
   `reviews_payload = [{source_id, author, rating, text, date_if_present}]`, sorted by date descending and
   then stable source ID ascending, capped at the first 10. Never use this sample to derive an aggregate
   rating or total count. Null if nothing review-shaped.
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

### Evidence classification and conflicts

The content map is product-type extensible, not garment-shaped. Classify verified facts under the most
specific available category, including at least `material`, `fit`, `dimensions`, `volume_size`,
`formulation`, `ingredients`, `dosage`, `usage`, `care`, `cautions`, `origin`, `shipping_terms`,
`return_terms`, `warranty`, and `other`; add a clearly named category when the product type needs one rather
than forcing 50 ml into a size chart or ingredients into material.

When sources conflict, prefer the evidence most specifically scoped to this exact product, variant, field,
and current store state: authoritative store fields and product-specific visible description/image evidence
outrank generic policy, brand-level prose, or theme chrome. Recency breaks ties only between equally scoped
sources. Record every conflict, the chosen source, and why in the preview; never silently pick. If two
equally specific sources remain irreconcilable (for example two usage sequences with different steps), keep
both as separately attributed instructions or ask the user—never merge them into an invented sequence and
never drop a required field merely because one weaker source disagrees.

Shipping, returns, and purchase-policy sections are optional when those facts already live visibly in the
host platform shell/tab. Record `already_in_host_shell` in the acceptance summary instead of duplicating
them in newly authored description HTML. This exception never licenses silently dropping a unique verified
fact that appears nowhere else.

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

**Precedence when sources conflict:** explicit task instructions and applicable brand rules/evals
(surface contradictions; never silently remove standing rules) > scoped `voice-overrides` >
brand examples > generated Plan/content context > generic recipe defaults. Actual responsive/schema,
claim ownership, and write-confirmation contracts remain required.

The Step 9 summary must list which reference files were loaded so the user can verify their exemplars are picked up.

### 5.1 Apply

**Scope branch (from Step 2.5):**
- `metadata_only` → do NOT author or rewrite visible description copy. Preserve the merchant's existing
  source description byte-for-byte in `current_description_html`; the proposed result must preserve every
  non-JSON-LD byte while replacing the consolidated schema layer. Produce separate values for the
  machine-readable layer: `json_ld_payload` (the fully preserved/merged Product / FAQPage / Review graph),
  `meta_title`, and `meta_description`. Context
  reviews may help assess positioning but must not create hidden FAQ/review claims in this scope. Do not insert visible
  headings or body copy. For the local preview only, render the unchanged description together with a clearly
  labeled, non-editing inspector block that shows the proposed JSON-LD/meta values; keep the store-write
  payload separate. Skip the BLUF/PREP copy-writing below, skip `sections_required`, and validate
  `must_include` / `forbidden` against JSON-LD + meta. Then continue to Step 5b.
- `content_and_metadata` → run the full generation below.

### Structured-data merge — mandatory in both scopes

The backend replaces the first double-quoted JSON-LD block and deletes every later double-quoted block. It
does not append safely. Therefore `json_ld_payload` must be the complete consolidated schema graph, not just
the nodes generated this run:

1. Start from every parsed node in `existing_schema_nodes`, preserving node order, every unknown node type,
   and every field not explicitly approved for change. This includes offers, GTIN/MPN, availability,
   BreadcrumbList, Organization, app-generated reviews, VideoObject, and fields this skill could not itself
   recreate.
2. Identify a Product node as the current product only from exact product identity (`url`, canonical,
   authoritative product ID/SKU, or exact normalized name plus page scope). If identity is ambiguous, do not
   merge or delete either Product; block live output and show the conflict.
3. Patch only evidence-backed fields generated in this run into that Product. Preserve all sibling fields.
   If no Product exists, a new Product may be added only when its mandatory facts are evidenced. Never remove
   an old value merely because the current run did not reload its source.
   When the host Product already contains identity, description, images, offers, and rating data, default to
   preserving that node and adding only eligible FAQ/meta or explicitly approved Product-field changes—never
   emit a second Product. Call a Product materially incomplete only by naming the exact missing/invalid fields
   in the diff and explaining why the merged replacement is safe.
4. FAQ is deterministic: preserve an existing FAQPage unchanged when fewer than three eligible current-run
   Q&As exist. Replace/add it only when at least three visibly matched Q&As pass the source rule. Never let a
   later run delete an earlier FAQPage because the current evidence load was thinner.
5. Aggregate totals never come from a capped review sample. `reviewCount` and `ratingValue` require explicit
   store-authoritative totals or explicit user confirmation; otherwise preserve existing values or omit them
   on a brand-new Product. Individual review samples sort by date descending, then stable source ID.
6. Emit exactly one `json_ld_payload` object:
   `{"@context":"https://schema.org","@graph":[<all preserved and approved nodes>]}`.

Before confirmation, show a JSON-LD Before/After diff by node identity and JSON Pointer. It must name every
added, changed, removed, or preserved node. Any unapproved removal, unparseable block, ambiguous Product
identity, or single-quoted JSON-LD block makes live update unavailable; preserve the preview and explain why.
The store API accepts one JSON object, not a list of separate payloads.

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

Honor `frontmatter.must_include` (every string present) + `forbidden` (none present) within the newly authored
HTML only. Acceptance gate for `sections_required`: every entry maps to a newly authored `<section>` heading
(case-insensitive, trimmed). Missing → iterate or fail; do NOT call `aeko_complete_action_item`. Never apply
these gates to the preserved merchant prefix; an existing link, script, alt-less image, or forbidden phrase
does not license editing that prefix.

Keep the draft HTML in memory at this point — do NOT write it to disk yet. Disk write happens at the end of Step 5b after pending verifications are resolved.

## Step 5b — Resolve pending verifications with the user

If `pending_verifications` is empty after Step 5, skip only the question/answer work in this step and continue
directly to Step 5c.

Otherwise, `Read references/prompts/verification-prompts.md` for the full prompt templates, reply-handling rules, and batch-shortcut behavior. Apply per the user's chat language; keep `frontmatter.target_language` only for the generated PDP content.

After collecting all answers, apply substitutions in-memory. Re-validate `must_include` (every required string still present) and `forbidden` (no banned strings introduced). If a substitution drops a `must_include` string, surface the conflict and re-ask only that item.

The final artifact must contain ZERO `[VERIFY: <field>]` badges in visible HTML and ZERO `.aeko-verify`-style decorations. The only acceptable unresolved-state form is HTML comments produced by the explicit `두기` / `leave` reply.

## Step 5c — Finalize and write the preview artifact

Apply the selected brand evals to the exact newly authored HTML/schema, with the original task
prompt retained. In `preserve_existing` mode, report conflicting preserved merchant text separately;
a rule failure does not authorize altering that prefix. A failed or unavailable required eval may
produce a labeled review preview but blocks the store-write/completion path after one correction.

Whether or not there were pending verifications, re-run the scope-specific acceptance checks after Step 5b,
then **always** write the finalized preview HTML to
`./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/pdp.html`. Skipping the questions when there
is nothing to verify must never skip this write.

For `preserve_existing`, validate the newly authored section by itself against the responsive contract. The
combined local preview may contain merchant-authored elements forbidden in new AEKO HTML; report those as
preserved, never strip or rewrite them.

## Step 6 — Local preview

Open the HTML in the default browser for review:
- macOS: `Bash(open ./aeko-artifacts/<domain_id>/<item_id>/pdp.html)`
- Linux: `Bash(xdg-open ./aeko-artifacts/<domain_id>/<item_id>/pdp.html)`

## Step 7 — Ask where the preview should go

The standard MCP surface has no private-draft creation operation. Do not advertise or probe a pseudo-draft
branch. Ask exactly one delivery question in the user's chat language:

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

For other chat languages, translate the English template naturally. Keep IDs, paths, and tool names
unchanged.

### Keep preview only

Set `delivery_mode="preview_only"`. Make no store call. Continue to Step 8.

### Apply to the current product page — explicit confirmation required

1. Resolve the exact `integration_id`, `domain_id`, and external product ID. Call
   `aeko_get_product_description(integration_id, external_product_id)` immediately before building the
   confirmation. Bind only its fenced `description_html` as the new `current_description_html`. If it differs
   byte-for-byte from the Step 4 base, stop, rebuild the preview on the new base, and ask again.
2. **Guaranteed recovery snapshot.** Before any mutating store call, write the exact fenced HTML bytes to
   `./aeko-artifacts/<domain_id>/<item_id>/before.html` without normalization. Re-read it and require exact
   length, byte equality to `current_description_html`, and the same `<img` count. If the snapshot cannot be
   proven exact, live delivery is unavailable. This file is the fallback when the backend audit cannot be
   reverted.
3. Re-parse JSON-LD from this fresh base and rebuild the complete graph/diff under Step 5. A parse failure,
   ambiguous Product, unapproved node removal, or single-quoted JSON-LD block stops the live path.
4. Build the exact proposed payload:
   - `metadata_only` → omit `description_html`. Send only the complete approved `json_ld_payload`,
     `meta_title`, and `meta_description`. This replaces/consolidates the JSON-LD layer while the backend
     preserves non-JSON-LD body bytes; it does **not** merely add metadata;
   - `preserve_existing` → keep `new_structured_section_html` separate. Build exactly once:
     `proposed_description_html = current_description_html + "\n<!-- AEKO appended -->\n" + new_structured_section_html`.
     Treat the current prefix as opaque bytes: save the new section separately and form `proposed.html` by
     local byte concatenation from `before.html`; never retype, summarize, or regenerate the prefix in model
     output. The API still performs a full-field replacement. Before enabling the live call, require the first
     `len(current_description_html.encode("utf-8"))` bytes of the proposed UTF-8 payload to be byte-identical
     to the current HTML and require `proposed_img_count >= current_description_img_count`. A longer total
     length is not evidence of preservation. If either assertion fails—or the host cannot guarantee that the
     exact validated value will be forwarded as the tool argument—refuse the write and offer
     `metadata_only` or manual append from the preview. Keep the existing double-append marker guard;
   - either rebuild strategy → replace the full description with `rendered_description_html`. Require
     `rendered_img_count >= current_description_img_count`, including images with no width/height attributes,
     or stop. For `rebuild_with_local`, require that uploads resolved every source and that the payload has
     none of `{{LOCAL_IMAGE_`, `data:image/`, `file://`, `./`, `../`, `/Users/`, `/home/`, a Windows drive
     path, or a UNC path. Otherwise stop. Pass `domain_id` to the update tool.
5. Apply every responsive/no-CTA/no-JS/alt/`must_include`/`forbidden` acceptance gate only to
   `new_structured_section_html` or a fully new rebuild. Under `preserve_existing`, do not strip links,
   scripts, handlers, alt-less images, or other merchant content from the byte-identical prefix.
6. In the user's chat language, show:
   - **Before**: product, exact description byte/character length, image count, schema-node inventory, and
     `before.html` path;
   - **After**: append-via-full-replacement vs rebuild vs metadata-only, exact proposed length/image count,
     affected sections/meta fields, JSON-LD node/JSON-Pointer diff, and preview path;
   - **Risk**: this changes the public product page. `preserve_existing` is the highest-risk option because
     the API has no append primitive and must resend the whole description. A description write also
     syndicates to `aeko.shop` for Pro/Enterprise accounts unless the approved call uses a supported opt-out;
     state that second surface;
   - **Undo**: a successful audit can be reverted, but revert restores the description captured at the AEKO
     write and will overwrite any merchant edits made afterward. The local `before.html` remains the manual
     recovery copy.
7. Ask a second explicit confirmation. KO: `현재 상품 페이지에 적용` / EN: `Apply to current page`.
   Translate the confirmation phrase for other chat languages and require that exact affirmative intent.
   Any cancellation or ambiguous reply sets `delivery_mode="preview_only"`; make no store call and continue
   to Step 8.
8. **TOCTOU gate after confirmation.** Call `aeko_get_product_description(integration_id,
   external_product_id)` once more and compare its fenced HTML byte-for-byte with `before.html`. If it changed,
   do not write: save the new base separately, rebuild/re-preview, and require a fresh confirmation. Re-run
   the JSON-LD, byte-prefix, image-count, and local-reference gates on the exact final payload.
9. Only after all gates pass, call `aeko_update_product_page(...)` **exactly once**, passing the exact
   `integration_id`, external product ID, `action_item_id=frontmatter.item_id`, and
   `execution_claim_id=execution_claim_id`, `domain_id=frontmatter.domain_id`, plus every approved
   description/JSON-LD/tag/meta field in that
   one request. Never split one PDP update across `aeko_update_product_description`,
   `aeko_update_product_tags`, or `aeko_update_product_meta`; the single response must yield one `audit_id`
   and one revert boundary. Parse `audit_id` and `admin_url`, then set `delivery_mode="current_product"`.
10. On a confirmed success, call `aeko_get_product_description(integration_id, external_product_id)` and
    compare the returned HTML with the locally emulated expected backend result, including JSON-LD
    consolidation and image count. Length alone never passes verification.
11. If the result is ambiguous (timeout/5xx after submission), do not release the claim or retry. Call
    `aeko_list_store_writes(limit=100, offset=0)` and filter to the exact integration and external product when
    those fields are exposed, then call `aeko_get_product_description(integration_id,
    external_product_id)` for the actual comparison. The currently shipped list tool has no integration
    filter parameter; never invent one. If the returned rows cannot prove the exact integration, treat
    reconciliation as inconclusive and escalate rather than guessing. A `failed` audit cannot be reverted,
    even when the store may have committed, and the pinned claim prevents a corrective payload. In that
    indeterminate state the item is stuck: keep the claim, do not complete, and tell the user recovery
    requires the store admin using `before.html` or AEKO support. Only one proven matching `success` audit
    permits completion with that audit ID.

## Step 8 — Mark complete

```
aeko_complete_action_item(
    item_id=frontmatter.item_id,
    artifact_summary="<one-line: artifact + delivery mode + audit id if any>",
    artifact_paths=[<absolute paths of pdp.html + any image files + before.html when live was attempted>],
    write_result={
        "mode": "<current_product | preview_only>",
        "audit_id": "<from write response; null for preview_only>",
        "admin_url": "<from write response; null otherwise>",
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
  Safety:        <preview file | current product page updated>
  Recovery copy: <before.html path when a live write was attempted>
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
  - prompts_to_rank_on_missing — add product-specific keywords or curated prompt IDs to the Action item, then rerun
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
- Ambiguous store response after submission → keep the claim, never retry, reconcile with the exact source
  description and audit data, and direct recovery to store admin/AEKO support when the audit is `failed` or
  inconclusive.

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
- Never offers a private-draft path because the standard tool surface cannot create one.
- In `metadata_only`, never rewrites visible non-JSON-LD copy. It replaces the consolidated JSON-LD layer
  only after every existing node is parsed, preserved or explicitly diffed, and approved.
- In `preserve_existing`, never describes the store call as an append: it is a high-risk full-description
  replacement. Never call it unless `before.html`, byte-prefix identity, nondecreasing image count, JSON-LD
  preservation, and the post-confirmation stale-base check all pass.
- Never apply new-HTML acceptance rules as permission to edit preserved merchant HTML.
- Never handles Technical or Content items (redirect to sibling executors).
- Never hallucinates product copy from blank OCR.
- Never omits alt text on an `<img>`.
- Never uses JavaScript in generated HTML.
- Never regenerates the Plan.md; fetch once, follow it.
- Never reads machine values from prose body.
- Never echoes raw frontmatter.
