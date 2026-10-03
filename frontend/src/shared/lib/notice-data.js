import { config } from '../config.js';
import { deadlineExpired } from './deadline.js';
import { matchesSearch } from './search.js';
import { noticeGroups, groupLabels } from './notice-groups.js';

export function noticeAi(notice) {
  return notice.ai?.status === 'done' ? notice.ai : null;
}

export function summaries(notice) {
  const summary = noticeAi(notice)?.summary;
  return Array.isArray(summary)
    ? summary.filter((item) => typeof item === 'string').slice(0, 3)
    : [];
}

export function recommendationReasons(notice) {
  if (!noticeAi(notice)) return [];
  const reasons =
    notice.recommendationReasons ?? notice.reasons ?? notice.recommendationReason ?? [];
  return (Array.isArray(reasons) ? reasons : [reasons])
    .map((item) => (typeof item === 'string' ? item : item?.text || item?.label))
    .filter((item) => typeof item === 'string' && item.trim());
}

export function categoriesFor(notice) {
  const values = noticeAi(notice)?.categories;
  return Array.isArray(values) ? values.filter((item) => config.categories.includes(item)) : [];
}

export function tagsFor(notice) {
  const values = noticeAi(notice)?.tags;
  return Array.isArray(values) ? values.filter((item) => config.tags.includes(item)) : [];
}

export function filterNotices(notices, filters, now = new Date()) {
  return notices.filter((notice) => {
    const ai = noticeAi(notice);
    const groups = filters.groups ?? [];
    const values = [
      notice.title,
      notice.source?.name,
      notice.source?.group,
      notice.department,
      ai?.apply,
      ai?.audience?.text,
      ...summaries(notice),
      ...tagsFor(notice),
      ...categoriesFor(notice),
      ...groupLabels(notice),
    ];
    return (
      matchesSearch(values, filters.query) &&
      (!filters.category || categoriesFor(notice).includes(filters.category)) &&
      (!groups.length || noticeGroups(notice).some((id) => groups.includes(id))) &&
      (!filters.source || notice.source?.id === filters.source) &&
      (filters.sort !== 'recommend' || !deadlineExpired(ai?.deadline, now))
    );
  });
}
