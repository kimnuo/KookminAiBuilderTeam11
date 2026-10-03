import { config } from '../config.js';
import { getProfileTags } from '../api/api-client.js';
import { demoState, isDemoMode } from './demo-mode.js';
import { profileTags, readLocalObject } from './profile.js';

/** 불러온 프로필 태그 전체. 켜짐·꺼짐은 기기에 따로 저장한다 (config.tagToggleKey). */
export const tagState = { tags: [] };

export async function loadProfileTags() {
  if (isDemoMode()) {
    tagState.tags = profileTags(demoState.profile);
    return;
  }
  const local = profileTags(readLocalObject(config.profileKey));
  if (local.length && !config.profileTagsEndpoint) {
    tagState.tags = local;
    return;
  }
  try {
    tagState.tags = await getProfileTags(undefined);
  } catch {
    tagState.tags = local;
  }
}

function disabledTags() {
  const value = readLocalObject(config.tagToggleKey).disabled;
  return Array.isArray(value) ? value : [];
}

export function activeTags() {
  const off = disabledTags();
  return tagState.tags.filter((tag) => !off.includes(tag));
}

export function toggleTag(tag) {
  const off = new Set(disabledTags());
  if (off.has(tag)) off.delete(tag);
  else off.add(tag);
  try {
    localStorage.setItem(config.tagToggleKey, JSON.stringify({ disabled: [...off] }));
  } catch {
    // 저장소를 못 쓰는 환경이면 이번 화면에서만 바뀐다
  }
}

function noticeText(notice) {
  return [notice.title, notice.originalTitle, ...(notice.ai?.summary ?? [])]
    .filter((value) => typeof value === 'string')
    .join(' ');
}

/** 영문 낱말은 단어 단위로만 맞춘다 (「AI」가 email·daily 안에서 걸리지 않게). */
function hasWord(text, word) {
  if (!/^[A-Za-z]+$/.test(word)) return text.includes(word);
  return new RegExp(`(?<![A-Za-z])${word}(?![A-Za-z])`, 'i').test(text);
}

export function matchedTags(notice, tags) {
  const text = noticeText(notice);
  return tags.filter((tag) =>
    (config.tagKeywords[tag] ?? [tag]).some((word) => hasWord(text, word)),
  );
}

/** 추천순 임시 규칙: 켜진 태그와 많이 겹치는 글을 위로, 같으면 서버 순서 유지. */
export function rankByTags(notices, tags) {
  if (!tags.length) return notices;
  return notices
    .map((notice, index) => ({
      notice: { ...notice, matchedTags: matchedTags(notice, tags) },
      index,
    }))
    .sort((a, b) => b.notice.matchedTags.length - a.notice.matchedTags.length || a.index - b.index)
    .map((item) => item.notice);
}
