---
channel: reddit
purpose: Reddit thread-reply recipe with affiliation and community-safety rules
load_when: SKILL.md selects channel=reddit for a thread reply or Contextual Review-driven thread discovery
---

# `reddit` — Thread reply recipe

Use this recipe for either a reply to an exact Reddit thread in the evidence snapshot/Plan or the narrowly
defined Contextual Review discovery branch below. Reddit renders comments, so return plain markdown. Never
post anything.

## Contextual Review discovery mode

Use this mode only when the frozen handoff says `origin=contextual_review`,
`rule=reddit_thread_discovery`, `action=prepare_and_find_thread`, and
`target_status=discovery_required`, with `evidence_basis=context_signal` (or legacy
`tier=context_signal`) and no sources. AEKO has identified a review-backed shopper question, not a Reddit
thread.

Return a `Thread search and answer preparation` brief in the user's chat language with:

- three to six manual search phrases based on the supplied prompt and review/Context themes;
- two to four subreddit categories, not invented subreddit handles;
- an answer-first framework using only frozen product facts and attributed review themes;
- unsupported claims, comparisons, and experiences to avoid;
- a checklist for topical fit, recency, locked/archived state, current subreddit rules, commercial
  participation, link policy, and usefulness;
- a plain affiliation disclosure in the likely reply language; and
- a request for the actual thread URL, pasted thread text, and the user's confirmation that they checked the
  current state and rules.

Write search phrases and the disclosure in the snapshot's target audience language when supplied. Otherwise
use the prompt language when it is clear; if neither is clear, use the user's chat language and label that
choice as provisional.

Do not call `WebSearch`, `WebFetch`, or `aeko_fetch_source_content`. Do not claim a thread was found or read,
name an unverified subreddit, cite a nonexistent source, or produce a post-ready comment. Do not show citation
counts or describe the brand as absent from Reddit.

If the user later supplies the URL and actual thread text and confirms the manual checks, a follow-up may
draft from that text. Label the original evidence `Frozen AEKO grounding` and the pasted text `User-provided
thread`; do not merge their provenance or claim AEKO verified the thread. A URL alone is insufficient. Never
fetch or post it.

## Source-identified reply preflight

This section and the reply structure/acceptance gates below apply only to a source-identified Reddit reply.
They do not require a URL for the discovery preparation brief and do not turn that brief into a reply draft.

The user must open the exact thread URL before posting and confirm that the thread is still relevant, not
locked or archived, and open to commercial participation. They must also read the current subreddit rules and
keep the affiliation disclosure. A snapshot title, prompt, citation count, or subreddit name does not prove
the thread body or current posting state.

In direct handoff mode, a post-ready candidate requires an owner-verified matching-crawl stored thread body from
`aeko_fetch_source_content`, an exact snapshot crawl-ID match, `body_available=true`, and `truncated=false`.
Snapshot excerpts and titles never satisfy this gate. When the gate fails, or when
product selection remains unresolved, do not claim to have read the entire live thread and do not return a
post-ready comment. Return a `Reply preparation brief` with:

- the known prompt/topic and thread URL;
- permitted grounding and attributed contextual-review themes from the snapshot. When product selection is
  unresolved, keep the brief product-neutral and list candidates only as unselected;
- an answer-first outline and proposed disclosure line;
- facts or comparisons that remain unsupported;
- the manual preflight above and a note that thread-specific wording requires verification.

## Reply structure

1. Open with a plain affiliation disclosure, such as "Disclosure: I'm affiliated with <brand>."
2. Answer the thread's question in the first paragraph. Do not begin with brand history or a product pitch.
3. Add the smallest amount of evidence needed: a product fact, limitation, correction, or practical step.
4. Close with a useful caveat or an invitation to verify a specific fact. Do not add a sales CTA.

Aim for 80–300 words unless the thread clearly calls for a shorter factual correction. Match the thread's
language and level of formality. No hashtags.

## Community rules

- Follow the named subreddit's rules when they are present in the handoff. If rules were not supplied, flag
  that the user must check them before posting.
- Do not disguise brand participation as an independent recommendation.
- Do not claim personal use, purchase, results, or customer experience unless that exact experience appears
  in approved evidence and belongs to the speaker.
- Do not attack another brand or ask readers to brigade, upvote, message, or repeat a claim.
- Use at most one link. Include it only when the link directly answers the question and already exists in the
  evidence. Default to no link.
- If commercial participation is barred, produce a factual internal response note instead of a post-ready
  comment. Do not suggest evasion through another account.

## Acceptance gates

For a source-identified reply draft:

- Direct handoff mode used an owner-verified, matching-crawl body with `body_available=true` and
  `truncated=false` before labeling the result a reply draft; otherwise the output is a preparation brief.
- Product selection was resolved or not required before adding any product claim or producing a candidate
  reply.
- Affiliation is clear in the first two lines.
- The first paragraph answers the question.
- Every product or brand claim traces to the supplied snapshot, fetched source, or official product evidence.
- No fabricated experience, hidden promotion, hard CTA, link spam, or unsupported comparison.
- The result names the exact thread URL separately from the draft, so the user can verify the destination,
  current thread state, and subreddit rules.

For Contextual Review discovery, acceptance instead requires no thread URL claim, no web/source fetch, no
post-ready reply, manual search phrases, category-only venue guidance, a rules checklist, a disclosure
template, and an explicit request for user-verified thread text.

## File output

- ActionItem mode: `./aeko-artifacts/<domain_id>/<item_id>/reddit/<slug>__reddit.md`.
- Direct handoff mode, when a local artifact is requested:
  `./aeko-artifacts/<domain_id>/handoffs/<handoff_id>/reddit/<slug>__reddit.md`.
