#!/usr/bin/env python3
"""
gen_entity_browser.py — bundle the cross-repo entity catalog into a single
self-contained HTML browser at domains/entities/browser.html.

Usage:
    python3 gen_entity_browser.py

Reads:
  - ~/projects/codebase-map/relations/entity-catalog.md          (master index)
  - ~/projects/codebase-map/relations/entity-catalog.raw.tsv     (per-class rows)
  - ~/projects/codebase-map/relations/entity_aliases.yaml        (alias map)
  - ~/projects/codebase-map/domains/entities/<Canonical>.md      (top-N pages)

Writes:
  - ~/projects/codebase-map/domains/entities/browser.html

The output is a single file:
  - All entity content embedded as JSON (no fetch() needed; works on file://).
  - Sidebar: search, top-25 toggle, domain filter chips.
  - Main pane renders the selected entity's markdown via marked.js (CDN).
  - For canonicals that don't have a dedicated page (below the top-N cutoff),
    a synthetic summary is generated from the master-index row.

Stdlib only. Mirrors gen_schema_browser.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

MAP_ROOT = Path.home() / "projects" / "codebase-map"
ENTITIES_DIR = MAP_ROOT / "domains" / "entities"
CATALOG_MD = MAP_ROOT / "relations" / "entity-catalog.md"
RAW_TSV = MAP_ROOT / "relations" / "entity-catalog.raw.tsv"
SHADOW_DIR = MAP_ROOT / "repos"
OUTPUT = ENTITIES_DIR / "browser.html"

FRONTMATTER_RE = re.compile(r"^---\n(?P<fm>.*?)\n---\n(?P<body>.*)", re.DOTALL)
FM_FIELD_RE = re.compile(r"^(?P<key>[\w-]+):\s*(?P<val>.*?)\s*$", re.MULTILINE)
CATALOG_ROW_RE = re.compile(
    r"^\|\s*(?P<rank>\d+)\s*\|\s*`(?P<canonical>[^`]+)`\s*\|"
    r"\s*(?P<aliases>[^|]*?)\s*\|\s*(?P<variants>\d+)\s*\|"
    r"\s*(?P<repos>\d+)\s*\|\s*(?P<domains>[^|]*?)\s*\|"
    r"\s*`(?P<owning>[^`]+)`\s*\|"
    r"\s*(?P<page>[^|]*?)\s*\|\s*$"
)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm: dict[str, str] = {}
    for line in m.group("fm").splitlines():
        fm_m = FM_FIELD_RE.match(line)
        if fm_m:
            fm[fm_m.group("key")] = fm_m.group("val")
    return fm, m.group("body")


def parse_catalog_rows(text: str) -> list[dict]:
    out: list[dict] = []
    for line in text.splitlines():
        m = CATALOG_ROW_RE.match(line)
        if not m:
            continue
        domains_raw = m.group("domains").strip()
        domains = []
        if domains_raw and domains_raw != "—":
            domains = [d.strip() for d in domains_raw.split(",") if d.strip()]
        aliases_raw = m.group("aliases").strip()
        aliases: list[str] = []
        if aliases_raw:
            for part in aliases_raw.split(","):
                p = part.strip()
                if p and not p.startswith("+"):
                    aliases.append(p)
        out.append({
            "rank": int(m.group("rank")),
            "canonical": m.group("canonical"),
            "aliases": aliases,
            "variants": int(m.group("variants")),
            "repos": int(m.group("repos")),
            "domains": domains,
            "owning": m.group("owning"),
            "has_page": "→" in m.group("page"),
        })
    return out


def load_repo_domains() -> dict[str, str]:
    """Map repo name → domain (read once from shadow frontmatter)."""
    out: dict[str, str] = {}
    for shadow in SHADOW_DIR.glob("*.md"):
        if shadow.name.startswith("_"):
            continue
        try:
            fm, _ = parse_frontmatter(shadow.read_text(errors="replace"))
            out[shadow.stem] = fm.get("domain", "unassigned")
        except Exception:
            continue
    return out


def parse_raw_rows() -> dict[str, list[dict]]:
    """canonical_name → [row]. We use this for the long-tail synthetic pages.
    The canonical is reconstructed using the same algorithm the cluster script
    applied. Cheapest approximation: walk the per-entity pages and the master
    catalog rows together. But since the raw TSV is keyed on `class_name`, the
    mapping `class_name -> canonical` is the inverse of what's stored in each
    entity page's `aliases` list.

    Returns rows grouped by the canonical they belong to.
    """
    if not RAW_TSV.exists():
        return {}
    rows_by_class: dict[str, list[dict]] = {}
    with RAW_TSV.open() as f:
        header = next(f).rstrip("\n").split("\t")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < len(header):
                parts += [""] * (len(header) - len(parts))
            row = dict(zip(header, parts))
            rows_by_class.setdefault(row["class_name"], []).append(row)
    return rows_by_class


def synth_page(c: dict, rows_by_class: dict[str, list[dict]]) -> str:
    """Build a minimal markdown body for an entity that has no dedicated page."""
    lines = [
        f"# {c['canonical']}",
        "",
        f"*Below the top-N cutoff — no dedicated page generated. "
        f"Summary derived from `relations/entity-catalog.md`.*",
        "",
        f"- **Rank:** {c['rank']}",
        f"- **Variants:** {c['variants']}",
        f"- **Repos:** {c['repos']}",
        f"- **Domains:** {', '.join(c['domains']) or '—'}",
        f"- **Owning service (alphabetically first occurrence):** `{c['owning']}`",
        "",
    ]
    if c["aliases"]:
        lines.append("## Aliases observed in source")
        lines.append("")
        for a in c["aliases"]:
            lines.append(f"- `{a}`")
        lines.append("")
    # Look up actual rows for each alias to give some grounding.
    matched_rows: list[dict] = []
    for a in c["aliases"]:
        matched_rows.extend(rows_by_class.get(a, []))
    if matched_rows:
        lines.append("## Per-repo occurrences")
        lines.append("")
        lines.append("| Repo | Class | Kind | Module | Field count |")
        lines.append("|---|---|---|---|---:|")
        # Cap at 40 to keep the bundle small.
        for r in matched_rows[:40]:
            lines.append(
                f"| `{r['repo']}` | `{r['class_name']}` | {r['kind']} | "
                f"`{r['module']}` | {r['field_count']} |"
            )
        lines.append("")
    return "\n".join(lines)


def collect_entities() -> list[dict]:
    if not CATALOG_MD.exists():
        return []
    catalog_text = CATALOG_MD.read_text(errors="replace")
    rows = parse_catalog_rows(catalog_text)
    rows_by_class = parse_raw_rows()
    repo_domains = load_repo_domains()

    out: list[dict] = []
    for r in rows:
        page_path = ENTITIES_DIR / f"{r['canonical']}.md"
        has_full_page = page_path.exists()
        if has_full_page:
            md = page_path.read_text(errors="replace")
        else:
            md = synth_page(r, rows_by_class)
        # Drop the rank into the record so the JS can sort/filter.
        out.append({
            "rank": r["rank"],
            "canonical": r["canonical"],
            "aliases": r["aliases"],
            "variants": r["variants"],
            "repos": r["repos"],
            "domains": r["domains"],
            "owning": r["owning"],
            "has_page": has_full_page,
            "md": md,
        })
    return out


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Entity Catalog Browser</title>
<meta name="generator" content="gen_entity_browser.py">
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
    --top: #5cdb95;
    --tail: #687085;
    --d-listings-trade: #5cdb95;
    --d-operations: #6cb3ff;
    --d-pricing-billing: #ffb454;
    --d-integrations: #c08bff;
    --d-identity: #ff7eb6;
    --d-communication: #ffd166;
    --d-platform: #7fd1c9;
    --d-analytics: #aab4ff;
    --d-infrastructure: #687085;
    --d-default: #8a92a6;
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
  main { display: grid; grid-template-columns: 380px 1fr; height: calc(100vh - 51px); }
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
  ul.entities { list-style: none; padding: 0; margin: 0; }
  ul.entities li {
    padding: 8px 10px;
    border-radius: 6px;
    cursor: pointer;
    display: grid;
    grid-template-columns: max-content 1fr max-content;
    gap: 6px;
    align-items: center;
    margin-bottom: 2px;
  }
  ul.entities li:hover { background: var(--panel-2); }
  ul.entities li.active { background: var(--panel-2); outline: 1px solid var(--link); }
  ul.entities li .rank {
    font-size: 11px;
    color: var(--muted);
    font-family: ui-monospace, monospace;
    min-width: 28px;
    text-align: right;
  }
  ul.entities li .name { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 13px; }
  ul.entities li .counts {
    font-size: 10px;
    color: var(--muted);
    text-align: right;
    white-space: nowrap;
  }
  ul.entities li .domain-row {
    grid-column: 1 / -1;
    display: flex; flex-wrap: wrap; gap: 3px;
    margin-top: 2px;
  }
  ul.entities li .dom {
    font-size: 9px;
    padding: 1px 6px;
    border-radius: 3px;
    background: var(--d-default);
    color: #0f1115;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
  }
  ul.entities li .dom[data-d="listings-trade"] { background: var(--d-listings-trade); }
  ul.entities li .dom[data-d="operations"] { background: var(--d-operations); }
  ul.entities li .dom[data-d="pricing-billing"] { background: var(--d-pricing-billing); }
  ul.entities li .dom[data-d="integrations"] { background: var(--d-integrations); }
  ul.entities li .dom[data-d="identity"] { background: var(--d-identity); }
  ul.entities li .dom[data-d="communication"] { background: var(--d-communication); }
  ul.entities li .dom[data-d="platform"] { background: var(--d-platform); }
  ul.entities li .dom[data-d="analytics"] { background: var(--d-analytics); }
  ul.entities li .dom[data-d="infrastructure"] { background: var(--d-infrastructure); color: #c7cbd5; }
  ul.entities li.top-25 .name { color: var(--top); font-weight: 600; }
  ul.entities li.tail .name { color: var(--text); }
  ul.entities li.tail .rank { color: var(--tail); }
  article.content {
    overflow-y: auto;
    padding: 24px 32px;
    max-width: 1080px;
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
    font-size: 12px;
  }
  article.content th, article.content td {
    border: 1px solid var(--border);
    padding: 5px 8px;
    text-align: left;
    vertical-align: top;
  }
  article.content th { background: var(--panel-2); color: var(--muted); font-weight: 600; text-transform: uppercase; font-size: 10px; letter-spacing: 0.5px; }
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
</style>
</head>
<body>
<header>
  <h1>Entity Catalog Browser</h1>
  <span class="meta">Cross-repo business-entity index • <span id="count"></span> canonicals • generated __GENERATED__</span>
</header>
<main>
  <aside class="sidebar">
    <div class="filter-bar">
      <input type="search" id="q" placeholder="Filter — name, alias, repo…" autocomplete="off">
    </div>
    <div class="chips" id="scope-chips">
      <span class="label">Scope</span>
      <button data-scope="all" class="active">All</button>
      <button data-scope="top">Top 25</button>
      <button data-scope="tail">Long tail</button>
    </div>
    <div class="chips" id="domain-chips">
      <span class="label">Domain</span>
      <button data-domain="all" class="active">Any</button>
    </div>
    <ul class="entities" id="entity-list"></ul>
  </aside>
  <article class="content landing" id="content">
    <div class="empty">
      <h2>Pick a canonical entity to view its catalog page</h2>
      <p>Top-25 entities have full pages with variants, field-union/intersection, REST surface, repository operations, and Pub/Sub topics. Long-tail entities show a one-glance summary.</p>
    </div>
  </article>
</main>

<script>
const ENTITIES = __ENTITIES_JSON__;
const TOP_N = __TOP_N__;
const ALL_DOMAINS = __DOMAINS_JSON__;

function $(id) { return document.getElementById(id); }
let activeScope = 'all', activeDomain = 'all', activeQuery = '';

function matches(e) {
  if (activeScope === 'top' && e.rank > TOP_N) return false;
  if (activeScope === 'tail' && e.rank <= TOP_N) return false;
  if (activeDomain !== 'all' && !e.domains.includes(activeDomain)) return false;
  if (activeQuery) {
    const q = activeQuery.toLowerCase();
    if (!e.canonical.toLowerCase().includes(q)
        && !e.aliases.some(a => a.toLowerCase().includes(q))
        && !e.owning.toLowerCase().includes(q)) {
      return false;
    }
  }
  return true;
}

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
                  .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function renderList() {
  const ul = $('entity-list');
  ul.innerHTML = '';
  let shown = 0;
  for (const e of ENTITIES) {
    if (!matches(e)) continue;
    const li = document.createElement('li');
    li.dataset.canonical = e.canonical;
    li.classList.add(e.rank <= TOP_N ? 'top-25' : 'tail');
    const domBadges = e.domains.map(d =>
      `<span class="dom" data-d="${escapeHtml(d)}">${escapeHtml(d)}</span>`
    ).join('');
    li.innerHTML = `
      <span class="rank">#${e.rank}</span>
      <span class="name">${escapeHtml(e.canonical)}</span>
      <span class="counts">${e.variants}v · ${e.repos}r</span>
      <span class="domain-row">${domBadges}</span>
    `;
    li.addEventListener('click', () => selectEntity(e.canonical));
    ul.appendChild(li);
    shown++;
  }
  if (shown === 0) {
    const li = document.createElement('li');
    li.innerHTML = '<span class="name" style="color:var(--muted)">No matches.</span>';
    ul.appendChild(li);
  }
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

function renderFmCard(e, fm) {
  const keys = [
    ['entity', e.canonical],
    ['rank', '#' + e.rank + (e.rank <= TOP_N ? ' (top ' + TOP_N + ')' : ' (long tail)')],
    ['variants', e.variants],
    ['repos', e.repos],
    ['domains', e.domains.join(', ') || '—'],
    ['owning-service', e.owning],
    ['aliases', e.aliases.join(', ') || '—'],
    ['last-extracted-date', fm['last-extracted-date'] || '—'],
  ];
  let html = '<div class="fm-card">';
  for (const [k, v] of keys) {
    html += '<div class="k">' + escapeHtml(k) + '</div><div class="v">' + escapeHtml(v) + '</div>';
  }
  html += '</div>';
  return html;
}

function selectEntity(canonical) {
  const e = ENTITIES.find(x => x.canonical === canonical);
  if (!e) return;
  const { body, fm } = stripFrontmatter(e.md);
  const content = $('content');
  content.classList.remove('landing');
  content.innerHTML = renderFmCard(e, fm) + marked.parse(body);
  for (const li of document.querySelectorAll('#entity-list li')) {
    li.classList.toggle('active', li.dataset.canonical === canonical);
  }
  content.scrollTop = 0;
  history.replaceState(null, '', '#' + encodeURIComponent(canonical));
}

function wireChips(groupId, setter) {
  const group = $(groupId);
  group.addEventListener('click', e => {
    const btn = e.target.closest('button');
    if (!btn) return;
    for (const b of group.querySelectorAll('button')) b.classList.remove('active');
    btn.classList.add('active');
    setter(btn.dataset.scope || btn.dataset.domain);
    renderList();
  });
}

function buildDomainChips() {
  const group = $('domain-chips');
  for (const d of ALL_DOMAINS) {
    const btn = document.createElement('button');
    btn.dataset.domain = d;
    btn.textContent = d;
    group.appendChild(btn);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  $('count').textContent = ENTITIES.length;
  $('q').addEventListener('input', e => { activeQuery = e.target.value; renderList(); });
  buildDomainChips();
  wireChips('scope-chips', v => activeScope = v);
  wireChips('domain-chips', v => activeDomain = v);
  renderList();
  const hash = decodeURIComponent(location.hash.slice(1));
  if (hash) selectEntity(hash);
});
</script>
<script src="https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"></script>
</body>
</html>
"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true", help="Print HTML to stdout instead of writing")
    p.add_argument("--top", type=int, default=25, help="Number of top-N entities to badge as 'top' (default 25)")
    args = p.parse_args()

    entities = collect_entities()
    if not entities:
        print(f"ERROR: no entities found. Has cluster_entities.py been run?", file=sys.stderr)
        return 2

    # Already sorted by rank from the master index.
    # Collect distinct domains for the chip row.
    domains_seen: list[str] = []
    seen: set[str] = set()
    for e in entities:
        for d in e["domains"]:
            if d not in seen:
                seen.add(d)
                domains_seen.append(d)
    domains_seen.sort()

    generated = dt.date.today().isoformat()
    payload = json.dumps(entities, ensure_ascii=False)
    out = (HTML_TEMPLATE
           .replace("__GENERATED__", generated)
           .replace("__TOP_N__", str(args.top))
           .replace("__ENTITIES_JSON__", payload)
           .replace("__DOMAINS_JSON__", json.dumps(domains_seen)))

    if args.dry_run:
        sys.stdout.write(out)
        print(f"\n[dry-run] {len(entities)} entities bundled.", file=sys.stderr)
        return 0

    ENTITIES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(out)
    size_kb = OUTPUT.stat().st_size // 1024
    print(f"wrote {OUTPUT} ({len(entities)} canonicals, {size_kb} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
