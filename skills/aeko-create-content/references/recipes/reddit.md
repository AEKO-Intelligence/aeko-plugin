---
channel: reddit
purpose: Reddit thread-reply recipe with affiliation and community-safety rules
load_when: SKILL.md selects channel=reddit for a thread reply
---

# `reddit` — Thread reply recipe

Use this recipe only for a reply to the exact Reddit thread in the evidence snapshot or Plan. Reddit renders
the comment, so return plain markdown. Never post it.

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

- Affiliation is clear in the first two lines.
- The first paragraph answers the question.
- Every product or brand claim traces to the supplied snapshot, fetched source, or official product evidence.
- No fabricated experience, hidden promotion, hard CTA, link spam, or unsupported comparison.
- The result names the exact thread URL separately from the draft, so the user can verify the destination.

## File output

- ActionItem mode: `./aeko-artifacts/<domain_id>/<item_id>/reddit/<slug>__reddit.md`.
- Direct handoff mode, when a local artifact is requested:
  `./aeko-artifacts/<domain_id>/handoffs/<handoff_id>/reddit/<slug>__reddit.md`.
