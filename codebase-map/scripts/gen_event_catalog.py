#!/usr/bin/env python3
"""
gen_event_catalog.py — generate the Tier 1 topic registry from fleet sources.

Usage:
    python3 gen_event_catalog.py [--dry-run]

Phases:
  A. Parse ~/projects/codebase-map/relations/service-graph.md for Pub/Sub edges
     (the existing curated source — ~97 rows covering ~30 topics).
  B. Sweep all 232 repos under ~/projects/ship-cars-usa/ with `rg` for
     producer/consumer call sites not already captured in Phase A.
  C. Resolve topic names from each Phase-B repo's config files
     (application.properties bracket-keys; Python os.environ.get patterns).
  D. Emit one markdown table at ~/projects/codebase-map/relations/event-catalog.md
     with seven columns:
        Topic | Producer(s) | Consumer(s) | Tier | Subscription(s)
              | Schema version | Status | Evidence

Carrier-suite topics (any topic with >=1 carrier producer/consumer) sort first.
Schema version is a `—` placeholder until the Pact Broker stands up.

Stdlib only. Falls back to `git grep` if `rg` is absent.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

PROJECTS_ROOT = Path.home() / "projects" / "ship-cars-usa"
MAP_ROOT = Path.home() / "projects" / "codebase-map"
SERVICE_GRAPH = MAP_ROOT / "relations" / "service-graph.md"
OUTPUT = MAP_ROOT / "relations" / "event-catalog.md"
SUBSCRIPTIONS_TSV = MAP_ROOT / "relations" / "event-catalog.subscriptions.tsv"

# Carrier-suite scope (per ~/projects/carrier-test-strategy/README.md §1).
# Any topic with >=1 producer or consumer in this set is Tier=carrier.
CARRIER_SUITE: frozenset[str] = frozenset({
    "platform-backend",
    "loadboard-backend",
    "posting-backend",
    "cube",
    "load-bookmark-backend",
    "load-bookmark-service",
    "saved-search-handler",
    "load-recommender",
    "ml-service-recommender",
    "negotiations-router",
    "trip-planner",
    "location-provider",
    "location-history-backend",
    "company-documents",
    "invoices",
    "command-executor",
    "integrators-data-bridge",
    "inventory-backend",
    "user-backend",
    "ctms-frontend",
    "loadboard-frontend",
    "trip-planner-frontend",
    "carrier-order-importer-frontend",
    "api-gateway",
})

# Producer / consumer regexes. Validated against posting-backend (Spring,
# OutboxMessageService class — there is no @OutboxMessage annotation),
# user-backend (OutboxPoller), cube + load-recommender (Quarkus custom wrapper
# PubSubConsumerBlocking), metadata (PubSubPublisherSync), platform-backend
# (Python listeners).
PRODUCER_PATTERNS: list[tuple[str, str]] = [
    ("spring-outbox-service", r"\bOutboxMessageService\b"),
    ("outbox-poller",         r"\bOutboxPoller\b"),
    ("spring-template",       r"\bPubSubTemplate\b"),
    ("quarkus-custom-pub",    r"\bPubSubPublisher(?:Sync|Async)?\b"),
    ("reactive-outgoing",     r"@Outgoing\("),
    ("python-publisher",      r"\bpublisher\.publish\("),
]
CONSUMER_PATTERNS: list[tuple[str, str]] = [
    ("quarkus-listener",      r"@PubSubListener\b"),
    ("spring-base",           r"\bextends\s+PubSubConsumer\b"),
    ("quarkus-blocking",      r"\bimplements\s+PubSubConsumerBlocking\b"),
    ("reactive-incoming",     r"@Incoming\("),
    ("python-subscriber",     r"\bpubsub_v1\.SubscriberClient\("),
]

VALID_STATUS = {"resolved", "symbolic", "partial", "unresolved"}
PLACEHOLDER = "—"

# Library / boilerplate repos that *define* the publisher/listener classes
# rather than use them as a service. Excluded from Phase B because matching
# them is meaningless — they're tooling, not Pub/Sub participants.
LIBRARY_REPOS: frozenset[str] = frozenset({
    "spring-commons",
    "quarkus-pubsub",
    "quarkus-boilerplate-DEPRECATED",
    "quarkus-imperative-boilerplate",
    "quarkus-notification-client",
    "quarkus-user-syncer",
    "knowledge",
})


# ----------------------------- data model ------------------------------------

@dataclass
class Claim:
    """A producer or consumer claim against a topic (or symbolic placeholder)."""
    repo: str
    topic: str               # canonical name, ${SYMBOLIC}, or <unresolved-prose>
    role: str                # "produces" or "consumes"
    subscription: str | None = None
    status: str = "resolved"
    evidence: str = ""


@dataclass
class TopicRow:
    topic: str
    producers: set[str] = field(default_factory=set)
    consumers: set[str] = field(default_factory=set)
    subscriptions: set[str] = field(default_factory=set)
    statuses: set[str] = field(default_factory=set)
    evidence: list[str] = field(default_factory=list)

    @property
    def tier(self) -> str:
        if (self.producers | self.consumers) & CARRIER_SUITE:
            return "carrier"
        return "fleet"

    @property
    def best_status(self) -> str:
        # Worst-case status wins (resolved < partial < symbolic < unresolved).
        order = ["resolved", "partial", "symbolic", "unresolved"]
        for s in reversed(order):
            if s in self.statuses:
                return s
        return "resolved"


# ----------------------------- Phase A ---------------------------------------

# Match a row of the service-graph edge table that uses Pub/Sub as the protocol.
# Five columns: caller | callee | protocol | evidence | last-confirmed.
PUBSUB_ROW_RE = re.compile(
    r"^\|\s*(?P<caller>[^|]+?)\s*\|\s*(?P<callee>[^|]+?)\s*\|\s*Pub/Sub\s*\|\s*(?P<evidence>[^|]*?)\s*\|\s*[^|]*?\s*\|\s*$"
)
ROLE_RE = re.compile(r"\*\(\s*(?P<role>[^)]+?)\s*\)\*")
BACKTICK_TOPIC_RE = re.compile(r"`([^`]+)`")


def _classify_role(role_text: str) -> str | None:
    """Map the *(...)* annotation in the callee cell to "produces" or "consumes"."""
    r = role_text.lower()
    if "publishes" in r or "produces" in r:
        return "produces"
    if "consumes" in r:
        return "consumes"
    return None


def _strip_backticks(s: str) -> str:
    return s.strip().strip("`").strip()


def _load_repo_set() -> set[str]:
    """Return the set of known repo names (from codebase-map/repos/*.md filenames)
       so we can filter out backticked repo references that aren't topic names."""
    repos_dir = MAP_ROOT / "repos"
    if not repos_dir.is_dir():
        return set()
    return {p.stem for p in repos_dir.glob("*.md") if not p.name.startswith("_")}


_KNOWN_REPOS: set[str] = set()


def _is_plausible_topic(token: str) -> bool:
    """Topics look like kebab-case / snake-case / dotted identifiers, or ${SYMBOLIC}.
       Reject DTO class names (PascalCase), property templates ({...}, starts with
       'config.pubsub.'), evidence paths, and bare repo references."""
    t = token.strip()
    if not t:
        return False
    if t.startswith("${") and t.endswith("}"):
        return True
    if "{" in t or "}" in t:
        return False
    if t.startswith("config.pubsub.") or t.startswith("executor.pubsub."):
        return False
    if "/" in t or " " in t:
        return False
    # PascalCase DTO classes: starts uppercase, contains lowercase, no hyphens/dots.
    if t[0].isupper() and "-" not in t and "." not in t and "_" not in t:
        return False
    # Skip exact repo-name matches (these are library/service references, not topics).
    if t in _KNOWN_REPOS:
        return False
    return True


def phase_a_parse_service_graph() -> list[Claim]:
    """Read service-graph.md and yield producer/consumer claims for Pub/Sub edges."""
    if not SERVICE_GRAPH.exists():
        return []
    global _KNOWN_REPOS
    _KNOWN_REPOS = _load_repo_set()

    claims: list[Claim] = []
    with SERVICE_GRAPH.open() as fh:
        for lineno, raw in enumerate(fh, start=1):
            m = PUBSUB_ROW_RE.match(raw)
            if not m:
                continue
            caller_cell = m.group("caller")
            callee_cell = m.group("callee")

            repo = _strip_backticks(caller_cell.split(" ")[0])
            role_m = ROLE_RE.search(callee_cell)
            if not role_m:
                continue
            role = _classify_role(role_m.group("role"))
            if role is None:
                continue

            # CRITICAL: only extract backticked topics from the substring BEFORE
            # the role annotation `*(...)*`. Anything inside or after the role
            # tends to be a library reference, DTO class, or prose qualifier
            # (e.g. *(publishes via `quarkus-notification-client`)*).
            topic_segment = callee_cell[:role_m.start()]
            topic_tokens = BACKTICK_TOPIC_RE.findall(topic_segment)

            ev_pointer = f"service-graph.md:L{lineno}"
            kept_any = False
            if topic_tokens:
                for tok in topic_tokens:
                    # Split comma-separated topics inside a single cell.
                    for part in tok.split(","):
                        topic = part.strip()
                        if not _is_plausible_topic(topic):
                            continue
                        if topic == repo:
                            continue
                        symbolic = topic.startswith("${") and topic.endswith("}")
                        status = "symbolic" if symbolic else "resolved"
                        claims.append(Claim(
                            repo=repo, topic=topic, role=role,
                            status=status, evidence=ev_pointer,
                        ))
                        kept_any = True
            if not kept_any:
                # No clean topic in this row — keep as prose so a human can
                # re-resolve at seed time. Strip role annotation, Pub/Sub
                # suffix, and stray backticks from the descriptive text.
                prose = ROLE_RE.sub("", callee_cell).strip()
                prose = re.sub(r"\s+Pub/Sub( topic| subscription)?\s*$", "", prose).strip()
                prose = re.sub(r"\s+", " ", prose).strip(" `")
                if not prose:
                    continue
                claims.append(Claim(
                    repo=repo, topic=f"<prose:{prose}>", role=role,
                    status="unresolved", evidence=ev_pointer,
                ))
    return claims


# ----------------------------- Phase B ---------------------------------------

_RG_BIN: str | None = None


def _resolve_rg() -> str | None:
    """Find the rg binary. shutil.which doesn't see /opt/homebrew/bin from
       Python's subprocess by default — probe known locations explicitly."""
    global _RG_BIN
    if _RG_BIN is not None:
        return _RG_BIN or None
    candidates = ["rg", "/opt/homebrew/bin/rg", "/usr/local/bin/rg", "/usr/bin/rg"]
    for c in candidates:
        hit = shutil.which(c) if not c.startswith("/") else (c if Path(c).is_file() else None)
        if hit:
            _RG_BIN = hit
            return hit
    _RG_BIN = ""
    return None


def _rg_filelist(repo: Path, pattern: str) -> list[str]:
    """Return file paths (repo-relative) in `repo` that contain pattern.
       Uses `rg -l -e <pat>`; falls back to `git grep -P -l -e <pat>` (PCRE)
       so `\\b` word-boundaries still work."""
    rg = _resolve_rg()
    if rg:
        cmd = [rg, "-l", "--glob", "!**/target/**",
               "--glob", "!**/node_modules/**", "--glob", "!**/.git/**",
               "--glob", "!**/*.md", "--glob", "!**/CLAUDE.md",
               "-e", pattern, str(repo)]
    else:
        # git grep requires -P for PCRE word boundaries; falls back gracefully
        # if the repo isn't a git checkout (we don't care — print stderr is suppressed).
        cmd = ["git", "-C", str(repo), "grep", "--no-recurse-submodules",
               "-P", "-l", "-e", pattern]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
    if out.returncode not in (0, 1):  # 1 = no matches; both fine.
        return []
    lines = [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]
    # Normalize rg's absolute paths to repo-relative.
    rel: list[str] = []
    repo_str = str(repo)
    for ln in lines:
        if ln.startswith(repo_str + "/"):
            rel.append(ln[len(repo_str) + 1:])
        else:
            rel.append(ln)
    return rel


def phase_b_sweep(known_repos: set[str]) -> dict[str, dict[str, list[str]]]:
    """Sweep all repos under PROJECTS_ROOT and return:
         { repo_name: { "produces": [hit_paths], "consumes": [hit_paths] } }
       Skips repos already represented in Phase A's known_repos when the hit
       wouldn't add new information.
    """
    by_repo: dict[str, dict[str, list[str]]] = {}
    if not PROJECTS_ROOT.is_dir():
        return by_repo
    for repo_dir in sorted(PROJECTS_ROOT.iterdir()):
        if not repo_dir.is_dir() or repo_dir.name.startswith("."):
            continue
        if repo_dir.name in LIBRARY_REPOS:
            continue
        produces_hits: list[str] = []
        consumes_hits: list[str] = []
        for _label, pat in PRODUCER_PATTERNS:
            produces_hits.extend(_rg_filelist(repo_dir, pat))
        for _label, pat in CONSUMER_PATTERNS:
            consumes_hits.extend(_rg_filelist(repo_dir, pat))
        if not produces_hits and not consumes_hits:
            continue
        by_repo[repo_dir.name] = {
            "produces": sorted(set(produces_hits)),
            "consumes": sorted(set(consumes_hits)),
        }
    return by_repo


# ----------------------------- Phase C ---------------------------------------

# Spring: `config.pubsub.topics[<topic>]=...` and `.subscriptions[<topic>]=...`
SPRING_PUBSUB_RE = re.compile(
    r"^\s*config\.pubsub\.(?P<kind>topics|subscriptions)\[(?P<key>[^\]]+)\]\s*="
)
# Python: os.environ.get('FOO_TOPIC') / os.environ.get("FOO_SUBSCRIPTION")
PY_ENV_RE = re.compile(
    r"os\.environ\.get\(\s*['\"](?P<var>[A-Z][A-Z0-9_]*(?:_TOPIC|_SUBSCRIPTION))['\"]"
)


def _resolve_spring_config(repo: Path) -> dict[str, set[str]]:
    """Return {"topics": {keys...}, "subscriptions": {keys...}} from .properties files."""
    out: dict[str, set[str]] = {"topics": set(), "subscriptions": set()}
    for prop in repo.rglob("application*.properties"):
        if "/target/" in str(prop) or "/test/" in str(prop):
            continue
        try:
            text = prop.read_text(errors="replace")
        except Exception:
            continue
        for line in text.splitlines():
            m = SPRING_PUBSUB_RE.match(line)
            if m:
                out[m.group("kind")].add(m.group("key"))
    return out


def _resolve_python_env(repo: Path) -> dict[str, set[str]]:
    """Return {"topic_vars": {...}, "subscription_vars": {...}} from .py files."""
    out: dict[str, set[str]] = {"topic_vars": set(), "subscription_vars": set()}
    for py in repo.rglob("*.py"):
        if "/.venv/" in str(py) or "/venv/" in str(py) or "/site-packages/" in str(py):
            continue
        try:
            text = py.read_text(errors="replace")
        except Exception:
            continue
        for m in PY_ENV_RE.finditer(text):
            var = m.group("var")
            if var.endswith("_TOPIC"):
                out["topic_vars"].add(var)
            elif var.endswith("_SUBSCRIPTION"):
                out["subscription_vars"].add(var)
    return out


def load_schema_source_map() -> dict[str, str]:
    """Read frontmatter `schema-source` from each relations/event-schemas/<topic>.md
       so the catalog can show a 9th `Schema source` column. Returns
       {topic: schema-source} (e.g. lombok-data, java-record, pydantic, none)."""
    out: dict[str, str] = {}
    schemas_dir = MAP_ROOT / "relations" / "event-schemas"
    if not schemas_dir.is_dir():
        return out
    fm_re = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
    for md in schemas_dir.glob("*.md"):
        if md.name.startswith("_"):
            continue
        m = fm_re.match(md.read_text(errors="replace"))
        if not m:
            continue
        topic_match = re.search(r"^topic:\s*(.+)$", m.group(1), re.MULTILINE)
        source_match = re.search(r"^schema-source:\s*(.+)$", m.group(1), re.MULTILINE)
        if topic_match and source_match:
            out[topic_match.group(1).strip()] = source_match.group(1).strip()
    return out


def load_subscription_map() -> dict[str, str]:
    """Read event-catalog.subscriptions.tsv if present.
       Format: subscription_name<TAB>topic_name<TAB>source"""
    out: dict[str, str] = {}
    if not SUBSCRIPTIONS_TSV.exists():
        return out
    for line in SUBSCRIPTIONS_TSV.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            out[parts[0].strip()] = parts[1].strip()
    return out


def phase_c_resolve(
    b_hits: dict[str, dict[str, list[str]]],
    a_claims: list[Claim],
    sub_map: dict[str, str],
) -> list[Claim]:
    """For each Phase-B repo not already in Phase A, parse configs and emit claims."""
    a_repos = {c.repo for c in a_claims}
    extra: list[Claim] = []
    for repo, sides in sorted(b_hits.items()):
        if repo in a_repos:
            # Already represented in service-graph.md; trust Phase A.
            continue
        repo_dir = PROJECTS_ROOT / repo
        spring = _resolve_spring_config(repo_dir)
        python = _resolve_python_env(repo_dir)

        # Pick a representative evidence pointer for the repo.
        all_hits = sides.get("produces", []) + sides.get("consumes", [])
        ev = f"{repo}/{all_hits[0]}" if all_hits else repo

        # Spring resolution: bracket keys ARE the topic names.
        for kind, keys in (("topics", spring["topics"]), ("subscriptions", spring["subscriptions"])):
            for key in sorted(keys):
                # A topic-key implies the repo publishes to it; a subscription-key
                # implies it consumes. Cross-check with Phase B's side-hits where possible.
                if kind == "topics" and sides.get("produces"):
                    extra.append(Claim(repo=repo, topic=key, role="produces",
                                       status="resolved", evidence=ev))
                if kind == "subscriptions" and sides.get("consumes"):
                    extra.append(Claim(repo=repo, topic=key, role="consumes",
                                       status="resolved", evidence=ev))

        # Python resolution: env vars give symbolic names; reverse-lookup via TSV.
        for var in sorted(python["topic_vars"]):
            topic = sub_map.get(var) or sub_map.get(var.replace("_TOPIC", ""))
            if topic:
                extra.append(Claim(repo=repo, topic=topic, role="produces",
                                   status="resolved", evidence=ev))
            else:
                extra.append(Claim(repo=repo, topic=f"${{{var}}}", role="produces",
                                   status="symbolic", evidence=ev))
        for var in sorted(python["subscription_vars"]):
            topic = sub_map.get(var)
            if topic:
                extra.append(Claim(repo=repo, topic=topic, role="consumes",
                                   subscription=var, status="resolved", evidence=ev))
            else:
                # Symbolic — record env var as both topic placeholder and subscription.
                extra.append(Claim(repo=repo, topic=f"${{{var}}}", role="consumes",
                                   subscription=var, status="symbolic", evidence=ev))

        # If neither config style resolved anything but Phase B saw call sites,
        # record a partial claim so the repo still appears in the catalog.
        if not spring["topics"] and not spring["subscriptions"] \
                and not python["topic_vars"] and not python["subscription_vars"]:
            for role_side in ("produces", "consumes"):
                if sides.get(role_side):
                    extra.append(Claim(
                        repo=repo,
                        topic=f"<unresolved:{repo}>",
                        role=role_side,
                        status="partial",
                        evidence=ev,
                    ))
    return extra


# ----------------------------- Phase D ---------------------------------------

def build_topic_rows(claims: list[Claim]) -> list[TopicRow]:
    rows: dict[str, TopicRow] = {}
    for c in claims:
        row = rows.setdefault(c.topic, TopicRow(topic=c.topic))
        if c.role == "produces":
            row.producers.add(c.repo)
        elif c.role == "consumes":
            row.consumers.add(c.repo)
        if c.subscription:
            row.subscriptions.add(c.subscription)
        row.statuses.add(c.status)
        if c.evidence and c.evidence not in row.evidence:
            row.evidence.append(c.evidence)
    return list(rows.values())


def _fmt_repo_list(repos: set[str]) -> str:
    if not repos:
        return PLACEHOLDER
    return ", ".join(f"`{r}`" for r in sorted(repos))


def _fmt_topic(topic: str) -> str:
    if topic.startswith("<prose:"):
        return f"_(prose)_ {topic[len('<prose:'):-1]}"
    if topic.startswith("<unresolved:"):
        return f"_(unresolved)_ {topic[len('<unresolved:'):-1]}"
    if topic.startswith("${"):
        return f"`{topic}`"
    return f"`{topic}`"


def emit_markdown(rows: list[TopicRow], schema_sources: dict[str, str] | None = None) -> str:
    today = dt.date.today().isoformat()
    rows = sorted(rows, key=lambda r: (0 if r.tier == "carrier" else 1, r.topic.lower()))
    schema_sources = schema_sources or {}

    carrier_count = sum(1 for r in rows if r.tier == "carrier")
    fleet_count = len(rows) - carrier_count

    header = f"""---
name: event-catalog
description: Tier 1 topic registry per ~/projects/carrier-test-strategy/EVENT-AND-ENTITY-MAP-TIERS.md
sources:
  - ~/projects/codebase-map/relations/service-graph.md
  - ~/projects/ship-cars-usa/<each repo>/application.properties + listeners
generator: ~/projects/codebase-map/scripts/gen_event_catalog.py
last-generated-date: {today}
carrier-rows: {carrier_count}
fleet-rows: {fleet_count}
status: stub
---

# Tier 1 — Pub/Sub topic registry

One row per topic across the Ship.Cars fleet. **Carrier-suite topics** (any topic with
≥1 producer or consumer in the contract-program scope) sort first; **fleet** topics
follow. The `Schema version` column ships as `{PLACEHOLDER}` placeholders until the
Pact Broker stands up.

**Regenerated by** `~/projects/codebase-map/scripts/gen_event_catalog.py`. Do not
hand-edit rows; correct upstream sources (service-graph.md, repo configs, the
subscriptions TSV) and re-run.

**Status legend:**
- `resolved` — topic name confirmed from config or service-graph backticks.
- `symbolic` — topic identity is `${{ENV_VAR}}`; needs config lookup or TSV row.
- `partial` — repo produces/consumes Pub/Sub but topic name not extractable yet.
- `unresolved` — service-graph prose-only mention; needs human re-resolution.

| Topic | Producer(s) | Consumer(s) | Tier | Subscription(s) | Schema version | Schema source | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
"""

    body_lines: list[str] = []
    for r in rows:
        topic_cell = _fmt_topic(r.topic)
        producers = _fmt_repo_list(r.producers)
        consumers = _fmt_repo_list(r.consumers)
        subs = ", ".join(f"`{s}`" for s in sorted(r.subscriptions)) if r.subscriptions else ""
        evidence = r.evidence[0] if r.evidence else ""
        # 9th column: schema-source from relations/event-schemas/<topic>.md
        # (links to the per-topic schema file when available).
        topic_clean = r.topic.strip("`")
        if topic_clean in schema_sources:
            src = schema_sources[topic_clean]
            schema_cell = f"[`{src}`](event-schemas/{topic_clean}.md)"
        else:
            schema_cell = PLACEHOLDER
        body_lines.append(
            f"| {topic_cell} | {producers} | {consumers} | {r.tier} | "
            f"{subs} | {PLACEHOLDER} | {schema_cell} | {r.best_status} | {evidence} |"
        )

    footer = f"""

## Open issues

- **Integration owner unnamed.** The tier doc flags this as the day-1 risk for
  the catalog. Without a named owner (~10 % of one engineer's time), this file
  bit-rots within a quarter. Staffing decision — not solved by the generator.
- **Pact Broker not stood up.** All `Schema version` cells ship as `{PLACEHOLDER}`.
  Column stays for format stability.
- **Tier 2 and Tier 3 deliberately deferred** per the tier doc. Tier 2 ops columns
  (DLQ, retention, idempotency, volume) emerge during L3b/L3d contract work in
  weeks 2–4. Tier 3 entity model is months of work with multi-sponsor scope.

## How to regenerate

```
python3 ~/projects/codebase-map/scripts/gen_event_catalog.py            # writes this file
python3 ~/projects/codebase-map/scripts/gen_event_catalog.py --dry-run  # preview to stdout
python3 ~/projects/codebase-map/scripts/drift_check.py --event-catalog  # CI-style check
python3 ~/projects/codebase-map/scripts/verify_links.py                 # lint
```

To refresh the Python-listener subscription→topic mapping (one-time per change):

```
python3 ~/projects/codebase-map/scripts/refresh_subscription_map.py
```
"""
    return header + "\n".join(body_lines) + footer


# ----------------------------- driver ----------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true",
                   help="Print catalog to stdout; do not write the file.")
    args = p.parse_args()

    if not SERVICE_GRAPH.exists():
        print(f"ERROR: {SERVICE_GRAPH} not found", file=sys.stderr)
        return 2
    if not PROJECTS_ROOT.is_dir():
        print(f"ERROR: {PROJECTS_ROOT} not found", file=sys.stderr)
        return 2

    print(f"Phase A: parsing {SERVICE_GRAPH.name} ...", file=sys.stderr)
    a_claims = phase_a_parse_service_graph()
    print(f"  -> {len(a_claims)} claims from service-graph.md", file=sys.stderr)

    print(f"Phase B: sweeping {PROJECTS_ROOT} for Pub/Sub call sites ...", file=sys.stderr)
    b_hits = phase_b_sweep({c.repo for c in a_claims})
    print(f"  -> Pub/Sub-touching repos: {len(b_hits)}", file=sys.stderr)

    print("Phase C: resolving topic names from configs ...", file=sys.stderr)
    sub_map = load_subscription_map()
    c_claims = phase_c_resolve(b_hits, a_claims, sub_map)
    print(f"  -> {len(c_claims)} additional claims after config resolution"
          f" (subscription-map entries: {len(sub_map)})", file=sys.stderr)

    all_claims = a_claims + c_claims
    rows = build_topic_rows(all_claims)
    schema_sources = load_schema_source_map()
    if schema_sources:
        print(f"  -> {len(schema_sources)} schema-source rows linked from event-schemas/",
              file=sys.stderr)
    text = emit_markdown(rows, schema_sources)

    if args.dry_run:
        sys.stdout.write(text)
        print(f"\n[dry-run] {len(rows)} topics rendered "
              f"({sum(1 for r in rows if r.tier == 'carrier')} carrier).",
              file=sys.stderr)
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(text)
    print(f"wrote {OUTPUT} ({len(rows)} topics, "
          f"{sum(1 for r in rows if r.tier == 'carrier')} carrier)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
