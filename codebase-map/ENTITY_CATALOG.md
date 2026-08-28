# Entity catalog — design & generation rules

Authoritative reference for the cross-repo business-entity catalog generated
under `domains/entities/`, `relations/entity-catalog.md`, and the rollups
injected into the Java shadow docs. **All four generator scripts read this
file's rules** — keep this document in sync with `scripts/extract_entities.py`
and `scripts/cluster_entities.py` if you change the regexes, blocklists, or
canonicalization order.

For step-by-step operational commands ("how do I refresh?") see
[`scripts/README.md`](scripts/README.md). This document is the *why* and
*what*, not the *how*.

## Pipeline at a glance

```
ship-cars-usa/<repo>/**/*.java                    (source — never edited)
       │
       ▼
extract_entities.py    →  relations/entity-catalog.raw.tsv
       │                  relations/entity-catalog.errors.log
       │
relations/entity_aliases.yaml   ◄── hand-curated, ~30-name table + split rules
       │
       ▼
cluster_entities.py    →  relations/entity-catalog.md            (master index)
                          domains/entities/<Canonical>.md         (top-N pages)
                          relations/entity-catalog.unaliased.tsv (review channel)
                          repos/*.md ## Entities sections          (managed)
       │
       ├─► gen_entity_browser.py  →  domains/entities/browser.html
       └─► gen_entity_graph.py    →  domains/entities/graph.html
```

Every step is idempotent and stdlib-only. Re-running with unchanged inputs
produces zero diffs.

## 1. Source selection

`extract_entities.py` only walks repos whose shadow-doc `stack:` frontmatter
begins with `Java/` (matches Quarkus, Spring Boot, Maven, Gradle Java).
**Excluded by stack:** `Docs`, `Browser extension`, `Terraform*`, `Helm`,
`Python`, `Go`, `Node*`, `Frontend`, `iOS`, `Android`.

**Also excluded:** every repo flagged `archive-candidate` in
`relations/infrastructure-triage.md` (typo'd duplicates, hackathon repos,
empty dirs, deprecated boilerplates).

**Special pseudo-repo:** `models-lib/` is walked even though it isn't a
service — it's the only shared-DTO library in the fleet.

Inside a selected repo, walking is restricted to `*.java` under
`src/main/java/`. Skipped paths: `src/test/`, `target/`, `*/generated-sources/*`,
`*/db-migration/*`, files > 500 KB.

## 2. Detection rules — what counts as an entity?

A class is captured if **any** rule matches:

| Rule | Sets `kind` | Notes |
|---|---|---|
| File contains `@Entity` annotation | `jpa` | Hibernate/JPA persistent entity |
| File contains `@Embeddable` | `embedded` | JPA embeddable value object |
| Class name ends `Dto`/`ReadDto`/`WriteDto`/`PubSubDto`/`EventDto`/`Response`/`Request` | `dto` | Common DTO naming |
| File has `@Data`/`@Value`/`@Builder`/`@Getter`/`@Setter` AND name doesn't end `Entity`/`DbEntity` | `dto` | Lombok-flagged POJO |
| File has `@JsonIgnoreProperties` | `dto` | Jackson-aware serializable shape |
| `record <Name>(…)` Java record | `dto` | Modern DTO shape |
| Filename `*Entity.java`/`*DbEntity.java` without `@Entity` | `other` | Mapped superclass / abstract base — kept so the clusterer can decide |

Anything else is **skipped**. We are not cataloging service classes,
controllers, mappers, or utilities.

### Dropped by class-name regex

Even when one of the rules above fires, the class is dropped if its name
matches the blocklist `DROP_NAME_RE` in `extract_entities.py`:

- Audit / base / abstract scaffolding: `BaseEntity`, `Base*Entity`, `Audit*`,
  `Versioned*`, `Abstract*`, `*Test*`, `*Mock*`, `*Stub*`, `MapStruct*`
- Hibernate Envers infrastructure: `RevisionInfo*`, `*RevisionEntity`,
  `EnversRevision*`, `RevisionData`, `ActorContext`
- Spring Data / Quarkus pagination wrappers: `Page`, `PageDto`, `PageModel`,
  `PageUtils`, `Page[A-Z]\w+`, `*PageDto`, `*PageModel`,
  `PagingCriteria`, `SortCriteria`, `Paged`, `PagedResponse`
- Framework config beans: `RestConfig`, `OpenApiConfig`, `SwaggerConfig`,
  `AppContext`, `AppConfig`, `InfraConfig`
- Logging / metadata utility wrappers: `LogMeta`, `TimeMeta`, `TraceMeta`
- Pub/Sub envelope types (handled by the event-schema catalog instead):
  `MessageEnvelope`, `MessageObject`, `MessageObjectDto`, `PubSubMessage`
- Generic error envelopes: `ErrorResponse`, `ErrorDto`, `ErrorResponseDto`

**To extend the blocklist:** edit `DROP_NAME_RE` in `extract_entities.py`.
Keep additions to *clearly framework-infrastructure* names. Don't drop
business types because they're noisy in v1 — use the alias YAML to merge
instead.

### Dropped by module / package

- `abstract class` modifier present
- Module's `artifactId` ends `-test-commons`, `-coverage-report`,
  `-integration-tests`, `-test-utils`
- Package contains `.test.` or `.testfixtures.`

### Field extraction

For each kept class, the extractor reads field declarations using
`JAVA_FIELD_RE` (idiom borrowed from `gen_event_schemas.py`):

- **Skipped fields:** `static`, `transient`, or annotated `@JsonIgnore`
  (within 4 lines above the declaration, bounded by the most-recent `;`/`{`/`}`).
- **Wrapper flattening:** `List<X>`, `Set<X>`, `Optional<X>`, `Iterable<X>`,
  `Collection<X>`, `Map<K,V>` → inner type with `[]` suffix marker.
- **`@Embedded` fields:** record the embedded type by name; do **not** expand
  recursively in v1.
- **JPA relations** (`@ManyToOne`/`@OneToMany`/`@JoinColumn`): keep target type
  as-is. These are first-class signal for the graph.
- **Heuristic:** field names that start uppercase are skipped — the regex
  occasionally false-matches method return-type fragments.

## 3. Canonicalization rules

Each captured class name is normalized into a *canonical* in this order
(implemented in `cluster_entities.py`):

1. **Splits override everything.** If `(repo, class_name)` is listed under a
   `splits:` rule in `entity_aliases.yaml`, return that canonical
   immediately. Also tried against the post-suffix-strip form.
2. **Suffix strip** (longest match first, idempotent loop):
   `DbEntity`, `Entity`, `PubSubDto`, `EventDto`, `ReadDto`, `WriteDto`,
   `Response`, `Request`, `Dto`, `Model`, `Embedded`, `Embeddable`, `Record`,
   `Bean`.
3. **Version prefix strip:** leading `V\d+`.
4. **Qualifier prefix strip:** leading `Internal`, `External`, `Public`,
   `Admin`.
5. **Service-prefix strip (conditional):** leading `Inventory`, `Loadboard`,
   `Posting`, `Payment`, `Notification`, `User`, `Chat`, `Driveaway`, `Trip`,
   `Tracking`, `Recommender`, `AutoIms`, `AutoIMS`, `Carrier` — **only if
   the prefix appears in the source repo name.** This deliberately preserves
   `InventoryUnit` in foreign repos as `InventoryUnit` (cross-repo signal)
   but strips it inside `inventory-backend` to `Unit`.
6. **Alias merge:** if the stripped name appears in any `canonical:` list in
   `entity_aliases.yaml`, return that canonical.
7. **Fallback:** the stripped name *is* its own canonical.

### Worked examples

| Observed in | Class | After strip | After prefix | After alias | Canonical |
|---|---|---|---|---|---|
| `loadboard-backend` | `VehicleEntity` | `Vehicle` | `Vehicle` | — | **Vehicle** |
| `inventory-backend` | `InventoryUnitDbEntity` | `InventoryUnit` | `Unit` (inventory-prefix stripped) | `Unit → Vehicle` | **Vehicle** |
| `loadboard-backend` | `CtmsVehiclePubSubDto` | `CtmsVehicle` | `CtmsVehicle` | `CtmsVehicle → Vehicle` | **Vehicle** |
| `user-backend` | `V2CompanySubscriptionPubSubDto` | `V2CompanySubscription` | `CompanySubscription` (V2 stripped) | — | **CompanySubscription** |
| `user-backend` | `UserAccountEntity` | `UserAccount` | `Account` (user-prefix stripped) | `Account → User` | **User** |
| `chat-backend` | `MessageEntity` | `Message` | — | split-rule fires | **ChatMessage** |
| `notification-backend` | `MessageDto` | `Message` | — | split-rule fires | **QueueMessage** |
| `models-lib` | `PostingVehicleReadDto` | `PostingVehicle` | `PostingVehicle` | not aliased | **PostingVehicle** (compound — deliberate) |

## 4. `entity_aliases.yaml` schema

The hand-curated input that drives all the merges + splits. Two top-level
keys:

```yaml
canonical:
  Vehicle:     [Vehicle, Unit, InventoryUnit, CtmsVehicle, Car, Truck, VehicleMSRPCache]
  User:        [User, UserAccount, UserInfo, UserProfile, Person, Account, DbUser]
  Company:     [Company, CarrierCompany, ShipperCompany, Customer, Organization, Carrier, DbCompany]
  ...

splits:
  - canonical: ChatMessage
    repos: [chat-backend, chat-frontend]
    names: [Message, MessageEntity, MessageDto, ChatMessage]

  - canonical: QueueMessage
    repos: [notification-backend, notification-orchestrator, pusher, pubsub-exception-handler]
    names: [Message, MessageDto]
```

### Rules

- **A name may appear under at most one `canonical:` key.** The clusterer
  exits with a non-zero code if it finds a duplicate — this is the one
  config bug that produces silent wrong answers.
- **Splits apply *before* alias merge.** Useful when the same simple name
  means two different concepts in different repos.
- **You don't need every observed alias.** Anything not listed survives
  through to step 6 of canonicalization and may still cluster correctly via
  suffix-stripping. The YAML is for the cases the stripping can't handle:
  cross-repo renames (`UserAccount` ↔ `Account`) and same-name collisions.

### When to edit the YAML

Use the side-channel: after each `cluster_entities.py` run,
`relations/entity-catalog.unaliased.tsv` lists every canonical with
occurrence ≥3 that didn't match any alias. For each row, decide:

- **Should this fold into an existing canonical?** Add it to that canonical's
  alias list. Re-run; verify the unaliased.tsv row disappears.
- **Is this a genuine new business entity?** Leave it; it'll get its own
  canonical. If it climbs into the top-N, it'll automatically grow a page.
- **Is this two concepts under one name?** Add a `splits:` rule.

Don't preemptively alias every unknown name; the YAML is hand-curated for a
reason. The top-25 covers the load-bearing entities; below that, signal-to-noise
drops fast.

## 5. Ranking — the composite score

For each canonical:

```
score = occurrence_count + 2 * distinct_domain_count
```

Where:
- `occurrence_count` = number of `(repo, class)` rows that map to this canonical
- `distinct_domain_count` = unique `domain:` values among those repos' shadow
  docs, excluding `unassigned`

**Domain spread is weighted 2×** because the catalog's user-facing value is
*cross-domain divergence*. An entity that lives only in `listings-trade` is
less interesting than one straddling `listings-trade + pricing-billing +
operations`.

The top-N (default 25) by composite score get a per-entity page under
`domains/entities/`. The rest still appear in the master index but with no
page link.

## 6. Use-case extraction (per top-N entity)

For each entity, three lookups across each variant's source repo:

### REST endpoints
- Find files with `@Path`, `@RequestMapping`, `@GetMapping`, `@PostMapping`,
  `@PutMapping`, `@DeleteMapping`, `@PatchMapping` (via `rg` if available,
  Python walk otherwise).
- Keep only files that mention the canonical's class name or any alias.
- Compose class-level `@Path` / `@RequestMapping` with method-level paths
  and HTTP verbs. Quarkus uses class-level `@Path` + method-level
  `@GET`/`@POST`/etc.; Spring uses `@RequestMapping(...)` at class +
  `@GetMapping(...)` at method.
- Capture `(file, http_verb, full_path)`. Dedupe by `(verb, path)`; cap at 40.

### Repository methods
- Find `*Repository.java` files.
- Match `interface *Repository extends|implements (JpaRepository|CrudRepository|
  PanacheRepository|...) <X, ...>`.
- If `X` is in the canonical's alias set, parse method declarations from the
  interface body. Spring Data derived names (`findByVin`,
  `countByCompanyId`) are excellent business-language signal.
- Skip noise tokens (`if`, `for`, `while`, `switch`, `return`, `throw`, `new`).

### Pub/Sub topics
- Read every `relations/event-schemas/*.md` frontmatter `canonical-dto:` field.
- Canonicalize the DTO simple name through the same alias map.
- Any topic whose resolved canonical matches the entity is linked on the
  entity's page.

### Not extracted in v1
- `@Scheduled` background jobs (separate axis)
- Kafka / non-Pub/Sub messaging (none used in this fleet)
- Frontend (TS/React) entity usage
- Direct DB-read edges (handled separately by `service-graph.md`)

## 7. Shadow-doc integration

After computing canonicals, `cluster_entities.py` injects a `## Entities`
section into **every Java shadow doc that has at least one detected entity**.
The section is bounded by HTML-comment markers:

```markdown
<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `VehicleEntity` | jpa | `db-entities` | [Vehicle](../domains/entities/Vehicle.md) |
| `PostingEntity` | jpa | `db-entities` | [Posting](../domains/entities/Posting.md) |
...
<!-- entities-end -->
```

The markers let `cluster_entities.py` safely re-emit the section on every
run without disturbing hand-edited content above or below. Same pattern as
`gen_index.py` uses for `_index.md`.

Stub shadows get the same treatment — auto-detection by "does this repo have
detected entities?" is cleaner than gating on `status: seed`.

## 8. Per-entity page schema

Each `domains/entities/<Canonical>.md` follows this layout:

```yaml
---
entity: <Canonical>
aliases: [<observed simple names>]
status: auto-generated     # human can flip to "reviewed" after editing narrative
domains: [<sorted domain slugs>]
occurrence-count: <int>
variant-count: <int>       # currently == occurrence-count; will diverge once
                           # we collapse duplicate variants per repo
owning-service: <heuristic pick>
last-extracted-date: YYYY-MM-DD
---
```

Body sections, in order:

1. **What it is** — auto-stubbed as `TODO: human narrative`. The only
   intentionally-hand-edited section in v1. Flip frontmatter `status:` to
   `reviewed` after editing so future regens know not to overwrite it.
   *Note: v1 still overwrites this on regen — the "reviewed" flag is an
   advisory tag, not enforced. Don't invest more than a paragraph until the
   override mechanism lands (deferred work).*
2. **Variants** — repo · class · kind · module · extends · field count · file path.
3. **Field union / intersection** — core fields (≥60% of variants) and
   variant-specific fields (the spread).
4. **Owning service** — heuristic pick. Order: REST-endpoint count, then JPA
   max field count, then alphabetical.
5. **Use cases** — REST surface, repository operations, Pub/Sub topics.
6. **Cross-references** — back to shadow, domain rollups, master index.

## 9. Visualizations

The catalog has four generated HTML views, all self-contained and
auto-regenerated from the same source files:

| File | Generator | Story it tells |
|---|---|---|
| `browser.html` | `gen_entity_browser.py` | Catalog browser — sidebar list of all 1,800 canonicals, click to read the full markdown page |
| `graph.html` | `gen_entity_graph.py` | **Entity ↔ entity** relations — what references what, via field types |
| `representations.html` | `gen_entity_representations.py` | **Entity ↔ repo** bipartite — where each canonical lives, with variant class names |
| `drift.html` | `gen_entity_drift.py` | **Field × variant heatmap per entity** — where each field is present, which type variants drift |

### 9a. `gen_entity_graph.py` — entity-to-entity edges

Reuses the same canonicalization helper applied to **field types** rather
than class names:

```
For each row in entity-catalog.raw.tsv:
  src = canonicalize(class_name, repo)
  For each (field_name, field_type) in fields:
    target_simple = strip <>, [], package prefix from field_type
    If target_simple in SCALAR_BLACKLIST: skip
    If target_simple ends "Enum": skip
    If target_simple has lowercase first letter: skip
    If length(target_simple) <= 1: skip (generic param)
    tgt = canonicalize(target_simple, repo)
    If tgt == src: skip (self-loop)
    Increment edge_weight[(src, tgt)]
    Record up to 4 sample fields per edge for tooltip
```

`SCALAR_BLACKLIST` covers Java primitives, common wrapper types, java.time,
java.util.Map/List/Set, and common framework types (`ResponseEntity`,
`Pageable`, `JsonNode`).

Edge weight = total field references across all variants of source canonical
pointing at target canonical. So `Vehicle → Attachment ×11` means 11 distinct
field declarations across all Vehicle variants in all repos reference an
Attachment-shaped type.

### 9b. `gen_entity_representations.py` — entity-to-repo bipartite

Different question, different graph: where does each canonical *live*?

Two node types:
- **Entity nodes** (circles) — one per canonical, sized by occurrence,
  colored by primary domain.
- **Repo nodes** (rounded rectangles) — one per repo that declares ≥1 variant
  of any kept entity, colored by repo `domain:` frontmatter.

For each row in `entity-catalog.raw.tsv`:

```
cano = canonicalize(class_name, repo)
edge[(cano, repo)].variants.append({
    class_name, kind, module, field_count
})
```

Edge weight = `len(edge.variants)` (the count of distinct variant classes for
that entity in that repo). The full variant list is bundled into the edge
record so the UI side panel can show per-class detail (kind badge, field
count, module path) on click.

D3 force layout uses **horizontal x-bias** (`forceX`) to pull entities
leftward and repos rightward, so the bipartite structure is visually obvious
even before the simulation settles. Stronger entity-side charge repulsion
(`-400` vs `-160`) gives entities more space than repos.

Three interaction modes for the side panel:
- Click **entity node** → list every repo that declares it, grouped, with
  variant-class detail (`AutoImsUnitDbEntity (jpa) · 28 fields`).
- Click **repo node** → list every catalog entity hosted in this repo with
  the same per-variant detail.
- Click an **edge** → focus on just that one (entity, repo) intersection.

`representations.html` answers different questions than `graph.html`:

- `graph.html`: "what does X reference?" (the entity-to-entity neighborhood)
- `representations.html`: "where does X live, and what does it look like in
  each of those places?" (the cross-repo divergence story)

### 9c. `gen_entity_drift.py` — field × variant heatmap

Reads the same inputs and goes one level deeper than `representations.html`:
where the bipartite graph shows *which* repo has *how many* variants of an
entity, the drift heatmap shows *which fields* each variant declares and
*what type* each field has.

Per top-N canonical (default 25):

```
Group raw rows by canonical.
Within each canonical:
  variants = sorted by (repo, class_name, module) for stable layout
  union_fields = union of every field name across variants
  for each field_name:
    types[field_name] = Counter of observed types across variants
    majority_type = most common type
    by_variant[field_name] = {variant_idx: type-observed-here}
    drift = (len(types) > 1)
  sort fields by presence desc, then alphabetical
  compute per-column "drift_minority_count" = how many of this column's
    cells are minority-type (used for the column-header drift bar)
```

The bundled JSON is ~500 KB for the top-25 entities — small enough that
the entire dataset ships inline; the browser renders one entity at a time
via the picker dropdown.

**Cell color encoding:**

| Color | Meaning |
|---|---|
| gray | field not declared in this variant (absent) |
| cyan | field declared, type matches the majority type for this field |
| orange (animated pulse) | field declared, type differs from the majority |
| purple | field declared in only this variant — repo-local addition |

The animation on minority-type cells (`drift-pulse` keyframes, 2.4 s easing)
is deliberately slow — pulls the eye without strobing.

**The "core fields" threshold** (`max(2, int(n_var * 0.6))`) is 60% rather
than the 80% used in cluster_entities's per-entity pages. The reason: many
catalog variants are thin DTOs that inherit most of their fields from a
base class and therefore declare `field_count == 0` in the raw TSV. At 80%,
those empty shells dominate the denominator and *every entity reports 0
core fields*, which buries the signal. 60% gives a usable threshold without
overstating commonality.

**Drift signals worth flagging from a real run on the Ship.Cars fleet:**

- `Vehicle.year` — `Integer` in 20 variants, `short` in 3
- `Vehicle.operable` — `Boolean` (boxed/nullable) in 9, `boolean` (primitive) in 4
- `Vehicle.createTime`/`updateTime` — `Instant` in 5, `Date` in 3 (legacy temporal type)
- `Vehicle.type` — `String` in 9, `VehicleType` enum in 4 (semantic drift)
- `Vehicle.weight` — `String` in 5, `Integer` in 1 (numeric-as-string anti-pattern)
- `Vehicle.attachments` — 8 different attachment-DTO list types

`drift.html` is the right tool when the question is *"is this field's type
consistent across the services that declare it?"* — the kind of question
that drives schema-coordination ADRs.

## 10. Output file locations

| File | Generator | Purpose |
|---|---|---|
| `relations/entity-catalog.raw.tsv` | `extract_entities.py` | Source-of-truth per-class rows |
| `relations/entity-catalog.errors.log` | `extract_entities.py` | Per-file parse failures (usually empty) |
| `relations/entity_aliases.yaml` | **human** | Canonical merges + splits |
| `relations/entity-catalog.md` | `cluster_entities.py` | Master ranked index (all canonicals) |
| `relations/entity-catalog.unaliased.tsv` | `cluster_entities.py` | Review side-channel |
| `domains/entities/<Canonical>.md` | `cluster_entities.py` | Top-N per-entity pages |
| `repos/<repo>.md` `## Entities` section | `cluster_entities.py` | Managed insertion per shadow |
| `domains/entities/browser.html` | `gen_entity_browser.py` | Self-contained catalog browser |
| `domains/entities/graph.html` | `gen_entity_graph.py` | Self-contained entity ↔ entity relation graph |
| `domains/entities/representations.html` | `gen_entity_representations.py` | Self-contained entity ↔ repo bipartite graph |
| `domains/entities/drift.html` | `gen_entity_drift.py` | Self-contained field × variant drift heatmap (one entity at a time) |

## 11. Idempotency guarantees

All four scripts are deterministic given identical inputs:

- `extract_entities.py` regenerates the raw TSV whole. No incremental cache.
- `cluster_entities.py` deletes stale per-entity pages on re-run (canonicals
  that dropped out of the top-N or got merged). Shadow `## Entities` sections
  use begin/end markers so re-runs don't accumulate.
- `gen_entity_browser.py`, `gen_entity_graph.py`,
  `gen_entity_representations.py`, and `gen_entity_drift.py` overwrite
  their outputs.

A re-run with no source changes produces zero diffs across all generated files.

## 12. Out-of-scope in v1 (explicitly)

- **Non-Java entities.** TypeScript types (frontend models.ts), Pydantic
  DTOs, Go structs. Out of scope per user decision — Java + models-lib only.
- **Java API surface.** Lombok-generated accessors and hand-written getters
  aren't surveyed. The catalog reflects persisted / serialized shape only.
- **Drift detection.** `drift_check.py` doesn't currently watch the entity
  catalog inputs. Re-run manually after repo changes.
- **OpenAPI cross-reference.** Sparse / low-signal in this fleet (only 2
  centralized specs).
- **`@Scheduled` jobs per entity.** Separate axis; can be added if asked.
- **Field-type normalization.** `Integer`/`int`/`Long` still cluster as
  distinct types in the field-intersection table.
- **Frontend → backend entity mapping.** Frontends carry their own projection
  layer; would be a v2 pass.

## 13. Troubleshooting

### "I added a new repo. Why doesn't its entities show up?"

`extract_entities.py` reads shadow-doc `stack:` to decide which repos to walk.
If the repo doesn't have a shadow yet, run `bootstrap_repo_md.py <repo-name>`
first to create one with the correct `stack:` field. Then re-run the entity
pipeline.

### "A class I expect isn't being detected"

Check in order:

1. Is the file under `src/main/java/`? Extractor doesn't walk other roots.
2. Does the class name match the `DROP_NAME_RE` blocklist? (e.g.
   `RestConfig` is filtered as a framework bean.)
3. Is the class `abstract class`? Abstracts are skipped.
4. Does the class have `@Entity`, `@Embeddable`, a DTO suffix, a Lombok
   annotation, or `@JsonIgnoreProperties`? Without any of these, it's
   intentionally skipped.
5. Run `python3 scripts/extract_entities.py --repo <repo>` and grep the raw
   TSV. If still missing, debug the class declaration regex against
   the file content.

### "Two entities should be one"

Add the lower-frequency name as an alias under the higher-frequency
canonical in `entity_aliases.yaml`. Re-run `cluster_entities.py`. Verify
the merged canonical's variant count grew by the expected amount and the
side-channel `unaliased.tsv` lost the old row.

### "One canonical actually represents two concepts"

Add a `splits:` rule with the specific `(repos, names)` tuples that should
get the distinct canonical. Splits apply *before* the alias merge.

### "Clusterer exits non-zero with 'alias appears under both X and Y'"

Two canonicals list the same observed name. Pick one and remove the
duplicate from the other.

### "The graph is too dense"

Use `gen_entity_graph.py --min-edge-weight 2` (or higher) to keep only
relations that repeat across multiple variants. Or in the live page, raise
the "min edge w" slider.

### "A per-entity page has wrong owning-service"

The heuristic is REST-count, then JPA-field-count, then alphabetical. For
event-only entities (no REST endpoints), the first non-zero tier loses to
alphabetical. Document the correct owning service in the page's
hand-editable "What it is" narrative; the auto-pick will be a known minor
inaccuracy.

### "Re-running the clusterer overwrites my hand-edited narrative"

Yes — v1 deliberately leaves the page body fully regenerated. The
`status: reviewed` frontmatter flag is advisory, not enforced. If you want
hand-edited narratives, the supported approach in v1 is to keep them in a
separate file outside `domains/entities/` (e.g. a hand-written ADR) and link
to it from the auto-generated page via `entity_aliases.yaml`-driven
references. A real override mechanism is deferred work.

## 14. When to update *this* file

- A new section is added to the per-entity page schema.
- A new canonicalization rule or filter is added.
- The alias YAML grows a new top-level key.
- A new generator script joins the pipeline.
- Out-of-scope items in §12 move into scope.

If you change `extract_entities.py` / `cluster_entities.py` behavior and
forget to update this file, future Claude sessions will have a wrong mental
model. Keep them in sync.
