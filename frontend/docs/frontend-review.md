# 민섭 담당 프론트 검증 — 2026-10-03

범위: `feed`, `notice`, `apply_helper` 및 이 화면의 공용 모델·API 어댑터. Flutter 3.47.4 / Dart 3.13.3에서 검사했습니다.

## 지적사항 처리

| 항목 | 처리와 확인 |
|---|---|
| 마감된 공고가 먼저 나옴 | 진행 중 공고의 마감 시각 순 → 마감 미확인 → 마감된 공고. 한국 시간 경계·같은 마감의 결정적 순서 검사 |
| 태그 검색 | `digest.tags`를 읽음. `matchedTags`와 혼동하지 않음. 태그에만 있는 검색어로 화면에서 1건 검색 |
| 데모 지원 정보 수정 | 데모 상세의 수정 버튼 숨김. 가상 정보만 읽음. 실서버 모드 저장 후 새 값 반영 확인 |
| 포스터와 신청 방법 | 이미지 첨부 URL 미리보기·확대, 상대 URL 해석. 근거 있는 신청·접수·제출 방법을 표시하고 주요 내역·필수 사항도 표시 |
| 문서 개인 경로·이름 | 개인 SDK 경로 삭제, 담당자 이름을 해서로 수정 |
| 배포 빌드 안내 | 공고 API와 `USE_MOCK`의 역할을 분리. 현재 서버 예시의 8091 포트 사용. 배포 주소와 가입 API 연결 상태에 따라 설정하도록 안내 |
| 카테고리 전체 목록 | 이름·전체 보기 버튼으로 열기. 3개 미리보기와 분리하여 전체 목록을 스크롤하고 12번째 공고 열기 검사 |
| 온보딩의 guide | `HC-onboarding`의 선택 인자 `guide`는 기존 `StepScaffold` 호출 방식과 호환됨 |

## 자동 회귀 검사: 새 검사 90/90 통과

| 테스트 파일 | 통과 |
|---|---:|
| `notice_deadline_test.dart` | 20 |
| `notice_view_test.dart` | 18 |
| `notice_media_test.dart` | 15 |
| `feed_controller_test.dart` | 8 |
| `notice_api_test.dart` | 5 |
| `application_values_test.dart` | 4 |
| `notice_widgets_test.dart` | 4 |
| `feed_widgets_test.dart` | 4 |
| `category_widgets_test.dart` | 5 |
| `apply_helper_test.dart` | 7 |

검사에는 한국 시간 자정·당일 마감 시각, 잘못된 날짜·시각·빈 근거, 태그/별칭/다중 검색, 분류 중복 선택, 홈 초기화, 이미지 URL·자료형, 실패 상태의 AI 결과 숨김, API 실패 재시도, 기기 저장값과 복사 성공·실패가 포함됩니다.

```bash
cd frontend
flutter test test/notice_deadline_test.dart test/notice_view_test.dart \
  test/notice_media_test.dart test/feed_controller_test.dart \
  test/notice_api_test.dart test/application_values_test.dart \
  test/notice_widgets_test.dart test/feed_widgets_test.dart \
  test/apply_helper_test.dart test/category_widgets_test.dart
flutter analyze
flutter build web
```

- 정적 분석: 이슈 0건.
- 웹 빌드: 성공.
- 수정 코드의 구조: 파일 200줄 이하, 함수 40줄 이하, 기능 간 직접 import 없음. 새 테스트의 함수 길이도 점검했습니다.
- 기존 로그인 통합 테스트의 예전 피드 자리표시자 기대값을 현재 크노 대시보드로 갱신했습니다.
- 전체 `flutter test`: **112건 통과 / 1건 실패**. 실패한 `pdf_extract_test.dart`는 PDFium 네이티브 라이브러리를 찾지 못합니다. 수정 전 main(`d7c3ad0`)을 별도 작업 폴더에서 실행해 같은 실패를 재현했습니다. PDF 추출 구현은 프론트 A 범위입니다.

위 수치는 프론트 로직·표시의 회귀 검사 결과입니다. AI 추출 정확도는 백엔드 평가 자료를 사용합니다. API 테스트는 서버 계약과 같은 가상 응답을 사용하며 실제 LLM을 호출하지 않습니다.

## 실행한 웹 화면 확인: 14개 시나리오 통과

Playwright 브라우저에서 Flutter 웹 빌드의 실제 화면을 조작했습니다. 데모 모드 및 `?demo=1`이 없는 API 모드에서 검사했으며, API 모드 응답은 서버 스키마를 재현한 가상 자료입니다.

1. 데스크톱 1280×720: 6개 카드와 여러 공고 표시.
2. 모바일 390×844: 2열×3행으로 6개 카드가 한 화면에 표시.
3. 데모 상세: 지원 정보 수정 버튼이 없고 가상 지원 정보 표시.
4. `digest.tags`에만 있는 검색어: 해당 공고 1건 검색.
5. 마감 임박 목록: D-1 → D-3 → 원문 확인 → 마감 순.
6. 데스크톱 상세: 중앙 팝업과 내부 스크롤, 고정 원문 버튼.
7. 모바일 상세: 팝업과 포스터·내부 스크롤.
8. `previewMedia` 없는 응답: `attachments`의 이미지 URL로 포스터 표시.
9. 데모와 네트워크 포스터: 확대 팝업 표시.
10. 신청 방법·주요 내역·필수 사항 및 근거 표시.
11. 실서버 모드 지원 정보 저장: 상세 재진입 후 가상 이메일 새 값 표시. 준비 API 404는 필수 사항과 원문 안내.
12. 예시 PDF 다운로드.
13. 카테고리 하단 전체 보기: 미리보기의 3개를 넘어 4번째 공고도 표시.
14. 카테고리 이름: 전체 목록을 열고 12번째 공고까지 스크롤 후 상세 열기.

스크린샷은 `output/playwright/kno-review-*.png`에 있습니다(생성물이라 Git 제외). 기기 저장 검사에는 `review@example.com` 같은 가상 값만 사용했습니다.

## 실제 배포에서 확인할 항목

- 서버가 본문 포스터 URL을 보내지 않으면 프론트가 그 이미지를 복원할 수 없습니다. 현재 계약의 이미지 첨부 URL은 미리보기하며 본문 이미지 URL 제공은 서버 작업이 필요합니다.
- 웹 주소는 `https://kmu-notice-demo.vercel.app`로 문서에 반영되었습니다. API 주소는 아직 확정되어 있지 않으므로 주소와 가입·온보딩 API 연결 상태를 README의 빌드 설정에 적용해야 합니다.
- 실제 서버의 응답·이미지 접근 정책·CORS는 배포 주소에서 최종 확인해야 합니다.

## 후속 서버 응답 점검

- API 모드의 마감순을 프론트에서 다시 날짜로 정렬하지 않습니다. 서버 순서를 유지하고 지난 마감만 뒤로 옮깁니다. 2022·2023년 마감과 서버 순서 보존 회귀 검사를 추가했습니다.
- 지원 준비 API의 `fields/documents`와 공고의 근거 있는 `digest.requirements`를 함께 읽습니다. 준비 API가 404여도 공고의 준비 항목은 표시하고, 같은 문장은 한 번만 표시합니다.
- 출처 `sw-notice`는 다른 메뉴 항목과 같은 형식인 `SW사업단 공지사항`으로 표시합니다. 출처 ID는 그대로 사용합니다.
- `apply_server_test.dart` 6건과 관련 회귀 검사 합계 **59건 통과**, 정적 분석 이슈 0건.
- 현재 main에는 `FitCard`와 합격 가능성 표시가 없습니다. 다른 팀원 브랜치의 합격 가능성 구현은 사용자의 지시에 따라 수정하지 않았습니다.
