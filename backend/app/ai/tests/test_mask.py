import json
import re
from pathlib import Path

import pytest

from app.ai.mask import PATTERNS, mask_contacts

CFG = json.loads((Path(__file__).parents[1] / "config" / "mask_patterns.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("raw", [
    "010-0000-0000", "01000000000", "010 0000 0000", "010.0000.0000", "010\u20130000\u20130000",
    "+82 10-0000-0000", "+821000000000", "02-000-0000", "(02) 000-0000", "031-000-0000", "070-0000-0000",
])
def test_phone_forms_masked(raw):
    assert mask_contacts(f"연락처 {raw} 입니다") == ("연락처 [전화번호] 입니다", 1)


def test_email_masked_whole_even_with_student_id_local_part():
    text, n = mask_contacts("메일 20990001@example.ac.kr, gasang.kim@example.com")
    assert (text, n) == ("메일 [이메일], [이메일]", 2)


@pytest.mark.parametrize("raw, masked", [
    ("학번: 20990001", "학번: [학번]"),
    ("학번 20990512", "학번 [학번]"),               # 날짜 모양이어도 라벨이 있으면 가린다
    ("Student ID: 20990003", "Student ID: [학번]"),
    ("student no. 2099000123", "student no. [학번]"),
    ("시각디자인학과 20990002", "시각디자인학과 [학번]"),   # 라벨 없음. 뒤 4자리(0002)가 날짜가 아니다
])
def test_student_id_masked(raw, masked):
    assert mask_contacts(raw) == (masked, 1)


@pytest.mark.parametrize("raw", [
    "작성일 20261003", "20250131", "2026.10.03", "2026-10-03", "2025.03 ~ 2025.06", "2025.02.15",
    "TOEIC 905", "GPA 4.12/4.5", "1,234,000원", "v1.2.3", "21학번", "1588-0000", "0.20231234",
])
def test_dates_and_other_numbers_kept(raw):
    assert mask_contacts(raw) == (raw, 0)


def test_known_limits():
    # 못 가리는 것: 이름, 개인 사이트 주소, 라벨 없이 날짜처럼 읽히는 학번(뒤 4자리 0512)
    raw = "김가상 github.com/example-gasang 20990512"
    assert mask_contacts(raw) == (raw, 0)
    # 잘못 가리는 것: 쉼표 없는 8자리 금액의 뒤 4자리가 날짜가 아니면 학번으로 본다
    assert mask_contacts("20231234원") == ("[학번]원", 1)


def test_count_and_masking_twice_is_noop():
    text, n = mask_contacts("010-0000-0000 / a@example.com / 학번: 20990001 / 작성일 20261003")
    assert n == 3 and "20261003" in text
    assert mask_contacts(text) == (text, 0)


def test_empty_input():
    assert mask_contacts("") == ("", 0)
    assert mask_contacts(None) == ("", 0)


def test_patterns_are_portable_to_javascript():
    # 프론트(mask_reference.js)가 같은 JSON 을 RegExp 로 읽는다. 두 엔진이 다르게 읽는 문법을 막는다.
    banned = ["(?P", "\\d", "\\w", "\\b", "\\s", "(?i", "(?m", "(?s", "(?x", "(?>"]
    for p in CFG["patterns"]:
        assert not [b for b in banned if b in p["regex"]], p["name"]
        assert re.compile(p["regex"]).groups >= p.get("keep", 0), p["name"]


def test_email_runs_before_student_id():
    names = [p["name"] for p in PATTERNS]
    assert names.index("email") < names.index("student_id_labeled") < names.index("student_id_bare")
