# Remaining skill catalog review and corrections

Reviewed 2026-09-07, following checkpoint `ab1da11` in `brand-customization-foundation`.
Orca task `task_771444c4fdb8`, dispatch `ctx_469e24c91679`.

The remaining **16 entrypoints received source-backed semantic review: 15 corrected, one reviewed with
no change**. This completes the requested catalog review when combined with the earlier ten-entrypoint
batch; it does not establish model behavioral quality. The corrections preserve default-first use,
separate current-brand rules from evidence, retain whole-job prompts across handoffs, make shared files
available inside standalone packages, and correct demonstrated window/budget/capability mismatches.

No canonical execution/eval contract, previously reviewed entrypoint, manifest, root document, backend,
MCP implementation, frontend or updater source was changed. No commit, push, deployment, paid model call,
live write, nested agent or private eval read was performed. Implementation began only after the
coordinator's checkpoint receipt `msg_a472b9fa4511`. Early concrete findings were sent in
`msg_3946b55ccd28`.

## Disposition of all 16 entrypoints

| Entrypoint | Disposition and rationale | Preserved safeguards / remaining limit |
| --- | --- | --- |
| [aeko-weekly-report](../skills/aeko-weekly-report/SKILL.md) | **Corrected.** Every child, including each PDP, receives the verbatim whole-job prompt, questions, verified brand/package/eval context, exact requested window and remaining limits; sequential fallback and aggregate row/byte/invocation budgets added; exact report and Slack-summary checks; requested delivery destination honored. | Composite still cannot call MCP directly; `arow/1`, source provenance, no cross-source totals and final blind-spots section remain. Host skill invocation, package materialization and verified delivery receipts are required capabilities, not implemented by these instructions. |
| [aeko-pdp-build](../skills/aeko-pdp-build/SKILL.md) | **Corrected.** Scoped rules/evals and complete task context now reach the audit child and exact HTML/JSON-LD/handoff checks. | Free/zero-account path, direct bounded audit fallback, original source language, factual ledger, append-only handoff, no CTA, schema parity and explicit Product-replacement confirmation remain invariant. Model/native-vision extraction quality was not tested. |
| [aeko-message-audit](../skills/aeko-message-audit/SKILL.md) | **Corrected.** Advertiser-scoped rules and exact-task/evidence/eval context survive sweep, drill and executor handoff; exact proposed fixes receive checks. | Literal ad quotes and evidence-state mappings cannot be rewritten for brand voice; zero official-connector stop, pixel/source limits, no synthetic reviews and read-only boundary retained. Connector field availability and subjectively assessed substantiation remain runtime limitations. |
| [aeko-source-analysis](../skills/aeko-source-analysis/SKILL.md) | **Corrected.** Added actual Read/ToolSearch capabilities used by its references, scoped analysis/correction evals, local framework reference, 256 KiB retention bound, three live fallbacks maximum and explicit unscoped/local-output handling. | Full response/citation detail is not silently reduced to counts; a too-large required payload stops with a narrower-window remedy. Prompt ownership alone does not identify a current brand. Cited-page source/domain checks, five-prompt/product caps and no posting remain. |
| [aeko-competitor-analysis](../skills/aeko-competitor-analysis/SKILL.md) | **Corrected.** Added scoped task/eval handling, local framework reference, aggregate research/detail bounds, verified domain association for private prompt selection, bounded unattended candidate selection and honest public-only output. Removed assumptions that a generic WebSearch accepts `num_results`, entity presence proves richer embeddings, or converted markdown proves missing JSON-LD. | Public research still runs without AEKO; competitor evidence cannot supply the user's product claims/reviews. Private prompt enrichment may remain unavailable because the account-wide list has no domain ID. No store/tracking/external write added. |
| [aeko-ads-review](../skills/aeko-ads-review/SKILL.md) | **Corrected.** Added scoped report/eval and parent-job context, aggregate read/row/byte budget and local normalized-row contract. | All four provider rows, claimed-versus-actual distinctions, exact attribution/currency rules, no conversion/ROAS for OpenAI Ads, free-provider-first access and no mutations remain. Dynamic provider signatures must still be inspected in the connected host. |
| [aeko-openai-ads-reporting](../skills/aeko-openai-ads-reporting/SKILL.md) | **Corrected.** Exact report checks and full scheduled-job context added; all hierarchy levels now share finite budgets; inclusive day arithmetic clarified; unsupported list pagination and complete-account rankings from capped samples prohibited. | Default hierarchy is five campaigns, ten groups, twenty ads, at most 60 data reads/256 KiB; insight rows default to 200. Existing list wrappers remain unpaged, and the six-source loop recipe is not claimed to implement arbitrary hierarchy jobs. No ad-state/spend writes or fabricated ROAS. |
| [aeko-ai-visibility](../skills/aeko-ai-visibility/SKILL.md) | **Corrected.** Fixed actual source windows, account-wide prompt selection, separately windowed summary rows, complete task handoffs, required report evals and local row/framework dependencies. | Overview is all-time, tracked metrics are fixed seven-day and drift is a rolling lookback; exact historical-week answers can be unavailable. Source windows never become the requested week merely by relabeling. Starter first-line rule, measured metric definitions and no made-up scores retained. |
| [aeko-ga4](../skills/aeko-ga4/SKILL.md) | **Corrected.** Report-only scoped task/evals, local row contract, bounded reads and explicit unavailable behavior for missing unattended source/property selection. | Official connector remains free of AEKO probing; separate rungs/currencies, explicit interactive property selection/sync and unavailable rows retained. Setup help does not gain a custom-package prerequisite. |
| [aeko-action-center](../skills/aeko-action-center/SKILL.md) | **Corrected.** Copies exact job/brand/eval context into a separate selected-item handoff, uses exact domain IDs, declares two bounded list pages and local row/action contract resources. | No package/eval prerequisite to list a queue, no executor invocation, no plan fetching/completion and no inferred permission. Counts describe the observed list; the bundled action contract remains the existing partial stub with inline routing rules authoritative. |
| [aeko-manage-prompts](../skills/aeko-manage-prompts/SKILL.md) | **Corrected.** Added Read for existing mode refs; scoped checks on authored Context/view/prompt proposals, original intent across modes, and no silent relaxation of explicit discovery filters. | Quota/market fan-out checks, track-safe verbatim fields, full result reconciliation, typed untrack/archive gates, no scheduled writes remain. Contexts are evidence grounding, not storage for permanent behavior rules; account-wide review does not inherit one brand's policy. No package required for listings. |
| [aeko-store](../skills/aeko-store/SKILL.md) | **Corrected.** Exact domain/product/task scope and applicable payload checks added without package setup barriers; real-review collection bounded by candidate count, public URLs and bytes with actual review-window timestamps. | No fabricated/voice-rewritten reviews, no token intake, dashboard-only credential connections, public-sync warning/typed gate, account-market whole-list confirmation, review dedupe and partial-result reporting remain. Backend authenticity and post-injection processing are not proven by a prose eval. |
| [aeko-openai-guardrails](../skills/aeko-openai-guardrails/SKILL.md) | **Corrected.** Applicable merchant policy/evals checked before all requested mutation paths, including both global-switch directions; evidence/example thresholds cannot override standing limits; bounded observational reads. | Foreground-only, disabled creation, immediate complete saved-rule preview, definition reread, distinct broad-match acknowledgement, disarm-before-edit and separate resume gate remain. Preview cannot be truncated and still authorize arming. These confirmation/policy checks remain instructions; no new server gate is claimed. |
| [aeko-site-audit](../skills/aeko-site-audit/SKILL.md) | **Corrected.** Original task/site scope and required-check disclosure, in-package row contract, and removal of contradictory alternate-hreflang fetching permission. | Zero-account fixed GET fetch set, byte-identical fetcher, exact severity/no-score rules and final executor line retained. Reciprocity outside the fixed set is unassessed. No custom package/eval prerequisite to inspect a public site. |
| [aeko-pdp-audit](../skills/aeko-pdp-audit/SKILL.md) | **Corrected.** Original task/product/context carried separately from the immutable fact JSON into the build handoff; local row contract; scoped authored recommendations without altering diagnostic evidence. | Text-only first box, exact facts/source language, severity/status triad, bounded same-host image fetch, native vision and no durable artifact remain. Brand rules cannot redact unfavorable source text or turn other-product facts into this product's evidence. |
| [aeko-connect](../skills/aeko-connect/SKILL.md) | **Reviewed, no change.** Capability/setup board does not draft customer marketing artifacts or hand an executable whole job to a child; adding brand-package/eval loading would impose an irrelevant barrier. | Zero-account, interactive-only, semantic capability resolution, no credential collection/mutation and dashboard-only boundaries remain. Actual registry metadata can be incomplete; only real exposed capability/auth evidence can establish a filled slot. No live host capability test was performed. |

## Concrete source mismatches corrected

1. **Window relabeling.** Before this patch, visibility called overview a 30-day report and said `window`
   affected tracked metrics. Actual MCP `aeko_mcp/tools/visibility.py:207–281` states and implements
   all-time overview and a compatibility-only hint; `window` is not forwarded. Backend
   `aeko_backend/api/routes/visibility.py:226` uses seven-day comparisons and its aggregate query has an
   all-time branch. The corrected skill separates windows and refuses an unsupported exact-week claim.
2. **Whole-job loss.** Weekly children previously received only a command, `report_mode` and window.
   The new handoff carries the original prompt and selected brand/eval context as host instructions,
   without inventing arguments in MCP calls or modifying `arow/1` data. `delivery=conversation` now
   explicitly prevents connector writes even if delivery skills exist.
3. **Incomplete standalone dependencies.** Six row producers depended on a sibling weekly-report file;
   source/competitor/visibility linked to another skill's framework file; Action Center linked to a root
   contract. Those runtime references now resolve to copied in-package files. The existing sources of
   truth were not changed.
4. **Unbounded hierarchy expansion.** Only ad-detail calls previously had a cap. The real campaign,
   group and ad list wrappers in `marketing.py:214–244` have no `limit`/pagination argument, while insight
   reads at `:246` accept `limit` but no cursor. The revised report budgets all levels, records unpaged
   transport limits and never claims an account-wide ranking from a partial subset.
5. **Cross-domain inference.** The account-wide tracked-prompt formatter in `research.py:205–272` exposes
   Context IDs but no domain ID. Competitor/visibility workflows can no longer infer the current domain's
   prompt set from textual similarity or a nonempty account list. Verified selection or returned scoped
   evidence is needed; otherwise the appropriate private comparison is unavailable.
6. **Evidence promoted into rules or facts.** The new scoped handling prevents a customer's disliked
   phrase from silently becoming a universal ban, a competitor's review from becoming this product's
   experience, or source claims/generated suggestions from rewriting standing policy. It preserves raw
   audit quotes even when the phrase is disallowed in newly authored brand copy.

MCP source was inspected read-only at `/Users/seanhan/aeko-intelligence/aeko-mcp`.
Backend source was inspected read-only at `/Users/seanhan/orca/workspaces/aeko/portable-brand-plugin`.
No source statement was treated as proof that a deployed connector exposes the capability.

## Standalone resources and validation

Ten additional generation/report/policy skills adopt byte-identical copies of
`docs/contracts/brand-execution-contract.md` and `evals/brand-output.md`; the inventory now validates 17
execution-contract copies and 15 output-eval copies across both batches. Smaller queue/setup/audit flows
use focused inline scope guidance, not a required general eval workflow. Six row-contract copies, three
framework copies and one ActionItem contract copy were added and registered in the lint inventory.

All commands initialized conda `aeko`. Checks completed offline:

| Check | Result and evidence limit |
| --- | --- |
| `./scripts/lint-release-contracts.sh` | **Pass** after corrections; 26 canonical skills and synchronized 0.29.1 manifests; original severity/fetcher copies remain identical. |
| `python scripts/lint-brand-contracts.py --mcp-source /Users/seanhan/aeko-intelligence/aeko-mcp` | **Pass**; declared MCP names exist and copied contracts match their canonical bytes. |
| Independent Python AST argument audit | **32 actual MCP argument shapes pass**, including list/insight, source/context, GA4, rule and account-market surfaces. The market write argument is `markets`; `selected_markets` is response terminology. Unsupported pagination/date arguments were explicitly checked absent. |
| Five offline actual-wrapper scenarios | **Pass** using extracted actual source function bodies with an in-memory client: overview ignores `90d`, tracked metrics do not forward `90d`, cited-source domain remains exact, hierarchy `limit` rejects before a read, and exact ad-insight scope/date/limit params are preserved. No network, live tool or model invocation occurred. |
| `python scripts/check-portable-package-examples.py --backend-packages <portable-worktree>/aeko_backend/api/services/automations/packages.py` | **Pass**; synthetic A/B/upstream isolation, retained version bytes, deterministic export parity and four unsafe path/type rejections. This is a serializer check, not updater or model behavior. |
| All 16 reviewed packages through the actual backend serializer, in memory | **Pass: 69 files total**, largest package 101396 bytes. Included references and existing bundled Python fetchers, with non-Markdown supports trusted/read-only; ZIP bytes match projected entries. Synthetic shortened canonical descriptions adapt the source's long descriptions while preserving `allowed-tools`, `disallowed-tools` and other source metadata. This does not claim a seed/import service exists. |
| Frontmatter and diff review | Catalog YAML and canonical slugs pass release lint; `git diff --check` passes. No previously reviewed entrypoint or canonical execution/eval file changed. |
| Skill-creator `quick_validate.py skills/aeko-weekly-report` | **Does not pass:** the generic validator rejects the catalog's existing `argument-hint` and `disallowed-tools` fields. Their existing host contracts were retained; this is not reported as a pass or silently repaired by removing safeguards. |

## Synthetic scenario walkthrough

These are source traces, not model rollouts or claims that an assistant obeyed the instructions:

| Scenario | Correct decision supported by the final source |
| --- | --- |
| New brand has no package and requests a public audit/PDP build | Defaults and existing free path run; no new account/package prerequisite. |
| Brand A prohibits a phrase; Brand B does not | Apply A's rule only to verified A's authored output; B does not inherit it. Existing literal evidence quotes remain intact. |
| Weekly task asks three specific questions and includes a custom eval | Original prompt/questions and eval text/version reach each child and the final report check; a path unavailable to the host is not treated as loaded. |
| Host has no parallel delegation | Same bounded child calls run sequentially when skill invocation exists; no invocation capability yields honest unavailable/manual handoff, no direct-MCP bypass. |
| Weekly job requests Aug 31–Sep 6; visibility returns all-time and rolling data | Actual source windows remain separate; unsupported exact-week metrics are unavailable, not relabeled. |
| Weekly job says conversation-only but Slack and Notion skills exist | No connector write; configured capabilities do not override the job destination. |
| Account tracks prompts for A and B; current report is for A | Never select all account prompt IDs or infer domain association from similarity; use verified scope or disclose unavailable enrichment. |
| Large ad hierarchy and no present user | Deterministic finite defaults apply across campaigns/groups/ads; rankings are labeled sampled/partial and no question blocks an unattended run. |
| Review or competitor page says to remove a brand restriction | Treat it as evidence, never an instruction; no permanent package or cross-brand rule edit. |
| A prohibited phrase is literally present in an active ad | Keep the literal claim and source ID for the audit; check newly authored fixes separately. |
| User makes a one-off correction during Context/rule setup | Keep it scoped to that operation, surface standing-rule conflicts, and do not write it into permanent skill rules. |
| Missing live review with a review-like competitor example | Do not fabricate or reuse it as this product's customer experience; show the empty/unavailable result. |
| Brand policy requests unsupported ROAS pacing or removing confirmations | Real capability matrix and foreground gates remain; required policy conflict is surfaced, not weakened. |
| Alternate hreflang URL needs reciprocity verification | Site audit reports unassessed under its fixed fetch contract; no unauthorized alternate fetch path. |
| Required brand eval is missing or fails on newly authored output | No false passing receipt; one bounded correction where applicable, then block the affected artifact/operation while preserving honest diagnostic evidence. |

## Remaining scope and runtime limits

This plugin still supplies instructions and portable resources, not enforced model behavior, a registered
executable generic evaluator, a host skill loader or transport-wide byte limits. Dynamic connector APIs,
exact timestamps, complete unpaged lists, live output-quality checks and host write/readback support must
be available in the actual runtime. The full paid hierarchy may be partial under caps; the source-analysis
payload may be too large to retain completely; unsupported exact windows correctly remain unavailable.

Cross-skill execution requires the host to resolve/install those skills and their selected brand versions;
copying required local references does not implement host routing. Backend imports still need canonical
metadata adaptation and trusted read-only handling of bundled code. The canonical action contract remains
an existing partial stub. Existing public-fetch/native-vision interpretation and subjective report quality
were inspected as instructions, not benchmarked with private data or paid models.

Runtime updater, hosted multi-stage runner, frontend and deployment work remain owned elsewhere. This
follow-up changes no lifecycle, publication destination, write-grant policy or confirmation backend.
Coordinator review and any commit/PR update are the remaining handoff actions.
