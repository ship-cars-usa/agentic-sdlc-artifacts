# Bulk Accept Revisions — orders stay in Active Revision after processing

`SCP-15047` · **proposed** · 2026-08-18 · hristo.savov@ship.cars · groomed 2026-08-18 · root cause confirmed in QA logs

**Services:** `platform-backend`, `ctms-frontend`, `carrier-packages-frontend`

![Design diagram](./diagram.svg)

## Context

The **Accept Revisions** bulk action leaves orders showing **Active Revision** after processing. **Root cause (confirmed in QA logs):** `process_bulk_action` serializes a *pre-mutation* `Load` instance — `Revision.accept()` mutates a **different** instance (`revision.load`), so the worker's `load` keeps the stale `active_revision_id`/`update_time` in memory and feeds both the HTTP response and `event.new_value`. Postgres and ES end up correct; the staleness lives only in the browser Redux store (survives navigation, not a reload). **Decision:** `refresh_from_db()` after `action_func`, and stop unconditionally overwriting the fresh `event.new_value`. No schema, endpoint-shape, or migration change.

## §4 · REST API & DTO

*Response contract · POST /api/loads/bulk/revision/accept/ (shape unchanged — values corrected)*

| Field | Before | After | Change | Note |
| --- | --- | --- | --- | --- |
| `results[].active_revision_id` | `stale (pre-accept)` | `null` | corrected | was non-null despite accepted=true |
| `results[].active_change_id` | `stale (pre-accept)` | `null` | corrected | same stale-instance cause |
| `results[].update_time` | `pre-mutation ts` | `post-accept ts` | corrected | auto_now bump now reflected |

## §3 · Pub/Sub event

*Payload delta · load-update event (event.new_value) on BROADCAST_EVENTS_TOPIC*

| Field | Change | Note |
| --- | --- | --- |
| `event.new_value` | corrected | built from the post-mutation instance; stop overwriting the correct populate_new_data() re-fetch at :4449-4450 |

## Where it lives & how it's wired

| Aspect | Detail |
| --- | --- |
| service | platform-backend · Django 6.x / Py 3.12 |
| fix | `api/order_api.py — refresh_from_db() after action_func (:4370); drop event.new_value overwrite (:4449-4450)` |
| reuse pattern | `api/actions.py:75-82 · api/order_api.py:4630` |
| endpoint | `POST /api/loads/bulk/revision/accept/` |
| topic | `BROADCAST_EVENTS_TOPIC (cars.ship.{env}.carrierlb.events)` |
| consumers | syncer (shielded by version guard) — audit other subscribers |
| datastores | Postgres & ES already correct — staleness only in browser Redux |
| new / migration | none — no field, serializer, or migration |

## Rollout

**§5 · rollout & sequencing ⚠️**

> Producer-before-consumer. (1) Record the response contract on the ticket (values corrected, no shape change). (2) Fix `platform-backend` — this is the only change that fixes the bug. (3) Verify in QA: response returns `active_revision_id: null` and syncer logs a *non-noop* `loads` write; the grid must clear **without** a browser refresh. (4) `ctms-frontend` + `carrier-packages-frontend` alignment runs in parallel — neither fixes the bug, don't merge them as the fix. (5) No syncer change. **Risk:** the stale second-pass `event.new_value` reaches *all* load-update subscribers; syncer is shielded by its version guard, but audit the other subscribers for one without an equivalent guard.
