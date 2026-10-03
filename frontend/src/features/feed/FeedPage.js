import { config } from '../../shared/config.js';
import { getFeed, getSources } from '../../shared/api/api-client.js';
import { escapeHtml } from '../../shared/lib/html.js';
import { filterNotices } from '../../shared/lib/notice-data.js';
import { activeTags, rankByTags, tagCounts, withTags } from '../../shared/lib/profile-tags.js';
import { feedCard } from './FeedCard.js';

class FeedPage {
  constructor({ onSelect, getUserId, onRender }) {
    this.onSelect = onSelect;
    this.getUserId = getUserId;
    this.onRender = onRender;
    this.list = document.getElementById('notice-list');
    this.sortInput = /** @type {HTMLSelectElement} */ (document.getElementById('sort-select'));
    this.query = /** @type {HTMLInputElement} */ (document.getElementById('search-input'));
    this.category = /** @type {HTMLSelectElement} */ (document.getElementById('category-filter'));
    this.source = /** @type {HTMLSelectElement} */ (document.getElementById('source-filter'));
    this.state = { notices: [], sort: this.sortInput.value, version: 0, controller: null };
    this.sourceVersion = 0;
    this.list.addEventListener('click', (event) => this.select(event));
    this.list.addEventListener('keydown', (event) => this.select(event));
    [this.query, this.category, this.source].forEach((input) =>
      input.addEventListener('input', () => this.render()),
    );
    this.sortInput.addEventListener('change', () => this.load());
    document.getElementById('refresh-button').addEventListener('click', () => this.refresh());
    this.category.insertAdjacentHTML(
      'beforeend',
      config.categories.map((item) => `<option>${escapeHtml(item)}</option>`).join(''),
    );
    this.refresh();
  }

  render() {
    const tags = activeTags();
    // 켜진 태그를 글마다 먼저 적어 둔다. 마감순에서도 카드에 겹친 태그가 보이게.
    const tagged = withTags(this.state.notices, tags);
    const filtered = filterNotices(tagged, {
      query: this.query.value,
      category: this.category.value,
      source: this.source.value,
      sort: this.state.sort,
    });
    const items = this.state.sort === 'recommend' ? rankByTags(filtered, tags) : filtered;
    document.getElementById('result-count').textContent = String(items.length);
    this.list.innerHTML = items.map((item) => feedCard(item, this.state.sort)).join('');
    document.getElementById('empty-state').hidden = items.length > 0;
    this.onRender?.(tagCounts(this.state.notices));
  }

  status(message = '', error = false) {
    const target = document.getElementById('feed-status');
    target.textContent = message;
    target.hidden = !message;
    target.classList.toggle('error', error);
  }

  async load() {
    const state = this.state;
    state.controller?.abort();
    state.controller = new AbortController();
    const version = ++state.version;
    const sort = this.sortInput.value;
    this.status('공고를 불러오고 있어요.');
    this.list.setAttribute('aria-busy', 'true');
    try {
      const items = await getFeed(sort, this.getUserId(), state.controller.signal);
      if (version !== state.version) return;
      state.notices = items;
      state.sort = sort;
      this.render();
      this.status('');
    } catch (error) {
      if (version !== state.version || error.name === 'AbortError') return;
      this.sortInput.value = state.sort;
      this.status(`피드를 불러오지 못했어요. ${error.message}`, true);
      this.render();
    } finally {
      if (version === state.version) this.list.setAttribute('aria-busy', 'false');
    }
  }

  async loadSources() {
    const version = ++this.sourceVersion;
    try {
      const sources = await getSources(undefined);
      if (version !== this.sourceVersion) return;
      const selected = this.source.value;
      this.source.innerHTML =
        '<option value="">모든 출처</option>' +
        sources
          .map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.name)}</option>`)
          .join('');
      this.source.value = selected;
      this.source.disabled = false;
      this.source.title = '';
      this.render();
    } catch {
      if (version !== this.sourceVersion) return;
      this.source.disabled = true;
      this.source.title = '출처 목록을 불러오지 못했어요. 새로고침으로 다시 시도해 주세요.';
    }
  }

  select(event) {
    const card = event.target instanceof Element ? event.target.closest('[data-id]') : null;
    if (!card) return;
    if (event.type === 'keydown' && !['Enter', ' '].includes(event.key)) return;
    if (event.type === 'keydown') event.preventDefault();
    this.onSelect(card.getAttribute('data-id'));
  }

  refresh() {
    this.loadSources();
    this.load();
  }
}

export function createFeedPage(options) {
  return new FeedPage(options);
}
