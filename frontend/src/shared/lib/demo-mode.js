import { config } from '../config.js';

export const demoState = { profile: {} };

export function isDemoMode() {
  return (
    typeof location !== 'undefined' &&
    new URLSearchParams(location.search).get(config.demoQueryKey) === '1'
  );
}
