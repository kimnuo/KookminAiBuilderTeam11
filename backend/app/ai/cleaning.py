"""LLM 이 낸 값 가운데 스키마는 통과하지만 이상한 값을 정리한다 (결정적 코드).

- 목록 값: 허용 목록 밖·빈 값·중복을 버리고 앞에서부터 n개만 남긴다.
- summary: 공백만 있는 줄을 버리고 3줄까지. 다 비면 None.
- audience: 학년은 1~6 정수만, 전공은 빈 문자열을 버린다. 다 비면 None.
- apply: 공백만 있으면 None.
"""


def pick(values, allowed, n: int = 3) -> list:
    out = []
    for v in values or []:
        if isinstance(v, str) and v in allowed and v not in out:
            out.append(v)
    return out[:n]


def summary(values) -> list | None:
    lines = [v.strip() for v in values or [] if isinstance(v, str) and v.strip()]
    return lines[:3] or None


def audience(a) -> dict | None:
    if not isinstance(a, dict):
        return None
    years = []
    for y in a.get("years") or []:
        try:
            y = int(y)
        except (TypeError, ValueError):
            continue
        if 1 <= y <= 6 and y not in years:
            years.append(y)
    majors = [m.strip() for m in a.get("majors") or [] if isinstance(m, str) and m.strip()]
    text = a.get("text").strip() if isinstance(a.get("text"), str) and a.get("text").strip() else None
    if not (years or majors or text):
        return None
    return {"years": years, "majors": majors, "text": text}


def text_or_none(v) -> str | None:
    return v.strip() if isinstance(v, str) and v.strip() else None
