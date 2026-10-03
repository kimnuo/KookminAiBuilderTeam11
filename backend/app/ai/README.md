# app/ai (담당: 현찬)

공지 한 건을 LLM(학교 AI 게이트웨이 `ai.cs.kookmin.ac.kr`)으로 분류·요약·마감 추출한다. 분류·요약·마감은 `claude-opus-5`, 본문이 포스터 이미지뿐인 공지의 글자 읽기는 `claude-haiku-4-5` 가 맡는다(2026-10-03 기준 이 키로 쓸 수 있는 모델은 이 둘뿐이다). PRD 3절·10절·11절을 구현한다. 입력 형식이 PRD 10절과 다른 점은 아래 「입력 형식」에 적었다.

**서버 연동 상태 (2026-10-03 제출 기준).** 해서의 백엔드는 자체 `digest.py` 로 요약하고, 이 모듈의 함수(enrich, poster, profile, requirements, recommend)는 아직 서버에서 부르지 않는다. 그래서 화면에 나오는 AI 결과는 이 모듈이 아니라 서버 digest 결과다. 이 모듈의 정확도는 아래 평가 스크립트로 따로 쟀다.

## 파일

| 파일 | 하는 일 |
|---|---|
| `enrich.py` | `enrich(notice, llm) -> ai` 객체. 스키마 검사, 호출 예외 포함 1회 재시도. 마감일은 달력에 있는 날짜이고, 근거가 원문에 글자 그대로 있고, 근거 속 날짜(범위면 끝)가 같아야 남긴다. 시각도 근거 안에 있어야 한다. 날짜 바로 앞의 항목 이름이 수강·교육·행사 같은 기간이면 마감으로 치지 않는다(`deadline_label.py`). 결과에 서비스 분류 6개(`serviceCategories`, `config/categories.json` 의 `serviceMap`)를 같이 싣는다 |
| `text.py` | `html_to_text`(블록 태그에서만 줄바꿈), `title_deadline`(제목의 "(~10/15)" 표기) |
| `llm_claude.py` | 게이트웨이의 Claude 를 Anthropic 공식 SDK(Claude 형식 `/v1/messages`)로 부른다. `make_claude_llm(task)` 가 `call(prompt, images=None)` 을 돌려준다. 작업별 모델은 `.env` 에서 읽는다 |
| `llm_gateway.py` | `.env` 읽기, 호스트 주소, 모델 목록. `python -m app.ai.llm_gateway` 로 쓸 수 있는 모델 이름을 본다(조회만 한다) |
| `poster.py`, `prompts/poster.md` | 본문이 포스터 이미지뿐인 공지에서 이미지를 받아(최대 3장, 5MB) 글자를 읽는다. 학교 서버가 이미지를 `application/x-download`, 확장자 없는 주소로 줘서 파일 앞부분으로 형식을 알아낸다 |
| `llm_bedrock.py` | AWS Bedrock Converse 호출 함수 (예비) |
| `llm_factory.py` | 평가 스크립트가 gateway / bedrock 을 고르는 곳 |
| `dates.py` | 글 속 날짜 표기를 (연, 월, 일)로 읽는다. 범위는 끝 날짜만 마감으로 본다. 제목 규칙과 마감 근거 검사가 같이 쓴다 |
| `cleaning.py` | LLM 값 정리(목록 밖·중복·빈 값 버림, 학년 숫자화) |
| `mask.py`, `config/mask_patterns.json` | `mask_contacts(text) -> (가린 글, 가린 개수)`. 전화번호·이메일·학번 모양을 가린다. 패턴은 JSON 한 곳에 둔다. Flutter 화면(`frontend/lib/features/profile/pii_masker.dart`)은 이 파일을 읽지 않고 자체 정규식을 쓴다. 두 쪽 결과가 같은지는 확인하지 않았다 |
| `mask_reference.js` | 옛 JS 프론트용 참조 구현(지금 화면은 Flutter 라 쓰지 않는다). 파이썬과 결과가 같은지 입력 39개와 PDF 3건으로 대조했다 |
| `profile.py`, `prompts/profile.md`, `schemas/profile.schema.json` | `extract_profile(masked_text, llm)` (P2). 근거 없는 항목 버림, 30자 미만이면 AI 안 부르고 status="no_text" |
| `prompts/enrich.md` | 프롬프트 |
| `schemas/notice_ai.schema.json` | LLM 출력 JSON 스키마 |
| `config/categories.json`, `config/tags.json` | 분야·태그 목록, 게시판별 기본 분야 |
| `recommend.py`, `config/recommend.json` | 추천 점수와 정렬 (순수 코드) |
| `requirements.py` | `extract_requirements(notice, llm) -> {status, fields, documents}` (PRD 6-1절 P3). 스키마 검사, 1회 재시도, 목록 밖 key 는 그 항목만 버림. 근거가 제목·본문에 글자 그대로(공백 무시) 없거나, 서류 이름·other label 이 근거 안에 없으면 버림 |
| `prompts/requirements.md`, `schemas/requirements.schema.json` | 지원 필요 항목 프롬프트와 출력 스키마. 고정 키 목록은 스키마 `$defs.fieldKey` 한 곳에 둔다 |
| `eval/` | 정답셋(enrich 20건, 지원 준비 8건)과 채점 스크립트. 2026-10-03 실호출 결과 원자료는 `eval/RESULTS.md` |

## 백엔드에서 쓰는 법

```python
from app.ai.enrich import enrich
from app.ai.llm_claude import make_claude_llm
from app.ai.poster import download_images, image_urls, needs_poster, read_poster
from app.ai.text import html_to_text

llm = make_claude_llm(task="classify")                          # 앱 시작 때 한 번 (backend/.env 를 읽는다)
vision = make_claude_llm(task="poster", max_tokens=2000, effort=None)

# view_el = 상세 페이지의 div.view_cont (BeautifulSoup 요소), page_url = 상세 페이지 주소
urls = image_urls(view_el, page_url)                            # html_to_text 가 요소를 고치므로 먼저 뽑는다
notice["body"] = html_to_text(view_el)
if needs_poster(notice):                                        # 본문이 거의 없으면 포스터를 읽는다
    notice["posterText"] = read_poster(download_images(urls), vision)
ai = enrich(notice, llm)          # notice: id, title, postedAt, body (+ source 또는 boardId, posterText)
```

같은 공지는 다시 부르지 않는다. 결과를 DB에 저장해 두고 재사용한다(PRD 11절). 호출이 실패해도 예외를 던지지 않고 `status="failed"` 를 돌려준다(제목에 마감이 있으면 그것만 남긴다).

## 입력 형식 (해서와 맞출 것)

- `notice` = PRD 10절 Notice(`id`, `source`, `title`, `postedAt`) + `body`(본문 텍스트). **`body` 는 PRD 10절에 없다.**
- `boardId` 가 없으면 `id`("kmu-4-12465")에서 게시판 번호를 뽑는다. 게시판 번호로 기본 분야를 정한다.
- 출력 `deadline` 에 `source`("ai", "poster", "title")가 붙는다. "poster" 는 근거가 AI 가 포스터에서 읽은 글에만 있다는 뜻이라 화면에 「포스터에서 읽음, 원문 확인」을 붙이는 게 좋다. **PRD 10절에 없는 필드**라 화면에서 쓸지 정해야 한다.
- `posterText` 도 PRD 10절에 없다. 저장할지는 해서가 정한다(다시 읽으면 크레딧이 또 든다).
- 실행 명령은 `backend` 폴더에서 `app.ai...` 로 import 한다고 가정했다. FastAPI 를 어디서 띄우느냐에 따라 바뀔 수 있다.

## 추천 순서 (`recommend.py`)

`rank(notices, user, today) -> [{id, score, reasons}]`. AI를 부르지 않는 순수 코드다. `notices` 는 `ai` 가 붙은 Notice 목록, `user` 는 Subscription 의 `major`, `year`, `categories`, `tags`, `today` 는 한국 시간 기준 "YYYY-MM-DD" 다.

- 점수는 겹치는 태그 수 × 3, 관심 분야가 하나라도 겹치면 2, 대상 학년에 내 학년이 있으면 2, 대상 전공에 내 전공이 있으면 2를 더한다. 가중치와 이유 문구는 `config/recommend.json` 에 있고, 표본으로 아직 확인하지 않은 초기값이다.
- 마감일이 today 보다 앞이면 뺀다. 마감일이 없으면 남긴다. 시각은 보지 않아서, 오늘 10:00 마감인 글은 그날 하루는 남는다.
- 대상 학년이 적혀 있는데 내 학년이 없으면 빼지 않고 20점을 깎아 맨 아래로 보낸다. 학년은 AI가 원문에서 뽑은 값이라 학기를 학년으로 읽는 식으로 틀릴 수 있고, 빼 버리면 사용자가 그 글을 볼 방법이 없다. 이유에 "1·2학년 대상 (내 학년 아님)"이 붙는다.
- 전공은 글자 포함 관계로만 맞춘다. 일치할 때만 더하고 불일치는 깎지 않는다.
- 같은 점수면 마감 임박 순(같은 날이면 시각이 있는 글 먼저, 마감 없는 글은 뒤), 그다음 게시일 최신 순, 마지막으로 id 순이다. 입력 순서가 달라도 결과가 같다.
- `ai` 가 null 이거나 pending 이면 점수 0으로 남긴다. failed 이면 게시판 기본 분야와 제목에서 뽑은 마감일을 그대로 쓴다.
- `today` 는 서버 시계가 아니라 한국 날짜로 넘긴다. 배포 서버가 UTC 면 한국 시간 0시~9시 사이에 하루 전 날짜가 들어간다.

## 지원 준비 (`requirements.py`, P3)

```python
from app.ai.requirements import extract_requirements
req = extract_requirements(notice, llm)   # notice 에서 title, body 만 쓴다. 프로필 값은 넣지 않는다
```

- 출력은 PRD 6-1절 모양에 `status`(done|failed)를 더했다. 고정 키 필드에는 label 이 없고 other 에만 있다. failed 면 두 목록이 빈 배열이다.
- condition 은 해석이라 원문 대조를 하지 않는다. key 와 근거의 뜻이 맞는지도 코드가 보지 않는다. 정밀도는 평가로 잰다.
- 모든 항목이 버려져도 status 는 done 이다. 화면에서 「공고에 없음」과 「전부 버려짐」을 아직 구분하지 못한다.
- 정답 초안(`eval/gold_requirements.json`)은 본문에 제출 정보·서류가 적힌 8건이다. 필수 47개, optional 14개다. Claude 가 썼고 사람 확인 전이다. 서류 37개 중 28개가 거의 같은 채용 공고 2건에서 나와서 공지별 평균 재현율을 같이 본다.

```bash
python -m app.ai.eval.run_requirements_eval --llm baseline        # LLM 없음, 비용 0, 재현율 0/47
python -m app.ai.eval.run_requirements_eval --llm gateway --yes   # 실제 호출, 크레딧 차감
```

## 포트폴리오 이력 추출 (`profile.py`, P2)

```python
from app.ai.llm_claude import make_claude_llm
from app.ai.profile import extract_profile
llm_profile = make_claude_llm(task="profile", max_tokens=6000)   # 이력은 출력이 길어 공지용과 따로 만든다
result = extract_profile(masked_text, llm_profile)    # masked_text: 브라우저에서 가린 글
```

- 서버는 요청 본문과 결과를 저장하거나 로그에 남기지 않는다(PRD 11절). 결과는 화면으로 돌려주고, 사용자가 검토·수정한 뒤 기기에 저장한다.
- `status` 는 `done`, `failed`, `no_text`(글자 30자 미만, 스캔 PDF로 보고 AI를 부르지 않음) 중 하나다. `no_text` 는 PRD 6-1절에 없는 값이라 프론트와 맞춘다.
- 가리지 못하는 것: 이름, 생년월일, 개인 사이트 주소, 라벨 없이 날짜처럼 읽히는 학번. 잘못 가리는 것: 쉼표 없는 8자리 금액(예: 20231234원). 국민대 학번이 8자리라는 건 추정이다.
- 정답 초안(`eval/portfolios/`)은 Claude 가 가상 인물 포트폴리오를 쓰면서 같이 적었다(confirmed: false). 표본 안 점수다.

## 환경변수 (`backend/.env`, 커밋 금지)

`backend/.env.example` 을 복사해서 만든다.

```
KMU_AI_BASE_URL=https://ai.cs.kookmin.ac.kr
KMU_AI_API_KEY=                        # 게이트웨이 [API 키] 메뉴에서 각자 발급
KMU_AI_MODEL_CLASSIFY=claude-opus-5     # 분류·요약·마감
KMU_AI_MODEL_POSTER=claude-haiku-4-5    # 포스터 글자 읽기
# KMU_AI_MODEL_PROFILE, KMU_AI_MODEL_REQUIREMENTS 를 비우면 CLASSIFY 모델을 쓴다
```

`.env.example` 은 `backend/` 바로 아래라 해서 담당 폴더다. 아직 커밋하지 않았으면 위 내용으로 만든다.

Bedrock 을 쓸 때만: `BEDROCK_MODEL_ID`, `AWS_REGION`, AWS 자격 증명.

## 필요한 패키지

`anthropic`(1.11.0 에서 확인), `jsonschema`, `beautifulsoup4`, `requests`, `pytest`, `boto3`(Bedrock 예비를 쓸 때만)

## 테스트와 평가 (backend 폴더에서)

```bash
python -m pytest app/ai/tests -q                    # LLM 없이 돈다
python -m app.ai.eval.fetch_bodies                  # 정답셋 본문을 eval/.cache 에 받는다 (커밋 안 함)
python -m app.ai.eval.run_eval --llm baseline       # 제목 규칙만, 비용 0
python -m app.ai.eval.run_eval --llm gateway --yes  # 실제 호출, 크레딧 차감
python -m app.ai.eval.run_profile_eval --llm baseline   # 가리기·프롬프트 유출 검사, 비용 0
python -m app.ai.eval.run_poster_eval                   # 포스터 이미지 개수·크기만, 비용 0
python -m app.ai.eval.run_poster_eval --yes --id kmu-11-12374   # 포스터 1건 실제 읽기, 크레딧 차감
```

`--yes` 가 없으면 gateway·bedrock 모드는 호출 수만 알려 주고 멈춘다.

## 알게 된 것 (2026-10-03, 표본 20건)

- **6건(30%)은 본문 글자가 0~50자이고 이미지가 1장 있다**(168KB~1MB). 글만으로는 마감을 못 뽑아서 `poster.py` 로 이미지 글자를 읽어 프롬프트에 붙인다.
- **첫 실호출 2건 (2026-10-03).** 글 공지 1건(kmu-4-12465)은 Opus 1회, 입력 1,617·출력 307 토큰, 마감 2026-10-16 17:00 과 분야 학사가 정답 초안과 같았다. 포스터 공지 1건(kmu-11-12374)은 Haiku 가 "09.01 - 09.22" 를 읽었고 Opus 가 마감 2026-09-22 를 냈다. 다만 Opus 가 댄 근거는 포스터가 아니라 제목의 "(~9/22)" 였다. 이때 "09.01 - 09.22" 를 2009-01-09 로 읽는 버그가 있어서 고쳤고(dates.py, 구분자가 같을 때만 연·월·일로 읽음), 근거가 포스터에만 있을 때 source="poster" 로 남는지는 가짜 LLM 테스트로만 확인했다. 게이트웨이 사용액(`/v1/dashboard/billing/usage` 의 total_usage)은 0 → 1.576 → 2.6462 였다. 단위를 센트로 보면 두 건 합계 $0.0265 이고, 공식 가격(Opus 5 입력 $5·출력 $25, Haiku 4.5 $1·$5, 100만 토큰당)으로 토큰 수를 계산한 값과 같다. 단위가 센트라는 건 이 대조로 추정한 것이다. 2건이라 정확도 숫자로는 못 쓴다.
- **전체 실호출 (2026-10-03, dates.py 수정 뒤).**
  - 글 경로 20건(`run_eval --llm gateway --yes`): 정답 초안 기준으로 마감일 20/20, 마감 시각 10/10, failed 0 이 나왔다. 그런데 정답 초안은 글만 보고 써서 포스터에만 마감이 있는 2건(kmu-7-12349, kmu-7-12339)을 「마감 없음」으로 두었다. 그래서 20/20 은 부풀려진 숫자다. 본문 공지 14건만 보면 AI 14/14, 기준선 4/14 다. 포스터 공지까지 합쳐 실제 마감이 있는 16건은 AI 16/16(포스터 경로 포함), 기준선 4/16 이다. 표본 안 점수다.
  - 포스터 6건(`run_poster_eval --yes`): Claude 가 이미지 6장을 직접 열어 대조했다(사람 확인 아님). 맞음 5, 틀림 1. 포스터에서만 나온 마감이 3건이다(9.23 17:00, 10.8, 9.22). 틀린 1건(kmu-6-12331)은 「신청 기간: 선착순 모집 마감 / 수강 기간: 9.21~12.20」에서 수강 기간 끝을 마감으로 잡았다. 날짜가 원문에 실제로 있어서 근거 검사를 통과한다. 근거 앞의 항목 이름을 코드가 보지 않아서였다. 그 뒤 `deadline_label.py` 를 더해, 날짜 바로 앞의 가장 가까운 항목 이름이 수강·교육·행사 같은 기간이면 마감으로 치지 않게 했다(테스트 `test_deadline_label.py`, 오늘 Opus 가 맞힌 마감 14건은 이 규칙에 하나도 안 걸림). 실호출로 다시 재지는 않았다.
  - 비용: 사용액 2.6462 → 44.2228(센트로 추정) 이라 $0.416. 글 공지는 건당 약 $0.015(Opus), 포스터 공지는 건당 약 $0.018(Haiku 판독 $0.005 + Opus $0.014)이다.
- **본문을 줄 단위로 뽑으면 날짜가 쪼개진다.** 인라인 태그마다 줄을 바꾸면 "2026.10.13.(화) 10:00"이 여러 줄로 갈라진다. `text.html_to_text`를 쓴다(수집기도 같은 함수를 쓰는 게 좋다).
- **기준선(LLM 없음):** 마감일 10/20, 마감 시각 0/10. 맞은 10건 중 6건은 정답과 예측이 둘 다 null 이라 맞은 것이다. 본문에만 마감이 있는 10건을 LLM이 얼마나 맞히는지가 AI의 몫이다.
- **분야 정확도는 이 표본에서 변별력이 없다.** 게시판 기본값만으로 20/20이 나온다.
- **정답셋의 한계.** 정답셋은 Claude가 원문을 읽고 적은 **초안**이다(`confirmed: false` = 사람이 아직 확인 안 함). PRD 11절은 사람이 먼저 적으라고 했는데 아직 그렇게 하지 않았다. 게다가 프롬프트를 이 20건을 읽은 뒤에 썼다(행사·계약 기간 제외, 선착순·모집완료는 null 규칙이 이 표본에서 나왔다). 그래서 이 20건 점수는 **표본 안 점수**다. 발표 숫자는 사람이 정답을 확인하고, 프롬프트를 고정한 뒤, 새로 모은 공지로 따로 낸다.
- 표본 규칙: 게시판 4·6·7·9·11 에서 고정 공지를 빼고 최신 글 4건씩(2026-10-03 수집).
- **일부러 남겨 둔 동작 (verifier 지적 중).**
  - LLM 이 마감을 null 로 내도 제목에 마감 표기가 있으면 제목 날짜를 쓴다. 본문이 이미지인 공지(30%)는 제목이 유일한 출처라서다. 대신 제목 규칙이 오탐하면 맞는 null 을 덮어쓴다. 오탐을 줄이려고 제목 규칙은 괄호 끝·까지·마감이 붙은 표기만 잡고, 범위·배수·퍼센트는 안 잡는다(반례 28개 중 27개 통과).
  - 제목에 연도가 적힌 표기는 그 연도를 따른다. 게시 2026-12-20 의 "(~26.1.5)" 는 2026-01-05 로 읽혀 마감 지난 글이 된다. 연도를 적어 둔 표기를 고쳐 읽지 않는 쪽을 골랐다.
  - 정답 근거가 원문에 글자 그대로 있는지는 본문 캐시(`eval/.cache`)가 있을 때만 테스트가 검사한다. 캐시는 커밋하지 않으므로 처음 받은 사람은 `fetch_bodies` 를 먼저 돌린다.
