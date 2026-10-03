"""공용 정렬 키. 같은 입력이면 같은 순서가 나와야 한다 (PRD 3절).

정렬 규칙 (사용자 지시, 2026-10-03): **① 만료 안 된 것 먼저, ② 올해 글 먼저**, 그다음 기존 기준.
지난 마감·지난해 글이 위로 올라오던 문제를 코드로 막는다. 판단은 전부 코드가 하고 AI 는 점수만 준다.
"""

from datetime import date

from app.core.schemas import Notice

# 날짜를 모르는 글(고정 공지 등)이 올해 글보다 위로 가지 않게 쓰는 값
UNKNOWN_YEAR_TIER = 99


def article_no(n: Notice) -> int:
    # id 끝자리가 글번호다 (kmu-4-12465, cs-2872)
    tail = n.id.rsplit("-", 1)[-1]
    return int(tail) if tail.isdigit() else 0


def newest_first(n: Notice) -> tuple:
    # 최신 날짜 먼저, 같은 날이면 글번호 큰 것 먼저, 날짜 없는 고정 공지는 맨 뒤
    posted = n.posted_at.toordinal() if n.posted_at else 0
    return (n.posted_at is None, -posted, -article_no(n), n.id)


def deadline_of(n: Notice) -> date | None:
    return n.digest.deadline.date if n.digest and n.digest.deadline else None


def is_expired(n: Notice, today: date) -> bool:
    """마감일이 오늘보다 앞이면 만료. 마감을 모르는 글은 만료로 보지 않는다 (상시 모집일 수 있다)."""
    deadline = deadline_of(n)
    return deadline is not None and deadline < today


def year_tier(n: Notice, today: date) -> int:
    """올해 글은 0, 지난해는 1, 그 전해는 2… 날짜를 모르면 맨 뒤 묶음."""
    if n.posted_at is None:
        return UNKNOWN_YEAR_TIER
    return max(0, min(UNKNOWN_YEAR_TIER - 1, today.year - n.posted_at.year))


def fresh_first(n: Notice, today: date) -> tuple:
    """만료 여부 → 연도 묶음. 모든 정렬 앞에 붙이는 공통 머리."""
    return (is_expired(n, today), year_tier(n, today))


def by_recommend(today: date):
    """추천순: 만료 안 된 것 → 올해 글 → AI 추천도 높은 순 → 최신순."""

    def key(n: Notice) -> tuple:
        priority = n.fit.priority if n.fit else -1
        return (*fresh_first(n, today), -priority, *newest_first(n))

    return key


def by_deadline(today: date):
    """마감순: 만료 안 된 것 → 마감 가까운 순. 마감을 모르는 글과 지난 마감은 뒤에서 최신순."""
    far_future = date.max.toordinal()

    def key(n: Notice) -> tuple:
        deadline = deadline_of(n)
        return (is_expired(n, today), deadline.toordinal() if deadline else far_future, *newest_first(n))

    return key
