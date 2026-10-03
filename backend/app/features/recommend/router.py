from fastapi import APIRouter

from app.core.schemas import RecommendRequest, RecommendResponse
from app.features.recommend.service import recommend

router = APIRouter(tags=["recommend"])


@router.post(
    "/recommend",
    response_model=RecommendResponse,
    summary="공지마다 될 가능성과 추천 근거 한 줄",
    description="상황 정보는 저장하지 않는다. 이름·학번·연락처는 받지 않는다.",
)
def recommendations(request: RecommendRequest) -> RecommendResponse:
    return recommend(request)
