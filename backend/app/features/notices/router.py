from fastapi import APIRouter, HTTPException, Query

from app.core.config import CATEGORIES, SOURCES, source_list_url
from app.core.schemas import Notice, NoticePage, Source
from app.features.notices import service

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
def get_notice(notice_id: str) -> Notice:
    notice = service.get_notice(notice_id)
    if notice is None:
        raise HTTPException(status_code=404, detail="notice not found")
    return notice
