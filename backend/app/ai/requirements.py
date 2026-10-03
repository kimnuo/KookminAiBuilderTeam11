"""공고 한 건에서 지원할 때 적을 정보와 낼 서류 목록을 뽑는다 (PRD 6-1절 extractRequirements, P3).

원칙 (PRD 6-1절 설계 원칙 1·2, 11절)
- AI 에는 공고 제목과 본문만 보낸다. 이 모듈은 사용자 프로필 값을 받지 않는다.
  notice 에 다른 키가 있어도 프롬프트에는 title, body 만 들어간다.

판단 규칙은 코드가 쥔다.
- LLM 출력은 JSON 스키마로 검사하고, 틀리면 1회 다시 부른다. 그래도 틀리면 status="failed", 목록은 빈 배열.
- key 는 고정 목록(schemas/requirements.schema.json 의 $defs.fieldKey)과 other 만 남긴다. 목록 밖이면 그 항목만 버린다.
- 근거(evidence)가 제목·본문에 글자 그대로(공백 무시) 없으면 그 항목을 버린다.
- 서류 이름(name)과 other 의 label 은 공고 문구를 그대로 쓰게 했으므로, 근거 안에 없으면 버린다.
  근거만 원문에서 복사하고 이름을 지어낸 경우를 막는다. key 와 근거의 뜻이 맞는지는 보지 않는다.
- 같은 key(other 는 label)와 같은 서류 이름이 또 나오면 처음 것만 남긴다.
- condition 은 해석이라 원문 대조를 하지 않는다.

입력 notice: title, body(본문 텍스트). llm 은 prompt(str) -> str 함수다.
"""
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

from app.ai.enrich import _squash, parse_json
from app.ai.text import is_short_body

AI_DIR = Path(__file__).parent
PROMPT = (AI_DIR / "prompts" / "requirements.md").read_text(encoding="utf-8")
_SCHEMA = json.loads((AI_DIR / "schemas" / "requirements.schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(_SCHEMA)
FIELD_KEYS = _SCHEMA["$defs"]["fieldKey"]["enum"]  # 고정 키 12개 + other
MAX_BODY_CHARS = 6000


def build_prompt(notice: dict) -> str:
    """제목과 본문만 넣는다. 자리표시는 한 번에 바꿔서, 본문에 {{...}} 가 있어도 다시 치환하지 않는다."""
    body = (notice.get("body") or "").strip()
    if is_short_body(body):
        body = (body + "\n(본문이 거의 없음. 포스터 이미지 공지일 수 있음)").strip()
    values = {
        "title": notice.get("title") or "",
        "body": body[:MAX_BODY_CHARS],
        "keys": ", ".join(FIELD_KEYS),
    }
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], PROMPT)


def _in(part: str, whole: str) -> bool:
    """공백을 뺀 part 가 공백을 뺀 whole 안에 있으면 True. 빈 문자열은 False."""
    p = _squash(part)
    return bool(p) and p in _squash(whole)


def _clean_field(f: dict, text: str):
    """버릴 항목이면 None, 남길 항목이면 PRD 6-1절 모양의 dict."""
    key, ev = f["key"], f["evidence"]
    if key not in FIELD_KEYS or not _in(ev, text):
        return None
    if key != "other":
        return {"key": key, "required": f["required"], "evidence": ev}
    label = (f.get("label") or "").strip()
    if not _in(label, ev):
        return None
    return {"key": key, "label": label, "required": f["required"], "evidence": ev}


def _clean_document(d: dict, text: str):
    name, ev = d["name"].strip(), d["evidence"]
    if not _in(ev, text) or not _in(name, ev):
        return None
    return {"name": name, "condition": (d.get("condition") or "").strip() or None, "evidence": ev}


def _field_id(f: dict) -> str:
    return f["key"] + ":" + _squash(f.get("label") or "")


def _doc_id(d: dict) -> str:
    return _squash(d["name"])


def _keep(items, clean_one, ident, text: str) -> list:
    out, seen = [], set()
    for it in items:
        c = clean_one(it, text)
        if c is None or ident(c) in seen:
            continue
        seen.add(ident(c))
        out.append(c)
    return out


def clean(data: dict, notice: dict) -> dict:
    text = (notice.get("title") or "") + "\n" + (notice.get("body") or "")
    return {
        "status": "done",
        "fields": _keep(data["fields"], _clean_field, _field_id, text),
        "documents": _keep(data["documents"], _clean_document, _doc_id, text),
    }


def failed() -> dict:
    return {"status": "failed", "fields": [], "documents": []}


def extract_requirements(notice: dict, llm, retries: int = 1) -> dict:
    prompt = build_prompt(notice)
    for _ in range(1 + retries):
        data = parse_json(llm(prompt))
        if data is not None and not any(VALIDATOR.iter_errors(data)):
            return clean(data, notice)
    return failed()
