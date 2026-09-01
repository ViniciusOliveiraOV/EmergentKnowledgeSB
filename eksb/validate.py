#!/usr/bin/env python3
"""Frontmatter/schema validator for an EKSB workspace.

    python -m eksb.validate [path] [--warnings-are-errors]
    python -m eksb.validate --selftest

Exit 0 = clean. Read-only: this never writes to a workspace.
"""
import hashlib, re, sys, pathlib

try:
    import yaml
except ImportError:                                    # pragma: no cover
    sys.exit("needs pyyaml:  python -m pip install pyyaml")

SKIP_DIRS = {".git", ".obsidian", "_templates", "node_modules", ".venv"}
# repo-convention files at the workspace root: not notes.
SKIP_ROOT_FILES = {"AGENTS.md", "README.md", "CLAUDE.md"}

# ontology: type -> (id prefix, allowed folders)
TYPES = {
    "concept":      ("c-",   {"concepts"}),
    "principle":    ("c-",   {"concepts"}),
    "hypothesis":   ("c-",   {"concepts"}),
    "question":     ("c-",   {"concepts"}),
    "risk":         ("c-",   {"concepts"}),
    "goal":         ("c-",   {"concepts"}),
    "person":       ("p-",   {"concepts"}),
    "organization": ("o-",   {"concepts"}),
    "technology":   ("t-",   {"concepts"}),
    "book":         ("b-",   {"references"}),
    "paper":        ("r-",   {"references"}),
    "decision":     ("d-",   {"decisions"}),
    "source":       ("src-", {"_sources"}),
    "project":      ("prj-", {"projects"}),
    "roadmap":      ("rm-",  {"projects"}),
    "moc":          ("moc-", {"projects"}),
    "dashboard":    ("dsh-", {"dashboards"}),
    "doc":          ("doc-", {"_system", ""}),   # "" = workspace root
}
RELATIONS = {"supports", "contradicts", "depends_on", "requires", "implements",
             "informed_by", "derived_from", "related_to", "replaces",
             "evolves_from", "questions", "applies_to"}
EPISTEMIC = {"user_position", "assistant_hypothesis", "external_fact",
             "source_claim", "inference", "open_question"}
REQUIRED = ("schema_version", "type", "id", "title", "created")
# system-time fields: full dates only. knowledge-time fields: imprecision
# is honest, so YYYY / YYYY-MM / YYYY-MM-DD all pass.
EXACT_DATES = ("created", "updated", "review", "ingested_at")
FUZZY_DATES = ("asserted_at", "valid_from", "valid_until", "decided_on",
               "source_date")
ID_RE = re.compile(r"^[a-z]+-\d{8}-[a-z0-9-]+$")
ADR_ID_RE = re.compile(r"^adr-\d{4}-[a-z0-9-]+$")
TRACKS = {"core", "instance"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
FUZZY_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
FM_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
TAG_RE = re.compile(r"#e/([a-z_]+)")


def split_frontmatter(text):
    """(frontmatter dict, body) or (None, error string)."""
    m = FM_RE.match(text)
    if not m:
        return None, "no YAML frontmatter"
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return None, f"unparseable frontmatter: {e}"
    if not isinstance(fm, dict):
        return None, "frontmatter is not a mapping"
    return fm, m.group(2)


def check(path, root, errors, warnings):
    rel = path.relative_to(root)
    err = lambda m: errors.append(f"{rel}: {m}")
    warn = lambda m: warnings.append(f"{rel}: {m}")

    fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
    if fm is None:
        return err(body)

    if "adr" in rel.parts:
        for k in ("id", "track", "status", "date"):
            if fm.get(k) in (None, ""):
                err(f"ADR missing required key: {k}")
        if not ADR_ID_RE.match(str(fm.get("id", ""))):
            err(f"ADR id {fm.get('id')!r} not adr-NNNN-slug")
        if fm.get("id") != path.stem:
            err(f"ADR id {fm.get('id')!r} must match filename {path.stem!r}")
        if fm.get("track") not in TRACKS:
            err(f"track {fm.get('track')!r} not in {sorted(TRACKS)}")
        if not DATE_RE.match(str(fm.get("date", ""))):
            err(f"ADR date {fm.get('date')!r} must be YYYY-MM-DD")
        for h in ("## Context", "## Decision", "## Rationale",
                  "## Consequences", "## Revisit when"):
            if h not in body:
                err(f"ADR missing section: {h}")
        return

    for k in REQUIRED:
        if fm.get(k) in (None, ""):
            err(f"missing required key: {k}")

    t = fm.get("type")
    if t not in TYPES:
        return err(f"unknown type: {t!r}")
    prefix, folders = TYPES[t]

    nid = str(fm.get("id", ""))
    if not ID_RE.match(nid):
        err(f"id {nid!r} not <prefix>-<yyyymmdd>-<slug>")
    elif not nid.startswith(prefix):
        err(f"id {nid!r} should start with {prefix!r} for type {t}")

    top = rel.parts[0] if len(rel.parts) > 1 else ""   # "" = workspace root
    if top not in folders:
        err(f"type {t} lives in {sorted(folders)}, found in {top}/")

    if fm.get("schema_version") != 1:
        err(f"schema_version {fm.get('schema_version')!r}, expected 1")

    for k in EXACT_DATES:
        v = fm.get(k)
        if v not in (None, "") and not DATE_RE.match(str(v)):
            err(f"{k}: {v!r} must be YYYY-MM-DD")
    for k in FUZZY_DATES:
        v = fm.get(k)
        if v not in (None, "") and not FUZZY_RE.match(str(v)):
            err(f"{k}: {v!r} must be YYYY, YYYY-MM or YYYY-MM-DD")

    # two clocks: knowledge time may precede system time (retroactive nodes are
    # normal) but a position asserted after its note existed is a data error.
    a, c = str(fm.get("asserted_at") or ""), str(fm.get("created") or "")
    if a and c:
        n = min(len(a), len(c))   # compare only the precision both share
        if a[:n] > c[:n]:
            warn(f"asserted_at {a} is after created {c} — check the two clocks")

    tr = fm.get("track")
    if tr is not None and tr not in TRACKS:
        err(f"track {tr!r} not in {sorted(TRACKS)}")

    ed = fm.get("epistemic_default")
    if ed and ed not in EPISTEMIC:
        err(f"epistemic_default {ed!r} not in {sorted(EPISTEMIC)}")

    if fm.get("status") == "superseded" and not fm.get("superseded_by"):
        err("status: superseded requires superseded_by")

    for r in fm.get("relations") or []:
        if not isinstance(r, dict) or "rel" not in r or "target" not in r:
            err(f"relation needs rel+target: {r!r}")
            continue
        if r["rel"] not in RELATIONS:
            err(f"unknown relation {r['rel']!r}")
        if r.get("epistemic") and r["epistemic"] not in EPISTEMIC:
            err(f"relation epistemic {r['epistemic']!r} invalid")
        # agent-asserted relations must be traceable (provenance rule 3)
        if r.get("epistemic") in {"assistant_hypothesis", "inference"} \
                and not r.get("source"):
            err(f"agent-asserted relation {r['rel']} needs a source")

    for tag in set(TAG_RE.findall(body)):
        if tag not in EPISTEMIC:
            err(f"invalid epistemic tag #e/{tag}")

    if t == "source":
        h = str(fm.get("content_hash") or "")
        actual = "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()
        if not h:
            warn("source has no content_hash (raw-history integrity unchecked)")
        elif h != actual:
            err(f"content_hash mismatch — raw body was edited. "
                f"expected {h}, got {actual}")
        for key in ("source_type", "ingested_at", "ingested_by"):
            if not fm.get(key):
                warn(f"source missing {key}")
    else:
        # unattributed claims: a bullet under ## Claims with no epistemic tag
        in_claims, bullet = False, None
        def flush():
            if bullet and not TAG_RE.search(bullet):
                warn(f"unattributed claim: {bullet[2:60].strip()!r}")
        for line in body.splitlines() + ["#"]:
            if line.startswith("- ") or line.startswith("#") or not line.strip():
                flush(); bullet = None
            if line.startswith("#"):
                in_claims = line.strip().lower().endswith("claims")
            elif in_claims and line.startswith("- "):
                bullet = line
            elif bullet is not None and line[:1].isspace():
                bullet += " " + line.strip()


def note_paths(root):
    return sorted(p for p in root.rglob("*.md")
                  if not SKIP_DIRS & set(p.relative_to(root).parts)
                  and not (p.parent == root and p.name in SKIP_ROOT_FILES))


def validate(root):
    """(errors, warnings, note_count). Never raises on note content."""
    root = pathlib.Path(root).resolve()
    errors, warnings = [], []
    files = note_paths(root)
    for p in files:
        check(p, root, errors, warnings)
    return errors, warnings, len(files)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    args = [a for a in argv if not a.startswith("-")]
    root = pathlib.Path(args[0]) if args else pathlib.Path.cwd()
    errors, warnings, n = validate(root)
    for w in warnings:
        print(f"warn  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{n} notes · {len(errors)} errors · {len(warnings)} warnings")
    strict = "--warnings-are-errors" in argv
    return 1 if errors or (strict and warnings) else 0


BAD = """---
schema_version: 1
type: concept
id: WRONG-ID
title: Bad
epistemic_default: totally_made_up
status: superseded
created: March 2026
asserted_at: 2026-3
relations:
  - rel: invented_relation
    target: "[[X]]"
  - rel: supports
    epistemic: inference
    target: "[[Y]]"
---

## Claims

- Untagged claim.
- Tagged wrong. #e/nonsense_tag
"""


def selftest():
    """One note that violates every rule; assert each is caught."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "concepts").mkdir()
        bad = root / "concepts" / "Bad.md"
        bad.write_text(BAD, encoding="utf-8")
        errors, warnings = [], []
        check(bad, root, errors, warnings)
        joined = " ".join(errors)
        for expect in ("not <prefix>", "epistemic_default", "superseded_by",
                       "unknown relation", "needs a source", "invalid epistemic tag",
                       "must be YYYY-MM-DD", "must be YYYY, YYYY-MM"):
            assert expect in joined, f"missed: {expect}\n{joined}"
        assert any("Untagged claim" in w for w in warnings), warnings
        # and a valid note must produce nothing
        good = root / "concepts" / "Good.md"
        good.write_text("---\nschema_version: 1\ntype: concept\n"
                        "id: c-20260826-good\ntitle: Good\n"
                        "created: 2026-08-26\nasserted_at: 2026-03\n---\n\n"
                        "## Claims\n\n- Fine. #e/user_position\n", encoding="utf-8")
        errors, warnings = [], []
        check(good, root, errors, warnings)
        # retroactive node: asserted_at 2026-03 precedes created — must be clean
        assert not errors and not warnings, (errors, warnings)
        # ...but a coarser date that is genuinely later must still warn
        good.write_text(good.read_text(encoding="utf-8").replace(
            "asserted_at: 2026-03", "asserted_at: 2027"), encoding="utf-8")
        errors, warnings = [], []
        check(good, root, errors, warnings)
        assert any("two clocks" in w for w in warnings), (errors, warnings)
        # ADR branch: its own minimal frontmatter, its own failure modes
        adr = root / "_system" / "adr" / "adr-0001-x.md"
        adr.parent.mkdir(parents=True)
        adr.write_text("---\nid: adr-1-x\ntrack: nope\nstatus: accepted\n"
                       "date: March\n---\n\n# D\n\n## Context\n", encoding="utf-8")
        errors, warnings = [], []
        check(adr, root, errors, warnings)
        joined = " ".join(errors)
        for expect in ("not adr-NNNN-slug", "must match filename", "track 'nope'",
                       "must be YYYY-MM-DD", "missing section: ## Decision"):
            assert expect in joined, f"ADR check missed: {expect}\n{joined}"
    print("selftest ok")


if __name__ == "__main__":
    from . import use_utf8
    use_utf8()
    if "--selftest" in sys.argv:
        selftest()
    else:
        sys.exit(main())
