# Portable brand foundation audit — 2026-09-07

This report records the first ten-skill batch, committed as `ab1da11`. The
[follow-up review](brand-foundation-followup.md) covers the remaining sixteen:
fifteen received targeted corrections and the connection board retained its existing
setup behavior. Together these reports cover all 26 entrypoints at source level;
they do not establish model behavioral quality. References below to uncommitted work
or a pending sixteen-skill audit describe the first batch's original handoff.

## Outcome and ownership

Local, reviewable changes in `/Users/seanhan/orca/workspaces/aeko-plugin/brand-customization-foundation`.
The dispatched worktree initially contained v0.27.0/21 skills at `5810807`; it was fast-forwarded
without creating a commit to the original checkout's tracked `f4138a0` (26 skills/v0.29.0).
All task changes are uncommitted on that base, with five manifests synchronized to **0.29.1**.
No original checkout or backend/frontend file was modified. No ignored eval workspace, output,
private corpus, or credential was read or copied. No external write, commit, push, publication,
nested agent, or paid model call was made. Sibling code was inspected read-only; the pure backend package serializer
was exercised in memory with synthetic data and bytecode writing disabled.

Read parent AGENTS, sibling MCP/backend AGENTS, skill-creator guidance, current release lint,
all 26 skill entrypoint inventories/tool declarations, manifests, README and CUSTOMIZATION.
There is no tracked plugin AGENTS/CLAUDE instruction file in this base. Deep workflow changes
are bounded to ten entrypoints; this is not a claim that all 26 have passed behavioral evals.

## Evidence-backed corrections

| Surface | Finding | Local correction |
| --- | --- | --- |
| Customization | Three-executor, cache-editing guide; no portable version/eval/job contract | Replaced with brand-owned working package flow, actual developing backend file seam, scoped examples/evals, manual + planned automatic evolution, private-corpus exclusion, bilingual summary |
| Shared execution | No consistent original task prompt, scope, eval, or output receipt contract | One canonical contract copied into seven adopting skills; byte-identity lint; five also load a generic output eval rubric |
| OpenAI ad composition | Requested every review, trusted omitted title/body backend generation, allowed schedule auto-approval, reused permanent cluster keys | One bounded sample, account preflight, explicit reviewed title/body/language/hints, required brand checks, proposal-only unattended behavior, per-logical-action idempotency/retry limits |
| Content drafting | Original prompt absent from child brief; recipe register beat brand rules; live synthetic-review fallback | Verbatim prompt + brand versions/rules/evals/window/limits in child brief, explicit-rule precedence, bounded evidence/examples, no live synthetic fallback, checks before save/completion; sequential fallback where delegation unavailable |
| Content-idea discovery | Claimed three wrappers were unbuilt despite sibling implementation | Live registry gate retained, source truth corrected, cursor/offset/window contract matched, one page by default, full handoff context preserved |
| Publish | Stored body flags could be mistaken for validated brand copy | Required brand eval cannot pass from hidden bodies or an unbound local file; stop as `brand_eval_unverifiable` when exact payload/receipt is unavailable |
| PDP/technical | Examples/recipes could outrank explicit task/brand rules | Scoped precedence and required exact-output evals; PDP merchant-prefix preservation, claims, store gates, technical syntax/deploy boundaries retained |
| Loop composer/runner | Config summary lacked original task prompt/report questions and package/eval/window fields | Preserve those fields through config readback and child invocation; verify materialization, cap work, incomplete brand config degrades to conversation-only |
| Budget scheduling | Universal `/schedule` example and executable-sounding staging language | Host-capability-based prompt handoff and proposal terminology; no unattended write permission |
| Start flow | Wrote into install caches; overstated Tistory/Naver publishing | Brand-owned working destination; supported aeko.shop/AEKO-draft distinction |

## Exact current capability gaps

1. **Daily new-context selection is not available through the ad-composition MCP primitive.**
   `aeko_mcp/tools/marketing.py:103` accepts only `domain_id`, `min_context_score`, `limit`.
   Backend `api/routes/review_integrations.py:376` returns a strongest-context-first sample;
   its response does not include context creation or review creation timestamps. It has neither
   a source window nor pagination. A last-24-hours request must report unavailable; a review
   posting timestamp would not be equivalent to context creation even if later exposed.
2. **Composition creates a new group, not an upload into an existing group.**
   `marketing.py:681` places one new group under an existing/new campaign. Its `ads` support
   explicit title/body/target_language. Backend `api/services/openai_ads/context_deploy.py`
   validates explicit fields and generates only when omitted, so supplying checked fields is
   supported. The tool supports up to 100 ads/group; this skill now chooses a much smaller cap.
3. **Publisher cannot re-evaluate unseen stored creative.**
   `content_variation.py:276` lists formatted metadata/body-presence flags, not raw bodies.
   No exact stored-body validation receipt is exposed by that list. Brand-required publish
   evals may therefore block until a suitable read/receipt capability exists. No new API is
   invented, and no claim of equivalence is made for an unbound local artifact.
4. **Content-idea wrappers exist in source, deployment presence is unverified.**
   `content_ideas.py:193,257,304` implements list/start/dismiss; list supports
   `7d|30d|90d|all`, limit/offset/cursor (no positive offset with cursor). Starting can refresh
   the evidence for an existing handoff; content creation still freezes one fetched snapshot
   for the run. Pro+ and ownership gates remain in force.
5. **Hosted agent execution and updater are separate missing services.**
   The existing AI automation stage loads skill text and composes `instructions_text` plus
   `brief_text` with the stage input; it is not the intended multi-stage MCP agent. The plugin
   does not provide updater event capture, Function/queue worker, regression activation,
   run-scoped write grants, automatic GitHub import/sync, or wiki retrieval. Exact-version
   preview/promote remains the developing backend lifecycle; no successful preview is fabricated.
6. **Loop security limits remain instruction-level.**
   The loop's atomic receipt/dedup prerequisites and same-turn marketing confirmation gates
   remain. A capable host must materialize selected package/eval bytes; a filesystem path in
   a cloud prompt is not access. Tool/byte caps in skills are instructions, not server-enforced
   resource limits. An older config without brand-job fields now renders conversation-only.
7. **Document seeding requires adaptation.**
   Many upstream descriptions exceed the backend 200-character limit. Source frontmatter
   `name` is the canonical plugin slug; exported document names are assigned by the backend.
   Seed with canonical metadata and skill body plus all required support files, rather than
   submitting conflicting frontmatter or an entire checkout. Existing HTML/JSON/Python
   supports require trusted read-only handling; the brand-editable seam accepts Markdown.
8. **Individual package completeness needs ongoing review.**
   The seven newly adopted shared refs are in-package files, not external symlinks. Existing
   cross-skill commands, root-doc links, and other runtime resources elsewhere in the catalog
   still require explicit materialization/routing by an importer/host. MCP is not a skill loader.

Evidence roots: `/Users/seanhan/aeko-intelligence/aeko-mcp/aeko_mcp/tools/` and
`/Users/seanhan/aeko-intelligence/aeko/{aeko_backend,aeko_ai}/`; package seam and product-owner
updates were read from the coordinator's `portable-brand-plugin` worktree, including
`docs/automations-brand-updater-contract.md`,
`docs/intent/2026-09-07-portable-brand-skills-decisions.md`, and
`aeko_backend/api/services/automations/packages.py`.

## Validation and its limits

- `./scripts/lint-release-contracts.sh`: **pass**, synchronized 0.29.1 manifests, existing
  severity/fetcher/retired-slug checks plus 26-slug/shared-reference/private-path checks.
- `python scripts/lint-brand-contracts.py --mcp-source /Users/seanhan/aeko-intelligence/aeko-mcp`:
  **pass**, every declared `aeko_*` allowed tool in all 26 skills exists in inspected source.
  This verifies names, not every prose call argument or production availability.
- `python scripts/check-portable-package-examples.py --backend-packages
  /Users/seanhan/orca/workspaces/aeko/portable-brand-plugin/aeko_backend/api/services/automations/packages.py`:
  **pass**, synthetic A/B + upstream package bytes remain isolated, A's prior version stays
  unchanged, A's rule/eval travel together, deterministic export equals projected entries,
  and four unsafe path/type cases are rejected. This tests serializer invariants, not DB
  tenancy, updater compare-and-swap, generation quality, or hosted-run materialization.
- `git diff --check`: **pass**.
- Generic skill-creator `quick_validate.py`: **does not pass** for the changed skill entrypoints,
  because the existing catalog uses `argument-hint` and, on some skills, `disallowed-tools`.
  Its accepted-key set excludes both. YAML parses; these pre-existing host fields were retained.
  This mismatch is reported rather than claiming the generic validator passed.
- `evals/brand-execution-scenarios.md`: 14 public synthetic scenarios, manually walked against
  the changed contracts. The source-backed cases informed the corrections; future runtime/
  updater cases remain acceptance requirements. No independent agent/model behavioral test,
  private corpus regression, live API mutation, host installation, or paid benchmark ran.

## Updater targeting and remaining audit

Target the brand's immutable document `text`, canonical/validated `metadata`, and explicit
`support_files`. Keep brand/domain ownership outside model-controlled text. Project one
`SKILL.md` plus allowed relative files with the canonical serializer/digest, and attach eval
versions separately to the configured job. Keep the saved whole-job prompt separate from
skill text and pass both at execution. Copy the shared execution contract/output rubric into
support files when seeding an adopting skill; include permitted brand rules/evals/examples,
not AEKO private corpora or workspace history. Preserve upstream slugs in source; map exported
package identity deliberately. The updater should emit attributed minimal diffs against a
pinned base digest, regression-check, protect concurrent manual edits, then activate under
its eventual validated policy with rollback. No updater operation is implemented here.

Prioritize deeper audits of these **16 unchanged entrypoints**:

- Generation/claims: `aeko-pdp-build`, `aeko-message-audit`, `aeko-source-analysis`,
  `aeko-competitor-analysis` — scoped rules/evals, exact task propagation, retrieval bounds.
- Reporting/orchestration: `aeko-weekly-report`, `aeko-ads-review`, `aeko-openai-ads-reporting`,
  `aeko-ai-visibility`, `aeko-ga4` — child prompt/package propagation, report evals, aggregate
  row/byte/call limits, destination materialization. Weekly report is the first follow-up.
- Account/state workflows: `aeko-action-center`, `aeko-manage-prompts`, `aeko-store`,
  `aeko-openai-guardrails` — brand-specific policy loading without weakening existing gates.
- Free audit/setup: `aeko-site-audit`, `aeko-pdp-audit`, `aeko-connect` — package portability,
  referenced helper materialization, and exact source/window intent where applicable.

These received inventory/tool-surface review, not full semantic or behavioral validation.
Existing broad generic-template examples and remaining fixed recipe preferences deserve
selective follow-up; no customer-specific preference was added to global runtime behavior.

## Changed files

- `.claude-plugin/marketplace.json`
- `.claude-plugin/plugin.json`
- `.codex-plugin/marketplace.json`
- `.codex-plugin/plugin.json`
- `CHANGELOG.md`
- `CUSTOMIZATION.md`
- `README.md`
- `docs/automation-prompt-examples.md`
- `docs/brand-foundation-audit.md`
- `docs/contracts/brand-execution-contract.md`
- `evals/brand-execution-scenarios.md`
- `evals/brand-output.md`
- `gemini-extension.json`
- `scripts/check-portable-package-examples.py`
- `scripts/lint-brand-contracts.py`
- `scripts/lint-release-contracts.sh`
- `skills/aeko-content-ideas/SKILL.md`
- `skills/aeko-create-content/SKILL.md`
- `skills/aeko-create-content/references/brand-execution-contract.md`
- `skills/aeko-create-content/references/brand-output-eval.md`
- `skills/aeko-create-content/references/drafter-instructions.md`
- `skills/aeko-create-content/references/examples/README.md`
- `skills/aeko-create-loop/SKILL.md`
- `skills/aeko-create-loop/references/brand-execution-contract.md`
- `skills/aeko-fix-technical/SKILL.md`
- `skills/aeko-fix-technical/references/brand-execution-contract.md`
- `skills/aeko-fix-technical/references/brand-output-eval.md`
- `skills/aeko-openai-budget-shift/SKILL.md`
- `skills/aeko-openai-compose-ads/SKILL.md`
- `skills/aeko-openai-compose-ads/references/brand-execution-contract.md`
- `skills/aeko-openai-compose-ads/references/brand-output-eval.md`
- `skills/aeko-publish-content/SKILL.md`
- `skills/aeko-publish-content/references/brand-execution-contract.md`
- `skills/aeko-publish-content/references/brand-output-eval.md`
- `skills/aeko-run-loop/SKILL.md`
- `skills/aeko-run-loop/references/brand-execution-contract.md`
- `skills/aeko-start/SKILL.md`
- `skills/aeko-update-pdp/SKILL.md`
- `skills/aeko-update-pdp/references/brand-execution-contract.md`
- `skills/aeko-update-pdp/references/brand-output-eval.md`

## Coordinator review
Default-first behavior clarified: a brand without customization uses AEKO defaults and can run without first creating a custom package. This preserves the starting-library product contract; explicit current-brand rules still apply. Canonical guidance and all seven materialized copies match. Root review traced the no-input, unsupported last-24h selector, explicit reviewed creative and cross-brand restriction cases; this was a source review, not a paid model behavioral benchmark.

Independent source/scenario QA subsequently reviewed the ten changed entrypoints, twelve relevant
MCP argument shapes, release checks and synthetic package isolation/export. It found an onboarding
receipt that incorrectly promised a separately saved working copy would be used automatically.
The corrected receipt requires verified host package selection and reference loading before that
claim; QA independently closed it. No reproduced defect remains in this bounded review. This is
still not a model behavioral benchmark or sign-off on the other sixteen entrypoints, whose deeper
audit is a follow-up task.
