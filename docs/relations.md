# Relations

Twelve link types, closed set. Extending it is a deliberate human edit to
this file and to [epistemic-model.md](epistemic-model.md), not something an
agent may do.

```yaml
relations:
  - rel: evolves_from
    target: "[[Tenant Sharding]]"
    epistemic: user_position
    source: src-20260826-demo-conversation-01
    note: position reversed 2026-08-24
```

`rel` and `target` are required. `epistemic` defaults to the note's
`epistemic_default`. `source` is **required** whenever an agent asserted the
relation rather than a human typing it.

## The vocabulary

| Relation | Use when | Shown as |
|---|---|---|
| `supports` | A is evidence or argument for B | supports |
| `contradicts` | A and B cannot both hold | contradicts |
| `depends_on` | A fails without B — logical | depends on |
| `requires` | A needs B present — practical, resource | requires |
| `implements` | A is a concrete realization of B | is a concrete form of |
| `informed_by` | A was shaped by B; weaker than `depends_on` | was shaped by |
| `derived_from` | A was extracted or computed from B | was taken from |
| `related_to` | associative — last resort | relates to |
| `replaces` | A supersedes B; B stays, marked superseded | replaces |
| `evolves_from` | A is a later state of B; history preserved | is a later version of |
| `questions` | A challenges B without refuting it | questions |
| `applies_to` | A is a general thing used in specific context B | applies to |

The right-hand column is what `eksb provenance` prints, in the CLI's
language. The stored value never changes.

## Choosing

**Prefer the most specific relation that is true.** `related_to` in bulk is a
sign extraction was lazy — it records that two notes have something to do
with each other while discarding what.

**`replaces` vs `evolves_from`.** Both keep the old note. `replaces` is used
by the thing doing the replacing when the old one is simply out
(a decision retiring an approach). `evolves_from` is used when the new
position grew out of the old one and the change itself is part of the story.
In practice a reversal of your own position is `evolves_from` on the new
note, `contradicts` on the old one, and `status: superseded` with
`superseded_by:` pointing forward.

**`depends_on` vs `requires`.** "This argument collapses without that premise"
is `depends_on`. "This service will not start without that database" is
`requires`.

**`implements` vs `applies_to`.** `implements` goes from the specific to the
general — time-range partitioning *is a concrete form of* horizontal
partitioning. `applies_to` goes the other way — a general technique *applies
to* a specific problem.

## What relations are not

They are not folders. A project being strategically broader than another is a
relation between two independent notes, never one note containing the other.
Identity stays local; significance is relational.

They are not a graph database. Twelve names in YAML, read at query time. If
that ever stops being enough, that is a decision to record in an ADR, not a
dependency to add quietly.

## Cannot express something?

Record the strain in `dashboards/Review Queue.md` and keep going with the
closest true relation. Do not extend the vocabulary mid-ingestion because one
source was awkward — a rich source is evidence about the ontology, not an
amendment to it.
