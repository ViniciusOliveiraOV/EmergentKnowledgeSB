"""End-to-end checks for the flows a first-time user actually walks through.

Everything runs against a temporary HOME and a temporary config dir, so a
developer's own workspace and settings are never touched or read.
"""
import io
import sys
from pathlib import Path

import pytest

from eksb import cli, config, i18n, workspace as ws
from eksb.validate import selftest, validate


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """A clean machine: no HOME config, no inherited workspace, no colour."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("APPDATA", str(home / "AppData"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    monkeypatch.setenv("EKSB_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "COLOR", False)
    i18n.set_lang("en")
    yield tmp_path


def run(*argv):
    """Run the CLI, capture stdout, return (exit code, output)."""
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        code = cli.main(list(argv))
    finally:
        sys.stdout = old
    return code, buf.getvalue()


# -- basics --------------------------------------------------------------
def test_validator_selftest():
    selftest()


def test_version_and_help():
    for flag in ("--version", "--help"):
        with pytest.raises(SystemExit) as e:
            run(flag)
        assert e.value.code == 0


def test_bundled_demo_is_valid():
    errors, warnings, n = validate(ws.DATA / "demo")
    assert not errors and not warnings, (errors, warnings)
    assert n >= 6


# -- demo ----------------------------------------------------------------
def test_demo_then_search_provenance_attention(isolated):
    code, out = run("demo", str(isolated / "demo"))
    assert code == 0 and "Demo ready" in out

    code, out = run("search", "partitioning", "-w", str(isolated / "demo"))
    assert code == 0 and "Time-Range Partitioning" in out

    code, out = run("provenance", "Time-Range Partitioning",
                    "-w", str(isolated / "demo"))
    assert code == 0
    assert "Came from" in out                      # traces to its source
    assert "you said it" in out                    # the human's own position
    assert "an assistant suggested it" in out      # never silently promoted
    assert "is a later version of" in out          # relation, in plain words

    code, out = run("attention", "-w", str(isolated / "demo"))
    assert code == 0
    assert "Open questions" in out
    assert "Positions you changed" in out

    code, out = run("validate", str(isolated / "demo"))
    assert code == 0 and "0 errors" in out


def test_demo_is_reinstallable(isolated):
    run("demo", str(isolated / "demo"))
    code, _ = run("demo", str(isolated / "demo"))
    assert code == 0


def test_get_by_id_and_alias(isolated):
    run("demo", str(isolated / "demo"))
    code, out = run("get", "c-20260826-horizontal-partitioning",
                    "-w", str(isolated / "demo"))
    assert code == 0 and "Definition" in out
    code, out = run("get", "Data Sharding", "-w", str(isolated / "demo"))
    assert code == 0 and "Horizontal Partitioning" in out   # alias resolves


# -- init ----------------------------------------------------------------
def test_init_creates_usable_workspace(isolated):
    target = isolated / "My Workspace"             # a space in the path
    code, out = run("init", str(target))
    assert code == 0 and "Workspace created" in out
    assert ws.is_workspace(target)
    for folder in ("concepts", "decisions", "_sources", "_templates"):
        assert (target / folder).is_dir()
    errors, _, _ = validate(target)
    assert not errors
    code, out = run("doctor", str(target))
    assert code == 0 and "EKSB is ready" in out


def test_init_unicode_path(isolated):
    target = isolated / "Espaço de Trabalho ✓"
    assert run("init", str(target))[0] == 0
    assert ws.is_workspace(target)


def test_init_refuses_existing_workspace(isolated):
    target = isolated / "w"
    run("init", str(target))
    code, out = run("init", str(target))
    assert code == 1 and "already an EKSB workspace" in out


def test_init_refuses_non_empty_folder(isolated):
    target = isolated / "busy"
    target.mkdir()
    (target / "notes.txt").write_text("hi", encoding="utf-8")
    code, out = run("init", str(target))
    assert code == 1 and "already has files" in out


# -- errors speak human --------------------------------------------------
def test_missing_workspace_is_a_sentence_not_a_traceback(isolated):
    code, out = run("search", "anything")
    assert code == 1
    assert "I couldn't find an EKSB workspace here." in out
    assert "eksb init" in out
    assert "Traceback" not in out


def test_unknown_note_is_a_sentence(isolated):
    run("demo", str(isolated / "demo"))
    code, out = run("get", "no such note", "-w", str(isolated / "demo"))
    assert code == 1 and "I couldn't find" in out and "Traceback" not in out


# -- language ------------------------------------------------------------
def test_language_switch_and_persistence(isolated):
    code, out = run("config", "--set-lang", "pt-BR")
    assert code == 0 and "Idioma definido" in out
    assert config.load()["lang"] == "pt-BR"

    run("demo", str(isolated / "demo"))
    code, out = run("attention", "-w", str(isolated / "demo"))
    assert "Coisas que precisam da sua atenção" in out

    code, out = run("--lang", "en", "attention", "-w", str(isolated / "demo"))
    assert "Things that need your attention" in out
    assert config.load()["lang"] == "pt-BR"        # a one-run override only


def test_both_languages_define_the_same_keys():
    en = set(i18n.STRINGS["en"])
    for lang, table in i18n.STRINGS.items():
        assert set(table) == en, f"{lang} key mismatch: {en ^ set(table)}"


def test_every_ui_string_is_translated():
    """No English leaking into the pt-BR table (paths and brand names aside)."""
    same = {k for k, v in i18n.STRINGS["pt-BR"].items()
            if v == i18n.STRINGS["en"][k]}
    allowed = {"doc.python", "doc.eksb", "doc.obsidian", "doc.ok",
               "doc.workspace", "ws.current",      # "workspace" is used as-is in pt-BR
               "lang.choose", "no", "learn.docs.body"}
    assert same <= allowed, same - allowed


# -- workspace discovery -------------------------------------------------
def test_workspace_found_from_a_subdirectory(isolated, monkeypatch):
    target = isolated / "w"
    run("init", str(target))
    sub = target / "concepts"
    monkeypatch.chdir(sub)
    code, out = run("doctor")
    assert code == 0 and "EKSB is ready" in out


def test_config_and_workspace_stay_separate(isolated):
    target = isolated / "w"
    run("init", str(target))
    assert config.config_file().is_file()
    assert not config.config_file().is_relative_to(target)
    assert not list(target.rglob("config.json"))


# -- transparency --------------------------------------------------------
def test_about_states_what_runs_and_where_data_lives(isolated):
    run("demo", str(isolated / "demo"))
    code, out = run("about", str(isolated / "demo"))
    assert code == 0
    assert "Nothing runs in the background" in out
    assert "no telemetry" in out
    assert str(isolated / "demo") in out
    assert str(config.config_dir()) in out


# -- interactive ---------------------------------------------------------
def feed(monkeypatch, answers):
    it = iter(answers)
    monkeypatch.setattr("builtins.input", lambda *_: next(it))


def test_first_run_onboarding_picks_language_then_demo(isolated, monkeypatch):
    feed(monkeypatch, ["2",          # Português
                       "1"])         # Try the demo
    code, out = run()
    assert code == 0
    assert "Escolha um idioma" in out
    assert "Pronto. Seu EKSB está preparado." in out
    assert config.load() == {**config.load(), "lang": "pt-BR", "onboarded": True}


def test_first_run_can_create_a_workspace(isolated, monkeypatch):
    target = isolated / "mine"
    feed(monkeypatch, ["1", "2", str(target)])   # English, create, path
    code, out = run()
    assert code == 0 and ws.is_workspace(target)
    assert "You're ready." in out


def menu_until_exit(isolated, monkeypatch, expect_present, expect_absent=()):
    """Open the menu, choose Exit, and assert on what it offered."""
    import re as _re
    box = {}

    def fake_input(prompt=""):
        # the options were just printed; find the number next to Exit
        text = box["buf"].getvalue()
        m = _re.search(r"(\d+)\. (Exit|Sair)$", text, _re.M)
        assert m, text
        return m.group(1)

    monkeypatch.setattr("builtins.input", fake_input)
    buf = io.StringIO()
    box["buf"] = buf
    old, sys.stdout = sys.stdout, buf
    try:
        code = cli.main([])
    finally:
        sys.stdout = old
    out = buf.getvalue()
    assert code == 0, out
    for s in expect_present:
        assert s in out, f"missing {s!r}\n{out}"
    for s in expect_absent:
        assert s not in out, f"unexpected {s!r}\n{out}"
    return out


def test_menu_offers_no_dead_options_without_a_workspace(isolated, monkeypatch):
    config.set_(onboarded=True, lang="en")
    # search / add / provenance all need a workspace, so none may be offered
    menu_until_exit(isolated, monkeypatch,
                    expect_present=["Try the demo", "Create my workspace", "Bye."],
                    expect_absent=["Search my knowledge", "Add something",
                                   "What needs my attention?"])


def test_menu_offers_knowledge_options_with_a_workspace(isolated, monkeypatch):
    config.set_(onboarded=True, lang="en")
    run("demo", str(isolated / "demo"))
    menu_until_exit(isolated, monkeypatch,
                    expect_present=["Search my knowledge", "Add something",
                                    "What needs my attention?",
                                    "Check where something came from"])


# -- adding --------------------------------------------------------------
def test_add_note_is_valid_and_findable(isolated):
    target = isolated / "w"
    run("init", str(target))
    code, out = run("add", "Read Latency Matters", "-w", str(target))
    assert code == 0 and "Created" in out
    errors, _, _ = validate(target)
    assert not errors, errors
    code, out = run("search", "Read Latency", "-w", str(target))
    assert code == 0 and "Read Latency Matters" in out


def test_add_decision_lands_in_decisions(isolated):
    target = isolated / "w"
    run("init", str(target))
    run("add", "--type", "decision", "Use Postgres", "-w", str(target))
    assert (target / "decisions" / "Use Postgres.md").is_file()
    assert not validate(target)[0]


def test_add_handles_accents_and_repeat_titles(isolated):
    target = isolated / "w"
    run("init", str(target))
    run("add", "Decisão sobre índices", "-w", str(target))
    run("add", "Decisão sobre índices", "-w", str(target))
    assert (target / "concepts" / "Decisão sobre índices.md").is_file()
    assert (target / "concepts" / "Decisão sobre índices 2.md").is_file()
    assert not validate(target)[0]      # ids stay ASCII-safe and unique enough


def test_save_source_is_verbatim_and_hash_checked(isolated):
    target = isolated / "w"
    run("init", str(target))
    src = isolated / "chat.md"
    src.write_text("Me: should we shard?\nAssistant: maybe not.\n", encoding="utf-8")
    code, out = run("save", str(src), "--kind", "chatgpt", "-w", str(target))
    assert code == 0 and "Kept as" in out

    kept = next((target / "_sources").glob("chat*.md"))
    assert "should we shard?" in kept.read_text(encoding="utf-8")
    assert not validate(target)[0]

    # editing raw history must be detected
    kept.write_text(kept.read_text(encoding="utf-8").replace("maybe not", "yes"),
                    encoding="utf-8")
    errors, _, _ = validate(target)
    assert any("content_hash mismatch" in e for e in errors), errors


def test_save_missing_file_is_a_sentence(isolated):
    target = isolated / "w"
    run("init", str(target))
    code, out = run("save", str(isolated / "nope.txt"), "-w", str(target))
    assert code == 1 and "There is no file at" in out and "Traceback" not in out
