"""Lightweight JavaScript structure extractor (functions, classes, AJAX endpoints)."""

from __future__ import annotations

import re
from typing import Dict, List, Set, Tuple

from ..models import JsCall, JsFunction, JsInfo
from .common import LineIndex, mask_code, squash, truncate

_FUNC_PATTERNS: List[Tuple["re.Pattern[str]", str]] = [
    (re.compile(r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)"), "function"),
    (re.compile(r"\b(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s+)?function\s*\*?\s*[\w$]*\s*\(([^)]*)\)"),
     "function"),
    (re.compile(r"\b(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?"
                r"(?:\(([^)]*)\)|([A-Za-z_$][\w$]*))\s*=>"), "arrow"),
    (re.compile(r"(?m)^[ \t]*([A-Za-z_$][\w$]*)\s*:\s*(?:async\s+)?function\s*\*?\s*[\w$]*\s*\(([^)]*)\)"),
     "method"),
    (re.compile(r"(?m)^[ \t]*([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)+)\s*=\s*(?:async\s+)?"
                r"function\s*\*?\s*[\w$]*\s*\(([^)]*)\)"), "assigned"),
]
_CLASS_RE = re.compile(r"\bclass\s+([A-Za-z_$][\w$]*)(?:\s+extends\s+([\w$.]+))?")
_IMPORT_RE = re.compile(r"\bimport\s+(?:[^;'\"`]*?\s+from\s+)?(?P<q>['\"`])")
_REQUIRE_RE = re.compile(r"\brequire\s*\(\s*(?P<q>['\"`])")
_EXPORT_RE = re.compile(r"\bexport\s+(?:default\s+)?(?:async\s+)?(?:function\*?|class|const|let|var)\s+([A-Za-z_$][\w$]*)")

_VERB = {"get": "GET", "getjson": "GET", "post": "POST", "put": "PUT", "delete": "DELETE", "patch": "PATCH"}
_CALL_PATTERNS: List[Tuple["re.Pattern[str]", str]] = [
    (re.compile(r"\$\.(?P<v>get|post|getJSON|put|delete)\s*\(\s*(?P<q>['\"`])"), "verb"),
    (re.compile(r"\b(?:axios|\$http|this\.http|http)\.(?P<v>get|post|put|delete|patch)\s*\(\s*(?P<q>['\"`])"), "verb"),
    (re.compile(r"\bfetch\s*\(\s*(?P<q>['\"`])"), "fetch"),
    (re.compile(r"\burl\s*:\s*(?P<q>['\"`])"), "ajax"),
]
_FRAMEWORKS = [
    ("jQuery", re.compile(r"\$\(|\bjQuery\b")),
    ("AngularJS", re.compile(r"\bangular\.module\b")),
    ("React", re.compile(r"\bReact\b")),
    ("Vue", re.compile(r"\bVue\b")),
    ("ExtJS", re.compile(r"\bExt\.(?:onReady|define|create|application)\b")),
    ("axios", re.compile(r"\baxios\b")),
    ("Dojo", re.compile(r"\bdojo\.")),
]


def _string_after(masked: str, text: str, quote_idx: int) -> str:
    q = masked[quote_idx]
    end = masked.find(q, quote_idx + 1)
    return text[quote_idx + 1 : end] if end != -1 else ""


def _description(text: str) -> str:
    m = re.match(r"\s*(?:['\"]use strict['\"];?\s*)?/\*+(.*?)\*/", text, re.S)
    if m:
        lines = [re.sub(r"^\s*\*\s?", "", ln).strip() for ln in m.group(1).splitlines()]
        lines = [ln for ln in lines if ln and not ln.startswith("@")]
        return truncate(squash(" ".join(lines)), 200)
    lines = []
    for ln in text.splitlines()[:15]:
        s = ln.strip()
        if s.startswith("//"):
            lines.append(s.lstrip("/ ").strip())
        elif s and lines:
            break
        elif s:
            break
    return truncate(squash(" ".join(x for x in lines if x)), 200)


def _vendor_reason(text: str, rel: str) -> str:
    if rel.lower().endswith(".min.js"):
        return "minified"
    lines = text.count("\n") + 1
    if len(text) > 4000 and len(text) / lines > 400:
        return "minified (very long lines)"
    head = text[:600]
    m = re.search(r"/\*[!*]?\s*(?:@license\s*)?\*?\s*(jQuery|Bootstrap|AngularJS|Lodash|Underscore|Moment|"
                  r"Backbone|Select2|DataTables|Chart\.js|Popper)[^\n]*", head, re.I)
    if m:
        return squash(m.group(0).lstrip("/*! "))[:80]
    return ""


def parse_js(text: str, rel: str) -> JsInfo:
    info = JsInfo()
    reason = _vendor_reason(text, rel)
    if reason:
        info.vendor = True
        info.vendor_note = reason
        return info

    masked = mask_code(text, js=True)
    li = LineIndex(text)
    info.description = _description(text)

    seen: Set[Tuple[str, int]] = set()
    for pat, kind in _FUNC_PATTERNS:
        for m in pat.finditer(masked):
            name = m.group(1)
            params = m.group(2) if m.group(2) is not None else (m.group(3) if m.lastindex and m.lastindex >= 3 else "")
            line = li.line(m.start(1))
            if (name, line) in seen:
                continue
            seen.add((name, line))
            info.functions.append(JsFunction(name, squash(params or ""), line, kind))
    info.functions.sort(key=lambda f: f.line)

    for m in _CLASS_RE.finditer(masked):
        info.classes.append(m.group(1) + (f" extends {m.group(2)}" if m.group(2) else ""))
    for pat in (_IMPORT_RE, _REQUIRE_RE):
        for m in pat.finditer(masked):
            mod = _string_after(masked, text, m.end("q") - 1)
            if mod and mod not in info.imports:
                info.imports.append(mod)
    info.exports = [m.group(1) for m in _EXPORT_RE.finditer(masked)]

    for pat, mode in _CALL_PATTERNS:
        for m in pat.finditer(masked):
            url = _string_after(masked, text, m.end("q") - 1).strip()
            if not url or url.startswith(("#", "javascript:", "data:", "mailto:")):
                continue
            tail = text[m.end(): m.end() + 300]
            if mode == "verb":
                verb = _VERB.get(m.group("v").lower(), "GET")
            else:
                vm = re.search(r"""(?:type|method)\s*:\s*['"](\w+)['"]""", tail)
                verb = vm.group(1).upper() if vm else ("GET" if mode == "fetch" else "AJAX")
            call = JsCall(verb, url, li.line(m.start()))
            if not any(c.url == call.url and c.line == call.line for c in info.calls):
                info.calls.append(call)
    info.calls.sort(key=lambda c: c.line)

    info.frameworks = [name for name, rx in _FRAMEWORKS if rx.search(masked)]
    return info
