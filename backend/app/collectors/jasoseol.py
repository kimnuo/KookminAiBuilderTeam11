"""자소설닷컴 신입 채용 (jasoseol.com, 로그인 없이 쓰는 공개 JSON API).

- 목록: /api/v1/employment_companies?per_page=100&page=N&after_end_time=오늘&sort=end_time
  (after_end_time 으로 진행 중인 공고만 받는다)
- **서버가 직무·신입 필터를 무시한다**(2026-10-03 확인). 그래서 받아서 코드로 거른다:
  신입(employments[].division 에 1) + 소프트웨어·하드웨어·AI 직무 + 학부생이 지원할 수 있는 것
- 최상위 recruit_type 은 신입/경력 구분이 아니다. 반드시 division 을 본다
- robots.txt 는 /crt/ 등 6개만 막고 API 경로는 허용한다 (AI 크롤러 차단 없음)
"""

from datetime import date, datetime

from app.collectors.common import Detail, build_notice, now_kst
from app.core.config import (
    JASOSEOL_BASE_URL,
    JASOSEOL_BROAD_DUTIES,
    JASOSEOL_DUTY_IDS,
    JASOSEOL_MAX_PAGES,
    JASOSEOL_UNDERGRAD,
    TECH_RE,
)
from app.core.http import fetch_json
from app.core.text import html_to_text
from bs4 import BeautifulSoup

PER_PAGE = 100
NEW = 1  # division 값: 1 신입, 2 경력, 3 인턴


def fetch_list(source: dict) -> list[dict] | list:
    fetched_at = now_kst()
    today = fetched_at.date().isoformat()
    notices = []
    for page in range(1, JASOSEOL_MAX_PAGES + 1):
        rows = fetch_json(
            f"{JASOSEOL_BASE_URL}/api/v1/employment_companies"
            f"?per_page={PER_PAGE}&page={page}&after_end_time={today}&sort=end_time"
        )
        if not isinstance(rows, list) or not rows:
            break
        keep = (r for r in rows if _wanted(r))
        notices += [n for n in (_to_notice(r, source, fetched_at) for r in keep) if n]
        if len(rows) < PER_PAGE:
            break
    return notices


def _wanted(row: dict) -> bool:
    """신입을 뽑고, 직무가 소프트웨어·하드웨어·AI 이고, 학부생이 지원할 수 있는 공고."""
    title = row.get("title") or ""
    return any(_job_wanted(job, title) for job in row.get("employments") or [])


def _job_wanted(job: dict, title: str) -> bool:
    duties = set(job.get("duty_group_ids") or [])
    if NEW not in (job.get("division") or []) or not duties & JASOSEOL_DUTY_IDS:
        return False
    if not _undergrad_ok(job.get("graduate_condition")):
        return False
    # 대기업 공채는 직무 코드를 수십 개 몰아 넣는다. 그럴 때는 직무 이름·제목 글자로 한 번 더 본다
    if len(duties) > JASOSEOL_BROAD_DUTIES:
        return bool(TECH_RE.search(f"{job.get('field') or ''} {title}"))
    return True


def _undergrad_ok(condition: str | None) -> bool:
    if not condition:
        return True  # 조건이 안 적혀 있으면 막지 않는다
    return bool({part.strip() for part in condition.split(",")} & JASOSEOL_UNDERGRAD)


def _to_notice(row: dict, source: dict, fetched_at: datetime):
    article = row.get("id")
    company = row.get("name") or (row.get("company_group") or {}).get("name") or ""
    if not article or not company:
        return None
    fields = [job.get("field") for job in row.get("employments") or [] if job.get("field")]
    return build_notice(
        source,
        article=str(article),
        title=f"{company} {row.get('title') or '신입 채용'}",
        url=f"{JASOSEOL_BASE_URL}/recruit/{article}",
        posted_at=_date(row.get("start_time") or row.get("opened_at")),
        department=company,
        fetched_at=fetched_at,
    )


def _date(value: str | None) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def fetch_detail(notice) -> Detail:
    article = notice.id.rsplit("-", 1)[-1]
    row = fetch_json(f"{JASOSEOL_BASE_URL}/api/v1/employment_companies/{article}")
    parts = [f"회사: {row.get('name') or ''}", f"공고: {row.get('title') or ''}"]
    if row.get("end_time"):
        parts.append(f"접수 마감: {str(row['end_time'])[:16].replace('T', ' ')}")
    if row.get("start_time"):
        parts.append(f"접수 시작: {str(row['start_time'])[:16].replace('T', ' ')}")
    for job in row.get("employments") or []:
        parts.append(
            f"- 직무: {job.get('field') or ''}"
            f" / 구분: {_division_text(job.get('division'))}"
            f" / 지원 가능: {job.get('graduate_condition') or '제한 없음'}"
        )
    if row.get("employment_page_url"):
        parts.append(f"지원 페이지: {row['employment_page_url']}")
    parts.append(html_to_text(BeautifulSoup(row.get("content") or "", "html.parser")))
    return Detail(body="\n".join(p for p in parts if p.strip()))


def _division_text(values: list | None) -> str:
    names = {1: "신입", 2: "경력", 3: "인턴", 4: "계약직", 7: "교육"}
    return "·".join(names.get(v, str(v)) for v in values or []) or "구분 없음"
