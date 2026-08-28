---
repo: attachment-backend
path: ~/projects/ship-cars-usa/attachment-backend
stack: Java 21 / Quarkus 3.27.5 (LTS)
domain: platform
shape: multi-module (11 modules + parent pom)
last-synced-commit: 50e6583bc200a34db73a799769d0182c4e8cb75b
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# attachment-backend

## What it is
Quarkus 3.27.5 (LTS) / Java 21 service that **owns file/media attachments fleet-wide**: upload (multipart + URL-fetch), GCS storage, PG metadata persistence, automatic thumbnailing (Thumbnailator, max 500×500 px), and soft-delete. Multi-tenant via company-ID scoping. Heavily called by `user-backend`, `posting-backend`, `inventory-backend`, `invoices`, `loadboard-backend`, `notification-backend`, and others — making it one of the highest-traffic platform services in the fleet.

> **🔄 Re-synced 2026-08-28:** migrated off Quarkus 3.20.4 to the **3.27.5 LTS** line (`pom.xml:59`; commit `3d7c7c3 LITE-7410 Migrate to Quarkus 3.27 LTS`). Also added **concurrent indexes for attachment lookups** (`LITE-3098`). No change to the module shape, API surface, or storage model.

## How it fits
- Consumes API of: none observed (`@RegisterRestClient` absent). Vert.x `WebClient` used internally for URL-fetch downloads (`CONFIG_DOWNLOAD_CONNECTION_TIMEOUT=PT60S`, `CONFIG_DOWNLOAD_READ_TIMEOUT=PT60S` defaults — **the only timeout-clean Quarkus outbound HTTP in the fleet sample so far**).
- Publishes events to: **Vert.x EventBus in-process** (`ATTACHMENT_CREATED_CHANNEL`) — payload `{attachmentId, allowedMimeTypes, maxSizeMb}`. **In-memory only**; no GCP Pub/Sub publish observed.
- Subscribes to: none observed (EventBus listeners are co-deployed in the same JVM).
- Owns data store: PostgreSQL (`attachment` db, HikariCP max-size=16 dev), Panache, Flyway; **GCS bucket** (`shipcars-platform-dev-media` dev) for blob storage. Table `attachments`: id, public_id (UUID), company_id, file_name, mime_type, size, status (`PENDING/READY/FAILED`), public_url, storage_path, thumbnail metadata, auto_delete_at.

## Build / test / run
```
./mvnw clean package -DskipTests
./mvnw quarkus:dev
# 11 modules: api-dtos, api-enums, api-quarkus, application, commons,
#             configuration, coverage-report, db-entities, db-migration,
#             resources, services
# Max upload: 10 MB (CONFIG_MEDIA_MAX_SIZE_MB)
```

## Key abstractions
- `AttachmentController` — `resources/.../AttachmentController.java` — `/api/v1/attachments`: `GET /{id}`, `GET /?id=...`, `POST` (JSON URL-fetch), `POST /bulk`, `POST /form-data` (multipart), `DELETE /{id}`, `DELETE /?id=...` (bulk).
- `AttachmentServiceImpl` — `services/.../AttachmentServiceImpl.java` — orchestrates upload, validation, deletion; publishes EventBus events.
- `StorageServiceImpl` — `services/.../StorageServiceImpl.java` — GCS abstraction (`storeFile`, `deleteFile`, `getFileMetadata`).
- `ThumbnailGeneratorServiceImpl` — Thumbnailator image resize.
- `AttachmentRepositoryServiceImpl` — Panache CRUD + status state machine.
- `AttachmentStorageServiceImpl` — MIME validation + URL-fetch orchestration.

## Don't-do-here / gotchas
- **`DELETE /?id=...` silently swallows per-ID errors** — catches each exception, logs it, returns `204 No Content` regardless. Callers cannot tell which deletes failed. Add per-ID status to the response.
- **Vert.x EventBus is in-memory, single-node** — if `attachment-backend` is horizontally scaled, `ATTACHMENT_CREATED_CHANNEL` events fire only on the node that processed the upload. Co-located consumers won't see events from other replicas. Replace with GCP Pub/Sub or document the single-node assumption.
- **Thumbnail generation is blocking** in the upload request thread — large image batches block; a slow Thumbnailator pass propagates to the caller. Consider offloading to a worker pool.
- **No virus scanning** — Tika excluded from `commons` to keep native-image size down. Trust is delegated to the caller via MIME validation only. Document this and confirm an upstream scanner exists, or add one (ClamAV sidecar).
- **HikariCP pool 16 in dev**; verify prod override under the high-fanout call pattern (every seeded service calls this).
- **URL-fetch defaults to 60 s connect + 60 s read** — if env vars aren't overridden, large slow-mirror downloads can pin a download thread for 2 minutes per attachment.
- **No fleet-wide signed-URL pattern observed** — download URLs go through a public-URL flow. Confirm bucket ACLs aren't open by default.
- **Bulk-create endpoint does not document a max-list size** — a 10 000-URL POST will start 10 000 concurrent downloads. Cap it.

## Relevant ADRs / docs
- `~/projects/codebase-map/relations/service-graph.md` — confirmed inbound from `user-backend`, `posting-backend`, `inventory-backend`, `invoices`, `loadboard-backend`.
- `~/projects/codebase-map/relations/rest-client-registry.md`.
- `~/projects/codebase-map/relations/media-url-flows.md` — **mints** the canonical company-scoped attachment URL that seeds the LBv3 media-URL pipeline (`AttachmentStorageServiceImpl.baseStoragePath` / `StorageServiceImpl.storeFile`).
- `~/projects/codebase-map/domains/platform.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `AttachmentEntity` | jpa | `db-entities` | [Attachment](../domains/entities/Attachment.md) |
| `Attachment` | dto | `db-entities` | [Attachment](../domains/entities/Attachment.md) |
| `AttachmentCreatedEvent` | dto | `services` | AttachmentCreatedEvent |
| `AttachmentDto` | dto | `api-dtos` | [Attachment](../domains/entities/Attachment.md) |
| `AttachmentStorageServiceImpl` | dto | `services` | AttachmentStorageServiceImpl |
| `BlobMetadata` | dto | `services` | BlobMetadata |
| `CreateAttachmentByUrlDto` | dto | `api-dtos` | CreateAttachmentByUrl |
| `CreateAttachmentDto` | dto | `api-dtos` | CreateAttachment |
| `CreateAttachmentVo` | dto | `services` | CreateAttachmentVo |
<!-- entities-end -->
