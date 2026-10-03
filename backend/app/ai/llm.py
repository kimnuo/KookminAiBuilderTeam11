"""LLM 호출을 이 파일 한 곳에 모은다. 배포 때 API 키 방식으로 바꾸면 여기만 고친다.

지금은 개발 서버의 Claude 구독 CLI(`claude -p`)를 부른다.
- 도구 끔(--tools ""), 세션 기록 안 남김(--no-session-persistence), 설정 파일 안 읽음
- 응답은 --json-schema 로 형식을 강제하고 structured_output 을 받는다
- 프로젝트 지침(CLAUDE.md)이 끼어들지 않게 레포 밖 임시 폴더에서 실행한다
"""

import json
import subprocess
import tempfile

from app.core.config import LLM_COMMAND, LLM_MODEL, LLM_TIMEOUT_SEC


class LlmError(Exception):
    pass


def complete_json(system: str, user: str, schema: dict) -> dict:
    cmd = [
        LLM_COMMAND, "-p",
        "--output-format", "json",
        "--model", LLM_MODEL,
        "--tools", "",
        "--no-session-persistence",
        "--setting-sources", "",
        "--system-prompt", system,
        "--json-schema", json.dumps(schema, ensure_ascii=False),
    ]
    try:
        proc = subprocess.run(
            cmd, input=user, capture_output=True, text=True,
            timeout=LLM_TIMEOUT_SEC, cwd=tempfile.gettempdir(),
        )
    except subprocess.TimeoutExpired as exc:
        raise LlmError(f"{LLM_TIMEOUT_SEC}초 안에 응답 없음") from exc
    return _parse(proc)


def _parse(proc: subprocess.CompletedProcess) -> dict:
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise LlmError(f"응답이 JSON 이 아님 (exit {proc.returncode}): {proc.stderr[:200]}") from exc
    if payload.get("is_error"):
        raise LlmError(f"LLM 오류: {str(payload.get('result'))[:200]}")
    output = payload.get("structured_output")
    if not isinstance(output, dict):
        raise LlmError("structured_output 없음")
    return output
