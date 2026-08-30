"""The `eksb` command: an interactive menu plus direct subcommands.

Cross-platform by construction — pathlib, no shell-outs, no POSIX assumptions.
"""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import sys
from pathlib import Path

from . import __version__, config, workspace as ws
from .i18n import LANGUAGES, get_lang, set_lang, t
from .validate import validate

DEBUG = False

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


def banner():
    tag = t("tagline")
    width = max(len("EKSB"), len(tag)) + 4
    if UNI:
        tl, tr, bl, br, h, v = "┌", "┐", "└", "┘", "─", "│"
    else:
        tl = tr = bl = br = "+"
        h, v = "-", "|"
    out()
    out(cyan(tl + h * width + tr))
    out(cyan(v) + bold("EKSB".center(width)) + cyan(v))
    out(cyan(v) + tag.center(width) + cyan(v))
    out(cyan(bl + h * width + br))


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
    path = ws.add_note(w, type_, title)
    out()
    out(green(t("add.created", path=path)))
    out(dim(t("add.edit")))
    return 0


def cmd_save(w, src, title=None, kind="personal_note"):
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

    def row(label, value, status=None):
        out(f"  {label:<22}{str(value):<34}{status or ''}".rstrip())

    row(t("doc.python"), platform.python_version(), green(t("doc.ok")))
    row(t("doc.eksb"), __version__, green(t("doc.ok")))

    try:
        w = resolve_ws(path)
    except UserError as e:
        row(t("doc.workspace"), t("doc.none"), yellow("—"))
        out()
        out(f"  {e}")
        out(f"  {dim(e.hint)}")
        w = None

    if w:
        row(t("doc.workspace"), _short(w.root), green(t("doc.ok")))
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
    out(dim(t("doc.optional")))
    row(t("doc.obsidian"),
        t("doc.detected") if find_obsidian() else t("doc.notdetected"), dim("—"))
    row("MCP", t("doc.notdetected"), dim("—"))

    out()
    out(green(t("doc.ready")) if ok else red(t("doc.notready")))
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
    banner()
    pick_language()
    rule(t("first.title"))
    out()
    out(t("pitch"))
    action = choose(t("first.what"), [
        ("demo", t("first.try")),
        ("create", t("first.create")),
        ("open", t("first.open")),
        ("learn", t("first.learn")),
    ])
    if action == "demo":
        cmd_demo()
    elif action == "create":
        default = str(Path.home() / "MyEKSB")
        path = ask(t("ws.where"), default)
        cmd_init(path)
        if find_obsidian():
            out()
            out(dim(t("about.obsidian.on")))
    elif action == "open":
        path = ask(t("ws.path"))
        p = Path(path).expanduser().resolve()
        if not ws.is_workspace(p):
            out(red(t("ws.notfound", path=p)))
        else:
            config.set_(workspace=str(p))
            out(green(t("ws.opened", path=p)))
    elif action == "learn":
        learn_menu()
    config.set_(onboarded=True)
    out()
    out(green(t("ready")))
    out()
    out(bold(t("ready.next")))
    out(f'  {cyan("eksb search")} {t("arg.word")}')
    out(f'  {cyan("eksb attention")}')
    out(f'  {cyan("eksb doctor")}')
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
            options += [("search", t("menu.search")),
                        ("add", t("menu.add")),
                        ("attention", t("menu.attention")),
                        ("provenance", t("menu.provenance")),
                        ("health", t("menu.health"))]
        else:
            options += [("demo", t("first.try")), ("create", t("first.create")),
                        ("open", t("first.open"))]
        options += [("about", t("menu.about")), ("settings", t("menu.settings")),
                    ("learn", t("menu.learn")), ("exit", t("menu.exit"))]
        pick = choose(t("menu.title"), options)
        out()
        if pick == "exit":
            out(t("bye"))
            return 0
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
        out()
        pause()


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
