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
    """Run the CLI, capture stdout, return (exit code, output).

    A scripted session that runs out of answers exits cleanly, exactly as it
    would on a closed stdin — so tests never have to encode menu numbering.
    """
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        code = cli.main(list(argv))
    except SystemExit as e:
        code = e.code or 0
    finally:
        sys.stdout = old
    return code, buf.getvalue()


# -- basics --------------------------------------------------------------
def test_validator_selftest():
    selftest()


def test_version_and_help():
    for flag in ("--version", "--help"):
        code, out = run(flag)
        assert code == 0, (flag, out)


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
               "product.name",                     # the product's name, not a phrase
               "conn.where",                       # a command to type, verbatim
               "demo.readonly.hint",               # a command to type, verbatim
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
    """Script the answers; running out behaves like the user closing stdin."""
    it = iter(answers)

    def scripted(prompt=""):
        print(prompt, end="")      # a real terminal shows the prompt; so must this
        try:
            answer = next(it)
        except StopIteration:
            print()
            raise EOFError
        print(answer)
        return answer
    monkeypatch.setattr("builtins.input", scripted)


def test_first_run_onboarding_picks_language_then_demo(isolated, monkeypatch):
    feed(monkeypatch, ["2",          # Português
                       "1",          # experimentar a demonstração
                       "n"])         # não, não quero conectar uma IA agora
    code, out = run()
    assert code == 0
    assert "Escolha um idioma" in out
    assert "Pronto. Seu EKSB está preparado." in out
    assert config.load()["lang"] == "pt-BR"
    assert config.load()["onboarded"] is True


def test_first_run_shows_the_whole_journey_not_just_install(isolated, monkeypatch):
    feed(monkeypatch, ["1", "1", "n"])
    code, out = run()
    assert code == 0
    # adding a project is a step, not the payoff: connecting an assistant follows
    assert "connect an AI assistant" in out
    assert "work normally" in out


def test_first_run_can_create_a_workspace(isolated, monkeypatch):
    target = isolated / "mine"
    feed(monkeypatch, ["1",              # English
                       "2",              # create my workspace
                       str(target),      # where
                       "n",              # no project folder yet
                       "n"])             # not connecting an assistant yet
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
    # search / add / projects / connect all need a workspace: none may be offered
    menu_until_exit(isolated, monkeypatch,
                    expect_present=["Try the demo", "Create my workspace", "Bye."],
                    expect_absent=["Search my history", "Add something",
                                   "Projects", "Connect an AI assistant",
                                   "What needs my attention?"])


def test_menu_offers_knowledge_options_with_a_workspace(isolated, monkeypatch):
    config.set_(onboarded=True, lang="en")
    mine = seeded(isolated)
    config.set_(workspace=str(mine))
    menu_until_exit(isolated, monkeypatch,
                    expect_present=["Where things stand", "Search my history",
                                    "Projects", "Connect an AI assistant",
                                    "Add something", "What needs my attention?",
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


# -- projects and directory ingestion ------------------------------------
def a_project(root: Path) -> Path:
    """A small project with the kinds of file a real one has."""
    (root / "docs").mkdir(parents=True)
    (root / "src").mkdir()
    (root / "node_modules" / "dep").mkdir(parents=True)
    (root / ".git").mkdir()
    (root / "README.md").write_text(
        "# Atlas\n\nRead latency is the binding constraint.\n", encoding="utf-8")
    (root / "docs" / "decisions.md").write_text(
        "# Decisions\n\nAdopted time-range partitioning.\n", encoding="utf-8")
    (root / "src" / "main.py").write_text("print('hi')\n", encoding="utf-8")
    (root / "node_modules" / "dep" / "readme.md").write_text("junk\n", encoding="utf-8")
    (root / ".git" / "config").write_text("[core]\n", encoding="utf-8")
    (root / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x01")
    return root


def test_ingest_indexes_prose_and_ignores_the_rest(isolated):
    w_path, proj = isolated / "w", a_project(isolated / "proj")
    run("init", str(w_path))
    code, out = run("ingest", str(proj), "--name", "Atlas", "-w", str(w_path))
    assert code == 0 and "Indexed Atlas" in out

    kept = sorted(p.name for p in (w_path / "_sources").glob("*.md"))
    assert len(kept) == 2, kept                 # README + docs/decisions
    assert not any("main.py" in k for k in kept)
    assert not any("junk" in k.lower() for k in kept)
    assert not validate(w_path)[0]


def test_ingest_is_incremental_and_never_destroys_history(isolated):
    w_path, proj = isolated / "w", a_project(isolated / "proj")
    run("init", str(w_path))
    run("ingest", str(proj), "-w", str(w_path))

    code, out = run("ingest", str(proj), "-w", str(w_path))
    assert code == 0
    assert "already up to date" in out
    assert len(list((w_path / "_sources").glob("*.md"))) == 2   # no duplicates

    (proj / "README.md").write_text("# Atlas\n\nNow with retention windows.\n",
                                    encoding="utf-8")
    code, out = run("ingest", str(proj), "-w", str(w_path))
    assert "changed since last time" in out
    kept = list((w_path / "_sources").glob("*README*"))
    assert len(kept) == 2, kept                 # the earlier version is still there
    bodies = "\n".join(p.read_text(encoding="utf-8") for p in kept)
    assert "binding constraint" in bodies and "retention windows" in bodies
    assert not validate(w_path)[0]


def test_ingest_reports_levels_honestly(isolated):
    from eksb import ingest as ing
    w_path, proj = isolated / "w", a_project(isolated / "proj")
    run("init", str(w_path))
    run("ingest", str(proj), "--name", "Atlas", "-w", str(w_path))

    rows = ing.levels(ws.Workspace(w_path))
    assert len(rows) == 1
    # indexed is NOT integrated: nothing has been understood yet
    assert rows[0]["level"] == 2 and rows[0]["level_name"] == "indexed"
    assert rows[0]["indexed"] == 2 and rows[0]["integrated"] == 0

    code, out = run("projects", "-w", str(w_path))
    assert "indexed" in out and "integrated" in out


def test_ingest_refuses_a_folder_inside_the_workspace(isolated):
    w_path = isolated / "w"
    run("init", str(w_path))
    code, out = run("ingest", str(w_path / "concepts"), "-w", str(w_path))
    assert code == 1 and "inside your workspace" in out


def test_ingest_dry_run_writes_nothing(isolated):
    w_path, proj = isolated / "w", a_project(isolated / "proj")
    run("init", str(w_path))
    run("ingest", str(proj), "--dry-run", "-w", str(w_path))
    assert not list((w_path / "_sources").glob("*.md"))


def seeded(isolated):
    """A workspace of the user's own, holding the demo's notes. Writable."""
    import shutil as _sh
    target = isolated / "mine"
    run("init", str(target))
    for folder in ("concepts", "decisions", "_sources"):
        src = ws.DATA / "demo" / folder
        if src.is_dir():
            _sh.copytree(src, target / folder, dirs_exist_ok=True)
    return target


# -- MCP ------------------------------------------------------------------
def mcp_session(root, *calls, client="test-agent"):
    """Drive the real server over a pipe, as a client would. Returns results."""
    import io as _io
    import json as _json
    from eksb import mcp

    lines = [_json.dumps({"jsonrpc": "2.0", "id": 0, "method": "initialize",
                          "params": {"protocolVersion": "2024-11-05",
                                     "clientInfo": {"name": client}}}),
             _json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})]
    for i, (name, args) in enumerate(calls, 1):
        lines.append(_json.dumps({"jsonrpc": "2.0", "id": i, "method": "tools/call",
                                  "params": {"name": name, "arguments": args}}))
    sink = _io.StringIO()
    mcp.serve(Path(root), _io.StringIO("\n".join(lines) + "\n"), sink)

    out = []
    for line in sink.getvalue().splitlines():
        msg = _json.loads(line)
        if msg.get("id") == 0:
            out.append(msg["result"])
        elif "result" in msg and "content" in msg["result"]:
            out.append(_json.loads(msg["result"]["content"][0]["text"]))
        else:
            out.append(msg)
    return out


def test_mcp_handshake_and_tool_list(isolated):
    import io as _io
    import json as _json
    from eksb import mcp
    run("demo", str(isolated / "demo"))

    req = "\n".join([
        _json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                     "params": {"protocolVersion": "2024-11-05",
                                "clientInfo": {"name": "c"}}}),
        _json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
    ]) + "\n"
    sink = _io.StringIO()
    mcp.serve(isolated / "demo", _io.StringIO(req), sink)
    msgs = [_json.loads(x) for x in sink.getvalue().splitlines()]

    assert msgs[0]["result"]["serverInfo"]["name"] == "eksb"
    assert msgs[0]["result"]["protocolVersion"] == "2024-11-05"
    names = [x["name"] for x in msgs[1]["result"]["tools"]]
    assert names == ["eksb_search", "eksb_get", "eksb_provenance", "eksb_attention",
                     "eksb_workspace_status", "eksb_ingest", "eksb_submit_candidate"]
    for tool in msgs[1]["result"]["tools"]:
        assert tool["description"] and tool["inputSchema"]["type"] == "object"


def test_mcp_read_tools(isolated):
    run("demo", str(isolated / "demo"))
    _, found, prov, status = mcp_session(
        isolated / "demo",
        ("eksb_search", {"query": "partitioning", "limit": 3}),
        ("eksb_provenance", {"id": "Time-Range Partitioning"}),
        ("eksb_workspace_status", {}))

    assert found["count"] == 3
    assert prov["came_from"][0]["kind"] == "chatgpt"
    # the distinction an agent must be able to see
    beliefs = [c["is_user_belief"] for c in prov["claims"]]
    assert True in beliefs and False in beliefs
    assert status["valid"] and status["notes"] == 7


def test_mcp_ingest_then_status_says_indexed_not_integrated(isolated):
    w_path, proj = isolated / "w", a_project(isolated / "proj")
    run("init", str(w_path))
    _, rep, status = mcp_session(
        w_path,
        ("eksb_ingest", {"path": str(proj), "name": "Atlas"}),
        ("eksb_workspace_status", {}))

    assert rep["ok"] and len(rep["added"]) == 2
    assert "not understood" in rep["note"]
    assert status["projects"][0]["level_name"] == "indexed"


# -- the boundary that matters -------------------------------------------
def test_agent_cannot_record_its_claim_as_the_users_position(isolated):
    mine = seeded(isolated)
    _, res = mcp_session(mine, ("eksb_submit_candidate", {
        "title": "Shard By Tenant Again",
        "claims": [{"text": "Tenant sharding is the right call after all.",
                    "epistemic": "user_position",
                    "source": "src-20260826-demo-conversation-01"}],
        "sources": ["src-20260826-demo-conversation-01"]}))

    assert res["action"] == "REJECTED"
    assert "may not assert user_position" in res["reason"]
    assert not list((mine / "concepts").glob("Shard By Tenant*"))


def test_agent_write_lands_as_a_proposal_not_a_belief(isolated):
    mine = seeded(isolated)
    _, res = mcp_session(mine, ("eksb_submit_candidate", {
        "type": "concept", "title": "Retention Window Policy",
        "summary": "How long event data is kept.",
        "claims": [{"text": "Retention is 90 days on the events table.",
                    "epistemic": "source_claim",
                    "source": "src-20260826-demo-conversation-01"}],
        "sources": ["src-20260826-demo-conversation-01"],
        "relations": [{"rel": "applies_to", "target": "Time-Range Partitioning"}]}))

    assert res["action"] == "CREATE" and res["applied"]
    text = Path(res["path"]).read_text(encoding="utf-8")
    assert "epistemic_default: assistant_hypothesis" in text
    assert "#e/source_claim" in text
    assert "#e/user_position" not in text
    assert not validate(mine)[0]                   # an agent cannot write invalid notes


def test_agent_claim_with_no_source_goes_to_review(isolated):
    mine = seeded(isolated)
    _, res = mcp_session(mine, ("eksb_submit_candidate", {
        "title": "Ungrounded Idea",
        "claims": [{"text": "We should rewrite it in Rust.",
                    "epistemic": "assistant_hypothesis"}]}))

    assert res["action"] == "REVIEW_REQUIRED" and not res["applied"]
    assert res["question"].endswith("Nothing was proposed as its source.")
    queue = (mine / "dashboards" / "Review Queue.md").read_text(encoding="utf-8")
    assert "Ungrounded Idea" in queue


def test_conflict_asks_one_plain_question(isolated):
    mine = seeded(isolated)
    _, res = mcp_session(mine, ("eksb_submit_candidate", {
        "title": "Tenant Sharding",
        "claims": [{"text": "Tenant sharding is back on the table.",
                    "epistemic": "assistant_hypothesis",
                    "source": "src-20260826-demo-conversation-01"}],
        "sources": ["src-20260826-demo-conversation-01"]}))

    assert res["action"] == "CONFLICT" and not res["applied"]
    q = res["question"]
    assert q.endswith("Which one is current?")
    # a question, not a form: no schema vocabulary reaches the user
    for jargon in ("epistemic", "canonical", "provenance", "promotion", "merge"):
        assert jargon not in q.lower()


def test_update_appends_and_never_overwrites(isolated):
    mine = seeded(isolated)
    note = mine / "concepts" / "Read Latency Is The Constraint.md"
    before = note.read_text(encoding="utf-8")

    _, res = mcp_session(mine, ("eksb_submit_candidate", {
        "title": "Read Latency Is The Constraint",
        "claims": [{"text": "p99 read latency is the number that is tracked.",
                    "epistemic": "source_claim",
                    "source": "src-20260826-demo-conversation-01"}],
        "sources": ["src-20260826-demo-conversation-01"]}))

    assert res["action"] == "UPDATE" and res["applied"]
    after = note.read_text(encoding="utf-8")
    for line in before.splitlines():
        assert line in after                        # nothing was removed
    assert "p99 read latency" in after
    assert not validate(mine)[0]


def test_resubmitting_the_same_claim_is_a_no_op(isolated):
    mine = seeded(isolated)
    cand = ("eksb_submit_candidate", {
        "title": "Read Latency Is The Constraint",
        "claims": [{"text": "p99 read latency is the number that is tracked.",
                    "epistemic": "source_claim",
                    "source": "src-20260826-demo-conversation-01"}],
        "sources": ["src-20260826-demo-conversation-01"]})
    _, first, second = mcp_session(mine, cand, cand)
    assert first["action"] == "UPDATE"
    assert second["action"] == "NO_OP" and not second["applied"]


def test_agent_cannot_invent_a_relation_or_a_source(isolated):
    mine = seeded(isolated)
    _, bad_rel, bad_src = mcp_session(
        mine,
        ("eksb_submit_candidate", {
            "title": "X", "claims": [{"text": "a", "epistemic": "inference",
                                      "source": "src-20260826-demo-conversation-01"}],
            "sources": ["src-20260826-demo-conversation-01"],
            "relations": [{"rel": "causes", "target": "Y"}]}),
        ("eksb_submit_candidate", {
            "title": "Y", "claims": [{"text": "b", "epistemic": "inference"}],
            "sources": ["src-does-not-exist"]}))

    assert bad_rel["action"] == "REJECTED" and "unknown relation" in bad_rel["reason"]
    assert bad_src["action"] == "REVIEW_REQUIRED"
    assert "not in this workspace" in bad_src["reason"]


# -- the whole point ------------------------------------------------------
def test_knowledge_outlives_the_session_that_produced_it(isolated):
    """Model A writes; model B, a separate session, inherits it."""
    mine = seeded(isolated)

    # --- session A: reads the history, works, writes back what it learned
    _, seen, written = mcp_session(
        mine,
        ("eksb_search", {"query": "partitioning"}),
        ("eksb_submit_candidate", {
            "type": "decision", "title": "Cap Retention At 90 Days",
            "summary": "Event partitions older than 90 days are dropped.",
            "claims": [{"text": "Partitions older than 90 days are dropped nightly.",
                        "epistemic": "source_claim",
                        "source": "src-20260826-demo-conversation-01"}],
            "sources": ["src-20260826-demo-conversation-01"],
            "relations": [{"rel": "implements", "target": "Time-Range Partitioning"}]}),
        client="model-a")
    assert seen["count"] > 0
    assert written["action"] == "CREATE" and written["applied"]

    # --- session B: a different client, a different process-worth of state
    _, found, prov = mcp_session(
        mine,
        ("eksb_search", {"query": "retention"}),
        ("eksb_provenance", {"id": "Cap Retention At 90 Days"}),
        client="model-b")

    assert any(r["title"] == "Cap Retention At 90 Days" for r in found["results"])
    assert prov["found"]
    assert prov["came_from"][0]["id"] == "src-20260826-demo-conversation-01"
    # and B can see it was A's proposal, not the user's belief
    assert all(c["is_user_belief"] is False for c in prov["claims"])
    assert prov["points_at"][0]["target"] == "Time-Range Partitioning"

    # the human, in their own terminal, sees the same thing
    code, out = run("provenance", "Cap Retention At 90 Days", "-w", str(mine))
    assert code == 0 and "a source says it" in out


def test_connect_prints_a_usable_client_config(isolated):
    import json as _json
    run("demo", str(isolated / "demo"))
    code, out = run("connect", "--json", "-w", str(isolated / "demo"))
    assert code == 0
    cfg = _json.loads(out)
    entry = cfg["mcpServers"]["eksb"]
    assert entry["args"][:3] == ["-m", "eksb", "mcp"]
    assert str(isolated / "demo") in entry["args"]


def test_mcp_survives_a_bad_request(isolated):
    import io as _io
    from eksb import mcp
    run("demo", str(isolated / "demo"))
    sink = _io.StringIO()
    mcp.serve(isolated / "demo",
              _io.StringIO('not json\n{"jsonrpc":"2.0","id":1,"method":"nope"}\n'
                           '{"jsonrpc":"2.0","id":2,"method":"ping"}\n'), sink)
    lines = sink.getvalue().splitlines()
    assert len(lines) == 3 and '"error"' in lines[0] and '"error"' in lines[1]
    assert '"result"' in lines[2]              # still serving after two bad messages


# -- the demo is a sandbox, not a place to put real work -----------------
def test_demo_stays_readable(isolated):
    """Every read path keeps working. The guard is on writes only."""
    run("demo", str(isolated / "demo"))
    demo = str(isolated / "demo")
    expect = {
        ("search", "partitioning", "-w", demo): "Time-Range Partitioning",
        ("get", "Time-Range Partitioning", "-w", demo): "Definition",
        ("provenance", "Time-Range Partitioning", "-w", demo): "you said it",
        ("attention", "-w", demo): "Open questions",
        ("validate", demo): "0 errors",
        ("doctor", demo): "EKSB is ready",
        ("about", demo): "Nothing runs in the background",
    }
    for argv, wanted in expect.items():
        code, out = run(*argv)
        assert code == 0, (argv, out)
        assert wanted in out, (argv, out)


def test_ingest_into_the_demo_is_refused(isolated):
    """The reported bug: a real project silently joining the fiction."""
    run("demo", str(isolated / "demo"))
    proj = a_project(isolated / "proj")

    code, out = run("ingest", str(proj), "-w", str(isolated / "demo"))
    assert code == 1
    assert "This is the demo workspace." in out
    assert "eksb init" in out
    assert "Traceback" not in out
    # nothing of the real project reached it
    assert not list((isolated / "demo" / "_sources").glob("*Atlas*"))
    assert not list((isolated / "demo" / "projects").glob("*.md"))
    assert not validate(isolated / "demo")[0]


def test_add_and_save_into_the_demo_are_refused(isolated):
    run("demo", str(isolated / "demo"))
    demo = str(isolated / "demo")

    code, out = run("add", "My Real Decision", "-w", demo)
    assert code == 1 and "This is the demo workspace." in out
    assert not list((isolated / "demo" / "concepts").glob("My Real*"))

    src = isolated / "chat.md"
    src.write_text("Me: something real.\n", encoding="utf-8")
    code, out = run("save", str(src), "-w", demo)
    assert code == 1 and "This is the demo workspace." in out
    assert not list((isolated / "demo" / "_sources").glob("chat*"))


def test_mcp_writeback_into_the_demo_is_refused(isolated):
    run("demo", str(isolated / "demo"))
    _, sub, ing, status = mcp_session(
        isolated / "demo",
        ("eksb_submit_candidate", {
            "title": "Real Thing",
            "claims": [{"text": "Something true about my actual project.",
                        "epistemic": "source_claim",
                        "source": "src-20260826-demo-conversation-01"}],
            "sources": ["src-20260826-demo-conversation-01"]}),
        ("eksb_ingest", {"path": str(a_project(isolated / "proj"))}),
        ("eksb_workspace_status", {}))

    assert sub["action"] == "REJECTED"
    assert "demo workspace" in sub["reason"]
    assert "eksb init" in sub["next"] or "eksb init" in sub["reason"]
    assert ing["ok"] is False and "demo workspace" in ing["reason"]
    # and the agent is told, so it can explain rather than retry
    assert status["is_demo_sandbox"] is True and status["writable"] is False

    assert not list((isolated / "demo" / "concepts").glob("Real Thing*"))
    assert not list((isolated / "demo" / "projects").glob("*.md"))


def test_the_users_own_workspace_stays_writable(isolated):
    """The guard must not leak onto real workspaces."""
    mine = seeded(isolated)
    proj = a_project(isolated / "proj")

    assert run("ingest", str(proj), "--name", "Atlas", "-w", str(mine))[0] == 0
    assert run("add", "My Real Decision", "--type", "decision",
               "-w", str(mine))[0] == 0
    src = isolated / "chat.md"
    src.write_text("Me: something real.\n", encoding="utf-8")
    assert run("save", str(src), "-w", str(mine))[0] == 0

    _, res = mcp_session(mine, ("eksb_submit_candidate", {
        "title": "Real Thing",
        "claims": [{"text": "Something true about my actual project.",
                    "epistemic": "source_claim",
                    "source": "src-20260826-demo-conversation-01"}],
        "sources": ["src-20260826-demo-conversation-01"]}))
    assert res["action"] == "CREATE" and res["applied"]
    assert not validate(mine)[0]


def test_demo_is_labelled_as_a_demo(isolated):
    run("demo", str(isolated / "demo"))
    for argv in (("doctor", str(isolated / "demo")),
                 ("about", str(isolated / "demo"))):
        code, out = run(*argv)
        assert code == 0 and "DEMO" in out, argv

    mine = seeded(isolated)
    code, out = run("doctor", str(mine))
    assert code == 0 and "DEMO" not in out


def test_demo_guard_speaks_portuguese_too(isolated):
    run("demo", str(isolated / "demo"))
    code, out = run("--lang", "pt-BR", "add", "Algo Real",
                    "-w", str(isolated / "demo"))
    assert code == 1
    assert "Este é o workspace de demonstração." in out
    assert "eksb init" in out


def test_a_demo_installed_anywhere_is_still_protected(isolated):
    """Not just the default location — the content is what makes it a demo."""
    run("demo", str(isolated / "elsewhere"))
    assert ws.Workspace(isolated / "elsewhere").is_demo
    code, out = run("add", "Real", "-w", str(isolated / "elsewhere"))
    assert code == 1 and "This is the demo workspace." in out


# -- getting out of the demo ---------------------------------------------
def test_demo_menu_offers_the_way_out(isolated, monkeypatch):
    """In the demo, creating or opening a real workspace must be right there."""
    config.set_(onboarded=True, lang="en")
    run("demo", str(isolated / "demo"))
    out = menu_until_exit(isolated, monkeypatch,
                          expect_present=["Create my workspace",
                                          "Open an existing workspace",
                                          "Search the demo",
                                          "Add something"],
                          # ingesting a project cannot work here at all
                          expect_absent=["Projects", "What needs my attention?"])
    assert "Look around the demo" in out


def test_refused_write_offers_to_create_a_workspace_then_ingest_works(isolated,
                                                                      monkeypatch):
    """demo -> try real work -> create -> active is real -> ingest succeeds."""
    config.set_(onboarded=True, lang="en")
    run("demo", str(isolated / "demo"))
    assert ws.Workspace(config.load()["workspace"]).is_demo

    mine = isolated / "MyEKSB"
    proj = a_project(isolated / "proj")

    feed(monkeypatch, [
        "4",            # Add something -- refused, because this is the demo
        "y",            # yes, create my own workspace
        str(mine),      # here -- no second confirmation: consent is given
    ])
    code, out = run()
    assert code == 0, out
    assert "This is the demo workspace." in out
    assert "Create your own workspace now?" in out

    # the new workspace exists, is real, and is now the active one
    assert ws.is_workspace(mine)
    active = ws.Workspace(config.load()["workspace"])
    assert active.root == mine.resolve() and not active.is_demo

    # and real work now lands in it
    code, out = run("ingest", str(proj), "--name", "Atlas")
    assert code == 0 and "Indexed Atlas" in out
    assert list((mine / "_sources").glob("*Atlas*"))
    assert not validate(mine)[0]
    assert not list((isolated / "demo" / "_sources").glob("*Atlas*"))


def test_typing_a_path_that_is_not_a_workspace_offers_to_create_it(isolated,
                                                                   monkeypatch):
    """The Settings dead end: ~/MyEKSB used to just say 'no workspace there'."""
    config.set_(onboarded=True, lang="en")
    run("demo", str(isolated / "demo"))
    mine = isolated / "MyEKSB"

    feed(monkeypatch, [
        "6",            # Open an existing workspace
        str(mine),      # ...which does not exist yet
        "y",            # yes, create one there
    ])
    code, out = run()
    assert code == 0, out
    assert "Create one there?" in out
    assert ws.is_workspace(mine)
    assert ws.Workspace(config.load()["workspace"]).root == mine.resolve()


def test_declining_creates_nothing(isolated, monkeypatch):
    config.set_(onboarded=True, lang="en")
    run("demo", str(isolated / "demo"))
    mine = isolated / "MyEKSB"

    feed(monkeypatch, ["6", str(mine), "n"])            # 6 = Open, in the demo menu
    code, out = run()
    assert code == 0, out
    assert not mine.exists()                            # nothing without consent
    assert ws.Workspace(config.load()["workspace"]).is_demo


def test_the_way_out_speaks_portuguese(isolated, monkeypatch):
    config.set_(onboarded=True, lang="pt-BR")
    run("demo", str(isolated / "demo"))
    mine = isolated / "MeuEKSB"

    feed(monkeypatch, ["4", "s", str(mine)])            # Adicionar algo -> recusa
    code, out = run()
    assert code == 0, out
    assert "Este é o workspace de demonstração." in out
    assert "Quer criar seu próprio workspace agora?" in out
    assert ws.is_workspace(mine)
