# Changelog

## 0.1.0-alpha — unreleased

First release intended to be installed and used by someone who did not write it.

The end-to-end loop it closes:

```
work history -> EKSB -> selective retrieval -> AI agent -> work
             -> structured writeback -> future retrieval
```

### Added

- **`eksb` command**, cross-platform, installed via `pip`. Run with no
  arguments for an interactive menu; every capability is also a subcommand.
- **`eksb mcp` — a generic MCP server**, spoken as plain JSON-RPC over stdio
  with no SDK and no new dependency. Seven tools: `eksb_search`, `eksb_get`,
  `eksb_provenance`, `eksb_attention`, `eksb_workspace_status`,
  `eksb_ingest`, `eksb_submit_candidate`. It belongs to EKSB — no vendor, no
  orchestrator, no private configuration. Started by the client, exits with
  it: no port, no daemon. `eksb connect` detects installed clients and prints
  the configuration to paste.
- **`eksb ingest PATH` — project directory ingestion.** Registers a project
  and indexes the prose inside it, skipping `.git`, `node_modules`, build
  output, caches, binaries and oversized files. Incremental: unchanged files
  are skipped, changed files become new source notes linked to the previous
  version, and nothing already indexed is destroyed. The source notes are
  their own ledger, so there is no side index to corrupt.
- **Three honest levels** — registered, indexed, integrated — reported by
  `eksb projects`, `eksb doctor` and `eksb_workspace_status`. Indexing a
  directory is never presented as understanding it.
- **A candidate lifecycle for agent writeback.** An agent proposes; EKSB
  decides: CREATE, UPDATE (claims appended, never overwritten), NO_OP, or
  CONFLICT / REVIEW_REQUIRED, which asks the user **one short question in
  ordinary language** instead of writing. The boundary the design exists for
  is enforced mechanically: a claim submitted as `user_position` by an agent
  is refused outright.
- **`eksb projects`** and a "Where things stand" screen: projects, knowledge
  count, connected assistants, what was touched recently, what is waiting.
- **English and Português (Brasil)** throughout the CLI. Chosen on first run,
  remembered, changeable with `eksb config --set-lang`.
- **Onboarding** — language, a three-sentence explanation, then a choice
  between the demo, a new workspace, or an existing one.
- **`eksb demo`** — a bundled fictional engineering discussion and the six
  notes extracted from it, demonstrating provenance, a changed position, an
  unendorsed assistant suggestion and an open question.
- **`eksb search`** over titles, aliases, ids, tags and bodies.
- **`eksb provenance`** — a note's source, each claim labelled with who
  asserted it, and its relations in plain language rather than schema terms.
- **`eksb attention`** — open questions, unconfirmed assistant suggestions,
  unverified outside claims, changed positions, review-queue entries.
- **`eksb add`** — a new note of a given type, pre-filled from the template.
- **`eksb save`** — keep a conversation or document verbatim as a hashed,
  append-only source.
- **`eksb init` / `eksb open`** — workspaces anywhere, including paths with
  spaces and non-Latin characters.
- **`eksb doctor`** — installation and workspace health. A missing optional
  integration is reported as normal, never as an error.
- **`eksb about`** — where data lives, what runs in the background (nothing),
  what network calls are made (none), and how to remove it all.
- **`eksb config`** — settings kept per-platform, outside every workspace.
- CI on Ubuntu, Windows and macOS across Python 3.11–3.13, covering install,
  the full command surface, both languages, Unicode paths, and detection of
  edited raw history.
- Documentation: getting started, CLI reference, workspace format, relations,
  development, a Void Linux smoke test, and integration pages for Obsidian
  and AI agents.

### Fixed

- **The demo no longer accepts real data.** Choosing the demo on first run
  made it the default workspace, so a later `eksb ingest ~/real/project`
  filed a real project into the fiction, silently. The demo is now a
  protected sandbox: reads work as before, and `ingest`, `add`, `save` and
  MCP writeback refuse with a sentence and the command to create a workspace
  of your own. Nothing is migrated or deleted automatically, and the demo is
  labelled `DEMO` in `doctor`, `about` and the status screen.
- **Getting out of the demo is now one step.** The demo's menu carries
  *Create my workspace* and *Open an existing workspace* directly, a refused
  write offers to create one on the spot, and typing a path that is not yet a
  workspace asks whether to create it there rather than dead-ending on "there
  is no EKSB workspace at …". The new workspace becomes active immediately;
  nothing is created without consent.

- **`eksb demo --reset`** restores the demo to the packaged fixture. A demo
  contaminated by an older EKSB — before the sandbox rule existed — is now
  recoverable in one command. It refuses to run against a workspace of your
  own, and a plain `eksb demo` no longer overwrites an existing demo.
- **Settings → Manage workspaces**: create, open another, stop using the
  current one, and — separately and destructively — delete it from disk.
  *Stop using* (`eksb forget`) clears the reference and deletes nothing;
  *Delete* asks you to type the folder name, refuses your home directory, and
  is never offered for the demo, which offers *Reset* instead.

- **`eksb status`** — the menu's "Where things stand" as a command.
- **`eksb workspace`** — `forget` and `delete PATH [--yes]`, so the two
  removals in Manage workspaces are scriptable too. Without `--yes` in a
  non-interactive session it refuses rather than prompting into a closed
  stdin.
- Picking a search result in the menu now shows the note itself as well as
  its provenance — `eksb get`'s guided equivalent.
- **Search results open by number.** `eksb search` on a terminal ends with
  `Open result [1-7, Enter to leave]`, and typing the number shows that note
  and its provenance. The number is that listing's alone: nothing is stored,
  and `eksb get 1` still means the note called `1`. Piped, the command lists
  and never prompts. Stable ids remain under each result, dimmed, for
  scripts, `eksb get` and MCP.
- **The ASCII identity is back on every interactive start**, not only on the
  first run. `eksb` opens with the logo, the product name and the version,
  then the compact `EKSB // Workbench` line and the workspace in use. It is
  shown once per run — returning from a submenu is not another arrival — and
  never when output is piped, on a terminal narrower than the logo, or by any
  subcommand.
- **`eksb help`** is a command, not an invalid choice. It used to print the
  list of commands only as part of an argparse error, and exit non-zero.
  `eksb help COMMAND` explains one — `eksb help ingest`, `eksb help workspace
  delete`. It is argparse's own help text, asked for the way people ask;
  a command that does not exist gets a sentence rather than "invalid choice".
  Each command's one-liner is now its description too, so `eksb help search`
  says what search is for and not only how to type it.
- **The guards on the one destructive command now live with the data.**
  `refuse_if_undeletable` sits next to the demo guard in `workspace.py`, so
  the menu, the subcommand and any later caller share one answer. It refuses
  a filesystem root, your home directory, any directory containing it, an
  ordinary folder that is not a workspace, and the demo — after resolving
  symlinks, so a link is not a loophole. `--yes` skips the question and
  nothing else.

### Changed

- The repository is now a Python project rather than a vault. Framework
  documentation moved from `_system/` to `docs/`; the vault skeleton moved
  into the package as the scaffold `eksb init` copies.
- The validator moved to `eksb/validate.py` and takes a workspace root, so it
  can check any workspace rather than only the repository.
- The generic fixture became the demo workspace. Its notes now live in the
  folders their types require, so it validates with zero warnings.

- **Surface parity is now a rule, and a test.** Every ordinary capability has
  both a guided path and a command; three commands are declared command-only
  with a reason (`validate`, `get`, `mcp`). Adding a capability to one surface
  and forgetting the other fails the suite.

### Not included

- **No built-in LLM.** EKSB calls no model and needs no API key. Semantic
  extraction happens through a connected agent, or by hand.
- No REST surface. MCP over stdio is the only programmatic writer, and it
  cannot delete, rename, edit raw sources or write an invalid note.
- No daemon, server, GUI, cloud sync, account system, vector database or
  telemetry.
- No measured token savings claimed — selective retrieval is a documented
  design goal, not a benchmarked result.

## 0.0.1-prealpha

Specification, ontology, ADRs, templates, a generic fixture, and a validator.
