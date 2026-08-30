# Changelog

## 0.1.0-alpha — unreleased

First release intended to be installed and used by someone who did not write it.

### Added

- **`eksb` command**, cross-platform, installed via `pip`. Run with no
  arguments for an interactive menu; every capability is also a subcommand.
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

- No ingestion automation: turning a conversation into notes is still manual
  and human-reviewed.
- No MCP or REST surface — see ADR-0003.
- No daemon, server, GUI, cloud sync, account system or telemetry.

## 0.0.1-prealpha

Specification, ontology, ADRs, templates, a generic fixture, and a validator.
