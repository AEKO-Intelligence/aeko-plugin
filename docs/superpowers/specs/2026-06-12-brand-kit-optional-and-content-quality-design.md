# Brand-Kit-Optional Publishing + Content-Quality Upgrades — Design

**Date:** 2026-06-12
**Author:** Sean (CTO) + Claude
**Repos touched:** `aeko` (backend), `aeko-plugin` (skills). **No `aeko-shop` change.**
**Status:** Approved design → ready for implementation plan.

---

## 1. Summary

Three changes, from three CTO directives:

1. **Image-only product pages must still yield the substance** — especially clinical/test
   results and numeric/data evidence — instead of being silently skipped. *(plugin)*
2. **Content must read realistically and trustworthily** — name real trade-offs/limitations,
   not advantages-only hype. *(plugin)*
3. **Publishing must work without a Brand Kit** — genuinely remove the requirement, with the
   verified **domain + AEKO user** as the identity. *(backend + plugin)*

Directive 3 was believed already done; investigation showed it was **not** — only the separate
aeko.shop *connect-brand claim* nudge was suspended (2026-06-11). The **Brand Kit itself is still
hard-required** to create PDP plans and to save/publish content. This spec removes that for real.

---

## 2. Background — what is actually enforced today

The Brand Kit is required at four points in `aeko/aeko_backend`:

| # | Location | Behavior |
|---|---|---|
| B1 | `api/routes/action_items.py:668` → `_resolve_brand_kit_snapshot(required=True)` | `pdp_html` sets `responsive_html_required=True` ⇒ `requires_brand_kit=True` ⇒ creating a PDP plan with no kit raises **409 `BRAND_KIT_REQUIRED`** (`action_items.py:230-238`). |
| B2 | `api/routes/content_variations.py:235-242` | Saving an `aeko_shop` variation whose item has no `brand_kit_id` → **422**. Backed by DB CHECK constraint. |
| B3 | `api/routes/content_variations.py:503-507`, `571-575` | Publishing `aeko_shop` with no `brand_kit_id`, or kit unloadable, → **422**. |
| B4 | `api/routes/content_variations.py:705-711` | `own_store_blog` publish with no `brand_kit_id` → **422** (column is NOT NULL). |

Schema backing:
- CHECK `ck_content_variations_brand_kit_required_for_aeko_shop` — predicate
  `(destination='aeko_shop' AND brand_kit_id IS NOT NULL) OR destination!='aeko_shop'`
  (`models.py:2467`, migration `a1c2e4f6b8d0`). `content_variations.brand_kit_id` is itself nullable.
- `aeko_content_drafts.brand_kit_id` **NOT NULL**, FK `ondelete=RESTRICT`
  (`models.py:2516`, migration `b2d4f6a8c0e2`).

**Key architectural fact (the unlock):** the aeko.shop publisher already resolves a brand **by its
store domain**, not by the kit. `aeko_shop_publisher.sync_brand` POSTs `slug` (from `domain.name`)
and `primary_url` (from `domain.base_url`) to `/internal/brands`; aeko.shop returns the canonical
domain-resolved brand id (`aeko_shop_publisher.py:140-148`). The Brand Kit is merely the **carrier**
of display fields (name/tagline/logo/about) + the **voice** for generation. So the verified domain
is the real identity, and removal is **AEKO-backend-only**.

---

## 3. Goals / Non-goals

**Goals**
- A user with a verified (owned) domain can create PDP/content plans, save, and publish to both
  `aeko_shop` and `own_store_blog` **with no Brand Kit**.
- When a kit exists, behavior is **unchanged** (kit enriches the public brand page + steers voice).
- Image-only PDPs surface clinical/test/numeric evidence in generated content.
- Generated content names realistic trade-offs/limitations by default.

**Non-goals (explicitly out of scope)**
- The **Pro/Enterprise tier gate** on aeko.shop publish stays (`enforce_publish_gate`,
  `aeko_shop_publisher.py:179-180`). It is the billing boundary, not the brand kit.
- No `aeko-shop` repo changes (domain-keyed brand resolution already exists there).
- No change to how kits are *created/edited* (`aeko-brand-kit` skill, brand-kit routes) beyond
  making them optional downstream.

---

## 4. Part A — Backend: Brand Kit optional, domain as identity

### A1. `requires_brand_kit` no longer auto-true for PDP
`action_items.py:668` becomes:
```python
requires_brand_kit = payload.brand_kit_id is not None
```
i.e. only true when the caller explicitly attaches a kit. Drops the `responsive_html_required`
clause. Effect: PDP/responsive plans stop 409-ing; `_resolve_brand_kit_snapshot` already returns
`(None, None)` when `required=False` and no id is passed (`action_items.py:216-218`), so the item is
created with `brand_kit_id=None`, `requires_brand_kit=False`. Plan.md frontmatter then carries
`requires_brand_kit: false`, which the plugin honors (Part B).

### A2. Introduce a `BrandIdentity` value object
The publisher currently demands a `BrandKits` ORM row. Replace that coupling with a small derived
identity the publisher consumes:

```
BrandIdentity:
  shop_brand_key: UUID        # kit.aeko_shop_brand_id or kit.id, else domain.id  (rate-limit/audit + _shop_brand_id)
  name: str                   # kit.brand_name else domain.name/title else slug
  slug_hint: str              # domain.name else _slugify(name)
  tagline: str | None         # kit only
  about_md: str | None        # kit only
  logo_url: str | None        # kit only
  hero_image_url: str | None  # kit only
  primary_url: str | None     # domain.base_url
  domain_id: UUID | None      # for product/integration resolution (sync_products)
  aeko_shop_disabled: bool    # kit only, else False
```
A builder resolves it from `(domain, optional brand_kit)`. When a kit is present, fields come from
the kit exactly as today (zero behavior change); when absent, from the `Domains` row. Every action
item already carries a verified `domain_id` (ownership enforced at create via
`_verify_domain_ownership`), so a domain is always available.

### A3. Decouple the publisher
`aeko_shop_publisher.py` methods that take `brand_kit: BrandKits` now take `identity: BrandIdentity`:
- `sync_brand` — build the `/internal/brands` payload from `identity` (null optional fields when no
  kit; aeko.shop upsert tolerates nulls / preserves prior values). Write the resolved id back onto
  the kit **only when a kit exists**.
- `_shop_brand_id` → `identity.shop_brand_key`.
- `enforce_publish_gate` / `_enforce_rate_limit` → key on `identity.shop_brand_key`.
- `record_audit` → `brand_id = identity.shop_brand_key`.
- `sync_products` → uses `identity.domain_id` (already domain-based).
- `presign_media_upload` → `identity` (media scope = shop_brand_key).

### A4. Remove the route gates (`content_variations.py`)
- **B2 (235-242):** delete the save-time 422. Saving with no kit is allowed.
- **B3 (`_publish_aeko_shop`, 503-507 & 571-575):** replace "missing brand_kit_id" 422 + mandatory
  `load_brand_kit_for_user` with: load the kit **iff** `row.brand_kit_id` is set; build a
  `BrandIdentity` from `(domain, kit-or-None)`; pass identity to the publisher.
- **B4 (`own_store_blog`, 705-711):** delete the 422; insert the draft with `brand_kit_id=None`
  when absent.

### A5. Alembic migrations (two, additive/relaxing — safe on existing rows)
1. **Drop the CHECK** `ck_content_variations_brand_kit_required_for_aeko_shop`
   (`op.drop_constraint(..., type_="check")`). Remove the matching `CheckConstraint` from
   `models.py` `ContentVariation.__table_args__`. Downgrade re-adds it.
2. **`aeko_content_drafts.brand_kit_id` → nullable.** `op.alter_column(..., nullable=True)`; relax
   FK `ondelete RESTRICT → SET NULL` for consistency with the now-optional link. Update
   `models.py:2516` to `Mapped[Optional[uuid.UUID]]`. Downgrade reverses (guard: only if no NULLs).

   Existing rows all have `brand_kit_id` populated, so both migrations are non-destructive.

### A6. Tier gate retained
No change to `enforce_publish_gate`'s Pro/Enterprise check. A Starter user still gets 403 on
aeko.shop publish — unrelated to the kit.

### A7. Tests (`aeko_backend/tests`)
- `test_content_variation_publish_errors.py`: the existing tests seed a `BRAND_KIT_ID` and assert
  the 422s. Update those assertions (kit-less is now allowed) and **add** kit-less paths: save +
  publish `aeko_shop` and `own_store_blog` with `brand_kit_id=None`, asserting success and that the
  publisher is called with a domain-derived identity.
- `test_plan_md.py` / action-item create: add a `pdp_html` create with no kit → expect 201 +
  `requires_brand_kit=False` (not 409).
- A focused unit test for the `BrandIdentity` builder: kit-present vs kit-absent field mapping.
- Keep one test asserting the **tier** gate still 403s without a kit (proves we removed the kit gate,
  not the billing gate).

---

## 5. Part B — Plugin: Brand Kit optional in generation

- `aeko-update-pdp/SKILL.md` **Step 2 (lines 58-64):** when `requires_brand_kit==false` (the new
  default) **or** the kit can't be resolved, **do not stop**. Proceed with a neutral,
  product-grounded voice and emit a one-line "no brand kit — using a neutral product-led voice;
  add a Brand Kit for on-brand tone" note. Keep the existing path when a kit *is* present.
- `aeko-fix-technical/SKILL.md` **line 79:** same softening.
- `aeko-create-content/SKILL.md`: already tolerant (resolves in order, warns-but-continues) — tighten
  wording so "no kit is fine" is explicit; ensure the no-kit voice fallback is stated.
- `aeko-create-content-workspace/skill-snapshot/SKILL.md` (line 142): eval fixture — update for
  parity so evals reflect the new optional behavior. *(low priority; note if deferred)*

---

## 6. Part C — Plugin: content-quality directives

### C1. Image-only pages → always extract the substance (Directive 1)
- **`aeko-create-content/SKILL.md` Step 3 (substance):** after `aeko_get_product_description`, detect
  image-only/thin sources — `full_description` empty or `< ~200` words while `image_url`/product
  page images exist. For those, `WebFetch` the product page, save images, open them with native
  `Read` (Claude vision) and extract substantive text, **prioritizing**: clinical/test results,
  lab/efficacy data, percentages, ingredient amounts/concentrations, certifications, before/after
  numbers, pricing. Merge into `products[].ocr_text`; flag `ocr_failed` when it can't. (Skill already
  has `WebFetch`/`Read`/`Bash`; no new tools.)
- **`aeko-create-content/references/drafter-instructions.md`:** document `ocr_text` in the brief and
  instruct drafters to treat extracted clinical/numeric evidence as **primary** substance for PREP
  examples and E-E-A-T FAQ answers.
- **`aeko-update-pdp/SKILL.md` Step 4 (OCR, line 117-119):** add explicit "prioritize and preserve
  clinical/test results and numeric/data evidence verbatim (values, units, %s); never round away or
  drop figures."
- **`aeko-create-content/references/aeo-frameworks.md` anti-fabrication rule:** extend to image
  sources — when evidence exists only in images, extract it via vision; **never** infer category-
  typical numbers from memory. Cite origin ("from the test certificate / packaging / label").
  Add a short note that data/numeric evidence is a high-citability signal.

### C2. Realistic, balanced writing (Directive 2)
The canonical `aeo-frameworks.md` already mandates honest trade-offs (E-E-A-T §4) and decision blocks
(§5) — but as *optional/conditional*. Elevate to a default principle:
- **`aeo-frameworks.md`:** add a first-class "Balanced positioning" subsection (under §4 or a new
  short section) — name 2-3 real trade-offs/limitations grounded in specs/reviews; AI engines and
  shoppers trust balance over hype; "best for X / not for Y" is a citation signal, not a weakness.
  Add a matching line to the **Quick self-check**. (Canonical → propagates to create-content,
  update-pdp, and the `aeo-audit` rubric.)
- **`drafter-instructions.md` §2 (Process/Draft):** make balanced positioning an active drafting task
  (include a trade-off/"not-for" beat when substance supports it; honest, not invented).
- **`aeko-update-pdp/references/recipes/json-ld-schemas.md` FAQ section:** reinforce that honest
  limitations beat marketing lines (the existing "2% shrinkage" example), framed as AEO strength.
- Guardrail: do **not** fabricate limitations; if a product genuinely has none in a dimension, say so
  honestly rather than inventing a flaw (ties to the anti-fabrication rule).

---

## 7. Risks & mitigations

| Risk | Mitigation |
|---|---|
| aeko.shop `/internal/brands` rejects null optional fields (tagline/logo/about) | Verify during impl; send domain-derived `name`/`slug`/`primary_url` (always non-null) and omit/null the rest. aeko.shop already upserts by domain. |
| Public brand page shows a bare domain-derived name until a kit is added | Acceptable per CTO; the "add a Brand Kit for on-brand tone" note nudges enrichment. |
| Migration on a busy table | Both are constraint-drop / nullable-relax — metadata-only, no row rewrite; existing rows already satisfy them. |
| aeko repo has unrelated WIP on `main` | Implement on dedicated feature branches; never touch the in-flight files. |
| Vision OCR token cost on many product images | Cap images per product; only trigger on thin/image-only detection, not every run. |
| Drafters inventing trade-offs to satisfy the balance rule | Explicit anti-fabrication guard in C2; balance must trace to specs/reviews. |

---

## 8. Sequencing

1. **Backend (aeko branch):** A1 → A2/A3 (publisher) → A4 (routes) → A5 (migrations + models) → A7
   (tests green).
2. **Plugin (aeko-plugin branch):** B (hard-stops) + C1 + C2. Independent of backend; can land in
   parallel. Skill prose has no test suite — rely on careful review + the QA skill.
3. Backend and plugin are separate deployables/commits; the plugin's "publish without a kit" promise
   is only fully true once the backend ships.

---

## 9. Acceptance criteria

- Verified-domain user with **no kit**: create PDP plan (201), save + publish `aeko_shop` (live URL
  returned), save + publish `own_store_blog` (draft row created) — all succeed; tier gate still
  applies. Kit-present flows unchanged.
- Image-only PDP run surfaces ≥1 clinical/numeric figure traceable to a product image.
- Generated PDP/content includes ≥1 honest trade-off/limitation grounded in substance.
