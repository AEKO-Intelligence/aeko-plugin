# Brand-specific exemplars

Drop a real winning post from your brand into one of these files and `/aeko-create-content` will mimic its tone and structure on the next run. **No forking the plugin. No editing SKILL.md.**

## How it works

When `/aeko-create-content` drafts a channel, the **substance** (what to say) comes from the product info + context-reviews + the prompt in the brief; the **quality frameworks** (BLUF, PREP, Informational Gain, E-E-A-T) live in `../aeo-frameworks.md`. Example files steer **tone and structure** on top of that:

1. Apply the AEO quality frameworks from `../aeo-frameworks.md` (the quality core — always).
2. Read the channel recipe from `../recipes/<channel>.md` (format conventions — length, required parts, acceptance gates).
3. **If a matching example file exists in this folder, mimic its tone and structure** where they refine the recipe. Recipe acceptance gates still apply.
4. Apply brand-kit voice (`tone_of_voice`) for sentence-level register.

So example files steer *feel*; the frameworks + substance drive *what gets said*. The recipe defines what *must* be present (acceptance gates); the example defines what *should* feel familiar.

## Files in this folder

| File | What to put in it | Channels it covers |
| --- | --- | --- |
| `blog-example.md` | A real Naver / Tistory blog post you'd be proud of | `naver_blog`, `tistory` |
| `instagram-post-example.md` | A real Instagram caption + hashtags + alt text | `instagram` |
| `in-store-content-example.md` | A real PDP, brand-page section, or owned-blog post | informs voice across all channels |
| `press-release-example.md` | A real press release you've issued (보도자료 or English) | `press_release` |
| `context-reviews-fixture.md` | Sample product context-reviews (the lived-experience substance) — used as a **fallback** when the `aeko_get_product_context_reviews` tool isn't live yet, and for evals | all channels (originality source) |
| `aeko_shop-fixture.*` | A worked aeko.shop article (`.md` + `.html` + `.meta.json`) showing the publish-ready triple | `aeko_shop` (reference only) |

You can add more — e.g., `tiktok-script-example.md`, `magazine-feature-example.md` — and the skill will pick them up as long as the filename matches `<channel>-*example*.md` (the SKILL.md's References section names the exact patterns it looks for).

## Format

No frontmatter required. Just paste the real content. Markdown welcome but not required.

If you want to annotate *why* a section works ("our hooks always lead with a sensory detail, never a question"), use a leading comment:

```markdown
<!-- AEKO note: hook always leads with sensory detail, never a question -->
오늘 아침 침구를 갈아끼울 때, 손끝에 느껴지는 온도가 달랐어요. ...
```

The skill reads these notes too — they steer it more reliably than abstract style guidance in the brand kit.

## What NOT to put here

- **No PII** — strip names, addresses, order numbers, internal SKUs. The skill reads these files into Claude's context.
- **No competitor content you don't have rights to** — examples should be your own work. The skill never copies verbatim from examples (style is mimicked, not text), but the file itself sits in your install.
- **No URLs you want cited** — example URLs are loaded as *style reference only* and are NOT carried into the artifact body. The drafter only links to real URLs from the brief (product `outbound_url`, brand kit, user-supplied media) — it never invents URLs.
- **Image placeholders are fine** — example files can contain `[Image]` markers as part of demonstrating your post format. The artifact's hard-gate scanner only checks the generated artifact body, not your example file.

## Verifying it worked

After running `/aeko-create-content <item_id>`, check the user-facing summary at the bottom. The **substance used** line shows how many products and context-reviews fed the draft, and the per-channel artifact lines show what was produced. If your exemplar file isn't being picked up, the most common cause is a filename that doesn't match the pattern (`<channel>-*example*.md`).

## Contributing back

If your example is brand-agnostic (could help any AEKO user) and PII-stripped, open a PR to [`AEKO-Intelligence/aeko-plugin`](https://github.com/AEKO-Intelligence/aeko-plugin) with the file added to this folder. We curate exemplars that demonstrate clear structural patterns (e.g., "Korean lifestyle 1인칭 review with sensory hook"), not brand-specific voice.
