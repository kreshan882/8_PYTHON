"""Markdown sections aimed at diagnosing production issues."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Dict, List, Tuple

from .analyzer import Knowledge
from .callgraph import _base
from .models import JavaMember, JavaType
from .render_util import cell, code, is_trivial, table
from .risks import Where

_MAX_DEPTH = 5
_MAX_FANOUT = 10
_FLOW_LINES = 45
_HOST_KEY = re.compile(r"(url|uri|host|endpoint|server|address|broker|queue|topic|bootstrap|jdbc|datasource|"
                       r"webservice|wsdl|ftp|smtp|redis)", re.I)
_TUNING_KEY = re.compile(r"(timeout|retry|retries|max|min|pool|size|limit|interval|cron|thread|ttl|expire|"
                         r"delay|batch|queue|cache|connection|period|schedule|rate)", re.I)


# ------------------------------------------------------------------ playbook
def playbook(k: Knowledge) -> List[str]:
    rows = [
        ["A stack trace", "Run `--investigate trace.txt`: it maps every frame to code, callers, SQL, config and recent changes. "
                          "Or look the class up in **Class catalog**."],
        ["A log line or an error text shown to users", "Search the exact words in **Message index**. For UI texts also check "
                                                       "the message bundles in **Configuration**."],
        ["A failing URL / API / screen", "**Entry points** → **Request flows** shows everything that runs for that request "
                                         "(services, SQL, external calls)."],
        ["Wrong, missing or duplicated data", "**Data layer** → *Database tables*: which entry points read or write the table, "
                                              "and the SQL used."],
        ["Works in one environment but not another", "**Configuration** → *Environment differences* lists keys that differ or "
                                                     "are missing per environment."],
        ["Started after a release", "**Recent changes**: files and commits of the last days, then open those classes in the catalog."],
        ["Intermittent, slow, or only under load", "**Risk hotspots**: shared mutable state, blocking calls, async jobs, "
                                                   "complex methods; **Integrations** for timeouts and external systems."],
        ["An external system is failing", "**Integrations**: who calls it, with which URL/queue, from which flow."],
        ["Errors that never show up in logs", "**Risk hotspots**: swallowed exceptions and error logs without stack trace."],
    ]
    L = ["Use this file as a map. Start from the evidence you have:", ""]
    L += table(["You have", "Go to"], [[a, b] for a, b in rows])
    L += ["", "**Root-cause checklist**", "",
          "1. Identify the exact failing code (Message index / stack trace) and the *condition* that leads to it (`When` column).",
          "2. Follow **Triggered by** to the entry point, then read its request flow to see which data and systems are involved.",
          "3. Check what the failing code depends on: SQL/tables, configuration keys, external calls.",
          "4. Compare configuration between environments and look at recent changes of the involved files.",
          "5. Check the risk list for the involved classes (swallowed exceptions, shared state, transaction pitfalls).",
          "", "_Everything here is derived statically from source: it shows what the code *can* do. "
          "Confirm with real logs/data before concluding._"]
    return L


# --------------------------------------------------------------------- flows
def _flags(k: Knowledge, key: str) -> str:
    pairs = k.cg.members_by_key.get(key, [])
    if not pairs:
        return ""
    t, m = pairs[0]
    flags: List[str] = []
    if any(a.name == "Transactional" for a in m.annotations + t.annotations):
        flags.append("TX")
    throws = []
    for ev in m.events:
        if ev.kind == "throw" and ev.detail != "rethrow" and ev.level not in throws:
            throws.append(ev.level)
    if throws:
        flags.append("throws " + ", ".join(throws[:3]))
    errs = sum(1 for ev in m.events if ev.kind == "log" and ev.level == "ERROR")
    if errs:
        flags.append(f"logs {errs} error")
    if any(ev.kind == "catch" and ("swallowed" in ev.detail or "EMPTY" in ev.detail) for ev in m.events):
        flags.append("SWALLOWS EXCEPTION")
    return "  " + " ".join(f"[{f}]" for f in flags) if flags else ""


def _node(k: Knowledge, key: str, depth: int, path: List[str], lines: List[str], budget: List[int]) -> None:
    cg = k.cg
    pad = "  " * depth
    if budget[0] <= 0:
        return
    budget[0] -= 1
    lines.append(f"{pad}- {code(cg.display(key))}{_flags(k, key)}")
    for s in cg.sql_by_method.get(key, [])[:3]:
        if budget[0] <= 0:
            return
        budget[0] -= 1
        tables = ", ".join(s.tables) or "?"
        lines.append(f"{pad}  - SQL **{s.op}** {code(tables)} — {code(cell(s.sql, 110))} _({s.source})_")
    seen_ext = set()
    for kind, typ, what, _ in cg.externals.get(key, []):
        if (kind, typ, what) in seen_ext or budget[0] <= 0:
            continue
        seen_ext.add((kind, typ, what))
        budget[0] -= 1
        lines.append(f"{pad}  - calls external **{kind}**: {code(typ + '.' + what)}")
    if depth >= _MAX_DEPTH:
        if cg.callees.get(key):
            lines.append(f"{pad}  - … (deeper calls omitted)")
        return
    shown = 0
    for callee, _ in cg.callees.get(key, []):
        pairs = cg.members_by_key.get(callee, [])
        if pairs and all(is_trivial(m) for _, m in pairs):
            continue
        if callee in path:
            lines.append(f"{pad}  - {code(cg.display(callee))} _(recursive)_")
            continue
        if shown >= _MAX_FANOUT:
            lines.append(f"{pad}  - … +{len(cg.callees[key]) - shown} more calls")
            break
        shown += 1
        _node(k, callee, depth + 1, path + [callee], lines, budget)


def flows(k: Knowledge) -> List[str]:
    cg = k.cg
    if cg is None or not cg.entry_labels:
        return []
    L = ["For each entry point: the methods it calls (interfaces resolved to implementations), SQL it runs and "
         "external systems it touches. `[TX]` = transactional, `[SWALLOWS EXCEPTION]` = an exception is silently ignored.",
         "Call resolution is heuristic: reflection, events and dynamic dispatch are not followed."]
    roots = sorted(((labels[0], key, labels) for key, labels in cg.entry_labels.items()
                    if key in cg.members_by_key), key=lambda x: x[0])
    shown = 0
    for _, key, labels in roots:
        if shown >= k.cfg.max_flows:
            L += ["", f"… +{len(roots) - shown} more entry points (raise `--max-flows`)"]
            break
        shown += 1
        t, m = cg.members_by_key[key][0]
        L += ["", f"#### {' · '.join(labels[:3])}", f"{code(t.rel + ':' + str(m.line))}"]
        lines: List[str] = []
        _node(k, key, 0, [key], lines, [_FLOW_LINES])
        L += lines
    return L


# -------------------------------------------------------------- integrations
def integrations(k: Knowledge) -> List[str]:
    cg = k.cg
    L: List[str] = []
    if cg is not None and cg.integrations:
        agg: Dict[Tuple[str, str], Dict[str, List[str]]] = defaultdict(lambda: {"where": [], "detail": []})
        for i in cg.integrations:
            slot = agg[(i.kind, i.type)]
            if i.where not in slot["where"]:
                slot["where"].append(i.where)
            if i.detail and i.detail not in slot["detail"]:
                slot["detail"].append(i.detail)
        rows = [[kind, code(typ), cell(", ".join(code(w) for w in v["where"][:6]) + (" …" if len(v["where"]) > 6 else ""), 160),
                 cell("; ".join(v["detail"][:4]), 160)]
                for (kind, typ), v in sorted(agg.items())]
        L += table(["Kind", "Type", "Used in", "Targets / calls"], rows)
    hosts = []
    for rel, p in k.props.items():
        if p.is_i18n:
            continue
        for key, val in p.entries:
            if _HOST_KEY.search(key) and val:
                users = sorted(k.prop_usage.get(key, []))
                hosts.append([code(key), cell(val, 80), code(rel.rsplit("/", 1)[-1]), cell(", ".join(users), 40)])
    if hosts:
        L += ["", "**Configured hosts / URLs / queues**", ""] + table(["Key", "Value", "File", "Read by"], hosts[:60])
    return L


# ---------------------------------------------------------------- exceptions
def _is_exception(k: Knowledge, t: JavaType, depth: int = 0) -> bool:
    for s in t.extends:
        name = _base(s).split(".")[-1]
        if name.endswith(("Exception", "Error", "Throwable")):
            return True
        sup = k.cg.resolve(s, t.rel)
        if sup is not None and sup is not t and depth < 5 and _is_exception(k, sup, depth + 1):
            return True
    return False


def errors(k: Knowledge) -> List[str]:
    L: List[str] = []
    rows = []
    for t in k.types:
        for m in t.members:
            for a in m.annotations:
                if a.name != "ExceptionHandler":
                    continue
                excs = re.findall(r"([A-Z]\w*)\.class", a.args) or ([_base(m.params[0][0])] if m.params else ["?"])
                status = next((x.args for x in m.annotations if x.name == "ResponseStatus"), "")
                if not status:
                    status = ", ".join(sorted({ev.level for ev in m.events if ev.kind == "http"}))
                rows.append([code(f"{t.display}.{m.name}()"), cell(", ".join(excs), 70), cell(status or "-", 50),
                             cell(m.doc, 80)])
    if rows:
        L += ["**Global exception handlers** (what the caller receives for each exception type)", ""]
        L += table(["Handler", "Handles", "HTTP status", "Notes"], rows)

    thrown: Dict[str, List[str]] = defaultdict(list)
    for s in k.messages:
        if s.kind == "THROW":
            thrown[s.level].append(f"{s.cls}.{s.method}:{s.line}")
    ex_rows = []
    for t in k.types:
        if not _is_exception(k, t):
            continue
        rs = next((a for a in t.annotations if a.name == "ResponseStatus"), None)
        sites = thrown.get(t.name, [])
        ex_rows.append([code(t.display), cell(", ".join(t.extends), 40),
                        cell(", ".join(code(x) for x in sites[:3]) + (f" … +{len(sites) - 3}" if len(sites) > 3 else "") or "-", 120),
                        cell(rs.args if rs else "", 40)])
    if ex_rows:
        L += ["", "**Custom exception types**", ""]
        L += table(["Exception", "Extends", "Thrown at", "@ResponseStatus"], ex_rows)
    return L


# ------------------------------------------------------------ message index
def messages(k: Knowledge) -> List[str]:
    sites = k.messages
    if not sites:
        return []
    counts = defaultdict(int)
    for s in sites:
        counts[(s.kind, s.level if s.kind == "LOG" else "")] += 1
    summary = ", ".join(f"{n} {kind}{' ' + lvl if lvl else ''}" for (kind, lvl), n in sorted(counts.items()))
    L = [f"{len(sites)} messages found ({summary}). `{{…}}` marks a value filled in at run time. "
         "Search for a few exact words from your log line; **When** is the condition under which it fires and "
         "**Triggered by** the entry points that can reach it.", ""]
    rows = []
    for s in sites[: k.cfg.max_messages]:
        notes = []
        if s.detail:
            notes.append(s.detail)
        if s.resolved:
            notes.append(f"text: {s.resolved}")
        label = s.level if s.kind == "LOG" else f"{s.kind} {s.level}"
        rows.append([cell(label, 34), cell(s.template or "(dynamic)", 90),
                     code(f"{s.cls}.{s.method}:{s.line}"), cell(s.context, 90),
                     cell("; ".join(s.entries), 70), cell("; ".join(notes), 110)])
    L += table(["Level", "Message", "Where", "When", "Triggered by", "Notes"], rows)
    if len(sites) > k.cfg.max_messages:
        L.append(f"\n… +{len(sites) - k.cfg.max_messages} more (raise `--max-messages`)")
    return L


# --------------------------------------------------------------------- risks
def _where_table(items: List[Where], text_header: str = "Detail", cap: int = 30) -> List[str]:
    if not items:
        return []
    rows = [[code(w.owner), code(f"{w.rel}:{w.line}"), cell(w.text, 130)] for w in items[:cap]]
    L = table(["Where", "File", text_header], rows)
    if len(items) > cap:
        L.append(f"\n… +{len(items) - cap} more")
    return L


def risks(k: Knowledge) -> List[str]:
    r = k.risks
    if r is None:
        return []
    L: List[str] = ["Patterns that frequently explain production incidents. These are *leads to check*, not proven defects."]

    def block(title: str, why: str, body: List[str]) -> None:
        if body:
            L.extend(["", f"#### {title}", f"_{why}_", ""] + body)

    block("Swallowed / ignored exceptions", "A failure here leaves no trace and the flow continues with wrong or missing data.",
          _where_table(r.swallowed, "Catch block"))
    block("Error logs without the stack trace", "The log shows a message only, so the failing line cannot be found in the logs.",
          _where_table(r.missing_trace, "Log message"))
    block("Shared mutable state", "Singleton beans and statics are shared by all requests: a classic cause of intermittent, "
                                  "load-dependent wrong results.", _where_table(r.shared_state))
    block("Spring proxy pitfalls", "Annotations such as @Transactional/@Async only work when called through the Spring proxy.",
          _where_table(r.proxy_pitfalls))
    if r.complex_methods:
        rows = [[code(w.owner), code(f"{w.rel}:{w.line}"), str(cx), str(loc)] for cx, loc, w in r.complex_methods]
        block("Most complex methods", "Many branches = many ways to fail; review these first when logic is suspected.",
              table(["Method", "File", "Complexity", "Lines"], rows))
    if r.long_methods:
        rows = [[code(w.owner), code(f"{w.rel}:{w.line}"), str(loc), str(cx)] for loc, cx, w in r.long_methods]
        block("Longest methods", "Large methods hide side effects.", table(["Method", "File", "Lines", "Complexity"], rows))
    if r.hardcoded:
        items = [Where(w.owner, w.rel, w.line, f"{kind}: {w.text}") for kind, w in r.hardcoded]
        block("Hard-coded URLs, IPs and paths", "These do not change with configuration, so they break when an environment differs.",
              _where_table(items))
    block("Console output (System.out / printStackTrace)", "Often missing from application logs, so evidence can be lost.",
          _where_table(r.prints))
    block("Blocking calls", "Blocks a request thread; under load this exhausts the pool.", _where_table(r.blocking))
    block("Asynchronous work, schedules and thread pools", "Runs outside the request: check timing, concurrency and failures that "
                                                          "nobody sees.", _where_table(r.async_jobs))
    block("Transaction boundaries", "Defines what is rolled back together; missing/incorrect settings cause partial updates.",
          _where_table(r.transactional))
    block("TODO / FIXME / HACK comments", "Known gaps left by the developers.", _where_table(r.todos, "Comment"))
    if r.broad_catches:
        L += ["", f"_{r.broad_catches} `catch (Exception/Throwable)` blocks exist; they can mask the real error type._"]
    return L if len(L) > 1 else []


# ------------------------------------------------------------ recent changes
def recent_changes(k: Knowledge) -> List[str]:
    g = k.git
    if g is None or not g.commits:
        return []
    L = [f"Git history of the last {g.days} days ({len(g.commits)} commits). Issues often follow recent changes: "
         "open the most recently changed classes first.", ""]
    files = sorted(g.files.items(), key=lambda kv: (kv[1].last_date, kv[1].commits), reverse=True)[:25]
    rows = [[code(rel), str(f.commits), f.last_date, cell(f.last_author, 24), cell(f.last_subject, 80), f.last_hash]
            for rel, f in files]
    L += ["**Most recently changed files**", ""] + table(["File", "Commits", "Last change", "Author", "Subject", "Commit"], rows)
    crow = [[c.hash, c.date, cell(c.author, 24), cell(c.subject, 90), str(len(c.files))] for c in g.commits[:25]]
    L += ["", "**Latest commits**", ""] + table(["Commit", "Date", "Author", "Subject", "Files"], crow)
    return L


# ----------------------------------------------- configuration: ops + env diff
def ops_settings(k: Knowledge) -> List[str]:
    rows = []
    for rel, p in k.props.items():
        if p.is_i18n:
            continue
        for key, val in p.entries:
            if _TUNING_KEY.search(key) and val:
                users = sorted(k.prop_usage.get(key, []))
                rows.append([code(key), cell(val, 60), code(rel.rsplit("/", 1)[-1]), cell(", ".join(users), 40)])
    if not rows:
        return []
    L = ["**Operational settings** (timeouts, pools, limits, schedules): wrong values here cause slowness and "
         "timeouts under load.", ""]
    L += table(["Key", "Value", "File", "Read by"], rows[:80])
    if len(rows) > 80:
        L.append(f"\n… +{len(rows) - 80} more")
    return L


def env_diff(k: Knowledge) -> List[str]:
    L: List[str] = []
    for base, envs in sorted(k.env_groups.items()):
        names = sorted(envs, key=lambda e: (e != "default", e))
        data = {e: dict(k.props[envs[e]].entries) for e in names}
        prints = {e: k.props[envs[e]].fingerprints for e in names}
        keys = sorted(set().union(*[set(d) for d in data.values()]))
        rows = []
        same = 0
        for key in keys:
            vals = []
            fps = {e: prints[e].get(key) for e in names}
            present = [e for e in names if key in data[e]]
            differs = len({fps[e] for e in present}) > 1
            if len(present) == len(names) and not differs:
                same += 1
                continue
            for e in names:
                if key not in data[e]:
                    vals.append("— missing")
                else:
                    v = data[e][key]
                    vals.append(cell(v + (" (differs)" if differs and v == "***" else ""), 38))
            rows.append([code(key)] + vals)
        L += ["", f"**{base}**: {', '.join(names)}", ""]
        if rows:
            L += table(["Key"] + names, rows[:60])
            if len(rows) > 60:
                L.append(f"\n… +{len(rows) - 60} more differing keys")
        L.append(f"\n{same} keys are identical in all variants.")
    if L:
        L = ["**Environment differences**: keys whose value differs, or that exist in only some environments. "
             "(Secrets are never shown; `***` marks a masked value.)"] + L
    return L
