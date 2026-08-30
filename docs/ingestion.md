# Ingestion Pipeline

**Design only. Not implemented.** Genesis defines the contracts; Phase 1
implements the first three stages by hand, with a human reading every output.

    RAW SOURCE
      → TranscriptIngestor    → EntityExtractor  → Canonicalizer
      → Retriever             → MergePlanner     → KnowledgeWriter
      → GraphLinker           → ContradictionDetector
      → Synthesizer           → Dashboards

Each stage is a pure function over the workspace plus its input. Every stage but
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
workspace already believes. Read-only.

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

Adds relations from the [architecture](architecture.md) vocabulary. Prefers the most
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

**Three real manual ingestions before deciding what belongs in deterministic
code, what belongs in LLM reasoning, and what belongs in
agent orchestration.** Automate a stage only after doing it by hand three times.

The three corpora are chosen to exercise **different knowledge modes**, and
are ingested **separately and in order** — each completing its full review
cycle before the next begins:

| Ingestion | Knowledge mode under test |
|---|---|
| 1A | strategic / philosophical / existential — a long conversational corpus |
| 1B | operational / software / professional — real project material |
| 1C | operational / software / professional, plus cross-project reconciliation |

1A is a **torture test** for provenance, epistemic status, canonicalization,
temporal evolution, contradictions, refinements, decisions, user positions,
assistant hypotheses, external facts, emerging concepts and relations. It
enters as immutable L0 first, always.

1B introduces a second, unrelated knowledge domain — architecture, technical
decisions, requirements, bugs, tickets, project history, business context,
tasks, technologies, unresolved technical questions. 1C repeats that domain
against a workspace that already holds one like it, and is therefore the first
real test of whether the Canonicalizer reconciles across projects instead of
silently duplicating them.

> **The corpus tests the schema. The corpus does not become the schema.**
>
> A large, conceptually rich conversation will be tempting to accommodate by
> bending the ontology to fit it. Don't. The Genesis architecture is the prior
> framework; the corpus is evidence against it. Record where the schema
> strains, finish the ingestion under the existing rules, and change the
> schema deliberately afterwards — never mid-ingestion, and never because one
> source was impressive.

### Entity independence

Each corpus constructs its own subject as an **independent canonical entity**
first. Where one project is strategically broader than another, that breadth
is expressed as **relations**, never as containment:

> **Identity remains local; strategic significance is relational.**

A broader effort must not become a universal parent that absorbs every other
entity. Each project keeps its own history, architecture, goals, decisions,
business context, problems and state. Relations between projects are
considered only *after* canonicalization and reconciliation, and only where
source evidence supports them.

**Folder rule.** `projects/` is flat, as [epistemic model](epistemic-model.md) already requires. A
nested folder tree must never stand in for a semantic relationship.

Every ingestion is evaluated on **two independent dimensions** —
epistemic integrity and Human Cognitive Utility ([ADR-0006](adr/adr-0006-human-cognitive-utility.md)).
Zero validation errors is not success on its own; the second assessment is
written down even when unflattering, and the first is never weakened to
improve it.

### Per-ingestion review cycle

Run once per corpus, start to finish, before the next corpus begins. Human
reviews every step:

1. Ingest to `_sources/` as one `type: source` note (stage 1, by hand).
2. Extract 5–15 candidates, no more (stage 2, by hand).
3. Canonicalize against current workspace state — record which alias rules fire.
4. Produce a written merge plan; the human approves it line by line.
5. Write L1 notes. Commit separately from the source commit.
6. Note what strained in the schema — in the review queue, not in
   `_system/`. **Decide on schema changes after the ingestion, not during.**
7. Answer the Human Cognitive Utility questions
   ([ADR-0006](adr/adr-0006-human-cognitive-utility.md)): was the result easier to think
   with than the raw conversation, or only more correct? Record the honest
   answer, including how much maintenance ceremony the ingestion cost.

### Cross-project synthesis — after 1C only

Only once 1A, 1B and 1C have each completed the cycle above. The subjects
remain distinct entities; the graph may then surface evidence-supported
relations among them — competencies recurring across projects, activities
that advance a broader goal, reusable technical assets, decisions that reveal
capability, activities with weak strategic alignment, and recurring
technologies, architectural patterns or business problems.

**Do not pre-encode the answers.** Let relations emerge from evidence, use
the closed vocabulary in [architecture](architecture.md), and prefer the most specific true
relation. "The evidence does not support one" is a valid result. If an
important recurring relationship cannot be expressed with the existing set,
record **schema strain** in the review queue rather than extending the
ontology mid-ingestion.

### Evaluation after the third ingestion

**Epistemic integrity** — did the system preserve provenance, attribution,
uncertainty, temporal change, canonical identities, and entity independence?

**Human Cognitive Utility** ([ADR-0006](adr/adr-0006-human-cognitive-utility.md)) — can the
human now see what each project currently is, how they relate, which skills
are accumulating, what strategic progress exists, what remains unresolved,
which patterns cross project boundaries, and which useful relationships were
not visible in the raw source material?

> The first real sign the system works is not valid YAML. It is useful
> structure emerging across previously separate parts of the operator's
> working and intellectual life.
