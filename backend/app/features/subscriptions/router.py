"""구독 설정(나의 상황). 화면 온보딩·설정에서 보내고, 피드 추천 순서에 쓴다."""

from fastapi import APIRouter, Header

from app.core.schemas import Subscription
from app.db import store
from app.features.auth.router import _me

router = APIRouter(tags=["subscriptions"])


@router.put("/subscriptions", summary="내 학과·학년·관심 분야·태그 저장 (보낸 항목만 바뀐다)")
def put_subscription(body: Subscription, authorization: str | None = Header(None)) -> dict:
    """보낸 항목만 덮어쓰고 나머지는 그대로 둔다.

    전에는 전체를 바꿔서, 이력 저장 화면이 `{tags}` 만 보내면 학과·학년·관심 분야가 null 이 됐다
    (팀 리뷰 5번). 지우고 싶으면 그 항목을 null·빈 배열로 **명시해서** 보내면 된다.
    """
    me = _me(authorization)
    raw = store.get_subscription(me)
    current = Subscription.model_validate_json(raw) if raw else Subscription()
    merged = current.model_copy(update=body.model_dump(exclude_unset=True))
    store.save_subscription(me, merged.model_dump_json(by_alias=True))
    return {"ok": True}


@router.get("/subscriptions", response_model=Subscription, summary="내 구독 설정")
def get_subscription(authorization: str | None = Header(None)) -> Subscription:
    raw = store.get_subscription(_me(authorization))
    return Subscription.model_validate_json(raw) if raw else Subscription()
