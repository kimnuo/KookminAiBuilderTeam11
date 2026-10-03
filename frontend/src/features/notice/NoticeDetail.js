import { getNotice } from '../../shared/api/api-client.js';
import { icon } from '../../shared/ui/icons.js';
import { escapeHtml, originalLink } from '../../shared/lib/html.js';
import { validDeadline } from '../../shared/lib/deadline.js';
import {
  noticeAi,
  summaries,
  recommendationReasons,
  categoriesFor,
} from '../../shared/lib/notice-data.js';

function detailMarkup(notice) {
  const ai = noticeAi(notice);
  const meta = `<div class="detail-meta"><span>${escapeHtml(notice.source?.name || '출처 확인')}</span><span>${escapeHtml(notice.postedAt || '')}</span></div>`;
  const title = `<h2 id="detail-title">${escapeHtml(notice.title)}</h2>`;
  const link = `<div class="detail-actions">${originalLink(notice)}</div>`;
  if (!ai)
    return `${meta}${title}${notice.ai?.status === 'failed' ? '' : '<p class="detail-summary">AI가 공고를 정리하고 있어요.</p>'}${link}`;
  const deadline = validDeadline(ai.deadline);
  const reasons = recommendationReasons(notice);
  return `${meta}${title}<span class="category-pill">${escapeHtml(categoriesFor(notice)[0] || '공지')}</span>
    <p class="detail-summary">${summaries(notice).map(escapeHtml).join('<br />') || '요약을 확인할 수 없어요.'}</p>
    ${reasons.length ? `<div class="reason">${icon('check-circle')}${escapeHtml(reasons[0])}</div>` : ''}
    ${section('마감일', deadline ? `${deadline.date}${deadline.time ? ` ${deadline.time}` : ' (시각은 원문 확인)'}` : '원문 확인', deadline?.evidence)}
    ${section('신청 방법', ai.apply || '원문에서 확인해 주세요.')}
    ${ai.audience?.text ? section('지원 대상', ai.audience.text) : ''}
    <section class="detail-section"><h3>지원 준비</h3><p class="local-note">내 값은 이 기기에서만 읽으며 서버로 보내지 않아요.</p><div id="requirements-content" role="status">필요 항목을 불러오고 있어요.</div></section>
    ${link}`;
}

function section(title, value, evidence = null) {
  return `<section class="detail-section"><h3>${escapeHtml(title)}</h3><p>${escapeHtml(value)}</p>${evidence ? `<span class="evidence">원문 근거: ${escapeHtml(evidence)}</span>` : ''}</section>`;
}

class NoticeDetail {
  constructor({ onReady, onClose }) {
    this.onReady = onReady;
    this.onClose = onClose;
    this.dialog = /** @type {HTMLDialogElement} */ (document.getElementById('detail-modal'));
    this.content = document.getElementById('detail-content');
    this.version = 0;
    this.controller = null;
    this.returnFocus = null;
    this.dialog.addEventListener('close', () => this.closed());
    this.dialog.addEventListener('click', (event) => {
      if (event.target === this.dialog) this.dialog.close();
    });
    document.getElementById('close-detail').addEventListener('click', () => this.dialog.close());
  }

  async show(id) {
    this.controller?.abort();
    this.controller = new AbortController();
    const current = ++this.version;
    if (!this.dialog.open) this.returnFocus = document.activeElement;
    this.content.innerHTML =
      '<h2 id="detail-title">공고 상세</h2><p class="status-message">공고 상세를 불러오고 있어요.</p>';
    if (!this.dialog.open) this.dialog.showModal();
    document.body.style.overflow = 'hidden';
    try {
      const notice = await getNotice(id, this.controller.signal);
      if (current !== this.version || !this.dialog.open) return;
      this.content.innerHTML = detailMarkup(notice);
      this.onReady(notice, document.getElementById('requirements-content'), this.controller.signal);
    } catch (error) {
      if (current !== this.version || error.name === 'AbortError') return;
      this.content.innerHTML = `<h2 id="detail-title">공고 상세</h2><p class="status-message error">${escapeHtml(error.message)}</p>`;
    }
  }

  closed() {
    ++this.version;
    this.controller?.abort();
    document.body.style.overflow = '';
    this.onClose();
    if (this.returnFocus instanceof HTMLElement && this.returnFocus.isConnected)
      this.returnFocus.focus();
  }
}

export function createNoticeDetail(options) {
  const detail = new NoticeDetail(options);
  return { show: (id) => detail.show(id) };
}
