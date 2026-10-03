# 예시 포스터 및 첨부파일

- `ai-challenge-poster.png`: imagegen 기본 도구로 생성한 가상 AI 공모전 포스터. 실제 대학 로고·일정·주최 정보는 넣지 않았습니다.
- `ai-challenge-guide.pdf`: 가상 공모전 참가 안내.
- `scholarship-form.pdf`: 개인정보가 없는 빈 장학금 신청 양식.
- `graduation-guide.pdf`: 가상 졸업 프로젝트 설명회 안내.

PDF는 `scripts/generate-demo-pdfs.py`와 ReportLab으로 생성했으며 PNG로 렌더링해 확인했습니다. 이미지와 문서는 `mock/media.json`을 통해 더미 공고에 연결합니다.

## 포스터 최종 생성 프롬프트

Use case: ads-marketing. Asset type: a fictional event poster image displayed as a sample attachment inside the Korean university notices web app 크노. Generate one polished portrait 1024x1536 poster, full bleed flat artwork, not a photo of a printed poster. Clean Korean typography, white and vibrant blue palette, spacious editorial layout with a glossy 3D laptop and floating translucent blue idea bubbles and small connected geometric nodes. Large headline in exact Korean: "대학생 AI" then "서비스 아이디어" then "공모전". Smaller text: "기획 · 개발 · 디자인", "개인 또는 4인 이하 팀", "온라인 접수". Small footer text exactly "크노 · 예시 포스터". This is fictional preview material: do not include university seals, real organizations logos, sponsors, dates, QR codes, phone numbers, awards or claims. Keep all text sharp and readable, tasteful campus event graphic. Opaque background.
