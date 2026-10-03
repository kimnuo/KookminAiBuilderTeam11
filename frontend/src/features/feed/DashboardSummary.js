import { config } from '../../shared/config.js';
import { validDeadline, deadlineExpired } from '../../shared/lib/deadline.js';
import { icon } from '../../shared/ui/icons.js';

function upcoming(notice, now) {
  const deadline = notice.ai?.status === 'done' ? validDeadline(notice.ai.deadline) : null;
  if (!deadline || deadlineExpired(deadline, now)) return false;
  const today = new Intl.DateTimeFormat('sv-SE', { timeZone: config.timeZone }).format(now);
  return Date.parse(deadline.date) - Date.parse(today) <= config.upcomingDays * 86400000;
}

export function renderDashboard(notices) {
  const now = new Date();
  const stats = [
    {
      label: '전체 공고',
      value: notices.length,
      icon: 'document',
      note: '한곳에 모인 학교 소식과 기회',
    },
    {
      label: `${config.upcomingDays}일 내 마감`,
      value: notices.filter((notice) => upcoming(notice, now)).length,
      icon: 'clock',
      note: '지원 전에 마감일을 확인해요',
    },
    {
      label: '공고 출처',
      value: new Set(notices.map((notice) => notice.source?.id).filter(Boolean)).size,
      icon: 'search',
      note: '출처별로도 골라볼 수 있어요',
    },
  ];
  document.getElementById('dashboard-summary').innerHTML = stats
    .map(
      (stat) =>
        `<div class="dashboard-stat"><span class="stat-icon">${icon(stat.icon)}</span><div><p>${stat.label}</p><strong>${stat.value}<small>개</small></strong><span class="stat-note">${stat.note}</span></div></div>`,
    )
    .join('');
}
