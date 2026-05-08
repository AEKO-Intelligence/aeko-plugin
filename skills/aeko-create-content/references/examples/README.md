# Brand-specific exemplars

Drop a real winning post from your brand into one of these files and `/aeko-create-content` will mimic its tone and structure on the next run. **No forking the plugin. No editing SKILL.md.**

## How it works

When `/aeko-create-content` is about to draft a channel, it does this in order:

1. Read the channel recipe from `../recipes/<channel>.md` (the generic structural rules — paragraph length, required parts, acceptance gates).
2. **If a matching example file exists in this folder, read it and mimic its tone and structure where they conflict with the recipe.** Recipe acceptance gates still apply.
3. Apply brand-kit voice (`tone_of_voice`) for sentence-level register.

So the precedence is: **example file > recipe defaults > brand kit voice**. The recipe defines what *must* be present (acceptance gates); the example defines what *should* feel familiar.

## Files in this folder

| File | What to put in it | Channels it covers |
| --- | --- | --- |
| `blog-example.md` | A real Naver / Tistory blog post you'd be proud of | `naver_blog`, `tistory` |
| `instagram-post-example.md` | A real Instagram caption + hashtags + alt text | `instagram` |
| `in-store-content-example.md` | A real PDP, brand-page section, or owned-blog post | informs voice across all channels via `aeko_list_own_content`-style signal |
| `press-release-example.md` | A real 보도자료 you've issued | `보도자료` |

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
- **No URLs you want cited** — example URLs are loaded as *style reference only*. They will NOT be carried into the artifact body. If you need a URL cited, that's a `frontmatter.cited_urls` job, not an example.
- **Image placeholders are fine** — example files can contain `[Image]` markers as part of demonstrating your post format. The artifact's hard-gate scanner only checks the generated artifact body, not your example file.

## Verifying it worked

After running `/aeko-create-content <item_id>`, check the user-facing summary at the bottom. If your example was loaded, you'll see something like:

```
Mimicked: instagram-post-example.md (your exemplar)
         + recipes/instagram.md (structural defaults)
```

If the line just says `recipes/instagram.md` and not your exemplar file, your example isn't being picked up. Most common cause: filename doesn't match the pattern (`<channel>-*example*.md`). See SKILL.md's References section for the exact filename pattern it scans.

## Contributing back

If your example is brand-agnostic (could help any AEKO user) and PII-stripped, open a PR to [`AEKO-Intelligence/aeko-plugin`](https://github.com/AEKO-Intelligence/aeko-plugin) with the file added to this folder. We curate exemplars that demonstrate clear structural patterns (e.g., "Korean lifestyle 1인칭 review with sensory hook"), not brand-specific voice.
