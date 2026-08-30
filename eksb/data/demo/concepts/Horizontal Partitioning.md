---
schema_version: 1
type: concept
track: core
id: c-20260826-horizontal-partitioning
title: Horizontal Partitioning
created: 2026-08-26
aliases: [Sharding, Data Sharding, Horizontal Partitioning, Partitioning]
tags: [databases]
epistemic_default: external_fact
status: active
confidence: medium
sources: [src-20260826-demo-conversation-01]
relations:
  - rel: applies_to
    target: "[[Read Latency Is The Constraint]]"
    epistemic: assistant_hypothesis
    source: src-20260826-demo-conversation-01
---

## Definition

Splitting a table's rows across multiple storage units by a partition key.

## Claims

- "Sharding", "horizontal partitioning" and "data sharding" are used
  interchangeably across most general sources, while vendor documentation
  treats them as distinct. #e/source_claim
  ([[src-20260826-demo-conversation-01]])
- PostgreSQL added declarative table partitioning in version 10, released
  October 2017; earlier versions required table inheritance with manually
  written triggers. #e/external_fact
  ([[src-20260826-demo-conversation-01]]) — *asserted by the assistant;
  verify against the PostgreSQL release notes before treating as settled.*

<!-- CANONICALIZER: four surface forms appear across one conversation —
     "sharding", "data sharding", "horizontal partitioning", "partitioning".
     All resolve here. Recorded in `aliases`, which is what prevents the
     fragmentation from recurring on the next ingestion. -->
