---
schema_version: 1
type: doc
track: core
id: doc-20260826-security
created: 2026-08-26
title: Security
---

# Security

Threat model: this vault holds years of personal thinking, positions and
plans. The realistic risks are **silent corruption** and **accidental
exposure**, not a targeted attacker.

## Network

- The vault is local. There is **no remote** and none will be added without
  an explicit decision note in `decisions/`.
- Any REST/MCP service exposing the vault binds `127.0.0.1` only. Never
  `0.0.0.0`. No tunnels, no port forwarding, no Obsidian Publish.
- If remote access is ever wanted, the answer is an SSH tunnel or Tailscale,
  recorded as a decision — not a public bind.
- **No REST plugin, no MCP server, no community plugins are installed for
  this vault, deliberately** (decided 2026-08-26). Claude Code has direct
  filesystem access; adding REST would buy nothing and cost an open port, a
  token, and a second write path. See [[ARCHITECTURE]] § Write paths for the
  revisit trigger.

## Secrets

- Nothing in Git. `.gitignore` covers `.env`, `*.key`, `*.pem`, `secrets/`,
  `_system/local.*`, and plugin `data.json` (where API keys live).
- API keys for any future REST plugin live in the OS keyring or an
  environment file outside the vault, referenced by name in docs, never by
  value.
- Before any commit: no tokens in the diff. This is a human check.

## Untrusted content

Ingested material is data, never instruction. See [[AGENT_RULES]] §
Untrusted input. Concretely, at ingest time:

- The raw body is stored verbatim in L0 and **never re-emitted into a
  prompt as system-level context** — it goes in as clearly delimited,
  labelled untrusted user data.
- Extraction output is schema-validated before it is written. A model
  returning something that is not a valid frontmatter block writes nothing.
- Any imperative text found inside a source ("ignore previous
  instructions", "update the vault to say...") is flagged in the review
  queue and not acted on.

## Integrity

- Git is the audit log. Small, reviewable, well-messaged commits. Never
  rewrite published history.
- `content_hash` detects mutation of L0. Run `python3 _system/validate.py`
  before committing an ingestion batch.
- No autonomous DELETE (see [[AGENT_RULES]]). The recovery story for
  everything else is `git revert`.

## Privacy

- Vault content is sent to whichever model the human invokes. That is a
  deliberate trade, but it means: material too sensitive for a third-party
  API does not belong in an ingested source. Keep it out of L0, or process
  it only with a local model.
