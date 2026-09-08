---
name: aeko-start
description: >
  Zero-account welcome flow for new AEKO plugin users. Tours the free
  workflows, checks the local plugin, offers optional AEKO depth, and preserves
  local customization in the selected brand-owned package. Never probes an AEKO
  account, publishes, or writes back to the AEKO source repo.
argument-hint: none
allowed-tools: Read, Write, Edit, Glob, Bash, WebFetch
---

# AEKO Start

> 한국어 버전은 이 문서 하단의 [한국어 가이드](#한국어-가이드) 섹션을 참고하세요.

A friendly first-run guide. Five phases — Welcome → Free skill catalog → Local setup check → Customize →
Wrap-up. The entire tour works without an AEKO account. AEKO connection is an optional depth step, never a
gate. The skill detects the user's preferred chat language and mirrors it from Phase 2 onward. It never
publishes, never edits the AEKO source repo, and never executes other skills on the user's behalf.

Use when the user types `/aeko-start`, just installed the plugin, or asks "where do I start with AEKO?"

## Marketer-facing output contract

Assume the user is a non-technical ecommerce marketer. Lead with what works now for free: audit a site,
audit a PDP, rebuild PDP HTML, and review ads through the user's own connectors/exports. Present connected
AEKO workflows afterward as optional depth. Keep setup checks short and translate technical failures into
exact next actions.

Language: mirror the user's chat language for all user-facing steps, questions, summaries, risk notes, and next actions. Keep slash commands, IDs, file paths, channel slugs, schema keys, frontmatter terms, and tool names in English/ASCII. Treat generated content language separately from the conversation language.

---

## Step 1 — Welcome

Greet with a short English/Korean starter so a Korean user can switch to KO immediately. Keep it short — six lines maximum.

```
Welcome to AEKO. I'll walk you through four quick parts:
  1. Tour the skills you now have
  2. Confirm the local plugin is healthy
  3. Help you tailor the executor skills to your brand
  4. Recap and point you at a sensible next step

AEKO에 오신 것을 환영합니다. 네 가지로 짧게 안내드리겠습니다:
  1. 사용 가능한 스킬 둘러보기
  2. 로컬 플러그인 상태 확인
  3. 실행 스킬을 브랜드에 맞게 커스터마이즈
  4. 요약 및 다음 단계 안내

Reply in your preferred language — English, Korean, or another language. I'll match that language for the rest of this run.
```

After the user's first substantive reply, set `session_language` to the detected chat language:
- Reply contains any Hangul → `ko`.
- Clear English / mixed code-switching with no Hangul → `en`.
- Other clear language signals → use the obvious language name/code (for example `ja`, `zh`, `es`, `fr`) and translate natural-language guidance into that language.
- If the user replies only `/aeko-start` again with no prose, keep the next message short and ask them to reply once in their preferred language. Do not assume Korean or English.

Mirror `session_language` for every subsequent prompt and table caption. Code blocks, slash commands, frontmatter terms, and tool names stay verbatim regardless of language.

---

## Step 2 — Skill catalog

List the current skills grouped by marketer journey so the user can see the surface area at a glance. Render
as a markdown table; mirror header labels in `session_language`.

| Group | Slash command | One-liner |
|---|---|---|
| **Start here** | `/aeko-start` | Zero-account first-run tour and local setup check. |
| **Free · no account** | `/aeko-site-audit <url>` | Checks whether a public site is readable by AI. |
|  | `/aeko-pdp-audit <url-or-file>` | Shows what AI can read on one PDP, including image-only facts. |
|  | `/aeko-pdp-build <facts-or-url>` | Builds responsive, paste-ready PDP HTML + JSON-LD without a store write. |
|  | `/aeko-ads-review` | Four-platform glance: three free customer connectors plus an account-gated OpenAI Ads row. |
|  | `/aeko-connect` | Shows which source and delivery slots are connected and how to fill the rest. |
|  | `/aeko-ga4` | Reads traffic through the user's own GA4 connector or an optional AEKO rung. |
|  | `/aeko-weekly-report` | Assembles the current normalized evidence into a provenance-carrying report. |
| **Weekly loop · no account** | `/aeko-create-loop` | Interactively composes, installs, and foreground dry-runs the weekly loop. |
|  | `/aeko-run-loop config=<notion-page-id>` | Scheduled read-and-propose entry point; scheduled marketing writes remain unsupported. |
| **AEKO depth (optional account)** | `/aeko-action-center` | Shows pending Technical, Product-page, and Content work. |
|  | `/aeko-store mode=setup` | Add a domain, connect or inject products, set markets, and accept starter prompts through MCP. |
| **Visibility & research** | `/aeko-ai-visibility` | AEO score, mentions, citations, sentiment over a window. |
|  | `/aeko-source-analysis <prompt-id>` | Shows why one tracked prompt wins or loses across AI platforms. |
|  | `/aeko-manage-prompts mode=discover` | Discover and track prompts your audience actually asks. |
|  | `/aeko-manage-prompts mode=review` | Review quota, segment tracked prompts by angles, and untrack selected prompts. |
|  | `/aeko-competitor-analysis scope=brand` | Brand-level positioning vs. competitors in AI answers. |
|  | `/aeko-competitor-analysis scope=product` | Product-level matrix: JSON-LD, FAQ, reviews, gaps. |
|  | `/aeko-source-analysis domain_id=<uuid> source_id=<uuid>` | Checks one AI-cited page against verified brand and official-product evidence. |
| **Executors (customizable)** | `/aeko-update-pdp` | Product page improvement with shopper copy, review proof, FAQ, and AI-readable facts. |
|  | `/aeko-create-content` | Multi-channel content grounded in product facts, reviews, tracked prompts, and content context. |
|  | `/aeko-fix-technical` | Technical health package for crawler access, llms.txt, robots.txt, and site schema. |
| **Agentic ads & reviews** | `/aeko-store mode=reviews` | Inject real merchant-provided or gathered reviews for stores without a review app. |
|  | `/aeko-openai-compose-ads` | Account-gated composition of paused, review-grounded OpenAI Ads groups. |
|  | `/aeko-openai-ads-reporting` | Account-gated client-ready OpenAI Ads report with optional organic AI visibility. |
|  | `/aeko-openai-budget-shift` | Account-gated dry-run and confirmation for OpenAI Ads budget optimization. |
|  | `/aeko-openai-guardrails` | Account-gated auto-pause rule for runaway OpenAI Ads spend; disabled until preview and confirmation. |
| **Publish** | `/aeko-publish-content` | Publish saved content variations only after explicit confirmation. |
| **Maintenance** | `/aeko-update-pdp mode=refresh` | Refresh review facts AI can read, such as rating and review count. |

Note: for `session_language=ko`, render the One-liner column in Korean; for `session_language=en`, render it in English; for other languages, translate the human-readable group labels and one-liners naturally. Keep slash commands and skill names verbatim.

After the table, ask which free outcome they want first and route to one of the four commands. Then say that
connecting AEKO is optional and adds AI-answer history, tracked evidence, action items, and guarded store
writes/publishing. Publish remains separate on purpose: AEKO drafts first, then asks before anything goes live.

---

## Step 3 — Local setup check, no account probe

Do not call any AEKO MCP tool, inspect the AEKO tool registry, test authentication, or ask the user to
connect an account. The zero-account tour must complete even when no AEKO server exists in the session.

### 3.1 Plugin version (local)

Locate the installed `plugin.json`. Try Glob in this priority order:

1. `**/.claude-plugin/plugin.json` rooted at the user's plugin install dirs. Common Claude Desktop / Claude Code paths to check (use whichever returns a file):
   - `~/.claude/plugins/**/.claude-plugin/plugin.json`
   - `~/Library/Application Support/Claude/plugins/**/.claude-plugin/plugin.json`
   - `~/Library/Application Support/Claude/Claude Extensions/**/.claude-plugin/plugin.json`
2. If the user has the source repo cloned (developer install): `**/aeko-plugin/.claude-plugin/plugin.json`.

For each candidate `plugin.json`, `Read` it and check `name == "aeko-plugin"`. Pick the first match. If multiple match, prefer the path the user just invoked from (the SKILL.md that's running lives next to its plugin's `.claude-plugin/`).

Read `version` and `skills` fields. List `<skills_dir>` to count installed skill folders.

If no `plugin.json` is found after Glob:
- Tell the user the plugin manifest wasn't located on disk and skip this probe (it does not block Step 4 — the customize step works as long as the user can identify their install path).
- Ask the user to share the plugin's install path if they want a definitive version readout.

### 3.2 Print the zero-account status block

Render in `session_language`:

```
Setup check
  Plugin version:     <version from plugin.json> (installed at <path>)
  Skills installed:   <count from skills directory>
  Free workflows:     ready · no AEKO account required
  AEKO connection:    optional · not checked
```

If the local probe failed, say so explicitly without blocking the tour.

### 3.3 Offer optional AEKO depth

After showing and routing the four free workflows, say what an AEKO connection adds: AI-answer visibility
history, tracked prompts/citations, action items, store writes/publishing, and OpenAI Ads. Ask whether the
user wants connection instructions. If not, continue without warning. If yes, show the host-appropriate
steps for `https://aeko-intelligence.com/mcp`; do not test the account in this skill and do not gate Step 4.

---

## Step 4 — Customize the executor skills

Three executor skills accept overrides under `references/{recipes,examples,style}/`:

- `aeko-create-content` — channel recipes, brand exemplars, voice overrides
- `aeko-update-pdp` — PDP HTML structure, JSON-LD field preferences, verification prompts
- `aeko-fix-technical` — llms.txt format, robots.txt additions, JSON-LD shape

Mention that the same self-serve guide lives in `CUSTOMIZATION.md`; it is the best handoff if the user wants
to customize later instead of doing it during this start flow.

Ask the user (in `session_language`): "Want to customize one of these now? Reply with the skill name, `all` to walk through each in turn, or `skip` to wrap up."

For each skill the user picks, run the same 4-substep loop.

### 4.1 List what's already there

Glob `<plugin_root>/skills/<skill_name>/references/{recipes,examples,style}/*` and print the file tree. Tell the user what each subfolder is for:

- `recipes/` — channel- or platform-specific structure rules (`instagram.md`, `naver_blog.md`, …). The executor loads the matching one when that channel runs.
- `examples/` — reference artifacts the executor mimics (your past hits, brand-specific exemplars).
- `style/` — voice overrides scoped by `domain_id` and/or `channel`. Highest-priority voice signal.

Before saving customization, read [the local customization contract](references/customization-contract.md).
Resolve a brand-owned working package and its domain; an installation cache or shared upstream
checkout is not durable brand storage. Manual edits and a deployed backend updater target the
same portable skill/eval/wiki versions. This local setup flow does not run the updater or provide
automatic GitHub App synchronization.

### 4.2 Ask what to add or change

Common entry points (offer as a numbered pick-list):

1. Add a new recipe (e.g. "I want a recipe for `<channel>` because my brand posts there often").
2. Add an example based on something the user has already published.
3. Override voice for a specific domain.
4. Edit an existing file.

If the user picks (1) or (2), proceed to §4.3. If (3) or (4), Read the existing file, draft an Edit, confirm with the user, then Write.

### 4.3 Source the example — three tiers in priority order

For "add an example" / "add a recipe modeled on a real post":

**Tier A — `/chrome` bridge active** (Claude for Chrome connected this session):

Detect by checking for any indicator that the Chrome bridge is wired up. If unsure, ask the user once: "Is `/chrome` connected on this session?"

If yes: ask the user to authorize navigation to **one specific domain** (e.g. `instagram.com/<their-handle>`, `blog.naver.com/<their-handle>`). On their `yes`, navigate via the bridge using their authenticated session, pull the 1–3 most recent posts, and normalize each into a `references/examples/<channel>-<slug>-example.md` file.

**One-domain-per-confirmation gate.** Never navigate to a second domain without re-asking. The bridge runs against the user's full Chrome session, so silent roaming is unacceptable. If the user wants three platforms scraped, ask three separate times.

**Read-only contract.** Never click compose, never fill a post form, never publish — even when the bridge is connected. Publishing belongs to `/aeko-publish-content` (live aeko.shop posts or AEKO-owned store-blog drafts only; Tistory/Naver Blog remain manual handoffs) and remains out of scope here for user-owned channels.

**Tier B — Public URL paste**:

User pastes a URL → `WebFetch` it. Works well for Naver Blog, Tistory, public blog platforms. Returns limited content for JS-heavy platforms (Instagram, TikTok video pages); on a thin payload, fall back to Tier C.

**Tier C — Paste raw content**:

User pastes the post text directly. Save as-is, with a one-line header noting the source channel + date.

### 4.4 Write and confirm

Draft the file using the conventions of the existing files in the same folder (Read 1–2 nearby files first to match structure / heading style / tag format). Confirm the path with the user, then Write to the **selected brand-owned working package** — never the AEKO source repo.

Write path template: `<brand_working_root>/skills/<skill_name>/references/<subfolder>/<filename>.md`,
or `references/<subfolder>/<filename>.md` inside that brand's exported standalone package.

After each successful write, confirm in `session_language`:

```
Saved to <path>.
This change is saved in your brand's working package.
```

Report whether the current host has actually selected that package. If it has not,
explain the supported selection/import step before the next run; do not claim a local
save activates a hosted AEKO version or synchronizes GitHub. Verify that the selected
skill explicitly loads the new reference, updating its reference index when needed.
Only say a future run will use the change after its package selection and reference
loading are verified.

If the file already exists, show a 3-way diff (existing / proposed / merged) and ask before overwriting. Never silently clobber.

### 4.5 Skip path

User can reply `skip` or `not now` at §4.1 or any sub-step. Close cleanly with the wrap-up — no error, no warning.

---

## Step 5 — Wrap-up

Print a summary in `session_language`:

```
AEKO start complete.
  Plugin:        <version from plugin.json> · <count from skills directory> skills installed
  Free workflows: ready · no AEKO account required
  AEKO:          optional · not checked
  Customized:    aeko-create-content/references/examples/instagram-2026-summer.md
                 aeko-create-content/references/style/voice-overrides.md (edited)
  Suggested next step: <one free command matching the user's goal>
```

The "Suggested next step" line should be context-aware:

- Site readability question → `/aeko-site-audit <site-root-url-or-domain>`.
- Product-page diagnosis → `/aeko-pdp-audit <product-page-url-or-local-html-file>`.
- Paste-ready rebuilt PDP → `/aeko-pdp-build <aeko_pdp_image_facts/v1-json-or-product-url>`.
- Cross-platform ad waste → `/aeko-ads-review`.
- Only when the user explicitly chose AEKO depth → `/aeko-store mode=setup`, then
  `/aeko-manage-prompts mode=discover` or `/aeko-ai-visibility` as appropriate.

End with the docs link (`https://aeko-intelligence.com`), mention `CUSTOMIZATION.md` for the self-serve file guide, and invite them to come back to `/aeko-start` whenever they want to add more recipes / examples.

---

## What this skill never does

- Never edits the AEKO source repository (`github.com/AEKO-Intelligence/aeko-plugin`). All customization writes target the selected **brand-owned working package**.
- Never executes `/aeko-update-pdp`, `/aeko-create-content`, `/aeko-fix-technical`, or any other executor on the user's behalf. Start stops at the suggested-next-step line.
- Never publishes content — even when the `/chrome` bridge is connected. Compose forms and publish buttons are out of scope; AEKO-owned publishing lives in `/aeko-publish-content`.
- Never calls an AEKO MCP tool, probes authentication, or turns a missing account into an error.
- Never roams authenticated sites silently. Every domain navigated via the `/chrome` bridge gets one explicit user confirmation.

---

## Errors & recovery

| Failure | Behavior |
|---|---|
| `plugin.json` not found anywhere via Glob | Skip the version line; ask the user to share their install path if they want a definitive readout. Phase 4 still runs — ask the user to confirm the plugin path before any Write. |
| User pastes a URL that 404s in Tier B | Tell them, fall back to Tier C (paste raw content). |
| `/chrome` bridge missing when user expected it | Tell them how to install Claude for Chrome + connect `/chrome`, then offer to retry Tier A or fall through to Tier B. |
| Write would overwrite an existing file | Show a diff and ask. Never silently overwrite. |
| User says `skip` / `not now` at any prompt | Move to Phase 5 cleanly. |

---

## 한국어 가이드

> 위 영문 가이드의 한국어 미러입니다. 동작은 동일하며, 사용자가 한국어로 답변하면 자동으로 이 톤으로 전환됩니다. 다른 언어 사용자는 해당 언어로 대화형 안내를 제공합니다.

### 1단계 — 환영 인사

영문/한국어 환영 인사를 동시에 출력합니다. 사용자의 첫 실질 답변 언어를 감지해 `session_language`를 설정한 뒤, 이후 단계는 해당 언어로 진행합니다. 언어 신호가 없으면 선호 언어로 한 번 답해 달라고 짧게 묻고, 한국어/영어 중 하나로 임의 추정하지 않습니다.

### 2단계 — 스킬 카탈로그

현재 스킬을 마케터 여정 기준으로 묶어 표로 보여줍니다. AEKO 계정 없이 바로 실행되는 네 가지를
항상 먼저 배치합니다.

| 그룹 | 슬래시 명령 | 한 줄 설명 |
|---|---|---|
| **시작점** | `/aeko-start` | 계정 없는 첫 실행 안내와 로컬 설정 확인. |
| **무료 · 계정 불필요** | `/aeko-site-audit <url>` | 공개 사이트를 AI가 읽을 수 있는지 확인. |
|  | `/aeko-pdp-audit <url-or-file>` | 이미지 속 사실을 포함해 상품 페이지에서 AI가 읽는 내용을 확인. |
|  | `/aeko-pdp-build <facts-or-url>` | 스토어에 쓰지 않고 붙여넣기 가능한 PDP HTML + JSON-LD 생성. |
|  | `/aeko-ads-review` | 사용자 자체 커넥터 3개와 계정 기반 OpenAI Ads row를 함께 보는 4-platform 요약. |
| **AEKO 심화 (계정 선택 사항)** | `/aeko-action-center` | 대기 작업을 기술 상태, 상품 페이지, 인용 가능한 콘텐츠로 나눠 안내. |
|  | `/aeko-store mode=setup` | 도메인 추가, 스토어 연결/상품 주입, 시장 설정, 시작 프롬프트 수락. |
| **가시성 · 리서치** | `/aeko-ai-visibility` | 기간별 AEO 점수, 멘션, 인용, 감성 분석. |
|  | `/aeko-source-analysis` | 추적 중인 프롬프트 1건이 AI 플랫폼별로 왜 이기거나 지는지 분석. |
|  | `/aeko-manage-prompts mode=discover` | 사용자 오디언스가 실제로 묻는 프롬프트 발굴 + 추적. |
|  | `/aeko-manage-prompts mode=review` | 쿼터 확인, 각도별 프롬프트 정리, 선택 프롬프트 추적 중단. |
|  | `/aeko-competitor-analysis scope=brand` | AI 답변 안에서 브랜드 vs 경쟁사 포지셔닝. |
|  | `/aeko-competitor-analysis scope=product` | 제품 단위 매트릭스 (JSON-LD, FAQ, 리뷰, 빈틈). |
|  | `/aeko-source-analysis` | AI 인용 페이지 1건을 검증된 브랜드·공식 상품 근거와 비교. |
| **실행 (커스터마이즈 가능)** | `/aeko-update-pdp` | 구매자 문구, 리뷰 근거, FAQ, AI가 읽는 상품 사실로 상품 페이지 개선. |
|  | `/aeko-create-content` | 상품 사실, 리뷰, 추적 프롬프트, 콘텐츠 컨텍스트 기반 멀티채널 콘텐츠 생성. |
|  | `/aeko-fix-technical` | 크롤러 접근, llms.txt, robots.txt, 사이트 스키마를 위한 기술 상태 패키지. |
| **광고 · 리뷰** | `/aeko-store mode=reviews` | 리뷰 앱이 없는 스토어의 실제 리뷰를 주입. |
|  | `/aeko-openai-compose-ads` | AEKO 계정 기반의 컨텍스트 리뷰 기반 OpenAI Ads 그룹 구성; 일시중지 상태로 생성. |
|  | `/aeko-openai-ads-reporting` | AEKO 계정 기반의 고객용 OpenAI Ads 리포트; 선택형 organic AI visibility 포함. |
|  | `/aeko-openai-budget-shift` | AEKO 계정 기반 OpenAI Ads 예산 최적화 드라이런과 명시 확인. |
|  | `/aeko-openai-guardrails` | AEKO 계정 기반 OpenAI Ads 자동 일시중지 규칙; 미리보기와 확인 전에는 비활성. |
| **게시** | `/aeko-publish-content` | 저장된 콘텐츠 변형본을 명시 확인 후 게시. |
| **유지보수** | `/aeko-update-pdp mode=refresh` | 평점과 리뷰 수처럼 AI가 읽는 리뷰 사실 새로고침. |

**실행 (커스터마이즈 가능)** 그룹의 3개 스킬은 `references/recipes/`, `references/examples/`, `references/style/` 하위 파일을 통해 브랜드별로 덮어쓸 수 있습니다. 자세한 내용은 4단계에서 안내합니다.

### 3단계 — 설치 상태 점검

1. **플러그인 버전 (로컬).** 설치된 `plugin.json`을 Glob으로 찾아 `version`, `skills` 필드를 읽습니다. 검색 경로 우선순위는 영문 가이드의 §3.1과 동일합니다.
2. **계정 없는 상태 블록.** `무료 워크플로: 준비됨 · AEKO 계정 불필요`,
   `AEKO 연결: 선택 사항 · 확인하지 않음`을 표시합니다.
3. **선택형 심화.** 네 가지 무료 워크플로를 먼저 안내한 뒤, 사용자가 원할 때만 AEKO 연결이
   추가하는 AI 답변 이력, 추적 근거, 액션 아이템, 보호된 스토어 쓰기/게시를 설명합니다.

이 스킬은 AEKO MCP 도구를 호출하거나 인증 상태를 검사하지 않습니다. 계정이 없어도 4단계와
5단계까지 모두 진행합니다.

### 4단계 — 실행 스킬 커스터마이즈

세 실행 스킬(`aeko-create-content`, `aeko-update-pdp`, `aeko-fix-technical`)에 대해 동일한 4단계 루프를 돕니다. 나중에 직접 파일을 수정하고 싶다면 같은 내용이 `CUSTOMIZATION.md`에 정리되어 있다고 안내합니다.

1. **현재 파일 트리 보여주기** — `references/recipes`, `references/examples`, `references/style`을 Glob으로 나열하고 각 폴더의 역할을 설명합니다.
2. **무엇을 추가/수정할지 묻기** — 새 레시피 추가, 예시 추가, 음성 톤 오버라이드, 기존 파일 편집 중 선택.
3. **예시 출처 — 우선순위 3계층:**
   - **A — `/chrome` 브릿지 사용**: Claude for Chrome이 연결되어 있고 사용자가 동의하면, 사용자의 인증된 세션으로 단일 도메인 1개에 한정해 최근 게시물 1–3개를 읽어와 `references/examples/<채널>-<slug>-example.md`로 저장합니다. **도메인 1개당 사용자 명시 동의 필수.** 절대 게시·작성 폼 클릭 없이 읽기 전용으로만 동작합니다.
   - **B — 공개 URL 붙여넣기**: 사용자가 URL을 주면 `WebFetch`로 가져옵니다. 네이버 블로그·티스토리는 잘 됩니다. 인스타그램·틱톡 비디오 페이지는 페이로드가 빈약하면 C로 폴백.
   - **C — 본문 직접 붙여넣기**: 사용자가 글을 직접 붙여 넣으면 채널·날짜 헤더를 한 줄 추가해 그대로 저장.
4. **저장 + 확인** — 같은 폴더의 기존 파일 1–2개를 Read해 구조/헤딩 스타일/태그 형식을 맞춘 뒤, 사용자에게 경로를 확인받고 **선택된 브랜드 소유 작업 패키지**에만 Write합니다. 설치 캐시를 유일한 저장소로 쓰지 않습니다. AEKO 저장소에는 절대 쓰지 않습니다. 동일 파일이 이미 있으면 3-way 차이점을 보여주고 묻습니다.

`skip` / `not now` 답변 시 5단계로 깔끔하게 넘어갑니다.

### 5단계 — 마무리

요약 블록에 `무료 워크플로: 준비됨`, `AEKO: 선택 사항 · 확인하지 않음`을 출력합니다. 사용자의
목표에 따라 `/aeko-site-audit`, `/aeko-pdp-audit`, `/aeko-pdp-build`, `/aeko-ads-review` 중 하나를
다음 명령으로 추천합니다. 사용자가 AEKO 심화를 명시적으로 선택했을 때만 `/aeko-store mode=setup`
등의 연결형 명령을 제안합니다.

### 이 스킬이 절대 하지 않는 것

- AEKO 소스 저장소 수정 — 모든 Write는 사용자의 로컬 설치 경로에만.
- 다른 실행 스킬을 사용자 대신 실행 — 5단계 마무리 안내까지만.
- 콘텐츠 게시 — `/chrome` 브릿지가 연결되어 있어도 작성 폼 클릭·게시는 본 스킬 범위 밖. AEKO 자체 채널(aeko.shop / Tistory / Naver Blog) 게시는 `/aeko-publish-content`.
- AEKO MCP 호출 또는 인증 상태 검사 — 계정 연결은 선택 사항이며 이 스킬의 게이트가 아닙니다.
- `/chrome` 브릿지에서 사용자 동의 없이 다른 도메인으로 이동 — 도메인당 1회 동의 원칙.

### 에러와 복구

영문 가이드의 표와 동일합니다. 사용자 언어가 한국어인 경우 위 표를 한국어로 미러링해 출력하세요 (셀 내용을 그대로 번역).
