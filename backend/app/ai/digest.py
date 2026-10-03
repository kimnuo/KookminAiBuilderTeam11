"""공지 하나(본문 + 첨부 글)를 한 페이지 요약(Digest)으로 만든다.

- AI 로 보내기 전에 학번을 가리고 길이를 자른다 (core/text.py)
- 형식이 틀리거나 호출이 실패하면 1회 다시 부르고, 그래도 안 되면 failed (PRD 11절)
- 근거 검사는 ai/verify.py
"""

import logging
from pathlib import Path

from pydantic import ValidationError

from app.ai.digest_schema import DIGEST_SCHEMA
from app.ai.llm import LlmError, complete_json
from app.ai.verify import to_digest
from app.core.config import ATTACHMENT_MAX_CHARS, LLM_INPUT_MAX_CHARS
from app.core.schemas import Digest, Notice
from app.core.text import clip, mask_pii

log = logging.getLogger(__name__)
SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "digest_system.md").read_text(encoding="utf-8")
MAX_ATTEMPTS = 2


def build_input(notice: Notice, body: str, files: list[tuple[str, str]]) -> str:
    parts = [
        f"출처: {notice.source.group} {notice.source.name}",
        f"원 제목: {notice.original_title}",
        f"게시일: {notice.posted_at or '모름'}",
        f"부서·분류: {notice.department or '모름'}",
        "",
        "[본문]",
        body.strip() or "(본문 없음 — 내용이 첨부파일에 있을 수 있음)",
    ]
    for name, text in files:
        parts += ["", f"[첨부: {name}]", clip(text, ATTACHMENT_MAX_CHARS)]
    return clip(mask_pii("\n".join(parts)), LLM_INPUT_MAX_CHARS)


def make_digest(notice: Notice, body: str, files: list[tuple[str, str]]) -> tuple[Digest, list[str]]:
    """(digest, categories). 실패해도 예외를 던지지 않고 failed digest 를 돌려준다."""
    user_input = build_input(notice, body, files)
    default_category = notice.categories[0]
    error = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            raw = complete_json(SYSTEM_PROMPT, user_input, DIGEST_SCHEMA)
            return to_digest(raw, user_input, default_category)
        except (LlmError, ValidationError, ValueError, TypeError) as exc:
            error = f"{type(exc).__name__}: {exc}"[:300]
            log.warning("digest 실패 %s (시도 %d/%d): %s", notice.id, attempt, MAX_ATTEMPTS, error)
    return Digest(status="failed", error=error), notice.categories
