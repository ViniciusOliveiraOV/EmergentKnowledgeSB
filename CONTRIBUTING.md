# Contributing

EKSB is early. Bug reports, portability fixes and documentation are the most
useful things right now.

## Setup

```bash
git clone https://github.com/ViniciusOliveiraOV/EmergentKnowledgeSB
cd EmergentKnowledgeSB
python -m venv .venv
# Windows:      .venv\Scripts\activate
# Linux/macOS:  source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Tests

```bash
python -m pytest                        # the suite
python -m eksb.validate --selftest      # the validator's own regression case
python -m eksb.validate eksb/data/demo  # the bundled demo must stay clean
```

The suite runs against a temporary HOME and a temporary config directory, so
it never reads or writes your own workspace. Every test must keep that
property — if you need config, set `EKSB_CONFIG_DIR`.

CI runs this on Ubuntu, Windows and macOS across Python 3.11–3.13. Windows
and Ubuntu are release blockers.

## What to keep in mind

**CORE vs WORKBENCH.** *Core* is the format and its rules — types, ids,
relations, epistemic statuses, provenance, validation. *Workbench* is the CLI
that makes them usable. A change to core changes what every existing
workspace means; a change to the workbench does not. Be much more careful
with the first.

**Backward compatibility.** A workspace someone created must keep opening.
Adding an optional frontmatter key is fine — unknown keys are ignored by
design. Renaming or repurposing an existing key is a breaking change and
requires bumping `schema_version` and writing an ADR.

**Epistemic integrity is the one thing that cannot be traded away.** No
change may make it possible for an assistant's claim to become a user
position without an explicit human act, or for provenance to be invented when
it is unknown. An absent field is honest; a plausible invented one is
corruption that survives for years looking correct. If a feature is only
convenient when it fabricates, the answer is no.

**Simple surface, rigorous inside.** The machinery is allowed to be precise.
What the user reads is not allowed to require the vocabulary. "Where did this
come from?" over "query canonical provenance". New user-facing strings go
through [`eksb/i18n.py`](eksb/i18n.py) — never inline literals.

**No new required dependency.** PyYAML is the only one, and it earns its
place. Stdlib first. No daemon, no server, no database, no GUI, no
background process: if Markdown, YAML and Python solve it, use those.

## Proposing a new relation or epistemic status

Both vocabularies are closed on purpose. To extend either:

1. Show two real cases the existing set cannot express — not hypotheticals.
2. Show why the closest existing value is actually wrong, not just imprecise.
3. Write an ADR in `docs/adr/` (Context, Decision, Rationale, Consequences,
   Revisit when) and open it as a PR before any code.
4. Update `eksb/validate.py`, [docs/relations.md](docs/relations.md) or
   [docs/epistemic-model.md](docs/epistemic-model.md), and the phrasing table
   in `eksb/cli.py` for **both** languages.

"The evidence does not support one" is a valid outcome. Record schema strain
in a workspace's review queue instead of widening the vocabulary to fit one
awkward source.

## Adding a language

1. Copy the `"en"` block in `eksb/i18n.py`, translate the values, add the
   code to `LANGUAGES`.
2. Add translations to the `SPEAKER` and `REL` tables in `eksb/cli.py` —
   these are the phrases the CLI uses instead of the technical terms.
3. `test_both_languages_define_the_same_keys` and
   `test_every_ui_string_is_translated` will tell you what you missed.

Translate the meaning, not the words. These strings exist to keep people away
from the jargon; a literal translation of a term of art defeats them.

## Adding an integration

Optional, off by default, never required to run anything. It must not
introduce a required dependency, a background process, or a network call in
the default path, and `eksb doctor` must report its absence as normal rather
than as an error. See [docs/integrations/](docs/integrations/).

## Pull requests

Small and focused. Say what changed and why. Include a test for anything with
a branch in it. Run the three commands above before pushing.

No secrets, no personal data, no absolute paths from your machine, and no
examples drawn from real people or projects — fixtures are fictional. See
[docs/security.md](docs/security.md).

## Reporting a security issue

Do not open a public issue. Describe the class of problem privately to the
maintainer first.
