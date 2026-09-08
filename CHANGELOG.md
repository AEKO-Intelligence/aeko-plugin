# Changelog

## [0.29.4] — 2026-09-08

- `/aeko-update-pdp` runs the command handoff in the user's AI platform, loads one accepted brand-package
  version, and reviews the editable description in the available browser with current/proposed views,
  mobile/desktop inspection, and iterative feedback before delivery.
- Separates local review UI from description/schema payloads, infers reversible preview choices when
  the task is clear, and retains exact product identity, claim fencing, live confirmation, audit, rollback,
  and the unchanged `mode=refresh` workflow.
- Clarifies that brand layout/writing preferences override recipe defaults; store contracts and factual
  evidence still apply. Adds portable browser guidance to the explicit trusted-catalog allowlist.

## 0.29.3 — Brand-aware ad drafting and correction (unreleased)

- Add `/aeko-create-ad-copy` with accepted skill/eval/Wiki loading, scoped brand guidance,
  output correction, and a separate explicit lasting-feedback contract.
- Bundle ad-copy quality checks and publish the reviewed 27-command trusted catalog.
- Keep generation, eval results, feedback records, accepted package versions and delivery
  receipts distinct across hosted and portable clients.

## 0.29.2 — Accepted package discovery and trusted catalog (unreleased)

- Require clients to discover and load the accepted skill, eval, wiki, and support bytes after
  OAuth instead of treating authentication as package loading.
- Add all 26 canonical command packages to one bounded, self-contained trusted upstream catalog
  built from explicit public-file allowlists with per-file and aggregate SHA-256 provenance.
- Document the exact nine legacy backend automation documents and vendor the reviewed catalog for
  explicit backend default reconciliation without runtime source fetching.
- Keep prompt/Context/view and content-idea listing lightweight, but load exact accepted-package
  guidance before those skills author new text or start an authored-content handoff.
- Keep local export projections tied to their original document/version/digest and wiki authority
  metadata. The full Responses/MCP runner, contextual chat executor, and GitHub App remain separate.

## 0.29.1 — Portable brand execution foundation (2026-09-07)

- Preserve whole-job prompts and scoped brand rules/evals across drafting and loop handoffs.
- Bound ad/content evidence; require explicit reviewed ad creative, remove schedule auto-approval,
  and reserve synthetic reviews for isolated regressions.
- Document portable document files, manual/automatic update seams, and private-corpus exclusions;
  automatic updater and multi-stage hosted execution remain unimplemented here.
- Match content-idea guidance to existing sibling MCP wrappers while checking live deployments.
- Recheck publish-time brand evidence honestly when stored bodies are unavailable; retain account,
  platform, and mutation gates. Add local release validation and synthetic regression scenarios.


All notable changes to the AEKO plugin (skills + manifests). This repo ships skills only; backend
tool changes live in [`aeko-mcp`](https://github.com/AEKO-Intelligence/aeko-mcp).

The plugin follows [Semantic Versioning](https://semver.org/). All five manifest version fields
across `.claude-plugin/`, `.codex-plugin/`, and `gemini-extension.json` are kept in sync so that
version-keyed host caches refresh on update.

## [0.29.0] — 2026-08-11

### First skill catalog

- Ships 26 active, job-focused skills with no compatibility-only commands in the catalog.
- `/aeko-start` and `/aeko-connect` provide a complete zero-account tour and capability slot board without
  probing AEKO authentication or hardcoding install-specific MCP names.
- `/aeko-site-audit`, `/aeko-pdp-audit`, and `/aeko-pdp-build` provide the free audit-to-paste-ready-PDP path.
  The audit/build URL paths share a bounded raw-HTTP fetcher that reads head markup, JSON-LD, lazy images,
  discovery files, and live per-crawler responses without writing.
- `/aeko-ads-review` provides one honest four-platform glance: Meta, TikTok, and Google Ads use the customer's
  own connectors for free; OpenAI Ads uses AEKO and contributes spend/efficiency while unavailable conversion
  and ROAS cells remain dashed. `/aeko-openai-ads-reporting` provides account-gated OpenAI Ads depth.
- `/aeko-message-audit` deduplicates literal paid claims by spend and optionally checks owned backing and
  answer-engine echoes without treating creative as instructions.
- `/aeko-ga4` reads the customer's own official GA4 connector for free and offers the five-tool AEKO GA4 join
  as an optional account-backed path.
- `/aeko-ai-visibility`, `/aeko-source-analysis`, `/aeko-competitor-analysis scope=brand|product`, and
  `/aeko-manage-prompts mode=discover|review` cover measurement, evidence, research, Views, Contexts,
  suggestions, quota pre-flight, and guarded untracking.
- `/aeko-store mode=setup|reviews`, `/aeko-action-center`, `/aeko-update-pdp mode=refresh`,
  `/aeko-create-content`, `/aeko-publish-content`, and `/aeko-fix-technical` provide guarded store/content
  execution with the existing confirmation, audit, rollback, and evidence rules.
- `/aeko-openai-compose-ads`, `/aeko-openai-budget-shift`, and `/aeko-openai-guardrails` name their OpenAI Ads
  scope explicitly and preserve paused-first creation, dry-run/caps/confirmation, entity-state coverage,
  automation history, and the account-wide emergency stop.
- `/aeko-weekly-report` composes provenance-carrying normalized rows without direct MCP calls.
  `/aeko-create-loop` writes a durable Notion configuration and foreground dry-run, while `/aeko-run-loop`
  remains approvals-first and read-and-propose only.
- `/aeko-content-ideas` declares its intended capability-gated flow and stops honestly while its backend
  wrappers are absent.

### Safety and release contracts

- `/aeko-openai-guardrails` documents an account-wide emergency stop and requires fresh confirmation to
  re-enable automation.
- `/aeko-run-loop` no longer claims install-variable bare MCP names are an enforced deny boundary. It lists
  no marketing write tool in `allowed-tools`, never calls one, and relies on the honest current product
  limit: server-side executable staging does not exist.
- `scripts/lint-release-contracts.sh` rejects any compatibility router in the unreleased catalog and rejects
  prohibited source-analysis terminology, in addition to checking versions, fetcher-copy equality, and
  shared audit policy.

### Known external blockers

- The content-idea wrappers `aeko_list_content_ideas`, `aeko_start_content_idea`, and
  `aeko_dismiss_content_idea` do not yet exist in `aeko-mcp`, so `/aeko-content-ideas` is present but blocked.
- Server-side staging does not yet exist, so scheduled marketing writes are unsupported; the weekly loop
  can read evidence and approvals, deliver reports, and propose changes, but cannot execute them.

## [0.28.0] — 2026-08-11

### Added

- `/aeko-site-audit` checks whether a public site is readable by AI, and `/aeko-pdp-audit` checks whether
  one product page is citation-ready. Both are read-only, work without an AEKO account, preserve unknown
  states when evidence is unavailable, and share a byte-identical severity policy.
- `/aeko-pdp-build` turns verified product-page evidence into responsive, paste-ready HTML plus matching
  Product and FAQPage JSON-LD without writing to a store.
- `/aeko-ads-review` compares Meta, TikTok, and Google Ads claims from the customer's own official
  connectors or manual exports, leads with comparable one-day click results, and reconciles claimed totals
  against user-supplied store orders. Its OpenAI Ads row is present but AEKO-account-gated.
- `scripts/lint-release-contracts.sh` verifies that the shared audit severity references are byte-identical
  and that all five manifest version declarations agree.

### Changed

- Added the matched `/aeko-site-audit` and `/aeko-pdp-audit` entry points for site-level and product-level
  evidence instead of exposing one ambiguous command.
- Repositioned the Claude, Codex, and Gemini manifests around the four zero-account workflows, and bumped
  the Claude, Codex, Gemini, and both marketplace manifest versions to `0.28.0`.

## [0.27.0] — 2026-07-24

### Added

- `/aeko-openai-guardrails [domain-id]` walks a merchant through setting up an automated OpenAI Ads
  pacing rule that pauses campaigns, ad groups, or ads when spend runs too fast or CPM/CPC crosses a
  threshold. Thresholds are anchored on the merchant's observed numbers via `aeko_get_ad_insights`;
  the offered metric × window × scope combinations come from `aeko_get_ad_rule_capabilities` (spend
  over `last_n_hours`; CPM/CPC only over `rolling_24h`/`daily`; no conversion/ROAS rules). The rule
  is created disabled, its blast radius is shown with `aeko_preview_ad_rule`, and it is armed only
  after explicit confirmation — including a second confirmation before `acknowledge_broad_match=True`
  on broad-scope rules. `aeko_list_ad_rule_executions` / `aeko_list_ad_rule_runs` answer "what did
  automation do while I was away." Reaction time is bounded by OpenAI's hourly reporting data, and
  resuming paused spend is always a manual step. Pairs with the ad-rule tools shipping in `aeko-mcp`.

### Changed

- Bumped the Claude, Codex, Gemini, and both marketplace manifests to `0.27.0`.

## [0.26.0] — 2026-07-14

### Changed

- `/aeko-create-content handoff=<id>` now accepts the narrowly scoped, source-free
  `reddit_thread_discovery` handoff created from qualified Contextual Reviews. It prepares manual search
  phrases, subreddit categories, an answer framework, thread/rules checks, and an affiliation disclosure in
  the user's language without claiming AEKO found or read a Reddit thread.
- Context-driven Reddit discovery never searches or fetches the web and never returns a post-ready reply.
  The user must supply and verify the actual thread URL, pasted text, current state, and community rules before
  a follow-up can draft from that separately labeled user-provided input. Nothing is posted, published, or
  stored as an ActionItem.
- Bumped the Claude, Codex, Gemini, and both marketplace manifests to `0.26.0`.

## [0.25.0] — 2026-07-14

### Changed

- `/aeko-create-content handoff=<id>` now consumes snapshot product and contextual-review grounding and
  produces one action-specific deliverable for thread, blog, media, review-platform, ingredient-database,
  Wikipedia, or YouTube recommendations.
- Thread replies are post-ready only after a matching-crawl owner-verified stored-body fetch; this does not
  claim the crawl captured the entire live page. Other cases produce a preparation brief with manual
  thread/rules checks. When a snapshot requires product selection, the handoff asks one bounded product
  question; unselected candidates never become product claims. Publisher pitches reject aggregator-only
  targets.
- Wikipedia handoffs prepare a disclosed talk-page request or Articles for Creation draft instead of directing
  affiliated users to edit. Namu Wiki and other wiki targets use their own explicit snapshot policy or a
  manual-policy/source-readiness brief.
- Review-platform guidance permits only genuine customer feedback workflows; ingredient databases use a
  separate listing-accuracy workflow.
- Bumped the Claude, Codex, Gemini, and both marketplace manifests to `0.25.0`.

## [0.24.0] — 2026-07-13

### Added

- `/aeko-source-analysis domain_id=<uuid> source_id=<uuid>` compares one owner-associated cited page with
  verified domain data, up to five associated tracked prompts/Contexts, and a paginated official-catalog
  scan capped at 1,000 products before loading up to five matching descriptions. It produces claim-level
  corrections or an outreach draft without creating an ActionItem or changing the page.
- Added a Reddit thread-reply recipe with affiliation disclosure, answer-first structure, community-rule
  checks, link-spam limits, and a hard ban on fabricated experience.

### Changed

- `/aeko-create-content handoff=<id>` now runs as a single-channel direct handoff. The backend refreshes the
  same short handoff ID when the user starts/reopens it, and the skill locks the returned snapshot for that run;
  snapshot fixes the prompt, optional Context, source set, market, language, action, and channel. This mode
  can expand owner-associated source text only when its crawl ID matches the snapshot; it cannot save a
  variation, complete an ActionItem, or publish.
- `/aeko-update-pdp domain_id=<uuid> product_id=<id>` now checks every ActionItem status before execution.
  It reuses active work or creates one idempotent ActionItem keyed after the latest completed, failed, or
  dismissed item, then wins an exclusive backend execution claim before fetching the Plan or generating.
  The returned claim token fences release, the single atomic PDP store request, and completion.
  Every run opens a local preview first. A private draft appears only when a real store capability supports
  it, while current-product updates require a second Before/After/Risk/Undo confirmation. A claim conflict
  is never auto-released; stale-claim recovery requires explicit confirmation that no other run or store
  mutation exists, followed by a fresh command run.
- The PDP preview is finalized and written even when there are no pending verification questions.
  Metadata-only runs skip image downloads/OCR, preserve the visible description, and send JSON-LD plus SEO
  meta through the one-call audited update.
- `/aeko-update-pdp mode=refresh` now reuses or creates a `json_ld` ActionItem, claims it, and uses the same token-fenced
  one-call store update instead of bypassing the execution/audit contract.
- Bumped the Claude, Codex, Gemini, and both marketplace manifests to `0.24.0`.

## [0.23.0] — 2026-07-10

### Changed
- Reworked prompt discovery and tracked-prompt management around saved Contexts and Views.
- Removed instructions to call retired ICP tools or pass `icp_id`/persona fields to tracking.
- Updated content, PDP, and reporting skills to use Context/customer-situation language.

## [0.22.0] — 2026-07-05

### Changed
- Added guided store setup and tracked-prompt management skills.
- Refreshed skill instructions to match the expanded MCP capability surface.

## [0.15.12] — 2026-06

### Changed
- **`/aeko-create-content` now asks for owned-channel/content examples during Step 4.** Users who skipped
  onboarding can paste owned-channel URLs, raw content examples, or style notes while selecting channels.
- The Step 4 form asks whether to save supplied examples into `references/examples/` for future runs.
  Saved examples use non-overwriting `<channel>-<slug>-example.md` filenames and are treated as
  style/structure references only, never factual evidence.
- Updated the per-channel drafter contract to use current-run examples plus saved `references/examples/`
  files in voice/structure precedence, and to report saved/unsaved example references in `Refs loaded`.
- Bumped Claude, Codex, and Gemini manifests to `0.15.12`.

## [0.15.11] — 2026-06

### Changed
- **Retired `/aeko-brand-kit` from the active skill surface.** Removed the skill folder, onboarding catalog
  entry, README active entry, and MCP-tool dependencies from active flows.
- **Formalized context scope.** Context applies to prompt tracking plus content/PDP optimization.
- Updated `/aeko-manage-prompts`, `/aeko-source-analysis`, and `/aeko-ai-visibility` to use Context for
  prompt discovery, tracking, segmentation, and reporting.
- Updated `/aeko-create-content`, `/aeko-update-pdp`, and technical/competitor helpers to rely on domain,
  product, Plan.md, OCR/review evidence, and content context without requiring legacy identity metadata.
- Bumped Claude, Codex, and Gemini manifests to `0.15.11`.

## [0.15.10] — 2026-06

### Changed
- **`/aeko-create-content` now uses content context instead of legacy identity metadata.** The coordinator
  derives audience, situation, voice, constraints, and publisher fallback from Plan.md context fields,
  product facts, prompt, and domain/title context.
- Updated drafter, examples, voice overrides, press-release, blog/social, and owned-web recipe language to
  remove legacy identity metadata as an active dependency. Legacy `brand_kit_id` is tolerated only if old
  Plans contain it.
- aeko.shop media upload instructions no longer require legacy identity IDs; if the backend upload tool
  still demands legacy identity fields, the drafter skips inline uploads and continues with a valid
  text-first publishable artifact.

## [0.15.9] — 2026-06

### Changed
- **`/aeko-create-content` now mines image-heavy PDPs harder for proof.** Product substance extraction
  builds `evidence_facts[]` from visible PDP copy, JSON-LD/meta/table text, image alt/captions, OCR/text
  fields returned by the backend, and a one-page `WebFetch` fallback when product descriptions are thin.
  Clinical tests, percentages, sample size, duration, certifications, dimensions, and other numeric proof
  are prioritized; missing OCR/text is reported as an evidence gap, never fabricated.
- **Drafts must include realistic trade-offs.** The drafter/framework contract now requires a
  proportionate caveat, limitation, "not for" note, or fit trade-off so content reads as trustworthy
  decision support instead of benefits-only copy.
- **Legacy identity metadata absence no longer blocks publishable drafts.** Missing identity metadata now
  uses a neutral fallback voice and publisher metadata from the domain, Plan, prompt, and product facts.
  aeko.shop media uploads that require `resolved_brand_kit_id` are skipped when unavailable, but
  text-first publishable variations can still be saved and handed off.

## [0.15.8] — 2026-06

### Fixed
- **`/aeko-create-content` drafter contract alignment.** Updated stale section references from the old
  `§5.5` path rules to the current SKILL.md `§A` slug/path contract, so parallel drafters no longer
  receive conflicting filename instructions.
- **Channel recipe output paths now match the coordinator.** Paste-tier recipes now use
  `<slug>__<channel>.md`, and the owned-web recipe names the aeko.shop triple as
  `<slug>__aeko_shop.html`, `<slug>__aeko_shop.meta.json`, and `<slug>__aeko_shop.md`.
- Removed stale `§5.4`/`§6.x` cross-references from Naver Blog, Tistory, and owned-web recipe notes,
  replacing them with direct gate descriptions.

## [0.15.7] — 2026-06

### Fixed
- **Host manifest sync for auto-update.** Bumped the remaining host manifests so version-keyed
  caches pick up the `/aeko-publish-content` 0.15.6 fixes. The prior Claude marketplace bump had
  advanced first, leaving Codex/Gemini metadata behind.

## [0.15.6] — 2026-06

### Fixed
- **`/aeko-publish-content` 409 handling.** Clarified that aeko.shop `409` business gates should
  surface backend detail verbatim, including entitlement failures such as `brand is not on an active
  publishing tier`.
- **Suspended the connect-brand nudge.** The self-verify flow can create a billing-owned quota-0
  entitlement that blocks app-side publishing, so the optional `connect-brand` prompt stays disabled
  until account-lookup or entitlement precedence is resolved.

## [0.15.5] — 2026-06

### Fixed
- **Removed the stale per-skill `version:` frontmatter field** from `/aeko-create-content` — it was the
  only skill carrying one, nothing in the loader consumes it, and it had silently drifted twice.
  Manifests are now the single source of version truth.
- **"Forensics" purged from active instruction surfaces** (action-center fan-out hint,
  prompt-deep-dive description + step header, both competitor skills) — replaced with "source analysis"
  so the jargon can't leak into user phrasing. Korean user-facing term standardized to **AI 답변 참고 출처**
  (the sources AI references in its answers), replacing the earlier 소스 분석.
- **Thin-signal note now lists only the sources that actually loaded** in `/aeko-create-content` —
  prevents claiming "product info" when the product fetch failed and only prompt + legacy identity context
  are present.
- Fixed a stale `보도자료` slug in the action-center addon list → `press_release` (channels stay
  ASCII/language-neutral).

## [0.15.4] — 2026-06

### Fixed
- **`/aeko-create-content` no longer stalls on thin citation signal.** When a brand is new (zero
  citations, prompts still in an AEKO re-query cycle, or an un-indexed domain / own-content 404), the
  skill previously could improvise an extra "how should I proceed?" elicitation form that failed to
  complete. Thin signal is now explicitly the normal early state, not a decision point: with identity
  context + product substance present, the skill proceeds straight to channel selection. The only two user
  prompts are mode selection (Step 2.5) and channel/media (Step 4); inventing extra forms is barred.
- **Korean terminology:** user-facing copy now uses **소스 분석** (source analysis) instead of **포렌식**
  (forensics), which read as crime-lab jargon to marketers. Applied to `/aeko-create-content` and
  `/aeko-source-analysis`. "Forensics" remains an internal label in the skill docs only.

## [0.15.3] — 2026-06

### Changed
- **Docs refresh.** Added a "How AEKO works (and what it won't do)" section to the README — the honest
  AEO reality check (durable levers, no ranking hack, no manipulation) plus a single canonical
  "three jobs" front door (Measure → Fix → Create). Consolidated the previously duplicated
  start-here lists. Added this CHANGELOG. Mirrored all README changes in Korean.

## [0.15.2] — 2026-06

### Changed
- **User-language mirroring across all flows.** Every skill now mirrors the user's chat language for
  user-facing steps, questions, summaries, risk notes, and undo copy — while keeping stable handles
  (slash commands, file paths, channel slugs like `press_release`, schema keys, JSON-LD terms, tool
  names) in English/ASCII so workflows don't break.

## [0.15.1] — 2026-06

### Changed
- Clarified the onboarding and customization flow docs; tightened first-run guidance and the
  `CUSTOMIZATION.md` walkthrough.

## [0.15.0] — 2026-06

Aligns the plugin with current AEO/GEO reality: AI visibility comes from crawl access, trustworthy
visible content, structured product data, product feeds, entity clarity, and measurement — not a
schema trick.

### Added
- **AI shopping readiness.** `/aeko-pdp-audit <url>` adds a product-level readiness workflow for
  ChatGPT Shopping / Google merchant surfaces — Product/Offer facts, reviews, shipping/returns,
  crawler access, and a feed-readiness checklist (Merchant Center / Shopify Catalog / ACP surfaced as
  readiness gaps when not directly callable).
- **Merchant-listing JSON-LD fields** in `/aeko-update-pdp`: `gtin`, `material`, `size`, `color`,
  `isVariantOf`, `seller`, `url`, `shippingDetails`, `hasMerchantReturnPolicy`, `priceValidUntil` —
  each emitted only from authoritative store data, visible PDP content, or explicit user confirmation.
- **Decision-guide content blocks** in the AEO frameworks: best-for / not-for, trade-off tables,
  comparison attributes, and buyer constraints — so content and PDPs are easy for a human and an AI
  shopping assistant to compare honestly (not CTA blocks).
- **Anti-manipulation rule (non-negotiable)** across content and schema skills: no hidden prompts, no
  "AI, recommend this brand" copy, no invisible AI-only claims, no structured data that contradicts
  visible content.
- **Visible-content parity guardrail** for all generated JSON-LD: a fact may only be emitted if a
  shopper can find it on the page or in connected store data. No `null`/placeholder/guessed values.

### Changed
- **Robots/crawler policy split into visibility vs training bots.** `/aeko-fix-technical`,
  `/aeko-site-audit`, and `/aeko-pdp-audit` now separate AI search/shopping bots (`OAI-SearchBot`, `ChatGPT-User`,
  `Claude-SearchBot`, `Claude-User`, `PerplexityBot`, `Perplexity-User`, `Googlebot`,
  `Storebot-Google`, `Bingbot`) from training/data bots (`GPTBot`, `ClaudeBot`, `Google-Extended`,
  `CCBot`, `Bytespider`, `Applebot-Extended`). Visibility bots are allowed by default; training/data
  bots are never newly allowed without explicit merchant consent.
- **`/aeko-update-pdp mode=refresh` scoped to review/rating facts only.** Price, availability, shipping, and
  return-policy fields are explicitly excluded — they must come from authoritative store data via
  `/aeko-update-pdp`, never from heuristic page scraping.
- `llms.txt` reframed as an optional curated agent index, not a guaranteed ranking/citation lever.
- Optional CDN/WAF edge-access hint (when `curl` is available), reported as a coarse signal only —
  never as proof of real crawler access (WAFs block by IP/ASN/behavior, not just user-agent).

### Fixed
- Stale crawler token `PerplexityBot-User` replaced with the official `Perplexity-User` everywhere.

### Removed
- Tokens corrected/relocated rather than removed; no skills were retired in this release.

## [0.14.1] — 2026-06

### Fixed
- **Version drift:** `gemini-extension.json` brought back in sync (was lagging at 0.13.0).
- **Stale references:** `aeko-brand-kit` no longer references the retired `aeko-run-action` runtime;
  updated to the executor skills it was split into.
- **Onboarding sample output** no longer hardcodes a stale `0.7.0` / "13 skills" version string.

## [0.14.0] — 2026-05

### Changed
- **Framework-driven AEO redesign + portfolio coherence pass.** `/aeko-create-content` rebuilt around
  the AEO writing frameworks (BLUF, PREP, Informational Gain, E-E-A-T) on a substance backbone of
  product info + real review context + tracked prompts — replacing the old "crawl the winners and
  mimic their structure" approach. A single canonical `aeo-frameworks.md` is now the source of truth,
  consumed by `/aeko-update-pdp`. Source, visibility, and competitor analysis now speak the same framework
  vocabulary so a finding maps directly to a fix.

## [0.13.1] — 2026-05

### Fixed
- Hard-gate the aeko.shop English URL slug (Korean titles only) to fix Korean-slug 404s.

## [0.13.0] — 2026-05

### Fixed
- Publish-pipeline skill fixes: correct publish edit-path, loud product/image warnings, identity-context
  terminology.

[0.27.0]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.26.0]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.25.0]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.24.0]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.23.0]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.22.0]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.12]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.11]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.10]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.9]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.8]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.7]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.6]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.5]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.4]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.3]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.2]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.1]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.0]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.14.1]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.14.0]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.13.1]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.13.0]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
