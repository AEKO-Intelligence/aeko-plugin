---
name: aeko-create-content
description: >
  Multi-channel AEO content executor for Action-tab items with
  `execution_class=local_content_artifact`. Fetches a Plan.md, pulls
  the substance to write from — product info (`aeko_get_product_description`
  + Plan `products[]` + visible PDP/page evidence), product context-reviews (lived experience), the
  tracked prompts the brand wants to be cited for, and the Plan's content context — then
  fans out per-channel drafters IN PARALLEL, each writing genuinely original,
  citable content via proven AEO frameworks (BLUF, PREP, Informational Gain,
  E-E-A-T). Optional `+ competitive context` mode adds the tracked-prompt
  snapshot's current AI answer + cited snippets for a gap/contrarian angle
  (no crawling; takes longer). Saves local artifacts; auto-saves aeko.shop
  publish variations to the AEKO backend; never writes to a connected store
  and never auto-publishes.
argument-hint: "<item-id> [deep]"
allowed-tools: aeko_get_action_plan, aeko_get_product_description, aeko_get_product_context_reviews, aeko_resolve_prompts_by_text, aeko_get_tracked_prompts, aeko_get_tracked_prompt, aeko_list_own_content, aeko_request_media_upload, aeko_save_content_variation, aeko_list_content_variations, aeko_complete_action_item, Task, Read, Write, Bash, WebFetch, WebSearch
---

# AEKO Create Content

**Changelog v0.15.3** — Added in-run owned-channel/content-example intake for users who skipped onboarding.
The Step 4 channel form now asks for owned channels, URLs, or pasted examples to mimic, and asks whether to
save them into `references/examples/` for future runs. Saved examples are style/structure references only.

**Changelog v0.15.2** — Added the user-language output contract: skill steps, confirmations, risk notes,
and summaries mirror the user's chat language, while `target_language` controls generated artifacts.

**Changelog v0.15.1** — Restored example-file loading in the parallel drafter contract, added `Refs loaded`
reporting so marketers can verify customization, and clarified `press_release` / 보도자료 slug handling.

**Changelog v0.15.0** — Added AI-shopping decision-guide blocks, visible-content/schema parity, and
anti-manipulation guardrails across content + JSON-LD recipes. Updated completion summaries to explain
source material, publish safety, revision path, and next step in marketer-facing language.

**Changelog v0.14.0** — Re-architected from forensics-mimicry to **framework-driven AEO**. Removed the
Phase 3A/3B citation-forensics crawl engine (`aeko_crawl_url`, recrawl budgets, `cited_url_allowlist`,
structural-target mimicry, crawl-based channel detection). Content substance now comes from **product
info + page-level evidence + context-reviews + the prompt + content context**; quality comes from the **AEO frameworks** in
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
artifacts for the content context → verify (re-checking publish-blocking gates) → auto-save `aeko_shop`
publish variations → mark complete only after required saves succeed.

Contract reference: `docs/contracts/action-item-contract.md` §3 (Plan.md), §3.2.1 (ProductRef), §6
(completion). Pinned to contract minor `v1.5`; tolerant of legacy Plans where `brand_kit_id` appears,
but the current source for content optimization is Plan.md context, not legacy identity fields or ICP.

## Marketer-facing output contract

Frame this as "drafting content AI can cite." Open with channels, source material, read/write safety, and whether
anything can publish live. Default copy should avoid internal terms like `execution_class` and raw frontmatter.
Before saving variations, show what will be saved, where it can appear, risk, and how to revise/undo.

**Plain words, not jargon.** Never surface "forensics" / 포렌식 in user-facing copy (it reads as crime-lab
jargon to marketers). In English say **source analysis**; in Korean say **AI 답변 참고 출처** (the sources AI
references in its answers). "Forensics" elsewhere in this doc is an internal label only.

**Only these interactive prompts exist in this skill:** the Step 2.5 mode question, the Step 4 channel +
owned-example form, and the Step 4 media form. Do **not** invent extra decision forms — most importantly,
do not add a "how should I proceed?" gate when the citation signal is thin. A thin or empty signal (zero
citations, prompts still in an AEKO re-query cycle, an un-indexed domain / own-content 404) is the
**normal early state for a new brand, not an error**. When the content context + product substance are
present, a Plan-only draft is fully workable: note the thin signal in one plain line and proceed straight
to Step 4. If the user did not onboard, capture optional owned-channel/content examples inside Step 4;
never ask a separate onboarding-style question outside Step 4.

Language: mirror the user's chat language for user-facing steps, summaries, questions, and risk/undo copy.
Keep slash commands, IDs, file paths, channel slugs such as `press_release`, schema keys, JSON-LD terms, and tool names in English/ASCII.
When a Plan includes `target_language`, use it for generated artifacts; do not let it override the assistant UI language.

## Input

- `item-id` (required) — `$1`. If missing, stop and point user to `/aeko-action-center <domain_id> content`.
- `mode` (optional) — `$2`. `deep` (or `competitive`) pre-selects the `+ competitive context` mode and
  skips the Step 2.5 prompt. Anything else / absent → ask in Step 2.5 (default Standard).

## Step 0 — Front-load deferred tools (do this FIRST, once per run)

Issue exactly ONE `ToolSearch` call before any other tool use:

```
ToolSearch(query="select:aeko_get_action_plan,aeko_get_product_description,aeko_get_product_context_reviews,aeko_resolve_prompts_by_text,aeko_get_tracked_prompts,aeko_get_tracked_prompt,aeko_list_own_content,aeko_request_media_upload,aeko_save_content_variation,aeko_list_content_variations,aeko_complete_action_item,Task,WebFetch,WebSearch", max_results=20)
```

Record `loaded_tools[]` for diagnostics. Do not add stale-MCP fallback branches: if a save/substance tool
is missing, the relevant step's degrade path handles it and the user should update the AEKO MCP. Do not
load deferred tools one-at-a-time mid-run.

> Reference-file reads (`references/aeo-frameworks.md`, `references/drafter-instructions.md`, recipes,
> persistent examples) are **not** loaded by the coordinator — each drafter subagent reads what it needs
> (Step 5). The coordinator only reads `references/examples/context-reviews-fixture.md` as a Step 3
> fallback, and may collect/write user-supplied owned examples in Step 4 when the user explicitly opts in.

## Step 1 — Fetch and parse the Plan.md

Call `aeko_get_action_plan(item_id)`. Parse the frontmatter + prose. Validate `execution_class ==
local_content_artifact` (else stop and route to the right skill). Extract:

- **`resolved_title`** — frontmatter `title` → Plan `# H1` → `item_id` (chain; first non-empty wins).
- **`domain_id`**, **`persona_label`** (if present), and **content context fields** from frontmatter/prose
  (`context`, `use_case`, `buyer_context`, `pain_points`, `desired_outcome`, `tone`, `positioning`,
  `audience`, or equivalent labels). Treat `brand_kit_id` as legacy only. Do not use ICP here; ICP is
  scoped to prompt tracking.
- **`parsed_products[]`** — optional. Backend `build_plan_md()` hydrates this from the user's selected
  store products; each entry should carry `id`, `source_id`, `name`, `slug`, `sku`, `outbound_url`,
  `image_url`, `short_description`. **Drop with a loud warning** any entry missing `id`/`source_id`/`name`/
  `outbound_url`/`image_url` (most common: no store-synced `source_id`). If the Plan was created in
  product-select mode but `parsed_products[]` is empty after validation, warn loudly — products won't link.
- **`must_include[]`**, **`forbidden[]`**, **`sections_required[]`**, **`prompts_to_rank_on`** (raw prompt
  text or IDs the brand wants to be cited for).

Print a compact context header in the user's chat language (domain, title, persona, product count). Never echo raw frontmatter.

## Step 2 — Resolve content context (use case, situation, and voice)

Do **not** call legacy identity tools. Build `content_context` from
the Plan.md frontmatter + prose:

- `context` / `use_case` / `buyer_context` / `pain_points` / `desired_outcome` → the situation and job to
  solve.
- `audience` / `persona` only when they appear as content context in the Plan; do not infer or apply ICP.
- `tone` / `positioning` / `must_include` / `forbidden` / `sections_required` → voice and constraints.
- Domain/title/product/prompt facts → fallback voice when no explicit tone exists.

If content context is thin, warn in one user-language line and continue. Thin context is not publish-blocking;
draft with a neutral, specific, evidence-first voice derived from the product facts and prompt.

## Step 2.5 — Mode selection (Standard vs + competitive context)

If `$2` is `deep`/`competitive`, set `mode = competitive` and skip the prompt. Otherwise ask ONE
question in the user's chat language, defaulting to Standard. For Korean/English, this compact prompt is acceptable:

```
어떤 방식으로 콘텐츠를 만들까요? / How should I generate this content?

  [1] 표준 / Standard  (기본)
      제품 정보 + 컨텍스트 리뷰 + 프롬프트 + content context로 작성. 빠릅니다.
      Product info + context-reviews + prompt + content context. Faster.

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

For every product, also build `evidence_facts[]` — short, traceable proof points mined from all visible
product-page substance. This is mandatory, especially when the PDP is image-heavy:

- First mine `full_description`, `short_description`, Plan prose, JSON-LD/meta fields, table text, alt
  text, image captions, OCR/text-extraction fields returned by `aeko_get_product_description`, and any
  product asset text the backend exposes.
- If `full_description` is thin (roughly <300 chars), mostly media markers, or lacks numbers, and
  `outbound_url` is available, `WebFetch` the product page once and extract visible text, image `alt`,
  captions, meta description, JSON-LD, and table/list copy. Do not crawl beyond that product page.
- Prioritize clinical-test results, lab/test names, before/after numbers, percentages, sample size,
  duration, ingredient/material quantities, certifications, care limits, price/availability, dimensions,
  and other numeric evidence. Keep the exact source field or URL with each fact.
- If an image-only PDP exposes no OCR/alt/caption/text, do **not** invent numbers. Record an
  `evidence_gap` note ("image-only PDP; no extractable clinical/numeric proof returned") and draft from
  the remaining product facts.

**Degrade gracefully:**
- `aeko_get_product_context_reviews` missing/empty → continue; product copy still carries substance.
  For evals or when no live reviews exist, read `references/examples/context-reviews-fixture.md` and use
  matching `product_source_id` entries as the review pool. Note in the summary that reviews were a fixture.
- `aeko_get_product_description` 4xx/5xx → fall back to the `parsed_products[]` Plan fields alone; warn once.

**No-product fallback** — when `parsed_products[]` is empty: skip the product/review calls entirely. The
drafters will write from the prompt + content context + their own expertise (honest expertise, never faked
experience — see `references/aeo-frameworks.md` anti-fabrication rule), and Step 8 surfaces a user-language
note that attaching a product (and its context-reviews) yields more original content.

## Step 3b — Light signal / competitive context (mode-aware)

Resolve the prompts: `aeko_resolve_prompts_by_text(prompts_to_rank_on)` → prompt UUIDs. Then
`aeko_get_tracked_prompt(prompt_id, window="latest")` for up to 5 prompts (single parallel batch). If no
prompts resolve, continue (the prompt text itself still gives topic/intent) — do NOT hard-stop.

**Thin signal is expected — never a fork.** Zero citations, prompts still in an AEKO re-query cycle, or an
un-indexed domain (own-content 404) are normal for a new brand. Do not stop, and do not ask the user how to
proceed — state it in one plain line and continue to Step 4. **Name only the sources that actually loaded**
(don't claim "상품 정보" if the product fetch failed): build the list dynamically from {불러온 상품 정보, 리뷰,
프롬프트, content context} that are present this run. Example when product + context loaded: "AI 답변 참고 출처는
아직 적지만, 컨텍스트와 불러온 상품 정보로 작성합니다" / "few cited sources yet — drafting from content context
and loaded product info." If only the prompt + context loaded, say exactly that instead. If
`mode = competitive` but the signal is thin (no cited snippets to distill), silently degrade to Standard with
that one-line note — competitive context adds nothing without citations.

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

## Step 4 — Channel, owned examples & media selection (interactive)

### 4.0 Auto-add aeko.shop + own-store for tenant brands
aeko.shop is AEKO's canonical destination. Prepend `aeko_shop` to the pre-checked set unless
Plan/context explicitly disables it (`aeko_shop_disabled`, `aeko_shop: disabled`, or equivalent).
Missing/malformed flags mean include it. Append `own_store_blog` to the offered set. Both are backend-saved draft targets; this
skill never writes to the connected store.

### 4-Form-1 Channel selection
Issue ONE elicitation form. Pre-check `suggested_channels[]` (from Step 3b) + `aeko_shop` + `own_store_blog`;
offer addon toggles: `press_release`, `magazine`, `instagram`, `tiktok`, `youtube`, `naver_blog`, `tistory`,
`reddit`, `other:<ascii_name>` (free-form `<name>` + optional reference URL/description; reject non-ASCII
`<name>`). Selecting `aeko_shop` is consent to backend-save after drafting. Use the §8.0 localized labels.
**If 0 channels selected → stop** (user-language notice; do not complete the item).

In the same form, ask for optional owned-channel/content examples for users who did not run onboarding:

```
참고할 온드 채널이나 기존 콘텐츠 예시가 있나요? / Any owned channels or existing content examples I should mimic?

- Paste public URLs or raw examples for Naver Blog, Tistory, Instagram, YouTube, own-store blog, aeko.shop,
  product/category pages, or other owned channels.
- These examples guide tone and structure only; they are not factual sources for claims.
- Use your own content and remove PII.
- Save to references/examples for future runs? [no / yes for all / choose per example]
```

Parse the answer into `run_example_refs[]`:

```
{
  channel: "naver_blog" | "instagram" | "own_store_blog" | "aeko_shop" | "global" | "other:<name>",
  source_type: "url" | "pasted_text" | "style_note",
  source_url: "https://..." | null,
  excerpt_or_text: "...",
  style_notes: "...",
  save_to_references: true | false,
  saved_path: "references/examples/<filename>.md" | null
}
```

For each URL, `WebFetch` it once. Public blogs/pages may return usable text; JS-heavy or private social
pages may be thin. If the fetched payload is thin, keep the URL + any user-provided note and warn once; do
not browse further or ask another question. Pasted text takes precedence over scraped text.

When `save_to_references=true`, write the example into this skill's local
`references/examples/` directory before Step 5:

- Filename: `<channel>-<safe-slug>-example.md`; use `in-store-<safe-slug>-example.md` for global owned
  PDP/category/brand-page examples. Collapse non-ASCII to ASCII where possible; if empty, use
  `example-<YYYYMMDD-HHMM>`. If the file exists, append `-2`, `-3`, etc. Do not overwrite.
- File header:
  `<!-- AEKO captured during /aeko-create-content. source: <url|pasted>; channel: <channel>; style-only, not factual source. -->`
- Body: the fetched/pasted example plus any style notes. Strip obvious PII if the user supplied it, and
  warn in the summary that saved examples are read into future model context.
- Record `saved_path`. Saved files are picked up by the matching example-file rules in Step 5; unsaved
  examples are passed directly in `run_example_refs`.

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
`content_context`, `voice_summary` (derived from content context), `target_cohort` (sharpen from context + persona + the prompt),
`must_include`, `forbidden`, `sections_required`, `contrarian_hint`, `competitive_brief` (competitive mode
only), `products` (with `full_description` and `evidence_facts`), `context_reviews`, `media`
(= `media_by_channel[channel]`), `run_example_refs` (matching this channel + `global`, including
`saved_path` when saved), `recipe_path`, `voice_overrides` (scoped block, if
`references/style/voice-overrides.md` has one for this domain/channel).

**Recipe routing by tier.** Owned-web channels (`aeko_shop`, `own_store_blog`) get
`recipe_path: references/recipes/editorial-html-jsonld.md` — that recipe covers both (aeko_shop = body-only,
no in-body JSON-LD; `own_store_blog` = self-contained HTML with *embedded* JSON-LD + responsive markup,
since the brand's store won't regenerate schema). Paste-tier channels with a recipe (`naver_blog`,
`tistory`, `instagram`, `tiktok`, `youtube`, `press_release`, `magazine`) get their thin
`references/recipes/<channel>.md`. Channels with no recipe (`reddit`, `partner_media`, `other:<name>`) get
`recipe_path: null` — the drafter works from frameworks + content-context voice (+ matching example files per
drafter-instructions.md §2 when present).

Collect each drafter's returned self-check into `drafter_results[]`. A drafter that returns no usable
result (skipped/errored) is recorded as a failed channel; continue with the rest.

## Step 6 — Verify (coordinator re-checks publish-blocking gates)

Drafters self-check, but their self-reports cannot be trusted for publish-blocking gates. The coordinator
re-verifies before any save:

- **Universal (every artifact):** no placeholder markers (`[Image`/`[photo`/`[placeholder`/`TODO` in body);
  every image has non-empty alt; `forbidden` strings absent; `must_include` strings present across the
  artifact set (not necessarily every channel); no fabricated external URLs (URLs must be from
  `products[].outbound_url`, Plan/context URLs, or user-supplied media in `media_by_channel{}` — there is no
  crawl allowlist anymore).
- **Framework quality (read each artifact):** BLUF in the opening; PREP-shaped body; ≥1 concrete evidence
  fact when available (clinical/test/data/numeric proof from `evidence_facts`, product copy, or Plan);
  ≥1 originality detail (traceable to a real context-review, or expertise-grounded + flagged when no
  reviews); a specific cohort named; ≥1 honest trade-off/limitation/fit caveat (not a pure benefits list);
  ≥1 contrarian/non-obvious claim; FAQ answers (if any) show E-E-A-T. Weak on a soft dimension →
  ask the drafter (or redraft) once; cap 2 soft iterations per artifact.
- **`aeko_shop` hard gates (re-run against the produced files — these block publish):** `.meta.json` parses
  and carries required `PostUpsert` fields; `slug` present, matches `^[a-z0-9]+(?:-[a-z0-9]+)*$`, and (for a
  non-ASCII title) is NOT equal to the romanized filename slug; `.html` is **sanitizer-safe** (zero
  `<script|article|header|footer|section|h1|meta|title|link|html|body|head>` — aeko.shop-specific); every
  body `<img src>` is an AEKO-media-CDN `public_url` (never a brand-domain URL, never `cdn.aeko.shop`); every
  `<img>` has `alt`/`width`/`height`/`loading`; the set of `data-product-source-id` in `.html` equals
  `featured_products[].product_source_id` in `.meta.json`; no `[image: …pending]` placeholders; structured-data
  completeness (title, `og_description`, publisher/author fallback present, product fields when products
  attached). Thin content context alone must not fail this gate.
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
  the embedded JSON-LD already carries Product schema). Collect `variation_id`s. **On any save failure:** do NOT complete; leave `pending`; print user-language retry
  guidance; stop (skip Steps 8–9). **On all saves succeed:** `aeko_complete_action_item(... write_result=
  {"backend_variations": saved_variations})`.

## Step 8 — User-facing summary

### 8.0 Channel labels (localized — never a bare slug)
`aeko_shop`=aeko.shop용 HTML / aeko.shop HTML · `naver_blog`=네이버 블로그용 초안 / Naver Blog draft ·
`tistory`=티스토리용 초안 / Tistory draft · `instagram`=Instagram용 캡션 / Instagram caption ·
`tiktok`=TikTok용 스크립트 / TikTok script · `youtube`=YouTube용 스크립트 / YouTube script ·
`magazine`=매거진 기고용 / Magazine pitch · `press_release`=보도자료 초안 / Press release draft ·
`partner_media`=파트너 미디어용 / Partner media draft · `reddit`=Reddit 포스트 초안 / Reddit post ·
`own_store_blog`=자사몰 블로그 초안 / Own-store blog draft · `other:<name>`=`<name> 초안` / `<name> draft`.
Lead with the label matching the user's chat language. For languages beyond Korean/English, translate the
human-readable label from the English label while keeping the slug unchanged. If the Plan's `target_language`
differs, note the artifact language separately in the summary.

### 8.1 Summary block
Print a marketer-facing block first, then technical details:

```
✔ Content drafts ready

What AEKO created
- <localized channel labels> for <brand/domain>

Source material used
- Product facts: N
- Evidence facts: N (clinical/data/numeric proof points; "none extractable" if the PDP was image-only)
- Real review/context details: N (or "none — attach product reviews for more original content")
- Content context: <loaded|thin — used neutral fallback>
- Owned examples: <none|used this run: N|saved to references/examples: N>

Safety
- This skill did not publish anything live.
- Connected store content was not changed.

Revision path
- Edit local drafts or saved backend variations, then publish only when ready.

Recommended next step
- <one command: /aeko-publish-content <item_id> when saved variations exist, otherwise /aeko-action-center <domain_id> content>
```

After that, include artifacts (one user-language line + path per file), media refs (N with alt / M skipped),
owned examples saved/used (with paths when saved), `Refs loaded` (recipe + example paths per channel, so
users can verify customization was picked up),
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
- Content context thin/missing → continue with neutral evidence-first voice; do not block save or publish handoff.
- No prompts resolve in Step 3b → continue on prompt text + product/review substance (do NOT hard-stop;
  this is no longer forensics-gated).
- `aeko_get_product_context_reviews` / `aeko_get_product_description` unavailable → degrade per Step 3.
- A drafter subagent errors/skips → record the channel as failed, continue with the rest.
- Citability hard-gate fails after the fix iteration → leave item `pending`; surface failed channels + dimensions.
- aeko.shop media upload fails → drafter omits that image, produces a valid text-only post, warns loudly; never a placeholder.
- Backend save fails → do NOT complete; item stays `pending`; user-language retry guidance; skip Steps 8–9.
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
- Never saves owned-channel/content examples into `references/examples/` without explicit user consent.
  Saved examples are style/structure references only, not factual evidence for generated claims.
- Never emits `[Image]`/`[photo]`/`[placeholder]`/`TODO` body markers; never invents URLs; never echoes raw
  frontmatter; never regenerates the Plan.md; never proceeds past Form-2 without an explicit submit.
