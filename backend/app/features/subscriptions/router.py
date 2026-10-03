"""구독 설정(나의 상황). 화면 온보딩·설정에서 보내고, 피드 추천 순서에 쓴다."""

from fastapi import APIRouter, Header

from app.core.schemas import Subscription
from app.db import store
from app.features.auth.router import _me

router = APIRouter(tags=["subscriptions"])


@router.put("/subscriptions", summary="내 학과·학년·관심 분야·태그 저장")
def put_subscription(body: Subscription, authorization: str | None = Header(None)) -> dict:
    store.save_subscription(_me(authorization), body.model_dump_json(by_alias=True))
    return {"ok": True}


@router.get("/subscriptions", response_model=Subscription, summary="내 구독 설정")
def get_subscription(authorization: str | None = Header(None)) -> Subscription:
    raw = store.get_subscription(_me(authorization))
    return Subscription.model_validate_json(raw) if raw else Subscription()
