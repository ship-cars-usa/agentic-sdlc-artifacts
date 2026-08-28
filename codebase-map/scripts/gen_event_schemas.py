#!/usr/bin/env python3
"""
gen_event_schemas.py — Tier 1.5 message-schema sidecar generator.

For each resolved topic in relations/event-catalog.md, find the consumer-side
DTO class, extract its field structure, and emit a per-topic markdown file at
relations/event-schemas/<topic>.md.

Usage:
    python3 gen_event_schemas.py [--dry-run] [--discover-only]

Three phases:
  1. DISCOVER — walk each consumer repo for Spring `*Consumer.java`
     (`fromPubSubMessage(..., X.class)`), Quarkus
     `PubSubConsumerBlocking<X>` impls, and Python Pydantic `BaseModel`
     listeners. Bind each consumer-file's DTO to a catalog topic via the
     subscription key / config-property near the call site.
  2. EXTRACT — open the DTO source file. Identify kind (Lombok @Data,
     Java record, Pydantic BaseModel, or unrecognized). Extract field list:
     name, type, JSON alias (from @JsonProperty), nullable hints. Recognize
     `EventDto<T>` envelopes from models-lib / quarkus-user-syncer; capture
     envelope fields + the parameter T's own DTO.
  3. EMIT — write one markdown file per resolved topic with frontmatter
     (topic, producers, consumers, canonical-dto, schema-source, ...) +
     a fields table. Nested DTOs that recur ≥2 times get their own file.

Stdlib only. Output read-only against ship-cars-usa/, writes only under
codebase-map/relations/event-schemas/.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECTS_ROOT = Path.home() / "projects" / "ship-cars-usa"
MAP_ROOT = Path.home() / "projects" / "codebase-map"
EVENT_CATALOG = MAP_ROOT / "relations" / "event-catalog.md"
OUTPUT_DIR = MAP_ROOT / "relations" / "event-schemas"

# Recognized output `schema-source` values:
#   lombok-data   — Java Lombok @Data / @Value class, fields extracted.
#   java-record   — Java record, components extracted.
#   pydantic      — Python Pydantic BaseModel, fields extracted.
#   partial       — DTO file found but unfamiliar kind; minimal extraction.
#   none          — no DTO discoverable (raw-dict consumer or unmatched topic).
SCHEMA_SOURCES = {"lombok-data", "java-record", "pydantic", "partial", "none"}


# ------------------------------ regexes --------------------------------------

# Spring consumer: messageConverter.fromPubSubMessage(msg, FooDto.class)
#               OR messageConverter.fromMessage(msg, FooDto.class)
SPRING_DTO_REF_RE = re.compile(
    r"\.from(?:PubSub)?Message\s*\(\s*[^,]+,\s*(?P<dto>[A-Z]\w+)\.class\s*\)"
)
# Spring subscription key: appConfig.getPubSub().getSubscriptions().get(AppConfig.PubSub.X_KEY)
SPRING_SUB_KEY_RE = re.compile(
    r"\.getSubscriptions\(\)\.get\s*\(\s*[\w.]*?(?P<key>[A-Z][A-Z0-9_]*)\s*\)"
)
# Quarkus listener type, multiple variants:
#  - PubSubConsumerBlocking<FooEventDto> (typed implementation)
#  - Class<FooDto> getMessageClass() (method-based DTO declaration)
#  - return FooDto.class; inside a getMessageClass body
QUARKUS_DTO_REF_RE = re.compile(
    r"\bPubSubConsumerBlocking\s*<\s*(?P<dto>[A-Z]\w+)\s*>"
)
QUARKUS_MSG_CLASS_RE = re.compile(
    r"\bClass\s*<\s*(?P<dto>[A-Z]\w+)\s*>\s+getMessageClass\b"
)
# Quarkus subscription / topic config property:
# @ConfigProperty(name = "my-svc.pubsub.foo-subscription-v2")
QUARKUS_CONFIG_PROP_RE = re.compile(
    r"@ConfigProperty\s*\(\s*name\s*=\s*\"(?P<key>[\w.\-]+)\""
)
# Quarkus @ConfigMapping accessor: pubSubConfig.ctmsSubscription()
# The camelCase method name maps to a kebab-case property key.
QUARKUS_CFG_METHOD_RE = re.compile(
    r"\bpubSubConfig\.(?P<method>[a-z]\w+)\(\s*\)"
)


def _camel_to_kebab(s: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "-", s).lower()


# ----- Producer-side patterns ------------------------------------------------
# Quarkus typed publisher method: `public void publishXxxMessage(<Type> message, ...)`
# paired with a `pubSubConfig.<camelCaseTopic>()` call somewhere in the method.
# The DTO is the parameter type; the topic is the camelCase method on the
# @ConfigMapping interface.
PRODUCER_QUARKUS_METHOD_RE = re.compile(
    r"public\s+void\s+(?P<method>publish\w+)\s*\("
    r"\s*(?:final\s+)?(?P<dto>[A-Z]\w+)\s+\w+",
    re.MULTILINE,
)
PRODUCER_QUARKUS_TOPIC_REF_RE = re.compile(
    r"pubSubConfig\.(?P<topic_method>[a-z]\w+)\(\s*\)"
)
# Spring outbox converter: `public <X> entityToDto(<Domain> entity)`.
# The DTO is X. Topic linkage is upstream (outbox dispatch) so we attach
# such DTOs only when caller specifies the producer repo + topic name.
SPRING_CONVERTER_METHOD_RE = re.compile(
    r"public\s+(?P<dto>[A-Z]\w+)\s+(?:entityToDto|toDto|convert)\s*\("
)
# Quarkus @Outgoing("topic-name") with a typed return method
QUARKUS_OUTGOING_RE = re.compile(
    r'@Outgoing\s*\(\s*"(?P<topic>[\w.\-]+)"\s*\)',
)
# Python publisher with topic literal: publisher.publish("topic-name", payload)
PY_PUBLISHER_RE = re.compile(
    r"\.publish\s*\(\s*['\"](?P<topic>[\w.\-]+)['\"]"
)
# Java import line: import com.foo.bar.Baz;
JAVA_IMPORT_RE = re.compile(r"^import\s+(?P<fqcn>[\w.]+\.[A-Z]\w+);", re.MULTILINE)
# Java class/record declaration. Captures optional `extends Base<T>` clause
# so we can walk the inheritance chain and merge envelope fields (e.g.
# MessageObjectDto extends MessageDto<Object> — MessageDto carries the
# envelope fields the leaf class doesn't redeclare).
JAVA_CLASS_RE = re.compile(
    r"\b(?:public\s+)?(?:final\s+)?(?:abstract\s+)?class\s+(?P<name>\w+)"
    r"(?:\s*<[^>]+>)?"
    r"(?:\s+extends\s+(?P<base>\w+)(?:\s*<(?P<base_args>[^>]+)>)?)?"
)
# Match only the "record <Name> (" prefix; the component list is captured
# separately via paren-balancing because annotations like @JsonProperty("x")
# contain unbalanced parens that defeat a naive [^)]* greedy match.
JAVA_RECORD_HEAD_RE = re.compile(
    r"\b(?:public\s+)?record\s+(?P<name>\w+)\s*(?:<[^>]+>)?\s*\("
)
# Lombok annotations that indicate a typed POJO with auto-generated accessors.
# @Data and @Value are the strongest signals; @Getter / @Setter / @Builder
# without @Data are common variants. Any of these means "JSON shape == fields".
LOMBOK_ANNOTATION_RE = re.compile(
    r"^\s*@(?:Data|Value|Getter|Setter|Builder)\b",
    re.MULTILINE,
)
# Jackson @JsonIgnoreProperties(ignoreUnknown = true)
JACKSON_IGN_UNKNOWN_RE = re.compile(r"@JsonIgnoreProperties\s*\(\s*ignoreUnknown\s*=\s*true")
# Lombok-class field declaration:
#   [annotations on prior lines]
#   private/public/protected [final] TYPE name [= ...];
# We capture name + type after stripping annotations.
JAVA_FIELD_RE = re.compile(
    r"^\s*(?P<mods>(?:private|public|protected|final|static|transient|volatile)"
    r"(?:\s+(?:private|public|protected|final|static|transient|volatile))*)\s+"
    r"(?P<type>[\w.<>,?\s\[\]]+?)\s+(?P<name>\w+)\s*(?:=\s*[^;]+)?;",
    re.MULTILINE,
)
# Jackson annotations attached to a field (on the line(s) above):
JSON_PROPERTY_RE = re.compile(r'@JsonProperty\s*\(\s*"(?P<alias>[^"]+)"\s*\)')
JSON_IGNORE_RE = re.compile(r"@JsonIgnore\b")
JSON_ALIAS_RE = re.compile(r'@JsonAlias\s*\(\s*\{?\s*"(?P<alias>[^"]+)"')
# Python Pydantic patterns
PY_IMPORT_RE = re.compile(r"^(?:from\s+(\S+)\s+import\s+(.+)|import\s+(\S+))", re.MULTILINE)
PY_CLASS_RE = re.compile(
    r"^class\s+(?P<name>\w+)\s*(?:\[[^\]]+\])?\s*"
    r"\(\s*(?P<bases>[^)]*?)\s*\)\s*:",
    re.MULTILINE,
)
PY_FIELD_RE = re.compile(
    r"^(?P<indent>\s+)(?P<name>[a-z_][a-z0-9_]*)\s*:\s*(?P<type>[^=\n]+?)"
    r"(?:\s*=\s*(?P<default>.+))?$",
    re.MULTILINE,
)

# Carrier-suite (mirrors gen_event_catalog.py) — used to tier-sort topics.
CARRIER_SUITE: frozenset[str] = frozenset({
    "platform-backend", "loadboard-backend", "posting-backend", "cube",
    "load-bookmark-backend", "load-bookmark-service", "saved-search-handler",
    "load-recommender", "ml-service-recommender", "negotiations-router",
    "trip-planner", "location-provider", "location-history-backend",
    "company-documents", "invoices", "command-executor",
    "integrators-data-bridge", "inventory-backend", "user-backend",
    "ctms-frontend", "loadboard-frontend", "trip-planner-frontend",
    "carrier-order-importer-frontend", "api-gateway",
})

# Extra roots where DTO source files may live (shared-models libraries).
# We try the consumer's own repo first, then these.
DTO_SEARCH_ROOTS = [
    "models-lib", "usermanagement-dtos", "notification-dtos", "load-bookmark-dtos",
    "quarkus-user-syncer", "spring-commons",
]

# Files that match consumer-side patterns.
JAVA_CONSUMER_GLOBS = ("*Consumer.java", "*Listener.java")
PY_LISTENER_GLOBS = (
    "*_listener.py", "*_subscriber.py",
    "*subscriber*.py", "*listener*.py",
)
# Files that match producer-side patterns. Scanned only when consumer-side
# binding fails or the catalog row has no listed consumers.
JAVA_PRODUCER_GLOBS = (
    "*MessagePublisher*.java", "*PublisherImpl.java", "*MessageSender*.java",
    "*PubSubConverter.java", "*PubSubPublisher*.java",
)
PY_PRODUCER_GLOBS = (
    "*_publisher.py", "*publisher*.py",
)


# ------------------------------ data model -----------------------------------

@dataclass
class CatalogRow:
    topic: str
    producers: list[str]
    consumers: list[str]
    tier: str
    status: str  # "resolved" | "symbolic" | "partial" | "unresolved"


@dataclass
class ConsumerHit:
    repo: str
    file: Path
    lang: str           # "java-spring" | "java-quarkus" | "python"
    dto_simple: str     # short class name (e.g. UserEventPubSubDto)
    subscription_key: str | None  # e.g. USER_STATE_KEY or load-recommender.pubsub.user-subscription-v2
    line: int


@dataclass
class FieldSpec:
    name: str
    type: str
    json_alias: str | None = None
    nullable: bool = False
    inherited_from: str | None = None  # simple name of base class if not declared on this DTO


@dataclass
class DtoSpec:
    fqcn: str | None
    file: Path | None
    kind: str  # one of SCHEMA_SOURCES
    fields: list[FieldSpec] = field(default_factory=list)
    ignores_unknown: bool = False
    base_class: str | None = None  # e.g. "EventDto<V2UserAccountPubSubDto>"
    nested_dtos: list[str] = field(default_factory=list)


# ------------------------------ catalog parser -------------------------------

CATALOG_ROW_RE = re.compile(
    r"^\|\s*(?P<topic>[^|]+?)\s*\|\s*(?P<producers>[^|]*?)\s*\|"
    r"\s*(?P<consumers>[^|]*?)\s*\|\s*(?P<tier>[^|]*?)\s*\|"
    r"\s*[^|]*?\s*\|\s*[^|]*?\s*\|\s*[^|]*?\s*\|"  # subs | schema-ver | schema-src
    r"\s*(?P<status>[^|]+?)\s*\|"
    r"\s*[^|]*?\s*\|\s*$"  # evidence
)


def _strip_md_topic(cell: str) -> str:
    """`foo-state` -> foo-state ; `${ENV_VAR}` kept verbatim; prose markers ignored."""
    cell = cell.strip()
    if cell.startswith("_(") and "_" in cell[2:]:
        return ""  # prose / unresolved marker
    if cell.startswith("`") and cell.endswith("`"):
        return cell[1:-1]
    return cell


def _parse_repo_list(cell: str) -> list[str]:
    cell = cell.strip()
    if cell == "—" or not cell:
        return []
    repos: list[str] = []
    for part in cell.split(","):
        part = part.strip().strip("`")
        if part:
            repos.append(part)
    return repos


def parse_catalog() -> list[CatalogRow]:
    if not EVENT_CATALOG.exists():
        return []
    rows: list[CatalogRow] = []
    for line in EVENT_CATALOG.read_text().splitlines():
        if not line.startswith("| "):
            continue
        m = CATALOG_ROW_RE.match(line)
        if not m:
            continue
        topic = _strip_md_topic(m.group("topic"))
        if not topic or topic.lower() == "topic":
            continue
        rows.append(CatalogRow(
            topic=topic,
            producers=_parse_repo_list(m.group("producers")),
            consumers=_parse_repo_list(m.group("consumers")),
            tier=m.group("tier").strip(),
            status=m.group("status").strip(),
        ))
    return rows


# ------------------------------ Phase 1: DISCOVER ----------------------------

_repo_scan_cache: dict[str, list[ConsumerHit]] = {}
_producer_scan_cache: dict[str, list[ConsumerHit]] = {}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except Exception:
        return ""


def _iter_files(repo: Path, java_globs: tuple[str, ...], py_globs: tuple[str, ...]) -> list[Path]:
    found: list[Path] = []
    for pat in java_globs:
        for f in repo.rglob(pat):
            sf = str(f)
            if "/target/" in sf or "/test/" in sf or "/it/" in sf or "/.git/" in sf:
                continue
            found.append(f)
    for pat in py_globs:
        for f in repo.rglob(pat):
            sf = str(f)
            if "/.venv/" in sf or "/venv/" in sf or "/site-packages/" in sf:
                continue
            found.append(f)
    return found


def _iter_consumer_files(repo: Path) -> list[Path]:
    return _iter_files(repo, JAVA_CONSUMER_GLOBS, PY_LISTENER_GLOBS)


def _iter_producer_files(repo: Path) -> list[Path]:
    return _iter_files(repo, JAVA_PRODUCER_GLOBS, PY_PRODUCER_GLOBS)


def scan_consumer_repo(repo_name: str) -> list[ConsumerHit]:
    """Return all (file, dto_simple, subscription_key) tuples discovered in a repo."""
    if repo_name in _repo_scan_cache:
        return _repo_scan_cache[repo_name]
    hits: list[ConsumerHit] = []
    repo = PROJECTS_ROOT / repo_name
    if not repo.is_dir():
        _repo_scan_cache[repo_name] = hits
        return hits

    for fpath in _iter_consumer_files(repo):
        text = _read_text(fpath)
        if not text:
            continue
        lang = "python" if fpath.suffix == ".py" else None
        if lang is None:
            # Java — decide spring vs quarkus by which patterns match.
            # A single file may handle multiple topics (e.g. LoadboardPubSubListener
            # consuming ctms-subscription + user-subscription + company-subscription).
            # Emit one ConsumerHit per subscription key found, sharing the DTO.
            spring_m = SPRING_DTO_REF_RE.search(text)
            quarkus_m = QUARKUS_DTO_REF_RE.search(text)
            if spring_m:
                lang = "java-spring"
                dto = spring_m.group("dto")
                line = text[:spring_m.start()].count("\n") + 1
                sub_keys = [m.group("key") for m in SPRING_SUB_KEY_RE.finditer(text)]
                if not sub_keys:
                    sub_keys = [None]  # type: ignore[list-item]
                for sk in sub_keys:
                    hits.append(ConsumerHit(
                        repo=repo_name, file=fpath, lang=lang,
                        dto_simple=dto, subscription_key=sk, line=line,
                    ))
            else:
                msg_class_m = QUARKUS_MSG_CLASS_RE.search(text)
                if quarkus_m or msg_class_m:
                    lang = "java-quarkus"
                    if quarkus_m:
                        dto = quarkus_m.group("dto")
                        line = text[:quarkus_m.start()].count("\n") + 1
                    else:
                        dto = msg_class_m.group("dto")
                        line = text[:msg_class_m.start()].count("\n") + 1
                    sub_keys: list[str | None] = [m.group("key")
                                                  for m in QUARKUS_CONFIG_PROP_RE.finditer(text)]
                    # @ConfigMapping accessor pattern: pubSubConfig.fooMethod()
                    for m in QUARKUS_CFG_METHOD_RE.finditer(text):
                        sub_keys.append(_camel_to_kebab(m.group("method")))
                    if not sub_keys:
                        sub_keys = [None]
                    seen: set[str | None] = set()
                    for sk in sub_keys:
                        if sk in seen:
                            continue
                        seen.add(sk)
                        hits.append(ConsumerHit(
                            repo=repo_name, file=fpath, lang=lang,
                            dto_simple=dto, subscription_key=sk, line=line,
                        ))
            continue
        # Python listener.
        # Heuristic: find Pydantic class names imported into the file. If
        # the file uses raw dicts (no Pydantic ref), we record a hit with
        # dto_simple="" so the topic can still be flagged as schema:none.
        py_class_hits = re.findall(
            r"from\s+\S+\s+import\s+([A-Z]\w+)", text)
        sub_key = None
        sub_m = re.search(r"os\.environ\.get\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]", text)
        if sub_m:
            sub_key = sub_m.group(1)
        pydantic_candidates = [n for n in py_class_hits
                               if n.endswith(("Message", "Event", "Dto", "Envelope", "Payload"))]
        if pydantic_candidates:
            hits.append(ConsumerHit(
                repo=repo_name, file=fpath, lang="python",
                dto_simple=pydantic_candidates[0],
                subscription_key=sub_key, line=1,
            ))
        else:
            hits.append(ConsumerHit(
                repo=repo_name, file=fpath, lang="python",
                dto_simple="", subscription_key=sub_key, line=1,
            ))

    _repo_scan_cache[repo_name] = hits
    return hits


def scan_producer_repo(repo_name: str) -> list[ConsumerHit]:
    """Discover producer-side (topic → DTO) hits.
       Returns ConsumerHit records with role implied = producer.
       Patterns:
         - Quarkus: `public void publishX(<DTO> message, ...)` + `pubSubConfig.<topic>()`
         - Quarkus @Outgoing("topic-name") on a method returning a DTO
         - Python: `publisher.publish("topic-name", <payload>)` near a typed model
         - Spring: `*PubSubConverter.java` with `public <DTO> entityToDto(...)`
       Topic linkage is best-effort; the producer DTO is the carryable value."""
    if repo_name in _producer_scan_cache:
        return _producer_scan_cache[repo_name]
    hits: list[ConsumerHit] = []
    repo = PROJECTS_ROOT / repo_name
    if not repo.is_dir():
        _producer_scan_cache[repo_name] = hits
        return hits

    for fpath in _iter_producer_files(repo):
        text = _read_text(fpath)
        if not text:
            continue
        if fpath.suffix == ".java":
            # Quarkus publisher: pair publishXxx(<dto>) with pubSubConfig.<X>()
            for m in PRODUCER_QUARKUS_METHOD_RE.finditer(text):
                dto = m.group("dto")
                if dto == "Object" or dto.endswith("Headers") or dto in ("String", "Map"):
                    continue
                method_name = m.group("method")
                body_start = m.end()
                body_end = min(body_start + 600, len(text))
                body = text[body_start:body_end]
                tref = PRODUCER_QUARKUS_TOPIC_REF_RE.search(body)
                topic_key = _camel_to_kebab(tref.group("topic_method")) if tref else None
                hits.append(ConsumerHit(
                    repo=repo_name, file=fpath, lang="java-quarkus",
                    dto_simple=dto, subscription_key=topic_key,
                    line=text[:m.start()].count("\n") + 1,
                ))
            # @Outgoing("topic") + return type extraction
            for m in QUARKUS_OUTGOING_RE.finditer(text):
                topic = m.group("topic")
                # Look at the next ~600 chars for `public <Type> <name>(`
                tail = text[m.end():m.end() + 600]
                rt_m = re.search(r"public\s+(?P<ret>[A-Z]\w+(?:<[\w<>,\s.]+>)?)\s+\w+\s*\(", tail)
                if rt_m:
                    dto = rt_m.group("ret").split("<")[0]
                    if dto in ("Multi", "Uni", "CompletionStage"):
                        # Reactive wrapper — unwrap by taking the first generic arg.
                        inner = re.search(r"<\s*([A-Z]\w+)", rt_m.group("ret"))
                        if inner:
                            dto = inner.group(1)
                    if dto not in ("Object", "String", "Void"):
                        hits.append(ConsumerHit(
                            repo=repo_name, file=fpath, lang="java-quarkus",
                            dto_simple=dto, subscription_key=topic,
                            line=text[:m.start()].count("\n") + 1,
                        ))
            # Spring outbox converters: each file ≈ one DTO. Topic linkage is
            # the producer repo + the V<N> prefix; record with no key so it
            # falls back to DTO-name matching.
            if fpath.name.endswith("PubSubConverter.java"):
                cm = SPRING_CONVERTER_METHOD_RE.search(text)
                if cm:
                    dto = cm.group("dto")
                    hits.append(ConsumerHit(
                        repo=repo_name, file=fpath, lang="java-spring",
                        dto_simple=dto, subscription_key=None,
                        line=text[:cm.start()].count("\n") + 1,
                    ))
        else:
            # Python publisher: take topic from .publish("topic", ...) call.
            for m in PY_PUBLISHER_RE.finditer(text):
                topic = m.group("topic")
                # No DTO extraction for Python publishers — payload is usually
                # a dict or Pydantic model whose type isn't visible at the call site.
                hits.append(ConsumerHit(
                    repo=repo_name, file=fpath, lang="python",
                    dto_simple="", subscription_key=topic,
                    line=text[:m.start()].count("\n") + 1,
                ))

    _producer_scan_cache[repo_name] = hits
    return hits


def _normalize_topic_key(s: str) -> str:
    """Normalize a topic string or subscription key for fuzzy matching.
       'USER_STATE_KEY' -> 'user-state'; 'load-recommender.pubsub.user-sub-v2'
       -> 'user-sub-v2'; 'user-state' -> 'user-state'."""
    s = s.lower()
    # Drop common prefixes/suffixes that vary.
    s = s.replace("_", "-")
    s = re.sub(r"\.pubsub\.", "/", s)
    if "/" in s:
        s = s.rsplit("/", 1)[1]
    for suffix in ("-key", "-topic", "-sub", "-subscription", "-events"):
        if s.endswith(suffix):
            s = s[: -len(suffix)]
            break
    return s


def match_topic_to_hit(topic: str, hits: list[ConsumerHit]) -> ConsumerHit | None:
    """Bind a catalog row's topic to one of the consumer-repo's discovered hits."""
    if not hits:
        return None
    topic_n = _normalize_topic_key(topic)
    best: tuple[int, ConsumerHit] | None = None
    for h in hits:
        score = 0
        if h.subscription_key:
            key_n = _normalize_topic_key(h.subscription_key)
            if key_n == topic_n:
                score = 100
            elif topic_n and topic_n in key_n:
                score = 60
            elif key_n and key_n in topic_n:
                score = 50
        # Secondary: DTO class name shares root with topic.
        if h.dto_simple:
            dto_low = h.dto_simple.lower()
            topic_root = topic_n.split("-")[0] if "-" in topic_n else topic_n
            if topic_root and topic_root in dto_low:
                score = max(score, 25)
        if score and (best is None or score > best[0]):
            best = (score, h)
    # Require an explicit subscription-key match (score >= 50). The
    # secondary-25 DTO-name match alone is too weak — it produced false
    # positives like binding `posting-state` to a `QuoteStateConsumer` just
    # because both contain "state". Topics whose subscription key isn't
    # extractable end up as schema:none — that's correct, not a regression.
    if best and best[0] >= 50:
        return best[1]
    return None


def _tokenize_topic(topic: str) -> list[str]:
    """Split a topic name like 'cube.search-posting-events' into lowercase
       word tokens for fuzzy DTO-name matching."""
    s = topic.lower()
    s = re.sub(r"[._\-]", " ", s)
    # Drop pure noise tokens that almost every topic has and would match anything.
    stop = {"topic", "subscription", "subs", "pubsub", "v", ""}
    return [t for t in s.split() if t and t not in stop]


def _tokenize_dto(simple_name: str) -> list[str]:
    """Split a Java class name like 'SearchPostingEventPubSubDto' into tokens."""
    parts = re.findall(r"[A-Z][a-z]+|V\d+|[A-Z]+(?=[A-Z][a-z]|$)|\d+", simple_name)
    out = [p.lower() for p in parts]
    # Drop the trailing 'Dto', 'PubSub' tokens — they're suffix noise.
    return [t for t in out if t not in {"dto", "pub", "sub", "pubsub"}]


def score_dto_against_topic(dto_simple: str, topic: str) -> int:
    """Return 0-100 score for how well a DTO class name matches a topic name."""
    topic_tokens = _tokenize_topic(topic)
    if not topic_tokens:
        return 0
    dto_tokens = _tokenize_dto(dto_simple)
    if not dto_tokens:
        return 0
    matched = 0
    for tt in topic_tokens:
        for dt in dto_tokens:
            # Match if one is prefix/suffix of the other (handles workflow~workflows).
            if tt == dt or tt.rstrip("s") == dt.rstrip("s") \
                    or (len(tt) >= 4 and len(dt) >= 4 and (tt in dt or dt in tt)):
                matched += 1
                break
    return int(100 * matched / len(topic_tokens))


DTO_CANDIDATE_GLOBS = (
    # Producer-side outgoing DTO conventions across the fleet:
    "**/*-dtos/**/pubsub/**/*PubSubDto.java",     # posting-dtos, notification-dtos
    "**/*-dtos/**/out/**/*PubSubDto.java",        # loadboard-backend api-dtos
    "**/*-dtos/**/*PubSubDto.java",               # usermanagement-dtos (v2/, v3/)
    "**/dtos/**/pubsub/**/*PubSubDto.java",
    "**/dtos/**/out/**/*PubSubDto.java",
    "**/dtos/**/out/**/*EventDto.java",
    "**/dtos/**/in/**/*PubSubDto.java",           # some consumers' DTOs live in in/
    "**/dtos/**/v*/**/*PubSubDto.java",
)

_producer_dto_cache: dict[str, list[Path]] = {}


def discover_producer_dto_candidates(repo_name: str) -> list[Path]:
    """Find typed *PubSubDto.java / *EventDto.java files in a producer repo's
       outgoing-DTO directories. Used as a fallback when consumer-side / typed-
       publisher discovery can't bind a topic to a DTO."""
    if repo_name in _producer_dto_cache:
        return _producer_dto_cache[repo_name]
    repo = PROJECTS_ROOT / repo_name
    out: list[Path] = []
    if not repo.is_dir():
        _producer_dto_cache[repo_name] = out
        return out
    seen: set[Path] = set()
    for pat in DTO_CANDIDATE_GLOBS:
        for cand in repo.glob(pat):
            sf = str(cand)
            if "/target/" in sf or "/test/" in sf or "/.git/" in sf:
                continue
            if cand not in seen:
                seen.add(cand)
                out.append(cand)
    _producer_dto_cache[repo_name] = out
    return out


def _count_token_matches(topic: str, dto_simple: str) -> int:
    """Number of distinct topic tokens that match a DTO token. Used to gate
       fuzzy binding — a single-token match (e.g. 'events') is too generic."""
    topic_tokens = _tokenize_topic(topic)
    dto_tokens = _tokenize_dto(dto_simple)
    matched = 0
    for tt in topic_tokens:
        for dt in dto_tokens:
            if tt == dt or tt.rstrip("s") == dt.rstrip("s") \
                    or (len(tt) >= 4 and len(dt) >= 4 and (tt in dt or dt in tt)):
                matched += 1
                break
    return matched


def match_topic_to_producer_dto(topic: str, repo_name: str) -> tuple[Path, int] | None:
    """Score each producer-DTO candidate against the topic and return the best
       match. Requires score >= 70 OR (score >= 50 AND ≥2 distinct topic
       tokens matched) — prevents single-token false positives like
       'loadboard-events-topic' binding to any `*Event*Dto`."""
    candidates = discover_producer_dto_candidates(repo_name)
    if not candidates:
        return None
    best: tuple[Path, int, int] | None = None  # (file, score, token_count)
    for cand in candidates:
        simple = cand.stem
        sc = score_dto_against_topic(simple, topic)
        tk = _count_token_matches(topic, simple)
        if best is None or sc > best[1]:
            best = (cand, sc, tk)
    if best is None:
        return None
    f, sc, tk = best
    if sc >= 70 or (sc >= 50 and tk >= 2):
        return (f, sc)
    return None


# ------------------------------ Phase 2: EXTRACT -----------------------------

def resolve_dto_fqcn(hit: ConsumerHit) -> str | None:
    """Resolve the simple DTO name to a fully-qualified class name via the
       consumer file's import statements."""
    if not hit.dto_simple:
        return None
    text = _read_text(hit.file)
    for m in JAVA_IMPORT_RE.finditer(text):
        fqcn = m.group("fqcn")
        if fqcn.rsplit(".", 1)[-1] == hit.dto_simple:
            return fqcn
    # Python: dto_simple may be importable from a sibling module.
    for m in PY_IMPORT_RE.finditer(text):
        mod, names, simple = m.groups()
        if names and hit.dto_simple in {n.strip() for n in names.split(",")}:
            return f"{mod}.{hit.dto_simple}" if mod else hit.dto_simple
        if simple and simple.endswith(f".{hit.dto_simple}"):
            return simple
    # If same-package class (no import) — look for class def in the same dir.
    return hit.dto_simple


def find_dto_file(fqcn: str, repo: str, lang: str) -> Path | None:
    """Locate the source file for a DTO. Search:
       1. The consumer's own repo.
       2. DTO_SEARCH_ROOTS sibling repos under PROJECTS_ROOT.
       3. Any path containing the FQCN's package as a directory chain."""
    simple = fqcn.rsplit(".", 1)[-1]
    if lang == "python":
        # Pydantic — fqcn looks like "schemas.pubsub.ContractMessage"
        if "." in fqcn:
            mod_path = fqcn.rsplit(".", 1)[0].replace(".", "/")
            for root in (PROJECTS_ROOT / repo,) + tuple(PROJECTS_ROOT / r for r in DTO_SEARCH_ROOTS):
                if not root.is_dir():
                    continue
                cand = root / "code" / f"{mod_path}.py"
                if cand.is_file():
                    return cand
                cand = root / f"{mod_path}.py"
                if cand.is_file():
                    return cand
        # Fallback: rg / find for class definition.
        for cand in (PROJECTS_ROOT / repo).rglob(f"*.py"):
            if "/site-packages/" in str(cand) or "/.venv/" in str(cand):
                continue
            txt = _read_text(cand)
            if re.search(rf"^class\s+{re.escape(simple)}\b", txt, re.MULTILINE):
                return cand
        return None
    # Java: look under consumer repo first, then dto-search roots, then all ship-cars-usa.
    pkg_path = fqcn.replace(".", "/")
    candidates_roots = [PROJECTS_ROOT / repo] + [PROJECTS_ROOT / r for r in DTO_SEARCH_ROOTS]
    for root in candidates_roots:
        if not root.is_dir():
            continue
        # Standard maven layout: src/main/java/<pkg>/<Simple>.java
        for sub in ("src/main/java", "runtime/src/main/java", "*/src/main/java"):
            for cand in root.glob(f"{sub}/{pkg_path}.java"):
                if cand.is_file():
                    return cand
    # Broader fallback: any .java file matching the simple name + the FQCN line.
    for cand in PROJECTS_ROOT.rglob(f"{simple}.java"):
        if "/target/" in str(cand):
            continue
        txt = _read_text(cand)
        if f"package {fqcn.rsplit('.', 1)[0]};" in txt:
            return cand
    return None


def _strip_annotations(line: str) -> str:
    return re.sub(r"@\w+(?:\([^)]*\))?\s*", "", line).strip()


def _resolve_base_class_file(text: str, base_simple: str, this_file: Path) -> Path | None:
    """Resolve the source file for an `extends Base` clause by walking the
       file's imports. Falls back to a same-package lookup, then a fleet-wide
       rglob if needed."""
    if not base_simple:
        return None
    # Import-based resolution
    for m in JAVA_IMPORT_RE.finditer(text):
        fqcn = m.group("fqcn")
        if fqcn.rsplit(".", 1)[-1] == base_simple:
            # Find the file from the FQCN.
            repo_guess = _file_repo(this_file)
            if repo_guess:
                hit = find_dto_file(fqcn, repo_guess, "java")
                if hit:
                    return hit
            # Last-resort: rglob the fleet.
            for cand in PROJECTS_ROOT.rglob(f"{base_simple}.java"):
                if "/target/" in str(cand) or "/test/" in str(cand):
                    continue
                pkg = fqcn.rsplit(".", 1)[0]
                if f"package {pkg};" in _read_text(cand):
                    return cand
            return None
    # Same-package fallback: scan adjacent files in the same directory.
    sibling = this_file.parent / f"{base_simple}.java"
    if sibling.is_file():
        return sibling
    return None


def _walk_inheritance(text: str, path: Path, depth: int = 0, max_depth: int = 3) -> list[FieldSpec]:
    """Return the merged field list from this class's parents, in declaration
       order. Each field gets `inherited_from` set to the base class simple
       name. Stops at depth `max_depth` or when no extends clause is found."""
    if depth >= max_depth:
        return []
    cls_m = JAVA_CLASS_RE.search(text)
    if not cls_m or not cls_m.group("base"):
        return []
    base = cls_m.group("base")
    # Skip non-Lombok-typical built-ins that won't have meaningful fields here.
    if base in {"Object", "Exception", "RuntimeException", "Throwable"}:
        return []
    base_file = _resolve_base_class_file(text, base, path)
    if not base_file:
        return []
    base_text = _read_text(base_file)
    if not base_text:
        return []
    # Recurse first so grandparent fields come before parent fields.
    inherited = _walk_inheritance(base_text, base_file, depth + 1, max_depth)
    own = _extract_java_fields(base_text)
    for f in own:
        if f.inherited_from is None:
            f.inherited_from = base
    return inherited + own


def parse_java_dto(path: Path) -> DtoSpec:
    text = _read_text(path)
    is_lombok = bool(LOMBOK_ANNOTATION_RE.search(text))
    ignores_unknown = bool(JACKSON_IGN_UNKNOWN_RE.search(text))

    # Java record?
    rec_m = JAVA_RECORD_HEAD_RE.search(text)
    if rec_m:
        # Walk from the opening paren to find the matching closing one.
        start = rec_m.end()
        depth = 1
        i = start
        in_str = False
        str_char = ""
        while i < len(text) and depth > 0:
            ch = text[i]
            if in_str:
                if ch == "\\" and i + 1 < len(text):
                    i += 2
                    continue
                if ch == str_char:
                    in_str = False
            else:
                if ch in '"\'':
                    in_str = True
                    str_char = ch
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        break
            i += 1
        components = text[start:i]

        # Look for an extends clause after the record header.
        ext_m = re.match(r"\s+extends\s+(?P<base>[\w<>,\s.]+?)(?:\s+implements\b|\s*\{|\s*$)",
                         text[i + 1:i + 200])
        rec_extends = ext_m.group("base").strip() if ext_m else None

        fields_list: list[FieldSpec] = []
        if components.strip():
            # Top-level comma split (respect <>, (), [], "" nesting).
            depth_g = 0
            depth_p = 0
            depth_b = 0
            in_str2 = False
            str_char2 = ""
            buf = ""
            parts: list[str] = []
            for ch in components:
                if in_str2:
                    if ch == "\\":
                        buf += ch
                        continue
                    if ch == str_char2:
                        in_str2 = False
                elif ch in '"\'':
                    in_str2 = True
                    str_char2 = ch
                elif ch == "<":
                    depth_g += 1
                elif ch == ">":
                    depth_g -= 1
                elif ch == "(":
                    depth_p += 1
                elif ch == ")":
                    depth_p -= 1
                elif ch == "[":
                    depth_b += 1
                elif ch == "]":
                    depth_b -= 1
                if ch == "," and depth_g == 0 and depth_p == 0 and depth_b == 0:
                    parts.append(buf.strip())
                    buf = ""
                else:
                    buf += ch
            if buf.strip():
                parts.append(buf.strip())

            for part in parts:
                # Strip leading annotations (capture @JsonProperty alias if present).
                part = re.sub(r"\s+", " ", part).strip()
                json_alias: str | None = None
                annot_re = re.compile(r"^@(\w+)\s*(?:\(([^)]*)\))?\s*")
                while True:
                    am = annot_re.match(part)
                    if not am:
                        break
                    ann_name = am.group(1)
                    ann_arg = am.group(2) or ""
                    if ann_name == "JsonProperty":
                        sm = re.search(r'"([^"]+)"', ann_arg)
                        if sm:
                            json_alias = sm.group(1)
                    part = part[am.end():].lstrip()
                bits = part.rsplit(" ", 1)
                if len(bits) == 2:
                    typ, nm = bits
                    fields_list.append(FieldSpec(
                        name=nm, type=typ.strip(), json_alias=json_alias))

        base = rec_extends
        inherited_fields: list[FieldSpec] = []
        if base:
            base_name = base.strip().split("<")[0].strip()
            base_file = _resolve_base_class_file(text, base_name, path)
            if base_file:
                base_text = _read_text(base_file)
                if base_text:
                    inherited_fields = _walk_inheritance(base_text, base_file, 0)
                    own_base = _extract_java_fields(base_text)
                    for f in own_base:
                        if f.inherited_from is None:
                            f.inherited_from = base_name
                    inherited_fields = inherited_fields + own_base
        return DtoSpec(
            fqcn=None, file=path, kind="java-record",
            fields=inherited_fields + fields_list,
            ignores_unknown=ignores_unknown,
            base_class=base.strip() if base else None,
        )

    # Class (Lombok @Data / @Value / @Getter / @Builder, or plain POJO).
    fields_list = _extract_java_fields(text)
    inherited_fields = _walk_inheritance(text, path, 0)
    cls_m = JAVA_CLASS_RE.search(text)
    base_class = None
    if cls_m and cls_m.group("base"):
        base_class = cls_m.group("base")
        if cls_m.group("base_args"):
            base_class = f"{base_class}<{cls_m.group('base_args')}>"

    return DtoSpec(
        fqcn=None, file=path,
        kind="lombok-data" if is_lombok else "partial",
        fields=inherited_fields + fields_list,
        ignores_unknown=ignores_unknown,
        base_class=base_class,
    )


def _extract_java_fields(text: str) -> list[FieldSpec]:
    """Extract Lombok-style fields with their preceding-line Jackson annotations."""
    lines = text.splitlines()
    out: list[FieldSpec] = []
    # Pre-scan all field positions.
    for m in JAVA_FIELD_RE.finditer(text):
        # Skip static fields (constants, not part of the data shape).
        if "static" in m.group("mods"):
            continue
        ftype = re.sub(r"\s+", " ", m.group("type")).strip()
        # Skip method-return-type false matches (heuristic: name shouldn't start uppercase).
        fname = m.group("name")
        if fname[:1].isupper():
            continue
        # Look at the annotations immediately above this field — bounded by
        # the previous semicolon or open-brace, so a prior field's
        # @JsonProperty doesn't leak forward.
        raw_prefix = text[max(0, m.start() - 400):m.start()]
        last_semi = max(raw_prefix.rfind(";"), raw_prefix.rfind("{"))
        prefix = raw_prefix[last_semi + 1:] if last_semi >= 0 else raw_prefix
        json_alias: str | None = None
        nullable = False
        skip = False
        prop_m = list(JSON_PROPERTY_RE.finditer(prefix))
        if prop_m:
            json_alias = prop_m[-1].group("alias")
        if JSON_IGNORE_RE.search(prefix):
            skip = True
        if skip:
            continue
        # Heuristic: Optional<T>, @Nullable, default null indicate nullable.
        if ftype.startswith("Optional<") or ftype.startswith("@Nullable") \
                or "@Nullable" in prefix:
            nullable = True
        out.append(FieldSpec(name=fname, type=ftype, json_alias=json_alias, nullable=nullable))
    return out


def parse_pydantic_dto(path: Path, target_class: str) -> DtoSpec:
    text = _read_text(path)
    # Find the class block.
    cls_m = None
    for m in PY_CLASS_RE.finditer(text):
        if m.group("name") == target_class:
            cls_m = m
            break
    if not cls_m:
        return DtoSpec(fqcn=None, file=path, kind="partial")
    bases = cls_m.group("bases")
    if "BaseModel" not in bases and "BaseSchema" not in bases \
            and "PubSubMessageData" not in bases:
        return DtoSpec(fqcn=None, file=path, kind="partial",
                       base_class=bases.strip())
    # Body extraction: indent-based.
    start = cls_m.end()
    rest = text[start:]
    # Find lines with the indent that match field syntax until a dedent.
    body_lines = []
    base_indent: int | None = None
    for line in rest.splitlines():
        if not line.strip():
            body_lines.append(line)
            continue
        cur_indent = len(line) - len(line.lstrip())
        if base_indent is None:
            base_indent = cur_indent
        if cur_indent < base_indent:
            break
        body_lines.append(line)
    body = "\n".join(body_lines)
    fields_list: list[FieldSpec] = []
    for fm in PY_FIELD_RE.finditer(body):
        nm = fm.group("name")
        if nm in ("model_config", "__doc__"):
            continue
        ftype = fm.group("type").strip()
        nullable = "| None" in ftype or "Optional[" in ftype
        default = fm.group("default")
        json_alias = None
        if default and "alias=" in default:
            am = re.search(r"alias\s*=\s*['\"]([^'\"]+)['\"]", default)
            if am:
                json_alias = am.group(1)
        fields_list.append(FieldSpec(name=nm, type=ftype, json_alias=json_alias, nullable=nullable))
    return DtoSpec(fqcn=None, file=path, kind="pydantic",
                   fields=fields_list, base_class=bases.strip())


# --------------- Type-to-JSON preview (recursive expansion) ------------------

JAVA_PRIMITIVE_MAP = {
    "String": "string",
    "UUID": "string (uuid)",
    "URI": "string (uri)",
    "URL": "string (url)",
    "Date": "string (iso-8601 datetime)",
    "Instant": "string (iso-8601 datetime)",
    "LocalDate": "string (iso-8601 date)",
    "LocalDateTime": "string (iso-8601 datetime)",
    "ZonedDateTime": "string (iso-8601 datetime)",
    "OffsetDateTime": "string (iso-8601 datetime)",
    "Duration": "string (iso-8601 duration)",
    "int": "integer",
    "Integer": "integer",
    "long": "integer (long)",
    "Long": "integer (long)",
    "short": "integer",
    "Short": "integer",
    "byte": "integer",
    "Byte": "integer",
    "float": "number",
    "Float": "number",
    "double": "number",
    "Double": "number",
    "BigDecimal": "number (decimal)",
    "BigInteger": "integer (big)",
    "boolean": "boolean",
    "Boolean": "boolean",
    "char": "string (char)",
    "Character": "string (char)",
    "Object": "any",
    "JsonNode": "any",
}

PY_PRIMITIVE_MAP = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "bytes": "string (base64)",
    "Decimal": "number (decimal)",
    "datetime": "string (iso-8601 datetime)",
    "date": "string (iso-8601 date)",
    "time": "string (iso-8601 time)",
    "UUID": "string (uuid)",
    "Any": "any",
    "None": "null",
    "NoneType": "null",
}


def _split_generic_args(arg_str: str) -> list[str]:
    """Split 'K, V' or 'String, Map<String, Object>' on top-level commas only."""
    parts: list[str] = []
    depth = 0
    buf = ""
    for ch in arg_str:
        if ch in "<[":
            depth += 1
        elif ch in ">]":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf.strip())
    return parts


# Fleet-wide DTO/enum index built lazily on first JSON expansion. Maps simple
# class name -> source file path. Used to resolve nested types like
# `V2UserAccountPubSubDto` or `WorkflowStatus` to their definitions.
_type_index: dict[str, Path] = {}
_type_index_built = False


def _build_type_index() -> None:
    global _type_index_built
    if _type_index_built:
        return
    skip_marker = "/target/"
    seen: dict[str, Path] = {}
    java_patterns = ("*Dto.java", "*Enum.java", "*Status.java", "*Type.java",
                     "*Event.java", "*Message.java", "*PubSub.java")
    for pat in java_patterns:
        for cand in PROJECTS_ROOT.rglob(pat):
            sf = str(cand)
            if skip_marker in sf or "/.git/" in sf:
                continue
            stem = cand.stem
            # Prefer non-test sources; first-write-wins for stable behavior.
            if stem not in seen or "/test/" in str(seen[stem]):
                seen[stem] = cand
    # Pydantic-style models
    for cand in PROJECTS_ROOT.rglob("*.py"):
        sf = str(cand)
        if "/.venv/" in sf or "/venv/" in sf or "/site-packages/" in sf:
            continue
        stem = cand.stem
        if stem.endswith(("_schema", "_schemas", "_model", "_models", "_dto",
                          "_dtos", "schema", "schemas", "model", "models")):
            # We don't have one-class-per-file in Python; index by filename.
            # The actual class name lookup will scan inside.
            if stem not in seen:
                seen[stem] = cand
    _type_index.update(seen)
    _type_index_built = True


def _find_type_file(simple_name: str) -> Path | None:
    _build_type_index()
    return _type_index.get(simple_name)


def _jsonify_type(
    type_str: str,
    depth: int = 0,
    visited: frozenset[str] = frozenset(),
    max_depth: int = 4,
) -> Any:
    """Convert a Java or Python type string to a JSON-like preview value.
       Returns a primitive string for leaf types, a list for arrays/sets,
       a dict for maps and nested objects."""
    type_str = type_str.strip()
    if not type_str:
        return "any"

    # Strip Optional[...] / Optional<...> / | None wrappers.
    if type_str.endswith(" | None"):
        return _jsonify_type(type_str[:-7].strip(), depth, visited, max_depth)
    m = re.match(r"^Optional\s*[<\[]\s*(.+?)\s*[>\]]$", type_str)
    if m:
        return _jsonify_type(m.group(1), depth, visited, max_depth)

    # Generic args: "Name<X, Y, Z>" → name='Name', args=['X','Y','Z']
    bare = type_str.split("<")[0].split("[")[0].strip()
    args: list[str] = []
    gen_m = re.match(r"^[\w.]+\s*[<\[](.+)[>\]]$", type_str)
    if gen_m:
        args = _split_generic_args(gen_m.group(1))

    # Collections → JSON arrays
    if bare in {"List", "Set", "Collection", "Iterable", "Queue", "Deque",
                "ArrayList", "LinkedList", "HashSet", "TreeSet",
                "list", "set", "tuple", "frozenset"}:
        inner = args[0] if args else "any"
        return [_jsonify_type(inner, depth, visited, max_depth)]

    # Maps / dicts → JSON objects with a placeholder key
    if bare in {"Map", "HashMap", "TreeMap", "LinkedHashMap", "dict", "Dict"}:
        if len(args) >= 2:
            key_type = _jsonify_type(args[0], depth, visited, max_depth)
            val_type = _jsonify_type(args[1], depth, visited, max_depth)
            return {f"<{key_type}>": val_type}
        return {"<string>": "any"}

    # Primitives
    if bare in JAVA_PRIMITIVE_MAP:
        return JAVA_PRIMITIVE_MAP[bare]
    if bare in PY_PRIMITIVE_MAP:
        return PY_PRIMITIVE_MAP[bare]

    # Generic placeholder like T, U, K, V (single uppercase letter).
    if len(bare) == 1 and bare.isupper():
        return f"<{bare}>"
    # Common Java generics convention: T1, K2, etc.
    if re.fullmatch(r"[A-Z]\d", bare):
        return f"<{bare}>"

    # Cycle protection
    if bare in visited:
        return f"<{bare} (cycle)>"
    if depth >= max_depth:
        return f"<{bare} (depth-cap)>"

    # Nested DTO / enum: resolve via the type index
    file = _find_type_file(bare)
    if not file:
        return f"<{bare}>"

    # Enum heuristic: if the file's source declares `enum`, extract values
    text = _read_text(file)
    if file.suffix == ".java":
        if re.search(rf"\bpublic\s+enum\s+{re.escape(bare)}\b", text):
            values = re.findall(r"^\s*([A-Z][A-Z0-9_]*)\s*[,;(]", text, re.MULTILINE)
            if values:
                # Filter out obvious non-enum-constant matches.
                values = [v for v in values if v not in ("CASE", "FILE", "BOOLEAN", "STRING")]
                return f"string (enum: {'|'.join(values[:8])}{'|...' if len(values) > 8 else ''})"
            return f"string (enum: <{bare}>)"
        # Class — parse and recurse
        nested = parse_java_dto(file)
    else:
        if re.search(rf"^class\s+{re.escape(bare)}\b.*\(.*Enum.*\)\s*:", text, re.MULTILINE):
            # Python enum
            values = re.findall(r"^\s*([A-Z][A-Z0-9_]*)\s*=", text, re.MULTILINE)
            if values:
                return f"string (enum: {'|'.join(values[:8])}{'|...' if len(values) > 8 else ''})"
        nested = parse_pydantic_dto(file, bare)
    if not nested or not nested.fields:
        return f"<{bare}>"

    next_visited = visited | {bare}
    out: dict[str, Any] = {}
    for f in nested.fields:
        key = f.json_alias if f.json_alias else f.name
        out[key] = _jsonify_type(f.type, depth + 1, next_visited, max_depth)
    return out


def build_json_preview(dto: DtoSpec) -> str:
    """Produce a pretty-printed JSON-shape preview of the topic's payload."""
    visited: frozenset[str] = frozenset()
    out: dict[str, Any] = {}
    for f in dto.fields:
        key = f.json_alias if f.json_alias else f.name
        out[key] = _jsonify_type(f.type, depth=0, visited=visited)
    return json.dumps(out, indent=2, ensure_ascii=False)


def parse_dto_file(path: Path, target_class: str) -> DtoSpec | None:
    if not path.is_file():
        return None
    if path.suffix == ".py":
        return parse_pydantic_dto(path, target_class)
    return parse_java_dto(path)


# ------------------------------ Phase 3: EMIT --------------------------------

def _md_repo_list(repos: list[str]) -> str:
    if not repos:
        return "—"
    return ", ".join(f"`{r}`" for r in repos)


def _md_type(t: str) -> str:
    return f"`{t}`"


def gather_candidate_dtos(row: CatalogRow) -> list[Path]:
    """Collect all *PubSubDto.java candidates from producers + consumers.
       Used to enrich both bound and unbound schema files."""
    seen: set[Path] = set()
    out: list[Path] = []
    for repo_name in row.producers + row.consumers:
        for cand in discover_producer_dto_candidates(repo_name):
            if cand not in seen:
                seen.add(cand)
                out.append(cand)
    return out


def emit_topic_md(row: CatalogRow, dto: DtoSpec | None, hit: ConsumerHit | None,
                  today: str) -> str:
    is_carrier = row.tier == "carrier"
    candidates = gather_candidate_dtos(row)
    if dto is None:
        # No canonical DTO bound. Still useful: surface candidate DTOs from
        # producer/consumer repos so the L3b authors have concrete files to
        # inspect (esp. for polymorphic outbox topics).
        evidence_lines: list[str] = []
        if hit:
            rel = hit.file.relative_to(PROJECTS_ROOT)
            evidence_lines.append(
                f"- Consumer/producer site: `{rel}:L{hit.line}` "
                f"(no typed DTO extractable — raw dict / `Object` parameter / custom dispatcher)"
            )
        else:
            evidence_lines.append(
                "- No code site bound to this topic by subscription key or "
                "DTO-name match — needs manual seeding."
            )

        cand_section = ""
        cand_kind = "none"
        if candidates:
            scored = sorted(
                ((score_dto_against_topic(c.stem, row.topic), c) for c in candidates),
                reverse=True,
            )[:30]
            lines = []
            for score, cand in scored:
                rel = cand.relative_to(PROJECTS_ROOT)
                marker = " ⭐ best match" if score >= 40 else ""
                lines.append(f"- [`{cand.stem}`](~/projects/ship-cars-usa/{rel}) — score {score}{marker}")
            cand_section = "\n## Candidate DTOs in producer/consumer repos\n\n" \
                + "These are typed DTO files in the producer/consumer repos that " \
                + "*could* be the payload for this topic. Sorted by name-match " \
                + "score against the topic. If a single one is canonical, flip " \
                + "this file to `schema-source: lombok-data` by hand and re-run.\n\n" \
                + "\n".join(lines) + "\n"
            cand_kind = "candidates"

        # Distinguish "schema by design: none" (Python raw-dict) from
        # "no binding found" (most cases).
        python_consumer = any(
            "platform-backend" == c or "ml-bot-order" in c or "ml-service-listener" in c
            for c in row.consumers
        )
        if python_consumer and not candidates:
            kind_label = "none-by-design"
            commentary = (
                "**No schema by design.** This topic is consumed by a Python "
                "service that parses the payload as a raw `dict` (e.g. "
                "`json.loads()` → `data['key']`), with no typed model. "
                "L3b will need a hand-authored schema based on the producer's "
                "outgoing payload shape."
            )
        elif candidates:
            kind_label = "candidates-only"
            commentary = (
                "**No single canonical DTO.** The topic carries one or more "
                "of the candidate DTOs listed below — likely an outbox-style "
                "polymorphic stream. L3b will likely need one contract *per "
                "DTO type* rather than one per topic."
            )
        else:
            kind_label = "none"
            commentary = (
                "**No typed DTO found.** Either the consumer uses raw dict / "
                "`JsonNode` access, the catalog has no listed consumers, or "
                "neither side's code matched the discovery patterns. "
                "Manual seed: read the producer/consumer code at the cited "
                "site and document the message shape here."
            )

        return f"""---
topic: {row.topic}
producers: [{', '.join(row.producers)}]
consumers: [{', '.join(row.consumers)}]
tier: {row.tier}
canonical-dto: ~
canonical-dto-file: ~
schema-source: none
candidate-dto-count: {len(candidates)}
binding: {kind_label}
shared-with-producer: ~
last-generated-date: {today}
status: stub
---

# Topic `{row.topic}` — schema

{commentary}

## Evidence
{chr(10).join(evidence_lines)}
- Topic registry row: [../event-catalog.md](../event-catalog.md)
{cand_section}
## Schema status: `none` (`{kind_label}`)
This file ships with `schema-source: none` and `status: stub`. The L3b
contract program will produce the canonical schema; this stub records the
gap and (when present) lists candidate DTOs to seed from.
"""
    rel_dto = dto.file.relative_to(PROJECTS_ROOT) if dto.file else None
    canonical_fqcn = dto.fqcn or _fqcn_from_path(dto.file) or "?"
    declared = sum(1 for f in dto.fields if not f.inherited_from)
    inherited = len(dto.fields) - declared
    summary = (
        f"**Total fields:** {len(dto.fields)}"
        + (f" ({inherited} inherited, {declared} declared)" if inherited else "")
    )
    if dto.fields:
        json_preview = build_json_preview(dto)
        fields_section = (
            f"## Payload shape (recursive JSON preview)\n\n{summary}\n\n"
            "Values are JSON type annotations (e.g. `\"string\"`, `\"integer\"`, "
            "`\"string (enum: A|B|C)\"`). Nested DTOs are expanded inline; "
            "arrays use a single-element list to show the item shape; maps use "
            "`{\"<key>\": <value>}`. Generic placeholders show as `<T>`. "
            "Cycle / depth-capped types show as `<TypeName (cycle)>` / "
            "`<TypeName (depth-cap)>`.\n\n"
            "```json\n" + json_preview + "\n```\n"
        )
    else:
        fields_section = (
            "## Payload shape\n\n_(no fields extracted — see DTO source)_\n"
        )

    base_note = ""
    if dto.base_class:
        base_note = f"\n**Base class / envelope:** `{dto.base_class}` " \
                    f"(see [event-envelope.md](./event-envelope.md) when applicable)\n"

    ign_note = ""
    if dto.ignores_unknown:
        ign_note = "\n**Forward-compatible:** consumer is annotated with " \
                   "`@JsonIgnoreProperties(ignoreUnknown = true)` — unknown JSON " \
                   "fields are silently dropped on deserialization."

    shared = _is_shared_with_producer(dto, row)
    return f"""---
topic: {row.topic}
producers: [{', '.join(row.producers)}]
consumers: [{', '.join(row.consumers)}]
tier: {row.tier}
canonical-dto: {canonical_fqcn}
canonical-dto-file: ~/projects/ship-cars-usa/{rel_dto if rel_dto else ''}
schema-source: {dto.kind}
shared-with-producer: {str(shared).lower()}
last-generated-date: {today}
status: stub
---

# Topic `{row.topic}` — schema

Canonical DTO: `{dto.fqcn or canonical_fqcn.rsplit('.', 1)[-1]}`
(consumer-side, from `{rel_dto}`)
{base_note}{ign_note}

{fields_section}

## Drift check
- **shared-with-producer:** `{str(shared).lower()}` —
  {"producer and consumer reference the same DTO class (no static drift detected)."
   if shared else
   "producer and consumer DTOs are in separate packages; L3b authors should compare shapes."}
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `{hit.file.relative_to(PROJECTS_ROOT)}:L{hit.line}`
- DTO source: `{rel_dto}`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
"""


def _is_shared_with_producer(dto: DtoSpec, row: CatalogRow) -> bool:
    """Heuristic: a DTO is shared producer↔consumer if its file lives in a
       repo distinct from both the producer and consumer, OR if any producer
       repo's source imports the same FQCN."""
    if not dto.file:
        return False
    file_repo = _file_repo(dto.file)
    if file_repo and file_repo not in row.consumers and file_repo in row.producers:
        return True
    if file_repo and file_repo not in row.consumers and file_repo not in row.producers:
        # Lives in a third repo (likely a shared *-dtos library) — shared.
        return True
    return False


def _file_repo(path: Path) -> str | None:
    try:
        rel = path.relative_to(PROJECTS_ROOT)
        return rel.parts[0] if rel.parts else None
    except ValueError:
        return None


def _fqcn_from_path(path: Path | None) -> str | None:
    """Derive the Java FQCN (or Python dotted module path) from a source file
       path by stripping the build-tool prefix and replacing slashes with dots."""
    if path is None:
        return None
    p = str(path)
    for marker in ("/src/main/java/", "/runtime/src/main/java/", "/services/src/main/java/"):
        if marker in p:
            after = p.split(marker, 1)[1]
            if after.endswith(".java"):
                return after[:-5].replace("/", ".")
    if p.endswith(".py"):
        # Strip the repo root and take the dotted module path.
        try:
            rel = path.relative_to(PROJECTS_ROOT)
            parts = rel.parts
            if "code" in parts:
                idx = parts.index("code")
                tail = parts[idx + 1:]
            else:
                tail = parts[1:]
            mod = ".".join(tail)
            if mod.endswith(".py"):
                mod = mod[:-3]
            return mod
        except ValueError:
            return None
    return None


def emit_index(specs: list[tuple[CatalogRow, DtoSpec | None]]) -> str:
    today = dt.date.today().isoformat()
    carrier = [(r, d) for r, d in specs if r.tier == "carrier"]
    fleet = [(r, d) for r, d in specs if r.tier != "carrier"]
    counts = defaultdict(int)
    for _r, d in specs:
        counts[d.kind if d else "none"] += 1

    def _row(r: CatalogRow, d: DtoSpec | None) -> str:
        kind = d.kind if d else "none"
        dto = f"`{Path(d.file).stem}`" if (d and d.file) else "—"
        return f"| [`{r.topic}`](./{r.topic}.md) | {kind} | {dto} | {r.tier} |"

    body = "\n".join(_row(r, d) for r, d in carrier + fleet)
    return f"""---
name: event-schemas-index
description: Per-topic schema files for the Ship.Cars Pub/Sub fleet (Tier 1.5 sidecar to event-catalog.md)
generator: ~/projects/codebase-map/scripts/gen_event_schemas.py
last-generated-date: {today}
total-topics: {len(specs)}
schema-source-counts:
  lombok-data: {counts['lombok-data']}
  java-record: {counts['java-record']}
  pydantic: {counts['pydantic']}
  partial: {counts['partial']}
  none: {counts['none']}
status: stub
---

# Event schemas — per-topic index

One markdown file per resolved topic in
[`../event-catalog.md`](../event-catalog.md). Each file captures the
**consumer-side** DTO that the topic's payload deserializes into, with field
names, types, JSON aliases (from `@JsonProperty`), and nullability hints.

**Why this exists**: the L3b contract program (per
`~/projects/carrier-test-strategy/CONTRACT-TESTING-PREREQUISITES.md`) is
going to author canonical machine-readable schemas. This sidecar captures
*what's there today* so the L3b authors have a concrete starting point rather
than a blank slate. **Not** a replacement for L3b contracts.

## Topic index

| Topic | Schema source | DTO | Tier |
|---|---|---|---|
{body}

## Schema-source legend
- **lombok-data** — Java Lombok `@Data` / `@Value` class. Fields extracted.
- **java-record** — Java record. Components extracted.
- **pydantic** — Python Pydantic `BaseModel`. Fields extracted.
- **partial** — DTO file found but not a recognized convention. Minimal extraction.
- **none** — no typed DTO found. Consumer uses raw dict / `JsonNode` access,
  or the consumer file couldn't be matched to this topic. Flagged as audit todo.

## Regenerate

```
python3 ~/projects/codebase-map/scripts/gen_event_schemas.py             # writes per-topic files + this index
python3 ~/projects/codebase-map/scripts/gen_event_schemas.py --dry-run   # preview to stdout (no writes)
python3 ~/projects/codebase-map/scripts/gen_event_schemas.py --discover-only
                                                                          # print (topic -> consumer file -> DTO) bindings only
```

## Status lifecycle

All files ship with `status: stub` on first generation. After a human review
pass against the source DTOs, flip individual frontmatter `status: stub` →
`status: seed`.
"""


# ------------------------------ driver ---------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true",
                   help="Print proposed outputs to stdout; do not write files.")
    p.add_argument("--discover-only", action="store_true",
                   help="Print Phase 1 discovery (topic -> consumer file -> DTO) and stop.")
    args = p.parse_args()

    catalog = parse_catalog()
    if not catalog:
        print(f"ERROR: no catalog rows at {EVENT_CATALOG}", file=sys.stderr)
        return 2
    resolved = [r for r in catalog if r.status == "resolved"]
    print(f"event-catalog: {len(catalog)} rows, {len(resolved)} resolved",
          file=sys.stderr)

    specs: list[tuple[CatalogRow, DtoSpec | None, ConsumerHit | None]] = []
    bound_count = 0
    for row in resolved:
        bound_hit: ConsumerHit | None = None
        dto: DtoSpec | None = None
        # 1) Consumer-side discovery (strongest signal).
        for repo_name in row.consumers:
            hits = scan_consumer_repo(repo_name)
            hit = match_topic_to_hit(row.topic, hits)
            if not hit:
                continue
            bound_hit = hit
            if hit.dto_simple:
                fqcn = resolve_dto_fqcn(hit)
                if fqcn:
                    dto_file = find_dto_file(fqcn, hit.repo, hit.lang)
                    if dto_file:
                        dto = parse_dto_file(dto_file, hit.dto_simple)
                        if dto:
                            dto.fqcn = fqcn
                            bound_count += 1
                            break
            break
        # 2) Producer-side fallback (typed publisher methods).
        if dto is None:
            for repo_name in row.producers:
                phits = scan_producer_repo(repo_name)
                phit = match_topic_to_hit(row.topic, phits)
                if not phit or not phit.dto_simple:
                    continue
                fqcn = resolve_dto_fqcn(phit)
                if not fqcn:
                    continue
                dto_file = find_dto_file(fqcn, phit.repo, phit.lang)
                if not dto_file:
                    continue
                p_dto = parse_dto_file(dto_file, phit.dto_simple)
                if not p_dto:
                    continue
                p_dto.fqcn = fqcn
                dto = p_dto
                bound_hit = phit
                bound_count += 1
                break
        # 3) Producer-convention fallback: scan producer repos' out/pubsub/
        # for *PubSubDto.java files and score by name against the topic.
        if dto is None:
            for repo_name in row.producers + row.consumers:
                m = match_topic_to_producer_dto(row.topic, repo_name)
                if not m:
                    continue
                dto_file, _score = m
                dto = parse_dto_file(dto_file, dto_file.stem)
                if dto:
                    dto.fqcn = _fqcn_from_path(dto_file)
                    # Synthesize a ConsumerHit for the evidence pointer.
                    bound_hit = ConsumerHit(
                        repo=repo_name, file=dto_file,
                        lang="java-quarkus" if dto_file.suffix == ".java" else "python",
                        dto_simple=dto_file.stem, subscription_key=None,
                        line=1,
                    )
                    bound_count += 1
                    break
        specs.append((row, dto, bound_hit))

    print(f"phase 1 bind: {bound_count} of {len(resolved)} topics have DTOs",
          file=sys.stderr)

    if args.discover_only:
        for row, dto, hit in specs:
            file = str(hit.file.relative_to(PROJECTS_ROOT)) if hit else "—"
            kind = dto.kind if dto else "none"
            print(f"  {row.topic:40}  {kind:12}  {file}")
        return 0

    today = dt.date.today().isoformat()
    if args.dry_run:
        for row, dto, hit in specs[:5]:
            print(f"\n----- {row.topic} -----\n")
            print(emit_topic_md(row, dto, hit, today))
        print(f"\n[dry-run] {len(specs)} topic files, "
              f"{bound_count} with extracted schemas. "
              f"(Sample of 5 shown.)", file=sys.stderr)
        return 0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for row, dto, hit in specs:
        path = OUTPUT_DIR / f"{row.topic}.md"
        # Skip topics whose name contains characters unsafe for filenames.
        if "/" in row.topic or row.topic.startswith("$"):
            continue
        path.write_text(emit_topic_md(row, dto, hit, today))
    index = OUTPUT_DIR / "_index.md"
    index.write_text(emit_index([(r, d) for r, d, _ in specs]))
    written = sum(1 for r, _, _ in specs if "/" not in r.topic and not r.topic.startswith("$"))
    print(f"wrote {written} per-topic files + _index.md to {OUTPUT_DIR}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
