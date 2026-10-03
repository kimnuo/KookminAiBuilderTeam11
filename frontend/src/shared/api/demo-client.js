import { config } from '../config.js';
import { demoState, isDemoMode } from '../lib/demo-mode.js';

let dataPromise;

async function readFixture(name) {
  const response = await fetch(`${config.demoBase}/${name}.json`);
  if (!response.ok) throw new Error('더미 데이터를 불러오지 못했어요.');
  return response.json();
}

function loadData() {
  dataPromise ??= Promise.all(
    ['notices', 'more-notices', 'campus-notices', 'sources', 'requirements', 'profile'].map(
      readFixture,
    ),
  ).then(([notices, more, campus, sources, requirements, profile]) => {
    demoState.profile = profile;
    return { notices: [...notices, ...more, ...campus], sources, requirements };
  });
  return dataPromise;
}

export async function prepareDemo() {
  if (isDemoMode()) await loadData();
}

function currentNotices(notices) {
  const today = new Intl.DateTimeFormat('sv-SE', { timeZone: config.timeZone }).format(new Date());
  const offset = Date.parse(today) - Date.parse(notices[0].postedAt);
  return notices.map((notice) => {
    const deadline = notice.ai.deadline;
    const date = new Date(Date.parse(deadline.date) + offset).toISOString().slice(0, 10);
    return {
      ...notice,
      postedAt: today,
      ai: {
        ...notice.ai,
        deadline: { ...deadline, date, evidence: deadline.evidence.replace(deadline.date, date) },
      },
    };
  });
}

export async function requestDemo(path, signal) {
  signal?.throwIfAborted();
  const data = await loadData();
  signal?.throwIfAborted();
  const url = new URL(path, 'https://example.com');
  const notices = currentNotices(data.notices);
  if (url.pathname === '/sources') return data.sources;
  if (url.pathname === '/feed') {
    return url.searchParams.get('sort') === 'deadline'
      ? notices.sort((a, b) => a.ai.deadline.date.localeCompare(b.ai.deadline.date))
      : notices;
  }
  const [, , id, section] = url.pathname.split('/');
  if (section === 'requirements') return data.requirements[id];
  return notices.find((notice) => notice.id === id);
}
