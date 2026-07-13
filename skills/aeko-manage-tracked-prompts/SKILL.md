---
name: aeko-manage-tracked-prompts
description: >
  Manage existing tracked prompts through AEKO MCP: inspect quota, list prompts
  grouped by Context, saved view, platform, country, funnel stage, query
  type, and tags, then untrack selected prompt IDs only after explicit user
  confirmation. Does not create new prompts; use /aeko-find-prompts-to-track
  for discovery and tracking.
argument-hint: "[domain-id]"
allowed-tools: aeko_list_domains, aeko_get_tracked_prompts, aeko_get_quota, aeko_untrack_prompt, aeko_list_contexts, aeko_list_views
---

# AEKO Manage Tracked Prompts

Use this when the user wants to review, organize, or stop tracking prompts already in AEKO.

Language: mirror the user's chat language for user-facing explanations, confirmations, and summaries. Keep tool names, IDs, and schema keys in English/ASCII.

## Safety

- Never untrack a prompt without explicit user confirmation.
- Never infer prompt IDs from prose when the user gave ambiguous labels. Show the list again and ask for exact IDs or row numbers.
- Untracking preserves historical responses and citations; it only stops future refreshes.
- This skill does not create prompts. Route discovery and creation to `/aeko-find-prompts-to-track`.

## Step 1 - Resolve optional domain

If `$1` is set, keep it as `domain_id`. If not set and context grouping is needed, call `aeko_list_domains` and let the user choose. Domain is optional because `aeko_get_tracked_prompts` lists the account's tracked prompts.

## Step 2 - Quota snapshot

Call `aeko_get_quota`.

Report:
- tracked count
- plan cap
- remaining slots
- package/tier if present

If quota is unavailable, continue with `aeko_get_tracked_prompts` and say that the backend will enforce hard limits.

## Step 3 - Pull prompts and angle catalogs

Call `aeko_get_tracked_prompts`.

If `domain_id` is known, also call:
- `aeko_list_contexts(domain_id=domain_id)`
- `aeko_list_views(domain_id=domain_id)`

Use those catalogs only to make IDs human-readable. The tracked-prompt list is authoritative.

## Step 4 - Segment the list

Render a compact grouped view. Prefer these groups in order when the data exists:

1. Context: `context_title` / `context_id`
2. Saved view: `view_id`
3. Platform + country
4. Funnel stage + query type
5. Tags

Show a table with:

```
| # | prompt_id | Prompt | Platform | Country | Context | Status |
|---|-----------|--------|----------|---------|---------|--------|
```

Keep prompt text to about 80 characters. Include exact `prompt_id` values in monospace.

## Step 5 - Ask for action

Ask what the user wants to do:

- Review only
- Untrack selected prompts
- Find new prompts to fill quota

If they choose "find new prompts", route to `/aeko-find-prompts-to-track`.

## Step 6 - Untrack selected prompts

When the user selects prompts to untrack:

1. Resolve row numbers to exact `prompt_id` values from the displayed table.
2. Echo the exact prompt IDs and first 80 characters of each prompt.
3. Ask for explicit confirmation.
4. After confirmation, call `aeko_untrack_prompt(prompt_id)` once per selected prompt.

Stop on backend 403/404 and surface the backend message.

## Step 7 - Summary

Print:

```
Untracked N prompt(s).

Still tracking: <count if known>
Remaining quota: <remaining if known>

Historical response and citation data is preserved.
```

If nothing changed, say so plainly.
