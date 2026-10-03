"""첨부파일 → 글자. 형식은 파일명보다 파일 앞부분(매직 바이트)을 먼저 믿는다.

지원: pdf, hwp, hwpx, docx, pptx. 그 밖(xls, xlsx, 이미지, zip …)은 분석하지 않고 링크만 둔다.
스캔 이미지 PDF 처럼 글자가 안 나오면 실패로 본다.
"""

import io
import zipfile

from app.attachments.hwp import extract_hwp, extract_hwpx
from app.attachments.office import extract_docx, extract_pdf, extract_pptx
from app.core.text import normalize

_EXTRACTORS = {
    "pdf": extract_pdf,
    "hwp": extract_hwp,
    "hwpx": extract_hwpx,
    "docx": extract_docx,
    "pptx": extract_pptx,
}
SUPPORTED_TYPES = set(_EXTRACTORS)
MIN_TEXT_CHARS = 20


class ExtractError(Exception):
    pass


def detect_type(data: bytes, name_type: str) -> str:
    if data.startswith(b"%PDF"):
        return "pdf"
    if data.startswith(b"\xd0\xcf\x11\xe0"):  # OLE: hwp 또는 옛 오피스(doc, xls)
        return "hwp" if name_type in ("hwp", "unknown") else name_type
    if data.startswith(b"PK"):
        return _zip_type(data, name_type)
    return name_type


def _zip_type(data: bytes, name_type: str) -> str:
    try:
        names = zipfile.ZipFile(io.BytesIO(data)).namelist()
    except zipfile.BadZipFile:
        return name_type
    if any(n.startswith("Contents/section") for n in names):
        return "hwpx"
    if any(n.startswith("word/") for n in names):
        return "docx"
    if any(n.startswith("ppt/") for n in names):
        return "pptx"
    return name_type


def extract_text(data: bytes, name_type: str) -> tuple[str, str]:
    """(실제 형식, 글자). 못 뽑으면 ExtractError."""
    kind = detect_type(data, name_type)
    extractor = _EXTRACTORS.get(kind)
    if extractor is None:
        raise ExtractError(f"{kind} 형식은 분석하지 않음")
    try:
        text = normalize(extractor(data))
    except Exception as exc:  # 깨진 파일·배포용 문서 등. 한 파일 실패로 전체가 멈추지 않게 한다
        raise ExtractError(f"{kind} 읽기 실패: {type(exc).__name__}") from exc
    if len(text) < MIN_TEXT_CHARS:
        raise ExtractError("글자가 거의 없음 (스캔 이미지일 수 있음)")
    return kind, text
