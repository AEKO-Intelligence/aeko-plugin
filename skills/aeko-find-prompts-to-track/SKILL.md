---
name: aeko-find-prompts-to-track
description: >
  Discovery workflow for research prompts. Walks the user through filtering
  AEKO's prompt library (AI platform + context + country + scope), surfaces
  the best candidates for their brand, and tracks the selected prompts so
  the AEKO pipeline re-queries them on cadence. Closes the find → pick →
  track loop without leaving Claude.
argument-hint: "[domain-id]"
allowed-tools: aeko_list_domains, aeko_get_domain_info, aeko_search_research_prompts, aeko_track_prompt, aeko_get_tracked_prompts, aeko_get_quota, aeko_list_contexts, aeko_create_context, aeko_list_views, aeko_create_view, aeko_add_prompts_to_view
---

# AEKO Find Prompts To Track

Helps the user discover research prompts worth tracking. Goal: after this skill runs, the user has 5-10 new tracked prompts relevant to their brand, without having to leave Claude and paste into the dashboard.

## Marketer-facing output contract

Explain prompts as "questions your customers may ask AI." Keep ranking tables compact and show why each prompt
matters: audience, buying stage, and competitor visibility. Never track prompts without explicit user selection.

Language: mirror the user's chat language for user-facing steps, summaries, questions, and confirmations.
Keep slash commands, IDs, file paths, prompt metadata keys, and tool names in English/ASCII.

## Input

- `domain-id` (optional) — UUID of the domain to scope suggestions to. If missing, offer `aeko_list_domains` pick-list.

## Step 1 — Resolve domain + optional angle defaults

1. If `$1` is set → use it.
2. Else → `aeko_list_domains`. If one domain: auto-pick. If multiple: show list and ask.
3. Call `aeko_get_domain_info(domain_id)`.
4. Call `aeko_list_views(domain_id=...)`.
5. Call `aeko_list_contexts(domain_id=...)` only if the user explicitly wants Context grounding, or if the domain info/tool output indicates Context is available. Context library is Pro+; a Starter 403 is not a blocker for basic prompt tracking.
6. Use domain fields plus the available IDs to seed sensible defaults:
   - `country` = first entry in domain's `selected_markets` / `target_country` if available, else ask.
   - `scope` = domain's `industry` / `vertical` / `scope` field if set.
   - `context_ids[]` = real Context ids from `aeko_list_contexts` when Pro+ Context is available.
   - `view_id` = a real saved view id from `aeko_list_views`.

If no Context fits and the user wants one, use `aeko_create_context` after explicit confirmation. If no view fits and the user wants grouping, use `aeko_create_view`. Do not block Starter users on missing Context access.

## Step 2 — Ask user for filter intent

Prompt in the user's chat language. Use the matching KO/EN template below when applicable; for other
languages, translate the EN template naturally while keeping platform/country/query-type tokens unchanged.

**KO:**
```
어떤 연구 프롬프트를 찾을까요? 비워두면 브랜드 기본값으로 검색할게요.

- 플랫폼: [claude / openai / google / perplexity / all]
- 국가: [KR / US / JP / ... / all]
- 컨텍스트 (저장된 Context 선택 또는 새 Context 저장)
- 저장할 View (선택)
- 키워드 (예: "이불 추천", "민감성 피부")
- 쿼리 유형 (informational / comparison / recommendation / transactional)

원하는 조합을 자유롭게 알려주세요.
```

**EN:**
```
What research prompts should I look for? Leave fields blank to use your brand defaults.

- Platform: [claude / openai / google / perplexity / all]
- Country: [KR / US / JP / ... / all]
- Context (choose saved Context IDs, or save a new Context)
- Saved view (optional)
- Keyword (e.g. "bedding recommendation", "sensitive skin")
- Query type (informational / comparison / recommendation / transactional)

Describe the combination you want.
```

Parse the user's response into search filters and tracking angles. `all` / blank → omit that filter (no param to the tool).

Tracking angles are only:
- `ai_platforms[]`
- `countries[]`
- `view_id`
- `context_ids[]` (Pro+ Context library only)

Do not promise direct tag/funnel/query-type writes. Tags, funnel stage, and query type are derived by AEKO after tracking.
For Starter users, use `ai_platforms=["openai"]` and one allowed country unless the backend/domain data says otherwise.

## Step 3 — Search

Call `aeko_search_research_prompts` with the parsed filters + `page_size=25`. At least one filter must be non-null (the tool rejects fully empty queries).

If zero results → widen: drop the most restrictive filter, typically `query_type` or an overly narrow keyword, and retry once. Tell the user what was relaxed.

## Step 4 — Score + rank candidates

For each returned prompt, assemble a relevance score using these signals:
- **Keyword/context overlap** between domain keywords, product/category context, user-provided context, and the prompt's text or `keywords[]`. High overlap → high score.
- **Context match** — prompt context/use case vs the requested customer situation. Context applies here and also later to content optimization.
- **Latest-response signals** (from the search payload's `latest_response`):
  - High `mention_count` across competitors → the prompt is a battleground worth contesting.
  - Presence of this brand in the mention breakdown → already getting mentioned; may not need tracking (user's call).
  - Absence of this brand with strong competitor mentions → prime tracking candidate.
- **Funnel stage balance** — prefer a mix across awareness / consideration / decision rather than all-same-stage.

Show top 10-15 sorted by score, in a compact table:

```
| # | Prompt | Platform | Country | Context | Competitors mentioning |
|---|--------|----------|---------|---------|------------------------|
| 1 | ...    | Claude   | KR      | sensitive skin | 필리, 모노랩스  |
```

Include the prompt ID as a monospace UUID column so the user can reference specific rows.

## Step 5 — Pick-list

Ask the user:

**KO:** "몇 번을 트래킹할까요? 쉼표로 여러 개 입력 가능. 전부 추적하려면 `all` 입력."
**EN:** "Which ones should I start tracking? Comma-separated for multiple. `all` to track every row shown."

Parse response into a list of row indices → prompt payloads.

## Step 6 — Pre-flight package limits

Call `aeko_get_quota` to see the tracked-prompt cap and remaining capacity. If quota data is unavailable, call `aeko_get_tracked_prompts` as a fallback count and let the backend enforce the hard cap.

If the user's selection would exceed their package cap → warn, show how many they can track, ask them to narrow.

## Step 7 — Track each selected prompt

For each selected row, call:

```
aeko_track_prompt(
    raw_prompt=row.raw_prompt,
    prompt_en=row.prompt_en,
    ai_platforms=[row.ai_platform] or selected_ai_platforms,
    countries=[row.country] or selected_countries,
    view_id=selected_view_id,        # only a real ID from aeko_list_views / aeko_create_view
    context_ids=selected_context_ids # only real IDs from aeko_list_contexts / aeko_create_context
)
```

Never pass search-row-only fields such as `prompt_ko`, `model`, `language`, `industry`, `vertical`, `tags`, `query_type`, or `funnel_stage` to `aeko_track_prompt`; AEKO derives them server-side.

Handle tool output:
- `tracked` / `associated` → note the tracked prompt ID.
- `already_tracked` → skip, note "already tracked". The backend returns HTTP 201 with this status, not 409.
- `reactivated` → note "reactivated". The backend returns HTTP 201 with this status.
- `failed` / `limit_blocked` / backend 403 → stop loop if it is a package cap; tell user how many succeeded before cap.

## Step 8 — Summary

Print:

```
✔ Tracking started for N prompts

  Newly tracked (N):
    - <prompt_id> · <ai_platform> · <country> · <first 80 chars>
    - ...
  Reactivated (M):
    - ...
  Skipped — already tracked (K):
    - ...

Next: AEKO will re-query these on cadence; check back in 1-3 days.
      For a deep-dive on one prompt's citation footprint:
      /aeko-prompt-deep-dive <prompt_id>
```

## Error paths

- No domains connected → tell user to add one at the AEKO dashboard; stop.
- Search returned zero even after widening → suggest manual prompt creation via AEKO dashboard; stop.
- User picks nothing → exit cleanly, no writes.
- Backend 403 on track → surface the upgrade pitch from the error verbatim (backend includes the package-cap reason and pitch message).

## What this skill never does

- Never tracks a prompt without explicit user selection.
- Never calls `aeko_track_prompt` with non-settable metadata fields, even if a search row contains them.
- Never deletes or untracks existing prompts — for that, use `/aeko-manage-tracked-prompts` or the dashboard.
