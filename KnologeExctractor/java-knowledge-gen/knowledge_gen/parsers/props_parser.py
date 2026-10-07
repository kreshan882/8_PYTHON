""".properties reader (continuations, escapes, \\uXXXX) with secret masking."""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterator, List, Tuple

from ..models import PropsInfo
from .common import mask_value

_ESC = re.compile(r"\\u([0-9a-fA-F]{4})|\\(.)", re.S)
_I18N_NAME = re.compile(r"(_[a-z]{2}(_[A-Z]{2})?\.properties$)|messages|i18n|bundle|labels|resources", re.I)


def _unescape(s: str) -> str:
    def fn(m: "re.Match[str]") -> str:
        if m.group(1):
            return chr(int(m.group(1), 16))
        c = m.group(2)
        return " " if c in "nt" else c

    return _ESC.sub(fn, s)


def _logical_lines(text: str) -> Iterator[str]:
    buf = ""
    for raw in text.splitlines():
        line = raw.lstrip()
        if not buf and (not line or line[0] in "#!"):
            continue
        m = re.search(r"(\\+)$", line)
        if m and len(m.group(1)) % 2 == 1:
            buf += line[:-1]
            continue
        yield buf + line
        buf = ""
    if buf:
        yield buf


def _split_kv(line: str) -> Tuple[str, str]:
    i, n = 0, len(line)
    key: List[str] = []
    while i < n:
        c = line[i]
        if c == "\\" and i + 1 < n:
            key.append(line[i:i + 2])
            i += 2
            continue
        if c in "=: \t":
            break
        key.append(c)
        i += 1
    while i < n and line[i] in " \t":
        i += 1
    if i < n and line[i] in "=:":
        i += 1
    while i < n and line[i] in " \t":
        i += 1
    return _unescape("".join(key)), _unescape(line[i:]).strip()


def parse_properties(text: str, rel: str) -> PropsInfo:
    info = PropsInfo()
    seen = Counter()
    for line in _logical_lines(text):
        key, value = _split_kv(line)
        if not key:
            continue
        seen[key] += 1
        info.entries.append((key, mask_value(key, value)))
    info.duplicates = [k for k, c in seen.items() if c > 1]
    groups = Counter(re.split(r"[._]", k, maxsplit=1)[0] for k, _ in info.entries)
    info.groups = groups.most_common(12)
    name = rel.rsplit("/", 1)[-1]
    info.is_i18n = bool(_I18N_NAME.search(name)) and len(info.entries) > 25
    return info
