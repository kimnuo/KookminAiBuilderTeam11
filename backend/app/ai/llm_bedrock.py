"""AWS Bedrock Converse API 로 LLM 을 부르는 함수를 만든다.

환경변수 (.env, 커밋 금지)
- BEDROCK_MODEL_ID : 콘솔에서 확인한 모델 ID 또는 추론 프로필 ID (예: GPT-5.6 Luna)
- AWS_REGION       : 모델을 쓸 수 있는 리전
- AWS 자격 증명    : boto3 기본 방식(AWS_ACCESS_KEY_ID 등 또는 프로필)

요청 형식(modelId, messages, inferenceConfig.maxTokens)은 boto3 공식 레퍼런스(bedrock-runtime converse)에서 확인했다.
응답 구조(output.message.content[].text)와 usage 필드 이름은 확인한 발췌에 완전히 나오지 않아 **미확인**이다.
첫 실호출 때 응답을 찍어 보고 맞춘다. 추론(reasoning) 모델이면 maxTokens 안에서 텍스트가 비는지도 본다.
"""
import os


def make_bedrock_llm(model_id: str | None = None, region: str | None = None, max_tokens: int = 1500):
    import boto3  # 실제로 쓸 때만 불러온다 (테스트는 boto3 없이 돈다)

    client = boto3.client("bedrock-runtime", region_name=region or os.environ["AWS_REGION"])
    mid = model_id or os.environ["BEDROCK_MODEL_ID"]
    usage = {"calls": 0, "inputTokens": 0, "outputTokens": 0}

    def call(prompt: str) -> str:
        resp = client.converse(
            modelId=mid,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": max_tokens},
        )
        u = resp.get("usage") or {}
        usage["calls"] += 1
        usage["inputTokens"] += u.get("inputTokens", 0)
        usage["outputTokens"] += u.get("outputTokens", 0)
        blocks = resp["output"]["message"]["content"]
        return "".join(b.get("text", "") for b in blocks)

    call.usage = usage
    return call
