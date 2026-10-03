import json

import pytest

from app.ai.profile import build_prompt, extract_profile

TEXT = """김가상
연락처 [전화번호] · [이메일]
기술 스택
Python, FastAPI, React
프로젝트
캠퍼스 빈 강의실 찾기 앱
2025.03 ~ 2025.06 · 백엔드 개발
수상
2025 가상대학교 캠퍼스 해커톤 최우수상 (2025.11)
활동
교내 개발 동아리 예시코드 부원 (2024.03 ~ 현재)
"""
GOOD = {
    "skills": ["Python", "FastAPI", "React"],
    "tags": ["개발"],
    "projects": [{"title": "캠퍼스 빈 강의실 찾기 앱", "role": "백엔드 개발", "period": "2025.03 ~ 2025.06",
                  "evidence": "캠퍼스 빈 강의실 찾기 앱\n2025.03 ~ 2025.06"}],   # PDF 줄바꿈을 넘는 근거
    "awards": [{"title": "캠퍼스 해커톤 최우수상", "date": "2025.11",
                "evidence": "2025 가상대학교 캠퍼스 해커톤 최우수상 (2025.11)"}],
    "activities": [{"title": "예시코드", "period": "2024.03 ~ 현재", "evidence": "교내 개발 동아리 예시코드 부원"}],
}
KEYS = ["status", "skills", "tags", "projects", "awards", "activities"]


def fake(*answers):
    calls = list(answers)
    return lambda prompt: calls.pop(0)


def ans(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False)


def test_good_answer_is_done():
    out = extract_profile(TEXT, fake(ans(GOOD)))
    assert list(out) == KEYS and out["status"] == "done"
    assert list(out["projects"][0]) == ["title", "role", "period", "evidence"]
    assert out["projects"][0]["period"] == "2025.03 ~ 2025.06"
    assert len(out["awards"]) == 1 and len(out["activities"]) == 1
    assert out["skills"] == ["Python", "FastAPI", "React"] and out["tags"] == ["개발"]


def test_retry_once_then_done():
    out = extract_profile(TEXT, fake("말로 대답함", "```json\n" + ans(GOOD) + "\n```"))
    assert out["status"] == "done"


def test_two_bad_answers_fail_empty():
    out = extract_profile(TEXT, fake("{}", ans({**GOOD, "projects": [{"title": "근거 없음"}]})))
    assert out == {"status": "failed", "skills": [], "tags": [], "projects": [], "awards": [], "activities": []}


def test_evidence_not_in_text_drops_only_that_item():
    bad = {**GOOD, "projects": [{"title": "AI 면접 연습 서비스", "evidence": "AI 면접 연습 서비스를 만들었다"}]}
    out = extract_profile(TEXT, fake(ans(bad)))
    assert out["projects"] == [] and len(out["awards"]) == 1


def test_invented_title_on_real_evidence_is_dropped():
    bad = {**GOOD, "awards": [{"title": "2025 전국 공모전 대상", "date": None, "evidence": "(2025.11)"},
                              {"title": "2025.11", "date": None, "evidence": "최우수상 (2025.11)"}]}
    out = extract_profile(TEXT, fake(ans(bad)))
    assert out["awards"] == []


def test_short_evidence_is_dropped():
    bad = {**GOOD, "activities": [{"title": "부원", "period": None, "evidence": "부원"}]}
    assert extract_profile(TEXT, fake(ans(bad)))["activities"] == []


def test_fields_not_in_text_become_null():
    odd = {**GOOD, "projects": [{**GOOD["projects"][0], "role": "프론트엔드 리드", "period": "2024.01 ~ 2024.02"}]}
    p = extract_profile(TEXT, fake(ans(odd)))["projects"][0]
    assert p["role"] is None and p["period"] is None and p["title"] == "캠퍼스 빈 강의실 찾기 앱"


def test_skills_must_stand_alone_in_text():
    odd = {**GOOD, "skills": ["Python", "python", "Kotlin", "R", "fastapi"]}
    assert extract_profile(TEXT, fake(ans(odd)))["skills"] == ["Python", "fastapi"]


def test_tags_only_from_list():
    odd = {**GOOD, "tags": ["개발", "없는태그", "개발", "AI·데이터"]}
    assert extract_profile(TEXT, fake(ans(odd)))["tags"] == ["개발", "AI·데이터"]


def test_tags_cleared_when_nothing_is_grounded():
    bad = {"skills": ["Kotlin"], "tags": ["개발"], "projects": [], "awards": [],
           "activities": [{"title": "지어낸 활동", "evidence": "지어낸 활동 2026"}]}
    out = extract_profile(TEXT, fake(ans(bad)))
    assert out["status"] == "done" and out["tags"] == [] and out["activities"] == []


def test_duplicate_items_dropped():
    dup = {**GOOD, "projects": GOOD["projects"] * 2}
    assert len(extract_profile(TEXT, fake(ans(dup)))["projects"]) == 1


def test_name_and_contact_fields_are_never_returned():
    leaky = {**GOOD, "name": "김가상", "phone": "[전화번호]", "email": "[이메일]"}
    assert list(extract_profile(TEXT, fake(ans(leaky)))) == KEYS


def test_server_masks_again_before_llm():
    seen = []

    def llm(prompt):
        seen.append(prompt)
        return ans(GOOD)

    extract_profile(TEXT + "\n연락처 010-0000-0000 a.b@example.com 학번: 20990001", llm)
    assert "010-0000-0000" not in seen[0] and "example.com" not in seen[0] and "20990001" not in seen[0]
    assert "[전화번호]" in seen[0]


def test_scanned_pdf_does_not_call_llm():
    def llm(prompt):
        raise AssertionError("글자가 없으면 AI를 부르지 않는다")

    assert extract_profile(" \n [전화번호] \n", llm)["status"] == "no_text"


def test_ligature_and_dash_variants_still_match():
    text = TEXT + "\nLLM \ufb01ne-tuning 실험\n2025.07 \u2013 2025.08\n"
    item = {"title": "LLM fine-tuning 실험", "role": None, "period": "2025.07 - 2025.08",
            "evidence": "LLM fine-tuning 실험 2025.07 - 2025.08"}
    out = extract_profile(text, fake(ans({**GOOD, "projects": [item]})))
    assert out["projects"][0]["period"] == "2025.07 - 2025.08"


def test_prompt_has_tags_and_keeps_user_text_literal():
    p = build_prompt("본문에 {{tags}} 라고 적힌 포트폴리오")
    assert "AI·데이터" in p and "{{text}}" not in p
    assert "본문에 {{tags}} 라고 적힌" in p


def test_gold_portfolios_survive_masking_and_grounding():
    # 실제 PDF(fitz 추출)에서: 가린 뒤 연락처 원문이 0건이고, 정답을 LLM 답으로 넣으면 하나도 버려지지 않는다.
    pytest.importorskip("fitz")
    from app.ai.eval.run_profile_eval import gold_as_answer, load_cases

    cases = load_cases()
    assert len(cases) == 3
    for c in cases:
        gold, exp = c["gold"], c["gold"]["expected"]
        assert c["maskCount"] == gold["mask"]["count"], gold["id"]
        assert not [h for h in gold["mask"]["hidden"] if h in c["masked"]], gold["id"]
        assert all(k in c["masked"] for k in gold["mask"]["kept"]), gold["id"]
        out = extract_profile(c["masked"], fake(ans(gold_as_answer(gold))))
        assert out["skills"] == exp["skills"] and out["tags"] == exp["tags"], gold["id"]
        for kind in ("projects", "awards", "activities"):
            want = [{k: v for k, v in it.items() if k != "key"} for it in exp[kind]]
            assert out[kind] == want, (gold["id"], kind)
