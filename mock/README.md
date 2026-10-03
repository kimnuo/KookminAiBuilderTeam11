# 더미 화면 자료

사용자가 요청한 UI 미리보기용 가상 공고와 가상 인물입니다. 실제 수집 결과가 아니며 대회에서 실제 수집을 시연하는 용도로 사용하지 않습니다.

- `notices.json`, `more-notices.json`, `campus-notices.json`: 공고 8개, Notice 형식
- `sources.json`: 가상 출처
- `requirements.json`: 공고 ID별 fields/documents 응답
- `profile.json`: 가상 프로필, 브라우저 메모리에서만 사용

`npm run dev --prefix frontend` 후 `http://127.0.0.1:4173/?demo=1`을 엽니다. 더미 모드에는 명시적인 안내가 표시됩니다.
- `profile-tags.json`: 가상 프로필 태그. `config.profileTagsEndpoint` 가 비어 있고 기기에 저장된 프로필 태그도 없을 때 일반 화면에서 쓴다
