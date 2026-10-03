export function escapeHtml(value = '') {
  return String(value).replace(
    /[&<>"']/g,
    (char) =>
      ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
      })[char],
  );
}

export function safeUrl(value) {
  try {
    const url = new URL(value);
    return ['http:', 'https:'].includes(url.protocol) ? url.href : null;
  } catch {
    return null;
  }
}

export function originalLink(notice) {
  const url = safeUrl(notice.url);
  if (!url) return '<p>원문 주소를 확인할 수 없어요.</p>';
  return `<a class="primary-link" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">원문 보기 ↗</a>`;
}
