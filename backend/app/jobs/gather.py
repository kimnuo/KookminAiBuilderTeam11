"""새 글 하나의 재료 모으기: 상세 본문 + 첨부파일 글자. (네트워크만, AI 는 부르지 않는다)"""

import json
import logging
from dataclasses import dataclass, field

from app.attachments import SUPPORTED_TYPES, ExtractError, extract_text
from app.collectors import fetch_detail
from app.core.config import ATTACHMENT_MAX_BYTES, ATTACHMENTS_PER_NOTICE
from app.core.http import TooLargeError, fetch_bytes
from app.core.schemas import Attachment, Notice
from app.core.text import mask_pii

log = logging.getLogger(__name__)


@dataclass
class Material:
    body: str
    files: list[tuple[str, str]] = field(default_factory=list)  # (파일명, 글자)

    def to_json(self) -> str:
        """DB 저장용. 학번을 가린 뒤 저장한다."""
        return json.dumps(
            {"body": mask_pii(self.body), "files": [[n, mask_pii(t)] for n, t in self.files]},
            ensure_ascii=False,
        )

    @classmethod
    def from_json(cls, raw: str) -> "Material":
        data = json.loads(raw)
        return cls(body=data["body"], files=[tuple(f) for f in data["files"]])


def gather(notice: Notice) -> tuple[Notice, Material]:
    detail = fetch_detail(notice)
    material = Material(body=detail.body)
    attachments = []
    for index, att in enumerate(detail.attachments):
        if index >= ATTACHMENTS_PER_NOTICE:
            att.note = f"첨부 {ATTACHMENTS_PER_NOTICE}개까지만 분석"
        else:
            _read_attachment(att, material)
        attachments.append(att)
    return notice.model_copy(update={"attachments": attachments}), material


def _read_attachment(att: Attachment, material: Material) -> None:
    if att.type not in SUPPORTED_TYPES and att.type != "unknown":
        att.note = f"{att.type} 형식은 분석하지 않음 (원문에서 확인)"
        return
    try:
        kind, text = extract_text(fetch_bytes(att.url, ATTACHMENT_MAX_BYTES), att.type)
    except (ExtractError, TooLargeError) as exc:
        att.note = str(exc)
        return
    except Exception as exc:  # 다운로드 실패 등. 첨부 하나 때문에 글 전체를 버리지 않는다
        log.warning("첨부 다운로드 실패 %s: %s", att.name, exc)
        att.note = "다운로드 실패"
        return
    att.type, att.analyzed = kind, True
    material.files.append((att.name, text))
