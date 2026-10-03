from fastapi import APIRouter

from app.collectors.common import now_kst
from app.core.schemas import Briefing, Situation
from app.features.briefing.service import build_briefing

router = APIRouter(tags=["briefing"])


@router.post(
    "/briefing",
    response_model=Briefing,
    summary="나의 상황에서 반드시 봐야 할 글",
    description="상황 정보는 저장하지 않는다. 이름·학번·연락처는 받지 않는다.",
)
def briefing(situation: Situation) -> Briefing:
    now = now_kst()
    return Briefing(generated_at=now, items=build_briefing(situation, now.date()))
