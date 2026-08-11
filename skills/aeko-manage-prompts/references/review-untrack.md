# Review, organize, and untrack prompts

Use this when the user wants to review, organize, or stop tracking prompts already in AEKO.

Language: mirror the user's chat language for user-facing explanations, confirmations, and summaries. Keep tool names, IDs, and schema keys in English/ASCII.

## Safety

- Never untrack a prompt without explicit user confirmation.
- Never infer prompt IDs from prose when the user gave ambiguous labels. Show the list again and ask for exact IDs or row numbers.
- Untracking preserves historical responses and citations; it only stops future refreshes.
- Discovery and new tracking use `/aeko-manage-prompts mode=discover`; never carry its permissive selection
  into this mode's destructive gate.

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
- Create a saved view or add existing prompts to one

If they choose "find new prompts", route to `/aeko-manage-prompts mode=discover`.

### Saved-view operations

- To create a view, collect `name` plus optional `product_label`, `description`, `scope`, and exact existing
  `prompt_ids`. Show the proposed grouping and confirm before
  `aeko_create_view(domain_id, name, product_label, description, scope, prompt_ids)`.
- To add prompts to an existing view, resolve a real ID from `aeko_list_views`, echo the exact prompt IDs,
  confirm the non-destructive organization change, then call
  `aeko_add_prompts_to_view(view_id, prompt_ids)`. An empty list is not a write.

## Step 6 - Untrack selected prompts

When the user selects prompts to untrack:

1. Resolve row numbers to exact `prompt_id` values from the displayed table.
2. Echo the exact prompt IDs and first 80 characters of each prompt.
3. Require the user to type `UNTRACK <N>` exactly, where `<N>` is the displayed number of prompts. Do not
   accept yes, approval of the displayed list, or any confirmation from discovery/view operations.
4. Only after the exact typed confirmation, call `aeko_untrack_prompt(prompt_id)` once per selected prompt.

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
