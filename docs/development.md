# Development

## Layout

```
eksb/
  cli.py         argparse commands, the interactive menu, all rendering
  workspace.py   reading and writing a workspace: notes, search, provenance
  validate.py    the schema validator, and its own selftest
  i18n.py        every user-facing string, en and pt-BR
  config.py      app settings, kept outside every workspace
  data/demo/     the bundled demo workspace
  data/scaffold/ what `eksb init` copies
docs/            this documentation
tests/           the suite
```

Five modules. Rendering lives in `cli.py` and nowhere else; `workspace.py`
returns data and never prints.

## Running from a checkout

```bash
python -m pip install -e ".[dev]"
python -m eksb            # same as the `eksb` command
python -m eksb.validate --selftest
```

## Conventions

**Nothing POSIX-only.** `pathlib` for paths, `shutil` for copies, no shelling
out, no assumption about `/`, `$HOME`, `/tmp` or which utilities exist. Paths
with spaces, accents and non-Latin characters must work; there are tests for
that.

**Every user-visible string goes through `t()`.** No literals in `cli.py`
output. Keys are namespaced by area (`menu.`, `ws.`, `prov.`, `att.`,
`doc.`, `about.`, `save.`, `add.`).

**Errors are sentences.** Raise `UserError(message, hint)` for anything a
person can fix; it prints the message and the hint and exits 1. A traceback
reaching the user is a bug — `--debug` is where the technical detail lives.

**No dead UI.** The main menu builds its option list from what is actually
available: without a workspace, the options that need one are not offered.
If a capability is not implemented, it does not get a menu entry.

## The validator

`validate(root)` returns `(errors, warnings, note_count)` and never raises on
note content. Errors are schema violations; warnings are advisory
(an untagged claim, a source with no hash).

`selftest()` builds one note that violates every rule in a temp directory and
asserts each violation is caught, plus a valid note that must produce nothing.
When you change a rule, extend the selftest in the same commit — it is the
validator's regression case and it runs in CI.

## Adding a command

1. `cmd_*` function in `cli.py`, returning an exit code.
2. A subparser in `build_parser()`.
3. A branch in `dispatch()`.
4. Strings in both languages in `i18n.py`.
5. A menu entry, only if it works without further setup.
6. A test, and a row in [cli.md](cli.md).

## The demo workspace

`eksb/data/demo/` is a real workspace that must validate with **zero errors
and zero warnings** — CI checks this. It is also the specification by example
for what extraction should produce; [demo-walkthrough.md](demo-walkthrough.md)
explains what each note is demonstrating and why.

If you change the schema, update the demo first and make the validator pass.

Editing the body of the demo source note changes its `content_hash`. Recompute
it — `sha256` of the body, everything after the closing `---` of the
frontmatter — or `eksb validate` will correctly report that raw history was
tampered with.

## Releasing

1. Bump `__version__` in `eksb/__init__.py`, `version` in `pyproject.toml`
   and `VERSION`. They must agree.
2. Update `CHANGELOG.md`.
3. Green CI on Ubuntu, Windows and macOS.
4. Run the [Void Linux smoke test](testing/void-linux-smoke-test.md) or an
   equivalent on a machine that has never had EKSB on it.
5. Tag.

Nothing is published to PyPI yet.
