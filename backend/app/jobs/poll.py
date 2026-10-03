"""수집 한 바퀴: 출처마다 새 글 → 재료 모으기 → DB(pending) → AI 요약 → DB(done/failed).

- 학교 서버 요청은 순서대로(전역 1초 간격), AI 호출만 LLM_CONCURRENCY 개씩 동시에
- 한 번에 한 바퀴만 돈다 (스케줄러와 「지금 수집」이 겹치지 않게)
- 실패하면 이전 데이터는 그대로 둔다 (PRD 15절)
"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from app.ai.digest import make_digest
from app.collectors import fetch_list
from app.collectors.common import now_kst
from app.core.config import LLM_CONCURRENCY, NEW_PER_SOURCE, SOURCES
from app.core.ordering import article_no
from app.core.schemas import Notice
from app.db import store
from app.jobs.gather import Material, gather

log = logging.getLogger(__name__)
_run_lock = threading.Lock()
status: dict = {"running": False, "startedAt": None, "finishedAt": None, "new": 0, "errors": []}


def poll_once(per_source: int = NEW_PER_SOURCE) -> dict:
    if not _run_lock.acquire(blocking=False):
        return {**status, "skipped": "이미 수집 중"}
    try:
        status.update(running=True, startedAt=_now(), finishedAt=None, new=0, errors=[])
        for source in SOURCES if per_source > 0 else []:
            _collect_source(source, per_source)
        _digest_pending()
    finally:
        status.update(running=False, finishedAt=_now())
        _run_lock.release()
    return dict(status)


def poll_in_background(per_source: int = NEW_PER_SOURCE) -> bool:
    if _run_lock.locked():
        return False
    threading.Thread(target=poll_once, args=(per_source,), daemon=True, name="poll").start()
    return True


def redigest_in_background() -> bool:
    """수집 없이 저장된 글 전부를 다시 요약한다."""
    if _run_lock.locked():
        return False
    store.mark_all_for_redigest()
    threading.Thread(target=poll_once, args=(0,), daemon=True, name="redigest").start()
    return True


def _collect_source(source: dict, per_source: int) -> None:
    try:
        listed = fetch_list(source)
    except Exception as exc:
        _error(f"{source['id']} 목록 실패: {type(exc).__name__}")
        return
    known = store.known_ids(source["id"])
    new = sorted((n for n in listed if n.id not in known), key=article_no, reverse=True)
    for notice in new[:per_source]:
        try:
            notice, material = gather(notice)
        except Exception as exc:
            _error(f"{notice.id} 상세 실패: {type(exc).__name__}")
            continue
        store.save(notice, body=material.to_json())
        status["new"] += 1


def _digest_pending() -> None:
    pending = store.pending_with_body(limit=500)
    with ThreadPoolExecutor(max_workers=LLM_CONCURRENCY, thread_name_prefix="digest") as pool:
        list(pool.map(_digest_one, pending))


def _digest_one(item: tuple[Notice, str]) -> None:
    notice, raw = item
    material = Material.from_json(raw)
    digest, categories = make_digest(notice, material.body, material.files)
    store.save(notice.model_copy(update={"digest": digest, "categories": categories}))


def _error(message: str) -> None:
    log.warning(message)
    status["errors"].append(message)


def _now() -> str:
    return datetime.isoformat(now_kst())
