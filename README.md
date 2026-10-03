# 크노: 흩어진 국민대 공지를 AI가 대신 읽고, 내 분야만 모아 준다

국민대 K-Builder 2026 팀 11. 주제는 「귀찮음 주식회사: 대학 생활의 귀찮은 순간을 돈 받고 해결하는 AI 서비스」다.

| 축 | 한 줄 |
|---|---|
| 누구의 귀찮음 (WHO) | 본부 공지, 단과대 공지, 공모전·채용 소식을 여러 사이트에서 찾아다니는 국민대 재학생 |
| AI가 대신하는 일 | 새 공지를 읽고 분야·요약·마감일을 뽑는다. 본문이 포스터 이미지뿐인 공지는 이미지 속 글자부터 읽는다 |
| 누가 돈을 내나 (MONEY) | 학생은 무료다. 학생에게 닿고 싶은 공모전·채용 주최 측과 학교가 낸다 (가설, [docs/PRD.md](docs/PRD.md) 4절) |

- 배포: 〔해서 도메인, 확정되면 적는다〕
- 발표자료: 〔제출본 경로〕

## 왜 필요한가

- 본부 공지만 해도 학사·행정·특강·장학·공모·채용 등 10개 넘는 분류로 나뉜다. 단과대 17곳은 홈페이지가 따로 있다.
- 학교 공식 앱은 2018-01-17 이후 업데이트가 없고 단과대 공지가 없다.
- 실제 공지 20건을 받아 보니 **6건(30%)은 본문이 포스터 이미지 1장뿐**이었다. 글자가 없으니 검색에도 키워드 알림에도 걸리지 않는다.

## 어떻게 동작하나

```
학교 게시판 ─▶ 수집(코드) ─▶ 글자 확보 ─▶ AI 해석 ─▶ 검사(코드) ─▶ 분야별 화면
                              │            │            │
                    포스터면 AI가 이미지   분야·요약·   근거 문장이 원문에
                    속 글자를 읽는다      마감·대상    그대로 있어야 마감을 띄운다
```

판단은 코드가 하고, AI는 해석만 한다. AI 출력은 JSON 스키마로 검사하고, 틀리면 한 번 다시 부르고, 그래도 틀리면 `failed`로 둔다. 마감일은 AI가 댄 근거 문장이 원문에 글자 그대로 있고 그 안의 날짜가 같을 때만 띄운다.

## 구현 상태

「다음 단계」는 이번 대회에서 만들지 않은 것이다. 문서에는 있어도 코드에는 없다.

| 기능 | 상태 | 코드 |
|---|---|---|
| 분야별 대시보드, 다중 선택, 검색, 출처 필터 | 구현 | `frontend/lib/features/feed/` |
| 공지 상세: 요약, 마감과 근거, 대상, 원문 링크 | 구현 | `frontend/lib/features/notice/` |
| 공지 수집 (본부 게시판, SW사업단, 소프트웨어융합대학 RSS)과 API 서버 | 구현, 백엔드 브랜치 | `origin/hs/feature-notice-digest` `backend/app/collectors/`, `features/` 〔main 머지 확인 필요〕 |
| AI 분류·요약·마감 추출 (근거 검사, 재시도) | 구현 | 서버 `backend/app/ai/digest.py` 〔머지 확인 필요〕, AI 모듈 [`backend/app/ai/enrich.py`](backend/app/ai/enrich.py) |
| 포스터 이미지 글자 읽기 | AI 모듈 구현, 서버 연결은 패치 대기 | [`backend/app/ai/poster.py`](backend/app/ai/poster.py) |
| 지원 준비: 필요한 항목·서류, 내 값 복사 | 화면 구현, 서버 API 없음 (데모 데이터) | `frontend/lib/features/apply_helper/`, [`backend/app/ai/requirements.py`](backend/app/ai/requirements.py) |
| 가입·동의·온보딩 | 화면 구현, 서버 API 없음 (기기 안에서만) | `frontend/lib/features/auth/`, `onboarding/` |
| 포트폴리오 PDF: 브라우저에서 글자 추출, 연락처·학번 가리기 | 구현 | `frontend/lib/features/profile/pdf_text_extractor.dart`, `pii_masker.dart` |
| 포트폴리오 AI 이력 추출 | AI 모듈 구현, 화면은 예시 결과 | [`backend/app/ai/profile.py`](backend/app/ai/profile.py) |
| 맞춤 추천 | 부분 구현. 서버 `POST /api/briefing`이 학과·학년·관심 분야에 맞는 글을 고르고, 태그 점수 규칙은 AI 모듈에 있다. 피드의 추천 순은 아직 최신순이다 | 서버 `backend/app/features/briefing/`, [`backend/app/ai/recommend.py`](backend/app/ai/recommend.py) |
| 온보딩에서 고른 분야로 피드 거르기 | 다음 단계. 지금은 대시보드에서 분야를 직접 고른다 | |
| 알림 발송 (웹푸시·봇) | 다음 단계 | 없음 |
| 링커리어 등 외부 플랫폼 | 다음 단계. 링커리어 약관 제39조 2호가 자동화 수단 접근을 금지한다 | 없음 |

## AI 정확도와 비용 (2026-10-03 실측)

본부 게시판 4·6·7·9·11에서 최신 4건씩, 실제 공지 20건으로 쟀다. 모델은 학교 AI 게이트웨이의 `claude-opus-5`(분류·요약·마감)와 `claude-haiku-4-5`(포스터 글자 읽기)다.

| 항목 | 제목 규칙만 (AI 없음) | AI |
|---|---|---|
| 실제 마감이 있는 16건의 마감일 | 4/16 | **16/16** |
| 그중 마감이 포스터 이미지에만 있는 3건 | 1/3 | **3/3** |
| 마감 시각 10건 | 0/10 | **10/10** |
| 마감이 없는 공지에 마감을 만들어 낸 것 | 0 | 1 |

- 틀린 1건: 포스터에 「신청 기간: 선착순 마감 / 수강 기간: 9.21~12.20」이 있었는데, 수강 기간 끝을 마감으로 잡았다. 날짜가 원문에 실제로 있어서 근거 검사도 통과했다. 근거 검사는 「그 날짜가 원문에 있나」만 보고 「그 날짜가 신청 마감인가」는 보지 못한다.
- **표본 안 점수다.** 정답은 Claude가 원문과 포스터 이미지를 보고 쓴 초안이고 사람이 확인하지 않았다. 프롬프트도 이 20건을 읽은 뒤에 썼다.
- 비용: 글 공지 1건 약 $0.015, 포스터 공지 1건 약 $0.018 (게이트웨이 사용 기록 기준). 같은 공지는 한 번만 처리하므로 원가는 학생 수가 아니라 공지 수에 비례한다.
- 자세한 기록과 재현 명령은 [`backend/app/ai/README.md`](backend/app/ai/README.md)에 있다.

## 실행

**화면 (Flutter 웹, 데모 데이터)**: [`frontend/README.md`](frontend/README.md)

```bash
cd frontend
flutter pub get
flutter run -d chrome --web-port 4173     # http://localhost:4173/?demo=1
```

**AI 모듈 테스트 (LLM 호출 없음, 비용 0)**

```bash
cd backend
pip install anthropic jsonschema beautifulsoup4 requests pytest
python -m pytest app/ai/tests -q
```

실제 AI 호출은 `backend/.env`에 학교 게이트웨이 키가 있어야 하고 크레딧이 든다. 변수 이름은 [`backend/app/ai/README.md`](backend/app/ai/README.md) 「환경변수」에 있다. 키는 저장소에 올리지 않는다.

## 개인정보 원칙

- 가입은 닉네임과 비밀번호만 받는다.
- 이름·연락처·학번 같은 지원용 정보는 기기에만 저장하고 서버와 AI로 보내지 않는다.
- 포트폴리오 PDF는 선택 동의 뒤에만 분석한다. 브라우저에서 전화번호·이메일·학번을 가린 다음 보낸다. 이름과 생년월일은 자동으로 가리지 못해서, 올리기 전에 경고한다.
- 수집한 공지의 작성자 실명은 저장하지 않는다.

## 저장소 구조

```
frontend/         Flutter 웹 (feed, notice, apply_helper, auth, onboarding, profile)
backend/app/ai/   AI 모듈: enrich, poster, recommend, profile, requirements, mask, eval, tests
docs/             PRD, 개발 계획, 동의 문구, 현장 설문
mock/             화면 개발용 예시 데이터
AGENTS.md         팀 작업 규칙 (브랜치, 키·개인정보, 코드 길이)
```

## 팀

| 역할 | 담당 |
|---|---|
| 백엔드 (수집, API) | 해서 |
| 프론트 A (가입, 동의, 온보딩, 이력) | 택준 |
| 프론트 B (대시보드, 상세, 지원 준비) | 민섭 |
| AI (분석, 포스터, 추천 규칙), 문서, 발표 | 현찬 |
