---
schema_version: 1
type: question
track: core
id: c-20260826-subsecond-retention-question
title: Does time-range partitioning survive sub-second retention
created: 2026-08-26
tags: [databases]
epistemic_default: open_question
status: active
sources: [src-20260826-demo-conversation-01]
relations:
  - rel: questions
    target: "[[Time-Range Partitioning]]"
    epistemic: open_question
    source: src-20260826-demo-conversation-01
---

## Question

Does time-range partitioning hold up if sub-second retention windows are
ever required, or does it degrade into the same rebalancing problem at a
smaller timescale? #e/open_question

## Bearing on

- [[Time-Range Partitioning]] — if it degrades, the current position is
  scoped to coarse retention windows rather than general.
