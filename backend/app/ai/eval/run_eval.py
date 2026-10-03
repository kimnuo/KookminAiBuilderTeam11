"""enrich 정확도를 정답셋(gold_enrich.json)으로 잰다.

실행 (backend 폴더에서, 먼저 fetch_bodies 로 본문 캐시를 만든다)
  python -m app.ai.eval.run_eval --llm baseline          # LLM 없이 제목 규칙만 (비용 0)
  python -m app.ai.eval.run_eval --llm gateway           # 학교 게이트웨이. 호출 수만 알려 주고 멈춘다
  python -m app.ai.eval.run_eval --llm gateway --yes     # 실제 호출 (크레딧 차감)
  python -m app.ai.eval.run_eval --llm bedrock           # 호출 수만 알려 주고 멈춘다
  python -m app.ai.eval.run_eval --llm bedrock --yes     # 실제 호출 (Bedrock 요금 발생)

채점
- 마감일: 날짜가 정답(또는 altDates)과 같으면 맞음. 둘 다 없음(null)도 맞음.
- 마감 시각: 정답에 시각이 있는 항목만 센다.
- 분야: 예측 분야 중 하나라도 정답 허용 목록에 있으면 맞음.
"""
import argparse
import json
from pathlib import Path

from app.ai.enrich import enrich
from app.ai.llm_factory import PAID, make_llm

HERE = Path(__file__).parent


def load_notices(limit: int | None):
    items = json.loads((HERE / "gold_enrich.json").read_text(encoding="utf-8"))["items"][:limit]
    notices = []
    for it in items:
        cache = HERE / ".cache" / f"{it['id']}.txt"
        if not cache.exists():
            raise SystemExit(f"본문 캐시가 없음: {cache.name}. 먼저 python -m app.ai.eval.fetch_bodies")
        notices.append({**it, "body": cache.read_text(encoding="utf-8")})
    return notices


def score(notices, preds):
    rows, n = [], {"date": 0, "time": 0, "time_total": 0, "cat": 0, "failed": 0}
    for nt, p in zip(notices, preds):
        exp = nt["expected"]
        gd, pd = exp["deadline"], p["deadline"]
        ok_date = (gd is None and pd is None) or (
            gd is not None and pd is not None and pd["date"] in [gd["date"], *exp["altDates"]])
        if gd and gd["time"]:
            n["time_total"] += 1
            n["time"] += bool(pd and pd.get("time") == gd["time"])
        ok_cat = any(c in exp["categories"] for c in p["categories"])
        n["date"] += ok_date
        n["cat"] += ok_cat
        n["failed"] += p["status"] == "failed"
        rows.append((nt["id"], exp["textSource"], gd and gd["date"], pd and pd["date"], ok_date, ok_cat))
    return rows, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", choices=["baseline", "gateway", "bedrock"], required=True)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--yes", action="store_true", help="유료 LLM 실제 호출에 동의")
    args = ap.parse_args()

    notices = load_notices(args.limit)
    if args.llm in PAID:
        if not args.yes:
            print(f"{args.llm} 호출 예정: 공지 {len(notices)}건, 최대 {len(notices) * 2}회(재시도 포함). 요금이 나간다.")
            print("진행하려면 --yes 를 붙인다.")
            return
        llm = make_llm(args.llm, task="classify", max_tokens=4000)
    else:
        llm = lambda prompt: ""  # LLM 없음 → 전부 failed → 제목 규칙만 남는다

    preds = [enrich(nt, llm) for nt in notices]
    rows, n = score(notices, preds)
    total = len(notices)
    for r in rows:
        print(f"{r[0]:<14} {r[1]:<5} 정답 {str(r[2]):<10} 예측 {str(r[3]):<10} 마감{'O' if r[4] else 'X'} 분야{'O' if r[5] else 'X'}")
    both_null = sum(1 for nt, p in zip(notices, preds) if nt["expected"]["deadline"] is None and p["deadline"] is None)
    unconfirmed = sum(1 for nt in notices if not nt["expected"].get("confirmed"))
    print(f"\n[{args.llm}] 마감일 {n['date']}/{total} (그중 정답·예측 둘 다 없음 {both_null}건)  "
          f"마감시각 {n['time']}/{n['time_total']}  분야 {n['cat']}/{total}  failed {n['failed']}/{total}")
    if unconfirmed:
        print(f"주의: 사람이 확인하지 않은 정답 {unconfirmed}건으로 낸 점수다. 프롬프트를 이 표본을 보고 썼으므로 표본 안 점수다.")
    if hasattr(llm, "usage"):
        print("사용량:", llm.usage)
    out = HERE / f"{args.llm}.predictions.json"
    out.write_text(json.dumps(preds, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
