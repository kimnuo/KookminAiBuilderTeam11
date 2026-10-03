"""정답셋 공지의 본문을 받아 eval/.cache/ 에 저장한다 (평가 전용, 수집기 아님).

실행: cd backend && python -m app.ai.eval.fetch_bodies
- 1.5초 간격으로 받는다 (학교 서버 부하).
- 상세 페이지 머리의 담당자 실명·전화는 저장하지 않는다. 본문(div.view_cont)만 저장한다.
- .cache/ 는 커밋하지 않는다 (본문에 담당자 연락처가 들어 있을 수 있다).
"""
import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from app.ai.text import html_to_text

HERE = Path(__file__).parent
GOLD = HERE / "gold_enrich.json"
CACHE = HERE / ".cache"
UA = {"User-Agent": "KMU-Notice-Hackathon-Team11/0.1"}


def fetch_body(url: str) -> str:
    r = requests.get(url, headers=UA, timeout=20)
    r.raise_for_status()
    r.encoding = "utf-8"
    el = BeautifulSoup(r.text, "html.parser").select_one("div.view_cont")
    return html_to_text(el) if el else ""


def main():
    CACHE.mkdir(exist_ok=True)
    items = json.loads(GOLD.read_text(encoding="utf-8"))["items"]
    for it in items:
        out = CACHE / f"{it['id']}.txt"
        if out.exists():
            continue
        out.write_text(fetch_body(it["url"]), encoding="utf-8")
        print("saved", it["id"])
        time.sleep(1.5)


if __name__ == "__main__":
    main()
