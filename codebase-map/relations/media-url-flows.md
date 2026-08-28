# Media / Attachment URL Flows

Cross-repo pipelines that **assemble the servable media/attachment URL** for a file. These flows span 5+ services and are invisible from any single shadow doc — this file is the canonical routing target for *"who builds / serves an attachment's media URL?"* questions.

This class of flow is what made **SCP-14564** a 5-repo bug: no single repo revealed that the URL served to CTMS for LBv3-synced attachments is *reassembled in `syncer`*, not minted by Django's `_url()`.

## Conventions

- Flows are ordered **producer → consumer** hops; each hop names the repo, its **role**, and `path:line` anchors inside that repo.
- **Role** is one of:
  - `mints` — generates the canonical object key / URL from scratch.
  - `owns` — this hop constructs (or rewrites) the URL that downstream serves; **the fix site for URL-shape bugs**.
  - `relays` — forwards the value verbatim, adds no host/path (may append signing params).
  - `stores-path` — persists only the object-key path (scheme+host stripped); no bytes, no re-upload.
  - `literal-lookup` — uses the value as-is against storage; not a fix site.
- Anchors are `path:line` relative to `~/projects/ship-cars-usa/<repo>/`. `last-confirmed` = date verified against source.

---

## Flow: LBv3 load/attachment media-URL pipeline

**last-confirmed: 2026-07-27** — every hop verified against source this session.

How an attachment's servable media URL is built when a load/attachment originates in **LBv3 (`loadboard-backend`)** and is synced into **CTMS (`platform-backend`)** for the orders/loadboard read surfaces.

**Async topic:** `loadboard-events` (config key `loadboard-events-topic`).
**Read store:** Elasticsearch — `syncer` writes the `loads` / `postings` indexes; `cube` reads them.

| # | Repo | Role | What it does to the URL | Evidence |
|---|---|---|---|---|
| 1 | `loadboard-backend` | relays | Uploads the file **once** to `attachment-backend`, keeps the returned absolute `downloadUrl` as `Attachment.fileUrl`, and publishes it **verbatim** as `AttachmentPubSubDto.fileUrl` to `loadboard-events`. | `converters/impl/PostingPubSubDtoConverter.java:243-268` (`.fileUrl(attachmentEntity.getFileUrl())`); publish at `services/impl/LoadboardNotificationsServiceImpl.java:65` (objectType=POSTING); topic at `configuration/.../application.properties:138` (`loadboard-events-topic`) |
| 2 | `platform-backend` | stores-path | `loadboard_sync_listener.py` subscribes `PUBSUB_LOADBOARD_SYNC_SUBSCRIPTION` (= `loadboard-events`), routes `objectType=="POSTING"` → `LoadboardSyncLoadSerializer`. `FileUrlField` **strips scheme+host and stores the PATH ONLY** onto `Attachment.file` — a plain string assignment, **no bytes, no re-upload, no Django-minted key** (a deliberate optimization). | `loadboard/sync/load_serializer.py:46-64` (`FileUrlField`, added in commit `2865a39b` / PR #2695) |
| 3 | `syncer` | **owns** | Indexing the CTMS order/loadboard doc into ES, it **glues a base URL onto the bare stored path** — **this is where the SCP-14564 bug lives.** `mediaBaseUrl` is configured **with a trailing `/media/`**, so prepending it to an already-object-key-scoped path yields a wrong `…/media/attachments/…`. | real-time path: `services/utils/CtmsMediaUrlTransformer.java:23` (`mediaUrl.contains(mediaBaseUrl) ? mediaUrl : mediaBaseUrl + mediaUrl`); resync path: `commons/util/CommonUtil.java:29-36` (`addBaseUrlIfNeeded`, guarded by `!urlHasScheme`) via `services/resyncers/CtmsOrdersIndexResyncer.java:188-206,223-229`; applied per-field (`file`,`original_file`,`fullSize`,`thumbnail`) in `services/converters/CtmsAttachmentDocumentConverter.java:95-140`, driven from `CtmsOrdersIndexListener.java:204,257,342` + `CtmsLoadboardIndexListener.java:240,399`; config `configuration/.../application.properties:116,185` (`syncer.common.config.media-base-url = https://media-<env>.ship.cars/media/`) |
| 4 | `cube` | relays | CQRS read side: reads the ES value **verbatim** and hands it to the media-proxy client — **adds no host/path prefix**; only appends `?key=&expiresAt=` signing params. | `ctms-orders/.../services/impl/OrdersMediaUrlPostProcessor.java` (`populateProxyMediaUrls` / `getProxyUrl`) → `MediaProxyClient.requestKey` (external `quarkus-extension-media-proxy`) |
| 5 | `media-proxy` | literal-lookup | Go service: literal single-bucket GCS lookup of the path; returns `OBJECT_NOT_FOUND` when the reassembled path is wrong. **Not a fix site.** | `service/gcs_storage.go:40,63` (`bucket.Object(path).Attrs()`); error at `utils/errors.go:122` |
| — | `attachment-backend` | mints | The canonical company-scoped key/URL generator that produced the original absolute `downloadUrl` at hop 1. | `AttachmentStorageServiceImpl.baseStoragePath:284` builds `/attachments/{companyId}/{folder}/{date}/{publicId}`; `StorageServiceImpl.storeFile:31` returns `mediaUrl + storagePath` |

### Key detectable lesson

The media URL served to CTMS for **orders/loadboard** is assembled in **`syncer`** (not in Django's `_url()`), **relayed by `cube`**, and only **looked up literally by `media-proxy`**. A future *"who builds/serves an attachment's media URL?"* question routes to hop 3 (`syncer`) first.

**Contrast — the direct-CTMS upload path works** because it does NOT go through hops 1–3: `platform-backend` `api/order_api.py:115` uses `MagicFileField`, a real DRF `FileField` that **re-uploads a second copy** into Django's own bucket. That is why direct-CTMS attachments resolve and LBv3-synced ones (bare path + `syncer` base-URL glue) do not.
