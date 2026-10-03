"""글 속 날짜 표기를 (연, 월, 일)로 읽는다 (결정적 코드, AI 아님).

title_deadline 과 마감일 근거 검사(enrich)가 같은 해석기를 쓴다.
읽는 표기: 2026.10.13 / 26.10.01 / 2026. 08. 25 / 2026년 9월 20일 / 9월 8일 / 10/15 / 10.12
          / 범위 끝의 일만 쓴 표기("~ 16.(금)", "~ 16일")는 앞 날짜의 연·월을 물려받는다.
범위("A ~ B")의 앞 날짜는 is_range_start=True 로 표시한다. 마감은 범위의 끝이다.
"""
import re
import unicodedata
from dataclasses import dataclass
from datetime import date

# 연·월·일 구분자는 같아야 한다. 다르면 "09.01 - 09.22"(포스터의 9/1~9/22)가 2009-01-09 로 읽힌다.
_FULL = re.compile(r"(?<![0-9])([0-9]{4}|[0-9]{2})\s*([./-])\s*([0-9]{1,2})\s*\2\s*([0-9]{1,2})(?![0-9])")
_KOR = re.compile(r"(?:([0-9]{4})\s*년\s*)?([0-9]{1,2})\s*월\s*([0-9]{1,2})\s*일")
_MD = re.compile(r"(?<![0-9.])([0-9]{1,2})\s*[./]\s*([0-9]{1,2})(?![0-9])(?!\s*(?:배|%|점|만점|명|원|개|시간|학점|kg|km))")
_DAY = re.compile(r"~\s*([0-9]{1,2})\s*(?:\.|일)")
_GAP_RANGE = re.compile(r"^[\s.)(월화수목금토일0-9:]*~")   # 두 날짜 사이가 요일·시각·~ 뿐이면 범위


@dataclass
class DateToken:
    year: int | None
    month: int
    day: int
    start: int
    end: int
    is_range_start: bool = False


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    return text.replace("〜", "~").replace("∼", "~")


def _mask(text: str, spans) -> str:
    chars = list(text)
    for s, e in spans:
        chars[s:e] = "#" * (e - s)
    return "".join(chars)


def _year(raw: str | None) -> int | None:
    if not raw:
        return None
    y = int(raw)
    return 2000 + y if y < 100 else y


def find_dates(text: str) -> list[DateToken]:
    """날짜 표기를 위치 순으로 돌려준다. 달력에 없는 날짜(13월 등)는 뺀다."""
    s = normalize(text)
    toks: list[DateToken] = []
    for pat, kind in ((_FULL, "ymd"), (_KOR, "kor"), (_MD, "md")):
        masked = _mask(s, [(t.start, t.end) for t in toks])
        for m in pat.finditer(masked):
            g = m.groups()
            if kind == "md":
                y, mo, d = None, int(g[0]), int(g[1])
            elif kind == "ymd":
                y, mo, d = _year(g[0]), int(g[2]), int(g[3])   # g[1] 은 구분자
            else:
                y, mo, d = _year(g[0]), int(g[1]), int(g[2])
            toks.append(DateToken(y, mo, d, m.start(), m.end()))
    toks.sort(key=lambda t: t.start)
    masked = _mask(s, [(t.start, t.end) for t in toks])
    for m in _DAY.finditer(masked):
        prev = [t for t in toks if t.end <= m.start()]
        if prev:
            p = prev[-1]
            toks.append(DateToken(p.year, p.month, int(m.group(1)), m.start(1), m.end(1)))
    toks.sort(key=lambda t: t.start)
    toks = [t for t in toks if _valid(t)]
    for a, b in zip(toks, toks[1:]):
        if _GAP_RANGE.match(s[a.end:b.start]):
            a.is_range_start = True
    return toks


def _valid(t: DateToken) -> bool:
    try:
        date(t.year or 2024, t.month, t.day)   # 2024 는 윤년이라 2/29 를 막지 않는다
        return True
    except ValueError:
        return False


def resolve(t: DateToken, posted: date | None) -> date | None:
    """연도가 없으면 게시일 연도로 보고, 게시일보다 30일 넘게 앞서면 다음 해로 본다."""
    if t.year:
        try:
            return date(t.year, t.month, t.day)
        except ValueError:
            return None
    if posted is None:
        return None
    for y in (posted.year, posted.year + 1):
        try:
            d = date(y, t.month, t.day)
        except ValueError:
            continue
        if (posted - d).days <= 30:
            return d
    return None


def parse_posted(posted_at) -> date | None:
    try:
        return date.fromisoformat(str(posted_at or "")[:10])
    except ValueError:
        return None
