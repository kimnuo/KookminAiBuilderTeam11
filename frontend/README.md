# 민섭 프론트엔드 (`MS`)

PRD 12절의 피드, 공지 상세, 지원 준비 패널을 구현한 브라우저 모듈 기반 화면입니다. 프레임워크는 아직 팀에서 정하지 않았으며, 런타임 외부 라이브러리 없이 동작합니다.

## 실행과 검사

```bash
cd frontend
npm ci
npm run dev
# http://127.0.0.1:4173

npm run check
npm test
npm run build
```

`check`는 JavaScript 타입 검사, 파일 200줄·함수 40줄 제한, 기능 간 import 금지, API 호출 위치와 포맷을 확인합니다. `build`는 배포용 정적 파일을 `frontend/dist/`에 만듭니다. 빌드 결과와 설치한 패키지는 Git에 올리지 않습니다.

## UI 참고

[토스 공식 디자인 시스템 자료](https://toss.tech/article/toss-design-system)를 참고해 밝은 회색 배경, 파란 강조색, 큰 글씨와 넉넉한 카드 여백을 적용했습니다. 모바일 상세는 하단 시트로 열리고 원문 버튼은 하단에 유지됩니다. 아이콘은 외부 폰트 없이 자체 SVG로 제공합니다. 서비스 이름과 공지 기능은 모아봄에 맞췄습니다.

## 폴더

- `src/app/`: 화면 연결과 진입점
- `src/features/feed/`: 피드와 카드, 검색·분야·출처 필터
- `src/features/notice/`: 상세 화면, 원문 근거, 키보드로 닫을 수 있는 대화상자
- `src/features/apply-helper/`: 필요 정보·서류 표시, 기기 내 값과 복사 버튼
- `src/shared/api/`: `fetch`를 사용하는 유일한 위치
- `src/shared/lib/`: 날짜, 개인정보 읽기, HTML 처리
- `src/shared/config.js`: API 주소·저장 키·태그 등 설정

## API 연동

정적 파일과 API는 같은 출처(origin)로 서비스해야 합니다. 별도 개발 서버를 쓸 경우 `/api`를 백엔드로 프록시해야 합니다. 기본 정적 서버는 API를 제공하지 않으므로 API 없이 실행하면 오류 안내와 빈 화면이 나옵니다. 임의 공지 데이터는 넣지 않았습니다.

- `GET /api/feed?sort=recommend|deadline&userId=...`: 서버가 결정한 순서 유지
- `GET /api/sources`
- `GET /api/notices/{id}`
- `GET /api/notices/{id}/requirements`

피드는 배열 또는 `{ items: [...] }`, `{ notices: [...] }`를 읽습니다. 추천 이유는 아직 PRD에 구체적인 응답 필드가 없어 `recommendationReasons`, `reasons`, `recommendationReason`을 지원합니다. 가중치·추천 점수는 화면에서 임의로 정하지 않습니다.

지원 준비는 PRD 6-1절의 `{ fields: [...], documents: [...] }`를 읽습니다. `key`는 PRD 고정 목록만 허용하며, `other`는 공고의 `label`만 보여 줍니다. 근거가 없는 마감일·항목은 표시하지 않고, AI가 `failed`이면 원문 링크를 보여 줍니다.

## 프론트 A와 맞출 설정

프로필 저장 키는 `kmu.profile`이며 PRD 10절 Profile 구조를 읽습니다. 수상·자격증·활동은 `history`에서 읽습니다. 지원 값은 기기에서 표시·복사만 하며 서버나 AI에 전송하지 않습니다.

선택적으로 `kmu.session`에 `{ "userId": "..." }`를 저장하면 피드 요청의 `userId`로 사용합니다. 없으면 동일 출처의 로그인 세션 쿠키를 사용합니다. 이 저장 키는 PRD에 미정이므로 프론트 A의 인증·프로필 화면과 연동할 때 `src/shared/config.js`에서 맞춰야 합니다. 추천 태그는 프로필의 `tags` 또는 `history.tags`를 읽습니다.

## 확인 범위

타입·구조·포맷 검사, 빌드와 12개 단위 검사를 통과했습니다. 단위 검사는 한국 날짜 기준 마감, 근거 없는 항목 제거, 실패한 AI 출력 숨김, 공식 지원 준비 응답, 잘못된 저장 데이터, 원문 URL과 API 개인정보 전송 여부를 다룹니다. 브라우저에서도 테스트 응답으로 필터·정렬 요청 경쟁·상세·지원 준비·복사·키보드·모바일 화면을 확인했습니다. 실제 API 연동 검증은 백엔드와 실제 수집 데이터가 준비된 뒤 필요합니다.

PR은 `main`을 대상으로 만들고, 머지 담당자가 **Create a merge commit**으로 합칩니다. `MS` 개인 브랜치는 머지 후에도 유지합니다.
