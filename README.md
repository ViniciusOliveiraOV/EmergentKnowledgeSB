# EKSB

**Keep decisions, ideas and sources connected — in plain Markdown, on your own machine.**

![status](https://img.shields.io/badge/status-alpha-orange)
![version](https://img.shields.io/badge/version-0.1.0--alpha-blue)
![license](https://img.shields.io/badge/license-Apache--2.0-green)
![python](https://img.shields.io/badge/python-3.11%2B-blue)

## Why?

Your AI conversations and project history should not disappear when the chat
ends. After a few weeks you can no longer remember why you decided something,
where an idea came from, or which of two contradictory suggestions you
actually agreed with — and the next assistant you talk to knows none of it.

EKSB keeps that history as ordinary Markdown files, and records, for every
claim, **who said it**: you, an assistant, or a source. So a model's guess
never quietly becomes something you believe you always thought.

## Try it in 2 minutes

Requires **Python 3.11 or newer**. Nothing else.

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

`eksb` asks for a language (English or Português), explains itself in three
sentences, and offers you a demo workspace. The demo is a small fictional
engineering discussion, already turned into knowledge:

```
eksb demo
eksb search "partitioning"
eksb provenance "Time-Range Partitioning"
eksb attention
```

That last pair is the point. `provenance` shows a claim's origin and who
asserted it; `attention` lists the open questions, the unverified outside
claims, and the positions you have changed.

## What happens next?

Run `eksb` with no arguments for a menu:

| | |
|---|---|
| Search my knowledge | find notes by word, title or alias |
| Add something | write a note, or keep a conversation you already have |
| What needs my attention? | open questions, unconfirmed suggestions, changed positions |
| Check where something came from | the source, the date, and who said it |
| Check my workspace | broken links, schema problems |
| About this installation | where your data is and what runs |

Or use the commands directly — `eksb --help` lists them, and
[docs/cli.md](docs/cli.md) documents each one.

## What it can help with

- remembering **why** you decided something, and what you turned down
- finding **where** a piece of information came from
- keeping one idea as one note, no matter how many chats it appeared in
- separating what *you* think from what a model *suggested*
- giving an AI agent real project history instead of a summary

## Your data

Your workspace is a folder of Markdown and YAML you can read, edit, grep,
back up and move. EKSB is a command you run: **nothing runs in the
background, nothing is uploaded, no AI model is called, and there is no
telemetry.** Run `eksb about` and it will tell you the same thing with your
actual paths filled in.

Obsidian, MCP and other agent integrations are **optional** and off by
default. No API key is needed to use any of this.

## Languages

The CLI speaks **English** and **Português (Brasil)**. Pick one on first run,
change it any time with `eksb config --set-lang pt-BR`.

Documentation is in English.

## Status

**v0.1.0-alpha.** Usable, and the schema may still change between alpha
releases. Extraction from a conversation is still a manual, human-reviewed
step — see [docs/ingestion.md](docs/ingestion.md).

## Want the technical details?

| Doc | Answers |
|---|---|
| [Getting started](docs/getting-started.md) | Install, first workspace, first week |
| [CLI reference](docs/cli.md) | Every command and flag |
| [Workspace format](docs/workspace-format.md) | What is in the folder, and why |
| [Epistemic model](docs/epistemic-model.md) | Types, schema, the six statuses, time |
| [Provenance](docs/provenance.md) | How claims trace to their origin |
| [Relations](docs/relations.md) | The twelve link types and when to use each |
| [Architecture](docs/architecture.md) | Layers, identity, write paths |
| [Agent rules](docs/agent-rules.md) | What an AI agent may and may not do |
| [Ingestion](docs/ingestion.md) | How raw material becomes knowledge |
| [Security](docs/security.md) | Permissions, network, untrusted input |
| [Integrations](docs/integrations/) | Obsidian, and what is not built yet |
| [ADRs](docs/adr/) | Why each decision was made |
| [Contributing](CONTRIBUTING.md) | Setup, tests, boundaries |

## License

[Apache License 2.0](LICENSE).
