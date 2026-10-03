import json

from app.ai.enrich import enrich

ANS = {"categories": ["특강·교육"], "tags": [], "summary": None, "audience": None, "apply": None}


def run(poster, date, evidence, title="교육 신청 안내(~선착순 마감)", posted="2026-09-01"):
    notice = {"id": "kmu-6-1", "postedAt": posted, "title": title, "body": "", "posterText": poster}
    ans = {**ANS, "deadline": {"date": date, "time": None, "evidence": evidence}}
    return enrich(notice, lambda p: json.dumps(ans, ensure_ascii=False))["deadline"]


def test_course_period_end_is_not_a_deadline():
    # 2026-10-03 실호출에서 틀린 포스터 (kmu-6-12331): 수강 기간 끝을 마감으로 잡았다
    poster = "신청 기간 | 선착순 모집 마감\n수강 기간 | 2026.09.21.(월) ~ 12.20.(일)"
    assert run(poster, "2026-12-20", "2026.09.21.(월) ~ 12.20.(일)") is None


def test_label_inside_evidence_is_checked():
    assert run("교육 기간 10.13 ~ 10.20", "2026-10-20", "교육 기간 10.13 ~ 10.20") is None


def test_apply_period_is_kept():
    dl = run("신청기간\n9. 1.(화) ~ 9. 23.(수) 17:00", "2026-09-23", "9. 1.(화) ~ 9. 23.(수) 17:00")
    assert dl["date"] == "2026-09-23" and dl["source"] == "poster"


def test_nearest_label_wins():
    # 교육 기간 뒤에 신청 마감이 오면 신청 마감 날짜는 남긴다
    poster = "교육기간 10.13~10.20, 신청마감 10.11"
    assert run(poster, "2026-10-11", "교육기간 10.13~10.20, 신청마감 10.11")["date"] == "2026-10-11"
    assert run(poster, "2026-10-20", "교육기간 10.13~10.20, 신청마감 10.11") is None


def test_no_label_is_not_judged():
    assert run("2026 하반기 채용 09.01 - 09.22", "2026-09-22", "09.01 - 09.22")["date"] == "2026-09-22"
