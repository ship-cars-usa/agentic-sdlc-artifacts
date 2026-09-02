# COI report for AAAG - feasibility and effort

`SCP-15147` · **proposed** · 2026-09-02 · hristo.savov@ship.cars · groomed 2026-09-02

**Services:** `company-documents`, `platform-backend`, `posting-backend`, `ml-central-data-storage`, `bi-databricks-backend`

**Legend:** 🟢 added · 🟡 updated · 🔴 removed · 🔵 reused

![Design diagram](./diagram.svg)

## Context

AAAG want a weekly report listing, for every carrier in each America's Auto Auction carrier network, whether the carrier uploaded **and shared** a COI (cargo insurance) with that auction, and if so its upload date and expiration date. Support produced it once by hand over several days. The stated motivation is HQ's, not AAAG's: there is no visibility into whether the auctions are checking carrier documents at all.

The report is feasible with **no new data capture** — all four facts are queryable in SQL today, on columns SCP-14900/14901 added and SCP-14902 backfills. Two constraints shape the design. First, the network list (`ComplianceNetworkLink`, platform-backend's Postgres) and the document facts (`CarrierDocument` / `ShipperCarrierDocument`, company-documents' own Postgres) live in **separate database instances**, so no single statement can produce the report — one side must call the other. Second, the *interactive* document-listing path is GCS-driven (one bucket listing per carrier), which is exactly why the denormalized columns exist; the report must use them and stay pure-SQL.

A read-only prod log cross-check on 2026-09-02 turned up one blocker and one caveat:

- **No evidence the SCP-14902 backfill has run in prod.** Two independent 60-day searches — by pod name and by the script's own log strings — returned nothing. Without it, `CarrierDocument.type` and `versions_create_time_list` are NULL for every pre-existing document, so a `type='cargo_insurance'` report returns almost nothing while *looking* correct.
- **The data foundation went live essentially today.** `GET /{shipper}/compliance-statuses` returned 404 on 18 of 18 prod calls up to 2026-08-31, then 200 after the 2026-09-02 07:49 UTC container restart. Nothing has been exercised against real AAAG data.
- The `filter_to_granted_carriers` fail-open path is **not** currently firing (zero occurrences in 14 days), though the code path stands and the new endpoint must not inherit it.

Two scope decisions are still open and change the column list, not the plumbing. **"AAAG's carrier network" is ~15+ networks**, one per child auction company, each with its own per-document expiration dates — so the report is per-auction, grouped under the AAAG parent. And **the AC measures carriers, not auctions**: the auction-side review signals (`is_shipper_tracked`, whether an expiration date was entered, `internal_notes`, `document_request_status`, `last_review_date`) are what would actually answer HQ, and they cost little on the same join.

Delivery is chosen between two existing rails rather than built: a Databricks gold view on AAAG's already-embedded dashboard, or a new report type on `posting-backend`'s production self-service scheduled-report product (Temporal Schedules, per-customer cadence and recipients, CSV → `attachment-backend` → `media-proxy` signed link → SendGrid). The Django `send_report` pattern was considered and rejected — it is on-demand only, with no per-customer schedule and no recipient model.

## §2a · PostgreSQL

*Column delta · `ShipperCarrierDocument` (DB `company-documents`)*

| Column | Type | Change | Null | Default / backfill |
| --- | --- | --- | --- | --- |
| `updated_at` | `DateTime` | 🟢 added | y | `default=now()`, `onupdate=now()` — **not retroactive**; "last reviewed by the auction" only starts accruing once shipped |
| `expiration_date` | `DateTime` | 🔵 reused | n | The per-shipper expiry the auction typed in — the report's expiration column |
| `is_shipper_tracked` | `Boolean` | 🔵 reused | n | `server_default=false` — auction-side review signal |
| `internal_notes` | `String` | 🔵 reused | n | Per-shipper note — auction-side review signal |
| `created_at` | `DateTime` | 🔵 reused | n | Only existing write timestamp; why `updated_at` is needed |

*Column delta · `CarrierDocument` (DB `company-documents`)*

| Column | Type | Change | Null | Default / backfill |
| --- | --- | --- | --- | --- |
| `type` | `String` | 🟡 updated | y | No schema change — **must be backfilled**. NULL rows are invisible to a `type='cargo_insurance'` filter, i.e. silently absent from the report |
| `versions_create_time_list` | `String` | 🟡 updated | y | No schema change — **must be backfilled**. Comma-joined per-version create times; last element = the report's upload date |
| `document_status` | `String` | 🔵 reused | y | `active` \| `requested` \| `request_cancelled` \| `archived` — the report must distinguish these, not collapse them |
| `visibility` | `String` | 🔵 reused | y | `public` \| `private` — half of the sharing predicate |

*Column delta · `ComplianceNetworkLink` (DB `platform`, platform-backend)*

| Column | Type | Change | Null | Default / backfill |
| --- | --- | --- | --- | --- |
| `shipper` / `carrier` | FK `Company` | 🔵 reused | n | `unique_together` — one link per (auction, carrier); the report's grouping key |
| `document_request_status` | `CharField` | 🔵 reused | n | `not_requested` \| `requested` \| `granted` — auction-side signal |
| `last_review_date` | `DateTime` | 🔵 reused | y | Auction-side signal |

## §4 · REST API & DTO

*New batch report endpoint · `company-documents`*

| Field | Type | Change | JSON name | Subscriber action |
| --- | --- | --- | --- | --- |
| — | route | 🟢 added | `GET /{company_id}/coi-report?carrier_ids=…` | Pure SQL, zero GCP calls; reuses the `compliance-statuses` sharing predicate verbatim |
| `carrier_user_management_id` | `str` | 🟢 added | `carrier_user_management_id` | Join key — the `C-…` UMID |
| `document_id` | `int \| None` | 🟢 added | `document_id` | `None` when the carrier has no usable COI |
| `document_status` | `str \| None` | 🟢 added | `document_status` | Lets the consumer separate "never requested" / "requested, not uploaded" / "archived" |
| `visibility` | `str \| None` | 🟢 added | `visibility` | Public-vs-shared provenance |
| `upload_date` | `str \| None` | 🟢 added | `upload_date` | Last element of `versions_create_time_list`; matches the UI's "Uploaded:" label |
| `expiration_date` | `str \| None` | 🟢 added | `expiration_date` | **Ungated** — unlike `compliance-statuses`, returned even when not tracked |
| `is_shipper_tracked` | `bool` | 🟢 added | `is_shipper_tracked` | Auction-side review signal |
| `has_internal_notes` | `bool` | 🟢 added | `has_internal_notes` | Auction-side review signal |
| `wrapper_created_at` | `str \| None` | 🟢 added | `wrapper_created_at` | When the auction first touched the document |

*New internal network-list endpoint · `platform-backend`*

| Field | Type | Change | JSON name | Subscriber action |
| --- | --- | --- | --- | --- |
| — | route | 🟢 added | `GET /api/internal/network/carriers/?shipper_id=…` | Enumerates a shipper's network; the existing `document_statuses` can only *filter* a caller-supplied list |
| `user_management_id` | `str` | 🔵 reused | `user_management_id` | Same shape the existing internal endpoint returns |
| `document_request_status` | `str` | 🔵 reused | `document_request_status` | — |
| `status` | `str` | 🟢 added | `status` | Network status: `verified` \| `under_review` \| `suspended` \| … |
| `last_review_date` | `str \| None` | 🟢 added | `last_review_date` | Auction-side review signal |

*Unchanged, consumed as-is*

| Field | Type | Change | JSON name | Subscriber action |
| --- | --- | --- | --- | --- |
| — | route | 🔵 reused | `GET /{company_id}/compliance-statuses` | Left alone — the FE depends on its current contract; do **not** add flags to it |
| — | DTO | 🔵 reused | `V1EmailNotificationAttachmentDto{name,fileURL,contentType}` | Delivery by reference (URL), not raw bytes; `notification-backend` fetches and attaches |

## Where it lives & how it's wired

| Aspect | Detail |
| --- | --- |
| service | `company-documents` · single-module FastAPI — **branch from `origin/production`, not `master`** (master is stale at `54d57c6`, 2026-04-28) |
| file | `api/routes/shipper_document_route.py:396-456` (pattern + sharing predicate) · `api/models/shipper_carrier_document.py:9-19` · new alembic migration |
| instance | `company-documents` · DB `company-documents` (own logical DB, `DATABASE_NAME` default) |
| service | `platform-backend` · Django 6.0.4 / Python 3.12 |
| file | `api/internal/network.py:24-39` (sibling endpoint) · `api/compliance_network/common.py:149-190` (queryset) · `compliance_network/models.py:11-80` |
| instance | `platform` · Cloud SQL Postgres |
| service | `posting-backend` · Quarkus + Temporal (Option B1) |
| file | `.../reporting/schedules/impl/ScheduleServiceImpl.java:44-77` · `.../workflows/impl/CreateReportWorkflowImpl.java` · `.../ReportingServiceImpl.java:152,211,225` · `posting-frontend/src/pages/Reporting/` |
| service | `ml-central-data-storage` · Databricks Asset Bundle (Option A) |
| table | `gold_{env}_catalog.aaag.aaag_coi_compliance_report` ← silver `company_documents_platform.{carrierdocument,shippercarrierdocument}` + `production_platform.{compliance_network_compliancenetworklink,users_company}`, all `__END_AT IS NULL` |
| join key | `C-…` user-management id, shared across `users_company.user_management_id`, `posting_core.company.external_id`, and company-documents' `carrier_id`/`shipper_id` |
| scope key | AAAG parent `external_parent_company_id = 'C-JCJSA2NLCNBDVIMMMM6Z43I52I'` → ~15+ child auction companies |
| topic | none — no event delta; delivery is REST (`notification-backend`) or a Databricks dashboard |

## Rollout

> ⚠️ **§5 · rollout & sequencing**
>
> Data-before-query, then producer-before-consumer. The first step is not optional: every option returns a near-empty report until it is done.
>
> 1. **Confirm and run the SCP-14902 backfill in prod.** `SELECT count(*) FROM "CarrierDocument" WHERE type IS NULL`, then `scripts/backfill_document_metadata.py --dry-run`, review the three tallies, re-run for real. There is no log evidence it has run.
> 2. **Verify the warehouse in parallel** — `DESCRIBE` the four silver tables and `MAX(_ingest_time)` on each; check whether the prod refresh job is still `pause_status: PAUSED` and who owns bronze ingestion. **This decides Option A vs B1.**
> 3. Add `ShipperCarrierDocument.updated_at` (forward-only, **not retroactive**) — every week it slips is a week of "last reviewed" that can never be recovered.
> 4. Run the one-off `utils/aaag/coi_report.py` probe to answer AAAG this week and settle the `versions_create_time_list` parse plus the `document_status`/`origin` edge cases.
> 5. Then the durable path: `coi-report` + the Django network-list endpoint **first** (producers), then the posting report type (consumer). Option A has no cross-service contract and can proceed independently once step 2 passes.
>
> **Risk:**
> - Backfill not run → `type`/`versions_create_time_list` NULL → report silently under-reports rather than failing. Highest risk in the design.
> - Silver schema is 100% auto-inferred with a single `__START_AT IS NOT NULL` check, and the document transformations predate the SCP-14900 columns by ~4 months — Option A is unsafe until step 2 passes.
> - `filter_to_granted_carriers` fails open on upstream error (not firing today) — the new endpoint must not inherit it.
> - Branching `company-documents` from `master` would silently revert SCP-14900/14901/14902/14904/14905.
> - Option B1 puts a compliance query in the posting domain — a boundary stretch to flag with that service's owner.
