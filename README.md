# AEKO Plugin

Skills for [AEKO](https://aeko-intelligence.com) — AEO (AI Engine Optimization) workflows for cross-border ecommerce. Guides Claude and Codex through optimizing product pages for ChatGPT/Claude/Gemini/Perplexity citations, drafting persona-targeted content, generating JSON-LD, managing brand kits, and executing action items.

This repo ships **skills only**. Backend access (tools like `aeko_get_domain_info`, `aeko_get_brand_kit`, etc.) comes from the separate [AEKO MCP server](https://github.com/AEKO-Intelligence/aeko-mcp), hosted at `https://aeko-intelligence.com/mcp`. Install both.

## Install

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

- `/aeko-action-center` — router: list pending Action + Technical items for a domain, hand off to executor
- `/aeko-run-action` — executor: run one Action item end-to-end (PDP rewrite / content draft / shadow write)
- `/aeko-fix-technical` — executor: run one Technical item (llms.txt, robots.txt, site-level JSON-LD)
- `/aeko-brand-kit` — view or edit your domain's brand kit (voice, guardrails, must-include / forbidden)

**Content + research:**

- `/aeko-create-own-content` — draft own-site content from a v2 brief
- `/aeko-create-external-content` — draft content for external media placements
- `/aeko-competitive-pdp-input` — competitor-focused research input for a PDP rewrite
- `/aeko-fix-store-level` — generate llms.txt, robots fixes, sitemap, schema
- `/competitive-research` — analyze competitor AI visibility gaps

**Audit + reporting:**

- `/aeo-audit` — audit a single URL or HTML for AI-citability
- `/aeo-audit-local` — batch-audit local content files
- `/create-visibility-report` — generate a comprehensive AI visibility report

### Retired (2026-04)

The 2026-04 consolidation retired 8 skills. If you have muscle memory for one of them, use the replacement:

| Retired | Use instead |
|---|---|
| `/aeko-optimize-pdp`, `/aeko-update-pdp`, `/aeo-optimize` | `/aeko-action-center` → `/aeko-run-action <item_id>` |
| `/generate-faq`, `/generate-jsonld` | Handled inline by `/aeko-run-action` or `/aeko-fix-technical` |
| `/create-blog-article`, `/create-social-content`, `/create-marketing-materials` | `/aeko-create-own-content <suggestion_key>` (brand-kit-grounded, tracked-prompt-seeded) |

### Ecosystem rule

If a skill does not call at least one AEKO MCP tool, it should not be an AEKO skill. Generic writing / audit skills that don't ground in your AEKO data (brand kit, tracked prompts, citability scores, visibility evidence) belong outside this plugin — use vanilla Claude for those.

## Relationship to other AEKO repos

- **[`aeko-mcp`](https://github.com/AEKO-Intelligence/aeko-mcp)** — Python MCP server. Hosts the `aeko_*` tools. Embedded in the AEKO backend and exposed at `/mcp`. You don't install this directly; you connect to the hosted endpoint.
- **`aeko-plugin`** (this repo) — Skills only. Distributed via the Claude/Codex plugin marketplaces.

## License

MIT
