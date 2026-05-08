---
name: aeko-create-content
description: >
  Multi-channel content executor for Action-tab items with
  `execution_class=local_content_artifact`. Fetches a Plan.md, runs
  tracked-prompt citation forensics to identify the source structures
  AI engines actually cite (Reddit threads, Naver blogs, partner media,
  etc.), then fans out into per-channel drafts: auto-detected channels
  from forensics PLUS user-added formats (보도자료 / magazine /
  Instagram / TikTok / YouTube / free-form). Optional image/video
  reference per channel. Saves locally; never writes to a store and
  never auto-publishes. Splits the content branch out of the retired
  `/aeko-run-action`.
argument-hint: "<item-id>"
allowed-tools: aeko_get_action_plan, aeko_get_brand_kit, aeko_get_tracked_prompts, aeko_get_tracked_prompt, aeko_crawl_url, aeko_list_own_content, aeko_complete_action_item, Read, Write, WebFetch, WebSearch
---

# AEKO Create Content

Executes one Action-tab content item end-to-end: fetch Plan.md → pull citation-forensics on tracked prompts → identify winning source structures + auto-detect channels → confirm channels with user + collect optional add-on formats and per-channel media → draft N channel-fitted artifacts in the brand voice → save local artifacts → mark complete.

Contract reference: `docs/contracts/action-item-contract.md` §3 (Plan.md), §6 (completion). Pinned to contract minor `v1.3` (skill-internal; no backend contract change in v2 — multi-channel fanout is driven by forensics + interactive prompts).

## Input

- `item-id` (required) — `$1`. If missing, stop and point user to `/aeko-action-center <domain_id> content`.

## Step 1 — Fetch and parse the Plan.md

Call `aeko_get_action_plan(item_id)`. Parse YAML frontmatter + prose.

**Validate:**
- `contract_version` starts with `2026-04-17.action.v1.` — else stop.
- Pin this skill to contract minor `v1.3`. Greater minor → print advisory + proceed.
- `tab == "action"` — else stop.
- `execution_class == "local_content_artifact"` — else redirect to the right executor.
- `artifact_type ∈ {own_store_markdown, external_media_markdown, own_store_content, external_media_content}` (accept both v1 and v2 names for forward-compat). In v2 this is **advisory** — actual channel set is decided in Step 4 — but it must be present.
- `status ∈ {pending, ready}` — else stop.
- `write_target == "local"` — content artifacts never write to store; mismatch → stop.
- `tier_required` gate via brand kit metadata.

Print header in `target_language`:
1. Action label — KO (own): "자사 콘텐츠 생성: `<artifact_type>`" / KO (external): "외부 매체 콘텐츠 생성: `<artifact_type>`" / EN: "Generating {own-site|external-media} content: `<artifact_type>`"
2. Context: domain, channels suggested by Plan (comma-joined).
3. Persona: `persona_label` if present.
4. Note: "Final channel set decided after forensics in Step 4."

Print prose verbatim. Never echo frontmatter.

## Step 2 — Stale brand-kit check

If `frontmatter.requires_brand_kit == true`:
- `aeko_get_brand_kit(frontmatter.domain_id)`. Missing / empty → stop with Brand-Kit-missing message.
- Verify voice minimum: `tone_of_voice` present + at least one of `{brand_voice_summary, target_audience}`. Thin kit → warn + offer to abort (`/aeko-brand-kit <domain_id> edit`).
- Snapshot-version drift: ask user.

## Step 3 — Citation forensics on tracked prompts

This is what makes AEKO-grounded content beat vanilla Claude. Build a structural model of what AI engines currently cite for this topic, then mimic — across one OR many channels.

### 3.0 Resolve `prompts_to_rank_on` to UUIDs

`frontmatter.prompts_to_rank_on` may carry either UUIDs (preferred — newer Plan-builders write these directly) or raw prompt text (older Plan-builders + manually authored Plans). `aeko_get_tracked_prompt` only accepts UUIDs, so resolve text → UUID before §3.1.

For each entry:

1. **UUID detection.** If the entry matches `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$` (case-insensitive), it's already a UUID — pass through.
2. **Text → UUID resolution.** If any entry is non-UUID text, call `aeko_get_tracked_prompts()` *once* (cache the result for the rest of this step). The response includes an `ID` column for every tracked prompt. Build a normalized lookup map: lowercase + strip punctuation + collapse whitespace, applied to both `prompt_en` and `prompt_ko`. Match each text entry against the map. Carry `(text → uuid, matched_via)` for §4a transparency.
3. **Unresolved entries.** Collect any text entries that didn't match. Surface them in §4a as "unresolved prompts" (don't silently drop) — the user needs to know which prompts were skipped.

**Hard precondition.** If zero entries resolve to UUIDs, stop here:

```
Forensics requires tracked prompts. None of `prompts_to_rank_on` resolved to a tracked UUID.

Either:
  • track these prompts first: /aeko-find-prompts-to-track <domain_id>
  • or rewrite the Plan with UUIDs from `aeko_get_tracked_prompts`.

Re-run /aeko-create-content <item_id> after.
```

Do not proceed to §3.1 with zero resolved UUIDs and do not fall back to research-prompt search — see §3.7.

Cap `prompts_to_rank_on` to the top 5 resolved UUIDs (by Plan ordering) before §3.1.

### 3.1 Pull the snapshot

For each resolved UUID from §3.0:

- Call `aeko_get_tracked_prompt(prompt_id, window="30d")` for the forensics payload.
- Across the responses, harvest **per response**: the full response body (the `Response body` block — falls back to a 300-char `Snippet` line if the backend hasn't shipped full bodies yet) so you can see how cited sources get woven into AI answers, not just the citation snippet.
- Per citation, harvest: `domain`, `source_url`, `source_type`, `position_in_response`, `context_snippet`, the `JSON-LD: …@types` line, the `Citability: …` score, and the `Extracted: …` body slice.

### 3.2 Rank cited sources

Rank the aggregated sources by **citation frequency × inverse average position × citability score** (when the score is present). Surface the top 5-10 source domains and their canonical URLs.

### 3.3 Auto-detect channels

For each top source, classify the domain into a channel slug:

- `reddit.com/*` → `reddit`
- `*.blog.naver.com` / `m.blog.naver.com` → `naver_blog`
- `*.tistory.com` → `tistory`
- `wikipedia.org` → `wikipedia`
- news / partner-media domains (heuristic: `news.*`, `*.co.kr/news/*`, established publication TLDs) → `partner_media`
- else → `web_article` (generic)

Deduplicate. Carry `auto_detected_channels[]` into Step 4.

### 3.4 Live re-crawl the top sources per channel

The tracked-prompt snapshot can be days or weeks old by the time this skill runs, and it does not include the page's current title / meta description / OG fields / current paragraph stats. For each channel in `auto_detected_channels`, pick the top 3 cited URLs and call `aeko_crawl_url(url, force_refresh=true)` on each — the whole point of this substep is to beat snapshot staleness, so accept the latency cost of bypassing the 24h cache. Build the per-channel `cited_url_allowlist[]` from these URLs as you go (Step 6.1 references it).

Merge the crawl payload into a per-channel structural template:

- **Numeric targets** (override snapshot when fresher): `paragraphs.avg_word_count`, `paragraphs.median_word_count`, heading count + max depth, `lists.ul_count`/`ol_count`/`total_items`, `images.count`, `images.with_alt`.
- **Schema signal**: collect `json_ld[]` raw blocks across the top sources; aggregate `@type`s. Drives the editorial-channel HTML JSON-LD recipe in Step 5 (e.g., if cited articles are `NewsArticle`, the partner_media draft's JSON-LD mirrors that, not a generic `Article`).
- **Title / meta seeds**: use `title` and `meta_description` to seed the draft's own title and meta when the channel has metadata slots.
- **Visual seeds**: `og.image` and `images.alt_examples` feed back into the Step 5.4 `media_specs:` block when the user skipped media — gives the designer/imagegen tool a real reference.
- **Tone signal**: combined with `crawl.extracted_text` from §3.1, the live crawl's title + meta + first heading establish the cited source's diction; carry into Step 5.3.

Cap: 3 crawls per channel × N channels. On crawl failure (4xx/5xx, connect error), log a single warning line and keep going on the snapshot signal alone — recrawl is enriching, not gating.

### 3.5 Build the per-channel structural template

For each `auto_detected_channels` entry, finalize `structural_template_by_channel[channel]` by combining:

1. Snapshot signals from §3.1 (citability score, JSON-LD `@type`s, extracted-text tone).
2. Live crawl signals from §3.4 (numeric targets, raw JSON-LD blocks, OG fields).
3. JSON-LD `@type` lock — when an `@type` dominates the channel's top sources, lock the recipe to it:
   - `QAPage` / `DiscussionForumPosting` → reddit recipe locked to Q&A
   - `Article` / `NewsArticle` → tistory / partner_media calibrated to measured paragraph + heading stats
   - `Recipe` / `HowTo` → step-list scaffold
   - `Review` → comparison / scoring scaffold

**You are not copying text** — you are matching format: if Reddit threads win, the draft reads like a Q&A with lived-experience tone; if Naver 블로그 wins, it reads like a first-person informal review with in-line images; if partner-media wins, it reads like a comparison article with product callouts. Carry `structural_template_by_channel{}` into Step 5.

**Initialize `cited_url_allowlist[]`** with every `source_url` harvested in §3.1 plus every URL recrawled in §3.4. Steps 3.6 and 4d will append to it; Step 6.1 reads it as the source of truth for "no invented URLs."

### 3.6 In-store content signature

In parallel with the cited-source forensics, sample the brand's *own* on-site content so the draft can mimic in-house tone and dedupe against existing pages:

- Call `aeko_list_own_content(domain_id, type="blog", limit=10)` and `aeko_list_own_content(domain_id, type="pdp", limit=5)`.
- For up to 3 blog posts, run `aeko_crawl_url(url)` (cached default — in-store pages don't change as fast and a 24h cache is fine here) to capture: title length, paragraph length, heading style, list density. Build `in_store_tone_signature{}` carried into Step 5.3. Append these URLs to `cited_url_allowlist[]` so the brand's own pages count as authorized links per Step 6.1.
- Build `in_store_topic_index[]` — the (title, url) pairs returned. Used in Step 4d to flag duplication: if the working draft title is ≥80% token-overlap with an existing page, surface the conflict at Step 4e and offer a pivot.
- New domain with no in-store content → both calls return empty; skip silently and note "no in-store signature — drafting from cited-source signal only" in Step 4a confidence output. This is non-fatal.

### 3.7 No-tracked-prompts handling

§3.0 already hard-stops when zero entries resolve to UUIDs. The skill does **not** fall back to `aeko_search_research_prompts` — research prompts are unrelated to the user's tracked-prompt set, so their forensics carry the wrong structural signal (different cited sources, different `@type`s, different audience). Substituting them produces drafts that look forensics-grounded but optimize for the wrong queries.

If §3.0 succeeded but every `aeko_get_tracked_prompt` call in §3.1 returns empty `responses[]` (tracked but never re-queried), surface this in §4a confidence as "tracked prompts exist but no response history yet — re-run after the next response cycle, or proceed with brand-kit-only drafting." The user decides at §4e whether to abort.

## Step 4 — Channel & media selection (interactive)

This step is the v2 fanout. Always run; respect `skip` / `none` for empty selections.

### 4a. Print forensics summary

Print the enriched forensics table so the user can tell at a glance whether forensics is grounded. Use the snapshot fields from §3.1 + the live recrawl signal from §3.4.

**Confidence band:**
- `high` — ≥3 prompts × ≥3 distinct cited domains × **≥50% of attempted live crawls succeeded** (the recrawl rate is the freshness gate; one 200 isn't enough).
- `medium` — ≥1 prompt × ≥2 cited domains, regardless of crawl success.
- `low` — anything weaker (e.g. only 1 prompt resolved, or all prompts have empty response history).

```
Prompt resolution (§3.0):
  resolved:    3/4 prompts (1 by UUID, 2 matched by text)
  unresolved:  "아토피 알레르기 이불 추천" — not in tracked set; track it via /aeko-find-prompts-to-track

Top cited source domains (top 5):
  1. reddit.com/r/sleeptips    · cited 5× · pos 2.1 · citability 0.81 · @types: [QAPage]      · "여름철 침구 추천..."
  2. blog.naver.com/<author>   · cited 3× · pos 3.4 · citability 0.74 · @types: []            · "1인칭 후기..."
  3. <partner-media>.com       · cited 2× · pos 4.0 · citability 0.69 · @types: [NewsArticle] · "비교 리뷰..."

Structural targets (median across top sources per channel):
  reddit:        ~340 words · 0 headings · Q&A pairs ~3
  naver_blog:    ~1500자 · 5 images · 2 H2 sections
  partner_media: ~1800 words · 4 H2 · 2 product callouts

Auto-detected channels:  reddit, naver_blog, partner_media
In-store signature:      derived from 3 existing posts (or "no in-store signature — new domain")
Live re-crawl:           7/9 succeeded · 2 failed (continuing on snapshot)
Forensics confidence:    high (5 prompts × 12 cited sources, 4 distinct domains, JSON-LD on 8/12)
```

If `Forensics confidence: low`, warn before Step 4b: "the structural template will be thin — consider tracking more prompts first via `/aeko-find-prompts-to-track` for higher-quality output." User may still proceed.

If §3.6 surfaced a likely duplicate (≥80% title token-overlap with an in-store page), append a single-line warning above the question in 4b: "⚠ This draft topic looks ≥80% similar to <existing-url> — consider pivoting the angle or canonicalizing in Step 4e."

### 4b. Confirm auto-detected channels

Ask: "Generate drafts for all auto-detected channels above? Reply with the channels to keep, or `all`, or `none`."

Parse user reply into `selected_detected_channels[]` (subset of `auto_detected_channels`).

### 4c. Add additional formats

Ask: "Add any of these formats?
- `보도자료` (Korean press release, 합니다체)
- `magazine` (Vogue-style editorial)
- `instagram` (caption + hashtags + alt text)
- `tiktok` (30–60s script with beats)
- `youtube` (title, description, chapters)
- `other:<name>` (free-form — describe the format briefly, or paste 1-2 reference URLs)

Reply with comma list, or `none`."

Parse into `selected_addon_channels[]`. For each `other:<name>`, ask one follow-up: "Reference URL(s) or short description for `<name>` format?"

### 4d. Per-channel media

For each channel in `selected_detected_channels + selected_addon_channels`, ask once:
"Image/video for `<channel>`? Reply with URL, local path, or `skip`."

Validate:
- URL → light `WebFetch` probe; warn if 4xx/5xx but allow continue.
- Local path → `Read` to confirm exists; warn + allow if missing.
- `skip` → record null.

Record into `media_by_channel{}`. For every URL captured here (and every URL pasted into `other:<name>` references in §4c), append to `cited_url_allowlist[]` so Step 6.1's "no invented URLs" gate accepts the user-supplied media link.

### 4e. Confirm before generating

Print a selection table:

```
| Channel       | Source template       | Media          |
| reddit        | forensics: r/<sub>    | skip           |
| naver_blog    | forensics: 1인칭 review | https://...   |
| 보도자료       | recipe: press_release | skip           |
| instagram     | recipe: instagram     | /Users/.../a.jpg |
```

Ask: "Proceed to draft? (`yes` / `cancel` / `edit`)". On `edit`, loop back to 4b. On `cancel`, stop without writing or completing.

If the **total selected channels is 0**, stop with "no channels selected" and do NOT call `aeko_complete_action_item`.

## Step 5 — Per-channel draft loop

Loop over the final selected channel list. For each channel:

### 5.0 Load references (per-channel, on-demand)

Reference content lives under `skills/aeko-create-content/references/` and is loaded **only when needed** per channel — Anthropic's progressive-disclosure model. SKILL.md stays small; recipes and brand-specific exemplars load when their channel runs.

For each channel `C` in the selection, before drafting:

1. **Load the recipe** (always, for built-in addon channels): `Read references/recipes/<C>.md`. Channel-to-file map:
    - `보도자료` → `references/recipes/보도자료.md` (also load `references/recipes/editorial-html-jsonld.md`)
    - `magazine` → `references/recipes/magazine.md` (also load `references/recipes/editorial-html-jsonld.md`)
    - `partner_media` → forensics-derived; load `references/recipes/editorial-html-jsonld.md` for the HTML/JSON-LD pair
    - `instagram` → `references/recipes/instagram.md`
    - `tiktok` → `references/recipes/tiktok.md`
    - `youtube` → `references/recipes/youtube.md`
    - Auto-detected forensics channels (`reddit`, `naver_blog`, `tistory`) — no recipe file; structural template comes from Step 3.5.
    - `other:<name>` — no recipe file; structural template comes from §5.1's mini-forensics.

2. **Load the brand-specific exemplar** (if it exists, conditional). Filename pattern: `references/examples/<C>-*example*.md` or the explicit names in the table below. Use a `Read` with `Glob`/check-exists semantics — silently skip if absent. Treat each match as style guidance:

    | channel | example file the skill scans for |
    | --- | --- |
    | `naver_blog`, `tistory` | `references/examples/blog-example.md` |
    | `instagram` | `references/examples/instagram-post-example.md` |
    | `보도자료` | `references/examples/press-release-example.md` |
    | `tiktok` | `references/examples/tiktok-script-example.md` (optional) |
    | `youtube` | `references/examples/youtube-description-example.md` (optional) |
    | `magazine` | `references/examples/magazine-feature-example.md` (optional) |
    | (any) | `references/examples/in-store-content-example.md` — voice signal across all channels |

3. **Load voice overrides** (if it exists): `Read references/style/voice-overrides.md`. Filter to blocks scoped to `domain: <frontmatter.domain_id>` and/or `channel: <C>`. Skip silently if the file doesn't exist or no scoped block matches.

**Example-file rules** (mirror §6.1 hard-gate intent):

- Example files are loaded as **style reference**, not as cited content. Any URL inside an example file MUST NOT be carried into the artifact — the §6.1 "no invented URLs" gate still applies, scoped to `cited_url_allowlist[]`.
- Example files may legitimately contain `[Image]` placeholders as part of demonstrating a brand's pattern. The §6.1 placeholder gate scans the *generated artifact*, not the example file.
- Mimic structure (paragraph length, hook style, hashtag density, heading cadence) and tone (sensory verbs, register, glossary). Do not copy phrases verbatim — even your brand's own exemplar.

The user-facing summary at Step 8 must list which reference files were loaded per channel so the user can verify their exemplars are picked up (e.g., `Mimicked: examples/instagram-post-example.md + recipes/instagram.md`).

### 5.1 Pick the structural source

- **Auto-detected channel**: use `structural_template_by_channel[channel]` from Step 3 (snapshot + live crawl already merged in §3.4 / §3.5).
- **Built-in addon** (`보도자료`, `magazine`, `instagram`, `tiktok`, `youtube`): use the recipe loaded in §5.0 from `references/recipes/<channel>.md` (and `references/recipes/editorial-html-jsonld.md` for editorial channels' HTML pair).
- **`other:<name>`**: if reference URLs were provided, fetch them via `aeko_crawl_url(url)` and derive an ad-hoc template (mini-forensics: title, meta, paragraph length, heading depth, list usage, JSON-LD `@type`s). Fall back to `WebFetch` if the crawl tool returns 4xx/5xx — for `other:<name>` channels, JSON-LD signal is nice-to-have, not required. If only a description was given, use the description plus brand-voice defaults.

### 5.2 Optional research

If frontmatter prose requests external research OR an `other:<name>` channel needs reference fetching:
- `WebSearch` for related context (competitor brand names, recent news, review themes).
- `WebFetch` on specific URLs called out in prose or supplied by user. Do NOT invent URLs.
- Append a research-log to the channel's artifact directory.

### 5.3 Draft the artifact

**Output format per channel** (overridden by `frontmatter.output_artifact_format` when present):

| channel | default format(s) |
| `reddit`, `naver_blog`, `tistory`, `instagram`, `tiktok`, `youtube` | `markdown` |
| `보도자료`, `magazine`, `partner_media` | `markdown` + `html` (both files written; HTML carries embedded JSON-LD per `references/recipes/editorial-html-jsonld.md`) |

Enforce:
- `frontmatter.must_include` — every string MUST appear in **at least one** generated artifact (not necessarily every channel — a brand name belongs in 보도자료 boilerplate but may not fit a TikTok beat).
- `frontmatter.forbidden` — no string MAY appear in any artifact.
- `frontmatter.sections_required` — applies to prose channels (forensics-detected, `보도자료`, `magazine`). Each entry MUST map to a heading or named section. Social channels (`instagram`, `tiktok`, `youtube`) use the recipe's required parts in place of `sections_required`.

**Voice discipline** (priority order, highest first):

1. **Voice overrides** (`references/style/voice-overrides.md`, if present) — domain- or channel-scoped exception sheet. Wins over everything below for the scopes it names.
2. **Brand-specific exemplar** (`references/examples/<channel>-*example*.md`, if present, loaded in §5.0) — drives structural mimicry (paragraph length, hook style, hashtag density, heading cadence) and channel-specific glossary. Recipe acceptance gates still apply on top.
3. **Brand kit** `tone_of_voice` drives sentence-level register; brand kit `must_include` and `forbidden` override frontmatter if conflicting (surface the conflict to the user before resolving).
4. **Cited-source structural template** (Step 3.5) drives format when no exemplar is present: paragraph length, heading depth, list density, list-vs-prose split, Q&A patterning when locked.
5. **In-store tone signature** (Step 3.6) — fills gaps when the brand kit's `tone_of_voice` is thin or absent. When brand kit and in-store conflict, brand kit wins; surface the conflict once at Step 4e.

Plus the always-on rules:
- Target audience from brand kit shapes word choice (beginner vs expert vocabulary).
- For `보도자료` specifically: 합니다체 is required even if brand voice elsewhere is 요체 — the format wins; surface the conflict before resolving.
- **No hard CTAs** ("Buy now" / "Click here" / promotional commands) in the body. Citability content earns the click via authority, not commands. Same principle as `/aeko-update-pdp`: AEKO injects citability content; the host channel owns the action UI.

**Structural discipline** (from Step 3 template or `references/recipes/<channel>.md`):
- Match the winning-source format the forensics identified.
- Be honest about what this is: Reddit-style Q&A is fine, but do NOT fake Reddit thread formatting or pretend the content is crowd-sourced.
- Link out to the top cited sources where the draft genuinely benefits from them (prevents the "generic AEO mush" failure mode).

### 5.4 Embed media reference

**Hard rule:** never emit `[Image #N]`, `[image placeholder]`, `[Image]`, `[photo]`, `[Video:` (without a real URL inside), `[Photo:`, `[graphic]`, or any unfilled `[…]` media marker in body text. Markdown image syntax (`![alt](url-or-path)`) is only permitted with a real URL or local path. If you find yourself wanting to write a placeholder, stop and use the `media_specs:` block below instead. The §6.1 hard gate scans for any `[Image`/`[image`/`[Video`/`[video`/`[Photo`/`[photo`/`[Graphic`/`[graphic`/`[placeholder` token followed by a non-URL — fail the artifact if any match.

**If `media_by_channel[channel]` is set** (real URL or local path supplied):

- Markdown channels → standard image / video markdown:
  - Image: `![<alt>](<url-or-path>)`
  - Video: `[Video](<url-or-path>)` link with caption on the next line. Bracket form `[Video: <url>]` (with a colon and inlined URL) is **not** allowed because the §6.1 scanner would flag it; use the link form so the URL parses cleanly.
- Instagram → `media:` field at the top of the file referencing the asset; alt text rendered in its own section.
- TikTok → reference inside the relevant beat (`[on-screen]: image at <path>`).
- YouTube → reference in description (`Thumbnail: <url-or-path>`).

The skill **does not copy or upload** the media — references only.

**If `media_by_channel[channel]` is null** (user replied `skip` in Step 4d):

- **Visual-first channels** (`instagram`, `tiktok`, `youtube`, `magazine`, `naver_blog`, `tistory`, `partner_media`): write a fenced `yaml` code block at the top of the file (immediately after the `# <title>` heading) containing the `media_specs:` array — one entry per slot the recipe expects (typically `hero` + 0-3 `inline` slots; YouTube also `thumbnail`; TikTok one entry per major beat). Fenced so downstream consumers (designer tools, image-gen pipelines) can reliably extract it; an unfenced `- ` prefixed list breaks markdown rendering AND parsing.

  Emit it exactly like this — opening and closing fences included:

  ````markdown
  ```yaml
  media_specs:
    - slot: hero
      composition: "<one-line composition direction>"
      subject: "<who/what is in the shot>"
      copy_overlay: "<on-image text, or 'none'>"
      alt_text: "<≤125 char alt text>"
      aspect_ratio: "<e.g., 1:1, 9:16, 16:9>"
      reference_image: "<og.image URL from §3.4 if available, else 'none'>"
  ```
  ````

  Body references slots by name (`see media_specs.hero`) — never by `[Image #N]` or any other bracket marker. Seed the `reference_image` field from §3.4's `og.image` and `images.alt_examples` when they exist for a top cited source on this channel; otherwise emit `'none'`.
- **Prose-only channels** (`reddit`, `보도자료`): no image references in body at all. Do not emit a `media_specs:` block — these channels are text-first and inserting visual specs creates noise. (`보도자료` may include media as a separate distribution attachment list at the bottom under `## 보도자료 첨부 참고`, but only if frontmatter prose explicitly requests it.)

### 5.5 Artifact path

**Always use channel-segmented paths.** Do not flatten artifacts into one folder — recent runs produced flat outputs because the slug rule was under-specified; fix is below.

Path template:

`./aeko-artifacts/<domain_id>/<item_id>/<channel_slug>/<filename>.<ext>`

**Slug derivation** (for prose channels and editorial HTML):

1. Source: `frontmatter.title` (not Plan prose, not response text).
2. Lowercase, ASCII-fold non-ASCII characters (Hangul → romanization via standard fold; if no fold available, drop the character).
3. Replace any run of non-alphanumeric characters with a single hyphen.
4. Truncate to **60 characters at the nearest word boundary** (don't truncate mid-word).
5. Strip leading and trailing hyphens.
6. On filename collision within the same channel directory, append `-2`, `-3`, … until unique.
7. **Empty-slug fallback.** If steps 1–5 produce an empty string (most common cause: 100% Hangul title with no romanization fold available), use `<frontmatter.item_id>` as the slug. Never write to a hidden filename like `.md`. Example: title `여름철 침구 가이드` with no fold → `<slug>` becomes `<item_id>` (a UUID), so the file lands at `.../naver_blog/3f2c1a04-….md` rather than `.../naver_blog/.md`.

**Filename rules per channel:**

| channel | filename pattern | extension(s) |
| `reddit`, `naver_blog`, `tistory`, `partner_media` | `<slug>` | `.md` |
| `보도자료`, `magazine` | `<slug>` | `.md` AND `.html` (see `references/recipes/editorial-html-jsonld.md`) |
| `instagram`, `tiktok`, `youtube` | the channel slug (literal `instagram` / `tiktok` / `youtube`) | `.md` |

**Worked-example directory tree** the skill MUST produce when 9 channels are selected for a draft titled "Summer Cooling Bedding — 2026 Guide":

```
aeko-artifacts/
  <domain_id>/
    <item_id>/
      reddit/summer-cooling-bedding-2026-guide.md
      naver_blog/summer-cooling-bedding-2026-guide.md
      tistory/summer-cooling-bedding-2026-guide.md
      partner_media/summer-cooling-bedding-2026-guide.md
      보도자료/summer-cooling-bedding-2026-guide.md
      보도자료/summer-cooling-bedding-2026-guide.html
      magazine/summer-cooling-bedding-2026-guide.md
      magazine/summer-cooling-bedding-2026-guide.html
      instagram/instagram.md
      tiktok/tiktok.md
      youtube/youtube.md
```

If frontmatter prose requests sibling files (JSON-LD, meta, social teaser), write them next to the channel's main file using the same `<slug>` stem (e.g., `<slug>.jsonld.json`, `<slug>.meta.json`).

### 5.6 Channel recipes (loaded from `references/recipes/`)

Built-in addon channels each have a recipe file under `references/recipes/`. They were loaded in §5.0; apply them now. Acceptance bullets in each recipe file ARE the §6.4 social-channel gates and the §6.2 prose-channel structural-target source.

| channel | recipe file | output |
| --- | --- | --- |
| `보도자료` | `references/recipes/보도자료.md` + `references/recipes/editorial-html-jsonld.md` | `.md` + `.html` |
| `magazine` | `references/recipes/magazine.md` + `references/recipes/editorial-html-jsonld.md` | `.md` + `.html` |
| `partner_media` | forensics template (Step 3.5) + `references/recipes/editorial-html-jsonld.md` | `.md` + `.html` |
| `instagram` | `references/recipes/instagram.md` | `.md` |
| `tiktok` | `references/recipes/tiktok.md` | `.md` |
| `youtube` | `references/recipes/youtube.md` | `.md` |

If a brand-specific exemplar was loaded in §5.0, mimic its structure on top of the recipe — recipe gates still apply. See §5.3 voice-discipline precedence for conflict resolution.

### 5.6.6 HTML + JSON-LD recipe (editorial channels)

Editorial channels (`보도자료`, `magazine`, `partner_media`) write a `.html` companion alongside the `.md`, with embedded JSON-LD. The full HTML wrapper, per-channel JSON-LD schema (`NewsArticle` / `Article` / `Article + Review`), validity rules, schema-parity rules, and emission notes live in `references/recipes/editorial-html-jsonld.md` — load it before drafting any editorial channel.

Applies to `보도자료`, `magazine`, and `partner_media`. These channels write **two** artifacts: the existing `<slug>.md` (canonical, human/editor-facing) AND a new `<slug>.html` (publish-ready, structured-data-bearing) at the same channel-segmented path. The `.md` remains the source of truth; the `.html` is generated from it.

**HTML structure** — minimal semantic wrapper, no styling, no scripts beyond the JSON-LD block:

```html
<!doctype html>
<html lang="<frontmatter.target_language>">
<head>
  <meta charset="utf-8">
  <title><headline></title>
  <meta name="description" content="<lead-sentence-or-meta>">
  <link rel="canonical" href="<frontmatter.canonical_url-if-present>">
</head>
<body>
  <article>
    <header>
      <h1><headline></h1>
      <p class="lead"><lead></p>
      <p class="byline">
        <author> · <ISO datePublished>
      </p>
    </header>
    <section>
      <!-- markdown body rendered to HTML; preserve heading hierarchy -->
    </section>
    <!-- if media_specs: was used in lieu of real media, mirror it as an HTML comment block above <footer> -->
    <footer>
      <p class="boilerplate"><brand boilerplate from brand kit></p>
      <p class="contact"><문의처 line for 보도자료, otherwise omit></p>
    </footer>
    <script type="application/ld+json">
      <!-- channel-specific JSON-LD: see schemas below -->
    </script>
  </article>
</body>
</html>
```

If a real media URL exists (`media_by_channel[channel]` set), inject `<figure><img src=... alt=...></figure>` blocks at the natural insertion points (after the lead for hero, between sections for inline). Skip when only `media_specs:` was emitted — HTML preserves the YAML block as a leading comment so the publishing editor sees the spec without it polluting the rendered article.

**JSON-LD schema per channel:**

- **`보도자료` → `NewsArticle`**:
  ```json
  {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    "headline": "<headline (≤110 chars per Schema.org guidance)>",
    "datePublished": "<ISO 8601 date the press release is dated for>",
    "dateModified": "<same as datePublished unless re-issued>",
    "author": { "@type": "Person|Organization", "name": "<from brand kit or 'Press' if absent>" },
    "publisher": {
      "@type": "Organization",
      "name": "<brand_kit.brand_name>",
      "logo": { "@type": "ImageObject", "url": "<brand_kit.logo_url if present>" }
    },
    "articleBody": "<body text, with HTML stripped>",
    "inLanguage": "<frontmatter.target_language>"
  }
  ```

- **`magazine` → `Article`**:
  ```json
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "<headline>",
    "datePublished": "<ISO date>",
    "author": { "@type": "Person|Organization", "name": "<from brand kit, or 'Editorial' if not specified>" },
    "publisher": { "@type": "Organization", "name": "<brand_kit.brand_name>" },
    "articleBody": "<body text>",
    "inLanguage": "<frontmatter.target_language>",
    "mentions": [
      { "@type": "Brand", "name": "<parent or related brand if brand kit names one>" }
    ]
  }
  ```
  Omit the `mentions` array entirely if the brand kit doesn't surface a relationship — don't fabricate.

- **`partner_media` → `Article`** (always) **+ `Review`** (when forensics-detected the draft is comparison-shaped, i.e., §3.5 locked the recipe to `Review` or detected `Review` as a top `@type`):
  ```json
  [
    {
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "<headline>",
      "datePublished": "<ISO date>",
      "author": { "@type": "Person|Organization", "name": "<...>" },
      "publisher": { "@type": "Organization", "name": "<brand_kit.brand_name>" },
      "articleBody": "<body text>",
      "inLanguage": "<frontmatter.target_language>"
    },
    {
      "@context": "https://schema.org",
      "@type": "Review",
      "itemReviewed": {
        "@type": "Product",
        "name": "<the comparison subject named in the draft body — derive from the H1 / lead paragraph; do NOT invent>"
      },
      "reviewRating": {
        "@type": "Rating",
        "ratingValue": "<numeric score the body actually substantiates, or omit>",
        "bestRating": "5"
      },
      "author": { "@type": "Person|Organization", "name": "<...>" },
      "reviewBody": "<the comparison summary paragraph>"
    }
  ]
  ```
  When emitting two blocks, use a JSON-LD array (top-level `[...]`) — schema.org and Google Rich Results both accept this.

**JSON-LD validity rules** (mirror `aeko-update-pdp` and `aeko-refresh-jsonld`):

- Valid JSON: parses with `json.loads(block)`.
- No trailing commas.
- No comments (`//` or `/* */`) inside the block.
- The opening tag is exactly `<script type="application/ld+json">` — no additional attributes, no whitespace differences in `type=`.
- `@context` is `https://schema.org` (not `http://`, not omitted).
- For numeric fields like `ratingValue`, do not include them unless the body actually justifies a number.
- **`inLanguage` must be a valid ISO-639-1 / BCP 47 code** (e.g. `"ko"`, `"en"`, `"en-US"`) — the contract pins `frontmatter.target_language` to ISO-639-1 (action-item-contract.md §3.1), but defensively normalize: if the field is `"Korean"`/`"한국어"` map to `"ko"`; `"English"`/`"영어"` map to `"en"`; if the value is unrecognized, fall back to `"ko"` (AEKO's primary market) and surface a one-line warning above the artifact summary.

**HTML emission notes:**

- The `media_specs:` YAML block (§5.4), when present, is mirrored into the HTML as an HTML comment above `<footer>`. Sanitize: replace any `--` sequence inside user-supplied strings with `- -` before wrapping in `<!-- … -->` so the comment can never close prematurely.
- If `frontmatter.canonical_url` is absent, omit the `<link rel="canonical">` tag entirely — do not emit an empty `href`.
- HTML files are minified-optional; readable indentation is fine. The skill never injects CSS or external `<script>` tags beyond the JSON-LD block.

**Schema parity** with cited sources (Step 3.5 / 3.4): if `structural_template_by_channel[channel]` carries observed JSON-LD `@type`s from cited sources, the artifact's emitted `@type` SHOULD be in the same family. Mismatch is a soft warning at Step 6, not a hard fail — sometimes the editorial choice is to upgrade (cited sources are bare `Article` but you have data for `NewsArticle`).

## Step 6 — Citability self-check (per artifact)

Run per artifact before completion.

### 6.1 Universal hard gates (every channel)

These fail the artifact immediately — one fix iteration, then leave the item `pending`:

- **No image placeholders.** Zero occurrences of `[Image`, `[image`, `[Photo`, `[photo`, `[placeholder`, `[Placeholder`, or `TODO` in body text. Real markdown image syntax with a URL or path is allowed; `media_specs:` YAML is allowed (it's a distinct format).
- **No invented URLs.** Every external URL in the artifact must appear in `cited_url_allowlist[]` — the union of: every cited `source_url` from Step 3.1, every URL passed to `aeko_crawl_url` in Step 3.4, every URL returned by `aeko_list_own_content` in Step 3.6, every URL in `media_by_channel{}` from Step 4d, plus any URL the user pasted into an `other:<name>` reference in Step 4c. Build this list explicitly in Step 3.5 (initial population) and Step 4d (final addition). Step 6's URL extractor scans the artifact for `https?://…` tokens and fails the artifact if any URL is not in the allowlist. Brand-internal anchor links (`#section`) and `mailto:` are exempt.
- **Frontmatter `forbidden` list:** zero matches.

### 6.2 Prose channels (forensics-detected, `보도자료`, `magazine`, `partner_media`)

Apply the 5 citability dimensions:
1. **Answer-block quality** — opening 1-2 sentences of each section directly answer a natural question.
2. **Self-containment** — subject named in every paragraph; no pronoun opens.
3. **Structural readability** — headings, lists, short paragraphs (≤167 words).
4. **Statistical density** — specific numbers / dimensions / years where appropriate.
5. **Uniqueness signals** — at least one claim or angle not obviously derivable from a generic search.

Plus the **structural-target deltas** from §3.5 / §3.4:

- Median paragraph word count within ±25% of the channel's target.
- Heading max-depth within ±1 of the target (e.g., target h3 → h2/h3/h4 OK, h5 not).
- List density (lists per 1000 words) within ±25% of target.
- Image count within ±1 of target (only when target > 0; not enforced if no media specs and target == 0).

Out-of-band targets are **soft warnings** unless the deviation is ≥50%, which becomes a hard gate (one fix iteration).

### 6.3 Editorial channels' HTML pair (`보도자료`, `magazine`, `partner_media`)

Both `<slug>.md` AND `<slug>.html` must exist. The `.html` file:

- Parses as HTML (well-formed enough for `lxml` / `html.parser` to accept).
- Contains exactly one `<article>` root.
- Each `<script type="application/ld+json">` block parses with `json.loads` after stripping the script wrapper.
- Required JSON-LD fields are present per the schema in `references/recipes/editorial-html-jsonld.md` (e.g., `NewsArticle` requires `headline`, `datePublished`, `author`, `publisher`).
- **Schema parity** soft check: emitted top-level `@type` is in the same family as the cited sources' dominant `@type` (`Article` ⊇ `NewsArticle`/`BlogPosting`; `Review` ⊇ `Review`/`Recommendation`). Mismatch warns once.

Any HTML-side hard-gate failure → one fix iteration → leave `pending`.

### 6.4 Social channels (`instagram`, `tiktok`, `youtube`)

Substitute the recipe's "Acceptance gates" section in `references/recipes/<channel>.md` as the gates. The §6.1 universal hard gates still apply.

### 6.5 Iteration budget

Weak on a soft-warning dimension → iterate that artifact's affected section. Cap at **2 soft iterations per artifact**. Hard-gate failures get **1 fix iteration** before failing the artifact. If any artifact still fails its hard gates, leave the entire item `pending` (do NOT call `aeko_complete_action_item`) and surface which channels failed and which dimensions need work.

## Step 7 — Mark complete

```
aeko_complete_action_item(
    item_id=frontmatter.item_id,
    artifact_summary="<N channels: reddit, naver_blog, 보도자료, instagram> · mimicked: <top 2 source patterns>",
    artifact_paths=[<absolute paths of every file written across all channels>],
    write_result=None,  # content artifacts never do store writes
)
```

Only complete if:
- ≥1 artifact written AND every written artifact passed its acceptance gates AND citability self-check passed for every artifact.

## Step 8 — User-facing summary

```
✔ Content drafted across <N> channels: <comma list>
  Domain:        <domain>
  Action item:   <item_id>
  Mimicked:      <top 2-3 source domains + format patterns>
  Refs loaded:
    - instagram    → recipes/instagram.md + examples/instagram-post-example.md
    - 보도자료      → recipes/보도자료.md + recipes/editorial-html-jsonld.md
    - naver_blog   → forensics-derived (no recipe file)
    - …            (one line per channel; show "no exemplar" when example file absent)
  Artifacts:
    - reddit       → <path>
    - naver_blog   → <path>
    - 보도자료      → <path>
    - instagram    → <path>
  Media refs:    <N attached, M skipped>
  Citability:    passed on N/N · failed on: <list or 'none'>
```

The **Refs loaded** block exists so users can verify their `references/examples/<file>.md` is being picked up — if a channel's line shows only `recipes/<channel>.md` and no `examples/...`, their exemplar isn't matching the filename pattern.

If any artifact targets external media, append a publish checklist:

```
External-media publish checklist (never auto-published):
  - reddit: review + post to <subreddit guess from forensics>
  - naver_blog: post under <author/account>
  - 보도자료: distribute via your PR channel
  - instagram / tiktok / youtube: schedule via your scheduling tool
  - Add canonical link back to <domain> when permitted
  - Mark the AEKO action complete after publishing (already done by this run if all checks passed)

Next: /aeko-action-center <domain_id> content
```

## Step 9 — Publish handoff (optional, forward-compat)

This skill never publishes — Step 8 stops at local files plus the manual checklist. Publishing via the user's authenticated browser session is the job of a separate skill, `/aeko-publish` (planned, not yet shipped). This step adds a **read-only handoff line** at the very end of the user-facing summary so the path is visible from day one.

### 9.1 Detect the Chrome bridge

Check whether Claude for Chrome is connected on the current session. Reliable signals (any one is sufficient):

- The session was started with `claude --chrome`.
- The user invoked `/chrome` earlier and the bridge ack'd.
- A previous tool call in this session used a Chrome-bridge tool successfully.

If unsure, do not probe — silence is the safe default. Treat "unknown" as "not connected" for this step.

### 9.2 Append one line to the Step 8 summary

Insert immediately under the `Next:` line in §8.

**If Chrome bridge is connected:**

```
Publish (optional): /aeko-publish <item_id>
  ↳ uses your authenticated Chrome session to draft posts on the channels above.
  ↳ skill is in development — if /aeko-publish is not yet installed, follow the checklist above.
```

**If Chrome bridge is NOT connected:**

```
Publish (optional): install Claude for Chrome and connect /chrome to enable the future
  /aeko-publish handoff. Until then, follow the checklist above.
```

### 9.3 Hard rules for this step

- **Never invoke** `/aeko-publish`, never simulate it, never click compose forms, never fill publish fields. This step is text-only — it adds two lines to the summary and stops.
- **Never alter** the External-media publish checklist in §8. The checklist is the load-bearing fallback; the handoff is a hint about a future shortcut.
- **Never widen** `allowed-tools` for this skill to include browser-bridge tools. Publishing capability lives in `/aeko-publish`'s own `allowed-tools`, not here.
- **No retro-edits** when `/aeko-publish` ships — that skill's `allowed-tools` and acceptance gates are scoped there. The handoff line stays as-is.

This keeps `aeko-create-content` honest about its boundary ("never auto-publishes") while making the publish path discoverable to users the moment it's available.

## Error paths

- Plan endpoint unavailable / parse error → stop; surface detail.
- Contract mismatch → stop.
- Stale brand kit + user declines → stop.
- No tracked prompts available AND research prompt fallback returns empty → tell user the skill needs at least one signal to mimic; stop and suggest `/aeko-find-prompts-to-track` first. Step 4 still runnable for fully-manual format choices, but the structural-template quality drops; warn before proceeding.
- `aeko_crawl_url` 4xx/5xx or unavailable (backend route not yet shipped) → log a single warning line in §3.4 and §4a, continue on the snapshot signal alone. Live recrawl is enriching, not gating.
- `aeko_list_own_content` 4xx/5xx or unavailable → log "no in-store signature — drafting from cited-source signal only" once, continue. In-store signature is enriching, not gating.
- Step 4e returns 0 selected channels → stop without writing or completing.
- User cancels at Step 4e → stop without writing or completing.
- Citability self-check hard-gate fails after the §6.5 iteration budget on any artifact → leave item `pending`; surface failed channels + dimensions.
- HTML emission fails on an editorial channel (markdown rendered, but JSON-LD won't validate) → write the `.md`, skip the `.html`, surface the JSON-LD error in the user summary, and treat the channel as failed for completion purposes.
- Non-interactive caller (e.g., dispatched from another agent): if `frontmatter.non_interactive == true` (forward-compat), skip 4b/4c/4d asks and default to: all auto-detected channels, no addons, no media. If 0 auto-detected, stop with "non-interactive run needs at least one auto-detected channel".

## What this skill never does

- Never writes to a connected store (PDP work is `/aeko-update-pdp`).
- Never publishes to external media automatically — always leaves local files only.
- Never copies or uploads media — only references URLs / paths the user supplies, plus the `media_specs:` YAML stubs when media was skipped.
- Never emits `[Image #N]` / `[Image]` / `[placeholder]` / `[photo]` / `TODO` markers in body text. Real markdown image syntax with a URL or path, or a `media_specs:` block — nothing else.
- Never fabricates the citation forensics; if tracked prompts have no responses, fall back transparently. Live `aeko_crawl_url` results never get faked when the backend is unavailable.
- Never copies text from cited sources verbatim; mimics format, not content. Cited-source `extracted_text` is for tone calibration only — never paste.
- Never invents URLs in artifacts — every URL must come from forensics, in-store content, live crawls, or user-supplied media.
- Never regenerates the Plan.md.
- Never reads machine values from prose.
- Never echoes raw frontmatter.
- Never proceeds past Step 4e without explicit user confirmation (except in non-interactive mode with a valid auto-detected channel set).
