# Three levels: registered, indexed, integrated

Pointing EKSB at a folder does not mean EKSB understands what is in it. This
page exists so that distinction is never blurred — not in the product, not in
the documentation, and not by an assistant reading the workspace.

```
1  registered    we know where the project is
2  indexed       its text is here, hashed, searchable and citable
3  integrated    durable knowledge exists, traced back to that text
```

`eksb projects` shows which level each project is at. So does
`eksb_workspace_status` over MCP, deliberately, so a connected assistant
cannot mistake a pile of indexed files for settled knowledge.

## Level 1 — registered

```
eksb ingest ~/Projects/atlas --name Atlas
```

This refuses to run against the bundled demo, which is a fixed sandbox —
create your own workspace with `eksb init` first.

Creates one `type: project` note recording where the project lives. That is
all it establishes: a name and a path.

## Level 2 — indexed

The same command then walks the directory and copies its **prose** into
`_sources/`, verbatim and hashed.

What gets indexed: `.md`, `.markdown`, `.mdx`, `.txt`, `.rst`, `.adoc`,
`.org`, and extensionless files named like `README`, `CHANGELOG`,
`CONTRIBUTING`, `ARCHITECTURE`, `ROADMAP`, `NOTES`, `TODO`, `DECISIONS`.

What does not: source code, binaries, images, and anything under `.git`,
`node_modules`, `vendor`, `__pycache__`, `.venv`, `dist`, `build`, `target`,
`.next`, `.terraform`, caches, coverage output and editor directories. Files
over 1 MB are skipped, and the walk stops at 500 files. Both limits are
reportable and adjustable (`--max-files`).

Every run tells you what it did:

```
Indexed Atlas

     2  newly indexed
     1  changed since last time (earlier versions kept)
    14  already up to date
     9  skipped: 6 ignored (build, cache, dependencies), 2 not text, 1 too large
```

**Re-running is safe and cheap.** A file whose bytes have not changed is left
alone. A file that *has* changed produces a **new** source note linked
`evolves_from` the previous one — the old version stays. Raw history is
append-only; nothing is overwritten and nothing is destroyed.

There is no side index to keep in sync: the source notes already in the
workspace are the ledger, each carrying `origin_path` and `origin_hash`. If
you delete a source note, that file is simply indexed again next time.

### What level 2 is not

Indexed text is searchable and citable. It is **not** knowledge. Nothing has
decided which of two contradictory design notes is current, which decision
was reversed, or which sentence in a README is a live constraint rather than
a leftover from 2023.

The CLI says so every time it finishes indexing, and so does the MCP tool
result. If EKSB ever implied otherwise, it would be doing the exact thing it
exists to prevent: making unverified material look settled.

## Level 3 — integrated

Durable notes — concepts, principles, decisions, questions — with claims that
cite the source ids they came from, and typed relations to each other.

Getting from 2 to 3 takes judgment, and there are two honest ways to do it:

**You write it.** `eksb add --type decision "..."`, then say what you
decided, what you turned down, and what it costs. The indexed sources are
there to cite.

**A connected assistant proposes it.** With
[MCP](integrations/mcp.md) configured, it reads the indexed sources and
submits candidates. EKSB adjudicates: safe additions are written as
proposals, ambiguous ones become one short question for you. Its claims land
as `assistant_hypothesis` or `source_claim` — never as your position.

There is no third way. EKSB ships no built-in LLM and will not pretend a
regex turned your README into a decision record.

## Why the distinction is load-bearing

The failure this prevents is the one the whole project is organized around:
material that looks authoritative because a tool absorbed it, rather than
because anyone decided it was true.

A README that says "we use MongoDB" is a `source_claim` from a file of
unknown age. It is not your position, and it may be two migrations out of
date. Level 2 records it faithfully and says nothing about whether it holds.
Only level 3 — with a date, a source and an epistemic status — can tell you
that you moved to Postgres in August and this line was never updated.

Collapsing the levels would make the first case indistinguishable from the
second, which is how a knowledge base quietly becomes a liability.
