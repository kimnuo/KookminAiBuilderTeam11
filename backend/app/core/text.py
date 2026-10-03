"""본문·첨부 글자 다루기: HTML → 글자, 개인정보 가리기, 길이 자르기."""

import re

from bs4 import Tag

# 학번: 19xx/20xx 로 시작하는 8자리 숫자 (선발·수상 결과 명단에 자주 나온다)
_STUDENT_ID_RE = re.compile(r"(?<!\d)(?:19|20)\d{6}(?!\d)")
_SPACES_RE = re.compile(r"[ \t 　]+")
_BLANK_LINES_RE = re.compile(r"\n{3,}")


def html_to_text(node: Tag) -> str:
    """표는 칸을 ' | ' 로, 블록은 줄바꿈으로 살린다."""
    for br in node.find_all("br"):
        br.replace_with("\n")
    for row in node.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
        row.replace_with("\n" + " | ".join(cells) + "\n")
    for block in node.find_all(["p", "div", "li", "h1", "h2", "h3", "h4", "h5"]):
        block.insert_after("\n")
    return normalize(node.get_text())


def normalize(text: str) -> str:
    lines = [_SPACES_RE.sub(" ", line).strip() for line in text.splitlines()]
    return _BLANK_LINES_RE.sub("\n\n", "\n".join(lines)).strip()


def mask_pii(text: str) -> str:
    """AI 로 보내기 전에 남의 학번을 가린다. 학교·부서 연락처는 공고 정보라 남긴다."""
    return _STUDENT_ID_RE.sub("[학번]", text)


def clip(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n…(이하 생략)"


def squash(text: str) -> str:
    """근거 문장 대조용: 공백을 모두 지운다."""
    return re.sub(r"\s+", "", text)
