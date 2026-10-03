"""지원 준비 패널용: 공고 하나에서 적을 정보와 낼 서류를 뽑는다.

뽑는 규칙과 검사는 현찬의 `app/ai/requirements.py` 를 그대로 쓰고,
이 파일은 저장해 둔 본문을 넘겨 주고 결과를 캐시하는 일만 한다.
LLM 은 학교 AI 게이트웨이(ai/gateway.py)로 부른다.
"""

import logging

from app.ai.gateway import complete_text
from app.ai.requirements import extract_requirements, failed
from app.db import store

log = logging.getLogger(__name__)


def requirements_of(notice_id: str) -> dict:
    cached = store.get_requirements(notice_id)
    if cached is not None:
        return cached
    notice = store.get(notice_id)
    body = store.body_of(notice_id)
    if notice is None:
        return failed()
    data = _extract(notice.digest.title or notice.original_title, body or "")
    if data.get("status") != "failed":
        store.save_requirements(notice_id, data)
    return data


def _extract(title: str, body: str) -> dict:
    try:
        return extract_requirements({"title": title, "body": body}, complete_text)
    except Exception as exc:  # 게이트웨이 오류·형식 오류 모두 failed 로 둔다
        log.warning("지원 준비 추출 실패: %s", exc)
        return failed()
