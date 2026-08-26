---
schema_version: 1
type: principle
track: core
id: c-20260826-tenant-sharding
title: Tenant Sharding
created: 2026-08-26
asserted_at: 2026
valid_until: 2026-08-24
tags: [databases]
epistemic_default: user_position
status: superseded
superseded_by: "[[Time-Range Partitioning]]"
confidence: high
sources: [src-20260826-fixture-generic-01]
relations:
  - rel: contradicts
    target: "[[Time-Range Partitioning]]"
    epistemic: user_position
    source: src-20260826-fixture-generic-01
---

> [!warning] Superseded 2026-08-24 by [[Time-Range Partitioning]]
> Retained as a historical record of a position that was actually held.
> Do not delete.

## Definition

Shard by tenant ID and scale horizontally, accepting individual query cost.

## Claims

- Sharding by tenant ID and scaling horizontally removes the need to optimize
  individual query cost. #e/user_position *(held ~2026-Q1 to 2026-08-24)*

<!-- TEMPORAL SEMANTICS: created 2026-08-26 (the note was written during
     extraction) but asserted_at 2026 (when the position was held).
     The source says only "back in Q1". The schema has no quarter precision,
     so the value degrades to the coarsest TRUE value rather than being
     sharpened into an invented 2026-01 or 2026-03. Losing precision is
     correct here; inventing it is not. The quarter survives in prose and in
     valid_until. -->
