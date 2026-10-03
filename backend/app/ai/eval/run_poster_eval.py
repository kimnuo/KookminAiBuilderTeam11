"""본문이 포스터 이미지뿐인 공지(정답셋 textSource=image)에서 포스터를 읽어 본다.

실행 (backend 폴더에서)
  python -m app.ai.eval.run_poster_eval                 # 이미지 개수·크기만 본다 (LLM 안 부름, 비용 0)
  python -m app.ai.eval.run_poster_eval --yes [--limit N | --id kmu-11-12374]
      # 포스터 읽기(KMU_AI_MODEL_POSTER) + 분류(KMU_AI_MODEL_CLASSIFY) 실제 호출, 크레딧 차감

포스터 공지의 정답(마감일)은 아직 사람이 이미지를 보고 적지 않았다. 그래서 점수를 내지 않고
읽은 글과 뽑은 마감일을 찍어서 사람이 이미지와 대조한다.
"""
import argparse
import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from app.ai.enrich import enrich
from app.ai.poster import UA, download_images, image_urls, read_poster

HERE = Path(__file__).parent


def poster_items(limit, only=None):
    items = json.loads((HERE / "gold_enrich.json").read_text(encoding="utf-8"))["items"]
    items = [it for it in items if it["expected"]["textSource"] == "image" and (not only or it["id"] == only)]
    return items[:limit]


def fetch_images(url: str):
    r = requests.get(url, headers=UA, timeout=20)
    r.raise_for_status()
    r.encoding = "utf-8"
    view = BeautifulSoup(r.text, "html.parser").select_one("div.view_cont")
    time.sleep(1.5)
    return download_images(image_urls(view, url))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yes", action="store_true", help="유료 LLM 실제 호출에 동의")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--id", help="공지 하나만 (예: kmu-11-12374)")
    args = ap.parse_args()

    items = poster_items(args.limit, args.id)
    if not items:
        raise SystemExit(f"포스터 공지가 없다: {args.id}")
    vision = classify = None
    if args.yes:
        from app.ai.llm_claude import make_claude_llm
        vision = make_claude_llm(task="poster", max_tokens=2000, effort=None)
        classify = make_claude_llm(task="classify", max_tokens=4000)
    for it in items:
        cache = HERE / ".cache" / f"{it['id']}.txt"
        body = cache.read_text(encoding="utf-8") if cache.exists() else ""
        images = fetch_images(it["url"])
        print(f"\n## {it['id']} {it['title'][:40]}")
        print(f"   이미지 {len(images)}장, {sum(len(b) for _, b in images) // 1024}KB")
        if not args.yes:
            continue
        text = read_poster(images, vision)
        print("   포스터 글:", (text or "(없음)")[:400].replace("\n", " / "))
        ai = enrich({**it, "body": body, "posterText": text}, classify)
        print("   마감:", ai["deadline"], "| 분야:", ai["categories"], "| status:", ai["status"])
    if args.yes:
        print("\n사용량 poster:", vision.usage, "| classify:", classify.usage)
    else:
        print(f"\n포스터 {len(items)}건. 실제로 읽으려면 --yes (포스터 읽기 {len(items)}회 + 분류 최대 {len(items) * 2}회).")


if __name__ == "__main__":
    main()
