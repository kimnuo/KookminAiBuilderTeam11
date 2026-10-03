"""평가 스크립트가 LLM 을 고르는 곳.

gateway = 학교 AI 게이트웨이의 Claude (llm_claude), bedrock = AWS Bedrock (예비).
task 는 classify / poster / profile / requirements 중 하나이고, 모델은 backend/.env 에서 읽는다.
"""

PAID = ("gateway", "bedrock")


def make_llm(kind: str, task: str = "classify", max_tokens: int = 4000):
    if kind == "gateway":
        from app.ai.llm_claude import make_claude_llm
        return make_claude_llm(task=task, max_tokens=max_tokens)
    if kind == "bedrock":
        from app.ai.llm_bedrock import make_bedrock_llm
        return make_bedrock_llm(max_tokens=max_tokens)
    raise ValueError(f"모르는 LLM 종류: {kind}")
