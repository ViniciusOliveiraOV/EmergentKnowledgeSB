# Architecture

## Decisions

Why the architecture is the way it is: [`docs/adr/`](adr/). Read those before
proposing a change to anything in this document.

## Four layers

| Layer | Name | Nature | Written by |
|---|---|---|---|
| **L0** | Raw sources | Append-only. Verbatim. Never rewritten. | Ingestor only |
| **L1** | Atomic knowledge | One durable entity per note, evolving | Agent (constrained) + human |
| **L2** | Synthetic knowledge | Assembled from L1. Projects, MOCs, strategies | Agent (proposed) + human |
| **L3** | Operational state | Dashboards, queues, current bottleneck | Agent (regenerated) |

L1 is canonical. A concept discussed in twenty conversations is **one** L1
note with twenty provenance references — never twenty summaries.

L3 is the only layer safe to regenerate wholesale, because it contains no
knowledge that does not exist upstream in L0–L2. If a dashboard is deleted it
must be reconstructible.

## Folders

Folders are for humans and validation. **Links and metadata carry the meaning.**
Topic (climate, AI, philosophy) is expressed by tags and links, never by folder.

    _system/      the workspace marker and alias table    (meta)
    _templates/   frontmatter schemas                     (meta)
    _sources/     L0 — conversations, papers, imports
    concepts/     L1 — concept, person, organization, technology,
                       hypothesis, question, risk, goal, principle
    references/   L1 — book, paper (bibliographic entities)
    decisions/    L1 — decision (own folder: high churn, audit value)
    projects/     L2 — project, roadmap, moc
    dashboards/   L3 — dashboard

Eight folders, deliberately flat. Adding a ninth requires a reason written
into this file.

## Identity

`id` is durable and frozen at creation. **Filenames are not identity** —
a note may be renamed freely; its `id` may not change.

Format: `<prefix>-<yyyymmdd>-<slug>`

    c-  concept, principle, hypothesis, question, risk, goal
    p-  person          o-  organization      t-  technology
    b-  book            r-  paper             d-  decision
    prj- project        rm- roadmap           moc- map of content
    src- source (L0)    dsh- dashboard        doc- system doc

The slug records what the note was called at birth. It is a fossil, not a
name. Renaming the note does not renumber it.

Which *language* a canonical title uses is a separate question, settled in
[epistemic model](epistemic-model.md) § Canonical language. Two clocks — `created` (system time) vs.
`asserted_at` (knowledge time) — are settled in [epistemic model](epistemic-model.md) § Temporal
semantics. Neither is a folder or filename concern.

## Relations

Wikilinks stay usable everywhere. Typed relations live in frontmatter when
the relation's *kind* matters:

```yaml
relations:
  - rel: contradicts
    target: "[[Tenant Sharding]]"
    epistemic: user_position
    source: src-20260826-demo-conversation-01
    note: position changed 2026-08-26
```

`rel` and `target` are required. `epistemic` defaults to the note's
`epistemic_default`. `source` is required whenever the relation was asserted
by an agent rather than typed by the human.

### Vocabulary (closed set — extending it is a human edit to [epistemic model](epistemic-model.md))

| Relation | Meaning |
|---|---|
| `supports` | A is evidence/argument for B |
| `contradicts` | A and B cannot both hold |
| `depends_on` | A fails without B (logical) |
| `requires` | A needs B present (practical/resource) |
| `implements` | A is a concrete realization of B |
| `informed_by` | A was shaped by B, weaker than depends_on |
| `derived_from` | A was extracted/computed from B |
| `related_to` | associative, last resort |
| `replaces` | A supersedes B; B stays, marked superseded |
| `evolves_from` | A is a later state of B; history preserved |
| `questions` | A challenges B without refuting it |
| `applies_to` | A is a general thing used in specific context B |

Prefer the most specific relation that is true. `related_to` in bulk is a
sign extraction was lazy.

## Epistemic status

Every claim carries a status. In frontmatter, `epistemic_default` sets the
note's baseline. Individual claims override it with an inline tag:

    - Deliberate practice matters more than volume. #e/user_position
    - Attention markets grew 4x since 2019. #e/external_fact ([[src-...]])
    - This may generalize to team-scale autonomy. #e/inference

Tags (not YAML) because Obsidian's tag pane and search make them navigable
with zero plugins. See [epistemic model](epistemic-model.md) § Epistemic status for the six values.

## Write paths

**Design goal: as few concurrent writers as possible.**

Every writer that bypasses the validator is a way for the vault to become
inconsistent without anyone noticing. The reference architecture is a single
programmatic writer plus an audit log:

    filesystem + Git + <one agent>

Rules, independent of any machine:

- A network sync service that writes into the vault is a **second writer**.
  It bypasses both version control and schema validation. Enabling one is an
  architectural change, not a convenience setting.
- A REST/MCP surface is a **third writer** plus an attack surface. Do not add
  one while the agent already has filesystem access; the capability is
  already there. See [security](security.md).
- Adding any write path requires a decision record first, then localhost-only
  binding, then installation — in that order.

**Which writers are actually live on a given machine is instance state, not
framework architecture.** It belongs in a workspace's own notes, never in framework documentation — recording
a particular vault's UUID or config paths in a core document turns one
person's setup into an apparent framework assumption.

## Clients

The vault is a directory of Markdown. Any MCP-capable agent — Claude Code,
Hermes, Codex, a local model — reads and writes it under the same
[agent rules](agent-rules.md). No client gets privileged state. If a client's memory
disagrees with the vault, the vault wins.
