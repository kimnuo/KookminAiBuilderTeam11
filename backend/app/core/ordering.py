"""공용 정렬 키. 같은 입력이면 같은 순서가 나와야 한다 (PRD 3절)."""

from app.core.schemas import Notice


def article_no(n: Notice) -> int:
    # id 끝자리가 글번호다 (kmu-4-12465, cs-2872)
    tail = n.id.rsplit("-", 1)[-1]
    return int(tail) if tail.isdigit() else 0


def newest_first(n: Notice) -> tuple:
    # 최신 날짜 먼저, 같은 날이면 글번호 큰 것 먼저, 날짜 없는 고정 공지는 맨 뒤
    posted = n.posted_at.toordinal() if n.posted_at else 0
    return (n.posted_at is None, -posted, -article_no(n), n.id)
