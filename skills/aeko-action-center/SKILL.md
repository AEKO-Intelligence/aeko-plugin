---
name: aeko-action-center
description: >
  Top-level router for AEKO optimization work. Lists pending items for a
  domain grouped into three categories (Technical / PDP update / Content
  generation) and prints ready-to-copy commands that route the user to
  `/aeko-fix-technical`, `/aeko-update-pdp`, or `/aeko-create-content`.
  Pure dispatcher — never executes items itself.
argument-hint: "[domain-id] [category]"
allowed-tools: aeko_list_action_items, aeko_list_technical_items, aeko_get_domain_info, aeko_list_domains
---

# AEKO Action Center

Router for three execution categories: **Technical fixes**, **상품 페이지 개선 (PDP update)**, and **Content generation**. You help the user pick one pending item and hand off to the correct executor skill. You do NOT generate artifacts, call write-back tools, or mark items complete.

Contract reference: `docs/contracts/action-item-contract.md`.

## Inputs

- `domain-id` (optional) — UUID of the domain. If missing, ask the user (or call `aeko_list_domains` to offer a pick-list).
- `category` (optional) — `technical` | `pdp` | `content` | `all` (default: `all`).

## Step 1 — Resolve the domain

Parse `$1` for a UUID. If absent:
- Call `aeko_list_domains` to show the user's connected domains and offer a pick-list, OR
- Call `aeko_get_domain_info` with a guess if one is obvious from context.

Do not proceed without a concrete `domain_id`.

## Step 2 — Fetch pending items

Call the two list endpoints in parallel (fast, independent):
- `aeko_list_action_items(domain_id, status="pending,ready")` → returns items with `tab="action"`.
- `aeko_list_technical_items(domain_id, status="pending,ready")` → returns items with `tab="technical"`.

Each summary (`AekoItemSummary`) carries: `id`, `tab`, `title`, `priority`, `execution_class`, `artifact_type`, `write_mode`, `preview`, `updated_at`, `target_url`, `product_id`.

If either endpoint errors, report it plainly and continue with whichever returned data. Do NOT fall back to retired tools (`aeko_get_suggestions_v2`, `aeko_get_suggestions`, campaigns). Those are deleted in v0.5.0 — any reference means stale skill code.

## Step 3 — Categorize by execution_class

Group the combined item list into three buckets:

| Category | Filter | Executor |
|---|---|---|
| **Technical** (기술 수정) | `execution_class == "technical_artifact"` | `/aeko-fix-technical <item_id>` |
| **PDP update** (상품 페이지 개선) | `execution_class == "store_write_artifact"` | `/aeko-update-pdp <item_id>` |
| **Content generation** (콘텐츠 생성) | `execution_class == "local_content_artifact"` | `/aeko-create-content <item_id>` |

If `$2` (category arg) is set to `technical` / `pdp` / `content`, filter to only that bucket. `all` or unset → show all three.

## Step 4 — Print a header

```
Domain: <domain_id>
Technical: N pending (top priority: <critical|high|medium|low>)
PDP update: M pending (top priority: ...)
Content: K pending (top priority: ...)
```

## Step 5 — Print ready-to-copy commands

For each category with ≥1 pending item, group items by priority (critical → low) and print a fenced code block per item, highest-priority-first. Cap at 10 items per category; if there are more, append a line noting how many are hidden.

**Technical items:**

````
# Technical · <artifact_type> · <priority>
# <title>
# updated <relative time>
# preview: <first 120 chars of preview>
/aeko-fix-technical <item_id>
````

**PDP update items:**

````
# PDP · <artifact_type> · <priority>
# <title>
# write_mode: <write_mode> · updated <relative time>
# target: <target_url or product_id>
# preview: <first 120 chars of preview>
/aeko-update-pdp <item_id>
````

**Content generation items:**

````
# Content · <artifact_type> · <priority>
# <title>
# updated <relative time>
# preview: <first 120 chars of preview>
/aeko-create-content <item_id>
````

After printing, ask which one the user wants to tackle. They copy the command block and run it themselves.

## Step 6 — If asked to "run them all"

Refuse: tell the user to run each executor one item at a time so they can review the output between runs. Writes to the store and content artifacts should not batch.

## Error paths

- `domain_id` missing AND `aeko_list_domains` returns zero → tell the user to add a domain in the AEKO dashboard first; stop.
- Both list endpoints unavailable → surface both error messages; suggest the user re-check backend deploy; stop.
- Zero pending items across all three categories → congratulate the user; suggest checking the Brand Kit (`/aeko-brand-kit <domain_id>`) or running `/aeko-visibility-report <domain_id>`.

## What this skill never does

- Never calls `aeko_get_action_plan` — that belongs to the executor skills.
- Never calls `aeko_complete_action_item` or any write-back tool.
- Never executes the item. Always stops at routing.
- Never displays `execution_class` raw to the user — always translate to the category label (Technical / PDP update / Content generation).
