import { escapeHtml, renderProfile, requirementItems, renderRequirements } from './support-panel.js';
const API = '/api';
const categories = ['학사', '장학', '공모전·행사', '채용·인턴', '특강·교육', '국제교류', '봉사', '생활·시설', '시스템', '기타'];
const state = { notices: [], sort: 'recommend', selected: null, loading: false };
const $ = (selector) => document.querySelector(selector);
const list = $('#notice-list');

async function request(path) {
  const response = await fetch(`${API}${path}`, { credentials: 'same-origin', headers: { Accept: 'application/json' } });
  if (!response.ok) throw new Error(`요청에 실패했어요 (${response.status})`);
  return response.json();
}

function formatDeadline(deadline) {
  if (!deadline?.date) return { label: '마감일 확인', className: 'no-deadline' };
  const date = new Date(`${deadline.date}T${deadline.time || '23:59'}:00+09:00`);
  if (Number.isNaN(date.getTime())) return { label: '마감일 확인', className: 'no-deadline' };
  const days = Math.ceil((date.getTime() - Date.now()) / 86400000);
  if (days < 0) return { label: '마감', className: 'no-deadline' };
  if (days === 0) return { label: '오늘 마감', className: '' };
  if (days <= 7) return { label: `D-${days}`, className: '' };
  return { label: `${deadline.date}${deadline.time ? ` ${deadline.time}` : ''}`, className: 'no-deadline' };
}

function summaries(notice) {
  const summary = notice.ai?.summary;
  if (Array.isArray(summary)) return summary.filter(Boolean);
  return typeof summary === 'string' && summary ? [summary] : [];
}

function recommendationReasons(notice) {
  const reasons = notice.recommendationReasons ?? notice.reasons ?? notice.recommendationReason ?? [];
  return (Array.isArray(reasons) ? reasons : [reasons]).filter(Boolean).map((item) => typeof item === 'string' ? item : item.text || item.label).filter(Boolean);
}

function visibleNotices() {
  const query = $('#search-input').value.trim().toLocaleLowerCase();
  const category = $('#category-filter').value;
  const source = $('#source-filter').value;
  return state.notices.filter((notice) => {
    const title = (notice.title || '').toLocaleLowerCase();
    const text = [...summaries(notice), notice.ai?.apply || '', notice.source?.name || ''].join(' ').toLocaleLowerCase();
    return (!query || title.includes(query) || text.includes(query))
      && (!category || notice.ai?.categories?.includes(category))
      && (!source || notice.source?.id === source);
  });
}

function renderNotices() {
  const notices = visibleNotices();
  $('#result-count').textContent = notices.length;
  list.innerHTML = notices.map((notice) => {
    const summary = summaries(notice);
    const deadline = formatDeadline(notice.ai?.deadline);
    const reasons = recommendationReasons(notice);
    const category = notice.ai?.categories?.[0] || '공지';
    const tags = notice.ai?.tags || [];
    return `<article class="notice-card" tabindex="0" role="button" data-id="${escapeHtml(notice.id)}" aria-label="${escapeHtml(notice.title)} 상세 보기">
      <div class="card-top"><span class="source-dot"></span><span>${escapeHtml(notice.source?.name || '출처 확인')}</span><span>·</span><span>${escapeHtml(notice.postedAt || '')}</span><span class="category-pill">${escapeHtml(category)}</span><span class="deadline ${deadline.className}">${escapeHtml(deadline.label)}</span></div>
      <h3>${escapeHtml(notice.title || '제목 없음')}</h3>
      ${summary.length ? `<p class="summary">${summary.map(escapeHtml).join('<br />')}</p>` : `<p class="summary">AI 요약을 확인할 수 없어요. 원문을 확인해 주세요.</p>`}
      ${state.sort === 'recommend' && reasons.length ? `<div class="reason"><span class="reason-icon">✳</span>${escapeHtml(reasons[0])}</div>` : ''}
      <div class="card-footer"><span>${escapeHtml(notice.department || notice.source?.group || '국민대학교')}</span><span class="tags">${tags.slice(0, 3).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}</span></div>
    </article>`;
  }).join('');
  $('#empty-state').hidden = notices.length > 0;
}

function setStatus(message = '', error = false) {
  const status = $('#feed-status');
  status.textContent = message;
  status.hidden = !message;
  status.classList.toggle('error', error);
}

async function loadFeed() {
  if (state.loading) return;
  state.loading = true;
  setStatus('공고를 불러오고 있어요.');
  $('#empty-state').hidden = true;
  try {
    const data = await request(`/feed?sort=${encodeURIComponent(state.sort)}`);
    state.notices = Array.isArray(data) ? data : data.items || data.notices || [];
    renderNotices();
    setStatus('');
  } catch (error) {
    state.notices = [];
    renderNotices();
    setStatus(`피드를 불러오지 못했어요. ${error.message}`, true);
  } finally { state.loading = false; }
}

async function showDetail(id) {
  const modal = $('#detail-modal');
  const content = $('#detail-content');
  modal.hidden = false;
  content.innerHTML = '<p class="status-message">공고 상세를 불러오고 있어요.</p>';
  try {
    const notice = await request(`/notices/${encodeURIComponent(id)}`);
    state.selected = notice;
    const ai = notice.ai || {};
    const deadline = ai.deadline;
    const reasons = recommendationReasons(notice);
    content.innerHTML = `<div class="detail-meta"><span>${escapeHtml(notice.source?.name || '출처 확인')}</span><span>·</span><span>${escapeHtml(notice.postedAt || '')}</span><span class="category-pill">${escapeHtml(ai.categories?.[0] || '공지')}</span></div>
      <h2 id="detail-title">${escapeHtml(notice.title || '제목 없음')}</h2>
      ${summaries(notice).length ? `<p class="detail-summary">${summaries(notice).map(escapeHtml).join('<br />')}</p>` : '<p class="detail-summary">AI 요약을 확인할 수 없어요.</p>'}
      ${reasons.length ? `<div class="reason"><span class="reason-icon">✳</span>${escapeHtml(reasons[0])}</div>` : ''}
      <section class="detail-section"><h3>마감일</h3><p>${deadline?.date ? `${escapeHtml(deadline.date)}${deadline.time ? ` ${escapeHtml(deadline.time)}` : ''}` : '확인할 수 없어요. 원문을 확인해 주세요.'}</p>${deadline?.evidence ? `<span class="evidence">원문 근거: ${escapeHtml(deadline.evidence)}</span>` : ''}</section>
      <section class="detail-section"><h3>신청 방법</h3><p>${escapeHtml(ai.apply || '원문에서 확인해 주세요.')}</p></section>
      ${ai.audience?.text ? `<section class="detail-section"><h3>지원 대상</h3><p>${escapeHtml(ai.audience.text)}</p></section>` : ''}
      <section class="detail-section"><h3>지원 준비</h3><div id="requirements-content"><p>필요 항목을 불러오고 있어요.</p></div></section>
      <div class="detail-actions"><a class="primary-link" href="${escapeHtml(notice.url || '#')}" target="_blank" rel="noopener noreferrer">원문 보기 ↗</a></div>`;
    loadRequirements(notice.id);
  } catch (error) {
    content.innerHTML = `<p class="status-message error">상세를 불러오지 못했어요. ${escapeHtml(error.message)}</p>`;
  }
}

async function loadRequirements(id) {
  const target = $('#requirements-content');
  try {
    const data = await request(`/notices/${encodeURIComponent(id)}/requirements`);
    if (target) target.innerHTML = renderRequirements(requirementItems(data));
  } catch {
    if (target) target.innerHTML = '<p>지원 준비 정보를 불러오지 못했어요. 원문을 확인해 주세요.</p>';
  }
}

async function loadFilters() {
  const categorySelect = $('#category-filter');
  categorySelect.insertAdjacentHTML('beforeend', categories.map((category) => `<option value="${escapeHtml(category)}">${escapeHtml(category)}</option>`).join(''));
  try {
    const data = await request('/sources');
    const sources = Array.isArray(data) ? data : data.items || data.sources || [];
    $('#source-filter').insertAdjacentHTML('beforeend', sources.map((source) => `<option value="${escapeHtml(source.id)}">${escapeHtml(source.name)}</option>`).join(''));
  } catch { /* The source filter remains available when the API is offline. */ }
}

document.addEventListener('click', async (event) => {
  const card = event.target.closest('.notice-card');
  if (card) await showDetail(card.dataset.id);
  const copy = event.target.closest('[data-copy]');
  if (copy) {
    await navigator.clipboard.writeText(copy.dataset.copy);
    copy.textContent = '복사됨';
  }
  if (event.target === $('#detail-modal') || event.target.closest('#close-detail')) $('#detail-modal').hidden = true;
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') $('#detail-modal').hidden = true;
  if ((event.key === 'Enter' || event.key === ' ') && event.target.matches('.notice-card')) showDetail(event.target.dataset.id);
});
$('#sort-select').addEventListener('change', (event) => { state.sort = event.target.value; loadFeed(); });
$('#search-input').addEventListener('input', renderNotices);
$('#category-filter').addEventListener('change', renderNotices);
$('#source-filter').addEventListener('change', renderNotices);
$('#refresh-button').addEventListener('click', loadFeed);
window.addEventListener('storage', (event) => { if (event.key === 'kmu.profile') renderProfile(); });

renderProfile();
loadFilters();
loadFeed();
