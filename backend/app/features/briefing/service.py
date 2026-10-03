"""「나의 상황」에서 반드시 봐야 할 글 고르기. AI 는 대상·마감·할 일 여부만 뽑아 두고, 고르는 건 코드다.

규칙 (모두 만족해야 들어간다)
1. AI 요약이 끝난 글 (done)
2. 마감이 안 지났다. 마감이 없으면 마지막 관련 날짜(lastDate)가 안 지났다. 둘 다 모르면 최근 30일 안에 올라온 글만
3. 학생이 할 일이 있다 (actionRequired)
4. 대상 조건(학년·학과·신분)이 내 상황과 맞는다. 조건이 비어 있으면 모두 대상
5. 내 관심 분류이거나, 누구에게나 필수인 분류(학사·생활, 졸업)
정렬: 마감 임박 순, 마감 모르는 글은 뒤에서 최신순. 출처만 다른 같은 공지는 하나로 합친다 (dedupe.py)
"""

from datetime import date, timedelta

from app.core.config import ALWAYS_RELEVANT_CATEGORIES
from app.core.ordering import newest_first
from app.core.schemas import BriefingItem, Notice, Situation
from app.features.briefing.dedupe import merge_duplicates
from app.features.briefing.matching import audience_reasons
from app.db import store

RECENT_DAYS = 30


def build_briefing(situation: Situation, today: date) -> list[BriefingItem]:
    items = []
    for notice in store.all_notices():
        item = _evaluate(notice, situation, today)
        if item:
            items.append(item)
    items.sort(key=lambda i: (i.days_left is None, i.days_left or 0, newest_first(i.notice)))
    return merge_duplicates(items)


def _evaluate(notice: Notice, situation: Situation, today: date) -> BriefingItem | None:
    digest = notice.digest
    if digest.status != "done" or not digest.action_required:
        return None
    days_left = (digest.deadline.date - today).days if digest.deadline else None
    if not _is_current(notice, days_left, today):
        return None
    matched = audience_reasons(digest.audience, situation)
    if matched is None:
        return None
    category_reason = _category_reason(notice, situation)
    if category_reason is None:
        return None
    reasons = [category_reason, *matched]
    if days_left is not None:
        reasons.append("오늘 마감" if days_left == 0 else f"마감 D-{days_left}")
    return BriefingItem(notice=notice, reasons=reasons, days_left=days_left)


def _is_current(notice: Notice, days_left: int | None, today: date) -> bool:
    if days_left is not None:
        return days_left >= 0
    if notice.digest.last_date:
        return notice.digest.last_date.date >= today
    return bool(notice.posted_at and notice.posted_at >= today - timedelta(days=RECENT_DAYS))


def _category_reason(notice: Notice, situation: Situation) -> str | None:
    for category in notice.categories:
        if category in situation.interests:
            return f"관심 분류 「{category}」"
    for category in notice.categories:
        if category in ALWAYS_RELEVANT_CATEGORIES:
            return f"모두 확인해야 하는 「{category}」 공지"
    return None
