# CLI reference

Everything is read-only except `init`, `demo`, `add`, `save`, `ingest`,
`workspace delete` and `config`. No command makes a network connection.

## Three surfaces, one implementation

> **Every ordinary human capability has a guided path. Every guided
> capability worth automating has a command. Infrastructure needs no menu
> entry.**

```
                        EKSB core
                            |
        +-------------------+-------------------+
        |                   |                   |
      menu                 CLI                 MCP
        |                   |                   |
   ordinary user       power user             agent
```

The menu and the commands call the same functions; neither is a reduced
version of the other. Someone who only ever types `eksb` can do everything
that constitutes normal use. Someone scripting over SSH can ignore the menu
entirely.

| Capability | Guided | Command |
|---|---|---|
| Try the demo | first run, menu | `eksb demo` |
| Reset the demo | menu, Manage workspaces | `eksb demo --reset` |
| Create a workspace | menu, Manage workspaces | `eksb init PATH` |
| Open another | menu, Manage workspaces | `eksb open PATH` |
| Stop using one | Manage workspaces | `eksb workspace forget` |
| Delete one from disk | Manage workspaces | `eksb workspace delete PATH --yes` |
| Where things stand | menu | `eksb status` |
| Search | menu | `eksb search QUERY` |
| Read a note | a search result | `eksb get ID` |
| Where it came from | menu | `eksb provenance ID` |
| What needs attention | menu | `eksb attention` |
| Add a note | Add something | `eksb add TITLE` |
| Keep a conversation | Add something | `eksb save FILE` |
| Add a project | Projects | `eksb ingest PATH` |
| List projects | Projects | `eksb projects` |
| Connect an assistant | menu | `eksb connect` |
| Check the workspace | menu | `eksb doctor` |
| Language, settings | Settings | `eksb config` |
| What runs, where data lives | Learn more | `eksb about` |

Four commands have no menu entry, deliberately. `eksb validate` is what
"Check my workspace" reports in plain words; `eksb get` is reached by picking
a search result; `eksb mcp` is started by an AI client and is not a human
task; `eksb help` lists the commands, and the menu is already that list. A
test enforces this table, so a capability cannot quietly gain one surface and
not the other.

```
eksb                       interactive menu (onboarding on first run)
eksb help [COMMAND]        list the commands, or explain one
eksb --help                the same list
eksb --version             version
eksb --debug <cmd>         show the technical error instead of a friendly one
eksb --lang en|pt-BR <cmd> language for this run only
```

## Workspaces

```
eksb init [PATH] [--name NAME]
```

Create a workspace. `PATH` defaults to the current directory. Refuses to
touch a folder that already holds a workspace or other files.

```
eksb open PATH
```

Remember `PATH` as the default workspace for later commands.

```
eksb workspace                       show which workspace is in use
eksb workspace forget                stop using it; deletes nothing
eksb workspace delete PATH [--yes]   delete it from disk
eksb forget                          shorthand for `workspace forget`
```

`forget` clears EKSB's reference and **deletes nothing** — reopen it any time
with `eksb open`.

`delete` is the destructive one. Interactively it asks you to type the folder
name; in a script it requires `--yes`, and refuses rather than prompting into
a closed stdin. `--yes` skips the question and nothing else: it will not
delete the demo (reset it instead), a filesystem root, your home directory,
any directory that contains it, or an ordinary folder that is not a
workspace. Symlinks are resolved before any of that is decided, so pointing a
link at a protected location does not get past it.

```
eksb ingest PATH [--name NAME] [--dry-run] [--max-files N] [-w PATH]
```

Register a project directory and index the prose inside it. Incremental:
unchanged files are skipped, changed files become new source notes and the
earlier versions are kept. Skips `.git`, `node_modules`, build output,
caches, binaries and files over 1 MB, and reports what it skipped and why.

**Indexing is not understanding** — see
[knowledge-levels.md](knowledge-levels.md).

```
eksb projects [-w PATH]
```

Every registered project and how far it has got: registered, indexed, or
integrated.

```
eksb demo [PATH] [--reset]
```

Install the bundled demo workspace and print what to try. `PATH` defaults to
a folder inside EKSB's own config directory, so it never lands in your
project. Running it again on an existing demo leaves it alone and says so.

`--reset` restores the demo to the packaged fixture, discarding whatever is
in it. Use it if an older EKSB let real material in before the sandbox rule
existed. It refuses to run against a workspace of your own, so it can never
be pointed at real work by mistake, and it asks for confirmation when run
interactively.

**The demo is a read-only sandbox.** Search, get, provenance, attention,
validate, doctor and about all work on it. `ingest`, `add`, `save` and MCP
writeback are refused, with a sentence telling you to create your own
workspace first — so a real project can never end up filed inside the
fiction. Nothing is migrated or deleted for you.

Interactively, that refusal offers to create a workspace there and then, and
the demo's menu carries **Create my workspace** and **Open an existing
workspace** as first-class options.

### How a workspace is found

In order: an explicit `-w/--workspace` (or the positional path, where a
command takes one), then the nearest workspace at or above the current
directory, then the one remembered by `eksb open` / `eksb init` / `eksb demo`.

If none is found you get a sentence, not a traceback:

```
I couldn't find an EKSB workspace here.
Create one with:  eksb init <folder>
```

## Reading

```
eksb search QUERY... [-w PATH]
```

Case-insensitive substring search over titles, aliases, ids, tags and bodies.
Title and alias matches rank above body matches.

```
eksb get ID|TITLE|ALIAS [-w PATH]
```

Print one note. Any of its id, its title or one of its aliases will find it.

```
eksb provenance ID|TITLE|ALIAS [-w PATH]
```

Where the note came from:

- the source note it was extracted from, its kind and its date
- each claim, with who asserted it in plain words
- what the note points at, and what points back at it

```
eksb attention [-w PATH]
```

What a human needs to look at, derived from the notes:

| Section | Comes from |
|---|---|
| Problems in the files | schema errors |
| Waiting in the review queue | non-empty entries in `dashboards/Review Queue.md` |
| Open questions | `type: question`, or `epistemic_default: open_question` |
| Suggested by an assistant | `#e/assistant_hypothesis`, `#e/inference` |
| Claims from outside | `#e/external_fact`, `#e/source_claim` |
| Positions you changed | `status: superseded` |
| Marked for review | a `review:` date in frontmatter |

## Writing

```
eksb add TITLE... [--type TYPE] [-w PATH]
```

Create a note from the workspace's template, with the id, title, type and
created date filled in. `--type` is one of `concept` (default), `principle`,
`question`, `decision`, `project`. The file lands in the folder that type
belongs to; open it in any editor and write.

```
eksb save FILE [--title TITLE] [--kind KIND] [-w PATH]
```

Keep a text or Markdown file as raw material. The body is copied **verbatim**
into `_sources/` and hashed, so a later edit is detectable. `--kind` is one
of `chatgpt`, `claude`, `codex`, `paper`, `book`, `web`, `personal_note`
(default), `voice`.

Raw sources are append-only. Do not edit them; extract from them.

## Checking

```
eksb validate [PATH] [--warnings-are-errors]
```

Check every note against the schema: required keys, id format, folder
placement, date precision, closed relation and status vocabularies, source
hashes, and untagged claims. Exit 0 means no errors. Warnings are advisory
unless you pass `--warnings-are-errors`.

```
eksb doctor [PATH]
```

Python version, EKSB version, workspace, note and connection counts, broken
references, config location, and which optional integrations are present. A
missing optional integration is never an error.

```
eksb about [PATH]
```

Where your data is, what runs in the background (nothing), what network
connections are made (none), which integrations are on, and how to remove
EKSB.

## AI assistants

```
eksb connect [--json] [-w PATH]
```

Detect MCP clients on this machine, say whether EKSB is wired into each, and
print the configuration to paste. `--json` prints only the configuration.

```
eksb mcp [-w PATH]
```

Run the MCP server: JSON-RPC over stdin and stdout. **You do not run this
yourself** — your AI client starts it, and it exits when the client does. No
port is bound and no daemon is left behind.

Tools: `eksb_search`, `eksb_get`, `eksb_provenance`, `eksb_attention`,
`eksb_workspace_status`, `eksb_ingest`, `eksb_submit_candidate`. The last is
the only write path, and it cannot delete, rename, edit raw sources, write an
invalid note, or record a claim as your own position. Full detail in
[integrations/mcp.md](integrations/mcp.md).

## Settings

```
eksb config
eksb config --set-lang en|pt-BR
eksb config --set-workspace PATH
```

Settings live outside every workspace, in a per-platform config directory:

| Platform | Location |
|---|---|
| Windows | `%APPDATA%\eksb\config.json` |
| macOS | `~/Library/Application Support/eksb/config.json` |
| Linux/BSD | `$XDG_CONFIG_HOME/eksb/config.json`, else `~/.config/eksb/config.json` |

Set `EKSB_CONFIG_DIR` to override it — useful for testing against a clean
environment. `NO_COLOR` disables colour output.

## Exit codes

`0` success · `1` a problem the message explains · `130` interrupted.
