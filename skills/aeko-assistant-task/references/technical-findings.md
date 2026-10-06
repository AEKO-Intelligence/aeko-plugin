# Cached product technical findings plan

Use only for `technical.findings_plan.v1` with `scope.selection={mode: explicit, resource: store_products, ids: [...]}` containing 1–20 products. Read each frozen `assistant_product_check` evidence ID and preserve its product ID, cached `aeo_status`, `aeo_checks`, URL, source revision and last-check time. The evidence is a cached structural inspection, not a live crawl or visual review.

Separate confirmed failed checks from analyzing, pending, missing or stale checks. Prioritize repairs by the actual observed issue and likely effort, and give a developer-ready next step for each supported finding. Do not invent an AEO/citability score, infer a product capability from the page URL, or claim that a fix has been deployed. If a check is absent or stale, propose a recheck before asserting current page behavior. Never invoke store-write or publishing tools from this saved task.

Save a cited `report_markdown` repair plan using `[evidence:<UUID>]` IDs from the selected products and pass exactly those cited IDs to `aeko_save_action_output`. The returned plan is for review; any implementation or store edit needs a separate action with its own permissions and receipt.
