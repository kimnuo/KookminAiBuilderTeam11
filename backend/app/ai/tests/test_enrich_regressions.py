"""verifier 반례 회귀 테스트 (2026-10-03). 고친 구멍이 다시 열리지 않게 막는다."""
import json
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from app.ai.dates import parse_posted
from app.ai.enrich import _evidence_supports, _squash, build_prompt, enrich, parse_json
from app.ai.text import html_to_text, title_deadline

BODY = "1. 신청기간 : 2026.10.13.(화) 10:00 ~ 10.16.(금) 17:00\n2. 대상 : 재학생"
EV = "2026.10.13.(화) 10:00 ~ 10.16.(금) 17:00"
NOTICE = {"id": "kmu-4-1", "boardId": "4", "postedAt": "2026-10-03", "title": "다전공 신청", "body": BODY}


def answer(date, time="17:00", evidence=EV, **extra):
    d = {"categories": ["학사"], "tags": [], "summary": ["안내"], "audience": None, "apply": None,
         "deadline": {"date": date, "time": time, "evidence": evidence}}
    d.update(extra)
    return lambda prompt: json.dumps(d, ensure_ascii=False)


def test_true_deadline_kept():
    out = enrich(NOTICE, answer("2026-10-16"))
    assert out["deadline"]["date"] == "2026-10-16" and out["deadline"]["time"] == "17:00"


@pytest.mark.parametrize("fake", ["2026-10-13", "2026-10-10", "2026-10-17", "1999-10-16"])
def test_fabricated_dates_from_same_evidence_dropped(fake):
    assert enrich(NOTICE, answer(fake))["deadline"] is None


@pytest.mark.parametrize("bad", ["2026-13-16", "2026-10-00", "２０２６-１０-１６", "2026-10-16\n"])
def test_impossible_or_non_ascii_dates_dropped(bad):
    assert enrich(NOTICE, answer(bad))["deadline"] is None


@pytest.mark.parametrize("t", ["09:00", "25:99"])
def test_time_not_in_evidence_becomes_null(t):
    out = enrich(NOTICE, answer("2026-10-16", time=t))
    assert out["deadline"]["date"] == "2026-10-16" and out["deadline"]["time"] is None


def test_llm_exception_is_failed_not_crash():
    def boom(prompt):
        raise TimeoutError("throttled")
    assert enrich(NOTICE, boom)["status"] == "failed"


@pytest.mark.parametrize("posted", [None, "", "2026.10.03", "2026-10-03T09:00:00+09:00"])
def test_posted_at_shapes_do_not_crash(posted):
    n = {**NOTICE, "title": "모집(~10/15)", "postedAt": posted}
    if posted is None:
        n.pop("postedAt")
    assert enrich(n, lambda p: "")["status"] == "failed"


def test_minor_schema_issues_are_cleaned_not_failed():
    out = enrich(NOTICE, answer("2026-10-16", categories=["학사", "학사", "장학", "특강·교육", "기타"],
                                summary=["", "  "], audience={"years": [0, 9], "majors": [""], "text": ""}, apply="  "))
    assert out["status"] == "done"
    assert out["categories"] == ["학사", "장학", "특강·교육"]
    assert out["summary"] is None and out["apply"] is None and out["audience"] is None


def test_audience_year_strings_become_ints():
    out = enrich(NOTICE, answer("2026-10-16", audience={"years": ["3", 4], "majors": [], "text": None}))
    assert out["audience"]["years"] == [3, 4]


def test_placeholders_in_notice_text_are_not_expanded():
    p = build_prompt({**NOTICE, "title": "제목 {{body}} 끝", "body": "본문 {{categories}}"})
    assert "제목 {{body}} 끝" in p and "본문 {{categories}}" in p


def test_parse_json_ignores_trailing_braces():
    assert parse_json('{"a": 1} 참고 {없음}') == {"a": 1}


def test_dl_dd_and_hr_are_separated():
    html = "<div><dl><dd>10.16</dd><dd>10.20</dd></dl>접수 마감 10.16<hr>20일 발표</div>"
    lines = html_to_text(BeautifulSoup(html, "html.parser").div).split("\n")
    assert "10.16" in lines and "10.20" in lines and "20일 발표" in lines


@pytest.mark.parametrize("title,posted,want", [
    ("지원금(~2.5배)", "2026-10-03", None), ("교재비 ~1/2 지원", "2026-10-03", None),
    ("행사(10/2 14:00~10/4)", "2026-10-03", None), ("모집(~10/15→10/20)", "2026-10-03", "2026-10-20"),
    ("모집(~10월 15일)", "2026-10-03", "2026-10-15"), ("모집（～10／15）", "2026-10-03", "2026-10-15"),
    ("모집(~2/29)", "2027-12-20", "2028-02-29"), ("모집(~10/15)", "2026.10.03", None),
])
def test_title_rule_counterexamples(title, posted, want):
    r = title_deadline(title, posted)
    assert (r and r["date"]) == want


def test_gold_evidence_resolves_to_gold_date():
    gold = json.loads((Path(__file__).parents[1] / "eval" / "gold_enrich.json").read_text(encoding="utf-8"))
    for it in gold["items"]:
        dl = it["expected"]["deadline"]
        if dl:
            assert _evidence_supports(dl, _squash(dl["evidence"]), parse_posted(it["postedAt"])), it["id"]


def test_gold_evidence_is_verbatim_in_cached_body():
    """본문 캐시가 있을 때만 돈다 (캐시는 커밋하지 않는다. fetch_bodies 로 받는다)."""
    eval_dir = Path(__file__).parents[1] / "eval"
    gold = json.loads((eval_dir / "gold_enrich.json").read_text(encoding="utf-8"))
    if not (eval_dir / ".cache").exists():
        pytest.skip("eval/.cache 없음")
    for it in gold["items"]:
        dl = it["expected"]["deadline"]
        if not dl:
            continue
        body = (eval_dir / ".cache" / f"{it['id']}.txt").read_text(encoding="utf-8")
        hay = _squash(it["title"]) if dl["source"] == "title" else _squash(body)
        assert _squash(dl["evidence"]) in hay, it["id"]
