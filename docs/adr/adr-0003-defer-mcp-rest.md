---
id: adr-0003-defer-mcp-rest
track: core
status: accepted
date: 2026-08-26
---

# Defer MCP/REST integration

## Context

The reference environment exposes the knowledge base as plain files on disk.
An agent with filesystem access can already read, search, create and patch
notes. A REST or MCP surface (for example an Obsidian Local REST API plugin)
is often installed reflexively at this point.

## Decision

Do not install a REST plugin, MCP server, or additional community plugins
while the operating agent already has direct filesystem access.

Add one only when an external client genuinely requires it — an agent on
another host, a mobile client, or a model that cannot touch the filesystem.
When that happens, in order: a decision record first, then localhost-only
binding, then installation.

## Rationale

The integration would buy capability that already exists, and cost an
authenticated HTTP port, a credential to protect, a background process, and a
second write path that bypasses schema validation.

The prompt to install is usually architectural tidiness ("agents should talk
over a protocol"), not a capability gap. Tidiness is not worth an attack
surface on a store of years of personal thinking.

## Consequences

- Clients that cannot reach the filesystem are unsupported for now. This is
  accepted.
- The framework must not assume any HTTP surface exists; all tooling stays
  file-based and stdlib-only.
- Which integrations are live on a given machine is instance state.

## Revisit when

An external agent that cannot use the filesystem genuinely needs access.
