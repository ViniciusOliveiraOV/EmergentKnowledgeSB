# EmergentKnowledgeSB

> **An agent-native, provenance-preserving framework for emergent personal
> knowledge systems.**

`SB` = Second Brain.

![status](https://img.shields.io/badge/status-experimental%20%2F%20pre--alpha-orange)
![version](https://img.shields.io/badge/version-0.0.1--prealpha-blue)
![license](https://img.shields.io/badge/license-Apache--2.0-green)

**Experimental / Pre-alpha. Breaking changes expected.**


<img width="507" height="460" alt="image" src="https://github.com/user-attachments/assets/0df95f86-83a9-448b-a72c-9d4604963398" />


---

## What this is

This is **not** an Obsidian template.

Obsidian is the current reference interface and storage environment. What the
framework actually consists of is Markdown files, YAML frontmatter, stable
IDs, and a protocol for how knowledge is allowed to change. Those primitives
are meant to outlive any particular editor, and the knowledge must be able to
leave — for another frontend, a graph database, or an agent system that does
not exist yet.

The subject of the framework is not a folder structure. It is a protocol:

```text
RAW HISTORY
→ CANONICAL KNOWLEDGE
→ RELATIONS
→ SYNTHESIS
→ OPERATIONAL STATE
→ NEW QUESTIONS
```

Raw material is preserved immutably. Durable entities are extracted from it
and canonicalized so the same idea stays one node no matter how many times it
is discussed. Typed relations connect them. Higher-order documents are
assembled from those. Operational state is derived, never authored. The gaps
that surface become new questions, which drive new material — and the loop
closes.

## What the framework asserts

- **The knowledge base is canonical.** Not any model's proprietary memory. If
  a client's memory disagrees with the vault, the vault wins.
- **LLMs are replaceable cognitive engines.** They operate over the source of
  truth; they are not the source of truth. Swapping the model must never
  threaten the knowledge.
- **Provenance is mandatory.** Every durable claim traces to its origin.
  Fabricating a source, hash, date or location is the worst available failure,
  because it survives for years looking correct.
- **Agent inferences do not silently become user beliefs.** Six epistemic
  states are tracked explicitly. Promotion between them is a human act that an
  agent may propose and may never perform.
- **Historical evolution is never overwritten.** A changed position is
  appended, dated and linked; the prior position stays reachable. It must
  remain possible to reconstruct what was believed, and when it changed.
- **Autonomy is bounded by explicit permissions.** READ and SEARCH are free,
  CREATE is conditional, PATCH is append-only, RENAME and MERGE need review,
  DELETE is human-only, always.
- **Markdown-first portability is intentional.** No required plugin, no
  binary state, no proprietary API. Validation is stdlib Python.

## The machinery is not the product

Everything above describes the control plane: the mechanisms that keep
knowledge trustworthy. It is not the intended human experience. The
long-term success criterion is whether a person's knowledge becomes simpler,
more intelligible and more useful than the conversations it came from — a
system can report zero validation errors and still fail that test. See
[ADR-0006](_system/adr/adr-0006-human-cognitive-utility.md). The framing of
this README is provisional for the same reason.

## Principles

> Never summarize when you can integrate.
> Never duplicate when you can link.
> Never overwrite history when you can append evolution.

> Provenance over compression.
> Historical fidelity over superficial cleanliness.
> Canonicalization over duplication.
> Human interpretability over cleverness.
> Safety over autonomy.

## Layers

| Layer | Content | Mutability |
|---|---|---|
| **L0** | raw sources — conversations, papers, imports | append-only, hash-verified |
| **L1** | atomic knowledge — canonical entities | evolves, never overwritten |
| **L2** | synthetic knowledge — projects, MOCs, strategies | assembled from L1 |
| **L3** | operational state — dashboards, queues | regenerable |

## Epistemic status

Every claim carries one of six states, as an inline tag so that plain search
and Obsidian's tag pane both navigate them with no plugin:

| State | Means |
|---|---|
| `user_position` | the human asserted or endorsed it |
| `assistant_hypothesis` | a model proposed it, unendorsed |
| `external_fact` | verifiable outside claim, source recorded |
| `source_claim` | a source asserts it; truth not assessed |
| `inference` | derived by reasoning over existing content |
| `open_question` | unresolved |

The failure this prevents — a model's guess becoming, months later, something
you believe you always thought — is the single worst thing a system like this
could do to its owner.

## Repository layout

```text
_system/           architecture, validator, ADRs, generic fixture
  adr/             why the architecture is the way it is
  fixtures/generic synthetic fixture + expected output
_templates/        frontmatter schemas
_sources/          L0 — raw material
concepts/          L1 — concepts, principles, questions, people, technologies
references/        L1 — books, papers
decisions/         L1 — decisions
projects/          L2 — projects, roadmaps, maps of content
dashboards/        L3 — operational state
```

## Documentation

| Doc | Answers |
|---|---|
| [ARCHITECTURE](_system/ARCHITECTURE.md) | Layers, identity, relations, write paths |
| [ONTOLOGY](_system/ONTOLOGY.md) | Types, schema, epistemic status, language, time |
| [PROVENANCE](_system/PROVENANCE.md) | How claims trace to origin |
| [AGENT_RULES](_system/AGENT_RULES.md) | What an agent may do unattended |
| [INGESTION_PIPELINE](_system/INGESTION_PIPELINE.md) | How raw material becomes knowledge |
| [SECURITY](_system/SECURITY.md) | Permissions, network, untrusted input |
| [ADRs](_system/adr/) | The reasoning behind each decision |

Agents entering the repository start at [AGENTS.md](AGENTS.md).

Documentation uses `[[wikilinks]]` in some internal cross-references, which
render as literal text on GitHub. Every document is written to stay readable
without them.

## Validating

```bash
python3 _system/validate.py             # schema integrity across the vault
python3 _system/validate.py --selftest  # the validator's own regression checks
```

Requires Python 3 and PyYAML. Nothing else.

Seven warnings are expected: the fixture's notes deliberately live outside
their type's folder. **The pass criterion is zero errors, not zero warnings.**

## CORE vs INSTANCE

The framework (**CORE**) is generic and carries no assumptions about any
particular person. A vault built on it (**INSTANCE**) holds one person's
concepts, projects, positions, sources and decisions. Files declare which side
they belong to with `track: core` or `track: instance`.

**Personal material must never contaminate the core.** This repository
contains only `track: core` files. See
[ADR-0005](_system/adr/adr-0005-core-instance-separation.md).

The framework is developed by dogfooding it in a separate private instance:

```text
private instance
        ↓ dogfooding
finds architectural improvements
        ↓
EmergentKnowledgeSB upstream
```

Vendoring and version pinning between the two are deliberately not implemented
yet.

## Maturity

**Experimental. Pre-alpha. Breaking changes expected.**

- **No real corpus has been ingested.** Every statement about pipeline
  behaviour is a design intention, not an observation.
- The schema is **not empirically validated** — it has been tested only
  against the synthetic fixture in this repository.
- Canonicalization, contradiction detection, temporal-evolution handling and
  synthesis are **specified, not implemented**. `_system/validate.py` is the
  only executable component.
- **Not recommended as a stable template.** Adopting it now means adopting a
  schema that will change.

Maturation is gated on evidence, not dates: roughly three to five real manual
ingestions in a private instance before the ontology is revised and
`v0.1.0-alpha` is prepared.

## License

[Apache License 2.0](LICENSE).
