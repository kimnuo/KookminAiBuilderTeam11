"""수집기 공용: 목록 → Notice(digest pending), 상세 → Detail(본문 + 첨부 목록)."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse

from app.core.schemas import Attachment, Digest, Notice, SourceRef

KST = timezone(timedelta(hours=9))


@dataclass
class Detail:
    body: str  # 본문 글자 (가리기 전)
    attachments: list[Attachment] = field(default_factory=list)


def now_kst() -> datetime:
    return datetime.now(KST).replace(microsecond=0)


def file_type(name: str) -> str:
    suffix = PurePosixPath(unquote(urlparse(name).path or name)).suffix
    return suffix.lstrip(".").lower() or "unknown"


def attachment(name: str, url: str) -> Attachment:
    name = " ".join(name.split())
    return Attachment(name=name, url=url, type=file_type(name))


def build_notice(
    source: dict,
    *,
    article: str,
    title: str,
    url: str,
    posted_at: date | None,
    department: str | None = None,
    pinned: bool = False,
    fetched_at: datetime,
) -> Notice:
    return Notice(
        id=f"{source['id']}-{article}",
        source=SourceRef(id=source["id"], name=source["name"], group=source["group"]),
        original_title=" ".join(title.split()),
        url=url,
        posted_at=posted_at,
        department=department,
        pinned=pinned,
        fetched_at=fetched_at,
        categories=[source["defaultCategory"]],
        digest=Digest(status="pending"),
    )
