import { config } from '../config.js';
import { isDemoMode } from '../lib/demo-mode.js';
import { requestDemo } from './demo-client.js';
import { toView } from '../lib/digest-view.js';

async function request(path, signal) {
  if (isDemoMode()) return requestDemo(path, signal);
  const response = await fetch(`${config.apiBase}${path}`, {
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
    signal,
  });
  if (!response.ok) throw new Error(`요청에 실패했어요 (${response.status})`);
  return response.json();
}

function listResponse(data, key) {
  const items = Array.isArray(data) ? data : (data?.items ?? data?.[key]);
  if (!Array.isArray(items)) throw new Error('응답 형식을 확인할 수 없어요.');
  return items;
}

export async function getFeed(sort, userId, signal) {
  const query = new URLSearchParams({ sort });
  if (typeof userId === 'string' && userId.trim()) query.set('userId', userId);
  const data = await request(`/feed?${query}`, signal);
  const items = listResponse(data, 'notices').map(toView);
  return items.filter(
    (item) => item && typeof item.id === 'string' && typeof item.title === 'string',
  );
}

export async function getSources(signal) {
  const data = await request('/sources', signal);
  return listResponse(data, 'sources').filter(
    (item) => item && typeof item.id === 'string' && typeof item.name === 'string',
  );
}

export async function getNotice(id, signal) {
  const data = toView(await request(`/notices/${encodeURIComponent(id)}`, signal));
  if (!data || data.id !== id || typeof data.title !== 'string')
    throw new Error('공고 응답 형식을 확인할 수 없어요.');
  return data;
}

export function getRequirements(id, signal) {
  return request(`/notices/${encodeURIComponent(id)}/requirements`, signal);
}

export async function getProfileTags(signal) {
  const url = config.profileTagsEndpoint || `${config.demoBase}/profile-tags.json`;
  const response = await fetch(url, {
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
    signal,
  });
  if (!response.ok) throw new Error(`프로필 태그를 불러오지 못했어요 (${response.status})`);
  const data = await response.json();
  const tags = Array.isArray(data) ? data : data?.tags;
  return Array.isArray(tags) ? tags.filter((tag) => config.tags.includes(tag)) : [];
}
