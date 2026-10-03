import json
from types import SimpleNamespace

from bs4 import BeautifulSoup

from app.ai.enrich import build_prompt, enrich
from app.ai.llm_claude import make_claude_llm
from app.ai.poster import download_images, image_urls, media_type, needs_poster, read_poster

PAGE = "https://www.kookmin.ac.kr/user/kmuNews/notice/7/12349/view.do"


def test_image_urls_absolute_dedup_no_data():
    html = ('<div class="view_cont"><img src="/upload/a.png"><img src="/upload/a.png">'
            '<img src="data:image/png;base64,xx"><img src="https://cdn.example.com/b.jpg"></div>')
    el = BeautifulSoup(html, "html.parser").div
    assert image_urls(el, PAGE) == ["https://www.kookmin.ac.kr/upload/a.png", "https://cdn.example.com/b.jpg"]


def test_media_type_sniffs_school_download_type():
    # 학교 서버: application/x-download + 확장자 없는 주소 (2026-10-03 실측)
    url = "https://kep.kookmin.ac.kr/com/cmsv/FileCtr/findUploadImg.do?fileNo=abc"
    assert media_type(url, "application/x-download;charset=UTF-8", b"\xff\xd8\xff\xe0...") == "image/jpeg"
    assert media_type(url, "application/x-download;charset=UTF-8", b"\x89PNG\r\n") == "image/png"
    assert media_type(url, "application/x-download;charset=UTF-8", b"%PDF-1.7") is None


def test_media_type_from_header_or_extension():
    assert media_type("x.bin", "image/png; charset=binary") == "image/png"
    assert media_type("https://h/x.JPG?v=1", None) == "image/jpeg"
    assert media_type("https://h/x.bmp", "application/octet-stream") is None


class FakeSession:
    def get(self, url, headers=None, timeout=None):
        if "bad" in url:
            raise OSError("down")
        return SimpleNamespace(content=b"\x89PNG..", headers={"Content-Type": "image/png"},
                               raise_for_status=lambda: None)


def test_download_skips_failures():
    assert download_images(["https://h/bad.png", "https://h/ok.png"], FakeSession()) == [("image/png", b"\x89PNG..")]


def test_read_poster_handles_empty_and_errors():
    assert read_poster([], lambda p, i: "x") is None
    assert read_poster([("image/png", b"1")], lambda p, i: "  ") is None

    def boom(p, i):
        raise RuntimeError("refusal")
    assert read_poster([("image/png", b"1")], boom) is None
    assert read_poster([("image/png", b"1")], lambda p, i: "접수 ~10/20") == "접수 ~10/20"


NOTICE = {"id": "kmu-7-12349", "postedAt": "2026-09-08", "title": "장학생 선발 공고", "body": ""}


def test_needs_poster_and_prompt_section():
    assert needs_poster(NOTICE)
    p = build_prompt({**NOTICE, "posterText": "신청기간 9.10.~9.25."})
    assert "[포스터 이미지에서 읽은 글자" in p and "신청기간 9.10.~9.25." in p


def test_deadline_from_poster_is_marked():
    ans = {"categories": ["장학"], "tags": [], "summary": None, "audience": None, "apply": None,
           "deadline": {"date": "2026-09-25", "time": None, "evidence": "9.10.~9.25."}}
    out = enrich({**NOTICE, "posterText": "신청기간 9.10.~9.25."}, lambda p: json.dumps(ans, ensure_ascii=False))
    assert out["deadline"]["date"] == "2026-09-25" and out["deadline"]["source"] == "poster"


class FakeClient:
    def __init__(self, stop="end_turn"):
        self.kwargs, self.stop = None, stop
        self.messages = self

    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(stop_reason=self.stop, usage=SimpleNamespace(input_tokens=10, output_tokens=5),
                               content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text="ok")])


def test_claude_llm_effort_only_for_models_that_take_it():
    c = FakeClient()
    assert make_claude_llm(client=c, model="claude-opus-5")("hi") == "ok"
    assert c.kwargs["output_config"] == {"effort": "low"}
    c2 = FakeClient()
    make_claude_llm(client=c2, model="claude-haiku-4-5")("hi", images=[("image/png", b"1")])
    assert "output_config" not in c2.kwargs
    blocks = c2.kwargs["messages"][0]["content"]
    assert blocks[0]["type"] == "image" and blocks[-1] == {"type": "text", "text": "hi"}


def test_claude_llm_refusal_raises_and_counts():
    llm = make_claude_llm(client=FakeClient(stop="refusal"), model="claude-opus-5")
    try:
        llm("hi")
        raise AssertionError("refusal 은 예외여야 한다")
    except RuntimeError:
        pass
    assert llm.usage["refusals"] == 1 and llm.usage["input_tokens"] == 10
