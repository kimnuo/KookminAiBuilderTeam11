import { config } from '../../shared/config.js';
import { getRequirements } from '../../shared/api/api-client.js';
import { escapeHtml } from '../../shared/lib/html.js';
import { profileValue, readLocalObject } from '../../shared/lib/profile.js';
import { requirementItems } from './requirements.js';

function fieldsMarkup(fields, profile) {
  return fields
    .map((item, index) => {
      const value = profileValue(profile, item.key);
      const label = item.key === 'other' ? item.label : config.profileFields[item.key];
      return `<div class="requirement-row"><div class="requirement-description">
      <strong>${escapeHtml(label)} <span class="requirement-kind">${item.required === true ? '필수' : item.required === false ? '선택' : '필수 여부 원문 확인'}</span></strong>
      <div class="requirement-evidence">근거: ${escapeHtml(item.evidence)}</div>
      <div class="requirement-value ${value === null ? 'missing-value' : ''}">${escapeHtml(value ?? '내 정보 없음 · 직접 준비해 주세요.')}</div>
    </div>${value !== null ? `<button class="copy-button" type="button" data-copy-index="${index}">복사</button>` : ''}</div>`;
    })
    .join('');
}

function documentsMarkup(documents) {
  return documents
    .map(
      (item) => `<div class="requirement-row"><div class="requirement-description">
    <strong>${escapeHtml(item.name)} <span class="requirement-kind">서류</span></strong>
    ${item.condition ? `<div class="requirement-value">${escapeHtml(item.condition)}</div>` : ''}
    <div class="requirement-evidence">근거: ${escapeHtml(item.evidence)}</div>
    <div class="missing-value">원문을 확인해 직접 준비해 주세요.</div>
  </div></div>`,
    )
    .join('');
}

class ApplyPanel {
  constructor() {
    this.version = 0;
  }

  async load(id, target, signal) {
    const current = ++this.version;
    try {
      const data = requirementItems(await getRequirements(id, signal));
      if (current !== this.version || signal.aborted || !target.isConnected) return;
      const profile = readLocalObject(config.profileKey);
      target.innerHTML =
        data.fields.length || data.documents.length
          ? `<div class="requirements">${fieldsMarkup(data.fields, profile)}${documentsMarkup(data.documents)}</div>`
          : '<p>근거가 확인된 필요 항목이 없어요. 공고 원문을 확인해 주세요.</p>';
      target.addEventListener('click', (event) =>
        this.copyField(event, data.fields, profile, current),
      );
    } catch (error) {
      if (current !== this.version || signal.aborted || !target.isConnected) return;
      target.innerHTML = '<p>지원 준비 정보를 불러오지 못했어요. 원문을 확인해 주세요.</p>';
    }
  }

  async copyField(event, fields, profile, current) {
    const button =
      event.target instanceof Element ? event.target.closest('[data-copy-index]') : null;
    if (!(button instanceof HTMLButtonElement)) return;
    const value = profileValue(profile, fields[Number(button.dataset.copyIndex)]?.key);
    if (value === null) return;
    try {
      await navigator.clipboard.writeText(value);
      if (current === this.version) button.textContent = '복사됨';
    } catch {
      if (current === this.version) button.textContent = '복사 실패 · 값을 선택해 주세요';
    }
  }

  cancel() {
    ++this.version;
  }
}

export function createApplyPanel() {
  const panel = new ApplyPanel();
  return {
    load: (id, target, signal) => panel.load(id, target, signal),
    cancel: () => panel.cancel(),
  };
}
