"""설정값과 고정 목록. 상수는 여기 한 곳에만 둔다 (지침서 4절)."""

import json
import os
import re
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
RECOMMEND_MAX = 80  # 한 요청에서 다룰 최대 공지 수
FEED_FIT_LIMIT = 80  # 피드에서 AI 적합도를 매길 상위 글 수 (나머지는 코드 순서 그대로 뒤에)

PAGE_SIZE = 20
# 쉼표로 여러 개. 공백을 지우고 빈 칸은 버린다 ("a, b" 의 b 가 안 맞던 문제, 팀 리뷰 11번)
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()] or ["*"]

# 관리자 전용 엔드포인트(/api/admin/poll-now, /redigest) 열쇠. backend/.env 의 ADMIN_TOKEN.
# 비어 있으면 그 두 엔드포인트는 503 으로 막힌다 (외부 공개 시 무인증 노출을 막기 위해 기본은 잠김).
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "").strip()

KMU_BASE_URL = "https://www.kookmin.ac.kr"
SW_BASE_URL = "https://software.kookmin.ac.kr"
CS_BASE_URL = "https://cs.kookmin.ac.kr"

# 교외 채용·대외활동 사이트 (공개 API). 조사 결과는 02-아이디에이션/백엔드-요구사항.md
JASOSEOL_BASE_URL = "https://jasoseol.com"
JASOSEOL_MAX_PAGES = 3  # per_page=100, 진행 중 공고가 300건 안팎이다
# 소프트웨어·AI·하드웨어 직무 코드 (GET /api/v1/duty-groups)
JASOSEOL_DUTY_IDS = set(range(160, 183)) | {219, 220, 221, 222, 224}
JASOSEOL_UNDERGRAD = {
    "모두 지원 가능", "대학생 전체", "3학년 1학기", "3학년 2학기", "4학년 1학기", "마지막 학기",
}

JASOSEOL_BROAD_DUTIES = 15  # 직무를 이보다 많이 적은 공고(대기업 공채)는 글자로 한 번 더 본다

INTHISWORK_BASE_URL = "https://inthiswork.com"
INTHISWORK_CLOSED_CATEGORY = 191700169  # ▶마감/비공개
# IT개발, 데이터분석, 전기전자, 반도체, 게임, PM·서비스기획
INTHISWORK_TAGS = [191700187, 191700191, 191700281, 191700312, 191700302, 191700271]
TECH_RE = re.compile(
    r"개발|소프트웨어|SW|백엔드|프론트|서버|앱|웹|임베디드|펌웨어|하드웨어|반도체|회로|제어"
    r"|AI|인공지능|머신러닝|딥러닝|LLM|데이터|클라우드|보안|전산|코딩|해커톤|알고리즘",
    re.IGNORECASE,
)

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
    {"id": "jasoseol", "name": "신입 채용", "group": "자소설닷컴", "kind": "jasoseol",
     "defaultCategory": "취업"},
    {"id": "itw-job", "name": "신입·인턴 채용", "group": "인디스워크", "kind": "inthiswork",
     "category": 191700167, "tagFilter": True, "defaultCategory": "취업"},
    {"id": "itw-activity", "name": "교육·대외활동", "group": "인디스워크", "kind": "inthiswork",
     "category": 191700345, "defaultCategory": "행사·대외활동"},
]


def source_list_url(source: dict) -> str:
    kind = source["kind"]
    if kind == "kmu_board":
        return f"{KMU_BASE_URL}/user/kmuNews/notice/{source['board']}/index.do"
    if kind == "sw_bulletin":
        return f"{SW_BASE_URL}{source['path']}?articleLimit=20"
    if kind == "jasoseol":
        return f"{JASOSEOL_BASE_URL}/recruit"
    if kind == "inthiswork":
        return f"{INTHISWORK_BASE_URL}/?cat={source['category']}"
    return f"{CS_BASE_URL}/news/{source['board']}/rss"


def find_source(source_id: str) -> dict | None:
    return next((s for s in SOURCES if s["id"] == source_id), None)
