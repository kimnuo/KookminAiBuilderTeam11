"""설정값과 고정 목록. 상수는 여기 한 곳에만 둔다 (지침서 4절)."""

import json
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]


def _load_env_file() -> None:
    """backend/.env 를 읽어 환경 변수로 넣는다 (이미 있는 값은 그대로 둔다). 키는 레포에 올리지 않는다."""
    path = BACKEND_DIR / ".env"
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


_load_env_file()

REPO_DIR = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / "data"  # .gitignore 됨
DB_PATH = Path(os.getenv("DB_PATH", DATA_DIR / "app.db"))
MOCK_NOTICES_PATH = REPO_DIR / "mock" / "live-notices.json"  # mock/notices.json 은 프론트 더미(?demo=1)

# 수집기가 학교 서버에 자기 이름을 밝힌다 (PRD 7절)
USER_AGENT = "KMU-Team11-NoticeBot/0.2 (K-Builder hackathon)"
REQUEST_TIMEOUT_SEC = 20
REQUEST_GAP_SEC = 1.0
POLL_INTERVAL_MIN = int(os.getenv("POLL_INTERVAL_MIN", "10"))
POLL_ON_STARTUP = os.getenv("POLL_ON_STARTUP", "0") == "1"
NEW_PER_SOURCE = int(os.getenv("NEW_PER_SOURCE", "8"))  # 한 번 돌 때 출처마다 새로 처리할 최대 글 수

# 첨부파일
ATTACHMENT_MAX_BYTES = 15 * 1024 * 1024
ATTACHMENT_MAX_CHARS = 12_000  # 파일 하나에서 AI 로 넘길 최대 글자 수
ATTACHMENTS_PER_NOTICE = 4

# AI (개발 중엔 이 서버의 Claude 구독 CLI. 배포 전 교체 — 05-제출/배포-전-확인-목록)
LLM_COMMAND = os.getenv("LLM_COMMAND", "claude")
LLM_MODEL = os.getenv("LLM_MODEL", "sonnet")
LLM_TIMEOUT_SEC = int(os.getenv("LLM_TIMEOUT_SEC", "180"))
LLM_CONCURRENCY = int(os.getenv("LLM_CONCURRENCY", "3"))
LLM_INPUT_MAX_CHARS = 30_000

# 학교 AI 게이트웨이. 변수 이름은 현찬의 ai/llm_gateway.py 와 맞춘다 (키는 backend/.env, 커밋 금지)
LLM_API_BASE = os.getenv("KMU_AI_BASE_URL", "https://ai.cs.kookmin.ac.kr").rstrip("/")
if not LLM_API_BASE.endswith("/v1"):
    LLM_API_BASE += "/v1"
LLM_API_KEY = os.getenv("KMU_AI_API_KEY", "")
LLM_API_MODEL = os.getenv("KMU_AI_MODEL", "claude-haiku-4-5")
RECOMMEND_BATCH = 8  # 한 번 호출에 넣는 공지 수
RECOMMEND_MAX = 40  # 한 요청에서 다룰 최대 공지 수

PAGE_SIZE = 20
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

KMU_BASE_URL = "https://www.kookmin.ac.kr"
SW_BASE_URL = "https://software.kookmin.ac.kr"
CS_BASE_URL = "https://cs.kookmin.ac.kr"

# 분류 (해서 확정 2026-10-03). 글 하나에 여러 개 붙을 수 있다
CATEGORIES = ["학사·생활", "졸업", "장학", "취업", "행사·대외활동", "기타"]

# 관심 분야 태그. 목록은 현찬의 app/ai/config/tags.json 한 곳에만 둔다 (지침서 4절)
TAGS = json.loads((BACKEND_DIR / "app" / "ai" / "config" / "tags.json").read_text(encoding="utf-8"))["tags"]
# 단과대학 이름으로 대상을 적은 공지를 학과와 맞추기 위한 표 (소융대 사이트 메뉴에서 확인)
MAJOR_GROUPS = {"소프트웨어융합대학": ["소프트웨어학부", "인공지능학부"]}
# 관심과 상관없이 「나의 상황」에 늘 넣는 분류
ALWAYS_RELEVANT_CATEGORIES = ["학사·생활", "졸업"]

# 수집 출처. defaultCategory 는 AI 처리 전 기본값이고 AI가 고친다
SOURCES = [
    {"id": "kmu-academic", "name": "학사공지", "group": "국민대 본부", "kind": "kmu_board",
     "board": 4, "defaultCategory": "학사·생활"},
    {"id": "sw-notice", "name": "공지사항", "group": "SW중심대학사업단", "kind": "sw_bulletin",
     "path": "/software/bulletin/notice.do", "defaultCategory": "행사·대외활동"},
    {"id": "cs-notice", "name": "SW 학사공지", "group": "소프트웨어융합대학", "kind": "cs_rss",
     "board": "notice", "defaultCategory": "학사·생활"},
    {"id": "cs-scholarship", "name": "SW 장학공지", "group": "소프트웨어융합대학", "kind": "cs_rss",
     "board": "scholarship", "defaultCategory": "장학"},
    {"id": "cs-jobs", "name": "SW 취업공지", "group": "소프트웨어융합대학", "kind": "cs_rss",
     "board": "jobs", "defaultCategory": "취업"},
    {"id": "cs-event", "name": "SW 특강 및 행사", "group": "소프트웨어융합대학", "kind": "cs_rss",
     "board": "event", "defaultCategory": "행사·대외활동"},
]


def source_list_url(source: dict) -> str:
    kind = source["kind"]
    if kind == "kmu_board":
        return f"{KMU_BASE_URL}/user/kmuNews/notice/{source['board']}/index.do"
    if kind == "sw_bulletin":
        return f"{SW_BASE_URL}{source['path']}?articleLimit=20"
    return f"{CS_BASE_URL}/news/{source['board']}/rss"


def find_source(source_id: str) -> dict | None:
    return next((s for s in SOURCES if s["id"] == source_id), None)
