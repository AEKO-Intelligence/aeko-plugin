---
name: aeko-onboarding
description: >
  Welcome flow for new AEKO plugin users. Tours available skills,
  verifies plugin version + MCP connectivity, and helps customize
  the three executor skills (`aeko-create-content`, `aeko-update-pdp`,
  `aeko-fix-technical`) with brand-specific recipes, examples, and
  voice overrides in the user's local plugin install. Read-only:
  never publishes, never writes back to the AEKO repo.
argument-hint: none
allowed-tools: aeko_list_domains, Read, Write, Edit, Glob, Bash, WebFetch
---

# AEKO Onboarding

> 한국어 버전은 이 문서 하단의 [한국어 가이드](#한국어-가이드) 섹션을 참고하세요.

A friendly first-run guide. Five phases — Welcome → Skill catalog → Setup check → Customize → Wrap-up. The skill detects the user's preferred chat language and mirrors that language from Phase 2 onward. English and Korean have curated copy; other languages are supported conversationally. It never publishes, never edits the AEKO source repo, never executes other skills on the user's behalf.

Use when the user types `/aeko-onboarding`, just installed the plugin, or asks "where do I start with AEKO?"

## Marketer-facing output contract

Assume the user is a non-technical ecommerce marketer. Explain AEKO as three journeys: see where AI finds us,
fix what blocks AI discovery, and improve products/content AI can cite. Keep setup checks short and translate
technical failures into exact next actions.

Language: mirror the user's chat language for all user-facing steps, questions, summaries, risk notes, and next actions. Keep slash commands, IDs, file paths, channel slugs, schema keys, frontmatter terms, and tool names in English/ASCII. Treat generated content language separately from the conversation language.

---

## Step 1 — Welcome

Greet with a short English/Korean starter so a Korean user can switch to KO immediately. Keep it short — six lines maximum.

```
Welcome to AEKO. I'll walk you through five quick steps:
  1. Tour the skills you now have
  2. Confirm the plugin + MCP are healthy
  3. Help you tailor the executor skills to your brand
  4. Recap and point you at a sensible next step

AEKO에 오신 것을 환영합니다. 다섯 단계로 안내드리겠습니다:
  1. 사용 가능한 스킬 둘러보기
  2. 플러그인과 MCP 연결 상태 확인
  3. 실행 스킬을 브랜드에 맞게 커스터마이즈
  4. 요약 및 다음 단계 안내

Reply in your preferred language — English, Korean, or another language. I'll match that language for the rest of this run.
```

After the user's first substantive reply, set `session_language` to the detected chat language:
- Reply contains any Hangul → `ko`.
- Clear English / mixed code-switching with no Hangul → `en`.
- Other clear language signals → use the obvious language name/code (for example `ja`, `zh`, `es`, `fr`) and translate natural-language guidance into that language.
- If the user replies only `/aeko-onboarding` again with no prose, keep the next message short and ask them to reply once in their preferred language. Do not assume Korean or English.

Mirror `session_language` for every subsequent prompt and table caption. Code blocks, slash commands, frontmatter terms, and tool names stay verbatim regardless of language.

---

## Step 2 — Skill catalog

List the 20 skills grouped by marketer journey so the user can see the surface area at a glance. Render as a markdown table; mirror header labels in `session_language`.

| Group | Slash command | One-liner |
|---|---|---|
| **Start here** | `/aeko-action-center` | Shows pending work as Technical health, Product pages, and Content AI can cite. |
|  | `/aeko-onboarding` | Guided first-run setup check and skill tour. |
|  | `/aeko-setup-store` | Add a domain, connect or inject products, set markets, and accept starter prompts through MCP. |
| **Visibility & research** | `/aeko-visibility-report` | AEO score, mentions, citations, sentiment over a window. |
|  | `/aeko-prompt-deep-dive` | Shows why one tracked prompt wins or loses across AI platforms. |
|  | `/aeko-find-prompts-to-track` | Discover and track prompts your audience actually asks. |
|  | `/aeko-manage-tracked-prompts` | Review quota, segment tracked prompts by angles, and untrack selected prompts. |
|  | `/aeko-brand-competitor-analysis` | Brand-level positioning vs. competitors in AI answers. |
|  | `/aeko-product-competitor-analysis` | Product-level matrix: JSON-LD, FAQ, reviews, gaps. |
|  | `/aeko-check-source` | Checks one AI-cited page against verified brand and official-product evidence. |
| **Executors (customizable)** | `/aeko-update-pdp` | Product page improvement with shopper copy, review proof, FAQ, and AI-readable facts. |
|  | `/aeko-create-content` | Multi-channel content grounded in product facts, reviews, tracked prompts, and content context. |
|  | `/aeko-fix-technical` | Technical health package for crawler access, llms.txt, robots.txt, and site schema. |
| **Agentic ads & reviews** | `/aeko-inject-reviews` | Inject real merchant-provided or gathered reviews for stores without a review app. |
|  | `/aeko-compose-ads` | Compose paused, review-grounded OpenAI Ads groups from contextual reviews. |
|  | `/aeko-ad-report` | Produce a paid-ad performance report from OpenAI Ads metrics. |
|  | `/aeko-optimize-budget` | Dry-run and confirm guarded campaign budget optimization. |
| **Publish** | `/aeko-publish-content` | Publish saved content variations only after explicit confirmation. |
| **Maintenance** | `/aeko-refresh-jsonld` | Refresh review facts AI can read, such as rating and review count. |
|  | `/aeo-audit` | Generic AEO audit; add `shopping` for product-level AI shopping readiness. |

Note: for `session_language=ko`, render the One-liner column in Korean; for `session_language=en`, render it in English; for other languages, translate the human-readable group labels and one-liners naturally. Keep slash commands and skill names verbatim.

After the table, say: "Most users should start with `/aeko-action-center` or `/aeko-visibility-report`. Publish is separate on purpose: AEKO drafts first, then asks before anything goes live."

---

## Step 3 — Setup check

Run two probes in parallel and report both in one block.

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
- Tell the user the plugin manifest wasn't located on disk and skip this probe (it does not block Phase 4 — the customize step works as long as the user can identify their install path).
- Ask the user to share the plugin's install path if they want a definitive version readout.

### 3.2 MCP connectivity

Call `aeko_list_domains`.

- **Success** (any HTTP 2xx, even with empty list): MCP is reachable and authenticated. Capture `domains.length`. If `domains.length == 0`, suggest `/aeko-setup-store` as the next step instead of sending the user to the dashboard.
- **401 / authentication error**: tell the user the AEKO connector isn't authenticated. Instruct: "Open Claude → Settings → Connectors → AEKO → re-authenticate at `https://aeko-intelligence.com/mcp`, then re-run `/aeko-onboarding`." Stop here; do NOT proceed to Phase 4 until reachable.
- **Other failures** (5xx, network): report verbatim. Offer to continue to Phase 4 in a degraded mode (the customization step uses local file edits, no MCP needed) but warn that visibility / executor skills will fail until the connector is reachable again.

### 3.3 Print the status block

Render in `session_language`:

```
Setup check
  Plugin version:     <version from plugin.json> (installed at <path>)
  Skills installed:   <count from skills directory>
  MCP connector:      connected · 2 domain(s) on file
```

If a probe failed, say so explicitly. Never invent a version string for the MCP server (no version endpoint exists) — only state "connected" or the failure mode.

---

## Step 4 — Customize the executor skills

Three executor skills accept overrides under `references/{recipes,examples,style}/`:

- `aeko-create-content` — channel recipes, brand exemplars, voice overrides
- `aeko-update-pdp` — PDP HTML structure, JSON-LD field preferences, verification prompts
- `aeko-fix-technical` — llms.txt format, robots.txt additions, JSON-LD shape

Mention that the same self-serve guide lives in `CUSTOMIZATION.md`; it is the best handoff if the user wants
to customize later instead of doing it during onboarding.

Ask the user (in `session_language`): "Want to customize one of these now? Reply with the skill name, `all` to walk through each in turn, or `skip` to wrap up."

For each skill the user picks, run the same 4-substep loop.

### 4.1 List what's already there

Glob `<plugin_root>/skills/<skill_name>/references/{recipes,examples,style}/*` and print the file tree. Tell the user what each subfolder is for:

- `recipes/` — channel- or platform-specific structure rules (`instagram.md`, `naver_blog.md`, …). The executor loads the matching one when that channel runs.
- `examples/` — reference artifacts the executor mimics (your past hits, brand-specific exemplars).
- `style/` — voice overrides scoped by `domain_id` and/or `channel`. Highest-priority voice signal.

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

**Read-only contract.** Never click compose, never fill a post form, never publish — even when the bridge is connected. Publishing belongs to `/aeko-publish-content` (for AEKO-owned channels: aeko.shop / Tistory / Naver Blog) and remains out of scope here for user-owned channels.

**Tier B — Public URL paste**:

User pastes a URL → `WebFetch` it. Works well for Naver Blog, Tistory, public blog platforms. Returns limited content for JS-heavy platforms (Instagram, TikTok video pages); on a thin payload, fall back to Tier C.

**Tier C — Paste raw content**:

User pastes the post text directly. Save as-is, with a one-line header noting the source channel + date.

### 4.4 Write and confirm

Draft the file using the conventions of the existing files in the same folder (Read 1–2 nearby files first to match structure / heading style / tag format). Confirm the path with the user, then Write to the **local plugin install** — never the AEKO source repo.

Write path template: `<plugin_root>/skills/<skill_name>/references/<subfolder>/<filename>.md`

After each successful write, confirm in `session_language`:

```
Saved to <path>.
Next /<skill_name> run will pick it up automatically.
```

If the file already exists, show a 3-way diff (existing / proposed / merged) and ask before overwriting. Never silently clobber.

### 4.5 Skip path

User can reply `skip` or `not now` at §4.1 or any sub-step. Close cleanly with the wrap-up — no error, no warning.

---

## Step 5 — Wrap-up

Print a summary in `session_language`:

```
Onboarding complete.
  Plugin:        <version from plugin.json> · <count from skills directory> skills installed
  MCP:           connected · 2 domain(s)
  Customized:    aeko-create-content/references/examples/instagram-2026-summer.md
                 aeko-create-content/references/style/voice-overrides.md (edited)
  Suggested next step: /aeko-action-center <domain_id>
```

The "Suggested next step" line should be context-aware:

- Customized `aeko-create-content` → `/aeko-create-content <item_id>` (or `/aeko-action-center <domain_id> content` if no item handy).
- Customized `aeko-update-pdp` → `/aeko-action-center <domain_id> pdp`.
- Customized `aeko-fix-technical` → `/aeko-action-center <domain_id> technical`.
- Skipped Phase 4 with at least one domain → `/aeko-action-center <domain_id>` (or `/aeko-visibility-report <domain_id>` if no domain has pending items).
- No domains connected → `/aeko-setup-store`.

End with the docs link (`https://aeko-intelligence.com`), mention `CUSTOMIZATION.md` for the self-serve file guide, and invite them to come back to `/aeko-onboarding` whenever they want to add more recipes / examples.

---

## What this skill never does

- Never edits the AEKO source repository (`github.com/AEKO-Intelligence/aeko-plugin`). All Writes target the user's **local plugin install**.
- Never executes `/aeko-update-pdp`, `/aeko-create-content`, `/aeko-fix-technical`, or any other executor on the user's behalf. Onboarding stops at the suggested-next-step line.
- Never publishes content — even when the `/chrome` bridge is connected. Compose forms and publish buttons are out of scope; AEKO-owned publishing lives in `/aeko-publish-content`.
- Never fabricates an MCP version string. There is no version endpoint on `https://aeko-intelligence.com/mcp` — report only "connected" / "not connected" / specific failure mode.
- Never roams authenticated sites silently. Every domain navigated via the `/chrome` bridge gets one explicit user confirmation.

---

## Errors & recovery

| Failure | Behavior |
|---|---|
| `aeko_list_domains` returns 401 | Halt at Phase 3. Tell user to re-auth the AEKO connector. Do not proceed to Phase 4. |
| `aeko_list_domains` returns 5xx / network error | Surface the error verbatim. Offer to continue to Phase 4 in degraded mode (file edits work without MCP). |
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

20개의 스킬을 마케터 여정 기준으로 묶어 표로 보여줍니다.

| 그룹 | 슬래시 명령 | 한 줄 설명 |
|---|---|---|
| **시작점** | `/aeko-action-center` | 대기 작업을 기술 상태, 상품 페이지, 인용 가능한 콘텐츠로 나눠 안내. |
|  | `/aeko-onboarding` | 첫 실행 설정 확인과 스킬 안내. |
|  | `/aeko-setup-store` | 도메인 추가, 스토어 연결/상품 주입, 시장 설정, 시작 프롬프트 수락. |
| **가시성 · 리서치** | `/aeko-visibility-report` | 기간별 AEO 점수, 멘션, 인용, 감성 분석. |
|  | `/aeko-prompt-deep-dive` | 추적 중인 프롬프트 1건이 AI 플랫폼별로 왜 이기거나 지는지 분석. |
|  | `/aeko-find-prompts-to-track` | 사용자 오디언스가 실제로 묻는 프롬프트 발굴 + 추적. |
|  | `/aeko-manage-tracked-prompts` | 쿼터 확인, 각도별 프롬프트 정리, 선택 프롬프트 추적 중단. |
|  | `/aeko-brand-competitor-analysis` | AI 답변 안에서 브랜드 vs 경쟁사 포지셔닝. |
|  | `/aeko-product-competitor-analysis` | 제품 단위 매트릭스 (JSON-LD, FAQ, 리뷰, 빈틈). |
|  | `/aeko-check-source` | AI 인용 페이지 1건을 검증된 브랜드·공식 상품 근거와 비교. |
| **실행 (커스터마이즈 가능)** | `/aeko-update-pdp` | 구매자 문구, 리뷰 근거, FAQ, AI가 읽는 상품 사실로 상품 페이지 개선. |
|  | `/aeko-create-content` | 상품 사실, 리뷰, 추적 프롬프트, 콘텐츠 컨텍스트 기반 멀티채널 콘텐츠 생성. |
|  | `/aeko-fix-technical` | 크롤러 접근, llms.txt, robots.txt, 사이트 스키마를 위한 기술 상태 패키지. |
| **광고 · 리뷰** | `/aeko-inject-reviews` | 리뷰 앱이 없는 스토어의 실제 리뷰를 주입. |
|  | `/aeko-compose-ads` | 컨텍스트 리뷰 기반의 일시중지 상태 OpenAI Ads 그룹 구성. |
|  | `/aeko-ad-report` | OpenAI Ads 성과 리포트 생성. |
|  | `/aeko-optimize-budget` | 확인 후 실행되는 예산 최적화 드라이런. |
| **게시** | `/aeko-publish-content` | 저장된 콘텐츠 변형본을 명시 확인 후 게시. |
| **유지보수** | `/aeko-refresh-jsonld` | 평점과 리뷰 수처럼 AI가 읽는 리뷰 사실 새로고침. |
|  | `/aeo-audit` | 일반 AEO 진단; `shopping`을 붙이면 상품 단위 AI 쇼핑 준비도 진단. |

**실행 (커스터마이즈 가능)** 그룹의 3개 스킬은 `references/recipes/`, `references/examples/`, `references/style/` 하위 파일을 통해 브랜드별로 덮어쓸 수 있습니다. 자세한 내용은 4단계에서 안내합니다.

### 3단계 — 설치 상태 점검

1. **플러그인 버전 (로컬).** 설치된 `plugin.json`을 Glob으로 찾아 `version`, `skills` 필드를 읽습니다. 검색 경로 우선순위는 영문 가이드의 §3.1과 동일합니다.
2. **MCP 연결.** `aeko_list_domains`를 한 번 호출합니다.
   - 200 응답 → "connected"으로 표시하고 도메인 수를 보고합니다.
   - 401 → AEKO 커넥터 재인증 안내 후 4단계 진행을 중단합니다.
   - 5xx / 네트워크 에러 → 에러 그대로 표시하고, 4단계는 파일 편집만으로도 가능하므로 degraded 모드로 진행할지 사용자에게 묻습니다.
상태 블록을 한국어 라벨로 출력합니다 — MCP 서버 버전은 엔드포인트가 없으므로 절대 임의의 버전 문자열을 만들지 않습니다.

### 4단계 — 실행 스킬 커스터마이즈

세 실행 스킬(`aeko-create-content`, `aeko-update-pdp`, `aeko-fix-technical`)에 대해 동일한 4단계 루프를 돕니다. 나중에 직접 파일을 수정하고 싶다면 같은 내용이 `CUSTOMIZATION.md`에 정리되어 있다고 안내합니다.

1. **현재 파일 트리 보여주기** — `references/recipes`, `references/examples`, `references/style`을 Glob으로 나열하고 각 폴더의 역할을 설명합니다.
2. **무엇을 추가/수정할지 묻기** — 새 레시피 추가, 예시 추가, 음성 톤 오버라이드, 기존 파일 편집 중 선택.
3. **예시 출처 — 우선순위 3계층:**
   - **A — `/chrome` 브릿지 사용**: Claude for Chrome이 연결되어 있고 사용자가 동의하면, 사용자의 인증된 세션으로 단일 도메인 1개에 한정해 최근 게시물 1–3개를 읽어와 `references/examples/<채널>-<slug>-example.md`로 저장합니다. **도메인 1개당 사용자 명시 동의 필수.** 절대 게시·작성 폼 클릭 없이 읽기 전용으로만 동작합니다.
   - **B — 공개 URL 붙여넣기**: 사용자가 URL을 주면 `WebFetch`로 가져옵니다. 네이버 블로그·티스토리는 잘 됩니다. 인스타그램·틱톡 비디오 페이지는 페이로드가 빈약하면 C로 폴백.
   - **C — 본문 직접 붙여넣기**: 사용자가 글을 직접 붙여 넣으면 채널·날짜 헤더를 한 줄 추가해 그대로 저장.
4. **저장 + 확인** — 같은 폴더의 기존 파일 1–2개를 Read해 구조/헤딩 스타일/태그 형식을 맞춘 뒤, 사용자에게 경로를 확인받고 **로컬 플러그인 설치 경로**에만 Write합니다. AEKO 저장소에는 절대 쓰지 않습니다. 동일 파일이 이미 있으면 3-way 차이점을 보여주고 묻습니다.

`skip` / `not now` 답변 시 5단계로 깔끔하게 넘어갑니다.

### 5단계 — 마무리

요약 블록을 출력하고, 사용자가 방금 커스터마이즈한 스킬에 맞춰 다음 슬래시 명령을 추천합니다.

### 이 스킬이 절대 하지 않는 것

- AEKO 소스 저장소 수정 — 모든 Write는 사용자의 로컬 설치 경로에만.
- 다른 실행 스킬을 사용자 대신 실행 — 5단계 마무리 안내까지만.
- 콘텐츠 게시 — `/chrome` 브릿지가 연결되어 있어도 작성 폼 클릭·게시는 본 스킬 범위 밖. AEKO 자체 채널(aeko.shop / Tistory / Naver Blog) 게시는 `/aeko-publish-content`.
- MCP 서버 버전 문자열 추측 — 엔드포인트가 없으니 만들지 않습니다.
- `/chrome` 브릿지에서 사용자 동의 없이 다른 도메인으로 이동 — 도메인당 1회 동의 원칙.

### 에러와 복구

영문 가이드의 표와 동일합니다. 사용자 언어가 한국어인 경우 위 표를 한국어로 미러링해 출력하세요 (셀 내용을 그대로 번역).
