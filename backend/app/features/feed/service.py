"""피드 개인 맞춤: 로그인한 사람의 구독 설정(나의 상황)으로 순서와 추천 이유를 붙인다.

- 순서와 이유는 **코드**가 정한다. 현찬의 `app/ai/recommend.py` 를 그대로 쓴다 (지침서 7절)
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
