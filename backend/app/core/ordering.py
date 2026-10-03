"""공용 정렬 키. 같은 입력이면 같은 순서가 나와야 한다 (PRD 3절).

정렬 규칙 (사용자 지시 + 팀 QA, 2026-10-03):
**① 만료 안 된 것 → ② 올해 글 → ③ 관심 분야에 맞는 글 → ④ AI 추천도 → ⑤ 최신순.**
지난 마감·지난해 글이 위로 올라오고, 관심 분야 밖 글이 1위로 오던 문제를 코드로 막는다.
판단·줄 세우기는 전부 코드가 하고 AI 는 점수만 준다 (지침서 7절).
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
    """올해 글은 0, 지난해는 1, 그 전해는 2…

    게시일이 없는 고정 공지(학사공지에 여러 건 있다)는 마감이 아직 남아 있으면 지금 글로 본다.
    그렇지 않으면 맨 뒤 묶음 — 날짜를 모른다고 올해 글보다 위로 올리지는 않는다.
    """
    if n.posted_at is None:
        deadline = deadline_of(n)
        return 0 if deadline and deadline >= today else UNKNOWN_YEAR_TIER
    return max(0, min(UNKNOWN_YEAR_TIER - 1, today.year - n.posted_at.year))


def matches_interest(n: Notice, interests: set[str]) -> bool:
    """내가 고른 관심 분야(categories)에 이 공지가 들어가나."""
    return bool(interests) and bool(set(n.categories) & interests)


def fresh_first(n: Notice, today: date) -> tuple:
    """만료 여부 → 연도 묶음. 모든 정렬 앞에 붙이는 공통 머리."""
    return (is_expired(n, today), year_tier(n, today))


def by_recommend(today: date, interests: set[str] | None = None):
    """추천순: 만료 안 된 것 → 올해 글 → 관심 분야 일치 → AI 추천도 높은 순 → 최신순.

    관심 분야를 AI 추천도보다 앞에 둔다 (팀 QA 2026-10-03: 분야를 「행사」로 바꿔도 1위가
    취업 글이었다). 분야를 안 고른 사람에게는 이 단계가 없는 것과 같다.
    """
    chosen = interests or set()

    def key(n: Notice) -> tuple:
        priority = n.fit.priority if n.fit else -1
        return (*fresh_first(n, today), not matches_interest(n, chosen), -priority, *newest_first(n))

    return key


def by_deadline(today: date):
    """마감순: 만료 안 된 것 → 마감 가까운 순. 마감을 모르는 글과 지난 마감은 뒤에서 최신순."""
    far_future = date.max.toordinal()

    def key(n: Notice) -> tuple:
        deadline = deadline_of(n)
        return (is_expired(n, today), deadline.toordinal() if deadline else far_future, *newest_first(n))

    return key
