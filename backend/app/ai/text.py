"""공지 본문 텍스트 처리 (결정적 코드, AI 아님).

- html_to_text: 블록 태그에서만 줄을 바꾼다. 인라인 태그마다 줄을 바꾸면
  "2026.10.13.(화) 10:00" 같은 날짜가 여러 줄로 쪼개져 AI가 잘못 읽는다.
- title_deadline: 제목의 마감 표기("(~10/15)", "(~10.12.)", "(마감 10/15)", "10/15까지")를 뽑는다.
  범위("(10/2~10/4)", "(10/2 14:00~10/4)")는 행사 기간이라 마감으로 보지 않는다.
  "~1/2 지원"처럼 괄호 끝·까지·마감이 따라오지 않는 표기는 날짜로 보지 않는다.
  "→", "연장"이 있으면 그 뒤의 마지막 날짜를 쓴다.
"""
import re

from app.ai.dates import find_dates, normalize, parse_posted, resolve

BLOCK_TAGS = ["p", "div", "li", "tr", "table", "ul", "ol", "section", "article", "blockquote",
              "pre", "h1", "h2", "h3", "h4", "h5", "h6", "dl", "dt", "dd", "hr", "header",
              "footer", "figure", "figcaption", "address"]
SHORT_BODY_CHARS = 100   # 이보다 짧으면 본문이 이미지일 가능성이 높다 (표본 20건 중 6건)

_MARK_BEFORE = re.compile(r"(~|마감)\s*\(?\s*$")
_MARK_AFTER = re.compile(r"^[\s.)일]*(\)|까지|마감|$)")


def html_to_text(el) -> str:
    """BeautifulSoup 요소를 텍스트로. 요소를 제자리에서 고친다."""
    for br in el.find_all("br"):
        br.replace_with("\n")
    for tag in el.find_all(BLOCK_TAGS):
        tag.insert_before("\n")
        tag.insert_after("\n")
    for cell in el.find_all(["td", "th"]):
        cell.insert_after(" ")
    text = el.get_text("")
    text = text.replace("​", "").replace("﻿", "").replace("\r", "\n")
    text = re.sub(r"[ \t 　]+", " ", text)
    text = re.sub(r" ?\n[ \n]*", "\n", text)
    return text.strip()


def is_short_body(body: str) -> bool:
    return len((body or "").strip()) < SHORT_BODY_CHARS


def _is_marked(s: str, t, prev) -> bool:
    before = s[(prev.end if prev else 0):t.start]
    if _MARK_BEFORE.search(before):
        return not (prev is not None and prev.is_range_start)   # "10/2~10/4" 의 끝은 행사 기간
    return bool(re.match(r"^[\s.)일]*까지", s[t.end:]))


def title_deadline(title: str, posted_at):
    """제목에서 마감일을 뽑는다. 없거나 게시일을 읽을 수 없으면 None."""
    s = normalize(title)
    posted = parse_posted(posted_at)
    toks = find_dates(s)
    ext = max(s.rfind("→"), s.rfind("연장"))
    if ext >= 0:
        after = [t for t in toks if t.start > ext and not t.is_range_start]
        picks = after[-1:]
    else:
        picks = [t for i, t in enumerate(toks)
                 if not t.is_range_start and _is_marked(s, t, toks[i - 1] if i else None)
                 and _MARK_AFTER.match(s[t.end:t.end + 8])]
    for t in picks:
        d = resolve(t, posted)
        if d:
            start = s.rfind("~", 0, t.start)
            start = start if start >= 0 and t.start - start <= 6 else t.start
            return {"date": d.isoformat(), "time": None, "evidence": s[start:t.end]}
    return None
