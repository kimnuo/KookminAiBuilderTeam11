import { config } from '../config.js';
import { normalizeSearch } from './search.js';

export function noticeGroups(notice) {
  const ai = notice.ai?.status === 'done' ? notice.ai : null;
  const categories = Array.isArray(ai?.categories) ? ai.categories : [];
  const source = normalizeSearch(
    [
      notice.source?.id,
      notice.source?.name,
      notice.source?.group,
      notice.department,
      notice.url,
    ].join(' '),
  );
  const title = normalizeSearch(notice.title);
  const groups = config.noticeGroups.filter((group) => {
    if (group.exclude?.some((word) => title.includes(normalizeSearch(word)))) return false;
    return (
      group.sources?.some((word) => source.includes(normalizeSearch(word))) ||
      group.categories?.some((category) => categories.includes(category)) ||
      group.keywords?.some((word) => title.includes(normalizeSearch(word)))
    );
  });
  return groups.length ? groups.map((group) => group.id) : ['other'];
}

export function groupLabels(notice) {
  const groups = noticeGroups(notice);
  return config.noticeGroups
    .filter((group) => groups.includes(group.id))
    .map((group) => group.label);
}
