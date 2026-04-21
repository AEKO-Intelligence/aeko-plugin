---
name: aeko-fix-store-level
description: >
  Own Store · Store-Level. Generates llms.txt, robots.txt fixes,
  sitemap.xml, and schema infrastructure based on an AEKO v2 store-level
  brief.
argument-hint: <suggestion-key>
allowed-tools: Read, Write, Bash(curl *)
---

# AEKO · Fix Store-Level Infrastructure

You are executing a single `store_level` suggestion from AEKO v2.

## Step 1: Load the brief

Call `aeko_get_store_level_brief(suggestion_key)`. Verify category is `store_level`. The brief will specify:
- `content_type` — one of `llms_txt`, `robots_txt`, `sitemap`, or a schema-infra type
- `target_domain` — the domain to fix
- `structure` and `must_include` — required elements

The brief output also includes a "Recommended chain" section telling you which existing AEKO tools to call next.

## Step 2: Resolve domain_id

You'll need the domain UUID. The brief's "Domain ID" line should surface it. If it's missing from the brief, **ask the user** — there is no URL-to-domain reverse lookup tool; `aeko_get_domain_info` takes a `domain_id` as input, not a URL.

## Step 3: Execute the chain

### If `content_type == "llms_txt"`:
1. `aeko_prepare_llms_txt(domain_id)` — pulls domain info, infrastructure status, and analyzed pages
2. Draft `llms.txt` following the llms.txt spec — title, description, sections, links
3. `aeko_save_content("store_level/llms.txt", <content>)`
4. Tell the user where to deploy it (root of their domain) and to re-run `aeko_validate_llms_txt(<deployed url>)` after upload.
5. **Cafe24 caveat**: Cafe24 hosted stores often can't serve arbitrary files at the domain root. Options: (a) use Cafe24's file manager under `/design/` if reachable at root, (b) deploy via a custom domain + reverse proxy, or (c) host on a subdomain. Warn the user before they try to upload.

### If `content_type == "robots_txt"`:
1. Fetch the current robots.txt via `curl -s <target_domain>/robots.txt` (Bash is allowed)
2. `aeko_prepare_robots_txt_fix(domain_id, current_robots_txt=<content>)`
3. Apply the recommended snippet to the current file
4. `aeko_save_content("store_level/robots.txt", <fixed content>)`
5. Explain which AI crawlers were unblocked

### If `content_type == "sitemap"`:
1. `aeko_get_domain_info(domain_id)` to check current sitemap state
2. Based on `brief.structure` and analyzed pages, generate a valid sitemap.xml
3. `aeko_save_content("store_level/sitemap.xml", <content>)`

### Otherwise (schema infra, e.g. Organization / WebSite JSON-LD):
1. `aeko_prepare_json_ld(domain_id, schema_type=<from brief>)`
2. Generate complete JSON-LD with every field in `brief.must_include`
3. `aeko_save_content("store_level/<schema_type>.jsonld.json", <content>)`

## Step 4: Complete

Call `aeko_complete_suggestion(suggestion_key)`. If the call fails, surface the exact error to the user instead of moving on. Then report:
- The file saved
- Where it needs to be deployed on the user's site
- Any verification command the user should run after deployment
