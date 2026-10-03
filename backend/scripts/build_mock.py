"""DB 에 쌓인 실제 수집·AI 결과에서 mock/live-notices.json 을 만든다 (프론트용 실제 데이터, PRD 10절).

실행: cd backend && .venv/bin/python -m scripts.build_mock
- 수집(POST /api/admin/poll-now)을 한 번 돌린 뒤 실행한다
- 출처마다 고르게, AI 요약이 끝난(done) 글로 20건. 지어낸 값은 넣지 않는다
- 형식은 GET /api/notices 응답과 같다
"""

import json

from app.core.config import MOCK_NOTICES_PATH, SOURCES
from app.core.ordering import newest_first
from app.core.schemas import NoticePage
from app.db import store

TOTAL = 20


def main() -> None:
    done = [n for n in store.all_notices() if n.digest.status == "done"]
    by_source = {s["id"]: sorted((n for n in done if n.source.id == s["id"]), key=newest_first)
                 for s in SOURCES}
    picked = []
    while len(picked) < TOTAL and any(by_source.values()):
        for queue in by_source.values():
            if queue and len(picked) < TOTAL:
                picked.append(queue.pop(0))
    picked.sort(key=newest_first)
    page = NoticePage(items=picked, next_cursor=None)
    MOCK_NOTICES_PATH.parent.mkdir(exist_ok=True)
    MOCK_NOTICES_PATH.write_text(
        json.dumps(page.model_dump(by_alias=True, mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{len(picked)}건 → {MOCK_NOTICES_PATH}")


if __name__ == "__main__":
    main()
