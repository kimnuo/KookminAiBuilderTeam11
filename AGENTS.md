<!-- NOTE FOR AI AGENTS: This file is UTF-8 encoded Korean text. If it looks garbled, re-read it as UTF-8 (PowerShell: Get-Content -Encoding UTF8). Read the whole file before writing code and follow every rule. If this file and docs/PRD.md disagree, stop and ask a human. -->

# 팀 11 공용 지침서

| 항목 | 내용 |
|---|---|
| 상태 | v0.1 (2026-10-03, K-Builder 현장) |
| 대상 | 팀원 4명과 각자 쓰는 AI 코딩 도구 |
| 같이 볼 문서 | `docs/PRD.md`는 무엇을 만드는지, 이 문서는 어떻게 만드는지 정한다 |

> **AI 도구에게:** 작업 전에 이 문서를 끝까지 읽고 따른다. 이 문서와 PRD가 다르면 멈추고 사람에게 묻는다. 이 파일은 저장소 맨 위의 `AGENTS.md`이고, `CLAUDE.md`가 이 파일을 불러온다.

---

## 1. 처음 시작할 때

```bash
git clone https://github.com/kimnuo/KookminAiBuilderTeam11.git
cd KookminAiBuilderTeam11
git config core.ignorecase false   # Windows: 파일명 대소문자 변경을 git이 알아채게 한다
git switch main
git pull origin main
```

- 이미 클론했다면 `git switch main` 후 `git pull origin main`부터 한다.
- 백엔드가 `.env.example`을 올리면 복사해서 `.env`를 만든다. 키 값은 팀원에게 DM으로 받는다.

## 2. Git 규칙

### 브랜치

- main에서 직접 작업하지 않는다. 기능마다 브랜치를 만든다.
- 이름은 `feat/<영역>-<기능>` 또는 `fix/<영역>-<내용>`으로 짓는다. 영역은 `fe`, `be`, `ai`, `docs` 중 하나다.
  - 예: `feat/fe-feed`, `feat/be-collector`, `feat/ai-enrich`, `fix/fe-login-redirect`
- 브랜치 하나에는 기능 하나만 담는다. 2~3시간 안에 머지할 수 있는 크기로 자르고 자주 머지한다.

### 작업 시작 전에 매번

```bash
git switch main
git pull origin main
git switch -c feat/fe-feed     # 새 기능이면 새 브랜치

# 이미 있는 내 브랜치에서 이어서 하면
git switch feat/fe-feed
git merge main                 # 최신 main을 내 브랜치에 합친다
```

### 커밋

- `git add -A`, `git add .`을 쓰지 않는다. 파일을 지정해서 올리고, 커밋 전에 `git status`로 무엇이 올라가는지 본다.
- 메시지는 `[영역] 한 일`로 짧게 쓴다. 예: `[FE] 피드 마감순 정렬`, `[BE] 학사공지 수집기`, `[AI] 마감일 추출 프롬프트`, `[DOCS] API 계약 수정`
- 올리면 안 되는 것: `.env`와 API 키, `node_modules/`, `.venv/`, 빌드 결과물, 실제 개인정보, 영상·PSD 같은 큰 파일

### main으로 머지

- GitHub에서 PR을 만들어 머지한다.
- 머지 전에 내 브랜치에 최신 main을 합치고(`git merge main`), 로컬에서 실행과 빌드가 되는지 확인한다.
- 머지 담당은 팀이 정한다. 각자 머지한다면 머지한 뒤 팀 채팅에 알린다.
- **PR 위에 PR을 쌓지 않는다.** 앞 PR이 머지되기 전에 그 브랜치에서 새 브랜치를 만들지 않는다. 기다릴 수 없으면 같은 PR에 커밋으로 얹는다.
- 머지한 뒤에는 GitHub에서 그 브랜치를 지운다(Delete branch). 그리고 main에 내 파일이 실제로 들어갔는지 확인한다.
- main에 force push 하지 않는다. `git reset --hard`나 `git push --force`는 내 브랜치에서도 팀에 먼저 말하고 한다.
- 무료 private 레포에서는 main 보호 규칙을 걸 수 없을 수 있다(**추정**). 그래서 위 규칙은 사람끼리 지킨다.

### 충돌

- 충돌이 나면 그 파일 담당자와 같이 푼다. 남의 코드를 지워서 충돌을 없애지 않는다.
- 공용 파일(API 계약, 공용 타입, 설정)은 바꾸기 전에 팀 채팅에 먼저 말한다.
- 충돌 없이 자동으로 합쳐진 파일도, 두 사람이 같은 목록이나 설정을 건드렸다면 눈으로 한 번 본다.

## 3. 폴더 구조 (기능별)

스택이 정해지면 이름만 맞춘다. 원칙은 **기능 단위로 폴더를 나누고, 여러 기능이 같이 쓰는 것만 공용 폴더에 둔다**는 것이다.

```
/
├─ AGENTS.md               이 문서
├─ CLAUDE.md               AGENTS.md를 불러온다
├─ docs/                   PRD, API 계약, 회의 메모
├─ mock/                   프론트용 가짜 데이터 (notices.json 등)
├─ frontend/
│  └─ src/
│     ├─ app/              라우팅, 진입점, 전역 설정만
│     ├─ features/
│     │  ├─ auth/          가입, 로그인, 동의
│     │  ├─ onboarding/    학과, 학년, 관심 분야
│     │  ├─ profile/       내 이력, 내 지원 정보 (기기 저장)
│     │  ├─ feed/          피드, 추천 순과 마감 순
│     │  ├─ notice/        공지 상세
│     │  └─ apply-helper/  지원 준비 패널
│     └─ shared/
│        ├─ ui/            버튼, 카드 같은 공용 컴포넌트
│        ├─ api/           서버 호출 함수 (fetch는 여기서만)
│        └─ lib/           날짜 포맷 같은 순수 함수
└─ backend/
   └─ app/
      ├─ main              서버 시작과 라우터 등록만
      ├─ features/
      │  ├─ notices/       공지 조회 API
      │  ├─ feed/          피드와 추천 순서
      │  ├─ auth/          가입, 로그인, 동의, 탈퇴
      │  ├─ subscriptions/ 구독 설정
      │  ├─ profile_analyze/  PDF 분석 중계 (저장·로그 금지)
      │  └─ push/          알림 발송
      ├─ collectors/       출처마다 파일 하나 (kmu_board, cs_rss)
      ├─ ai/               enrich, extract_profile, extract_requirements, prompts/
      ├─ db/               모델, 저장소
      └─ core/             설정, 비밀번호 해시, 공용 에러
```

- 기능 폴더 안에서도 역할별로 파일을 나눈다.
  - 프론트: 화면(`FeedPage`), 부품(`FeedCard`), 상태(`useFeed`), 서버 호출(`feed.api`)
  - 백엔드: 라우터(`router`), 로직(`service`), 입출력 형식(`schema`)
- 기능 폴더끼리 서로 import하지 않는다. 같이 쓸 것이 생기면 프론트는 `shared/`, 백엔드는 `core/`로 옮긴다.
### 폴더 담당 (2026-10-03 확정)

| 폴더 | 담당 |
|---|---|
| `backend/` (`ai/` 제외), `mock/` | 해서 (백엔드) |
| `frontend/src/features/auth/`, `onboarding/`, `profile/` | 택준 (프론트 A) |
| `frontend/src/features/feed/`, `notice/`, `apply-helper/` | 민섭 (프론트 B) |
| `backend/app/ai/`, `docs/` | 현찬 |
| `frontend/src/shared/`, `frontend/src/app/` | 프론트 둘이 같이. 고치기 전에 서로 말한다 |

- 자세한 일은 PRD 12절 표를 따른다. 남의 폴더를 고칠 때는 담당자에게 먼저 말한다.

## 4. 코드 길이

| 기준 | 상한 | 넘으면 |
|---|---|---|
| 파일 | 200줄 | 역할별로 파일을 나눈다 |
| 함수 | 40줄 | 작은 함수로 나눈다 |
| 컴포넌트 | 파일 하나에 하나 | 작은 부품은 같은 기능 폴더에 새 파일로 |
| 중첩 | 3단계 | 조건을 먼저 걸러 리턴하거나 함수로 뺀다 |

- 새 기능은 기존 파일을 늘리지 않고, 해당 기능 폴더에 새 파일로 만든다.
- 파일 하나는 역할 하나만 맡는다. 파일 이름만 보고 무엇을 하는지 알 수 있게 짓는다.
- 안 쓰는 코드와 주석 처리한 코드 덩어리는 커밋하지 않는다.
- 너무 잘게 쪼개지도 않는다. 한 번만 쓰는 코드를 미리 공용으로 만들지 않는다.
- 상수와 설정값(폴링 간격, 태그 목록, API 주소)은 코드에 박지 않고 설정 파일 한 곳에 둔다.

## 5. 이름 규칙

- 파일과 폴더 이름은 영어로 짓는다. 한글 파일명은 쓰지 않는다(Windows와 배포 서버 사이에서 깨진다).
- 대소문자를 정확히 맞춘다. Windows는 대소문자를 구분하지 않지만 배포 서버(Linux)는 구분해서, 로컬에서는 되고 배포에서만 깨진다. 파일 이름을 바꿀 때는 에디터로 바꾸지 말고 `git mv`를 쓴다.
- 코드 이름은 스택의 관례를 따른다. 포매터(예: Prettier, Black)를 하나 정해서 저장할 때 자동으로 정리되게 한다.

## 6. 프론트와 백엔드 사이 약속

- API 형식의 기준은 `docs/PRD.md` 10절이다. 바꾸려면 문서를 먼저 고치고, 팀 채팅에 알린 뒤 코드를 바꾼다.
- 백엔드가 준비되기 전에는 프론트가 `mock/` 데이터로 작업한다. mock은 실제 API와 같은 형식이어야 한다.
- 날짜와 시각은 ISO 8601 형식에 한국 시간(+09:00)으로 쓴다. 예: `2026-10-03T12:00:00+09:00`
- 모르는 값은 `null`로 둔다. 빈 문자열이나 그럴듯한 값으로 채우지 않는다.

## 7. AI 기능 코드

- 판단, 필터, 정렬은 코드로 하고, 해석(분류, 요약, 추출)만 AI에게 맡긴다. 같은 입력이면 같은 결과가 나와야 한다.
- AI 출력은 정해진 JSON 형식으로 받아 검사한다. 형식이 틀리면 1회 다시 부르고, 그래도 틀리면 `failed`로 둔다.
- 근거 문장이 없는 값(마감일, 이력 항목, 필요 서류)은 버린다.
- 같은 입력으로 AI를 다시 부르지 않는다(결과 캐시). API 키와 크레딧은 정해진 한도 안에서만 쓴다.
- 프롬프트는 `backend/app/ai/prompts/`에 파일로 둔다. 코드 중간에 긴 문자열로 박지 않는다.

## 8. 비밀정보와 개인정보

- API 키, 토큰, 비밀번호는 `.env`에만 둔다. 코드, 커밋, 스크린샷, 단체 채팅방에 그대로 올리지 않는다.
- 키를 실수로 커밋했으면 바로 팀에 알리고 그 키를 폐기한 뒤 새로 발급한다. 커밋만 지워서는 안 된다. 이미 새어 나간 것으로 본다.
- 테스트와 데모에는 지어낸 가상 인물만 쓴다. 팀원이나 지인의 실제 이름, 연락처, 학번을 넣지 않는다.
- 수집한 공지의 작성자 실명은 저장하지 않는다.
- 비밀번호는 비밀번호 전용 해시(bcrypt, argon2 등)로만 저장한다.
- 이름, 연락처, 학번은 서버와 AI로 보내지 않는다. 이건 PRD 6-1절의 제안이라, 팀이 바꾸면 이 줄도 같이 고친다.
- 로그에 요청 본문을 통째로 찍지 않는다.

## 9. AI 코딩 도구를 쓸 때

- 일을 시키기 전에 이 문서를 읽게 한다. `AGENTS.md`를 읽는 도구(Codex 등)와 `CLAUDE.md`를 읽는 Claude Code는 자동으로 읽는다. 다른 도구는 첫 메시지에 이 파일을 넣는다.
- AI가 만든 코드는 커밋 전에 직접 한 번 돌려 본다. 만들어졌다고 돌아가는 것은 아니다.
- AI에게 git 명령(브랜치 전환, `add -A`, force push)을 맡기지 않는다. 커밋과 푸시는 사람이 한다.
- 한 사람이 AI 세션을 여러 개 동시에 돌리면 세션마다 `git worktree`로 폴더를 나눈다. 같은 폴더에서 두 세션이 git을 건드리면 서로의 작업을 덮는다.
- 전체 빌드에서 내 담당 폴더 밖의 오류가 나면, 남이 아직 만드는 중인 코드일 수 있다. 내 블로커로 판단하기 전에 확인한다.
- 큰 리팩터링, 폴더 구조 변경, 라이브러리 교체는 팀에 먼저 말한다.

## 10. Windows에서 작업할 때

- 한글이 들어간 경로에서 Python을 돌리면 `PYTHONUTF8=1`을 켠다.
- 파일명 대소문자가 다르면 로컬에서는 되고 배포에서만 깨진다(5절).
- 푸시 전에 빌드와 타입 검사를 돌리고, 실패하면 푸시하지 않는다. 예: `npm run build && git push`

## 11. 해커톤 운영

- 2~3시간마다 30초씩 맞춘다. 각자 "지금 데모 되나?"를 한 문장으로 말한다.
- 5분 넘게 막히면 혼자 붙잡지 말고 팀에 공유한다.
- 데모에 안 보이는 것은 만들지 않는다. 우선순위는 PRD 6-1절의 P0부터 P3 순서다.
- 마감 2시간 전에 코드를 얼린다. 그 뒤로는 새 기능을 머지하지 않고 버그 수정과 리허설만 한다.
- 정상 동작 화면을 미리 녹화해 둔다. 현장 와이파이나 서버가 죽어도 보여 줄 수 있다.
- 배포 URL을 제출하면 제출 직후부터 심사가 끝날 때까지 main에 머지하지 않는다. 문서만 바꾼 커밋도 배포를 다시 빌드한다.
- 데모용 가짜 공지를 넣지 않는다. 실제 수집으로 시연한다.

## 12. .gitignore에 있어야 하는 것

지금 저장소의 `.gitignore`는 Visual Studio 템플릿이다. 2026-10-03에 확인했을 때 `.env`, `node_modules/`, `__pycache__/`는 걸렸지만 `.venv/`와 `.next/`는 빠져 있었다. 아래 목록과 대조해서 빠진 것을 더한다.

```
.env
.env.*
!.env.example
node_modules/
.venv/
venv/
__pycache__/
.next/
dist/
build/
*.log
.DS_Store
.playwright-mcp/
```

## 13. 이 문서를 고칠 때

- 무엇을 만드는지는 PRD, 어떻게 만드는지는 이 문서를 본다. 둘 다 답이 없으면 팀 채팅에 묻는다.
- 이 문서는 `docs/` 브랜치에서 PR로 고치고, 고친 내용을 팀에 알린다.
