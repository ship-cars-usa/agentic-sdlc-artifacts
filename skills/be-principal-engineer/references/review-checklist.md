# Principal-Level Code Review Checklist

Apply by impact — production-breakers first. Cite `file:line` for every finding and propose the concrete fix.

## Universal (Java + Python)

### Correctness
- [ ] Inputs validated at the trust boundary (request handler, queue consumer, file reader). Internal code does not re-validate.
- [ ] Nullability/`None` handled at every external return. No `.get()` chains without explicit handling.
- [ ] Concurrency: shared mutable state is either immutable, locked, or owned by one thread/coroutine.
- [ ] Off-by-one and boundary cases (empty collection, single element, max size, exactly-at-limit) are tested.
- [ ] Error paths actually do something. No bare `catch (Exception e) {}` or `except Exception: pass`.
- [ ] Time-of-check vs. time-of-use: no stale reads between an existence check and an operation.

### Operability
- [ ] Every external call has a timeout.
- [ ] Every external call has a retry policy (or an explicit decision not to retry).
- [ ] Structured logs at every boundary (request in, downstream call out, response back). Correlation/trace ID propagated.
- [ ] Metrics exist for the SLI: request rate, error rate, latency histogram, saturation.
- [ ] No secrets, tokens, PII, or full request bodies in logs.
- [ ] Health checks differentiate liveness (process alive) from readiness (can serve traffic).
- [ ] Graceful shutdown: in-flight requests drain, background tasks finish or persist.

### Scalability
- [ ] No N+1 queries (look for ORM access in loops).
- [ ] No unbounded collections, queues, or caches.
- [ ] Pagination on every list endpoint.
- [ ] Hot keys / hot partitions considered for caches and DBs.
- [ ] Connection pools sized intentionally and matched to thread/coroutine concurrency.
- [ ] Locks held only across in-memory work, never across I/O.

### Security
- [ ] Authentication and authorization checked at the handler, not deeper.
- [ ] SQL parameterized; no string concatenation into queries.
- [ ] Output encoded for the destination context (HTML, JSON, shell, SQL).
- [ ] File paths, URLs, and identifiers from users are validated against allowlists.
- [ ] Dependencies pinned and scanned.

### Maintainability
- [ ] Names describe intent, not implementation. `process()` and `data` are red flags.
- [ ] Functions do one thing at one level of abstraction.
- [ ] No commented-out code. No dead branches. No "TODO: fix later" without a ticket.
- [ ] Tests are at the level that gives the most signal — integration for I/O, unit for logic.

## Java-Specific

- [ ] No blocking calls on reactive event loops (Netty, Vert.x, Mutiny). `block()` outside main is a bug.
- [ ] `@Transactional` does not span external HTTP/queue calls.
- [ ] Hibernate: lazy associations not accessed outside session; `@EntityGraph` or fetch joins used to prevent N+1.
- [ ] `HikariCP` pool size is justified; default 10 is rarely correct for either direction.
- [ ] HTTP clients (`RestTemplate`, `WebClient`, `OkHttp`) configured with connect/read/write timeouts and connection pool limits.
- [ ] `CompletableFuture` chains have an explicit executor; no use of the common ForkJoinPool for blocking work.
- [ ] Logging uses parameterized form (`log.info("user={}", id)`) not string concatenation.
- [ ] Jackson: no infinite-recursion serialization on bidirectional relationships. `@JsonIgnore` or DTOs.
- [ ] Resource try-with-resources for every `Closeable`.
- [ ] No `Thread.sleep` in production code paths. No `synchronized` on `String` or `Integer` cached values.
- [ ] GC log enabled. Heap, metaspace, and direct memory limits set. `-XX:+HeapDumpOnOutOfMemoryError`.

## Python-Specific

- [ ] No sync I/O library (`requests`, `psycopg2`, `redis-py` sync, `boto3` sync) inside an `async def` handler.
- [ ] No CPU-heavy work on the event loop (parsing large JSON/XML, image processing, ML inference) — offloaded to a worker or process pool.
- [ ] `asyncio.gather` used for parallel awaits, not sequential `await` in a loop.
- [ ] No mutable default arguments (`def f(x=[])`).
- [ ] DB sessions/engines created at app startup, not per request.
- [ ] Pydantic models validate at the boundary; internal code passes typed objects.
- [ ] `httpx.AsyncClient` reused across requests, not constructed per call.
- [ ] Background tasks (`BackgroundTasks`, `asyncio.create_task`) reference-held so they are not GC'd mid-flight.
- [ ] Logging configured with structured output (`structlog`, `python-json-logger`); no `print()` in production code.
- [ ] `__del__` not used for resource cleanup; context managers instead.
- [ ] Type hints present on public APIs; `mypy --strict` clean for new code.
- [ ] No `from x import *`. No circular imports masked by lazy imports.

## Web App Architecture Smell Tests

- [ ] Could one slow downstream dependency consume all request capacity? (If yes — bulkheads missing.)
- [ ] Could a 10× traffic spike take down the database? (If yes — caching, rate limiting, or backpressure missing.)
- [ ] Could a deploy mid-request lose user work? (If yes — graceful shutdown missing.)
- [ ] Could a single bad request crash the worker? (If yes — error isolation missing.)
- [ ] Could a partial outage of a non-critical dependency take down the critical path? (If yes — circuit breaker or fallback missing.)
- [ ] Is there a metric that would page someone before users notice? (If no — observability gap.)
- [ ] Is there a runbook for the most likely failure modes? (If no — operability gap.)
