import { escapeHtml, originalLink } from '../../shared/lib/html.js';
import { deadlineLabel } from '../../shared/lib/deadline.js';
import {
  noticeAi,
  summaries,
  recommendationReasons,
  categoriesFor,
  tagsFor,
} from '../../shared/lib/notice-data.js';

export function feedCard(notice, sort) {
  const ai = noticeAi(notice);
  const deadline = deadlineLabel(ai?.deadline);
  const summary = summaries(notice);
  const reasons = recommendationReasons(notice);
  const failed = notice.ai?.status === 'failed';
  return `<article class="notice-card" ${failed ? '' : `tabindex="0" role="button" data-id="${escapeHtml(notice.id)}" aria-label="${escapeHtml(notice.title)} 상세 보기"`}>
    <div class="card-top"><span class="source-dot"></span>
      <span>${escapeHtml(notice.source?.name || '출처 확인')}</span><span>·</span>
      <span>${escapeHtml(notice.postedAt || '')}</span>
      ${ai ? `<span class="category-pill">${escapeHtml(categoriesFor(notice)[0] || '공지')}</span><span class="deadline ${deadline.className}">${escapeHtml(deadline.label)}</span>` : ''}
    </div>
    <h3>${escapeHtml(notice.title)}</h3>
    ${failed ? originalLink(notice) : summaryMarkup(summary, ai)}
    ${sort === 'recommend' && reasons.length ? `<div class="reason"><span>✳</span>${escapeHtml(reasons[0])}</div>` : ''}
    <div class="card-footer"><span>${escapeHtml(notice.department || notice.source?.group || '')}</span>
      <span class="tags">${tagsFor(notice)
        .slice(0, 3)
        .map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`)
        .join('')}</span>
    </div>
  </article>`;
}

function summaryMarkup(summary, ai) {
  if (summary.length) return `<p class="summary">${summary.map(escapeHtml).join('<br />')}</p>`;
  return `<p class="summary">${ai ? '요약을 확인할 수 없어요. 원문을 확인해 주세요.' : 'AI가 공고를 정리하고 있어요.'}</p>`;
}
