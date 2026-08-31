# Production Troubleshooting Playbook (Java + Python Web Services)

For each symptom: stabilize, gather evidence, form hypothesis, validate cheaply, fix, write the postmortem.

## Latency Spike (p99 climbing)

**Stabilize:** check recent deploy → consider rollback. Check downstream dashboards → if a dependency is degraded, enable fallback / shed traffic / scale that dependency.

**Gather:**
- Latency histogram by endpoint, by region, by upstream caller.
- Request rate timeline (is it load, or is each request slower?).
- Downstream call latencies (DB, cache, external HTTP).
- GC log (Java) / event-loop lag (Python).
- Connection pool saturation metrics.

**Common causes, in order of likelihood:**
1. Slow downstream — DB query plan changed, cache cold, external API degraded.
2. Connection pool exhaustion — concurrency exceeds pool, requests queue.
3. GC pressure — heap too small for live data, allocation rate spiked, leak filling old gen.
4. Lock contention — new code path holding a contended lock, DB row locks.
5. CPU saturation — autoscaler hasn't kicked in, or per-pod CPU limit hit.

**Validate cheaply:**
- Java: `jcmd <pid> Thread.print` → see what threads are doing right now. JFR for 60s during the spike.
- Python: `py-spy dump --pid <pid>` for stack snapshots, `py-spy top` for live CPU.
- DB: `pg_stat_activity` / `SHOW PROCESSLIST` / slow query log.

## Out of Memory / OOMKilled

**Stabilize:** scale up memory or scale out replicas to keep service alive while investigating. Do not just bump memory permanently without finding the cause.

**Java:**
1. Confirm `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=...` is set. If not, set it before next occurrence.
2. Check GC log: is old gen filling and never reclaiming? → leak. Or filling fast under load? → allocation rate problem.
3. Take heap dump: `jcmd <pid> GC.heap_dump /tmp/heap.hprof`.
4. Open in Eclipse MAT → Leak Suspects report. Look at dominator tree.
5. Common culprits: caches without eviction, `ThreadLocal` not cleaned up, classloader leak (hot reload), `Statement`/`ResultSet` not closed, listener registrations not unregistered.

**Python:**
1. `tracemalloc.start()` early, then snapshot at intervals: `tracemalloc.take_snapshot().compare_to(prev, 'lineno')`.
2. `objgraph.show_growth()` to find growing object types.
3. `scalene` for line-level memory.
4. Common culprits: unbounded list/dict accumulators, references held in module-level state, `lru_cache` on methods (caches `self`), pandas DataFrames not freed, large response objects buffered fully before sending.

## Connection Pool Exhaustion

**Symptom:** requests timing out at exactly the pool's connection-acquisition timeout; downstream service appears healthy.

**Java (HikariCP):**
- Check `hikaricp_connections_active` vs. `hikaricp_connections_pending`.
- If pending > 0 sustained → pool too small or connections held too long.
- Held too long usually means `@Transactional` spanning external I/O, or N+1 queries.
- Right-size: `pool_size = ((core_count * 2) + effective_spindle_count)` is the historical heuristic, but for cloud DBs measure under load.

**Python:**
- SQLAlchemy: `pool_size`, `max_overflow`, `pool_timeout`. Watch `engine.pool.status()`.
- Sessions not closed → connections leaked. Use `async with` / context managers.
- Sync ORM in async handler → connections held across event loop suspension.

## Async Event Loop Stall (Python)

**Symptom:** all requests on a worker slow down simultaneously, then resolve in a burst.

**Diagnose:**
- `PYTHONASYNCIODEBUG=1` logs slow callbacks.
- `aiomonitor` exposes the running loop for inspection.
- `py-spy dump` during the stall shows what is blocking.

**Common causes:**
- Sync DB driver in async path (`psycopg2` instead of `asyncpg`).
- `requests` instead of `httpx`.
- CPU-bound work (JSON parse of huge payload, regex, ML model inference).
- Logging handlers that block (network log shipper without queue).
- DNS resolution using blocking resolver.

**Fix:** offload to executor (`loop.run_in_executor`) for one-off, swap to async lib for systematic.

## GC Thrashing (Java)

**Symptom:** CPU pegged, throughput collapsing, GC log shows continuous Full GCs that reclaim almost nothing.

**Diagnose:**
- GC log: look at `Pause Full` frequency and bytes reclaimed.
- Live data set size after Full GC = your real working set. If it equals heap size → heap too small or leak.
- JFR: allocation profile (which call sites allocate the most).

**Fix order:**
1. Enlarge heap if live set < heap and you have memory headroom.
2. Find and fix the leak if live set keeps growing across Full GCs.
3. Reduce allocation rate (object reuse, primitive collections, streaming instead of buffering).
4. Switch GC algorithm only after the above (G1 → ZGC for latency-sensitive, large heap).

## Cascading Failure / Outage Spreading

**Symptom:** one service fails, then its callers fail, then theirs.

**Stabilize:** identify the origin and cut traffic to it (circuit breaker manual trip, load shed). Do not let healthy services keep retrying into the dead one.

**Diagnose post-incident:**
- Did circuit breakers trip? (If no — missing or misconfigured.)
- Did timeouts fire? (If timeouts were too long, callers blocked instead of failing fast.)
- Did retries amplify load on the recovering service? (Need retry budgets and jitter.)
- Was there a bulkhead? (If no — one slow dependency saturated all threads/connections.)

**Structural fixes:** Resilience4j (Java) / `tenacity` + circuit-breaker libs (Python); per-dependency thread/connection pools; retry budgets; load shedding via 429 with Retry-After.

## Database CPU Spike

**Diagnose:**
- pg_stat_statements / Performance Schema → top queries by total time.
- EXPLAIN ANALYZE the suspect query.
- Recent schema/index changes? Statistics stale (`ANALYZE`)?
- New code path doing N+1?

**Fix order:**
1. Add or fix the index. Most "DB is slow" is "missing index".
2. Rewrite the query (avoid `SELECT *`, push filters, fix join order).
3. Cache the read.
4. Add a read replica.
5. Shard. Almost never the right first answer.

## Hot Key in Cache or DB

**Symptom:** one shard / one Redis node CPU-maxed while others idle.

**Diagnose:**
- Cache: `redis-cli --hotkeys` or sampling.
- DB: query plan showing skewed value distribution.

**Fix:**
- Add an in-process layer (Caffeine, `lru_cache`) in front of Redis for the hot key.
- Shard the hot key with a salt suffix and aggregate on read (split-and-merge).
- Pre-compute or pre-warm.
- Rate-limit upstream if traffic is genuinely a hot path on a single entity.

## Quick-Reference: Production-Safe Profiling Commands

```bash
# === Java ===
jcmd <pid> Thread.print > threads.txt
jcmd <pid> GC.heap_info
jcmd <pid> GC.heap_dump /tmp/heap.hprof
jcmd <pid> JFR.start name=prod duration=120s filename=/tmp/p.jfr
jcmd <pid> JFR.stop name=prod
# async-profiler (CPU flame graph, low overhead)
./profiler.sh -d 30 -f /tmp/cpu.html <pid>
# Allocation flame graph
./profiler.sh -d 30 -e alloc -f /tmp/alloc.html <pid>

# === Python ===
py-spy top --pid <pid>                    # live CPU
py-spy dump --pid <pid>                   # stack snapshot of all threads
py-spy record -o flame.svg --pid <pid> --duration 30
scalene --html --outfile out.html script.py
python -X tracemalloc=25 app.py           # 25 frames of alloc context

# === System ===
# I/O
iostat -xz 1
# CPU per-thread (Linux)
top -H -p <pid>
# Network
ss -tnp
# File descriptors
ls /proc/<pid>/fd | wc -l
```

## Postmortem Template

After every non-trivial incident, capture:

1. **Timeline** — UTC, what was observed, who did what.
2. **User impact** — duration, affected percentage, error rate, lost requests.
3. **Trigger** — the change or event that started the incident.
4. **Root cause** — the underlying defect, not the proximate failure.
5. **Detection** — how was it noticed? Was monitoring sufficient?
6. **Mitigation** — what stopped the bleeding?
7. **What worked / what didn't** — honest, blameless.
8. **Action items** — concrete, owned, dated. Each one prevents this *class* of incident, not just this instance.
