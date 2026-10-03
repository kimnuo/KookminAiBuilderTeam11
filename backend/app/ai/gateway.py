"""학교 AI 게이트웨이(ai.cs.kookmin.ac.kr) 호출. 키는 backend/.env 의 LLM_API_KEY.

- Anthropic Messages 형식(`/v1/messages`)에 도구 하나를 강제해서 정해진 JSON 만 받는다.
  이 게이트웨이는 OpenAI 형식의 `response_format: json_schema` 를 무시해서(2026-10-03 확인)
  도구 강제가 형식을 지키는 유일한 방법이다.
- 쓸 수 있는 모델: claude-haiku-4-5, claude-opus-5
"""

import httpx

from app.ai.llm import LlmError
from app.core.config import LLM_API_BASE, LLM_API_KEY, LLM_API_MODEL, LLM_TIMEOUT_SEC


def complete_json(system: str, user: str, schema: dict, tool_name: str = "answer") -> dict:
    if not LLM_API_KEY:
        raise LlmError("LLM_API_KEY 가 없다 (backend/.env)")
    payload = {
        "model": LLM_API_MODEL,
        "max_tokens": 2000,
        "system": system,
        "messages": [{"role": "user", "content": user}],
        "tools": [{"name": tool_name, "description": "정해진 형식으로 답한다", "input_schema": schema}],
        "tool_choice": {"type": "tool", "name": tool_name},
    }
    headers = {"x-api-key": LLM_API_KEY, "anthropic-version": "2023-06-01"}
    try:
        response = httpx.post(
            f"{LLM_API_BASE}/messages", json=payload, headers=headers, timeout=LLM_TIMEOUT_SEC
        )
    except httpx.HTTPError as exc:
        raise LlmError(f"게이트웨이 호출 실패: {exc}") from exc
    if response.status_code != 200:
        raise LlmError(f"게이트웨이 {response.status_code}: {response.text[:200]}")
    return _tool_input(response.json(), tool_name)


def _tool_input(body: dict, tool_name: str) -> dict:
    for block in body.get("content", []):
        if block.get("type") == "tool_use" and block.get("name") == tool_name:
            value = block.get("input")
            if isinstance(value, dict):
                return value
    raise LlmError("도구 응답이 없다")


def complete_text(prompt: str) -> str:
    """현찬의 ai 모듈들이 쓰는 형태(prompt -> 글자). JSON 검사는 그쪽에서 한다."""
    if not LLM_API_KEY:
        raise LlmError("KMU_AI_API_KEY 가 없다 (backend/.env)")
    payload = {
        "model": LLM_API_MODEL,
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {"x-api-key": LLM_API_KEY, "anthropic-version": "2023-06-01"}
    try:
        response = httpx.post(
            f"{LLM_API_BASE}/messages", json=payload, headers=headers, timeout=LLM_TIMEOUT_SEC
        )
    except httpx.HTTPError as exc:
        raise LlmError(f"게이트웨이 호출 실패: {exc}") from exc
    if response.status_code != 200:
        raise LlmError(f"게이트웨이 {response.status_code}: {response.text[:200]}")
    blocks = response.json().get("content", [])
    return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
