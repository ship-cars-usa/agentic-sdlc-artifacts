# COI report for AAAG - feasibility and effort

`SCP-15147` · **proposed** · 2026-09-03 · hristo.savov@ship.cars · groomed 2026-09-03 (re-groomed)

**Services:** `ml-central-data-storage`, `company-documents`, `platform-backend`, `airbyte`, `metabase`

**Legend:** 🟢 added · 🟡 updated · 🔴 removed · 🔵 reused

![Design diagram](./diagram.svg)

## Columns required on the Databricks side

The handoff list for the data team. These are the **source columns the gold view must read** — distinct from the six columns it *emits* (see §2c). All six tables already have silver transformations wired into the `dev` and `prod` pipeline globs, and Airbyte replicates with `propagate_fully`, so this is a **verification checklist first** (`DESCRIBE` each table and confirm presence + `MAX(_ingest_time)`), not a request for new ingestion.

Catalog: `silver_{env}_catalog`. ✅ = drives a report column · 🔑 = join key · ⚙️ = filter/predicate only · ⚠️ = backfill-dependent, see the blocker below.

**`company_documents_platform.carrierdocument`** *(Postgres `company_documents."CarrierDocument"`)*

| Column | Type | Role | Note |
| --- | --- | --- | --- |
| `id` | int | 🔑 | → `shippercarrierdocument.carrier_document_id` |
| `carrier_id` | string | 🔑 | the `C-…` user-management id → `users_company.user_management_id` |
| `type` | string | ⚙️ ⚠️ | filter `= 'cargo_insurance'` **exactly**. Do **not** use the sibling enum value `'certificate_insurance'` — no route writes it |
| `document_status` | string | ⚙️ | filter `= 'active'` |
| `visibility` | string | ⚙️ | `'public'` is one half of the sharing predicate |
| `versions_create_time_list` | string | ✅ ⚠️ | → **Upload Date**. Comma-joined version timestamps; take `element_at(split(…, ','), -1)` |
| `created_at` | timestamp | ✅ (fallback) | first-upload date; use only if `versions_create_time_list` is unusable |
| `expiration_date` | **string** | 🚫 **do not use** | the *carrier's* raw blob-metadata copy. The report's expiration comes from the wrapper table below |

**`company_documents_platform.shippercarrierdocument`** *(Postgres `company_documents."ShipperCarrierDocument"`)*

| Column | Type | Role | Note |
| --- | --- | --- | --- |
| `id` | int | ⚙️ | `IS NULL` distinguishes "public doc the auction never engaged with" from a real wrapper row |
| `carrier_document_id` | int | 🔑 | → `carrierdocument.id` |
| `shipper_id` | string | 🔑 | the auction's `C-…` id → `users_company.user_management_id` |
| `status` | string | ⚙️ | `'active'` is the other half of the sharing predicate |
| `expiration_date` | **timestamp** | ✅ | → **Expiration Date**. Shipper-entered; blank for ~15% of shared COIs, and that blank is meaningful (see Context) |
| `is_shipper_tracked` | boolean | optional | useful diagnostic: has the auction opted into monitoring this document |
| `created_at` | timestamp | optional | proxy for "when the auction first engaged with this document" |
| `updated_at` | timestamp | optional | **does not exist yet** — added by §2a; not retroactive |

**`production_platform.users_company`** *(Django `users_company`; joined **twice** — once as auction, once as carrier)*

| Column | Type | Role | Note |
| --- | --- | --- | --- |
| `id` | int | 🔑 | → `compliance_network_compliancenetworklink.shipper_id` / `.carrier_id` |
| `name` | string | ✅ | → **Auction Name** (auction side) and **Carrier Name** (carrier side) |
| `user_management_id` | string | 🔑 | the `C-…` id that bridges to `company_documents_platform.*` and `posting_core.company.external_id` |
| `is_shipper` / `is_carrier` | boolean | ⚙️ | role filters. **Note:** this table has **no `active`/`is_active` column** — use `posting_core.company.active` to exclude inactive auctions |

**`production_platform.compliance_network_compliancenetworklink`** *(defines the report's grain)*

| Column | Type | Role | Note |
| --- | --- | --- | --- |
| `shipper_id` | int | 🔑 | unique together with `carrier_id` → one row per (auction, carrier) |
| `carrier_id` | int | 🔑 | as above |
| `status` | string | ✅ | → **Status**. Sample contains only `verified` \| `suspended` \| `under_review`; the model also defines `not_verified` and `not_verified_offered` — filter explicitly (Q3) |
| `document_request_status` | string | optional | `not_requested` \| `requested` \| `granted` — separates "never asked" from "asked, not uploaded" |
| `last_review_date` | timestamp | optional | `auto_now`, so it moves on **any** save — weak as a review signal |

**`posting_core.company`** *(the auction hierarchy — not available in Django)*

| Column | Type | Role | Note |
| --- | --- | --- | --- |
| `external_id` | string | 🔑 | = `users_company.user_management_id` |
| `external_parent_company_id` | string | ⚙️ | scopes to the parent's child auctions. Prefer matching on the **parent's name** over hard-coding the id, so the report serves all LMP partners (Q4) |
| `name` | string | ✅ | auction name and parent name (`CASE WHEN external_parent_company_id IS NULL THEN name ELSE parent.name END`) |
| `active` | boolean | ⚙️ | excludes inactive auctions — the only `active` flag available anywhere in the join |

**Housekeeping columns present on every silver table — required, not optional**

| Column | Role | Note |
| --- | --- | --- |
| `__END_AT` | ⚙️ | SCD2 current-record filter. **Every join needs `AND x.__END_AT IS NULL`** or rows fan out across history |
| `__START_AT` | — | SCD2 validity start; the only column the existing silver GX suites check |
| `_ab_cdc_deleted_at` | ⚙️ | Airbyte soft-delete. **Every join needs `AND x._ab_cdc_deleted_at IS NULL`** or deleted rows resurface |
| `_ingest_time` | verification | added by the silver transformation; use `MAX(_ingest_time)` to prove freshness |

> ⚠️ **Two traps for whoever writes the SQL.**
> 1. **Timestamps arrive as union types.** Airbyte's parquet output makes timestamp columns structs — the existing gold views access them as `col.member0` (e.g. `dispatch_date.member0`, `update_time.member0`). Expect `expiration_date.member0` and `created_at.member0` rather than the bare column.
> 2. **Two different `expiration_date` columns exist**, one on each document table, with different types and meanings. The report needs the **wrapper's** `timestamp` (shipper-entered), never the carrier document's `string` (raw blob metadata) — using the wrong one would silently diverge from the compliance state the product displays.

## Context

> **Supersedes the 2026-09-02 record.** On 2026-09-03 the story was updated with `AAAG_LMP_COI Tracker_Reporting Request_Form (1).xlsx` — the org's **Databricks report-request form** plus a **659-row sample report**. It narrows the ask substantially and corrects two facts the earlier record got wrong. Every source fact below was re-verified against the deployed branches.

AAAG mandate their auctions to hold a current Certificate of Insurance for every hauler. The requester (Business Development) wants a weekly report answering two questions: **which auctions still have carriers outstanding**, and **which carriers' COIs are expiring**.

**The ask is narrower than the story's AC.** A working report already exists — built in Metabase by the BI/reporting owner — and three of its six columns are filled in **by hand**. The form's own words: *"See 'COI Report' Tab for the three columns of data that we can't pull today that are manual… The other data points we can currently pull via Metabase… We just need the ability for him to pull in these few fields that currently aren't available."* So the deliverable is making three fields queryable next to the other three, not building a report product.

The sample tab specifies the artefact exactly: **6 columns, one row per (auction, carrier)** — `Auction Name`, `Carrier Name`, `Status`, `COI` (Yes/No), `Upload Date`, `Expiration Date` — across **49** America's Auto Auction child auctions and 526 carriers.

**Why the answer is Databricks.** The report spans three domains in three different Postgres databases: the auction hierarchy (`posting`), network membership and company names (`production`), and the COI facts (`company_documents`). Postgres cannot join across databases and no `postgres_fdw`/`dblink` is provisioned, so the join is **structurally impossible** in Metabase — which is precisely why three columns are typed in by hand. In the Databricks lakehouse all six tables are schemas in one catalog and the join is one statement.

That path is already fully built and needs **zero pipeline work**:

- Airbyte CDC already replicates `production` (incl. `users_company`, `compliance_network_compliancenetworklink`) and **all** of `company_documents` into the Databricks bronze volumes, configured `non_breaking_schema_updates_behavior = "propagate_fully"` with new-column backfill — so the columns added on 2026-08-07 propagate automatically.
- All six silver transformations already exist and are wired into the `dev` **and** `prod` pipeline library globs.
- The same request form has been filed twice before as **RE-975** and **RE-977** under epic **RE-976 "Reporting Requests"**, both `Done`, each delivered as a **single ~180-line file** in `ml-central-data-storage`.

So the only new artefact is **one gold materialized view**. No new endpoint, no event, no application deploy. This replaces the earlier record's plan for a `company-documents` report endpoint, a Django network-list endpoint and a `posting-backend` Temporal scheduled report — all three are now unnecessary.

**Two corrections to the 2026-09-02 record:**

1. `company_documents` and `production` are **separate databases on the *same* Cloud SQL instance** (`platform`), not separate instances. That matters twice over: a BI read replica (`platform-replica-analytics`) already physically carries both, so exposing the COI tables to Metabase is a GRANT rather than new infrastructure — but they are still separate *databases*, so a single-query join remains impossible.
2. `compliance-statuses` now returns `expiration_date` **ungated** by `is_shipper_tracked` (SCP-14905, on production), and wrapper status no longer masks a non-active document (SCP-15092). The earlier record invented a new endpoint partly to work around gating that no longer exists.

**One blocker survives.** Three independent 60-day prod log searches found no evidence the metadata backfill has ever run. Four commits landed on `origin/production` on **2026-08-07** under SCP-14461 — `3ddc910` (migration `0fa047cb2bea`, the denormalized columns + tracking flag), `6e8c00d` (compliance/metadata helpers), `bcbf0f9` (**the one-off GCP→DB metadata backfill script**), `29a2402` (tests) — and every upload since writes the values on the write path (`apply_document_metadata` at `carrier_document_route.py:82`, `shipper_document_route.py:78`, re-sync `:276`/`:325`). But the sample's upload dates reach back to **2023-07-06**, so most of the corpus predates that and still depends on the backfill. Documents with `type = NULL` are invisible to a `type='cargo_insurance'` filter: the report would come back near-empty while *looking* correct. The sample's **443 COI=Yes** is the oracle that detects this.

**This reconciles the requesting thread's conclusion, which was that the report cannot be built.** Three of its claims hold — it genuinely cannot be built in Metabase (separate databases, no `postgres_fdw`), a prior Databricks attempt at a carrier-insurance report left nothing committed on any branch, and the expiration-date limitation is real. The load-bearing claim — *"the data required is not presented in the database; it can be found only in metadata of the bucket… maybe a script that will add the data into a new column"* — was **already out of date when it was written**, by roughly 3–4 weeks: the columns exist, the write path populates them, and the proposed script is `scripts/backfill_document_metadata.py`. Where that diagnosis remains effectively correct is exactly this blocker — for pre-2026-08-07 documents the values *are* still only in bucket metadata until the backfill runs. Same fact, two sides. **So the scoping question behind this ticket — "a small tweak or a major architectural change?" — resolves to a small tweak:** the architectural change shipped on 2026-08-07; what remains is running an existing script, one GRANT, and one gold view.

**One limitation is deliberate, not a gap.** `expiration_date` is **shipper-entered**, not parsed from the document, and **68 of the 443 shared COIs in the sample have none** (15%). Per the carrier PO this is by design — the auction must open and verify the document, because a carrier could enter any date and even machine-reading the file could not establish that it is valid. **So CPDR-424 "COI Data Parsing" would not close this gap.** For the report this means a blank expiration is meaningful output — *"this auction has not reviewed this document yet"* — arguably its most actionable signal, rather than a defect to suppress.

## §2a · PostgreSQL

*Column delta · `ShipperCarrierDocument` (database `company_documents`, instance `platform`) — the only schema change in the design; independent of which report route is chosen*

| Column | Type | Change | Null | Default / backfill |
| --- | --- | --- | --- | --- |
| `updated_at` | `DateTime` | 🟢 added | y | `default=now()`, `onupdate=now()`; **not retroactive** — answers "when did this auction last review this document" only from ship date forward |
| `created_at` | `DateTime` | 🔵 reused | n | the only write timestamp on the row today, which is why `updated_at` is needed |
| `expiration_date` | `DateTime` | 🔵 reused | see note | report column 6. Shipper-entered; blank for 68/443 shared COIs. Model declares `nullable=False` but migration `d5f4426bee2f` created it nullable — verify live schema before relying on NOT NULL |
| `is_shipper_tracked` | `Boolean` | 🔵 reused | n | added by `0fa047cb2bea`; gates compliance display, **not** `expiration_date` (SCP-14905) |
| `status` | `String` | 🔵 reused | n | `'active'` is half the sharing predicate |

*Data delta (no schema change) · `CarrierDocument` (database `company_documents`)*

| Column | Type | Change | Null | Default / backfill |
| --- | --- | --- | --- | --- |
| `type` | `String` | 🟡 backfill required | y | added `0fa047cb2bea` (2026-08-07). **NULL for every earlier document until `scripts/backfill_document_metadata.py` runs.** Report filters `type = 'cargo_insurance'` exactly — the sibling enum member `certificate_of_insurance` = `"certificate_insurance"` is referenced by no route |
| `versions_create_time_list` | `String` | 🟡 backfill required | y | comma-joined version timestamps; report column 5 = `element_at(split(…, ','), -1)`. Same NULL exposure |
| `document_status` | `String` | 🔵 reused | y | `'active'` is the other half of the predicate |
| `visibility` | `String` | 🔵 reused | y | `'public'` + no wrapper row = shared without the auction ever engaging |

*Read-only access delta · database `company_documents` on replica `platform-replica-analytics`*

| Grant | Type | Change | Null | Default / backfill |
| --- | --- | --- | --- | --- |
| `CONNECT` on `company_documents` for role `analytics` | grant | 🟢 added | — | role already exists instance-level (`platform/locals.tf:23-30`) |
| `SELECT` on `CarrierDocument`, `ShipperCarrierDocument` for `analytics` | grant | 🟢 added | — | two tables only; nothing else |

## §2c · Databricks gold view

*New materialized view · `gold_{env}_catalog.internal_reports.AaagLmpCoiTracker` — the design's primary deliverable. One row per (auction, carrier).*

| Column | Type | Change | Source (silver) | Note |
| --- | --- | --- | --- | --- |
| `auction_name` | `string` | 🟢 added | `posting_core.company.name` | scoped by `external_parent_company_id`; parameterise on parent **name** so it serves all LMP partners, not just AAAG |
| `carrier_name` | `string` | 🟢 added | `production_platform.users_company.name` | 526 distinct in the sample |
| `status` | `string` | 🟢 added | `compliance_network_compliancenetworklink.status` | sample holds only `verified` \| `suspended` \| `under_review` — 3 of the model's 5 values. Filter must be explicit (**Q3**) |
| `coi` | `string` | 🟢 added | `carrierdocument` + `shippercarrierdocument` | `'Yes'`/`'No'`. Predicate copied verbatim from `shipper_document_route.py:427-438`: `type='cargo_insurance' AND document_status='active' AND (visibility='public' with no wrapper OR wrapper.status='active')` |
| `upload_date` | `date` | 🟢 added | `carrierdocument.versions_create_time_list` | `element_at(split(…, ','), -1)`; string parse with an ordering assumption (**Q2**) |
| `expiration_date` | `date` | 🟢 added | `shippercarrierdocument.expiration_date` | the **wrapper's** DateTime, *not* `CarrierDocument.expiration_date` (a nullable String copied from blob metadata) |
| six silver tables | — | 🔵 reused | — | all exist, all wired into the `dev` + `prod` pipeline globs; every join carries `__END_AT IS NULL AND _ab_cdc_deleted_at IS NULL` |
| bronze ingestion | — | 🔵 reused | Airbyte CDC | `propagate_fully` + new-column backfill — no pipeline change needed |
| `user_ids` / row-level security | — | 🔴 removed | — | not applicable: this is an **internal** report in `internal_reports`, not a customer-embedded dashboard, so the `user_ids` RLS column the `executive_dashboards` gold views carry is deliberately absent |

## §4 · REST API & DTO

**No delta.** The recommended design adds and changes no endpoint, DTO field or published event anywhere in the fleet.

| Surface | Change | Note |
| --- | --- | --- |
| `GET /{company_id}/compliance-statuses` | 🔵 reused | read for its sharing predicate only; **not called** by the report — the warehouse reads the replicated tables. Healthy in prod (8× 200 / 0 errors in the 3 days to 2026-09-03) |
| `GET /{company_id}/coi-report` | 🔴 removed | proposed by the 2026-09-02 record; **no longer needed** |
| Django internal "list a shipper's network" endpoint | 🔴 removed | proposed by the 2026-09-02 record; **no longer needed** |
| `posting-backend` Reporting report type + Temporal schedule | 🔴 removed | proposed by the 2026-09-02 record; over-engineering against the actual ask |
| any service-to-service read of the gold view | 🔴 removed | **not possible.** A fleet-wide audit (2026-09-03) found nothing in the fleet runs SQL against Databricks — no `jdbc:databricks`, no `DatabricksJDBC`, no `databricks-sql-connector`, no `/api/2.0/sql/statements`, and no repo declares a Databricks SDK. `bi-databricks-backend` is an **OAuth + embed-token broker only** (`POST /oidc/v1/token`, `GET /api/2.0/lakeview/dashboards/{id}/published/tokeninfo`) and never reads data; the only programmatic consumption pattern is an embedded AI/BI dashboard querying from the browser via `@databricks/aibi-client`. The view is therefore consumed by a human or by an embed — never by a backend |

## Where it lives & how it's wired

| Aspect | Detail |
| --- | --- |
| report service | `ml-central-data-storage` · `transformations/gold/Internal_Reports/Aaag_Lmp_Coi_Tracker.py` (new; template `Posted_Vs_Dispatched_Price_Gap.py`, RE-975) |
| report tests | `ml-central-data-storage` · `transformations/tests/gold/` · pattern `tests/gold/AAAG/gold_gx_aaag.py:27-50` → results to `audit_{env}_catalog` |
| column-owning service | `company-documents` · `api/models/{carrier_document,shipper_carrier_document}.py` · migration `0fa047cb2bea` · backfill `scripts/backfill_document_metadata.py` |
| branch to work from | `company-documents` → **`origin/production`** (`4269067`); `ml-central-data-storage` → **`origin/dev`** (`e63fe62`). Both repos' `master` is ~4 months stale and lacks this feature |
| instance | `platform` (POSTGRES_18, `db-custom-16-40960`) · DB `company_documents` **and** DB `production` — same instance, **different databases** |
| BI replica | `platform-replica-analytics` (read replica of the `platform` instance) · 6 vCPU · `max_standby_streaming_delay = -1` · carries both databases |
| BI tool | Metabase — the internal-only support instance (`nginx-internal`; owner recorded as a podLabel in its helm values) |
| ingestion | Airbyte CDC → GCS Parquet → `bronze_{env}_catalog` · `production` at `0 0 2,14` UTC, `company_documents` at `0 15 2,14` UTC |
| pipeline refresh | Databricks `ml_central_data_storage_refresh` · `0 0 11,16` GMT · `UNPAUSED` in prod, **`PAUSED`** in staging |
| consumption | human (Databricks UI / Metabase) or an embedded AI/BI dashboard via the token broker — **no backend read path exists fleet-wide** |
| topic | none — no Pub/Sub delta |
| ES index | none — no Elasticsearch delta |
| jira home | the report belongs under epic **RE-976 "Reporting Requests"**; SCP-15147 correctly owns the `company-documents` backfill prerequisite |

## Backfill — runbook, rollout & estimate

**No new script is needed.** `scripts/backfill_document_metadata.py` shipped to `origin/production` on 2026-08-07 (`bcbf0f9`) and is idempotent and re-runnable — "rows already in sync are simply rewritten with identical values". Its own docstring defines a four-step rollout, and **the first three are already done**:

| Step (from the script's docstring) | State |
| --- | --- |
| 1. `--scan-only` before the migration merges | — no evidence either way, and moot now: the migration is applied |
| 2. Apply the migration (columns exist, all NULL) | ✅ `3ddc910`, migration `0fa047cb2bea`, 2026-08-07 |
| 3. Deploy the write-path sync (new/updated documents fill their own columns) | ✅ `apply_document_metadata` at `carrier_document_route.py:82`, `shipper_document_route.py:78` |
| 4. **`--dry-run`, review, then a real run for the historical rest** | ❌ **no evidence this ever ran in prod** — three independent 60-day log searches, all severities, zero hits |

So the work is **step 4 only**. What follows is the runbook, because that is the part that does not exist yet.

### Step 0 — measure first (read-only, ~5 min)

Against the `company_documents` database (ideally the `platform-replica-analytics` replica, so it costs prod nothing). This is the number that turns the estimate below from a range into a figure:

```sql
-- Overall coverage. MISSING_FILTER in the script is (type IS NULL AND filename IS NULL).
SELECT count(*)                                                        AS total_rows,
       count(*) FILTER (WHERE type IS NULL)                            AS type_null,
       count(*) FILTER (WHERE type IS NULL AND filename IS NULL)       AS script_backlog,
       count(*) FILTER (WHERE versions_create_time_list IS NULL)       AS upload_date_null,
       count(*) FILTER (WHERE created_at <  '2026-08-07')              AS pre_writepath,
       count(*) FILTER (WHERE created_at >= '2026-08-07')              AS post_writepath
FROM   "CarrierDocument";

-- Sanity: the write path should have kept everything after 2026-08-07 populated.
-- A non-zero count here means the write-path sync itself has a gap — investigate
-- before backfilling, because the backfill would mask it.
SELECT count(*) FROM "CarrierDocument"
WHERE  created_at >= '2026-08-07' AND type IS NULL;

-- What the report will actually see today, before any backfill.
SELECT count(*) AS active_cargo_insurance_docs
FROM   "CarrierDocument"
WHERE  type = 'cargo_insurance' AND document_status = 'active';
```

`script_backlog` is the row count the script will process. `pre_writepath` bounds the true historical backlog — if it is far larger than `type_null`, the backfill has in fact already run and the blocker dissolves.

### Step 1 — the runbook (real flags, verified against source)

Run from the repo root **inside the service's own pod**, so it inherits the pod service account and env (it reads GCS blob metadata per row):

```bash
# 1. Read-only scan: no schema, no rows touched. Prints the four tallies.
python -m scripts.backfill_document_metadata --scan-only

# 2. Writes then rolls back. Review the tallies again before committing anything.
python -m scripts.backfill_document_metadata --dry-run

# 3. The real run. Commits per batch (default 200) and logs
#    "Committed through document id <N>" so an interrupted run is resumable.
python -m scripts.backfill_document_metadata --batch-size 200
```

Constraints the CLI enforces: `--fill-missing` and `--scan-only` are mutually exclusive, and `--limit` is only valid with `--fill-missing`.

### Step 2 — verification

**The four tallies** the script logs on every mode (capture all four in the ticket, before and after):

1. `document_status` values seen — the compliance query only counts `'active'`.
2. Non-null counts per mapped column — *a systematically-zero column means the field mapping is wrong*, which is the failure this tally exists to catch.
3. Unmapped blob-metadata keys — `create_time` and `relation_id` are deliberately unmapped (exact duplicates of `created_at`/`id`); anything else is new and needs a decision.
4. `expiration_date` format buckets (`empty` / `iso_date` / `iso_datetime` / `other`) — decides whether the optional `ALTER COLUMN … TYPE date` follow-up is safe.

**The oracle.** The attached sample is the independent check no tally can give: it lists **443 COI=Yes** and **447 upload dates** across 49 AAAG auctions, compiled by hand from the UI (i.e. from GCS, the source of truth). After the backfill, the AAAG-scoped reconciliation must land near those figures. Because the auction/network side lives in a different database, run that reconciliation **in Databricks** once replication has caught up — it is the same six-table join the gold view uses. A materially lower number means the backfill is still incomplete; a *higher* number is expected and fine (the sample omits `not_verified` carriers, see Q3).

### `--fill-missing` — a separate mode, not step 4

The script's docstring is explicit that this is **"a separate follow-up mode, not a step of the rollout above"**, so it is deliberately not numbered with the three commands above. It has two distinct uses, and for a large backlog it can *replace* the full run rather than follow it:

```bash
# Reports how many rows are still unfilled, then fills only those. Bounded and repeatable.
python -m scripts.backfill_document_metadata --fill-missing --limit 500
```

| Use it… | Why |
| --- | --- |
| **After** a full run | Closes gaps left by an interrupted run or transient GCS errors — one short run instead of a full re-scan. |
| **Instead of** a full run | For a large backlog this is the safer shape: each invocation is bounded by `--limit`, so you take the work in short, attended chunks that contend with live traffic for minutes rather than hours, and you can stop between them. |

> ⚠️ **It is not a complete substitute — check Step 0's two counts first.** `--fill-missing` selects on `MISSING_FILTER`, which is `type IS NULL` **AND** `filename IS NULL` (both conditions). The full run rewrites **every** row. So a document with `type IS NULL` but a populated `filename` is **invisible to `--fill-missing`** and only the full run would fix it. That is exactly why the Step 0 query reports `type_null` and `script_backlog` separately:
> - `type_null == script_backlog` → `--fill-missing` alone is sufficient; prefer it for a large backlog.
> - `type_null > script_backlog` → the difference is rows only a **full run** will repair. Do the full run.
>
> Two further quirks: `--limit` bounds rows *selected*, not rows filled; and a row the script cannot fill still matches `MISSING_FILTER`, so it is re-selected on every later run — meaning `Unfilled rows remaining` can plateau above zero rather than reach it. Treat a stable plateau as "these rows have no usable blob", not as an incomplete run.

### Rollout strategy

> ℹ️ **Low-risk by construction, with one operational caveat.**
>
> 1. **Step 0 measurement** on the replica — read-only, tells you whether there is any work at all.
> 2. **`--scan-only`**, then **`--dry-run`**, capturing the four tallies each time. Stop here if tally 2 shows a systematically-zero column.
> 3. **Choose the shape from Step 0's counts.** If `type_null == script_backlog` and the backlog is large, take it in bounded `--fill-missing --limit N` chunks. Otherwise do the **full real run off-peak** in a single pod, watching the `Committed through document id` line for progress.
> 4. **`--fill-missing --limit N`** afterwards either way, to close gaps from blob-read errors. Repeat until the count stops falling — a plateau above zero means those rows have no usable blob, which is an answer, not a failure.
> 5. **Re-run the Step 0 queries** and paste before/after into the ticket. Only then estimate the gold view.
>
> **Why the risk is low:** GCS stays the source of truth and the script only ever *mirrors* into columns that are currently NULL, so it is additive; it is explicitly idempotent, so a re-run is safe; it commits per batch, so an interruption loses at most one batch and is resumable; and blob-less or erroring rows are counted and skipped rather than failing the run.
>
> **No rollback is needed or defined** — and none is really possible, since the pre-state is "NULL" and the post-state is a copy of GCS. If the mapping were wrong, the fix is to correct the mapping and re-run, not to revert. That is exactly what `--scan-only`/`--dry-run` are for.
>
> **Operational caveat:** the script runs *inside a serving pod* and does one sequential GCS metadata read per row, on a service that uses sync SQLAlchemy and sync GCS calls inside async handlers, with a DB pool of 10 (+20 overflow). A long run therefore contends with live traffic. Mitigate by running off-peak, keeping `--batch-size` at the default 200, and — for a large backlog — chunking with `--fill-missing --limit` across several short runs rather than one long one.
>
> **Risk:** the only real one is *not doing this*. Until it runs, `type` is NULL for pre-2026-08-07 documents, and a `type = 'cargo_insurance'` report omits them **silently** rather than failing — a compliance report that under-reports while looking correct.

### Rough estimate

Runtime is bound by one GCS `list_single_blob` call per row, issued sequentially, so it scales linearly with `script_backlog` from Step 0. In-cluster metadata reads realistically run 50–150 ms each (~7–20 rows/s):

| `script_backlog` (rows with `type IS NULL`) | Expected real-run wall time |
| --- | --- |
| ~1 000 | under 3 min |
| ~10 000 | 10–25 min |
| ~50 000 | 45 min – 2 h |
| ~200 000 | 3–8 h — chunk it with `--fill-missing --limit` |

**Engineering effort — 0.5 day**, unchanged from the estimate table below, and independent of the row count:

| Activity | Effort |
| --- | --- |
| Step 0 measurement queries | ~15 min |
| `--scan-only` + `--dry-run` + reading the four tallies | ~1 h |
| Real run (attended; wall time per the table above, mostly waiting) | ~1–2 h attended |
| `--fill-missing` passes to zero | ~30 min |
| Post-run verification + writing the before/after into the ticket | ~1 h |
| **Total** | **~0.5 day** (+ unattended wall time if the backlog is large) |

There is **no development work** in this line item — the script, the columns and the write path all already exist. It is an operational task, and the right owner is the `company-documents` maintainer who wrote them.

## Rollout

> ⚠️ **§5 · rollout & sequencing**
>
> Prove the data before materialising anything — a silently under-reporting compliance report is worse than none.
>
> 1. **Measure the backfill (blocks every estimate).** Follow [Backfill — runbook, rollout & estimate](#backfill--runbook-rollout--estimate): Step 0 measurement queries, then `--scan-only`, `--dry-run`, and the real run, recording the four tallies before and after. **~0.5 day of effort**, plus unattended wall time if the backlog is large.
> 2. **Grant + add the Metabase data source** on `platform-replica-analytics` (parallel with step 1 — each is the other's proof). This **unblocks the report owner this week** and immediately measures backfill coverage against the sample's **443 COI=Yes / 447 upload dates**.
> 3. **Verify silver reality.** `DESCRIBE` the six silver tables and `SELECT MAX(_ingest_time)`, checking every column in [Columns required on the Databricks side](#columns-required-on-the-databricks-side) — in particular `type`, `versions_create_time_list`, `expiration_date`, `is_shipper_tracked`, `external_parent_company_id`, `user_management_id`. Airbyte's `propagate_fully` says they should; silver's schema is auto-inferred, so prove it.
> 4. **Answer Q1–Q4** (expiration gap · which upload date · which statuses · AAAG-only vs all LMP partners) — these change column semantics, not plumbing.
> 5. **Add `ShipperCarrierDocument.updated_at`** — independent, do it early, it is not retroactive.
> 6. **Build the gold view in `dev`**, reconcile against the sample (49 auctions / ~659 rows / ~443 Yes), add the GX suite, then promote to `prod`. **Do not plan a staging sign-off** — staging's library globs exclude `company_documents_platform`, `production_platform` and AAAG gold, and its refresh job is `PAUSED`.
>
> **Risk:**
> - **Backfill unevidenced** — three independent 60-day searches found nothing; NULL `type` makes documents *silently absent* rather than flagged. Steps 1–2 exist for this.
> - **Silver column presence unproven** — silver declares no schema and its only data-quality check is `__START_AT IS NOT NULL`, so nothing would have alerted if the 2026-08 columns never arrived.
> - **No staging validation path** — validate in `dev`, promote to `prod`.
> - **Freshness is ~12–24h end to end** (Airbyte twice daily → Databricks twice daily). Ample for a weekly report; do not describe the output as live.
> - **Delivery is a queryable table, not a pushed file — and that is structural, not a gap in this repo.** A fleet-wide audit (2026-09-03) found **no service-to-service query path into Databricks anywhere**: the only programmatic consumption pattern is an embedded AI/BI dashboard, and `ml-central-data-storage` has no email or export mechanism either. So the view is read by a human in the Databricks UI or via an embed — no backend can consume it. A Databricks SQL subscription or export job is a follow-up, not part of this estimate, and would be the first of its kind in the fleet.
> - **The sample itself is partly corrupt** — one expiration cell reads literally `Oct`, five rows say COI=`No` yet carry dates. Reconciliation must expect the *sample* to be wrong in those places, not the query.
> - **Tier 2 must not become permanent** — the Metabase grant leaves a manual lookup step. Label it a bridge, or the days-of-support-work problem simply returns in a faster form.
