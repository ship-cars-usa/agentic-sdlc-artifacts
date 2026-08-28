#!/usr/bin/env python3
"""
gen_entity_graph.py — render the cross-repo entity catalog as a force-directed
SVG graph at domains/entities/graph.html.

Usage:
    python3 gen_entity_graph.py [--min-occurrence N] [--min-edge-weight N]

Reads:
  - ~/projects/codebase-map/relations/entity-catalog.md
  - ~/projects/codebase-map/relations/entity-catalog.raw.tsv
  - ~/projects/codebase-map/relations/entity_aliases.yaml
  - ~/projects/codebase-map/repos/<repo>.md         (frontmatter domain:)

Writes:
  - ~/projects/codebase-map/domains/entities/graph.html

Self-contained HTML — D3 v7 loaded from CDN. Nodes are canonical entities
sized by occurrence and colored by their primary domain. Edges represent
field-type references (e.g. `PostingEntity.vehicles : VehicleEntity[]` →
edge `Posting -> Vehicle`). Edges aggregate across all variants; line width
encodes reference count.

Stdlib only. Mirrors gen_entity_browser.py / gen_schema_browser.py style.
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
OUTPUT = ENTITIES_DIR / "graph.html"

# Java types that never resolve to a business entity — drop them from edges.
SCALAR_BLACKLIST = {
    "String", "Integer", "Long", "Boolean", "Double", "Float", "Short",
    "Byte", "Character", "int", "long", "boolean", "double", "float",
    "short", "byte", "char", "void", "Object", "Number", "BigDecimal",
    "BigInteger", "UUID", "URI", "URL", "Date", "Instant", "LocalDate",
    "LocalDateTime", "LocalTime", "ZonedDateTime", "OffsetDateTime",
    "Duration", "Period", "Timestamp", "Time",
    "List", "Set", "Map", "Optional", "Iterable", "Collection",
    "Class", "Enum", "JsonNode", "ObjectNode", "ArrayNode",
    "byte[]", "char[]", "int[]", "long[]",
    # Common framework / utility shapes that aren't business entities
    "JsonObject", "JsonArray", "PageRequest", "Pageable", "Sort",
    "Direction", "Order", "ResponseEntity",
}

# Mirror cluster_entities normalization (kept narrow & duplicated rather than
# importing — cross-script imports are not a precedent in this scripts dir).
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


def parse_alias_yaml(text: str) -> tuple[dict[str, list[str]], list[dict]]:
    canonical: dict[str, list[str]] = {}
    splits: list[dict] = []
    section: str | None = None
    cur_split: dict | None = None
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
                if cur_split: splits.append(cur_split)
                cur_split = {"canonical": m.group(1), "repos": [], "names": []}
                continue
            if cur_split is None: continue
            m = re.match(r"^\s+repos:\s*\[(.*)\]\s*$", line)
            if m:
                cur_split["repos"] = [n.strip() for n in m.group(1).split(",") if n.strip()]
                continue
            m = re.match(r"^\s+names:\s*\[(.*)\]\s*$", line)
            if m:
                cur_split["names"] = [n.strip() for n in m.group(1).split(",") if n.strip()]
                continue
    if cur_split: splits.append(cur_split)
    return canonical, splits


def base_strip(name: str) -> str:
    prev = ""
    while prev != name:
        prev = name
        name = SUFFIX_STRIP_RE.sub("", name)
        name = VERSION_PREFIX_RE.sub("", name)
        name = QUALIFIER_PREFIX_RE.sub("", name)
    return name


def strip_prefix_if_matches(name: str, repo: str) -> str:
    for p in SERVICE_PREFIXES:
        if name.startswith(p) and len(name) > len(p) and name[len(p)].isupper():
            if p.lower() in repo.lower():
                return name[len(p):]
    return name


def build_canonicalizer(canonical_map, splits):
    name_to_canonical: dict[str, str] = {}
    for cano, names in canonical_map.items():
        for n in names:
            name_to_canonical[n] = cano
    split_map: dict[tuple[str, str], str] = {}
    for s in splits:
        for r in s["repos"]:
            for n in s["names"]:
                split_map[(r, n)] = s["canonical"]
    def to_canonical(class_name: str, repo: str = "") -> str | None:
        if not class_name or class_name in SCALAR_BLACKLIST:
            return None
        if (repo, class_name) in split_map:
            return split_map[(repo, class_name)]
        stripped = base_strip(class_name)
        if (repo, stripped) in split_map:
            return split_map[(repo, stripped)]
        stripped = strip_prefix_if_matches(stripped, repo)
        if stripped in SCALAR_BLACKLIST:
            return None
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
    """Returns (rows, fields_per_row) where rows is a list of dicts and
    fields_per_row[i] is a list of (name, type) pairs."""
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
            # Parse fields
            fields = []
            for chunk in (row.get("fields") or "").split(";"):
                if ":" not in chunk: continue
                n, _, t = chunk.partition(":")
                fields.append((n.strip(), t.strip()))
            row["_fields"] = fields
            rows.append(row)
    return rows


def field_type_to_canonical_candidate(ftype: str) -> str | None:
    """Extract a simple type name from a (possibly-wrapped) field type. Returns
    None if it's clearly a scalar / primitive / framework type."""
    if not ftype: return None
    t = ftype.strip()
    # Drop collection marker we set in extractor.
    while t.endswith("[]"):
        t = t[:-2].strip()
    # Drop array brackets like `String[]`
    t = t.replace("[]", "").strip()
    # If there's still a generic, take the inner-most simple-looking type
    inner = re.search(r"<\s*([\w.]+)\s*>", t)
    if inner:
        t = inner.group(1)
    # Trim package prefix
    if "." in t:
        t = t.rsplit(".", 1)[-1]
    # Drop enum-suffix patterns — they're not entities
    if t.endswith("Enum"): return None
    if t in SCALAR_BLACKLIST: return None
    # Single uppercase letter (generic type parameter)
    if len(t) <= 1: return None
    if not t[:1].isupper(): return None
    return t


def primary_domain(domains: list[str]) -> str:
    if not domains: return "unassigned"
    # Prefer business-meaningful first
    pref = [
        "listings-trade", "operations", "pricing-billing", "integrations",
        "identity", "communication", "platform", "analytics", "infrastructure",
    ]
    for p in pref:
        if p in domains: return p
    return domains[0]


def build_graph(min_occurrence: int, min_edge_weight: int):
    rows = parse_raw_rows()
    catalog_text = CATALOG_MD.read_text(errors="replace")
    catalog_rows = parse_catalog_rows(catalog_text)
    canonical_to_meta = {r["canonical"]: r for r in catalog_rows}

    canonical_map, splits = parse_alias_yaml(ALIAS_YAML.read_text())
    to_canonical = build_canonicalizer(canonical_map, splits)

    # Edges: (src_canonical, tgt_canonical) -> weight
    edge_w: dict[tuple[str, str], int] = collections.Counter()
    # Sample fields per edge for the tooltip — capped to 4.
    edge_samples: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    for r in rows:
        src = to_canonical(r["class_name"], r["repo"])
        if not src: continue
        for fname, ftype in r["_fields"]:
            simple = field_type_to_canonical_candidate(ftype)
            if not simple: continue
            tgt = to_canonical(simple, r["repo"])
            if not tgt or tgt == src: continue
            edge_w[(src, tgt)] += 1
            samples = edge_samples[(src, tgt)]
            if len(samples) < 4:
                marker = " [list]" if "[]" in ftype else ""
                samples.append(f"{r['repo']}.{r['class_name']}.{fname}{marker}")

    # Nodes: every canonical referenced by any rendered edge OR present in
    # catalog with occurrence >= min_occurrence.
    canonicals_used: set[str] = set()
    edges_out: list[dict] = []
    for (s, t), w in edge_w.items():
        if w < min_edge_weight: continue
        edges_out.append({"source": s, "target": t, "weight": w,
                          "samples": edge_samples[(s, t)]})
        canonicals_used.add(s); canonicals_used.add(t)

    nodes_out: list[dict] = []
    for cano in sorted(canonicals_used):
        meta = canonical_to_meta.get(cano)
        if meta is None:
            # Orphan canonical (extracted but not in catalog index because of
            # late-stage filtering) — synthesize a minimal node.
            occ = sum(1 for r in rows
                      if to_canonical(r["class_name"], r["repo"]) == cano)
            if occ < min_occurrence:
                continue
            nodes_out.append({
                "id": cano, "rank": 9999, "variants": occ, "repos": 0,
                "domains": [], "primary_domain": "unassigned",
                "owning": "—", "has_page": False,
            })
            continue
        if meta["variants"] < min_occurrence:
            continue
        nodes_out.append({
            "id": cano,
            "rank": meta["rank"],
            "variants": meta["variants"],
            "repos": meta["repos"],
            "domains": meta["domains"],
            "primary_domain": primary_domain(meta["domains"]),
            "owning": meta["owning"],
            "has_page": meta["has_page"],
        })

    # Now drop edges whose endpoints were filtered out.
    node_ids = {n["id"] for n in nodes_out}
    edges_out = [e for e in edges_out
                 if e["source"] in node_ids and e["target"] in node_ids]

    # Compute degree for size sorting / focus emphasis.
    deg = collections.Counter()
    for e in edges_out:
        deg[e["source"]] += e["weight"]
        deg[e["target"]] += e["weight"]
    for n in nodes_out:
        n["degree"] = deg.get(n["id"], 0)

    # Sort nodes by rank ascending (top entities first) so the list view in
    # the right panel is ordered. D3 force layout doesn't care about order.
    nodes_out.sort(key=lambda n: (n["rank"], n["id"]))

    return nodes_out, edges_out


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Entity Relation Graph</title>
<meta name="generator" content="gen_entity_graph.py">
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
    width: 200px;
  }
  main { display: grid; grid-template-columns: 1fr 320px; height: calc(100vh - 51px); }
  #graph-host {
    position: relative;
    overflow: hidden;
    background:
      radial-gradient(circle at 25% 30%, rgba(108, 179, 255, 0.05), transparent 50%),
      radial-gradient(circle at 75% 70%, rgba(255, 180, 84, 0.05), transparent 50%),
      var(--bg);
  }
  svg.graph { width: 100%; height: 100%; cursor: grab; }
  svg.graph.dragging { cursor: grabbing; }
  .edge { stroke: var(--edge); stroke-opacity: 0.5; transition: stroke 200ms, stroke-opacity 200ms, stroke-width 200ms; }
  .edge.hi { stroke: var(--edge-hi); stroke-opacity: 0.95; }
  .edge.dim { stroke-opacity: 0.08; }
  .node { cursor: pointer; transition: opacity 200ms; }
  .node circle {
    stroke: #0f1115;
    stroke-width: 1.5;
    transition: stroke 200ms, stroke-width 200ms;
  }
  .node.hi circle { stroke: var(--edge-hi); stroke-width: 2.5; }
  .node.dim { opacity: 0.18; }
  .node text {
    fill: var(--text);
    font-size: 10px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    pointer-events: none;
    text-anchor: middle;
    paint-order: stroke;
    stroke: #0f1115;
    stroke-width: 3;
    stroke-linejoin: round;
  }
  .node.top text { font-weight: 600; font-size: 11px; }
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
  aside.detail h2 { margin: 0 0 6px; font-size: 16px; }
  aside.detail .sub { color: var(--muted); font-size: 11px; margin-bottom: 14px; }
  aside.detail .stats { display: grid; grid-template-columns: max-content 1fr; gap: 3px 12px; font-size: 12px; margin-bottom: 14px; }
  aside.detail .stats .k { color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; font-size: 10px; align-self: center; }
  aside.detail .stats .v { font-family: ui-monospace, monospace; word-break: break-all; }
  aside.detail h3 { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin: 16px 0 6px; }
  aside.detail ul { list-style: none; padding: 0; margin: 0; }
  aside.detail ul li { padding: 4px 0; font-size: 12px; border-bottom: 1px solid var(--border); }
  aside.detail ul li:last-child { border-bottom: none; }
  aside.detail .arrow { color: var(--muted); margin: 0 4px; }
  aside.detail .neigh { font-family: ui-monospace, monospace; font-size: 12px; cursor: pointer; color: var(--link); }
  aside.detail .neigh:hover { text-decoration: underline; }
  aside.detail .field { font-family: ui-monospace, monospace; font-size: 11px; color: var(--muted); }
  aside.detail .weight { color: var(--accent); font-weight: 600; }
  .dom-badge {
    display: inline-block;
    font-size: 9px;
    padding: 1px 5px;
    border-radius: 3px;
    margin-right: 3px;
    color: #0f1115;
    background: var(--d-unassigned);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
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
  aside.detail .empty { color: var(--muted); padding-top: 30px; text-align: center; }
  .legend {
    position: absolute;
    bottom: 12px; left: 12px;
    background: rgba(22, 25, 34, 0.85);
    backdrop-filter: blur(8px);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 11px;
    pointer-events: none;
  }
  .legend .row { display: flex; align-items: center; gap: 6px; margin: 2px 0; }
  .legend .dot { width: 9px; height: 9px; border-radius: 50%; }
  .legend-title { color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; font-size: 9px; margin-bottom: 4px; }
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
</style>
</head>
<body>
<header>
  <h1>Entity Relation Graph</h1>
  <span class="meta"><span id="node-count"></span> nodes · <span id="edge-count"></span> edges · generated __GENERATED__</span>
  <div class="controls">
    <input type="search" id="q" placeholder="Highlight node by name…" autocomplete="off">
    <div class="ctl-group">
      <label for="top-slider">Top-N <span id="top-val">50</span></label>
      <input type="range" id="top-slider" min="10" max="200" step="5" value="50">
    </div>
    <div class="ctl-group">
      <label for="edge-slider">min edge w <span id="edge-val">1</span></label>
      <input type="range" id="edge-slider" min="1" max="10" step="1" value="1">
    </div>
  </div>
</header>
<main>
  <div id="graph-host">
    <svg class="graph" id="graph"></svg>
    <div class="hud">drag to pan · scroll to zoom · click node to focus · drag node to pin</div>
    <div class="legend">
      <div class="legend-title">Domains</div>
      <div class="row"><span class="dot" style="background:var(--d-listings-trade)"></span>listings-trade</div>
      <div class="row"><span class="dot" style="background:var(--d-operations)"></span>operations</div>
      <div class="row"><span class="dot" style="background:var(--d-pricing-billing)"></span>pricing-billing</div>
      <div class="row"><span class="dot" style="background:var(--d-integrations)"></span>integrations</div>
      <div class="row"><span class="dot" style="background:var(--d-identity)"></span>identity</div>
      <div class="row"><span class="dot" style="background:var(--d-communication)"></span>communication</div>
      <div class="row"><span class="dot" style="background:var(--d-platform)"></span>platform</div>
      <div class="row"><span class="dot" style="background:var(--d-analytics)"></span>analytics</div>
      <div class="row"><span class="dot" style="background:var(--d-infrastructure)"></span>infrastructure</div>
    </div>
  </div>
  <aside class="detail" id="detail">
    <div class="empty">
      <div style="font-size: 36px; margin-bottom: 8px;">◉</div>
      <p><strong>Click a node</strong> to see its incoming &amp; outgoing entity references.</p>
      <p style="font-size: 11px;">Node size = occurrence count.<br>Edge thickness = number of field references.<br>Edge direction: source declares a field typed as target.</p>
    </div>
  </aside>
</main>

<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<script>
const NODES = __NODES_JSON__;
const EDGES = __EDGES_JSON__;
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
let topN = 50;
let minEdgeWeight = 1;
let selected = null;
const $ = id => document.getElementById(id);

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
                  .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function nodeRadius(n) {
  // sqrt scaling so a 40-variant node isn't 8x larger than a 5-variant one
  return Math.max(4, Math.min(28, 3 + Math.sqrt(n.variants) * 2.4));
}

const svg = d3.select("#graph");
const width  = $('graph-host').clientWidth;
const height = $('graph-host').clientHeight;
svg.attr("viewBox", `0 0 ${width} ${height}`);

// Arrow marker for directed edges
svg.append("defs").append("marker")
  .attr("id", "arrow")
  .attr("viewBox", "0 -4 8 8")
  .attr("refX", 6)
  .attr("refY", 0)
  .attr("markerWidth", 6)
  .attr("markerHeight", 6)
  .attr("orient", "auto")
  .append("path")
  .attr("d", "M0,-4L8,0L0,4")
  .attr("fill", "#3a4257");

const root = svg.append("g").attr("class", "root");
const edgeLayer = root.append("g").attr("class", "edges");
const nodeLayer = root.append("g").attr("class", "nodes");

const zoom = d3.zoom()
  .scaleExtent([0.25, 4])
  .on("zoom", (e) => root.attr("transform", e.transform));
svg.call(zoom);

let sim = null;
let visibleNodes = [];
let visibleEdges = [];

function applyFilter() {
  // Take top-N by rank, plus any node referenced by a kept edge of weight >= min.
  const ranked = NODES.slice().sort((a, b) => a.rank - b.rank);
  const keptIds = new Set(ranked.slice(0, topN).map(n => n.id));
  const initialEdges = EDGES.filter(e => e.weight >= minEdgeWeight);
  // Expand: 1-hop neighbors of the kept set, but only via edges that meet min weight.
  let expanded = new Set(keptIds);
  for (const e of initialEdges) {
    if (keptIds.has(e.source) || keptIds.has(e.target)) {
      expanded.add(e.source); expanded.add(e.target);
    }
  }
  visibleNodes = NODES.filter(n => expanded.has(n.id))
                      .map(n => ({...n}));  // shallow clone so D3 can mutate x/y
  const idMap = new Map(visibleNodes.map(n => [n.id, n]));
  visibleEdges = initialEdges.filter(e => idMap.has(e.source) && idMap.has(e.target))
                              .map(e => ({...e}));
  $('node-count').textContent = visibleNodes.length;
  $('edge-count').textContent = visibleEdges.length;
  rebuild();
}

function rebuild() {
  edgeLayer.selectAll("*").remove();
  nodeLayer.selectAll("*").remove();

  const link = edgeLayer.selectAll("line")
    .data(visibleEdges, d => `${d.source}|${d.target}`)
    .join("line")
    .attr("class", "edge")
    .attr("stroke-width", d => Math.min(5, 0.6 + Math.log2(d.weight + 1)))
    .attr("marker-end", "url(#arrow)");

  const node = nodeLayer.selectAll("g")
    .data(visibleNodes, d => d.id)
    .join("g")
    .attr("class", d => "node" + (d.rank <= 25 ? " top" : ""))
    .call(d3.drag()
      .on("start", dragStart)
      .on("drag", dragging)
      .on("end", dragEnd))
    .on("click", (event, d) => { event.stopPropagation(); selectNode(d.id); });

  node.append("circle")
    .attr("r", nodeRadius)
    .attr("fill", d => DOMAIN_COLORS[d.primary_domain] || DOMAIN_COLORS.unassigned)
    .attr("opacity", 0.85);

  node.append("text")
    .attr("dy", d => nodeRadius(d) + 11)
    .text(d => d.id);

  node.append("title")
    .text(d => `${d.id}\n#${d.rank} · ${d.variants} variants · ${d.repos} repos\ndomains: ${d.domains.join(', ') || '—'}`);

  if (sim) sim.stop();
  sim = d3.forceSimulation(visibleNodes)
    .force("link", d3.forceLink(visibleEdges)
      .id(d => d.id)
      .distance(d => 60 + 20 / Math.sqrt(d.weight)))
    .force("charge", d3.forceManyBody().strength(-220))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collide", d3.forceCollide().radius(d => nodeRadius(d) + 6))
    .alpha(1).alphaDecay(0.02)
    .on("tick", () => {
      link
        .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
        .attr("x2", d => {
          // Pull arrowhead just outside the target circle
          const r = nodeRadius(d.target);
          const dx = d.target.x - d.source.x;
          const dy = d.target.y - d.source.y;
          const L = Math.sqrt(dx*dx + dy*dy) || 1;
          return d.target.x - (dx / L) * (r + 3);
        })
        .attr("y2", d => {
          const r = nodeRadius(d.target);
          const dx = d.target.x - d.source.x;
          const dy = d.target.y - d.source.y;
          const L = Math.sqrt(dx*dx + dy*dy) || 1;
          return d.target.y - (dy / L) * (r + 3);
        });
      node.attr("transform", d => `translate(${d.x}, ${d.y})`);
    });

  // Apply selection highlight if any
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
  // Leave d.fx / d.fy set so the node stays pinned where dropped.
  svg.classed("dragging", false);
}

function applySelection(id) {
  const incoming = visibleEdges.filter(e =>
    (typeof e.target === 'object' ? e.target.id : e.target) === id);
  const outgoing = visibleEdges.filter(e =>
    (typeof e.source === 'object' ? e.source.id : e.source) === id);
  const neighborIds = new Set([id]);
  incoming.forEach(e => neighborIds.add(typeof e.source === 'object' ? e.source.id : e.source));
  outgoing.forEach(e => neighborIds.add(typeof e.target === 'object' ? e.target.id : e.target));

  nodeLayer.selectAll("g.node")
    .classed("hi", d => d.id === id)
    .classed("dim", d => !neighborIds.has(d.id));
  edgeLayer.selectAll("line")
    .classed("hi", e => {
      const s = typeof e.source === 'object' ? e.source.id : e.source;
      const t = typeof e.target === 'object' ? e.target.id : e.target;
      return s === id || t === id;
    })
    .classed("dim", e => {
      const s = typeof e.source === 'object' ? e.source.id : e.source;
      const t = typeof e.target === 'object' ? e.target.id : e.target;
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
  renderDetail(id);
  // Pulse the selected node briefly.
  nodeLayer.selectAll("g.node circle").classed("pulse", d => d.id === id);
  setTimeout(() => nodeLayer.selectAll("circle").classed("pulse", false), 1600);
}

function renderDetailEmpty() {
  $('detail').innerHTML = `
    <div class="empty">
      <div style="font-size: 36px; margin-bottom: 8px;">◉</div>
      <p><strong>Click a node</strong> to see its incoming &amp; outgoing entity references.</p>
      <p style="font-size: 11px;">Node size = occurrence count.<br>Edge thickness = number of field references.<br>Edge direction: source declares a field typed as target.</p>
    </div>
  `;
}

function edgeEndpoint(e, side) {
  const v = side === 'src' ? e.source : e.target;
  return typeof v === 'object' ? v.id : v;
}

function renderDetail(id) {
  const node = NODES.find(n => n.id === id);
  if (!node) return;
  const incoming = EDGES.filter(e => edgeEndpoint(e, 'tgt') === id && e.weight >= minEdgeWeight);
  const outgoing = EDGES.filter(e => edgeEndpoint(e, 'src') === id && e.weight >= minEdgeWeight);
  incoming.sort((a, b) => b.weight - a.weight);
  outgoing.sort((a, b) => b.weight - a.weight);
  const domBadges = (node.domains || []).map(d =>
    `<span class="dom-badge" data-d="${escapeHtml(d)}">${escapeHtml(d)}</span>`).join('');

  let html = `
    <h2>${escapeHtml(node.id)}</h2>
    <div class="sub">rank #${node.rank}${node.rank <= 25 ? ' · top-25' : ''}</div>
    <div class="stats">
      <div class="k">Variants</div><div class="v">${node.variants}</div>
      <div class="k">Repos</div><div class="v">${node.repos}</div>
      <div class="k">Owning</div><div class="v">${escapeHtml(node.owning)}</div>
      <div class="k">Domains</div><div class="v">${domBadges || '—'}</div>
    </div>
  `;

  html += `<h3>Outgoing — fields point at (${outgoing.length})</h3><ul>`;
  if (outgoing.length === 0) html += `<li class="field">none</li>`;
  for (const e of outgoing.slice(0, 30)) {
    const tgt = edgeEndpoint(e, 'tgt');
    html += `<li>
      <div><span class="neigh" data-jump="${escapeHtml(tgt)}">${escapeHtml(tgt)}</span>
        <span class="weight">×${e.weight}</span></div>
      <div class="field">${(e.samples || []).slice(0, 3).map(escapeHtml).join('<br>')}</div>
    </li>`;
  }
  html += `</ul>`;

  html += `<h3>Incoming — pointed at by (${incoming.length})</h3><ul>`;
  if (incoming.length === 0) html += `<li class="field">none</li>`;
  for (const e of incoming.slice(0, 30)) {
    const src = edgeEndpoint(e, 'src');
    html += `<li>
      <div><span class="neigh" data-jump="${escapeHtml(src)}">${escapeHtml(src)}</span>
        <span class="weight">×${e.weight}</span></div>
      <div class="field">${(e.samples || []).slice(0, 3).map(escapeHtml).join('<br>')}</div>
    </li>`;
  }
  html += `</ul>`;

  if (node.has_page) {
    html += `<div style="margin-top: 14px; font-size: 11px;"><a href="./${encodeURIComponent(node.id)}.md" style="color: var(--link);">→ open ${escapeHtml(node.id)}.md</a></div>`;
  }
  $('detail').innerHTML = html;

  // Wire jump links.
  for (const el of document.querySelectorAll('.neigh[data-jump]')) {
    el.addEventListener('click', () => {
      const target = el.getAttribute('data-jump');
      if (NODES.find(n => n.id === target)) {
        // If target not currently visible, expand top-N until it is.
        let nodeRec = NODES.find(n => n.id === target);
        if (!visibleNodes.find(n => n.id === target)) {
          // Try expanding top slider to reveal it.
          if (nodeRec.rank > topN) {
            topN = Math.max(topN, Math.min(200, nodeRec.rank + 5));
            $('top-slider').value = topN;
            $('top-val').textContent = topN;
            applyFilter();
            // After rebuild, select.
            setTimeout(() => selectNode(target), 80);
            return;
          }
        }
        selectNode(target);
      }
    });
  }
}

// Background click clears selection
svg.on("click", clearSelection);

// Search box: highlight the first matching node
$('q').addEventListener('input', e => {
  const q = e.target.value.trim().toLowerCase();
  if (!q) { clearSelection(); return; }
  const hit = visibleNodes.find(n => n.id.toLowerCase() === q)
           || visibleNodes.find(n => n.id.toLowerCase().startsWith(q))
           || visibleNodes.find(n => n.id.toLowerCase().includes(q));
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

// Restore from URL hash
const hash = decodeURIComponent(location.hash.slice(1));
if (hash) setTimeout(() => selectNode(hash), 500);
</script>
</body>
</html>
"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--min-occurrence", type=int, default=2,
                   help="Drop nodes with fewer than N variants (default 2)")
    p.add_argument("--min-edge-weight", type=int, default=1,
                   help="Drop edges with fewer than N references (default 1)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if not CATALOG_MD.exists() or not RAW_TSV.exists() or not ALIAS_YAML.exists():
        print("ERROR: required inputs missing. Run extract_entities.py + cluster_entities.py first.",
              file=sys.stderr)
        return 2

    nodes, edges = build_graph(args.min_occurrence, args.min_edge_weight)
    if not nodes:
        print("ERROR: no nodes pass the filter — check raw TSV and alias YAML.", file=sys.stderr)
        return 2

    generated = dt.date.today().isoformat()
    nodes_json = json.dumps(nodes, ensure_ascii=False)
    edges_json = json.dumps(edges, ensure_ascii=False)
    out = (HTML_TEMPLATE
           .replace("__GENERATED__", generated)
           .replace("__NODES_JSON__", nodes_json)
           .replace("__EDGES_JSON__", edges_json))

    if args.dry_run:
        sys.stdout.write(out)
        print(f"\n[dry-run] {len(nodes)} nodes, {len(edges)} edges bundled.", file=sys.stderr)
        return 0

    ENTITIES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(out)
    size_kb = OUTPUT.stat().st_size // 1024
    print(f"wrote {OUTPUT} ({len(nodes)} nodes, {len(edges)} edges, {size_kb} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
