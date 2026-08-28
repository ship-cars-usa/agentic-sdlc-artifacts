# Enable Driver LoadBoard Access by Default

`SCP-15137` · **proposed** · 2026-08-28 · hristo.savov@ship.cars · groomed 2026-08-28

**Services:** `platform-backend`, `platform-frontend`, `epod-ios`, `epod-android`

**Legend:** 🟢 added · 🟡 updated · 🔴 removed · 🔵 reused

![Design diagram](./diagram.svg)

## Context

Flip two existing carrier (`Company`) boolean flags to **enabled-by-default**: `drivers_enabled` ("Allow Drivers to Post Offers") and `drivers_enabled_accept` ("Allow Drivers to Accept the Orders they've Claimed"). New carriers should default ON; existing never-configured carriers get a one-time flip to ON.

**No schema shape change, no new endpoint, no new event, no new DTO field.** Both columns already exist (migrations 0117/0118) as `BooleanField(null=True)` with no default. Every reader/enforcer is untouched — enforcement uses plain truthiness (`if drivers_enabled:` at `api/filters.py:60`, `epod/models.py:3089,3773`, `api/order_api.py:4184`), so `None` already means "forbidden." The entire change is a **default + one-time backfill**.

Because the column is **nullable**, the backfill can distinguish `NULL` (never configured) from `False` (dispatcher explicitly restricted) — the recommended backfill targets **NULL-only**, honoring the AC's "forbid only when explicitly restricted." `db_default=True` (Django 6) covers every insert path (incl. any outside this repo's ORM); a bulk `.update()` avoids flooding `BROADCAST_EVENTS_TOPIC`. `syncer` does not index these flags, so there is no ES resync. FE + both ePOD apps consume the value with no code change (FE renders `null` as OFF — the load-bearing contract is that the API returns explicit `true`).

## §2a · PostgreSQL

*Column default + one-time backfill · Company (users_company)*

| Column | Type | Change | Null | Default / backfill |
| --- | --- | --- | --- | --- |
| `drivers_enabled` | `boolean` | 🟡 default + backfill | y (unchanged) | add default=True & db_default=True; RunPython UPDATE ... SET =true WHERE drivers_enabled IS NULL (NULL-only, per Q1) |
| `drivers_enabled_accept` | `boolean` | 🟡 default + backfill | y (unchanged) | add default=True & db_default=True; RunPython UPDATE ... SET =true WHERE drivers_enabled_accept IS NULL (NULL-only, per Q1) |

## Where it lives & how it's wired

| Aspect | Detail |
| --- | --- |
| service | platform-backend · users app (Django 6.0.4 / Python 3.12) |
| model | `users/models/user_models.py:418-419 (Company.drivers_enabled / drivers_enabled_accept)` |
| migration | `new users/ migration chaining after users/migrations/0153_* — mirror 0139 (AlterField + RunPython bulk .update())` |
| instance | platform · DB platform (Cloud SQL Postgres) |
| enforcement (unchanged) | `api/filters.py:52-83 · epod/models.py:3086-3089,3767-3773 · api/order_api.py:4183-4185` |
| setters (unchanged) | `POST /api/companies/{id}/set_drivers_enabled[_accept]/ — api/companies/__init__.py:780-788` |
| events | backfill via bulk .update() emits NO BROADCAST_EVENTS_TOPIC event (bypasses Company.save()) |
| ES | NOT indexed — syncer CompanyReadDto drops both flags; no resync |
| consumers (no code change) | platform-frontend toggles · epod-ios menu/accept · epod-android nav/accept |

## Rollout

**§5 · rollout ⚠️**

> Single platform-backend deploy delivers both halves (AlterField default + RunPython backfill). Forward-only data migration — the reverse is RunPython.noop (do NOT auto-revert flipped values). Decide Q1 first (NULL-only vs blanket-including-False) — it sets the backfill WHERE clause; blanket would silently re-enable carriers who deliberately turned it OFF. No FE/mobile deploy: both pick up the new server value automatically; already-open mobile sessions roll out on next refresh (iOS cold-start; Android online dashboard reload — flag-push websocket enums exist but are unwired). Verify the FE null-render trap (a leftover NULL renders the toggle OFF via `!!company.field`) with a post-migration QA case. Audit tests that assume the factory default-off (test_loadboard.py / test_users.py) in the same PR.
