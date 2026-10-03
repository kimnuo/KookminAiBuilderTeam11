import { getFeed, getSources } from '../../shared/api/api-client.js';
import { escapeHtml } from '../../shared/lib/html.js';
import { filterNotices } from '../../shared/lib/notice-data.js';
import { feedCard } from './FeedCard.js';
import { createCategoryFilter } from './CategoryFilter.js';
import { renderDashboard } from './DashboardSummary.js';
import { renderFilterSummary } from './FilterSummary.js';

class FeedPage {
  constructor({ onSelect, getUserId }) {
    this.onSelect = onSelect;
    this.getUserId = getUserId;
    this.list = document.getElementById('notice-list');
    this.sortInput = /** @type {HTMLSelectElement} */ (document.getElementById('sort-select'));
    this.query = /** @type {HTMLInputElement} */ (document.getElementById('search-input'));
    this.category = createCategoryFilter(() => this.render());
    this.source = /** @type {HTMLSelectElement} */ (document.getElementById('source-filter'));
    this.state = { notices: [], sort: this.sortInput.value, version: 0, controller: null };
    this.sourceVersion = 0;
    this.list.addEventListener('click', (event) => this.select(event));
    this.list.addEventListener('keydown', (event) => this.select(event));
    [this.query, this.source].forEach((input) =>
      input.addEventListener('input', () => this.render()),
    );
    this.sortInput.addEventListener('change', () => this.load());
    document.getElementById('clear-filters').addEventListener('click', () => this.clearFilters());
    document.getElementById('filter-summary').addEventListener('click', (event) => {
      const button =
        event.target instanceof Element ? event.target.closest('[data-remove-group]') : null;
      if (!(button instanceof HTMLElement)) return;
      this.category.values.delete(button.dataset.removeGroup);
      this.render();
    });
    this.refresh();
  }

  render() {
    const items = filterNotices(this.state.notices, {
      query: this.query.value,
      category: '',
      groups: [...this.category.values],
      source: this.source.value,
      sort: this.state.sort,
    });
    this.category.update(this.state.notices);
    renderDashboard(this.state.notices);
    renderFilterSummary(this.category.values, this.query.value, this.source.value, items.length);
    document.getElementById('result-count').textContent = String(items.length);
    this.list.innerHTML = items.map((item) => feedCard(item, this.state.sort)).join('');
    document.getElementById('empty-state').hidden = items.length > 0;
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
      this.status(`공고를 불러오지 못했어요. ${error.message}`, true);
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
      this.source.title = '출처 목록을 불러오지 못했어요. 잠시 후 다시 접속해 주세요.';
    }
  }

  select(event) {
    const card = event.target instanceof Element ? event.target.closest('[data-id]') : null;
    if (!card) return;
    if (event.type === 'keydown' && !['Enter', ' '].includes(event.key)) return;
    if (event.type === 'keydown') event.preventDefault();
    this.onSelect(card.getAttribute('data-id'));
  }

  clearFilters() {
    this.query.value = '';
    this.source.value = '';
    this.category.clear();
    this.query.focus();
  }

  refresh() {
    this.loadSources();
    this.load();
  }
}

export function createFeedPage(options) {
  return new FeedPage(options);
}
