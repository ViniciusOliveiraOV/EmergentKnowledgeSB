"""The `eksb` command: an interactive menu plus direct subcommands.

Cross-platform by construction — pathlib, no shell-outs, no POSIX assumptions.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
from pathlib import Path

from . import __version__, config, ingest, workspace as ws
from .i18n import LANGUAGES, get_lang, set_lang, t
from .validate import validate

DEBUG = False
VERSION_LABEL = "0.1.0-alpha"

# -- terminal ------------------------------------------------------------
def _use_color() -> bool:
    if os.environ.get("NO_COLOR") or os.environ.get("EKSB_NO_COLOR"):
        return False
    if not sys.stdout.isatty():
        return False
    if sys.platform == "win32" and not os.environ.get("WT_SESSION") \
            and os.environ.get("TERM") is None:
        # legacy conhost may not handle ANSI; plain text is always readable
        return os.environ.get("ANSICON") is not None
    return True


COLOR = _use_color()


def _unicode_ok() -> bool:
    enc = (sys.stdout.encoding or "").lower()
    return "utf" in enc


UNI = _unicode_ok()


def c(s, code):
    return f"\033[{code}m{s}\033[0m" if COLOR else str(s)


def bold(s):  return c(s, "1")
def dim(s):   return c(s, "2")
def cyan(s):  return c(s, "36")
def green(s): return c(s, "32")
def red(s):   return c(s, "31")
def yellow(s): return c(s, "33")


def out(s=""):
    """Print without ever dying on a console that cannot encode a character."""
    try:
        print(s)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "ascii"
        print(str(s).encode(enc, "replace").decode(enc))


# Pure ASCII on purpose: it renders identically in PowerShell, cmd, and every
# Linux/macOS terminal, in any code page.
LOGO = r"""
 ______ _  __  _____  ____
|  ____| |/ / / ____||  _ \
| |__  | ' / | (___  | |_) |
|  __| |  <   \___ \ |  _ <
| |____| . \  ____) || |_) |
|______|_|\_\|_____/ |____/
"""
LOGO_WIDTH = 30


def term_width() -> int:
    try:
        return shutil.get_terminal_size((80, 24)).columns
    except Exception:
        return 80


def banner(full: bool = False) -> None:
    """The identity. Silent when piped; compact when narrow or routine."""
    if not sys.stdout.isatty():
        return                              # never in machine-readable output
    if full and term_width() >= LOGO_WIDTH:
        for line in LOGO.strip("\n").splitlines():
            out(cyan(line))
        out()
        out(bold(t("product.name")))
        out(dim(f"v{VERSION_LABEL}"))
    else:
        out()
        out(bold("EKSB") + dim(" // Workbench"))


def tagline() -> None:
    if sys.stdout.isatty():
        out()
        out(t("tagline"))


def rule(title=""):
    out()
    out(bold(title) if title else "")


def ask(prompt, default=""):
    try:
        s = input(f"{prompt}{dim(' [' + default + ']') if default else ''}: ").strip()
    except (EOFError, KeyboardInterrupt):
        out()
        raise SystemExit(0)
    return s or default


def ask_yes(prompt) -> bool:
    return ask(f"{prompt} {t('yn')}").lower().startswith(t("yes"))


def pause():
    try:
        input(dim(t("press.enter")))
    except (EOFError, KeyboardInterrupt):
        raise SystemExit(0)


def choose(title, options, allow_back=False):
    """options: list of (key, label). Returns key, or None if backed out."""
    while True:
        rule(title)
        for i, (_, label) in enumerate(options, 1):
            out(f"  {cyan(str(i) + '.')} {label}")
        if allow_back:
            out(f"  {cyan('0.')} {t('menu.back')}")
        out()
        s = ask(t("menu.choose"))
        if allow_back and s == "0":
            return None
        if s.isdigit() and 1 <= int(s) <= len(options):
            return options[int(s) - 1][0]
        out(red(t("menu.invalid")))


# -- workspace resolution ------------------------------------------------
class UserError(Exception):
    """An error phrased for the person at the keyboard."""

    def __init__(self, msg, hint=""):
        super().__init__(msg)
        self.hint = hint


def demo_guard(w) -> None:
    """Turn the demo's read-only rule into a sentence with a next step."""
    if w is not None and w.is_demo:
        raise UserError(t("demo.readonly"),
                        t("demo.readonly.hint",
                          path=Path.home() / "MyEKSB"))


def resolve_ws(path=None) -> ws.Workspace:
    """Explicit path > nearest workspace above cwd > configured default."""
    if path:
        p = Path(path).expanduser()
        if not ws.is_workspace(p):
            raise UserError(t("ws.notfound", path=p), t("ws.none.hint"))
        return ws.Workspace(p)
    found = ws.find()
    if found:
        return ws.Workspace(found)
    saved = config.load().get("workspace")
    if saved and ws.is_workspace(Path(saved)):
        return ws.Workspace(Path(saved))
    raise UserError(t("ws.none"), t("ws.none.hint"))


# -- rendering -----------------------------------------------------------
SPEAKER = {
    "user_position":        ("you said it", "você disse"),
    "assistant_hypothesis": ("an assistant suggested it — not confirmed",
                             "um assistente sugeriu — não confirmado"),
    "external_fact":        ("claimed outside this workspace",
                             "afirmado fora deste workspace"),
    "source_claim":         ("a source says it", "uma fonte afirma"),
    "inference":            ("follows from other notes",
                             "decorre de outras notas"),
    "open_question":        ("still open", "ainda em aberto"),
}

REL = {
    "supports":     ("supports", "apoia"),
    "contradicts":  ("contradicts", "contradiz"),
    "depends_on":   ("depends on", "depende de"),
    "requires":     ("requires", "requer"),
    "implements":   ("is a concrete form of", "é uma forma concreta de"),
    "informed_by":  ("was shaped by", "foi moldado por"),
    "derived_from": ("was taken from", "foi extraído de"),
    "related_to":   ("relates to", "se relaciona com"),
    "replaces":     ("replaces", "substitui"),
    "evolves_from": ("is a later version of", "é uma versão posterior de"),
    "questions":    ("questions", "questiona"),
    "applies_to":   ("applies to", "se aplica a"),
}


def phrase(table, key):
    pair = table.get(key)
    if not pair:
        return key
    return pair[1] if get_lang() == "pt-BR" else pair[0]


def show_note_line(n, i=None):
    num = f"{cyan(str(i) + '.'):>6} " if i is not None else "  "
    out(f"{num}{bold(n.title)}  {dim('(' + n.type + ')')}")


def cmd_search(w, query, interactive=False):
    hits = w.search(query)
    if not hits:
        out(t("search.none", q=query))
        return 1
    rule(t("search.count", n=len(hits), q=query))
    for i, (n, snippet) in enumerate(hits, 1):
        show_note_line(n, i)
        if snippet and snippet.lower() != n.title.lower():
            out(f"        {dim(snippet[:100])}")
        out(f"        {dim(n.id)}")
    if interactive:
        out()
        s = ask(t("search.pick"))
        if s.isdigit() and 1 <= int(s) <= len(hits):
            show_provenance(w, hits[int(s) - 1][0])
    return 0


def show_note(n):
    rule(n.title)
    out(dim(f"{n.type} · {n.id}"))
    out()
    out(n.body.strip())


def show_provenance(w, n):
    p = w.provenance(n)
    rule(t("prov.title", title=n.title))
    out(dim(f"{n.type} · {n.id}"))

    out()
    out(bold(t("prov.sources") + ":"))
    if p["sources"]:
        for s in p["sources"]:
            out(f"  {s.title}")
            kind = s.fm.get("source_type") or "?"
            date = s.fm.get("source_date") or s.fm.get("created") or "?"
            out(f"    {dim(t('prov.origin', kind=kind, date=date))}")
            out(f"    {dim(str(s.path.name))}")
    else:
        out(f"  {dim(t('prov.nosources'))}")
    if p["missing_sources"]:
        out(f"  {yellow(t('prov.missing', ids=', '.join(p['missing_sources'])))}")

    if p["claims"]:
        out()
        out(bold(t("prov.claims") + ":"))
        for tag, text in p["claims"]:
            label = phrase(SPEAKER, tag)
            colour = green if tag == "user_position" else (
                yellow if tag in ("assistant_hypothesis", "inference") else dim)
            out(f"  • {text}")
            out(f"    {colour('→ ' + label)}")

    if p["outgoing"]:
        out()
        out(bold(t("prov.out") + ":"))
        for r, target in p["outgoing"]:
            name = target.title if target else str(r.get("target", "?")).strip("[]")
            mark = "" if target else yellow("  (missing)")
            out(f"  {phrase(REL, r.get('rel', '?'))} {bold(name)}{mark}")

    if p["incoming"]:
        out()
        out(bold(t("prov.in") + ":"))
        for other, r in p["incoming"]:
            out(f"  {bold(other.title)}  {dim(phrase(REL, r.get('rel', '?')) + ' ' + t('prov.this'))}")


def show_attention(w):
    a = w.attention()
    rule(t("att.title"))
    shown = False

    def block(key, items, fmt):
        nonlocal shown
        if not items:
            return
        shown = True
        out()
        out(bold(t(key) + f"  ({len(items)})"))
        for item in items[:15]:
            out("  " + fmt(item))
        if len(items) > 15:
            out(dim(f"  ... +{len(items) - 15}"))

    block("att.errors", a["errors"], lambda e: red(e))
    block("att.queue", a["queue"], lambda q: q)
    block("att.open", a["open_questions"], lambda p: p[0].title)
    block("att.unendorsed", a["unendorsed"],
          lambda p: f"{p[1][:80]}  {dim('— ' + p[0].title)}")
    block("att.unverified", a["unverified"],
          lambda p: f"{p[1][:80]}  {dim('— ' + p[0].title)}")
    block("att.superseded", a["superseded"],
          lambda p: f"{p[0].title} {dim('→ ' + str(p[1]).strip('[]'))}")
    block("att.review", a["review_due"], lambda p: f"{p[0].title} {dim(p[1])}")
    block("att.warnings", a["warnings"], lambda x: dim(x))

    if not shown:
        out()
        out(green(t("att.clean")))
    return 0


def cmd_add(w, type_, title):
    demo_guard(w)
    path = ws.add_note(w, type_, title)
    out()
    out(green(t("add.created", path=path)))
    out(dim(t("add.edit")))
    return 0


def cmd_save(w, src, title=None, kind="personal_note"):
    demo_guard(w)
    try:
        path = ws.save_source(w, Path(src), title, kind)
    except ws.WorkspaceError as e:
        reason, _, p = str(e).partition(":")
        raise UserError(t("save.nofile" if reason == "no-file" else "save.nottext",
                          path=p))
    out()
    out(green(t("save.saved", path=path)))
    out(dim(t("save.kept")))
    return 0


def add_menu(w):
    kind = choose(t("add.what"), [
        ("note", t("add.note")),
        ("source", t("add.source")),
    ], allow_back=True)
    if kind is None:
        return
    if kind == "source":
        src = ask(t("save.path"))
        if not src:
            return
        pick = choose(t("save.kind"), [(k, t("save.kind." + k))
                                       for k in ("chatgpt", "claude", "web",
                                                 "paper", "personal_note")])
        cmd_save(w, src, None, pick)
        return
    type_ = choose(t("add.type"), [(x, t("type." + x)) for x in ws.ADDABLE],
                   allow_back=True)
    if type_ is None:
        return
    title = ask(t("add.title"))
    if title:
        cmd_add(w, type_, title)


# -- projects and ingestion ----------------------------------------------
LEVEL_KEY = {1: "level.registered", 2: "level.indexed", 3: "level.integrated"}


def cmd_ingest(w, path, name=None, dry_run=False, max_files=None):
    demo_guard(w)
    try:
        rep = ingest.ingest(w, Path(path), name,
                            max_files=max_files or ingest.DEFAULT_MAX_FILES,
                            dry_run=dry_run)
    except ws.WorkspaceError as e:
        reason, _, detail = str(e).partition(":")
        raise UserError(t({"no-dir": "ing.nodir",
                           "inside-workspace": "ing.inside"}.get(reason, "ing.nodir"),
                          path=detail))
    rule(t("ing.done", project=rep.project))
    out()

    def tally(n, colour, label):
        out("  " + colour(f"{n:>5}") + "  " + label)

    tally(len(rep.added), green, t("ing.added"))
    if rep.updated:
        tally(len(rep.updated), yellow, t("ing.updated"))
    if rep.unchanged:
        tally(len(rep.unchanged), dim, t("ing.unchanged"))
    if rep.skipped:
        by = {}
        for _, why in rep.skipped:
            by[why] = by.get(why, 0) + 1
        detail = ", ".join(f"{n} {t('skip.' + why)}" for why, n in sorted(by.items()))
        tally(len(rep.skipped), dim, dim(t("ing.skipped") + ": " + detail))
    if rep.truncated:
        out()
        out(yellow(t("ing.truncated", n=ingest.DEFAULT_MAX_FILES)))
    out()
    out(t("ing.indexed_not_understood"))
    out(dim(t("ing.next")))
    return 0


def cmd_projects(w):
    rows = ingest.levels(w)
    rule(t("proj.title"))
    if not rows:
        out()
        out(dim(t("proj.none")))
        out(dim(t("proj.hint")))
        return 0
    out()
    for r in rows:
        out(f"  {bold(r['title'])}  {dim('(' + t(LEVEL_KEY[r['level']]) + ')')}")
        out(f"    {dim(r['root'])}")
        out(f"    {dim(t('proj.counts', indexed=r['indexed'], integrated=r['integrated']))}")
    out()
    out(dim(t("proj.levels")))
    return 0


# -- AI assistants --------------------------------------------------------
def mcp_command() -> list[str]:
    """How a client should launch this server. Uses the running interpreter."""
    return [sys.executable, "-m", "eksb", "mcp"]


def mcp_config(workspace: Path | None) -> dict:
    cmd = mcp_command()
    entry = {"command": cmd[0], "args": cmd[1:]}
    if workspace:
        entry["args"] = cmd[1:] + ["--workspace", str(workspace)]
    return {"mcpServers": {"eksb": entry}}


CLIENT_CONFIGS = {
    "Claude Code": lambda: [Path.home() / ".claude.json", Path.cwd() / ".mcp.json"],
    "Claude Desktop": lambda: [
        Path(os.environ["APPDATA"]) / "Claude" / "claude_desktop_config.json"
        if os.environ.get("APPDATA") else
        Path.home() / "Library" / "Application Support" / "Claude"
        / "claude_desktop_config.json",
        Path.home() / ".config" / "Claude" / "claude_desktop_config.json",
    ],
}


def detect_clients() -> list[tuple[str, bool]]:
    """(client, is EKSB already configured there). Read-only, best effort."""
    found = []
    for name, paths in CLIENT_CONFIGS.items():
        try:
            candidates = [p for p in paths() if p.is_file()]
        except Exception:
            candidates = []
        if not candidates:
            continue
        wired = False
        for p in candidates:
            try:
                if "eksb" in p.read_text(encoding="utf-8", errors="replace").lower():
                    wired = True
                    break
            except OSError:
                pass
        found.append((name, wired))
    return found


def cmd_connect(w=None, json_only=False):
    cfg = mcp_config(w.root if w else None)
    if json_only:
        print(json.dumps(cfg, indent=2))
        return 0
    rule(t("conn.title"))
    out()
    out(t("conn.what"))
    out()
    clients = detect_clients()
    if clients:
        out(bold(t("conn.detected")))
        for name, wired in clients:
            mark = green("[x]") if wired else dim("[ ]")
            state = t("conn.wired") if wired else t("conn.notwired")
            out(f"  {mark} {name}  {dim(state)}")
    else:
        out(dim(t("conn.nodetect")))
    out()
    out(bold(t("conn.howto")))
    out()
    out(json.dumps(cfg, indent=2))
    out()
    out(t("conn.where"))
    out(dim(t("conn.restart")))
    out()
    out(dim(t("conn.docs")))
    return 0


def cmd_mcp(path=None):
    from . import mcp
    w = resolve_ws(path)
    return mcp.serve(w.root)


# -- where things stand ---------------------------------------------------
def _recent(w, limit=5):
    def when(n):
        return str(n.fm.get("updated") or n.fm.get("created") or "")
    notes = [n for n in w.notes if n.type != "source"]
    return sorted(notes, key=when, reverse=True)[:limit]


def show_status(w):
    """The 'where was I' screen. Reads, never asks."""
    counts = w.counts()
    projects = ingest.levels(w)
    rule(t("stat.title"))
    out()
    if w.is_demo:
        out("  " + yellow("[" + t("demo.label") + "] " + t("demo.readonly")))
        out()
    out(f"  {t('stat.projects')}: {bold(str(len(projects)))}"
        f"    {t('stat.items')}: {bold(str(counts['notes']))}")
    for p in projects[:5]:
        out(f"    {dim('-')} {p['title']} {dim('(' + t(LEVEL_KEY[p['level']]) + ')')}")

    clients = detect_clients()
    out()
    out(f"  {t('stat.ai')}: " + (
        ", ".join(f"{n}{'' if wired else dim(' (' + t('conn.notwired') + ')')}"
                  for n, wired in clients)
        if clients else dim(t("stat.noai"))))

    recent = _recent(w)
    if recent:
        out()
        out(bold(t("stat.recent")))
        for n in recent:
            out(f"  {n.title}  {dim('(' + n.type + ')')}")

    a = w.attention()
    pending = (len(a["queue"]) + len(a["open_questions"]) + len(a["errors"]))
    out()
    if pending:
        out(bold(t("stat.pending", n=pending)))
        for line in a["queue"][:5]:
            out(f"  {yellow('!')} {line}")
        for n, _ in a["open_questions"][:5]:
            out(f"  {dim('?')} {n.title}")
        for e in a["errors"][:3]:
            out(f"  {red('x')} {e}")
        out()
        out(dim(t("stat.seeall")))
    else:
        out(green(t("att.clean")))
    return 0


def find_obsidian() -> bool:
    """Portable, non-invasive: a config dir or an executable on PATH."""
    if shutil.which("obsidian"):
        return True
    home = Path.home()
    candidates = [home / ".config" / "obsidian",
                  home / "Library" / "Application Support" / "obsidian"]
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates.append(Path(appdata) / "obsidian")
    return any(p.is_dir() for p in candidates)


def cmd_doctor(path=None):
    rule(t("doc.title"))
    out()
    ok = True

    # labels differ in length by language, so measure rather than assume
    labels = [t(k) for k in ("doc.python", "doc.eksb", "doc.workspace", "doc.schema",
                             "doc.items", "doc.relations", "doc.broken", "doc.config",
                             "doc.obsidian", "doc.mcp", "doc.project")]
    pad = max(len(x) for x in labels) + 2

    def row(label, value, status=None):
        value = str(value)
        if len(value) > 34 and status:      # a long path must not eat its status
            out(f"  {label:<{pad}}{status}")
            out(f"  {'':<{pad}}{dim(value)}")
        else:
            out(f"  {label:<{pad}}{value:<34}{status or ''}".rstrip())

    row(t("doc.python"), platform.python_version(), green(t("doc.ok")))
    row(t("doc.eksb"), __version__, green(t("doc.ok")))

    note = None
    try:
        w = resolve_ws(path)
    except UserError as e:
        row(t("doc.workspace"), t("doc.none"), yellow("—"))
        note = e                            # said after the table, not inside it
        w = None

    if w:
        row(t("doc.workspace"),
            _short(w.root) + (yellow("  [" + t("demo.label") + "]") if w.is_demo else ""),
            green(t("doc.ok")))
        row(t("doc.schema"), "1", green(t("doc.ok")))
        counts = w.counts()
        row(t("doc.items"), counts["notes"])
        row(t("doc.relations"), counts["relations"])
        row(t("doc.broken"), counts["broken"],
            green(t("doc.ok")) if not counts["broken"] else red(t("doc.problem")))
        errors, warnings, _ = validate(w.root)
        if errors:
            ok = False
            out()
            for e in errors[:20]:
                out(f"  {red(e)}")
        if counts["broken"]:
            ok = False

    cfg = config.config_file()
    row(t("doc.config"), _short(cfg) if cfg.exists() else t("doc.none"),
        green(t("doc.ok")))

    out()
    if w:
        rows = ingest.levels(w)
        if rows:
            out()
            for r in rows:
                row(t("doc.project"), f"{r['title']} ({t(LEVEL_KEY[r['level']])})",
                    dim(t("proj.counts", indexed=r["indexed"],
                          integrated=r["integrated"])))

    out()
    out(dim(t("doc.optional")))
    row(t("doc.obsidian"),
        t("doc.detected") if find_obsidian() else t("doc.notdetected"), dim("—"))
    clients = detect_clients()
    wired = [n for n, on in clients if on]
    row(t("doc.mcp"),
        ", ".join(wired) if wired else
        (t("doc.available") if clients else t("doc.notdetected")), dim("—"))

    out()
    out(green(t("doc.ready")) if ok else red(t("doc.notready")))
    if note is not None:
        out()
        out(f"  {note}")
        out(f"  {dim(note.hint)}")
    return 0 if ok else 1


def _short(p) -> str:
    p = Path(p)
    try:
        return "~" + os.sep + str(p.relative_to(Path.home()))
    except ValueError:
        return str(p)


def cmd_about(path=None):
    rule(t("about.title"))
    try:
        w = resolve_ws(path)
        ws_path = str(w.root)
    except UserError:
        ws_path = t("doc.none")

    out()
    out(bold(t("about.data")))
    if w is not None and w.is_demo:
        out("  " + yellow("[" + t("demo.label") + "] " + t("demo.readonly")))
    out(f"  {t('about.data.ws')}")
    out(f"    {cyan(ws_path)}")
    out(f"  {t('about.data.cfg')}")
    out(f"    {cyan(str(config.config_dir()))}")

    out()
    out(bold(t("about.running")))
    out("  " + t("about.nodaemon").replace("\n", "\n  "))

    out()
    out(bold(t("about.network")))
    out("  " + t("about.nonetwork").replace("\n", "\n  "))

    out()
    out(bold(t("about.integrations")))
    out("  " + (t("about.obsidian.on") if find_obsidian() else t("about.obsidian.off")))
    out("  " + t("about.agents"))

    out()
    out(dim(t("about.stop")))
    return 0


def cmd_demo(path=None):
    target = Path(path).expanduser() if path else config.demo_dir()
    out(t("demo.installing"))
    w = ws.install_demo(target)
    config.set_(workspace=str(w.root))
    out()
    out(green(t("demo.ready", path=w.root)))
    out()
    out(t("demo.what"))
    out()
    out(bold(t("demo.try")))
    out(f'  {cyan("eksb search")} "partitioning"')
    out(f'  {cyan("eksb provenance")} "Time-Range Partitioning"')
    out(f'  {cyan("eksb attention")}')
    out(f'  {cyan("eksb validate")}')
    return 0


def cmd_init(path=None, name=None):
    target = Path(path).expanduser() if path else Path.cwd()
    try:
        w = ws.create(target, name)
    except ws.WorkspaceError as e:
        kind, _, p = str(e).partition(":")
        raise UserError(t("ws.exists" if kind == "already-workspace" else "ws.notempty",
                          path=p))
    config.set_(workspace=str(w.root))
    out()
    out(green(t("ws.created", path=w.root)))
    out(t("ws.stored"))
    return 0


def cmd_config(args):
    cfg = config.load()
    if args.set_lang:
        if args.set_lang not in LANGUAGES:
            raise UserError(f"unknown language: {args.set_lang}. "
                            f"Available: {', '.join(LANGUAGES)}")
        cfg = config.set_(lang=args.set_lang)
        set_lang(args.set_lang)
        out(green(t("lang.saved", lang=LANGUAGES[args.set_lang])))
        return 0
    if args.set_workspace:
        p = Path(args.set_workspace).expanduser().resolve()
        if not ws.is_workspace(p):
            raise UserError(t("ws.notfound", path=p), t("ws.none.hint"))
        config.set_(workspace=str(p))
        out(green(t("ws.opened", path=p)))
        return 0
    rule(t("set.title"))
    out()
    out(f"  {t('set.lang'):<22}{LANGUAGES.get(cfg.get('lang') or 'en')}")
    out(f"  {t('set.ws'):<22}{cfg.get('workspace') or t('doc.none')}")
    out(f"  {t('set.file'):<22}{config.config_file()}")
    return 0


def cmd_validate(path=None, strict=False):
    root = Path(path).expanduser() if path else None
    try:
        w = resolve_ws(root)
    except UserError:
        if root and root.is_dir():
            w = ws.Workspace(root)      # validate any folder of notes on request
        else:
            raise
    errors, warnings, n = validate(w.root)
    for x in warnings:
        out(yellow(f"warn  {x}"))
    for x in errors:
        out(red(f"ERROR {x}"))
    out()
    out(f"{n} notes · {len(errors)} errors · {len(warnings)} warnings")
    return 1 if errors or (strict and warnings) else 0


# -- interactive ---------------------------------------------------------
def pick_language(force=False) -> str:
    cfg = config.load()
    if cfg.get("lang") and not force:
        return set_lang(cfg["lang"])
    codes = list(LANGUAGES)
    rule(t("lang.choose"))
    for i, code in enumerate(codes, 1):
        out(f"  {cyan(str(i) + '.')} {LANGUAGES[code]}")
    out()
    while True:
        s = ask(t("menu.choose"), "1")
        if s.isdigit() and 1 <= int(s) <= len(codes):
            code = codes[int(s) - 1]
            config.set_(lang=code)
            set_lang(code)
            out(green(t("lang.saved", lang=LANGUAGES[code])))
            return code
        out(red(t("menu.invalid")))


def onboarding():
    banner(full=True)
    pick_language()
    tagline()
    rule(t("first.title"))
    out()
    out(t("pitch"))
    out()
    out(dim(t("first.journey")))
    action = choose(t("first.what"), [
        ("demo", t("first.try")),
        ("create", t("first.create")),
        ("open", t("first.open")),
        ("learn", t("first.learn")),
    ])
    made = None
    if action == "demo":
        cmd_demo()
        made = ws.Workspace(config.load()["workspace"])
    elif action == "create":
        default = str(Path.home() / "MyEKSB")
        cmd_init(ask(t("ws.where"), default))
        made = ws.Workspace(config.load()["workspace"])
        if find_obsidian():
            out()
            out(dim(t("about.obsidian.on")))
        if ask_yes(t("first.addproject")):
            path = ask(t("ing.path"))
            if path:
                try:
                    cmd_ingest(made, path)
                except UserError as e:
                    out(red(str(e)))
    elif action == "open":
        p = Path(ask(t("ws.path"))).expanduser().resolve()
        if not ws.is_workspace(p):
            out(red(t("ws.notfound", path=p)))
        else:
            config.set_(workspace=str(p))
            made = ws.Workspace(p)
            out(green(t("ws.opened", path=p)))
    elif action == "learn":
        learn_menu()
    config.set_(onboarded=True)

    out()
    out(green(t("ready")))
    if made is not None:
        out()
        out(t("first.connect.hint"))
        if ask_yes(t("first.connect.now")):
            cmd_connect(made)
    out()
    out(bold(t("ready.next")))
    out(f'  {cyan("eksb search")} {t("arg.word")}')
    out(f'  {cyan("eksb ingest")} {t("arg.path")}')
    out(f'  {cyan("eksb connect")}')
    return 0


def learn_menu():
    while True:
        pick = choose(t("learn.title"), [
            ("what", t("learn.what")),
            ("data", t("learn.data")),
            ("concepts", t("learn.concepts")),
            ("docs", t("learn.docs")),
        ], allow_back=True)
        if pick is None:
            return
        out()
        if pick == "what":
            out(t("pitch"))
        elif pick == "data":
            cmd_about()
        elif pick == "concepts":
            out(t("learn.concepts.body"))
        else:
            out(t("learn.docs.body"))
        out()
        pause()


def settings_menu():
    while True:
        cmd_config(argparse.Namespace(set_lang=None, set_workspace=None))
        pick = choose(t("set.title"), [
            ("lang", t("set.changelang")),
            ("ws", t("set.changews")),
        ], allow_back=True)
        if pick is None:
            return
        if pick == "lang":
            pick_language(force=True)
        else:
            path = ask(t("ws.path"))
            p = Path(path).expanduser().resolve()
            if ws.is_workspace(p):
                config.set_(workspace=str(p))
                out(green(t("ws.opened", path=p)))
            else:
                out(red(t("ws.notfound", path=p)))


def project_menu(w):
    pick = choose(t("proj.what"), [
        ("list", t("proj.list")),
        ("add", t("proj.add")),
    ], allow_back=True)
    if pick is None:
        return
    if pick == "list":
        cmd_projects(w)
        return
    path = ask(t("ing.path"))
    if not path:
        return
    name = ask(t("ing.name"), Path(path).expanduser().name)
    try:
        cmd_ingest(w, path, name)
    except UserError as e:
        out(red(str(e)))
        if e.hint:
            out(dim(e.hint))


def menu():
    """The main loop. Only offers what this build can actually do."""
    banner()
    try:
        w = resolve_ws()
        out(dim(f"{t('ws.current')}: {w.root}"))
    except UserError:
        w = None
        out(dim(t("ws.none")))
    while True:
        options = []
        if w:
            options += [("continue", t("menu.continue")),
                        ("search", t("menu.search")),
                        ("provenance", t("menu.provenance")),
                        ("project", t("menu.project")),
                        ("add", t("menu.add")),
                        ("connect", t("menu.connect")),
                        ("attention", t("menu.attention")),
                        ("health", t("menu.health"))]
        else:
            options += [("demo", t("first.try")), ("create", t("first.create")),
                        ("open", t("first.open"))]
        options += [("settings", t("menu.settings")),
                    ("learn", t("menu.learn")), ("exit", t("menu.exit"))]
        pick = choose(t("menu.title"), options)
        out()
        if pick == "exit":
            out(t("bye"))
            return 0
        try:
            w = dispatch_menu(pick, w)
        except UserError as e:          # stay in the menu; say what to do instead
            out(red(str(e)))
            if e.hint:
                out(dim(e.hint))
        out()
        pause()


def dispatch_menu(pick, w):
    """Run one menu choice. Returns the (possibly new) active workspace."""
    if pick == "continue":
        show_status(w)
    elif pick == "project":
        project_menu(w)
    elif pick == "connect":
        cmd_connect(w)
    elif pick == "search":
        cmd_search(w, ask(t("search.prompt")), interactive=True)
    elif pick == "add":
        add_menu(w)
    elif pick == "attention":
        show_attention(w)
    elif pick == "provenance":
        q = ask(t("search.prompt"))
        hits = w.search(q)
        n = w.get(q) or (hits[0][0] if hits else None)
        show_provenance(w, n) if n else out(red(t("note.notfound", q=q)))
    elif pick == "health":
        cmd_doctor(w.root)
    elif pick == "about":
        cmd_about(w.root if w else None)
    elif pick == "settings":
        settings_menu()
    elif pick == "learn":
        learn_menu()
    elif pick == "demo":
        cmd_demo()
        w = ws.Workspace(config.load()["workspace"])
    elif pick == "create":
        cmd_init(ask(t("ws.where"), str(Path.home() / "MyEKSB")))
        w = ws.Workspace(config.load()["workspace"])
    elif pick == "open":
        p = Path(ask(t("ws.path"))).expanduser().resolve()
        if ws.is_workspace(p):
            config.set_(workspace=str(p))
            w = ws.Workspace(p)
            out(green(t("ws.opened", path=p)))
        else:
            out(red(t("ws.notfound", path=p)))
    return w


# -- entry point ---------------------------------------------------------
def build_parser():
    p = argparse.ArgumentParser(
        prog="eksb",
        description="EKSB — keep decisions, ideas and sources connected.\n"
                    "Run `eksb` with no arguments for the interactive menu.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"eksb {__version__}")
    p.add_argument("--debug", action="store_true",
                   help="show technical details on errors")
    p.add_argument("--lang", choices=list(LANGUAGES),
                   help="language for this run (en, pt-BR)")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("demo", help="set up a demo workspace and show what to try") \
        .add_argument("path", nargs="?", help="where to put it")
    i = sub.add_parser("init", help="create a new workspace")
    i.add_argument("path", nargs="?", help="folder for the workspace")
    i.add_argument("--name", help="name for the workspace")
    sub.add_parser("open", help="use an existing workspace by default") \
        .add_argument("path", help="folder holding the workspace")

    s = sub.add_parser("search", help="find notes by word or phrase")
    s.add_argument("query", nargs="+")
    s.add_argument("-w", "--workspace")

    ad = sub.add_parser("add", help="create a new note")
    ad.add_argument("title", nargs="+")
    ad.add_argument("--type", default="concept", choices=list(ws.ADDABLE))
    ad.add_argument("-w", "--workspace")

    sv = sub.add_parser("save", help="keep a conversation or document as a source")
    sv.add_argument("file", help="text or Markdown file to keep")
    sv.add_argument("--title")
    sv.add_argument("--kind", default="personal_note", choices=list(ws.SOURCE_KINDS))
    sv.add_argument("-w", "--workspace")

    ig = sub.add_parser("ingest", help="add a project directory and index its text")
    ig.add_argument("path", help="the project directory")
    ig.add_argument("--name", help="what to call the project")
    ig.add_argument("--dry-run", action="store_true",
                    help="report what would be indexed, write nothing")
    ig.add_argument("--max-files", type=int, default=ingest.DEFAULT_MAX_FILES)
    ig.add_argument("-w", "--workspace")

    sub.add_parser("projects", help="list projects and how far each has got") \
        .add_argument("-w", "--workspace")

    cn = sub.add_parser("connect", help="connect an AI assistant over MCP")
    cn.add_argument("--json", action="store_true",
                    help="print only the client configuration")
    cn.add_argument("-w", "--workspace")

    sub.add_parser("mcp", help="run the MCP server (started by an AI client)") \
        .add_argument("-w", "--workspace")

    g = sub.add_parser("get", help="show one note")
    g.add_argument("id", help="note id, title or alias")
    g.add_argument("-w", "--workspace")

    pr = sub.add_parser("provenance", help="show where a note's content came from")
    pr.add_argument("id", help="note id, title or alias")
    pr.add_argument("-w", "--workspace")

    at = sub.add_parser("attention", help="list what needs a human decision")
    at.add_argument("-w", "--workspace")

    v = sub.add_parser("validate", help="check a workspace for problems")
    v.add_argument("path", nargs="?")
    v.add_argument("--warnings-are-errors", action="store_true")

    sub.add_parser("doctor", help="check the installation and workspace") \
        .add_argument("path", nargs="?")
    sub.add_parser("about", help="what EKSB stores and runs on this machine") \
        .add_argument("path", nargs="?")

    cf = sub.add_parser("config", help="show or change settings")
    cf.add_argument("--set-lang", metavar="LANG")
    cf.add_argument("--set-workspace", metavar="PATH")
    return p


def dispatch(args):
    if args.cmd is None:
        cfg = config.load()
        return menu() if cfg.get("onboarded") else onboarding()
    if args.cmd == "demo":
        return cmd_demo(args.path)
    if args.cmd == "init":
        return cmd_init(args.path, args.name)
    if args.cmd == "open":
        p = Path(args.path).expanduser().resolve()
        if not ws.is_workspace(p):
            raise UserError(t("ws.notfound", path=p), t("ws.none.hint"))
        config.set_(workspace=str(p))
        out(green(t("ws.opened", path=p)))
        return 0
    if args.cmd == "search":
        return cmd_search(resolve_ws(args.workspace), " ".join(args.query))
    if args.cmd == "add":
        return cmd_add(resolve_ws(args.workspace), args.type, " ".join(args.title))
    if args.cmd == "save":
        return cmd_save(resolve_ws(args.workspace), args.file, args.title, args.kind)
    if args.cmd == "ingest":
        return cmd_ingest(resolve_ws(args.workspace), args.path, args.name,
                          args.dry_run, args.max_files)
    if args.cmd == "projects":
        return cmd_projects(resolve_ws(args.workspace))
    if args.cmd == "connect":
        w = None
        try:
            w = resolve_ws(args.workspace)
        except UserError:
            pass                    # a config without a workspace is still useful
        return cmd_connect(w, args.json)
    if args.cmd == "mcp":
        return cmd_mcp(args.workspace)
    if args.cmd == "get":
        w = resolve_ws(args.workspace)
        n = w.get(args.id)
        if not n:
            raise UserError(t("note.notfound", q=args.id))
        show_note(n)
        return 0
    if args.cmd == "provenance":
        w = resolve_ws(args.workspace)
        n = w.get(args.id)
        if not n:
            raise UserError(t("note.notfound", q=args.id))
        show_provenance(w, n)
        return 0
    if args.cmd == "attention":
        return show_attention(resolve_ws(args.workspace))
    if args.cmd == "validate":
        return cmd_validate(args.path, args.warnings_are_errors)
    if args.cmd == "doctor":
        return cmd_doctor(args.path)
    if args.cmd == "about":
        return cmd_about(args.path)
    if args.cmd == "config":
        return cmd_config(args)
    return 1


def main(argv=None):
    global DEBUG
    args = build_parser().parse_args(argv)
    DEBUG = args.debug
    set_lang(args.lang or config.load().get("lang"))
    try:
        return dispatch(args)
    except UserError as e:
        out()
        out(red(str(e)))
        if e.hint:
            out(dim(e.hint))
        return 1
    except KeyboardInterrupt:
        out()
        out(t("err.interrupted"))
        return 130
    except Exception as e:                              # pragma: no cover
        if DEBUG:
            raise
        out()
        out(red(t("err.generic", msg=e)))
        out(dim(t("err.debug")))
        return 1


if __name__ == "__main__":
    sys.exit(main())
