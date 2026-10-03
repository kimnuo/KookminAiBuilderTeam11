import json
import re
from pathlib import Path

import pytest

from app.ai.eval.run_requirements_eval import score_one, summarize
from app.ai.requirements import FIELD_KEYS, build_prompt, clean, extract_requirements

EVAL = Path(__file__).parents[1] / "eval"
GOLD = json.loads((EVAL / "gold_requirements.json").read_text(encoding="utf-8"))

NOTICE = {
    "id": "kmu-7-1", "title": "가나재단 장학생 선발 공고", "postedAt": "2026-09-15",
    "body": "ㅇ 제목양식: 가나재단(학번, 이름)\n제출서류\n- 재학증명서\n- 성적증명서(해당자에 한함)\n"
            "ㅇ 포트폴리오 링크 기재(선택)\n문의: 학생지원팀",
}
GOOD = {
    "fields": [
        {"key": "studentId", "label": None, "required": True, "evidence": "제목양식: 가나재단(학번, 이름)"},
        {"key": "name", "required": True, "evidence": "제목양식: 가나재단(학번, 이름)"},
        {"key": "portfolioUrl", "required": False, "evidence": "포트폴리오 링크 기재(선택)"},
    ],
    "documents": [
        {"name": "재학증명서", "condition": None, "evidence": "- 재학증명서"},
        {"name": "성적증명서", "condition": "해당자에 한함", "evidence": "성적증명서(해당자에 한함)"},
    ],
}


def fake(*answers):
    calls = list(answers)
    return lambda prompt: calls.pop(0)


def run(data, notice=NOTICE):
    return extract_requirements(notice, fake(json.dumps(data, ensure_ascii=False)))


def test_good_answer_is_done_in_prd_shape():
    out = run(GOOD)
    assert out["status"] == "done"
    assert [f["key"] for f in out["fields"]] == ["studentId", "name", "portfolioUrl"]
    assert "label" not in out["fields"][0]  # 고정 키는 label 이 없다 (PRD 6-1절 예시 모양)
    assert out["documents"][1] == {"name": "성적증명서", "condition": "해당자에 한함",
                                   "evidence": "성적증명서(해당자에 한함)"}


def test_retry_once_then_done():
    out = extract_requirements(NOTICE, fake("말로 대답함", json.dumps(GOOD, ensure_ascii=False)))
    assert out["status"] == "done"


def test_two_bad_answers_fail_with_empty_lists():
    out = extract_requirements(NOTICE, fake("{}", '{"fields": [], "documents": [{"name": "x"}]}'))
    assert out == {"status": "failed", "fields": [], "documents": []}


def test_required_must_be_boolean():
    bad = {**GOOD, "fields": [{**GOOD["fields"][0], "required": "yes"}]}
    out = extract_requirements(NOTICE, fake(json.dumps(bad), json.dumps(bad)))
    assert out["status"] == "failed"


def test_evidence_not_in_text_drops_only_that_item():
    bad = {**GOOD, "documents": GOOD["documents"] + [
        {"name": "졸업증명서", "condition": None, "evidence": "졸업증명서 1부"}]}
    out = run(bad)
    assert [d["name"] for d in out["documents"]] == ["재학증명서", "성적증명서"]


def test_whitespace_differences_in_evidence_are_ignored():
    data = {"fields": [], "documents": [{"name": "재학 증명서", "condition": None, "evidence": "-  재학 증명서"}]}
    assert run(data)["documents"][0]["name"] == "재학 증명서"


def test_blank_evidence_is_dropped():
    data = {"fields": [{"key": "name", "required": True, "evidence": "   "}], "documents": []}
    out = run(data)
    assert out["status"] == "done" and out["fields"] == []


def test_unknown_key_drops_only_that_item():
    data = {**GOOD, "fields": [{"key": "gpa", "required": True, "evidence": "제목양식: 가나재단(학번, 이름)"},
                               GOOD["fields"][1]]}
    out = run(data)
    assert out["status"] == "done"
    assert [f["key"] for f in out["fields"]] == ["name"]


def test_document_name_not_in_evidence_is_dropped():
    # 근거는 원문에서 복사했지만 이름을 지어낸 경우
    data = {"fields": [], "documents": [{"name": "주민등록등본", "condition": None, "evidence": "- 재학증명서"}]}
    assert run(data)["documents"] == []


def test_other_label_must_be_in_evidence():
    ok = {"key": "other", "label": "포트폴리오 링크", "required": False, "evidence": "포트폴리오 링크 기재(선택)"}
    made_up = {"key": "other", "label": "희망 근무지", "required": True, "evidence": "포트폴리오 링크 기재(선택)"}
    out = run({"fields": [ok, made_up], "documents": []})
    assert out["fields"] == [ok]


def test_duplicates_keep_first():
    data = {"fields": [GOOD["fields"][1], {**GOOD["fields"][1], "required": False}],
            "documents": [GOOD["documents"][0], {**GOOD["documents"][0], "name": "재학 증명서"}]}
    out = run(data)
    assert len(out["fields"]) == 1 and out["fields"][0]["required"] is True
    assert len(out["documents"]) == 1


def test_title_counts_as_source_text():
    data = {"fields": [], "documents": [{"name": "장학생 선발", "condition": None, "evidence": "장학생 선발 공고"}]}
    assert run(data)["documents"][0]["name"] == "장학생 선발"


def test_prompt_has_only_notice_text_not_profile_values():
    # PRD 6-1절 원칙 1·2: 개인정보 값은 AI 로 보내지 않는다
    notice = {**NOTICE, "profile": {"name": "가상인물", "phone": "010-0000-1234"}, "phone": "010-0000-1234"}
    p = build_prompt(notice)
    assert NOTICE["body"] in p and NOTICE["title"] in p
    assert "010-0000-1234" not in p and "가상인물" not in p
    assert "{{" not in p and "studentId" in p and "other" in p


def test_braces_in_body_are_not_substituted():
    p = build_prompt({**NOTICE, "body": "본문에 {{title}} 이라는 글자가 있다"})
    assert "본문에 {{title}} 이라는" in p


def test_prompt_marks_image_notice():
    assert "포스터 이미지" in build_prompt({**NOTICE, "body": ""})


# ---- 정답 초안 검사 (eval/gold_requirements.json)

def _cached(item):
    cache = EVAL / ".cache" / f"{item['id']}.txt"
    if not cache.exists():
        pytest.skip("eval/.cache 가 없다 (python -m app.ai.eval.fetch_bodies)")
    return {**item, "body": cache.read_text(encoding="utf-8")}


def test_gold_is_marked_as_unconfirmed_draft():
    for it in GOLD["items"]:
        assert it["confirmed"] is False and "표본 안 점수" in it["note"], it["id"]
        for f in it["expected"]["fields"]:
            assert f["key"] in FIELD_KEYS, it["id"]


def test_gold_has_no_contact_info():
    raw = json.dumps(GOLD, ensure_ascii=False)
    assert not re.findall(r"\d{2,3}[-)\s]\d{3,4}-\d{4}", raw)
    assert not re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", raw)


@pytest.mark.parametrize("item", GOLD["items"], ids=[it["id"] for it in GOLD["items"]])
def test_gold_survives_evidence_guard(item):
    # 정답을 그대로 LLM 답으로 넣으면 하나도 버려지지 않아야 한다 (근거가 원문 글자 그대로라는 기계 대조)
    notice = _cached(item)
    out = clean(item["expected"], notice)
    assert len(out["fields"]) == len(item["expected"]["fields"])
    assert len(out["documents"]) == len(item["expected"]["documents"])


@pytest.mark.parametrize("item", GOLD["items"], ids=[it["id"] for it in GOLD["items"]])
def test_gold_as_prediction_scores_full(item):
    notice = _cached(item)
    row = score_one(clean(item["expected"], notice), item["expected"])
    t = summarize([row])
    assert t["all"][0] == t["all"][1] and t["all"][2] == t["all"][3]


def test_scoring_counts_misses_and_extras():
    exp = {"fields": [{"key": "name", "required": True, "evidence": "e"},
                      {"key": "certificates", "required": True, "evidence": "e", "optional": True}],
           "documents": [{"name": "졸업증명서", "condition": None, "evidence": "e"},
                         {"name": "응시원서", "alt": ["응시지원서"], "condition": None, "evidence": "e"}]}
    pred = {"fields": [{"key": "name", "required": False, "evidence": "e"},
                       {"key": "email", "required": True, "evidence": "e"}],
            "documents": [{"name": "응시지원서(붙임1)", "condition": None, "evidence": "e"}]}
    row = score_one(pred, exp)
    assert row["fields"] == [1, 1, 1, 2]       # name 맞힘, optional 은 분모 제외, email 은 오답
    assert row["documents"] == [1, 2, 1, 1]    # alt 로 응시원서 맞힘, 졸업증명서 놓침
    assert row["required"] == [0, 1]
