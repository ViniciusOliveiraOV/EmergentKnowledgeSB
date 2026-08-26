---
id: adr-0002-temporal-semantics
track: core
status: accepted
date: 2026-08-26
---

# Two clocks: system time and knowledge time

## Context

Ingestion constantly surfaces positions older than the vault that records
them. A conversation captured in August can describe a belief held in March.
With a single `created` field, either the note claims to be older than it is,
or the position appears to have been formed on the day it was extracted.
Both are false, and both destroy the ability to answer *when did I believe
this*.

## Decision

Two distinct clocks:

    created      = SYSTEM time      — when the node was created in the vault
    asserted_at  = KNOWLEDGE time   — when the position was actually held

`created` is never backdated. Supporting fields: `valid_from`, `valid_until`,
`decided_on`, and on L0 sources `source_date` (knowledge time) versus
`ingested_at` (system time).

**Precision is never fabricated to satisfy a schema.** `asserted_at` accepts
`YYYY`, `YYYY-MM` or `YYYY-MM-DD`. A source saying "back in March" yields
`asserted_at: 2026-03`. Coercing it to `2026-03-01` is fabricated provenance.

## Rationale

The two clocks answer different questions and neither can be derived from the
other. Conflating them is unrecoverable: once `created` has been backdated,
there is no record of when the note actually entered the vault.

Partial dates are the honest representation of partial knowledge. A schema
that only accepts full dates does not eliminate imprecision — it launders
imprecision into false precision, which is worse, because it looks reliable
to every future reader.

## Consequences

- Retroactive nodes (`asserted_at` earlier than `created`) are normal, and
  the validator must treat them as clean.
- Date fields split into two classes: exact (`created`, `updated`,
  `ingested_at`) and partial-tolerant (`asserted_at`, `valid_from`,
  `valid_until`, `decided_on`, `source_date`).
- Date comparison must compare only the precision two values share.
- Any future export or graph database must preserve partial dates rather than
  normalizing them to timestamps.

## Revisit when

Sub-day precision is genuinely needed, or a target system cannot represent
partial dates — at which point the loss must be explicit, not silent.
