# Connecting an AI assistant (MCP)

**Optional.** EKSB works without it. But this is what it is for: an assistant
that can look things up in your history instead of making you re-explain the
project every time.

No API key is needed by EKSB. No account, no cloud, no port, no daemon.

## What actually happens

Your MCP client — Claude Code, Claude Desktop, or anything else that speaks
the protocol — starts `eksb mcp` as a child process when it needs it, talks
to it over that process's own standard input and output, and kills it when
it exits. There is no server listening on your machine.

```
your AI client  ──starts──>  eksb mcp  ──reads──>  your workspace folder
                <──JSON-RPC──>
```

`eksb about` will tell you the same thing with your paths filled in.

**Local memory is not a local model.** The workspace stays on your disk; the
model you are talking to can be anywhere. EKSB does not care which one it is,
and swapping it changes nothing about your knowledge — that is the point.

## Setting it up

```
eksb connect
```

That detects any MCP client already on the machine, tells you whether EKSB is
wired into it, and prints the exact configuration to paste. `eksb connect
--json` prints only the JSON, for scripting.

The configuration looks like this:

```json
{
  "mcpServers": {
    "eksb": {
      "command": "/path/to/python",
      "args": ["-m", "eksb", "mcp", "--workspace", "/path/to/MyEKSB"]
    }
  }
}
```

It names the interpreter EKSB is installed in, so it keeps working whether
you used a virtualenv, a system Python, or pipx.

**Claude Code**

```bash
claude mcp add-json eksb '{"command":"...","args":["-m","eksb","mcp"]}'
```

or drop a `.mcp.json` with the block above into a project directory.

**Claude Desktop** — paste into `claude_desktop_config.json`:

| Platform | Location |
|---|---|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

Then restart the client.

**Anything else** — it is a standard stdio MCP server. Point your client at
the command and arguments above.

If you leave `--workspace` off, the server uses the same workspace the CLI
would: the one at or above the working directory, else the one you last
opened.

## The tools

| Tool | What the assistant gets |
|---|---|
| `eksb_search` | matching notes — titles, types, ids and one line each |
| `eksb_get` | one note in full |
| `eksb_provenance` | a note's source, and **who asserted each claim** |
| `eksb_attention` | open questions, unconfirmed suggestions, changed positions |
| `eksb_workspace_status` | counts, validity, and each project's level |
| `eksb_ingest` | index a project directory's text |
| `eksb_submit_candidate` | propose durable knowledge — the only way to write |

Search returns lines rather than whole notes on purpose. The assistant
narrows first and fetches second, which is what makes it possible to give it
the relevant history without sending all of your history.

## What it cannot do

This is a narrow surface rather than filesystem access, and the difference is
the point:

- **It cannot record a claim as your position.** `user_position` submitted by
  an agent is refused outright. An assistant may propose; only you promote.
- **It cannot delete or rename anything.** Neither is in the tool set.
- **It cannot edit raw sources.** `_sources/` is append-only and hashed.
- **It cannot write an invalid note.** Everything goes through the same
  schema the CLI enforces.
- **It cannot overwrite what you wrote.** An update appends to the Claims
  section; existing text is never touched.
- **It cannot write into the demo.** The bundled demo is a fixed sandbox:
  readable, never writable. `eksb_workspace_status` reports
  `is_demo_sandbox`, so a well-behaved assistant tells you to create your own
  workspace rather than retrying.
- **It cannot resolve an ambiguity on your behalf.** A candidate that
  contradicts a superseded position, replaces an existing note, or traces to
  nothing goes to the review queue with one plain-language question.

## What comes back when it writes

```
CREATE            no match; written as a proposal
UPDATE            new claims appended to an existing note
NO_OP             already recorded; nothing to do
CONFLICT          ─┐ not written. One short question for you,
REVIEW_REQUIRED   ─┘ queued in dashboards/Review Queue.md
REJECTED          malformed, or something an agent may not assert
```

A well-behaved assistant puts the question to you in ordinary language:

> I found two conflicting database decisions. Which one is still current?

Not:

> Please review epistemic status, provenance and canonical merge disposition.

You will still see the queue in `eksb attention` if the assistant forgets.

## A working session

Ask your assistant to *"check my EKSB workspace before answering"*. A good
one will search, read provenance on what it finds, and tell you when a claim
it found was a previous model's guess rather than something you decided.

At the end of a working session, ask it to *"record what we decided in
EKSB"*. It submits a candidate; you see the file, or the question.

Nothing about that requires you to know the word "epistemic".

## Troubleshooting

The client shows no EKSB tools — check the interpreter path is the one EKSB
is installed in (`eksb connect` fills in the right one), and restart the
client.

Everything the server does is also a CLI command, so if `eksb search foo`
works in your terminal and the assistant cannot see anything, the problem is
the client's configuration, not EKSB.

To see the raw protocol:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | eksb mcp -w /path/to/MyEKSB
```
