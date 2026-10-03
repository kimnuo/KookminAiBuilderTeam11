"""공지 조회 로직: 필터와 정렬 (판단은 코드가 한다)."""

from app.core.ordering import newest_first
from app.core.paging import paginate
from app.core.schemas import Notice, NoticePage
from app.db import store


def get_notice(notice_id: str) -> Notice | None:
    return store.get(notice_id)


def list_notices(
    *,
    category: str | None,
    source: str | None,
    q: str | None,
    action_required: bool | None,
    cursor: str | None,
) -> NoticePage:
    notices = [
        n for n in store.all_notices()
        if _matches(n, category=category, source=source, q=q, action_required=action_required)
    ]
    notices.sort(key=newest_first)
    items, next_cursor = paginate(notices, cursor)
    return NoticePage(items=items, next_cursor=next_cursor)


def _matches(n: Notice, *, category, source, q, action_required) -> bool:
    if category and category not in n.categories:
        return False
    if source and n.source.id != source:
        return False
    if q and q.lower() not in f"{n.original_title} {n.digest.title or ''}".lower():
        return False
    if action_required is not None and n.digest.action_required is not action_required:
        return False
    return True
