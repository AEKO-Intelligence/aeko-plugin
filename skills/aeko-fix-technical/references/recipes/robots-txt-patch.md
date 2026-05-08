---
recipe: robots-txt-patch
purpose: AI-crawler allowlist + patch generation for robots.txt
load_when: SKILL.md §3 dispatches artifact_type=robots_txt_patch or technical_bundle includes it
---

# `robots_txt_patch` recipe

## Spec rules (AI-crawler coverage for AEO)

The AI crawlers AEKO cares about:

- `GPTBot`
- `ChatGPT-User`
- `OAI-SearchBot`
- `ClaudeBot`
- `Claude-User`
- `Google-Extended`
- `PerplexityBot`
- `PerplexityBot-User`
- `Applebot-Extended`
- `CCBot`
- `Bytespider`

**Allow** these crawlers by default unless the merchant has explicit reason to block.

## Cafe24 hosting caveat

Some Cafe24 plans auto-inject a restrictive `robots.txt` that blocks non-standard user agents. If the current file looks auto-generated (starts with `# Cafe24` or has a single `Disallow: /admin` block), advise the user that their robots.txt may need to be patched via the Cafe24 admin, not file upload.

## Generation

1. **Resolve `site_base_url`:**
   - Required per contract §4.2. If missing or malformed → stop with: "site_base_url not set on this item; backend must populate the site origin."
   - Derive `{site_base_url}/robots.txt`.
2. **Fetch current robots.txt** via `WebFetch`. On 404 or empty → treat as empty baseline (legitimate case).
3. **On fetch failure** (timeout, non-200, non-404) → ask user in `target_language`: "Couldn't read <url>. Paste your current robots.txt, or confirm the site has none."
4. **Parse** the current file into rule groups (User-agent + Allow/Disallow blocks).
5. **Compute a patch** that:
   - Adds `User-agent: <crawler>\nAllow: /` blocks for each AI crawler missing from the current file (unless a `Disallow: /` rule explicitly targets that crawler — in which case surface the conflict and ask the user).
   - Preserves all existing rules untouched.
   - Adds a single comment header above the new section: `# AEKO: AI crawler allowlist`.
6. **Produce** unified diff + final merged file. Honor `must_include` / `forbidden` / `sections_required` (each required section maps to a block with matching user-agent or comment-header label).
7. **Write** both to `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/` as `robots.txt.diff` and `robots.txt`.

## Brand-specific override

If `references/examples/robots-txt-additions-example.txt` exists, append its rules at the end of the patch (after the AEKO allowlist block). Useful for brands with custom partner-crawler rules or specific path disallows the recipe doesn't generate.
