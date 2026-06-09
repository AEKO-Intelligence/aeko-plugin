---
recipe: robots-txt-patch
purpose: AI-crawler allowlist + patch generation for robots.txt
load_when: SKILL.md §3 dispatches artifact_type=robots_txt_patch or technical_bundle includes it
---

# `robots_txt_patch` recipe

## Spec rules (AI crawler coverage for AEO)

Explain this in marketer language before showing the patch:

- **AI search/shopping visibility** — whether tools like ChatGPT, Claude, Perplexity, Google, and Bing can read public pages for answers, product discovery, and shopping surfaces.
- **AI training/data use** — whether model-training or broad data crawlers may collect public content. This is a separate privacy/business choice.

### Visibility/search bots

Add `Allow: /` blocks for these bots by default when they are missing or implicitly blocked, unless the merchant explicitly asked to block them:

- `OAI-SearchBot`
- `ChatGPT-User`
- `Claude-SearchBot`
- `Claude-User`
- `PerplexityBot`
- `Perplexity-User`
- `Googlebot`
- `Storebot-Google`
- `Bingbot`

### Training/data/control bots

Never newly allow these bots by default. If the current file already allows them, preserve that. If the current file blocks them, preserve that. If the user or Plan explicitly requests training/data access changes, surface it as a consent choice before patching:

- `GPTBot`
- `ClaudeBot`
- `Google-Extended`
- `CCBot`
- `Bytespider`
- `Applebot-Extended`

Do not use the stale token `PerplexityBot-User`; the official user-retrieval token is `Perplexity-User`.

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
   - Adds `User-agent: <crawler>\nAllow: /` blocks for each visibility/search bot missing from the current file when doing so does not override an explicit merchant block.
   - If any visibility/search bot has an explicit `Disallow: /`, stop and ask the user whether they want AI search/shopping tools to read the public site.
   - Preserves training/data/control bot rules untouched unless the user explicitly opts in to changing them.
   - Preserves all existing rules untouched.
   - Adds a single comment header above the new section: `# AEKO: AI search and shopping visibility`.
6. **Optional edge-access hint** (only if Bash/curl is available and the user is comfortable with a network check):
   - Run a light `curl -I -A "<bot user agent>" <site_base_url>` for 2-3 key visibility bots.
   - Report only as: "robots allows; this request was not blocked from your current network" or "this request was blocked from your current network."
   - Never claim this proves real crawler access. WAFs and CDNs may block by IP range, ASN, request pattern, or bot verification, not just user-agent.
7. **Produce** unified diff + final merged file. Honor `must_include` / `forbidden` / `sections_required` (each required section maps to a block with matching user-agent or comment-header label).
8. **Write** both to `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/` as `robots.txt.diff` and `robots.txt`.

## User-facing summary language

Default summary should be plain:

```
What this changes
- Lets AI search/shopping tools read public product and content pages.
- Does not newly allow model-training crawlers.

Risk
- Low for public ecommerce pages; no customer/account/admin paths are opened.
- Confirm with your privacy/legal owner before changing training/data bot rules.

Undo
- Restore the previous robots.txt or apply the reverse diff in robots.txt.diff.
```

## Brand-specific override

If `references/examples/robots-txt-additions-example.txt` exists, append its rules at the end of the patch (after the AEKO visibility block). Useful for brands with custom partner-crawler rules or specific path disallows the recipe doesn't generate.
