#!/usr/bin/env python3
"""
gen_entity_representations.py — bipartite graph of canonical entities ↔ repos.

Each canonical entity gets a circle node; each repo that declares one or
more variants of any entity gets a rounded-square node. Edges connect an
entity to a repo when the repo has at least one variant of that entity.
Edge thickness encodes the number of variant classes for that pairing;
hover/click reveals the actual class names + kinds.

Usage:
    python3 gen_entity_representations.py [--min-occurrence N] [--top N]

Reads:
  - ~/projects/codebase-map/relations/entity-catalog.md            (canonical index)
  - ~/projects/codebase-map/relations/entity-catalog.raw.tsv       (per-class rows)
  - ~/projects/codebase-map/relations/entity_aliases.yaml          (canonicalizer)
  - ~/projects/codebase-map/repos/<repo>.md                        (domain coloring)

Writes:
  - ~/projects/codebase-map/domains/entities/representations.html

Self-contained. D3 v7 loaded from CDN. Stdlib only on the Python side.
Mirrors gen_entity_graph.py / gen_entity_browser.py style.
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
OUTPUT = ENTITIES_DIR / "representations.html"


# --- shared regex idioms ----------------------------------------------------

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
            "has_page": "→" in m.group("page"),
        })
    return out


def parse_raw_rows():
    if not RAW_TSV.exists(): return []
    rows = []
    with RAW_TSV.open() as f:
        header = next(f).rstrip("\n").split("\t")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < len(header):
                parts += [""] * (len(header) - len(parts))
            rows.append(dict(zip(header, parts)))
    return rows


def primary_domain(domains):
    if not domains: return "unassigned"
    pref = [
        "listings-trade", "operations", "pricing-billing", "integrations",
        "identity", "communication", "platform", "analytics", "infrastructure",
    ]
    for p in pref:
        if p in domains: return p
    return domains[0]


def build_graph(min_occurrence, top_n):
    rows = parse_raw_rows()
    catalog_text = CATALOG_MD.read_text(errors="replace")
    catalog_rows = parse_catalog_rows(catalog_text)
    canonical_meta = {r["canonical"]: r for r in catalog_rows}

    canonical_map, splits = parse_alias_yaml(ALIAS_YAML.read_text())
    to_canonical = build_canonicalizer(canonical_map, splits)
    repo_domains = load_repo_domains()

    # Build edges: (canonical, repo) -> list of {class_name, kind, module, fields}
    edge_variants: dict[tuple[str, str], list[dict]] = collections.defaultdict(list)
    canonical_variant_count: collections.Counter = collections.Counter()
    repo_variant_count: collections.Counter = collections.Counter()
    canonical_kinds: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)

    for r in rows:
        cano = to_canonical(r["class_name"], r["repo"])
        if not cano: continue
        try:
            fcount = int(r.get("field_count") or 0)
        except ValueError:
            fcount = 0
        variant = {
            "class_name": r["class_name"],
            "kind": r["kind"],
            "module": r["module"],
            "field_count": fcount,
        }
        edge_variants[(cano, r["repo"])].append(variant)
        canonical_variant_count[cano] += 1
        repo_variant_count[r["repo"]] += 1
        canonical_kinds[cano][r["kind"]] += 1

    # Filter: keep only canonicals with occurrence >= min_occurrence AND in top-N by rank.
    keep_canonicals: set[str] = set()
    ranked_by_rank = sorted(
        (c for c, n in canonical_variant_count.items() if n >= min_occurrence),
        key=lambda c: canonical_meta.get(c, {}).get("rank", 9999),
    )
    keep_canonicals = set(ranked_by_rank[:top_n])

    # Collect every repo touched by at least one kept canonical.
    keep_repos: set[str] = set()
    for (cano, repo), vs in edge_variants.items():
        if cano in keep_canonicals:
            keep_repos.add(repo)

    # Build node + edge payloads.
    entity_nodes = []
    for c in ranked_by_rank:
        if c not in keep_canonicals: continue
        meta = canonical_meta.get(c, {})
        entity_nodes.append({
            "id": f"E:{c}",
            "type": "entity",
            "name": c,
            "rank": meta.get("rank", 9999),
            "variants": canonical_variant_count[c],
            "repos": sum(1 for (cc, _) in edge_variants if cc == c),
            "primary_domain": primary_domain(meta.get("domains", [])),
            "domains": meta.get("domains", []),
            "owning": meta.get("owning", "—"),
            "has_page": meta.get("has_page", False),
            "kind_breakdown": dict(canonical_kinds[c]),
        })

    repo_nodes = []
    # Tally per-repo: how many distinct kept canonicals does it host?
    repo_canonical_count: collections.Counter = collections.Counter()
    repo_total_variant_count: collections.Counter = collections.Counter()
    for (cano, repo), vs in edge_variants.items():
        if cano in keep_canonicals:
            repo_canonical_count[repo] += 1
            repo_total_variant_count[repo] += len(vs)
    for repo in sorted(keep_repos):
        repo_nodes.append({
            "id": f"R:{repo}",
            "type": "repo",
            "name": repo,
            "primary_domain": repo_domains.get(repo, "unassigned"),
            "canonical_count": repo_canonical_count[repo],
            "variant_count": repo_total_variant_count[repo],
        })

    edges = []
    for (cano, repo), vs in edge_variants.items():
        if cano not in keep_canonicals: continue
        edges.append({
            "source": f"E:{cano}",
            "target": f"R:{repo}",
            "weight": len(vs),
            "variants": sorted(vs, key=lambda v: (v["kind"], v["class_name"])),
        })

    return entity_nodes, repo_nodes, edges


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Entity Representations Across Repos</title>
<meta name="generator" content="gen_entity_representations.py">
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
    --edge: #3a4257;
    --edge-hi: #ffb454;
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
  html, body { margin: 0; padding: 0; height: 100%; background: var(--bg); color: var(--text); font: 14px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; overflow: hidden; }
  header {
    padding: 12px 20px;
    background: var(--panel);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: baseline; gap: 16px; flex-wrap: wrap;
    height: 50px;
  }
  header h1 { margin: 0; font-size: 15px; font-weight: 600; }
  header .meta { color: var(--muted); font-size: 11px; }
  header .controls { display: flex; gap: 10px; align-items: center; margin-left: auto; }
  header .ctl-group { display: flex; gap: 4px; align-items: center; font-size: 12px; color: var(--muted); }
  header .ctl-group input[type="range"] { width: 100px; }
  header input[type=search] {
    padding: 5px 10px;
    border: 1px solid var(--border);
    background: var(--panel-2);
    color: var(--text);
    border-radius: 6px;
    font: inherit;
    font-size: 12px;
    width: 220px;
  }
  main { display: grid; grid-template-columns: 1fr 360px; height: calc(100vh - 51px); }
  #graph-host {
    position: relative;
    overflow: hidden;
    background:
      radial-gradient(circle at 20% 30%, rgba(108, 179, 255, 0.05), transparent 50%),
      radial-gradient(circle at 80% 70%, rgba(255, 180, 84, 0.05), transparent 50%),
      var(--bg);
  }
  svg.graph { width: 100%; height: 100%; cursor: grab; }
  svg.graph.dragging { cursor: grabbing; }
  .edge { stroke: var(--edge); stroke-opacity: 0.45; fill: none;
          transition: stroke 200ms, stroke-opacity 200ms, stroke-width 200ms; }
  .edge.hi { stroke: var(--edge-hi); stroke-opacity: 0.95; }
  .edge.dim { stroke-opacity: 0.05; }
  .node { cursor: pointer; transition: opacity 200ms; }
  .node circle, .node rect {
    stroke: #0f1115;
    stroke-width: 1.5;
    transition: stroke 200ms, stroke-width 200ms;
  }
  .node.entity circle { fill-opacity: 0.92; }
  .node.repo rect { fill-opacity: 0.85; }
  .node.hi circle, .node.hi rect { stroke: var(--edge-hi); stroke-width: 2.5; }
  .node.dim { opacity: 0.15; }
  .node text {
    fill: var(--text);
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    pointer-events: none;
    text-anchor: middle;
    paint-order: stroke;
    stroke: #0f1115;
    stroke-width: 3;
    stroke-linejoin: round;
  }
  .node.entity text { font-size: 12px; font-weight: 600; }
  .node.repo text { font-size: 10px; }
  .pulse {
    animation: pulse 1.6s ease-in-out infinite;
    transform-origin: center;
    transform-box: fill-box;
  }
  @keyframes pulse {
    0%, 100% { opacity: 0.55; transform: scale(1); }
    50%      { opacity: 1.00; transform: scale(1.18); }
  }
  aside.detail {
    background: var(--panel);
    border-left: 1px solid var(--border);
    overflow-y: auto;
    padding: 14px 16px;
  }
  aside.detail h2 { margin: 0 0 4px; font-size: 16px; }
  aside.detail .sub { color: var(--muted); font-size: 11px; margin-bottom: 12px; }
  aside.detail .stats { display: grid; grid-template-columns: max-content 1fr; gap: 3px 12px; font-size: 12px; margin-bottom: 14px; }
  aside.detail .stats .k { color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; font-size: 10px; align-self: center; }
  aside.detail .stats .v { font-family: ui-monospace, monospace; word-break: break-all; }
  aside.detail h3 { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin: 16px 0 6px; }
  aside.detail .repo-group {
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 10px;
    margin-bottom: 8px;
    background: var(--panel-2);
  }
  aside.detail .repo-group .repo-name {
    font-family: ui-monospace, monospace;
    font-size: 12px;
    color: var(--link);
    cursor: pointer;
    margin-bottom: 4px;
    font-weight: 600;
  }
  aside.detail .repo-group .repo-name:hover { text-decoration: underline; }
  aside.detail .variant {
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: ui-monospace, monospace;
    font-size: 11px;
    margin: 2px 0;
  }
  aside.detail .kind-badge {
    display: inline-block;
    font-size: 9px;
    padding: 1px 5px;
    border-radius: 3px;
    color: #0f1115;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    min-width: 50px;
    text-align: center;
  }
  aside.detail .kind-jpa      { background: var(--kind-jpa); }
  aside.detail .kind-dto      { background: var(--kind-dto); }
  aside.detail .kind-embedded { background: var(--kind-embedded); }
  aside.detail .kind-other    { background: var(--kind-other); color: #c7cbd5; }
  aside.detail .variant .class { color: var(--text); }
  aside.detail .variant .field-count { color: var(--muted); font-size: 10px; }
  aside.detail .variant .module { color: var(--muted); font-size: 10px; }
  aside.detail .dom-badge {
    display: inline-block;
    font-size: 9px;
    padding: 1px 5px;
    border-radius: 3px;
    color: #0f1115;
    background: var(--d-unassigned);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
    margin-right: 3px;
  }
  aside.detail .dom-badge[data-d="listings-trade"]  { background: var(--d-listings-trade); }
  aside.detail .dom-badge[data-d="operations"]      { background: var(--d-operations); }
  aside.detail .dom-badge[data-d="pricing-billing"] { background: var(--d-pricing-billing); }
  aside.detail .dom-badge[data-d="integrations"]    { background: var(--d-integrations); }
  aside.detail .dom-badge[data-d="identity"]        { background: var(--d-identity); }
  aside.detail .dom-badge[data-d="communication"]   { background: var(--d-communication); }
  aside.detail .dom-badge[data-d="platform"]        { background: var(--d-platform); }
  aside.detail .dom-badge[data-d="analytics"]       { background: var(--d-analytics); }
  aside.detail .dom-badge[data-d="infrastructure"]  { background: var(--d-infrastructure); color: #c7cbd5; }
  aside.detail .empty { color: var(--muted); padding-top: 30px; text-align: center; }
  aside.detail .empty .legend-block {
    text-align: left;
    background: var(--panel-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    margin: 16px 0;
    font-size: 11px;
  }
  aside.detail .legend-row { display: flex; align-items: center; gap: 6px; margin: 3px 0; }
  aside.detail .shape-dot { width: 12px; height: 12px; border-radius: 50%; }
  aside.detail .shape-sq  { width: 12px; height: 8px; border-radius: 2px; }
  .hud {
    position: absolute;
    top: 12px; right: 12px;
    background: rgba(22, 25, 34, 0.85);
    backdrop-filter: blur(8px);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 11px;
    color: var(--muted);
    pointer-events: none;
  }
  .summary-bar {
    position: absolute;
    bottom: 12px; left: 12px; right: 12px;
    background: rgba(22, 25, 34, 0.85);
    backdrop-filter: blur(8px);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 11px;
    color: var(--muted);
    pointer-events: none;
    display: flex;
    gap: 16px;
  }
  .summary-bar strong { color: var(--text); font-weight: 600; }
</style>
</head>
<body>
<header>
  <h1>Entity Representations Across Repos</h1>
  <span class="meta">bipartite · <span id="entity-count"></span> entities · <span id="repo-count"></span> repos · <span id="edge-count"></span> connections · generated __GENERATED__</span>
  <div class="controls">
    <input type="search" id="q" placeholder="Highlight entity or repo…" autocomplete="off">
    <div class="ctl-group">
      <label for="top-slider">Top entities <span id="top-val">__TOP_N__</span></label>
      <input type="range" id="top-slider" min="5" max="50" step="1" value="__TOP_N__">
    </div>
    <div class="ctl-group">
      <label for="edge-slider">min variants <span id="edge-val">1</span></label>
      <input type="range" id="edge-slider" min="1" max="6" step="1" value="1">
    </div>
  </div>
</header>
<main>
  <div id="graph-host">
    <svg class="graph" id="graph"></svg>
    <div class="hud">circles = canonical entities · rectangles = repos · click a node to drill in</div>
    <div class="summary-bar" id="summary-bar"></div>
  </div>
  <aside class="detail" id="detail">
    <div class="empty">
      <div style="font-size: 36px; margin-bottom: 8px;">⊙ ⬚</div>
      <p><strong>Click a node</strong> to see how an entity is represented across repos — or which entities a repo hosts.</p>
      <div class="legend-block">
        <div style="color:var(--muted); text-transform:uppercase; letter-spacing:0.5px; font-size:9px; margin-bottom:6px;">Legend</div>
        <div class="legend-row"><span class="shape-dot" style="background:var(--d-listings-trade)"></span> circle = canonical entity (color = primary domain)</div>
        <div class="legend-row"><span class="shape-sq" style="background:var(--d-operations)"></span> rounded rect = repo (color = repo domain)</div>
        <div class="legend-row"><span class="kind-badge kind-jpa">jpa</span> &nbsp;<span class="kind-badge kind-dto">dto</span> &nbsp;<span class="kind-badge kind-embedded">embedded</span> &nbsp;<span class="kind-badge kind-other">other</span></div>
      </div>
      <p style="font-size: 11px;">Edge thickness = number of variant classes that repo declares for that entity.</p>
    </div>
  </aside>
</main>

<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<script>
const ENTITY_NODES = __ENTITY_NODES_JSON__;
const REPO_NODES   = __REPO_NODES_JSON__;
const EDGES        = __EDGES_JSON__;
const DOMAIN_COLORS = {
  "listings-trade":  getComputedStyle(document.documentElement).getPropertyValue('--d-listings-trade').trim(),
  "operations":       getComputedStyle(document.documentElement).getPropertyValue('--d-operations').trim(),
  "pricing-billing":  getComputedStyle(document.documentElement).getPropertyValue('--d-pricing-billing').trim(),
  "integrations":     getComputedStyle(document.documentElement).getPropertyValue('--d-integrations').trim(),
  "identity":         getComputedStyle(document.documentElement).getPropertyValue('--d-identity').trim(),
  "communication":    getComputedStyle(document.documentElement).getPropertyValue('--d-communication').trim(),
  "platform":         getComputedStyle(document.documentElement).getPropertyValue('--d-platform').trim(),
  "analytics":        getComputedStyle(document.documentElement).getPropertyValue('--d-analytics').trim(),
  "infrastructure":   getComputedStyle(document.documentElement).getPropertyValue('--d-infrastructure').trim(),
  "unassigned":       getComputedStyle(document.documentElement).getPropertyValue('--d-unassigned').trim(),
};
let topN = __TOP_N__;
let minEdgeWeight = 1;
let selected = null;
const $ = id => document.getElementById(id);

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
                  .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function entityRadius(n) {
  return Math.max(7, Math.min(28, 4 + Math.sqrt(n.variants) * 2.2));
}

function repoSize(n) {
  // width x height
  const cnt = n.canonical_count || 1;
  const w = Math.max(40, Math.min(140, 40 + cnt * 6));
  return { w, h: 18 };
}

const svg = d3.select("#graph");
const width  = $('graph-host').clientWidth;
const height = $('graph-host').clientHeight;
svg.attr("viewBox", `0 0 ${width} ${height}`);

const root = svg.append("g").attr("class", "root");
const edgeLayer = root.append("g").attr("class", "edges");
const nodeLayer = root.append("g").attr("class", "nodes");

const zoom = d3.zoom()
  .scaleExtent([0.2, 4])
  .on("zoom", (e) => root.attr("transform", e.transform));
svg.call(zoom);

let sim = null;
let visibleEntities = [];
let visibleRepos = [];
let visibleEdges = [];

function applyFilter() {
  // 1. Keep top-N entities by rank.
  const sorted = ENTITY_NODES.slice().sort((a, b) => a.rank - b.rank);
  const keptE = new Set(sorted.slice(0, topN).map(n => n.id));
  // 2. Keep edges meeting min weight and whose entity is kept.
  visibleEdges = EDGES.filter(e =>
    e.weight >= minEdgeWeight && keptE.has(e.source)
  ).map(e => ({...e}));
  // 3. Keep entity nodes that survive AND have at least one kept edge.
  const liveEntities = new Set(visibleEdges.map(e => e.source));
  visibleEntities = ENTITY_NODES.filter(n => keptE.has(n.id) && liveEntities.has(n.id))
                                 .map(n => ({...n}));
  // 4. Keep repos that are endpoints of any kept edge.
  const liveRepos = new Set(visibleEdges.map(e => e.target));
  visibleRepos = REPO_NODES.filter(n => liveRepos.has(n.id)).map(n => ({...n}));

  $('entity-count').textContent = visibleEntities.length;
  $('repo-count').textContent = visibleRepos.length;
  $('edge-count').textContent = visibleEdges.length;
  renderSummary();
  rebuild();
}

function renderSummary() {
  if (visibleEdges.length === 0) {
    $('summary-bar').innerHTML = '';
    return;
  }
  // Total variant count = sum of edge weights
  const totalVariants = visibleEdges.reduce((acc, e) => acc + e.weight, 0);
  // Heaviest edge
  const heaviest = visibleEdges.slice().sort((a, b) => b.weight - a.weight)[0];
  const ePart = heaviest ? `${heaviest.source.replace('E:', '')} × ${heaviest.target.replace('R:', '')}` : '—';
  // Most-connected entity (most repos)
  const entityRepoCount = new Map();
  for (const e of visibleEdges) {
    entityRepoCount.set(e.source, (entityRepoCount.get(e.source) || 0) + 1);
  }
  let topEntity = null, topCount = 0;
  for (const [eid, c] of entityRepoCount) {
    if (c > topCount) { topCount = c; topEntity = eid; }
  }
  $('summary-bar').innerHTML = `
    <span><strong>${totalVariants}</strong> total variant classes</span>
    <span>most-spread entity: <strong>${escapeHtml((topEntity || '—').replace('E:', ''))}</strong> (${topCount} repos)</span>
    <span>heaviest connection: <strong>${escapeHtml(ePart)}</strong> (${heaviest ? heaviest.weight : 0} variants)</span>
  `;
}

function rebuild() {
  edgeLayer.selectAll("*").remove();
  nodeLayer.selectAll("*").remove();

  const link = edgeLayer.selectAll("line")
    .data(visibleEdges, d => `${d.source}|${d.target}`)
    .join("line")
    .attr("class", "edge")
    .attr("stroke-width", d => Math.min(6, 0.8 + Math.log2(d.weight + 1) * 1.4))
    .on("mouseover", function(event, d) {
      d3.select(this).classed("hi", true);
    })
    .on("mouseout", function(event, d) {
      if (!selected) d3.select(this).classed("hi", false);
    })
    .on("click", (event, d) => {
      event.stopPropagation();
      selectEdge(d);
    });

  link.append("title").text(d =>
    `${d.source.replace('E:','')}  ×  ${d.target.replace('R:','')}\n${d.weight} variant class(es)`
  );

  const allNodes = visibleEntities.concat(visibleRepos);
  const node = nodeLayer.selectAll("g")
    .data(allNodes, d => d.id)
    .join("g")
    .attr("class", d => "node " + d.type)
    .call(d3.drag()
      .on("start", dragStart)
      .on("drag", dragging)
      .on("end", dragEnd))
    .on("click", (event, d) => { event.stopPropagation(); selectNode(d.id); });

  // Entity nodes: circles
  node.filter(d => d.type === "entity")
    .append("circle")
    .attr("r", entityRadius)
    .attr("fill", d => DOMAIN_COLORS[d.primary_domain] || DOMAIN_COLORS.unassigned);

  // Repo nodes: rounded rectangles
  node.filter(d => d.type === "repo")
    .append("rect")
    .attr("x", d => -repoSize(d).w / 2)
    .attr("y", d => -repoSize(d).h / 2)
    .attr("width",  d => repoSize(d).w)
    .attr("height", d => repoSize(d).h)
    .attr("rx", 4)
    .attr("ry", 4)
    .attr("fill", d => DOMAIN_COLORS[d.primary_domain] || DOMAIN_COLORS.unassigned);

  // Labels
  node.filter(d => d.type === "entity")
    .append("text")
    .attr("dy", d => entityRadius(d) + 11)
    .text(d => d.name);
  node.filter(d => d.type === "repo")
    .append("text")
    .attr("dy", 3)
    .style("stroke-width", 0)
    .style("fill", "#0f1115")
    .text(d => d.name);

  // Tooltip
  node.append("title").text(d => {
    if (d.type === "entity") {
      const kbd = Object.entries(d.kind_breakdown || {})
        .map(([k, v]) => `${k}=${v}`).join(', ');
      return `${d.name}\n#${d.rank} · ${d.variants} variants · ${d.repos} repos\nkinds: ${kbd}`;
    } else {
      return `${d.name}\ndomain: ${d.primary_domain}\nhosts ${d.canonical_count} catalog entities (${d.variant_count} variants)`;
    }
  });

  if (sim) sim.stop();
  sim = d3.forceSimulation(allNodes)
    .force("link", d3.forceLink(visibleEdges)
      .id(d => d.id)
      .distance(d => 80 + 6 / Math.sqrt(d.weight))
      .strength(d => Math.min(0.7, 0.15 * Math.log2(d.weight + 1) + 0.15)))
    .force("charge", d3.forceManyBody().strength(d => d.type === "entity" ? -400 : -160))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collide", d3.forceCollide().radius(d => d.type === "entity" ? entityRadius(d) + 18 : repoSize(d).w / 2 + 6))
    .force("x", d3.forceX(d => d.type === "entity" ? width * 0.35 : width * 0.7).strength(0.08))
    .alpha(1).alphaDecay(0.025)
    .on("tick", () => {
      link
        .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
      node.attr("transform", d => `translate(${d.x}, ${d.y})`);
    });

  if (selected) applySelection(selected);
}

function dragStart(event, d) {
  if (!event.active) sim.alphaTarget(0.3).restart();
  d.fx = d.x; d.fy = d.y;
  svg.classed("dragging", true);
}
function dragging(event, d) { d.fx = event.x; d.fy = event.y; }
function dragEnd(event, d) {
  if (!event.active) sim.alphaTarget(0);
  svg.classed("dragging", false);
}

function endpointId(e, side) {
  const v = side === 'src' ? e.source : e.target;
  return typeof v === 'object' ? v.id : v;
}

function applySelection(id) {
  const neighborIds = new Set([id]);
  for (const e of visibleEdges) {
    const s = endpointId(e, 'src');
    const t = endpointId(e, 'tgt');
    if (s === id) neighborIds.add(t);
    if (t === id) neighborIds.add(s);
  }
  nodeLayer.selectAll("g.node")
    .classed("hi", d => d.id === id)
    .classed("dim", d => !neighborIds.has(d.id));
  edgeLayer.selectAll("line")
    .classed("hi", e => {
      const s = endpointId(e, 'src');
      const t = endpointId(e, 'tgt');
      return s === id || t === id;
    })
    .classed("dim", e => {
      const s = endpointId(e, 'src');
      const t = endpointId(e, 'tgt');
      return s !== id && t !== id;
    });
}

function clearSelection() {
  selected = null;
  nodeLayer.selectAll("g.node").classed("hi", false).classed("dim", false);
  edgeLayer.selectAll("line").classed("hi", false).classed("dim", false);
  renderDetailEmpty();
}

function selectNode(id) {
  selected = id;
  applySelection(id);
  if (id.startsWith("E:")) renderEntityDetail(id);
  else renderRepoDetail(id);
  nodeLayer.selectAll("g.node circle, g.node rect").classed("pulse", d => d.id === id);
  setTimeout(() => nodeLayer.selectAll("circle, rect").classed("pulse", false), 1600);
}

function selectEdge(d) {
  // Highlight edge + its two endpoints. Detail panel shows just this edge's variants.
  selected = null;
  nodeLayer.selectAll("g.node")
    .classed("hi", n => n.id === d.source || n.id === d.target)
    .classed("dim", n => n.id !== d.source && n.id !== d.target);
  edgeLayer.selectAll("line")
    .classed("hi", e => e === d)
    .classed("dim", e => e !== d);
  renderEdgeDetail(d);
}

function renderDetailEmpty() {
  $('detail').innerHTML = `
    <div class="empty">
      <div style="font-size: 36px; margin-bottom: 8px;">⊙ ⬚</div>
      <p><strong>Click a node</strong> to see how an entity is represented across repos — or which entities a repo hosts.</p>
      <div class="legend-block">
        <div style="color:var(--muted); text-transform:uppercase; letter-spacing:0.5px; font-size:9px; margin-bottom:6px;">Legend</div>
        <div class="legend-row"><span class="shape-dot" style="background:var(--d-listings-trade)"></span> circle = canonical entity (color = primary domain)</div>
        <div class="legend-row"><span class="shape-sq" style="background:var(--d-operations)"></span> rounded rect = repo (color = repo domain)</div>
        <div class="legend-row"><span class="kind-badge kind-jpa">jpa</span> &nbsp;<span class="kind-badge kind-dto">dto</span> &nbsp;<span class="kind-badge kind-embedded">embedded</span> &nbsp;<span class="kind-badge kind-other">other</span></div>
      </div>
      <p style="font-size: 11px;">Edge thickness = number of variant classes that repo declares for that entity.</p>
    </div>
  `;
}

function variantBadge(v) {
  return `<span class="kind-badge kind-${escapeHtml(v.kind)}">${escapeHtml(v.kind)}</span>`;
}

function renderEntityDetail(id) {
  const entity = ENTITY_NODES.find(n => n.id === id);
  if (!entity) return;
  const edgesForEntity = EDGES.filter(e => e.source === id)
                              .sort((a, b) => b.weight - a.weight);
  const domBadges = (entity.domains || []).map(d =>
    `<span class="dom-badge" data-d="${escapeHtml(d)}">${escapeHtml(d)}</span>`).join('');
  const kbd = entity.kind_breakdown || {};
  const kindLine = Object.entries(kbd).map(([k, v]) =>
    `<span class="kind-badge kind-${escapeHtml(k)}">${escapeHtml(k)} ×${v}</span>`
  ).join(' ');

  let html = `
    <h2>⊙ ${escapeHtml(entity.name)}</h2>
    <div class="sub">rank #${entity.rank}${entity.rank <= 25 ? ' · top-25' : ''}</div>
    <div class="stats">
      <div class="k">Variants</div><div class="v">${entity.variants}</div>
      <div class="k">Repos</div><div class="v">${entity.repos}</div>
      <div class="k">Owning</div><div class="v">${escapeHtml(entity.owning)}</div>
      <div class="k">Domains</div><div class="v">${domBadges || '—'}</div>
      <div class="k">Kinds</div><div class="v">${kindLine || '—'}</div>
    </div>
    <h3>Representations by repo (${edgesForEntity.length})</h3>
  `;
  for (const e of edgesForEntity) {
    const repo = e.target.replace('R:', '');
    const vlist = (e.variants || []).map(v => `
      <div class="variant">
        ${variantBadge(v)}
        <span class="class">${escapeHtml(v.class_name)}</span>
        <span class="field-count">· ${v.field_count} fields</span>
      </div>
      <div class="variant"><span class="module">module: ${escapeHtml(v.module)}</span></div>
    `).join('');
    html += `
      <div class="repo-group">
        <div class="repo-name" data-jump="R:${escapeHtml(repo)}">⬚ ${escapeHtml(repo)} <span style="color:var(--muted); font-weight:400; font-size:10px;">· ${e.weight} variant${e.weight === 1 ? '' : 's'}</span></div>
        ${vlist}
      </div>
    `;
  }
  if (entity.has_page) {
    html += `<div style="margin-top: 14px; font-size: 11px;"><a href="./${encodeURIComponent(entity.name)}.md" style="color: var(--link);">→ open ${escapeHtml(entity.name)}.md</a></div>`;
  }
  $('detail').innerHTML = html;
  wireJumps();
}

function renderRepoDetail(id) {
  const repo = REPO_NODES.find(n => n.id === id);
  if (!repo) return;
  const edgesForRepo = EDGES.filter(e => e.target === id)
                            .sort((a, b) => b.weight - a.weight);

  let html = `
    <h2>⬚ ${escapeHtml(repo.name)}</h2>
    <div class="sub">repo</div>
    <div class="stats">
      <div class="k">Domain</div><div class="v"><span class="dom-badge" data-d="${escapeHtml(repo.primary_domain)}">${escapeHtml(repo.primary_domain)}</span></div>
      <div class="k">Catalog entities hosted</div><div class="v">${repo.canonical_count}</div>
      <div class="k">Variant classes</div><div class="v">${repo.variant_count}</div>
    </div>
    <div style="margin-top: 8px; font-size: 11px;"><a href="../../repos/${encodeURIComponent(repo.name)}.md" style="color: var(--link);">→ open shadow doc</a></div>
    <h3>Entities declared here (${edgesForRepo.length})</h3>
  `;
  for (const e of edgesForRepo) {
    const ent = e.source.replace('E:', '');
    const vlist = (e.variants || []).map(v => `
      <div class="variant">
        ${variantBadge(v)}
        <span class="class">${escapeHtml(v.class_name)}</span>
        <span class="field-count">· ${v.field_count} fields</span>
        <span class="module">· ${escapeHtml(v.module)}</span>
      </div>
    `).join('');
    html += `
      <div class="repo-group">
        <div class="repo-name" data-jump="E:${escapeHtml(ent)}">⊙ ${escapeHtml(ent)} <span style="color:var(--muted); font-weight:400; font-size:10px;">· ${e.weight} variant${e.weight === 1 ? '' : 's'}</span></div>
        ${vlist}
      </div>
    `;
  }
  $('detail').innerHTML = html;
  wireJumps();
}

function renderEdgeDetail(edge) {
  const entId = endpointId(edge, 'src').replace('E:', '');
  const repoId = endpointId(edge, 'tgt').replace('R:', '');
  let html = `
    <h2><span style="color:var(--muted)">⊙</span> ${escapeHtml(entId)}
        <span style="color:var(--muted); font-weight:400;">→</span>
        <span style="color:var(--muted)">⬚</span> ${escapeHtml(repoId)}</h2>
    <div class="sub">${edge.weight} variant${edge.weight === 1 ? '' : 's'}</div>
  `;
  for (const v of (edge.variants || [])) {
    html += `
      <div class="repo-group">
        <div class="variant">
          ${variantBadge(v)}
          <span class="class">${escapeHtml(v.class_name)}</span>
          <span class="field-count">· ${v.field_count} fields</span>
        </div>
        <div class="variant"><span class="module">module: ${escapeHtml(v.module)}</span></div>
      </div>
    `;
  }
  html += `
    <div style="margin-top: 12px; font-size: 11px; display: flex; gap: 10px;">
      <span class="repo-name" data-jump="E:${escapeHtml(entId)}" style="cursor:pointer;">⊙ open entity</span>
      <span class="repo-name" data-jump="R:${escapeHtml(repoId)}" style="cursor:pointer;">⬚ open repo</span>
    </div>
  `;
  $('detail').innerHTML = html;
  wireJumps();
}

function wireJumps() {
  for (const el of document.querySelectorAll('.repo-name[data-jump]')) {
    el.addEventListener('click', () => {
      const target = el.getAttribute('data-jump');
      const exists = ENTITY_NODES.find(n => n.id === target)
                  || REPO_NODES.find(n => n.id === target);
      if (exists) selectNode(target);
    });
  }
}

svg.on("click", clearSelection);

$('q').addEventListener('input', e => {
  const q = e.target.value.trim().toLowerCase();
  if (!q) { clearSelection(); return; }
  const pool = visibleEntities.concat(visibleRepos);
  const hit = pool.find(n => n.name.toLowerCase() === q)
           || pool.find(n => n.name.toLowerCase().startsWith(q))
           || pool.find(n => n.name.toLowerCase().includes(q));
  if (hit) selectNode(hit.id);
});

$('top-slider').addEventListener('input', e => {
  topN = parseInt(e.target.value, 10);
  $('top-val').textContent = topN;
  applyFilter();
});
$('edge-slider').addEventListener('input', e => {
  minEdgeWeight = parseInt(e.target.value, 10);
  $('edge-val').textContent = minEdgeWeight;
  applyFilter();
});

applyFilter();
renderDetailEmpty();

// Restore from URL hash: E:Vehicle or R:loadboard-backend
const hash = decodeURIComponent(location.hash.slice(1));
if (hash) setTimeout(() => selectNode(hash), 500);
</script>
</body>
</html>
"""


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--min-occurrence", type=int, default=2)
    p.add_argument("--top", type=int, default=15,
                   help="Default top-N entities loaded (slider goes 5-50; default 15 keeps the layout readable)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if not CATALOG_MD.exists() or not RAW_TSV.exists() or not ALIAS_YAML.exists():
        print("ERROR: required inputs missing. Run extract_entities.py + cluster_entities.py first.",
              file=sys.stderr)
        return 2

    entity_nodes, repo_nodes, edges = build_graph(args.min_occurrence, top_n=50)
    if not entity_nodes:
        print("ERROR: no entity nodes produced.", file=sys.stderr)
        return 2

    generated = dt.date.today().isoformat()
    out = (HTML_TEMPLATE
           .replace("__GENERATED__", generated)
           .replace("__TOP_N__", str(args.top))
           .replace("__ENTITY_NODES_JSON__", json.dumps(entity_nodes, ensure_ascii=False))
           .replace("__REPO_NODES_JSON__", json.dumps(repo_nodes, ensure_ascii=False))
           .replace("__EDGES_JSON__", json.dumps(edges, ensure_ascii=False)))

    if args.dry_run:
        sys.stdout.write(out)
        print(f"\n[dry-run] {len(entity_nodes)} entities, {len(repo_nodes)} repos, {len(edges)} edges bundled.", file=sys.stderr)
        return 0

    ENTITIES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(out)
    size_kb = OUTPUT.stat().st_size // 1024
    print(f"wrote {OUTPUT} ({len(entity_nodes)} entities, "
          f"{len(repo_nodes)} repos, {len(edges)} edges, {size_kb} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
