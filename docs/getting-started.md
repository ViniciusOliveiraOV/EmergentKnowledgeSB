# Getting started

## Install

You need Python 3.11 or newer. Check with `python --version` (Windows) or
`python3 --version` (Linux/macOS).

```bash
python -m pip install git+https://github.com/ViniciusOliveiraOV/EmergentKnowledgeSB
```

If `eksb` is not found afterwards, your Python scripts directory is not on
`PATH`. `python -m eksb` works identically and always resolves.

To install for development instead, see [development.md](development.md).

## First run

```
eksb
```

You will be asked for a language, shown a three-sentence explanation, and
given four choices. Take the demo first — it costs nothing and is the
fastest way to see what the tool is for.

## The demo

```
eksb demo
```

This writes a small workspace containing one fictional engineering
conversation and the six notes extracted from it. Nothing in it refers to a
real person or project.

Then:

```
eksb search "partitioning"
```

Four surface forms — "sharding", "data sharding", "horizontal partitioning",
"partitioning" — all resolve to one note, because the alternatives are
recorded as aliases rather than as separate notes.

```
eksb provenance "Time-Range Partitioning"
```

Read the output carefully. It shows three claims on that note and labels each
one: two are *yours*, one was *suggested by an assistant and not confirmed*.
That third claim is the one the whole design exists to protect. In the source
conversation the engineer answered "maybe, not sure that's always true" — and
six months later that must still be visible.

It also shows the note is *a later version of* "Tenant Sharding", a position
that was held earlier and then reversed. The old note was not deleted.

```
eksb attention
```

Open questions, claims from outside that nobody has verified, suggestions you
never confirmed, and positions you have changed. Nothing here is invented —
every line is derived from what the notes already say.

## Your own workspace

```
eksb init "~/MyEKSB"
```

Any folder on any drive works, including paths with spaces and accents.
On Windows, `eksb init "C:\Users\You\Documents\MyEKSB"`.

The folder is yours. It contains:

```
_sources/      conversations and documents, kept word for word
concepts/      ideas, principles, questions, people, technologies
references/    books and papers
decisions/     choices you made, with what you turned down
projects/      projects, roadmaps, maps of content
dashboards/    generated views, safe to delete and rebuild
_templates/    the shape of each kind of note
_system/       the workspace marker and alias table
```

See [workspace-format.md](workspace-format.md) for what the files look like.

## Your first week

**Keep a conversation.** Export a chat to a text or Markdown file, then:

```
eksb save chat.md --kind chatgpt
```

It is copied verbatim into `_sources/` and fingerprinted. If anyone ever
edits it, `eksb validate` will say so. Raw history is append-only on purpose.

**Write down one thing you decided.**

```
eksb add --type decision "Use Postgres for the events table"
```

That creates a file with the right frontmatter already filled in. Open it in
any editor and write the three things that matter: what you decided, what you
turned down, and what it costs you.

**Tag who said what.** Inside a note, end a claim with its status:

```markdown
- Read latency is the constraint, not write throughput. #e/user_position
- This may generalize to any customer-derived key. #e/assistant_hypothesis
- PostgreSQL 10 added declarative partitioning. #e/external_fact
```

Those tags are what make `eksb attention` and `eksb provenance` useful. There
are six of them; [epistemic-model.md](epistemic-model.md) lists them all.

**Check in.**

```
eksb doctor      # is everything wired up?
eksb attention   # what did I leave unresolved?
```

## When something goes wrong

`eksb doctor` reports on the installation and the workspace. `eksb validate`
checks every note against the schema. Neither writes anything.

If a command fails with a message you don't understand, run it again with
`--debug` for the technical detail.
