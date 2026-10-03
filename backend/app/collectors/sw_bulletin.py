"""SW중심대학사업단 게시판 (software.kookmin.ac.kr, HTML 표).

목록: {path}?articleLimit=20  상세: {path}?mode=view&articleNo=  첨부: ?mode=download&articleNo=&attachNo=
- 목록 칸 순서: 번호(고정 공지는 「공지」), 분류, 제목, 파일, 작성자(읽지 않음), 등록일, 조회수
- 본문은 .b-content-box, 첨부 목록은 .b-file-box
- robots.txt 가 AI 크롤러와 첨부파일 수집을 막아 두었다. 첨부까지 받는 건 해서 결정(2026-10-03),
  배포 전 팀 확인 필요 (05-제출/배포-전-확인-목록)
"""

import re
from datetime import date, datetime

from bs4 import BeautifulSoup, Tag

from app.collectors.common import Detail, attachment, build_notice, now_kst
from app.core.config import SW_BASE_URL, source_list_url
from app.core.http import fetch_text
from app.core.schemas import Notice
from app.core.text import html_to_text

ARTICLE_RE = re.compile(r"articleNo=(\d+)")


def fetch_list(source: dict) -> list[Notice]:
    soup = BeautifulSoup(fetch_text(source_list_url(source)), "html.parser")
    fetched_at = now_kst()
    rows = soup.select("table.board-table tbody tr")
    items = (_parse_row(tr, source, fetched_at) for tr in rows)
    return [n for n in items if n]


def _parse_row(tr: Tag, source: dict, fetched_at: datetime) -> Notice | None:
    tds = tr.find_all("td", recursive=False)
    link = tr.select_one(".b-title-box a[href*='articleNo=']")
    if len(tds) < 6 or not link:
        return None
    article = ARTICLE_RE.search(link["href"]).group(1)
    return build_notice(
        source,
        article=article,
        title=link.get("title", "").removesuffix("자세히 보기").strip() or link.get_text(" ", strip=True),
        url=f"{SW_BASE_URL}{source['path']}?mode=view&articleNo={article}",
        posted_at=_parse_date(tds[5].get_text(strip=True)),
        department=tds[1].get_text(" ", strip=True) or None,  # 원 사이트 분류 (학생지원, 산학협력 …)
        pinned="b-top-box" in (tr.get("class") or []),
        fetched_at=fetched_at,
    )


def _parse_date(text: str) -> date | None:
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def fetch_detail(notice: Notice) -> Detail:
    soup = BeautifulSoup(fetch_text(notice.url), "html.parser")
    body_node = soup.select_one(".b-content-box")
    body = html_to_text(body_node) if body_node else ""
    base = notice.url.split("?", 1)[0]
    files = [
        attachment(a.get_text(" ", strip=True), base + a["href"])
        for a in soup.select(".b-file-box a[href*='mode=download']")
    ]
    return Detail(body=body, attachments=files)
