# EKSB

```
 ______ _  __  _____  ____
|  ____| |/ / / ____||  _ \
| |__  | ' / | (___  | |_) |
|  __| |  <   \___ \ |  _ <
| |____| . \  ____) || |_) |
|______|_|\_\|_____/ |____/
```

**Emergent Knowledge Second Brain — your knowledge should outlive the chat,
and the model.**

![status](https://img.shields.io/badge/status-alpha-orange)
![version](https://img.shields.io/badge/version-0.1.0--alpha-blue)
![license](https://img.shields.io/badge/license-Apache--2.0-green)
![python](https://img.shields.io/badge/python-3.11%2B-blue)

## Why?

You work with an AI assistant for weeks. Then the session ends, and so does
everything it knew. Next time you re-explain the project, re-litigate a
decision you already made, and get a confident suggestion that contradicts
one you accepted a month ago — with no way to tell which of the two you
actually agreed to.

**Your AI history should become reusable knowledge, not disposable context.**

EKSB keeps your decisions, sources and project history in plain Markdown that
belongs to *you* — not to one chat, one model or one provider. Connect an
assistant and it looks up the part it needs, instead of you pasting context
into every conversation.

For every claim, EKSB records **who said it**: you, an assistant, or a
source. So a model's guess never quietly becomes something you believe you
always thought.

## Try it in 2 minutes

Requires **Python 3.11 or newer**. Nothing else — no API key, no account, no
model.

**Windows** (PowerShell):

```powershell
python -m pip install git+https://github.com/ViniciusOliveiraOV/EmergentKnowledgeSB
eksb
```

**Linux / macOS**:

```bash
python3 -m pip install git+https://github.com/ViniciusOliveiraOV/EmergentKnowledgeSB
eksb
```

`eksb` asks for a language (English or Português) and offers you a demo: a
small fictional engineering discussion, already turned into knowledge.

```
eksb demo
eksb provenance "Time-Range Partitioning"
```

That second command is the one to read carefully. It shows a note's source,
and labels each of its claims — two the engineer asserted, one an assistant
suggested and nobody confirmed. Six months later, that difference is still
visible. That is the whole idea.

## The loop

```
1. install EKSB
2. try the demo
3. add a project              eksb ingest ~/Projects/atlas
4. connect an AI assistant    eksb connect
5. work normally
6. EKSB is the memory your assistant reads from — and writes back to
```

Step 4 is the one that matters. Adding a directory is preparation, not the
payoff.

Your assistant searches your history instead of asking you to repeat it, and
at the end of a session records what you decided. The next session — a
different model, a different tool — inherits it.

**Local memory is not a local model.** The workspace stays on your disk; the
assistant can be Claude Code, an IDE, or anything else that speaks MCP.
Swapping the model changes nothing about your knowledge.

## What EKSB gives an agent that a folder does not

- **Selective retrieval.** It asks for the relevant history rather than
  loading the whole project into every context window.
- **Attribution.** It can tell your decision apart from a previous model's
  suggestion — and is refused if it tries to record its own guess as your
  position.
- **What changed.** Superseded positions are kept and marked, so it knows
  what you used to think and when that stopped being true.
- **Where it came from.** Every claim traces to a source that is still there,
  hashed, unedited.
- **A place to write back.** Safe additions land as proposals; genuine
  ambiguity becomes one short question for you, not a form to fill in.

We are not claiming measured token savings — there are no benchmarks yet. The
design goal is stated plainly: *give AI agents the relevant history without
sending all of your history every time.*

## Without an assistant

EKSB is still a working tool on its own: search, provenance, decisions,
changed positions, and a review queue, over Markdown you can edit in any
editor. That is genuinely useful — but AI-assisted longitudinal work is what
it is built for.

## What happens when you run it

Run `eksb` with no arguments for a menu — where things stand, search,
projects, add something, connect an assistant, what needs attention. Or use
the commands directly; `eksb --help` lists them and
[docs/cli.md](docs/cli.md) documents each one.

## Your data

A folder of Markdown and YAML you can read, edit, grep, back up and move.
**Nothing runs in the background, nothing is uploaded, no model is called,
and there is no telemetry.** The MCP server exists only while your AI client
is running it — no port, no daemon. `eksb about` says all of this with your
actual paths filled in.

## Honest about what it does not do

Pointing EKSB at a directory does not mean it understands the directory.
There are three levels, and it tells you which one you are at:

| | |
|---|---|
| **registered** | EKSB knows where the project is |
| **indexed** | its text is here, hashed and searchable — **not** understood |
| **integrated** | durable knowledge exists, traced back to that text |

Getting from indexed to integrated takes judgment: yours, or a connected
assistant's, reviewed. EKSB ships no built-in LLM and will not pretend a
regex turned your README into a decision record. See
[docs/knowledge-levels.md](docs/knowledge-levels.md).

## Where it sits

Not a replacement for the tools you use — a different layer.

| | |
|---|---|
| Note apps | store and organize what you write |
| Provider memory | remembers you, inside one product's ecosystem |
| Plain RAG | retrieves passages that look relevant |
| **EKSB** | portable knowledge with provenance, attribution, changed positions and typed relations — reusable by any model |

They compose. EKSB is a folder of Markdown, so Obsidian can open it, and
nothing stops you indexing it with something else.

## Languages

The CLI speaks **English** and **Português (Brasil)**. Pick one on first run,
change it with `eksb config --set-lang pt-BR`. Documentation is in English.

## Status

**v0.1.0-alpha.** The end-to-end loop works and is tested; the schema may
still change between alpha releases.

## Documentation

| Doc | Answers |
|---|---|
| [Getting started](docs/getting-started.md) | Install, first workspace, first week |
| [Connect an AI assistant](docs/integrations/mcp.md) | MCP setup, the tools, the limits |
| [Knowledge levels](docs/knowledge-levels.md) | registered vs. indexed vs. integrated |
| [CLI reference](docs/cli.md) | Every command and flag |
| [Workspace format](docs/workspace-format.md) | What is in the folder, and why |
| [Epistemic model](docs/epistemic-model.md) | Types, schema, the six statuses, time |
| [Provenance](docs/provenance.md) | How claims trace to their origin |
| [Relations](docs/relations.md) | The twelve link types and when to use each |
| [Architecture](docs/architecture.md) | Layers, identity, write paths |
| [Agent rules](docs/agent-rules.md) | What an AI agent may and may not do |
| [Ingestion](docs/ingestion.md) | How raw material becomes knowledge |
| [Security](docs/security.md) | Permissions, network, untrusted input |
| [Obsidian](docs/integrations/obsidian.md) | Optional, and why it just works |
| [ADRs](docs/adr/) | Why each decision was made |
| [Contributing](CONTRIBUTING.md) | Setup, tests, boundaries |

## License

[Apache License 2.0](LICENSE).
