# Changelog

All notable changes to the AEKO plugin (skills + manifests). This repo ships skills only; backend
tool changes live in [`aeko-mcp`](https://github.com/AEKO-Intelligence/aeko-mcp).

The plugin follows [Semantic Versioning](https://semver.org/). All four host manifests
(`.claude-plugin/`, `.codex-plugin/`, `gemini-extension.json`) are kept in version sync so that
version-keyed host caches refresh on update.

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
- Publish-pipeline skill fixes: correct publish edit-path, loud product/image warnings, brand-kit
  terminology.

[0.15.3]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.2]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.1]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.15.0]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.14.1]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.14.0]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.13.1]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
[0.13.0]: https://github.com/AEKO-Intelligence/aeko-plugin/commits/main
