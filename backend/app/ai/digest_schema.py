"""LLM 출력 형식 (JSON Schema). --json-schema 로 넘긴다."""

from app.core.config import CATEGORIES, TAGS

_STR = {"type": "string"}
_EVIDENCE = {"type": "string", "description": "입력 글에서 그대로 복사한 구절"}

DIGEST_SCHEMA = {
    "type": "object",
    "properties": {
        "title": _STR,
        "summary": _STR,
        "categories": {"type": "array", "items": {"type": "string", "enum": CATEGORIES}},
        "tags": {"type": "array", "items": {"type": "string", "enum": TAGS},
                 "description": "관심 분야 0~3개. 맞는 것이 없으면 빈 배열"},
        "keyPoints": {"type": "array", "items": {
            "type": "object",
            "properties": {"label": _STR, "value": _STR, "evidence": _EVIDENCE},
            "required": ["label", "value", "evidence"],
        }},
        "requirements": {"type": "array", "items": {
            "type": "object",
            "properties": {"text": _STR, "evidence": _EVIDENCE, "origin": _STR},
            "required": ["text", "evidence", "origin"],
        }},
        "deadline": {"type": ["object", "null"], "properties": {
            "date": {"type": "string", "description": "YYYY-MM-DD"},
            "time": {"type": ["string", "null"], "description": "HH:MM"},
            "evidence": _EVIDENCE,
        }, "required": ["date", "time", "evidence"]},
        "lastDate": {"type": ["object", "null"], "properties": {
            "date": {"type": "string", "description": "YYYY-MM-DD"},
            "evidence": _EVIDENCE,
        }, "required": ["date", "evidence"]},
        "actionRequired": {"type": "boolean"},
        "audience": {"type": ["object", "null"], "properties": {
            "years": {"type": "array", "items": {"type": "integer"}},
            "majors": {"type": "array", "items": _STR},
            "statuses": {"type": "array", "items": _STR},
            "text": {"type": ["string", "null"]},
        }, "required": ["years", "majors", "statuses", "text"]},
        "etc": {"type": "array", "items": _STR},
    },
    "required": [
        "title", "summary", "categories", "keyPoints", "requirements",
        "deadline", "lastDate", "actionRequired", "audience", "etc",
    ],
}
