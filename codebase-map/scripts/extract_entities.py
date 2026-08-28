#!/usr/bin/env python3
"""
extract_entities.py — walk Java repos, find candidate business-entity classes,
emit one TSV row per class.

Usage:
    python3 extract_entities.py [--repo <name>] [--limit N]

Reads:
  - ~/projects/codebase-map/repos/*.md         (frontmatter — stack + status)
  - ~/projects/codebase-map/relations/infrastructure-triage.md (skip archive-candidates)
  - ~/projects/ship-cars-usa/<repo>/**/*.java  (source under src/main/java)
  - ~/projects/ship-cars-usa/models-lib/**/*.java (special pseudo-repo)

Writes:
  - ~/projects/codebase-map/relations/entity-catalog.raw.tsv
  - ~/projects/codebase-map/relations/entity-catalog.errors.log

Columns of the raw TSV:
    repo  module  file_path  class_name  kind  extends  table_or_path
        field_count  fields

`kind` is one of: jpa | dto | embedded | other
`fields` is `;`-joined `name:type` pairs. Collection inner types are kept with
a trailing `[]` marker.

Stdlib only. Adapted from regex patterns in `gen_event_schemas.py`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

HOME = Path.home()
PROJECTS_ROOT = HOME / "projects" / "ship-cars-usa"
MAP_ROOT = HOME / "projects" / "codebase-map"
SHADOW_DIR = MAP_ROOT / "repos"
TRIAGE_FILE = MAP_ROOT / "relations" / "infrastructure-triage.md"
RAW_TSV = MAP_ROOT / "relations" / "entity-catalog.raw.tsv"
ERR_LOG = MAP_ROOT / "relations" / "entity-catalog.errors.log"
MODELS_LIB = "models-lib"


# --- regexes (idioms borrowed from gen_event_schemas.py) ---------------------

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

JAVA_CLASS_RE = re.compile(
    r"^\s*(?P<mods>(?:public\s+|protected\s+|private\s+|final\s+|abstract\s+|"
    r"sealed\s+|non-sealed\s+|static\s+)*)"
    r"class\s+(?P<name>\w+)"
    r"(?:\s*<[^>]+>)?"
    r"(?:\s+extends\s+(?P<base>\w+)(?:\s*<[^>]+>)?)?",
    re.MULTILINE,
)
JAVA_RECORD_HEAD_RE = re.compile(
    r"^\s*(?:public\s+|protected\s+|private\s+|static\s+)*"
    r"record\s+(?P<name>\w+)\s*(?:<[^>]+>)?\s*\(",
    re.MULTILINE,
)
JAVA_FIELD_RE = re.compile(
    r"^\s*(?P<mods>(?:private|public|protected|final|static|transient|volatile)"
    r"(?:\s+(?:private|public|protected|final|static|transient|volatile))*)\s+"
    r"(?P<type>[\w.<>,?\s\[\]]+?)\s+(?P<name>\w+)\s*(?:=\s*[^;]+)?;",
    re.MULTILINE,
)
ENTITY_ANNO_RE = re.compile(r"^\s*@Entity\b", re.MULTILINE)
EMBEDDABLE_ANNO_RE = re.compile(r"^\s*@Embeddable\b", re.MULTILINE)
MAPPED_SUPERCLASS_ANNO_RE = re.compile(r"^\s*@MappedSuperclass\b", re.MULTILINE)
LOMBOK_DATA_RE = re.compile(r"^\s*@(?:Data|Value|Builder|Getter|Setter)\b", re.MULTILINE)
JSON_IGNORE_PROPS_RE = re.compile(r"@JsonIgnoreProperties\b")
TABLE_ANNO_RE = re.compile(r'@Table\s*\(\s*name\s*=\s*"([^"]+)"')
PATH_ANNO_RE = re.compile(r'@(?:Path|RequestMapping)\s*\(\s*"([^"]+)"')
PKG_RE = re.compile(r"^\s*package\s+([\w.]+)\s*;", re.MULTILINE)

DROP_NAME_RE = re.compile(
    r"^(?:BaseEntity|Base\w*Entity|Audit\w*|Versioned\w*|Abstract\w*|"
    r"\w*Test\w*|\w*Mock\w*|\w*Stub\w*|MapStruct\w*|"
    # Hibernate Envers + audit infrastructure
    r"RevisionInfo\w*|\w*RevisionEntity|EnversRevision\w*|"
    r"RevisionData|ActorContext|"
    # Spring Data / Quarkus pagination wrappers
    r"Page|PageDto|PageModel|PageUtils|Page[A-Z]\w+|"
    r"\w*PageDto|\w*PageModel|"
    # Framework config beans (these are wiring, not business data)
    r"RestConfig|OpenApiConfig|SwaggerConfig|"
    # Logging / metadata utility wrappers
    r"LogMeta|TimeMeta|TraceMeta|"
    # Common Pub/Sub envelope types — handled separately by the catalog
    r"MessageEnvelope|MessageObject|MessageObjectDto|PubSubMessage|"
    # Spring/Quarkus pagination / sort criteria
    r"PagingCriteria|SortCriteria|Paged|PagedResponse|"
    # Generic config beans (AppContext, AppConfig, InfraConfig are framework wiring)
    r"AppContext|AppConfig|InfraConfig|"
    # Generic error envelopes
    r"ErrorResponse|ErrorDto|ErrorResponseDto)$"
)
TEST_PATH_RE = re.compile(r"(/src/test/|/\.test\.|/testfixtures/|/test-fixtures/)")
GENERATED_PATH_RE = re.compile(r"(/generated-sources/|/target/|/build/|/db-migration/)")
TEST_ARTIFACT_RE = re.compile(r"-(?:test-commons|coverage-report|integration-tests|test-utils)$")

DTO_SUFFIX_RE = re.compile(r"(?:Dto|ReadDto|WriteDto|PubSubDto|EventDto|Response|Request)$")
ENTITY_SUFFIX_RE = re.compile(r"(?:Entity|DbEntity)$")

MAX_FILE_BYTES = 500_000


@dataclass
class ExtractedClass:
    repo: str
    module: str
    file_path: str
    class_name: str
    kind: str  # jpa | dto | embedded | other
    extends: str
    table_or_path: str
    fields: list[tuple[str, str]]  # (name, type)


# --- shadow-doc selection ---------------------------------------------------

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


def load_archive_candidates() -> set[str]:
    if not TRIAGE_FILE.exists():
        return set()
    text = TRIAGE_FILE.read_text(errors="replace")
    out: set[str] = set()
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        if "archive-candidate" not in line:
            continue
        m = re.search(r"\|\s*\[([\w.\-]+)\]\(", line)
        if m:
            out.add(m.group(1))
    return out


def select_java_repos() -> list[str]:
    archived = load_archive_candidates()
    repos: list[str] = []
    for shadow in sorted(SHADOW_DIR.glob("*.md")):
        if shadow.name.startswith("_"):
            continue
        fm = parse_frontmatter(shadow.read_text(errors="replace"))
        stack = fm.get("stack", "")
        if not stack.startswith("Java"):
            continue
        repo = shadow.stem
        if repo in archived:
            continue
        if not (PROJECTS_ROOT / repo).is_dir():
            continue
        repos.append(repo)
    # models-lib is the shared-DTO pseudo-repo; ensure it's included.
    if (PROJECTS_ROOT / MODELS_LIB).is_dir() and MODELS_LIB not in repos:
        repos.append(MODELS_LIB)
    return sorted(repos)


# --- per-file extraction -----------------------------------------------------

def find_module(repo_root: Path, file: Path) -> str:
    """Walk up from `file` to repo_root, return the topmost pom-owning dir name."""
    cur = file.parent
    last_module = ""
    while cur != repo_root and cur != cur.parent:
        if (cur / "pom.xml").exists():
            last_module = cur.name
        cur = cur.parent
    if not last_module:
        return repo_root.name
    return last_module


def iter_java_files(repo_root: Path):
    """Yield candidate .java paths under src/main/java, filtered cheaply."""
    for p in repo_root.rglob("*.java"):
        sp = str(p)
        if "/src/main/java/" not in sp:
            continue
        if TEST_PATH_RE.search(sp) or GENERATED_PATH_RE.search(sp):
            continue
        try:
            if p.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        yield p


def classify_kind(text: str, class_name: str, file_name: str, is_record: bool) -> str:
    if ENTITY_ANNO_RE.search(text):
        return "jpa"
    if EMBEDDABLE_ANNO_RE.search(text):
        return "embedded"
    has_dto_suffix = bool(DTO_SUFFIX_RE.search(class_name) or DTO_SUFFIX_RE.search(file_name.removesuffix(".java")))
    has_entity_suffix = bool(ENTITY_SUFFIX_RE.search(class_name) or ENTITY_SUFFIX_RE.search(file_name.removesuffix(".java")))
    has_lombok = bool(LOMBOK_DATA_RE.search(text))
    has_jackson = bool(JSON_IGNORE_PROPS_RE.search(text))
    if has_dto_suffix or (has_lombok and not has_entity_suffix) or has_jackson:
        return "dto"
    if is_record:
        # record types without entity annotations are treated as DTOs
        # (records are the modern Java DTO shape; rare in this fleet but
        # we explicitly support them per Plan).
        return "dto"
    if has_entity_suffix:
        return "other"  # *Entity.java but no @Entity — mapped superclass / base
    return ""  # skip — not interesting


def find_class_decl(text: str) -> tuple[str, str, bool] | None:
    """Return (class_name, base_class, is_record) for the first interesting type
    declaration in the file, or None."""
    # Prefer record if present (rare).
    rec = JAVA_RECORD_HEAD_RE.search(text)
    cls = JAVA_CLASS_RE.search(text)
    if rec and (not cls or rec.start() < cls.start()):
        return rec.group("name"), "", True
    if cls:
        mods = cls.group("mods") or ""
        # Skip abstract bases — they aren't entities we care about.
        if "abstract" in mods:
            return None
        return cls.group("name"), (cls.group("base") or ""), False
    return None


def extract_fields(text: str) -> list[tuple[str, str]]:
    """Return (name, type) pairs for non-static, non-transient fields whose
    declaration is not preceded by @JsonIgnore. Collection inner types are
    flattened to `Inner[]`."""
    out: list[tuple[str, str]] = []
    for m in JAVA_FIELD_RE.finditer(text):
        mods = m.group("mods")
        if "static" in mods or "transient" in mods:
            continue
        ftype = re.sub(r"\s+", " ", m.group("type")).strip()
        fname = m.group("name")
        # JAVA_FIELD_RE can match method-return-line false positives; heuristic
        # used in gen_event_schemas — field names start lowercase.
        if not fname or fname[:1].isupper():
            continue
        # Scan a small window above for @JsonIgnore.
        prefix = text[max(0, m.start() - 200):m.start()]
        # bound to the most recent ; or { so prior fields' annotations don't leak.
        last_break = max(prefix.rfind(";"), prefix.rfind("{"), prefix.rfind("}"))
        if last_break >= 0:
            prefix = prefix[last_break + 1:]
        if re.search(r"@JsonIgnore\b", prefix):
            continue
        out.append((fname, _flatten_type(ftype)))
    return out


def _flatten_type(t: str) -> str:
    """Reduce collection/optional wrappers to their inner type with []. Map
    becomes V[] (we lose the key — fine for v1 catalog signal)."""
    t = t.strip()
    # Strip @Nullable / @NotNull / @Valid annotations sometimes captured in type
    t = re.sub(r"@\w+(?:\([^)]*\))?\s+", "", t).strip()
    m = re.match(r"^(List|Set|Optional|Iterable|Collection)\s*<\s*(.+?)\s*>\s*$", t)
    if m:
        inner = _flatten_type(m.group(2))
        return f"{inner}[]"
    m = re.match(r"^Map\s*<\s*[^,]+,\s*(.+?)\s*>\s*$", t)
    if m:
        inner = _flatten_type(m.group(1))
        return f"{inner}[]"
    # Trim trailing whitespace inside generics
    return t


def parse_java_file(repo: str, repo_root: Path, file: Path) -> ExtractedClass | None:
    try:
        text = file.read_text(errors="replace")
    except Exception:
        return None
    decl = find_class_decl(text)
    if not decl:
        return None
    class_name, base, is_record = decl
    if DROP_NAME_RE.match(class_name):
        return None
    kind = classify_kind(text, class_name, file.name, is_record)
    if not kind:
        return None
    # Drop test-flavored modules by artifact name.
    module = find_module(repo_root, file)
    if TEST_ARTIFACT_RE.search(module):
        return None
    # @Table(name="x") or @Path("/y") if present.
    table = ""
    if kind == "jpa":
        tm = TABLE_ANNO_RE.search(text)
        if tm:
            table = tm.group(1)
    elif kind == "dto":
        pm = PATH_ANNO_RE.search(text)
        if pm:
            table = pm.group(1)
    fields = extract_fields(text)
    return ExtractedClass(
        repo=repo,
        module=module,
        file_path=str(file.relative_to(repo_root)),
        class_name=class_name,
        kind=kind,
        extends=base,
        table_or_path=table,
        fields=fields,
    )


def scan_repo(repo: str) -> tuple[list[ExtractedClass], list[str]]:
    repo_root = PROJECTS_ROOT / repo
    classes: list[ExtractedClass] = []
    errors: list[str] = []
    for f in iter_java_files(repo_root):
        try:
            ec = parse_java_file(repo, repo_root, f)
        except Exception as e:
            errors.append(f"{repo}\t{f}\t{type(e).__name__}: {e}")
            continue
        if ec:
            classes.append(ec)
    return classes, errors


# --- output ----------------------------------------------------------------

def format_row(ec: ExtractedClass) -> str:
    fields_str = ";".join(f"{n}:{t}" for n, t in ec.fields)
    return "\t".join([
        ec.repo, ec.module, ec.file_path, ec.class_name, ec.kind,
        ec.extends or "", ec.table_or_path or "",
        str(len(ec.fields)), fields_str,
    ])


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", help="Limit to a single repo (debug)")
    p.add_argument("--limit", type=int, help="Stop after N repos (debug)")
    args = p.parse_args()

    repos = select_java_repos()
    if args.repo:
        if args.repo not in repos:
            print(f"WARN: {args.repo} not in Java-repo set; running anyway", file=sys.stderr)
            repos = [args.repo]
        else:
            repos = [args.repo]
    if args.limit:
        repos = repos[: args.limit]

    print(f"scanning {len(repos)} Java repos…", file=sys.stderr)
    started = time.monotonic()
    all_classes: list[ExtractedClass] = []
    all_errors: list[str] = []
    for i, repo in enumerate(repos, 1):
        t0 = time.monotonic()
        classes, errors = scan_repo(repo)
        dt_ms = (time.monotonic() - t0) * 1000
        all_classes.extend(classes)
        all_errors.extend(errors)
        print(f"  [{i:3d}/{len(repos)}] {repo}: {len(classes):4d} classes, "
              f"{len(errors)} errors  ({dt_ms:.0f} ms)", file=sys.stderr)

    if not all_classes:
        print("ERROR: zero classes detected — extraction is broken", file=sys.stderr)
        return 2

    RAW_TSV.parent.mkdir(parents=True, exist_ok=True)
    header = "repo\tmodule\tfile_path\tclass_name\tkind\textends\ttable_or_path\tfield_count\tfields\n"
    with RAW_TSV.open("w") as out:
        out.write(header)
        for ec in all_classes:
            out.write(format_row(ec) + "\n")

    if all_errors:
        ERR_LOG.write_text("\n".join(all_errors) + "\n")
    elif ERR_LOG.exists():
        ERR_LOG.unlink()

    elapsed = time.monotonic() - started
    print(f"\nwrote {RAW_TSV} ({len(all_classes)} rows) in {elapsed:.1f}s", file=sys.stderr)
    if all_errors:
        print(f"wrote {ERR_LOG} ({len(all_errors)} errors)", file=sys.stderr)
    # Tally for sanity.
    by_kind: dict[str, int] = {}
    for ec in all_classes:
        by_kind[ec.kind] = by_kind.get(ec.kind, 0) + 1
    print(f"by kind: {by_kind}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
