# backend — 국민대 공지 한 페이지 요약 API

담당: 해서. Python 3.12 + FastAPI + SQLite.
국민대 소프트웨어·AI·컴공 계열 학생이 보는 공지를 모아서, 길고 난잡한 공지(본문 + 첨부 PDF·HWP 등)를 **글 하나 = 한 화면**으로 요약한다.

## 실행

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8091 --reload
```

- API 문서(Swagger): http://localhost:8091/docs
- 처음엔 DB 가 비어 있다. `POST /api/admin/poll-now` 로 수집을 한 번 돌린다 (출처마다 새 글 8건, 몇 분 걸림)
- AI 요약은 지금 이 개발 서버의 `claude` CLI(구독)를 부른다. 다른 PC에서 돌리면 요약은 `failed` 가 된다 → 프론트는 `mock/live-notices.json`(실제 수집 + AI 결과 20건) 이나 개발 서버 API 를 쓴다. `mock/notices.json` 은 프론트 더미 화면(`?demo=1`)용 가상 공고다

| 환경변수 | 기본값 | 뜻 |
|---|---|---|
| `POLL_INTERVAL_MIN` | 10 | 주기 수집 간격(분). 0 이면 끔 |
| `POLL_ON_STARTUP` | 0 | 1 이면 서버 켜자마자 수집 |
| `NEW_PER_SOURCE` | 8 | 한 번에 출처마다 새로 처리할 최대 글 수 |
| `KMU_AI_BASE_URL` | https://ai.cs.kookmin.ac.kr | 학교 AI 게이트웨이 (추천 적합도·지원 준비) |
| `KMU_AI_API_KEY` | (없음) | 게이트웨이 키. `backend/.env` 에만 두고 레포에 올리지 않는다 |
| `KMU_AI_MODEL` | claude-haiku-4-5 | `claude-opus-5` 도 쓸 수 있다 |
| `LLM_COMMAND` | claude | 요약에 쓰는 CLI |
| `LLM_MODEL` | sonnet | 요약용 (개발 서버 Claude 구독 CLI) |
| `LLM_TIMEOUT_SEC` | 180 | 요약 한 번의 제한 시간(초) |
| `LLM_CONCURRENCY` | 3 | 동시에 돌릴 AI 요약 수 |
| `ADMIN_TOKEN` | (없음) | `/api/admin/poll-now`·`/redigest` 열쇠. 비어 있으면 그 두 개는 503 |
| `CORS_ORIGINS` | * | 쉼표로 구분 (공백은 무시한다) |
| `DB_PATH` | backend/data/app.db | |

## 출처 (6개)

| ID | 이름 | 방식 |
|---|---|---|
| `kmu-academic` | 국민대 본부 학사공지 | HTML. 첨부는 portal 파일 API |
| `sw-notice` | SW중심대학사업단 공지사항 | HTML 표 |
| `cs-notice` / `cs-scholarship` / `cs-jobs` / `cs-event` | 소프트웨어융합대학 학사·장학·취업·특강행사 | RSS + 상세 HTML |

## 흐름

```
[목록에서 새 글] → [상세 본문 + 첨부 다운로드 → 글자 추출(pdf·hwp·hwpx·docx·pptx)]
 → [학번 가리기] → [AI: 한 페이지 요약 (JSON 스키마 고정)] → [코드: 근거가 원문에 있는지 검사, 없으면 버림] → DB
```

## API 계약

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/categories` | 분류 6개 (고정): 학사·생활, 졸업, 장학, 취업, 행사·대외활동, 기타 |
| GET | `/api/sources` | 출처 목록 |
| GET | `/api/notices?category=&source=&q=&actionRequired=&cursor=` | 목록, 최신순 20건씩. `nextCursor` 를 그대로 다시 보내면 다음 쪽 |
| GET | `/api/feed?sort=recommend\|deadline` | 피드 화면용 전체 목록 (페이지 없음). recommend 는 지금 최신순 |
| GET | `/api/notices/{id}` | **한 페이지 요약** (목록 항목과 같은 형식) |
| POST | `/api/briefing` | **나의 상황**에서 반드시 볼 글 |
| POST | `/api/recommend` | 공지마다 **될 가능성(0~100)** 과 **추천 근거 한 줄**. 상황은 저장하지 않는다 |
| POST | `/api/admin/poll-now` | 지금 수집 (백그라운드, 바로 응답) |
| POST | `/api/admin/redigest` | 저장된 글 전부 다시 요약 (프롬프트를 바꿨을 때) |
| GET | `/api/admin/poll-status` | 수집 진행 상황 |

### 공지 (Notice)

```json
{
  "id": "cs-notice-2872",
  "source": { "id": "cs-notice", "name": "SW 학사공지", "group": "소프트웨어융합대학" },
  "originalTitle": "2026학년도 졸업앨범 촬영 안내",
  "url": "https://cs.kookmin.ac.kr/news/notice/2872",
  "postedAt": "2026-10-01",
  "department": null,
  "pinned": false,
  "fetchedAt": "2026-10-03T13:00:00+09:00",
  "categories": ["졸업"],
  "attachments": [
    { "name": "신청서.hwp", "url": "…", "type": "hwp", "analyzed": true, "note": null }
  ],
  "digest": {
    "status": "done",
    "title": "졸업앨범 촬영 10/12, 예약 10/11 14:00까지",
    "summary": "2~3문장 요약",
    "keyPoints": [{ "label": "장소", "value": "종합복지관 222호", "evidence": "촬영장소: 종합복지관 222호" }],
    "requirements": [{ "text": "맥스튜디오 홈페이지에서 예약", "evidence": "…", "origin": "본문" }],
    "deadline": { "date": "2026-10-11", "time": "14:00", "evidence": "~ 2026년 10월 11일(일) 14:00 까지" },
    "lastDate": { "date": "2026-10-12", "evidence": "촬영일시: 2026년 10월 12일(월)" },
    "actionRequired": true,
    "audience": { "years": [], "majors": [], "statuses": ["졸업예정자"], "text": "2027년 2월 졸업예정자" },
    "etc": ["문의: …"],
    "error": null
  }
}
```

| 화면 칸 | 필드 |
|---|---|
| 요약 제목 / 원 제목 | `digest.title` / `originalTitle` |
| 내용 요약 | `digest.summary` |
| 주요 내역 | `digest.keyPoints[]` (label: value) |
| 필수 사항 | `digest.requirements[]` (`origin` 이 "첨부:파일명"이면 첨부에서 나온 것) |
| 기타 | `digest.etc[]` |
| 직접 링크 | `url` |
| 마감 배지 | `digest.deadline` (null 이면 "원문 확인") |
| (내부용) 공지 유효 기간 | `digest.lastDate`: 행사·시험 마지막 날까지 포함한 마지막 관련 날짜. 브리핑에서 지난 글을 뺄 때 쓴다 |

- `digest.status`: `pending`(아직 요약 전) / `done` / `failed`(요약 실패 → 원 제목과 링크만 보여 준다)
- 모르는 값은 `null` 또는 빈 배열. `evidence` 는 원문에 실제로 있는 구절이다 (코드가 검사, 없으면 항목을 버림)
- 첨부: `analyzed=false` 이면 `note` 에 이유 (xls 형식, 다운로드 실패, 스캔 이미지 등) → "원문에서 확인"
- `id` 는 `{출처ID}-{글번호}`

### 나의 상황 (Briefing)

```
POST /api/briefing
{ "major": "소프트웨어학부", "year": 4, "status": "재학", "graduating": true, "interests": ["취업", "장학"] }
```

```json
{ "generatedAt": "…", "items": [ { "notice": { …Notice… }, "reasons": ["모두 확인해야 하는 「졸업」 공지", "졸업예정자 대상", "마감 D-8"], "daysLeft": 8 } ] }
```

- 상황 정보는 **저장하지 않는다.** 이름·학번·연락처는 받지 않는다
- 고르는 규칙은 코드다 (`app/features/briefing/service.py` 맨 위 설명): 요약 완료 · 마감 전(마감이 없으면 lastDate 전, 둘 다 모르면 최근 30일) · 할 일 있음 · 대상 조건(학년·학과·신분)이 내 상황과 맞음 · 관심 분류이거나 학사·생활/졸업
- 학과: 「소프트웨어융합대학」 대상 글은 소프트웨어학부·인공지능학부와 맞는 것으로 본다 (`MAJOR_GROUPS`)
- 출처만 다른 같은 공지(본부 학사공지 ↔ 소융대 학사공지)는 하나로 합치고 이유에 「…에도 같은 공지」를 붙인다
- 정렬: 마감 임박 순

## 폴더

```
app/
├─ main.py            서버 시작·라우터 등록
├─ core/              설정, 공용 스키마(API 계약), HTTP, 글자 처리, 정렬·페이지네이션
├─ collectors/        출처마다 파일 하나 (kmu_board, sw_bulletin, cs_rss)
├─ attachments/       첨부 → 글자 (pdf, hwp/hwpx, docx, pptx)
├─ ai/                LLM 호출(llm.py), 요약(digest.py), 근거 검사(verify.py), prompts/
├─ jobs/              수집 한 바퀴(poll.py), 재료 모으기(gather.py), 주기 실행(scheduler.py)
├─ db/                SQLite 저장소
└─ features/          notices, briefing, admin (router·service)
```

### 추천 적합도 (POST /api/recommend)

```json
{ "situation": { "major": "소프트웨어학부", "year": 3, "status": "재학", "interests": ["장학"] },
  "tags": ["AI·데이터"], "noticeIds": ["kmu-academic-12465"] }
```

```json
{ "model": "claude-haiku-4-5",
  "items": [{ "noticeId": "kmu-academic-12465", "chance": 5, "reason": "3학년은 7차 학기가 아니므로 자격 미충족" }] }
```

- `chance` 는 **지원·신청했을 때 될 가능성**(0~100). 화면은 제목 위에 한 줄로 보여 준다
- 같은 상황·같은 글이면 다시 묻지 않는다 (DB 캐시). 상황은 해시로만 남기고 저장하지 않는다
- 어떤 글을 어떤 순서로 보여 줄지는 화면이 정한다. AI 는 해석만 한다 (지침서 7절)
