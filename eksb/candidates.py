"""What an agent may propose, and what EKSB does with it.

An agent reads a workspace and proposes a **candidate**: a durable note it
thinks should exist, with claims, sources and relations. This module decides
what happens to it, deterministically:

    CREATE           no canonical match      -> written
    UPDATE           new claims on a match   -> appended, never overwritten
    LINK             a relation to add       -> appended
    NO_OP            already there           -> nothing
    CONFLICT         contradicts a position  -> review queue
    REVIEW_REQUIRED  identity/authority call -> review queue

The rule the whole design exists to enforce: **an agent's claim can never
enter the workspace as the user's own position.** `user_position` submitted
by an agent is refused outright — not downgraded quietly, refused, so the
caller learns the boundary rather than silently producing a wrong record.

Everything here is ordinary Python and file appends. There is no engine.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .validate import EPISTEMIC, RELATIONS, TYPES
from .workspace import (Note, Workspace, WorkspaceError, _unique, new_id,
                        refuse_if_demo, safe_filename)

# What an agent is allowed to assert. `user_position` is deliberately absent:
# only a human can hold a position.
AGENT_EPISTEMIC = {"assistant_hypothesis", "source_claim", "external_fact",
                   "inference", "open_question"}

PROPOSABLE = ("concept", "principle", "hypothesis", "question", "decision",
              "risk", "goal", "technology", "project")

ACTIONS = ("CREATE", "UPDATE", "LINK", "NO_OP", "CONFLICT", "REVIEW_REQUIRED",
           "REJECTED")

QUEUE = Path("dashboards") / "Review Queue.md"

DEMO_REASON = ("this is the demo workspace, which is a fixed sandbox. Ask the "
               "user to create or open their own workspace (eksb init <path>) "
               "before recording anything real.")


@dataclass
class Outcome:
    action: str
    reason: str = ""
    note_id: str = ""
    path: str = ""
    question: str = ""            # the one short question to put to a human
    applied: bool = False
    details: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        d = {"action": self.action, "applied": self.applied}
        for k in ("reason", "note_id", "path", "question"):
            if getattr(self, k):
                d[k] = getattr(self, k)
        if self.details:
            d["details"] = self.details
        return d


class Rejected(Exception):
    """The candidate is malformed or asks for something an agent may not do."""


# -- shape ---------------------------------------------------------------
def normalize(cand: dict, asserted_by: str = "agent") -> dict:
    """Validate an incoming candidate. Raises Rejected with a plain reason."""
    if not isinstance(cand, dict):
        raise Rejected("candidate must be an object")

    kind = str(cand.get("type") or cand.get("kind") or "concept").strip()
    if kind not in PROPOSABLE:
        raise Rejected(f"type {kind!r} cannot be proposed; "
                       f"use one of: {', '.join(PROPOSABLE)}")
    if kind not in TYPES:
        raise Rejected(f"unknown type {kind!r}")

    title = str(cand.get("title") or "").strip()
    if not title:
        raise Rejected("a candidate needs a title")
    if len(title) > 200:
        raise Rejected("title is too long")

    sources = [str(s).strip() for s in (cand.get("sources") or []) if str(s).strip()]

    claims = []
    for raw in cand.get("claims") or []:
        if isinstance(raw, str):
            raw = {"text": raw}
        if not isinstance(raw, dict):
            raise Rejected(f"each claim must be an object or a string: {raw!r}")
        text = " ".join(str(raw.get("text") or "").split())
        if not text:
            raise Rejected("a claim needs text")
        ep = str(raw.get("epistemic") or "assistant_hypothesis").strip()
        if ep == "user_position":
            raise Rejected(
                "an agent may not assert user_position. Propose it as "
                "assistant_hypothesis or source_claim; only the person can "
                "promote it.")
        if ep not in EPISTEMIC:
            raise Rejected(f"unknown epistemic status {ep!r}")
        if ep not in AGENT_EPISTEMIC:
            raise Rejected(f"an agent may not assert {ep!r}")
        src = str(raw.get("source") or "").strip()
        claims.append({"text": text, "epistemic": ep, "source": src})

    relations = []
    for raw in cand.get("relations") or []:
        if not isinstance(raw, dict):
            raise Rejected(f"each relation must be an object: {raw!r}")
        rel = str(raw.get("rel") or "").strip()
        target = str(raw.get("target") or "").strip().strip("[]")
        if rel not in RELATIONS:
            raise Rejected(f"unknown relation {rel!r}; "
                           f"the vocabulary is closed: {', '.join(sorted(RELATIONS))}")
        if not target:
            raise Rejected(f"relation {rel} needs a target")
        relations.append({"rel": rel, "target": target,
                          "epistemic": "assistant_hypothesis"})

    return {"type": kind, "title": title,
            "summary": " ".join(str(cand.get("summary") or "").split()),
            "claims": claims, "relations": relations, "sources": sources,
            "aliases": [str(a).strip() for a in (cand.get("aliases") or [])
                        if str(a).strip()],
            "supersedes": str(cand.get("supersedes") or "").strip(),
            "asserted_by": asserted_by}


# -- adjudication --------------------------------------------------------
def _claim_key(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", text.lower()).strip()


def adjudicate(w: Workspace, cand: dict) -> Outcome:
    """Decide, without writing anything. `cand` must already be normalized."""
    if not cand["sources"] and not any(c["source"] for c in cand["claims"]):
        return Outcome("REVIEW_REQUIRED",
                       reason="nothing to trace this back to",
                       question=f"Where did “{cand['title']}” come from? "
                                f"Nothing was proposed as its source.")

    missing = [s for s in cand["sources"] if w.get(s) is None]
    if missing:
        return Outcome("REVIEW_REQUIRED",
                       reason=f"source not in this workspace: {', '.join(missing)}",
                       question=f"“{cand['title']}” cites {', '.join(missing)}, "
                                f"which is not here. Should it be added first?")

    if cand["supersedes"]:
        target = w.get(cand["supersedes"])
        where = target.title if target else cand["supersedes"]
        return Outcome("REVIEW_REQUIRED",
                       reason="replacing an existing note is a human decision",
                       question=f"Does “{cand['title']}” replace “{where}”, "
                                f"or do both still hold?")

    match = w.get(cand["title"]) or next(
        (n for a in cand["aliases"] if (n := w.get(a)) is not None), None)

    if match is None:
        return Outcome("CREATE", note_id="", reason="no existing note matches")

    if match.type == "source":
        return Outcome("REVIEW_REQUIRED", note_id=match.id,
                       reason="that title belongs to raw material",
                       question=f"“{cand['title']}” is already the name of a "
                                f"source. What should the new note be called?")

    held = {_claim_key(text): tag for tag, text in match.claims()}
    new_claims = [c for c in cand["claims"] if _claim_key(c["text"]) not in held]

    contradicted = [c for c in cand["claims"]
                    if held.get(_claim_key(c["text"])) == "user_position"]
    if contradicted:
        return Outcome("NO_OP", note_id=match.id,
                       reason="already recorded as the person's own position")

    if match.fm.get("status") == "superseded":
        return Outcome("CONFLICT", note_id=match.id,
                       reason="the matching note was superseded",
                       question=f"“{match.title}” was replaced by "
                                f"“{str(match.fm.get('superseded_by') or '?').strip('[]')}”, "
                                f"but new material still points at it. "
                                f"Which one is current?")

    if not new_claims and not cand["relations"]:
        return Outcome("NO_OP", note_id=match.id, reason="nothing new to add")

    return Outcome("UPDATE", note_id=match.id,
                   reason=f"{len(new_claims)} new claim(s)",
                   details=[c["text"] for c in new_claims])


# -- writing -------------------------------------------------------------
def apply(w: Workspace, cand: dict, decision: Outcome) -> Outcome:
    """Carry out a safe decision; queue an unsafe one. Returns the outcome."""
    if decision.action == "CREATE":
        path = _create(w, cand)
        decision.path, decision.applied = str(path), True
        w._notes = None
        note = w.get(cand["title"])
        decision.note_id = note.id if note else ""
    elif decision.action == "UPDATE":
        note = w.get(decision.note_id)
        if note is None:
            decision.action, decision.reason = "REVIEW_REQUIRED", "note disappeared"
        else:
            _append_claims(w, note, cand, decision.details)
            decision.path, decision.applied = str(note.path), True
            w._notes = None
    elif decision.action in ("CONFLICT", "REVIEW_REQUIRED"):
        queue(w, decision.action, cand, decision)
        decision.applied = False
    return decision


def submit(w: Workspace, raw: dict, asserted_by: str = "agent") -> Outcome:
    """normalize -> adjudicate -> apply. The whole writeback path."""
    try:
        refuse_if_demo(w)
    except WorkspaceError:
        return Outcome("REJECTED", reason=DEMO_REASON)
    try:
        cand = normalize(raw, asserted_by)
    except Rejected as e:
        return Outcome("REJECTED", reason=str(e))
    return apply(w, cand, adjudicate(w, cand))


def _frontmatter(cand: dict, nid: str) -> str:
    lines = ["---", "schema_version: 1", f"type: {cand['type']}",
             "track: instance", f"id: {nid}",
             f'title: "{cand["title"].replace(chr(34), chr(39))}"',
             f"created: {date.today().isoformat()}"]
    if cand["aliases"]:
        lines.append("aliases: [" + ", ".join(
            f'"{a}"' for a in cand["aliases"]) + "]")
    # the note's baseline is what an agent is allowed to assert, never a position
    lines += ["epistemic_default: assistant_hypothesis", "status: active",
              f"proposed_by: {cand['asserted_by']}"]
    if cand["sources"]:
        lines.append("sources: [" + ", ".join(cand["sources"]) + "]")
    else:
        lines.append("sources: []")
    if cand["relations"]:
        lines.append("relations:")
        for r in cand["relations"]:
            lines += [f"  - rel: {r['rel']}",
                      f'    target: "[[{r["target"]}]]"',
                      "    epistemic: assistant_hypothesis"]
            if cand["sources"]:
                lines.append(f"    source: {cand['sources'][0]}")
    else:
        lines.append("relations: []")
    lines.append("---")
    return "\n".join(lines) + "\n"


def _claim_line(c: dict, cand: dict) -> str:
    src = c["source"] or (cand["sources"][0] if cand["sources"] else "")
    cite = f" ([[{src}]])" if src else ""
    return f"- {c['text']} #e/{c['epistemic']}{cite}\n"


def _create(w: Workspace, cand: dict) -> Path:
    nid = new_id(cand["type"], cand["title"])
    body = [""]
    if cand["summary"]:
        body += ["## Definition", "", cand["summary"], ""]
    if cand["claims"]:
        body += ["## Claims", ""]
        body += [_claim_line(c, cand).rstrip() for c in cand["claims"]]
        body += [""]
    body += ["<!-- Proposed by an assistant and not yet endorsed. Claims stay",
             "     #e/assistant_hypothesis until a person promotes them. -->", ""]
    folder = sorted(TYPES[cand["type"]][1])[0] or "."
    dest = _unique(w.root / folder / safe_filename(cand["title"]))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(_frontmatter(cand, nid) + "\n".join(body), encoding="utf-8")
    return dest


def _append_claims(w: Workspace, note: Note, cand: dict, texts: list[str]) -> None:
    """Append under ## Claims. Existing text is never touched."""
    wanted = {t for t in texts}
    new = [c for c in cand["claims"] if c["text"] in wanted] or cand["claims"]
    if not new:
        return
    text = note.path.read_text(encoding="utf-8")
    block = "".join(_claim_line(c, cand) for c in new)
    lines = text.splitlines(keepends=True)

    insert_at, in_claims = None, False
    for i, ln in enumerate(lines):
        if ln.startswith("#"):
            if in_claims:
                insert_at = i
                break
            in_claims = ln.strip().lower().endswith("claims")
    if in_claims and insert_at is None:
        insert_at = len(lines)

    if insert_at is None:                       # no Claims section yet
        text = text.rstrip("\n") + "\n\n## Claims\n\n" + block
    else:
        while insert_at > 0 and not lines[insert_at - 1].strip():
            insert_at -= 1
        lines.insert(insert_at, block)
        text = "".join(lines)
    note.path.write_text(text, encoding="utf-8")


def queue(w: Workspace, kind: str, cand: dict, decision: Outcome) -> Path:
    """Append to the review queue. Only a human clears an item."""
    path = w.root / QUEUE
    heading = {"CONFLICT": "## CONFLICT — contradictions needing a human ruling",
               "REVIEW_REQUIRED": "## REVIEW_REQUIRED — identity, merges, renames"}[kind]
    entry = (f"- **{cand['title']}** — {decision.question or decision.reason}  \n"
             f"  <!-- proposed {date.today().isoformat()} by {cand['asserted_by']}; "
             f"{decision.reason} -->\n")
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "---\nschema_version: 1\ntype: dashboard\ntrack: instance\n"
            f"id: {new_id('dashboard', 'review queue')}\n"
            "title: Review Queue\n"
            f"created: {date.today().isoformat()}\ngenerated: true\n---\n\n"
            f"{heading}\n\n_(none)_\n", encoding="utf-8")

    text = path.read_text(encoding="utf-8")
    if heading not in text:
        text = text.rstrip("\n") + f"\n\n{heading}\n\n_(none)_\n"
    lines = text.splitlines(keepends=True)
    start = next(i for i, ln in enumerate(lines) if ln.startswith(heading))
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].startswith("## ")), len(lines))
    section = lines[start:end]
    section = [ln for ln in section if ln.strip() != "_(none)_"]
    while len(section) > 1 and not section[-1].strip():
        section.pop()
    section.append(entry)
    section.append("\n")
    path.write_text("".join(lines[:start] + section + lines[end:]), encoding="utf-8")
    w._notes = None
    return path
