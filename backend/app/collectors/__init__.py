"""출처마다 수집기 파일 하나. 출처 종류(kind)에 맞는 수집기로 보낸다."""

from types import ModuleType

from app.collectors import cs_rss, kmu_board, sw_bulletin
from app.collectors.common import Detail
from app.core.config import find_source
from app.core.schemas import Notice

_MODULES: dict[str, ModuleType] = {
    "kmu_board": kmu_board,
    "sw_bulletin": sw_bulletin,
    "cs_rss": cs_rss,
}


def fetch_list(source: dict) -> list[Notice]:
    return _MODULES[source["kind"]].fetch_list(source)


def fetch_detail(notice: Notice) -> Detail:
    source = find_source(notice.source.id)
    return _MODULES[source["kind"]].fetch_detail(notice)
