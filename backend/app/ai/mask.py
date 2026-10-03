"""포트폴리오 글에서 전화번호·이메일·학번 모양의 글자를 가린다 (PRD 6-1절 원칙 2).

브라우저(프론트)가 먼저 가려서 보내고, 서버도 AI를 부르기 전에 한 번 더 가린다.
패턴은 config/mask_patterns.json 한 곳에 두고 프론트 참조 구현(mask_reference.js)과 같이 쓴다.
이름, 생년월일, 개인 사이트 주소는 가리지 못한다. 한계는 JSON 의 note 에 적었다.
"""
import json
import re
from pathlib import Path

_CFG = json.loads((Path(__file__).parent / "config" / "mask_patterns.json").read_text(encoding="utf-8"))
PATTERNS = [
    {"name": p["name"], "re": re.compile(p["regex"]), "keep": p.get("keep", 0), "replace": p["replace"]}
    for p in _CFG["patterns"]
]


def _replacer(pattern: dict):
    keep, token = pattern["keep"], pattern["replace"]
    return lambda m: ((m.group(keep) or "") if keep else "") + token


def mask_contacts(text: str) -> tuple[str, int]:
    """(가린 글, 가린 개수)를 돌려준다. 이미 가린 글을 다시 넣으면 개수는 0이다."""
    out, total = text or "", 0
    for p in PATTERNS:
        out, n = p["re"].subn(_replacer(p), out)
        total += n
    return out, total
