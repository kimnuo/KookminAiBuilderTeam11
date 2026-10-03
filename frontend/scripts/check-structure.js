import { readdir, readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import ts from 'typescript';

const root = fileURLToPath(new URL('../src/', import.meta.url));
const errors = [];

async function checkDirectory(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = `${directory}/${entry.name}`;
    if (entry.isDirectory()) {
      await checkDirectory(path);
      continue;
    }
    const text = await readFile(path, 'utf8');
    const lines = text.trimEnd().split('\n').length;
    if (lines > 200) errors.push(`${path}: ${lines} lines (max 200)`);
    if (!path.endsWith('.js')) continue;
    const source = ts.createSourceFile(path, text, ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
    visit(source, source);
    if (!path.includes('/shared/api/') && /\bfetch\s*\(/.test(text))
      errors.push(`${path}: fetch outside shared/api`);
    for (const statement of source.statements) checkImport(statement, path);
  }
}

function visit(node, source) {
  if (ts.isFunctionLike(node) && node.body) {
    const start = source.getLineAndCharacterOfPosition(node.getStart(source)).line;
    const end = source.getLineAndCharacterOfPosition(node.end).line;
    if (end - start + 1 > 40)
      errors.push(`${source.fileName}:${start + 1}: function exceeds 40 lines`);
  }
  ts.forEachChild(node, (child) => visit(child, source));
}

function checkImport(statement, path) {
  if (!ts.isImportDeclaration(statement) || !path.includes('/features/')) return;
  const target = statement.moduleSpecifier.getText().slice(1, -1);
  if (target.includes('/features/') || /^\.\.\/(feed|notice|apply-helper)\//.test(target))
    errors.push(`${path}: cross-feature import`);
}

await checkDirectory(root);
if (errors.length) {
  console.error(errors.join('\n'));
  process.exitCode = 1;
} else console.log('AGENTS structure: file/function limits, imports and fetch location passed');
