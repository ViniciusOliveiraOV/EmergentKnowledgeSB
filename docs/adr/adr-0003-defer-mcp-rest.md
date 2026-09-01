---
id: adr-0003-defer-mcp-rest
track: core
status: superseded
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

---

**Update, v0.1.0-alpha.** Revisited and partly reversed. An MCP
surface is now implemented (`eksb mcp`), because the deciding factor
changed: the value is not remote access but *selective retrieval* —
an agent asking for the relevant history instead of being handed the
whole corpus. The reasoning below still governs its shape, and the
concerns were answered rather than dropped:

- **Not a network surface.** stdio only, started by the client as a
  child process, gone when it exits. No port is bound, nothing
  listens, and there is no daemon.
- **Not a second writer that bypasses validation.** The only write
  path is `eksb_submit_candidate`, which goes through the same schema
  and the same adjudication as any other write. It cannot delete,
  rename, edit `_sources/`, or record a claim as the user's position.
- **REST is still deferred**, on the original reasoning.

See [../integrations/mcp.md](../integrations/mcp.md).
