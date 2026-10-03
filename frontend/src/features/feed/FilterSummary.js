import { config } from '../../shared/config.js';
import { escapeHtml } from '../../shared/lib/html.js';

export function renderFilterSummary(groups, query, source, count) {
  const selected = config.noticeGroups.filter((group) => groups.has(group.id));
  const labels = selected.map((group) => group.label);
  document.getElementById('feed-title').textContent = labels.length
    ? '선택한 카테고리'
    : '전체 공고';
  document.getElementById('filter-summary').innerHTML = selected
    .map(
      (group) =>
        `<button class="selected-category" type="button" data-remove-group="${group.id}" aria-label="${escapeHtml(group.label)} 선택 해제">${escapeHtml(group.label)}<span aria-hidden="true">×</span></button>`,
    )
    .join('');
  document.getElementById('clear-filters').hidden = !groups.size && !query.trim() && !source;
  document.getElementById('results-description').textContent = query.trim()
    ? `“${query.trim()}” 검색 결과 ${count}개 · ${labels.join(', ') || '전체 카테고리'}`
    : `${labels.join(', ') || '전체 카테고리'}에서 ${count}개를 찾았어요.`;
}
