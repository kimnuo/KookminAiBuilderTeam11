"""가상 포트폴리오 PDF 로 가리기와 extract_profile 을 잰다 (PRD 14절 P2 기준).

실행 (backend 폴더에서)
  python -m app.ai.eval.run_profile_eval --llm baseline          # LLM 없음, 비용 0
  python -m app.ai.eval.run_profile_eval --llm bedrock           # 호출 수만 알려 주고 멈춘다
  python -m app.ai.eval.run_profile_eval --llm bedrock --yes     # 실제 호출 (Bedrock 요금 발생)

흐름: PDF 에서 fitz 로 글자 추출 → mask_contacts → extract_profile → 정답(portfolios/*.expected.json) 대조.
브라우저(pdf.js)가 뽑는 글자 순서는 fitz 와 다를 수 있다. 여기서 재는 것은 fitz 기준이다.

보는 것
- 가리기: 정답의 hidden(전화·이메일·학번 원문)이 AI로 가는 프롬프트에 몇 번 나오나(0이어야 한다),
  kept(날짜 등)가 가려지지 않고 남았나, 가린 개수가 정답과 같나.
- 정답 근거: 정답을 LLM 답처럼 넣었을 때 검사기가 항목을 버리지 않나. 버리면 검사기나 정답이 틀린 것이다.
- 추출: 칸마다 찾은 수/정답 수(재현율)와 맞은 수/낸 수(정밀도). 정답의 key 가 예측의 제목이나 근거에 있으면 맞다.
- 근거 없음: 낸 항목 중 근거가 가린 글에 없는 수. PRD 14절 기준은 0건이다.
"""
import argparse
import json
from pathlib import Path

import fitz

from app.ai.mask import mask_contacts
from app.ai.profile import clean, extract_profile, norm_text

HERE = Path(__file__).parent
PORTFOLIOS = HERE / "portfolios"
ITEM_KINDS = ("projects", "awards", "activities")
FIELDS = ("skills", "tags", *ITEM_KINDS)


def pdf_text(path: Path) -> str:
    with fitz.open(path) as doc:
        return "\n".join(page.get_text() for page in doc)


def load_cases() -> list:
    cases = []
    for gold_path in sorted(PORTFOLIOS.glob("*.expected.json")):
        gold = json.loads(gold_path.read_text(encoding="utf-8"))
        raw = pdf_text(PORTFOLIOS / f"{gold['id']}.pdf")
        masked, count = mask_contacts(raw)
        cases.append({"gold": gold, "raw": raw, "masked": masked, "maskCount": count})
    return cases


def gold_as_answer(gold: dict) -> dict:
    """정답을 LLM 답 모양으로 바꾼다. 검사기가 정답을 버리지 않는지 볼 때 쓴다."""
    exp = gold["expected"]
    return {"skills": exp["skills"], "tags": exp["tags"], **{k: exp[k] for k in ITEM_KINDS}}


def _hit(key: str, item: dict) -> bool:
    return norm_text(key).casefold() in norm_text(item["title"] + item["evidence"]).casefold()


def _same_skill(a: str, b: str) -> bool:
    x, y = set(a.casefold().split()), set(b.casefold().split())
    return x <= y or y <= x


def score_case(pred: dict, gold: dict) -> dict:
    """칸마다 [찾은 수, 정답 수, 맞은 수, 낸 수]."""
    exp = gold["expected"]
    ok_tags = exp["tags"] + exp.get("tagsAllowed", [])
    out = {
        "skills": [sum(any(_same_skill(g, p) for p in pred["skills"]) for g in exp["skills"]), len(exp["skills"]),
                   sum(any(_same_skill(g, p) for g in exp["skills"]) for p in pred["skills"]), len(pred["skills"])],
        "tags": [len(set(pred["tags"]) & set(exp["tags"])), len(exp["tags"]),
                 sum(t in ok_tags for t in pred["tags"]), len(pred["tags"])],
    }
    for kind in ITEM_KINDS:
        p_items, g_items = pred[kind], exp[kind]
        out[kind] = [sum(any(_hit(g["key"], p) for p in p_items) for g in g_items), len(g_items),
                     sum(any(_hit(g["key"], p) for g in g_items) for p in p_items), len(p_items)]
    return out


def mask_report(case: dict, prompts: list) -> dict:
    m = case["gold"]["mask"]
    return {
        "count": case["maskCount"], "countExpected": m["count"],
        "leaks": sum(h in p for p in prompts for h in m["hidden"]),
        "keptOk": sum(k in case["masked"] for k in m["kept"]), "keptTotal": len(m["kept"]),
        "notMasked": [s for s in m.get("notMasked", []) if s in case["masked"]],
    }


def gold_check(case: dict) -> tuple[int, int]:
    """정답을 그대로 넣었을 때 살아남는 항목 수 / 정답 항목 수."""
    kept = clean(gold_as_answer(case["gold"]), case["masked"])
    return (sum(len(kept[k]) for k in ITEM_KINDS) + len(kept["skills"]),
            sum(len(case["gold"]["expected"][k]) for k in ITEM_KINDS) + len(case["gold"]["expected"]["skills"]))


def ungrounded(pred: dict, masked: str) -> int:
    text_n = norm_text(masked)
    return sum(norm_text(it["evidence"]) not in text_n for k in ITEM_KINDS for it in pred[k])


def run_case(case: dict, llm) -> dict:
    prompts = []

    def capturing(prompt: str) -> str:
        prompts.append(prompt)
        return llm(prompt)

    pred = extract_profile(case["masked"], capturing)
    return {"id": case["gold"]["id"], "pred": pred, "score": score_case(pred, case["gold"]),
            "mask": mask_report(case, prompts), "gold": gold_check(case),
            "ungrounded": ungrounded(pred, case["masked"]), "calls": len(prompts)}


def print_case(r: dict, chars: int) -> None:
    m, s = r["mask"], r["score"]
    print(f"{r['id']:<12} 글자 {chars:<5} 가림 {m['count']}/{m['countExpected']}  프롬프트 새어나감 {m['leaks']}  "
          f"날짜·숫자 보존 {m['keptOk']}/{m['keptTotal']}  정답근거 통과 {r['gold'][0]}/{r['gold'][1]}  "
          f"상태 {r['pred']['status']}  호출 {r['calls']}")
    print("             " + "  ".join(f"{k} {s[k][0]}/{s[k][1]}(낸 {s[k][3]}, 맞음 {s[k][2]})" for k in FIELDS)
          + f"  근거없음 {r['ungrounded']}")
    if m["notMasked"]:
        print(f"             가리지 못한 식별 단서(알려진 한계): {', '.join(m['notMasked'])}")


def print_total(results: list, name: str) -> None:
    tot = {k: [sum(r["score"][k][i] for r in results) for i in range(4)] for k in FIELDS}
    recall = "  ".join(f"{k} {v[0]}/{v[1]}" for k, v in tot.items())
    precision = "  ".join(f"{k} {v[2]}/{v[3]}" for k, v in tot.items())
    print(f"\n[{name}] 재현율 {recall}")
    print(f"[{name}] 정밀도 {precision}")
    print(f"[{name}] 프롬프트 새어나감 {sum(r['mask']['leaks'] for r in results)}  "
          f"근거없음 {sum(r['ungrounded'] for r in results)}  "
          f"failed {sum(r['pred']['status'] == 'failed' for r in results)}/{len(results)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", choices=["baseline", "gateway", "bedrock"], required=True)
    ap.add_argument("--yes", action="store_true", help="유료 LLM 실제 호출에 동의")
    args = ap.parse_args()

    cases = load_cases()
    if args.llm in ("gateway", "bedrock"):
        if not args.yes:
            chars = sum(len(c["masked"]) for c in cases)
            print(f"{args.llm} 호출 예정: 포트폴리오 {len(cases)}건, 최대 {len(cases) * 2}회(재시도 포함), "
                  f"보낼 글 합계 {chars}자. 요금이 나간다.\n진행하려면 --yes 를 붙인다.")
            return
        from app.ai.llm_factory import make_llm
        llm = make_llm(args.llm, task="profile", max_tokens=6000)
    else:
        llm = lambda prompt: ""  # LLM 없음 → 전부 failed. 가리기와 정답 근거 검사만 의미가 있다

    results = [run_case(c, llm) for c in cases]
    for c, r in zip(cases, results):
        print_case(r, len(c["raw"]))
    print_total(results, args.llm)
    if any(not c["gold"].get("confirmed") for c in cases):
        print("주의: 정답은 Claude 가 원본을 쓰면서 함께 적은 초안이다(confirmed=false). 사람이 확인하기 전 점수다.")
    if hasattr(llm, "usage"):
        print("사용량:", llm.usage)
        out = HERE / f"profile_{args.llm}.predictions.json"
        out.write_text(json.dumps([{"id": r["id"], **r["pred"]} for r in results], ensure_ascii=False, indent=1),
                       encoding="utf-8")


if __name__ == "__main__":
    main()
