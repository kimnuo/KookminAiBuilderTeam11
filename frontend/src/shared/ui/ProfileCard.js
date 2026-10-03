import { config } from '../config.js';
import { readLocalObject, profileTags } from '../lib/profile.js';
import { escapeHtml } from '../lib/html.js';

export function renderProfileCard() {
  const tags = profileTags(readLocalObject(config.profileKey));
  document.getElementById('profile-tags').innerHTML = tags.length
    ? tags.map((tag) => `<span class="profile-tag">${escapeHtml(tag)}</span>`).join('')
    : '<span class="muted-tag">등록된 태그가 없어요</span>';
}
