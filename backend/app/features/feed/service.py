"""피드 개인 맞춤: 로그인한 사람의 구독 설정(나의 상황)으로 순서와 추천 이유를 붙인다.

- 추천순은 **AI 가 본 추천도(priority)** 가 높은 순이다. 같으면 현찬의 `app/ai/recommend.py`
  코드 점수, 그다음 마감·게시일 순이다. 점수를 매기는 일만 AI 가 하고, 거르고 줄 세우는 것은 코드가 한다
- chance 는 (나의 상황 + 공지) 로 캐시해서, 같은 사람이 다시 열면 AI 를 부르지 않는다
- 구독 설정이 없으면(로그인 전) 최신순 그대로 둔다
"""

from app.ai.recommend import rank
from app.collectors.common import now_kst
from app.core.schemas import Notice, Subscription


def ai_view(notice: Notice) -> dict:
    """recommend.rank 가 보는 형태. 화면의 notice_view.dart 와 같은 digest → ai 변환이다."""
    digest = notice.digest
    return {
        "id": notice.id,
        "postedAt": notice.posted_at.isoformat() if notice.posted_at else None,
        "ai": {
            "categories": notice.categories,
            "tags": digest.tags,
            "deadline": digest.deadline.model_dump(by_alias=True, mode="json") if digest.deadline else None,
            "audience": digest.audience.model_dump(by_alias=True, mode="json") if digest.audience else None,
        },
    }


def personalize(notices: list[Notice], subscription: Subscription) -> list[Notice]:
    """추천 이유(코드) + 될 가능성(AI) 을 붙이고, 될 가능성이 높은 순으로 줄 세운다."""
    ordered = with_reasons(notices, subscription)
    fits = fits_for(ordered, subscription)
    for notice in ordered:
        notice.fit = fits.get(notice.id)
    ordered.sort(key=lambda n: -(n.fit.priority if n.fit else -1))
    return ordered


def fits_for(notices: list[Notice], subscription: Subscription) -> dict:
    from app.features.recommend.service import fits_of  # 순환 import 를 피해 여기서 부른다

    return fits_of(notices, subscription)


def with_reasons(notices: list[Notice], subscription: Subscription) -> list[Notice]:
    user = {
        "tags": subscription.tags,
        "categories": subscription.categories,
        "year": subscription.year,
        "major": subscription.major,
    }
    ranked = rank([ai_view(n) for n in notices], user, now_kst().date().isoformat())
    by_id = {n.id: n for n in notices}
    result = []
    for row in ranked:
        notice = by_id.get(row["id"])
        if notice is None:
            continue
        notice.recommendation_reasons = row["reasons"]
        result.append(notice)
    return result
