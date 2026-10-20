import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const files = [];
function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const target = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(target);
    else if (/\.(html|md)$/.test(entry.name)) files.push(target);
  }
}
walk(root);
let checked = 0;
const failures = [];
const ids = new Map();
for (const filename of files.filter(f => f.endsWith('.html'))) {
  const all = [...fs.readFileSync(filename, 'utf8').matchAll(/\bid="([^"]+)"/g)].map(m => m[1]);
  if (new Set(all).size !== all.length) failures.push(`${filename}: duplicate HTML id`);
  ids.set(filename, new Set(all));
}
for (const filename of files) {
  const content = fs.readFileSync(filename, 'utf8');
  const links = filename.endsWith('.html')
    ? [...content.matchAll(/\b(?:href|src)="([^"]+)"/g)].map(m => m[1])
    : [...content.matchAll(/\[[^\]]+\]\(((?:[^()\s]|\([^()]*\))+)\)/g)].map(m => m[1]);
  for (const link of links) {
    if (/^(https?:|mailto:|data:|javascript:)/i.test(link)) continue;
    const [raw, fragment] = link.split('#');
    const target = raw ? path.resolve(path.dirname(filename), decodeURIComponent(raw.split('?')[0])) : filename;
    if (!fs.existsSync(target)) failures.push(`${path.relative(root, filename)}: missing ${link}`);
    else if (fragment && target.endsWith('.html') && !ids.get(target)?.has(decodeURIComponent(fragment))) failures.push(`${path.relative(root, filename)}: missing anchor ${link}`);
    checked++;
  }
}
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'contracts/tool-contracts.json')));
const html = fs.readFileSync(path.join(root, 'architecture.html'), 'utf8');
if (!html.includes(`${catalog.tools.length} proposed operations`)) failures.push('Overview tool count disagrees with registry');
if ((html.match(/data-agent-doc="D[1-8]"/g) || []).length !== 7) failures.push('Overview must have seven current agent cards');
if (/data-agent-doc="D2"/.test(html)) failures.push('Removed D2 restored');
if (failures.length) throw new Error(failures.join('\n'));
console.log(`PASS: ${checked} local file/anchor links; unique HTML IDs; seven-agent roster and ${catalog.tools.length}-tool count.`);
