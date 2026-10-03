export function icon(name) {
  const id = /^[a-z-]+$/.test(name) ? name : 'document';
  return `<svg class="icon" aria-hidden="true" focusable="false"><use href="./src/shared/ui/icons.svg#${id}"></use></svg>`;
}
