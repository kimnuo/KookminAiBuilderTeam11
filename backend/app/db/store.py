"""공지 저장소 (SQLite, 파일 하나). 공지는 API 형식 그대로 JSON 으로 둔다.

- 요청마다 연결을 새로 열어 스레드 사이에 공유하지 않는다 (수집 스레드 + API 동시 사용)
- WAL 모드: 쓰는 중에도 읽기가 막히지 않는다
- body 는 AI 재처리용 본문·첨부 글이다. 학번은 가린 뒤 저장한다
"""

import json
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

CREATE TABLE IF NOT EXISTS subscriptions (
    user_id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS requirements (
    notice_id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    nickname TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS consents (
    user_id TEXT NOT NULL,
    type TEXT NOT NULL,
    version TEXT NOT NULL,
    agreed_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (user_id, type)
);

CREATE TABLE IF NOT EXISTS recommendations (
    cache_key TEXT PRIMARY KEY,
    notice_id TEXT NOT NULL,
    chance INTEGER NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
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


def cached_recommendations(keys: list[str]) -> dict[str, tuple[int, str]]:
    """같은 상황·같은 글이면 AI 를 다시 부르지 않는다 (지침서 7절)."""
    if not keys:
        return {}
    marks = ",".join("?" * len(keys))
    with closing(_connect()) as conn:
        rows = conn.execute(
            f"SELECT cache_key, chance, reason FROM recommendations WHERE cache_key IN ({marks})",
            keys,
        ).fetchall()
    return {k: (c, r) for k, c, r in rows}


def save_recommendations(rows: list[tuple[str, str, int, str]]) -> None:
    with closing(_connect()) as conn, conn:
        conn.executemany(
            "INSERT INTO recommendations (cache_key, notice_id, chance, reason) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(cache_key) DO UPDATE SET chance=excluded.chance, reason=excluded.reason",
            rows,
        )


def create_user(user_id: str, nickname: str, password_hash: str) -> bool:
    """닉네임이 이미 있으면 False. 비밀번호는 해시만 들어온다."""
    with closing(_connect()) as conn, conn:
        try:
            conn.execute(
                "INSERT INTO users (id, nickname, password_hash) VALUES (?, ?, ?)",
                (user_id, nickname, password_hash),
            )
        except sqlite3.IntegrityError:
            return False
    return True


def find_user(nickname: str) -> tuple[str, str] | None:
    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT id, password_hash FROM users WHERE nickname = ?", (nickname,)
        ).fetchone()
    return (row[0], row[1]) if row else None


def save_session(token: str, user_id: str) -> None:
    with closing(_connect()) as conn, conn:
        conn.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))


def session_user(token: str) -> str | None:
    with closing(_connect()) as conn:
        row = conn.execute("SELECT user_id FROM sessions WHERE token = ?", (token,)).fetchone()
    return row[0] if row else None


def drop_session(token: str) -> None:
    with closing(_connect()) as conn, conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))


def delete_user(user_id: str) -> None:
    """탈퇴: 계정·세션·동의 기록을 모두 지운다."""
    with closing(_connect()) as conn, conn:
        conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM consents WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))


def save_consent(user_id: str, kind: str, version: str) -> None:
    with closing(_connect()) as conn, conn:
        conn.execute(
            "INSERT INTO consents (user_id, type, version) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id, type) DO UPDATE SET version=excluded.version, "
            "agreed_at=datetime('now')",
            (user_id, kind, version),
        )


def body_of(notice_id: str) -> str | None:
    with closing(_connect()) as conn:
        row = conn.execute("SELECT body FROM notices WHERE id = ?", (notice_id,)).fetchone()
    return row[0] if row else None


def get_requirements(notice_id: str) -> dict | None:
    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT data FROM requirements WHERE notice_id = ?", (notice_id,)
        ).fetchone()
    return json.loads(row[0]) if row else None


def save_requirements(notice_id: str, data: dict) -> None:
    with closing(_connect()) as conn, conn:
        conn.execute(
            "INSERT INTO requirements (notice_id, data) VALUES (?, ?) "
            "ON CONFLICT(notice_id) DO UPDATE SET data=excluded.data",
            (notice_id, json.dumps(data, ensure_ascii=False)),
        )


def save_subscription(user_id: str, data: str) -> None:
    with closing(_connect()) as conn, conn:
        conn.execute(
            "INSERT INTO subscriptions (user_id, data) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET data=excluded.data, updated_at=datetime('now')",
            (user_id, data),
        )


def get_subscription(user_id: str) -> str | None:
    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT data FROM subscriptions WHERE user_id = ?", (user_id,)
        ).fetchone()
    return row[0] if row else None
