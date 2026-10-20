import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// A dependency-free renderer for this research pack's Markdown subset.
// Rebuild after editing notes: node research/build-overview.mjs
const root = path.dirname(fileURLToPath(import.meta.url));
const walk = dir => fs.readdirSync(dir, { withFileTypes: true }).flatMap(e => {
  const p = path.join(dir, e.name);
  return e.isDirectory() ? walk(p) : p.endsWith('.md') ? [p] : [];
});
const escape = s => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const idFor = p => p.replace(/\.md$/, '').replaceAll('/', '--').toLowerCase();
const docs = walk(root).sort().map(p => {
  const rel = path.relative(root, p).split(path.sep).join('/');
  const md = fs.readFileSync(p, 'utf8');
  return { rel, md, id: idFor(rel), title: md.match(/^# (.+)$/m)?.[1] || rel };
});
const docMap = new Map(docs.map(d => [d.rel, d.id]));
const descriptions = {
  'uber-debug-assist': 'Fixed workflow, parallel debugging specialists, evidence timelines, and bounded execution.',
  'holmesgpt': 'Inspectable tool loop, structured failures, query concurrency, and open evaluation practices.',
  'assignment-reading': 'Every requirement, deliverable, constraint, and ambiguity in the two-page assignment.',
  'system-requirements': 'Current scope: vague-input discovery, code, database contents, infrastructure, and AI prompt/tool/coordination investigation.',
  'architecture-options': 'User proposal versus fixed workflows and peer handoffs; a hypothesis-driven alternative with explicit trade-offs.',
  'scalable-design': 'Large multi-repository estates: indexed retrieval, deployment provenance, bounded source contracts, expansion rules and scale-validation limits.',
  'question-grounding': 'How D1 earns specific questions from specialist findings; premise tracking, investigator self-audit and planned anti-hallucination tests.',
  'agent-protocol': 'Shared interfaces and lifecycle: late-result applicability, exact-report approval, invalidation and reviewer-failure status.',
  'agent-contract-research': 'Primary-source recheck and the reasoning behind the seven proposed agent contracts.',
  'runtime-and-tools': 'Where code, replicas and cloud sources live; the backend/model/tool loop and a concrete code-to-data handoff.',
  'implementation-plan': 'End-to-end build plan: KookarCore reuse limits, private gateway, source onboarding, role wiring, implementation phases and security gates.',
  'tool-catalog': '41 exact proposed tool contracts: inputs, outputs, source backends, role access and guards.',
  'd1-investigation-lead': 'Navigation access, dynamic delegation, hypothesis comparison, state updates and stopping; no D2.',
  'd3-observability': 'Observed execution, telemetry coverage, asynchronous correlation and delivery outcomes.',
  'd4-code-deployment': 'Discover versioned implementation, cross-repository wiring, effective deployments/config and mechanisms.',
  'd5-data': 'Actual data/read scope, incident-time history, consistency paths and database diagnostics.',
  'd6-ai-behavior': 'Actual AI prompts, retrieval, tools, state handoffs and behavioral divergence.',
  'd7-critic': 'Independent source/premise checks, causal challenge and version-bound report review.',
  'd8-report-writer': 'Concise grounded reports, scoped uncertainty, immutable drafts and no self-approval.',
  'comparison': 'Compare the published evidence against the assignment and identify useful patterns.',
  'evaluation-landscape': 'Benchmarks, datasets, metrics, and fairness considerations for later evaluation.',
  'research-method': 'How claims were checked, what evidence labels mean, and limitations of this research.',
  'next-discussion': 'Questions to resolve when we move from research to choosing an architecture.',
  'readme': 'Reading guide and complete file map for the research pack.'
};
function group(d) {
  if (d.rel.startsWith('contracts/') || /^(runtime-and-tools|tool-catalog)\.md$/.test(d.rel)) return 'Runtime & tool contracts';
  if (d.rel.startsWith('agents/')) return 'Agent contracts';
  if (!d.rel.startsWith('systems/')) return 'Reading guides';
  if (/uber|meta|drp/i.test(d.rel)) return 'Internal production systems';
  if (/datadog|incident-io|incidentio|resolve|cleric/i.test(d.rel)) return 'Commercial systems';
  return 'Open source & research';
}
function description(d) {
  if (d.rel === 'contracts/README.md') return 'Strict schemas and seven complete synthetic Task/model-answer/trusted-result examples; offline contract checks.';
  if (d.rel === 'agents/README.md') return 'Start here: seven agent roles, interaction map, shared protocol and corrected incident example.';
  const key = path.basename(d.rel, '.md').toLowerCase();
  if (descriptions[key]) return descriptions[key];
  if (/datadog/i.test(key)) return 'Hypothesis-driven telemetry investigation and production-data evaluation.';
  if (/incident/i.test(key)) return 'Parallel evidence gathering, revisable findings, and adversarial verification.';
  if (/resolve/i.test(key)) return 'Specialist investigators, verification, and lessons from failed investigations.';
  if (/meta|drp/i.test(key)) return 'Production evidence for change ranking, workflow orchestration, or investigation support.';
  if (/mabc/i.test(key)) return 'Collaborating diagnostic agents, feedback, and paper-versus-code findings.';
  if (/rcacopilot/i.test(key)) return 'Microsoft incident diagnostics, retrieval, and root-cause category prediction.';
  if (/rcagent/i.test(key)) return 'Controller-and-expert investigation with data processing and evidence management.';
  if (/itbench/i.test(key)) return 'Runnable SRE scenarios and an evaluation environment with version-specific limitations.';
  return 'Architecture, evidence, evaluation, assignment relevance, and source links.';
}
function hrefFor(href, doc) {
  if (/^(https?:|mailto:|#)/i.test(href)) return href;
  const decoded = (() => { try { return decodeURI(href); } catch { return href; } })();
  const resolved = path.posix.normalize(path.posix.join(path.posix.dirname(doc.rel), decoded));
  if (docMap.has(resolved)) return '#doc-' + docMap.get(resolved);
  return resolved;
}
function inline(s, doc) {
  const tokens = [];
  const token = html => { tokens.push(html); return '\u0000' + (tokens.length - 1) + '\u0000'; };
  s = s.replace(/`([^`]+)`/g, (_, code) => token('<code>' + escape(code) + '</code>'));
  s = s.replace(/(!?)\[([^\]]+)\]\(((?:[^()\s]|\([^()]*\))+)\)/g, (_, image, label, href) => {
    const url = hrefFor(href, doc);
    if (/^javascript:/i.test(url)) return escape(label);
    if (image) return token('<figure><img loading="lazy" src="' + escape(url) + '" alt="' + escape(label) + '"><figcaption>' + escape(label) + '</figcaption></figure>');
    return token('<a href="' + escape(url) + '"' + (/^https?:/i.test(url) ? ' target="_blank" rel="noopener noreferrer"' : '') + '>' + escape(label) + '</a>');
  });
  s = escape(s).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');
  return s.replace(/\u0000(\d+)\u0000/g, (_, i) => tokens[Number(i)]);
}
function render(md, doc) {
  const lines = md.replaceAll('\r', '').split('\n');
  const out = []; let paragraph = []; let list = null;
  const flush = () => { if (paragraph.length) { out.push('<p>' + inline(paragraph.join(' '), doc) + '</p>'); paragraph = []; } };
  const closeList = () => { if (list) { out.push('</' + list + '>'); list = null; } };
  const cells = s => s.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(v => v.trim());
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^\s*```/.test(line)) {
      flush(); closeList(); const lang = line.trim().slice(3); const code = [];
      while (++i < lines.length && !/^\s*```/.test(lines[i])) code.push(lines[i]);
      out.push('<div class="code-label">' + escape(lang === 'mermaid' ? 'Flow definition (Mermaid source)' : lang || 'Diagram / example') + '</div><pre><code>' + escape(code.join('\n')) + '</code></pre>'); continue;
    }
    if (/^#{1,6} /.test(line)) {
      flush(); closeList(); const m = line.match(/^(#{1,6}) (.+)$/); const level = Math.min(6, m[1].length + 1);
      out.push('<h' + level + '>' + inline(m[2], doc) + '</h' + level + '>'); continue;
    }
    if (line.includes('|') && i + 1 < lines.length && /^\s*\|?\s*:?-{3,}/.test(lines[i + 1])) {
      flush(); closeList(); out.push('<div class="table-wrap"><table><thead><tr>' + cells(line).map(c => '<th>' + inline(c, doc) + '</th>').join('') + '</tr></thead><tbody>'); i++;
      while (i + 1 < lines.length && lines[i + 1].includes('|') && lines[i + 1].trim()) {
        out.push('<tr>' + cells(lines[++i]).map(c => '<td>' + inline(c, doc) + '</td>').join('') + '</tr>');
      }
      out.push('</tbody></table></div>'); continue;
    }
    const lm = line.match(/^(\s*)(?:([-*+])|\d+\.)\s+(.*)$/);
    if (lm) {
      flush(); const type = lm[2] ? 'ul' : 'ol'; if (list !== type) { closeList(); out.push('<' + type + '>'); list = type; }
      out.push('<li' + (lm[1].length ? ' class="indent"' : '') + '>' + inline(lm[3], doc) + '</li>'); continue;
    }
    if (!line.trim()) { flush(); if (list && !/^\s*(?:[-*+]|\d+\.)\s/.test(lines[i + 1] || '')) closeList(); continue; }
    if (/^---+$/.test(line.trim())) { flush(); closeList(); out.push('<hr>'); continue; }
    if (/^>/.test(line)) { flush(); closeList(); out.push('<blockquote>' + inline(line.replace(/^>\s?/, ''), doc) + '</blockquote>'); continue; }
    closeList(); paragraph.push(line.trim());
  }
  flush(); closeList(); return out.join('\n');
}
const groups = ['Reading guides', 'Agent contracts', 'Runtime & tool contracts', 'Internal production systems', 'Commercial systems', 'Open source & research'];
const systemCount = docs.filter(d => d.rel.startsWith('systems/')).length;
const activeAgentCount = docs.filter(d => /^agents\/d[1-8]-/.test(d.rel)).length;
const cards = groups.map(g => '<section class="card-group"><h2>' + g + '</h2><div class="cards">' + docs.filter(d => group(d) === g).map(d => '<a class="card" data-doc="' + d.id + '" href="#doc-' + d.id + '"><span class="file-kind">' + escape(d.rel.startsWith('systems/') ? 'SYSTEM STUDY' : d.rel.startsWith('agents/') ? 'AGENT CONTRACT' : 'DESIGN / RESEARCH NOTE') + '</span><h3>' + escape(d.title.split(':')[0]) + '</h3><p>' + escape(description(d)) + '</p><span class="card-foot">Read study <span aria-hidden="true">↗</span></span></a>').join('') + '</div></section>').join('');
const nav = groups.map(g => '<div class="nav-group"><p>' + g + '</p>' + docs.filter(d => group(d) === g).map(d => '<a data-doc="' + d.id + '" href="#doc-' + d.id + '">' + escape(d.title.split(':')[0]) + '</a>').join('') + '</div>').join('');
const panels = docs.map(d => '<article class="doc-panel" id="doc-' + d.id + '" data-id="' + d.id + '"><div class="doc-toolbar"><a href="#overview">← Overview</a><a href="' + escape(d.rel) + '">Open Markdown ↗</a></div><div class="article-meta">' + escape(group(d)) + ' · ' + escape(d.rel) + '</div>' + render(d.md, d) + '</article>').join('\n');
const searchData = JSON.stringify(docs.map(d => ({ id: d.id, text: (d.title + ' ' + d.md).toLowerCase() }))).replaceAll('<', '\\u003c');
const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><title>Production Incident Investigation — Research Atlas</title>
<style>
:root{--ink:#222b33;--muted:#657078;--accent:#bc4d24;--paper:#faf8f3;--line:#e3e0d8;--sidebar:#f1eee6}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.7 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:var(--accent);text-underline-offset:3px}a:hover{color:#813019}button,input{font:inherit}.layout{display:grid;grid-template-columns:284px minmax(0,1fr);min-height:100vh}.sidebar{background:var(--sidebar);border-right:1px solid var(--line);padding:27px 22px;position:sticky;top:0;height:100vh;overflow:auto}.brand{display:block;text-decoration:none;font-weight:750;font-size:19px;color:var(--ink);line-height:1.35}.brand small{display:block;color:var(--accent);font-size:10px;letter-spacing:1.8px;margin-bottom:10px}.search-label{display:block;font-size:12px;margin-top:24px;color:var(--muted)}#search{width:100%;padding:10px 11px;background:#fff;border:1px solid #d8d3c8;border-radius:6px;margin-top:5px;font-size:13px}#search:focus{outline:2px solid #dd916f;outline-offset:2px}.search-status{font-size:11px;color:var(--muted);min-height:20px;margin:5px 0}.home-link{display:block;margin:13px 0;font-size:14px;font-weight:600;text-decoration:none}.nav-group p{text-transform:uppercase;letter-spacing:1.2px;color:var(--muted);font-size:10px;font-weight:700;margin:22px 0 7px}.nav-group a{display:block;padding:6px 9px;margin-left:-9px;font-size:13px;line-height:1.45;color:#414b52;text-decoration:none;border-radius:5px}.nav-group a:hover,.nav-group a.active{background:#e5dfd2;color:#a43d19}.sidebar footer{border-top:1px solid #d9d3c6;margin-top:26px;padding-top:14px;font-size:11px;color:var(--muted)}main{min-width:0;padding:46px clamp(22px,4.8vw,82px) 80px;max-width:1500px}.eyebrow{color:var(--accent);text-transform:uppercase;font-weight:750;letter-spacing:2px;font-size:11px}.hero h1{font-family:Georgia,"Times New Roman",serif;font-weight:400;font-size:clamp(33px,3.9vw,58px);letter-spacing:-1.5px;line-height:1.09;max-width:840px;margin:17px 0 24px}.hero .intro{font-size:18px;color:#58646c;max-width:780px;line-height:1.7}.stats{display:flex;gap:34px;margin:29px 0 34px;padding:23px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);flex-wrap:wrap}.stat b{font-size:28px;font-weight:650;line-height:1.2;display:block}.stat span{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:1px}.note{padding:17px 21px;border-left:3px solid var(--accent);background:#f0e9dd;max-width:950px;font-size:14px;margin:24px 0}.note p{margin:4px 0}.reading-path{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0 36px}.reading-path a{border:1px solid #d6cec0;padding:8px 12px;border-radius:5px;font-size:12px;text-decoration:none;background:#fffdf8}.card-group{margin:35px 0 40px}.card-group>h2{font-size:13px;letter-spacing:.7px;font-weight:700;margin:0 0 15px;text-transform:uppercase;color:#697169}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:15px}.card{display:flex;flex-direction:column;padding:23px;border:1px solid var(--line);background:#fffdf8;border-radius:9px;text-decoration:none;color:var(--ink);transition:transform .16s,border-color .16s}.card:hover{transform:translateY(-3px);border-color:#bf8e71;color:var(--ink)}.file-kind{font-size:9px;font-weight:750;letter-spacing:1.5px;color:var(--accent)}.card h3{margin:12px 0 9px;font-size:20px;line-height:1.3;font-weight:650}.card p{font-size:13px;line-height:1.65;color:var(--muted);margin:0 0 20px}.card-foot{display:flex;justify-content:space-between;margin-top:auto;font-size:11px;color:var(--accent);font-weight:650}.doc-panel{max-width:990px;padding-bottom:55px;border-bottom:1px solid var(--line);margin-bottom:45px}.doc-toolbar{display:flex;justify-content:space-between;gap:12px;font-size:12px;border-bottom:1px solid var(--line);padding-bottom:19px;margin-bottom:27px}.article-meta{font-size:11px;color:var(--muted);letter-spacing:.2px}.doc-panel h2{font-family:Georgia,"Times New Roman",serif;font-size:36px;line-height:1.2;letter-spacing:-.8px;font-weight:400;margin:14px 0 28px}.doc-panel h3{font-size:21px;margin:35px 0 13px;line-height:1.4}.doc-panel h4{font-size:17px;margin:25px 0 8px}.doc-panel p,.doc-panel li{font-size:15px}.doc-panel ul,.doc-panel ol{padding-left:24px}.doc-panel li{margin:7px 0}.doc-panel li.indent{margin-left:20px}strong{font-weight:650}.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:5px;margin:20px 0 27px}table{border-collapse:collapse;min-width:560px;width:100%;font-size:12px;line-height:1.6}td,th{text-align:left;vertical-align:top;padding:13px 14px;border-bottom:1px solid var(--line)}th{background:#eee9df;font-weight:650}tr:last-child td{border-bottom:0}td code{white-space:normal}code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;background:#eee9df;border-radius:3px;padding:2px 4px;font-size:.85em;overflow-wrap:anywhere}pre{background:#222d34;color:#e9ece8;border-radius:0 0 6px 6px;padding:22px;overflow:auto;font-size:12px;line-height:1.65;margin:0 0 25px}pre code{background:none;color:inherit;padding:0;font-size:inherit;overflow-wrap:normal}.code-label{background:#dfe1dc;color:#4e5a5e;padding:6px 13px;font-size:10px;letter-spacing:.6px;border-radius:6px 6px 0 0;margin-top:23px}blockquote{border-left:3px solid #c7a482;margin:18px 0;padding:8px 18px;background:#f0ece4}figure{margin:24px 0}figure img{max-width:100%;height:auto}figcaption{font-size:12px;color:var(--muted)}.file-index{margin:35px 0;font-size:13px}.file-index summary{cursor:pointer;font-weight:650}.file-index li{margin:6px 0}.page-footer{font-size:12px;color:var(--muted);border-top:1px solid var(--line);margin-top:45px;padding-top:20px}.js-ready .doc-panel{display:none}.js-ready .doc-panel.selected{display:block}.js-ready #overview.hidden{display:none}[hidden]{display:none!important}a:focus-visible{outline:2px solid var(--accent);outline-offset:4px}.empty{color:var(--muted);font-size:14px;padding:20px 0}
@media(max-width:850px){.layout{grid-template-columns:215px minmax(0,1fr)}.sidebar{padding:22px 16px}main{padding:32px 24px}.cards{grid-template-columns:1fr}.hero h1{font-size:40px}}@media(max-width:620px){.layout{display:block}.sidebar{position:relative;height:auto;padding:18px 20px;border-right:0;border-bottom:1px solid var(--line)}.sidebar nav{max-height:235px;overflow:auto;margin-top:12px}.sidebar footer{display:none}.brand small{margin-bottom:5px}.search-label{margin-top:13px}main{padding:29px 20px}.hero h1{font-size:36px}.hero .intro{font-size:16px}.stats{gap:24px}.doc-panel h2{font-size:30px}}@media print{.sidebar,.doc-toolbar,.reading-path,#search{display:none}.layout{display:block}main{padding:0;max-width:none}.js-ready .doc-panel{display:block!important}#overview.hidden{display:block!important}.doc-panel{page-break-before:always;max-width:none}.card{break-inside:avoid}pre{white-space:pre-wrap;background:#eee;color:#111}.table-wrap{overflow:visible}table{min-width:0}a{color:#333}}
</style></head><body><div class="layout"><aside class="sidebar"><a class="brand" href="#overview"><small>ORANGE · ASSIGNMENT RESEARCH</small>Investigation<br>systems atlas</a><label class="search-label" for="search">Search every note</label><input id="search" type="search" placeholder="Try critic, retries, Uber…" autocomplete="off"><p class="search-status" id="search-status" aria-live="polite"></p><a class="home-link" href="#overview">↖ Research overview</a><nav aria-label="Research notes">${nav}</nav><footer>Researched 20 October 2026<br>Primary sources · Explicit unknowns<br>Full notes embedded for offline reading</footer></aside>
<main><section id="overview"><header class="hero"><div class="eyebrow">Research + design · Separate agent contracts</div><h1>How existing systems investigate production incidents.</h1><p class="intro">A source-backed field guide for the Orange assignment: what companies and research teams have already built, how their investigations work, and which ideas deserve a closer look.</p><div class="stats"><div class="stat"><b>${systemCount}</b><span>System studies</span></div><div class="stat"><b>${docs.length}</b><span>Markdown notes</span></div><div class="stat"><b>${activeAgentCount}</b><span>Current agents</span></div><div class="stat"><b>20 Oct ’26</b><span>Research date</span></div></div></header>
<div class="note"><p><strong>Start here.</strong> The assignment asks for collaborating investigators that compare explanations, challenge weak evidence, recover from failures, and can remain inconclusive. A useful reference needs more than an AI-generated incident summary.</p><p>Your Uber reference is <strong>Debug Assist</strong>. Its case study distinguishes the supplied talk and screenshots from online corroboration.</p></div><div class="reading-path"><a href="#doc-assignment-reading">01 · Read the assignment map</a><a href="#doc-systems--uber-debug-assist">02 · Explore Uber</a><a href="#doc-comparison">03 · Compare approaches</a><a href="#doc-evaluation-landscape">04 · Review evaluation</a><a href="#doc-next-discussion">05 · Prepare our discussion</a></div>
${cards}<p class="empty" id="no-matches" hidden>No notes match this search. Try a broader term.</p><details class="file-index"><summary>All research files and original material</summary><ul>${docs.map(d=>'<li><a href="#doc-'+d.id+'">'+escape(d.rel)+'</a> · <a href="'+escape(d.rel)+'">Markdown</a></li>').join('')}<li><a href="../Orange%20Invest%20Assignment%20FE%20%281%29.pdf">Original assignment PDF</a></li><li><a href="../uberassist/uberassist_youtube_transcript.txt">Supplied Uber talk transcript</a></li><li><a href="../uberassist/uberassist.png">Uber screenshot 1</a> · <a href="../uberassist/uberassist1.png">Uber screenshot 2</a></li><li><a href="build-overview.mjs">HTML build script</a></li><li><a href="index.html">This HTML overview</a></li></ul></details><div class="page-footer">Published descriptions, research prototypes, and inspectable code are labeled separately. Vendor metrics are attributed and are not directly comparable across systems. Architecture decisions are left for our next discussion.</div></section>${panels}</main></div>
<script>
const data=${searchData};
document.documentElement.classList.add('js-ready');
function route(){const hash=decodeURIComponent(location.hash||'#overview');const panel=document.getElementById(hash.slice(1));const selected=panel&&panel.classList.contains('doc-panel')?panel:null;document.getElementById('overview').classList.toggle('hidden',!!selected);document.querySelectorAll('.doc-panel').forEach(p=>p.classList.toggle('selected',p===selected));document.querySelectorAll('nav a').forEach(a=>{const active=selected&&a.dataset.doc===selected.dataset.id;a.classList.toggle('active',!!active);if(active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});document.title=selected?selected.querySelector('h2').textContent+' — Research Atlas':'Production Incident Investigation — Research Atlas';window.scrollTo(0,0)}
window.addEventListener('hashchange',route);route();
document.getElementById('search').addEventListener('input',e=>{const q=e.target.value.trim().toLowerCase();const words=q.split(/\\s+/).filter(Boolean);const matched=new Set(data.filter(d=>words.every(w=>d.text.includes(w))).map(d=>d.id));document.querySelectorAll('[data-doc]').forEach(el=>el.hidden=!matched.has(el.dataset.doc));document.querySelectorAll('.card-group').forEach(el=>el.hidden=!el.querySelector('.card:not([hidden])'));document.querySelectorAll('.nav-group').forEach(el=>el.hidden=!el.querySelector('a:not([hidden])'));document.getElementById('no-matches').hidden=matched.size>0;document.getElementById('search-status').textContent=q?matched.size+' of '+data.length+' notes match':''});
</script></body></html>`;
fs.writeFileSync(path.join(root, 'detailed-research.html'), html);
console.log(`Built research/detailed-research.html with ${docs.length} complete notes and ${systemCount} system studies (${Math.round(Buffer.byteLength(html) / 1024)} KiB).`);
