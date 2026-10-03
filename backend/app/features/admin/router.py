"""데모·운영용. 「지금 수집」은 백그라운드로 돌고, 진행 상황은 poll-status 로 본다."""

from fastapi import APIRouter

from app.db import store
from app.jobs import poll

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/poll-now", summary="지금 수집 (백그라운드, 바로 응답)")
def poll_now() -> dict:
    started = poll.poll_in_background()
    return {"started": started, "status": poll.status}


@router.post("/redigest", summary="저장된 글 전부 다시 요약 (프롬프트를 바꿨을 때)")
def redigest() -> dict:
    return {"started": poll.redigest_in_background(), "status": poll.status}


@router.get("/poll-status", summary="수집 진행 상황과 저장된 글 수")
def poll_status() -> dict:
    return {"status": poll.status, "counts": store.counts()}
