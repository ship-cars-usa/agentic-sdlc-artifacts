---
topic: sms-events
producers: []
consumers: [ml-bot-order]
tier: fleet
canonical-dto: ~
canonical-dto-file: ~
schema-source: none
candidate-dto-count: 0
binding: none-by-design
shared-with-producer: ~
last-generated-date: 2026-05-15
status: stub
---

# Topic `sms-events` — schema

**No schema by design.** This topic is consumed by a Python service that parses the payload as a raw `dict` (e.g. `json.loads()` → `data['key']`), with no typed model. L3b will need a hand-authored schema based on the producer's outgoing payload shape.

## Evidence
- No code site bound to this topic by subscription key or DTO-name match — needs manual seeding.
- Topic registry row: [../event-catalog.md](../event-catalog.md)

## Schema status: `none` (`none-by-design`)
This file ships with `schema-source: none` and `status: stub`. The L3b
contract program will produce the canonical schema; this stub records the
gap and (when present) lists candidate DTOs to seed from.
