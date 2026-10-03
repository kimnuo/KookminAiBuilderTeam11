"""인디스워크 신입 채용·대외활동 (inthiswork.com, 공개 WordPress REST API).

- 목록: /wp-json/wp/v2/posts?categories=&categories_exclude=마감&tags=&per_page=
- 제목은 「회사｜공고명 (구분)」 꼴이고 구분자가 전각 ｜(U+FF5C) 다
- **본문에는 글이 거의 없다**(공고 내용이 포스터 이미지 한 장). 그래서 마감일은
  publishpress_future_action.date(마감 시각에 분류를 바꾸려고 예약해 둔 값)에서 읽고,
  분야는 태그에서 읽어 본문 대신 쓴다
- robots.txt 는 우리 봇을 막지 않지만 AI 크롤러 14종을 막아 두었다. 요청을 적게 쓰고
  제목·마감·원문 링크만 저장한다. 배포 전 팀 확인 (05-제출/배포-전-확인-목록)
"""

import html
import re
from datetime import date, datetime

from app.collectors.common import Detail, build_notice, now_kst
from app.core.config import (
    INTHISWORK_BASE_URL,
    INTHISWORK_CLOSED_CATEGORY,
    INTHISWORK_TAGS,
    TECH_RE,
)
from app.core.http import fetch_json
from app.core.text import html_to_text
from bs4 import BeautifulSoup

PER_PAGE = 50
FIELDS = "id,date,link,title,tags,categories,publishpress_future_action,content"
_HREF_RE = re.compile(r'href="(https?://[^"]+)"')
BAR = "｜"  # 전각 세로줄 (U+FF5C)


def fetch_list(source: dict) -> list:
    fetched_at = now_kst()
    query = (
        f"categories={source['category']}"
        f"&categories_exclude={INTHISWORK_CLOSED_CATEGORY}"
        f"&per_page={PER_PAGE}&orderby=date&order=desc&_fields={FIELDS}"
    )
    if source.get("tagFilter"):
        query += "&tags=" + ",".join(str(t) for t in INTHISWORK_TAGS)
    rows = fetch_json(f"{INTHISWORK_BASE_URL}/wp-json/wp/v2/posts?{query}")
    if not isinstance(rows, list):
        return []
    return [n for n in (_to_notice(r, source, fetched_at) for r in rows if _wanted(r)) if n]


def _dict(value) -> dict:
    """WordPress 는 값이 없을 때 빈 배열을 주기도 한다. 사전이 아니면 빈 사전으로 본다."""
    return value if isinstance(value, dict) else {}


def _title_of(row: dict) -> str:
    return html.unescape(_dict(row.get("title")).get("rendered") or "").strip()


def _wanted(row: dict) -> bool:
    """소프트웨어·하드웨어·AI 와 관련된 글만. 태그로 걸리거나 제목에 관련 낱말이 있으면 받는다."""
    if set(row.get("tags") or []) & set(INTHISWORK_TAGS):
        return True
    return bool(TECH_RE.search(_title_of(row)))


def _to_notice(row: dict, source: dict, fetched_at: datetime):
    article, title = row.get("id"), _title_of(row)
    if not article or not title:
        return None
    company = title.split(BAR)[0].strip() if BAR in title else None
    return build_notice(
        source,
        article=str(article),
        title=title.replace(BAR, " · "),
        url=row.get("link") or f"{INTHISWORK_BASE_URL}/archives/{article}",
        posted_at=_date(row.get("date")),
        department=company,
        fetched_at=fetched_at,
    )


def _date(value: str | None) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def fetch_detail(notice) -> Detail:
    article = notice.id.rsplit("-", 1)[-1]
    row = fetch_json(
        f"{INTHISWORK_BASE_URL}/wp-json/wp/v2/posts/{article}?_fields={FIELDS}&_embed=1"
    )
    title = _title_of(row)
    parts = [f"공고: {title}"]
    if BAR in title:
        parts.insert(0, f"회사·주최: {title.split(BAR)[0].strip()}")
    deadline = (_dict(row.get("publishpress_future_action")).get("date") or "")[:16]
    if deadline:
        parts.append(f"마감: {deadline} (한국 시간)")
    names = _term_names(row)
    if names:
        parts.append(f"분야: {', '.join(names)}")
    raw = _dict(row.get("content")).get("rendered") or ""
    body = html_to_text(BeautifulSoup(raw, "html.parser"))
    link = _HREF_RE.search(raw)
    if link:
        parts.append(f"지원 페이지: {html.unescape(link.group(1))}")
    parts.append("공고 내용은 원문 포스터 이미지에 있습니다. 자세한 조건은 원문을 확인하세요.")
    if body.strip() and body.strip() != "지원하러 가기":
        parts.append(body)
    return Detail(body="\n".join(p for p in parts if p.strip()))


def _term_names(row: dict) -> list[str]:
    groups = _dict(row.get("_embedded")).get("wp:term") or []
    return [t.get("name") for group in groups for t in group if t.get("name")]
