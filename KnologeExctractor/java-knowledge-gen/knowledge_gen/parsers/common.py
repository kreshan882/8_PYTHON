"""Helpers shared by the source parsers (masking, brace matching, text utils)."""

from __future__ import annotations

import re
from bisect import bisect_right
from typing import Dict, List

_JAVA_TOKEN = re.compile(
    r'//[^\n]*|/\*.*?\*/|"""(?:.|\n)*?"""|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'', re.S
)
_JS_TOKEN = re.compile(
    r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'|`(?:\\.|[^`\\])*`', re.S
)

SECRET_RE = re.compile(
    r"pass(?:word|wd|phrase)?|pwd|secret|token|api[_.\-]?key|credential|private[_.\-]?key|access[_.\-]?key",
    re.IGNORECASE,
)


def mask_code(text: str, js: bool = False) -> str:
    """Blank out comments and string contents while preserving every offset/newline.

    Comments become spaces; string literals keep their quotes but their content is
    replaced by ``_``. Structural regexes can then run on the result without being
    fooled by braces or keywords inside comments/strings, and positions still map
    1:1 onto the original text.
    """
    rx = _JS_TOKEN if js else _JAVA_TOKEN

    def repl(m: "re.Match[str]") -> str:
        s = m.group(0)
        if s.startswith("//") or s.startswith("/*"):
            return "".join(c if c == "\n" else " " for c in s)
        k = 3 if (not js and s.startswith('"""')) else 1
        if len(s) < 2 * k:
            return s
        mid = "".join("\n" if c == "\n" else "_" for c in s[k:-k])
        return s[:k] + mid + s[-k:]

    return rx.sub(repl, text)


class LineIndex:
    def __init__(self, text: str) -> None:
        self._nl = [m.start() for m in re.finditer("\n", text)]

    def line(self, pos: int) -> int:
        return bisect_right(self._nl, pos - 1) + 1


_BRACKETS = re.compile(r"[{}()]")


class Depth:
    """Brace / parenthesis nesting depth lookup plus open->close matching."""

    def __init__(self, masked: str) -> None:
        self._bpos: List[int] = []
        self._bval: List[int] = []
        self._ppos: List[int] = []
        self._pval: List[int] = []
        self.match: Dict[int, int] = {}
        d = pd = 0
        bstack: List[int] = []
        pstack: List[int] = []
        for m in _BRACKETS.finditer(masked):
            c = m.group()
            i = m.start()
            if c == "{":
                bstack.append(i)
                d += 1
                self._bpos.append(i)
                self._bval.append(d)
            elif c == "}":
                if bstack:
                    self.match[bstack.pop()] = i
                d = max(0, d - 1)
                self._bpos.append(i)
                self._bval.append(d)
            elif c == "(":
                pstack.append(i)
                pd += 1
                self._ppos.append(i)
                self._pval.append(pd)
            else:
                if pstack:
                    self.match[pstack.pop()] = i
                pd = max(0, pd - 1)
                self._ppos.append(i)
                self._pval.append(pd)

    def brace(self, pos: int) -> int:
        """Brace depth *before* character ``pos``."""
        i = bisect_right(self._bpos, pos - 1)
        return self._bval[i - 1] if i else 0

    def paren(self, pos: int) -> int:
        i = bisect_right(self._ppos, pos - 1)
        return self._pval[i - 1] if i else 0


def split_top_level(s: str, sep: str = ",") -> List[str]:
    parts: List[str] = []
    depth = 0
    cur: List[str] = []
    for ch in s:
        if ch in "<([{":
            depth += 1
        elif ch in ">)]}":
            depth = max(0, depth - 1)
        if ch == sep and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


def squash(s: str) -> str:
    return " ".join(s.split())


def truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def mask_value(key: str, value: str) -> str:
    """Hide secrets: whole value for secret-looking keys, credentials inside URLs."""
    if SECRET_RE.search(key or ""):
        return "***" if value else value
    value = re.sub(r"(://[^:/@\s]+:)[^@/\s]+@", r"\1***@", value)
    value = re.sub(r"(?i)\b(password|pwd|passwd)=[^&;\s]+", r"\1=***", value)
    return value
