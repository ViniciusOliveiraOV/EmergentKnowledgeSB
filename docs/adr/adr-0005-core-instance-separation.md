---
id: adr-0005-core-instance-separation
track: core
status: accepted
date: 2026-08-26
---

# CORE / INSTANCE separation

## Context

The system has two audiences that were initially the same files: a generic
framework (schemas, ontology primitives, provenance rules, validation,
ingestion protocol, merge semantics, contradiction rules, agent permissions,
security) and one person's knowledge base (concepts, projects, positions,
sources, references, decisions, dashboards).

An audit at Genesis found real contamination: framework documentation named
the instance, a conceptual architecture document contained a machine-specific
vault UUID and local configuration paths, ontology rules were taught using
the operator's personal concepts, and the "synthetic" fixture was in fact
derived from the operator's real context.

## Decision

Files declare which side they belong to:

    track: core       generic framework — no assumptions about any person
    track: instance   one person's knowledge, configuration, machine state

Personal preferences, beliefs, projects and data must never contaminate
`track: core`. Core documentation names the framework, never the instance.
Known non-public material is marked `publishable: false`.

At this version the boundary is **declarative, not enforced**: files are
labelled and separated by document, not by repository or directory tree.

## Rationale

Declaring the boundary before it is enforced is deliberate. Enforcement
(configurable taxonomy, a `--track core` validation mode, a separate
repository, vendored core) is real work that would harden a schema which has
not yet survived a single real ingestion. Doing it now would mean doing it
twice.

Labelling costs almost nothing and delivers most of the value: the boundary
becomes inspectable, contamination becomes reportable, and every subsequent
edit has an obvious side to land on. Deferring the labelling instead would
let contamination accumulate through Phase 1 and multiply the eventual cost.

## Consequences

- Every new file must declare a track. An undeclared file is an unanswered
  question, not a neutral default.
- The core cannot use the operator's concepts as teaching examples; generic
  examples are needed, and some current ones remain contaminated.
- The Genesis fixture is instance-scoped and non-publishable. A generic
  public fixture must be written from scratch in an unrelated domain —
  sanitizing the existing one would preserve the shape of the operator's
  thinking.
- Nothing is published while any core file still contains personal material.

## Revisit when

Roughly three real ingestions have been completed and the schema has
stabilized — at which point enforcement becomes worth building: configurable
taxonomy, `--track core` validation, and a separate public repository.
