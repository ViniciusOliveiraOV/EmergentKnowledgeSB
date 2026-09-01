---
schema_version: 1
type: concept
track: core
id: c-20260826-read-latency-constraint
title: Read Latency Is The Constraint
created: 2026-08-26
updated: 2026-08-26
aliases: [Read Latency Constraint, Latency-First Design]
tags: [databases, performance]
epistemic_default: user_position
status: active
confidence: high
sources: [src-20260826-demo-conversation-01]
relations:
  - rel: informed_by
    target: "[[Horizontal Partitioning]]"
    epistemic: assistant_hypothesis
    source: src-20260826-demo-conversation-01
  - rel: questions
    target: "[[Does time-range partitioning survive sub-second retention]]"
    epistemic: open_question
    source: src-20260826-demo-conversation-01
---

## Definition

Read latency, not write throughput, is treated as the binding constraint on
this system's data architecture. Other design choices are considered
downstream of it.

## Claims

- Read latency is the constraint that must be solved; write throughput is
  not. #e/user_position
- Everything else in the design is downstream of read latency.
  #e/user_position
- The framing corresponds to availability-favouring design in the CAP
  literature. #e/assistant_hypothesis ([[src-20260826-demo-conversation-01]])

## Open questions

- [[Does time-range partitioning survive sub-second retention]]
