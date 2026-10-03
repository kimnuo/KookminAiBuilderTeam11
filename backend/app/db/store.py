"""공지 저장소 (SQLite, 파일 하나). 공지는 API 형식 그대로 JSON 으로 둔다.

- 요청마다 연결을 새로 열어 스레드 사이에 공유하지 않는다 (수집 스레드 + API 동시 사용)
- WAL 모드: 쓰는 중에도 읽기가 막히지 않는다
- body 는 AI 재처리용 본문·첨부 글이다. 학번은 가린 뒤 저장한다
"""

import sqlite3
from contextlib import closing

from app.core.config import DB_PATH
from app.core.schemas import Notice

_SCHEMA = """
CREATE TABLE IF NOT EXISTS notices (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    digest_status TEXT NOT NULL,
    data TEXT NOT NULL,
    body TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_notices_source ON notices(source_id);
"""


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init() -> None:
    with closing(_connect()) as conn, conn:
        conn.executescript(_SCHEMA)


def save(notice: Notice, body: str | None = None) -> None:
    data = notice.model_dump_json(by_alias=True)
    with closing(_connect()) as conn, conn:
        conn.execute(
            """INSERT INTO notices (id, source_id, digest_status, data, body) VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET digest_status=excluded.digest_status, data=excluded.data,
               body=COALESCE(excluded.body, notices.body), updated_at=datetime('now')""",
            (notice.id, notice.source.id, notice.digest.status, data, body),
        )


def get(notice_id: str) -> Notice | None:
    with closing(_connect()) as conn:
        row = conn.execute("SELECT data FROM notices WHERE id = ?", (notice_id,)).fetchone()
    return Notice.model_validate_json(row[0]) if row else None


def all_notices() -> list[Notice]:
    with closing(_connect()) as conn:
        rows = conn.execute("SELECT data FROM notices").fetchall()
    return [Notice.model_validate_json(r[0]) for r in rows]


def known_ids(source_id: str) -> set[str]:
    with closing(_connect()) as conn:
        rows = conn.execute("SELECT id FROM notices WHERE source_id = ?", (source_id,)).fetchall()
    return {r[0] for r in rows}


def pending_with_body(limit: int) -> list[tuple[Notice, str]]:
    """AI 처리가 아직이거나 실패한 글 (본문이 저장된 것만)."""
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT data, body FROM notices WHERE digest_status != 'done' AND body IS NOT NULL "
            "ORDER BY updated_at LIMIT ?", (limit,),
        ).fetchall()
    return [(Notice.model_validate_json(d), b) for d, b in rows]


def mark_all_for_redigest() -> int:
    """프롬프트를 바꿨을 때 전부 다시 요약하게 표시한다. 기존 요약은 새 결과가 나올 때까지 그대로 보인다."""
    with closing(_connect()) as conn, conn:
        return conn.execute("UPDATE notices SET digest_status = 'pending' WHERE body IS NOT NULL").rowcount


def counts() -> dict[str, int]:
    with closing(_connect()) as conn:
        rows = conn.execute("SELECT digest_status, COUNT(*) FROM notices GROUP BY 1").fetchall()
    return dict(rows)
