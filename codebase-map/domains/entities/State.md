---
entity: State
aliases: [StateDto, StateEntity]
status: auto-generated
domains: [analytics, platform, pricing-billing]
occurrence-count: 7
variant-count: 7
owning-service: quarkus-k8s-boilerplate
last-extracted-date: 2026-05-15
---

# State

## What it is

TODO: human narrative. 7 variants across 4 repos and 3 domains (analytics, platform, pricing-billing). Owning service: [`quarkus-k8s-boilerplate`](../../repos/quarkus-k8s-boilerplate.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [ai-dashboard-backend](../../repos/ai-dashboard-backend.md) | `StateDto` | dto | `ai-dashboard-backend` | — | 0 | `src/main/java/cars/ship/aidashboard/dto/StateDto.java` |
| [ai-dashboard-backend](../../repos/ai-dashboard-backend.md) | `StateEntity` | jpa | `ai-dashboard-backend` | `BaseDbEntity` | 2 | `src/main/java/cars/ship/aidashboard/entity/StateEntity.java` |
| [contract-pricing-backend](../../repos/contract-pricing-backend.md) | `StateDto` | dto | `contract-pricing-dtos` | — | 0 | `contract-pricing-dtos/src/main/java/cars/ship/contractpricing/dtos/StateDto.java` |
| [quarkus-imperative-boilerplate](../../repos/quarkus-imperative-boilerplate.md) | `StateDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/boilerplate/dtos/StateDto.java` |
| [quarkus-imperative-boilerplate](../../repos/quarkus-imperative-boilerplate.md) | `StateEntity` | jpa | `db-entities` | `BaseDbEntity` | 2 | `db-entities/src/main/java/cars/ship/boilerplate/entities/StateEntity.java` |
| [quarkus-k8s-boilerplate](../../repos/quarkus-k8s-boilerplate.md) | `StateDto` | dto | `quarkus-k8s-boilerplate` | — | 0 | `src/main/java/cars/ship/boilerplate/dto/StateDto.java` |
| [quarkus-k8s-boilerplate](../../repos/quarkus-k8s-boilerplate.md) | `StateEntity` | jpa | `quarkus-k8s-boilerplate` | `BaseDbEntity` | 2 | `src/main/java/cars/ship/boilerplate/entity/StateEntity.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 4/7 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `name` | `ai-dashboard-backend`, `quarkus-imperative-boilerplate`, `quarkus-k8s-boilerplate` |
| `region` | `ai-dashboard-backend`, `quarkus-imperative-boilerplate`, `quarkus-k8s-boilerplate` |

## Use cases

### REST surface

**ai-dashboard-backend**:
- `ANY /states` — `src/main/java/cars/ship/aidashboard/resource/StateResource.java`
- `ANY /count` — `src/main/java/cars/ship/aidashboard/resource/StateResource.java`
- `ANY /{id}` — `src/main/java/cars/ship/aidashboard/resource/StateResource.java`
- `ANY /{id}/audit` — `src/main/java/cars/ship/aidashboard/resource/StateResource.java`

**quarkus-imperative-boilerplate**:
- `ANY /states` — `resources/src/main/java/cars/ship/boilerplate/rest/StateResource.java`
- `ANY /count` — `resources/src/main/java/cars/ship/boilerplate/rest/StateResource.java`
- `ANY /{id}` — `resources/src/main/java/cars/ship/boilerplate/rest/StateResource.java`
- `ANY /{id}/audit` — `resources/src/main/java/cars/ship/boilerplate/rest/StateResource.java`

**quarkus-k8s-boilerplate**:
- `ANY /states` — `src/main/java/cars/ship/boilerplate/resource/StateResource.java`
- `ANY /count` — `src/main/java/cars/ship/boilerplate/resource/StateResource.java`
- `ANY /{id}` — `src/main/java/cars/ship/boilerplate/resource/StateResource.java`
- `ANY /{id}/audit` — `src/main/java/cars/ship/boilerplate/resource/StateResource.java`

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`quarkus-k8s-boilerplate`](../../repos/quarkus-k8s-boilerplate.md)
- Domain rollup: [`analytics`](../analytics.md)
- Domain rollup: [`platform`](../platform.md)
- Domain rollup: [`pricing-billing`](../pricing-billing.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
