# AEKO Plugin

Skills for [AEKO](https://aeko-intelligence.com) — AEO (AI Engine Optimization) workflows for cross-border ecommerce. Guides Claude and Codex through optimizing product pages for ChatGPT/Claude/Gemini/Perplexity citations, drafting persona-targeted content, generating JSON-LD, managing brand kits, and executing action items.

This repo ships **skills only**. Backend access (tools like `aeko_get_domain_info`, `aeko_get_brand_kit`, etc.) comes from the separate [AEKO MCP server](https://github.com/AEKO-Intelligence/aeko-mcp), hosted at `https://aeko-intelligence.com/mcp`. Install both.

## Install

### Prerequisite — filesystem + shell access

Most skills read files, write artifacts (HTML, markdown, JSON), or shell out to open previews. Your MCP host needs filesystem + shell tools for these to work:

- **Claude Code:** native — `Read`, `Write`, `Glob`, `Bash` are built-in.
- **Claude Desktop:** install `@modelcontextprotocol/server-filesystem` (or equivalent) alongside the AEKO connector. Skills that save local artifacts will fail without it.
- **Codex / Cursor:** verify per-host filesystem tooling before install.

### Claude Desktop (recommended)

**Step 1 — Add the AEKO MCP custom connector** (for backend tools):

1. Settings → Connectors → **Add custom connector**
2. Server URL: `https://aeko-intelligence.com/mcp`
3. Advanced → Client ID: `aeko-mcp-v1`
4. Advanced → Client Secret: leave blank
5. Connect — complete browser OAuth

**Step 2 — Install this plugin** (for skills / slash commands):

1. Settings → Plugins → **Browse plugins → Add marketplace**
2. Paste: `AEKO-Intelligence/aeko-plugin`
3. Install **aeko-plugin**

After both steps, `/aeko-plugin:aeko-brand-kit`, `/aeko-plugin:aeko-action-center`, etc. are available in any chat.

### Claude Code

```bash
/plugin marketplace add AEKO-Intelligence/aeko-plugin
/plugin install aeko-plugin@AEKO-Intelligence
```

Then set up the MCP connection separately:

```bash
claude mcp add --transport http aeko https://aeko-intelligence.com/mcp
```

### Codex Desktop / Codex CLI

```bash
codex mcp add --transport http aeko https://aeko-intelligence.com/mcp
```

This repo also includes a Codex plugin manifest at `.codex-plugin/plugin.json` for marketplace discovery.

## Available Skills

See [`skills/`](skills/). Each is a self-contained SKILL.md consumed by Claude or Codex.

**Entry points:**

- `/aeko-action-center [domain_id] [category]` — router: lists pending items in three categories (Technical / PDP / Content generation) and prints ready-to-copy executor commands
- `/aeko-update-pdp <item_id>` — PDP executor. Fetches Plan.md, asks image strategy, WebFetches the live page, generates responsive HTML + JSON-LD, writes to store (shadow-by-default) with audit trail
- `/aeko-fix-technical <item_id>` — Technical executor. Generates llms.txt / robots.txt patches / site-level JSON-LD with embedded spec rules
- `/aeko-create-content <item_id>` — Content executor. Pulls tracked-prompt citation forensics to mimic winning source structures; saves locally, never writes to store
- `/aeko-brand-kit <domain_id>` — view or edit your domain's brand kit (voice, guardrails, must-include / forbidden)

**Research + discovery:**

- `/aeko-find-prompts-to-track [domain_id]` — filter the research library, rank candidates for your brand, track selected prompts
- `/aeko-prompt-deep-dive <prompt_id> [window]` — citation-forensics on one tracked prompt (which competitors win it, which sources AI cites, what to mirror)
- `/aeko-brand-competitor-analysis [domain_id] <competitor>` — brand-level positioning via WebSearch + Wikipedia/Wikidata + AEKO citation data
- `/aeko-product-competitor-analysis <product_id> [urls...]` — product-level property-by-property comparison against 3-5 competing PDPs

**Maintenance + reporting:**

- `/aeko-refresh-jsonld <product_id>` — periodic JSON-LD refresh (review counts, ratings) via read-patch-write. Designed for `/schedule`
- `/aeko-visibility-report [domain_id] [window] [depth]` — on-demand report. `window=7d|14d|30d|90d`, `depth=summary|full`
- `/aeo-audit <url>` — generic AEO readiness audit for any URL (uses Claude's reasoning; no AEKO data dependency)

### Retired

Retired across the 2026-04 (v0.4.0) and 2026-04 v0.5.0 consolidations. If you have muscle memory for one of them, use the replacement:

| Retired | Use instead |
|---|---|
| `/aeko-run-action` | Split: `/aeko-update-pdp` (PDP items) + `/aeko-create-content` (content items) + `/aeko-fix-technical` (technical items). `/aeko-action-center` dispatches to the right one. |
| `/aeko-optimize-pdp`, `/aeo-optimize` | `/aeko-action-center` → `/aeko-update-pdp <item_id>` |
| `/generate-faq`, `/generate-jsonld` | Handled inline by executor skills. `/aeko-refresh-jsonld` for periodic review-count refresh. |
| `/aeko-create-own-content`, `/aeko-create-external-content` | `/aeko-create-content <item_id>` (venue determined by Plan.md `artifact_type`) |
| `/aeko-competitive-pdp-input` | Research absorbed into `/aeko-update-pdp` (product context) and `/aeko-brand-competitor-analysis` (standalone) |
| `/aeko-fix-store-level` | `/aeko-fix-technical <item_id>` |
| `/aeo-audit-local` | Deprecated — file-level citability lint isn't reliably doable from bare text |
| `/competitive-research` | Split: `/aeko-brand-competitor-analysis` + `/aeko-product-competitor-analysis` |
| `/create-visibility-report` | Merged into `/aeko-visibility-report [domain_id] [window] depth=full` |
| `/create-blog-article`, `/create-social-content`, `/create-marketing-materials` | `/aeko-create-content` (brand-kit-grounded, tracked-prompt-seeded) |

**Note on `/aeko-update-pdp`:** v0.4.0 retired it as a deprecated wrapper; v0.5.0 revives the name as a Plan.md-driven executor. Check `CHANGELOG.md` in `aeko-mcp` for the history.

### Skill operating principle

An AEKO skill earns its slot if it **compresses useful workflow** — stringing together AEKO tools + Claude's reasoning into a repeatable single-command flow. Most AEKO skills call at least one `aeko_*` MCP tool (brand kit, tracked prompts, action items, store writes), but it isn't a hard rule. `/aeo-audit` is the exception: it operationalizes AEO audit heuristics as a workflow even though it uses no AEKO backend data.

Bug fix if a skill's prose references AEKO primitives its `allowed-tools` doesn't actually list — that's credibility debt. Either ground the skill or retire it.

## Relationship to other AEKO repos

- **[`aeko-mcp`](https://github.com/AEKO-Intelligence/aeko-mcp)** — Python MCP server. Hosts the `aeko_*` tools. Embedded in the AEKO backend and exposed at `/mcp`. You don't install this directly; you connect to the hosted endpoint.
- **`aeko-plugin`** (this repo) — Skills only. Distributed via the Claude/Codex plugin marketplaces.

## License

MIT
