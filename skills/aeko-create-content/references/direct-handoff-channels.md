# Direct content-idea channel contracts

Apply only in `handoff=<id>` mode. Use the frozen snapshot. Follow the output-language map below and keep
user-facing notes in the user's chat language. Do not post, submit, edit, enroll, publish, or contact anyone.

## Output language

- External venue-facing copy (thread reply, publisher pitch, disclosed wiki request/AfC text): use the verified
  destination language from an owner-verified matching stored source body, explicit venue metadata, or a deterministic venue
  convention (`community_kr` → Korean; Wikipedia language subdomain). If still ambiguous, return an
  operator-facing preparation brief and mark the target language unresolved.
- Brand-owned content (Naver/Tistory/other blog post, YouTube script): use the tracked prompt's target
  audience/market language. `naver_blog` is always Korean. A cited source's language is evidence context, not
  the owned content's publishing language.
- Operator-facing work (reply-preparation brief, review action guide, ingredient packet, source/notability or
  platform-readiness checklist, video brief): use the user's chat language. Preserve exact product, field,
  venue, and source names. Put any included external-ready copy in its target language and label it separately.

## Deliverable map

| Channel or rule | Accepted action | Deliverable |
|---|---|---|
| `reddit_thread_discovery` | `prepare_and_find_thread` | Thread-discovery and answer-preparation brief |
| `reddit`, `community_kr`, `thread_reply` | `reply_on_source` | Reply draft or reply-preparation brief |
| `naver_blog`, `tistory`, `blog_other`, `blog_post_gap` | `create_post` | Blog post draft |
| `news`, `media_pitch` | `pitch_media` | Publisher pitch draft |
| `review_site`, `review_presence` | `build_presence` | Eligibility, listing, and genuine-review plan |
| `ingredient_db` | `maintain_product_data` (`build_presence`, `correct_listing` legacy) | Product/ingredient listing-accuracy packet |
| `wiki`, `wiki_entry` | `prepare_wiki_request` (`edit_wiki` legacy) | Readiness assessment plus disclosed request/AfC draft |
| `youtube`, `video_brief` | `create_video_brief` (`create_post` legacy) | Video brief and optional script |

Use a natural action label in the user's language: 답변 초안/reply draft, 답변 준비안/reply preparation,
스레드 탐색·답변 준비/thread search and answer preparation, 글 초안/post draft,
피치 초안/pitch draft, 실행 가이드/action guide, 등록 정보 정리/listing packet, 편집 요청 초안/edit
request, or 영상 기획안/video brief.

## Product-selection gate

When `grounding.requires_product_selection=true`, parse both `grounding.product_candidates[]` and
`grounding.products[]` as unselected options; the latter may contain known matches while another reference is
unresolved or several matches remain. Deduplicate by `store_product_id`, then `external_product_id`. Do not
pick a product or use candidate facts as if they belong to the recommendation. Candidate order and wording are
not a selection signal.

If candidates exist, ask exactly one short product question in the user's chat language. List at most five
candidate titles and stable IDs plus a product-neutral / no-product choice. An explicit title or ID resolves
the selection for this run only; do not persist it or refresh the snapshot. Use only the selected candidate's
official snapshot fields. Use a contextual review for product-specific work only when its `store_product_id`
matches the candidate's `store_product_id`, or its `product_external_ref` matches the candidate's
`external_product_id`.

If the user chooses product-neutral, there are no candidates, or the reply is ambiguous, continue without
product claims. Thread, blog, and video actions then return product-neutral preparation or an outline.
Review-platform and ingredient-database actions list unresolved candidates and stop before a product-specific
fact sheet or listing packet. Do not send the user to a nonexistent selector elsewhere in AEKO.

## Thread reply

For Reddit, load `recipes/reddit.md`. For a Korean community, apply the same disclosure and evidence rules
but match that community's format only when the snapshot supplies it.

- Draft a candidate reply only when direct mode obtained an owner-verified matching-crawl stored thread body
  fetch, the crawl ID matches the snapshot, `body_available=true`, `truncated=false`, and product selection is
  resolved or not required. Put a `게시 전 확인` /
  `Check before posting` block above it: open the URL, confirm the post is still relevant and replyable, read
  current rules, confirm commercial participation is allowed, and keep the affiliation disclosure.
- Snapshot excerpts, titles, and truncated bodies never qualify for a post-ready reply. Use them only in a
  preparation brief. Do not claim to have read the entire live thread. Include the known prompt/topic, permitted
  grounding, attributed contextual-review themes, a proposed answer-first outline, an affiliation-disclosure
  line, unsupported facts to avoid, and the manual preflight. Mark thread-specific wording as pending.
- If no relevant product or contextual review was included, say so. Use only other grounded facts in the
  snapshot and list the missing evidence needed for a useful response.

## Contextual Review-driven Reddit discovery

Use this branch only for the exact source-free contract
`origin=contextual_review`, `rule=reddit_thread_discovery`, `action=prepare_and_find_thread`,
`evidence_basis=context_signal` (or legacy `tier=context_signal`), and
`target_status=discovery_required`. This is not a thread-reply recommendation. AEKO has surfaced a shopper
question from qualified Contextual Reviews, but it has not found, opened, or read a Reddit thread.

Return one operator-facing brief in the user's chat language. Write search phrases in the snapshot's target
audience language when it is known, and label them when that differs from the chat language. If it is absent,
use the prompt language when clear; otherwise use the user's chat language and mark the search/disclosure
language as provisional. Include:

1. the shopper question and the Context/review themes that support it, with review counts or product names
   only when the snapshot supplies them;
2. three to six manual Reddit search phrases derived from that evidence;
3. two to four subreddit categories to explore, such as problem-solving, product-category, routine, or
   market/location communities. Do not invent or assert active subreddit handles;
4. an answer-first framework: the useful question to answer, snapshot-backed facts or attributed experience
   themes that may support it, limitations to state, and unsupported claims to avoid;
5. a thread-selection and rules checklist: topical match, recency, open/archived/locked state, subreddit rules,
   commercial participation, link policy, and whether an affiliated answer would add value;
6. a short affiliation-disclosure line in the likely reply language; and
7. the exact input needed next: the user must supply the actual thread URL and pasted thread text and confirm
   they checked the current thread state and community rules.

Do not call `WebSearch`, `WebFetch`, or `aeko_fetch_source_content`; do not name a found thread; do not use
citation counts or brand-absence language; and do not return a post-ready reply. Do not create or complete an
ActionItem, publish, or save a variation.

If the user later supplies the actual URL and thread text and confirms the checklist, a follow-up may draft a
candidate reply from that user-provided current input. Keep two explicit evidence labels: `Frozen AEKO
grounding` for the original snapshot and `User-provided thread` for the pasted text. A URL without pasted
thread text is not enough. Do not fetch the URL or imply AEKO verified it, and never post the reply.

## Blog post

Draft one post for the prescribed venue and topic, unless product selection remains unresolved; then return a
product-neutral outline. Use official selected-product evidence and contextual reviews from the snapshot.
Attribute customer experiences as experiences; do not present them as measured outcomes. Use source excerpts
only to understand the cited topic, never to copy a publisher's wording or structure.

Do not infer a venue's formatting, length, link, disclosure, or moderation rules from its name. Apply explicit
requirements from the snapshot. If any are missing, list them under `Manual venue checks` and keep the draft
in plain markdown with no platform-specific claim.

## Publisher pitch

Target the actual publisher, not an aggregator. Treat `news.naver.com`, `m.news.naver.com`, `v.daum.net`,
`news.daum.net`, `news.nate.com`, and `news.google.com` as aggregators. If the snapshot provides only an
aggregator, return a short blocker naming the missing original publisher; do not address a pitch to the
aggregator.

When an actual publisher is present, return:

1. the publisher and evidence URL;
2. one topic angle tied to the cited prompt;
3. a subject line and concise email pitch;
4. a fact/asset list the brand must verify before sending;
5. missing editor/contact details, without guessing them.

Disclose the brand relationship. Do not promise coverage, payment, exclusivity, samples, test results, or an
embargo unless the snapshot says so. Do not imitate an editor's voice or invent personalization.

## Review platform presence

Return an action guide, not fabricated reviews:

1. check platform and market eligibility;
2. prepare a verified product/brand fact sheet from snapshot products;
3. list required ownership or listing evidence;
4. propose a neutral workflow for inviting real customers to leave honest feedback;
5. list profile accuracy and ongoing response checks.

When product selection remains unresolved, list candidate identifiers/titles under `Unselected candidates`. Do not
prepare the product fact sheet or imply that any candidate is the intended listing.

Never write customer reviews for posting. Never recommend employee reviews, review gating, undisclosed
seeding, discounts, gifts, or other review incentives. If platform terms or eligibility are absent, mark them
for manual verification.

## Ingredient database

Return a listing-accuracy packet, not a review-acquisition plan. Include only snapshot-backed product name,
variant, ingredient list, ingredient order when supplied, claims, certifications, official URL, and known
listing discrepancies. Separate facts supplied by the brand from third-party database text. Ask the user to
verify the final INCI and variant before submission. Do not infer concentrations, safety, efficacy, or missing
ingredients.

When product selection remains unresolved, return only the workflow and an `Unselected candidates` list with stable
IDs/titles. Do not combine candidate facts or create a product-specific packet.

## Wiki targets

Determine the target from the snapshot source URL, not the venue label.

For `wikipedia.org` and its subdomains, never direct-edit on behalf of an affiliated brand account. Treat the
legacy `edit_wiki` action as a request to prepare a conflict-of-interest-safe path.

1. Assess readiness using independent, reliable, in-depth sources in the snapshot. Brand pages, product pages,
   press releases, social posts, databases, and passing mentions do not establish notability by themselves.
2. If evidence is insufficient, return only a source-gap/notability checklist. Do not draft an article that
   implies eligibility.
3. For an existing article, draft a concise, disclosed talk-page edit request with proposed neutral wording
   and citations.
4. For a potentially notable new topic, draft an Articles for Creation outline or draft with a clear paid/
   affiliated-contributor disclosure and neutral sourcing notes.

Do not write promotional claims, remove sourced criticism, manufacture citations, or advise evading
conflict-of-interest rules.

For `namu.wiki` and every non-Wikipedia wiki, do not use Wikipedia Talk-page or Articles for Creation language.
Return a platform-policy and source-readiness brief. Include an edit request, discussion, submission, or
disclosure route only when that exact route and its requirements appear in the snapshot. Otherwise mark the
platform rules and contribution route for manual verification.

## YouTube

Return a video brief with audience/question, answer-first angle, working title, hook, section outline,
grounded fact ledger, caveats, visual/B-roll notes, and source notes. Add a script only when the snapshot has
enough product/context evidence to support it. Attribute review themes and do not script fake testimonials or
present a creator as an independent reviewer. Include title/description/chapters only when useful; do not
claim the video was filmed or published.

When product selection remains unresolved, return a product-neutral video outline and candidate-selection note. Do
not add candidate product facts or a product script.
