---
name: aeko-connect
description: >
  Interactive, zero-account connection board for AEKO, ads, analytics, store,
  docs/Notion, chat/Slack, and calendar capabilities. Shows which slots are
  filled, what each empty slot unlocks, and exact host-appropriate connection
  steps. Use when a marketer asks to connect tools or diagnose missing access.
argument-hint: "[slot=all|aeko|ads|analytics|store|docs|chat|calendar]"
allowed-tools: ToolSearch
disallowed-tools: Write, Edit, Bash
---

# AEKO Connect

Show the user what is connected and how to fill each missing capability slot. This skill is interactive
only and completes without an AEKO account. If invoked by a schedule, routine, or unattended wrapper, stop
and ask the user to run `/aeko-connect` in a foreground conversation where authorization prompts are visible.

## User-facing language

Mirror the user's chat language. Use `filled / 연결됨`, `partial / 일부 연결`, `expired / 만료됨`,
`empty / 비어 있음`, and `ambiguous / 확인 필요` as the stable meanings. Keep slot keys, provider names,
URLs, account IDs, commands, and tool names in English/ASCII. The brand mark is always `AEKO`.

## Step 1 — resolve capabilities, never names

Inspect the live tool and connector registry, including input/output schemas, read/write annotations,
provider identity metadata, authorization state, account identity, transport, expiry, and reauthorization
metadata. Resolve a slot by **capability detection**, never by equality, prefix, substring, or regular-
expression matching against a tool name or MCP server name. The server segment in
`mcp__<server>__<tool>` varies by installation and is not provider identity.

Do not invoke a mutation or begin an OAuth flow while probing. A read-only identity/status operation is
allowed only when the registry identifies its provider and schema unambiguously. Treat an unavailable tool
as different from a known expired authorization. When two connectors satisfy the same slot, show both
account identities and mark the slot `ambiguous` until the user chooses.

Capability evidence for each slot:

| Slot | Filled when the live registry proves | Empty slot unlocks |
|---|---|---|
| `aeko` | authenticated AEKO read capabilities are exposed; do not call a domain/account tool just to test | AI-answer history, tracked evidence, Action items, the OpenAI Ads row/depth report, and guarded AEKO store/OpenAI Ads writes |
| `ads` | an official Meta, Google Ads, or TikTok reporting connector exposes authenticated date-ranged reads; list each provider separately | the three free vendor rows in `/aeko-ads-review`; AEKO supplies the separate OpenAI Ads row |
| `analytics` | an official GA4 property-reporting connector is authorized, or the optional AEKO GA4 rung is explicitly connected | traffic, ecommerce impact, and `/aeko-ga4` rows |
| `store` | an official commerce/store connector is authorized, or the optional AEKO store integration is explicitly present | product grounding, review attachment, and confirmed store workflows |
| `docs` | an authorized Notion connector can read and create/update pages | durable `/aeko-weekly-report` delivery, `/aeko-create-loop` config, review state, and approvals |
| `chat` | an authorized Slack connector can read threads and post to the selected internal channel | weekly delivery, notifications, and exact-ID approval threads for `/aeko-run-loop` |
| `calendar` | an authorized calendar connector can list/search events over explicit dates | due-decision checks and blackout/freeze windows for `/aeko-run-loop` |

A generic browser, scraper, web search, warehouse, similarly named custom server, or write-only tool does
not fill a slot. Never treat provider-looking words inside a tool name as evidence.

## Step 2 — print the slot board

Render every slot even when empty:

```text
# AEKO Connection Board

| Slot | State | Account/provider | Capability evidence | What it unlocks | Next step |
|---|---|---|---|---|---|
| AEKO | ... | ... | ... | ... | ... |
| Ads | ... | ... | ... | ... | ... |
| Analytics | ... | ... | ... | ... | ... |
| Store | ... | ... | ... | ... | ... |
| Docs / Notion | ... | ... | ... | ... | ... |
| Chat / Slack | ... | ... | ... | ... | ... |
| Calendar | ... | ... | ... | ... | ... |
```

For every filled row, include the provider/account identity, authorization state, and the capability
evidence used. For every empty, expired, partial, or ambiguous row, include a reason and one exact next step.
Absence is never printed as `0` and an expired authorization is never labeled never connected.

## Step 3 — exact fill steps

Use the host's live connector metadata and current UI/CLI affordances to name the actual settings path,
provider entry, authorization URL, or command. Never invent a command or stale UI label. If the host exposes
no machine-readable setup path, print this numbered fallback with the provider and account substituted:

1. Open this host's **Connectors / Integrations** settings.
2. Select the exact provider shown in the empty slot.
3. Authorize the intended account and approve read scopes needed for that slot.
4. Return to this conversation and rerun `/aeko-connect slot=<slot>`.

Provider-specific requirements:

- `aeko`: connect the HTTP MCP endpoint `https://aeko-intelligence.com/mcp` through the host's connector
  flow and complete its OAuth step. This is optional; never gate the other slots on it.
- `ads`: connect the customer's own official Meta, Google Ads, or TikTok connector. These connectors belong
  to the customer and do not require an AEKO account. Name each missing provider separately.
- `analytics`: connect the customer's own official GA4 connector for the free path. Offer the account-gated
  AEKO GA4 rung only as a separate choice through `/aeko-ga4 source=aeko`.
- `store`: use the host's official commerce connector when present, or offer `/aeko-store mode=setup` as the
  separate AEKO-account path. Do not claim the slot is free merely because the board itself is free.
- `docs`, `chat`, `calendar`: authorize Notion, Slack, or Calendar in the host. For Slack, require an internal
  channel that the connector can post to; do not represent an externally shared Slack Connect channel as a
  verified approval destination unless a live post/readback proves it.

## Dashboard-only boundary

Say this plainly in every run, even when all slots are filled:

```text
This skill cannot connect review-platform credentials or AEKO OpenAI Ads account tokens. cre.ma,
Judge.me, Cafe24 review credentials, ad-account tokens, pixel IDs, and conversions API tokens are
dashboard-only; no skill can complete those credential flows.
```

KO:

```text
이 스킬은 리뷰 플랫폼 자격 증명이나 AEKO OpenAI Ads 계정 토큰을 연결할 수 없습니다. cre.ma,
Judge.me, Cafe24 리뷰 자격 증명, 광고 계정 토큰, pixel ID, conversions API token은 대시보드
전용이며 어떤 스킬도 이 자격 증명 연결을 완료할 수 없습니다.
```

Do not offer a workaround that asks the user to paste a token into chat.

## Close

Recommend at most one next action, based on the user's stated goal. A full board is a status report, not
permission to invoke another skill or mutate a connector.

## What this skill never does

- Never checks for, creates, or gates on an AEKO account.
- Never resolves a connector from a hardcoded tool or server-name match.
- Never mutates connector state, stores credentials, starts an unattended OAuth flow, or pastes secrets.
- Never claims that review-platform credentials or ad-account tokens can be completed by a skill.
