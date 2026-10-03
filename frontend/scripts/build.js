import { cp, mkdir, rm } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const output = `${root}dist`;
await rm(output, { recursive: true, force: true });
await mkdir(output, { recursive: true });
await cp(`${root}index.html`, `${output}/index.html`);
await cp(`${root}src`, `${output}/src`, { recursive: true });
await cp(`${root}../mock`, `${output}/mock`, { recursive: true });
console.log('Static build ready: frontend/dist');
