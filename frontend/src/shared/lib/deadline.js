import { config } from '../config.js';

export function validDeadline(deadline) {
  if (!deadline || typeof deadline.evidence !== 'string' || !deadline.evidence.trim()) return null;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(deadline.date)) return null;
  const date = new Date(`${deadline.date}T00:00:00+09:00`);
  if (Number.isNaN(date.getTime())) return null;
  if (new Date(`${deadline.date}T00:00:00Z`).toISOString().slice(0, 10) !== deadline.date)
    return null;
  if (deadline.time != null && !/^([01]\d|2[0-3]):[0-5]\d$/.test(deadline.time)) return null;
  return { date: deadline.date, time: deadline.time ?? null, evidence: deadline.evidence.trim() };
}

function koreaDate(now) {
  const parts = new Intl.DateTimeFormat('en', {
    timeZone: config.timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).formatToParts(now);
  const part = (type) => parts.find((item) => item.type === type).value;
  return `${part('year')}-${part('month')}-${part('day')}`;
}

export function deadlineExpired(deadline, now = new Date()) {
  const valid = validDeadline(deadline);
  if (!valid) return false;
  if (!valid.time) return valid.date < koreaDate(now);
  return new Date(`${valid.date}T${valid.time}:00+09:00`).getTime() <= now.getTime();
}

export function deadlineLabel(deadline, now = new Date()) {
  const valid = validDeadline(deadline);
  if (!valid) return { label: '원문 확인', className: 'no-deadline' };
  if (deadlineExpired(valid, now)) return { label: '마감', className: 'no-deadline' };
  const days = Math.round((Date.parse(valid.date) - Date.parse(koreaDate(now))) / 86400000);
  if (days === 0) return { label: '오늘 마감', className: '' };
  if (days <= 7) return { label: `D-${days}`, className: '' };
  return { label: `${valid.date}${valid.time ? ` ${valid.time}` : ''}`, className: 'no-deadline' };
}
