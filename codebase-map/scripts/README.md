# `codebase-map/scripts/`

Thirteen Python 3 scripts. **Stdlib only** — no `pip install` needed (the
`gen_event_catalog.py`, `gen_event_schemas.py`, and `cluster_entities.py`
scripts optionally shell out to `rg` for speed and fall back to a Python
walk if `rg` isn't on PATH).

For the **entity catalog** specifically (`extract_entities.py`,
`cluster_entities.py`, `gen_entity_browser.py`, `gen_entity_graph.py`), the
full design reference — detection rules, canonicalization order, alias YAML
schema, noise filters, troubleshooting — lives in
[`../ENTITY_CATALOG.md`](../ENTITY_CATALOG.md). The sections below are the
operational summary.

## `bootstrap_repo_md.py`

Generate a stub shadow doc for one repo.

```bash
python3 ~/projects/codebase-map/scripts/bootstrap_repo_md.py <repo-name>
python3 ~/projects/codebase-map/scripts/bootstrap_repo_md.py <repo-name> --force   # overwrite
```

What it does:
- Reads `~/projects/ship-cars-usa/<repo>/` to detect stack (Quarkus / Spring / Node / Python / Go / Terraform / unknown).
- Counts `pom.xml` files to detect single-module vs. multi-module.
- Captures `git rev-parse HEAD` as `last-synced-commit`.
- Writes `~/projects/codebase-map/repos/<repo>.md` with `status: stub`.

What it does **not** do:
- It does not fill in domain, maintainer, key abstractions, gotchas, or call-graph relations. Those need a human (or a deeper Claude pass) — the stub is a starting point.

## `drift_check.py`

Compare each shadow's `last-synced-commit` to the repo's current git HEAD,
or diff a freshly regenerated event-catalog against the committed copy.

```bash
python3 ~/projects/codebase-map/scripts/drift_check.py <repo-name>
python3 ~/projects/codebase-map/scripts/drift_check.py --all
python3 ~/projects/codebase-map/scripts/drift_check.py --all --mark-stale
python3 ~/projects/codebase-map/scripts/drift_check.py --event-catalog
python3 ~/projects/codebase-map/scripts/drift_check.py --event-schemas
```

`--mark-stale` rewrites `status: stale` in the frontmatter when drift is found, so `_index.md` and humans can see at a glance which shadows need re-syncing.

`--event-catalog` reruns `gen_event_catalog.py --dry-run`, normalizes the
`last-generated-date` field, and diffs against the committed
`relations/event-catalog.md`. Use this in CI to catch fleet drift between
weekly regenerations.

`--event-schemas` regenerates each per-topic schema file under
`relations/event-schemas/` and reports drift (changed / new / removed files).
The `last-generated-date` field is normalized so timestamp churn doesn't
trigger a false drift.

Exit codes: `0` clean, `1` drift detected, `2` invocation error.

## `gen_event_catalog.py`

Generate the Tier 1 Pub/Sub topic registry at `relations/event-catalog.md`.
See `~/projects/carrier-test-strategy/EVENT-AND-ENTITY-MAP-TIERS.md` for the
spec.

```bash
python3 ~/projects/codebase-map/scripts/gen_event_catalog.py            # writes the file
python3 ~/projects/codebase-map/scripts/gen_event_catalog.py --dry-run  # preview to stdout
```

Four-phase pipeline:

1. **Phase A** — parse `relations/service-graph.md` for already-curated Pub/Sub edges.
2. **Phase B** — `rg`-sweep all 232 repos under `ship-cars-usa/` for producer
   and consumer call sites not already in Phase A. Excludes library/boilerplate
   repos (`spring-commons`, `quarkus-pubsub`, etc.) that *define* the publisher
   classes rather than use them.
3. **Phase C** — resolve topic names from `application.properties` bracket-keys
   (Spring) and `os.environ.get('*_TOPIC' | '*_SUBSCRIPTION')` patterns (Python).
4. **Phase D** — emit the 8-column registry, carrier-suite topics first.

Python services that only expose subscription names need a static
subscription→topic lookup at `relations/event-catalog.subscriptions.tsv`.
Until that's populated, affected rows ship as `Status: symbolic`.

## `gen_event_schemas.py`

Generate the Tier 1.5 per-topic message-schema sidecar at
`relations/event-schemas/<topic>.md`. For each resolved topic in
`event-catalog.md`, finds the consumer-side DTO class and extracts its
field structure.

```bash
python3 ~/projects/codebase-map/scripts/gen_event_schemas.py
python3 ~/projects/codebase-map/scripts/gen_event_schemas.py --dry-run
python3 ~/projects/codebase-map/scripts/gen_event_schemas.py --discover-only
```

Three phases:

1. **Discover** — walk each consumer repo for Spring `*Consumer.java`
   (`fromPubSubMessage(..., X.class)`), Quarkus
   `PubSubConsumerBlocking<X>` impls or `Class<X> getMessageClass()` /
   `pubSubConfig.fooMethod()`, and Python Pydantic `BaseModel` listeners.
   Bind each consumer-file's DTO to a catalog topic via the subscription
   key / config property near the call site.
2. **Extract** — open the DTO source file. Detect kind (Lombok `@Data`,
   Java record, Pydantic `BaseModel`, or unrecognized). Extract field
   list: name, type, JSON alias (from `@JsonProperty`), nullability hints.
3. **Emit** — one markdown file per topic with frontmatter (`topic`,
   `producers`, `consumers`, `canonical-dto`, `schema-source`, ...) and a
   fields table.

**Out of scope** (deliberately):

- Producer↔consumer field-by-field diff (type-level `shared-with-producer`
  is in scope; full diff is L3b authoring work).
- Nested expansion past depth 1.
- JSON Schema emission — that's the L3b contract program's deliverable;
  this sidecar feeds it but does not replace it.
- Raw-dict Python schema inference (e.g. `platform-backend` listeners) —
  flagged as `schema-source: none` with a pointer to the listener file.

`gen_event_catalog.py` automatically reads `event-schemas/<topic>.md`
frontmatter to populate the `Schema source` column in `event-catalog.md`.

## `gen_schema_browser.py`

Bundle all `relations/event-schemas/*.md` files into a single self-contained
HTML browser at `relations/event-schemas/browser.html`. Double-click the file
to open it — no local server needed.

```bash
python3 ~/projects/codebase-map/scripts/gen_schema_browser.py
```

Features:

- Sidebar with filterable topic list (search, tier chips, schema-source chips).
- Color-coded badges for `lombok-data` / `java-record` / `pydantic` /
  `partial` / `none`.
- Click a topic to render its markdown (tables, code blocks, links) in the
  main pane via marked.js loaded from CDN. URL hash updates so a specific
  topic is shareable as `browser.html#user-state`.
- All schema content embedded as JSON in the file itself — works offline
  except for the marked.js CDN load on first open.

Regenerate after running `gen_event_schemas.py` so the browser stays in sync.

## `extract_entities.py`

Walk every Java repo whose shadow doc has `stack: Java/*` (plus `models-lib`
as a shared-DTO pseudo-repo) and emit one row per declared business-entity
class to `relations/entity-catalog.raw.tsv`.

```bash
python3 ~/projects/codebase-map/scripts/extract_entities.py
python3 ~/projects/codebase-map/scripts/extract_entities.py --repo loadboard-backend  # debug
python3 ~/projects/codebase-map/scripts/extract_entities.py --limit 5                  # debug
```

What it captures: `@Entity`, `@Embeddable`, Lombok-annotated DTOs
(`@Data`/`@Builder`/`@Value`), Jackson-annotated DTOs, and Java records.
Field names + flattened types (with `[]` markers for collection-ness) are
emitted in the `fields` column as `;`-joined `name:type` pairs.

What it filters: test fixtures, generated sources, abstract base classes,
Hibernate Envers infrastructure, pagination wrappers, framework config beans,
Pub/Sub envelopes. See `ENTITY_CATALOG.md` for the complete blocklist.

Runs in ~2 s over the ~73 Java repos in the fleet. Zero parse errors expected;
any per-file failures are logged to `relations/entity-catalog.errors.log` and
the run continues.

## `cluster_entities.py`

Normalize the per-class TSV into canonical buckets, score them, render the
master index + top-25 per-entity pages + `## Entities` rollups in each Java
shadow doc.

```bash
python3 ~/projects/codebase-map/scripts/cluster_entities.py
python3 ~/projects/codebase-map/scripts/cluster_entities.py --top 30           # change top-N
python3 ~/projects/codebase-map/scripts/cluster_entities.py --no-shadow-update # skip shadow edits
python3 ~/projects/codebase-map/scripts/cluster_entities.py --no-rest          # skip REST/repo scan (faster)
```

Inputs: `relations/entity-catalog.raw.tsv`, `relations/entity_aliases.yaml`,
shadow-doc `domain:` frontmatter, `relations/event-schemas/*.md` for
canonical-dto cross-references.

Outputs:
- `relations/entity-catalog.md` — full ranked index
- `domains/entities/<Canonical>.md` × top-N — per-entity pages with variants,
  field union/intersection, REST surface, repository methods, Pub/Sub topics
- `relations/entity-catalog.unaliased.tsv` — review side-channel (canonicals
  with occurrence ≥3 that didn't match any alias)
- `## Entities` section injected into each Java shadow doc that has detected
  entities, bounded by `<!-- entities-begin -->` / `<!-- entities-end -->`
  markers (idempotent on re-run)

Validation: fails fast if `entity_aliases.yaml` lists the same name under
two `canonical:` keys (the one config bug that produces silent wrong
answers).

## `gen_entity_browser.py`

Bundle the catalog + all per-entity pages into a single self-contained HTML
browser at `domains/entities/browser.html`. Double-click to open — no local
server needed.

```bash
python3 ~/projects/codebase-map/scripts/gen_entity_browser.py
```

Features:
- Sidebar list of all canonicals (not just top-25), sorted by composite score.
- Search by name, alias, or owning repo.
- Filter chips: scope (Top-25 / Long-tail / All), primary domain.
- Top-25 entities render as full markdown pages (variants, fields, use cases).
  Long-tail canonicals render a synthesized summary from the raw TSV.
- URL hash for shareable links: `browser.html#Vehicle`.
- Markdown rendered via `marked.js` from CDN (works offline once first loaded).

Regenerate after running `cluster_entities.py` so the browser stays in sync.

## `gen_entity_graph.py`

Render the cross-repo entity catalog as a D3-v7 force-directed SVG graph at
`domains/entities/graph.html`. Edges are extracted from field types:
`PostingEntity.vehicles : VehicleEntity[]` → `Posting → Vehicle`.

```bash
python3 ~/projects/codebase-map/scripts/gen_entity_graph.py
python3 ~/projects/codebase-map/scripts/gen_entity_graph.py --min-occurrence 3    # fewer nodes
python3 ~/projects/codebase-map/scripts/gen_entity_graph.py --min-edge-weight 2   # only repeated refs
```

Features:
- Nodes sized by occurrence count (sqrt scaling), colored by primary domain.
- Edge thickness = number of field references aggregated across all variants.
- Sliders: top-N (10-200), minimum edge weight (1-10).
- Click a node → highlight 1-hop neighborhood + show incoming/outgoing
  edges with concrete field-level evidence (`loadboard-backend.PostingDto.vehicles [list]`).
- Drag-to-pin nodes, scroll-to-zoom, search-to-highlight.
- URL hash for shareable focus: `graph.html#Vehicle`.

Reads the same inputs as `cluster_entities.py` plus the raw TSV. Regenerate
after editing `entity_aliases.yaml` or re-running the extractor.

## `gen_entity_representations.py`

Render a **bipartite** force-directed SVG graph at
`domains/entities/representations.html` showing how each canonical entity is
represented across repos. Circles = canonical entities (colored by primary
domain); rounded rectangles = repos (colored by repo domain). Edge thickness
encodes the number of variant classes that repo declares for that entity.

```bash
python3 ~/projects/codebase-map/scripts/gen_entity_representations.py
python3 ~/projects/codebase-map/scripts/gen_entity_representations.py --top 25     # initial top-N (slider goes 5–50)
python3 ~/projects/codebase-map/scripts/gen_entity_representations.py --min-occurrence 3
```

Features:
- Two node types with distinct shapes — entity ↔ repo at a glance.
- **Click an entity** → side panel groups every repo that declares it, with
  each variant class listed (kind-coded: jpa / dto / embedded / other) plus
  field counts and module paths.
- **Click a repo** → side panel lists every catalog entity it hosts with the
  same per-variant detail.
- **Click an edge** → focus the panel on just that entity↔repo intersection.
- Summary bar shows total variants, most-spread entity, heaviest connection.
- URL hash: `representations.html#E:Vehicle` or `#R:loadboard-backend`.

Reads the same inputs as `cluster_entities.py` plus the raw TSV.

## `gen_entity_drift.py`

Render a **field × variant heatmap** at `domains/entities/drift.html` that
makes the shape divergence of each canonical entity across services
visually obvious. For each top-N entity:

- Rows = field names (union across all variants of this entity)
- Columns = variants (one column per `(repo, class_name)` row, grouped so
  same-repo columns sit adjacent)
- Cell colors:
  - **gray**: field absent in this variant
  - **cyan**: present, type matches the majority type for this field
  - **orange (animated)**: present, type differs from majority — *type drift*
  - **purple**: only this variant has this field

```bash
python3 ~/projects/codebase-map/scripts/gen_entity_drift.py
python3 ~/projects/codebase-map/scripts/gen_entity_drift.py --top 15   # smaller bundle
```

Features:
- Entity picker dropdown at the top (one heatmap at a time keeps the layout
  readable; with 25 entities × up to 42 variants × 200+ fields, an all-in-one
  view would be unreadable).
- Sort modes: by presence frequency (default), alphabetical, or drift-first.
- "drift only" toggle hides fields whose type is consistent across all variants.
- Field-name filter (substring match).
- Hover any cell for full type info + the type-distribution histogram across
  all variants.
- Per-column drift-count bars in the header reveal which variants are the
  outliers.
- URL hash: `drift.html#Vehicle` jumps to that entity's heatmap.

Answers questions the other visualizations can't, e.g.: *"Where is
`Vehicle.year` `Integer` and where is it `short`? Which services serialize
timestamps as `Date` vs `Instant`?"*

Reads the same inputs as `cluster_entities.py`.

## `refresh_subscription_map.py`

Optional one-time helper that calls `gcloud pubsub subscriptions list` and
rewrites `relations/event-catalog.subscriptions.tsv`.

```bash
python3 ~/projects/codebase-map/scripts/refresh_subscription_map.py --project <gcp-project>
```

Requires `gcloud auth application-default login`. Not part of the auto-run path
— run manually when subscriptions change.

## `verify_links.py`

Lint pass — run before committing changes to the map.

```bash
python3 ~/projects/codebase-map/scripts/verify_links.py
```

Checks:
- Required frontmatter fields present (`repo`, `path`, `stack`, `domain`, `shape`, `last-synced-commit`, `last-synced-date`, `maintainer`, `status`).
- `path:` resolves to an existing directory.
- `repo:` matches the filename stem.
- No duplicate `repo:` values.
- `status:` is one of `{seed, stub, verified, stale}`.
- `_index.md` matches the actual file set.
- Tilde-prefixed links (`~/projects/...`) resolve.

Exit code `0` on clean, `1` on any failure.

## Typical workflows

**New repo appears.** Owner of the map runs `bootstrap_repo_md.py <new-repo>`, edits the stub to add real content, sets status to `seed` once they trust it.

**Weekly drift sweep.** Run `drift_check.py --all --mark-stale`. Skim the report, decide which stale shadows need re-syncing this week.

**Weekly event-catalog refresh.** Run `gen_event_catalog.py` after the drift
sweep. If the diff is non-trivial, review the new rows (especially any
`Status: partial` or `unresolved` entries) and flip `status: stub` → `seed`
once you trust the corrections.

**Weekly event-schemas refresh.** Run `gen_event_schemas.py` after the
event-catalog refresh — it depends on the catalog for its topic list. Review
new/changed per-topic files (especially `schema-source: none` rows that may
need manual seeding) and flip individual `status: stub` → `seed` once correct.

**Entity-catalog refresh.** Six scripts run in order:

```bash
python3 ~/projects/codebase-map/scripts/extract_entities.py             # ~2s   → raw.tsv
python3 ~/projects/codebase-map/scripts/cluster_entities.py             # ~20s  → catalog.md + per-entity pages + shadows
python3 ~/projects/codebase-map/scripts/gen_entity_browser.py           # ~1s   → browser.html
python3 ~/projects/codebase-map/scripts/gen_entity_graph.py             # ~1s   → graph.html
python3 ~/projects/codebase-map/scripts/gen_entity_representations.py   # ~1s   → representations.html
python3 ~/projects/codebase-map/scripts/gen_entity_drift.py             # ~1s   → drift.html
```

Re-run after any of: `entity_aliases.yaml` edits, source-repo changes that
touch declared entities, a `bootstrap_repo_md.py` for a new Java repo.
All four scripts are idempotent. After re-running, review
`relations/entity-catalog.unaliased.tsv` for newly-surfaced canonicals worth
folding into the alias YAML.

The deep design reference (detection rules, canonicalization order, alias
schema, troubleshooting) is at [`../ENTITY_CATALOG.md`](../ENTITY_CATALOG.md).

**Pre-commit / CI.** Run `verify_links.py`. Fail the change if non-zero.
For event-catalog-touching PRs, also run `drift_check.py --event-catalog`.
