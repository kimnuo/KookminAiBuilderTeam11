import { config } from '../config.js';

export function normalizeSearch(value) {
  let text = String(value ?? '')
    .normalize('NFKC')
    .toLocaleLowerCase('ko')
    .replace(/[^\p{L}\p{N}]/gu, '');
  for (const alias of config.searchAliases) {
    for (const term of alias.terms) text = text.replaceAll(term, alias.replacement);
  }
  return text;
}

export function matchesSearch(values, query) {
  const text = normalizeSearch(values.filter(Boolean).join(' '));
  const words = query.trim().split(/\s+/u).map(normalizeSearch).filter(Boolean);
  return words.every((word) => text.includes(word));
}
