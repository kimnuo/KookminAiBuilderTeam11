"""같은 공지가 두 출처에 올라온 것을 목록에서 하나로 줄인다 (팀 QA 2026-10-03).

같은 글이 본부·SW사업단·소융 게시판에 동시에 올라온다 (ICPC 참가 신청, AI역량평가 접수 등).
**제목이 같고 게시일이 사흘 안쪽**일 때만 같은 글로 본다 — 제목만 보면 몇 달 뒤 재공지
(6/30 「AI역량평가 응시 안내」 vs 9/29 같은 제목)까지 지워져서 다른 회차가 사라진다.

남길 글은 코드가 정한다: 요약이 끝난 것 → 출처 목록(config.SOURCES) 순서 → 최근 게시 → id.
같은 입력이면 같은 결과가 나와야 한다 (PRD 3절).
"""

import re
from collections import defaultdict

from app.core.config import SOURCES
from app.core.schemas import Notice

SAME_WITHIN_DAYS = 3
_SOURCE_ORDER = {source["id"]: i for i, source in enumerate(SOURCES)}
_TRIM = re.compile(r"[\s\[\]()·…~\-–—:,.\"'“”‘’!?/]+")


def _key(notice: Notice) -> str:
    return _TRIM.sub("", notice.original_title).lower()


def _rank(notice: Notice) -> tuple:
    posted = notice.posted_at.toordinal() if notice.posted_at else 0
    return (
        notice.digest.status != "done",
        _SOURCE_ORDER.get(notice.source.id, len(_SOURCE_ORDER)),
        -posted,
        notice.id,
    )


def _pick(items: list[Notice]) -> list[Notice]:
    """제목이 같은 글들 중에서, 게시일이 가까운 것끼리 묶어 묶음마다 하나만 남긴다."""
    if len(items) == 1:
        return items
    kept: list[Notice] = []
    for notice in sorted(items, key=_rank):
        posted = notice.posted_at
        near = any(
            k.posted_at is not None
            and posted is not None
            and abs((k.posted_at - posted).days) <= SAME_WITHIN_DAYS
            for k in kept
        )
        if not near:
            kept.append(notice)
    return kept


def unique(notices: list[Notice]) -> list[Notice]:
    """목록에서 겹치는 글을 덜어 낸다. 상세(`/api/notices/{id}`)는 그대로 열린다."""
    groups: dict[str, list[Notice]] = defaultdict(list)
    for notice in notices:
        groups[_key(notice)].append(notice)
    keep = {n.id for items in groups.values() for n in _pick(items)}
    return [n for n in notices if n.id in keep]
