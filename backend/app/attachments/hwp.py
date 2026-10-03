"""한글 문서에서 글자 뽑기.

- HWP 5.x: OLE 파일. BodyText/Section{n} 스트림(대개 zlib 압축)의 PARA_TEXT 레코드에 UTF-16 글자가 있다.
  배포용(암호화) 문서는 본문을 못 읽으므로 PrvText(미리보기 글자, 앞부분만)로 대신한다.
- HWPX: zip 안의 Contents/section*.xml 에서 <hp:t> 글자를 모은다.
"""

import io
import re
import struct
import zipfile
import zlib

import olefile

PARA_TEXT_TAG = 67
# 8 글자(16바이트)를 차지하는 제어 문자 (인라인·확장 컨트롤)
_WIDE_CONTROLS = {1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23}
_HWPX_TEXT_RE = re.compile(r"<hp:t(?:\s[^>]*)?>(.*?)</hp:t>", re.S)
_TAG_RE = re.compile(r"<[^>]+>")


def extract_hwp(data: bytes) -> str:
    with olefile.OleFileIO(io.BytesIO(data)) as ole:
        compressed = bool(ole.openstream("FileHeader").read()[36] & 1)
        sections = sorted(
            (e for e in ole.listdir() if e[0] == "BodyText"),
            key=lambda e: int(e[1].removeprefix("Section") or 0),
        )
        texts = [_section_text(ole.openstream(e).read(), compressed) for e in sections]
        text = "\n".join(t for t in texts if t)
        if not text.strip() and ole.exists("PrvText"):
            text = ole.openstream("PrvText").read().decode("utf-16-le", "ignore")
    return text


def _section_text(raw: bytes, compressed: bool) -> str:
    try:
        data = zlib.decompress(raw, -15) if compressed else raw
    except zlib.error:
        return ""  # 배포용(암호화) 문서
    paragraphs, pos = [], 0
    while pos + 4 <= len(data):
        header = struct.unpack_from("<I", data, pos)[0]
        tag, size, pos = header & 0x3FF, (header >> 20) & 0xFFF, pos + 4
        if size == 0xFFF:
            size, pos = struct.unpack_from("<I", data, pos)[0], pos + 4
        if tag == PARA_TEXT_TAG:
            paragraphs.append(_decode_para(data[pos:pos + size]))
        pos += size
    return "\n".join(paragraphs)


def _decode_para(chunk: bytes) -> str:
    codes = struct.unpack(f"<{len(chunk) // 2}H", chunk[: len(chunk) // 2 * 2])
    out, i = [], 0
    while i < len(codes):
        code = codes[i]
        if code in _WIDE_CONTROLS:
            i += 8
            continue
        if code >= 32:
            out.append(chr(code))
        elif code in (10, 13):
            out.append("\n")
        i += 1
    return "".join(out)


def extract_hwpx(data: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = sorted(n for n in z.namelist() if re.match(r"Contents/section\d+\.xml$", n))
        texts = []
        for name in names:
            xml = z.read(name).decode("utf-8", "ignore")
            texts += [_TAG_RE.sub("", t) for t in _HWPX_TEXT_RE.findall(xml)]
    return "\n".join(texts)
