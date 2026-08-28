#!/usr/bin/env python3
"""
gen_entity_drift.py — render a field × variant heatmap that reveals the
shape drift of each canonical entity across the services that declare it.

Usage:
    python3 gen_entity_drift.py [--top N]

Reads:
  - ~/projects/codebase-map/relations/entity-catalog.md
  - ~/projects/codebase-map/relations/entity-catalog.raw.tsv
  - ~/projects/codebase-map/relations/entity_aliases.yaml
  - ~/projects/codebase-map/repos/<repo>.md     (frontmatter domain:)

Writes:
  - ~/projects/codebase-map/domains/entities/drift.html

Per top-N canonical:
  - rows  = union of field names across variants, sorted by presence-frequency
  - cols  = variant classes (one per (repo, class) row in the raw TSV)
  - cells = empty (absent) | majority-type (cyan) | minority-type (orange, animated)

The visualization makes it visually obvious which fields are "core" to the
business object versus which are repo-local additions, and which field types
genuinely drift between services (often the most important signal: e.g.
`weight: Integer` here vs `weight: long` there).

Stdlib only. D3 v7 from CDN.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import re
import sys
from pathlib import Path

MAP_ROOT = Path.home() / "projects" / "codebase-map"
ENTITIES_DIR = MAP_ROOT / "domains" / "entities"
CATALOG_MD = MAP_ROOT / "relations" / "entity-catalog.md"
RAW_TSV = MAP_ROOT / "relations" / "entity-catalog.raw.tsv"
ALIAS_YAML = MAP_ROOT / "relations" / "entity_aliases.yaml"
SHADOW_DIR = MAP_ROOT / "repos"
OUTPUT = ENTITIES_DIR / "drift.html"

DEFAULT_TOP_N = 25


# --- shared idioms (mirrors gen_entity_graph.py / cluster_entities.py) ------

SUFFIX_STRIP_RE = re.compile(
    r"(?:DbEntity|Entity|PubSubDto|EventDto|ReadDto|WriteDto|Response|Request"
    r"|Dto|Model|Embedded|Embeddable|Record|Bean)$"
)
VERSION_PREFIX_RE = re.compile(r"^(?:V\d+)")
QUALIFIER_PREFIX_RE = re.compile(r"^(?:Internal|External|Public|Admin)")
SERVICE_PREFIXES = (
    "Inventory", "Loadboard", "Posting", "Payment", "Notification",
    "User", "Chat", "Driveaway", "Trip", "Tracking", "Recommender",
    "AutoIms", "AutoIMS", "Carrier",
)
FRONTMATTER_RE = re.compile(r"^---\n(?P<fm>.*?)\n---\n(?P<body>.*)", re.DOTALL)
FM_FIELD_RE = re.compile(r"^(?P<key>[\w-]+):\s*(?P<val>.*?)\s*$", re.MULTILINE)
CATALOG_ROW_RE = re.compile(
    r"^\|\s*(?P<rank>\d+)\s*\|\s*`(?P<canonical>[^`]+)`\s*\|"
    r"\s*(?P<aliases>[^|]*?)\s*\|\s*(?P<variants>\d+)\s*\|"
    r"\s*(?P<repos>\d+)\s*\|\s*(?P<domains>[^|]*?)\s*\|"
    r"\s*`(?P<owning>[^`]+)`\s*\|"
    r"\s*(?P<page>[^|]*?)\s*\|\s*$"
)


def parse_alias_yaml(text):
    canonical, splits = {}, []
    section, cur = None, None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("canonical:"):
            section = "canonical"; continue
        if line.startswith("splits:"):
            section = "splits"; continue
        if section == "canonical":
            m = re.match(r"^\s+([\w]+):\s*\[(.*)\]\s*$", line)
            if m:
                canonical[m.group(1).strip()] = [
                    n.strip() for n in m.group(2).split(",") if n.strip()
                ]
            continue
        if section == "splits":
            m = re.match(r"^\s*-\s+canonical:\s*(\w+)\s*$", line)
            if m:
                if cur: splits.append(cur)
                cur = {"canonical": m.group(1), "repos": [], "names": []}
                continue
            if cur is None: continue
            m = re.match(r"^\s+repos:\s*\[(.*)\]\s*$", line)
            if m:
                cur["repos"] = [n.strip() for n in m.group(1).split(",") if n.strip()]
                continue
            m = re.match(r"^\s+names:\s*\[(.*)\]\s*$", line)
            if m:
                cur["names"] = [n.strip() for n in m.group(1).split(",") if n.strip()]
                continue
    if cur: splits.append(cur)
    return canonical, splits


def base_strip(name):
    prev = ""
    while prev != name:
        prev = name
        name = SUFFIX_STRIP_RE.sub("", name)
        name = VERSION_PREFIX_RE.sub("", name)
        name = QUALIFIER_PREFIX_RE.sub("", name)
    return name


def strip_prefix_if_matches(name, repo):
    for p in SERVICE_PREFIXES:
        if name.startswith(p) and len(name) > len(p) and name[len(p)].isupper():
            if p.lower() in repo.lower():
                return name[len(p):]
    return name


def build_canonicalizer(canonical_map, splits):
    name_to_canonical = {}
    for cano, names in canonical_map.items():
        for n in names:
            name_to_canonical[n] = cano
    split_map = {}
    for s in splits:
        for r in s["repos"]:
            for n in s["names"]:
                split_map[(r, n)] = s["canonical"]
    def to_canonical(class_name, repo=""):
        if not class_name: return None
        if (repo, class_name) in split_map:
            return split_map[(repo, class_name)]
        stripped = base_strip(class_name)
        if (repo, stripped) in split_map:
            return split_map[(repo, stripped)]
        stripped = strip_prefix_if_matches(stripped, repo)
        if stripped in name_to_canonical:
            return name_to_canonical[stripped]
        if class_name in name_to_canonical:
            return name_to_canonical[class_name]
        return stripped
    return to_canonical


def parse_frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    if not m: return {}, text
    fm = {}
    for line in m.group("fm").splitlines():
        fm_m = FM_FIELD_RE.match(line)
        if fm_m: fm[fm_m.group("key")] = fm_m.group("val")
    return fm, m.group("body")


def load_repo_domains():
    out = {}
    for shadow in SHADOW_DIR.glob("*.md"):
        if shadow.name.startswith("_"): continue
        try:
            fm, _ = parse_frontmatter(shadow.read_text(errors="replace"))
            out[shadow.stem] = fm.get("domain", "unassigned")
        except Exception:
            continue
    return out


def parse_catalog_rows(text):
    out = []
    for line in text.splitlines():
        m = CATALOG_ROW_RE.match(line)
        if not m: continue
        domains_raw = m.group("domains").strip()
        domains = []
        if domains_raw and domains_raw != "—":
            domains = [d.strip() for d in domains_raw.split(",") if d.strip()]
        out.append({
            "rank": int(m.group("rank")),
            "canonical": m.group("canonical"),
            "variants": int(m.group("variants")),
            "repos": int(m.group("repos")),
            "domains": domains,
            "owning": m.group("owning"),
        })
    return out


def parse_raw_rows():
    rows = []
    if not RAW_TSV.exists():
        return rows
    with RAW_TSV.open() as f:
        header = next(f).rstrip("\n").split("\t")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < len(header):
                parts += [""] * (len(header) - len(parts))
            row = dict(zip(header, parts))
            fields = []
            seen_in_row = set()
            for chunk in (row.get("fields") or "").split(";"):
                if ":" not in chunk: continue
                n, _, t = chunk.partition(":")
                n = n.strip()
                t = t.strip()
                # Dedupe within a single class (extractor sometimes emits
                # duplicates for shadowed fields / repeated lines).
                if n in seen_in_row: continue
                seen_in_row.add(n)
                fields.append((n, t))
            row["_fields"] = fields
            rows.append(row)
    return rows


def build_drift_payload(top_n: int) -> tuple[list[dict], dict]:
    rows = parse_raw_rows()
    catalog_text = CATALOG_MD.read_text(errors="replace")
    catalog_rows = parse_catalog_rows(catalog_text)
    canonical_meta = {r["canonical"]: r for r in catalog_rows}
    repo_domains = load_repo_domains()

    canonical_map, splits = parse_alias_yaml(ALIAS_YAML.read_text())
    to_canonical = build_canonicalizer(canonical_map, splits)

    # Group rows by canonical.
    by_canonical: dict[str, list[dict]] = collections.defaultdict(list)
    for r in rows:
        cano = to_canonical(r["class_name"], r["repo"])
        if not cano: continue
        by_canonical[cano].append(r)

    # Sort canonicals by rank (top-N from the master index drives the picker).
    ranked = sorted(by_canonical.keys(),
                    key=lambda c: canonical_meta.get(c, {}).get("rank", 9999))
    selected = ranked[:top_n]

    out: list[dict] = []
    for cano in selected:
        variants_raw = by_canonical[cano]
        if len(variants_raw) < 2:
            # Drift needs at least 2 variants. Skip singletons even when they
            # cracked top-N by rank.
            continue
        # Sort variants for a stable, repo-grouped layout: (repo, class_name, module)
        variants_raw.sort(key=lambda r: (r["repo"], r["class_name"], r["module"]))

        variants_meta = []
        for v in variants_raw:
            variants_meta.append({
                "repo": v["repo"],
                "class_name": v["class_name"],
                "kind": v["kind"],
                "module": v["module"],
                "file_path": v["file_path"],
                "field_count": len(v["_fields"]),
                "repo_domain": repo_domains.get(v["repo"], "unassigned"),
            })

        # Build per-field stats: presence count + type counts + majority type.
        field_to_types: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
        field_to_variant_idx: dict[str, dict[int, str]] = collections.defaultdict(dict)
        for vi, v in enumerate(variants_raw):
            for fname, ftype in v["_fields"]:
                field_to_types[fname][ftype] += 1
                field_to_variant_idx[fname][vi] = ftype

        n_var = len(variants_raw)
        fields_out: list[dict] = []
        for fname, types in field_to_types.items():
            presence = sum(types.values())
            majority_type, _ = types.most_common(1)[0]
            # Drift = field appears with >1 distinct type
            type_count = len(types)
            drift = type_count > 1
            fields_out.append({
                "name": fname,
                "presence": presence,
                "presence_pct": round(100 * presence / n_var, 1),
                "majority_type": majority_type,
                "type_count": type_count,
                "drift": drift,
                "types": dict(types),
                # Sparse map: variant_idx -> type observed in that variant
                "by_variant": field_to_variant_idx[fname],
            })

        # Sort fields: presence desc, name asc.
        fields_out.sort(key=lambda f: (-f["presence"], f["name"]))

        # Aggregate column stats (per-variant drift counts).
        col_drift_count = [0] * n_var
        for f in fields_out:
            if not f["drift"]: continue
            for vi, t in f["by_variant"].items():
                if t != f["majority_type"]:
                    col_drift_count[vi] += 1

        for vi, m in enumerate(variants_meta):
            m["drift_minority_count"] = col_drift_count[vi]

        meta = canonical_meta.get(cano, {})
        # Shared-field threshold: present in >=60% of variants. 80% is too
        # strict here because many "variants" are thin DTOs that inherit
        # most of their fields from a base class and therefore declare 0
        # own-fields in the raw TSV (`field_count == 0`). 60% gives a
        # signal that surfaces fields actually shared by the majority of
        # *meaningful* variants without over-counting empty shells.
        core_threshold = max(2, int(n_var * 0.6))
        core_count = sum(1 for f in fields_out if f["presence"] >= core_threshold)
        drift_field_count = sum(1 for f in fields_out if f["drift"])

        out.append({
            "canonical": cano,
            "rank": meta.get("rank", 9999),
            "domains": meta.get("domains", []),
            "owning": meta.get("owning", "—"),
            "n_variants": n_var,
            "n_fields": len(fields_out),
            "n_core_fields": core_count,
            "n_drift_fields": drift_field_count,
            "core_threshold": core_threshold,
            "variants": variants_meta,
            "fields": fields_out,
        })

    summary = {
        "total_entities": len(out),
        "generated": dt.date.today().isoformat(),
    }
    return out, summary


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Entity Field Drift</title>
<meta name="generator" content="gen_entity_drift.py">
<meta name="generated" content="__GENERATED__">
<style>
  :root {
    --bg: #0f1115;
    --panel: #161922;
    --panel-2: #1c2030;
    --panel-3: #232838;
    --border: #2a2f3e;
    --text: #e6e8ee;
    --muted: #8a92a6;
    --link: #7cc4ff;
    --accent: #ffb454;

    --cell-empty:    rgba(106, 114, 138, 0.08);
    --cell-empty-bd: rgba(106, 114, 138, 0.18);
    --cell-present:  #6cb3ff;   /* same-type-as-majority */
    --cell-drift:    #ff9347;   /* differs from majority — the interesting signal */
    --cell-only:     #c08bff;   /* only one variant has this field */

    --kind-jpa: #5cdb95;
    --kind-dto: #6cb3ff;
    --kind-embedded: #c08bff;
    --kind-other: #687085;

    --d-listings-trade: #5cdb95;
    --d-operations: #6cb3ff;
    --d-pricing-billing: #ffb454;
    --d-integrations: #c08bff;
    --d-identity: #ff7eb6;
    --d-communication: #ffd166;
    --d-platform: #7fd1c9;
    --d-analytics: #aab4ff;
    --d-infrastructure: #687085;
    --d-unassigned: #8a92a6;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; height: 100%; background: var(--bg); color: var(--text); font: 13px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  header {
    padding: 12px 20px;
    background: var(--panel);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
    height: 50px;
    position: sticky; top: 0; z-index: 5;
  }
  header h1 { margin: 0; font-size: 15px; font-weight: 600; }
  header .meta { color: var(--muted); font-size: 11px; }
  header .controls { display: flex; gap: 10px; align-items: center; margin-left: auto; }
  header label { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }
  header select, header input[type=search] {
    padding: 5px 10px;
    border: 1px solid var(--border);
    background: var(--panel-2);
    color: var(--text);
    border-radius: 6px;
    font: inherit;
    font-size: 12px;
  }
  header select { padding-right: 24px; cursor: pointer; }
  header .toggle {
    display: flex; align-items: center; gap: 6px;
    font-size: 11px; color: var(--muted);
    cursor: pointer; user-select: none;
  }
  header .toggle input { cursor: pointer; }

  main { padding: 16px 20px; }
  .summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 10px;
    margin-bottom: 14px;
  }
  .stat {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
  }
  .stat .k { color: var(--muted); font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
  .stat .v { font-family: ui-monospace, monospace; font-size: 18px; margin-top: 3px; }
  .stat .v.warn { color: var(--cell-drift); }
  .stat .v.good { color: var(--kind-jpa); }

  .legend {
    display: flex; flex-wrap: wrap; gap: 16px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 14px;
    font-size: 11px;
    color: var(--muted);
  }
  .legend-row { display: flex; align-items: center; gap: 6px; }
  .legend-swatch { width: 14px; height: 14px; border-radius: 3px; }

  .heatmap-wrap {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: auto;
    position: relative;
    max-height: calc(100vh - 280px);
  }
  #heatmap { display: block; }

  .field-row.dim { opacity: 0.18; }
  .col-hi rect.col-bg { fill: rgba(255, 180, 84, 0.07); }

  .tooltip {
    position: fixed;
    pointer-events: none;
    background: rgba(15, 17, 21, 0.96);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
    line-height: 1.4;
    color: var(--text);
    max-width: 360px;
    z-index: 100;
    box-shadow: 0 6px 20px rgba(0,0,0,0.45);
    opacity: 0;
    transition: opacity 100ms;
  }
  .tooltip.visible { opacity: 1; }
  .tooltip .tip-title { font-weight: 600; margin-bottom: 4px; }
  .tooltip .tip-mono { font-family: ui-monospace, monospace; font-size: 11px; }
  .tooltip .tip-section { color: var(--muted); font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 6px; }
  .tooltip .type-row { display: flex; justify-content: space-between; gap: 12px; font-family: ui-monospace, monospace; font-size: 11px; }
  .tooltip .type-row.majority { color: var(--cell-present); }
  .tooltip .type-row.minority { color: var(--cell-drift); }

  .kind-badge {
    display: inline-block; font-size: 9px; padding: 1px 5px; border-radius: 3px;
    color: #0f1115; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
  }
  .kind-badge.jpa      { background: var(--kind-jpa); }
  .kind-badge.dto      { background: var(--kind-dto); }
  .kind-badge.embedded { background: var(--kind-embedded); }
  .kind-badge.other    { background: var(--kind-other); color: #c7cbd5; }

  .dom-badge {
    display: inline-block; font-size: 9px; padding: 1px 5px; border-radius: 3px;
    color: #0f1115; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
    margin-right: 3px;
  }
  .dom-badge[data-d="listings-trade"]  { background: var(--d-listings-trade); }
  .dom-badge[data-d="operations"]      { background: var(--d-operations); }
  .dom-badge[data-d="pricing-billing"] { background: var(--d-pricing-billing); }
  .dom-badge[data-d="integrations"]    { background: var(--d-integrations); }
  .dom-badge[data-d="identity"]        { background: var(--d-identity); }
  .dom-badge[data-d="communication"]   { background: var(--d-communication); }
  .dom-badge[data-d="platform"]        { background: var(--d-platform); }
  .dom-badge[data-d="analytics"]       { background: var(--d-analytics); }
  .dom-badge[data-d="infrastructure"]  { background: var(--d-infrastructure); color: #c7cbd5; }
  .dom-badge[data-d="unassigned"]      { background: var(--d-unassigned); color: #c7cbd5; }

  /* Animation for drift cells — gentle, doesn't strobe. */
  @keyframes drift-pulse {
    0%, 100% { opacity: 0.92; }
    50%      { opacity: 0.62; }
  }
  rect.drift-cell {
    animation: drift-pulse 2.4s ease-in-out infinite;
  }
  .empty-state {
    text-align: center;
    padding: 60px 20px;
    color: var(--muted);
  }
</style>
</head>
<body>
<header>
  <h1>Entity Field Drift</h1>
  <span class="meta">cross-service field heatmap · generated __GENERATED__</span>
  <div class="controls">
    <label for="entity-picker">Entity</label>
    <select id="entity-picker"></select>
    <label for="sort-picker">Sort fields</label>
    <select id="sort-picker">
      <option value="presence">By presence ↓</option>
      <option value="name">By name A→Z</option>
      <option value="drift-first">Drift first</option>
    </select>
    <label class="toggle">
      <input type="checkbox" id="drift-only"> drift only
    </label>
    <input type="search" id="q" placeholder="Filter fields…" autocomplete="off" style="width: 160px;">
  </div>
</header>
<main>
  <div id="banner"></div>
  <div class="summary" id="summary"></div>
  <div class="legend">
    <div class="legend-row"><span class="legend-swatch" style="background: var(--cell-present);"></span>field present, type matches majority</div>
    <div class="legend-row"><span class="legend-swatch" style="background: var(--cell-drift);"></span>field present, type differs from majority (drift)</div>
    <div class="legend-row"><span class="legend-swatch" style="background: var(--cell-only);"></span>field present in only one variant</div>
    <div class="legend-row"><span class="legend-swatch" style="background: var(--cell-empty); border: 1px solid var(--cell-empty-bd);"></span>field absent in this variant</div>
    <div class="legend-row"><span class="kind-badge jpa">jpa</span> <span class="kind-badge dto">dto</span> <span class="kind-badge embedded">embedded</span> <span class="kind-badge other">other</span></div>
  </div>
  <div class="heatmap-wrap">
    <svg id="heatmap"></svg>
  </div>
</main>
<div class="tooltip" id="tooltip"></div>

<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<script>
const ENTITIES = __ENTITIES_JSON__;
const $ = id => document.getElementById(id);

let currentEntityId = ENTITIES[0]?.canonical || null;
let sortMode = 'presence';
let driftOnly = false;
let nameFilter = '';

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
                  .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function buildPicker() {
  const sel = $('entity-picker');
  for (const e of ENTITIES) {
    const opt = document.createElement('option');
    opt.value = e.canonical;
    opt.textContent = `${e.canonical}  (${e.n_variants}v · ${e.n_drift_fields} drift fields)`;
    sel.appendChild(opt);
  }
  sel.addEventListener('change', e => {
    currentEntityId = e.target.value;
    render();
  });
}

function renderSummary(ent) {
  const domBadges = (ent.domains || []).map(d =>
    `<span class="dom-badge" data-d="${escapeHtml(d)}">${escapeHtml(d)}</span>`).join('');
  $('banner').innerHTML = `
    <h2 style="margin: 0 0 4px; font-size: 18px;">${escapeHtml(ent.canonical)}</h2>
    <div style="color: var(--muted); font-size: 11px; margin-bottom: 12px;">
      rank #${ent.rank} · owning service: <code>${escapeHtml(ent.owning)}</code> · ${domBadges || '—'}
    </div>
  `;
  const driftPct = ent.n_fields ? Math.round(100 * ent.n_drift_fields / ent.n_fields) : 0;
  $('summary').innerHTML = `
    <div class="stat">
      <div class="k">Variants</div>
      <div class="v">${ent.n_variants}</div>
    </div>
    <div class="stat">
      <div class="k">Union of fields</div>
      <div class="v">${ent.n_fields}</div>
    </div>
    <div class="stat">
      <div class="k">Shared fields (≥${ent.core_threshold}/${ent.n_variants})</div>
      <div class="v good">${ent.n_core_fields}</div>
    </div>
    <div class="stat">
      <div class="k">Type-drift fields</div>
      <div class="v ${ent.n_drift_fields > 0 ? 'warn' : ''}">${ent.n_drift_fields} <span style="color: var(--muted); font-size: 12px;">(${driftPct}%)</span></div>
    </div>
  `;
}

function showTip(html, evt) {
  const tip = $('tooltip');
  tip.innerHTML = html;
  tip.classList.add('visible');
  // Position with edge-aware clamping.
  const w = tip.offsetWidth;
  const h = tip.offsetHeight;
  let x = evt.clientX + 14;
  let y = evt.clientY + 14;
  if (x + w > window.innerWidth - 8)  x = evt.clientX - w - 14;
  if (y + h > window.innerHeight - 8) y = evt.clientY - h - 14;
  tip.style.left = `${x}px`;
  tip.style.top  = `${y}px`;
}
function hideTip() { $('tooltip').classList.remove('visible'); }

function render() {
  const ent = ENTITIES.find(e => e.canonical === currentEntityId);
  if (!ent) return;
  renderSummary(ent);

  // Filter + sort fields
  let fields = ent.fields.slice();
  if (driftOnly) fields = fields.filter(f => f.drift);
  if (nameFilter) fields = fields.filter(f => f.name.toLowerCase().includes(nameFilter));
  if (sortMode === 'name') fields.sort((a, b) => a.name.localeCompare(b.name));
  else if (sortMode === 'drift-first')
    fields.sort((a, b) => (b.drift - a.drift) || (b.presence - a.presence) || a.name.localeCompare(b.name));
  // 'presence' is the source order — already sorted server-side.

  const nVar = ent.variants.length;
  const nFld = fields.length;

  // Layout constants
  const CELL = 18;
  const HEADER_H = 130;
  const FIELD_LABEL_W = 220;
  const PRESENCE_W = 60;
  const ROW_GAP = 1;
  const COL_GAP = 1;
  const PADDING = 12;

  const totalW = FIELD_LABEL_W + PRESENCE_W + nVar * (CELL + COL_GAP) + PADDING * 2;
  const totalH = HEADER_H + Math.max(nFld, 1) * (CELL + ROW_GAP) + PADDING;

  const svg = d3.select('#heatmap')
    .attr('width',  totalW)
    .attr('height', totalH);
  svg.selectAll('*').remove();

  if (nFld === 0) {
    svg.append('text')
      .attr('x', totalW / 2)
      .attr('y', totalH / 2)
      .attr('text-anchor', 'middle')
      .attr('fill', 'var(--muted)')
      .style('font-size', '14px')
      .text('No fields match the current filter.');
    return;
  }

  // Column background (used for highlight)
  const colBg = svg.append('g').attr('class', 'col-bg-layer');
  ent.variants.forEach((v, vi) => {
    const x = PADDING + FIELD_LABEL_W + PRESENCE_W + vi * (CELL + COL_GAP);
    colBg.append('rect')
      .attr('class', 'col-bg')
      .attr('x', x)
      .attr('y', PADDING)
      .attr('width', CELL)
      .attr('height', HEADER_H - PADDING + nFld * (CELL + ROW_GAP))
      .attr('fill', 'transparent')
      .attr('data-vi', vi);
  });

  // Column headers — rotated labels for repo / class / kind
  const colHdr = svg.append('g').attr('class', 'col-headers');
  ent.variants.forEach((v, vi) => {
    const x = PADDING + FIELD_LABEL_W + PRESENCE_W + vi * (CELL + COL_GAP) + CELL / 2;
    const baseY = HEADER_H;
    // Kind badge as a small bar at the bottom of the header band
    const kindColor = `var(--kind-${v.kind})`;
    colHdr.append('rect')
      .attr('x', x - CELL / 2)
      .attr('y', baseY - 5)
      .attr('width', CELL)
      .attr('height', 4)
      .attr('fill', kindColor);
    // Drift count bar above the kind ribbon
    if (v.drift_minority_count > 0) {
      const denom = ent.n_drift_fields || 1;
      const hgt = Math.min(20, 4 + Math.round(20 * v.drift_minority_count / denom));
      colHdr.append('rect')
        .attr('x', x - CELL / 2 + 4)
        .attr('y', baseY - 5 - hgt)
        .attr('width', CELL - 8)
        .attr('height', hgt)
        .attr('fill', 'var(--cell-drift)')
        .attr('opacity', 0.7);
    }
    // Repo + class label, rotated -55° for readability
    const label = `${v.repo} · ${v.class_name}`;
    colHdr.append('text')
      .attr('transform', `translate(${x}, ${baseY - 12}) rotate(-55)`)
      .attr('text-anchor', 'start')
      .attr('fill', 'var(--text)')
      .style('font-family', 'ui-monospace, monospace')
      .style('font-size', '10px')
      .text(label.length > 38 ? label.slice(0, 38) + '…' : label)
      .on('mousemove', evt => {
        const tip = `
          <div class="tip-title">${escapeHtml(v.class_name)}</div>
          <div class="tip-mono">repo: ${escapeHtml(v.repo)}</div>
          <div class="tip-mono">module: ${escapeHtml(v.module)}</div>
          <div class="tip-mono">file: ${escapeHtml(v.file_path)}</div>
          <div class="tip-section">stats</div>
          <div class="tip-mono">kind: <span class="kind-badge ${v.kind}">${v.kind}</span> · ${v.field_count} fields</div>
          <div class="tip-mono">domain: <span class="dom-badge" data-d="${v.repo_domain}">${v.repo_domain}</span></div>
          <div class="tip-mono">type-drift cells in this column: <strong>${v.drift_minority_count}</strong></div>
        `;
        showTip(tip, evt);
      })
      .on('mouseleave', hideTip)
      .style('cursor', 'pointer');
  });

  // Field rows
  const rowG = svg.append('g').attr('class', 'rows');
  fields.forEach((f, fi) => {
    const y = HEADER_H + fi * (CELL + ROW_GAP);

    const row = rowG.append('g').attr('class', 'field-row');

    // Field name label
    row.append('text')
      .attr('x', PADDING + FIELD_LABEL_W - 8)
      .attr('y', y + CELL / 2 + 4)
      .attr('text-anchor', 'end')
      .attr('fill', f.drift ? 'var(--cell-drift)' : 'var(--text)')
      .style('font-family', 'ui-monospace, monospace')
      .style('font-size', '11px')
      .style('font-weight', f.drift ? '600' : '400')
      .text(f.name);

    // Presence histogram bar
    const presenceX = PADDING + FIELD_LABEL_W + 6;
    const presW = PRESENCE_W - 14;
    const pct = f.presence / nVar;
    row.append('rect')
      .attr('x', presenceX)
      .attr('y', y + 4)
      .attr('width', presW)
      .attr('height', CELL - 8)
      .attr('fill', 'var(--panel-3)');
    row.append('rect')
      .attr('x', presenceX)
      .attr('y', y + 4)
      .attr('width', presW * pct)
      .attr('height', CELL - 8)
      .attr('fill', pct >= 0.8 ? 'var(--kind-jpa)' :
                   pct >= 0.5 ? 'var(--cell-present)' :
                                'var(--cell-only)');
    row.append('text')
      .attr('x', presenceX + presW + 4)
      .attr('y', y + CELL / 2 + 4)
      .attr('fill', 'var(--muted)')
      .style('font-family', 'ui-monospace, monospace')
      .style('font-size', '9px')
      .text(`${f.presence}/${nVar}`);

    // Cells
    ent.variants.forEach((v, vi) => {
      const cx = PADDING + FIELD_LABEL_W + PRESENCE_W + vi * (CELL + COL_GAP);
      const observed = f.by_variant[vi];
      const present = observed != null;
      const drift = present && observed !== f.majority_type;
      const onlyOne = f.presence === 1 && present;

      let fill;
      let cls = 'cell';
      if (!present) {
        fill = 'var(--cell-empty)';
        cls += ' absent-cell';
      } else if (onlyOne) {
        fill = 'var(--cell-only)';
      } else if (drift) {
        fill = 'var(--cell-drift)';
        cls += ' drift-cell';
      } else {
        fill = 'var(--cell-present)';
      }

      const cell = row.append('rect')
        .attr('class', cls)
        .attr('x', cx)
        .attr('y', y)
        .attr('width', CELL)
        .attr('height', CELL)
        .attr('rx', 2)
        .attr('fill', fill)
        .attr('stroke', present ? 'none' : 'var(--cell-empty-bd)')
        .attr('stroke-width', 1);

      cell.on('mousemove', evt => {
        const tip = present ? `
          <div class="tip-title">${escapeHtml(f.name)} <span style="color: var(--muted); font-weight: 400;">in ${escapeHtml(v.class_name)}</span></div>
          <div class="tip-mono">repo: ${escapeHtml(v.repo)}</div>
          <div class="tip-mono">observed type: <strong>${escapeHtml(observed)}</strong></div>
          <div class="tip-mono">majority type: <strong>${escapeHtml(f.majority_type)}</strong></div>
          ${drift ? '<div class="tip-section">⚠ TYPE DRIFT</div>' : ''}
          ${onlyOne ? '<div class="tip-section">solo — only variant with this field</div>' : ''}
          <div class="tip-section">type distribution across ${nVar} variants</div>
          ${Object.entries(f.types).sort((a,b) => b[1] - a[1]).map(([t, c]) =>
            `<div class="type-row ${t === f.majority_type ? 'majority' : 'minority'}">
              <span>${escapeHtml(t)}</span><span>×${c}</span>
            </div>`
          ).join('')}
        ` : `
          <div class="tip-title">${escapeHtml(f.name)} <span style="color: var(--muted); font-weight: 400;">absent in ${escapeHtml(v.class_name)}</span></div>
          <div class="tip-mono">${escapeHtml(v.repo)}</div>
          <div class="tip-section">present in ${f.presence}/${nVar} variants</div>
        `;
        showTip(tip, evt);
      });
      cell.on('mouseleave', hideTip);
    });
  });

  // Highlight a column's cells on hover (col-bg-layer behaviour).
  svg.selectAll('rect.col-bg').on('mouseenter', function() {
    d3.select(this).attr('fill', 'rgba(255, 180, 84, 0.06)');
  }).on('mouseleave', function() {
    d3.select(this).attr('fill', 'transparent');
  });
}

document.addEventListener('DOMContentLoaded', () => {
  buildPicker();
  $('sort-picker').addEventListener('change', e => { sortMode = e.target.value; render(); });
  $('drift-only').addEventListener('change', e => { driftOnly = e.target.checked; render(); });
  $('q').addEventListener('input', e => { nameFilter = e.target.value.trim().toLowerCase(); render(); });
  // URL hash restore
  const hash = decodeURIComponent(location.hash.slice(1));
  if (hash && ENTITIES.find(e => e.canonical === hash)) {
    currentEntityId = hash;
    $('entity-picker').value = hash;
  }
  render();
  // Update hash on entity change
  $('entity-picker').addEventListener('change', () => {
    history.replaceState(null, '', '#' + encodeURIComponent($('entity-picker').value));
  });
});
</script>
</body>
</html>
"""


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--top", type=int, default=DEFAULT_TOP_N,
                   help=f"Number of top canonicals to bundle (default {DEFAULT_TOP_N})")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if not CATALOG_MD.exists() or not RAW_TSV.exists() or not ALIAS_YAML.exists():
        print("ERROR: required inputs missing. Run extract_entities.py + cluster_entities.py first.",
              file=sys.stderr)
        return 2

    payload, summary = build_drift_payload(args.top)
    if not payload:
        print("ERROR: no canonicals with >=2 variants.", file=sys.stderr)
        return 2

    out = (HTML_TEMPLATE
           .replace("__GENERATED__", summary["generated"])
           .replace("__ENTITIES_JSON__", json.dumps(payload, ensure_ascii=False)))

    if args.dry_run:
        sys.stdout.write(out)
        print(f"\n[dry-run] {len(payload)} entities bundled.", file=sys.stderr)
        return 0

    ENTITIES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(out)
    size_kb = OUTPUT.stat().st_size // 1024
    # Quick aggregate signal — useful in the run log.
    total_drift_fields = sum(e["n_drift_fields"] for e in payload)
    total_fields = sum(e["n_fields"] for e in payload)
    print(f"wrote {OUTPUT} ({len(payload)} entities, "
          f"{total_drift_fields}/{total_fields} type-drift fields, {size_kb} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
