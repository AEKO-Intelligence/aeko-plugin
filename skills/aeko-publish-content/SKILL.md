---
name: aeko-publish-content
description: >
  Backend-first publisher for content variations saved by
  `/aeko-create-content` (or any other authoring flow that calls
  `aeko_save_content_variation`). Looks up saved rows for an item_id,
  asks the user which destination to publish when more than one exists,
  and calls the single backend publish route — which branches per
  destination: `aeko_shop` → live publish via the existing aeko.shop
  pipeline; `own_store_blog` → AEKO-owned draft row only (never calls
  Cafe24/Shopify live APIs). Other channels (tistory, naver_blog,
  social, editorial) remain generation-only — clients post them
  themselves.
argument-hint: "<item-id>"
allowed-tools: aeko_list_content_variations, aeko_publish_content_variation
---

# AEKO Publish Content

Runs after `/aeko-create-content` (or after any other flow that saved publishable variations to the AEKO backend). Picks a saved variation row for the item_id, confirms with the user, and calls the single backend publish route. The backend branches on the row's destination — `aeko_shop` publishes live; `own_store_blog` creates an AEKO-owned draft row the user can push to their connected store later.

**Key change from earlier versions of this skill:** the publish source-of-truth moved from local disk files to backend `content_variations` rows. The skill no longer scans `./aeko-artifacts/`, no longer reads `.meta.json`, no longer parses HTML for product IDs. Every payload field comes from the stored row. This means the skill works cross-machine, cross-session, and from any authoring flow that calls `aeko_save_content_variation` — not just `/aeko-create-content`.

> **Backend prerequisite — three new MCP tools.** This skill requires `aeko_list_content_variations` and `aeko_publish_content_variation`. If either is missing from the current MCP session (handlers rolling out), Step 0 surfaces a friendly bilingual "come back later" message before any user prompts. The companion tool `aeko_save_content_variation` is called by `/aeko-create-content`; this skill never calls it directly.

## Input

- `item-id` (required) — `$1`. If missing, stop and point the user to `/aeko-action-center <domain_id> content` to discover the item, or to `/aeko-create-content <item_id>` if drafts don't exist yet.

## Step 0 — Backend availability preflight

The three new MCP tools (`aeko_save_content_variation`, `aeko_list_content_variations`, `aeko_publish_content_variation`) are shipped ahead of the backend handlers in some environments. This skill calls two of them; rather than introspect the tool registry (FastMCP doesn't expose a public registry API to skills), wrap the first MCP call in a try/except — if the tool isn't registered the MCP layer raises `MethodNotFound` (or equivalent), and we catch it to surface a friendly bilingual message instead of a raw stack trace.

The probe is implicit: if Step 1's `aeko_list_content_variations` call raises `MethodNotFound` / "tool not found" / equivalent, stop and print (bilingual; pick by the locale of the most recent variation row when available, else default to the user's locale):

- EN:
  ```
  aeko publish backend is rolling out

  The MCP tools that drive publish (aeko_list_content_variations,
  aeko_publish_content_variation) are the last pieces still shipping.
  Your saved drafts are preserved — re-run /aeko-publish-content <item_id>
  once the tools land. No re-drafting needed.

  Status: track AEKO release notes or run /aeko-action-center to check.
  ```
- KO:
  ```
  AEKO 게시 백엔드가 곧 출시됩니다

  게시를 담당하는 MCP 도구 (aeko_list_content_variations,
  aeko_publish_content_variation)가 마지막으로 출시 대기 중입니다.
  저장된 초안은 보존되어 있으니, 도구가 출시되면 /aeko-publish-content <item_id>를
  다시 실행하면 됩니다. 다시 작성할 필요는 없습니다.

  상태 확인: AEKO 릴리즈 노트를 확인하거나 /aeko-action-center를 실행하세요.
  ```

Exit with status code 0 — work-preserved, come-back-later. Apply the same try/except pattern around Step 6's `aeko_publish_content_variation` call.

## Step 1 — Fetch saved variations for the item

Call:

```
aeko_list_content_variations(item_id=<item_id>)
```

Three branches on the returned row count:

### 1.a — Zero rows (no saved variations)

Stop with a bilingual actionable message:

- EN:
  ```
  No saved variations for <item_id>.

  To publish via this skill:
    1) Run /aeko-create-content <item_id>
    2) When asked "Save N publishable variation(s) to AEKO backend?", answer Y.
       Both aeko_shop and own_store_blog drafts get saved if they were generated.

  If you used a different authoring flow, make sure it called
  aeko_save_content_variation under this item_id.
  ```
- KO:
  ```
  <item_id>에 저장된 변형본이 없습니다.

  이 스킬로 게시하려면:
    1) /aeko-create-content <item_id> 실행
    2) "N개의 게시 가능한 변형본을 AEKO 백엔드에 저장할까요?"에 Y로 답변하세요.
       aeko_shop과 own_store_blog 초안이 모두 생성되었다면 함께 저장됩니다.

  다른 작성 플로우를 사용한 경우, 해당 플로우가 동일 item_id로
  aeko_save_content_variation를 호출했는지 확인해 주세요.
  ```

Exit 0; no error.

### 1.b — Single row

Auto-pick. Skip directly to Step 5 (confirm) with the row's `variation_id` and `destination`.

### 1.c — Multiple rows (e.g., both `aeko_shop` and `own_store_blog`, or two `aeko_shop` versions)

Present a numbered list grouped by destination, newest-first. Show `variation_id` (short prefix), `title`, `created_at`, `status`:

```
Saved variations for <item_id>:

aeko_shop (M)
  1) <variation_id_prefix>  — <title>  · <created_at>  · status=<status>
  2) <variation_id_prefix>  — <title>  · <created_at>  · status=<status>

own_store_blog (N)
  3) <variation_id_prefix>  — <title>  · <created_at>  · status=<status>

Pick a number to publish (or `cancel`):
```

Parse the reply to a single `variation_id`. (Multi-publish — picking more than one row in one shot — is a v2 follow-up; v1 is single-select. If the user wants to publish two destinations, they re-run this skill.)

If the user picks a row whose `status == 'published'`, tell them it is already published and ask: `This variation is already published. Show stored publish result? [Y/n]`. Default `Y` → continue to Step 6 so the backend returns the stored `aeko_shop_url`/`post_id` or `draft_id` without creating duplicates. `n` → exit silently.

## Step 5 — Confirm

Print a one-block summary built from the row's `meta_summary` and other list-response fields. No local file reads — every field is from the stored row.

```
Publish plan
  destination:       <"aeko_shop" or "own_store_blog">
  item:              <item_id>
  variation:         <variation_id>
  title:             <variation.title>
  saved at:          <variation.created_at>
  has hero image:    <meta_summary.has_hero_image ? "yes" : "no">
  featured products: <meta_summary.featured_products_count> (aeko_shop upserts missing products, then maps post_products)
  locale:            <meta_summary.locale or "unknown">
  current status:    <variation.status>
```

Ask for confirmation (bilingual per `meta_summary.locale` when available; else default to user's locale):

- EN: `Proceed with publish? [y/N]`
- KO: `게시할까요? [y/N]`

If declined → stop without sending anything. Skip this prompt only when an explicit `non_interactive` flag is passed by a caller (forward-compat; no such caller exists today).

## Step 6 — Publish

Wrap the call in the same try/except pattern as Step 0 (catch `MethodNotFound`):

```
aeko_publish_content_variation(
    item_id=<item_id>,
    variation_id=<variation_id>,
)
```

The backend route reads the variation row server-side and branches on `destination`. The skill sends only `item_id` for item/variation matching — server is the source of truth for publish payload fields.

If the call fails:

- **`MethodNotFound` / tool unregistered** → emit the Step 0 bilingual "rolling out" message and exit 0.
- **4xx** — surface the backend message verbatim. Common cases:
  - `403` Pro+ tier gate failed (enforced by `publisher.enforce_publish_gate`) — common for `aeko_shop`; rare for `own_store_blog` (no tier gate on draft creation).
  - `409` `brand.aeko_shop_disabled = true` (per-brand opt-out) — `aeko_shop` only.
  - `429` Rate-limited (>10 aeko.shop publishes / hour per brand).
  - `502` Upstream aeko-shop error — re-run after the upstream recovers. Idempotent: re-running on the same `variation_id` is safe.
  - `422` Adapter validation (e.g., `body_html` or `meta.og_description` missing for `aeko_shop` — this should be caught at save time, but if it slipped through, the variation needs to be re-saved with the missing field).
- **`503` Service not configured** — the backend can't produce a clickable post URL (`AEKO_SHOP_PUBLIC_URL` unset). This is a **deployment-side** issue, **not retriable by the user**: surface the backend message and tell the user to contact support; do NOT advise re-running (it will fail identically until an operator fixes the config). The variation stays `saved`.
- **5xx / network** (excluding the 503 above) → surface error + tell the user the publish was not recorded. Re-running is safe (idempotent).

On any failure, the variation row stays in its current state — tier/disabled/rate-limit failures leave it as `saved` (retriable); 422 and 502 may flip to `failed` server-side with `last_error` populated. Already-published rows return a normal success response with stored handles.

## Step 7 — Report

On success or an already-published stored-result response, print bilingual report (per `meta_summary.locale` when available):

### For `destination == 'aeko_shop'`:

EN:
```
Published to aeko.shop:    <aeko_shop_url>
Post ID:                   <post_id>
Variation:                 <variation_id>
Status:                    published
Featured products:         <N> linked to your live catalog
Structured data:           Article + Product schemas regenerated at render time —
                           ChatGPT / Claude / Perplexity / Gemini can cite the post
                           and the linked products directly from the rendered page.
```

KO:
```
aeko.shop에 게시 완료:      <aeko_shop_url>
포스트 ID:                  <post_id>
변형본:                     <variation_id>
상태:                       published
연결된 상품:                실시간 카탈로그 <N>개 연결
구조화 데이터:              Article + Product 스키마가 렌더링 시점에 재생성되어
                            ChatGPT / Claude / Perplexity / Gemini가 본 포스트와
                            연결된 상품을 직접 인용할 수 있습니다.
```

**Then append a single soft "claim your brand" nudge** (one line, after the report block — publishing does NOT require claiming; this is optional and never blocks). The aeko.shop brand was auto-created/owned for you on publish; finishing connect-brand verifies your site and unlocks the on-site shop agent. Do not gate or repeat — just offer it once:

- EN: `Tip: your aeko.shop brand is live. If you own this site, you can finish connecting it to unlock the shop agent → https://aeko.shop/connect-brand (optional).`
- KO: `팁: aeko.shop 브랜드가 게시되었습니다. 이 사이트의 소유자라면 사이트를 연결해 숍 에이전트를 활성화할 수 있습니다 → https://aeko.shop/connect-brand (선택).`

### For `destination == 'own_store_blog'`:

EN:
```
Saved as AEKO content draft:  <draft_id>
Variation:                    <variation_id>
Status:                       published (draft row created in aeko_content_drafts)

This is a draft only — AEKO never auto-pushes to Cafe24 / Shopify CMS / your
connected store. Push from the AEKO dashboard, or wait for the future
auto-connector to land.
```

KO:
```
AEKO 콘텐츠 드래프트로 저장됨:  <draft_id>
변형본:                         <variation_id>
상태:                           게시 완료 (aeko_content_drafts에 드래프트 행 생성)

이는 드래프트일 뿐 — AEKO는 Cafe24 / Shopify CMS / 연결된 스토어로 자동
게시하지 않습니다. AEKO 대시보드에서 직접 게시하거나, 자동 커넥터 출시를
기다려 주세요.
```

If publish failed → hard stop with the backend error. The action item's completion state was already set by `/aeko-create-content`; this skill does not modify it.

## Editing or updating a post

There are two distinct edit paths depending on whether the variation has been published yet:

- **Edit a draft (not yet published).** Use `aeko_update_content_variation(variation_id, title?, body_html?, body_markdown?, metadata?)` to change a saved variation in place — tweak the body, fix `og_description`, swap the hero, add/adjust `featured_products` — without saving a whole new variation. Only the fields you pass change. The backend re-checks the `aeko_shop` contract on the merged result (non-empty `body_html`; valid `metadata` with `og_description` and an absolute-https `hero_image_url`) and returns 422 if it would break. A variation left in `failed` state is reset to `saved` on a successful edit so you can retry publish. Then publish as normal.

- **Edit an already-published post.** aeko.shop posts are upserted by `source_content_id`, which is scoped to the **action item** (`aeko-item:{item_id}`) — so every variation of that item maps to the *same* live post. To change a published post, **re-run `/aeko-create-content <item_id>` to regenerate (this saves a NEW variation) and publish it**: because the key is item-scoped, publishing the new variation **overwrites the same live post in place** — the page re-renders, images/featured-products/JSON-LD regenerate, and a changed slug emits a 308 redirect from the old URL. This never creates a `…-2 / …-3` duplicate.
  - **Re-publishing the *same* already-published variation is a no-op:** the backend returns the stored URL/post_id without re-rendering (it does not pick up edits). To push a change you must publish a *new* variation for the item — not re-publish the old one.
  - **`aeko_update_content_variation` works only on a *not-yet-published* draft** (it returns 409 on a published variation). So the "edit then publish" path applies to drafts; for an already-live post, regenerate + publish.

> **No version history.** Variations are not snapshotted/recoverable after publish — re-publishing overwrites the live post and the previous rendered version is not retained. If you need to keep the prior copy, save it before overwriting. Published variations themselves are immutable via `aeko_update_content_variation` (returns 409); edit happens by re-publishing, not by mutating the published row.

## Error paths

- Tools rolling out (`MethodNotFound` at Step 1 or Step 6) → emit Step 0 bilingual message; exit 0.
- Zero saved variations → emit Step 1.a actionable message; exit 0.
- User cancels at Step 1.c picker → exit 0 silently.
- User declines at Step 5 → exit 0 silently.
- Backend publish 4xx (tier / disabled / 422) → surface backend message; do not retry.
- Backend publish 5xx / network → surface; instruct re-run; rely on idempotency.

## Hard rules

- **Backend rows are the source of truth.** This skill never reads local `./aeko-artifacts/` files. The variation row's `body_html` / `body_markdown` / `metadata` ARE the publish payload — whatever is stored is what gets published.
- **Single-select.** v1 publishes one `variation_id` per invocation. Multi-publish is deferred; users who want to publish both `aeko_shop` and `own_store_blog` simply re-run this skill.
- **Never modifies the variation row from the skill.** Status transitions (`saved` → `published`, `saved` → `failed`) happen server-side inside the publish route's transaction.
- **Never auto-posts to external stores.** `own_store_blog` creates an AEKO-owned draft only. No Cafe24, no Shopify CMS, no third-party APIs are called by this skill or by the backend route. The future auto-connector (separate ticket) will push from `aeko_content_drafts`.
- **Never widens `allowed-tools`** to include disk reads, browser-bridge tools, or external-channel APIs.
- **Idempotent.** Re-running on the same `(item_id, variation_id)` is safe — backend returns stored URL/draft_id on already-published rows without creating duplicates.
- **Never read prose to extract machine values** — `post_id`, `aeko_shop_url`, `draft_id`, `status` come only from the structured MCP response.

## What this skill never does

- Never writes to Tistory, Naver Blog, Instagram, TikTok, YouTube, or any external channel directly.
- Never reads or writes local `./aeko-artifacts/` files.
- Never modifies the variation row from the skill (status flips are server-side).
- Never modifies the originating action item's completion state (that was set by `/aeko-create-content`).
- Never publishes a variation that wasn't saved via `aeko_save_content_variation` — the stored row is the source.
- Never invents URLs or post IDs — those come from the MCP response, or the call failed.
- Never calls Cafe24 / Shopify CMS live publish APIs for `own_store_blog` — that destination is draft-only.
