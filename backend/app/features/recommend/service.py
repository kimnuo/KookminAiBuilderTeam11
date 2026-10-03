"""추천 적합도: 학생 상황 + 공지 → 될 가능성(chance) 과 근거 한 줄(reason).

- AI 는 해석만 한다. 어떤 글을 보여 줄지·어떤 순서로 둘지는 화면과 코드가 정한다 (지침서 7절)
- 같은 상황·같은 글이면 다시 부르지 않는다 (DB 에 캐시)
- 상황 정보는 저장하지 않는다. 캐시에는 상황을 해시로만 남긴다
"""

import hashlib
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.ai.gateway import complete_json
from app.ai.recommend import rank
from app.ai.llm import LlmError
from app.core.config import LLM_API_MODEL, LLM_CONCURRENCY, RECOMMEND_BATCH, RECOMMEND_MAX
from app.collectors.common import now_kst
from app.core.schemas import Fit, Notice, RecommendRequest, Recommendation, RecommendResponse
from app.db import store

log = logging.getLogger(__name__)
SYSTEM_PROMPT = (
    Path(__file__).resolve().parents[2] / "ai" / "prompts" / "recommend_system.md"
).read_text(encoding="utf-8")

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "noticeId": {"type": "string"},
                    "chance": {"type": "integer", "minimum": 0, "maximum": 100},
                    "reason": {"type": "string"},
                },
                "required": ["noticeId", "chance", "reason"],
            },
        }
    },
    "required": ["items"],
}


def cache_key(request: RecommendRequest, notice: Notice) -> str:
    situation = request.situation.model_dump_json(by_alias=True)
    seed = f"{LLM_API_MODEL}|{situation}|{sorted(request.tags)}|{notice.id}|{notice.digest.title}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def notice_brief(notice: Notice) -> dict:
    digest = notice.digest
    return {
        "noticeId": notice.id,
        "title": digest.title or notice.original_title,
        "categories": notice.categories,
        "summary": digest.summary,
        "audience": digest.audience.text if digest.audience else None,
        "requirements": [item.text for item in digest.requirements[:4]],
        "deadline": digest.deadline.date.isoformat() if digest.deadline else None,
    }


def build_input(request: RecommendRequest, notices: list[Notice]) -> str:
    situation = request.situation.model_dump(by_alias=True, mode="json")
    situation["tags"] = request.tags
    return json.dumps(
        {"student": situation, "notices": [notice_brief(n) for n in notices]},
        ensure_ascii=False,
    )


def ask(request: RecommendRequest, notices: list[Notice]) -> list[dict]:
    try:
        raw = complete_json(SYSTEM_PROMPT, build_input(request, notices), ANSWER_SCHEMA)
    except LlmError as exc:
        log.warning("추천 적합도 실패 (%d건): %s", len(notices), exc)
        return []
    items = raw.get("items")
    return items if isinstance(items, list) else []


def clean(item: dict, known: dict[str, Notice]) -> Recommendation | None:
    notice_id = item.get("noticeId")
    reason = str(item.get("reason") or "").strip().replace("\n", " ")
    if notice_id not in known or not reason:
        return None
    try:
        chance = int(item.get("chance"))
    except (TypeError, ValueError):
        return None
    return Recommendation(notice_id=notice_id, chance=max(0, min(100, chance)), reason=reason[:60])


def recommend(request: RecommendRequest) -> RecommendResponse:
    wanted = request.notice_ids[:RECOMMEND_MAX]
    done = {n.id: n for n in store.all_notices() if n.digest.status == "done"}
    notices = [done[i] for i in wanted if i in done] if wanted else list(done.values())[:RECOMMEND_MAX]
    keys = {n.id: cache_key(request, n) for n in notices}
    cached = store.cached_recommendations(list(keys.values()))
    found = {
        n.id: Recommendation(notice_id=n.id, chance=cached[keys[n.id]][0], reason=cached[keys[n.id]][1])
        for n in notices
        if keys[n.id] in cached
    }
    missing = [n for n in notices if n.id not in found]
    for item in _ask_all(request, missing):
        found[item.notice_id] = item
    store.save_recommendations(
        [(keys[i.notice_id], i.notice_id, i.chance, i.reason) for i in found.values() if i.notice_id in keys]
    )
    items = [found[n.id] for n in notices if n.id in found]
    return RecommendResponse(model=LLM_API_MODEL, items=add_code_score(request, notices, items))


def ai_view(notice: Notice) -> dict:
    """현찬의 app/ai/recommend.py 가 보는 형태(ai 칸)로 맞춘다. 화면의 notice_view.dart 와 같은 변환."""
    digest = notice.digest
    return {
        "id": notice.id,
        "postedAt": notice.posted_at,
        "ai": {
            "categories": notice.categories,
            "tags": digest.tags,
            "deadline": digest.deadline.model_dump(by_alias=True, mode="json") if digest.deadline else None,
            "audience": digest.audience.model_dump(by_alias=True, mode="json") if digest.audience else None,
        },
    }


def add_code_score(
    request: RecommendRequest, notices: list[Notice], items: list[Recommendation]
) -> list[Recommendation]:
    """순서·점수는 코드가 매긴다 (지침서 7절). AI 는 될 가능성과 근거 한 줄만 본다."""
    user = {
        "tags": request.tags,
        "categories": request.situation.interests,
        "year": request.situation.year,
        "major": request.situation.major,
    }
    ranked = {r["id"]: r for r in rank([ai_view(n) for n in notices], user, now_kst().date().isoformat())}
    for item in items:
        scored = ranked.get(item.notice_id)
        if scored:
            item.score = scored["score"]
            item.reasons = scored["reasons"]
    return items


def _ask_all(request: RecommendRequest, missing: list[Notice]) -> list[Recommendation]:
    if not missing:
        return []
    known = {n.id: n for n in missing}
    chunks = [missing[i : i + RECOMMEND_BATCH] for i in range(0, len(missing), RECOMMEND_BATCH)]
    with ThreadPoolExecutor(max_workers=LLM_CONCURRENCY, thread_name_prefix="recommend") as pool:
        results = list(pool.map(lambda chunk: ask(request, chunk), chunks))
    cleaned = [clean(item, known) for batch in results for item in batch]
    return [item for item in cleaned if item]


def fit_of(notice_id: str, request: RecommendRequest) -> Fit | None:
    """공지 하나의 될 가능성. 상세 화면에서 쓴다 (캐시에 있으면 AI 를 부르지 않는다)."""
    answer = recommend(request.model_copy(update={"notice_ids": [notice_id]}))
    item = answer.items[0] if answer.items else None
    return Fit(chance=item.chance, reason=item.reason) if item else None
