import random

from app.ai.enrich import failed
from app.ai.recommend import WEIGHTS, rank

TODAY = "2026-10-03"
# 지어낸 가상 사용자
USER = {"major": "소프트웨어학부", "year": 3, "categories": ["장학"], "tags": ["AI·데이터", "개발"]}


def notice(nid, tags=(), cats=(), deadline=None, time=None, posted="2026-10-01", audience=None):
    dl = {"date": deadline, "time": time, "evidence": "가상 근거"} if deadline else None
    ai = {"status": "done", "categories": list(cats), "tags": list(tags),
          "deadline": dl, "audience": audience}
    return {"id": nid, "postedAt": posted, "ai": ai}


def ids(out):
    return [o["id"] for o in out]


def test_more_tag_overlap_ranks_higher():
    out = rank([notice("none"), notice("one", tags=["AI·데이터"]),
                notice("two", tags=["개발", "AI·데이터", "디자인"])], USER, TODAY)
    assert ids(out) == ["two", "one", "none"]
    assert [o["score"] for o in out] == [2 * WEIGHTS["tag"], WEIGHTS["tag"], 0]


def test_expired_notice_is_dropped_but_today_and_null_stay():
    out = rank([notice("past", deadline="2026-10-02"), notice("today", deadline="2026-10-03"),
                notice("null")], USER, TODAY)
    assert ids(out) == ["today", "null"]


def test_tie_sorted_by_deadline_then_time_then_posted():
    # id 를 기대 순서와 반대 알파벳순으로 지어, 마지막 id 정렬만으로는 통과하지 못하게 한다
    out = rank([
        notice("c-late", deadline="2026-10-20"),
        notice("d-soon-no-time", deadline="2026-10-10"),
        notice("e-soon-10am", deadline="2026-10-10", time="10:00"),
        notice("b-null-new", posted="2026-10-02"),
        notice("a-null-old", posted="2026-09-30"),
    ], USER, TODAY)
    assert ids(out) == ["e-soon-10am", "d-soon-no-time", "c-late", "b-null-new", "a-null-old"]


def test_same_input_same_output_in_any_order():
    base = [notice(f"n{i}", tags=["개발"] if i % 2 else [], deadline=None if i % 3 else "2026-10-09")
            for i in range(8)]
    base += [notice("twin-b"), notice("twin-a")]  # 정렬 기준이 모두 같은 두 글
    first = rank(base, USER, TODAY)
    assert rank(base, USER, TODAY) == first
    for seed in range(5):
        shuffled = base[:]
        random.Random(seed).shuffle(shuffled)
        assert rank(shuffled, USER, TODAY) == first
    assert ids(first).index("twin-a") < ids(first).index("twin-b")


def test_reason_text_and_score():
    full = notice("full", tags=["AI·데이터", "개발"], cats=["장학", "학사"],
                  audience={"years": [3, 4], "majors": ["소프트웨어학부"], "text": "3·4학년"})
    out = rank([full, notice("single", tags=["AI·데이터"])], USER, TODAY)
    assert out[0]["reasons"] == [
        "내 태그 「AI·데이터」, 「개발」과 겹침",
        "관심 분야 「장학」",
        "3학년 대상",
        "내 전공 「소프트웨어학부」 대상",
    ]
    w = WEIGHTS
    assert out[0]["score"] == 2 * w["tag"] + w["category"] + w["yearMatch"] + w["majorMatch"]
    assert out[1]["reasons"] == ["내 태그 「AI·데이터」와 겹침"]


def test_year_mismatch_is_kept_but_sinks_below_everything():
    wrong_year = notice("wrong-year", tags=["AI·데이터", "개발"], cats=["장학"],
                        audience={"years": [2, 1], "majors": ["소프트웨어학부"], "text": None})
    out = rank([wrong_year, notice("plain")], USER, TODAY)
    assert ids(out) == ["plain", "wrong-year"]
    assert "1·2학년 대상 (내 학년 아님)" in out[1]["reasons"]
    assert out[1]["score"] < 0


def test_year_mismatch_penalty_outweighs_max_positive_score():
    # enrich 는 태그를 3개까지만 남긴다. 학년 불일치 글은 어떤 글보다도 아래여야 한다.
    w = WEIGHTS
    assert w["yearMismatch"] + 3 * w["tag"] + w["category"] + w["majorMatch"] < 0


def test_unknown_year_or_no_year_target_is_neutral():
    aud = {"years": [1], "majors": [], "text": None}
    no_year_user = {**USER, "year": None}
    assert rank([notice("a", audience=aud)], no_year_user, TODAY)[0] == {"id": "a", "score": 0, "reasons": []}
    open_to_all = notice("b", audience={"years": [], "majors": [], "text": "전 학년"})
    assert rank([open_to_all], USER, TODAY)[0]["score"] == 0


def test_year_given_as_string_still_matches():
    out = rank([notice("a", audience={"years": [3], "majors": [], "text": None})],
               {**USER, "year": "3"}, TODAY)
    assert out[0]["reasons"] == ["3학년 대상"]


def test_major_match_is_lenient_and_mismatch_is_not_penalized():
    near = notice("near", audience={"years": [], "majors": ["소프트웨어학부 재학생"], "text": None})
    other = notice("other", audience={"years": [], "majors": ["경영학부"], "text": None})
    out = {o["id"]: o for o in rank([near, other], USER, TODAY)}
    assert out["near"]["score"] == WEIGHTS["majorMatch"]
    assert out["other"] == {"id": "other", "score": 0, "reasons": []}


def test_ai_null_or_pending_is_kept_with_zero_score():
    raw = {"id": "raw", "postedAt": "2026-10-02", "ai": None}
    pending = {"id": "pending", "postedAt": "2026-10-01", "ai": {"status": "pending"}}
    out = rank([pending, raw], USER, TODAY)
    assert out == [{"id": "raw", "score": 0, "reasons": []},
                   {"id": "pending", "score": 0, "reasons": []}]


def test_failed_ai_uses_board_default_and_title_deadline():
    # enrich.failed 가 실제로 만드는 모양을 그대로 쓴다
    kept = {"id": "kmu-7-1", "title": "장학생 선발 공고", "postedAt": "2026-09-20"}
    gone = {"id": "kmu-7-2", "title": "장학생 선발(~10/1)", "postedAt": "2026-09-20"}
    kept["ai"], gone["ai"] = failed(kept), failed(gone)
    assert gone["ai"]["status"] == "failed" and gone["ai"]["deadline"]["date"] == "2026-10-01"
    out = rank([kept, gone], USER, TODAY)
    assert ids(out) == ["kmu-7-1"]
    assert out[0]["reasons"] == ["관심 분야 「장학」"]


def test_bad_values_do_not_crash():
    odd = {"id": "odd", "postedAt": None,
           "ai": {"tags": "개발", "categories": None, "deadline": {"date": "2026-99-99", "time": 5},
                  "audience": {"years": ["삼학년", None], "majors": [None]}}}
    assert rank([odd], {}, TODAY) == [{"id": "odd", "score": 0, "reasons": []}]
    assert rank([odd], None, TODAY)[0]["score"] == 0
