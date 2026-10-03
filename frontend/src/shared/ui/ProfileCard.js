import { escapeHtml } from '../lib/html.js';
import { activeTags, otherTags, tagState, toggleTag } from '../lib/profile-tags.js';

/** 태그마다 겹치는 글 수. 피드를 그릴 때 받아 두고, 태그를 눌렀을 때도 그대로 쓴다. */
const matchCounts = { value: {} };

export function renderProfileCard(counts) {
  if (counts) matchCounts.value = counts;
  const target = document.getElementById('profile-tags');
  const active = activeTags();
  const mine = tagState.tags.map((tag) => tagButton(tag, active.includes(tag)));
  const others = otherTags().map((tag) => tagButton(tag, active.includes(tag)));
  target.innerHTML =
    (mine.length ? mine.join('') : '<span class="muted-tag">등록된 태그가 없어요</span>') +
    (others.length ? `<p class="tag-group">다른 분야로도 켜 보기</p>${others.join('')}` : '');
}

function tagButton(tag, on) {
  const count = matchCounts.value[tag] ?? 0;
  const name = escapeHtml(tag);
  return `<button type="button" class="profile-tag ${on ? '' : 'off'}" data-tag="${name}" aria-pressed="${on}" aria-label="${name} 태그, 겹치는 공고 ${count}개, ${on ? '눌러서 끄기' : '눌러서 켜기'}">${name}<span class="tag-count">${count}</span></button>`;
}

/** 태그를 눌러 켜고 끈다. 바뀌면 onChange 로 피드를 다시 그린다. */
export function bindProfileTagToggles(onChange) {
  document.getElementById('profile-tags').addEventListener('click', (event) => {
    const button = event.target instanceof Element ? event.target.closest('[data-tag]') : null;
    if (!button) return;
    toggleTag(button.getAttribute('data-tag'));
    renderProfileCard();
    onChange();
  });
}
