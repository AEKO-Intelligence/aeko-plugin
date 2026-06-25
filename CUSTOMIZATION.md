# Customizing the AEKO Plugin

> 한국어 버전은 아래를 참고하세요 → [한국어](#한국어-버전).

The AEKO plugin ships generic best-practice recipes. Your brand isn't generic. This guide shows how to add **brand-specific exemplars, recipe preferences, and voice overrides** so the three executor skills — `/aeko-create-content`, `/aeko-update-pdp`, `/aeko-fix-technical` — work in *your* voice and structural conventions, without forking the plugin for normal customization.

The pattern works because of [Anthropic's progressive-disclosure model for skills](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/best-practices) (sometimes called Skills 2.0): SKILL.md tells Claude *when* to load a reference file, and reference files contain the heavy detail. For supported example and override patterns, you add files to `references/` and Claude picks them up automatically when the relevant channel runs.

**Audience.** This guide is layered:
- **Brand operators** (no engineering background): start at §2. You'll be customizing in under 10 minutes.
- **Developers / agencies**: skim §2, jump to §3 (how it works), then §4–6 (per-skill customization + advanced).

**Skills covered.** All three executor skills now follow the same `references/{recipes,examples,style}/` layout:

| Skill | Customizes | Section |
| --- | --- | --- |
| `/aeko-create-content` | Channel-specific tone (Instagram, blog, `press_release` / 보도자료, etc.) | §2, §4 |
| `/aeko-update-pdp` | PDP HTML structure + JSON-LD field choices | §5 |
| `/aeko-fix-technical` | llms.txt format, robots.txt additions, JSON-LD shape, deploy notes | §6 |

## 1. Where the plugin lives

After installing the AEKO plugin, the files you'll edit are at:

| Host | Path |
| --- | --- |
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/Claude Extensions/aeko-plugin/skills/` |
| Claude Desktop (Windows) | `%APPDATA%\Claude\Claude Extensions\aeko-plugin\skills\` |
| Claude Code | `~/.claude/plugins/aeko-plugin/skills/` |
| Codex Desktop | `~/.codex/plugins/aeko-plugin/skills/` |

Open the folder for the skill you want to customize, for example `aeko-create-content/` or
`aeko-update-pdp/`. If you're not sure where it is, run `/aeko-onboarding` and choose the customization
step; it locates the local plugin install for you.

## 2. Quick-start — make Instagram (or any channel) sound like you

**Goal.** Drop one real winning Instagram post from your brand into a file. Next time `/aeko-create-content` drafts an Instagram artifact, it mimics that post's tone and structure.

### 2a. Open the examples folder

Navigate to:

```
skills/aeko-create-content/references/examples/
```

You'll see 4 starter templates (`blog-example.md`, `instagram-post-example.md`, `in-store-content-example.md`, `press-release-example.md`) and a `README.md`.

### 2b. Edit `instagram-post-example.md`

Open it in any text editor. Delete the comment block at the top. Replace the placeholder content with a real Instagram post from your brand — caption, hashtags, alt text, all of it. Save.

That's it. No frontmatter, no YAML, no JSON. Just paste your post.

### 2c. Run `/aeko-create-content` and verify

```
/aeko-create-content <item_id>
```

When the run finishes, look at the user-facing summary at the bottom. You should see a **Refs loaded** block:

```
Refs loaded:
    - instagram → recipes/instagram.md + examples/instagram-post-example.md
```

If your example file appears there, you're done. The drafted Instagram post should now mirror your hook style, body cadence, hashtag count, and emoji density.

If the line says only `recipes/instagram.md` (no `examples/...`), your file isn't being picked up — most common cause is filename. New example files should include the channel slug and `example`, such as `instagram-summer-example.md`. The bundled aliases (`blog-example.md`, `press-release-example.md`, `in-store-content-example.md`) also work.

### 2d. Repeat for other channels

Same flow:
- `blog-example.md` → covers Naver Blog and Tistory drafts
- `press-release-example.md` → covers the `press_release` channel (shown as 보도자료 in Korean UI)
- `in-store-content-example.md` → informs voice across all channels (this is your owned-content style signal — your PDP, brand-story page, or category landing copy)

You can add more files: `tiktok-script-example.md`, `youtube-description-example.md`, `magazine-feature-example.md`. The normal pattern is `<channel>-*example*.md`; the bundled aliases `blog-example.md`, `press-release-example.md`, and `in-store-content-example.md` are also recognized. For new press-release examples, prefer the slug form: `press_release-summer-launch-example.md`.

## 3. How progressive disclosure works

Anthropic's skills system loads content in three stages:

1. **Discovery** (always loaded): only the `name` and `description` from SKILL.md's frontmatter — about 30–50 tokens. Lets Claude decide whether the skill matches a user request.
2. **Activation** (loaded when the skill matches): the body of SKILL.md. The executor logic.
3. **Execution** (loaded on demand): files in `references/`, but **only if SKILL.md tells Claude to read them**. Files that exist but aren't named in SKILL.md never load.

That third rule is the one most people miss. **Dropping a file into `references/` does nothing on its own.** SKILL.md has to say: "If channel is X, `Read references/recipes/X.md`."

For `aeko-create-content`, that mapping lives in §5.0 of [SKILL.md](skills/aeko-create-content/SKILL.md). When Instagram is selected for drafting, SKILL.md instructs Claude to:
1. Always read `references/recipes/instagram.md` (the structural recipe — required parts, acceptance gates).
2. Read `references/examples/instagram-post-example.md` *if it exists* (the brand-specific exemplar — silent skip if absent).
3. Read `references/style/voice-overrides.md` *if it exists* and a scoped block applies.

The **precedence rule** when these conflict:

> voice-overrides > example file > content context > recipe defaults

So your example file overrides the generic recipe's defaults, but the recipe's hard acceptance gates (like "5–12 hashtags" for Instagram) still apply. If you want to override an acceptance gate too — e.g., your brand uses 3 hashtags, not 5 — that's what `voice-overrides.md` is for (§5).

## 4. Advanced — adding a custom channel recipe

Two ways to handle a channel that isn't built in:

### Option A: one-shot (no file change)

When `/aeko-create-content` asks "Add any of these formats?", you can reply `other:linkedin` and paste a reference URL or short style note. The skill uses that input as style guidance for *that run only*. Good for experiments.

### Option B: permanent (add a recipe file)

If you'll keep using the channel, add a recipe file:

```
skills/aeko-create-content/references/recipes/linkedin.md
```

Use this template (matches the existing recipe files):

```markdown
---
channel: linkedin
purpose: LinkedIn post (long-form professional tone)
load_when: SKILL.md §5.1 selects channel=linkedin
---

# `linkedin` — Post recipe

## Structure

- **Hook line** — first 2 lines visible above "see more" fold
- **Body** — 5–12 short paragraphs, single-sentence paragraphs OK
- **Closing CTA-question** — invite a reply, not a click
- **Hashtags** — 3–6 at the bottom

## Acceptance gates

- Hook ≤2 lines
- Body has paragraph breaks every 1–2 sentences
- Closing question present
- Hashtags 3–6
```

Then add a one-line entry to SKILL.md §5.0's channel table so Claude knows to load it. That means editing your local installed plugin or maintaining a fork. If you do not want to edit SKILL.md, use the `other:<name>` route above.

In the meantime, the `other:<name>` route covers the same ground for the channels you draft a few times per quarter. Permanent recipe files are best for channels you draft weekly.

## 5. `/aeko-update-pdp` — PDP HTML + JSON-LD preferences

PDP customization lets you control the structural shape of generated product-page HTML and which optional JSON-LD fields the skill always emits.

### 5a. Quick-start

Navigate to:

```
skills/aeko-update-pdp/references/examples/
```

Three files matter:

| File | Purpose |
| --- | --- |
| `pdp-html-example.html` | Paste a real, well-performing PDP description block from your store. The skill picks up your section ordering, heading copy, and class-name conventions. |
| `json-ld-preferences.json` | Set optional JSON-LD fields to `true` (always include) or `false` (always omit). Required keys (per `references/recipes/json-ld-schemas.md`) cannot be overridden — the file only adjusts optional/recommended fields. |
| `verification-prompt-example.md` | (Optional) draft of how you'd phrase the Step 5b user-facing question. Skill mirrors register and phrasing; structure stays the same. |

### 5b. What CAN'T be customized

The hard contract in `references/recipes/responsive-html-contract.md` always applies:
- Mobile-first, no fixed-pixel widths
- Semantic tags only (`<section>`, `<h2>`, etc.)
- **No `<a href>` or `<button>` action elements anywhere** — AEKO produces citability content; the host platform owns action UI
- No JavaScript
- Citability baseline (80–167 word passages, named subjects, direct-answer leads)

Examples can't relax these. If your `pdp-html-example.html` contains `<button>` elements, the skill strips them.

### 5c. Verifying it worked

Run `/aeko-update-pdp <item_id>` and check the Step 9 summary:

```
Refs loaded:   recipes/{pdp-scaffold,responsive-html-contract,json-ld-schemas}.md
               + examples/pdp-html-example.html  (when present)
               + examples/json-ld-preferences.json  (when present)
```

If your example file isn't named in `Refs loaded`, the file isn't being picked up.

## 6. `/aeko-fix-technical` — llms.txt / robots.txt / JSON-LD / deploy

Technical-artifact customization covers four files:

| File | What it changes |
| --- | --- |
| `references/examples/llms-txt-example.txt` | Section ordering, heading wording, link-description style of generated llms.txt |
| `references/examples/robots-txt-additions-example.txt` | Custom partner-crawler rules / path disallows appended after the AEKO AI search/shopping visibility block |
| `references/examples/json-ld-example.json` | Preferred Organization / WebSite shape (single block vs. `@graph`), optional fields you always emit (e.g., `foundingDate`, `potentialAction.SearchAction`) |
| `references/examples/deploy-notes-example.md` | Internal deploy steps appended to the generated DEPLOY.md (your CI script, staging URL, owner contacts) |

### 6a. Hard rules that always apply

- llms.txt: H1 first line, `## ` headings + markdown lists, absolute URLs.
- robots.txt: must parse as valid robots.txt syntax. AEKO separates AI search/shopping visibility bots from training/data crawlers. Examples can add partner/path rules, but cannot override that crawler policy.
- JSON-LD: valid JSON, no trailing commas, no comments, `<script type="application/ld+json">` exactly.

### 6b. Per-domain technical voice

`skills/aeko-fix-technical/references/style/voice-overrides.md` handles things like:
- Korean-only section headings in llms.txt
- Brand-specific JSON-LD `description` length conventions
- Domain-specific deploy gotchas ("this domain hosts on Vercel, not Cafe24")

Same `## domain: <id>` block format as the other skills.

## 7. Advanced — voice overrides (universal pattern)

`references/style/voice-overrides.md` is for rules that should be stricter than the domain's general content context — usually because they're **per-channel** or **per-domain** exceptions. Same pattern across all three executor skills (each skill has its own `voice-overrides.md`; the file isn't shared).

Format (H2 blocks scope the rule):

```markdown
## domain: <your-domain-id>, channel: instagram

- Always English hashtags only (no Korean hashtags)
- Hook always opens as a question
- Forbidden: "출시", "런칭" — we say "공개" instead

## channel: press_release

<!-- Korean users see this as 보도자료 in the channel picker; the internal slug is press_release. -->

- Boilerplate last line always includes English company name in parens
- Quote attribution: title + name (not name + title)
```

The skill reads this at §5.3 voice-discipline time and applies any block scoped to the current `frontmatter.domain_id` and the current channel. Unscoped blocks (e.g., a top-level `## glossary`) apply globally.

When to use this vs. AEKO context:
- **Content context** is the broad source of audience, situation, voice, constraints, and must-include facts for content optimization.
- **voice-overrides** is for channel/domain-specific exceptions: *for this brand on this channel, override X.*
- If you run multiple brands from one AEKO install, voice-overrides is essential because each skill reads the block scoped to the current `domain_id` and channel.

## 8. Contributing back

If your example or recipe is brand-agnostic and PII-stripped, open a PR to [`AEKO-Intelligence/aeko-plugin`](https://github.com/AEKO-Intelligence/aeko-plugin) and other AEKO users will benefit. We curate exemplars that demonstrate **clear structural patterns** (e.g., "Korean lifestyle 1인칭 review with sensory hook") rather than brand-specific voice.

Criteria for acceptance:
- No real PII (names, emails, order numbers, internal SKUs).
- No content you don't have rights to redistribute.
- Demonstrates a structural pattern, not just a particular brand voice.
- One example per pattern — we don't want 12 variations of the same hook style.

Custom recipes (Option B above) are also welcome as PRs. Channels we'd like to add to the built-in set: LinkedIn, Threads, X long-post, Substack, Korean cafe blogs (네이버 카페).

## 9. Layout reference

All three executor skills share the same `references/{recipes,examples,style}/` layout:

```
skills/aeko-create-content/
├── SKILL.md                                    ← executor logic (don't edit unless forking)
└── references/
    ├── recipes/                                ← structural rules per channel (don't edit)
    │   ├── press_release.md
    │   ├── magazine.md
    │   ├── instagram.md
    │   ├── naver_blog.md
    │   ├── tiktok.md
    │   ├── tistory.md
    │   ├── youtube.md
    │   └── editorial-html-jsonld.md
    ├── examples/                               ← YOUR CUSTOMIZATION GOES HERE
    │   ├── README.md
    │   ├── blog-example.md                     ← edit me
    │   ├── instagram-post-example.md           ← edit me
    │   ├── in-store-content-example.md        ← edit me
    │   ├── press-release-example.md           ← edit me
    │   ├── context-reviews-fixture.md          ← fallback/eval fixture
    │   └── aeko_shop-fixture.*                 ← reference only
    └── style/
        └── voice-overrides.md                  ← edit for multi-brand / per-channel rules

skills/aeko-update-pdp/
├── SKILL.md
└── references/
    ├── recipes/                                ← don't edit
    │   ├── pdp-scaffold.md
    │   ├── responsive-html-contract.md
    │   └── json-ld-schemas.md
    ├── prompts/
    │   └── verification-prompts.md             ← Step 5b prompt templates
    ├── examples/                               ← YOUR CUSTOMIZATION
    │   ├── README.md
    │   ├── pdp-html-example.html               ← edit me
    │   └── json-ld-preferences.json            ← edit me
    └── style/
        └── voice-overrides.md                  ← edit for per-domain rules

skills/aeko-fix-technical/
├── SKILL.md
└── references/
    ├── recipes/                                ← don't edit
    │   ├── llms-txt.md
    │   ├── robots-txt-patch.md
    │   ├── json-ld.md
    │   └── deploy-checklist.md
    ├── examples/                               ← YOUR CUSTOMIZATION
    │   ├── README.md
    │   ├── llms-txt-example.txt                ← edit me
    │   ├── robots-txt-additions-example.txt    ← edit me
    │   ├── json-ld-example.json                ← edit me
    │   └── deploy-notes-example.md             ← edit me
    └── style/
        └── voice-overrides.md                  ← edit for per-domain technical conventions
```

Other AEKO skills (research and reporting) don't currently use `references/` — they're under Anthropic's 1,500-word target and don't have the kind of customizable structural detail that benefits from extraction.

---

# 한국어 버전

AEKO 플러그인은 일반적인 레시피로 시작하지만, 당신의 브랜드는 일반적이지 않습니다. 이 가이드는 세 개의 executor 스킬 — `/aeko-create-content`, `/aeko-update-pdp`, `/aeko-fix-technical` — 가 *당신의 목소리와 구조 컨벤션*으로 작동하도록 **브랜드 전용 예시, 레시피 선호도, 보이스 오버라이드**를 추가하는 방법을 설명합니다. 일반적인 커스터마이징은 플러그인을 포크하지 않아도 됩니다.

이 패턴은 [Anthropic의 점진적 공개(progressive disclosure) 모델](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/best-practices) — 일명 Skills 2.0 — 에 기반합니다. SKILL.md가 Claude에게 *언제* 어떤 참조 파일을 읽어야 하는지 지시하고, 무거운 디테일은 참조 파일에 둡니다. 지원되는 예시/오버라이드 패턴의 경우 사용자가 `references/`에 파일을 추가하면 해당 채널 실행 시 Claude가 자동으로 가져옵니다.

**대상 독자.** 이 가이드는 계층적으로 작성되었습니다:
- **브랜드 운영자** (개발 배경 없음): §2부터 시작하세요. 10분 안에 첫 커스터마이징을 마칠 수 있습니다.
- **개발자 / 에이전시**: §2를 빠르게 훑고 §3(작동 원리), §4–6(스킬별 커스터마이징 + 고급)으로 건너뛰세요.

**다루는 스킬.** 세 executor 스킬 모두 동일한 `references/{recipes,examples,style}/` 레이아웃을 따릅니다:

| 스킬 | 커스터마이즈 대상 | 섹션 |
| --- | --- | --- |
| `/aeko-create-content` | 채널별 톤 (Instagram, 블로그, `press_release` / 보도자료 등) | §2, §4 |
| `/aeko-update-pdp` | PDP HTML 구조 + JSON-LD 필드 선택 | §5 |
| `/aeko-fix-technical` | llms.txt 형식, robots.txt 추가 규칙, JSON-LD 형태, 배포 노트 | §6 |

## 1. 플러그인 위치

AEKO 플러그인 설치 후 편집할 파일은 다음 경로에 있습니다:

| 호스트 | 경로 |
| --- | --- |
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/Claude Extensions/aeko-plugin/skills/` |
| Claude Desktop (Windows) | `%APPDATA%\Claude\Claude Extensions\aeko-plugin\skills\` |
| Claude Code | `~/.claude/plugins/aeko-plugin/skills/` |
| Codex Desktop | `~/.codex/plugins/aeko-plugin/skills/` |

커스터마이즈하려는 스킬 폴더를 여세요. 예: `aeko-create-content/`, `aeko-update-pdp/`.
경로를 모르겠다면 `/aeko-onboarding`을 실행하고 커스터마이즈 단계를 선택하세요. 로컬 플러그인 설치 위치를 찾아줍니다.

## 2. 빠른 시작 — Instagram(또는 어떤 채널이든)이 우리 브랜드처럼 들리게 만들기

**목표.** 브랜드의 실제로 잘 된 Instagram 포스트 한 개를 파일에 붙여넣기. 다음번에 `/aeko-create-content`가 Instagram 아티팩트를 작성할 때 그 톤과 구조를 모방합니다.

### 2a. examples 폴더 열기

다음 경로로 이동:

```
skills/aeko-create-content/references/examples/
```

4개의 시작 템플릿(`blog-example.md`, `instagram-post-example.md`, `in-store-content-example.md`, `press-release-example.md`)과 `README.md`가 보입니다.

### 2b. `instagram-post-example.md` 편집

원하는 텍스트 에디터로 엽니다. 상단의 주석 블록을 삭제하세요. 자리표시자 콘텐츠를 브랜드의 실제 Instagram 포스트로 교체합니다 — 캡션, 해시태그, alt 텍스트 모두. 저장.

끝입니다. 프론트매터도, YAML도, JSON도 필요 없습니다. 그냥 포스트를 붙여넣으세요.

### 2c. `/aeko-create-content` 실행 후 확인

```
/aeko-create-content <item_id>
```

실행이 끝나면 하단의 사용자 요약을 보세요. **Refs loaded** 블록이 보여야 합니다:

```
Refs loaded:
    - instagram → recipes/instagram.md + examples/instagram-post-example.md
```

여기에 예시 파일이 보이면 완료입니다. 작성된 Instagram 포스트가 당신의 후크 스타일, 본문 리듬, 해시태그 수, 이모지 밀도를 반영해야 합니다.

`recipes/instagram.md`만 보이고 `examples/...`가 없다면 파일이 인식되지 않은 것입니다 — 가장 흔한 원인은 파일명입니다. 새 예시 파일은 `instagram-summer-example.md`처럼 채널 slug와 `example`을 포함하세요. 번들 alias(`blog-example.md`, `press-release-example.md`, `in-store-content-example.md`)도 인식됩니다.

### 2d. 다른 채널도 동일하게

같은 흐름으로:
- `blog-example.md` → 네이버 블로그, 티스토리 초안에 적용
- `press-release-example.md` → `press_release` 채널에 적용 (한국어 UI에서는 보도자료로 표시)
- `in-store-content-example.md` → 모든 채널의 보이스에 영향 (PDP, 브랜드 스토리 페이지, 카테고리 랜딩 카피 등 자사 콘텐츠 보이스 시그널)

파일을 더 추가할 수 있습니다: `tiktok-script-example.md`, `youtube-description-example.md`, `magazine-feature-example.md`. 일반 패턴은 `<channel>-*example*.md`입니다. 새 보도자료 예시는 slug 형태인 `press_release-summer-launch-example.md`를 권장합니다.

## 3. 점진적 공개(progressive disclosure)는 어떻게 작동하나

Anthropic의 스킬 시스템은 콘텐츠를 3단계로 로드합니다:

1. **Discovery** (항상 로드): SKILL.md 프론트매터의 `name`과 `description`만 — 약 30–50 토큰. Claude가 사용자 요청에 스킬이 맞는지 판단할 때 사용.
2. **Activation** (스킬이 매칭되면 로드): SKILL.md 본문. 실행기 로직.
3. **Execution** (요청 시 로드): `references/` 안의 파일들 — **단, SKILL.md가 Claude에게 읽으라고 명시한 경우에만**. 존재하더라도 SKILL.md에 명시되지 않은 파일은 절대 로드되지 않습니다.

세 번째 규칙이 가장 자주 놓치는 부분입니다. **`references/`에 파일만 떨어뜨려서는 아무 일도 일어나지 않습니다.** SKILL.md가 "채널이 X면 `references/recipes/X.md`를 `Read`해라"고 말해야 합니다.

`aeko-create-content`의 경우 그 매핑이 [SKILL.md](skills/aeko-create-content/SKILL.md) §5.0에 있습니다. Instagram이 작성 대상으로 선택되면 SKILL.md는 Claude에게:
1. 항상 `references/recipes/instagram.md`를 읽음 (구조 레시피 — 필수 구성 요소, 수용 게이트).
2. `references/examples/instagram-post-example.md`가 있으면 읽음 (브랜드 전용 예시 — 없으면 조용히 스킵).
3. `references/style/voice-overrides.md`가 있고 범위가 일치하는 블록이 있으면 읽음.

이들이 충돌할 때의 **우선순위 규칙**:

> voice-overrides > 예시 파일 > 콘텐츠 컨텍스트 > 레시피 기본값

즉, 예시 파일이 일반 레시피의 기본값을 덮어씁니다. 단, 레시피의 하드 수용 게이트(예: Instagram의 "해시태그 5–12개")는 여전히 적용됩니다. 수용 게이트도 덮어쓰고 싶다면 — 예: 우리 브랜드는 해시태그 3개 — 그게 `voice-overrides.md`의 역할입니다(§5).

## 4. 고급 — 커스텀 채널 레시피 추가

빌트인이 아닌 채널을 다루는 두 가지 방법:

### 옵션 A: 일회성 (파일 변경 없음)

`/aeko-create-content`가 "Add any of these formats?" 질문을 할 때 `other:linkedin`이라고 답하고 참고 URL이나 짧은 스타일 설명을 붙여넣을 수 있습니다. 스킬은 그 입력을 *그 실행에 한해서* 스타일 가이드로 사용합니다. 실험에 좋습니다.

### 옵션 B: 영구 (레시피 파일 추가)

해당 채널을 계속 쓸 거라면 레시피 파일을 추가하세요:

```
skills/aeko-create-content/references/recipes/linkedin.md
```

기존 레시피 파일과 같은 형식의 템플릿:

```markdown
---
channel: linkedin
purpose: LinkedIn post (long-form professional tone)
load_when: SKILL.md §5.1 selects channel=linkedin
---

# `linkedin` — Post recipe

## Structure

- **Hook line** — "see more" 접힘 위에 보이는 첫 2줄
- **Body** — 5–12 짧은 단락, 한 문장 단락도 OK
- **Closing CTA-question** — 클릭이 아닌 댓글을 유도
- **Hashtags** — 하단에 3–6개

## Acceptance gates

- Hook ≤2 줄
- 본문은 1–2 문장마다 단락 구분
- 마무리 질문 존재
- 해시태그 3–6개
```

그 후 SKILL.md §5.0의 채널 표에 한 줄을 추가해야 Claude가 로드합니다. 즉, 로컬 설치본의 SKILL.md를 편집하거나 포크를 유지해야 합니다. SKILL.md를 편집하고 싶지 않다면 위의 `other:<name>` 경로를 사용하세요.

당분간 분기에 몇 번만 작성하는 채널은 `other:<name>` 경로로 충분합니다. 영구 레시피 파일은 매주 작성하는 채널에 적합합니다.

## 5. `/aeko-update-pdp` — PDP HTML + JSON-LD 환경설정

PDP 커스터마이징은 생성되는 상품 페이지 HTML의 구조적 형태와 어떤 선택적 JSON-LD 필드를 항상 내보낼지 제어할 수 있게 해줍니다.

### 5a. 빠른 시작

이동:

```
skills/aeko-update-pdp/references/examples/
```

세 파일이 핵심:

| 파일 | 용도 |
| --- | --- |
| `pdp-html-example.html` | 스토어에서 잘 나오는 실제 PDP 설명 블록을 붙여넣기. 스킬이 섹션 순서, 헤딩 카피, 클래스 명명 컨벤션을 따라합니다. |
| `json-ld-preferences.json` | 선택적 JSON-LD 필드를 `true`(항상 포함) 또는 `false`(항상 생략)로 설정. 필수 키(`references/recipes/json-ld-schemas.md`)는 덮어쓸 수 없으며, 이 파일은 선택/권장 필드만 조정합니다. |
| `verification-prompt-example.md` | (선택) Step 5b 사용자 질문을 어떻게 표현할지 초안. 스킬이 레지스터와 어조를 따라하지만 구조는 동일하게 유지됩니다. |

### 5b. 커스터마이즈 불가능한 것

`references/recipes/responsive-html-contract.md`의 하드 컨트랙트는 항상 적용:
- 모바일 우선, 고정 픽셀 너비 금지
- 시맨틱 태그만 (`<section>`, `<h2>` 등)
- **`<a href>`나 `<button>` 액션 요소 어디서든 금지** — AEKO는 citability 콘텐츠를 만들고, 호스트 플랫폼이 액션 UI를 소유
- JavaScript 금지
- Citability 베이스라인 (80–167 단어 단락, 명명된 주어, 직답 리드)

예시는 이걸 완화할 수 없습니다. `pdp-html-example.html`에 `<button>`이 있어도 스킬이 제거합니다.

### 5c. 적용 확인

`/aeko-update-pdp <item_id>` 실행 후 Step 9 요약 확인:

```
Refs loaded:   recipes/{pdp-scaffold,responsive-html-contract,json-ld-schemas}.md
               + examples/pdp-html-example.html  (있는 경우)
               + examples/json-ld-preferences.json  (있는 경우)
```

`Refs loaded`에 예시 파일이 안 보이면 인식되지 않은 것입니다.

## 6. `/aeko-fix-technical` — llms.txt / robots.txt / JSON-LD / 배포

기술 아티팩트 커스터마이징은 4개 파일을 다룹니다:

| 파일 | 변경되는 것 |
| --- | --- |
| `references/examples/llms-txt-example.txt` | 생성되는 llms.txt의 섹션 순서, 헤딩 표현, 링크 설명 스타일 |
| `references/examples/robots-txt-additions-example.txt` | AEKO AI 검색/쇼핑 가시성 블록 뒤에 추가되는 커스텀 파트너 크롤러 규칙 / 경로 disallow |
| `references/examples/json-ld-example.json` | 선호하는 Organization / WebSite 형태 (단일 블록 vs `@graph`), 항상 내보내는 선택 필드 (예: `foundingDate`, `potentialAction.SearchAction`) |
| `references/examples/deploy-notes-example.md` | 생성된 DEPLOY.md에 추가되는 내부 배포 단계 (CI 스크립트, 스테이징 URL, 담당자 연락처) |

### 6a. 항상 적용되는 하드 룰

- llms.txt: 첫 줄 H1, `## ` 헤딩 + 마크다운 리스트, 절대 URL.
- robots.txt: 유효한 robots.txt 문법으로 파싱되어야 함. AEKO는 AI 검색/쇼핑 가시성 봇과 training/data 크롤러를 분리합니다. 예시는 파트너/경로 규칙을 추가할 수 있지만 이 크롤러 정책을 덮어쓸 수 없습니다.
- JSON-LD: 유효한 JSON, trailing comma 금지, 주석 금지, `<script type="application/ld+json">` 정확히 그대로.

### 6b. 도메인별 기술 보이스

`skills/aeko-fix-technical/references/style/voice-overrides.md`로 다음을 다룹니다:
- llms.txt에서 한국어만 쓴 섹션 헤딩
- 브랜드별 JSON-LD `description` 길이 컨벤션
- 도메인별 배포 함정 ("이 도메인은 Cafe24가 아니라 Vercel에 호스팅")

다른 스킬과 동일한 `## domain: <id>` 블록 형식.

## 7. 고급 — 보이스 오버라이드 (공통 패턴)

`references/style/voice-overrides.md`는 도메인의 일반 콘텐츠 컨텍스트보다 더 강하게 적용해야 하는 규칙을 위한 곳입니다 — 보통 **채널별** 또는 **도메인별** 예외이기 때문입니다. 세 executor 스킬 모두 동일한 패턴 (각 스킬이 자체 `voice-overrides.md`를 가짐 — 파일은 공유되지 않음).

형식 (H2 블록이 규칙의 범위를 정의):

```markdown
## domain: <your-domain-id>, channel: instagram

- 항상 영어 hashtag만 사용 (한글 hashtag 금지)
- Hook은 항상 질문형으로 시작
- Forbidden: "출시", "런칭" — 우리는 "공개"라고 말함

## channel: press_release

<!-- 한국어 UI에서는 보도자료로 보이지만 내부 channel slug는 press_release입니다. -->

- Boilerplate 마지막 줄에 항상 영문 사명을 병기
- Quote 표기: 직책 + 이름 (이름 + 직책 X)
```

스킬은 §5.3 보이스 디시플린 단계에서 이 파일을 읽고, 현재 `frontmatter.domain_id`와 채널에 범위가 맞는 블록만 적용합니다. 범위 없는 블록(예: 최상위 `## glossary`)은 전역 적용됩니다.

브랜드 키트 vs voice-overrides 사용 기준:
- **브랜드 키트**: 문장 수준 레지스터 — *이 브랜드는 어떻게 말해야 하나?*
- **voice-overrides**: 채널/도메인별 예외 — *이 브랜드, 이 채널에서는 X를 덮어써라.*
- 한 AEKO 설치에서 여러 브랜드를 운영한다면 voice-overrides가 필수입니다 — 브랜드 키트는 한 번에 하나의 보이스만 다룹니다.

## 8. 기여하기

당신의 예시나 레시피가 브랜드에 종속되지 않고 PII가 제거되었다면 [`AEKO-Intelligence/aeko-plugin`](https://github.com/AEKO-Intelligence/aeko-plugin)에 PR을 열어주세요. 다른 AEKO 사용자에게도 도움이 됩니다. 우리는 특정 브랜드 보이스가 아니라 **명확한 구조 패턴**(예: "감각적 후크가 있는 한국 라이프스타일 1인칭 리뷰")을 보여주는 예시를 큐레이션합니다.

수용 기준:
- 실제 PII 없음 (이름, 이메일, 주문번호, 내부 SKU).
- 재배포 권한이 없는 콘텐츠 없음.
- 특정 브랜드 보이스가 아닌, 구조 패턴을 보여줄 것.
- 패턴당 하나의 예시 — 같은 후크 스타일의 12개 변종은 받지 않습니다.

커스텀 레시피(위 옵션 B) PR도 환영합니다. 빌트인에 추가하고 싶은 채널: LinkedIn, Threads, X 롱포스트, Substack, 네이버 카페.

## 9. 레이아웃 참조

세 executor 스킬 모두 동일한 `references/{recipes,examples,style}/` 레이아웃:

```
skills/aeko-create-content/
├── SKILL.md                                    ← 실행기 로직 (포크하지 않는 한 편집 금지)
└── references/
    ├── recipes/                                ← 채널별 구조 규칙 (편집 금지)
    │   ├── press_release.md
    │   ├── magazine.md
    │   ├── instagram.md
    │   ├── naver_blog.md
    │   ├── tiktok.md
    │   ├── tistory.md
    │   ├── youtube.md
    │   └── editorial-html-jsonld.md
    ├── examples/                               ← 커스터마이징은 여기서
    │   ├── README.md
    │   ├── blog-example.md                     ← 편집 대상
    │   ├── instagram-post-example.md           ← 편집 대상
    │   ├── in-store-content-example.md        ← 편집 대상
    │   ├── press-release-example.md           ← 편집 대상
    │   ├── context-reviews-fixture.md          ← fallback/eval fixture
    │   └── aeko_shop-fixture.*                 ← 참고용
    └── style/
        └── voice-overrides.md                  ← 멀티브랜드 / 채널별 규칙 시 편집

skills/aeko-update-pdp/
├── SKILL.md
└── references/
    ├── recipes/                                ← 편집 금지
    │   ├── pdp-scaffold.md
    │   ├── responsive-html-contract.md
    │   └── json-ld-schemas.md
    ├── prompts/
    │   └── verification-prompts.md             ← Step 5b 프롬프트 템플릿
    ├── examples/                               ← 커스터마이징은 여기서
    │   ├── README.md
    │   ├── pdp-html-example.html               ← 편집 대상
    │   └── json-ld-preferences.json            ← 편집 대상
    └── style/
        └── voice-overrides.md                  ← 도메인별 규칙 시 편집

skills/aeko-fix-technical/
├── SKILL.md
└── references/
    ├── recipes/                                ← 편집 금지
    │   ├── llms-txt.md
    │   ├── robots-txt-patch.md
    │   ├── json-ld.md
    │   └── deploy-checklist.md
    ├── examples/                               ← 커스터마이징은 여기서
    │   ├── README.md
    │   ├── llms-txt-example.txt                ← 편집 대상
    │   ├── robots-txt-additions-example.txt    ← 편집 대상
    │   ├── json-ld-example.json                ← 편집 대상
    │   └── deploy-notes-example.md             ← 편집 대상
    └── style/
        └── voice-overrides.md                  ← 도메인별 기술 컨벤션 시 편집
```

리서치, 리포팅, 브랜드 키트 등 다른 AEKO 스킬은 현재 `references/`를 사용하지 않습니다 — Anthropic의 1,500단어 목표 미만이며 추출이 도움 되는 종류의 커스터마이즈 가능한 구조 디테일이 없습니다.
