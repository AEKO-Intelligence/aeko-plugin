# Channel detection — cited-source domain → channel slug

Used by `aeko-create-content` Phase 3A.3. Classifies each top cited domain (ranked in 3A.2) into a channel slug so 3A.3 can produce `auto_detected_channels[]` without inflating SKILL.md. Loaded lazily on first need; one Read per skill execution.

## Classification table

| Domain pattern | Channel slug | Notes |
| --- | --- | --- |
| `reddit.com/*` | `reddit` | Forum / Q&A; usually maps to `QAPage` / `DiscussionForumPosting` @type in 3B |
| `*.blog.naver.com`, `m.blog.naver.com` | `naver_blog` | First-person Korean review register |
| `*.tistory.com` | `tistory` | Korean long-form blog |
| `wikipedia.org` | `wikipedia` | Encyclopedic; cited for definitional anchoring — not usually a drafting target |
| `news.*`, `*.co.kr/news/*`, established publication TLDs | `partner_media` | News / partner-media heuristic; calibrate to `NewsArticle` / `Article` in 3B |
| (no match) | `web_article` | Generic fallback; structural template comes from the live recrawl alone |

## Deduplication

After classification, deduplicate `auto_detected_channels[]` while preserving the ranking order from 3A.2 (the first-occurring channel wins position). Carry the deduplicated list into Step 4.

## Future extensions

Reserved for the broader channel-taxonomy plan (separate workstream) which will add ownership-aware channels:

- `own_store_blog` — user's connected store CMS (Cafe24 / Shopify) content section
- `aeko_owned_tistory` — `aeko.tistory.com`
- `aeko_owned_naver_blog` — `blog.naver.com/aeko_ai`
- `aeko_shop` — `aeko.shop`

Until that plan lands, those slugs are not produced by this classifier. The reshape in `aeko-create-content` v1.3 keeps the existing channel set; ownership is layered on later.
