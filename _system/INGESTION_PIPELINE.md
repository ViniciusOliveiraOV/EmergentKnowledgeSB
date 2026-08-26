---
schema_version: 1
type: doc
track: core
id: doc-20260826-ingestion
created: 2026-08-26
title: Ingestion Pipeline
---

# Ingestion Pipeline

**Design only. Not implemented.** Genesis defines the contracts; Phase 1
implements the first three stages by hand, with a human reading every output.

    RAW SOURCE
      → TranscriptIngestor    → EntityExtractor  → Canonicalizer
      → Retriever             → MergePlanner     → KnowledgeWriter
      → GraphLinker           → ContradictionDetector
      → Synthesizer           → Dashboards

Each stage is a pure function over the vault plus its input. Every stage but
`KnowledgeWriter` is read-only. **One writer** is the core safety property:
no other stage may touch disk.

---

## 1. TranscriptIngestor  — raw → L0

In: an export file (ChatGPT JSON, Claude transcript, PDF, notes).
Out: one `type: source` note per conversation/document, verbatim body.

- Normalizes format, never content. Speaker turns preserved.
- Computes `content_hash` over the body. Sets `ingested_at`, `ingested_by`.
- Idempotent: re-ingesting the same `source_ref` is a NO_OP, not a duplicate.
- Writes only to `_sources/`. Never reads L1.

## 2. EntityExtractor  — L0 → candidate entities

In: one source note. Out: a list of candidates, in memory. Writes nothing.

Each candidate: `{surface_form, type, epistemic, claims[], excerpt_ref}`.

- `epistemic` is assigned from **who said it**, structurally, not from tone:
  human turn → `user_position`; model turn → `assistant_hypothesis`;
  cited external → `source_claim`. Never upgrade at this stage.
- Under-extract rather than over-extract. Ten good entities beat sixty noisy
  ones; noise is expensive to un-merge later.

## 3. Canonicalizer  — candidates → canonical identities

**The stage that decides whether the graph is worth having.**

Must collapse `sharding` / `data sharding` / `horizontal partitioning` /
`partitioning` into one identity, and must not collapse things that merely
look alike.

Resolution order:
1. exact `id` match
2. exact title match
3. `aliases` match (case/space/punctuation-normalized)
4. normalized-slug match — casefold, strip punctuation and spaces, collapse
   digits+separators (`society5` == `society 5.0`)
5. cross-language known-pairs table in `_system/aliases.yml` (`sociedade` ↔
   `society`) — a small hand-curated file, not a translation model
6. fuzzy/embedding similarity → **never auto-merges**; emits `REVIEW_REQUIRED`

Steps 1–5 may auto-resolve. Step 6 may only propose. When a new surface form
resolves to an existing entity, the form is added to that note's `aliases`
— that is a legitimate automatic PATCH, and it makes the resolver stronger
over time.

Homonyms are the inverse failure: two distinct things sharing a name are
disambiguated by title (`Bridge (protocol)`), never by silently merging.

## 4. Retriever  — canonical ids → existing state

Reads current L1/L2 for each resolved entity: existing claims, relations,
epistemic status, evolution history. Supplies the MergePlanner with what the
vault already believes. Read-only.

## 5. MergePlanner  — (new, existing) → operation plan

Emits an **explicit plan**. Never writes. Never overwrites.

| Op | When | Authority |
|---|---|---|
| `CREATE` | no canonical match, schema-valid | auto |
| `UPDATE` | new claim, append-only, provenance attached | auto |
| `LINK` | new typed relation between existing entities | auto |
| `NO_OP` | already present, nothing added | auto |
| `CONFLICT` | new claim contradicts existing | human |
| `REVIEW_REQUIRED` | ambiguous identity, merge, rename, low confidence | human |

The plan is a reviewable artifact — written to the review queue and, at
least through Phase 1, read by a human before execution.

## 6. KnowledgeWriter  — plan → disk

**The only stage that writes.** Executes `CREATE`/`UPDATE`/`LINK`/`NO_OP`
only. Refuses `CONFLICT` and `REVIEW_REQUIRED`, routing them to
`dashboards/Review Queue.md`.

- Validates frontmatter before writing; invalid output writes nothing.
- `UPDATE` appends to a section. Never rewrites a line it did not add.
- Each write is attributable in `git` to one source ingestion.

## 7. GraphLinker  — entities → typed relations

Adds relations from the [[ARCHITECTURE]] vocabulary. Prefers the most
specific true relation. A run producing mostly `related_to` is a failed run.
Relations asserted by an agent always carry `source` and `epistemic`.

## 8. ContradictionDetector  — the hard one

Must classify, not just flag:

| Kind | Signal | Action |
|---|---|---|
| **temporal evolution** | same asserter, different dates | append to `## Evolution`, keep both, auto |
| **refinement** | new is narrower/more precise, compatible | append, mark `evolves_from` |
| **contextual difference** | both true in stated different contexts | `applies_to` both, no conflict |
| **uncertainty** | one or both `low` confidence or hedged | open question, no conflict |
| **actual contradiction** | same context, same time, incompatible | `CONFLICT` → human |

Default when unsure: not a contradiction. A false contradiction erodes trust
in the detector; a missed one surfaces later anyway.

**A changed position is never an erasure.** Old text stays, dated, with the
new position appended and `evolves_from` linking them.

## 9. Synthesizer  — L1 → L2

Proposes updates to projects, MOCs, strategies from their constituent L1
notes. Output is always a diff proposal. **Synthesis is never authoritative
over its own sources** — if L2 disagrees with L1, L1 wins and L2 is stale.

## 10. Dashboards  — → L3

Regenerated, not edited. Bottleneck, active hypotheses, open questions,
review queue, unresolved contradictions, decisions awaiting action. Safe to
delete and rebuild — that is the test of whether a dashboard is really L3.

---

## Phase 1 — manual, review-driven

**Roughly three real manual ingestions before deciding what belongs in
deterministic code, what belongs in LLM reasoning, and what belongs in
future Hermes orchestration.** Automate a stage only after doing it by hand
three times.

The first corpus is an exported ChatGPT conversation — likely large. Treat it
as a **torture test** for provenance, epistemic status, canonicalization,
temporal evolution, contradictions, refinements, decisions, user positions,
assistant hypotheses, external facts, emerging concepts, and relations. It
enters as immutable L0 first, always.

> **The corpus tests the schema. The corpus does not become the schema.**
>
> A large, conceptually rich conversation will be tempting to accommodate by
> bending the ontology to fit it. Don't. The Genesis architecture is the prior
> framework; the corpus is evidence against it. Record where the schema
> strains, finish the ingestion under the existing rules, and change the
> schema deliberately afterwards — never mid-ingestion, and never because one
> source was impressive.

Human reviews every step:

1. Ingest to `_sources/` as one `type: source` note (stage 1, by hand).
2. Extract 5–15 candidates, no more (stage 2, by hand).
3. Canonicalize against an empty vault — record which alias rules fire.
4. Produce a written merge plan; the human approves it line by line.
5. Write L1 notes. Commit separately from the source commit.
6. Note what strained in the schema — in the review queue, not in
   `_system/`. **Decide on schema changes after the ingestion, not during.**
