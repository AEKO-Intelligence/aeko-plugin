# Whole-job automation prompts

These are editable setup examples, not installed schedules or runnable API payloads. Fill
every placeholder before enabling a job. The saved prompt is additional to the attached
brand skill/evals. Keep it verbatim across handoffs; resolve resource IDs and permissions
during setup. Each host authenticates separately. The plugin does not implement AEKO's
multi-stage hosted agent runner, automatic updater, or GitHub synchronization.

## Daily review-grounded ad proposals

Status: foreground draft/preview with `/aeko-openai-compose-ads` is available when its AEKO
tools/account gates pass. Hosted daily selection and unattended upload via this skill are
unavailable. Its contextual-review MCP tool has no date filter or pagination; do not present
this example as an installed last-24-hours workflow.

```text
Every day at <time> in <IANA timezone>, prepare review-grounded OpenAI Ads for
brand <brand name>, owned domain <domain_id>, market <market>, language <language>.
Task: <the customer's purpose, audience, creative direction, and required deliverables>.
Use only contexts created during [scheduled_at - 24 hours, scheduled_at), recording both
timestamps. Require authoritative created_at values; if that selector is unavailable, stop
with source_window_unavailable. Do not substitute older high-score reviews.
Attach the active brand version of /aeko-openai-compose-ads and these required evals:
<exact eval package IDs/paths and versions>. Apply its default recipe unless the task or
explicit brand rules specify otherwise; preserve all standing brand constraints.
Select at most 30 contexts and 10 distinct products; read at most 64 KiB of source text,
make at most 20 tool calls, use at most one correction attempt per output, and stop at
<configured model token/spend ceiling>. Record skipped and truncated counts.
Produce at most three groups with exact titles, bodies, source IDs, and context hints.
Destination: proposal report <authorized destination ID>. Intended later upload target:
<authorized OpenAI account ID>/<ad_group_id>, PAUSED; unattended upload is unavailable
in this plugin. Never redirect to Meta, TikTok, or Google Ads or infer a target by name.
Run all applicable brand evals on the exact creative. Missing, failed, or unavailable
required checks prevent delivery as accepted creative. If there are no eligible inputs,
return no_eligible_inputs with the window and counts, and create no ad structures.
Finish with package versions, evaluated output, limitations, and actual delivery receipts.
```

## Weekly content draft

Status: foreground content-idea selection and direct handoff drafting are available when
the live wrappers/account permit them. Hosted content-draft automation is coming soon;
the plugin does not install that hosted job or publish the handoff.

```text
Each <weekday/time> in <IANA timezone>, prepare one <channel slug> draft for
brand <brand name>, domain <domain_id>, market <market>, language <language>.
Task: <campaign question, intended audience, desired reader outcome, and format>.
Use /aeko-content-ideas window=7d for at most 12 ideas (one page), recording snapshot_at
and the actual seven-day source window. Do not broaden to 30d/all when nothing qualifies.
Select one explicitly configured eligible idea, then retain its exact fingerprint/handoff
and frozen evidence snapshot. Use the brand version of /aeko-create-content with required
eval packages <IDs/paths and versions> and at most three matching brand examples.
Keep task_prompt, brand rules, source window, snapshot channel/action, and evals in the
drafting brief. A conflicting task/channel is a needs_review result, not an implicit rewrite.
Limits: one draft, five products, five reviews per product, 64 KiB of source text, 20 tool
calls, one correction attempt, and <configured model token/spend ceiling>.
Destination: draft artifact <exact local path for foreground use or authorized hosted
destination ID when supported>. Direct handoff mode does not save/publish through AEKO.
Check claims, brand rules, and channel formatting before marking the draft accepted.
If the queue/evidence is empty, return no_eligible_inputs and the missing evidence; create
no synthetic reviews, generic substitute idea, saved variation, or published post.
```

## Weekly marketing report on a capable host

Status: `/aeko-create-loop` can compose this read-and-propose job for a host's advertised
scheduler after its foreground test. Delivery needs the declared connectors; the current
loop config is stored in Notion. This does not install an AEKO hosted agent job.

```text
Run /aeko-run-loop config=<verified Notion config page ID> for brand <brand name>,
domain <domain_id>, using the brand package <version/digest> and report evals <IDs/paths>.
Task: <the exact marketing questions this report must answer>.
Window: previous complete Monday–Sunday in <IANA timezone>, resolved at scheduled_at;
retain exact start/end timestamps and source fetch times on all results.
Read only the configured platforms, GA4 property, domains and up to 10 PDP URLs.
Limits: 50 rows per kind, 64 KiB selected source text, 30 tool calls, no marketing writes,
one delivery retry, and <configured model token/spend ceiling>.
Deliver to <exact Notion destination ID> and optional <exact Slack channel ID> only when
they match the AEKO_LOOP_SECURITY_V1 envelope produced by /aeko-create-loop.
Preserve that complete envelope verbatim here: <verified envelope from the composer>.
Apply the selected evals to the report and preserve provider/window comparability.
No input: render unavailable rows and a short reason; never turn absence into zero.
If the package, envelope, or destination cannot be verified, render conversation-only
without claiming external delivery, approval, or scheduled marketing execution.
```
