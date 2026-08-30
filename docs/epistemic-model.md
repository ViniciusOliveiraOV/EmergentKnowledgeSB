# Ontology

Small on purpose. A type earns its place by changing how a note is *used*,
not by being a different topic. "medieval history" is a tag; `concept` is
a type.

## Types

| Type | Layer | Qualifies when | Folder |
|---|---|---|---|
| `concept` | L1 | A durable idea you will refer back to by name | concepts/ |
| `principle` | L1 | A concept stated as a rule you intend to act on | concepts/ |
| `hypothesis` | L1 | A claim that could be tested and is not yet settled | concepts/ |
| `question` | L1 | An open question worth returning to | concepts/ |
| `risk` | L1 | A named way things could go wrong | concepts/ |
| `goal` | L1 | A desired end state with an owner | concepts/ |
| `person` | L1 | A human referenced more than once | concepts/ |
| `organization` | L1 | A company, lab, institution, government body | concepts/ |
| `technology` | L1 | A tool, protocol, model, language, system | concepts/ |
| `book` | L1 | A book, read or unread | references/ |
| `paper` | L1 | A paper, preprint, article | references/ |
| `decision` | L1 | A choice made, with alternatives rejected | decisions/ |
| `source` | L0 | Raw ingested material | _sources/ |
| `project` | L2 | Sustained effort with state and an end | projects/ |
| `roadmap` | L2 | Ordered plan across time | projects/ |
| `moc` | L2 | Map of content — curated entry point to a domain | projects/ |
| `dashboard` | L3 | Regenerable view of current state | dashboards/ |
| `doc` | meta | System documentation | _system/ |

### Boundary calls

- **concept vs. principle** — if you would ever say "I should X because of it",
  it is a principle. Otherwise concept.
- **hypothesis vs. question** — a hypothesis proposes an answer; a question
  does not.
- **concept vs. project** — a project has state that changes and can finish.
- **decision** — created when an alternative was *rejected*. If nothing was
  given up, it is not a decision, it is a note.
- **person/organization** — create on second mention, not first. One-off name
  drops stay inline.
- Cannot decide? Use `concept` and let the note tell you later. Retyping is
  cheap; a fragmented graph is not.

## Frontmatter schema

Required on every note:

```yaml
schema_version: 1
type: concept          # from the table above
id: c-20260826-slug    # durable, frozen, see ARCHITECTURE § Identity
title: Human Title     # may differ from filename
created: 2026-08-26    # SYSTEM time — see § Temporal semantics
```

Optional, semantics fixed:

```yaml
track: core | instance         # which side of the boundary — see ADR-0005
publishable: false             # known non-public material, marked explicitly
updated: 2026-08-26
asserted_at: 2026-03           # KNOWLEDGE time — when it was actually held
valid_from: 2026-03            # when it began to apply, if different
valid_until: 2026-08-24        # when it stopped applying
aliases: [Sharding, Data Sharding]      # feeds the Canonicalizer
tags: [governance, policy]              # topic only, never type or status
epistemic_default: user_position        # baseline for unmarked claims
status: active | superseded | draft | archived
superseded_by: "[[Newer Note]]"         # required when status: superseded
sources: [src-20260826-demo-conversation-01]   # provenance, see PROVENANCE
relations: []                           # see ARCHITECTURE § Relations
confidence: high | medium | low         # the human's, not the model's
review: 2026-11-01                      # date this should be revisited
```

Unknown keys are allowed and ignored by the validator — the vault outlives
this schema. Renaming or repurposing an existing key is a breaking change and
requires bumping `schema_version`.

`aliases` is the single most load-bearing optional field: it is how
`sharding` / `data sharding` / `horizontal partitioning` stay one entity.

## CORE / INSTANCE

`track` declares which side of the framework boundary a file belongs to:

    track: core       generic framework — no assumptions about any person
    track: instance   one person's knowledge, configuration, machine state

Personal preferences, beliefs, projects and data must never appear in a
`track: core` file. Core documentation names the framework, never the
instance. Material known to be non-public carries `publishable: false`.

At `v0.0.1-prealpha` the boundary is **declarative, not enforced** — labelled
per file, not split by repository. Enforcement is deferred deliberately; see
[ADR-0005](adr/adr-0005-core-instance-separation.md).

An undeclared `track` on a system document is an unanswered question, not a
neutral default, and the validator warns about it.

## Architectural Decision Records

`docs/adr/` records why the architecture is the way it is. ADRs use their
own minimal frontmatter — `id`, `track`, `status`, `date` — and five fixed
sections: Context, Decision, Rationale, Consequences, Revisit when. The `id`
must match the filename (`adr-NNNN-slug`). Validated as a distinct shape, not
as a note.

Write one when a decision constrains future work and its reasoning would
otherwise be lost. Do not write one for reversible details.

## Canonical language

> Canonical titles use the language in which the concept has its strongest
> established identity.

- **User-originated** philosophical, existential or personal concepts keep
  **the operator's own language** — a concept you coined is named in the
  language you coined it in.
- **Internationally established** technical, academic or institutional
  concepts keep **their canonical name**. `[[Ambient Intelligence]]`,
  `[[Digital Twin]]`, `[[Conflict-Free Replicated Data Type]]`

Cross-language discoverability is `aliases`, always — never a second note. A
coined concept and its English gloss are one entity with two surface forms.
**A translation is never a reason to create a node.**

Where identity is genuinely contested (a Portuguese term for an English
concept you have made your own), pick one, alias the other, and move on. The
cost of the wrong choice is a rename; the cost of two nodes is a split graph
that quietly gets worse for years.

A workspace's `_system/aliases.yml` equivalence table exists to enforce
this mechanically — see [ingestion](ingestion.md) § Canonicalizer step 5.

## Temporal semantics

Two clocks. Confusing them is how a vault loses the ability to say *when you
believed something*.

    created      = SYSTEM time      — when the node was created in the vault
    asserted_at  = KNOWLEDGE time   — when the position was actually held

`created` is **never** backdated to when an idea was first expressed. A
position held in March 2026 and extracted in August 2026 has
`created: 2026-08-26` and `asserted_at: 2026-03`. Both are true; they answer
different questions.

| Field | Answers |
|---|---|
| `created` | When did this note come into existence? |
| `updated` | When was the note last touched? |
| `asserted_at` | When did the human actually hold or state this? |
| `valid_from` / `valid_until` | Over what period did it apply? |
| `decided_on` (decisions) | When was the commitment made? |
| `source_date` (L0) | When was the raw material produced? |
| `ingested_at` (L0) | When did it enter the vault? |

**Imprecision is honest.** `asserted_at` accepts `YYYY`, `YYYY-MM`, or
`YYYY-MM-DD`. If a transcript says "back in March", write `2026-03`. Do not
invent `2026-03-01` to satisfy a date parser — that is fabricated provenance
under [provenance](provenance.md) rule 2.

Retroactive nodes are normal and expected: real ingestion constantly
surfaces positions older than the vault itself.

## Epistemic status

Six values. Mandatory distinction — the whole system depends on it.

| Value | Means | May become a user belief by |
|---|---|---|
| `user_position` | The human asserted or endorsed it | — it already is one |
| `assistant_hypothesis` | A model proposed it, unendorsed | explicit human endorsement |
| `external_fact` | Verifiable claim from outside, source recorded | verification, keeps source |
| `source_claim` | A source asserts it; truth not assessed | promotion to external_fact w/ evidence |
| `inference` | Derived by reasoning over vault content | explicit human endorsement |
| `open_question` | Unresolved | being answered, then restated |

Inline form: `#e/user_position`, `#e/inference`, etc.

**Promotion is always an explicit, logged human act.** An agent may propose a
promotion in a review queue. An agent may never perform one. The failure mode
this prevents — a model's guess becoming, six months later, something you
believe you always thought — is the single worst thing this system could do
to you.
