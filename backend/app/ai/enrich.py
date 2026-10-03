"""공지 한 건을 LLM 으로 분류·요약·마감 추출한다 (PRD 3절, 10절 ai 객체).

판단 규칙은 코드가 쥔다.
- LLM 출력은 JSON 스키마로 검사하고, 틀리거나 호출이 예외를 던지면 1회 다시 부른다. 그래도 안 되면 status="failed".
- 목록 밖 분야·태그는 버리고, 중복·빈 값은 정리하고, 넘치는 건 자른다.
- 마감일: 달력에 있는 날짜여야 하고, 근거(evidence)가 원문에 글자 그대로 있어야 하고,
  근거 안의 날짜 표기(범위면 끝 날짜)가 LLM 날짜와 같아야 한다. 시각도 근거 안에 있어야 한다.
  근거가 버려지거나 LLM 이 null 을 내면 제목 표기(title_deadline)로 대신한다.
  제목 규칙은 괄호 끝·까지·마감이 붙은 표기만 잡는다("~2.5배", 행사 범위는 안 잡는다).

입력 notice: PRD 10절 Notice(id, source, title, postedAt) + body(본문 텍스트) + posterText(선택, poster.py 가 읽은 글).
body, posterText, deadline.source(ai|poster|title) 는 PRD 10절에 없는 필드라 백엔드와 맞춰야 한다.
llm 은 prompt(str) -> str 함수다 (llm_claude.make_claude_llm 또는 llm_bedrock.make_bedrock_llm).
"""
import json
import re
from datetime import date, time
from pathlib import Path

from jsonschema import Draft202012Validator

from app.ai import cleaning
from app.ai.dates import find_dates, normalize, parse_posted, resolve
from app.ai.text import is_short_body, title_deadline

AI_DIR = Path(__file__).parent
_CAT = json.loads((AI_DIR / "config" / "categories.json").read_text(encoding="utf-8"))
CATEGORIES = _CAT["categories"]
BOARD_DEFAULT = _CAT["boardDefault"]
TAGS = json.loads((AI_DIR / "config" / "tags.json").read_text(encoding="utf-8"))["tags"]
PROMPT = (AI_DIR / "prompts" / "enrich.md").read_text(encoding="utf-8")
VALIDATOR = Draft202012Validator(
    json.loads((AI_DIR / "schemas" / "notice_ai.schema.json").read_text(encoding="utf-8")))
MAX_BODY_CHARS = 6000
_ASCII_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_ASCII_TIME = re.compile(r"[0-9]{2}:[0-9]{2}")


def build_prompt(notice: dict) -> str:
    body = (notice.get("body") or "").strip()
    poster = (notice.get("posterText") or "").strip()
    if poster:
        body = (body + "\n\n[포스터 이미지에서 읽은 글자 (AI 판독, 오탈자가 있을 수 있음)]\n" + poster).strip()
    elif is_short_body(body):
        body = (body + "\n(본문이 거의 없음. 포스터 이미지 공지일 수 있음)").strip()
    values = {
        "board": notice.get("board") or (notice.get("source") or {}).get("name") or "",
        "posted_at": str(notice.get("postedAt") or ""),
        "title": notice.get("title") or "",
        "body": body[:MAX_BODY_CHARS],
        "categories": ", ".join(CATEGORIES),
        "tags": ", ".join(TAGS),
    }
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values.get(m.group(1), m.group(0)), PROMPT)


def parse_json(raw: str):
    """LLM 응답에서 처음 나오는 JSON 객체 하나를 꺼낸다. 실패하면 None."""
    if not raw:
        return None
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", raw):
        try:
            data, _ = dec.raw_decode(raw[m.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    return None


def _squash(s: str) -> str:
    return re.sub(r"\s+", "", normalize(s or "")).replace("​", "").replace("﻿", "")


def board_id(notice: dict) -> str:
    """boardId 가 없으면 id("kmu-4-12465")에서 게시판 번호를 뽑는다 (PRD 10절 Notice 에는 boardId 가 없다)."""
    if notice.get("boardId"):
        return str(notice["boardId"])
    m = re.match(r"kmu-(\d+)-", notice.get("id") or "")
    return m.group(1) if m else ""


def _default_category(notice: dict) -> str:
    return BOARD_DEFAULT.get(board_id(notice), "기타")


def _evidence_supports(dl: dict, text: str, posted: date | None = None) -> bool:
    """근거가 원문(squash 한 글)에 있고, 근거 속 날짜(범위면 끝)가 dl["date"] 와 같아야 한다."""
    ev = dl.get("evidence") or ""
    if len(_squash(ev)) < 4 or _squash(ev) not in text:
        return False
    target = date.fromisoformat(dl["date"])
    for t in find_dates(ev):
        if t.is_range_start:
            continue
        if t.year is None and posted is None:
            if (t.month, t.day) == (target.month, target.day):
                return True
        elif resolve(t, posted) == target:
            return True
    return False


def _valid_deadline(dl) -> dict | None:
    """키를 걸러 내고, 달력·시계에 있는 ASCII 값인지 본다."""
    if not isinstance(dl, dict) or not isinstance(dl.get("date"), str):
        return None
    out = {k: dl.get(k) for k in ("date", "time", "evidence")}
    try:
        if not _ASCII_DATE.fullmatch(out["date"]):
            return None
        date.fromisoformat(out["date"])
    except ValueError:
        return None
    t = out["time"]
    try:
        ok_time = isinstance(t, str) and _ASCII_TIME.fullmatch(t) and time.fromisoformat(t)
    except ValueError:
        ok_time = False
    if not ok_time:
        out["time"] = None   # 시각만 틀리면 시각만 버리고 날짜는 남긴다
    return out


def _time_in_evidence(dl: dict) -> dict:
    if dl["time"]:
        hh, mm = dl["time"].split(":")
        if not re.search(rf"(?<![0-9]){int(hh)}:{mm}(?![0-9])", normalize(dl["evidence"] or "")):
            dl = {**dl, "time": None}
    return dl


def _deadline(ai_deadline, notice: dict):
    text = _squash(notice.get("title")) + "¶" + _squash(notice.get("body"))
    posted = parse_posted(notice.get("postedAt"))
    dl = _valid_deadline(ai_deadline)
    if dl and _evidence_supports(dl, text, posted):
        return {**_time_in_evidence(dl), "source": "ai"}
    if dl and notice.get("posterText") and _evidence_supports(dl, _squash(notice["posterText"]), posted):
        return {**_time_in_evidence(dl), "source": "poster"}   # 근거가 AI 가 읽은 포스터 글에만 있다
    fallback = title_deadline(notice.get("title") or "", notice.get("postedAt"))
    return {**fallback, "source": "title"} if fallback else None


def clean(data: dict, notice: dict) -> dict:
    return {
        "status": "done",
        "categories": cleaning.pick(data.get("categories"), CATEGORIES) or [_default_category(notice)],
        "tags": cleaning.pick(data.get("tags"), TAGS),
        "summary": cleaning.summary(data.get("summary")),
        "deadline": _deadline(data.get("deadline"), notice),
        "audience": cleaning.audience(data.get("audience")),
        "apply": cleaning.text_or_none(data.get("apply")),
    }


def failed(notice: dict) -> dict:
    return {
        "status": "failed",
        "categories": [_default_category(notice)],
        "tags": [],
        "summary": None,
        "deadline": _deadline(None, notice),
        "audience": None,
        "apply": None,
    }


def enrich(notice: dict, llm, retries: int = 1) -> dict:
    prompt = build_prompt(notice)
    for _ in range(1 + retries):
        try:
            data = parse_json(llm(prompt))
        except Exception:   # 네트워크·한도 초과 등은 실패 1회로 센다
            data = None
        if data is not None and not any(VALIDATOR.iter_errors(data)):
            return clean(data, notice)
    return failed(notice)
