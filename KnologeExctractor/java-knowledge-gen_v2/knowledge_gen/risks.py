"""Code patterns that commonly sit behind production incidents."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Tuple

from .callgraph import _base, mkey
from .models import JavaMember, JavaType

if TYPE_CHECKING:  # pragma: no cover
    from .analyzer import Knowledge

_SINGLETON = {"Service", "Component", "Controller", "RestController", "Repository", "Configuration",
              "Stateless", "Singleton"}
_DI = {"Autowired", "Resource", "Inject", "Value", "PersistenceContext", "Mock", "InjectMocks"}
_NOT_THREAD_SAFE = {"SimpleDateFormat", "DateFormat", "NumberFormat", "DecimalFormat", "Calendar",
                    "HashMap", "ArrayList", "HashSet", "LinkedList", "TreeMap", "StringBuilder",
                    "LinkedHashMap", "Random", "Matcher"}
_PROXY_ANNS = {"Transactional", "Async", "Cacheable", "CacheEvict", "CachePut", "Retryable", "PreAuthorize"}


@dataclass
class Where:
    owner: str          # Class.method()
    rel: str
    line: int
    text: str = ""


@dataclass
class Risks:
    complex_methods: List[Tuple[int, int, Where]] = field(default_factory=list)   # complexity, loc
    long_methods: List[Tuple[int, int, Where]] = field(default_factory=list)
    swallowed: List[Where] = field(default_factory=list)
    broad_catches: int = 0
    missing_trace: List[Where] = field(default_factory=list)
    prints: List[Where] = field(default_factory=list)
    hardcoded: List[Tuple[str, Where]] = field(default_factory=list)
    todos: List[Where] = field(default_factory=list)
    shared_state: List[Where] = field(default_factory=list)
    proxy_pitfalls: List[Where] = field(default_factory=list)
    transactional: List[Where] = field(default_factory=list)
    async_jobs: List[Where] = field(default_factory=list)
    blocking: List[Where] = field(default_factory=list)


def owner_at(t_list: List[JavaType], line: int) -> str:
    """Class.method() containing ``line`` in a file's types."""
    best = ""
    best_span = 10 ** 9
    for t in t_list:
        for m in t.members:
            if m.kind in ("method", "constructor") and m.line <= line <= max(m.end_line, m.line):
                span = m.end_line - m.line
                if span < best_span:
                    best, best_span = f"{t.display}.{m.name}()", span
        if not best and t.line <= line <= max(t.end_line, t.line):
            best = t.display
    return best


def collect_risks(k: "Knowledge") -> Risks:
    r = Risks()
    for t in k.types:
        is_test = bool(re.search(r"(^|/)src/test/|(^|/)tests?/", t.rel))
        anns = {a.name for a in t.annotations}
        singleton = bool(anns & _SINGLETON)
        class_tx = next((a for a in t.annotations if a.name == "Transactional"), None)
        if class_tx is not None:
            r.transactional.append(Where(t.display + " (class)", t.rel, t.line, class_tx.args or "default settings"))
        own_methods = {m.name: m for m in t.members if m.kind == "method"}

        for m in t.members:
            if m.kind == "field":
                _field_risks(r, t, m, singleton, is_test)
                continue
            who = f"{t.display}.{'<init>' if m.kind == 'constructor' else m.name}()"
            where = Where(who, t.rel, m.line)
            if is_test:
                continue
            if m.complexity >= 10:
                r.complex_methods.append((m.complexity, m.loc, where))
            if m.loc >= 80:
                r.long_methods.append((m.loc, m.complexity, where))
            for a in m.annotations:
                if a.name == "Transactional":
                    r.transactional.append(Where(who, t.rel, m.line, a.args or "default settings"))
                if a.name in ("Async", "Scheduled"):
                    r.async_jobs.append(Where(who, t.rel, m.line, f"@{a.name} {a.args}".strip()))
                if a.name in _PROXY_ANNS and "private" in m.modifiers:
                    r.proxy_pitfalls.append(Where(who, t.rel, m.line,
                                                  f"@{a.name} on a private method is ignored by Spring proxies"))
            for ev in m.events:
                w = Where(who, t.rel, ev.line, ev.context)
                if ev.kind == "catch":
                    if "swallowed" in ev.detail or "EMPTY" in ev.detail:
                        w.text = f"catch ({ev.level}) - {ev.detail}"
                        r.swallowed.append(w)
                    if "broad catch" in ev.detail:
                        r.broad_catches += 1
                elif ev.kind == "log" and not ev.exc_logged:
                    w.text = ev.template
                    r.missing_trace.append(w)
                elif ev.kind == "print":
                    w.text = f"{ev.level}: {ev.template}".strip(": ")
                    r.prints.append(w)
                elif ev.kind == "hardcoded":
                    w.text = ev.template
                    r.hardcoded.append((ev.level, w))
            for c in m.calls:
                if c.recv == "Thread" and c.name == "sleep":
                    r.blocking.append(Where(who, t.rel, c.line, "Thread.sleep() blocks the request thread"))
                if c.recv == "Executors" and c.name.startswith("new"):
                    r.async_jobs.append(Where(who, t.rel, c.line, f"Executors.{c.name}() - creates a thread pool"))
            # Spring proxy self-invocation: a @Transactional method called via `this`
            if not class_tx and not any(a.name == "Transactional" for a in m.annotations):
                for c in m.calls:
                    if c.recv in ("", "this") and c.name in own_methods:
                        callee = own_methods[c.name]
                        txa = next((a for a in callee.annotations if a.name in _PROXY_ANNS), None)
                        if txa is not None and callee is not m:
                            r.proxy_pitfalls.append(Where(
                                who, t.rel, c.line,
                                f"calls @{txa.name} method {c.name}() on the same class - the proxy is bypassed, "
                                f"so @{txa.name} does not apply"))

    for rel, jf in k.java.items():
        for line, text in jf.todos:
            r.todos.append(Where(owner_at(jf.types, line) or rel, rel, line, text))

    r.complex_methods.sort(key=lambda x: -x[0])
    r.long_methods.sort(key=lambda x: -x[0])
    r.complex_methods = r.complex_methods[:15]
    r.long_methods = r.long_methods[:10]
    return r


def _field_risks(r: Risks, t: JavaType, m: JavaMember, singleton: bool, is_test: bool) -> None:
    if is_test or m.name == "serialVersionUID":
        return
    mods = set(m.modifiers)
    base = _base(m.type_name).split(".")[-1]
    if base in ("Logger", "Log", "Marker"):
        return
    where = Where(f"{t.display}.{m.name}", t.rel, m.line)
    if "static" in mods and "final" not in mods:
        where.text = f"static mutable field `{m.type_name} {m.name}` - shared by every request/thread"
        r.shared_state.append(where)
    elif "static" in mods and base in _NOT_THREAD_SAFE:
        where.text = f"static `{base}` is not thread-safe `{m.name}`"
        r.shared_state.append(where)
    elif singleton and "static" not in mods and "final" not in mods \
            and not ({a.name for a in m.annotations} & _DI):
        where.text = f"mutable instance field `{m.type_name} {m.name}` in a singleton bean - shared across requests"
        r.shared_state.append(where)
    elif singleton and "static" not in mods and base in _NOT_THREAD_SAFE \
            and not ({a.name for a in m.annotations} & _DI):
        where.text = f"`{base}` field `{m.name}` in a singleton bean is not thread-safe"
        r.shared_state.append(where)
