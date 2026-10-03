"""본문이 포스터 이미지뿐인 공지에서 이미지를 받아 글자를 읽는다 (표본 20건 중 6건이 이런 공지).

흐름: image_urls(본문 요소) → download_images → read_poster(이미지, Haiku) → notice["posterText"]
enrich 는 posterText 를 프롬프트에 붙이고, 마감 근거가 포스터 글에서만 나오면 deadline.source="poster" 로 표시한다.
읽은 글은 AI 판독이라 오탈자가 있을 수 있다. 화면에서 "포스터에서 읽음"을 밝힌다.
"""
from pathlib import Path
from urllib.parse import urljoin

import requests

from app.ai.text import is_short_body

PROMPT = (Path(__file__).parent / "prompts" / "poster.md").read_text(encoding="utf-8")
UA = {"User-Agent": "KMU-Notice-Hackathon-Team11/0.1"}
MEDIA = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}
MAX_IMAGES = 3
MAX_BYTES = 5_000_000   # 큰 이미지는 보내지 않는다 (API 이미지 크기 제한, 비용)


def needs_poster(notice: dict) -> bool:
    return is_short_body(notice.get("body") or "")


def image_urls(view_el, page_url: str) -> list[str]:
    """본문 요소(div.view_cont)의 이미지 주소를 절대 주소로. data: 주소는 뺀다."""
    out = []
    for img in view_el.find_all("img") if view_el else []:
        src = (img.get("src") or "").strip()
        if src and not src.startswith("data:"):
            url = urljoin(page_url, src)
            if url not in out:
                out.append(url)
    return out[:MAX_IMAGES]


def sniff(data: bytes) -> str | None:
    """파일 앞부분으로 이미지 형식을 알아낸다. 학교 서버는 포스터를 application/x-download 로 보내고
    주소에 확장자도 없어서(findUploadImg.do?fileNo=...) 헤더·확장자만으로는 알 수 없다."""
    if data.startswith(b"\x89PNG"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def media_type(url: str, content_type: str | None, data: bytes = b"") -> str | None:
    found = sniff(data)
    if found:
        return found
    ct = (content_type or "").split(";")[0].strip().lower()
    if ct in MEDIA.values():
        return ct
    ext = url.split("?")[0].rsplit(".", 1)[-1].lower()
    return MEDIA.get(ext)


def download_images(urls: list[str], session=None) -> list[tuple[str, bytes]]:
    s = session or requests
    out = []
    for url in urls[:MAX_IMAGES]:
        try:
            r = s.get(url, headers=UA, timeout=20)
            r.raise_for_status()
        except Exception:
            continue
        mt = media_type(url, r.headers.get("Content-Type"), r.content)
        if mt and 0 < len(r.content) <= MAX_BYTES:
            out.append((mt, r.content))
    return out


def read_poster(images: list[tuple[str, bytes]], vision_llm) -> str | None:
    """vision_llm(prompt, images) -> 글자. 실패하거나 글자가 없으면 None."""
    if not images:
        return None
    try:
        text = (vision_llm(PROMPT, images) or "").strip()
    except Exception:
        return None
    return text or None
