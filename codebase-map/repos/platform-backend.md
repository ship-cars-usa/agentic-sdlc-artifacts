---
repo: platform-backend
path: ~/projects/ship-cars-usa/platform-backend
stack: Python 3.12 / Django 6.0.4 (WSGI) / gunicorn 25.3.0 / Celery 5.6.3 + Kombu 5.6.2 (RabbitMQ/AMQP broker) / pip-compile-managed deps
domain: platform
shape: multi-module (Django monolith; 16 in-repo Django apps + `epod_project` config, 8 `*_listener.py` Pub/Sub scripts)
last-synced-commit: 1951e0607503b083febd0894c3f5674aa198152e
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# platform-backend

## What it is
**The original Ship.Cars Loadmate Django monolith.** Despite the misleading `epod` package.json name, this is a **Django 6.0.4 backend on Python 3.12, served in prod via gunicorn (WSGI)** — the legacy backend that the fleet's Quarkus + Spring microservices were **extracted from** over time. Still actively deployed and actively maintained: last commit 2026-07-10 (`SCP-14837 Recognize QA/staging test shipper as Montway (#2975)`) — **PR #2975**, the highest PR-number signal in the catalog. Receives constant change.

> **🔄 Stack re-synced 2026-07-20:** this repo was previously documented as **Python 3.6 / Daphne (ASGI) / Django Channels**. That is **historical** — the repo has since been modernized to **Python 3.12** (Dockerfile base `builder-django-docker-base:latest-3.12`), **Django 6.0.4** (`requirements.in` line 1), and a **gunicorn / WSGI** runtime (`WSGI_APPLICATION = 'epod_project.wsgi.application'`, `gunicorn==25.3.0` in `requirements.txt`). `channels` and `daphne` are **no longer dependencies** and `daphne_deploy.sh` no longer exists. `asgiref` is still present, but only as a transitive dep of Django/Celery — it does **not** indicate an ASGI server. Celery is now **5.6.3** on a **RabbitMQ/AMQP** broker.

> **⚠️ PROJECTS_INDEX.md miscategorization (verified 2026-07-17):** the immutable `PROJECTS_INDEX.md` lists `platform-backend` under **"Node/Other (TS APIs, packages, tooling)"** — this is **wrong**. It is Python/Django. The index's language detector tripped on the root `package.json`/`bower.json`, which exist only to bundle frontend static assets (see the `.ttf` fonts + `copy-static.sh`). Root markers `manage.py` + `requirements.txt` confirm Django. **This shadow doc is authoritative; the index is not.**

The repo's top-level entries include `manage.py` (Django convention), `epod_project/wsgi.py` (the gunicorn WSGI entrypoint), `docker-compose-*.yaml`, **8 `*_listener.py`** files (`company_documents_listener.py`, `fraud_detector_listener.py`, `loadboard_sync_listener.py`, `metadata_listener.py`, `orchestrator_listener.py`, `payment_listener.py`, `trip_management_listener.py`, `user_management_listener.py` — Google Pub/Sub message handlers; `metadata_listener.py` is new since the last sync), and `Roboto-*.ttf` font files (PDF generation — likely the dispatch-sheet PDF rendering). The ~16 in-repo Django apps: `api`, `changes`, `company_stats`, `compliance_network`, `credentials`, `documents`, `epod`, `loadboard`, `location_tracking`, `notifications`, `pubsub`, `report_templates`, `shortner`, `user_management_integration`, `users`, `utils` (+ `epod_project` settings/config).

`requirements.txt` is `pip-compile`-managed from `requirements.in` and targets **Python 3.12** (Dockerfile base `builder-django-docker-base:latest-3.12`) with **Django 6.0.4** (`requirements.txt:87`, `requirements.in:1`). Key deps: `celery==5.6.3` + `kombu==5.6.2` + `amqp==5.3.1` over a **RabbitMQ/AMQP** broker (`CELERY_BROKER_URL` defaults to `amqp://guest:guest@localhost:5672//`, from `RABBITMQ_URL`), `gunicorn==25.3.0` (WSGI prod server), `grpcio==1.80.0`, `google-cloud-pubsub==2.37.0` (the listeners), `ddtrace` (Datadog tracing), `UnleashClient` (feature flags), `django-phonenumber-field` (i18n), `zeep` (SOAP client). Following the 2026 modernization it is **no longer** part of the fleet's EOL-Python cohort.

Recent change signal: HEAD `1951e06 SCP-15052 Handles change to smarthaul payment method (#3087)` (2026-08-28) — still the highest PR-number signal in the catalog (#3087), receiving multiple commits per week.

The user-management integration subdirectory (`user_management_integration/`) implies the monolith still owns some user/company logic that hasn't been fully extracted to `user-backend`. Same for `trip_management_listener.py` (overlap with `trip-planner`).

## How it fits

- **Consumer of:** essentially every Ship.Cars Quarkus + Spring service — receives async events via Pub/Sub listeners, makes outbound calls to specific services.
- **Producer of:** `company_documents_listener.py` and similar suggest it consumes external events / emits Pub/Sub events on company / trip / user state changes.
- **Owns:** the legacy "Loadmate" Postgres / MySQL schemas that haven't been fully migrated. Authoritative source of truth for some operational data still served via Django REST views.
- **Inbound REST callers — the carrier-persona MFEs (confirmed by grep 2026-05-12).** All four carrier-facing MFEs still hit this Django monolith via the unversioned DRF-style `/api/<noun>/` URL convention. **This is not peripheral; it owns the operational core of the carrier flow.**
  - `ctms-frontend` → `/api/users/me/` (in-repo) + (via `entities-frontend-package`) `/api/loads/`, `/api/orders/`, `/api/negotiations/`, `/api/offers/`, `/api/postings/` (unversioned), `/api/contacts/`, `/api/carrier_companies/`, `/api/network_companies/`, `/api/companies/`, `/api/carriers/`, `/api/vehicles/`, `/api/load_cancel_reasons/`, …
  - `loadboard-frontend` → `/api/postings/`, `/api/network_companies/`, `/api/network_companies/${id}/safer_watch/`, `/api/carrier_companies/`, `/api/shipper_companies/`, `/api/generic_change_log/`.
  - `trip-planner-frontend` → `/api/loads/`, `/api/trips/`, `/api/trips/${id}/assign/`, `/api/trips/${id}/reassign/`, `/api/users/`, `/api/extra/loads/next_shipper_id/`.
  - `carrier-order-importer-frontend` → `/api/contacts/`, `/api/vehicles/${id}/`, `/api/vehicles/${vin}/vin/`, `/api/extra/loads/next_shipper_id/`. **Its entire direct surface is on this Django backend.**
- **URL-ownership convention:** `platform-backend` owns the **unversioned** `/api/<noun>/` (Django REST framework, trailing slash) paths. The extracted Quarkus / Spring services use the **versioned** `/api/<service>/v<N>/...` convention. The `api-gateway` (Go/Fiber) routes by URL prefix. Several nouns are dual-served (e.g. `/api/trips/` here vs `/api/tripplanner/v1/trips/` on `trip-planner`; `/api/users/` here vs `/api/usermanagement/v2,v3/` on `user-backend`) — extraction is incomplete and the MFEs hit both surfaces.
- **Smoking gun for ongoing Django consumption:** `globals-frontend-package/utils/errors.ts` exports both `parseDjangoErrorMessage` and `parseJavaErrorMessage` — the shared error parser exists precisely because every Loadmate MFE deals with both backend ecosystems on a normal request path.
- **Loadmate-app coupling:** the legacy in-repo parcels in `platform-frontend` (`src/CTMS`, `src/ContractPricing`, etc.) call this backend.

## Build / test / run
```
pip-compile requirements.in           # regenerate requirements.txt
pip install -r requirements.txt
python manage.py runserver            # Django dev server
gunicorn epod_project.wsgi:application # WSGI prod server
celery -A epod_project worker         # Celery worker (RabbitMQ/AMQP broker)
celery -A epod_project beat           # Celery beat (schedule in epod_project/celery.py)
```

## Key abstractions
- `JWTAuthenticationMiddleware` / `GlobalRequestMiddleware` / `AttachMediaKeyMiddleware` / `HidePublicIdMiddleware` — `epod/middleware.py` — the per-request auth + media-URL + public-id middleware stack (`JWTAuthenticationMiddleware.process_request` delegates to `api.permissions.JWTAuthentication`).
- `JWTAuthentication` — `api/permissions.py` — Keycloak JWT auth; **enforces the per-request `is_active` deactivation gate** (`permissions.py:206`, `:235` — `if not request.user.is_active` / `ret[0].is_active` fails the request).
- `*_listener.py` (8 scripts, repo root) — standalone Google Pub/Sub subscriber processes, each subscribing to a specific topic and deployed as its own worker.
- `api/order_api.py` — `MagicFileField` re-upload attachment path (contrast `loadboard_sync_listener`'s path-only `FileUrlField`); see `relations/media-url-flows.md`.
- `epod_project/celery.py` — Celery app, beat schedule, and `task_routes` (e.g. `lowpriority` queue for `performance_loadboard_batch`); broker is RabbitMQ/AMQP.

## Don't-do-here / gotchas

- **The per-request `is_active` gate is the ONLY immediate user-kill in the fleet.** Every other resource server validates Keycloak JWTs statelessly (no introspection / notBefore), so a Keycloak "logout all sessions" does not evict an active token. Setting `User.is_active=False` here makes `api/permissions.py:206,235` reject the very next request. Do not remove or bypass this check assuming Keycloak handles revocation — it does not.
- **Prod runtime is gunicorn / WSGI — not ASGI.** The repo was modernized off Python 3.6 + Daphne/Channels; do **not** pattern-match Channels concurrency, consumers, or ASGI middleware. There is no `channels`/`daphne` dependency and no `daphne_deploy.sh`. `asgiref` in the lockfile is transitive (Django/Celery) and does not imply an ASGI server. Treat this as standard synchronous Django under gunicorn.
- **The monolith still receives 1+ commits per week** despite being officially "the thing we're migrating off of." Coordinate extracted-microservice work with platform-backend's current owner — features still landing here must be aware of any new microservice boundaries.
- **Celery runs on RabbitMQ/AMQP** (not the Google Pub/Sub used by the listeners). The beat schedule and `task_routes` live in `epod_project/celery.py` (e.g. `lowpriority` queue for `performance_loadboard_batch`); the broker URL comes from `RABBITMQ_URL`.
- **Per-listener Pub/Sub coupling:** the 8 `*_listener.py` scripts each subscribe to specific Google Pub/Sub topics. Adding a new topic = adding a new listener + a new deploy script.
- **Dispatch-sheet PDF generation** (the `Roboto-*.ttf` files) — likely uses ReportLab or similar. Touching this affects driver-facing operational documents.
- **The whole repo is the fleet's biggest lifecycle item** for migration/extraction work — even after the Py3.12 / Django 6 modernization, it still owns the operational core of the carrier flow. Don't expect a quick rewrite.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/platform-backend-data-model.md` — **complete Django model inventory (62 entities, 10 apps) + Mermaid ER diagrams.** Hub entities: `users.Company`, `users.User`, `epod.Load`. Extracted 2026-05-15.
- `~/projects/codebase-map/repos/platform-frontend.md` — the Loadmate root config + in-repo parcels that talk to this backend.
- `~/projects/codebase-map/repos/ctms-frontend.md` / `loadboard-frontend.md` / `trip-planner-frontend.md` / `carrier-order-importer-frontend.md` — **the 4 carrier-persona MFEs that depend on this Django backend** (in-repo grep evidence 2026-05-12).
- `~/projects/codebase-map/repos/entities-frontend-package.md` — the shared FE library whose `/api/...` paths reveal the breadth of MFE→Django coupling.
- `~/projects/codebase-map/repos/api-gateway.md` — the Go/Fiber proxy whose URL-prefix routing distinguishes Django (`/api/<noun>/`) from Java (`/api/<svc>/v<N>/`) endpoints.
- `~/projects/codebase-map/repos/user-backend.md` — extracted user-management successor; partial overlap.
- `~/projects/codebase-map/repos/trip-planner.md` — extracted trip-management successor; partial overlap.
- `~/projects/codebase-map/repos/lead-parser.md` / `rateengine.md` — the EOL-Python/Spring services on the P1 lifecycle list (platform-backend was part of this cohort until its 2026 Python 3.12 / Django 6 modernization).
- `~/projects/codebase-map/relations/quarkus-version-matrix.md` — context for the EOL-language cohort (also `archiver` Quarkus 2.9, `notification-orchestrator` Quarkus 3.8.3).
- `~/projects/codebase-map/relations/media-url-flows.md` — `loadboard_sync_listener` stores the attachment **PATH only**, no re-upload (`FileUrlField`, hop 2); contrast the direct-CTMS `api/order_api.py` `MagicFileField` re-upload path (which is why direct-CTMS attachments resolve and LBv3-synced ones don't).
- `~/projects/codebase-map/relations/service-graph.md` — see the "MFE→Django edges (2026-05-12)" section for the explicit inbound edges.
- `~/projects/codebase-map/domains/platform.md`.
