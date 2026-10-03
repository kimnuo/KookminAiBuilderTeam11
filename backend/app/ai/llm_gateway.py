"""학교 AI 게이트웨이(ai.cs.kookmin.ac.kr, new-api) 공통 설정과 모델 목록 조회.

실제 호출은 llm_claude.py (Anthropic 공식 SDK, Claude 형식 /v1/messages) 가 한다.
확인한 것 (new-api 공식 문서, context7 /quantumnous/new-api-docs-v1)
- 모델 목록: GET {host}/v1/models, Authorization: Bearer <API 키>
  조회만 한다. 크레딧이 드는지는 문서에 언급이 없어 미확인, 안 들 것으로 추정.

환경변수 (backend/.env, 커밋 금지): KMU_AI_BASE_URL(호스트, 예: https://ai.cs.kookmin.ac.kr), KMU_AI_API_KEY
"""
import os
from pathlib import Path

import requests

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"   # backend/.env


def load_env(path: Path = ENV_FILE) -> None:
    """backend/.env 의 KEY=VALUE 를 환경변수로 읽는다. 이미 있는 값은 덮어쓰지 않는다."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if v.strip():
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def base_host() -> str:
    """게이트웨이 호스트. 끝의 /v1 은 떼어 낸다 (SDK 가 /v1/messages 를 붙인다)."""
    load_env()
    base = os.environ.get("KMU_AI_BASE_URL", "https://ai.cs.kookmin.ac.kr").rstrip("/")
    return base[:-3] if base.endswith("/v1") else base


def list_models() -> list[str]:
    load_env()
    key = os.environ.get("KMU_AI_API_KEY")
    if not key:
        raise RuntimeError("KMU_AI_API_KEY 가 없다. backend/.env 에 넣는다 (커밋 금지).")
    r = requests.get(f"{base_host()}/v1/models", headers={"Authorization": f"Bearer {key}"}, timeout=20)
    r.raise_for_status()
    return sorted(m.get("id", "") for m in r.json().get("data", []))


if __name__ == "__main__":
    # 모델 이름 확인용 (조회만. 크레딧은 안 들 것으로 추정): cd backend && python -m app.ai.llm_gateway
    for name in list_models():
        print(name)
