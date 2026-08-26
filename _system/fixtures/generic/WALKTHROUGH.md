---
schema_version: 1
type: doc
track: core
id: doc-20260826-generic-walkthrough
created: 2026-08-26
title: Generic Fixture Walkthrough
---

# Generic Fixture Walkthrough

`raw-conversation.md` is a fully synthetic engineering discussion. `expected/`
holds the L1 notes the pipeline should produce from it. Nothing here refers to
a real person, project or organization — this directory is a **specification
by example** and the validator's regression case.

## What the fixture contains, by design

| # | Element | In the conversation | Expected handling |
|---|---|---|---|
| 1 | **Existing concept** | partitioning, under four surface forms | Canonicalizer collapses to one note; forms recorded in `aliases` |
| 2 | **New concept** | read latency as the binding constraint | `CREATE` — no canonical match |
| 3 | **Decision** | adopt time-range partitioning | `CREATE` decision; two rejected alternatives recorded |
| 4 | **Assistant hypothesis** | "any customer-derived key has the same skew" | stays `#e/assistant_hypothesis` — the engineer said "maybe"; **never promoted** |
| 5 | **External fact** | PostgreSQL 10 added declarative partitioning, Oct 2017 | `#e/external_fact`, source retained, marked unverified |
| 6 | **Change of position** | Q1: tenant sharding → Aug: time-range partitioning | temporal evolution; both notes kept, old one superseded not deleted |

## Stage-by-stage expected behaviour

**TranscriptIngestor** — writes one `type: source` note verbatim, sets
`content_hash`, touches nothing in L1.

**EntityExtractor** — six candidates, no more. Epistemic status assigned
*structurally by speaker*: engineer turns → `user_position`, assistant turns
→ `assistant_hypothesis`. The PostgreSQL release claim is `external_fact`
because it is a verifiable outside claim, and it is written with a
verification caveat rather than as settled.

**Canonicalizer** — the load-bearing case:

    sharding             ─┐
    data sharding        ─┤  normalized slug + alias table
    horizontal partitioning ─┤
    partitioning         ─┘

    → ONE entity. Four aliases persisted, so it cannot re-fragment.

**MergePlanner** — against an empty vault:

    CREATE  Read Latency Is The Constraint
    CREATE  Horizontal Partitioning          (4 surface forms → 1)
    CREATE  Time-Range Partitioning
    CREATE  Tenant Sharding                  (superseded, retained)
    CREATE  Adopt Time-Range Partitioning
    CREATE  Does time-range partitioning survive sub-second retention
    LINK    Read Latency informed_by Horizontal Partitioning
    LINK    Time-Range Partitioning evolves_from Tenant Sharding
    NO_OP   customer-key skew generalization   (unendorsed; queued, not written)

**ContradictionDetector** — Q1 versus August is the interesting case. Same
asserter, different dates, incompatible claims → **temporal evolution**, not
`CONFLICT`. Handled automatically, both notes preserved, no human needed. Had
two *different* sources asserted incompatible things at the same time, that
would be `CONFLICT` → review queue.

## Temporal semantics in the fixture

`Tenant Sharding` is the retroactive case:

    created:     2026-08-26   # when the note was written
    asserted_at: 2026         # when the position was held
    valid_until: 2026-08-24   # when it stopped applying

The source says "back in Q1". The schema has no quarter precision, so
`asserted_at` degrades to the coarsest **true** value rather than being
sharpened into an invented `2026-01`. Losing precision is correct; inventing
it is not.

## The two failures this fixture exists to prevent

1. **Inference becoming belief.** Element 4 is the trap. The assistant
   proposed a generalization; the engineer said "maybe, not sure that's always
   true." If that ever appears as `#e/user_position`, the system has failed at
   its primary job.

2. **History erased by an update.** Element 6 is the other trap. The naive
   implementation overwrites the Q1 position with the August one, and then
   there is no way to know the view ever changed, or when, or why.

## Using this fixture

    python3 _system/validate.py

When the schema changes, update `expected/` first and make the validator
pass. This fixture is the schema's regression test.
