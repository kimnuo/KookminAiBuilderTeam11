import { config } from '../../shared/config.js';

function evidenceItems(values) {
  return Array.isArray(values)
    ? values.filter((item) => item && typeof item.evidence === 'string' && item.evidence.trim())
    : [];
}

export function requirementItems(data) {
  const fields = evidenceItems(data?.fields).filter(
    (item) =>
      Object.hasOwn(config.profileFields, item.key) ||
      (item.key === 'other' && typeof item.label === 'string' && item.label.trim()),
  );
  const documents = evidenceItems(data?.documents).filter(
    (item) => typeof item.name === 'string' && item.name.trim(),
  );
  return { fields, documents };
}
