# aeko_shop English Slug Hard Gate — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `/aeko-create-content` enforce a meaningful English `aeko_shop` URL slug via a hard gate, so the shop backend's Korean-title romanization fallback stops firing on normal publishes.

**Architecture:** Pure prompt/skill edits in `aeko-plugin`. Promote the §5.5.6 English slug from advisory to a §6.3 hard gate, add a recipe gate that matches, and flip the recipe field tables from "strongly recommended" to "required". The slug keeps traveling inside the existing `metadata` dict (no `aeko-mcp`/backend change). Detection rule: present + valid `^[a-z0-9]+(?:-[a-z0-9]+)*$` + **not equal to the §5.5.3 romanized filename slug *when the title is non-ASCII (Korean)*** (no fuzzy transliteration check — it would false-positive on legit Latin brand names; the non-ASCII condition avoids false-positiving on already-English titles whose filename slug is itself meaningful).

**Tech Stack:** Markdown skill files; `grep` for verification; git for the final commit.

**Spec:** `docs/superpowers/specs/2026-06-01-aeko-shop-slug-hard-gate-design.md`

---

## File Structure

- Modify: `skills/aeko-create-content/SKILL.md` — §5.5.6 (slug generation) and §6.3 (aeko_shop acceptance gates)
- Modify: `skills/aeko-create-content/references/recipes/editorial-html-jsonld.md` — `.meta.json` field tables (×2) and the aeko_shop acceptance gate

All paths are relative to the `aeko-plugin` repo root: `/Users/seanhan/aeko-intelligence/aeko-plugin`.

---

### Task 1: §5.5.6 — promote slug to REQUIRED + ban filename-slug reuse

**Files:**
- Modify: `skills/aeko-create-content/SKILL.md` (§5.5.6, ~lines 840-847)

- [ ] **Step 1: Replace the §5.5.6 heading + intro line**

Find:
```
#### 5.5.6 aeko_shop publish slug (meaningful English) — `aeko_shop` only

The §5.5.3 slug is romanized for **local file organization**. The **published aeko.shop URL** uses a *separate* slug carried in `<slug>.meta.json`'s top-level `slug` field. Do **NOT** reuse the romanized filename slug for the URL — for a Korean title it transliterates to phonetic gibberish (`eseutetig-mogongpaegeul-…`) that reads as noise to humans and AI engines. Instead, write a **meaningful English** slug:
```

Replace with:
```
#### 5.5.6 aeko_shop publish slug (meaningful English) — `aeko_shop` only

**REQUIRED for `aeko_shop` — enforced as a hard gate at §6.3.** The §5.5.3 slug is romanized for **local file organization** only. The **published aeko.shop URL** uses a *separate* slug carried in `<slug>.meta.json`'s top-level `slug` field. Do **NOT** reuse the romanized §5.5.3 filename slug for the URL — for a Korean title it transliterates to phonetic gibberish (`eseutetig-mogongpaegeul-…`) that reads as noise to humans and AI engines, and the §6.3 gate rejects a `slug` equal to the filename slug. Write a **meaningful English** slug:
```

- [ ] **Step 2: Update the closing item (4) to state enforcement**

Find:
```
4. The aeko.shop backend uses this as the post's URL slug and enforces uniqueness (appends `-2`/`-3` on collision). If you omit `slug`, the backend falls back to an ASCII transliteration of the title — valid and routable, but less readable, so always supply a meaningful English slug for `aeko_shop`.
```

Replace with:
```
4. The aeko.shop backend uses this as the post's URL slug and enforces uniqueness (appends `-2`/`-3` on collision). Omitting `slug` (or reusing the §5.5.3 romanized filename slug) makes the backend fall back to an ASCII transliteration of the Korean title — phonetic gibberish. This is a **hard gate** (§6.3): for `aeko_shop` you MUST write a meaningful English `slug` that is not the filename slug, or the draft fails and the item stays `pending`.
```

- [ ] **Step 3: Verify the edit landed**

Run: `cd /Users/seanhan/aeko-intelligence/aeko-plugin && grep -nE "REQUIRED for .aeko_shop. — enforced as a hard gate at §6.3|the §6.3 gate rejects a .slug. equal to the filename slug|This is a \*\*hard gate\*\* \(§6.3\)" skills/aeko-create-content/SKILL.md`
Expected: 3 matching lines printed (one per inserted phrase).

---

### Task 2: §6.3 — add the slug hard-gate bullet

**Files:**
- Modify: `skills/aeko-create-content/SKILL.md` (§6.3 "Channel `aeko_shop`", immediately after the `.meta.json exists and parses` bullet, ~line 934)

- [ ] **Step 1: Insert the new hard-gate bullet after the existing `.meta.json` bullet**

Find (the existing bullet to anchor on):
```
- `<slug>.meta.json` exists and parses with `json.loads`. Required fields present; all values within their `PostUpsert` constraints (recipe's "`<slug>.meta.json`" §). Hard gate.
```

Replace with (original bullet, then the new bullet):
```
- `<slug>.meta.json` exists and parses with `json.loads`. Required fields present; all values within their `PostUpsert` constraints (recipe's "`<slug>.meta.json`" §). Hard gate.
- `<slug>.meta.json` `slug` is present, non-empty, matches `^[a-z0-9]+(?:-[a-z0-9]+)*$`, **and is NOT equal to this draft's §5.5.3 romanized filename `<slug>` token** (reusing the romanized filename slug is the failure mode that produces phonetic-gibberish URLs). Hard gate. On failure, regenerate a meaningful English slug per §5.5.6 (one fix iteration per §6.5); if it is still missing, invalid, or equal to the filename slug, leave the item `pending`.
```

- [ ] **Step 2: Verify the bullet landed exactly once**

Run: `cd /Users/seanhan/aeko-intelligence/aeko-plugin && grep -c "is NOT equal to this draft's §5.5.3 romanized filename" skills/aeko-create-content/SKILL.md`
Expected: `1`

- [ ] **Step 3: Verify it sits inside the aeko_shop gate block (after §6.3 heading, before §6.4)**

Run: `cd /Users/seanhan/aeko-intelligence/aeko-plugin && awk '/^### 6.3 /{f=1} /^### 6.4 /{f=0} f && /is NOT equal to this draft/{print NR": "$0}' skills/aeko-create-content/SKILL.md`
Expected: one line printed with a line number between the §6.3 and §6.4 headings.

---

### Task 3: Recipe field tables — "strongly recommended" → "required"

**Files:**
- Modify: `skills/aeko-create-content/references/recipes/editorial-html-jsonld.md` (the `.meta.json` field table ~line 170, and the field-mapping table ~line 403)

- [ ] **Step 1: Update the `.meta.json` field table row (~line 170)**

Find:
```
| `slug` | **strongly recommended** (`aeko_shop`) | str \| null | A **meaningful English** slug (translate, don't transliterate) — see SKILL.md §5.5.6. Must match `^[a-z0-9]+(?:-[a-z0-9]+)*$` (lowercase ASCII, hyphen-separated; ≤220). Becomes the post URL slug (backend appends `-2`/`-3` on collision). Omit → backend transliterates the title to ASCII (routable but phonetic). **Never Korean/non-ASCII** — the backend rejects it (422). |
```

Replace with:
```
| `slug` | **required (`aeko_shop`)** | str | A **meaningful English** slug (translate, don't transliterate) — see SKILL.md §5.5.6. Must match `^[a-z0-9]+(?:-[a-z0-9]+)*$` (lowercase ASCII, hyphen-separated; ≤220) and must NOT be the §5.5.3 romanized filename slug. Becomes the post URL slug (backend appends `-2`/`-3` on collision). Enforced by the SKILL §6.3 hard gate — omitting it (or reusing the filename slug) fails the draft. **Never Korean/non-ASCII** — the backend rejects it (422). |
```

- [ ] **Step 2: Update the field-mapping table row (~line 403)**

Find:
```
| `slug` | `slug` | strongly recommended — meaningful English slug (§5.5.6); lowercase-ASCII `^[a-z0-9]+(?:-[a-z0-9]+)*$`. Omit → backend transliterates the title. |
```

Replace with:
```
| `slug` | `slug` | **required (aeko_shop)** — meaningful English slug (§5.5.6); lowercase-ASCII `^[a-z0-9]+(?:-[a-z0-9]+)*$`, not the §5.5.3 filename slug. Enforced by SKILL §6.3 hard gate; omit → fails the draft. |
```

- [ ] **Step 3: Verify both rows now say required and neither says "strongly recommended" for slug**

Run: `cd /Users/seanhan/aeko-intelligence/aeko-plugin && grep -nE "^\| \`slug\`" skills/aeko-create-content/references/recipes/editorial-html-jsonld.md`
Expected: 2 lines, both containing `required (`aeko_shop`)` / `required (aeko_shop)`, neither containing `strongly recommended`. (Other table rows where `slug` appears as a sub-field of `featured_products` are unaffected.)

---

### Task 4: Recipe acceptance gate — add slug to the `.meta.json` gate

**Files:**
- Modify: `skills/aeko-create-content/references/recipes/editorial-html-jsonld.md` (aeko_shop acceptance gate, ~lines 373-374)

- [ ] **Step 1: Insert a slug gate line after the `.meta.json` validates bullet**

Find:
```
- `<slug>.meta.json` validates against the `PostUpsert` shape table in §"`<slug>.meta.json`" above: required fields present, every field within its constraint (length, count caps, absolute-https origin for `hero_image_url`, valid `locale`, valid `product_source_id` length, etc.).
```

Replace with:
```
- `<slug>.meta.json` validates against the `PostUpsert` shape table in §"`<slug>.meta.json`" above: required fields present, every field within its constraint (length, count caps, absolute-https origin for `hero_image_url`, valid `locale`, valid `product_source_id` length, etc.).
- `<slug>.meta.json` `slug` is present, matches `^[a-z0-9]+(?:-[a-z0-9]+)*$`, and is NOT the §5.5.3 romanized filename slug (mirrors SKILL §6.3 hard gate). **Hard gate.**
```

- [ ] **Step 2: Verify the gate line landed**

Run: `cd /Users/seanhan/aeko-intelligence/aeko-plugin && grep -nE "mirrors SKILL §6.3 hard gate" skills/aeko-create-content/references/recipes/editorial-html-jsonld.md`
Expected: 1 matching line.

---

### Task 5: Cross-file consistency check + fixture sanity

**Files:** none modified (verification only)

- [ ] **Step 1: Confirm the fixture still satisfies the new gate (present, valid, English)**

Run: `cd /Users/seanhan/aeko-intelligence/aeko-plugin && grep -nE '"slug"' skills/aeko-create-content/references/examples/aeko_shop-fixture.meta.json`
Expected: a line like `"slug": "merino-cooling-sleepwear-summer-bedding-data",` — lowercase ASCII, hyphenated, clearly English (not a romanization). If the fixture lacks a `slug` or has a romanized one, update it to a meaningful English slug so the canonical example passes the new gate.

- [ ] **Step 2: Confirm no remaining "strongly recommended" wording for the URL slug**

Run: `cd /Users/seanhan/aeko-intelligence/aeko-plugin && grep -rniE "slug.*strongly recommended|strongly recommended.*slug" skills/aeko-create-content/`
Expected: no output (zero matches).

- [ ] **Step 3: Confirm §5.5.6 ↔ §6.3 ↔ recipe all reference the filename-slug ban**

Run: `cd /Users/seanhan/aeko-intelligence/aeko-plugin && grep -rnE "filename slug|filename .<slug>. token" skills/aeko-create-content/SKILL.md skills/aeko-create-content/references/recipes/editorial-html-jsonld.md`
Expected: ≥3 lines (§5.5.6, §6.3, and the recipe gate/field table) — confirming the rule is stated consistently across all three locations.

---

### Task 6: Commit (gated on user go-ahead)

**Files:** none modified

- [ ] **Step 1: Show the diff for review**

Run: `cd /Users/seanhan/aeko-intelligence/aeko-plugin && git status && git diff -- skills/aeko-create-content/`
Expected: changes only in `SKILL.md` and `editorial-html-jsonld.md` (plus the spec/plan docs under `docs/superpowers/`).

- [ ] **Step 2: Commit with explicit paths (only after the user confirms)**

Do NOT commit unless the user has asked. When they do:

```bash
cd /Users/seanhan/aeko-intelligence/aeko-plugin && \
git add skills/aeko-create-content/SKILL.md \
        skills/aeko-create-content/references/recipes/editorial-html-jsonld.md \
        docs/superpowers/specs/2026-06-01-aeko-shop-slug-hard-gate-design.md \
        docs/superpowers/plans/2026-06-01-aeko-shop-slug-hard-gate.md && \
git commit -m "$(cat <<'EOF'
fix(aeko-create-content): hard-gate the aeko_shop English URL slug

Promote §5.5.6's meaningful-English slug from advisory to a §6.3 hard
gate: .meta.json slug must be present, match ^[a-z0-9]+(?:-[a-z0-9]+)*$,
and not equal the §5.5.3 romanized filename slug. Flip the recipe field
tables from "strongly recommended" to "required" and add a matching
recipe acceptance-gate line. Stops the shop backend from falling back to
romanizing the Korean title (gibberish URLs) when no slug is supplied.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Verification (post-implementation)

A prompt-gate change cannot be unit-tested. After Tasks 1-5 pass their `grep` checks:

1. **Doc consistency** — Tasks 3/5 confirm no stray "strongly recommended"; Task 5 confirms the filename-slug ban is stated in all three places.
2. **Live end-to-end (with user go-ahead, on a test item):** run `/aeko-create-content` for a Korean-titled test item, confirm `<slug>.meta.json.slug` is English and ≠ the filename slug, then `aeko_save_content_variation` → `aeko_publish_content_variation`, and confirm the live aeko.shop post URL slug is the English slug.
3. **If the live slug is still romanized despite a correct `metadata.slug`:** the drop is in the main AEKO backend (`/api/content-variations` save or `AekoShopPublisher`) — out of lane → escalate to Codex.
