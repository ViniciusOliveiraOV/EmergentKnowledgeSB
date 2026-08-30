"""A generic MCP server over the workspace. Any compatible client can use it.

    eksb mcp [--workspace PATH]

JSON-RPC 2.0 over stdio, spoken directly — no SDK, no new dependency, no
socket, no port, no daemon. The client starts the process and it exits with
the client.

It belongs to EKSB and to nothing else: no vendor, no orchestrator, no
private configuration. Seven tools, each one a capability the CLI already
has, so nothing here can drift away from what `eksb` itself does.

Safety, which is the whole reason this is a narrow surface rather than a
filesystem: the server can read anything in the workspace, and can write
only through `eksb_submit_candidate`, which goes through the same
adjudication a human-run submission would. It cannot delete, cannot rename,
cannot edit raw sources, and cannot record a claim as the user's own
position.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from . import __version__, candidates, ingest, workspace as ws
from .validate import validate

PROTOCOL = "2024-11-05"
KNOWN_PROTOCOLS = {"2024-11-05", "2025-03-26", "2025-06-18"}
MAX_RESULTS = 25

TOOLS = [
    {
        "name": "eksb_search",
        "description": (
            "Search the user's EKSB knowledge workspace for notes matching a "
            "word or phrase. Use this BEFORE asking the user to re-explain a "
            "project, a past decision, or why something was done — the answer "
            "is often already recorded. Returns titles, types, ids and a "
            "matching line, not whole notes, so it stays cheap; follow up with "
            "eksb_get or eksb_provenance on the ids that look relevant."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "word or phrase"},
                "limit": {"type": "integer", "description":
                          f"max results, default 10, cap {MAX_RESULTS}"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "eksb_get",
        "description": (
            "Read one note in full, by its id, exact title or alias. Use after "
            "eksb_search has told you which note matters."),
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "string",
                                  "description": "note id, title or alias"}},
            "required": ["id"],
        },
    },
    {
        "name": "eksb_provenance",
        "description": (
            "Where a note came from and who asserted each of its claims: the "
            "user's own position, an assistant's unendorsed suggestion, a "
            "source's claim, an inference, or an open question. Use this "
            "before treating anything in the workspace as settled — a claim "
            "marked assistant_hypothesis is a previous model's guess, not "
            "something the user believes. Also returns the note's typed "
            "relations in both directions."),
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "string",
                                  "description": "note id, title or alias"}},
            "required": ["id"],
        },
    },
    {
        "name": "eksb_attention",
        "description": (
            "What in the workspace still needs a human decision: open "
            "questions, assistant suggestions never confirmed, outside claims "
            "never verified, positions the user has changed, and items already "
            "queued for review. Use this to avoid re-opening a settled "
            "question, or to surface a genuine ambiguity to the user."),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "eksb_workspace_status",
        "description": (
            "What this workspace actually contains: note and relation counts, "
            "validation state, and each registered project with how far it has "
            "got — registered (we know where it is), indexed (its text is "
            "here and retrievable), or integrated (durable knowledge exists, "
            "traced back to that text). A project at level 1 or 2 has NOT been "
            "understood; do not treat its files as canonical knowledge."),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "eksb_ingest",
        "description": (
            "Register a project directory and index the documentation text "
            "inside it, so it becomes searchable and citable. Incremental: "
            "unchanged files are skipped, changed files are kept as new "
            "versions, and nothing already indexed is destroyed. This does "
            "NOT extract knowledge — it makes raw material available so that "
            "you can propose knowledge from it with eksb_submit_candidate."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "the project directory"},
                "name": {"type": "string", "description": "optional project name"},
                "dry_run": {"type": "boolean",
                            "description": "report what would be indexed only"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "eksb_submit_candidate",
        "description": (
            "Propose durable knowledge for the workspace: a concept, "
            "principle, question, decision, risk, goal, technology or project, "
            "with its claims, sources and relations. EKSB decides what happens "
            "— CREATE, UPDATE (claims appended, never overwritten), NO_OP, or "
            "CONFLICT / REVIEW_REQUIRED, which puts one short question to the "
            "user instead of writing.\n\n"
            "Every claim must say who asserted it. You may use "
            "assistant_hypothesis (you are proposing it), source_claim (a "
            "source says it), external_fact (verifiable outside), inference "
            "(follows from what is already here) or open_question. You may NOT "
            "use user_position: only the person can hold a position, and "
            "submitting one is refused. Cite the source id each claim came "
            "from; a candidate that traces to nothing goes to review."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": list(candidates.PROPOSABLE),
                         "description": "what kind of thing this is"},
                "title": {"type": "string",
                          "description": "canonical name, as it should be known"},
                "summary": {"type": "string",
                            "description": "one paragraph: what this is"},
                "aliases": {"type": "array", "items": {"type": "string"},
                            "description": "other names for the same thing, so it "
                                           "does not fragment into duplicates"},
                "claims": {
                    "type": "array",
                    "description": "what the note asserts, each attributed",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "epistemic": {"type": "string",
                                          "enum": sorted(candidates.AGENT_EPISTEMIC)},
                            "source": {"type": "string",
                                       "description": "source note id"},
                        },
                        "required": ["text", "epistemic"],
                    },
                },
                "relations": {
                    "type": "array",
                    "description": "typed links to other notes; closed vocabulary",
                    "items": {
                        "type": "object",
                        "properties": {
                            "rel": {"type": "string",
                                    "enum": sorted(candidates.RELATIONS)},
                            "target": {"type": "string",
                                       "description": "the other note's title or id"},
                        },
                        "required": ["rel", "target"],
                    },
                },
                "sources": {"type": "array", "items": {"type": "string"},
                            "description": "source note ids this came from"},
                "supersedes": {"type": "string",
                               "description": "a note this replaces; always goes "
                                              "to human review"},
            },
            "required": ["title", "claims"],
        },
    },
]


class Server:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.client = ""

    # a fresh view per call: the files are the state, and they can change
    @property
    def w(self) -> ws.Workspace:
        return ws.Workspace(self.root)

    # -- tools -----------------------------------------------------------
    def t_eksb_search(self, query: str = "", limit: int = 10) -> dict:
        limit = max(1, min(int(limit or 10), MAX_RESULTS))
        hits = self.w.search(str(query), limit=limit)
        return {"query": query, "count": len(hits), "results": [
            {"id": n.id, "title": n.title, "type": n.type, "match": snippet[:200]}
            for n, snippet in hits]}

    def t_eksb_get(self, id: str = "") -> dict:
        n = self.w.get(str(id))
        if n is None:
            return {"found": False, "id": id,
                    "hint": "try eksb_search first; ids look like c-20260826-slug"}
        return {"found": True, "id": n.id, "title": n.title, "type": n.type,
                "aliases": n.aliases, "status": str(n.fm.get("status") or "active"),
                "sources": n.sources, "body": n.body.strip()}

    def t_eksb_provenance(self, id: str = "") -> dict:
        w = self.w
        n = w.get(str(id))
        if n is None:
            return {"found": False, "id": id}
        p = w.provenance(n)
        return {
            "found": True, "id": n.id, "title": n.title, "type": n.type,
            "status": str(n.fm.get("status") or "active"),
            "superseded_by": str(n.fm.get("superseded_by") or "").strip("[]"),
            "came_from": [{"id": s.id, "title": s.title,
                           "kind": str(s.fm.get("source_type") or ""),
                           "dated": str(s.fm.get("source_date") or "")}
                          for s in p["sources"]],
            "missing_sources": p["missing_sources"],
            "claims": [{"text": text, "asserted_as": tag,
                        "is_user_belief": tag == "user_position"}
                       for tag, text in p["claims"]],
            "points_at": [{"rel": r.get("rel"),
                           "target": t.title if t else str(r.get("target")).strip("[]"),
                           "resolved": t is not None}
                          for r, t in p["outgoing"]],
            "pointed_at_by": [{"rel": r.get("rel"), "from": o.title}
                              for o, r in p["incoming"]],
        }

    def t_eksb_attention(self) -> dict:
        a = self.w.attention()
        return {
            "open_questions": [n.title for n, _ in a["open_questions"]],
            "unconfirmed_suggestions": [{"note": n.title, "claim": c}
                                        for n, c in a["unendorsed"]][:MAX_RESULTS],
            "unverified_outside_claims": [{"note": n.title, "claim": c}
                                          for n, c in a["unverified"]][:MAX_RESULTS],
            "changed_positions": [{"was": n.title, "now": str(x).strip("[]")}
                                  for n, x in a["superseded"]],
            "in_review_queue": a["queue"],
            "problems": a["errors"][:MAX_RESULTS],
        }

    def t_eksb_workspace_status(self) -> dict:
        w = self.w
        counts = w.counts()
        errors, warnings, n = validate(w.root)
        return {
            "workspace": str(w.root), "name": w.name,
            "notes": counts["notes"], "relations": counts["relations"],
            "broken_references": counts["broken"],
            "valid": not errors, "errors": errors[:10], "warnings": len(warnings),
            "projects": ingest.levels(w),
            "levels_explained": {
                "1 registered": "the directory is known; nothing read",
                "2 indexed": "its text is here and searchable; NOT understood",
                "3 integrated": "durable knowledge exists, traced to that text",
            },
        }

    def t_eksb_ingest(self, path: str = "", name: str = "",
                      dry_run: bool = False) -> dict:
        w = self.w
        try:
            rep = ingest.ingest(w, Path(str(path)), name or None,
                                dry_run=bool(dry_run))
        except ws.WorkspaceError as e:
            reason, _, detail = str(e).partition(":")
            return {"ok": False, "reason": reason, "detail": detail}
        d = rep.as_dict()
        d["ok"] = True
        d["note"] = ("Indexed, not understood. Propose knowledge from these "
                     "sources with eksb_submit_candidate.")
        return d

    def t_eksb_submit_candidate(self, **cand) -> dict:
        outcome = candidates.submit(self.w, cand, asserted_by=self.client or "agent")
        d = outcome.as_dict()
        if outcome.action in ("CONFLICT", "REVIEW_REQUIRED"):
            d["next"] = ("Not written. Put this one question to the user in "
                         "plain language, then act on their answer.")
        elif outcome.action == "REJECTED":
            d["next"] = "Fix the candidate and submit again."
        elif outcome.applied:
            d["next"] = ("Written as a proposal. Claims stay "
                         "assistant_hypothesis until the user promotes them.")
        return d

    # -- protocol --------------------------------------------------------
    def call_tool(self, name: str, args: dict) -> dict:
        fn = getattr(self, "t_" + name, None)
        if fn is None:
            raise KeyError(name)
        if not isinstance(args, dict):
            args = {}
        if name == "eksb_submit_candidate":
            return fn(**args)
        allowed = fn.__code__.co_varnames[1:fn.__code__.co_argcount]
        return fn(**{k: v for k, v in args.items() if k in allowed})

    def handle(self, req: dict) -> dict | None:
        """One JSON-RPC message in, one response out (None for notifications)."""
        method, rid = req.get("method"), req.get("id")
        params = req.get("params") or {}

        if method == "initialize":
            asked = str(params.get("protocolVersion") or "")
            info = params.get("clientInfo") or {}
            self.client = str(info.get("name") or "agent")[:60]
            return _ok(rid, {
                "protocolVersion": asked if asked in KNOWN_PROTOCOLS else PROTOCOL,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "eksb", "version": __version__},
                "instructions": (
                    "This is the user's own knowledge workspace: decisions, "
                    "positions, sources and project history that outlive any "
                    "one chat.\n\n"
                    "Search it before asking the user to re-explain something, "
                    "and retrieve only what you need rather than loading whole "
                    "projects into context.\n\n"
                    "Check eksb_provenance before relying on a claim: a claim "
                    "marked assistant_hypothesis was a previous model's guess, "
                    "not the user's belief. You may never record a claim as "
                    "the user's own position — propose it, and let them "
                    "promote it.\n\n"
                    "When work produces something durable — a decision, a "
                    "reversal, a new constraint — submit it with "
                    "eksb_submit_candidate so the next session inherits it."),
            })

        if method in ("notifications/initialized", "initialized", "notifications/cancelled"):
            return None

        if method == "ping":
            return _ok(rid, {})

        if method == "tools/list":
            return _ok(rid, {"tools": TOOLS})

        if method == "tools/call":
            name = str(params.get("name") or "")
            try:
                result = self.call_tool(name, params.get("arguments") or {})
            except KeyError:
                return _err(rid, -32602, f"unknown tool: {name}")
            except ws.WorkspaceError as e:
                result = {"ok": False, "error": str(e)}
            except Exception as e:                       # never kill the session
                return _ok(rid, {"isError": True, "content": [
                    {"type": "text", "text": json.dumps(
                        {"error": f"{type(e).__name__}: {e}"})}]})
            return _ok(rid, {"content": [
                {"type": "text",
                 "text": json.dumps(result, ensure_ascii=False, indent=2)}]})

        if method in ("shutdown", "exit"):
            return _ok(rid, {})

        if rid is None:
            return None
        return _err(rid, -32601, f"method not found: {method}")


def _ok(rid, result):
    return {"jsonrpc": "2.0", "id": rid, "result": result}


def _err(rid, code, message):
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}}


def serve(root: Path, stdin=None, stdout=None) -> int:
    """Read newline-delimited JSON-RPC from stdin until it closes."""
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    server = Server(root)          # one per session: it remembers who connected
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except ValueError:
            _write(stdout, _err(None, -32700, "parse error"))
            continue
        for one in (req if isinstance(req, list) else [req]):
            if not isinstance(one, dict):
                continue
            response = server.handle(one)
            if response is not None:
                _write(stdout, response)
    return 0


def _write(stream, payload) -> None:
    stream.write(json.dumps(payload, ensure_ascii=False) + "\n")
    stream.flush()
