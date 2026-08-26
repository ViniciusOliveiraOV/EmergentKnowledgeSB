---
schema_version: 1
type: decision
track: core
id: d-20260826-adopt-time-range-partitioning
title: Adopt Time-Range Partitioning
created: 2026-08-26
decided_on: 2026-08-24
status: active
epistemic_default: user_position
confidence: high
sources: [src-20260826-fixture-generic-01]
relations:
  - rel: implements
    target: "[[Time-Range Partitioning]]"
    epistemic: user_position
    source: src-20260826-fixture-generic-01
  - rel: replaces
    target: "[[Tenant Sharding]]"
    epistemic: user_position
    source: src-20260826-fixture-generic-01
---

## Decision

The events table moves to time-range partitioning, effective next sprint.

## Context

Tenant sharding produced hot shards on the ten largest tenants and a quarter
of rebalancing work.

## Alternatives rejected

- **Stay on tenant sharding** — rejected: the skew is structural and will not
  improve with scale.
- **Hybrid tenant-plus-time composite key** — rejected: makes every
  cross-tenant analytical query a full scan.

## Consequences

Accepts that cross-partition queries spanning long time ranges become more
expensive, in exchange for eliminating tenant-driven skew.

<!-- Qualifies as `decision` because alternatives were explicitly rejected.
     Had nothing been given up, this would be a note, not a decision. -->
