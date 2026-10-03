import { escapeHtml, originalLink } from '../../shared/lib/html.js';
import { deadlineLabel } from '../../shared/lib/deadline.js';
import { groupLabels } from '../../shared/lib/notice-groups.js';
import { icon } from '../../shared/ui/icons.js';
import {
  noticeAi,
  summaries,
  recommendationReasons,
  tagsFor,
} from '../../shared/lib/notice-data.js';

export function feedCard(notice, sort) {
  const ai = noticeAi(notice);
  const reasons = recommendationReasons(notice);
  const failed = notice.ai?.status === 'failed';
  return `<article class="notice-card" ${failed ? '' : `tabindex="0" role="button" data-id="${escapeHtml(notice.id)}" aria-label="${escapeHtml(notice.title)} 상세 보기"`}>
    ${cardHeader(notice, ai)}
    <h3>${escapeHtml(notice.title)}</h3>
    ${failed ? originalLink(notice) : summaryMarkup(summaries(notice), ai)}
    ${sort === 'recommend' && reasons.length ? `<div class="reason">${icon('check-circle')}${escapeHtml(reasons[0])}</div>` : ''}
    ${cardFooter(notice, failed)}
  </article>`;
}

function cardHeader(notice, ai) {
  const deadline = deadlineLabel(ai?.deadline);
  return `<div class="card-top">
    <span class="source-icon">${icon('document')}</span>
    <div class="source-meta"><span class="source-name">${escapeHtml(notice.source?.name || '출처 확인')}</span><span class="source-date">${escapeHtml(notice.postedAt || '')}</span></div>
    ${ai ? `<span class="deadline ${deadline.className}">${escapeHtml(deadline.label)}</span>` : ''}
  </div>`;
}

function cardFooter(notice, failed) {
  const categories = failed ? [] : groupLabels(notice).slice(0, 2);
  const tags = tagsFor(notice).slice(0, 2);
  return `<div class="card-footer"><div class="card-meta">
    ${categories.map((category) => `<span class="category-pill">${escapeHtml(category)}</span>`).join('')}
    <span class="tags">${tags.map((tag) => `<span class="tag">#${escapeHtml(tag)}</span>`).join('')}</span>
    </div>${failed ? '' : `<span class="card-open">자세히 보기 ${icon('chevron-right')}</span>`}
  </div>`;
}

function summaryMarkup(summary, ai) {
  if (summary.length) return `<p class="summary">${summary.map(escapeHtml).join('<br />')}</p>`;
  return `<p class="summary">${ai ? '요약을 확인할 수 없어요. 원문을 확인해 주세요.' : 'AI가 공고를 정리하고 있어요.'}</p>`;
}
