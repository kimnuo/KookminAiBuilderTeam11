"""extract_requirements 를 정답 초안(gold_requirements.json)으로 잰다.

실행 (backend 폴더에서, 먼저 fetch_bodies 로 본문 캐시 eval/.cache 를 만든다)
  python -m app.ai.eval.run_requirements_eval --llm baseline          # LLM 없음, 비용 0 (전부 failed, 배선 확인용)
  python -m app.ai.eval.run_requirements_eval --llm bedrock           # 호출 수만 알려 주고 멈춘다
  python -m app.ai.eval.run_requirements_eval --llm bedrock --yes     # 실제 호출 (Bedrock 요금 발생)
  --out 경로 를 주면 예측을 JSON 으로 저장한다 (기본은 저장 안 함).

채점
- 필드: key 가 같으면 맞음. other 는 예측 label 이 정답 label 을 포함해야 맞음.
- 서류: 예측 이름이 정답 이름이나 alt 중 하나를 포함하면 맞음 (공백 무시).
- 정답 하나에 예측 하나만 짝짓는다. optional 이 아닌 정답부터 짝짓는다.
- optional 정답은 못 맞혀도 재현율 분모에서 빼고, 맞히면 정밀도에서 오답으로 치지 않는다.
- 재현율 = 맞힌 정답 / optional 아닌 정답, 정밀도 = 짝지어진 예측 / 전체 예측.
"""
import argparse
import json
from pathlib import Path

from app.ai.enrich import _squash, parse_json
from app.ai.requirements import extract_requirements

HERE = Path(__file__).parent
KINDS = ("fields", "documents")


def load_notices(limit: int | None):
    items = json.loads((HERE / "gold_requirements.json").read_text(encoding="utf-8"))["items"][:limit]
    notices = []
    for it in items:
        cache = HERE / ".cache" / f"{it['id']}.txt"
        if not cache.exists():
            raise SystemExit(f"본문 캐시가 없음: {cache.name}. 먼저 python -m app.ai.eval.fetch_bodies")
        notices.append({**it, "body": cache.read_text(encoding="utf-8")})
    return notices


def same_field(p: dict, g: dict) -> bool:
    if p["key"] != g["key"]:
        return False
    return g["key"] != "other" or _squash(g["label"]) in _squash(p.get("label") or "")


def same_document(p: dict, g: dict) -> bool:
    return any(_squash(n) in _squash(p["name"]) for n in [g["name"], *g.get("alt", [])])


def match(preds: list, golds: list, same) -> list:
    """(예측, 정답) 짝 목록. 정답 하나에 예측 하나만, optional 아닌 정답을 먼저 짝짓는다."""
    order = sorted(range(len(golds)), key=lambda i: bool(golds[i].get("optional")))
    used, pairs = set(), []
    for p in preds:
        i = next((i for i in order if i not in used and same(p, golds[i])), None)
        if i is not None:
            used.add(i)
            pairs.append((p, golds[i]))
    return pairs


def score_one(pred: dict, expected: dict) -> dict:
    """한 공지의 종류별 [맞힌 정답, 정답 수, 맞은 예측, 예측 수] 와 required 일치 [같음, 짝 수]."""
    out = {}
    for kind, same in (("fields", same_field), ("documents", same_document)):
        golds, preds = expected[kind], pred[kind]
        pairs = match(preds, golds, same)
        out[kind] = [sum(not g.get("optional") for _, g in pairs),
                     sum(not g.get("optional") for g in golds), len(pairs), len(preds)]
        if kind == "fields":
            out["required"] = [sum(p["required"] == g["required"] for p, g in pairs), len(pairs)]
    return out


def _ratio(a: int, b: int) -> str:
    return f"{a}/{b} ({a / b:.0%})" if b else f"{a}/{b} (-)"


def summarize(rows: list) -> dict:
    tot = {k: [sum(r[k][i] for r in rows) for i in range(4)] for k in KINDS}
    tot["all"] = [tot["fields"][i] + tot["documents"][i] for i in range(4)]
    tot["required"] = [sum(r["required"][i] for r in rows) for i in range(2)]
    per = [(r["fields"][0] + r["documents"][0]) / (r["fields"][1] + r["documents"][1])
           for r in rows if r["fields"][1] + r["documents"][1]]
    tot["macro_recall"] = sum(per) / len(per) if per else None
    return tot


def counting_llm(llm, raw_counts: list):
    """LLM 응답에 들어 있던 항목 수를 센다. 근거 대조로 몇 개가 버려졌는지 보려고."""
    def call(prompt: str) -> str:
        raw = llm(prompt)
        data = parse_json(raw) or {}
        raw_counts.append(sum(len(data.get(k) or []) for k in KINDS if isinstance(data.get(k), list)))
        return raw
    if hasattr(llm, "usage"):
        call.usage = llm.usage
    return call


def make_llm(args, n: int):
    if args.llm == "baseline":
        return lambda prompt: ""  # LLM 없음 → 전부 failed → 빈 목록
    if not args.yes:
        print(f"{args.llm} 호출 예정: 공지 {n}건, 최대 {n * 2}회(재시도 포함). 요금이 나간다.")
        print("진행하려면 --yes 를 붙인다.")
        return None
    from app.ai.llm_factory import make_llm as _make
    return _make(args.llm, task="requirements", max_tokens=6000)


def report(args, notices, preds, rows, raw_counts):
    for nt, p, r in zip(notices, preds, rows):
        f, d = r["fields"], r["documents"]
        print(f"{nt['id']:<14} {p['status']:<6} 필드 정답 {f[0]}/{f[1]} 예측 {f[2]}/{f[3]}  "
              f"서류 정답 {d[0]}/{d[1]} 예측 {d[2]}/{d[3]}")
    t = summarize(rows)
    failed = sum(p["status"] == "failed" for p in preds)
    print(f"\n[{args.llm}] 공지 {len(notices)}건, failed {failed}")
    for name, k in (("필드", "fields"), ("서류", "documents"), ("전체", "all")):
        print(f"  {name}: 재현율 {_ratio(t[k][0], t[k][1])}  정밀도 {_ratio(t[k][2], t[k][3])}")
    macro = "-" if t["macro_recall"] is None else f"{t['macro_recall']:.0%}"
    print(f"  공지별 평균 재현율 {macro}  required 일치 {_ratio(*t['required'])}")
    kept = t["all"][3]
    if raw_counts:
        print(f"  LLM 이 낸 항목 {sum(raw_counts)}개(재시도 포함) 중 남은 것 {kept}개. 나머지는 형식·근거 대조로 버려졌다.")
    if any(not nt.get("confirmed") for nt in notices):
        print("주의: 사람이 확인하지 않은 정답 초안으로 낸 점수다. 프롬프트를 이 표본을 보고 썼으므로 표본 안 점수다.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", choices=["baseline", "gateway", "bedrock"], required=True)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--yes", action="store_true", help="유료 LLM 실제 호출에 동의")
    ap.add_argument("--out", help="예측 JSON 저장 경로 (선택)")
    args = ap.parse_args()

    notices = load_notices(args.limit)
    llm = make_llm(args, len(notices))
    if llm is None:
        return
    raw_counts = []
    if args.llm != "baseline":
        llm = counting_llm(llm, raw_counts)
    preds = [extract_requirements(nt, llm) for nt in notices]
    rows = [score_one(p, nt["expected"]) for nt, p in zip(notices, preds)]
    report(args, notices, preds, rows, raw_counts)
    if hasattr(llm, "usage"):
        print("사용량:", llm.usage)
    if args.out:
        Path(args.out).write_text(json.dumps(preds, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
