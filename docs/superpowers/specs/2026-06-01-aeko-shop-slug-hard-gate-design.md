# Design — make the aeko_shop English slug a hard gate

Date: 2026-06-01
Repo: `aeko-plugin`
Status: approved (design); pending implementation plan

## Problem

Blog posts published to aeko.shop via `/aeko-create-content` → `/aeko-publish-content`
get **romanized** URL slugs — a phonetic ASCII transliteration of the Korean title
(e.g. `에스테틱 모공팩을 집에서 구매 가이드` → `eseutetig-mogongpaegeul-jibeseo-gumae-gaideu`)
instead of a meaningful English slug (`volcanic-clay-pore-pack-home-guide`).

### Root cause (verified)

The romanization is the **aeko-shop-backend's intended fallback**, not a backend bug.
Commit `fec8e58` deliberately made slug generation ASCII via
`slugify(value, allow_unicode=False)` (python-slugify + text-unidecode) to kill a
Korean-slug 404 class. That fallback fires **only when `PostUpsert.slug` is null**:

- `aeko-shop-backend/app/routes/internal.py:951` — `base = _base_slug(provided_slug or title)`
- `_base_slug` (`internal.py:934-939`) romanizes Korean → ASCII.
- `PostUpsert.slug` (`aeko-shop-backend/app/schemas.py:418-420`) is optional and
  regex-locked to `^[a-z0-9]+(?:-[a-z0-9]+)*$`, so a Korean slug from the caller is
  **structurally impossible** (422). A romanized stored slug therefore *proves* no
  slug reached the backend.

The "send a meaningful English slug" contract breaks **upstream in the plugin**:

- `aeko-create-content/SKILL.md` §5.5.6 tells the model to write an English `slug`
  to `<slug>.meta.json`, but only as "strongly recommended" — there is **no §6.3 hard
  gate** asserting it is present or non-romanized.
- The slug rides only inside the `metadata` dict (no first-class `slug=` arg on
  `aeko_save_content_variation`), so it is easy to silently omit.
- A separate §5.5.3 romanized *filename* slug exists; reusing it for the URL slug
  reproduces the bug exactly (the "two-slug trap").

When the slug is omitted (or the filename slug is reused), the backend romanizes the
Korean title — the reported behavior. Deleting old posts does not help because the
defect is in the live generation path, not stale rows.

### Out-of-scope verification gap (acknowledged)

Two hops live in the **main AEKO backend** (`AEKO_API_URL`, a repo not in this
workspace): whether `/api/content-variations` *persists* an arbitrary `metadata.slug`,
and whether `AekoShopPublisher` *forwards* it into `PostUpsert.slug`. If either drops
it, this plugin fix is necessary but not sufficient, and the fault is server-side
(Codex / backend lane). This is confirmed by a live test publish (see Verification).

## Goal

`/aeko-create-content` must never ship an `aeko_shop` variation without a meaningful
English `metadata.slug`. Enforce it with a hard gate consistent with the existing §6.5
iteration model (regenerate once, then leave the item `pending`).

## Scope

In scope (chosen: "plugin docs only"):
- `skills/aeko-create-content/SKILL.md`
- `skills/aeko-create-content/references/recipes/editorial-html-jsonld.md`

Explicitly out of scope:
- `aeko-mcp` — no first-class `slug=` arg; the slug keeps riding the existing
  `metadata` dict (proven channel, zero save-regression risk).
- `aeko-shop-backend` — correct as-is; modifying it is the Codex/backend lane and
  re-litigates `fec8e58`.
- No fuzzy "looks transliterated" detector (false-positives on legitimate Latin brand
  names such as `colmo`, `slound`, which §5.5.6 explicitly permits).

## Changes

### 1. `SKILL.md` §5.5.6 (lines ~840-847)
Reframe from advisory ("always supply") to **REQUIRED for `aeko_shop` — enforced at
§6.3**. Keep the generation guidance (translate-don't-transliterate; use an
established Latin brand name when one exists; `^[a-z0-9]+(?:-[a-z0-9]+)*$`; ≤70 chars;
drop stop-words). Add: the URL slug **MUST NOT** equal this draft's §5.5.3 romanized
filename `<slug>` token.

### 2. `SKILL.md` §6.3 aeko_shop gate (after the `.meta.json` bullet, line ~934)
Add a hard-gate bullet:

> `.meta.json` `slug` is present, non-empty, matches `^[a-z0-9]+(?:-[a-z0-9]+)*$`,
> **and is not equal to the §5.5.3 romanized filename `<slug>` token**. Hard gate. On
> failure, regenerate per §5.5.6 (one fix iteration per §6.5); if still
> missing/invalid/equal-to-filename-slug, leave the item `pending`.

### 3. `editorial-html-jsonld.md` field tables (lines 170, 403)
Change the `slug` row from "**strongly recommended** (aeko_shop)" to
"**required (aeko_shop)**" in both tables; update the trailing note (the
"Omit → backend transliterates" wording) to state the field is now gated.

### 4. `editorial-html-jsonld.md` acceptance gate (lines ~373-374)
Add `slug` to the `.meta.json` required-fields gate so the recipe's acceptance gate
matches SKILL §6.3 (present + valid pattern + not equal to the filename slug).

## Detection rule (deliberate)

The "bad slug" signal is **equality with the §5.5.3 romanized filename slug *when the
title is non-ASCII (Korean)*** — the concrete, common failure mode — plus presence +
pattern validity. No semantic / dictionary check, to avoid false-positives on allowed
Latin brand names.

**ASCII-title carve-out (added post-review):** §5.5.3 romanization is a no-op for an
already-English `resolved_title`, so its filename slug *is* the meaningful English slug
(e.g. `Summer Cooling Bedding — 2026 Guide` → `summer-cooling-bedding-2026-guide`). A
naked "slug ≠ filename slug" check would hard-fail that legitimate post and park it at
`pending` with no recoverable fix. The equality check therefore fires **only when
`resolved_title` contained a non-ASCII character**; for a pure-ASCII title, a slug equal
to the filename slug passes.

## Error handling

Reuse the existing §6.5 model: hard-gate failure → 1 regenerate iteration → if still
failing, leave the item `pending` (do NOT call `aeko_complete_action_item`), surface
which gate failed. No silent auto-rewrite.

## Verification

A prompt-gate change cannot be unit-tested. Verification is:
1. Doc-consistency self-review (no contradictions between §5.5.6, §6.3, and the recipe
   field tables / acceptance gate; the `aeko_shop-fixture.meta.json` already models a
   correct English slug and should still pass).
2. One live end-to-end publish on a **test item** (with the user's go-ahead): run
   `/aeko-create-content`, confirm `.meta.json.slug` is English and != filename slug,
   `aeko_save_content_variation`, `aeko_publish_content_variation`, then confirm the
   live aeko.shop post slug is the English slug.
3. If `metadata.slug` is present but the post still romanizes → the drop is in the main
   AEKO backend → escalate to Codex (backend lane).
