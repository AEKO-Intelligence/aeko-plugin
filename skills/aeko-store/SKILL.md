---
name: aeko-store
description: >
  Interactive AEKO domain/manual-catalog setup and Pro+ real-review intake.
  Use mode=setup for domains, dashboard-connected store sync, manual products,
  account markets, quota, and starter prompts; use mode=reviews for verified
  merchant-provided or public-source reviews. Never accepts credentials or
  fabricates products/reviews, and confirms every live write in the same turn.
argument-hint: "[mode=setup|reviews] [domain-id-or-url]"
allowed-tools: aeko_list_domains, aeko_add_domain, aeko_get_domain_info, aeko_list_store_integrations, aeko_sync_store, aeko_inject_products, aeko_list_store_products, aeko_get_current_markets, aeko_update_markets, aeko_get_quota, aeko_generate_starter_prompts, aeko_accept_starter_prompts, aeko_list_review_integrations, aeko_inject_reviews, WebSearch, WebFetch, Read
---

# AEKO Store

Own two related workflows without blurring their safety rules: initial domain/store setup and real-review
intake. Mirror the user's chat language for questions, confirmations, errors, and summaries. Keep IDs,
country codes, platform values, product keys, JSON fields, paths, slash commands, and tool names in
English/ASCII. The brand mark is always `AEKO`.

If invoked from a schedule, routine, cron wrapper, or any context without a present user, stop immediately.
Neither mode has a non-interactive bypass: each live write requires a fresh, same-turn human confirmation.

## Select one mode

- `mode=setup` — add/select a domain, sync a dashboard-connected Cafe24/Shopify store or inject manual products, verify
  products, set markets, inspect quota, and generate/accept starter prompts. Read
  `references/setup-mode.md` completely.
- `mode=reviews` — collect only genuine merchant-provided or public-source reviews, normalize and preview
  them, then inject into the manual review source. Read `references/review-intake-mode.md` completely.

Infer reviews mode from an explicit request to import/inject reviews; otherwise default to setup. Never run
both write flows behind one confirmation.

## Review intake boundary

`aeko_inject_reviews` is the **only review intake available to an agent**. AEKO deliberately does not expose
cre.ma, Judge.me, Cafe24, or any other review-platform credential connection/sync flow through MCP. Do not
imply those services can be connected here: direct the user to the AEKO dashboard for credentialed review
integrations, or use `mode=reviews` for the credential-less manual source.

Apply the same secret boundary to store OAuth tokens. Never ask a user to paste a Cafe24/Shopify access or
refresh token into chat and never call a token-bearing connect tool. Connection is dashboard-only; the
credential-less manual product path remains available here.
