"""소프트웨어융합대학 게시판 (RSS 2.0). 학사·장학·취업·특강행사 4개가 같은 형식이다.

- 목록: /news/{게시판}/rss  상세: /news/{게시판}/{글번호}
- <link> 에 글번호만 있다 (예: 2872)
- <author> 는 직원 실명이라 읽지 않는다 (PRD 7절)
- <lastBuildDate> 는 요청 시각 +9시간으로 찍혀 나와 쓰지 않는다 (2026-10-03 확인). pubDate 만 쓴다
  (feedparser 의 published_parsed 는 UTC 로 바뀌므로 원문 문자열을 직접 읽는다)
- 상세 본문은 td.board-view-content, 첨부는 td.attach-file 의 링크
"""

from datetime import date, datetime
from email.utils import parsedate_to_datetime

import feedparser
from bs4 import BeautifulSoup

from app.collectors.common import KST, Detail, attachment, build_notice, now_kst
from app.core.config import CS_BASE_URL, source_list_url
from app.core.http import fetch_text
from app.core.schemas import Notice
from app.core.text import html_to_text


def fetch_list(source: dict) -> list[Notice]:
    feed = feedparser.parse(fetch_text(source_list_url(source)))
    fetched_at = now_kst()
    notices = []
    for entry in feed.entries:
        article = str(entry.get("link", "")).strip().rsplit("/", 1)[-1]
        if not article.isdigit():
            continue
        notices.append(_build(source, entry, article, fetched_at))
    return notices


def _build(source: dict, entry, article: str, fetched_at: datetime) -> Notice:
    return build_notice(
        source,
        article=article,
        title=entry.get("title", ""),
        url=f"{CS_BASE_URL}/news/{source['board']}/{article}",
        posted_at=_posted_date(entry.get("published")),
        fetched_at=fetched_at,
    )


def _posted_date(published: str | None) -> date | None:
    if not published:
        return None
    try:
        return parsedate_to_datetime(published).astimezone(KST).date()
    except (TypeError, ValueError):
        return None


def fetch_detail(notice: Notice) -> Detail:
    soup = BeautifulSoup(fetch_text(notice.url), "html.parser")
    body_node = soup.select_one("td.board-view-content") or soup.select_one("#view-detail-data")
    body = html_to_text(body_node).removeprefix("게시물 내용").strip() if body_node else ""
    files = []
    for a in soup.select("td.attach-file a[href]"):
        name = a.get_text(" ", strip=True).split(" (")[0]  # "파일명.xls (35.0 KB)"
        files.append(attachment(name, a["href"]))
    return Detail(body=body, attachments=files)
