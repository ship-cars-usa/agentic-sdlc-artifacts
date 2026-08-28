#!/usr/bin/env python3
"""
gen_schema_browser.py — bundle the per-topic event-schemas/*.md files into a
single self-contained HTML browser at relations/event-schemas/browser.html.

Usage:
    python3 gen_schema_browser.py

The output is a single file:
  - All schema content embedded as JSON (no fetch() needed; works on file://).
  - Sidebar with filterable topic list, tier chips, and schema-source chips.
  - Main pane renders the selected topic's markdown via marked.js (CDN-loaded).
  - Color-coded badges per schema-source.

Stdlib only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

MAP_ROOT = Path.home() / "projects" / "codebase-map"
SCHEMAS_DIR = MAP_ROOT / "relations" / "event-schemas"
OUTPUT = SCHEMAS_DIR / "browser.html"

FRONTMATTER_RE = re.compile(r"^---\n(?P<fm>.*?)\n---\n(?P<body>.*)", re.DOTALL)
FIELD_RE = re.compile(r"^(?P<key>[\w-]+):\s*(?P<val>.*?)\s*$", re.MULTILINE)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm: dict[str, str] = {}
    for line in m.group("fm").splitlines():
        fm_m = FIELD_RE.match(line)
        if fm_m:
            fm[fm_m.group("key")] = fm_m.group("val")
    return fm, m.group("body")


def collect_schemas() -> list[dict]:
    """Read every event-schemas/*.md file and return a list of records."""
    if not SCHEMAS_DIR.is_dir():
        return []
    out: list[dict] = []
    for md in sorted(SCHEMAS_DIR.glob("*.md")):
        if md.name.startswith("_") or md.name == "browser.html":
            continue
        text = md.read_text(errors="replace")
        fm, _body = parse_frontmatter(text)
        topic = fm.get("topic", md.stem)
        out.append({
            "topic": topic,
            "tier": fm.get("tier", "fleet"),
            "schema_source": fm.get("schema-source", "none"),
            "producers": fm.get("producers", "[]"),
            "consumers": fm.get("consumers", "[]"),
            "canonical_dto": fm.get("canonical-dto", "~"),
            "status": fm.get("status", "stub"),
            "md": text,  # full file including frontmatter — renderer hides it
        })
    return out


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Event Schemas Browser</title>
<meta name="generator" content="gen_schema_browser.py">
<meta name="generated" content="__GENERATED__">
<style>
  :root {
    --bg: #0f1115;
    --panel: #161922;
    --panel-2: #1c2030;
    --border: #2a2f3e;
    --text: #e6e8ee;
    --muted: #8a92a6;
    --link: #7cc4ff;
    --accent: #ffb454;
    --carrier: #5cdb95;
    --fleet: #8a92a6;
    --src-lombok: #5cdb95;
    --src-record: #6cb3ff;
    --src-pydantic: #c08bff;
    --src-partial: #ffd166;
    --src-none: #687085;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; height: 100%; background: var(--bg); color: var(--text); font: 14px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  header {
    padding: 14px 20px;
    background: var(--panel);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: baseline; gap: 16px; flex-wrap: wrap;
  }
  header h1 { margin: 0; font-size: 16px; font-weight: 600; letter-spacing: 0.2px; }
  header .meta { color: var(--muted); font-size: 12px; }
  main { display: grid; grid-template-columns: 340px 1fr; height: calc(100vh - 51px); }
  aside.sidebar {
    background: var(--panel);
    border-right: 1px solid var(--border);
    overflow-y: auto;
    padding: 12px;
  }
  .filter-bar { margin-bottom: 12px; }
  .filter-bar input[type=search] {
    width: 100%;
    padding: 8px 10px;
    border: 1px solid var(--border);
    background: var(--panel-2);
    color: var(--text);
    border-radius: 6px;
    font: inherit;
  }
  .chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }
  .chips button {
    background: var(--panel-2);
    border: 1px solid var(--border);
    color: var(--muted);
    padding: 4px 10px;
    border-radius: 999px;
    cursor: pointer;
    font: inherit;
    font-size: 12px;
  }
  .chips button.active { background: var(--accent); color: #1a1a1a; border-color: var(--accent); font-weight: 600; }
  .chips .label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; align-self: center; margin-right: 4px; }
  ul.topics { list-style: none; padding: 0; margin: 0; }
  ul.topics li {
    padding: 8px 10px;
    border-radius: 6px;
    cursor: pointer;
    display: flex; align-items: center; gap: 6px;
    margin-bottom: 2px;
  }
  ul.topics li:hover { background: var(--panel-2); }
  ul.topics li.active { background: var(--panel-2); outline: 1px solid var(--link); }
  ul.topics li .name { flex: 1; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; }
  ul.topics li .badge {
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 3px;
    background: var(--src-none);
    color: #0f1115;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  ul.topics li .tier-dot {
    width: 6px; height: 6px; border-radius: 50%; background: var(--fleet);
    flex: 0 0 6px;
  }
  ul.topics li[data-tier="carrier"] .tier-dot { background: var(--carrier); }
  .badge-lombok-data { background: var(--src-lombok); }
  .badge-java-record { background: var(--src-record); }
  .badge-pydantic { background: var(--src-pydantic); }
  .badge-partial { background: var(--src-partial); }
  .badge-none { background: var(--src-none); color: #c7cbd5; }
  article.content {
    overflow-y: auto;
    padding: 24px 32px;
    max-width: 980px;
  }
  article.content.landing { color: var(--muted); }
  article.content h1, article.content h2, article.content h3 { color: var(--text); }
  article.content h1 { font-size: 22px; margin-top: 0; }
  article.content h2 { font-size: 17px; margin-top: 24px; border-bottom: 1px solid var(--border); padding-bottom: 6px; }
  article.content h3 { font-size: 14px; margin-top: 16px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
  article.content p { margin: 8px 0; }
  article.content a { color: var(--link); text-decoration: none; }
  article.content a:hover { text-decoration: underline; }
  article.content code {
    background: var(--panel-2);
    padding: 1px 5px;
    border-radius: 3px;
    font: 12px/1.4 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    color: #ffd9a8;
  }
  article.content pre {
    background: var(--panel-2);
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    border: 1px solid var(--border);
  }
  article.content pre code { background: none; color: var(--text); padding: 0; }
  article.content table {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    background: var(--panel);
  }
  article.content th, article.content td {
    border: 1px solid var(--border);
    padding: 6px 10px;
    text-align: left;
    font-size: 13px;
  }
  article.content th { background: var(--panel-2); color: var(--muted); font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }
  article.content blockquote { border-left: 3px solid var(--accent); margin: 12px 0; padding: 4px 12px; color: var(--muted); }
  article.content ul, article.content ol { padding-left: 22px; }
  article.content hr { border: none; border-top: 1px solid var(--border); margin: 20px 0; }
  .fm-card {
    background: var(--panel-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 18px;
    display: grid;
    grid-template-columns: max-content 1fr;
    gap: 4px 16px;
    font-size: 13px;
  }
  .fm-card .k { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; align-self: center; }
  .fm-card .v { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; word-break: break-all; }
  .empty { padding: 40px; text-align: center; color: var(--muted); }
  .footer-hint {
    font-size: 11px; color: var(--muted); margin-top: 24px; padding-top: 12px;
    border-top: 1px solid var(--border);
  }
</style>
</head>
<body>
<header>
  <h1>Event Schemas Browser</h1>
  <span class="meta">Tier 1.5 sidecar • <span id="count"></span> topics • generated __GENERATED__</span>
</header>
<main>
  <aside class="sidebar">
    <div class="filter-bar">
      <input type="search" id="q" placeholder="Filter topics…" autocomplete="off">
    </div>
    <div class="chips" id="tier-chips">
      <span class="label">Tier</span>
      <button data-tier="all" class="active">All</button>
      <button data-tier="carrier">Carrier</button>
      <button data-tier="fleet">Fleet</button>
    </div>
    <div class="chips" id="source-chips">
      <span class="label">Source</span>
      <button data-src="all" class="active">All</button>
      <button data-src="resolved">Resolved</button>
      <button data-src="partial">Partial</button>
      <button data-src="none">None</button>
    </div>
    <ul class="topics" id="topic-list"></ul>
  </aside>
  <article class="content landing" id="content">
    <div class="empty">
      <h2>Pick a topic to view its schema</h2>
      <p>Use the search box or filter chips on the left.</p>
      <p>Badge colors: <span class="badge badge-lombok-data">lombok-data</span>
         <span class="badge badge-java-record">java-record</span>
         <span class="badge badge-pydantic">pydantic</span>
         <span class="badge badge-partial">partial</span>
         <span class="badge badge-none">none</span></p>
    </div>
  </article>
</main>

<script>
const SCHEMAS = __SCHEMAS_JSON__;

function $(id) { return document.getElementById(id); }
let activeTier = 'all', activeSource = 'all', activeQuery = '';

function srcGroup(src) {
  if (src === 'lombok-data' || src === 'java-record' || src === 'pydantic') return 'resolved';
  return src;  // 'partial' | 'none'
}

function renderList() {
  const ul = $('topic-list');
  ul.innerHTML = '';
  const q = activeQuery.toLowerCase();
  let shown = 0;
  for (const s of SCHEMAS) {
    if (activeTier !== 'all' && s.tier !== activeTier) continue;
    if (activeSource !== 'all' && srcGroup(s.schema_source) !== activeSource) continue;
    if (q && !s.topic.toLowerCase().includes(q)) continue;
    const li = document.createElement('li');
    li.dataset.tier = s.tier;
    li.dataset.topic = s.topic;
    li.innerHTML = `
      <span class="tier-dot" title="${s.tier}"></span>
      <span class="name">${escapeHtml(s.topic)}</span>
      <span class="badge badge-${s.schema_source}">${s.schema_source}</span>
    `;
    li.addEventListener('click', () => selectTopic(s.topic));
    ul.appendChild(li);
    shown++;
  }
  if (shown === 0) {
    const li = document.createElement('li');
    li.innerHTML = '<span class="name" style="color:var(--muted)">No matches.</span>';
    ul.appendChild(li);
  }
}

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function stripFrontmatter(md) {
  if (!md.startsWith('---\n')) return { body: md, fm: {} };
  const end = md.indexOf('\n---\n', 4);
  if (end < 0) return { body: md, fm: {} };
  const fmText = md.slice(4, end);
  const body = md.slice(end + 5);
  const fm = {};
  for (const line of fmText.split('\n')) {
    const m = /^([\w-]+):\s*(.*?)\s*$/.exec(line);
    if (m) fm[m[1]] = m[2];
  }
  return { body, fm };
}

function renderFmCard(fm) {
  const keys = ['topic', 'tier', 'schema-source', 'canonical-dto', 'canonical-dto-file',
                'producers', 'consumers', 'shared-with-producer', 'status', 'last-generated-date'];
  let html = '<div class="fm-card">';
  for (const k of keys) {
    if (fm[k] === undefined) continue;
    let val = fm[k];
    if (k === 'schema-source') {
      val = '<span class="badge badge-' + escapeHtml(val) + '">' + escapeHtml(val) + '</span>';
    } else {
      val = escapeHtml(val);
    }
    html += '<div class="k">' + escapeHtml(k) + '</div><div class="v">' + val + '</div>';
  }
  html += '</div>';
  return html;
}

function selectTopic(topic) {
  const s = SCHEMAS.find(x => x.topic === topic);
  if (!s) return;
  const { body, fm } = stripFrontmatter(s.md);
  const content = $('content');
  content.classList.remove('landing');
  content.innerHTML = renderFmCard(fm) + marked.parse(body);
  for (const li of document.querySelectorAll('#topic-list li')) {
    li.classList.toggle('active', li.dataset.topic === topic);
  }
  // Scroll to top of content pane.
  content.scrollTop = 0;
  // Update URL hash for shareability.
  history.replaceState(null, '', '#' + encodeURIComponent(topic));
}

function wireChips(groupId, setter) {
  const group = $(groupId);
  group.addEventListener('click', e => {
    const btn = e.target.closest('button');
    if (!btn) return;
    for (const b of group.querySelectorAll('button')) b.classList.remove('active');
    btn.classList.add('active');
    setter(btn.dataset.tier || btn.dataset.src);
    renderList();
  });
}

document.addEventListener('DOMContentLoaded', () => {
  $('count').textContent = SCHEMAS.length;
  $('q').addEventListener('input', e => { activeQuery = e.target.value; renderList(); });
  wireChips('tier-chips', v => activeTier = v);
  wireChips('source-chips', v => activeSource = v);
  renderList();
  // Restore from hash if present.
  const hash = decodeURIComponent(location.hash.slice(1));
  if (hash) selectTopic(hash);
});
</script>
<script src="https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"></script>
</body>
</html>
"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true", help="Print HTML to stdout instead of writing")
    args = p.parse_args()

    schemas = collect_schemas()
    if not schemas:
        print(f"ERROR: no schema files at {SCHEMAS_DIR}", file=sys.stderr)
        return 2

    # Sort: carrier first, then fleet, alphabetical within each tier.
    schemas.sort(key=lambda s: (0 if s["tier"] == "carrier" else 1, s["topic"].lower()))

    generated = dt.date.today().isoformat()
    payload = json.dumps(schemas, ensure_ascii=False)
    out = HTML_TEMPLATE \
        .replace("__GENERATED__", generated) \
        .replace("__SCHEMAS_JSON__", payload)

    if args.dry_run:
        sys.stdout.write(out)
        print(f"\n[dry-run] {len(schemas)} schemas bundled.", file=sys.stderr)
        return 0

    OUTPUT.write_text(out)
    size_kb = OUTPUT.stat().st_size // 1024
    print(f"wrote {OUTPUT} ({len(schemas)} topics, {size_kb} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
