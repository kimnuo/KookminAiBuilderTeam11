"""학교 AI 게이트웨이의 Claude 모델을 Anthropic 공식 SDK 로 부른다.

확인한 것
- 게이트웨이(new-api) 문서: Claude 형식 POST /v1/messages, x-api-key + anthropic-version 헤더 (SDK 가 붙인다).
- SDK 사용법(claude-api 스킬 python README): Anthropic(api_key, base_url), messages.create,
  이미지 base64 블록, output_config={"effort": ...}, 응답은 content 블록 중 type="text".
- Opus 5 는 사고 과정이 기본으로 켜져 있어 effort 를 low 로 낮춘다. Haiku 4.5 는 effort 를 보내면 오류라 보내지 않는다.

작업별 모델은 backend/.env 의 KMU_AI_MODEL_<작업> 에서 읽는다 (classify, poster, profile, requirements).
profile·requirements 가 비어 있으면 classify 모델을 쓴다.
"""
import base64
import os

from app.ai.llm_gateway import base_host, load_env

TASK_ENV = {"classify": "KMU_AI_MODEL_CLASSIFY", "poster": "KMU_AI_MODEL_POSTER",
            "profile": "KMU_AI_MODEL_PROFILE", "requirements": "KMU_AI_MODEL_REQUIREMENTS"}
NO_EFFORT_MODELS = ("claude-haiku-4-5",)   # effort 파라미터를 받지 않는 모델


def model_for(task: str) -> str | None:
    load_env()
    return os.environ.get(TASK_ENV.get(task, "")) or os.environ.get("KMU_AI_MODEL_CLASSIFY")


def _client():
    import anthropic
    load_env()
    key = os.environ.get("KMU_AI_API_KEY")
    if not key:
        raise RuntimeError("KMU_AI_API_KEY 가 없다. backend/.env 에 넣는다 (커밋 금지).")
    return anthropic.Anthropic(api_key=key, base_url=base_host(), max_retries=2, timeout=120.0)


def image_block(media_type: str, data: bytes) -> dict:
    return {"type": "image", "source": {"type": "base64", "media_type": media_type,
                                        "data": base64.standard_b64encode(data).decode("utf-8")}}


def make_claude_llm(task: str = "classify", max_tokens: int = 4000, effort: str | None = "low",
                    client=None, model: str | None = None):
    """call(prompt, images=None) -> 응답 글자. images 는 [(media_type, bytes), ...]."""
    client = client or _client()
    mid = model or model_for(task)
    if not mid:
        raise RuntimeError(f"{task} 모델이 없다. backend/.env 의 {TASK_ENV.get(task)} 를 채운다.")
    usage = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "refusals": 0}

    def call(prompt: str, images=None) -> str:
        content = [image_block(mt, data) for mt, data in images or []] + [{"type": "text", "text": prompt}]
        kwargs = {"model": mid, "max_tokens": max_tokens, "messages": [{"role": "user", "content": content}]}
        if effort and not mid.startswith(NO_EFFORT_MODELS):
            kwargs["output_config"] = {"effort": effort}
        resp = client.messages.create(**kwargs)
        u = getattr(resp, "usage", None)
        usage["calls"] += 1
        usage["input_tokens"] += getattr(u, "input_tokens", 0) or 0
        usage["output_tokens"] += getattr(u, "output_tokens", 0) or 0
        if getattr(resp, "stop_reason", None) == "refusal":
            usage["refusals"] += 1
            raise RuntimeError("모델이 응답을 거절했다 (refusal)")   # enrich 는 실패 1회로 센다
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")

    call.usage = usage
    call.model = mid
    return call
