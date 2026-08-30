# Demo walkthrough

`eksb demo` installs the workspace this page describes. Its `_sources/` note
is a fully synthetic engineering discussion; the notes in `concepts/` and
`decisions/` are what extraction should produce from it. Nothing refers to a
real person, project or organization.

It serves two purposes: it is the fastest way to see what EKSB is for, and it
is the **specification by example** for what good extraction looks like. It
must validate with zero errors and zero warnings — CI checks that.

Run `eksb provenance "Time-Range Partitioning"` while reading this.

## What it contains, by design

| # | Element | In the conversation | Expected handling |
|---|---|---|---|
| 1 | **Existing concept** | partitioning, under four surface forms | Canonicalizer collapses to one note; forms recorded in `aliases` |
| 2 | **New concept** | read latency as the binding constraint | `CREATE` — no canonical match |
| 3 | **Decision** | adopt time-range partitioning | `CREATE` decision; two rejected alternatives recorded |
| 4 | **Assistant hypothesis** | "any customer-derived key has the same skew" | stays `#e/assistant_hypothesis` — the engineer said "maybe"; **never promoted** |
| 5 | **External fact** | PostgreSQL 10 added declarative partitioning, Oct 2017 | `#e/external_fact`, source retained, marked unverified |
| 6 | **Change of position** | Q1: tenant sharding → Aug: time-range partitioning | temporal evolution; both notes kept, old one superseded not deleted |

## Stage-by-stage expected behaviour

**Ingestion** — writes one `type: source` note verbatim, sets
`content_hash`, touches nothing in L1.

**Extraction** — six candidates, no more. Epistemic status assigned
*structurally by speaker*: engineer turns → `user_position`, assistant turns
→ `assistant_hypothesis`. The PostgreSQL release claim is `external_fact`
because it is a verifiable outside claim, and it is written with a
verification caveat rather than as settled.

**Canonicalization** — the load-bearing case:

    sharding             ─┐
    data sharding        ─┤  normalized slug + alias table
    horizontal partitioning ─┤
    partitioning         ─┘

    → ONE entity. Four aliases persisted, so it cannot re-fragment.

**Merge planning** — against an empty vault:

    CREATE  Read Latency Is The Constraint
    CREATE  Horizontal Partitioning          (4 surface forms → 1)
    CREATE  Time-Range Partitioning
    CREATE  Tenant Sharding                  (superseded, retained)
    CREATE  Adopt Time-Range Partitioning
    CREATE  Does time-range partitioning survive sub-second retention
    LINK    Read Latency informed_by Horizontal Partitioning
    LINK    Time-Range Partitioning evolves_from Tenant Sharding
    NO_OP   customer-key skew generalization   (unendorsed; queued, not written)

**Contradiction handling** — Q1 versus August is the interesting case. Same
asserter, different dates, incompatible claims → **temporal evolution**, not
`CONFLICT`. Handled automatically, both notes preserved, no human needed. Had
two *different* sources asserted incompatible things at the same time, that
would be `CONFLICT` → review queue.

## Two clocks, in practice

`Tenant Sharding` is the retroactive case:

    created:     2026-08-26   # when the note was written
    asserted_at: 2026         # when the position was held
    valid_until: 2026-08-24   # when it stopped applying

The source says "back in Q1". The schema has no quarter precision, so
`asserted_at` degrades to the coarsest **true** value rather than being
sharpened into an invented `2026-01`. Losing precision is correct; inventing
it is not.

## The two failures the demo exists to show

1. **Inference becoming belief.** Element 4 is the trap. The assistant
   proposed a generalization; the engineer said "maybe, not sure that's always
   true." If that ever appears as `#e/user_position`, the system has failed at
   its primary job.

2. **History erased by an update.** Element 6 is the other trap. The naive
   implementation overwrites the Q1 position with the August one, and then
   there is no way to know the view ever changed, or when, or why.

## Working on the demo

    eksb validate eksb/data/demo

When the schema changes, update these notes first and make the validator
pass. The demo is the schema's regression test as well as its shop window.

Editing the source note's body changes its `content_hash` — recompute it, or
the validator will correctly report that raw history was tampered with.
