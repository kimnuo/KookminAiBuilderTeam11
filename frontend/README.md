# 크노 — Flutter 웹

택준의 Flutter 가입·동의·온보딩·이력·PDF·설정 화면과 민섭의 카테고리 대시보드·공고 상세·지원 준비 화면을 하나의 앱으로 통합했습니다. 기존 JavaScript 프론트는 제거했습니다.

## 실행

Flutter 3.47 / Dart 3.13.3 이상을 사용합니다.

```bash
cd frontend
flutter pub get
flutter run -d chrome --web-port 4173
```

더미 데이터는 `http://localhost:4173/?demo=1`에서 볼 수 있습니다. 가상 공고 9개와 가상 지원 정보를 메모리에서 사용하며 기존 저장 정보를 덮어쓰지 않습니다. `assets/demo/`는 루트 `mock/`의 미리보기 자료 사본입니다. 변경 시 `python3 scripts/sync-demo.py`로 동기화합니다.

## 빌드와 정적 미리보기

```bash
flutter analyze
flutter build web
python3 scripts/dev-server.py
# http://127.0.0.1:4173/?demo=1
```

빌드 결과는 `build/web/`이며 Git에 포함하지 않습니다. SDK가 PATH에 없으면 이 기기의 `/Users/seopseopi/develop/flutter/bin/flutter`를 사용합니다.

## 화면과 동작

- 혜선의 백엔드 분류(학사·생활, 졸업, 장학, 취업, 행사·대외활동, 기타) 6개를 첫 화면에 모두 배치합니다. 가로·세로 크기에 따라 3열×2행, 2열×3행으로 바뀌고 화면 높이에 맞춰 카드 크기를 조절합니다. 작은 화면에서는 미리보기 문장을 줄입니다.
- 웹 카드에는 공고를 최대 3개씩 함께 표시하며, 제목을 누르면 바로 상세로 이동합니다. 작은 화면에서는 카드 높이에 맞춰 미리보기 수를 줄입니다.
- 카드를 누르면 해당 카테고리 목록이 대화상자로 열립니다. 목록은 8개씩 페이지를 나누며 대화상자 내부에서 스크롤합니다.
- 체크박스로 여러 카테고리를 선택한 뒤 `선택 공고`를 누르면 합쳐진 목록을 볼 수 있습니다. 겹치는 공고는 한 번만 표시합니다.
- 검색은 제목·출처·요약·태그·카테고리에서 여러 단어를 찾습니다. 대소문자·전각 영문·공백과 SW대학·SW사업단의 명칭 차이를 처리합니다. 출처 필터와 추천/마감 임박 정렬도 지원합니다.
- 대시보드에서 공고를 누르면 최대 너비 820px·높이 720px의 중앙 팝업으로 상세가 열립니다. 내용만 내부에서 스크롤되며, 닫으면 검색과 선택 상태가 유지됩니다.
- 상세에는 요약, 한국 시간 마감과 근거, 대상·신청 방법·추천 이유와 원문 링크를 보여 줍니다. AI 분석 실패 시 AI 결과를 숨깁니다.
- 지원 준비에는 근거가 있는 항목·서류만 표시하고 기기에 저장한 값을 복사합니다. 프로필 값은 서버와 AI로 보내지 않습니다.
- 상단의 내 지원 정보와 설정 버튼에서 택준의 화면으로 이동합니다. 가입은 `/#/signup`, 로그인은 `/#/login`에 있습니다.

## API 모드

`?demo=1` 없이 실행하면 공고 API를 사용합니다. URL 기본값은 `http://localhost:8000`입니다.

```bash
flutter run -d chrome --dart-define=USE_MOCK=false --dart-define=API_BASE_URL=http://localhost:8000
flutter build web --dart-define=USE_MOCK=false --dart-define=API_BASE_URL=https://api.example.com
```

`USE_MOCK`는 팀원의 가입·온보딩 API 미리보기 설정입니다. 공고 더미 모드는 명시적인 `?demo=1`로만 켭니다. 실서비스는 `USE_MOCK=false`로 빌드하고 서버의 CORS에서 웹 주소를 허용해야 합니다. 서버 연결 실패 시 더미 데이터로 바꾸지 않고 오류를 표시합니다.

## 구조

`lib/app/`는 라우팅과 기능 연결, `lib/features/`는 기능별 화면, `lib/shared/api/`는 서버 호출, `lib/shared/lib/`는 공용 모델·검색·날짜·기기 저장 정보, `lib/shared/ui/`는 공용 디자인입니다. 기능끼리 직접 import하지 않도록 app에서 상세와 지원 준비를 연결합니다.

## 예시 포스터와 첨부파일

`assets/demo/media/`에 AI 공모전 포스터와 PDF 3개가 있습니다. 공고 상세 팝업의 포스터는 확대할 수 있고 PDF는 다운로드합니다. `mock/media.json`은 공고와 예시 자료의 연결만 정의하며 실제 API 계약에는 추가하지 않습니다. 백엔드의 기존 `attachments`도 파일 링크로 표시합니다. 자료·이미지 생성 프롬프트는 [assets/demo/media/README.md](assets/demo/media/README.md)에 정리했습니다.
