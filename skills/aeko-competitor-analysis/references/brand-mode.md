# Brand scope

Produce a competitor-positioning analysis at the **brand level**. Output a clear picture of what the
competitor stands for publicly, where they win AI answers when AEKO evidence is available, and one concrete
action the user could take.

## Marketer-facing output contract

Frame this as "why AI may mention this competitor instead of us." Start with public positioning, AI visibility
gap, and one practical next move. Keep source caveats clear; never imply AEKO has measured a signal when it is
inferred from WebSearch/WebFetch.

Language: mirror the user's chat language for user-facing steps, summaries, questions, and next actions.
Keep slash commands, IDs, file paths, channel slugs, schema keys, and tool names in English/ASCII.

## Inputs

- `domain-id` (optional) — UUID. It is needed only for the connected comparison; never require it before
  public research.
- `competitor` (required) — Competitor name OR root domain (e.g. "필리" or "pilly.co.kr"). Passed as `$1` (if no domain arg) or `$2`.

## Step 1 — Resolve the competitor publicly

Parse the arguments. If the first positional is clearly a UUID, retain it as `domain_id` and use the next
value as the competitor; otherwise treat the positional value as competitor. Do not call AEKO yet.

If competitor is a name (not URL), run a quick `WebSearch` for `"<competitor>" official site` to resolve to a root domain. Confirm with the user if ambiguous.

## Step 2 — Gather public signals on the competitor

Collect in parallel where possible:

1. **Root page crawl** — `WebFetch(<competitor_root>)`. Extract: tagline, hero messaging, top-nav categories, whether llms.txt / structured data is present.
2. **Wikipedia / Wikidata entity check** — `WebSearch("<competitor> site:wikipedia.org")` and `WebSearch("<competitor> site:wikidata.org")`. A matching result is a public entity signal, not proof of model training, embeddings, or citation causation.
3. **Recent news** — `WebSearch("<competitor> news 2026")` (adjust year if needed). Surface any fundraising, product launches, brand refresh.
4. **Press / partnerships** — `WebSearch("<competitor> partnership OR acquired OR launch")` — optional if prose asks for depth.

Record the sources. Do NOT fabricate; if a search returns empty, note that.

## Step 3 — Add AEKO citation data when connected

Only now resolve the user's domain. If `domain_id` is absent, call `aeko_list_domains`; if none are available,
or the connector is missing/returns 401, retain the complete public-signals report and label this section
"AEKO comparison unavailable — no authenticated account." Do not discard Steps 1–2.

1. `aeko_get_domain_info(domain_id)` to ground the "vs us" comparison using names, URLs, keywords, market,
   industry, and surfaced Context.
2. `aeko_get_visibility_summary(domain_id, scope="cited_sources")` — surfaces pages from the user's domain AI engines cite.
3. Call `aeko_get_tracked_prompts` once and select at most ten relevant tracked prompts only when the job
   or returned domain-scoped evidence establishes their relation to this domain. The account-wide list's
   formatter exposes no domain ID; similarity alone cannot establish that relation. If no scoped selection
   is available, mark the prompt comparison unavailable and keep public/domain-level findings. If the tracked
   set is empty, use domain keywords/context with `aeko_search_research_prompts(scope=..., country=...)` as
   a research fallback, but label those rows untracked and do not claim measured history.
4. For each selected tracked prompt:
   - Call `aeko_get_tracked_prompt(prompt_id, window=<supported job window or "30d">)` for cited-source
     analysis. Record actual response dates; do not silently broaden an explicit window.
   - Count how often the competitor's brand name appears in `responses[].mentions`.
   - Count how often the competitor's root domain appears in `responses[].citations[].domain`.
5. Build a comparison matrix:

```
| Prompt | Our mentions | Competitor mentions | Our citations | Competitor citations |
|--------|--------------|---------------------|---------------|----------------------|
| ...    | ...          | ...                 | ...           | ...                  |
```

Rank prompts by `competitor_mentions + competitor_citations - our_mentions - our_citations`. Top rows = prompts where the competitor is winning and the user isn't.

## Step 4 — Write the analysis

Compose a markdown report:

```
# Competitor Analysis: <competitor>
**Against:** <user's brand> (`<domain>`)
**Generated:** <ISO date>

## Public positioning

- **Tagline:** <from hero crawl, or "none found">
- **Top categories:** <from top-nav>
- **Wikipedia entity:** <yes with URL | no>
- **Wikidata entity:** <yes with URL | no>
- **Recent news:** <1-3 headlines, each with date and URL>

## AI visibility footprint vs <user's brand>

(Embed the comparison matrix from Step 3.)

**Interpretation:**
<one paragraph on what the matrix shows — e.g. "The competitor dominates
awareness-stage informational prompts in KR; we're stronger at
recommendation-stage prompts where brand reputation matters. The gap is
most pronounced in the top-3 prompts, where our brand is absent from
AI answers entirely.">

## What the competitor does that we don't

(From Step 2 signals that translate to AEO leverage:)
- Wikipedia entity → an observed public identity reference, with unmeasured model effect
- llms.txt → presence only when the exact resource was fetched within the shared WebFetch cap; a homepage
  link alone is not its contents or proof of AI-readability
- Structured data present → Product / FAQPage / Organization schemas
- Recent news coverage → fresh signal for news-aware AI engines
- **Content frameworks** → where the competitor's *cited pages* win on substance, name it in the plugin's
  AEO vocabulary (BLUF / PREP / Informational Gain / E-E-A-T — see
  `aeo-frameworks.md`) so the gap maps to a fix the executor skills apply.

Flag a difference only when both sides were actually assessed; unavailable user evidence is not absence.
Converted page text alone cannot establish raw JSON-LD absence. Preserve unknown fields instead of
asserting the competitor has markup the user's page lacks.

## Recommended action

<one concrete command the user could run to start closing the gap>
```

## Step 5 — Save + summary

After the entrypoint's exact-report checks, write to
`./aeko-artifacts/<verified-domain-id-or-public>/competitor-analyses/<competitor-slug>-<YYYYMMDD>.md`
when the requested local destination is writable; otherwise render in conversation and state no local
persistence. A public-only run must not guess a brand/domain folder or claim a missing comparison matrix.

User-facing summary:

```
✔ Competitor analysis saved: <path>
  Competitor: <competitor>
  Biggest gap: <top row from Step 3 matrix>
  Next: <recommended action command>
```

## Error paths

- Competitor name ambiguous + WebSearch returns multiple candidates → ask user to pick or paste the root URL directly.
- All cross-reference calls fail, including 401 → still produce the Step 2 / Step 4 public-signals portion;
  note AEKO cited-source data missing.
- No tracked prompts + research-prompt fallback returns empty → note the user's domain doesn't have any tracked-prompt coverage yet; suggest `/aeko-manage-prompts mode=discover` as a prerequisite.

## What this skill never does

- Never silently switches to product scope; use `/aeko-competitor-analysis scope=product`.
- Never fabricates Wikipedia / news findings.
- Never posts anything externally.
- Never mutates tracking state.
