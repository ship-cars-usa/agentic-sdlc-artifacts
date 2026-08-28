# Change Design Records

One folder per record, GitHub-native and directly editable. `README.md` is the **single source of truth** — there is no backing JSON or HTML viewer.

```
<KEY>/
  README.md     the record — edit this directly (plain Markdown)
  diagram.svg   the blast-radius graphic (self-contained; renders on GitHub)
```

## Use

- **Read** a record by opening its folder here on GitHub — `README.md` renders in place with the diagram inline.
- **Edit** a record by editing `README.md` directly (GitHub's web editor, or any text editor). No build step, no export.
- Change rows are colour-coded via emoji so they read on GitHub: **🟢 added · 🟡 updated · 🔴 removed · 🔵 reused** (a legend sits at the top of each record).
- `diagram.svg` is **self-contained** (inline styles + white background), so it renders on GitHub; hand-edit it or redraw in a vector tool.

Keep `Services` slugs matching `codebase-map/repos/<slug>.md` so records stay joinable to the map.

## Records

| Record | Status | Change |
|---|---|---|
| [SCP-15047](SCP-15047/) | proposed | Bulk Accept Revisions — orders stay in Active Revision after processing |
| [SCP-15096](SCP-15096/) | proposed | [AAAG] VIN mandatory during Manual Status Update where Ghost Vehicle is enabled |
| [SCP-15134](SCP-15134/) | proposed | [Montway][Faster Payments] Faster-Pay eligibility in LoadScout recommendations |
| [SCP-15137](SCP-15137/) | proposed | Enable Driver LoadBoard access by default |
| [cdr-0007](cdr-0007/) | example | Add expedited flag to CTMS orders (illustrative walkthrough) |
| [cdr-0008](cdr-0008/) | shipped | Idempotency key on carrier payment transactions |
| [cdr-0009](cdr-0009/) | proposed | Add DRIVER_REASSIGNED lifecycle event (breaking) |
| [cdr-0010](cdr-0010/) | shipped | N-gram substring search on company name |
| [cdr-0011](cdr-0011/) | proposed | Cursor-paged /v2 inventory units endpoint |
| [cdr-0012](cdr-0012/) | proposed | Rename a loadboard column read cross-DB |
| [cdr-0013](cdr-0013/) | accepted | GPS heading on location-log events |

## Record shape

Each `README.md` follows the same layout: an `# H1` title; a metadata line (`` `key` `` · **status** · date · author); a `**Services:**` line; the **Legend**; the embedded `![diagram](./diagram.svg)`; a `## Context`; one `##` section per delta kind (PostgreSQL / Elasticsearch / Pub/Sub event / REST API & DTO) rendered as a table whose **Change** column is emoji-coded; a `## Where it lives & how it's wired` table; and a blockquoted `## Rollout`.
