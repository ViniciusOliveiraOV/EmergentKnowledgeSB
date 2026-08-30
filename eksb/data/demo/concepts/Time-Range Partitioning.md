---
schema_version: 1
type: principle
track: core
id: c-20260826-time-range-partitioning
title: Time-Range Partitioning
created: 2026-08-26
updated: 2026-08-26
asserted_at: 2026-08-24
valid_from: 2026-08-24
aliases: [Partition By Time Range]
tags: [databases]
epistemic_default: user_position
status: active
confidence: high
sources: [src-20260826-demo-conversation-01]
relations:
  - rel: evolves_from
    target: "[[Tenant Sharding]]"
    epistemic: user_position
    source: src-20260826-demo-conversation-01
    note: position reversed 2026-08-24
  - rel: implements
    target: "[[Horizontal Partitioning]]"
    epistemic: user_position
    source: src-20260826-demo-conversation-01
---

## Definition

Partition by time range within a single cluster, rather than distributing by
a customer-derived key.

## Claims

- Time-range partitioning within one cluster is the current position.
  #e/user_position
- Tenant-derived partition keys produce structural skew that does not improve
  with scale. #e/user_position
- Any partition key derived from a customer attribute may have the same skew
  problem. #e/assistant_hypothesis — *proposed by the assistant; the engineer
  answered "maybe, not sure that's always true". Not endorsed.*

## Evolution

### ~2026-Q1 — prior position: [[Tenant Sharding]]
"Shard by tenant ID, scale horizontally, stop worrying about individual query
cost." #e/user_position

### 2026-08-24 — position reversed
Current position above. Trigger: hot shards on the ten largest tenants and a
quarter spent on rebalancing. Source:
[[src-20260826-demo-conversation-01]].

<!-- CONTRADICTION DETECTOR: same asserter, different dates, incompatible
     claims -> TEMPORAL EVOLUTION, not CONFLICT. Handled automatically. The
     Q1 position is preserved and marked superseded, never deleted, and is
     NOT escalated to the human. -->
