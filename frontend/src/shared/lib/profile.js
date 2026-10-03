import { config } from '../config.js';
import { demoState, isDemoMode } from './demo-mode.js';

export function readStoredObject(storage, key) {
  try {
    const value = JSON.parse(storage.getItem(key) || 'null');
    return value && typeof value === 'object' && !Array.isArray(value) ? value : {};
  } catch {
    return {};
  }
}

export function readLocalObject(key) {
  if (isDemoMode() && key === config.profileKey) return demoState.profile;
  try {
    return readStoredObject(localStorage, key);
  } catch {
    return {};
  }
}

export function profileTags(profile) {
  const values = profile.tags ?? profile.recommendationTags ?? profile.history?.tags;
  return Array.isArray(values) ? values.filter((item) => config.tags.includes(item)) : [];
}

function historyItem(item) {
  if (typeof item === 'string') return item;
  if (!item || typeof item !== 'object') return '';
  return [item.title ?? item.name, item.role, item.period ?? item.date]
    .filter((value) => ['string', 'number'].includes(typeof value) && String(value).trim())
    .join(' · ');
}

export function profileValue(profile, key) {
  if (!Object.hasOwn(config.profileFields, key)) return null;
  const historyKeys = ['certificates', 'awards', 'activities'];
  const value = historyKeys.includes(key) ? profile.history?.[key] : profile[key];
  if (Array.isArray(value)) return value.map(historyItem).filter(Boolean).join('\n') || null;
  return ['string', 'number'].includes(typeof value) && String(value).trim() ? String(value) : null;
}
