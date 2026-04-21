---
name: aeko-action-center
description: >
  Top-level router for AEKO optimization work. Lists pending Action-tab
  and Technical-tab items for a domain, previews their plan/guide summary,
  and prints ready-to-copy commands that route the user to aeko-run-action
  or aeko-fix-technical. Pure dispatcher — never executes items itself.
argument-hint: "[domain-id] [tab]"
allowed-tools: aeko_list_action_items, aeko_list_technical_items, aeko_get_domain_info
---

# AEKO Action Center

Router for the Action + Technical Optimize tabs. You help the user pick one pending item and hand off to the correct executor skill. You do NOT generate artifacts, call write-back tools, or mark items complete.

Contract reference: `docs/contracts/action-item-contract.md`.

## Inputs

- `domain-id` (optional) — UUID of the domain. If missing, ask the user.
- `tab` (optional) — `action` | `technical` | `both` (default: `both`).

## Step 1 — Resolve the domain

Parse `$1` for a UUID. If absent:
- Ask the user to provide a domain UUID, OR
- Call `aeko_get_domain_info` with a guess if one is obvious from context.

Do not proceed without a concrete `domain_id`.

## Step 2 — Fetch pending items for the chosen tabs

Based on `$2`:
- `action` → call `aeko_list_action_items(domain_id, status="pending")`
- `technical` → call `aeko_list_technical_items(domain_id, status="pending")`
- `both` / unset → call both in parallel

Each summary (`AekoItemSummary` from the contract) carries: `id`, `tab`, `title`, `priority`, `execution_class`, `artifact_type`, `write_mode`, `preview`, `updated_at`.

If either backend endpoint is unavailable (stub error), report it plainly to the user and continue with whichever tab did return data. Do NOT fall back to any retired tool (`aeko_get_suggestions_v2`, `aeko_get_suggestions`, campaigns). Those no longer drive routing.

## Step 3 — Summarize

Print a short header:

```
Domain: <domain_id>
Action tab: N pending (top priority: <critical|high|medium|low>)
Technical tab: M pending (top priority: ...)
```

## Step 4 — Print ready-to-copy commands

For each tab with ≥1 pending item, group items by priority (critical → low) and print a fenced code block per item, highest-priority-first. Cap at 10 items per tab; if there are more, append a line noting how many are hidden.

Format for Action items:

````
# Action · <artifact_type> · <priority>
# <title>
# execution_class: <execution_class> | write_mode: <write_mode or "n/a"> | updated <relative time>
# preview: <first 120 chars of preview>
/aeko-run-action <item_id>
````

Format for Technical items:

````
# Technical · <artifact_type> · <priority>
# <title>
# execution_class: technical_artifact | updated <relative time>
# preview: <first 120 chars of preview>
/aeko-fix-technical <item_id>
````

Note: `deploy_mode` is only available inside the full guide.md frontmatter (fetched by `aeko-fix-technical`), not in `AekoItemSummary`. The router does not render it. If the user wants to know whether a Technical item auto-deploys, they'll see it after invoking `/aeko-fix-technical <item_id>`.

After printing, ask which one the user wants to tackle. They copy the command block and run it themselves.

## Step 5 — If asked to "run them all"

Refuse: tell the user to run each executor one item at a time so they can review the output between runs. Writes to the store and content artifacts should not batch.

## Error paths

- `domain_id` missing → ask for it; stop.
- Both list endpoints unavailable → surface both error messages; tell the user the new Action/Technical surface isn't backing yet; stop.
- Zero pending items → congratulate the user; suggest checking the Brand Kit (`/aeko-brand-kit <domain_id>`) or running a domain-wide report (`/create-visibility-report <domain_id>`).

## What this skill never does

- Never calls `aeko_get_action_plan` / `aeko_get_technical_guide` — those belong to the executor skills.
- Never calls `aeko_complete_action_item`, `aeko_create_shadow_product`, or any write-back tool.
- Never executes the item. Always stops at routing.
