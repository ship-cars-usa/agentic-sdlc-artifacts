---
entity: FileContent
aliases: [FileContent, FileContentDto]
status: auto-generated
domains: [identity, listings-trade, operations, platform]
occurrence-count: 5
variant-count: 5
owning-service: user-backend
last-extracted-date: 2026-05-15
---

# FileContent

## What it is

TODO: human narrative. 5 variants across 5 repos and 4 domains (identity, listings-trade, operations, platform). Owning service: [`user-backend`](../../repos/user-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [driveaway-backend](../../repos/driveaway-backend.md) | `FileContent` | dto | `db-entities` | — | 0 | `db-entities/src/main/java/cars/ship/driveaway/db/entities/vo/FileContent.java` |
| [loadbuilder-backend](../../repos/loadbuilder-backend.md) | `FileContentDto` | dto | `infra-interfaces` | — | 0 | `infra-interfaces/src/main/java/cars/ship/loadbuilder/infra/attachment/dtos/FileContentDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `FileContent` | dto | `posting-app` | — | 3 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/vo/FileContent.java` |
| [spring-commons](../../repos/spring-commons.md) | `FileContentDto` | dto | `spring-gcp-storage-client-impl` | — | 3 | `spring-gcp-storage-client-impl/src/main/java/cars/ship/commons/spring/gcp/storage/dto/FileContentDto.java` |
| [user-backend](../../repos/user-backend.md) | `FileContent` | dto | `usermanagement-app` | — | 3 | `usermanagement-app/src/main/java/cars/ship/shipperlite/user/domain/model/vo/FileContent.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 3/5 or more):

| Field | Common type | Variants with it |
|---|---|---:|
| `extension` | `String` | 3 |

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `bytes` | `posting-backend`, `spring-commons` |
| `originalFileName` | `posting-backend`, `spring-commons` |
| `data` | `user-backend` |
| `name` | `user-backend` |

## Use cases

### REST surface

_(no REST endpoints reference this entity in any variant repo)_

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`user-backend`](../../repos/user-backend.md)
- Domain rollup: [`identity`](../identity.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`operations`](../operations.md)
- Domain rollup: [`platform`](../platform.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
