"""국민대 본부 공지 게시판 (HTML).

목록: /user/kmuNews/notice/{게시판}/index.do  상세: /user/kmuNews/notice/{게시판}/{글번호}/view.do
- 일반 글은 .board_etc 에 날짜·부서·작성자·조회수, 고정 공지(li.notice)는 제목만 있다
- 본문은 .view_cont
- 첨부는 상세 페이지 JS 가 portal.kookmin.ac.kr/por/restapi/file/{uuid} 로 목록을 받는다
- 작성자 실명은 읽지 않는다 (PRD 7절)
"""

import re
from datetime import date, datetime

from bs4 import BeautifulSoup, Tag

from app.collectors.common import Detail, attachment, build_notice, now_kst
from app.core.config import KMU_BASE_URL, source_list_url
from app.core.http import fetch_json, fetch_text
from app.core.schemas import Attachment, Notice
from app.core.text import html_to_text

DETAIL_RE = re.compile(r"/user/kmuNews/notice/(\d+)/(\d+)/view\.do")
DATE_RE = re.compile(r"(\d{4})\.(\d{2})\.(\d{2})")
UUID_RE = re.compile(r'attflUuidValue\s*=\s*"([0-9a-f]+)"')
FILE_LIST_URL = "https://portal.kookmin.ac.kr/por/restapi/file/{uuid}"
FILE_DOWNLOAD_URL = "https://kep.kookmin.ac.kr/com/cmsv/FileCtr/fileDefaultDownload.do?fileNo={no}&seq={seq}"


def fetch_list(source: dict) -> list[Notice]:
    soup = BeautifulSoup(fetch_text(source_list_url(source)), "html.parser")
    fetched_at = now_kst()
    items = (_parse_item(li, source, fetched_at) for li in soup.select(".board_list li"))
    return [n for n in items if n]


def _parse_item(li: Tag, source: dict, fetched_at: datetime) -> Notice | None:
    link = li.find("a", href=DETAIL_RE)
    title = li.select_one(".title")
    if not link or not title:
        return None
    board, article = DETAIL_RE.search(link["href"]).groups()
    posted_at, department = _parse_etc(li)
    return build_notice(
        source,
        article=article,
        title=title.get_text(" ", strip=True),
        url=f"{KMU_BASE_URL}/user/kmuNews/notice/{board}/{article}/view.do",
        posted_at=posted_at,
        department=department,
        pinned="notice" in (li.get("class") or []),
        fetched_at=fetched_at,
    )


def _parse_etc(li: Tag) -> tuple[date | None, str | None]:
    """.board_etc 의 span 순서: 날짜, 부서, 작성자(읽지 않음), 조회수."""
    spans = [s.get_text(strip=True) for s in li.select(".board_etc > span")]
    posted_at = None
    if spans and (m := DATE_RE.fullmatch(spans[0])):
        posted_at = date(*map(int, m.groups()))
    department = spans[1] if len(spans) > 1 and spans[1] else None
    return posted_at, department


def fetch_detail(notice: Notice) -> Detail:
    html = fetch_text(notice.url)
    soup = BeautifulSoup(html, "html.parser")
    body_node = soup.select_one(".view_cont")
    body = html_to_text(body_node) if body_node else ""
    return Detail(body=body, attachments=_attachments(html))


def _attachments(html: str) -> list[Attachment]:
    m = UUID_RE.search(html)
    if not m:
        return []
    files = fetch_json(FILE_LIST_URL.format(uuid=m.group(1))) or []
    return [
        attachment(f["fileNm"], FILE_DOWNLOAD_URL.format(no=f["fileNo"], seq=f["seq"]))
        for f in files
        if f.get("fileNo") and f.get("fileNm")
    ]
