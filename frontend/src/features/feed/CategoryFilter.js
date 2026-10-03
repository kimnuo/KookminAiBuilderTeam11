import { config } from '../../shared/config.js';
import { escapeHtml } from '../../shared/lib/html.js';
import { noticeGroups } from '../../shared/lib/notice-groups.js';
import { icon } from '../../shared/ui/icons.js';

function markup() {
  return `<button type="button" class="category-all" data-all aria-pressed="true">${icon('document')}전체 공고<span data-count="all">—</span></button>
    <fieldset class="category-options"><legend>카테고리 <small>여러 개 선택 가능</small></legend>
    ${config.noticeGroups.map((group) => `<label class="category-option"><input type="checkbox" value="${group.id}" />${icon(group.icon)}<span>${escapeHtml(group.label)}</span><span class="category-count" data-count="${group.id}">—</span></label>`).join('')}
    </fieldset>`;
}

class CategoryFilter {
  constructor(onChange) {
    this.values = new Set();
    this.onChange = onChange;
    this.targets = ['category-navigation', 'mobile-categories'].map((id) =>
      document.getElementById(id),
    );
    this.targets.forEach((target) => {
      target.innerHTML = markup();
      target.addEventListener('change', (event) => this.changed(event));
      target.querySelector('[data-all]').addEventListener('click', () => this.clear());
    });
  }

  changed(event) {
    const input = event.target;
    if (!(input instanceof HTMLInputElement)) return;
    if (input.checked) this.values.add(input.value);
    else this.values.delete(input.value);
    this.onChange();
  }

  clear() {
    this.values.clear();
    this.onChange();
  }

  update(notices) {
    const counts = Object.fromEntries(config.noticeGroups.map((group) => [group.id, 0]));
    notices.forEach((notice) => noticeGroups(notice).forEach((id) => counts[id]++));
    this.targets.forEach((target) => {
      target.querySelector('[data-all]').setAttribute('aria-pressed', String(!this.values.size));
      target.querySelectorAll('input').forEach((input) => {
        input.checked = this.values.has(input.value);
      });
      target.querySelectorAll('[data-count]').forEach((node) => {
        if (!(node instanceof HTMLElement)) return;
        node.textContent = String(
          node.dataset.count === 'all' ? notices.length : counts[node.dataset.count],
        );
      });
    });
  }
}

export function createCategoryFilter(onChange) {
  return new CategoryFilter(onChange);
}
