# Obsidian

**Optional.** EKSB does not need it, is not a plugin for it, and does nothing
to it. If you have never used Obsidian, skip this page — nothing is missing.

## Why it works anyway

A workspace is a folder of Markdown with YAML frontmatter and `[[wikilinks]]`.
That is also what an Obsidian vault is. So you can point Obsidian at your
workspace folder and it will open, with working links and a graph view, with
no configuration and no plugin.

The reverse is also true: an existing Obsidian vault will not become an EKSB
workspace on its own — run `eksb init` in it only if it is otherwise empty,
or create the workspace separately and move notes in as you convert them.

## What you get

- `[[wikilinks]]` between notes resolve
- the tag pane lists `#e/user_position`, `#e/assistant_hypothesis` and the
  rest, so you can browse claims by who asserted them
- the graph view draws the relations
- `aliases:` in frontmatter feeds Obsidian's own alias resolution, which is
  why that field is spelled the way it is

None of this needs a community plugin.

## What EKSB will not do

- install, launch, configure or read Obsidian
- write into `.obsidian/`
- require any plugin
- treat "Obsidian not detected" as a problem — `eksb doctor` lists it as
  optional and moves on

`eksb doctor` checks for an Obsidian config directory or an executable on
`PATH`, purely so it can tell you it found one. That is the entire
integration.

## If you use both

Two writers on one folder is worth thinking about. EKSB only writes when you
run a command, so there is no background process to collide with your editor
— but a sync service writing into the same folder is a genuine third writer
that bypasses both validation and version control. See
[../architecture.md](../architecture.md) § Write paths.

Keep `.obsidian/workspace.json` out of version control; it is per-machine UI
state, not knowledge.

## Removing it from the picture

Nothing to remove. Stop opening the folder in Obsidian.
