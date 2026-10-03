"""피드 화면용 전체 목록 (프론트 FeedPage 가 한 번에 받아 화면에서 거른다).

- recommend: 로그인해서 구독 설정(학과·학년·분야·태그)이 있으면 그 사람에 맞춰 순서를 매기고
  추천 이유(recommendationReasons)를 붙인다. 설정이 없으면 최신순이다
- deadline: 마감 가까운 순, 마감 모르는 글은 뒤에서 최신순
- 어느 순서든 **만료(마감 지난) 글과 지난해 글은 아래로 내린다** (app/core/ordering)
- 같은 글이 두 출처에 올라온 것은 하나만 보낸다 (app/core/dedupe)
"""

from typing import Literal

from fastapi import APIRouter, Header, Query

from app.collectors.common import now_kst
from app.core.dedupe import unique
from app.core.ordering import by_deadline, newest_first
from app.core.schemas import NoticePage, Subscription
from app.db import store
from app.features.auth.router import _bearer
from app.features.auth.service import user_of
from app.features.feed.service import personalize

router = APIRouter(tags=["feed"])


@router.get("/feed", response_model=NoticePage, summary="피드 (전체 목록, 페이지 없음)")
def get_feed(
    sort: Literal["recommend", "deadline"] = "recommend",
    user_id: str | None = Query(None, alias="userId", description="지금은 쓰지 않음 (토큰으로 본다)"),
    authorization: str | None = Header(None),
) -> NoticePage:
    notices = unique(store.all_notices())  # 같은 글이 두 출처에 올라온 것은 하나로
    today = now_kst().date()
    notices.sort(key=by_deadline(today) if sort == "deadline" else newest_first)
    subscription = _subscription(authorization)
    if sort == "recommend" and subscription is not None:
        notices = personalize(notices, subscription)
    return NoticePage(items=notices)


def _subscription(authorization: str | None) -> Subscription | None:
    me = user_of(_bearer(authorization))
    raw = store.get_subscription(me) if me else None
    return Subscription.model_validate_json(raw) if raw else None
