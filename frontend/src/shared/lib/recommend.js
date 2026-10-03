import { config } from '../config.js';
import { getMockProfile, getRecommendations } from '../api/api-client.js';
import { readLocalObject } from './profile.js';

/**
 * 추천 적합도: 공지마다 「될 가능성(chance)」과 근거 한 줄을 서버에서 받아 온다.
 * 서버로는 학과·학년·상태·관심 분야·태그만 보낸다. 이름·학번·연락처는 보내지 않는다 (지침서 8절).
 */
export function toSituation(profile, tags) {
  const year = Number.parseInt(profile?.year, 10);
  const interests = Array.isArray(profile?.interests) ? profile.interests : [];
  return {
    situation: {
      major: typeof profile?.major === 'string' ? profile.major : null,
      year: Number.isInteger(year) && year >= 1 && year <= 6 ? year : null,
      status: typeof profile?.status === 'string' ? profile.status : '재학',
      graduating: profile?.graduating === true,
      interests: interests.filter((item) => config.categories.includes(item)),
    },
    tags,
  };
}

/** 내 프로필. 기기에 저장된 것이 없으면 mock 프로필을 쓴다 (입력 화면은 아직 없다). */
export async function loadProfile(signal) {
  const local = readLocalObject(config.profileKey);
  if (local.major || local.year) return local;
  return getMockProfile(signal);
}

export async function loadFits(noticeIds, tags, signal) {
  if (!noticeIds.length) return {};
  const profile = await loadProfile(signal);
  const body = { ...toSituation(profile, tags), noticeIds };
  const items = await getRecommendations(body, signal);
  return Object.fromEntries(
    items.map((item) => [item.noticeId, { chance: item.chance, reason: item.reason }]),
  );
}

export function withFits(notices, fits) {
  return notices.map((notice) => ({ ...notice, fit: fits[notice.id] ?? null }));
}

/**
 * 추천 점수. 순서대로 1) 될 가능성이 반반은 되는 글 2) 내가 켠 태그와 겹치는 글 3) 가능성 높은 글.
 * 적합도를 아직 못 받았으면 50 으로 본다.
 */
export function fitScore(notice) {
  const chance = Number.isFinite(notice.fit?.chance) ? notice.fit.chance : 50;
  const likely = chance >= 50 ? 1000 : 0;
  return likely + 100 * Math.min(notice.matchedTags?.length ?? 0, 2) + chance;
}

/** 추천순: 점수가 높은 글 먼저, 같으면 서버가 준 순서를 지킨다. */
export function rankByFit(notices) {
  return notices
    .map((notice, index) => ({ notice, index }))
    .sort((a, b) => fitScore(b.notice) - fitScore(a.notice) || a.index - b.index)
    .map((item) => item.notice);
}
