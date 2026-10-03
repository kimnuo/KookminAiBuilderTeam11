import { config } from '../config.js';
import { isDemoMode } from '../lib/demo-mode.js';
import { escapeHtml } from '../lib/html.js';

export function renderDemoBanner() {
  if (!isDemoMode()) return;
  const url = new URL(location.href);
  url.searchParams.delete(config.demoQueryKey);
  document
    .querySelector('.main-content')
    .insertAdjacentHTML(
      'afterbegin',
      `<aside class="demo-banner" aria-label="더미 데이터 안내"><div><strong>더미 데이터 미리보기</strong><p>모든 공고·지원 정보는 가상 데이터예요. 실제 모집이나 신청이 아닙니다.</p></div><a href="${escapeHtml(url.pathname + url.search + url.hash)}">실제 데이터 화면</a></aside>`,
    );
}
