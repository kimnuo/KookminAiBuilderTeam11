from bs4 import BeautifulSoup

from app.ai.text import html_to_text, is_short_body, title_deadline


def test_inline_spans_stay_on_one_line():
    html = "<div><p>1. 기간 : <span>2026.10.13.</span>(<span>화</span>) 10:00 ~ 16.(<b>금</b>) 17:00</p><p>2. 대상</p></div>"
    text = html_to_text(BeautifulSoup(html, "html.parser").div)
    assert "1. 기간 : 2026.10.13.(화) 10:00 ~ 16.(금) 17:00" in text.split("\n")
    assert "2. 대상" in text.split("\n")


def test_br_and_table_cells():
    html = "<div>접수<br>마감<table><tr><td>A</td><td>B</td></tr></table></div>"
    text = html_to_text(BeautifulSoup(html, "html.parser").div)
    assert text.split("\n")[:2] == ["접수", "마감"]
    assert "A B" in text


def test_title_deadline_slash_and_dot():
    assert title_deadline("KAI 현장실습 모집(~10/15)", "2026-10-01")["date"] == "2026-10-15"
    assert title_deadline("계약직 채용 안내(~10.12.)", "2026-10-02")["date"] == "2026-10-12"
    assert title_deadline("수강생 모집(~10/2일 까지)", "2026-09-22")["date"] == "2026-10-02"


def test_title_range_is_event_not_deadline():
    assert title_deadline("청년 상생마켓(10/2~10/4)", "2026-09-22") is None


def test_title_without_date():
    assert title_deadline("온라인 교육 신청 안내(~선착순 마감)", "2026-09-02") is None
    assert title_deadline("장학생 선발 공고", "2026-09-02") is None


def test_title_deadline_rolls_to_next_year():
    assert title_deadline("동계 모집(~1/5)", "2026-12-20")["date"] == "2027-01-05"


def test_short_body():
    assert is_short_body("")
    assert is_short_body("신청링크 <<< 클릭")
    assert not is_short_body("가" * 120)
