"""이력서·포트폴리오 글에서 이력을 뽑는다 (화면: 포트폴리오 PDF 로 채우기).

- 뽑는 규칙과 근거 검사는 현찬의 `app/ai/profile.py` 를 그대로 쓴다
- 화면이 기기에서 개인정보를 가린 글만 보낸다. 서버는 `mask_contacts` 로 한 번 더 가린다
- **본문을 로그에 남기지 않고 DB 에도 저장하지 않는다** (PRD 11절, docs/consent.md)
"""

import logging

from fastapi import APIRouter, HTTPException

from app.ai.gateway import complete_text
from app.ai.profile import empty, extract_profile
from app.core.schemas import ProfileAnalyzeRequest

router = APIRouter(tags=["profile"])
log = logging.getLogger(__name__)
MAX_CHARS = 60_000


@router.post(
    "/profile/analyze",
    summary="이력서 글 → 기술·태그·프로젝트·수상·활동",
    description="보낸 글은 저장하지 않는다. 근거가 원문에 없는 항목은 버린다.",
)
def analyze(body: ProfileAnalyzeRequest) -> dict:
    if len(body.text) > MAX_CHARS:
        raise HTTPException(status_code=413, detail="글이 너무 길어요.")
    try:
        return extract_profile(body.text, complete_text)
    except Exception as exc:  # 게이트웨이 오류도 화면에서는 "찾지 못했어요" 로 보이게 한다
        log.warning("이력 추출 실패: %s", type(exc).__name__)
        return empty("failed")
