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
allowed-tools: aeko_get_action_plan, aeko_get_brand_kit, aeko_get_tracked_prompt, aeko_search_research_prompts, aeko_complete_action_item, Read, Write, WebFetch, WebSearch
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

1. Read `frontmatter.prompts_to_rank_on` (list of prompt IDs or text). For each prompt ID (up to 5 — top-5 by priority if prose indicates ordering):
   - Call `aeko_get_tracked_prompt(prompt_id, window="30d")` for the forensics payload.
   - Across the responses, collect the cited sources: source URL, domain, source_type, position_in_response, and the crawled metadata (`extracted_text`, `json_ld` types, `source_analysis.citability_score`).
2. Rank the aggregated sources by citation frequency × average position (lower position = better). Surface the top 5-10 source domains and their canonical URLs.
3. For each top source, note structural signals:
   - Average paragraph length.
   - Heading hierarchy depth.
   - Presence of bulleted lists, numbered steps, Q&A blocks.
   - JSON-LD types present on the page (if any).
   - Citability score if the backend surfaced one.
4. **Auto-detect channels.** For each top source, classify the domain into a channel slug:
   - `reddit.com/*` → `reddit`
   - `*.blog.naver.com` / `m.blog.naver.com` → `naver_blog`
   - `*.tistory.com` → `tistory`
   - `wikipedia.org` → `wikipedia`
   - news / partner-media domains (heuristic: `news.*`, `*.co.kr/news/*`, established publication TLDs) → `partner_media`
   - else → `web_article` (generic)
   Deduplicate. Carry `auto_detected_channels[]` into Step 4.
5. Build a per-channel **structural template** the draft should mimic. **You are not copying text** — you are matching format: if Reddit threads win, the draft reads like a Q&A with lived-experience tone; if Naver 블로그 wins, it reads like a first-person informal review with in-line images; if partner-media wins, it reads like a comparison article with product callouts. Carry `structural_template_by_channel{}` into Step 5.

If `prompts_to_rank_on` is empty OR `aeko_get_tracked_prompt` 404s on every prompt ID → fall back: pull 3-5 candidate prompts via `aeko_search_research_prompts` using `frontmatter.keywords` + `frontmatter.target_country`, derive the structural template from those, and tell the user forensics fell back. `auto_detected_channels[]` may be empty — that's fine; user picks formats manually in Step 4.

## Step 4 — Channel & media selection (interactive)

This step is the v2 fanout. Always run; respect `skip` / `none` for empty selections.

### 4a. Print forensics summary

```
Top cited source domains for this prompt set:
  1. reddit.com/r/<sub>           (cited N× · avg position X · Q&A format)
  2. blog.naver.com/<author>      (cited N× · avg position X · 1인칭 review)
  3. <partner-media>.com          (cited N× · avg position X · 비교 article)
Auto-detected channels: <comma list, or 'none — forensics fallback used'>
```

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

Record into `media_by_channel{}`.

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

### 5.1 Pick the structural source

- **Auto-detected channel**: use `structural_template_by_channel[channel]` from Step 3.
- **Built-in addon** (`보도자료`, `magazine`, `instagram`, `tiktok`, `youtube`): use the inline recipe in §5.6.
- **`other:<name>`**: if reference URLs were provided, fetch them via `WebFetch` and derive an ad-hoc template (mini-forensics: paragraph length, heading depth, list usage, tone signal). If only a description was given, use the description plus brand-voice defaults.

### 5.2 Optional research

If frontmatter prose requests external research OR an `other:<name>` channel needs reference fetching:
- `WebSearch` for related context (competitor brand names, recent news, review themes).
- `WebFetch` on specific URLs called out in prose or supplied by user. Do NOT invent URLs.
- Append a research-log to the channel's artifact directory.

### 5.3 Draft the artifact

Follow `frontmatter.output_artifact_format` (typically `markdown`) for prose channels, or the recipe-defined format for social channels. Enforce:
- `frontmatter.must_include` — every string MUST appear in **at least one** generated artifact (not necessarily every channel — a brand name belongs in 보도자료 boilerplate but may not fit a TikTok beat).
- `frontmatter.forbidden` — no string MAY appear in any artifact.
- `frontmatter.sections_required` — applies to prose channels (forensics-detected, `보도자료`, `magazine`). Each entry MUST map to a heading or named section. Social channels (`instagram`, `tiktok`, `youtube`) use the recipe's required parts in place of `sections_required`.

**Voice discipline:**
- Brand kit `tone_of_voice` drives sentence-level register.
- Brand kit `must_include` terms + `forbidden` terms override frontmatter if conflicting (surface the conflict to the user before resolving).
- Target audience from brand kit shapes word choice (beginner vs expert vocabulary).
- For `보도자료` specifically: 합니다체 is required even if brand voice elsewhere is 요체 — the format wins; surface the conflict before resolving.
- **No hard CTAs** ("Buy now" / "Click here" / promotional commands) in the body. Citability content earns the click via authority, not commands. Same principle as `/aeko-update-pdp`: AEKO injects citability content; the host channel owns the action UI.

**Structural discipline** (from Step 3 template or §5.6 recipe):
- Match the winning-source format the forensics identified.
- Be honest about what this is: Reddit-style Q&A is fine, but do NOT fake Reddit thread formatting or pretend the content is crowd-sourced.
- Link out to the top cited sources where the draft genuinely benefits from them (prevents the "generic AEO mush" failure mode).

### 5.4 Embed media reference

If `media_by_channel[channel]` is set:
- Markdown channels → standard image / video markdown:
  - Image: `![<alt>](<url-or-path>)`
  - Video: `[Video: <url-or-path>]` block with caption.
- Instagram → `media:` field at the top of the file referencing the asset; alt text rendered in its own section.
- TikTok → reference inside the relevant beat (`[on-screen]: image at <path>`).
- YouTube → reference in description (`Thumbnail: <url-or-path>`).

The skill **does not copy or upload** the media — references only.

### 5.5 Artifact path

Always use channel-segmented paths in v2:

`./aeko-artifacts/<domain_id>/<item_id>/<channel_slug>/<slug>.<ext>`

- Markdown channels: `.md` extension; `slug` derived from the Plan title.
- Social channels: filename is the channel slug (`instagram.md`, `tiktok.md`, `youtube.md`) — single file containing caption / script / metadata sections.

If frontmatter prose requests sibling files (JSON-LD, meta, social teaser), write them next to the channel's main file.

### 5.6 Inline channel recipes

Use these structural recipes for built-in addon channels.

- **`보도자료`** (Korean press release, 합니다체):
  - Headline (≤40자) · 부제 · 리드 (5W1H in opening 2 sentences)
  - 본문 3–4 단락 · 1 인용문 (CEO or product lead) · boilerplate (one paragraph about the brand — pull from `brand_kit.brand_voice_summary`; never hard-code "AEKO" since this skill drafts for the user's domain, not for AEKO itself)
  - 문의처 line at bottom · embargo line at top if user supplies one
  - **Acceptance**: 5W1H present in lead, 합니다체 throughout, ≥1 quote, boilerplate present.

- **`magazine`** (Vogue-style editorial; KO/EN per `target_language`):
  - Hook quote (italic, ≤25 words) · editor's note (1 paragraph)
  - 3–4 lifestyle scenes weaving the product/topic in (NOT a listicle)
  - Subject named per paragraph; sensory verbs; minimal hashtags
  - **Acceptance**: hook quote present, narrative scenes ≥3, no bullet lists.

- **`instagram`** (KO default, EN if `target_language=en`):
  - Caption: 1 hook line · 3–5 body lines · 5–12 hashtags (KO + EN mix)
  - Alt text (≤125 chars, accessibility)
  - Optional 5-slide carousel outline if forensics suggests carousel beats listicle
  - **Acceptance**: hook ≤2 lines, hashtags 5–12, alt text present.

- **`tiktok`**:
  - 30–60 second script as numbered beats: `[0–3s] hook · [3–10s] context · …`
  - On-screen text per beat · voiceover line per beat · 3–6 hashtags
  - **Acceptance**: total runtime in 30–60s window, ≥1 hook beat ≤3s, every beat has both on-screen and voiceover lines.

- **`youtube`**:
  - Title (≤60 chars, includes prompt keyword)
  - Description: first 200 chars = hook (above the fold), then full description, then chapter list (`00:00 Intro / …`), then tags
  - **Acceptance**: title ≤60 chars, ≥3 chapters, hook in first 200 chars.

## Step 6 — Citability self-check (per artifact)

Run per artifact before completion.

**Prose channels** (forensics-detected, `보도자료`, `magazine`) — apply the existing 5 dimensions:
1. **Answer-block quality** — opening 1-2 sentences of each section directly answer a natural question.
2. **Self-containment** — subject named in every paragraph; no pronoun opens.
3. **Structural readability** — headings, lists, short paragraphs (≤167 words).
4. **Statistical density** — specific numbers / dimensions / years where appropriate.
5. **Uniqueness signals** — at least one claim or angle not obviously derivable from a generic search.

**Social channels** (`instagram`, `tiktok`, `youtube`) — substitute the recipe's acceptance bullets in §5.6 as the gates.

Weak on a dimension → iterate that artifact's affected section. Cap at 2 iterations per artifact. If any artifact still fails after 2 iterations, leave the entire item `pending` (do NOT call `aeko_complete_action_item`) and surface which channels failed and which dimensions need work.

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
  Artifacts:
    - reddit       → <path>
    - naver_blog   → <path>
    - 보도자료      → <path>
    - instagram    → <path>
  Media refs:    <N attached, M skipped>
  Citability:    passed on N/N · failed on: <list or 'none'>
```

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

## Error paths

- Plan endpoint unavailable / parse error → stop; surface detail.
- Contract mismatch → stop.
- Stale brand kit + user declines → stop.
- No tracked prompts available AND research prompt fallback returns empty → tell user the skill needs at least one signal to mimic; stop and suggest `/aeko-find-prompts-to-track` first. Step 4 still runnable for fully-manual format choices, but the structural-template quality drops; warn before proceeding.
- Step 4e returns 0 selected channels → stop without writing or completing.
- User cancels at Step 4e → stop without writing or completing.
- Citability self-check fails after 2 iterations on any artifact → leave item `pending`; surface failed channels + dimensions.
- Non-interactive caller (e.g., dispatched from another agent): if `frontmatter.non_interactive == true` (forward-compat), skip 4b/4c/4d asks and default to: all auto-detected channels, no addons, no media. If 0 auto-detected, stop with "non-interactive run needs at least one auto-detected channel".

## What this skill never does

- Never writes to a connected store (PDP work is `/aeko-update-pdp`).
- Never publishes to external media automatically — always leaves local files only.
- Never copies or uploads media — only references URLs / paths the user supplies.
- Never fabricates the citation forensics; if tracked prompts have no responses, fall back transparently.
- Never copies text from cited sources verbatim; mimics format, not content.
- Never regenerates the Plan.md.
- Never reads machine values from prose.
- Never echoes raw frontmatter.
- Never proceeds past Step 4e without explicit user confirmation (except in non-interactive mode with a valid auto-detected channel set).
