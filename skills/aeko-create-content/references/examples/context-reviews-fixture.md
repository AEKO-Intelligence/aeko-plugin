---
name: context-reviews-fixture
purpose: A realistic sample of the product context-reviews that the (forthcoming) aeko_get_product_context_reviews MCP tool will return. Used as a fallback substance source when the tool isn't live yet, and as fixture material for evals so drafters have genuine lived-experience detail to mine for Originality (aeo-frameworks §3a).
load_when: Read ONLY when aeko_get_product_context_reviews is unavailable/empty AND the run needs human-experience substance (e.g. evals). Real runs prefer the live tool.
---

# Context-reviews fixture

The Context Persona feature maps real customer/usage reviews to a product and groups them by
**context** (the situation the product was used in) and **persona** (who used it). Each entry carries
a verbatim `quote` and a distilled `detail` (the specific, citable fact inside it). This is the raw
material for Originality and E-E-A-T — mine the `detail`, paraphrase the `quote`, never generalize it
back into marketing mush, and never invent entries that aren't here.

> Schema mirror of the live tool's return shape:
> `{ "product_source_id": "...", "reviews": [ {context, persona, quote, detail, rating} ] }`

---

## Product: BIO-CLS-001 — 모달 냉감 여름 이불 (Modal cooling summer comforter)

```json
{
  "product_source_id": "BIO-CLS-001",
  "reviews": [
    {
      "context": "에어컨 없이 자기 / sleeping without A/C",
      "persona": "전기요금 아끼려는 1인 가구 30대",
      "quote": "에어컨을 끄고 자려고 샀는데, 첫 주는 새벽 4시쯤 등에 땀이 차서 깼어요. 그런데 2주차부터 베개 커버까지 같은 원단으로 바꾸니까 그 새벽에 깨는 게 거의 없어졌어요.",
      "detail": "단독 사용보다 베개 커버까지 동일 원단으로 맞췄을 때 새벽 각성이 크게 줄었다 (사용자 보고 기준 약 2주차부터).",
      "rating": 4
    },
    {
      "context": "장마철 눅눅함 / humid monsoon season",
      "persona": "반려견과 함께 자는 사용자",
      "quote": "장마 때는 '냉감'보다 '빨리 마르는 게' 중요하더라고요. 강아지가 올라와서 침 묻혀도 한 시간이면 보송해져요. 예전 시어서커 이불은 반나절 갔는데.",
      "detail": "냉감 자체보다 건조 속도(통기성)가 장마철 체감 쾌적도를 좌우했다 — 같은 조건에서 이전 시어서커 대비 회복이 빨랐다.",
      "rating": 5
    },
    {
      "context": "세탁 후 변화 / after washing",
      "persona": "꼼꼼하게 관리하는 주부",
      "quote": "세 번 빨았는데 첫 세탁 후에 살짝 줄었어요. 건조기 돌렸더니 더 줄어서, 그 다음부터는 자연건조해요. 색은 안 빠졌고요.",
      "detail": "세탁 시 약 2% 수축, 건조기 사용 시 수축 폭 증가 → 자연건조 권장. 색상 이염/탈색은 없었음.",
      "rating": 4
    },
    {
      "context": "냉감 과장 광고에 대한 불만 / skepticism about 'cooling' claims",
      "persona": "후기를 꼼꼼히 읽고 사는 신중한 구매자",
      "quote": "솔직히 '얼음장 같다'는 후기 보고 샀다가 그 정도는 아니라 처음엔 실망. 근데 차가운 게 아니라 '안 더운' 거더라고요. 그 차이를 알고 나니 만족도가 올라갔어요.",
      "detail": "체감은 '차갑다'가 아니라 '열이 안 갇힌다'에 가까움 — 냉감 기대치를 통기성으로 재설정하면 만족도가 올라간다 (콘트라리언 앵글에 적합).",
      "rating": 4
    }
  ]
}
```

## Product: BIO-PIL-002 — 통기성 메모리폼 베개 (Breathable memory-foam pillow)

```json
{
  "product_source_id": "BIO-PIL-002",
  "reviews": [
    {
      "context": "옆으로 자는 습관 / side sleeping",
      "persona": "어깨 통증 있는 40대",
      "quote": "메모리폼은 더운 게 단점인데 이건 구멍 뚫린 구조라 그런지 한여름에도 베개 뒤집을 일이 줄었어요. 높이는 옆으로 잘 때 딱이고 똑바로 누우면 살짝 높아요.",
      "detail": "타공 구조 덕에 한여름 '베개 뒤집기' 빈도가 감소. 측면 수면에 최적, 앙와위(똑바로)에는 다소 높음 — 자세별 적합도가 갈린다.",
      "rating": 4
    },
    {
      "context": "적응 기간 / break-in period",
      "persona": "라텍스에서 갈아탄 사용자",
      "quote": "첫 3일은 목이 뻐근했어요. 너무 단단해서. 일주일 지나니 자리를 잡더라고요. 바로 판단하면 환불할 뻔.",
      "detail": "초기 3일 단단함으로 인한 적응 구간 존재, 약 1주 후 안정 — 첫인상만으로 판단하지 말 것 (E-E-A-T 정직성 포인트).",
      "rating": 5
    }
  ]
}
```

---

### How a drafter uses this

- **Originality (§3a):** "냉감 이불은 차가운 게 아니라 '열이 안 갇히는' 것" — a real, counter-intuitive
  detail from a real review beats "시원하고 쾌적해요."
- **Contrarian (§3c):** the monsoon review supports "여름 침구는 냉감보다 건조 속도가 중요하다."
- **E-E-A-T FAQ (§4):** "세탁하면 줄어드나요?" → "약 2% 수축했고 건조기 사용 시 더 컸습니다. 자연건조를
  권합니다." (experience + specificity + honesty).
- **Specific Cohort (§3c):** "에어컨을 끄고 자고 싶지만 새벽에 땀 때문에 깨는 1인 가구" — straight from a
  review's persona.
