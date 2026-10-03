"""서버 안에서 POLL_INTERVAL_MIN 분마다 수집한다 (PRD 9절: 학교 서버 부하를 고려해 10분)."""

import logging
import threading

from app.core.config import POLL_INTERVAL_MIN, POLL_ON_STARTUP
from app.jobs.poll import poll_once

log = logging.getLogger(__name__)
_stop = threading.Event()


def start() -> None:
    if POLL_INTERVAL_MIN <= 0:
        log.info("주기 수집 꺼짐 (POLL_INTERVAL_MIN=0)")
        return
    threading.Thread(target=_loop, daemon=True, name="scheduler").start()


def stop() -> None:
    _stop.set()


def _loop() -> None:
    if not POLL_ON_STARTUP:
        _stop.wait(POLL_INTERVAL_MIN * 60)
    while not _stop.is_set():
        try:
            poll_once()
        except Exception:
            log.exception("주기 수집 실패")
        _stop.wait(POLL_INTERVAL_MIN * 60)
