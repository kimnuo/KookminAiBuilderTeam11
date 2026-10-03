"""마감 근거 날짜 바로 앞의 항목 이름을 보고, 신청 마감이 아니라 다른 기간의 날짜인지 가린다 (코드, AI 아님).

근거 검사(enrich._evidence_supports)는 「그 날짜가 원문에 있나」만 본다. 그래서 포스터의
「신청 기간: 선착순 모집 마감 / 수강 기간: 9.21~12.20」에서 수강 기간 끝(12.20)을 마감으로
잡아도 통과했다(2026-10-03 실호출, kmu-6-12331). 날짜 바로 앞에서 가장 가까운 항목 이름이
수강·교육·행사 같은 기간이면 마감으로 치지 않는다. 신청·접수·모집·마감이면 마감으로 친다.
항목 이름이 없으면 판단하지 않는다(그대로 통과).
"""
import re

OTHER = ("수강", "교육", "행사", "활동", "운영", "계약", "근무", "연수", "강의", "봉사",
         "이용", "대여", "전시", "공연", "파견", "체류", "사업", "학습", "실습", "축제")
APPLY = ("신청", "접수", "모집", "제출", "지원", "등록", "예약", "응모", "서류")
_LABEL = re.compile(rf"({'|'.join(OTHER + APPLY)})(?:기간|일정|일시)|(마감|기한|까지)")
WINDOW = 12   # 근거 앞에서 볼 글자 수 (공백을 뺀 글 기준)


def is_other_period(text_sq: str, ev_sq: str, before_date_sq: str) -> bool:
    """text_sq: 공백을 뺀 원문, ev_sq: 공백을 뺀 근거, before_date_sq: 근거 안에서 그 날짜 앞까지(공백 뺌)."""
    i = text_sq.find(ev_sq)
    ctx = (text_sq[max(0, i - WINDOW):i] if i > 0 else "") + before_date_sq
    labels = _LABEL.findall(ctx)
    if not labels:
        return False
    kind, deadline_word = labels[-1]
    return bool(kind) and kind in OTHER and not deadline_word
