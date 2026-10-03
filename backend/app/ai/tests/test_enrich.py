import json
from pathlib import Path

from app.ai.enrich import _evidence_supports, _squash, build_prompt, enrich, parse_json

NOTICE = {
    "id": "kmu-4-1", "boardId": "4", "board": "학사", "postedAt": "2026-10-03",
    "title": "2026학년도 2학기 다전공 신청",
    "body": "1. 신청기간 : 2026.10.13.(화) 10:00 ~ 10.16.(금) 17:00\n2. 대상 : 3~7차 학기 재학생",
}
GOOD = {
    "categories": ["학사"], "tags": [], "summary": ["다전공 신청 안내"],
    "deadline": {"date": "2026-10-16", "time": "17:00", "evidence": "10.16.(금) 17:00"},
    "audience": None, "apply": "온라인 신청",
}


def fake(*answers):
    calls = list(answers)
    return lambda prompt: calls.pop(0)


def test_good_answer_is_done():
    out = enrich(NOTICE, fake(json.dumps(GOOD, ensure_ascii=False)))
    assert out["status"] == "done"
    assert out["deadline"]["date"] == "2026-10-16" and out["deadline"]["source"] == "ai"


def test_code_fence_is_parsed():
    raw = "```json\n" + json.dumps(GOOD, ensure_ascii=False) + "\n```"
    assert parse_json(raw)["categories"] == ["학사"]


def test_retry_once_then_done():
    out = enrich(NOTICE, fake("말로 대답함", json.dumps(GOOD, ensure_ascii=False)))
    assert out["status"] == "done"


def test_two_bad_answers_fail_with_board_default():
    out = enrich(NOTICE, fake("{}", "아님"))
    assert out["status"] == "failed"
    assert out["categories"] == ["학사"]


def test_evidence_not_in_text_is_dropped():
    bad = {**GOOD, "deadline": {"date": "2026-10-20", "time": None, "evidence": "10월 20일까지"}}
    out = enrich(NOTICE, fake(json.dumps(bad, ensure_ascii=False)))
    assert out["deadline"] is None  # 근거가 원문에 없고 제목에도 마감 표기가 없다


def test_short_evidence_without_month_day_is_dropped():
    # 검수에서 찾은 구멍: 근거가 "10" 처럼 짧으면 지어낸 날짜가 통과했다
    bad = {**GOOD, "deadline": {"date": "2026-12-31", "time": None, "evidence": "10"}}
    out = enrich(NOTICE, fake(json.dumps(bad, ensure_ascii=False)))
    assert out["deadline"] is None


def test_gold_evidence_passes_month_day_check():
    gold = json.loads((Path(__file__).parents[1] / "eval" / "gold_enrich.json").read_text(encoding="utf-8"))
    for it in gold["items"]:
        dl = it["expected"]["deadline"]
        if dl:
            assert _evidence_supports(dl, _squash(dl["evidence"])), it["id"]


def test_prd_shaped_notice_without_board_id():
    notice = {"id": "kmu-7-12387", "source": {"id": "kmu-scholarship", "name": "장학공지"},
              "title": "장학생 선발", "postedAt": "2026-09-15", "body": ""}
    out = enrich(notice, fake("{}", "{}"))
    assert out["categories"] == ["장학"]


def test_title_fallback_when_ai_has_no_deadline():
    notice = {**NOTICE, "title": "현대그룹 신입 채용(~9/22)", "boardId": "11", "body": ""}
    out = enrich(notice, fake(json.dumps({**GOOD, "deadline": None}, ensure_ascii=False)))
    assert out["deadline"]["date"] == "2026-09-22" and out["deadline"]["source"] == "title"


def test_unknown_category_and_tag_dropped():
    odd = {**GOOD, "categories": ["없는분야"], "tags": ["AI·데이터", "없는태그"]}
    out = enrich(NOTICE, fake(json.dumps(odd, ensure_ascii=False)))
    assert out["categories"] == ["학사"]
    assert out["tags"] == ["AI·데이터"]


def test_prompt_marks_image_notice():
    p = build_prompt({**NOTICE, "body": ""})
    assert "포스터 이미지" in p and "{{" not in p
