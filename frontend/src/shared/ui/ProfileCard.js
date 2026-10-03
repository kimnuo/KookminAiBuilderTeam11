import { escapeHtml } from '../lib/html.js';
import { activeTags, tagState, toggleTag } from '../lib/profile-tags.js';

export function renderProfileCard() {
  const target = document.getElementById('profile-tags');
  const active = activeTags();
  target.innerHTML = tagState.tags.length
    ? tagState.tags.map((tag) => tagButton(tag, active.includes(tag))).join('')
    : '<span class="muted-tag">등록된 태그가 없어요</span>';
}

function tagButton(tag, on) {
  return `<button type="button" class="profile-tag ${on ? '' : 'off'}" data-tag="${escapeHtml(tag)}" aria-pressed="${on}" title="${on ? '눌러서 끄기' : '눌러서 켜기'}">${escapeHtml(tag)}</button>`;
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
