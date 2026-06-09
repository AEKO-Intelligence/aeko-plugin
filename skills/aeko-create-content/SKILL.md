---
name: aeko-create-content
version: 0.15.1
description: >
  Multi-channel AEO content executor for Action-tab items with
  `execution_class=local_content_artifact`. Fetches a Plan.md, pulls
  the substance to write from — product info (`aeko_get_product_description`
  + Plan `products[]`), product context-reviews (lived experience), the
  tracked prompts the brand wants to be cited for, and the brand kit — then
  fans out per-channel drafters IN PARALLEL, each writing genuinely original,
  citable content via proven AEO frameworks (BLUF, PREP, Informational Gain,
  E-E-A-T). Optional `+ competitive context` mode adds the tracked-prompt
  snapshot's current AI answer + cited snippets for a gap/contrarian angle
  (no crawling; takes longer). Saves local artifacts; auto-saves aeko.shop
  publish variations to the AEKO backend; never writes to a connected store
  and never auto-publishes.
argument-hint: "<item-id> [deep]"
allowed-tools: aeko_get_action_plan, aeko_get_brand_kit, aeko_get_brand_kit_by_id, aeko_list_brand_kits, aeko_get_product_description, aeko_get_product_context_reviews, aeko_resolve_prompts_by_text, aeko_get_tracked_prompts, aeko_get_tracked_prompt, aeko_list_own_content, aeko_request_media_upload, aeko_save_content_variation, aeko_list_content_variations, aeko_complete_action_item, Task, Read, Write, Bash, WebFetch, WebSearch
---

# AEKO Create Content

**Changelog v0.15.1** — Restored example-file loading in the parallel drafter contract, added `Refs loaded`
reporting so marketers can verify customization, and clarified `press_release` / 보도자료 slug handling.

**Changelog v0.15.0** — Added AI-shopping decision-guide blocks, visible-content/schema parity, and
anti-manipulation guardrails across content + JSON-LD recipes. Updated completion summaries to explain
source material, publish safety, revision path, and next step in marketer-facing language.

**Changelog v0.14.0** — Re-architected from forensics-mimicry to **framework-driven AEO**. Removed the
Phase 3A/3B citation-forensics crawl engine (`aeko_crawl_url`, recrawl budgets, `cited_url_allowlist`,
structural-target mimicry, crawl-based channel detection). Content substance now comes from **product
info + context-reviews + the prompt + brand kit**; quality comes from the **AEO frameworks** in
`references/aeo-frameworks.md` (BLUF, PREP, Informational Gain, E-E-A-T). Per-channel drafting now **fans
out to parallel drafter subagents** instead of a sequential loop (see Step 5). New optional
`+ competitive context` mode (arg `deep`) surfaces the tracked-prompt snapshot's current AI answer + cited
snippets for a gap/contrarian angle — no crawling, but it takes noticeably longer, so the skill warns
first. New tools: `aeko_get_product_description`, `aeko_get_product_context_reviews`. The aeko.shop
publish mechanics (media upload, sanitizer-safe HTML, meaningful-English slug, `.meta.json` payload,
product callouts) are unchanged and live in `references/recipes/editorial-html-jsonld.md`.

**Two-tier channel model (v0.14.0).** Only **owned-web surfaces** get HTML + JSON-LD engineering, because
AEO there depends on markup AEKO/the store controls: **`aeko_shop`** (body-only HTML; the aeko.shop
frontend regenerates JSON-LD) and **`own_store_blog`** (now *upgraded* to self-contained HTML with
*embedded* JSON-LD + responsive markup, since the brand's store renders it as-is and won't regenerate
schema). All other channels are **paste-into-platform** — the platform/editor (Naver, Tistory, Instagram,
a media outlet) owns the final markup, so they ship as **clean text/markdown only** with thin convention
notes. This demotes `press_release`/`magazine`/`partner_media` from HTML+JSON-LD output to text. The
`press_release` channel is language-aware (Korean 합니다체 **or** English AP-style) — it serves KO- and
EN-market brands equally; the slug is ASCII (`press_release`), the KO label stays `보도자료`.

Executes one Action-tab content item end-to-end: fetch Plan.md → pull product/review/prompt substance →
pick mode → confirm channels + media → **fan out parallel per-channel drafters** that write framework-driven
artifacts in the brand voice → verify (re-checking publish-blocking gates) → auto-save `aeko_shop`
publish variations → mark complete only after required saves succeed.

Contract reference: `docs/contracts/action-item-contract.md` §3 (Plan.md), §3.2.1 (ProductRef), §6
(completion). Pinned to contract minor `v1.5`; tolerant of v1.3/v1.4 Plans where `brand_kit_id` or
`products[]` is absent.

## Marketer-facing output contract

Frame this as "drafting content AI can cite." Open with channels, source material, read/write safety, and whether
anything can publish live. Default copy should avoid internal terms like `execution_class` and raw frontmatter.
Before saving variations, show what will be saved, where it can appear, risk, and how to revise/undo.

## Input

- `item-id` (required) — `$1`. If missing, stop and point user to `/aeko-action-center <domain_id> content`.
- `mode` (optional) — `$2`. `deep` (or `competitive`) pre-selects the `+ competitive context` mode and
  skips the Step 2.5 prompt. Anything else / absent → ask in Step 2.5 (default Standard).

## Step 0 — Front-load deferred tools (do this FIRST, once per run)

Issue exactly ONE `ToolSearch` call before any other tool use:

```
ToolSearch(query="select:aeko_get_action_plan,aeko_get_brand_kit,aeko_get_brand_kit_by_id,aeko_list_brand_kits,aeko_get_product_description,aeko_get_product_context_reviews,aeko_resolve_prompts_by_text,aeko_get_tracked_prompts,aeko_get_tracked_prompt,aeko_list_own_content,aeko_request_media_upload,aeko_save_content_variation,aeko_list_content_variations,aeko_complete_action_item,Task,WebFetch,WebSearch", max_results=20)
```

Record `loaded_tools[]` for diagnostics. Do not add stale-MCP fallback branches: if a save/substance tool
is missing, the relevant step's degrade path handles it and the user should update the AEKO MCP. Do not
load deferred tools one-at-a-time mid-run.

> Reference-file reads (`references/aeo-frameworks.md`, `references/drafter-instructions.md`, recipes,
> examples) are **not** loaded by the coordinator — each drafter subagent reads what it needs (Step 5).
> The coordinator only reads `references/examples/context-reviews-fixture.md`, and only as a Step 3 fallback.

## Step 1 — Fetch and parse the Plan.md

Call `aeko_get_action_plan(item_id)`. Parse the frontmatter + prose. Validate `execution_class ==
local_content_artifact` (else stop and route to the right skill). Extract:

- **`resolved_title`** — frontmatter `title` → Plan `# H1` → `item_id` (chain; first non-empty wins).
- **`domain_id`**, **`brand_kit_id`** (if present), **`persona_label`** (if present).
- **`parsed_products[]`** — optional. Backend `build_plan_md()` hydrates this from the user's selected
  store products; each entry should carry `id`, `source_id`, `name`, `slug`, `sku`, `outbound_url`,
  `image_url`, `short_description`. **Drop with a loud warning** any entry missing `id`/`source_id`/`name`/
  `outbound_url`/`image_url` (most common: no store-synced `source_id`). If the Plan was created in
  product-select mode but `parsed_products[]` is empty after validation, warn loudly — products won't link.
- **`must_include[]`**, **`forbidden[]`**, **`sections_required[]`**, **`prompts_to_rank_on`** (raw prompt
  text or IDs the brand wants to be cited for).

Print a compact bilingual context header (domain, title, persona, product count). Never echo raw frontmatter.

## Step 2 — Resolve the brand kit (voice)

Resolve in order: `aeko_get_brand_kit_by_id(brand_kit_id)` → `aeko_get_brand_kit(domain_id)` →
`aeko_list_brand_kits(domain_id)`. Capture `tone_of_voice`, `brand_voice_summary`, `target_audience`,
`must_include`, `forbidden`, `aeko_shop_disabled`, and richness fields (`logo_url`, `primary_url`,
`tagline`). If the voice fields are empty and the kit is `draft`/`generating`, warn but continue.
Keep `resolved_brand_kit_id` for media presign and the structured-data gate.

## Step 2.5 — Mode selection (Standard vs + competitive context)

If `$2` is `deep`/`competitive`, set `mode = competitive` and skip the prompt. Otherwise ask ONE
bilingual question, defaulting to Standard:

```
어떤 방식으로 콘텐츠를 만들까요? / How should I generate this content?

  [1] 표준 / Standard  (기본)
      제품 정보 + 컨텍스트 리뷰 + 프롬프트 + 브랜드 보이스로 작성. 빠릅니다.
      Product info + context-reviews + prompt + brand voice. Faster.

  [2] + 경쟁 컨텍스트 / + Competitive context
      추적 중인 프롬프트의 현재 AI 답변과 인용 출처를 함께 분석해
      'AI가 아직 말하지 않은 빈틈/반대 관점'을 찾습니다. (크롤링 없음)
      ⚠ 시간이 더 오래 걸립니다 / This takes noticeably longer.
```

Set `mode ∈ {standard, competitive}`. The warning on option 2 is mandatory — competitive mode runs extra
tracked-prompt analysis and hands each drafter more context, so it is slower.

## Step 3 — Pull the substance (the *what to write about*)

This is the substance backbone. When `parsed_products[]` is non-empty (the usual case), issue a single
**parallel batch** of, per product `p`:

- `aeko_get_product_description(p.source_id or p.id)` → full product copy / specs (`full_description`).
- `aeko_get_product_context_reviews(p.source_id)` → lived-experience reviews keyed by context/persona.

Build `substance` = `{ products: [...with full_description...], context_reviews: [...] }`.

**Degrade gracefully:**
- `aeko_get_product_context_reviews` missing/empty → continue; product copy still carries substance.
  For evals or when no live reviews exist, read `references/examples/context-reviews-fixture.md` and use
  matching `product_source_id` entries as the review pool. Note in the summary that reviews were a fixture.
- `aeko_get_product_description` 4xx/5xx → fall back to the `parsed_products[]` Plan fields alone; warn once.

**No-product fallback** — when `parsed_products[]` is empty: skip the product/review calls entirely. The
drafters will write from the prompt + brand kit + their own expertise (honest expertise, never faked
experience — see `references/aeo-frameworks.md` anti-fabrication rule), and Step 8 surfaces a bilingual
note that attaching a product (and its context-reviews) yields more original content.

## Step 3b — Light signal / competitive context (mode-aware)

Resolve the prompts: `aeko_resolve_prompts_by_text(prompts_to_rank_on)` → prompt UUIDs. Then
`aeko_get_tracked_prompt(prompt_id, window="latest")` for up to 5 prompts (single parallel batch). If no
prompts resolve, continue (the prompt text itself still gives topic/intent) — do NOT hard-stop.

- **Standard mode:** keep only the *signal* — for each top cited source **domain**, map it to a channel
  slug via the inline map below to build `suggested_channels[]`, and optionally derive a one-line
  `contrarian_hint` from how the brand currently appears (or doesn't). **Do not retain response bodies.**
- **+ Competitive context mode:** additionally retain, per resolved prompt, the **current AI answer** and
  the **600-char cited snippets** + who's-mentioned. Distill these into a compact `competitive_brief`:
  what the consensus answer says, which competitors win it, and the **gap/contrarian angle** the brand can
  own. This is intelligence already in the snapshot — **never call `aeko_crawl_url`, never fetch pages,
  never build a URL allowlist.** Pass `competitive_brief` + `contrarian_hint` into each drafter brief.

Inline domain→channel suggestion map (replaces the old crawl-based detector): `*.blog.naver.com` →
`naver_blog`; `*.tistory.com` → `tistory`; `reddit.com` → `reddit`; news/매체 domains → `partner_media`;
`youtube.com` → `youtube`; `instagram.com` → `instagram`. Anything else (wikipedia, generic web) →
ignore for channel suggestion. Suggestions are a convenience for Step 4; the user always confirms.

## Step 4 — Channel & media selection (interactive)

### 4.0 Auto-add aeko.shop + own-store for tenant brands
aeko.shop is AEKO's canonical destination. Prepend `aeko_shop` to the pre-checked set unless
`brand_kit.aeko_shop_disabled === true` (missing/malformed → include it; emit a one-line "assuming
enabled" note). Append `own_store_blog` to the offered set. Both are backend-saved draft targets; this
skill never writes to the connected store.

### 4-Form-1 Channel selection
Issue ONE elicitation form. Pre-check `suggested_channels[]` (from Step 3b) + `aeko_shop` + `own_store_blog`;
offer addon toggles: `press_release`, `magazine`, `instagram`, `tiktok`, `youtube`, `naver_blog`, `tistory`,
`reddit`, `other:<ascii_name>` (free-form `<name>` + optional reference URL/description; reject non-ASCII
`<name>`). Selecting `aeko_shop` is consent to backend-save after drafting. Use the §8.0 bilingual labels.
**If 0 channels selected → stop** (bilingual notice; do not complete the item).

### 4-Form-2 Per-channel media + alt-text
Issue a SECOND form. Per selected channel, collect image slots (editorial: hero + up to 2 inline; social:
one image; tiktok/youtube also a video-reference URL) with a **required alt-text** per populated slot and a
"skip media for this channel" option. Accept file upload OR a pasted URL. Image MIME must be
`image/(jpeg|png|webp|gif)`. Parse into `media_by_channel{}` (`{slot: {src, alt, type} | null}`). For
`aeko_shop`, a single supplied image with empty inline slots is the hero; when products exist the first
product image auto-fills the hero.

## Step 5 — Fan out parallel per-channel drafters

This replaces the old sequential Step 5 loop. Drafting is independent per channel, so run it in parallel.

### 5.1 Compute shared identifiers ONCE (coordinator owns these)
- `slug` — per **§A (slug derivation)** from `resolved_title`.
- `filename_token` per channel — per **§A (alias map)**.
- `aeko_shop_publish_slug` — meaningful **English** slug per **§A**, for the aeko.shop `.meta.json`.

### 5.2 Build one brief per selected channel and spawn drafters in ONE message
For each selected channel, spawn a `Task` (general-purpose) drafter **in a single message** (so they run
concurrently). Each drafter's prompt instructs it to:
> Read `skills/aeko-create-content/references/drafter-instructions.md` and
> `skills/aeko-create-content/references/aeo-frameworks.md` (and, for editorial/HTML channels,
> `skills/aeko-create-content/references/recipes/editorial-html-jsonld.md`; for channels with a recipe,
> `skills/aeko-create-content/references/recipes/<channel>.md`). Also read matching example files when
> present per drafter-instructions.md §2. Then draft this channel and return the self-check JSON defined
> in drafter-instructions.md §4.

Pass the JSON brief (the shape in drafter-instructions.md §1): `channel`, `domain_id`, `item_id`,
`resolved_title`, `slug`, `filename_token`, `aeko_shop_publish_slug` (aeko_shop only), `target_language`,
`brand_voice_summary`, `target_cohort` (sharpen from `target_audience` + persona + the prompt),
`must_include`, `forbidden`, `sections_required`, `contrarian_hint`, `competitive_brief` (competitive mode
only), `products` (with `full_description`), `context_reviews`, `media` (= `media_by_channel[channel]`),
`recipe_path`, `voice_overrides` (scoped block, if `references/style/voice-overrides.md` has one for this
domain/channel), and `resolved_brand_kit_id` (aeko_shop only, for media presign).

**Recipe routing by tier.** Owned-web channels (`aeko_shop`, `own_store_blog`) get
`recipe_path: references/recipes/editorial-html-jsonld.md` — that recipe covers both (aeko_shop = body-only,
no in-body JSON-LD; `own_store_blog` = self-contained HTML with *embedded* JSON-LD + responsive markup,
since the brand's store won't regenerate schema). Paste-tier channels with a recipe (`naver_blog`,
`tistory`, `instagram`, `tiktok`, `youtube`, `press_release`, `magazine`) get their thin
`references/recipes/<channel>.md`. Channels with no recipe (`reddit`, `partner_media`, `other:<name>`) get
`recipe_path: null` — the drafter works from frameworks + brand voice (+ matching example files per
drafter-instructions.md §2 when present).

Collect each drafter's returned self-check into `drafter_results[]`. A drafter that returns no usable
result (skipped/errored) is recorded as a failed channel; continue with the rest.

## Step 6 — Verify (coordinator re-checks publish-blocking gates)

Drafters self-check, but their self-reports cannot be trusted for publish-blocking gates. The coordinator
re-verifies before any save:

- **Universal (every artifact):** no placeholder markers (`[Image`/`[photo`/`[placeholder`/`TODO` in body);
  every image has non-empty alt; `forbidden` strings absent; `must_include` strings present across the
  artifact set (not necessarily every channel); no fabricated external URLs (URLs must be from
  `products[].outbound_url`, the brand kit, or user-supplied media in `media_by_channel{}` — there is no
  crawl allowlist anymore).
- **Framework quality (read each artifact):** BLUF in the opening; PREP-shaped body; ≥1 originality detail
  (traceable to a real context-review, or expertise-grounded + flagged when no reviews); a specific cohort
  named; ≥1 contrarian/non-obvious claim; FAQ answers (if any) show E-E-A-T. Weak on a soft dimension →
  ask the drafter (or redraft) once; cap 2 soft iterations per artifact.
- **`aeko_shop` hard gates (re-run against the produced files — these block publish):** `.meta.json` parses
  and carries required `PostUpsert` fields; `slug` present, matches `^[a-z0-9]+(?:-[a-z0-9]+)*$`, and (for a
  non-ASCII title) is NOT equal to the romanized filename slug; `.html` is **sanitizer-safe** (zero
  `<script|article|header|footer|section|h1|meta|title|link|html|body|head>` — aeko.shop-specific); every
  body `<img src>` is an AEKO-media-CDN `public_url` (never a brand-domain URL, never `cdn.aeko.shop`); every
  `<img>` has `alt`/`width`/`height`/`loading`; the set of `data-product-source-id` in `.html` equals
  `featured_products[].product_source_id` in `.meta.json`; no `[image: …pending]` placeholders; structured-data
  completeness (title, `og_description`, brand kit resolved; product fields when products attached).
- **`own_store_blog` hard gates (self-contained — the store renders it as-is, won't regenerate schema):**
  `.html` parses; it **embeds** `<script type="application/ld+json">` carrying `Article`/`BlogPosting`
  (always) **plus `Product`** when products are attached, and each block parses with `json.loads` with its
  required fields; every `<img>` is responsive (`alt` + `width`/`height` + `loading` + `max-width:100%`
  style) and references a real URL (product `image_url`/brand CDN or user-supplied — **no** AEKO-media
  presign here); no placeholder markers. Unlike aeko_shop it is **not** sanitizer-constrained — semantic
  tags (`<article>`/`<h1>`/`<script>` JSON-LD) are expected.

One fix iteration on any hard-gate failure; still failing → leave the item `pending`. Full gate definitions
live in `references/recipes/editorial-html-jsonld.md`.

## Step 7 — Validate & save

Proceed only if ≥1 artifact was written and every written artifact passed its hard gates.

`publishable_artifacts[]` = drafted channels whose destination is `aeko_shop` or `own_store_blog`.
**`aeko_shop` save is mandatory** once selected (Form-1 selection was consent). Every other channel is
local-only.

- If `publishable_artifacts` is empty → call `aeko_complete_action_item(item_id, artifact_summary,
  artifact_paths=[all files], write_result=None)`; set `saved_variations=[]`; go to Step 8.
- Otherwise, for each publishable artifact call `aeko_save_content_variation(item_id, destination, title,
  body_html, body_markdown, metadata, artifact_paths)`. For `aeko_shop`, `metadata` carries
  `featured_product_source_ids[]` (may be `[]`) plus full `featured_products[]` snapshots (join key is
  `product_source_id`, never `ProductRef.id`); body-only `body_html`; `slug` = `aeko_shop_publish_slug`.
  For `own_store_blog`, populate BOTH `body_html` (the self-contained, embedded-JSON-LD `.html`) and
  `body_markdown` (the mirror); `metadata = {title, og_description, slug}` (no `featured_products` payload —
  the embedded JSON-LD already carries Product schema). Collect `variation_id`s. **On any save failure:** do NOT complete; leave `pending`; print bilingual retry
  guidance; stop (skip Steps 8–9). **On all saves succeed:** `aeko_complete_action_item(... write_result=
  {"backend_variations": saved_variations})`.

## Step 8 — User-facing summary

### 8.0 Channel labels (bilingual — never a bare slug)
`aeko_shop`=aeko.shop용 HTML / aeko.shop HTML · `naver_blog`=네이버 블로그용 초안 / Naver Blog draft ·
`tistory`=티스토리용 초안 / Tistory draft · `instagram`=Instagram용 캡션 / Instagram caption ·
`tiktok`=TikTok용 스크립트 / TikTok script · `youtube`=YouTube용 스크립트 / YouTube script ·
`magazine`=매거진 기고용 / Magazine pitch · `press_release`=보도자료 초안 / Press release draft ·
`partner_media`=파트너 미디어용 / Partner media draft · `reddit`=Reddit 포스트 초안 / Reddit post ·
`own_store_blog`=자사몰 블로그 초안 / Own-store blog draft · `other:<name>`=`<name> 초안` / `<name> draft`.
Lead with the label matching `target_language`.

### 8.1 Summary block
Print a marketer-facing block first, then technical details:

```
✔ Content drafts ready

What AEKO created
- <bilingual channel labels> for <brand/domain>

Source material used
- Product facts: N
- Real review/context details: N (or "none — attach product reviews for more original content")
- Brand Kit: <loaded|missing>

Safety
- This skill did not publish anything live.
- Connected store content was not changed.

Revision path
- Edit local drafts or saved backend variations, then publish only when ready.

Recommended next step
- <one command: /aeko-publish-content <item_id> when saved variations exist, otherwise /aeko-action-center <domain_id> content>
```

After that, include artifacts (one bilingual line + path per file), media refs (N with alt / M skipped),
`Refs loaded` (recipe + example paths per channel, so users can verify customization was picked up),
citability (passed N/N · failed: list or none), and the "publish checklist (never auto-published by AEKO)"
for client-managed channels.

## Step 9 — Publish handoff (read-only)

This skill never publishes. Gated on `saved_variations`:
- Contains `aeko_shop` → print the dedicated, unmissable aeko.shop block first: the three file paths, a
  one-line structural summary (`<h2>` count · tables · inline images · body chars · hero url|null · product
  callouts), and `게시 명령어 / Publish command: /aeko-publish-content <item_id>`. Do NOT inline a raw-HTML
  preview. Then add the non-aeko_shop tail (own_store_blog → AEKO-owned draft row you push later).
- Non-empty but no `aeko_shop` → print the plain `Publish: /aeko-publish-content <item_id>` line.
- Empty → omit the publish line; the §8 checklist is the only post-creation guidance.

Optional: if a Chrome bridge is detected, append one hint that `/chrome` can help post client-managed
channels. Hard rules: never invoke/simulate `/aeko-publish-content`; never widen `allowed-tools` to browser
or external-posting APIs; the only publish-side capability is `aeko_request_media_upload` for aeko_shop media.

---

## §A — Slug & filename rules (coordinator computes once; passed to drafters)

### A.1 filename_token alias map
`filename_token == channel_slug` for every channel (all slugs are now ASCII, including `press_release`)
**except** `other:<ascii_name>` → `other_<ascii_name>` (collapse `:`→`_`; reject non-ASCII names at Form-1).
The alias affects filesystem OUTPUT only — recipe lookup always uses `channel_slug` (`references/recipes/<channel_slug>.md`).

### A.2 Path template
`./aeko-artifacts/<domain_id>/<item_id>/<filename_token>/<slug>__<filename_token>.<ext>`

| channel | extension(s) |
| --- | --- |
| Paste-tier (`reddit`, `naver_blog`, `tistory`, `partner_media`, `instagram`, `tiktok`, `youtube`, `press_release`, `magazine`) | `.md` (text only — the platform/editor renders it) |
| `own_store_blog` (owned-web) | `.html` (self-contained, embedded JSON-LD, responsive) + `.md` mirror |
| `aeko_shop` (owned-web) | `.html` (body-only, frontend regenerates JSON-LD) + `.meta.json` + `.md` (publish-ready triple) |

### A.3 slug derivation (local file slug)
From `resolved_title`: lowercase → ASCII-fold non-ASCII (Hangul → romanization; drop if no fold) → replace
non-alphanumeric runs with a single `-` → truncate to 60 chars at a word boundary → strip leading/trailing
`-`. On collision within a channel dir, append `-2`, `-3`, …. **Empty-slug fallback:** if the result is
empty (e.g. all-Hangul title with no fold), use `<item_id>` — never write a hidden `__<channel>.md`.

### A.4 aeko_shop publish slug (meaningful English — REQUIRED, §6 hard gate)
The §A.3 slug is for local files only. The **published** aeko.shop URL needs a *meaningful English* slug in
`.meta.json slug`: translate the meaning (don't transliterate), 3–8 words, lowercase, hyphen-joined,
`^[a-z0-9]+(?:-[a-z0-9]+)*$`, ≤70 chars, drop stop-words; use a brand/product's established Latin name when
it has one (don't invent names). Example: `에스테틱 모공팩을 집에서…` → `volcanic-clay-pore-pack-home-guide`.
For a non-ASCII title this MUST differ from the §A.3 romanized filename slug (that reuse is the
phonetic-gibberish 404 bug). For an already-English title, reusing the §A.3 slug is fine.

## Error paths

- Plan unavailable / parse error / contract mismatch → stop with detail.
- Stale brand kit + user declines → stop.
- No prompts resolve in Step 3b → continue on prompt text + product/review substance (do NOT hard-stop;
  this is no longer forensics-gated).
- `aeko_get_product_context_reviews` / `aeko_get_product_description` unavailable → degrade per Step 3.
- A drafter subagent errors/skips → record the channel as failed, continue with the rest.
- Citability hard-gate fails after the fix iteration → leave item `pending`; surface failed channels + dimensions.
- aeko.shop media upload fails → drafter omits that image, produces a valid text-only post, warns loudly; never a placeholder.
- Backend save fails → do NOT complete; item stays `pending`; bilingual retry guidance; skip Steps 8–9.
- 0 channels selected at Form-1 → stop without writing or completing.

## What this skill never does

- Never crawls competitor/cited pages (`aeko_crawl_url` is gone) — competitive context, when requested,
  comes only from the tracked-prompt snapshot already fetched.
- Never **fabricates lived experience** — Originality and E-E-A-T Experience must trace to real
  context-reviews or product facts; no reviews → expertise-grounded + flagged (see aeo-frameworks.md).
- Never writes to a connected store (that's `/aeko-update-pdp`) and never auto-publishes (that's
  `/aeko-publish-content`, aeko.shop only). All other channels are generation-only outputs.
- Never copies or uploads media for non-aeko_shop channels — references only. `aeko_shop` is the single
  exception — its media upload procedure lives in `references/recipes/editorial-html-jsonld.md`.
- Never emits `[Image]`/`[photo]`/`[placeholder]`/`TODO` body markers; never invents URLs; never echoes raw
  frontmatter; never regenerates the Plan.md; never proceeds past Form-2 without an explicit submit.
