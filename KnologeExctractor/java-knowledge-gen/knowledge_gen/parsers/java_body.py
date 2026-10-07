"""Method-body analysis: call sites and the events that matter for production diagnosis.

Everything works on the *masked* source (comments blanked, string contents replaced by
``_``) so offsets map 1:1 onto the original text, which is used to read literal values.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from ..models import Call, CodeEvent
from .common import Depth, LineIndex, mask_value, split_top_level, squash, truncate
from .xml_parser import _tables_from_sql

_LEVELS = {
    "trace": "DEBUG", "debug": "DEBUG", "fine": "DEBUG", "finer": "DEBUG", "finest": "DEBUG",
    "info": "INFO", "warn": "WARN", "warning": "WARN",
    "error": "ERROR", "fatal": "ERROR", "severe": "ERROR",
}

_CX_RE = re.compile(r"\b(?:if|for|while|case|catch)\b|&&|\|\||\s\?\s")
_LOG_RE = re.compile(
    r"(?<![\w$])(?P<lg>[A-Za-z_]\w*)\s*\.\s*"
    r"(?P<lvl>trace|debug|info|warn|error|fatal|severe|warning|fine|finer|finest)\s*\("
)
_PRINT_RE = re.compile(r"(?<![\w$])System\s*\.\s*(?P<ch>out|err)\s*\.\s*print(?:ln|f)?\s*\(")
_PST_RE = re.compile(r"\.\s*printStackTrace\s*\(\s*\)")
_THROW_RE = re.compile(r"\bthrow\s+(?:new\s+(?P<type>[A-Za-z_][\w.]*)\s*\(|(?P<var>[A-Za-z_]\w*)\s*;)")
_CATCH_RE = re.compile(r"\bcatch\s*\(\s*(?:final\s+)?(?P<types>[^)]*?)\s+(?P<var>\w+)\s*\)\s*\{")
_CALL_RE = re.compile(r"(?<![\w$])([A-Za-z_]\w*)\s*\(")
_HTTP_RE = re.compile(
    r"\bHttpStatus\s*\.\s*(?P<st>[A-Z_]+)|\bsendError\s*\(\s*(?P<code>\d{3})|"
    r"\bResponseEntity\s*\.\s*(?P<re>badRequest|notFound|unprocessableEntity)\s*\("
)
_LOCAL_RE = re.compile(
    r"(?<![\w.])(?P<type>[A-Z][\w.]*(?:<[^;(){}=]*?>)?(?:\[\])*)\s+(?P<name>[a-z_]\w*)\s*(?=[=;:,)])"
)
_VAR_NEW_RE = re.compile(r"\bvar\s+(?P<name>[a-z_]\w*)\s*=\s*new\s+(?P<type>[A-Z][\w.]*)")
_STR_TOK = re.compile(r'"""[_\n]*"""|"_*"')
_OPEN_BRACE = re.compile(r"\{")
_CONTROL = re.compile(r"(?:if|else|for|while|do|switch|try|catch|finally|synchronized)\b")
_EXC_ARG = re.compile(r"(?:e|ex|exc|exception|t|th|throwable|err|error|cause|ioe|sqle)\d*", re.I)

_CALL_KW = {"if", "for", "while", "switch", "catch", "synchronized", "return", "new", "throw", "super",
            "this", "else", "do", "try", "assert", "case", "instanceof"}
_OK_STATUS = ("OK", "CREATED", "ACCEPTED", "NO_CONTENT", "CONTINUE", "SWITCHING")

_SQL_START = re.compile(r"\s*(?:select|insert\s+into|update|delete\s+from|merge\s+into|call|with)\b", re.I)
_SQL_HINT = re.compile(r"\b(?:from|into|set|values|where|join|call)\b", re.I)
_URL_RE = re.compile(r"^(?:https?|ftp|sftp|ldaps?|smtp|amqp|redis|tcp|mongodb)://|^jdbc:", re.I)
_IP_RE = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?\b")
_PATH_RE = re.compile(r"^[A-Za-z]:[\\/]|^/(?:etc|var|opt|home|tmp|data|usr|mnt|srv|app|logs?)/")


def _unescape(s: str) -> str:
    return (s.replace('\\"', '"').replace("\\n", " ").replace("\\t", " ")
            .replace("\\r", " ").replace("\\\\", "\\"))


def _fmt_to_placeholders(s: str) -> str:
    s = re.sub(r"%(?:\d+\$)?[-#+ 0,(]*\d*(?:\.\d+)?[a-zA-Z%]",
               lambda m: "%" if m.group(0) == "%%" else "{}", s)
    return re.sub(r"\{\d+(?:,[^}]*)?\}", "{}", s)


def _split_offsets(masked: str, a: int, b: int, sep: str) -> List[Tuple[int, int]]:
    """Top-level split of masked[a:b] on ``sep`` -> list of (start, end) offsets."""
    parts: List[Tuple[int, int]] = []
    depth = 0
    start = a
    for i in range(a, b):
        c = masked[i]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == sep and depth == 0:
            parts.append((start, i))
            start = i + 1
    if masked[start:b].strip() or not parts:
        parts.append((start, b))
    return parts


def build_template(text: str, masked: str, a: int, b: int) -> Tuple[str, List[str], List[str]]:
    """Message expression text[a:b] -> (template with {placeholders}, literals, identifiers)."""
    tpl: List[str] = []
    lits: List[str] = []
    idents: List[str] = []
    for s, e in _split_offsets(masked, a, b, "+"):
        mp = masked[s:e].strip()
        op = text[s:e].strip()
        if not op:
            continue
        if len(mp) >= 2 and mp[0] == '"' and mp[-1] == '"' and mp.count('"') == 2:
            lit = _unescape(op[1:-1])
            lits.append(lit)
            tpl.append(lit)
            continue
        inner = re.findall(r'"((?:[^"\\]|\\.)*)"', op)
        fm = re.match(r'(?:String\s*\.\s*format|MessageFormat\s*\.\s*format|[\w.]*\bformat)\s*\(\s*"((?:[^"\\]|\\.)*)"', op)
        if fm:
            lits.append(fm.group(1))
            tpl.append(_fmt_to_placeholders(_unescape(fm.group(1))))
        elif re.search(r"\b(?:getMessage|getString|getText|getLocalizedMessage)\s*\(\s*\"", op) and inner:
            lits.append(inner[0])
            tpl.append("{msg:" + inner[0] + "}")
        elif re.fullmatch(r"[A-Za-z_][\w.]*", op):
            idents.append(op)
            tpl.append("{" + truncate(op, 30) + "}")
        elif re.fullmatch(r"[\w.]+\(\)", op):
            tpl.append("{" + op + "}")
        else:
            lits.extend(inner)
            tpl.append("{…}")
    return "".join(tpl), lits, idents


def literal_runs(text: str, masked: str, b0: int, b1: int, li: LineIndex) -> List[Tuple[str, int]]:
    """String literals in masked[b0:b1], with ``"a" + "b"`` runs merged into one value."""
    runs: List[List] = []
    cur: Optional[List] = None
    for m in _STR_TOK.finditer(masked, b0, b1 + 1):
        s, e = m.start(), m.end()
        raw = text[s + 3:e - 3] if m.group().startswith('"""') else text[s + 1:e - 1]
        if cur is not None and re.fullmatch(r"\s*\+\s*", masked[cur[1]:s]):
            cur[1] = e
            cur[2] += _unescape(raw)
        else:
            if cur is not None:
                runs.append(cur)
            cur = [s, e, _unescape(raw), s]
    if cur is not None:
        runs.append(cur)
    return [(truncate(squash(v), 400), li.line(first)) for _, _, v, first in runs if len(v.strip()) >= 3]


def analyze_body(text: str, masked: str, dp: Depth, li: LineIndex, b0: int, b1: int) -> Dict[str, object]:
    """Analyse a method body spanning masked[b0] == '{' .. masked[b1] == '}'."""
    body = masked[b0:b1 + 1]
    complexity = 1 + len(_CX_RE.findall(body))
    events: List[CodeEvent] = []

    # ---- enclosing blocks -------------------------------------------------
    def enclosing(pos: int) -> List[str]:
        blocks: List[str] = []
        for om in _OPEN_BRACE.finditer(masked, b0 + 1, pos):
            i = om.start()
            if dp.match.get(i, -1) > pos:
                start = max(masked.rfind(";", b0, i), masked.rfind("{", b0, i), masked.rfind("}", b0, i)) + 1
                hdr = squash(text[start:i])
                if hdr and _CONTROL.match(hdr):
                    blocks.append(hdr)
        return blocks

    def ctx_of(pos: int) -> Tuple[str, str]:
        blocks = enclosing(pos)
        catch_var = ""
        for h in blocks:
            cm = re.match(r"catch\s*\((?:final\s+)?.*?\s+(\w+)\s*\)", h)
            if cm:
                catch_var = cm.group(1)
        return " › ".join(truncate(h, 90) for h in blocks[-3:]), catch_var

    def args_of(open_idx: int, close: int) -> List[Tuple[int, int]]:
        return _split_offsets(masked, open_idx + 1, close, ",") if masked[open_idx + 1:close].strip() else []

    def message_event(kind: str, level: str, open_idx: int, close: int, pos: int) -> CodeEvent:
        ctx, catch_var = ctx_of(pos)
        ev = CodeEvent(kind=kind, level=level, line=li.line(pos), context=ctx)
        parts = args_of(open_idx, close)
        idx = next((i for i, (a, b) in enumerate(parts) if '"' in masked[a:b]), 0 if parts else -1)
        rest: List[str] = []
        if idx >= 0:
            ev.template, ev.literals, ev.idents = build_template(text, masked, *parts[idx])
            rest = [text[x:y].strip() for i, (x, y) in enumerate(parts) if i > idx]
        if kind == "log" and level in ("ERROR", "WARN") and catch_var:
            passed = any(r == catch_var or _EXC_ARG.fullmatch(r) for r in rest)
            ev.exc_logged = passed
            if not passed:
                ev.detail = "exception stack trace NOT logged (message only)"
        if kind == "throw":
            allargs = [text[x:y].strip() for x, y in parts]
            if catch_var and catch_var in allargs:
                ev.detail = "wraps caught exception"
        return ev

    # ---- log / print / throw / catch / http ----------------------------------
    for m in _LOG_RE.finditer(body):
        lg = m.group("lg")
        if "log" not in lg.lower():
            continue
        oi = b0 + m.end() - 1
        close = dp.match.get(oi, -1)
        if close != -1:
            events.append(message_event("log", _LEVELS[m.group("lvl").lower()], oi, close, b0 + m.start()))

    for m in _PRINT_RE.finditer(body):
        oi = b0 + m.end() - 1
        close = dp.match.get(oi, -1)
        if close != -1:
            ev = message_event("print", "stdout" if m.group("ch") == "out" else "stderr", oi, close, b0 + m.start())
            ev.detail = "console output, bypasses the logging framework"
            events.append(ev)
    for m in _PST_RE.finditer(body):
        pos = b0 + m.start()
        ctx, _ = ctx_of(pos)
        events.append(CodeEvent("print", "printStackTrace", "", li.line(pos), ctx,
                                "prints to stderr, often missing from application logs"))

    for m in _THROW_RE.finditer(body):
        pos = b0 + m.start()
        if m.group("type"):
            oi = b0 + m.end() - 1
            close = dp.match.get(oi, -1)
            if close == -1:
                continue
            events.append(message_event("throw", re.sub(r"<.*", "", m.group("type")), oi, close, pos))
        else:
            ctx, _ = ctx_of(pos)
            events.append(CodeEvent("throw", m.group("var"), "", li.line(pos), ctx, "rethrow"))

    for m in _CATCH_RE.finditer(body):
        bo = b0 + m.end() - 1
        bc = dp.match.get(bo, -1)
        if bc == -1:
            continue
        inner = masked[bo + 1:bc]
        types = squash(m.group("types"))
        has_throw = bool(re.search(r"\bthrow\b", inner))
        has_log = bool(_LOG_RE.search(inner) and any("log" in x.group("lg").lower() for x in _LOG_RE.finditer(inner))) \
            or bool(_PST_RE.search(inner)) or bool(_PRINT_RE.search(inner))
        if not inner.strip():
            flags = ["EMPTY catch - exception swallowed silently"]
        elif has_throw:
            flags = ["rethrown/wrapped"]
        elif has_log:
            flags = ["logged only - execution continues"]
        else:
            flags = ["swallowed - no log, no rethrow"]
        if re.search(r"(?:^|[|\s])(?:Exception|Throwable)(?:$|[|\s])", types):
            flags.append("broad catch")
        pos = b0 + m.start()
        ctx, _ = ctx_of(pos)
        events.append(CodeEvent("catch", types, "", li.line(pos), ctx, "; ".join(flags)))

    for m in _HTTP_RE.finditer(body):
        status = m.group("st") or m.group("code") or m.group("re")
        if status and status.startswith(_OK_STATUS):
            continue
        pos = b0 + m.start()
        ctx, _ = ctx_of(pos)
        events.append(CodeEvent("http", status or "", "", li.line(pos), ctx, "error response"))

    # ---- literals: SQL, hard-coded endpoints/paths -----------------------------
    literals = literal_runs(text, masked, b0, b1, li)
    for val, line in literals:
        if _SQL_START.match(val) and len(val) > 12 and _SQL_HINT.search(val):
            events.append(CodeEvent("sql", re.match(r"\s*(\w+)", val).group(1).upper(),
                                    truncate(val, 300), line, "", ", ".join(_tables_from_sql(val))))
        elif _URL_RE.match(val):
            events.append(CodeEvent("hardcoded", "url", mask_value("", truncate(val, 160)), line))
        elif _IP_RE.search(val) and len(val) < 60 and not re.search(r"[a-zA-Z]{4,}", val):
            events.append(CodeEvent("hardcoded", "ip", val, line))
        elif _PATH_RE.match(val):
            events.append(CodeEvent("hardcoded", "path", truncate(val, 160), line))

    # ---- locals ----------------------------------------------------------------
    locals_: Dict[str, str] = {}
    for m in _LOCAL_RE.finditer(body):
        locals_.setdefault(m.group("name"), squash(m.group("type")))
    for m in _VAR_NEW_RE.finditer(body):
        locals_.setdefault(m.group("name"), m.group("type"))

    # ---- call sites --------------------------------------------------------------
    calls: Dict[Tuple[str, str, str], Call] = {}
    for m in _CALL_RE.finditer(body):
        name = m.group(1)
        if name in _CALL_KW:
            continue
        s = m.start(1)
        before = body[max(0, s - 90):s]
        if re.search(r"\bnew\s+$", before):
            continue
        mm = re.search(r"([A-Za-z_]\w*|\))\s*\.\s*$", before)
        if mm:
            recv = "<chain>" if mm.group(1) == ")" else mm.group(1)
        elif before.rstrip().endswith("."):
            recv = "<chain>"
        else:
            recv = ""
        if recv and ("log" in recv.lower() or (recv in ("out", "err") and name.startswith("print"))):
            continue
        oi = b0 + m.end() - 1
        close = dp.match.get(oi, -1)
        arg0 = ""
        if close != -1:
            seg = masked[oi + 1:close]
            lead = len(seg) - len(seg.lstrip())
            if seg[lead:lead + 1] == '"':
                e = seg.find('"', lead + 1)
                if e != -1:
                    arg0 = _unescape(text[oi + 2 + lead:oi + 1 + e])[:120]
        key = (recv, name, arg0)
        if key not in calls:
            calls[key] = Call(recv, name, li.line(b0 + s), arg0)

    events.sort(key=lambda ev: ev.line)
    return {
        "complexity": complexity, "events": events, "calls": list(calls.values()),
        "locals": locals_, "literals": literals,
    }
