---
id: adr-0004-single-writer
track: core
status: accepted
date: 2026-08-26
---

# Single programmatic writer during Genesis and early Phase 1

## Context

Several things can write into a Markdown knowledge base at once: an agent, a
human in the editor, a network sync service, a REST plugin, a scheduled job.
Each writer that bypasses schema validation can leave the vault inconsistent
with no record of how. Concurrent writers also break the assumption that
version control is a complete audit log.

## Decision

Keep exactly one programmatic writer plus version control:

    filesystem + Git + <one agent>

Direct human editing is expected and unrestricted. Every additional
programmatic writer — sync services, REST surfaces, automation — is an
architectural change requiring a decision record before it is enabled.

## Rationale

The system's core promises are provenance and reconstructible history. Both
depend on every programmatic change being attributable and reviewable. One
writer plus Git delivers that with no coordination machinery at all.

This is a temporary constraint held while the schema is unvalidated, not a
permanent rejection of concurrency. Its value is diagnostic: during early
ingestion, anything wrong in the vault was either the agent or the human, and
telling those apart is trivial. That property is worth more right now than
the convenience of a second writer.

## Consequences

- No multi-agent concurrent writing until the schema has survived real use.
- A sync service that writes into the vault is a second writer even when it
  feels passive; enabling one requires revisiting this decision.
- Which writers are live on a given machine is instance state, recorded in
  instance documentation, never in core architecture.

## Revisit when

The schema has stabilized over several real ingestions and a second writer
(orchestration, a second agent, sync across devices) has a concrete need —
at which point conflict semantics must be designed, not assumed.
