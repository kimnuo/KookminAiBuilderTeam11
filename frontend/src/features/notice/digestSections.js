import { escapeHtml } from '../../shared/lib/html.js';

/** 백엔드 한 페이지 요약(digest)의 칸: 주요 내역, 필수 사항, 대상, 기타, 첨부 */
export function digestSections(notice) {
  const digest = notice.digest;
  return [
    listSection('주요 내역', digest.keyPoints, keyPointItem),
    listSection('필수 사항', digest.requirements, requirementItem),
    digest.audience?.text ? textSection('대상', digest.audience.text) : '',
    listSection('기타', digest.etc, (item) => `<li>${escapeHtml(item)}</li>`),
    listSection('첨부파일', notice.attachments, attachmentItem),
  ].join('');
}

/** 요약 제목 바로 아래에 붙이는 원 제목 */
export function originalTitle(notice) {
  if (!notice.originalTitle || notice.originalTitle === notice.title) return '';
  return `<p class="detail-original">원 제목 · ${escapeHtml(notice.originalTitle)}</p>`;
}

function textSection(title, value) {
  return `<section class="detail-section"><h3>${escapeHtml(title)}</h3><p>${escapeHtml(value)}</p></section>`;
}

function listSection(title, items, render) {
  if (!Array.isArray(items) || !items.length) return '';
  return `<section class="detail-section"><h3>${escapeHtml(title)}</h3><ul class="digest-list">${items.map(render).join('')}</ul></section>`;
}

function keyPointItem(item) {
  return `<li><strong>${escapeHtml(item.label)}</strong> ${escapeHtml(item.value)}${evidence(item.evidence)}</li>`;
}

function requirementItem(item) {
  const origin = item.origin && item.origin !== '본문' ? ` · ${item.origin}` : '';
  return `<li>${escapeHtml(item.text)}${evidence(item.evidence, origin)}</li>`;
}

function attachmentItem(item) {
  const state = item.analyzed ? 'AI 분석함' : item.note || '분석 안 함';
  return `<li>${escapeHtml(item.name)} <span class="digest-muted">(${escapeHtml(state)})</span></li>`;
}

function evidence(text, suffix = '') {
  if (!text) return '';
  return `<span class="evidence">원문 근거: ${escapeHtml(text)}${escapeHtml(suffix)}</span>`;
}
