"""출처가 다른데 같은 공지인 글 합치기 (본부 학사공지와 소융대 학사공지에 같은 글이 올라온다).

같은 공지로 보는 조건: 출처가 다르고, 마감 날짜가 같고(시각은 둘 다 있을 때만 비교), 제목에서 연도·학기·「안내」 같은
흔한 말을 뺀 나머지가 거의 같다 (difflib 유사도 0.75 이상).
"""

import re
from difflib import SequenceMatcher

from app.core.schemas import BriefingItem

_NOISE_RE = re.compile(r"\(.*\)|\[.*\]|\d{4}학년도|\d{4}년|\d학기|\d{4}-\d|안내|신청|공지|모집")
_LOOSE_RE = re.compile(r"[\s·.,:~\-–—_/|]+")
THRESHOLD = 0.75


def _core(title: str) -> str:
    return _LOOSE_RE.sub("", _NOISE_RE.sub("", title))


def _same(a: BriefingItem, b: BriefingItem) -> bool:
    da, db = a.notice.digest.deadline, b.notice.digest.deadline
    if a.notice.source.id == b.notice.source.id or not da or not db:
        return False
    if da.date != db.date or (da.time and db.time and da.time != db.time):
        return False
    ratio = SequenceMatcher(None, _core(a.notice.original_title), _core(b.notice.original_title)).ratio()
    return ratio >= THRESHOLD


def merge_duplicates(items: list[BriefingItem]) -> list[BriefingItem]:
    kept: list[BriefingItem] = []
    for item in items:
        twin = next((k for k in kept if _same(k, item)), None)
        if twin is None:
            kept.append(item)
        else:
            source = item.notice.source
            twin.reasons.append(f"{source.group} {source.name}에도 같은 공지")
    return kept
