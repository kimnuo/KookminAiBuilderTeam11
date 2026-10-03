"""LLM 출력을 코드가 검사한다. 근거(evidence)가 입력 글에 실제로 없으면 그 항목은 버린다."""

import logging
import re
from datetime import date

from app.core.config import CATEGORIES
from app.core.schemas import Audience, Deadline, Digest, KeyDate, KeyPoint, Requirement

log = logging.getLogger(__name__)
_LOOSE_RE = re.compile(r"[\s\"'“”‘’`·•.,:;()\[\]{}<>~\-–—_/|*※]+")


def loose(text: str) -> str:
    """공백·문장부호를 지워 비교한다 (LLM 이 띄어쓰기·따옴표만 바꾼 경우는 통과)."""
    return _LOOSE_RE.sub("", text or "")


def to_digest(raw: dict, source_text: str, default_category: str) -> tuple[Digest, list[str]]:
    haystack = loose(source_text)
    found = lambda ev: bool(loose(ev)) and loose(ev) in haystack  # noqa: E731
    title, summary = (raw.get("title") or "").strip(), (raw.get("summary") or "").strip()
    if not title or not summary:
        raise ValueError("요약 제목·내용 요약이 비어 있음")
    digest = Digest(
        status="done",
        title=title,
        summary=summary,
        key_points=[KeyPoint(**k) for k in raw.get("keyPoints", []) if found(k.get("evidence"))],
        requirements=[Requirement(**r) for r in raw.get("requirements", []) if found(r.get("evidence"))],
        deadline=_dated(Deadline, raw.get("deadline"), found),
        last_date=_dated(KeyDate, raw.get("lastDate"), found),
        action_required=raw.get("actionRequired"),
        audience=_audience(raw.get("audience")),
        etc=[e for e in raw.get("etc", []) if e and e.strip()][:4],
    )
    _log_dropped(raw, digest)
    return digest, _categories(raw.get("categories"), default_category)


def _dated(model, raw: dict | None, found):
    if not raw or not found(raw.get("evidence")):
        return None
    try:
        date.fromisoformat(raw.get("date", ""))
    except ValueError:
        return None
    return model(**raw)


def _audience(raw: dict | None) -> Audience | None:
    if not raw:
        return None
    years = [y for y in raw.get("years", []) if isinstance(y, int) and 1 <= y <= 6]
    return Audience(
        years=years, majors=raw.get("majors", []), statuses=raw.get("statuses", []),
        text=raw.get("text"),
    )


def _categories(raw: list | None, default_category: str) -> list[str]:
    picked = [c for c in (raw or []) if c in CATEGORIES]
    return list(dict.fromkeys(picked))[:2] or [default_category]


def _log_dropped(raw: dict, digest: Digest) -> None:
    dropped = (len(raw.get("keyPoints", [])) - len(digest.key_points)
               + len(raw.get("requirements", [])) - len(digest.requirements)
               + (1 if raw.get("deadline") and digest.deadline is None else 0))
    if dropped:
        log.info("근거를 원문에서 못 찾아 버린 항목 %d개 (%s)", dropped, digest.title)
