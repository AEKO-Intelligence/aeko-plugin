---
name: aeko-create-content
description: >
  Content executor for Action-tab items with
  `execution_class=local_content_artifact`. Fetches a Plan.md, pulls
  tracked-prompt citation forensics to identify the source structures AI
  engines actually cite (Reddit threads, Naver blogs, partner media,
  etc.), drafts own-site or external-media content that mimics those
  structures in the brand voice, and saves locally. Never writes to a
  store. Splits the content branch out of the retired `/aeko-run-action`.
argument-hint: "<item-id>"
allowed-tools: aeko_get_action_plan, aeko_get_brand_kit, aeko_get_tracked_prompt, aeko_search_research_prompts, aeko_complete_action_item, Read, Write, WebFetch, WebSearch
---

# AEKO Create Content

Executes one Action-tab content item end-to-end: fetch Plan.md → pull citation-forensics on tracked prompts → identify winning source structures → draft content mimicking those structures in the brand voice → save local artifact → mark complete.

Contract reference: `docs/contracts/action-item-contract.md` §3 (Plan.md), §6 (completion).

## Input

- `item-id` (required) — `$1`. If missing, stop and point user to `/aeko-action-center <domain_id> content`.

## Step 1 — Fetch and parse the Plan.md

Call `aeko_get_action_plan(item_id)`. Parse YAML frontmatter + prose.

**Validate:**
- `contract_version` starts with `2026-04-17.action.v1.` — else stop.
- Pin this skill to contract minor `v1.2`. Greater minor → print advisory + proceed.
- `tab == "action"` — else stop.
- `execution_class == "local_content_artifact"` — else redirect to the right executor.
- `artifact_type ∈ {own_store_markdown, external_media_markdown, own_store_content, external_media_content}` (accept both v1 and v2 names for forward-compat) — else stop.
- `status ∈ {pending, ready}` — else stop.
- `write_target == "local"` — content artifacts never write to store; mismatch → stop.
- `tier_required` gate via brand kit metadata.

Print header in `target_language`:
1. Action label — KO (own): "자사 콘텐츠 생성: `<artifact_type>`" / KO (external): "외부 매체 콘텐츠 생성: `<artifact_type>`" / EN: "Generating {own-site|external-media} content: `<artifact_type>`"
2. Context: domain, channels (comma-joined).
3. Persona: `persona_label` if present.

Print prose verbatim. Never echo frontmatter.

## Step 2 — Stale brand-kit check

If `frontmatter.requires_brand_kit == true`:
- `aeko_get_brand_kit(frontmatter.domain_id)`. Missing / empty → stop with Brand-Kit-missing message.
- Verify voice minimum: `tone_of_voice` present + at least one of `{brand_voice_summary, target_audience}`. Thin kit → warn + offer to abort (`/aeko-brand-kit <domain_id> edit`).
- Snapshot-version drift: ask user.

## Step 3 — Citation forensics on tracked prompts

This is what makes AEKO-grounded content beat vanilla Claude. Build a structural model of what AI engines currently cite for this topic, then mimic.

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
4. Compose a brief internal "structural template" the draft should mimic. **You are not copying text** — you are matching format: if Reddit threads win, the draft reads like a Q&A with lived-experience tone; if Naver 블로그 wins, it reads like a first-person informal review with in-line images; if partner-media wins, it reads like a comparison article with product callouts.

If `prompts_to_rank_on` is empty OR `aeko_get_tracked_prompt` 404s on every prompt ID → fall back to a lighter flow: pull 3-5 candidate prompts via `aeko_search_research_prompts` using `frontmatter.keywords` + `frontmatter.target_country`, and derive structural template from those. Tell the user forensics fell back and why.

## Step 4 — Research phase (optional — prose-guided)

If prose requests external research beyond forensics:
- `WebSearch` for related context (competitor brand names, recent news, review themes).
- `WebFetch` on specific URLs called out in prose. Do NOT invent URLs.
- Record the sources used in a research-log that gets appended to the artifact's sibling file.

## Step 5 — Draft the artifact

Follow `frontmatter.output_artifact_format` (typically `markdown`). Enforce:
- `frontmatter.must_include` — every string MUST appear in the draft.
- `frontmatter.forbidden` — no string MAY appear.
- `frontmatter.sections_required` — every entry MUST map to a heading or named section (markdown heading, case-insensitive trim). Missing → iterate or fail the run (do NOT call `aeko_complete_action_item`).

**Voice discipline:**
- Brand kit `tone_of_voice` drives sentence-level register.
- Brand kit `must_include` terms + `forbidden` terms override frontmatter if conflicting (surface the conflict to the user before resolving).
- Target audience from brand kit shapes word choice (beginner vs expert vocabulary).

**Structural discipline** (from Step 3 template):
- Match the winning-source format the forensics identified.
- Be honest about what this is: if forensics showed Reddit threads win, write in Q&A / lived-experience tone, but do NOT fake Reddit formatting or pretend the content is crowd-sourced.
- Link out to the top cited sources where the draft genuinely benefits from them (prevents the "generic AEO mush" failure mode).

**Artifact location:**
- Own-site: `./aeko-artifacts/<domain_id>/<item_id>/<slug>.md` where `slug` is derived from the Plan's title.
- External media: `./aeko-artifacts/<domain_id>/<item_id>/<target_channel>/<slug>.md` (e.g. `naver-blog/`, `wikipedia/`, `partner-media/`).
- If prose requests sibling files (JSON-LD, meta, social teaser), write them next to the main `.md`.

## Step 6 — Citability self-check

Before completion, re-read the draft against the 5 citability dimensions (apply inline; no backend call needed since `aeko_score_text` was retired):
1. **Answer-block quality** — opening 1-2 sentences of each section directly answer a natural question.
2. **Self-containment** — subject named in every paragraph; no pronoun opens.
3. **Structural readability** — headings, lists, short paragraphs (≤167 words).
4. **Statistical density** — specific numbers / dimensions / years where appropriate.
5. **Uniqueness signals** — at least one claim or angle not obviously derivable from a generic search.

Weak on a dimension → iterate the affected section before completion.

## Step 7 — Mark complete

```
aeko_complete_action_item(
    item_id=frontmatter.item_id,
    artifact_summary="<one-line: artifact path + mimicked source pattern>",
    artifact_paths=[<absolute paths of every file written>],
    write_result=None,  # content artifacts never do store writes
)
```

Only complete if:
- Artifact written AND acceptance gates passed AND citability self-check passed.

## Step 8 — User-facing summary

```
✔ Content drafted: <artifact_type>
  Venue:      <own-site | external-media channel>
  Artifacts:  <paths>
  Mimicked:   <top 2-3 source domains + format pattern>
  Citability: <which dimensions passed>

Next: /aeko-action-center <domain_id> content
```

If the artifact is for external media, include a publish checklist:

```
Publish checklist (external media — never auto-published):
- Review the draft in <path>
- Post to <target_channel> (<url_pattern>)
- Add canonical link back to <domain> when permitted
- Mark the AEKO action complete after publishing
```

## Error paths

- Plan endpoint unavailable / parse error → stop; surface detail.
- Contract mismatch → stop.
- Stale brand kit + user declines → stop.
- No tracked prompts available AND research prompt fallback returns empty → tell user the skill needs at least one signal to mimic; stop and suggest `/aeko-find-prompts-to-track` first.
- Citability self-check fails after 2 iterations → leave item `pending` and surface which dimensions failed + which sections need work.

## What this skill never does

- Never writes to a connected store (PDP work is `/aeko-update-pdp`).
- Never publishes to external media automatically — always leaves local files only.
- Never fabricates the citation forensics; if tracked prompts have no responses, fall back transparently.
- Never copies text from cited sources verbatim; mimics format, not content.
- Never regenerates the Plan.md.
- Never reads machine values from prose.
- Never echoes raw frontmatter.
