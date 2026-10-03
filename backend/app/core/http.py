"""학교 서버 요청용 HTTP 클라이언트. 이름을 밝힌 User-Agent 와 요청 간격(전역)을 지킨다."""

import threading
import time

import httpx

from app.core.config import REQUEST_GAP_SEC, REQUEST_TIMEOUT_SEC, USER_AGENT

_lock = threading.Lock()
_last_request_at = 0.0


class TooLargeError(Exception):
    pass


def _wait_turn() -> None:
    global _last_request_at
    wait = REQUEST_GAP_SEC - (time.monotonic() - _last_request_at)
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def _client() -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT_SEC,
        follow_redirects=True,
    )


def fetch_text(url: str) -> str:
    with _lock:
        _wait_turn()
        with _client() as client:
            response = client.get(url)
    response.raise_for_status()
    return response.text


def fetch_json(url: str):
    with _lock:
        _wait_turn()
        with _client() as client:
            response = client.get(url)
    response.raise_for_status()
    return response.json()


def fetch_bytes(url: str, max_bytes: int) -> bytes:
    """첨부파일 다운로드. max_bytes 를 넘으면 받다가 멈추고 TooLargeError."""
    with _lock:
        _wait_turn()
        with _client() as client, client.stream("GET", url) as response:
            response.raise_for_status()
            chunks, size = [], 0
            for chunk in response.iter_bytes():
                size += len(chunk)
                if size > max_bytes:
                    raise TooLargeError(f"{size} bytes 초과")
                chunks.append(chunk)
    return b"".join(chunks)
