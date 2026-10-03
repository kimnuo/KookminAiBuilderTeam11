"""서버 시작과 라우터 등록만 한다 (지침서 3절)."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS
from app.db import store
from app.features.admin.router import router as admin_router
from app.features.auth.router import router as auth_router
from app.features.briefing.router import router as briefing_router
from app.features.feed.router import router as feed_router
from app.features.notices.router import router as notices_router
from app.features.recommend.router import router as recommend_router
from app.features.subscriptions.router import router as subscriptions_router
from app.jobs import scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI):
    store.init()
    scheduler.start()
    yield
    scheduler.stop()


app = FastAPI(
    title="Team 11 국민대 공지 한 페이지 요약 API",
    version="0.2.0",
    description="형식 설명은 backend/README.md 「API 계약」",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (auth_router, notices_router, feed_router, briefing_router, recommend_router, subscriptions_router, admin_router):
    app.include_router(router, prefix="/api")


@app.get("/api/health", tags=["system"])
def health() -> dict:
    return {"ok": True}
