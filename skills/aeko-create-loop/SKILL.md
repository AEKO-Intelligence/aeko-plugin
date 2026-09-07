---
name: aeko-create-loop
description: >
  Interactive schedule composer for the weekly AEKO loop. Probes connection
  slots, interviews the user, writes a durable Notion config, composes the
  scheduled prompt, installs it through the host or gives exact UI steps, and
  foreground dry-runs it once. Never acts as the scheduled orchestrator.
argument-hint: "[cadence] [config=<notion-page-id>]"
allowed-tools: Read, Skill, ToolSearch
disallowed-tools: Write, Edit, Bash
---

# AEKO Create Loop

Before work, read [the brand execution contract](references/brand-execution-contract.md).
Preserve the exact task prompt and apply only this brand's selected rules, evals, and examples.

Set up the user's weekly loop. This skill is an interactive **schedule composer**, not an orchestrator: it
does not pull weekly sources, inspect approval threads, evaluate decisions, stage marketing changes, or run
the loop itself. `/aeko-run-loop` owns scheduled execution.

If invoked from a schedule, routine, cron wrapper, or any context without a present user, stop immediately:

```text
/aeko-create-loop is interactive only. Run it in a foreground conversation so connection, destination,
cadence, and dry-run decisions are visible.
```

Mirror the user's chat language. Keep config keys, provider names, IDs, timezones, commands, and the brand
mark `AEKO` in English/ASCII.

## Step 1 — probe what is connected

Invoke `/aeko-connect slot=all` and retain its capability receipt. Do not recreate connector resolution
here and do not identify connectors by hardcoded tool/server names. Classify:

- sources: public site/PDP, ads providers, official GA4, AEKO visibility/actions;
- durable destinations: Notion and Slack;
- decision input: Calendar;
- host scheduler: programmatic creation, UI-only scheduling, or prompt-only handoff.

Do not begin OAuth in the background. If a required slot is empty, show the exact `/aeko-connect` step and
let the user choose whether to connect it before continuing.

## Step 2 — interview the user

Ask in a short sequence and echo the final answers before writing anything:

1. What must the user know every week? Convert the answer to explicit report questions, not vague goals.
2. Which sources should be pulled? Capture exact site root, up to 10 PDP URLs, declared ad platforms, GA4
   source/property, and AEKO domain IDs. Keep an unavailable declared source in config so it renders a dash.
3. Where should the full report land: Notion, Slack summary, or both?
4. Who should be notified? For Slack, record exact channel and user IDs; do not infer approvers from names.
5. What cadence, local time, timezone, start date, and optional end date should apply?
6. What report language should be used? Keep slash commands and schema keys untranslated.
7. Which Calendar and blackout convention should be obeyed, or what standing quiet window should be used as
   the weaker fallback?

Do not collapse several unresolved choices into one assumed default. A cadence is not authorization for a
marketing write.

## Step 3 — durable destination gate

Before installing a cloud schedule, require a durable collaboration surface. If neither Notion nor Slack is
connected, refuse to arm it and say:

```text
I will not arm this cloud schedule because neither Notion nor Slack is connected. A scheduled run cannot
reach local files and has no durable place to put a report or approval. Connect one with /aeko-connect, or
use a local foreground run instead.
```

KO:

```text
Notion과 Slack이 모두 연결되어 있지 않아 이 cloud schedule을 활성화하지 않습니다. 예약 실행은
로컬 파일에 접근할 수 없고 보고서나 승인을 둘 영구 위치가 없습니다. /aeko-connect로 하나를
연결하거나 로컬 foreground 실행을 사용하세요.
```

This release stores the schedule definition in Notion, so Notion must be writable before installation.
Slack can be the notification/approval surface but does not replace the Notion config pointer. When Slack
is connected without Notion, give the Notion connection step and stop before schedule creation; do not hide
the config in a local file or in the scheduled prompt.

## Step 4 — write and verify the Notion config

Resolve an installed Notion connector skill by capability, then delegate creation of one page titled
`AEKO Loop Config — <brand or site>`. Do not call a Notion MCP tool directly from this composer when a
connector skill is available. Put a human-readable summary first and one fenced block below it:

```yaml
schema: aeko-loop-config/1
summary: <plain-language weekly job>
task_prompt: <original user job instructions verbatim; not just the summary>
report_questions: []
brand_package_ref: <selected identity and version/digest>
eval_package_refs: []
source_window: {kind: previous_complete_week, timezone: <IANA timezone>}
no_input_behavior: report_unavailable_without_marketing_writes
timezone: <IANA timezone>
cadence: <human-readable cadence>
language: <language code>
sources:
  site_roots: []
  pdp_urls: []
  ad_platforms: []
  ga4: {source: official, property_id: null}
  aeko_domain_ids: []
destinations:
  notion_page_id: <report parent/page id>
  slack_channel_id: null
  notify_user_ids: []
approval:
  approver_user_ids: []
  ttl_hours: 72
calendar:
  calendar_id: null
  blackout_convention: null
  standing_quiet_window: null
caps: {pdp_urls: 10, rows_per_kind: 50, source_bytes: 65536, tool_calls: 30, delivery_retries: 1}
```

Use exact IDs from connector receipts. After creation, delegate one readback and verify the schema, cadence,
timezone, sources, destinations, and page ID. A write receipt without successful readback is not a durable
config. Print the verified Notion page ID and URL.

The original prompt must survive the Notion readback and every child skill brief. Compare it
verbatim, separately from the summary. A package reference is not package loading: verify the
host can read the selected skill/eval bytes; if not, stop setup with that missing capability.
These config fields describe this plugin's host loop, not an AEKO hosted automation API.

Edits to sources, report questions, cadence, and language happen on this page. Security-sensitive fields are
different: the page is editable and has no cryptographic integrity proof, so approver IDs and delivery
destinations must also be frozen into the independently stored scheduled prompt. Changing those fields
requires recreating the schedule in a foreground run.

Individual approval thread addresses are dynamic and therefore are not frozen into the prompt. Require the
scheduled run to accept one only when an atomic proposal-creation receipt binds that exact address to its
proposal ID/hash inside the frozen Slack channel or Notion destination. The editable config is never enough
to introduce an approval thread.

## Step 5 — compose the scheduled prompt

Compose a short prompt with both a human-readable summary and the verified pointer:

```text
Run the AEKO weekly marketing loop for <brand/site>.
Task: <original user job instructions verbatim>.
Package/evals: <selected immutable versions/digests and required references>.
Source window: previous complete week in <timezone>, resolved at scheduled_at.
Cadence: <cadence in timezone>. Deliver to <destinations>. Report language: <language>.
AEKO_LOOP_SECURITY_V1
config_page_id: <exact verified Notion config page ID>
notion_destination_id: <exact ID or null>
slack_channel_id: <exact ID or null>
approver_user_ids: [<exact sorted immutable Slack user IDs>]
max_ttl_hours: 72
END_AEKO_LOOP_SECURITY_V1
Read the current configuration from Notion page <page-id> (<page-url>), then invoke:
/aeko-run-loop config=<page-id>
Do not use local files. The loop is read-and-propose only; scheduled marketing writes are unsupported.
```

The pointer is load-bearing for sources, blackout rules, report questions, and language, which change on the
next run without rebuilding the schedule. The fixed security envelope is load-bearing for destinations and
approver IDs. `/aeko-run-loop` compares the editable config with it and falls back to conversation-only when
it is absent or mismatched; never let config-only edits redirect delivery or grant approval authority.

## Step 6 — install honestly for this host

Inspect the host's live scheduling capabilities rather than assuming Claude-only tool names.

- **Programmatic scheduler:** show cadence, timezone, prompt, destination gate, and first-run time. Obtain
  explicit confirmation, then call the advertised schedule-create capability. Prefer a disabled/draft
  install when supported; otherwise choose a first fire safely after the foreground test. Record schedule ID,
  effective cadence, timezone, enabled state, and the exact prompt.
- **UI-only host (including Cowork/Desktop surfaces):** do not claim creation. Print the exact prompt and
  numbered steps using the host's currently advertised Schedule/Automation UI: create a task, paste the
  prompt unchanged, set cadence/timezone, select the connected account, and save after reviewing the dry run.
- **No scheduler on this host:** never dead-end and never create an OS cron through `Bash`. Give the exact
  prompt plus the steps to paste it into a supported host's scheduling UI, and offer the foreground command
  `/aeko-run-loop config=<page-id>` for manual cadence.

Host installation only schedules `/aeko-run-loop`; it never substitutes this composer as the entry point.

## Step 7 — foreground dry-run once

Before asking the user to trust or enable the schedule, invoke:

```text
/aeko-run-loop config=<page-id> dry_run=true delivery=conversation
```

Run it in the foreground so the user sees the real approval-read, calendar, source, degradation, assembly,
and delivery preview. A dry run cannot arm, publish, change spend, update a PDP, or persist a stage. Show the
actual output and every unavailable source.

If the dry run fails, keep a programmatically created schedule disabled when possible, or give the exact UI
pause/delete steps. Fix the config and rerun foreground before enablement. Only after a successful dry run
and explicit confirmation may a draft schedule be enabled or the user be told to save the UI schedule.

## What this skill never does

- Never runs unattended or acts as the weekly orchestrator.
- Never stores durable config in local files or inside the scheduled prompt.
- Never arms a cloud schedule without the durable destination gate and a successful foreground dry run.
- Never treats schedule creation as approval for a marketing write.
