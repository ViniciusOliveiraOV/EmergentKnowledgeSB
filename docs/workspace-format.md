# Workspace format

A workspace is a directory of Markdown files with YAML frontmatter. There is
no database, no index, no lock file and no binary state. Everything EKSB
knows, it reads from the files at the moment you ask.

That is the point: the knowledge has to be able to leave — for another tool,
another editor, or an agent that does not exist yet.

## Layout

```
_system/workspace.yml   marks the directory as a workspace; holds its name
_system/aliases.yml     hand-curated equivalences (ships empty)
_templates/             the shape of each kind of note
_sources/               raw material, word for word, append-only
concepts/               ideas, principles, questions, people, technologies
references/             books, papers
decisions/              choices made, with what was rejected
projects/               projects, roadmaps, maps of content
dashboards/             generated views — safe to delete and rebuild
```

Eight folders, flat. Folders exist for humans and for validation; **meaning
is carried by links and metadata, never by folder nesting.** Topic is a tag,
not a directory.

Which folder a note belongs in follows from its `type` — see
[epistemic-model.md](epistemic-model.md). `eksb validate` enforces it.

## A note

```markdown
---
schema_version: 1
type: principle
id: c-20260826-time-range-partitioning
title: Time-Range Partitioning
created: 2026-08-26
asserted_at: 2026-08-24
aliases: [Partition By Time Range]
tags: [databases]
epistemic_default: user_position
status: active
sources: [src-20260826-demo-conversation-01]
relations:
  - rel: evolves_from
    target: "[[Tenant Sharding]]"
    epistemic: user_position
    source: src-20260826-demo-conversation-01
---

## Definition

Partition by time range within a single cluster.

## Claims

- Time-range partitioning within one cluster is the current position.
  #e/user_position
- Any partition key derived from a customer attribute may have the same skew
  problem. #e/assistant_hypothesis
```

Five keys are required: `schema_version`, `type`, `id`, `title`, `created`.
Everything else is optional with fixed meaning. Unknown keys are allowed and
ignored — the workspace outlives this schema.

## The three things worth understanding

**`id` is identity; the filename is not.** Rename a note freely; its `id`
never changes. The slug inside the id records what the note was called at
birth. It is a fossil, not a name.

**`aliases` prevents fragmentation.** One idea stays one note no matter how
many words you have used for it over the years. This is the single most
load-bearing optional field.

**`#e/…` tags say who asserted a claim.** Six values, listed in
[epistemic-model.md](epistemic-model.md). They are inline tags rather than
frontmatter so that plain text search — and Obsidian's tag pane, if you use
it — navigate them with no plugin.

## Two clocks

`created` is when the *note* was made. `asserted_at` is when the *position
was held*. A view you held in March and wrote down in August has
`created: 2026-08-26` and `asserted_at: 2026-03`. Both are true; they answer
different questions.

Knowledge-time fields accept `YYYY`, `YYYY-MM` or `YYYY-MM-DD`, because
imprecision is honest. If a transcript says "back in March", write `2026-03`.
Never sharpen a vague date into a precise one to satisfy a parser.

## Sources are append-only

A note in `_sources/` carries a `content_hash` of its body, set at ingest.
`eksb validate` recomputes it. A mismatch means raw history was edited, which
is the one thing that must never happen silently — every claim extracted from
that source depends on it still saying what it said.

`eksb save` sets the hash for you.

## Editing by hand

Encouraged. It is Markdown. Use any editor, put the folder in Git, sync it
however you like. Run `eksb validate` afterwards and it will tell you if
something drifted out of shape.

The one rule: do not edit anything in `_sources/`.
