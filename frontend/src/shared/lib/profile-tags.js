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

/** 내 태그는 꺼진 것만, 내 태그가 아닌 분야 태그는 켠 것만 저장한다. */
function toggles() {
  const saved = readLocalObject(config.tagToggleKey);
  return {
    off: Array.isArray(saved.disabled) ? saved.disabled : [],
    on: Array.isArray(saved.extra) ? saved.extra : [],
  };
}

/** 내 프로필 태그 + 나머지 분야 태그. 화면에서 아무 태그나 켜 보려고 전부 보여 준다. */
export function otherTags() {
  return config.tags.filter((tag) => !tagState.tags.includes(tag));
}

export function activeTags() {
  const { off, on } = toggles();
  const mine = tagState.tags.filter((tag) => !off.includes(tag));
  return [...mine, ...otherTags().filter((tag) => on.includes(tag))];
}

export function toggleTag(tag) {
  const { off, on } = toggles();
  const mine = tagState.tags.includes(tag);
  const list = new Set(mine ? off : on);
  if (list.has(tag)) list.delete(tag);
  else list.add(tag);
  const next = mine ? { disabled: [...list], extra: on } : { disabled: off, extra: [...list] };
  try {
    localStorage.setItem(config.tagToggleKey, JSON.stringify(next));
  } catch {
    // 저장소를 못 쓰는 환경이면 이번 화면에서만 바뀐다
  }
}

/** 태그를 맞춰 볼 글자: 요약 제목·원 제목·요약문에 한 페이지 요약 속 내용까지 더한다. */
function noticeText(notice) {
  const digest = notice.digest ?? {};
  return [
    notice.title,
    notice.originalTitle,
    ...(notice.ai?.summary ?? []),
    ...(digest.keyPoints ?? []).flatMap((item) => [item?.label, item?.value]),
    ...(digest.requirements ?? []).map((item) => item?.text),
    ...(digest.etc ?? []),
  ]
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

/** 켜진 태그와 겹치는 것을 글마다 적어 둔다. 정렬과 상관없이 카드에 태그가 보이게. */
export function withTags(notices, tags) {
  if (!tags.length) return notices.map((notice) => ({ ...notice, matchedTags: [] }));
  return notices.map((notice) => ({ ...notice, matchedTags: matchedTags(notice, tags) }));
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

/** 태그마다 겹치는 글이 몇 개인지. 태그 단추에 숫자로 보여 준다. */
export function tagCounts(notices) {
  const all = [...tagState.tags, ...otherTags()];
  const counts = {};
  for (const notice of notices)
    for (const tag of matchedTags(notice, all)) counts[tag] = (counts[tag] ?? 0) + 1;
  return counts;
}
