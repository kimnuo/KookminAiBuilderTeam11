"""커서 페이지네이션. 커서는 다음 페이지 시작 위치(문자열)다. 프론트는 값을 해석하지 말고 그대로 돌려준다."""

from app.core.config import PAGE_SIZE


def paginate(items: list, cursor: str | None) -> tuple[list, str | None]:
    start = int(cursor) if cursor and cursor.isdigit() else 0
    end = start + PAGE_SIZE
    return items[start:end], (str(end) if end < len(items) else None)
