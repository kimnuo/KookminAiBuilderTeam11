"""가린 포트폴리오 글에서 내 이력을 뽑는다 (PRD 6-1절 extractProfile, P2).

판단 규칙은 코드가 쥔다.
- 서버도 AI를 부르기 전에 mask_contacts 로 한 번 더 가린다. 프론트가 빠뜨려도 여기서 막는다.
- 글자가 거의 없으면(스캔 이미지 PDF) AI를 부르지 않고 status="no_text" 를 돌려준다. 화면은 수기 입력을 안내한다.
- LLM 출력은 JSON 스키마로 검사하고, 틀리면 1회 다시 부른다. 그래도 틀리면 status="failed".
- 프로젝트·수상·활동은 근거(evidence)가 글에 글자 그대로 있고, 제목의 낱말 하나 이상이 근거 안에 있어야 남는다.
  비교할 때 공백과 줄바꿈은 무시한다. PDF 에서 뽑은 글은 문장 중간에 줄이 바뀌기 때문이다.
- role, period, date 는 글에 글자 그대로 없으면 null 로 바꾼다. 항목은 남긴다.
- skills 는 그 이름이 글에 따로 떨어져 있을 때만 남긴다. "R" 이 "React" 안에 있는 것은 치지 않는다.
- tags 는 config/tags.json 목록에서만 고르고, 남은 기술·항목이 하나도 없으면 비운다.
- 이름·연락처 칸은 만들지 않는다. LLM 이 그런 칸을 보내도 버린다.
결과는 바로 저장하지 않는다. 사용자가 검토·수정한 뒤 기기에 저장한다(PRD 6-1절).
llm 은 prompt(str) -> str 함수다. 실제 호출은 llm_claude.make_claude_llm(task="profile") 이 만든다.
"""
import json
import re
import unicodedata
from pathlib import Path

from jsonschema import Draft202012Validator

from app.ai.enrich import parse_json
from app.ai.mask import mask_contacts

AI_DIR = Path(__file__).parent
TAGS = json.loads((AI_DIR / "config" / "tags.json").read_text(encoding="utf-8"))["tags"]
PROMPT = (AI_DIR / "prompts" / "profile.md").read_text(encoding="utf-8")
VALIDATOR = Draft202012Validator(
    json.loads((AI_DIR / "schemas" / "profile.schema.json").read_text(encoding="utf-8")))
MAX_TEXT_CHARS = 12000   # 프롬프트에 넣는 글 길이 상한. 넘는 뒤쪽은 AI가 보지 못한다
MIN_TEXT_CHARS = 30      # 공백을 뺀 글이 이보다 짧으면 스캔 이미지 PDF로 본다
MIN_EVIDENCE_CHARS = 4   # 공백을 뺀 근거 길이 하한. "2025" 같은 조각 근거가 통과하지 않게 한다
MAX_ITEMS, MAX_SKILLS, MAX_TAGS = 20, 30, 5
ITEM_FIELDS = {"projects": ("role", "period"), "awards": ("date",), "activities": ("period",)}
_DASHES = str.maketrans({**{c: "-" for c in "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"},
                         "\u223c": "~", "\u301c": "~"})
_WORD_SPLIT = re.compile(r"[\s,.·:;|/()\[\]「」『』\"'~-]+")
_LETTER = re.compile(r"[^\W\d_]")


def norm_text(s: str) -> str:
    """비교용. 합자(ﬁ)와 전각 문자를 풀고, 줄표 변형을 맞추고, 공백을 모두 없앤다."""
    s = unicodedata.normalize("NFKC", s or "").translate(_DASHES)
    return re.sub(r"\s+", "", s)


def _flat(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").translate(_DASHES)
    return re.sub(r"\s+", " ", s).strip().casefold()


def build_prompt(masked_text: str) -> str:
    # 글을 마지막에 넣는다. 글 안에 "{{tags}}" 같은 글자가 있어도 다시 바뀌지 않는다.
    return PROMPT.replace("{{tags}}", ", ".join(TAGS)).replace("{{text}}", masked_text[:MAX_TEXT_CHARS])


def _grounded(item: dict, text_n: str) -> bool:
    """근거가 글에 글자 그대로 있고, 제목 낱말 하나 이상이 근거 안에 있어야 한다.

    낱말은 2자 이상이고 글자(한글·영문)가 들어 있어야 한다. "2025" 같은 숫자만으로는
    지어낸 제목("2025 OO 해커톤")이 날짜 근거("2025.11")에 붙어 통과하기 때문이다.
    """
    ev = norm_text(item.get("evidence"))
    if len(ev) < MIN_EVIDENCE_CHARS or ev not in text_n:
        return False
    words = [w for w in _WORD_SPLIT.split(item.get("title") or "") if len(w) >= 2 and _LETTER.search(w)]
    return any(norm_text(w).casefold() in ev.casefold() for w in words)


def _verbatim(value, text_n: str):
    if isinstance(value, str) and value.strip() and norm_text(value) in text_n:
        return value.strip()
    return None


def _items(raw, kind: str, text_n: str) -> list:
    kept, seen = [], set()
    for it in raw or []:
        key = norm_text(it["title"]).casefold()
        if key in seen or not _grounded(it, text_n):
            continue
        seen.add(key)
        row = {"title": it["title"].strip()}
        row.update({f: _verbatim(it.get(f), text_n) for f in ITEM_FIELDS[kind]})
        row["evidence"] = it["evidence"].strip()
        kept.append(row)
    return kept[:MAX_ITEMS]


def _skills(raw, text: str) -> list:
    flat, out, seen = _flat(text), [], set()
    for s in raw or []:
        f = _flat(s)
        if not f or f in seen:
            continue
        if re.search(r"(?<![a-z0-9])" + re.escape(f) + r"(?![a-z0-9])", flat):
            seen.add(f)
            out.append(s.strip())
    return out[:MAX_SKILLS]


def clean(data: dict, text: str) -> dict:
    text_n = norm_text(text)
    items = {kind: _items(data.get(kind), kind, text_n) for kind in ITEM_FIELDS}
    skills = _skills(data.get("skills"), text)
    has_any = bool(skills) or any(items.values())
    tags = [t for t in dict.fromkeys(data.get("tags") or []) if t in TAGS][:MAX_TAGS] if has_any else []
    return {"status": "done", "skills": skills, "tags": tags, **items}


def empty(status: str) -> dict:
    return {"status": status, "skills": [], "tags": [], "projects": [], "awards": [], "activities": []}


def extract_profile(masked_text: str, llm, retries: int = 1) -> dict:
    text, _ = mask_contacts(masked_text)
    if len(norm_text(text)) < MIN_TEXT_CHARS:
        return empty("no_text")
    prompt = build_prompt(text)
    for _ in range(1 + retries):
        data = parse_json(llm(prompt))
        if data is not None and not any(VALIDATOR.iter_errors(data)):
            return clean(data, text)
    return empty("failed")
