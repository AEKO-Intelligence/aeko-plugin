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

See [`skills/`](skills/). Each is a self-contained SKILL.md consumed by Claude or Codex. Examples:

- `/aeko-action-center` — surface your top AEKO action items
- `/aeko-brand-kit` — view or edit your domain's brand kit
- `/aeko-run-action` — execute a specific action item end-to-end
- `/aeko-optimize-pdp` — rewrite a product page for AEO
- `/aeko-update-pdp` — incremental PDP updates from a v2 brief
- `/aeko-create-own-content` — draft own-site content from a v2 brief
- `/aeo-audit` — audit a page for AI-citability

## Relationship to other AEKO repos

- **[`aeko-mcp`](https://github.com/AEKO-Intelligence/aeko-mcp)** — Python MCP server. Hosts the `aeko_*` tools. Embedded in the AEKO backend and exposed at `/mcp`. You don't install this directly; you connect to the hosted endpoint.
- **`aeko-plugin`** (this repo) — Skills only. Distributed via the Claude/Codex plugin marketplaces.

## License

MIT
