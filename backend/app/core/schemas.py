"""API 계약 (공용 스키마). 형식 설명은 backend/README.md 「API 계약」.

JSON 필드는 camelCase, 파이썬 속성은 snake_case 로 쓰고 alias 로 바꾼다.
모르는 값은 null. AI 가 만든 항목은 모두 원문 근거(evidence)가 있다 (없으면 버린다).
"""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class SourceRef(ApiModel):
    id: str
    name: str
    group: str


class Source(SourceRef):
    url: str
    default_category: str


class Attachment(ApiModel):
    name: str
    url: str
    type: str  # pdf, hwp, hwpx, docx, pptx, xls … (확장자)
    analyzed: bool = False  # 글자를 뽑아 AI 에 넣었는가
    note: str | None = None  # 분석 못 한 이유 등


class KeyPoint(ApiModel):
    label: str  # 신청 기간, 대상, 장소, 금액 …
    value: str
    evidence: str


class Requirement(ApiModel):
    text: str  # 학생이 반드시 해야 하거나 갖춰야 할 것
    evidence: str
    origin: str = "본문"  # "본문" 또는 "첨부:파일명"


class Deadline(ApiModel):
    date: date
    time: str | None = None  # "17:00"
    evidence: str


class KeyDate(ApiModel):
    date: date
    evidence: str


class Audience(ApiModel):
    years: list[int] = []  # 대상 학년. 비어 있으면 학년 제한 없음
    majors: list[str] = []  # 대상 학과·전공. 비어 있으면 제한 없음
    statuses: list[str] = []  # 재학, 휴학, 졸업예정, 졸업생 … 비어 있으면 제한 없음
    text: str | None = None  # 원문 표현 그대로


class Digest(ApiModel):
    status: Literal["pending", "done", "failed"]
    title: str | None = None  # 요약 제목
    summary: str | None = None  # 내용 요약 (2~3문장)
    key_points: list[KeyPoint] = []  # 주요 내역
    requirements: list[Requirement] = []  # 필수 사항
    deadline: Deadline | None = None
    last_date: KeyDate | None = None  # 이 공지가 의미 있는 마지막 날 (행사 종료일 등). 지나면 브리핑에서 뺀다
    action_required: bool | None = None  # 신청·제출 등 학생이 할 일이 있는가
    audience: Audience | None = None
    etc: list[str] = []  # 기타
    error: str | None = None  # failed 일 때 이유


class Notice(ApiModel):
    id: str  # {출처ID}-{글번호}
    source: SourceRef
    original_title: str  # 원 제목
    url: str  # 원문 직접 링크
    posted_at: date | None
    department: str | None = None  # 작성 부서·원 사이트 분류 (작성자 실명은 두지 않는다)
    pinned: bool = False
    fetched_at: datetime
    categories: list[str]
    attachments: list[Attachment] = []
    digest: Digest


class NoticePage(ApiModel):
    items: list[Notice]
    next_cursor: str | None = None


class Situation(ApiModel):
    """나의 상황. 저장하지 않는다. 이름·학번·연락처는 받지 않는다."""

    major: str | None = Field(None, examples=["소프트웨어학부"])
    year: int | None = Field(None, ge=1, le=6, examples=[4])
    status: str | None = Field(None, examples=["재학"])  # 재학, 휴학, 졸업예정 …
    graduating: bool = False  # 이번 학기 졸업 예정
    interests: list[str] = Field([], examples=[["취업", "장학"]])  # CATEGORIES 중에서


class BriefingItem(ApiModel):
    notice: Notice
    reasons: list[str]  # 왜 나에게 해당하는지 (코드가 만든다)
    days_left: int | None  # 마감까지 남은 날 (마감일 모르면 null)


class Briefing(ApiModel):
    generated_at: datetime
    items: list[BriefingItem]
