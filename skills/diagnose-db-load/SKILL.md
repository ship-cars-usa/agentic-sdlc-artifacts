---
name: diagnose-db-load
description: >
  Evaluate Cloud SQL (Postgres) database load, find CPU / latency spikes, trace
  them to a root cause, and map that root cause to the module and code snippet that
  triggers it. Use when asked to investigate a database spike, high CPU, slow
  queries, "why was the DB slow / pegged", a load or latency anomaly, to find the
  culprit / root cause of a Cloud SQL performance event, or to point a DB spike at
  the offending code. Drives GCP Cloud Monitoring + Cloud Logging read-only via
  db_load_probe.py and gcloud, then greps the platform-backend source.
---

# diagnose-db-load

A read-only investigation harness for Cloud SQL (Postgres) load spikes on GCP. The
driver is **`<REPO>/skills/diagnose-db-load/db_load_probe.py`** (`<REPO>` = the
`agentic-sdlc-artifacts` checkout; the source it greps is `<SHIP_CARS_DIR>`, i.e.
`$SHIP_CARS_DIR` or `<WORKSPACE>/ship-cars-usa`, and `--repo-root` defaults to it). It
pulls Cloud Monitoring time series using the gcloud
CLI's own token, so every call is a read-only GET — no DB credentials, no mutations.

The method has a spine you follow top to bottom; do **not** stop at "the slowest
query" — that is the trap this skill exists to avoid (see Gotchas).

**Two rules that override everything below**, both learned from real misdiagnoses:

1. **Never size a load from a saturated window.** `cpu_est` has no run-queue term, so once
   CPU pegs, time spent waiting for a core is counted as CPU used and every attribution
   inflates past what is physically possible. `window` prints a capacity line, warns when
   CPU ≥ 85%, and flags a total > 100% — believe those warnings and re-measure earlier.
2. **An instance hosts many databases.** "Query X burned the CPU" is not a root cause until
   `window` [2] shows that X's *database* dominates the box. Always check the co-tenant
   ranking before naming a culprit; a big `exec` that is mostly `io_wait` is a latency
   problem for that tenant, not a CPU cause for the instance.

## Prerequisites

```bash
# gcloud must be authenticated and pointed at the project (prod is the default here).
gcloud auth print-access-token >/dev/null   # if this errors -> user runs: ! gcloud auth login
python3 --version                            # stdlib only; no pip installs needed
```

If `print-access-token` fails with a reauth error, it cannot be fixed non-interactively —
ask the user to run `! gcloud auth login` in the prompt.

## Run (agent path) — the investigation, in order

Every command below was run this session against `shipcars-platform-prod`.

**1. Pick the instance.** There are many; the biggest primary is usually the target.
```bash
python3 <REPO>/skills/diagnose-db-load/db_load_probe.py instances
```

**2. Characterise load + locate the spike.** Stats + the 8 hottest buckets.
```bash
python3 <REPO>/skills/diagnose-db-load/db_load_probe.py cpu --instance platform --hours 24
# -> avg=10.2% p95=34.5% max=83.5%; TOP SPIKE BUCKET 2026-07-28T20:05:59Z 83.5%
```

**3. (Optional) See the standing-cost queries.** Two rankings — they differ:
```bash
# load hogs (latency x frequency):
python3 <REPO>/skills/diagnose-db-load/db_load_probe.py queries --instance platform --rank total
# genuinely slow per call (min 50 calls):
python3 <REPO>/skills/diagnose-db-load/db_load_probe.py queries --instance platform --rank latency
```

**4. Deep-dive the spike window.** THE key step. Take the hot bucket from step 2 and
bracket it by a few minutes.
```bash
python3 <REPO>/skills/diagnose-db-load/db_load_probe.py window --instance platform \
    --start 2026-07-28T19:58:00Z --end 2026-07-28T20:08:00Z
```
It opens with the **capacity header** — tier, vCPU, `CAPACITY = vCPU × window_seconds`,
`1 backend = 1 core = N%`, and observed CPU avg/max. Read that first: it is the yardstick
for everything under it, and it raises a **SATURATION WARNING** at CPU ≥ 85% telling you the
magnitudes below are inflated. Then four sections:

- **[1] decomposition** — a query with high `io%` was a **VICTIM** (starved by I/O it
  didn't cause); high `cpu%` is a **CONTRIBUTOR**. In one verified run the top-exec
  `DISTINCT epod_load` query was 2% CPU / 98% io-wait — a victim, not the culprit.
  The `%cap` column is each query's share of the whole instance, and the footer sums
  **Σ cpu_est vs capacity**. A total > 100% is *arithmetically impossible* and means the
  window is saturated — discard the magnitudes, re-measure earlier. A total under ~40% of
  observed CPU means most of the CPU is non-query (autovacuum, background) or unsampled.
- **[2] load by database (co-tenancy)** — **check this before naming any culprit.** One
  instance hosts many databases; this ranks them and reports the top tenant's share of
  capacity and of CPU actually in use. Tenants whose time is mostly `io_wait` are marked
  `<- mostly io_wait, not CPU`: they have a latency problem, they are not your CPU cause.
  In the verified core 2026-08-17 event this printed `posting 42.9% of capacity, ~83% of
  CPU in use` against `quote_manager 0.1%`, which settled a co-tenant hypothesis in one
  command.
- **[3] correlation** — the real spike signal is `active` backends and `read_ops`
  jumping together (2→27 active, 2k→70k read-ops here), with a trailing `wal_MB` /
  `write_ops` burst as the work commits. That shape = a **concurrency burst / thundering
  herd**, not one slow statement.
- **[4] source** — which `application_name` pool the active backends came from.
  `Unknown` = Django/psycopg (doesn't set application_name); named pools = the Java services.

Two failure shapes, and how [1]+[2] tell them apart:

| Signature | Reading |
|---|---|
| `Σ cpu_est` small vs observed CPU, `active` backends spiking | **concurrency burst** — no single query explains it; find the fan-out |
| `Σ cpu_est` explains most of observed CPU, one database dominates [2] | **query-cost problem** — that tenant's query shape is the cause |

**4b. Rule out a hung interactive session / long-open transaction.** `window` is built to
find a *query* cause, so it deliberately shows only `state=active` backends — which means it
is **blind to the opposite failure mode**: a human at a CLI/GUI (`psql`, DataGrip, IntelliJ,
pgAdmin…) who left a transaction open. That transaction blocks autovacuum → dead tuples pile
up → every *other* query scans more rows → instance-wide CPU climbs with no single query to
blame. Run `sessions` on the SAME window before you commit to a "concurrency burst" verdict:
```bash
python3 <REPO>/skills/diagnose-db-load/db_load_probe.py sessions --instance core \
    --start 2026-07-24T06:45:00Z --end 2026-07-24T08:25:00Z --resolution 60s
# -> [1] flags interactive clients (psql/DataGrip/IntelliJ) among the connection sources
#    [2] per-minute idle_in_txn + interactive backends + oldest_transaction_age
#    [3] VERDICT: "HUNG INTERACTIVE SESSION SUSPECTED — held a txn open ~85 min (06:52->08:16)"
```
The signature (verified on the `core` 2026-07-24 08:05 spike, 95%+): an interactive
`application_name` present the whole time, and `oldest_transaction_age` that **climbs
monotonically then snaps back to ~0 the minute the session is killed** (there, 478→101,800→0
at 08:17, exactly when CPU recovered).

**The discriminator is monotonicity, not run length.** Run length alone over-fires badly: any
workload that opens a fresh short transaction per unit of work (per page, per batch, per
request) keeps `oldest_transaction_age` above the floor for an hour without ever holding *one*
transaction open. `sessions` now reports `age rising in N% of steps` and requires **≥90%**,
calibrated on two verified events on the same instance:

| Event | run | rising | verdict |
|---|---|---|---|
| core 2026-07-24 hung DataGrip session | 85 min | **100%** | HUNG SESSION — correct |
| core 2026-08-17 report workload | 50 min | **56%** | NOT a held transaction — correct |

Do not lower that threshold. At 0.6 the 2026-08-17 report workload is reported as a hung
session, which is how that event was initially misdiagnosed. When the check rejects, the output
points you at `window` [2] instead — churn like this is a query-cost problem, and an interactive
client merely being *connected* is not evidence of anything.

Default is `--hours 24 @ 300s` (a fast standing check that also catches app pools that leak a
long transaction); bracket a known spike with `--start/--end --resolution 60s` for the detail.

**5. Trace the trigger in the logs.** Metrics prove *what* (concurrency from pool X);
logs name *which job*. `pg_stat_activity` is gone for past events — use Cloud Logging.
```bash
# 5a. find how the app is labelled:
gcloud logging read 'timestamp>="2026-07-28T20:00:00Z" AND timestamp<="2026-07-28T20:05:00Z" AND resource.labels.container_name=~"platform"' \
  --project=shipcars-platform-prod --limit=1 --format="value(resource.type, resource.labels)"

# 5b. which containers are noisy in the window (web vs celery worker):
gcloud logging read '<same time filter> AND resource.type="k8s_container" AND resource.labels.namespace_name="production"' \
  --project=shipcars-platform-prod --limit=1000 --format="value(resource.labels.container_name)" | sort | uniq -c | sort -rn

# 5c. THE money query — per-minute rate of batch-ish tasks, server-filtered so it
#     stays under the 1000-line cap, then bucketed locally. A scheduled fan-out shows
#     up as one task type spiking in the :00 minute. (Found: 501 expire_load + 216
#     expire_offer enqueued at 20:00 -> the thundering herd.)
gcloud logging read 'timestamp>="2026-07-28T19:55:00Z" AND timestamp<="2026-07-28T20:07:00Z" AND resource.type="k8s_container" AND resource.labels.container_name="celery-dynamic" AND (textPayload=~"expire_load|expire_offer|generate_bol|archive_posting" OR jsonPayload.message=~"expire_load|expire_offer|generate_bol|archive_posting")' \
  --project=shipcars-platform-prod --limit=1000 --format=json > /tmp/tasks.json
python3 -c "
import json,re,collections
d=json.load(open('/tmp/tasks.json'))
g=collections.defaultdict(collections.Counter)
for e in d:
    m=e.get('textPayload') or (e.get('jsonPayload') or {}).get('message') or ''
    if 'received' not in m: continue
    mm=re.search(r'tasks\.(\w+)\[',m)
    if mm: g[e['timestamp'][11:16]][mm.group(1)]+=1
for minute in sorted(g):
    print(minute, dict(g[minute]))
"
```

**6. Map the root cause to code.** Once step 5 names a celery task (or step 4 names a
table/query), locate the source: the task *definition*, the *enqueue site* (the real
trigger — a loop, `transaction.on_commit`, or `eta=`), and whether it's beat-scheduled.
This is a local grep of `platform-backend`; no GCP needed. Verified this session:
```bash
# task -> definition + fan-out site + schedule:
python3 <REPO>/skills/diagnose-db-load/db_load_probe.py locate --task expire_load
# -> def epod/tasks.py:340; enqueue epod/models.py:3959 via apply_async(eta=self.expiration_time)
#    => NOT beat-swept: each load pre-schedules its own expiry at its expiration_time,
#       so loads expiring on the same top-of-hour all fire at once (the fan-out).
python3 <REPO>/skills/diagnose-db-load/db_load_probe.py locate --task post_processing
# -> def epod/tasks.py:205; enqueued transaction.on_commit PER attachment at
#    api/order_api.py:358/364/373 (attachment + parent + sub) => scales with upload volume.

# SQL table -> Django model + suspect querysets (best-effort; Django table = <app>_<model>):
python3 <REPO>/skills/diagnose-db-load/db_load_probe.py locate --table epod_load
# -> class Load epod/models.py:2127 (LoadManager); DISTINCT querysets at epod/models.py:5811,5838
```
Pass `--repo <name>` / `--repo-root <path>` for other services (default: `platform-backend`
under `<SHIP_CARS_DIR>`). `--task` accepts either `expire_load` or the dotted
`epod.tasks.expire_load`.

## Gotchas (the traps that make a naive answer wrong)

- **`execution_time` is WALL-CLOCK, not CPU** — despite the `us{CPU}` unit label. A
  query with a huge `execution_time` may have spent it all *waiting* on I/O or locks.
  Never conclude "this query burned the CPU" from exec-time alone. `window`'s
  decomposition (`cpu_est = exec − io_wait − lock`) is what separates cause from victim.
- **`cpu_est` is ALSO wrong once the instance saturates.** It has no term for run-queue
  wait, so time a query spent queued for a core is counted as CPU it consumed. Verified on
  core 2026-08-17: in the pegged window `cpu_est` credited `posting` with **10,519 CPU-s
  against 7,680 available — 137% of the instance**, physically impossible. The same
  measurement 30 minutes earlier, unsaturated, gave the true 42.9%. **Always size a load on
  a window where observed CPU stayed below ~85%**; use the saturated window only for shape.
  `window` computes this check and prints `>>> IMPOSSIBLE (>100%)` when it trips.
- **Co-tenancy: one instance, many databases.** `core` hosts `posting`, `quote_manager`,
  `load_recommender`, `invoices`, `temporal`, `trip_planner` and more. A per-query ranking
  cannot tell you whether the top query's service caused the event or was a victim of a
  noisy neighbour — only `window` [2] can. And judge a co-tenant by `cpu_est`, not `exec`:
  `quote_manager`'s Envers `SELECT MAX("rev")` shows ~11,000 s/day of exec-time, which looks
  alarming, but it is mostly `io_wait` — a latency problem for that service that contributes
  almost nothing to instance CPU.
- **"Slowest query" ≠ cause of a CPU spike.** Query Insights is *sampled / top-N*: in
  the verified event the sum of *all* per-query CPU-est over the window was <1% of
  instance capacity while CPU sat at 95%. The spike was concurrency, invisible in any
  single-query ranking. Always corroborate with `window` [2] (active backends + read-ops).
- **One backend = one core.** A single Postgres query cannot exceed `1/vCPU` of
  instance-wide CPU (≈6% on a 16-vCPU box) without parallel workers. If instance CPU is
  high but no single query can explain it arithmetically, the cause is *many concurrent*
  queries — look for a fan-out.
- **Two different resource types / label names.** Query Insights metrics
  (`.../insights/...`) live on `cloudsql_instance_database`, filtered by
  `resource.labels.resource_id`. Standard metrics (cpu, disk, backends, wal) live on
  `cloudsql_database`, filtered by `resource.labels.database_id`. Both values equal
  `PROJECT:INSTANCE`. The driver handles this; know it if you hand-write a filter.
- **`groupByFields` format** is `metric.labels.<name>` / `resource.labels.<name>`
  (note plural `labels`) and is a *repeated* query param — a bad value 400s with
  "improperly formatted".
- **`application_name = Unknown`** means the client didn't set it — which is the
  **Django/psycopg default**, i.e. platform-backend and the celery workers. The Java
  services show as `PostgreSQL JDBC Driver` / `vertx-pg-client`. Attribution to
  "the Django pool" is inference, not proof.
- **A CPU spike with no query to blame may be a *held transaction*, not load.** `window`
  only surfaces `active` backends, so it cannot see an `idle in transaction` session; a human
  at `psql`/DataGrip/IntelliJ (or an app pool that skipped a commit) holding a transaction open
  blocks autovacuum and inflates every query's scan cost. Use `sessions` (step 4b). The tell is
  `oldest_transaction_age` sustained ≥15 min **and rising in ≥90% of steps** — duration alone
  is not enough, because per-request transactions produce a long elevated run that bounces
  rather than climbs. Note the hard limit: metrics show *that* a client held a long
  txn, never *which* session or SQL — `pg_stat_activity` is live-only. Catch it live with
  `SELECT pid,usename,application_name,state,xact_start,query FROM pg_stat_activity WHERE
  state='idle in transaction' ORDER BY xact_start;` or prevent recurrence with
  `idle_in_transaction_session_timeout`.
- **Cloud Logging caps at 1000 lines** and the Django app does **not** populate
  `httpRequest`, and messages land in `textPayload` *or* `jsonPayload.message`
  inconsistently. Filter server-side to get under the cap (counts are otherwise floors),
  and read both payload fields when parsing.
- **`locate`: "no beat entry" ≠ "not scheduled".** A fan-out can come from `.delay()`
  in a request path (per user action), from `transaction.on_commit` (per row created —
  scales with volume), or from `apply_async(eta=...)` (pre-scheduled per row — a
  thundering herd when many rows share the same ETA, e.g. top-of-hour expirations).
  Read the enqueue snippet to tell which; the count spiking at `:00` points at ETA
  clustering, not a beat loop.
- **`locate --table` is best-effort.** Django's default table name is `<app>_<model>`
  with *no* `db_table=` in the source, so there's nothing to grep for the binding — the
  command falls back to the model class by naming convention and lists the app's
  `.distinct()`/`annotate(Count)` querysets. Treat its output as leads to read, not a
  definitive "this line emitted that SQL" (the ORM assembles SQL dynamically).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Reauthentication failed. cannot prompt` | Token expired; ask user to run `! gcloud auth login`. |
| `does not specify a valid combination of metric and monitored resource` | Wrong resource label — insights metrics use `resource_id`, standard metrics use `database_id`. |
| `groupByFields ... improperly formatted` | Use `metric.labels.<name>` (plural), not `metric.label.<name>`; don't pass an empty value. |
| `window` [1] empty but [2] shows load | Query Insights sampled nothing that window — rely on [2]/[3] + logs; the spike may be non-query CPU (autovacuum, parallel workers). |
| Blocked: "unrecognized gcloud verb" | The read-only guard mis-parsed a compound shell line; run the gcloud read on its own line. |
```
