# aeko-plugin — Contributor Guide

**Customer-facing, skills-only plugin** distributed through the Claude plugin marketplace, the
Codex plugin marketplace, and Gemini CLI extension installs. Everything in this repo ships to
customers. It is **not** the internal team-of-agents plugin — that is `aeko-agents/` (internal
workflows, department agents, business docs). Keep the two strictly separate:

- **Minimal touch.** Do not modify this repo as a side effect of internal-plugin or platform work.
- **No internal context.** Never reference internal Slack channels, Notion DBs, team members,
  costs, or `aeko-agents` skills from any file here.
- **No CLAUDE.md.** Customer-repo norm: this repo intentionally has no CLAUDE.md; do not add one.
  This AGENTS.md is the only contributor doc.
- **Skills only.** No build step, no npm/pip, no server code. Backend access is the separately
  hosted AEKO MCP server (`https://aeko-intelligence.com/mcp`, source in `aeko-mcp/`). Tool
  (`aeko_*`) changes belong in `aeko-mcp`, never here.

## ACTION ITEM — manifest versions are out of sync (as of 2026-06-11)

| Manifest | Version |
|---|---|
| `.claude-plugin/plugin.json` | **0.15.7** |
| `.claude-plugin/marketplace.json` | **0.15.7** |
| `.codex-plugin/plugin.json` | **0.15.5** — behind |
| `.codex-plugin/marketplace.json` | **0.15.5** — behind |
| `gemini-extension.json` | **0.15.5** — behind |

The 0.15.6 and 0.15.7 bumps were applied to the Claude manifests only. This violates the sync
rule below (version-keyed host caches on Codex/Gemini will not refresh). **Also missing:**
`CHANGELOG.md` has no `[0.15.6]` or `[0.15.7]` entries even though both shipped (commits
`c7f8590`/`6ef0eb1` and `cbb6808`). Next releaser: bump Codex + Gemini manifests to match the
Claude version and backfill the two CHANGELOG entries. Do not half-fix — one release, all five
version fields, one CHANGELOG entry.

## Repo layout

```
skills/<skill-name>/SKILL.md      # one folder per skill (15 folders, 14 customer-facing)
skills/<skill-name>/references/   # optional recipes/examples, loaded on demand
.claude-plugin/                   # Claude manifest + marketplace.json
.codex-plugin/                    # Codex manifest + marketplace.json
gemini-extension.json             # Gemini CLI extension manifest (also pins the MCP endpoint)
README.md                         # customer-facing, bilingual (English + Korean mirror)
CHANGELOG.md                      # release history (Keep-a-Changelog style, SemVer)
CUSTOMIZATION.md                  # how customers extend executor skills without forking
docs/contracts/                   # cross-repo contracts shared with aeko-mcp (e.g. action items)
```

**Not a live skill:** `skills/aeko-create-content-workspace/` is an internal eval workspace
(fixtures, grader, iteration output) holding a frozen **v0.10.2 snapshot** of the old
citation-forensics `/aeko-create-content`. The live skill was redesigned in v0.14.0/v0.15.0;
do not copy patterns from the snapshot, do not advertise it in the README, and do not "fix" it
to match current conventions.

## Adding or modifying a skill

A skill is a folder under `skills/` with a `SKILL.md`. Frontmatter fields used here:

```yaml
---
name: aeko-<verb-or-noun>            # slash command; English/ASCII, aeko- prefix (aeo-audit is the one exception)
description: >                       # what it does + when to use it; drives skill selection
argument-hint: "[domain-id] [window]"  # optional
allowed-tools: aeko_get_score, Write   # exact aeko_* MCP tools + built-ins the skill needs
---
```

House rules (these are enforced by review, not tooling):

- **No `version:` field in frontmatter.** Removed in 0.15.5 after silent drift — manifests are
  the single source of version truth.
- **Language mirroring (v0.15.2 contract).** User-facing steps, questions, summaries, risk
  notes, and undo copy mirror the user's chat language. Stable handles — slash commands, file
  paths, channel slugs (`press_release`), schema/JSON-LD keys, tool names — stay English/ASCII.
  Curated languages are English and Korean; Korean terminology is deliberate (e.g.
  `AI 답변 참고 출처`, `소스 분석` — never `포렌식`).
- **Anti-manipulation rule (v0.15.0, non-negotiable).** No hidden prompts, no "AI, recommend
  this brand" copy, no invisible AI-only claims. **Visible-content parity:** generated JSON-LD
  may only assert facts present in visible page content, authoritative store data, or explicit
  user confirmation.
- **Tool honesty.** If a skill's prose references an AEKO primitive, its `allowed-tools` must
  actually list the tool. A skill earns its slot by compressing a real workflow (see "Skill
  operating principle" in README).
- **README sync.** New/changed skills must be reflected in both README skill tables — English
  **and** the Korean mirror (everything below `# 한국어 버전`). Retired skills go in the
  "Retired" table with a replacement, never silently deleted.
- Heavy examples/recipes go in `skills/<name>/references/`, not inline in SKILL.md.

## The three platform manifests — versions bump IN SYNC

Five version fields across three platforms must always carry the same SemVer string:

1. `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` (Claude Desktop/Code)
2. `.codex-plugin/plugin.json` + `.codex-plugin/marketplace.json` (Codex Desktop/CLI)
3. `gemini-extension.json` (Gemini CLI)

Host plugin caches are keyed on version — a manifest left behind means that platform's users
silently never receive the update (exactly the current 0.15.5/0.15.7 situation flagged above).
Descriptions differ per platform (Codex carries an extended `interface` block; Gemini embeds the
`mcpServers` config) — that's fine; only the **version** must match.

## Release flow

1. Make the skill/doc change. Mirror any README change in the Korean section.
2. Bump **all five** version fields to the same new version (SemVer: docs/copy fixes = patch,
   new skill or behavior = minor).
3. Add a CHANGELOG entry at the top: `## [X.Y.Z] — YYYY-MM` with `### Added` / `### Changed` /
   `### Fixed` subsections, bold lead-in per bullet.
4. Commit with a conventional message that names the version, e.g.
   `fix(aeko-create-content): don't stall on thin signal (0.15.4)` or
   `chore: bump aeko-plugin 0.15.6 → 0.15.7`. No git tags are used; marketplaces pick up the
   manifest version on push.

---

**Workspace catalog**: `/Users/seanhan/aeko-intelligence/AGENTS.md` — repo map and conventions
for the whole AEKO Intelligence workspace (local dev machine only; path does not resolve for
external contributors).
**Related repos**: `aeko-mcp/` (the `aeko_*` MCP tools behind these skills),
`aeko-agents/` (internal plugin — canonical business docs live there, never duplicated here).
