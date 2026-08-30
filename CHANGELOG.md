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

### Changed

- The repository is now a Python project rather than a vault. Framework
  documentation moved from `_system/` to `docs/`; the vault skeleton moved
  into the package as the scaffold `eksb init` copies.
- The validator moved to `eksb/validate.py` and takes a workspace root, so it
  can check any workspace rather than only the repository.
- The generic fixture became the demo workspace. Its notes now live in the
  folders their types require, so it validates with zero warnings.

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
