#!/usr/bin/env python3
"""
db_load_probe.py — evaluate Cloud SQL (Postgres) load, find CPU/latency spikes,
and trace them to a root cause using Cloud Monitoring (read-only).

No third-party deps. Auth is borrowed from the gcloud CLI
(`gcloud auth print-access-token`), so all calls are read-only GETs.

Subcommands (run in this order when investigating):
  instances                     list Cloud SQL instances (name, tier, vCPU, disk)
  cpu       --instance X        CPU-utilization timeline + stats, auto-flags spike buckets
  queries   --instance X        top queries by total exec-time OR avg latency (Query Insights)
  window    --instance X --start ISO --end ISO
                                the spike deep-dive: [1] per-query CPU/io/lock decomposition
                                (cause vs victim, each as % of instance capacity)
                                [2] load BY DATABASE (co-tenancy — which tenant owns the load)
                                [3] instance-load correlation (backends, read/write-ops, WAL)
                                [4] by-application connection source
  sessions  --instance X        hung-CLI / long-open-transaction check: interactive
                                clients (psql/pgAdmin/...), idle-in-transaction backends,
                                and oldest_transaction_age — the spike `window` can't see

Examples:
  python3 db_load_probe.py instances
  python3 db_load_probe.py cpu     --instance platform --hours 24
  python3 db_load_probe.py queries --instance platform --hours 24 --rank latency
  python3 db_load_probe.py window  --instance platform \
      --start 2026-07-28T19:55:00Z --end 2026-07-28T20:10:00Z

KEY GOTCHA baked into `window`: the perquery/aggregate `execution_time` metric is
WALL-CLOCK time (despite the `us{CPU}` unit label), so it does NOT prove CPU burn.
`window` splits it into cpu_est = exec - io_wait - lock so you can tell a query that
BURNED the CPU from one that was a VICTIM (high io-wait) of contention it didn't cause.

SECOND GOTCHA, and the reason `window` prints a capacity line and a saturation warning:
cpu_est has NO TERM FOR RUN-QUEUE WAIT (time spent waiting for a core). Once the
instance saturates, scheduling delay is silently counted as CPU used, so every
attribution inflates — it can and does exceed 100% of the instance, which is
arithmetically impossible and the tell that the window is unusable for sizing.
=> Size the load on a window where observed CPU stayed below ~85%; use the saturated
   window only to read the SHAPE of the load. `window` now computes the
   Sigma(cpu_est) vs vCPU x window_seconds check for you and flags an impossible total.

THIRD GOTCHA: a Cloud SQL instance hosts MANY databases. "Query X burned CPU" is not a
root cause until you know whether X's DATABASE dominates the instance or whether a
co-tenant does — otherwise you can't separate "this service caused it" from "this
service is a victim of a noisy neighbour". `window` [2] attributes load by database,
and marks any tenant whose time is mostly io_wait (a latency problem for that service,
not a CPU cause for the instance).
"""
import argparse, datetime, json, os, subprocess, sys, urllib.error, urllib.parse, urllib.request

# --- Workspace-relative path resolution (no hardcoded user paths) ----------
# This script lives at <REPO>/skills/diagnose-db-load/db_load_probe.py.
#   REPO_ROOT      = two dirs up from this script's own dir (…/skills/<name>/ -> REPO)
#   WORKSPACE_ROOT = $AGENTIC_SDLC_WORKSPACE or the parent of REPO_ROOT
#   SHIP_CARS_DIR  = $SHIP_CARS_DIR or <WORKSPACE_ROOT>/ship-cars-usa  (--repo-root default)
_SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(_SKILL_DIR))
WORKSPACE_ROOT = os.environ.get("AGENTIC_SDLC_WORKSPACE") or os.path.dirname(REPO_ROOT)
SHIP_CARS_DIR = os.environ.get("SHIP_CARS_DIR") or os.path.join(WORKSPACE_ROOT, "ship-cars-usa")

API = "https://monitoring.googleapis.com/v3/projects"
INS = "cloudsql.googleapis.com/database/postgresql/insights"   # resource: cloudsql_instance_database
DB  = "cloudsql.googleapis.com/database"                       # resource: cloudsql_database


def gcloud_out(cmd, **kw):
    """Run a gcloud command and return stdout. On expired auth or any gcloud
    failure, print a friendly reauth hint and exit(1) instead of dumping a raw
    Python traceback (CalledProcessError)."""
    try:
        return subprocess.check_output(cmd, **kw)
    except FileNotFoundError:
        print("ERROR: `gcloud` not found on PATH. Install the Google Cloud CLI, then run "
              "`gcloud auth login`.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("ERROR: gcloud command failed (auth may have expired). Run `gcloud auth login` "
              "and confirm access to the project, then retry.", file=sys.stderr)
        sys.exit(1)


def token():
    return gcloud_out(["gcloud", "auth", "print-access-token"]).decode().strip()


def default_project():
    return gcloud_out(
        ["gcloud", "config", "get-value", "project"], stderr=subprocess.DEVNULL).decode().strip()


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def window_bounds(args):
    if args.start and args.end:
        return args.start, args.end
    now = datetime.datetime.now(datetime.timezone.utc)
    return iso(now - datetime.timedelta(hours=args.hours)), iso(now)


def fetch(project, tk, metric, res_filter, aligner,
          reducer="REDUCE_NONE", group=None, align="300s", start=None, end=None):
    """List time series. Handles pagination. Returns [] on HTTP error (prints body)."""
    params = {
        "filter": f'metric.type="{metric}" AND {res_filter}',
        "interval.startTime": start, "interval.endTime": end,
        "aggregation.alignmentPeriod": align,
        "aggregation.perSeriesAligner": aligner,
        "aggregation.crossSeriesReducer": reducer,
        "view": "FULL", "pageSize": "2000",
    }
    qs = urllib.parse.urlencode(params)
    for g in (group or []):                       # groupByFields is a repeated field
        qs += "&" + urllib.parse.urlencode({"aggregation.groupByFields": g})
    out, url = [], f"{API}/{project}/timeSeries?{qs}"
    while url:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tk}"})
        try:
            data = json.load(urllib.request.urlopen(req))
        except urllib.error.HTTPError as e:
            print(f"  [api-error {metric}] {e.read().decode()[:300]}", file=sys.stderr)
            return []
        out.extend(data.get("timeSeries", []))
        npt = data.get("nextPageToken")
        url = f"{API}/{project}/timeSeries?{qs}&pageToken={urllib.parse.quote(npt)}" if npt else None
    return out


def pnum(p):
    v = p["value"]
    return float(v.get("int64Value", v.get("doubleValue", 0)))


def resid(project, instance):
    return f"{project}:{instance}"


# ---------------------------------------------------------------- capacity (vCPU)
# vCPU count is the denominator for EVERY "is this arithmetically possible?" check:
#   - one backend = one core, so a single query can't exceed 1/vCPU of instance CPU
#   - total CPU available in a window = vcpu * window_seconds
# Without it you cannot tell a real attribution from run-queue inflation, so it is
# resolved once and cached rather than left to the reader to eyeball off the tier string.
SHARED_CORE = {"db-f1-micro": 1, "db-g1-small": 1}
_VCPU_CACHE = {}


def tier_vcpu(tier):
    """vCPU count from a Cloud SQL tier string. None when it can't be determined."""
    if not tier:
        return None
    if tier in SHARED_CORE:
        return SHARED_CORE[tier]
    parts = tier.split("-")                       # db-custom-<vcpu>-<mem_mb>
    if len(parts) >= 4 and parts[1] == "custom" and parts[2].isdigit():
        return int(parts[2])
    return None


def instance_vcpu(project, instance):
    """Look up vCPU for one instance (cached). Returns (vcpu|None, tier|None)."""
    key = (project, instance)
    if key in _VCPU_CACHE:
        return _VCPU_CACHE[key]
    try:
        tier = subprocess.check_output(
            ["gcloud", "sql", "instances", "describe", instance, "--project", project,
             "--format=value(settings.tier)"], stderr=subprocess.DEVNULL).decode().strip()
    except subprocess.CalledProcessError:
        tier = None
    _VCPU_CACHE[key] = (tier_vcpu(tier), tier)
    return _VCPU_CACHE[key]


def window_seconds(s, e):
    """Length of an ISO8601 window in seconds; None if unparseable."""
    try:
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        return (datetime.datetime.strptime(e, fmt) - datetime.datetime.strptime(s, fmt)).total_seconds()
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------- subcommands
def cmd_instances(args):
    # gcloud is the source of truth for the inventory; vCPU is derived from the tier
    # because the CPU-share arithmetic downstream is meaningless without it.
    out = gcloud_out(
        ["gcloud", "sql", "instances", "list", "--project", args.project,
         "--format=value(name,databaseVersion,region,settings.tier,settings.dataDiskSizeGb)"]
    ).decode().splitlines()
    rows = []
    for line in out:
        f = line.split("\t")
        if len(f) < 5:
            continue
        name, ver, region, tier, disk = f[:5]
        vc = tier_vcpu(tier)
        rows.append((name, ver, region, tier, vc, disk))
    print(f"{'NAME':<34} {'VERSION':<14} {'REGION':<13} {'TIER':<20} {'vCPU':>5} {'DISK_GB':>8}")
    for name, ver, region, tier, vc, disk in sorted(rows):
        vcs = str(vc) if vc else "?"
        print(f"{name:<34} {ver:<14} {region:<13} {tier:<20} {vcs:>5} {disk:>8}")
    print("\nvCPU is the denominator for every capacity check: one backend = one core, so a single")
    print("query cannot exceed 1/vCPU of instance CPU, and a window holds vCPU x seconds of CPU time.")


def cmd_cpu(args):
    tk = token(); s, e = window_bounds(args)
    rf = f'resource.labels.database_id="{resid(args.project, args.instance)}"'
    series = fetch(args.project, tk, f"{DB}/cpu/utilization", rf, "ALIGN_MEAN",
                   align=args.resolution, start=s, end=e)
    pts = sorted((p["interval"]["endTime"], pnum(p)) for ss in series for p in ss["points"])
    if not pts:
        print("no CPU samples (check --instance / auth / window)"); return
    vals = sorted(v for _, v in pts)
    pct = lambda q: vals[min(len(vals) - 1, int(len(vals) * q))]
    print(f"WINDOW {s} -> {e}  instance={args.instance}  samples={len(pts)} @ {args.resolution}")
    print(f"  avg={sum(vals)/len(vals)*100:5.1f}%  min={vals[0]*100:5.1f}%  "
          f"p50={pct(.5)*100:5.1f}%  p95={pct(.95)*100:5.1f}%  p99={pct(.99)*100:5.1f}%  "
          f"max={vals[-1]*100:5.1f}%")
    print("\nTOP 8 SPIKE BUCKETS (feed the hottest one's timestamp into `window`):")
    for t, v in sorted(pts, key=lambda x: -x[1])[:8]:
        print(f"  {t}  {v*100:5.1f}%")


def cmd_queries(args):
    tk = token(); s, e = window_bounds(args)
    rf = f'resource.labels.resource_id="{resid(args.project, args.instance)}"'
    grp = ["metric.labels.query_hash", "metric.labels.querystring", "resource.labels.database"]
    ex = fetch(args.project, tk, f"{INS}/perquery/execution_time", rf,
               "ALIGN_DELTA", "REDUCE_SUM", grp, "86400s", s, e)
    la = fetch(args.project, tk, f"{INS}/perquery/latencies", rf,
               "ALIGN_DELTA", "REDUCE_SUM", grp, "86400s", s, e)
    agg = {}
    for ss in ex:
        l = ss["metric"]["labels"]; h = l.get("query_hash", "")
        d = agg.setdefault(h, {"q": l.get("querystring", ""),
                               "db": ss["resource"]["labels"].get("database", "?"),
                               "exec": 0.0, "calls": 0, "latsum": 0.0})
        d["exec"] += sum(pnum(p) for p in ss["points"])
    for ss in la:
        h = ss["metric"]["labels"].get("query_hash", "")
        d = agg.setdefault(h, {"q": "", "db": "?", "exec": 0.0, "calls": 0, "latsum": 0.0})
        for p in ss["points"]:
            dv = p["value"].get("distributionValue")
            if dv:
                c = int(dv.get("count", 0)); d["calls"] += c; d["latsum"] += c * float(dv.get("mean", 0))
    rows = list(agg.values())
    clean = lambda q: " ".join(q.split())[:150]
    print(f"WINDOW {s} -> {e}  instance={args.instance}  digests={len(rows)}\n")
    if args.rank == "latency":
        rows = [d for d in rows if d["calls"] >= args.min_calls]
        rows.sort(key=lambda d: -(d["latsum"] / d["calls"]) if d["calls"] else 0)
        print(f"TOP {args.top} BY AVG LATENCY / EXECUTION (min {args.min_calls} calls) — genuinely slow")
        for i, d in enumerate(rows[:args.top], 1):
            print(f"{i:2}. avg={d['latsum']/d['calls']/1000:9.1f}ms  calls={d['calls']:>9,}  "
                  f"total={d['exec']/1e6:7.1f}s  db={d['db']}\n    {clean(d['q'])}")
    else:
        rows.sort(key=lambda d: -d["exec"])
        print(f"TOP {args.top} BY TOTAL EXEC-TIME (latency x frequency) — load hogs")
        for i, d in enumerate(rows[:args.top], 1):
            avg = d["latsum"] / d["calls"] / 1000 if d["calls"] else 0
            print(f"{i:2}. total={d['exec']/1e6:9,.1f}s  calls={d['calls']:>10,}  "
                  f"avg={avg:8.1f}ms  db={d['db']}\n    {clean(d['q'])}")


def _delta_by_key(series, keyfn):
    out = {}
    for ss in series:
        out[keyfn(ss)] = out.get(keyfn(ss), 0) + sum(pnum(p) for p in ss["points"])
    return out


def cmd_window(args):
    tk = token(); s, e = args.start, args.end
    if not (s and e):
        sys.exit("window requires --start and --end (ISO8601, e.g. 2026-07-28T20:00:00Z)")
    rid = f'resource.labels.resource_id="{resid(args.project, args.instance)}"'
    did = f'resource.labels.database_id="{resid(args.project, args.instance)}"'
    span = "900s"
    grp = ["metric.labels.query_hash", "metric.labels.querystring"]

    # --- 1. per-query CPU vs io-wait vs lock decomposition: cause vs victim ---
    ex = _delta_by_key(fetch(args.project, tk, f"{INS}/perquery/execution_time", rid,
                             "ALIGN_DELTA", "REDUCE_SUM", grp, span, s, e),
                       lambda x: (x["metric"]["labels"].get("query_hash", ""),
                                  x["metric"]["labels"].get("querystring", "")))
    io = _delta_by_key(fetch(args.project, tk, f"{INS}/perquery/io_time", rid,
                             "ALIGN_DELTA", "REDUCE_SUM", grp, span, s, e),
                       lambda x: x["metric"]["labels"].get("query_hash", ""))
    lk = _delta_by_key(fetch(args.project, tk, f"{INS}/perquery/lock_time", rid,
                             "ALIGN_DELTA", "REDUCE_SUM", grp, span, s, e),
                       lambda x: x["metric"]["labels"].get("query_hash", ""))
    # Capacity + saturation context. cpu_est has NO term for run-queue (waiting for a
    # core), so once the instance pegs, scheduling delay is silently counted as CPU used
    # and every attribution inflates. Establish that up front so [1]/[2] are read correctly.
    vcpu, tier = instance_vcpu(args.project, args.instance)
    if getattr(args, "vcpu", None):
        vcpu, tier = args.vcpu, f"{tier or '?'} (vCPU overridden)"
    wsec = window_seconds(s, e)
    capacity = vcpu * wsec if (vcpu and wsec) else None
    cpu_vals = [pnum(p) for ss in fetch(args.project, tk, f"{DB}/cpu/utilization", did,
                                        "ALIGN_MEAN", align="60s", start=s, end=e)
                for p in ss["points"]]
    cpu_avg = sum(cpu_vals) / len(cpu_vals) if cpu_vals else None
    cpu_max = max(cpu_vals) if cpu_vals else None

    print(f"WINDOW {s} -> {e}  instance={args.instance}")
    if vcpu:
        print(f"  tier={tier}  vCPU={vcpu}  window={wsec/60:.0f}min  "
              f"=> CAPACITY {capacity:,.0f} CPU-seconds   (1 backend = 1 core = {100/vcpu:.1f}% max)")
    else:
        print(f"  tier={tier or '?'}  vCPU=UNKNOWN — capacity checks disabled "
              f"(pass --vcpu N to enable)")
    if cpu_avg is not None:
        print(f"  observed CPU: avg {cpu_avg*100:.1f}%  max {cpu_max*100:.1f}%")
    saturated = cpu_max is not None and cpu_max >= 0.85
    if saturated:
        print("\n  !! SATURATION WARNING — CPU reached "
              f"{cpu_max*100:.0f}% in this window, so cpu_est is NOT trustworthy here.")
        print("     cpu_est = exec - io_wait - lock has no run-queue term, so time a query spent")
        print("     WAITING FOR A CORE is counted as CPU it used. Attributions below are inflated,")
        print("     possibly past 100%. Re-run `window` on an EARLIER, unsaturated window to size")
        print("     the load; use this one only to read its SHAPE (which queries, cause vs victim).")

    print("\n[1] PER-QUERY TIME DECOMPOSITION (seconds) — cpu_est = exec - io_wait - lock")
    print("    high io%% => VICTIM of I/O contention;  high cpu%% => CPU CONTRIBUTOR")
    hdr_cap = f" {'%cap':>6}" if capacity else ""
    print(f"    {'exec':>8} {'io_wait':>8} {'lock':>8} {'cpu_est':>8} {'cpu%':>5}{hdr_cap}  query")
    rows = []
    for (h, q), exv in ex.items():
        exs, ios, lks = exv / 1e6, io.get(h, 0) / 1e6, lk.get(h, 0) / 1e6
        rows.append((exs, ios, lks, max(0.0, exs - ios - lks), q))
    shown = sorted(rows, key=lambda r: -r[0])[:args.top]
    for exs, ios, lks, cpu, q in shown:
        pctc = cpu / exs * 100 if exs else 0
        capcol = f" {cpu/capacity*100:5.1f}%" if capacity else ""
        print(f"    {exs:8.1f} {ios:8.1f} {lks:8.1f} {cpu:8.1f} {pctc:4.0f}%{capcol}"
              f"  {' '.join(q.split())[:60]}")

    # The arithmetic sanity check the reader would otherwise have to do by hand — and the
    # one that catches run-queue inflation, because an impossible total is self-evident.
    if capacity:
        tot_cpu = sum(r[3] for r in rows)
        share = tot_cpu / capacity * 100
        print(f"\n    TOTAL cpu_est across ALL {len(rows)} sampled digests: {tot_cpu:,.1f} CPU-s "
              f"= {share:.1f}% of the {capacity:,.0f} CPU-s available")
        if share > 100:
            print("    >>> IMPOSSIBLE (>100%): this attribution cannot be literal. It is run-queue")
            print("        inflation from a saturated window. Discard these magnitudes and re-measure")
            print("        on a window where observed CPU stayed below ~85%.")
        elif cpu_avg and share < cpu_avg * 100 * 0.4:
            print("    >>> Queries explain <40% of observed CPU. The rest is non-query CPU (autovacuum,")
            print("        background workers) or unsampled digests — Query Insights is top-N/sampled.")
            print("        Corroborate with [3] active-backends and [4] connection source.")

    # --- 2. BY DATABASE: co-tenancy. An instance hosts many DBs; a spike attributed to
    # one query means little until you know whether that query's DATABASE dominates the
    # box, or whether a co-tenant does. This is what distinguishes "this service caused
    # it" from "this service is a victim of a noisy neighbour".
    print("\n[2] LOAD BY DATABASE (co-tenancy) — which tenant on this instance owns the load")
    dbgrp = ["resource.labels.database"]

    def _db_totals(metric):
        agg = {}
        for ss in fetch(args.project, tk, f"{INS}/perquery/{metric}", rid,
                        "ALIGN_DELTA", "REDUCE_SUM", dbgrp, span, s, e):
            db = ss["resource"]["labels"].get("database", "?")
            agg[db] = agg.get(db, 0.0) + sum(pnum(p) for p in ss["points"]) / 1e6
        return agg

    dex, dio, dlk = _db_totals("execution_time"), _db_totals("io_time"), _db_totals("lock_time")
    if not dex:
        print("    (no per-database samples in this window)")
    else:
        hc = f" {'%cap':>6}" if capacity else ""
        print(f"    {'exec':>10} {'io_wait':>9} {'cpu_est':>10}{hc}  database")
        drows = []
        for db, exv in dex.items():
            cpu = max(0.0, exv - dio.get(db, 0.0) - dlk.get(db, 0.0))
            drows.append((cpu, exv, dio.get(db, 0.0), db))
        for cpu, exv, iov, db in sorted(drows, reverse=True):
            capcol = f" {cpu/capacity*100:5.1f}%" if capacity else ""
            io_note = "  <- mostly io_wait, not CPU" if exv and iov / exv > 0.5 else ""
            print(f"    {exv:10.1f} {iov:9.1f} {cpu:10.1f}{capcol}  {db}{io_note}")
        top = sorted(drows, reverse=True)[0]
        rest = sum(r[0] for r in sorted(drows, reverse=True)[1:])
        if capacity:
            top_share = top[0] / capacity * 100
            print(f"\n    top tenant '{top[3]}' = {top_share:.1f}% of instance capacity; "
                  f"all others combined = {rest/capacity*100:.1f}%")
            # Only derive "share of CPU in use" when the inputs are physically possible.
            # In a saturated window the numerator is inflated, so the ratio is meaningless
            # and printing it anyway would launder a bad number into a confident one.
            if saturated or top_share > 100:
                print("    (share-of-CPU-in-use not derived: inflated window — but note the RANKING")
                print("     and the io_wait split stay valid, so co-tenancy is still readable here.)")
            elif cpu_avg and cpu_avg > 0:
                print(f"    => '{top[3]}' is ~{top[0]/capacity/cpu_avg*100:.0f}% "
                      f"of the CPU actually in use ({cpu_avg*100:.1f}% observed)")
        print("    NB: a co-tenant that is large in `exec` but mostly io_wait is a LATENCY problem")
        print("        for its own service, not a CPU cause for this instance.")

    # --- 3. instance-load correlation timeline (the reliable spike signal) ---
    print("\n[3] INSTANCE-LOAD CORRELATION (per-minute) — active backends + read-ops are the truth")
    m = {"cpu": (f"{DB}/cpu/utilization", "ALIGN_MEAN", did),
         "backends": (f"{DB}/postgresql/num_backends", "ALIGN_MEAN", did),
         "read_ops": (f"{DB}/disk/read_ops_count", "ALIGN_DELTA", did),
         "write_ops": (f"{DB}/disk/write_ops_count", "ALIGN_DELTA", did),
         "txn/m": (f"{DB}/postgresql/transaction_count", "ALIGN_DELTA", did),
         "wal_MB": (f"{DB}/postgresql/write_ahead_log/written_bytes_count", "ALIGN_DELTA", did)}
    cols = {}
    for name, (metric, aligner, rf) in m.items():
        series = fetch(args.project, tk, metric, rf, aligner, align="60s", start=s, end=e)
        by_min = {}
        for ss in series:
            for p in ss["points"]:
                by_min[p["interval"]["endTime"][11:16]] = by_min.get(p["interval"]["endTime"][11:16], 0) + pnum(p)
        cols[name] = by_min
    active = {}
    for ss in fetch(args.project, tk, f"{DB}/postgresql/num_backends_by_state", did,
                    "ALIGN_MEAN", "REDUCE_SUM", ["metric.labels.state"], "60s", s, e):
        if ss["metric"]["labels"].get("state") == "active":
            for p in ss["points"]:
                active[p["interval"]["endTime"][11:16]] = pnum(p)
    mins = sorted(cols["cpu"])
    print(f"    {'min':5} {'cpu%':>6} {'active':>7} {'backends':>9} {'read_ops':>9} {'write_ops':>9} {'txn/m':>7} {'wal_MB':>7}")
    for t in mins:
        print(f"    {t:5} {cols['cpu'].get(t,0)*100:6.1f} {active.get(t,0):7.0f} "
              f"{cols['backends'].get(t,0):9.0f} {cols['read_ops'].get(t,0):9.0f} "
              f"{cols['write_ops'].get(t,0):9.0f} {cols['txn/m'].get(t,0):7.0f} {cols['wal_MB'].get(t,0)/1e6:7.1f}")

    # --- 4. which client drove it (application_name) ---
    print("\n[4] ACTIVE-CONNECTION SOURCE (num_backends_by_application, avg over window)")
    print("    NB: 'Unknown' = clients that don't set application_name (Django/psycopg default)")
    ap = {}
    for ss in fetch(args.project, tk, f"{DB}/postgresql/num_backends_by_application", did,
                    "ALIGN_MEAN", "REDUCE_SUM", ["metric.labels.application"], "60s", s, e):
        lab = ss["metric"]["labels"].get("application", "") or "(unset)"
        vals = [pnum(p) for p in ss["points"]]
        if vals:
            ap[lab] = sum(vals) / len(vals)
    for lab, v in sorted(ap.items(), key=lambda x: -x[1])[:8]:
        print(f"    {v:6.1f}  {lab}")


# ---------------------------------------------------------------- sessions (hung CLI / long txn)
# application_name substrings that mean "a human at an interactive client", NOT an app pool.
# App pools seen on the fleet: "PostgreSQL JDBC Driver", "vertx-pg-client", "Debezium General",
# "Unknown" (Django/psycopg default). Anything matching below is a person, and a person who
# leaves a transaction open is the classic invisible CPU spike (blocks autovacuum -> bloat).
INTERACTIVE_HINTS = ("psql", "pgadmin", "dbeaver", "datagrip", "tableplus", "navicat",
                     "pgcli", "jetbrains", "intellij", "beekeeper", "postico", "adminer")


def _is_interactive(app):
    a = (app or "").lower()
    return any(h in a for h in INTERACTIVE_HINTS)


def _grouped(project, tk, metric, rf, label_key, aligner, s, e, align="60s"):
    """Return {label: {minute: value}} for a metric grouped by one label."""
    out = {}
    for ss in fetch(project, tk, metric, rf, aligner, "REDUCE_SUM",
                    [f"metric.labels.{label_key}"], align, s, e):
        lab = ss["metric"]["labels"].get(label_key, "") or "(unset)"
        d = out.setdefault(lab, {})
        for p in ss["points"]:
            d[p["interval"]["endTime"][11:16]] = pnum(p)
    return out


def cmd_sessions(args):
    """Detect the hung-interactive-session / long-open-transaction signature that a
    CPU spike hides: an interactive client (psql/pgAdmin/...) holding a transaction open,
    which blocks autovacuum and bloats every other query's scans. The tells `window` misses:
    an interactive application_name present, `idle in transaction` backends, and — the
    cleanest — vacuum/oldest_transaction_age climbing then snapping back to ~0 when the
    session is killed. pg_stat_activity is live-only, so this is the best after-the-fact view."""
    tk = token(); s, e = window_bounds(args)
    did = f'resource.labels.database_id="{resid(args.project, args.instance)}"'
    res = args.resolution

    cpu = {}
    for ss in fetch(args.project, tk, f"{DB}/cpu/utilization", did, "ALIGN_MEAN", align=res, start=s, end=e):
        for p in ss["points"]:
            cpu[p["interval"]["endTime"][11:16]] = pnum(p)
    age = {}
    for ss in fetch(args.project, tk, f"{DB}/postgresql/vacuum/oldest_transaction_age",
                    did, "ALIGN_MAX", align=res, start=s, end=e):
        for p in ss["points"]:
            age[p["interval"]["endTime"][11:16]] = pnum(p)
    waits = {}
    for ss in fetch(args.project, tk, f"{DB}/postgresql/backends_in_wait",
                    did, "ALIGN_MEAN", align=res, start=s, end=e):
        for p in ss["points"]:
            waits[p["interval"]["endTime"][11:16]] = pnum(p)
    by_state = _grouped(args.project, tk, f"{DB}/postgresql/num_backends_by_state",
                        did, "state", "ALIGN_MEAN", s, e, res)
    by_app = _grouped(args.project, tk, f"{DB}/postgresql/num_backends_by_application",
                      did, "application", "ALIGN_MEAN", s, e, res)

    idle_txn = by_state.get("idle in transaction", {})
    interactive = {}                                   # minute -> summed interactive backends
    for app, series in by_app.items():
        if _is_interactive(app):
            for t, v in series.items():
                interactive[t] = interactive.get(t, 0) + v

    mins = sorted(cpu)
    if not mins:
        print("no samples (check --instance / auth / window)"); return
    print(f"WINDOW {s} -> {e}  instance={args.instance}  @ {res}")

    # [1] the application_name roster, interactive clients flagged
    print("\n[1] CONNECTION SOURCES (peak backends over window)  —  <<< = interactive/human client")
    peaks = sorted(((max(v.values()) if v else 0, app) for app, v in by_app.items()), reverse=True)
    for pk, app in peaks[:12]:
        flag = "  <<< INTERACTIVE" if _is_interactive(app) else ""
        print(f"    {pk:6.1f}  {app}{flag}")

    # A HUNG transaction is SUSTAINED, not big: a healthy DB sits at age~0 with the odd
    # single-bucket blip (a transaction that spanned one sample). The discriminator is the
    # longest consecutive run of elevated buckets, NOT the peak value — a run keeps the
    # median high, so any relative-to-median test would (wrongly) call the hung case normal.
    res_sec = int(str(res).rstrip("s")) or 300
    AGE_FLOOR = 120                                    # ignore trivial sub-sample transactions
    elevated = [t for t in mins if age.get(t, 0) > AGE_FLOOR]
    elev_set = set(elevated)
    best_run, cur = [], []                             # longest run of adjacent elevated buckets
    for t in mins:
        if t in elev_set:
            cur.append(t)
            if len(cur) > len(best_run):
                best_run = cur[:]
        else:
            cur = []
    run_min = len(best_run) * res_sec / 60.0
    inter_in_run = any(interactive.get(t, 0) > 0 for t in best_run)

    # Run length ALONE over-fires: a workload that opens a fresh short transaction per unit of
    # work (per page, per batch) keeps age above the floor for a long run while never holding
    # ONE transaction open. Two calibrated discriminators, both measured against the verified
    # core 2026-07-24 hung session and the verified core 2026-08-17 false positive:
    #
    #   monotonicity — one transaction ageing sample-over-sample rises EVERY step.
    #                  true positive  (2026-07-24): 100% of steps rising, age 93172 -> 101800
    #                  false positive (2026-08-17):  70% of steps, bouncing 254/4889/115/2680
    #                  => threshold 0.9. Do not lower it; 0.6 admits the false positive.
    #   release      — a held txn ENDS: age collapses toward zero right after the run
    #                  (101800 -> 6 -> 0). Churn just carries on at the same level.
    ages = [age.get(t, 0) for t in best_run]
    rises = sum(1 for a, b in zip(ages, ages[1:]) if b > a)
    monotonic_frac = rises / max(1, len(ages) - 1)
    climbing = monotonic_frac >= 0.9

    after = mins[mins.index(best_run[-1]) + 1:][:2] if best_run else []
    peak_in_run = max(ages) if ages else 0
    released = bool(after) and peak_in_run > 0 and \
        min(age.get(t, 0) for t in after) < peak_in_run * 0.05

    # >=15 min AND one transaction demonstrably ageing. `released` is corroboration, not a
    # requirement — the txn may still be open at the end of the window.
    sustained = run_min >= 15 and climbing

    # [2] the timeline — only rows that carry a signal, so a 24h scan stays readable
    def notable(t):
        return interactive.get(t, 0) > 0 or t in elev_set
    rows = [t for t in mins if notable(t)]
    print(f"\n[2] SIGNAL TIMELINE ({len(rows)}/{len(mins)} buckets with a signal; "
          f"'*' = interactive client connected; oldTxnAge climb-then-reset = a held txn released)")
    print(f"    {'min':5} {'cpu%':>6} {'idle_in_txn':>11} {'interactive':>11} {'oldTxnAge':>10} {'waits':>6}")
    shown = rows if len(rows) <= 150 else rows[:150]
    for t in shown:
        mark = " *" if interactive.get(t, 0) > 0 else "  "
        print(f"  {mark}{t:5} {cpu.get(t,0)*100:6.1f} {idle_txn.get(t,0):11.1f} "
              f"{interactive.get(t,0):11.1f} {age.get(t,0):10.0f} {waits.get(t,0):6.1f}")
    if len(rows) > 150:
        print(f"    ... {len(rows)-150} more signal buckets suppressed (narrow --start/--end)")

    # [3] verdict — the whole point: name the signature so it isn't read as "just a busy DB"
    inter_peak = max((interactive.get(t, 0) for t in mins), default=0)
    age_max = max((age.get(t, 0) for t in mins), default=0)
    print("\n[3] VERDICT")
    print(f"    longest elevated-age run: {run_min:.0f} min"
          + (f" ({best_run[0]}->{best_run[-1]} UTC, peak age {age_max:.0f})" if best_run else "")
          + f"  |  age rising in {monotonic_frac*100:.0f}% of steps (>=90% = one ageing txn)"
          + f"  |  released after run: {'yes' if released else 'no'}"
          + f"  |  interactive backends: peak={inter_peak:.0f}")
    if run_min >= 15 and not climbing:
        print(f"\n    >>> NOT a held transaction. Age is elevated for {run_min:.0f} min but rises in only")
        print(f"        {monotonic_frac*100:.0f}% of steps — it bounces instead of ageing upward, so these are")
        print("        MANY SHORT transactions (one per page / batch / request), not one held open.")
        print("        A busy write workload looks exactly like this. Look for query COST or VOLUME:")
        print("        run `window` over the same range and read [2] LOAD BY DATABASE to find which")
        print("        tenant owns the load, then [1] for the query shape.")
        if inter_peak > 0:
            print(f"        (An interactive client was connected — peak {inter_peak:.0f} backends — but merely")
            print("         being connected is not evidence; the age trace says it held nothing open.)")
    if sustained and inter_in_run:
        print("    >>> HUNG INTERACTIVE SESSION SUSPECTED — a human client held a transaction open")
        print(f"        for ~{run_min:.0f} min while connected. That blocks autovacuum -> table bloat")
        print("        -> every other query scans more dead rows -> instance-wide CPU climbs. The age")
        print("        snapping back to ~0 at the run's end marks the moment the session was killed.")
    elif sustained:
        print("    >>> LONG-RUNNING TRANSACTION (app or unlabelled client, no interactive client seen).")
        print("        Same autovacuum-blocking / bloat mechanism. Check the idle_in_txn column and")
        print("        whether an app pool left a transaction open (missing commit / long batch).")
    elif inter_peak > 0 and run_min < 15:
        print("    interactive sessions present but no sustained (>=15 min) open transaction — benign.")
    elif not sustained and run_min < 15:
        print("    no hung-session / long-transaction signature in this window.")
    print("\n    NB: metrics can show THAT a human client held a long txn, not WHICH session/SQL —")
    print("        pg_stat_activity is live-only. To catch it live:")
    print("        SELECT pid,usename,application_name,state,xact_start,query FROM pg_stat_activity")
    print("        WHERE state='idle in transaction' ORDER BY xact_start;   (or set")
    print("        idle_in_transaction_session_timeout so it can't recur).")


# ---------------------------------------------------------------- locate (root cause -> code)
def _rg(pattern, root, extra=None):
    """Return [(relpath, lineno, text)] for a ripgrep match. Empty on no match."""
    cmd = ["rg", "-n", "--no-heading", "-t", "py"] + (extra or []) + [pattern, root]
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = []
    for line in r.stdout.splitlines():
        parts = line.split(":", 2)
        if len(parts) == 3:
            out.append((parts[0], int(parts[1]), parts[2]))
    return out


def _snippet(path, lineno, before=3, after=10):
    """Print lines around a hit; `before` catches decorators above a def."""
    try:
        lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return
    lo, hi = max(0, lineno - 1 - before), min(len(lines), lineno + after)
    rel = path.replace(SHIP_CARS_DIR.rstrip("/") + "/", "")
    print(f"    ── {rel}:{lineno}")
    for i in range(lo, hi):
        mark = ">>" if i == lineno - 1 else "  "
        print(f"    {mark} {i+1:5} {lines[i]}")
    print()


def cmd_locate(args):
    """Map a root cause (celery task name and/or SQL table) to source code."""
    repo = f"{args.repo_root}/{args.repo}"
    if args.task:
        name = args.task.split(".")[-1]            # accept epod.tasks.expire_load or expire_load
        print(f"# TASK  '{name}'  in  {args.repo}\n")
        print("[definition]  the @shared_task function that ran:")
        for f, ln, _ in _rg(rf"^\s*def {name}\b", repo):
            _snippet(f, ln, before=4, after=args.context)
        print("[enqueue sites]  WHERE it is fanned out (the real trigger — look for .delay/"
              "apply_async in a loop, transaction.on_commit, or eta=):")
        no_tests = ["-g", "!**/tests/**", "-g", "!**/test_*.py"]
        for f, ln, _ in _rg(rf"{name}\.(delay|apply_async)\b", repo, extra=no_tests):
            _snippet(f, ln, before=2, after=3)
        print("[schedule]  beat entries mentioning it (if periodic):")
        hits = _rg(name, repo, extra=["-g", "*celery*", "-g", "*beat*", "-g", "*settings*"])
        for f, ln, txt in hits:
            print(f"    {f.replace(args.repo_root + '/', '')}:{ln}: {txt.strip()}")
        if not hits:
            print("    (none — not a beat task; likely per-event .delay/eta scheduled)")
        print()
    if args.table:
        # Django default table name is "<app>_<model>"; e.g. epod_load -> app 'epod', model 'Load'
        app, _, rest = args.table.partition("_")
        model = rest.replace("_", " ").title().replace(" ", "")
        print(f"# SQL TABLE  '{args.table}'  -> app '{app}', model '{model}' (best-effort)\n")
        no_mig = ["-g", "!**/migrations/**", "-g", "!**/tests/**"]
        print("[explicit db_table binding, if any]:")
        db = _rg(rf"db_table\s*=\s*['\"]{args.table}['\"]", repo, extra=no_mig)
        for f, ln, _ in db:
            _snippet(f, ln, before=6, after=1)
        print(f"[model class '{model}' (implicit table name = the default)]:")
        for f, ln, _ in _rg(rf"^class {model}\b.*models\.Model", repo, extra=no_mig)[:3]:
            _snippet(f, ln, before=0, after=4)
        print(f"[querysets in '{app}' likely behind DISTINCT/COUNT SQL — inspect these]:")
        for f, ln, txt in _rg(r"\.distinct\(\)|annotate\(.*Count", f"{repo}/{app}", extra=no_mig)[:8]:
            print(f"    {f.replace(args.repo_root + '/', '')}:{ln}: {txt.strip()[:90]}")


def main():
    ap = argparse.ArgumentParser(description="Cloud SQL load / spike / root-cause probe (read-only)")
    ap.add_argument("--project", default=None, help="GCP project (default: gcloud config)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("instances"); p.set_defaults(fn=cmd_instances)

    p = sub.add_parser("cpu"); p.set_defaults(fn=cmd_cpu)
    p.add_argument("--instance", required=True)
    p.add_argument("--hours", type=float, default=24)
    p.add_argument("--start"); p.add_argument("--end")
    p.add_argument("--resolution", default="300s")

    p = sub.add_parser("queries"); p.set_defaults(fn=cmd_queries)
    p.add_argument("--instance", required=True)
    p.add_argument("--hours", type=float, default=24)
    p.add_argument("--start"); p.add_argument("--end")
    p.add_argument("--rank", choices=["total", "latency"], default="total")
    p.add_argument("--min-calls", type=int, default=50)
    p.add_argument("--top", type=int, default=10)

    p = sub.add_parser("window"); p.set_defaults(fn=cmd_window)
    p.add_argument("--instance", required=True)
    p.add_argument("--start", required=True); p.add_argument("--end", required=True)
    p.add_argument("--top", type=int, default=8)
    p.add_argument("--vcpu", type=int, default=None,
                   help="override vCPU count (only needed if the tier can't be parsed)")

    p = sub.add_parser("sessions"); p.set_defaults(fn=cmd_sessions)
    p.add_argument("--instance", required=True)
    p.add_argument("--hours", type=float, default=24)
    p.add_argument("--start"); p.add_argument("--end")
    p.add_argument("--resolution", default="300s")

    p = sub.add_parser("locate"); p.set_defaults(fn=cmd_locate)
    p.add_argument("--task", help="celery task name (e.g. expire_load or epod.tasks.expire_load)")
    p.add_argument("--table", help="SQL table name (e.g. epod_load) -> Django model, best-effort")
    p.add_argument("--repo", default="platform-backend")
    p.add_argument("--repo-root", default=SHIP_CARS_DIR)
    p.add_argument("--context", type=int, default=12)

    args = ap.parse_args()
    if args.cmd != "locate" and not args.project:   # locate is a local grep, no GCP needed
        args.project = default_project()
    args.fn(args)


if __name__ == "__main__":
    main()
