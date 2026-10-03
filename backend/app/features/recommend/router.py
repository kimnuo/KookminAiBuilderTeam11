from fastapi import APIRouter, Header

from app.core.schemas import RecommendRequest, RecommendResponse, Situation, Subscription
from app.db import store
from app.features.auth.router import _bearer
from app.features.auth.service import user_of
from app.features.recommend.service import recommend

router = APIRouter(tags=["recommend"])


@router.post(
    "/recommend",
    response_model=RecommendResponse,
    summary="공지마다 될 가능성과 추천 근거 한 줄",
    description="상황 정보는 저장하지 않는다. 이름·학번·연락처는 받지 않는다.",
)
def recommendations(
    request: RecommendRequest, authorization: str | None = Header(None)
) -> RecommendResponse:
    return recommend(with_subscription(request, authorization))


def with_subscription(request: RecommendRequest, authorization: str | None) -> RecommendRequest:
    """상황을 안 보냈으면 로그인한 사람의 구독 설정(학과·학년·분야·태그)으로 채운다."""
    me = user_of(_bearer(authorization))
    raw = store.get_subscription(me) if me else None
    if raw is None:
        return request
    sub = Subscription.model_validate_json(raw)
    situation = request.situation
    if situation.major is None and situation.year is None and not situation.interests:
        situation = Situation(major=sub.major, year=sub.year, status="재학", interests=sub.categories)
    return request.model_copy(update={"situation": situation, "tags": request.tags or sub.tags})
