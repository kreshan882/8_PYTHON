"""Small Markdown helpers shared by the renderers."""

from __future__ import annotations

import re
from typing import List

from .models import JavaMember

_ACCESSOR = re.compile(r"^(get|set|is)[A-Z]\w*$")


def cell(s: object, n: int = 110) -> str:
    t = " ".join(str(s).split()).replace("|", "\\|")
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def code(s: object) -> str:
    return "`" + str(s).replace("`", "'") + "`"


def slug(title: str) -> str:
    return re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")


def table(header: List[str], rows: List[List[str]]) -> List[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return out


def is_trivial(m: JavaMember) -> bool:
    """Plain getter/setter/toString-style method that carries no knowledge."""
    if m.kind != "method" or m.annotations or m.doc:
        return False
    if m.name in ("toString", "hashCode", "equals"):
        return True
    return bool(_ACCESSOR.match(m.name)) and m.complexity <= 1 and len(m.calls) <= 1 and not m.events
