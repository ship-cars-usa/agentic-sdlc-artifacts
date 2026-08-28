#!/usr/bin/env python3
"""
cluster_entities.py — normalize entity-catalog.raw.tsv into canonical buckets,
emit the master index, per-entity pages, and shadow-doc `## Entities` sections.

Usage:
    python3 cluster_entities.py [--top N] [--no-shadow-update]

Reads:
  - ~/projects/codebase-map/relations/entity-catalog.raw.tsv   (extractor output)
  - ~/projects/codebase-map/relations/entity_aliases.yaml       (hand-curated)
  - ~/projects/codebase-map/repos/<repo>.md                     (frontmatter domain:)
  - ~/projects/codebase-map/relations/event-schemas/*.md        (canonical-dto:)

Writes:
  - ~/projects/codebase-map/relations/entity-catalog.md         (master index)
  - ~/projects/codebase-map/domains/entities/<Canonical>.md     (top-N)
  - ~/projects/codebase-map/relations/entity-catalog.unaliased.tsv
  - ~/projects/codebase-map/repos/<repo>.md                     (## Entities section)

Stdlib only. Run extract_entities.py first.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

HOME = Path.home()
PROJECTS_ROOT = HOME / "projects" / "ship-cars-usa"
MAP_ROOT = HOME / "projects" / "codebase-map"
SHADOW_DIR = MAP_ROOT / "repos"
RAW_TSV = MAP_ROOT / "relations" / "entity-catalog.raw.tsv"
ALIAS_YAML = MAP_ROOT / "relations" / "entity_aliases.yaml"
CATALOG_MD = MAP_ROOT / "relations" / "entity-catalog.md"
UNALIASED_TSV = MAP_ROOT / "relations" / "entity-catalog.unaliased.tsv"
ENTITIES_DIR = MAP_ROOT / "domains" / "entities"
EVENT_SCHEMA_DIR = MAP_ROOT / "relations" / "event-schemas"

DEFAULT_TOP_N = 25

SHADOW_SECTION_BEGIN = "<!-- entities-begin -->"
SHADOW_SECTION_END = "<!-- entities-end -->"

# --- minimal yaml parser ----------------------------------------------------
# entity_aliases.yaml has a constrained shape: two top-level keys (`canonical:`
# and `splits:`); under canonical, `<Canonical>: [name, name, ...]`; under
# splits, a list of dicts with `canonical:`, `repos: [...]`, `names: [...]`.
# Writing a tiny parser avoids a pyyaml dependency.

def parse_alias_yaml(text: str) -> tuple[dict[str, list[str]], list[dict]]:
    """Returns (canonical_map, splits)."""
    canonical: dict[str, list[str]] = {}
    splits: list[dict] = []
    section: str | None = None
    cur_split: dict | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("canonical:"):
            section = "canonical"
            continue
        if line.startswith("splits:"):
            section = "splits"
            continue
        if section == "canonical":
            m = re.match(r"^\s+([\w]+):\s*\[(.*)\]\s*$", line)
            if m:
                key = m.group(1).strip()
                names = [n.strip() for n in m.group(2).split(",") if n.strip()]
                canonical[key] = names
            continue
        if section == "splits":
            # New split entry
            m = re.match(r"^\s*-\s+canonical:\s*(\w+)\s*$", line)
            if m:
                if cur_split:
                    splits.append(cur_split)
                cur_split = {"canonical": m.group(1), "repos": [], "names": []}
                continue
            if cur_split is None:
                continue
            m = re.match(r"^\s+repos:\s*\[(.*)\]\s*$", line)
            if m:
                cur_split["repos"] = [n.strip() for n in m.group(1).split(",") if n.strip()]
                continue
            m = re.match(r"^\s+names:\s*\[(.*)\]\s*$", line)
            if m:
                cur_split["names"] = [n.strip() for n in m.group(1).split(",") if n.strip()]
                continue
    if cur_split:
        splits.append(cur_split)
    return canonical, splits


# --- frontmatter helpers ---------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict[str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


def load_repo_domains() -> dict[str, str]:
    out: dict[str, str] = {}
    for p in SHADOW_DIR.glob("*.md"):
        if p.name.startswith("_"):
            continue
        fm = parse_frontmatter(p.read_text(errors="replace"))
        out[p.stem] = fm.get("domain", "unassigned")
    return out


# --- name normalization ----------------------------------------------------

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


def base_strip(name: str) -> str:
    """Apply suffix + qualifier + version stripping. Idempotent."""
    prev = ""
    while prev != name:
        prev = name
        name = SUFFIX_STRIP_RE.sub("", name)
        name = VERSION_PREFIX_RE.sub("", name)
        name = QUALIFIER_PREFIX_RE.sub("", name)
    return name


def maybe_strip_service_prefix(name: str, repo: str) -> str:
    """Strip leading service-name prefix only when it matches a known service."""
    for p in SERVICE_PREFIXES:
        if name.startswith(p) and len(name) > len(p) and name[len(p)].isupper():
            # Only strip when repo or domain implies this service
            repo_low = repo.lower()
            if p.lower() in repo_low:
                return name[len(p):]
    return name


@dataclass
class Row:
    repo: str
    module: str
    file_path: str
    class_name: str
    kind: str
    extends: str
    table_or_path: str
    field_count: int
    fields: list[tuple[str, str]] = field(default_factory=list)


def parse_raw_tsv(path: Path) -> list[Row]:
    rows: list[Row] = []
    with path.open() as f:
        next(f, None)  # header
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                parts += [""] * (9 - len(parts))
            fields_raw = parts[8]
            pairs: list[tuple[str, str]] = []
            if fields_raw:
                for chunk in fields_raw.split(";"):
                    if ":" in chunk:
                        n, _, t = chunk.partition(":")
                        pairs.append((n.strip(), t.strip()))
            try:
                fc = int(parts[7] or 0)
            except ValueError:
                fc = 0
            rows.append(Row(
                repo=parts[0], module=parts[1], file_path=parts[2],
                class_name=parts[3], kind=parts[4], extends=parts[5],
                table_or_path=parts[6], field_count=fc, fields=pairs,
            ))
    return rows


# --- canonical assignment --------------------------------------------------

def build_name_to_canonical(canonical_map: dict[str, list[str]]) -> dict[str, str]:
    """Reverse the YAML: each observed name -> canonical."""
    out: dict[str, str] = {}
    for cano, names in canonical_map.items():
        for n in names:
            if n in out and out[n] != cano:
                raise SystemExit(
                    f"ERROR: alias '{n}' appears under both '{out[n]}' and '{cano}'. "
                    f"Fix entity_aliases.yaml."
                )
            out[n] = cano
    return out


def split_lookup(splits: list[dict]) -> dict[tuple[str, str], str]:
    """(repo, name) -> canonical override."""
    out: dict[tuple[str, str], str] = {}
    for s in splits:
        for r in s["repos"]:
            for n in s["names"]:
                out[(r, n)] = s["canonical"]
    return out


def canonicalize(row: Row,
                 name_map: dict[str, str],
                 split_map: dict[tuple[str, str], str]) -> str:
    # 1. Splits override anything (apply on the raw class name AND on its
    #    suffix-stripped form, since aliases are usually base-form).
    stripped_full = base_strip(row.class_name)
    if (row.repo, row.class_name) in split_map:
        return split_map[(row.repo, row.class_name)]
    if (row.repo, stripped_full) in split_map:
        return split_map[(row.repo, stripped_full)]
    # 2. Strip suffix, version, qualifier.
    name = stripped_full
    # 3. Service-prefix strip.
    name = maybe_strip_service_prefix(name, row.repo)
    # 4. Alias merge.
    if name in name_map:
        return name_map[name]
    if row.class_name in name_map:
        return name_map[row.class_name]
    # 5. Otherwise the post-strip name is its own canonical.
    return name


# --- event-schema cross-reference -----------------------------------------

def load_event_schema_index(name_map: dict[str, str],
                            split_map: dict[tuple[str, str], str]) -> dict[str, list[dict]]:
    """canonical -> [{topic, producers, consumers, dto_file, source_path}]."""
    out: dict[str, list[dict]] = collections.defaultdict(list)
    if not EVENT_SCHEMA_DIR.exists():
        return out
    for p in sorted(EVENT_SCHEMA_DIR.glob("*.md")):
        if p.name.startswith("_"):
            continue
        text = p.read_text(errors="replace")
        fm = parse_frontmatter(text)
        topic = fm.get("topic", p.stem)
        dto = fm.get("canonical-dto", "").strip("~").strip()
        if not dto:
            continue
        # dto may be FQCN or simple name
        simple = dto.rsplit(".", 1)[-1]
        # Canonicalize: split → suffix → alias
        stripped = base_strip(simple)
        canonical = name_map.get(stripped, name_map.get(simple, stripped))
        out[canonical].append({
            "topic": topic,
            "producers": fm.get("producers", ""),
            "consumers": fm.get("consumers", ""),
            "dto_simple": simple,
            "schema_path": p.name,
        })
    return out


# --- ranking ---------------------------------------------------------------

@dataclass
class Cluster:
    canonical: str
    rows: list[Row] = field(default_factory=list)
    aliases: set[str] = field(default_factory=set)

    @property
    def occurrence(self) -> int:
        return len(self.rows)

    @property
    def repos(self) -> set[str]:
        return {r.repo for r in self.rows}


def cluster_all(rows: list[Row],
                name_map: dict[str, str],
                split_map: dict[tuple[str, str], str]) -> dict[str, Cluster]:
    clusters: dict[str, Cluster] = {}
    for r in rows:
        cano = canonicalize(r, name_map, split_map)
        if not cano:
            continue
        c = clusters.setdefault(cano, Cluster(canonical=cano))
        c.rows.append(r)
        c.aliases.add(r.class_name)
    return clusters


def score(c: Cluster, repo_domains: dict[str, str]) -> tuple[int, int, int]:
    domains = {repo_domains.get(r, "unassigned") for r in c.repos}
    domains.discard("unassigned")
    composite = c.occurrence + 2 * len(domains)
    return (composite, c.occurrence, len(domains))


# --- use-case extraction (REST endpoints + repository methods) -------------

REST_ANNO_RE = re.compile(
    r'@(?P<verb>Path|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)'
    r'\s*\(\s*(?:value\s*=\s*)?"(?P<path>[^"]+)"'
)
SPRING_GET_RE = re.compile(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\s*(?:\(\s*"([^"]*)"\s*\))?')
METHOD_DECL_RE = re.compile(
    r'^\s*(?:public|protected|private)?\s*'
    r'(?:[\w.<>,?\s\[\]]+\s+)?'  # return type (loose)
    r'(?P<name>\w+)\s*\([^)]*\)\s*(?:throws[^{;]+)?[{;]',
    re.MULTILINE,
)
REPO_INTERFACE_RE = re.compile(
    r"\binterface\s+(?P<name>\w+Repository)\b[^{]*?"
    r"\b(?:extends|implements)\s+[^{]*?(?P<base>JpaRepository|CrudRepository|"
    r"PagingAndSortingRepository|MongoRepository|PanacheRepository|"
    r"PanacheRepositoryBase|ReactivePanacheRepository|Repository)"
    r"\s*<\s*(?P<target>\w+)",
    re.DOTALL,
)


def find_repo_root(repo_name: str) -> Path:
    return PROJECTS_ROOT / repo_name


def find_rest_endpoints(repo_name: str, names: set[str]) -> list[tuple[str, str, str]]:
    """Return [(file_relpath, verb, path), ...] for files that reference any
    `names` (entity simple names / aliases). Best-effort; skips test files."""
    repo_root = find_repo_root(repo_name)
    if not repo_root.is_dir():
        return []
    # Use rg if available for speed; fall back to Python walk.
    try:
        # Find candidate REST-annotated files first via rg
        out = subprocess.run(
            ["rg", "-l", "-t", "java",
             r"@(Path|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)",
             str(repo_root)],
            capture_output=True, text=True, timeout=20,
        )
        files = [Path(p) for p in out.stdout.splitlines() if p]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        files = list(repo_root.rglob("*.java"))
    results: list[tuple[str, str, str]] = []
    for f in files:
        s = str(f)
        if "/src/test/" in s or "/target/" in s or "/generated-sources/" in s:
            continue
        try:
            text = f.read_text(errors="replace")
        except OSError:
            continue
        # Must mention at least one of the canonical names
        if not any(re.search(rf"\b{re.escape(n)}\b", text) for n in names):
            continue
        # Class-level @Path
        class_path = ""
        cm = re.search(r'@Path\s*\(\s*"([^"]+)"\s*\)\s*(?:public\s+)?(?:abstract\s+)?(?:class|interface)\s+\w+', text)
        if cm:
            class_path = cm.group(1).rstrip("/")
        else:
            cm = re.search(r'@RequestMapping\s*\(\s*(?:value\s*=\s*)?"([^"]+)"\s*\)\s*public\s+class\s+\w+', text)
            if cm:
                class_path = cm.group(1).rstrip("/")
        for m in REST_ANNO_RE.finditer(text):
            verb_anno = m.group("verb")
            path = m.group("path")
            # Map annotation to HTTP verb where possible.
            if verb_anno == "Path":
                # Quarkus @Path — verb is determined by @GET/@POST sibling on same method.
                # Look at the next ~120 chars for @GET/@POST/etc.
                window = text[m.end(): m.end() + 200]
                vm = re.search(r"@(GET|POST|PUT|DELETE|PATCH)\b", window)
                http_verb = vm.group(1) if vm else "ANY"
            elif verb_anno == "RequestMapping":
                http_verb = "ANY"
            else:
                http_verb = verb_anno.replace("Mapping", "").upper()
            full_path = path
            if class_path and not path.startswith("/"):
                full_path = f"{class_path}/{path}"
            elif class_path and path != class_path:
                full_path = f"{class_path}{path}" if path.startswith("/") else f"{class_path}/{path}"
            results.append((str(f.relative_to(repo_root)), http_verb, full_path))
    # Dedup + cap
    seen: set[tuple[str, str]] = set()
    deduped: list[tuple[str, str, str]] = []
    for r in results:
        key = (r[1], r[2])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)
    return deduped[:40]


def find_repo_methods(repo_name: str, names: set[str]) -> list[tuple[str, str, list[str]]]:
    """Return [(file_relpath, target_type, [method_names])] for *Repository
    interfaces whose generic target matches an alias."""
    repo_root = find_repo_root(repo_name)
    if not repo_root.is_dir():
        return []
    out: list[tuple[str, str, list[str]]] = []
    for f in repo_root.rglob("*Repository.java"):
        sp = str(f)
        if "/src/test/" in sp or "/target/" in sp or "/generated-sources/" in sp:
            continue
        try:
            text = f.read_text(errors="replace")
        except OSError:
            continue
        m = REPO_INTERFACE_RE.search(text)
        if not m:
            continue
        target = m.group("target")
        if target not in names:
            continue
        # Body of the interface: everything between the next { and matching }.
        body_start = text.find("{", m.end())
        if body_start < 0:
            continue
        depth = 0
        body_end = len(text)
        for i, ch in enumerate(text[body_start:], start=body_start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    body_end = i
                    break
        body = text[body_start + 1: body_end]
        method_names: list[str] = []
        for mm in METHOD_DECL_RE.finditer(body):
            nm = mm.group("name")
            if nm in {"if", "for", "while", "switch", "return", "throw", "new"}:
                continue
            method_names.append(nm)
        # Dedup preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for n in method_names:
            if n in seen:
                continue
            seen.add(n)
            unique.append(n)
        out.append((str(f.relative_to(repo_root)), target, unique[:30]))
    return out


# --- field union/intersection ---------------------------------------------

def compute_field_stats(cluster: Cluster) -> tuple[list[tuple[str, str, int]],
                                                    list[tuple[str, list[str]]]]:
    """Return (core_fields, variant_fields).

    core_fields  = list of (field_name, commonest_type, presence_count) for
                   fields present in >=60% of variants.
    variant_fields = list of (field_name, [repos that have it]) for
                     fields present in <60% of variants.
    """
    variant_count = len(cluster.rows)
    if variant_count == 0:
        return [], []
    field_to_repos: dict[str, list[str]] = collections.defaultdict(list)
    field_to_types: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in cluster.rows:
        seen_in_row: set[str] = set()
        for n, t in r.fields:
            if n in seen_in_row:
                continue
            seen_in_row.add(n)
            field_to_repos[n].append(r.repo)
            field_to_types[n][t] += 1
    threshold = max(2, int(variant_count * 0.6))
    core: list[tuple[str, str, int]] = []
    variant: list[tuple[str, list[str]]] = []
    for fname, repos in field_to_repos.items():
        common_type, _ = field_to_types[fname].most_common(1)[0]
        if len(set(repos)) >= threshold:
            core.append((fname, common_type, len(set(repos))))
        else:
            variant.append((fname, sorted(set(repos))))
    core.sort(key=lambda x: (-x[2], x[0]))
    variant.sort(key=lambda x: (-len(x[1]), x[0]))
    return core, variant


# --- owning service heuristic ---------------------------------------------

def pick_owning_service(cluster: Cluster, repo_domains: dict[str, str],
                        rest_counts: dict[str, int]) -> str | None:
    if not cluster.rows:
        return None
    # Prefer the repo whose domain "matches" the canonical name.
    candidates = sorted(cluster.repos)
    by_score: list[tuple[int, int, str]] = []
    for repo in candidates:
        domain_match = 1 if cluster.canonical.lower() in repo_domains.get(repo, "").lower() else 0
        # Largest JPA field count in this repo
        max_fields = max(
            (r.field_count for r in cluster.rows if r.repo == repo and r.kind == "jpa"),
            default=0,
        )
        rest = rest_counts.get(repo, 0)
        # primary: rest endpoint count; tiebreak: jpa field count; tiebreak: domain match
        by_score.append((rest, max_fields, domain_match, repo))  # type: ignore[arg-type]
    by_score.sort(reverse=True)
    return by_score[0][-1]  # type: ignore[return-value]


# --- rendering -------------------------------------------------------------

def fence(s: str) -> str:
    return f"`{s}`"


def render_entity_page(c: Cluster,
                       repo_domains: dict[str, str],
                       event_index: dict[str, list[dict]],
                       today: str) -> str:
    aliases = sorted(c.aliases)
    domains = sorted({repo_domains.get(r, "unassigned") for r in c.repos})
    occurrence = c.occurrence
    seed_repo_default = sorted(c.repos)[0] if c.repos else "unknown"

    # Compute REST endpoints + repo methods per variant repo.
    names_set: set[str] = set(c.aliases)
    rest_per_repo: dict[str, list[tuple[str, str, str]]] = {}
    method_per_repo: dict[str, list[tuple[str, str, list[str]]]] = {}
    rest_counts: dict[str, int] = {}
    for repo in sorted(c.repos):
        rest = find_rest_endpoints(repo, names_set)
        if rest:
            rest_per_repo[repo] = rest
            rest_counts[repo] = len(rest)
        methods = find_repo_methods(repo, names_set)
        if methods:
            method_per_repo[repo] = methods

    owning = pick_owning_service(c, repo_domains, rest_counts) or seed_repo_default

    # Core / variant fields
    core, variant = compute_field_stats(c)

    lines: list[str] = []
    lines.append("---")
    lines.append(f"entity: {c.canonical}")
    lines.append(f"aliases: [{', '.join(aliases)}]")
    lines.append("status: auto-generated")
    lines.append(f"domains: [{', '.join(domains)}]")
    lines.append(f"occurrence-count: {occurrence}")
    lines.append(f"variant-count: {len(c.rows)}")
    lines.append(f"owning-service: {owning}")
    lines.append(f"last-extracted-date: {today}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {c.canonical}")
    lines.append("")

    # What it is
    lines.append("## What it is")
    lines.append("")
    lines.append(f"TODO: human narrative. {occurrence} variants across "
                 f"{len(c.repos)} repos and {len(domains)} domains "
                 f"({', '.join(domains)}). Owning service: "
                 f"[`{owning}`](../../repos/{owning}.md).")
    lines.append("")

    # Variants
    lines.append("## Variants")
    lines.append("")
    lines.append("| Repo | Class | Kind | Module | Extends | Field count | Module path |")
    lines.append("|---|---|---|---|---|---:|---|")
    for r in sorted(c.rows, key=lambda r: (r.repo, r.class_name)):
        lines.append(
            f"| [{r.repo}](../../repos/{r.repo}.md) | `{r.class_name}` | "
            f"{r.kind} | `{r.module}` | "
            f"{fence(r.extends) if r.extends else '—'} | "
            f"{r.field_count} | `{r.file_path}` |"
        )
    lines.append("")

    # Field union / intersection
    lines.append("## Field union / intersection")
    lines.append("")
    lines.append(f"**Core fields** (present in ≥60% of variants — {max(2, int(len(c.rows)*0.6))}/{len(c.rows)} or more):")
    lines.append("")
    if core:
        lines.append("| Field | Common type | Variants with it |")
        lines.append("|---|---|---:|")
        for fname, ftype, cnt in core[:40]:
            lines.append(f"| `{fname}` | `{ftype}` | {cnt} |")
    else:
        lines.append("_(no fields shared by ≥60% of variants — high heterogeneity)_")
    lines.append("")
    lines.append("**Variant-specific fields** (present in <60% of variants, top 30 by spread):")
    lines.append("")
    if variant:
        lines.append("| Field | Repos that declare it |")
        lines.append("|---|---|")
        for fname, repos in variant[:30]:
            lines.append(f"| `{fname}` | {', '.join('`' + r + '`' for r in repos)} |")
    else:
        lines.append("_(no variant-specific fields)_")
    lines.append("")

    # Use cases
    lines.append("## Use cases")
    lines.append("")
    lines.append("### REST surface")
    lines.append("")
    if rest_per_repo:
        for repo in sorted(rest_per_repo):
            lines.append(f"**{repo}**:")
            for fpath, verb, path in rest_per_repo[repo][:25]:
                lines.append(f"- `{verb} {path}` — `{fpath}`")
            lines.append("")
    else:
        lines.append("_(no REST endpoints reference this entity in any variant repo)_")
        lines.append("")

    lines.append("### Repository operations")
    lines.append("")
    if method_per_repo:
        for repo in sorted(method_per_repo):
            lines.append(f"**{repo}**:")
            for fpath, target, methods in method_per_repo[repo]:
                lines.append(f"- `{fpath}` — `{target}`")
                if methods:
                    lines.append(f"  - methods: " + ", ".join(f"`{m}()`" for m in methods[:15]))
            lines.append("")
    else:
        lines.append("_(no Spring Data / Panache repositories typed on this entity found)_")
        lines.append("")

    lines.append("### Carried by Pub/Sub topics")
    lines.append("")
    schemas = event_index.get(c.canonical, [])
    if schemas:
        for s in schemas:
            lines.append(f"- [`{s['topic']}`](../../relations/event-schemas/{s['schema_path']}) — "
                         f"DTO `{s['dto_simple']}`")
        lines.append("")
    else:
        lines.append("_(no resolved Pub/Sub schemas reference this entity; "
                     "check `relations/event-schemas/` for unresolved canonical-dto fields)_")
        lines.append("")

    # Cross-references
    lines.append("## Cross-references")
    lines.append("")
    lines.append(f"- Owning service shadow: [`{owning}`](../../repos/{owning}.md)")
    for d in domains:
        if d != "unassigned":
            lines.append(f"- Domain rollup: [`{d}`](../{d}.md)")
    lines.append("- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)")
    lines.append("")

    return "\n".join(lines)


def render_catalog_md(clusters: list[Cluster],
                      repo_domains: dict[str, str],
                      top_n: int,
                      today: str) -> str:
    total = len(clusters)
    lines: list[str] = []
    lines.append("---")
    lines.append("name: entity-catalog")
    lines.append("description: Canonical business-entity index across the Java fleet. Cross-repo divergences captured.")
    lines.append("sources:")
    lines.append("  - ~/projects/codebase-map/relations/entity-catalog.raw.tsv (extractor output)")
    lines.append("  - ~/projects/codebase-map/relations/entity_aliases.yaml (hand-curated)")
    lines.append("  - ~/projects/codebase-map/repos/<repo>.md frontmatter (domain:)")
    lines.append("generator: ~/projects/codebase-map/scripts/cluster_entities.py")
    lines.append(f"last-generated-date: {today}")
    lines.append(f"total-entities: {total}")
    lines.append(f"top-n-pages: {top_n}")
    lines.append("scope-notes: |")
    lines.append("  v1: Java (Quarkus + Spring Boot + models-lib) only. No TS / Python / Node.")
    lines.append("  Detection is regex-based; captures persisted/serialized shape, not Java API surface.")
    lines.append("  Lombok @Data / @Builder classes are included as DTOs even without explicit @Entity.")
    lines.append("status: seed")
    lines.append("---")
    lines.append("")
    lines.append("# Cross-repo entity catalog")
    lines.append("")
    lines.append(f"One row per canonical business entity in the 73-repo Java fleet under "
                 f"`~/projects/ship-cars-usa/`. **Top {top_n}** by composite score "
                 f"(`occurrence + 2 * distinct-domain-count`) get a per-entity page under "
                 f"[`domains/entities/`](../domains/entities/); the rest are listed for completeness.")
    lines.append("")
    lines.append("Regenerated by `scripts/cluster_entities.py`. Do not hand-edit the table — "
                 "tighten `relations/entity_aliases.yaml` and re-run.")
    lines.append("")
    lines.append("## Index")
    lines.append("")
    lines.append("| Rank | Canonical | Aliases | Variants | Repos | Domains | Owning service | Page |")
    lines.append("|---:|---|---|---:|---:|---|---|---|")
    for i, c in enumerate(clusters, 1):
        aliases = ", ".join(sorted(c.aliases)[:6])
        if len(c.aliases) > 6:
            aliases += f", +{len(c.aliases)-6}"
        domains = sorted({repo_domains.get(r, "unassigned") for r in c.repos})
        domains_s = ", ".join(d for d in domains if d != "unassigned") or "—"
        owning = sorted(c.repos)[0]
        page = (f"[→](../domains/entities/{c.canonical}.md)" if i <= top_n else "—")
        lines.append(
            f"| {i} | `{c.canonical}` | {aliases} | "
            f"{len(c.rows)} | {len(c.repos)} | {domains_s} | "
            f"`{owning}` | {page} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_shadow_section(repo: str, rows: list[Row],
                          cluster_of: dict[tuple[str, str], str],
                          top_canonicals: set[str]) -> str:
    """Build the `## Entities` section body to inject into a shadow doc."""
    if not rows:
        return ""
    out_lines: list[str] = []
    out_lines.append(SHADOW_SECTION_BEGIN)
    out_lines.append("## Entities")
    out_lines.append("")
    out_lines.append("Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:")
    out_lines.append("")
    out_lines.append("| Class | Kind | Module | Catalog canonical |")
    out_lines.append("|---|---|---|---|")
    # Sort by kind (jpa first), then class name
    kind_order = {"jpa": 0, "embedded": 1, "dto": 2, "other": 3}
    for r in sorted(rows, key=lambda r: (kind_order.get(r.kind, 9), r.class_name)):
        cano = cluster_of.get((r.repo, r.class_name), "—")
        if cano in top_canonicals:
            cano_md = f"[{cano}](../domains/entities/{cano}.md)"
        else:
            cano_md = cano
        out_lines.append(f"| `{r.class_name}` | {r.kind} | `{r.module}` | {cano_md} |")
    out_lines.append(SHADOW_SECTION_END)
    return "\n".join(out_lines)


def update_shadow_doc(shadow_path: Path, section: str) -> str:
    """Idempotently replace (or append) the managed `## Entities` section.
    Returns: 'updated' | 'noop' | 'skipped (no shadow)'."""
    if not shadow_path.exists():
        return "skipped (no shadow)"
    text = shadow_path.read_text(errors="replace")
    # If markers exist, replace.
    if SHADOW_SECTION_BEGIN in text and SHADOW_SECTION_END in text:
        new = re.sub(
            re.escape(SHADOW_SECTION_BEGIN) + r".*?" + re.escape(SHADOW_SECTION_END),
            section,
            text,
            count=1,
            flags=re.DOTALL,
        )
    else:
        # Append at end, separated by a blank line.
        sep = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
        new = text + sep + "\n" + section + "\n"
    if new == text:
        return "noop"
    shadow_path.write_text(new)
    return "updated"


# --- main ------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--top", type=int, default=DEFAULT_TOP_N,
                   help=f"Number of top entities to render per-page (default {DEFAULT_TOP_N})")
    p.add_argument("--no-shadow-update", action="store_true",
                   help="Skip writing ## Entities sections into shadow docs")
    p.add_argument("--no-rest", action="store_true",
                   help="Skip REST + repository-method extraction (much faster)")
    args = p.parse_args()

    if not RAW_TSV.exists():
        print(f"ERROR: {RAW_TSV} not found. Run extract_entities.py first.", file=sys.stderr)
        return 2
    if not ALIAS_YAML.exists():
        print(f"ERROR: {ALIAS_YAML} not found.", file=sys.stderr)
        return 2

    canonical_map, splits = parse_alias_yaml(ALIAS_YAML.read_text())
    name_map = build_name_to_canonical(canonical_map)
    split_map = split_lookup(splits)
    print(f"loaded {sum(len(v) for v in canonical_map.values())} aliases under "
          f"{len(canonical_map)} canonicals; {len(splits)} split rules", file=sys.stderr)

    rows = parse_raw_tsv(RAW_TSV)
    print(f"loaded {len(rows)} extracted classes", file=sys.stderr)

    repo_domains = load_repo_domains()
    clusters = cluster_all(rows, name_map, split_map)
    print(f"clustered into {len(clusters)} canonical entities", file=sys.stderr)

    # event-schema cross-reference
    event_index = load_event_schema_index(name_map, split_map)
    print(f"resolved {sum(len(v) for v in event_index.values())} event-schema bindings "
          f"across {len(event_index)} canonicals", file=sys.stderr)

    # Sort by composite score.
    ranked = sorted(clusters.values(), key=lambda c: score(c, repo_domains), reverse=True)
    top_canonicals = {c.canonical for c in ranked[: args.top]}

    today = dt.date.today().isoformat()

    # Filter: skip degenerate canonicals with occurrence < 2 from the top pages
    # but keep them in the master index.
    # (Already handled by ranking; degenerates fall below top-N naturally.)

    # Per-entity pages — delete stale pages first (canonicals that dropped
    # out of the top-N or got merged via an alias change).
    ENTITIES_DIR.mkdir(parents=True, exist_ok=True)
    keep_paths = {ENTITIES_DIR / f"{c.canonical}.md" for c in ranked[: args.top]}
    keep_paths.add(ENTITIES_DIR / "_index.md")  # if it exists
    removed = 0
    for existing in ENTITIES_DIR.glob("*.md"):
        if existing not in keep_paths:
            existing.unlink()
            removed += 1
    if removed:
        print(f"removed {removed} stale per-entity pages", file=sys.stderr)
    if args.no_rest:
        # Monkey-patch the rest/repo lookups to no-ops for speed.
        global find_rest_endpoints, find_repo_methods
        _orig_rest = find_rest_endpoints
        _orig_repo = find_repo_methods
        find_rest_endpoints = lambda *a, **k: []   # type: ignore
        find_repo_methods = lambda *a, **k: []     # type: ignore
    written = 0
    for c in ranked[: args.top]:
        body = render_entity_page(c, repo_domains, event_index, today)
        out = ENTITIES_DIR / f"{c.canonical}.md"
        if not out.exists() or out.read_text() != body:
            out.write_text(body)
            written += 1
        print(f"  page: {c.canonical:30s} occ={c.occurrence:3d} repos={len(c.repos):3d}",
              file=sys.stderr)
    print(f"wrote {written} per-entity pages "
          f"({len(ranked[:args.top]) - written} unchanged)", file=sys.stderr)

    # Master index
    catalog_text = render_catalog_md(ranked, repo_domains, args.top, today)
    if not CATALOG_MD.exists() or CATALOG_MD.read_text() != catalog_text:
        CATALOG_MD.write_text(catalog_text)
        print(f"wrote {CATALOG_MD}", file=sys.stderr)
    else:
        print(f"{CATALOG_MD} unchanged", file=sys.stderr)

    # Unaliased report
    unaliased = []
    for c in ranked:
        # canonical wasn't created from alias YAML if its name doesn't appear
        # in canonical_map keys AND no alias mapped it there.
        if c.canonical not in canonical_map:
            unaliased.append(c)
    unaliased_signal = [c for c in unaliased if c.occurrence >= 3]
    lines = ["canonical\toccurrence\trepo_count\tsample_aliases\tsample_repos\n"]
    for c in sorted(unaliased_signal, key=lambda c: (-c.occurrence, c.canonical)):
        aliases = ",".join(sorted(c.aliases)[:5])
        repos = ",".join(sorted(c.repos)[:5])
        lines.append(f"{c.canonical}\t{c.occurrence}\t{len(c.repos)}\t{aliases}\t{repos}\n")
    UNALIASED_TSV.write_text("".join(lines))
    print(f"wrote {UNALIASED_TSV} ({len(unaliased_signal)} unaliased entities with occurrence ≥ 3)",
          file=sys.stderr)

    # Shadow-doc ## Entities sections
    if args.no_shadow_update:
        print("--no-shadow-update: skipping shadow updates", file=sys.stderr)
    else:
        # Build (repo, class_name) -> canonical lookup
        cluster_of: dict[tuple[str, str], str] = {}
        for c in clusters.values():
            for r in c.rows:
                cluster_of[(r.repo, r.class_name)] = c.canonical
        # Group rows by repo
        rows_by_repo: dict[str, list[Row]] = collections.defaultdict(list)
        for r in rows:
            rows_by_repo[r.repo].append(r)
        updated = 0
        noop = 0
        skipped = 0
        for repo, rrows in sorted(rows_by_repo.items()):
            section = render_shadow_section(repo, rrows, cluster_of, top_canonicals)
            if not section:
                continue
            result = update_shadow_doc(SHADOW_DIR / f"{repo}.md", section)
            if result == "updated":
                updated += 1
            elif result == "noop":
                noop += 1
            else:
                skipped += 1
        print(f"shadow docs: {updated} updated, {noop} noop, {skipped} skipped", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
