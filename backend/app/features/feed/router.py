"""피드 화면용 전체 목록 (프론트 FeedPage 가 한 번에 받아 화면에서 거른다).

- recommend: 아직 개인 맞춤 점수가 없어 최신순이다. 개인 맞춤은 POST /api/briefing
- deadline: 마감 가까운 순, 마감 모르는 글은 뒤에서 최신순
"""

from datetime import date
from typing import Literal

from fastapi import APIRouter, Query

from app.core.ordering import newest_first
from app.core.schemas import Notice, NoticePage
from app.db import store

router = APIRouter(tags=["feed"])
_FAR_FUTURE = date.max.toordinal()


@router.get("/feed", response_model=NoticePage, summary="피드 (전체 목록, 페이지 없음)")
def get_feed(
    sort: Literal["recommend", "deadline"] = "recommend",
    user_id: str | None = Query(None, alias="userId", description="지금은 쓰지 않음"),
) -> NoticePage:
    notices = store.all_notices()
    notices.sort(key=_by_deadline if sort == "deadline" else newest_first)
    return NoticePage(items=notices)


def _by_deadline(n: Notice) -> tuple:
    deadline = n.digest.deadline.date.toordinal() if n.digest.deadline else _FAR_FUTURE
    return (deadline, *newest_first(n))
