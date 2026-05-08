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

**Precedence when sources conflict:** `voice-overrides` > `examples/*` > `recipes/*` > brand-kit `tone_of_voice` > prose body voice cues.

The Step 9 summary must list which reference files were loaded so the user can verify their exemplars are picked up.

### 5.1 Apply

Read `prose` for voice/structure guidance, `frontmatter.pdp_responsive_contract.*` for hard rules, live brand kit from Step 2, OCR payload from Step 4. Apply the loaded recipes (§5.0) — citability baseline, pending-verification handling, scaffold + strategy branches, responsive contract, JSON-LD schemas all live in the recipe files.

Honor `frontmatter.must_include` (every string present) + `forbidden` (none present). Acceptance gate for `sections_required`: every entry maps to a `<section>` heading (case-insensitive, trimmed). Missing → iterate or fail; do NOT call `aeko_complete_action_item`.

Keep the draft HTML in memory at this point — do NOT write it to disk yet. Disk write happens at the end of Step 5b after pending verifications are resolved.

## Step 5b — Resolve pending verifications with the user

If `pending_verifications` is empty after Step 5, skip this step.

Otherwise, `Read references/prompts/verification-prompts.md` for the full KO/EN prompt templates, reply-handling rules, and batch-shortcut behavior. Apply per `target_language`.

After collecting all answers, apply substitutions in-memory. Re-validate `must_include` (every required string still present) and `forbidden` (no banned strings introduced). If a substitution drops a `must_include` string, surface the conflict and re-ask only that item.

The final artifact must contain ZERO `[VERIFY: <field>]` badges in visible HTML and ZERO `.aeko-verify`-style decorations. The only acceptable unresolved-state form is HTML comments produced by the explicit `두기` / `leave` reply.

Write the finalized HTML to `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/pdp.html`.

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
  Write mode:    <write_mode>
  Audit ID:      <audit_id>         (revert: aeko_revert_store_write("<audit_id>"))
  Admin URL:     <admin_url>
  Artifact:      <pdp.html path>
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
