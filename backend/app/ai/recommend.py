"""공지 추천 순서를 코드로 매긴다 (PRD 6-1절 「추천 순서 (코드)」). AI 호출 없음.

점수 = 겹치는 태그 수 x tag + 관심 분야 일치(category, 한 번만) + 대상 학년 일치(yearMatch)
      + 대상 전공 일치(majorMatch). 가중치와 이유 문구는 config/recommend.json 에 있다.

- 마감(deadline.date)이 today 보다 앞이면 뺀다. deadline 이 없거나 날짜를 못 읽으면 남긴다.
- 대상 학년이 적혀 있는데 내 학년이 없으면 빼지 않고 yearMismatch(음수)를 더해 맨 아래로 보낸다.
  학년 값은 AI 가 원문에서 뽑은 것이라 틀릴 수 있고(학기를 학년으로 읽는 등), 빼면 사용자가 그 글을 못 본다.
- 전공은 AI 가 뽑은 자유 문구라 글자 비교가 자주 빗나간다. 일치할 때만 더하고 불일치는 깎지 않는다.
- 내 학년·전공을 모르면(null) 학년·전공 점수는 0 이다.
- 정렬: 점수 높은 순 > 마감 임박 순(날짜, 시각. 없으면 뒤) > 게시일 최신 순 > id.
  마지막에 id 를 넣어 입력 순서가 달라도 같은 결과가 나온다.
- ai 가 null 이거나 pending·failed 여도 있는 값만 쓴다. failed 의 분야(게시판 기본값)와
  마감(제목 규칙)은 코드가 정한 값이라 그대로 쓴다.
"""
import json
import re
from datetime import date
from pathlib import Path

_CFG = json.loads((Path(__file__).parent / "config" / "recommend.json").read_text(encoding="utf-8"))
WEIGHTS = _CFG["weights"]
REASONS = _CFG["reasons"]
NO_TIME = "99:99"  # 마감 시각이 없으면 같은 날 시각이 있는 글 뒤로


def _parse_date(value):
    """'YYYY-MM-DD'(뒤에 시각이 붙어도 됨)를 date 로. 형식이 틀리면 None."""
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _as_int(value):
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _strs(values) -> list:
    """목록에서 문자열만 순서대로, 중복 없이."""
    if not isinstance(values, list):
        return []
    return list(dict.fromkeys(v for v in values if isinstance(v, str) and v))


def _norm(text) -> str:
    return re.sub(r"\s+", "", text) if isinstance(text, str) else ""


def _josa_wa(word: str) -> str:
    """받침이 있으면 '과', 없으면 '와'. 마지막 글자가 한글이 아니면 '와'로 둔다."""
    last = word[-1] if word else ""
    if "가" <= last <= "힣":
        return "과" if (ord(last) - ord("가")) % 28 else "와"
    return "와"


def _quote(names: list) -> str:
    return ", ".join(f"「{n}」" for n in names)


def _ai(notice: dict) -> dict:
    ai = notice.get("ai")
    return ai if isinstance(ai, dict) else {}


def _deadline(ai: dict) -> dict:
    dl = ai.get("deadline")
    return dl if isinstance(dl, dict) else {}


def _is_expired(notice: dict, today: date) -> bool:
    d = _parse_date(_deadline(_ai(notice)).get("date"))
    return d is not None and d < today


def _tag_part(ai: dict, user: dict):
    mine = set(_strs(user.get("tags")))
    hit = [t for t in _strs(ai.get("tags")) if t in mine]
    if not hit:
        return 0, []
    reason = REASONS["tags"].format(names=_quote(hit), josa=_josa_wa(hit[-1]))
    return len(hit) * WEIGHTS["tag"], [reason]


def _category_part(ai: dict, user: dict):
    mine = set(_strs(user.get("categories")))
    hit = [c for c in _strs(ai.get("categories")) if c in mine]
    if not hit:
        return 0, []
    return WEIGHTS["category"], [REASONS["categories"].format(names=_quote(hit))]


def _year_part(audience: dict, user: dict):
    raw = audience.get("years") if isinstance(audience.get("years"), list) else []
    years = sorted({y for y in map(_as_int, raw) if y is not None})
    mine = _as_int(user.get("year"))
    if not years or mine is None:
        return 0, []
    if mine in years:
        return WEIGHTS["yearMatch"], [REASONS["yearMatch"].format(year=mine)]
    label = "·".join(str(y) for y in years)
    return WEIGHTS["yearMismatch"], [REASONS["yearMismatch"].format(years=label)]


def _major_part(audience: dict, user: dict):
    mine = _norm(user.get("major"))
    if not mine:
        return 0, []
    for major in _strs(audience.get("majors")):
        theirs = _norm(major)
        if theirs and (theirs in mine or mine in theirs):
            return WEIGHTS["majorMatch"], [REASONS["majorMatch"].format(major=user["major"].strip())]
    return 0, []


def score_notice(notice: dict, user: dict):
    """공지 한 건의 (점수, 이유 목록). 이유 순서: 태그, 분야, 학년, 전공."""
    ai = _ai(notice)
    audience = ai.get("audience") if isinstance(ai.get("audience"), dict) else {}
    parts = [_tag_part(ai, user), _category_part(ai, user),
             _year_part(audience, user), _major_part(audience, user)]
    return sum(p[0] for p in parts), [r for p in parts for r in p[1]]


def _sort_key(entry):
    notice, score, _ = entry
    dl = _deadline(_ai(notice))
    d = _parse_date(dl.get("date"))
    time = dl.get("time") if isinstance(dl.get("time"), str) else NO_TIME
    deadline = (0, d.toordinal(), time) if d else (1, 0, "")
    posted = _parse_date(notice.get("postedAt"))
    return (-score, deadline, -posted.toordinal() if posted else 0, str(notice.get("id")))


def rank(notices: list, user: dict, today: str) -> list:
    """추천 순서로 [{id, score, reasons}]. today 는 한국 시간 기준 'YYYY-MM-DD'."""
    today_d = date.fromisoformat(today)
    user = user or {}
    entries = [(n, *score_notice(n, user)) for n in notices if not _is_expired(n, today_d)]
    entries.sort(key=_sort_key)
    return [{"id": n.get("id"), "score": s, "reasons": r} for n, s, r in entries]
