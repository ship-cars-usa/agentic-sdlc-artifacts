# Idempotency key on carrier payment transactions

`CDR-0008` · **shipped** · 2026-08-28 · hristo.savov@ship.cars · real · shipped as V10.0

**Services:** `payment-backend`

**Legend:** 🟢 added · 🟡 updated · 🔴 removed · 🔵 reused

![Design diagram](./diagram.svg)

## Context

Retried payout requests double-pay carriers.

**Decision:** a client-supplied `idempotency_key`, enforced by a partial unique index, makes a retried `POST /internal/v1/transactions` a no-op — the DB unique index, not `@Version`, is the fence.

**This documents the real shipped migration V10.0. Blast radius:** payment-backend Postgres + one JAX-RS endpoint; no event, no ES.

## §2a · PostgreSQL

*Column delta · public.transactions (+ transactions_aud)*

| Column | Type | Change | Null | Default / backfill |
| --- | --- | --- | --- | --- |
| `idempotency_key` | `varchar(128)` | 🟢 added | yes | also added to Envers transactions_aud |
| `uq_transactions_idempotency_key` | `partial unique index` | 🟢 added | — | (from_company_id, idempotency_key) WHERE … NOT NULL |

## §4 · REST API & DTO

*Endpoint · payment-backend · Quarkus JAX-RS · MicroProfile (DTOs: Swagger v3)*

| In-code | External | Method | Change | Request DTO | Response DTO |
| --- | --- | --- | --- | --- | --- |
| `/internal/v1/transactions` | `/api/payment/internal/v1/transactions` | POST | 🟡 changed | `CreateTransactionDto` | `TransactionDto` |

*DTO field delta · CreateTransactionDto (Java record)*

| DTO | Field | Type | Change | JSON name |
| --- | --- | --- | --- | --- |
| `CreateTransactionDto` | `idempotencyKey` | `String @Size(max 128)` | 🟢 added | `idempotencyKey` |

## Where it lives & how it's wired

| Aspect | Detail |
| --- | --- |
| service | payment-backend · resources module |
| file | `db-migration/…/V10.0__add_idempotency_key_to_transactions.sql` |
| instance | users · DB payment |
| entity | `TransactionEntity (Panache)` |
| host var | Helm-injected (none in repo) |
| base | BaseDbEntity · @SQLDelete soft-delete · Envers @Audited |
| tool | Flyway (flat V{maj.min}) |
| readers | none observed |

## Rollout

> ⚠️ **§5 · rollout**
>
> Real shipped change via `TransactionInternalController`. Migration adds the column to `transactions` and `transactions_aud` plus the partial unique index; create such an index `CONCURRENTLY` to avoid locking the hot table.
>
> Forward-only DB → rollback is a follow-up migration. No resync, no event coordination.
>
> Note: the resource uses MicroProfile OpenAPI while its DTOs use Swagger v3 — a real per-repo split.
