const PROFILE_KEY = 'kmu.profile';
const $ = (selector) => document.querySelector(selector);

export function escapeHtml(value = '') {
  return String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
}

export function getProfile() {
  try { return JSON.parse(localStorage.getItem(PROFILE_KEY) || '{}'); }
  catch { return {}; }
}

export function renderProfile() {
  const profile = getProfile();
  const tags = profile.tags || profile.recommendationTags || profile.history?.tags || [];
  $('#profile-tags').innerHTML = tags.length
    ? tags.map((tag) => `<span class="profile-tag">${escapeHtml(tag)}</span>`).join('')
    : '<span class="muted-tag">등록된 태그가 없어요</span>';
}

function fieldLabel(field) {
  const labels = { name: '이름', phone: '연락처', email: '이메일', studentId: '학번', school: '학교', major: '학과', year: '학년', birthDate: '생년월일', portfolioUrl: '포트폴리오 링크' };
  return labels[field] || field;
}

function profileValue(profile, key) {
  const value = key.split('.').reduce((current, part) => current?.[part], profile);
  return value == null || value === '' ? '' : Array.isArray(value) ? value.join(', ') : String(value);
}

function requirementItems(data) {
  if (Array.isArray(data)) return data;
  return data.items || data.requirements || [];
}

function renderRequirements(items) {
  if (!items.length) return '<p>필요 항목을 찾지 못했어요. 공고 원문을 확인해 주세요.</p>';
  const profile = getProfile();
  return `<div class="requirements">${items.map((item) => {
    const key = item.profileField || item.profileKey || item.field || item.key || '';
    const label = item.label || item.name || fieldLabel(key);
    const value = key ? profileValue(profile, key) : '';
    return `<div class="requirement-row"><div><div class="requirement-title">${escapeHtml(label)}</div>${item.evidence ? `<div class="requirement-evidence">근거: ${escapeHtml(item.evidence)}</div>` : ''}</div><div class="requirement-value ${value ? '' : 'missing-value'}">${escapeHtml(value || '내 정보 없음')}</div>${value ? `<button class="copy-button" type="button" data-copy="${escapeHtml(value)}">복사</button>` : ''}</div>`;
  }).join('')}</div>`;
}

export { requirementItems, renderRequirements };
