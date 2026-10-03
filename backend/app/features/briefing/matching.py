"""공지 대상 조건(Audience)과 내 상황(Situation) 대조.

None = 나는 대상이 아님. 빈 목록 = 대상 조건이 없어 모두 대상. 문자열 목록 = 맞는 이유.
학과·신분은 표기가 제각각이라 부분 일치로 본다 (예: 「소프트웨어」 ⊂ 「소프트웨어학부」).
"""

from app.core.config import MAJOR_GROUPS
from app.core.schemas import Audience, Situation

# 신분 표기는 제각각이라 같은 뜻끼리 묶는다
_STATUS_GROUPS = {
    "재학": ("재학", "대학생", "학부생"),
    "휴학": ("휴학",),
    "졸업예정": ("졸업예정", "졸업 예정", "졸업대상", "졸업 대상", "수료예정"),
    "졸업생": ("졸업생", "졸업자", "졸업한"),
}


def audience_reasons(audience: Audience | None, me: Situation) -> list[str] | None:
    if audience is None:
        return []
    reasons: list[str] = []
    for check in (_year, _major, _status):
        result = check(audience, me)
        if result is None:
            return None
        reasons += result
    return reasons


def _year(audience: Audience, me: Situation) -> list[str] | None:
    if not audience.years or me.year is None:
        return []
    return [f"{me.year}학년 대상"] if me.year in audience.years else None


def _major(audience: Audience, me: Situation) -> list[str] | None:
    if not audience.majors or not me.major:
        return []
    mine = me.major.replace(" ", "")
    for major in audience.majors:
        theirs = major.replace(" ", "")
        group = MAJOR_GROUPS.get(theirs, [theirs])
        if any(g and (g in mine or mine in g) for g in group):
            return [f"{major} 대상"]
    return None


def _status(audience: Audience, me: Situation) -> list[str] | None:
    """공지가 아는 신분을 적었는데 그중 내 신분이 없으면 대상 아님. 모르는 표현만 있으면 거르지 않는다."""
    if not audience.statuses or not (me.status or me.graduating):
        return []
    text = " ".join(audience.statuses)
    named = {group for group, words in _STATUS_GROUPS.items() if any(w in text for w in words)}
    if not named:
        return []
    mine = _my_groups(me)
    hit = [g for g in ("졸업예정", "재학", "휴학", "졸업생") if g in named and g in mine]
    return [f"{hit[0]}생 대상" if hit[0] != "졸업예정" else "졸업예정자 대상"] if hit else None


def _my_groups(me: Situation) -> set[str]:
    groups = {g for g, words in _STATUS_GROUPS.items() if me.status and any(w in me.status for w in words)}
    if me.graduating:
        groups |= {"졸업예정", "재학"}
    return groups
