# Changelog

All notable changes to the AEKO plugin (skills + manifests). This repo ships skills only; backend
tool changes live in [`aeko-mcp`](https://github.com/AEKO-Intelligence/aeko-mcp).

The plugin follows [Semantic Versioning](https://semver.org/). All five manifest version fields
across `.claude-plugin/`, `.codex-plugin/`, and `gemini-extension.json` are kept in sync so that
version-keyed host caches refresh on update.

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
- Updated `/aeko-find-prompts-to-track`, `/aeko-prompt-deep-dive`, and `/aeko-visibility-report` to use
  Context for prompt discovery, tracking, segmentation, and reporting.
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
  `/aeko-prompt-deep-dive`. "Forensics" remains an internal label in the skill docs only.

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
- **AI shopping readiness.** `/aeo-audit <url> shopping` adds a product-level readiness mode for
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
- **Robots/crawler policy split into visibility vs training bots.** `/aeko-fix-technical` and
  `/aeo-audit` now separate AI search/shopping bots (`OAI-SearchBot`, `ChatGPT-User`,
  `Claude-SearchBot`, `Claude-User`, `PerplexityBot`, `Perplexity-User`, `Googlebot`,
  `Storebot-Google`, `Bingbot`) from training/data bots (`GPTBot`, `ClaudeBot`, `Google-Extended`,
  `CCBot`, `Bytespider`, `Applebot-Extended`). Visibility bots are allowed by default; training/data
  bots are never newly allowed without explicit merchant consent.
- **`/aeko-refresh-jsonld` scoped to review/rating facts only.** Price, availability, shipping, and
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
  consumed by `/aeko-update-pdp` and cited by `/aeo-audit`. Diagnostic skills (prompt-deep-dive,
  visibility-report, competitor analyses) now speak the same framework vocabulary so a finding maps
  directly to a fix.

## [0.13.1] — 2026-05

### Fixed
- Hard-gate the aeko.shop English URL slug (Korean titles only) to fix Korean-slug 404s.

## [0.13.0] — 2026-05

### Fixed
- Publish-pipeline skill fixes: correct publish edit-path, loud product/image warnings, identity-context
  terminology.

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
