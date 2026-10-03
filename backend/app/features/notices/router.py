from fastapi import APIRouter, Header, HTTPException, Query

from app.core.config import CATEGORIES, SOURCES, source_list_url
from app.core.schemas import Notice, NoticePage, RecommendRequest, Source
from app.features.notices import service
from app.features.notices.requirements import requirements_of
from app.features.recommend.router import with_subscription
from app.features.recommend.service import fit_of

router = APIRouter(tags=["notices"])


@router.get("/sources", response_model=list[Source], summary="수집 출처 목록")
def list_sources() -> list[Source]:
    return [
        Source(id=s["id"], name=s["name"], group=s["group"],
               url=source_list_url(s), default_category=s["defaultCategory"])
        for s in SOURCES
    ]


@router.get("/categories", response_model=list[str], summary="분류 목록 (고정)")
def list_categories() -> list[str]:
    return CATEGORIES


@router.get("/notices", response_model=NoticePage, summary="공지 목록 (최신순, 20건씩)")
def list_notices(
    category: str | None = Query(None, description="분류 (GET /api/categories 중 하나)"),
    source: str | None = Query(None, description="출처 ID"),
    q: str | None = Query(None, description="원 제목·요약 제목 검색"),
    action_required: bool | None = Query(None, alias="actionRequired", description="할 일이 있는 글만"),
    cursor: str | None = Query(None, description="이전 응답의 nextCursor"),
) -> NoticePage:
    return service.list_notices(
        category=category, source=source, q=q, action_required=action_required, cursor=cursor
    )


@router.get("/notices/{notice_id}", response_model=Notice, summary="한 페이지 요약 (공지 상세)")
def get_notice(notice_id: str, authorization: str | None = Header(None)) -> Notice:
    notice = service.get_notice(notice_id)
    if notice is None:
        raise HTTPException(status_code=404, detail="notice not found")
    request = with_subscription(RecommendRequest(), authorization)
    notice.fit = fit_of(notice_id, request)
    return notice


@router.get(
    "/notices/{notice_id}/requirements",
    summary="지원할 때 적을 정보와 낼 서류 (지원 준비 패널)",
    description="현찬의 app/ai/requirements.py 로 뽑는다. 사용자 정보는 보내지 않는다.",
)
def get_requirements(notice_id: str) -> dict:
    if service.get_notice(notice_id) is None:
        raise HTTPException(status_code=404, detail="notice not found")
    return requirements_of(notice_id)
