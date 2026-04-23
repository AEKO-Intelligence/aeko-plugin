---
name: aeko-find-prompts-to-track
description: >
  Discovery workflow for research prompts. Walks the user through filtering
  AEKO's prompt library (AI platform + persona + country + scope), surfaces
  the best candidates for their brand, and tracks the selected prompts so
  the AEKO pipeline re-queries them on cadence. Closes the find → pick →
  track loop without leaving Claude.
argument-hint: "[domain-id]"
allowed-tools: aeko_list_domains, aeko_get_domain_info, aeko_get_brand_kit, aeko_search_research_prompts, aeko_track_prompt, aeko_get_tracked_prompts, WebFetch
---

# AEKO Find Prompts To Track

Helps the user discover research prompts worth tracking. Goal: after this skill runs, the user has 5-10 new tracked prompts relevant to their brand, without having to leave Claude and paste into the dashboard.

## Input

- `domain-id` (optional) — UUID of the domain to scope suggestions to. If missing, offer `aeko_list_domains` pick-list.

## Step 1 — Resolve domain + brand context

1. If `$1` is set → use it.
2. Else → `aeko_list_domains`. If one domain: auto-pick. If multiple: show list and ask.
3. Call `aeko_get_domain_info(domain_id)` and `aeko_get_brand_kit(domain_id)`. Use these to seed sensible default filters:
   - `country` = first entry in domain's `selected_markets` if available, else from `target_country` on the brand kit, else ask.
   - `scope` = domain's `industry` / `vertical` / `scope` field if set.

## Step 2 — Ask user for filter intent

Prompt in `target_language`:

**KO:**
```
어떤 연구 프롬프트를 찾을까요? 비워두면 브랜드 기본값으로 검색할게요.

- 플랫폼: [claude / openai / google / perplexity / all]
- 국가: [KR / US / JP / ... / all]
- 페르소나 (예: new_mom, enthusiast, beginner)
- 키워드 (예: "이불 추천", "민감성 피부")
- 쿼리 유형 (informational / comparison / recommendation / transactional)

원하는 조합을 자유롭게 알려주세요.
```

**EN:**
```
What research prompts should I look for? Leave fields blank to use your brand defaults.

- Platform: [claude / openai / google / perplexity / all]
- Country: [KR / US / JP / ... / all]
- Persona (e.g. new_mom, enthusiast, beginner)
- Keyword (e.g. "bedding recommendation", "sensitive skin")
- Query type (informational / comparison / recommendation / transactional)

Describe the combination you want.
```

Parse the user's response into filter args. `all` / blank → omit that filter (no param to the tool).

## Step 3 — Search

Call `aeko_search_research_prompts` with the parsed filters + `page_size=25`. At least one filter must be non-null (the tool rejects fully empty queries).

If zero results → widen: drop the most restrictive filter (typically `persona_type` or `query_type`) and retry once. Tell the user what was relaxed.

## Step 4 — Score + rank candidates

For each returned prompt, assemble a relevance score using these signals:
- **Keyword overlap** between brand kit `brand_keywords[]` + `must_include[]` and the prompt's text or `keywords[]`. High overlap → high score.
- **Persona match** — prompt's `persona` vs brand kit `target_audience`.
- **Latest-response signals** (from the search payload's `latest_response`):
  - High `mention_count` across competitors → the prompt is a battleground worth contesting.
  - Presence of this brand in the mention breakdown → already getting mentioned; may not need tracking (user's call).
  - Absence of this brand with strong competitor mentions → prime tracking candidate.
- **Funnel stage balance** — prefer a mix across awareness / consideration / decision rather than all-same-stage.

Show top 10-15 sorted by score, in a compact table:

```
| # | Prompt | Platform | Country | Persona | Competitors mentioning |
|---|--------|----------|---------|---------|------------------------|
| 1 | ...    | Claude   | KR      | new_mom | 필리, 모노랩스          |
```

Include the prompt ID as a monospace UUID column so the user can reference specific rows.

## Step 5 — Pick-list

Ask the user:

**KO:** "몇 번을 트래킹할까요? 쉼표로 여러 개 입력 가능. 전부 추적하려면 `all` 입력."
**EN:** "Which ones should I start tracking? Comma-separated for multiple. `all` to track every row shown."

Parse response into a list of row indices → prompt payloads.

## Step 6 — Pre-flight package limits

Call `aeko_get_tracked_prompts` to see the user's current tracked count. Compare against known package limits (derived from brand kit `metadata.account_tier` or, if unknown, just proceed and let the backend 403 — tell the user that's the fallback).

If the user's selection would exceed their package cap → warn, show how many they can track, ask them to narrow.

## Step 7 — Track each selected prompt

For each selected row, call:

```
aeko_track_prompt(
    raw_prompt=row.raw_prompt,
    ai_platform=row.ai_platform,
    prompt_en=row.prompt_en,
    prompt_ko=row.prompt_ko,
    model=row.model,
    language=row.language,
    country=row.country,
    industry=row.industry,
    vertical=row.vertical,
    persona=row.persona,
    tags=row.tags,
)
```

Handle response codes:
- Success → note the new tracked prompt ID.
- 409 (already tracking) → skip, note "already tracked".
- 403 (package cap hit) → stop loop; tell user how many succeeded before cap.
- Reactivation message (backend returns 200 with status `tracked` when previously untracked) → note "reactivated".

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
- Never calls `aeko_track_prompt` with fields the search result didn't provide (no fabrication).
- Never deletes or untracks existing prompts — for that, use `/aeko-prompt-deep-dive` or the dashboard.
