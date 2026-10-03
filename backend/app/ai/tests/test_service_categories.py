import json
from pathlib import Path

from app.ai.enrich import CATEGORIES, SERVICE_MAP, enrich, service_categories

CFG = json.loads((Path(__file__).parents[1] / "config" / "categories.json").read_text(encoding="utf-8"))


def test_every_ai_category_maps_to_a_service_category():
    assert set(SERVICE_MAP) == set(CATEGORIES)
    assert set(SERVICE_MAP.values()) <= set(CFG["service"])


def test_service_names_match_backend_bytes():
    # 서버 core/config.py 의 CATEGORIES 와 같은 글자(가운뎃점 U+00B7)여야 화면 카드에 붙는다
    assert CFG["service"] == ["학사·생활", "졸업", "장학", "취업", "행사·대외활동", "기타"]


def test_mapping_dedupes_and_adds_graduation_from_title():
    assert service_categories(["특강·교육", "공모전·행사"], "AI 특강") == ["행사·대외활동"]
    assert service_categories(["학사"], "2026학년도 후기 졸업 사정 안내") == ["졸업", "학사·생활"]


def test_enrich_and_failed_both_carry_service_categories():
    notice = {"id": "kmu-11-1", "postedAt": "2026-09-01", "title": "신입 채용", "body": "본문"}
    ans = {"categories": ["채용·인턴"], "tags": [], "summary": None, "deadline": None, "audience": None, "apply": None}
    assert enrich(notice, lambda p: json.dumps(ans, ensure_ascii=False))["serviceCategories"] == ["취업"]
    assert enrich(notice, lambda p: "not json")["serviceCategories"] == ["취업"]   # failed → 게시판 기본값(11 → 채용·인턴)
