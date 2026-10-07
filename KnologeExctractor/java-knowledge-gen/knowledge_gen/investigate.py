"""Investigation mode: turn a stack trace / log excerpt / search words into a root-cause worksheet."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from .callgraph import mkey
from .messages import match_text
from .models import JavaMember, JavaType
from .render_util import cell, code, table
from .risks import owner_at

if TYPE_CHECKING:  # pragma: no cover
    from .analyzer import Knowledge

_FRAME = re.compile(r"^\s*at\s+(?:[\w.$-]+/)*([\w$.<>]+)\.([\w$<>]+)\((?:([\w$-]+\.(?:java|kt|groovy)):(\d+)|[^)]*)\)")
_HEADER = re.compile(r"(?:(Caused by|Suppressed):\s*)?((?:[a-zA-Z_][\w$]*\.)*[A-Z][\w$]*(?:Exception|Error|Throwable|Failure|Fault))"
                     r"(?::\s*(.*))?\s*$")
_MORE = re.compile(r"^\s*\.\.\.\s*(\d+)\s+(?:more|common frames omitted)")
_LIB_PREFIX = ("java.", "javax.", "jakarta.", "jdk.", "sun.", "com.sun.", "org.springframework.", "org.apache.",
               "org.hibernate.", "org.eclipse.", "io.netty.", "reactor.", "com.zaxxer.", "org.mybatis.",
               "org.junit.", "com.fasterxml.", "org.aspectj.", "net.sf.cglib.", "com.mysql.", "oracle.", "org.postgresql.",
               "org.xnio.", "io.undertow.", "ch.qos.", "org.slf4j.", "kotlin.", "scala.", "groovy.")

# Exception type (simple name) -> (meaning, what to check)
HINTS: List[Tuple[str, str, str]] = [
    ("NullPointerException", "A value was null when the code used it.",
     "Find which expression is null (see the helpful message / source line). Typical causes: missing row/record, "
     "optional field not sent by the client, bean or config value not injected, a failed upstream call returning null."),
    ("SQLSyntaxErrorException|BadSqlGrammarException|SQLGrammarException", "The database rejected the SQL text.",
     "Compare the SQL with the real schema: missing/renamed column or table, a database migration not applied in this environment."),
    ("DuplicateKeyException|SQLIntegrityConstraintViolationException|ConstraintViolationException|DataIntegrityViolationException",
     "A database constraint (unique / not null / foreign key) was violated.",
     "Look at the constraint named in the message and at the data being written; check for double submits or retries."),
    ("DeadlockLoserDataAccessException|CannotAcquireLockException|LockTimeoutException|PessimisticLockingFailureException|OptimisticLockingFailureException|StaleObjectStateException",
     "Concurrent updates collided in the database.",
     "Find the other transactions touching the same rows (tables below), look at transaction length and update order."),
    ("CannotGetJdbcConnectionException|SQLTransientConnectionException|PoolExhaustedException|JDBCConnectionException",
     "No database connection could be obtained.",
     "Connection pool exhausted (leaks, slow queries, long transactions) or the database is unreachable - check pool settings below."),
    ("SocketTimeoutException|ReadTimeoutException|ConnectTimeoutException|HttpTimeoutException|TimeoutException|ResourceAccessException",
     "A call to another system did not answer in time.",
     "Identify the remote system (Integrations below); check its health and the configured timeouts; look for retries that multiply load."),
    ("ConnectException|UnknownHostException|NoRouteToHostException|ConnectionRefused|SSLHandshakeException|SSLException",
     "The remote host could not be reached or trusted.",
     "Wrong URL/host for this environment, DNS/firewall, or expired/untrusted certificate."),
    ("OutOfMemoryError", "The JVM ran out of memory.",
     "Look for unbounded caches/collections, loading large result sets or files fully in memory (risk list), then take a heap dump."),
    ("StackOverflowError", "Endless or very deep recursion.", "Look for a method calling itself indirectly (toString/equals/JSON cycles between entities)."),
    ("ClassCastException", "An object was treated as the wrong type.", "Check generics/raw types, JSON/map deserialisation and class-loader duplicates."),
    ("NumberFormatException|DateTimeParseException|ParseException|IllegalArgumentException", "Input text could not be converted or a precondition failed.",
     "Find the offending input value in the log; check client format, locale and default values."),
    ("IndexOutOfBoundsException|ArrayIndexOutOfBoundsException|NoSuchElementException", "A list/array/optional was accessed without the expected content.",
     "Empty result where at least one row/element was assumed."),
    ("ConcurrentModificationException", "A collection was modified while being iterated.",
     "Shared mutable collection used by several threads (see shared-state risks)."),
    ("NoSuchMethodError|NoClassDefFoundError|ClassNotFoundException|AbstractMethodError|LinkageError|NoSuchBeanDefinitionException|BeanCreationException|UnsatisfiedDependencyException",
     "Classes/beans do not match what the code expects.",
     "Deployment problem: wrong or duplicate library versions, missing bean definition or property for this environment."),
    ("AccessDeniedException|AuthenticationException|UnauthorizedException|ForbiddenException", "The caller is not authenticated or lacks rights.",
     "Check role/permission configuration and the security column of the endpoint."),
    ("FileNotFoundException|NoSuchFileException|AccessDeniedException|IOException", "File or network I/O failed.",
     "Check path, permissions, disk space and the file/FTP integrations below."),
    ("HttpMessageNotReadableException|JsonParseException|JsonMappingException|MismatchedInputException|UnrecognizedPropertyException|HttpMediaTypeNotSupportedException",
     "The request/response body could not be parsed.", "Compare the payload sent by the client with the DTO fields."),
    ("TransactionSystemException|UnexpectedRollbackException|IllegalTransactionStateException", "A transaction was rolled back or misused.",
     "A nested call marked the transaction rollback-only, or @Transactional is bypassed (see proxy risks)."),
    ("RejectedExecutionException", "A thread pool refused work.", "Pool and queue sizes are too small for the load; check async jobs."),
    ("InterruptedException", "A thread was interrupted while waiting.", "Shutdown or timeout cancelled the work."),
]
_NPE_INVOKE = re.compile(r'Cannot (?:invoke|read|load|store|assign|read the array length of|throw|enter synchronized block using)[^"]*"([^"]+)"?')
_NPE_BECAUSE = re.compile(r'because (?:the return value of )?"([^"]+)" is null')


@dataclass
class Frame:
    cls: str
    method: str
    file: str
    line: int
    raw: str
    project: Optional[JavaType] = None
    member: Optional[JavaMember] = None


@dataclass
class Chain:
    exc: str
    message: str
    kind: str                   # "" | Caused by | Suppressed
    frames: List[Frame] = field(default_factory=list)
    omitted: int = 0


# ------------------------------------------------------------------ parsing
def parse_trace(text: str) -> List[Chain]:
    chains: List[Chain] = []
    cur: Optional[Chain] = None
    for raw in text.splitlines():
        fm = _FRAME.match(raw)
        if fm:
            if cur is None:
                cur = Chain("(unknown exception)", "", "")
                chains.append(cur)
            cur.frames.append(Frame(fm.group(1), fm.group(2), fm.group(3) or "", int(fm.group(4) or 0), raw.strip()))
            continue
        mm = _MORE.match(raw)
        if mm and cur is not None:
            cur.omitted = int(mm.group(1))
            continue
        hm = _HEADER.search(raw)
        if hm and not raw.lstrip().startswith("at "):
            # a header either follows a trace (Caused by) or starts one; plain text lines mentioning an
            # exception name without a package are accepted too.
            if hm.group(1) or "." in hm.group(2) or raw.strip().startswith(hm.group(2)) or cur is None or cur.frames:
                cur = Chain(hm.group(2), (hm.group(3) or "").strip(), hm.group(1) or "")
                chains.append(cur)
    return [c for c in chains if c.frames or c.exc != "(unknown exception)"]


def _clean_class(name: str) -> str:
    name = re.split(r"\$\$|\$\$Lambda|\$Lambda", name)[0]
    return name


def _map_frames(k: "Knowledge", chain: Chain) -> None:
    cg = k.cg
    for fr in chain.frames:
        q = _clean_class(fr.cls)
        t = cg.type_by_q.get(q.replace("$", "."))
        probe = q
        while t is None and "$" in probe:                       # inner/anonymous class -> outer class
            probe = probe.rsplit("$", 1)[0]
            t = cg.type_by_q.get(probe.replace("$", "."))
        if t is None and fr.file:                               # fall back to the file name
            stem = fr.file.rsplit(".", 1)[0]
            cands = [x for x in k.types if x.name == stem and x.outer is None]
            if len(cands) == 1:
                t = cands[0]
        if t is None:
            continue
        fr.project = t
        name = fr.method
        lam = re.match(r"lambda\$([\w]+)\$\d+", name)
        if lam:
            name = lam.group(1)
        ms = [m for m in t.members if m.kind in ("method", "constructor")
              and (m.name == name or (name == "<init>" and m.kind == "constructor"))]
        # nested/anonymous types hold their own members: search inner types too
        if not ms:
            for inner in k.types:
                if inner.outer == t.qualified:
                    ms += [m for m in inner.members if m.kind == "method" and m.name == name]
        if fr.line:
            exact = [m for m in ms if m.line <= fr.line <= max(m.end_line, m.line)]
            if exact:
                ms = exact
            else:                                               # line is inside a different member (lambda / init block)
                span = [m for m in t.members if m.kind in ("method", "constructor") and m.line <= fr.line <= max(m.end_line, m.line)]
                ms = span or ms
        fr.member = ms[0] if ms else None


def _is_lib(cls: str) -> bool:
    return cls.startswith(_LIB_PREFIX)


# ------------------------------------------------------------------ helpers
def _source_lines(k: "Knowledge", rel: str) -> List[str]:
    for f in k.files:
        if f.rel == rel:
            return f.text.splitlines()
    return []


def _snippet(k: "Knowledge", rel: str, line: int, radius: int = 3) -> List[str]:
    src = _source_lines(k, rel)
    if not src or not line:
        return []
    lo, hi = max(1, line - radius), min(len(src), line + radius)
    out = ["```java"]
    for n in range(lo, hi + 1):
        out.append(f"{'>>' if n == line else '  '} {n:>4} | {src[n - 1].rstrip()[:160]}")
    out.append("```")
    return out


def _hint(exc: str) -> Optional[Tuple[str, str]]:
    simple = exc.rsplit(".", 1)[-1]
    for pat, meaning, check in HINTS:
        if re.fullmatch(pat, simple):
            return meaning, check
    for pat, meaning, check in HINTS:                           # subclass naming convention (FooTimeoutException)
        if any(simple.endswith(p) for p in pat.split("|")):
            return meaning, check
    return None


def _npe_help(message: str) -> List[str]:
    out = []
    a = _NPE_INVOKE.search(message)
    b = _NPE_BECAUSE.search(message)
    if b:
        target = b.group(1)
        if target.startswith("<local"):
            out.append(f"The null value is a local variable ({code(target)}; compile without -g hides the name). "
                       "Check what the code assigned to it just before.")
        elif target.endswith("()") or "(" in target:
            out.append(f"The call {code(target)} returned **null** - check why it can return null (no data found, error path).")
        elif target.startswith("this."):
            out.append(f"The field {code(target)} is **null** - probably an injected bean or config value that was not set.")
        else:
            out.append(f"{code(target)} is **null**.")
    if a:
        out.append(f"The code was trying to use {code(a.group(1))} on it.")
    return out


def _config_for(k: "Knowledge", t: JavaType) -> List[Tuple[str, str, str]]:
    rows = []
    for key, users in k.key_usage.items():
        for rel, owner, line in users:
            if rel == t.rel:
                rows.append((key, owner, f"L{line}"))
    for key, names in k.prop_usage.items():
        if t.name in names and not any(r[0] == key for r in rows):
            rows.append((key, t.display, ""))
    out = []
    for key, owner, line in sorted(set(rows))[:12]:
        vals = k.props_flat.get(key)
        val = cell(vals[0][1], 40) if vals else "(not defined in scanned files)"
        out.append((key, val, f"{owner} {line}".strip()))
    return out


def _git_for(k: "Knowledge", rel: str) -> str:
    g = k.git.files.get(rel) if k.git else None
    if not g or not g.last_date:
        return ""
    return f"{g.last_date} by {g.last_author}: {cell(g.last_subject, 80)} ({g.last_hash}, {g.commits} commit(s) in {k.git.days} days)"


def _risks_for(k: "Knowledge", t: JavaType, m: Optional[JavaMember]) -> List[str]:
    r = k.risks
    if r is None:
        return []
    prefix = t.display + "."
    own = f"{t.display}.{m.name}()" if m else None
    out = []
    for label, items in (("swallowed exception", r.swallowed), ("error logged without stack trace", r.missing_trace),
                         ("shared mutable state", r.shared_state), ("proxy pitfall", r.proxy_pitfalls),
                         ("blocking call", r.blocking), ("hard-coded value", [w for _, w in r.hardcoded])):
        for w in items:
            if w.owner.startswith(prefix) and (own is None or w.owner == own or label in ("shared mutable state",)):
                out.append(f"{label} at L{w.line}: {cell(w.text, 100)}")
    return out[:8]


def _method_report(k: "Knowledge", t: JavaType, m: Optional[JavaMember], line: int, role: str) -> List[str]:
    cg = k.cg
    L: List[str] = [f"**{role}: {code(t.display + ('.' + m.name + '()' if m else ''))}** — {code(t.rel)}" + (f" line {line}" if line else "")]
    git = _git_for(k, t.rel)
    if git:
        L.append(f"- Last changed: {git}")
    if m is not None:
        key = mkey(t, m.name)
        sn = _snippet(k, t.rel, line or m.line)
        if sn:
            L += ["", *sn, ""]
        conds = [e for e in m.events if e.kind in ("throw", "log") and abs(e.line - line) <= 6 and line]
        for e in conds:
            L.append(f"- Nearby {e.kind} at L{e.line}: {code(cell(e.template, 90))}" + (f" when {cell(e.context, 70)}" if e.context else ""))
        callers = sorted({cg.display(c) for c, _ in cg.callers.get(key, [])})
        if callers:
            L.append("- Called by: " + ", ".join(code(c) for c in callers[:8]) + (" …" if len(callers) > 8 else ""))
        entries = cg.entries_of(key, limit=5)
        if entries:
            L.append("- Triggered by: " + "; ".join(code(e) for e in entries))
            for e in entries[:3]:
                http = re.match(r"(?:GET|POST|PUT|DELETE|PATCH|ANY)\s+(\S+)", e)
                if http:
                    js = [f"{rel}:{ln}" for rel, _, url, ln, _m in k.js_calls if http.group(1).rstrip("/") in url or url.rstrip("/").endswith(http.group(1).rstrip("/"))]
                    if js:
                        L.append(f"  - UI/JS calling {code(e)}: " + ", ".join(code(x) for x in js[:4]))
        tabs = cg.tables_reached(key)
        if tabs:
            L.append("- Tables touched below this method: " + ", ".join(f"{code(tb)} ({op})" for tb, op in sorted(tabs.items())))
        ext = cg.externals.get(key, [])
        if ext:
            L.append("- External calls: " + ", ".join(code(f"{x[0]}.{x[1]}") for x in ext[:6]))
        flag = _risks_for(k, t, m)
        for f in flag:
            L.append(f"- ⚠ {f}")
    else:
        sn = _snippet(k, t.rel, line)
        if sn:
            L += ["", *sn, ""]
    conf = _config_for(k, t)
    if conf:
        L += ["- Configuration read by this class:"]
        L += [f"  - {code(key)} = {code(val)} ({where})" for key, val, where in conf[:8]]
    return L


# ------------------------------------------------------------------ main entry
def investigate(k: "Knowledge", text: str, searches: List[str]) -> str:
    L: List[str] = ["# Investigation worksheet", "",
                    f"> Generated {k.generated_at} from static analysis of `{k.cfg.root.resolve().name}`. "
                    "It lists what the code *can* do for the evidence given - confirm with real logs and data.", ""]
    chains = parse_trace(text) if text.strip() else []
    for c in chains:
        _map_frames(k, c)

    # ---- summary
    summary: List[str] = []
    if chains:
        root = chains[-1]
        summary.append(f"Exception chain: " + " → ".join(code(c.exc.rsplit('.', 1)[-1]) for c in chains))
        top = next((f for c in reversed(chains) for f in c.frames if f.project), None)
        summary.append(f"Root exception: {code(root.exc)}" + (f" — {cell(root.message, 160)}" if root.message else ""))
        if top:
            summary.append(f"First project code on the root-cause side: {code(top.cls.rsplit('.', 1)[-1] + '.' + top.method + '()')} "
                           f"({top.file}:{top.line})")
        else:
            summary.append("No frame belongs to the scanned project - the failure is inside a library or the stack trace is cut.")
    if summary:
        L += ["## Summary", ""] + [f"- {s}" for s in summary] + [""]

    # ---- per chain
    n = 0
    reported: set = set()
    for ci, c in enumerate(chains, 1):
        n += 1
        title = f"{c.kind + ': ' if c.kind else ''}{c.exc}"
        L += [f"## {n}. {code(title)}", ""]
        if c.message:
            L += [f"Message: {code(cell(c.message, 300))}", ""]
        hint = _hint(c.exc)
        if hint:
            L += [f"**Meaning:** {hint[0]}", "", f"**Check:** {hint[1]}", ""]
        if c.exc.endswith("NullPointerException") and c.message:
            L += [f"- {x}" for x in _npe_help(c.message)] + [""]
        simple = c.exc.rsplit(".", 1)[-1]
        thrown = [s for s in k.messages if s.kind == "THROW" and s.level.rsplit(".", 1)[-1] == simple]
        if thrown:
            L += [f"This exception type is thrown by the project at {len(thrown)} place(s):", ""]
            L += table(["Where", "Message", "When"], [[code(f"{s.cls}.{s.method}():{s.line}"), cell(s.template or s.resolved, 70),
                                                         cell(s.context, 60)] for s in thrown[:8]]) + [""]
        proj = [f for f in c.frames if f.project and "$$" not in f.cls]
        if c.frames:
            rows = []
            shown_lib = 0
            for f in c.frames[:60]:
                if f.project and "$$" in f.cls:
                    rows.append(["proxy", cell(f"{f.cls}.{f.method}", 80), "(Spring/CGLIB proxy - calls the class above)"])
                elif f.project:
                    rows.append(["**project**", code(f"{f.cls}.{f.method}"), f"{f.file}:{f.line}"])
                elif shown_lib < 4 or _is_lib(f.cls) is False:
                    rows.append(["library" if _is_lib(f.cls) else "other", cell(f"{f.cls}.{f.method}", 80), f"{f.file}:{f.line}" if f.line else ""])
                    shown_lib += 1
            L += table(["Origin", "Frame", "Location"], rows)
            if len(c.frames) > 60:
                L.append(f"\n… +{len(c.frames) - 60} more frames")
            L.append("")
        for idx, f in enumerate(proj[:3]):
            role = "Failing code" if idx == 0 else "Called from"
            ident = (f.project.rel, f.member.name if f.member else "", f.line if idx == 0 else 0)
            seen_key = (f.project.rel, f.member.name if f.member else "", f.line)
            if seen_key in reported:
                L += [f"**{role}: {code(f.project.display + '.' + f.method + '()')}** — details above.", ""]
                continue
            reported.add(seen_key)
            L += _method_report(k, f.project, f.member, f.line, role) + [""]
        if not proj and c.frames:
            L += ["_No project frame in this part of the trace._", ""]

    # ---- log lines
    log_lines = []
    if text.strip():
        for raw in text.splitlines():
            s = raw.strip()
            if len(s) < 15 or _FRAME.match(raw) or _MORE.match(raw):
                continue
            s = re.sub(r"^\d{4}-\d\d-\d\d[ T][\d:.,]+\s*(?:\w+\s+)?(?:\[[^\]]*\]\s*)*", "", s)
            s = re.sub(r"^(?:ERROR|WARN|INFO|DEBUG|FATAL|SEVERE)\s+(?:\d+\s+)?(?:---\s+)?(?:\[[^\]]*\]\s*)*(?:[\w.$]+\s*:\s+)?", "", s)
            if s and s not in log_lines:
                log_lines.append(s)
    msg_rows: List[List[str]] = []
    seen_sites = set()
    for line in log_lines[:40]:
        for score, how, site in match_text(k, line, limit=3):
            sid = (site.rel, site.line)
            if sid in seen_sites:
                continue
            seen_sites.add(sid)
            msg_rows.append([cell(line, 70), how, code(f"{site.cls}.{site.method}():{site.line}"),
                             cell(site.template or site.resolved, 70), cell(site.context, 50),
                             cell("; ".join(site.entries), 50)])
    for term in searches:
        for score, how, site in match_text(k, term, limit=5):
            sid = (site.rel, site.line)
            if sid in seen_sites:
                continue
            seen_sites.add(sid)
            msg_rows.append([cell(term, 70), how, code(f"{site.cls}.{site.method}():{site.line}"),
                             cell(site.template or site.resolved, 70), cell(site.context, 50),
                             cell("; ".join(site.entries), 50)])
    if msg_rows:
        L += ["## Log / message matches", "",
              "Messages in the code that can produce the given text (`exact` = template matches, `similar` = most words match).", ""]
        L += table(["Evidence", "Match", "Code", "Message template", "Only when", "Triggered by"], msg_rows[:40]) + [""]

    # ---- free-text search
    for term in searches:
        L += _search(k, term)

    if not chains and not msg_rows and not searches:
        L += ["_No stack trace, log text or search term was recognised in the input._", ""]
    elif not chains and not msg_rows and searches and len(L) < 8:
        L += ["_Nothing found._", ""]

    if k.git and k.git.commits:
        involved = {f.project.rel for c in chains for f in c.frames if f.project}
        recent = [c for c in k.git.commits if involved & set(c.files)]
        if recent:
            L += ["## Recent commits touching the involved files", ""]
            L += table(["Commit", "Date", "Author", "Subject"],
                       [[c.hash, c.date, cell(c.author, 24), cell(c.subject, 90)] for c in recent[:10]]) + [""]

    L += ["## Suggested next checks", ""]
    steps = ["Confirm the failing line with the live code version (the source shown is from the scanned tree).",
             "Find the input that triggered it in the application log around the same time (request id / user / order number).",
             "Check the *Triggered by* flow in knowledgeFile.md → *Request flows* for the data and systems involved.",
             "Compare configuration of this environment with a working one (knowledgeFile.md → *Environment differences*).",
             "If recent commits touch the failing class, compare behaviour before/after that release."]
    L += [f"{i}. {s}" for i, s in enumerate(steps, 1)]
    return "\n".join(L).rstrip() + "\n"


def _search(k: "Knowledge", term: str) -> List[str]:
    term_l = term.lower()
    hits: List[List[str]] = []
    for f in k.files:
        if not f.text or f.ext not in (".java", ".js", ".xml", ".properties"):
            continue
        jf = k.java.get(f.rel)
        for i, line in enumerate(f.text.splitlines(), 1):
            if term_l in line.lower():
                where = owner_at(jf.types, i) if jf else ""
                hits.append([code(f"{f.rel}:{i}"), code(where) if where else "", cell(line.strip(), 120)])
                if len(hits) >= 25:
                    break
        if len(hits) >= 25:
            break
    L = [f"## Search: {code(term)}", ""]
    if hits:
        L += table(["Location", "Inside", "Line"], hits) + [""]
        if len(hits) >= 25:
            L += ["_Only the first 25 hits are shown._", ""]
    else:
        L += ["_No occurrence in the scanned files._", ""]
    return L
