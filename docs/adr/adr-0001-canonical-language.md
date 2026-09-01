---
id: adr-0001-canonical-language
track: core
status: accepted
date: 2026-08-26
---

# Canonical title language

## Context

A knowledge system used bilingually will encounter the same concept in both
languages. Naively, each surface form becomes a node, and the graph splits
along a language seam that has nothing to do with meaning. The split is
silent, compounds over years, and is expensive to repair once relations point
at both halves.

## Decision

Canonical titles use the language in which the concept has the strongest
established identity.

- User-originated philosophical, existential or personal concepts generally
  take the operator's own language.
- Internationally established technical, academic or institutional concepts
  keep their canonical name in the language that established them.
- Cross-language discoverability is handled through `aliases`, always.

**Translation alone is never sufficient reason to create another canonical
node.**

Where identity is genuinely ambiguous: choose one canonical identity, alias
the alternatives, and move on.

## Rationale

Identity should track the concept, not the words used to reach it. `aliases`
already exists, is already consulted by the Canonicalizer, and makes both
surface forms resolve to the same node — so a second node buys nothing and
costs graph coherence.

Deliberating over an ambiguous name is itself the failure mode. A naming
choice is reversible with a rename; fragmentation is not reversible in any
cheap way, because relations, provenance and history accumulate on both
halves in the meantime.

## Consequences

- Some canonical titles will be in one language, some in another. This looks
  inconsistent and is correct.
- `aliases` becomes load-bearing rather than decorative; an entity without
  its alternate forms recorded will re-fragment on the next ingestion.
- The Canonicalizer needs a cross-language equivalence table
  (`_system/aliases.yml`), which is instance-scoped configuration.
- Renames will happen. They are cheap by design: identity is the frozen `id`,
  not the filename.

## Revisit when

A third language enters regular use, or when equivalence-table maintenance
becomes a recurring cost rather than a rare edit.
