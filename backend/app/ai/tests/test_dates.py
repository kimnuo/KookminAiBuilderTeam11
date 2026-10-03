from datetime import date

from app.ai.dates import find_dates, parse_posted, resolve

P = date(2026, 10, 3)


def ends(text):
    return [resolve(t, P) for t in find_dates(text) if not t.is_range_start]


def test_full_range_end_only():
    assert ends("2026.10.13.(화) 10:00 ~ 10.16.(금) 17:00") == [date(2026, 10, 16)]


def test_day_only_range_end_inherits_month():
    assert ends("2026.10.13.(화) 10:00 ~ 16.(금) 17:00") == [date(2026, 10, 16)]


def test_two_digit_year_and_spaces():
    assert ends("26.10.01.(목) ~ 26.10.15.(목)") == [date(2026, 10, 15)]
    assert ends("2026. 08. 25.(화) ~ 2026. 09. 09.(수) 18:00") == [date(2026, 9, 9)]
    assert ends("26. 9. 16.(수) ~ 26. 9. 30.(수) 16:00까지") == [date(2026, 9, 30)]
    assert ends("2026-10-13 ~ 2026-10-16") == [date(2026, 10, 16)]


def test_mixed_separators_are_not_a_short_year():
    # 현대그룹 채용 포스터를 Haiku 가 읽은 표기 (2026-10-03 실호출). 2009-01-09 로 읽으면 안 된다
    toks = find_dates("09.01 - 09.22")
    assert [(t.year, t.month, t.day) for t in toks] == [(None, 9, 1), (None, 9, 22)]


def test_korean_month_day():
    assert ends("2026년 9월 20일(22:59까지)") == [date(2026, 9, 20)]
    assert ends("~ 2026년 10월 2일(금) 23:59까지") == [date(2026, 10, 2)]
    assert ends("9월 8일(화)까지 사전 신청") == [date(2026, 9, 8)]


def test_times_and_units_are_not_dates():
    assert ends("10:00 ~ 17:00") == []
    assert ends("지원금 ~2.5배, 경쟁률 3.5%") == []


def test_impossible_dates_dropped():
    assert ends("2026.13.16") == []
    assert ends("2026.10.00") == []


def test_fullwidth_normalized():
    assert ends("２０２６．１０．１６") == [date(2026, 10, 16)]


def test_parse_posted_shapes():
    assert parse_posted("2026-10-03T09:00:00+09:00") == P
    assert parse_posted("2026.10.03") is None
    assert parse_posted(None) is None
