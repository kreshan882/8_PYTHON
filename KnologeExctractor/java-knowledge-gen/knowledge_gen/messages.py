"""Index of log / exception / error-response messages and matching of production text against it."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Dict, List, Optional, Pattern, Tuple

from .callgraph import mkey
from .models import MessageSite

if TYPE_CHECKING:  # pragma: no cover
    from .analyzer import Knowledge

_PLACEHOLDER = re.compile(r"\{[^{}]*\}")
_WORD = re.compile(r"[A-Za-z]{4,}")


def build_messages(k: "Knowledge") -> List[MessageSite]:
    cg = k.cg
    sites: List[MessageSite] = []
    for t in k.types:
        for m in t.members:
            if m.kind not in ("method", "constructor"):
                continue
            key = mkey(t, m.name)
            name = "<init>" if m.kind == "constructor" else m.name
            for ev in m.events:
                if ev.kind == "log":
                    if ev.level == "DEBUG" and not k.cfg.include_debug_logs:
                        continue
                    kind = "LOG"
                elif ev.kind == "throw":
                    if ev.detail == "rethrow":
                        continue
                    kind = "THROW"
                elif ev.kind == "http":
                    kind = "HTTP"
                else:
                    continue
                site = MessageSite(
                    kind=kind, level=ev.level, template=ev.template, rel=t.rel, cls=t.display, method=name,
                    line=ev.line, context=ev.context, detail=ev.detail, exc_logged=ev.exc_logged, key=key,
                )
                site.entries = cg.entries_of(key, limit=3)
                site.resolved = _resolve_text(k, ev.literals, ev.idents)
                sites.append(site)
    sites.sort(key=lambda s: (s.rel, s.line))
    return sites


def _resolve_text(k: "Knowledge", literals: List[str], idents: List[str]) -> str:
    """Text behind message-bundle keys or constants used in the call arguments."""
    for lit in literals:
        if lit in k.props_flat:
            return f"{lit} = {k.props_flat[lit][0][1]}"
    for ident in idents:
        value = k.consts.get(ident) or k.consts.get(ident.rsplit(".", 1)[-1])
        if value is None:
            continue
        if value in k.props_flat:
            return f"{ident} = {value} = {k.props_flat[value][0][1]}"
        return f"{ident} = {value}"
    return ""


def template_regex(template: str) -> Optional[Pattern[str]]:
    """Regex that matches a rendered message built from ``template`` (None if too generic)."""
    parts = _PLACEHOLDER.split(template)
    literal_len = sum(len(p.strip()) for p in parts)
    if literal_len < 8:
        return None
    pieces = []
    for p in parts:
        esc = re.escape(p)
        esc = re.sub(r"(?:\\ )+", r"\\s+", esc)
        pieces.append(esc)
    try:
        return re.compile(".*?".join(pieces), re.IGNORECASE | re.DOTALL)
    except re.error:
        return None


def _literal_len(template: str) -> int:
    return sum(len(p.strip()) for p in _PLACEHOLDER.split(template))


def match_text(k: "Knowledge", text: str, limit: int = 5) -> List[Tuple[int, str, MessageSite]]:
    """Find message sites whose template could have produced ``text`` (one log line or phrase)."""
    text = " ".join(text.split())
    hits: List[Tuple[int, str, MessageSite]] = []
    words = set(w.lower() for w in _WORD.findall(text))
    for site in k.messages:
        if not site.template:
            continue
        rx = k.regex_cache.get(site.template, False)
        if rx is False:
            rx = template_regex(site.template)
            k.regex_cache[site.template] = rx
        if rx is not None and rx.search(text):
            hits.append((1000 + _literal_len(site.template), "exact", site))
            continue
        lit_words = set(w.lower() for w in _WORD.findall(_PLACEHOLDER.sub(" ", site.template)))
        if len(lit_words) >= 3 and words:
            overlap = len(lit_words & words) / len(lit_words)
            if overlap >= 0.7:
                hits.append((int(overlap * 100), "similar", site))
    hits.sort(key=lambda h: -h[0])
    return hits[:limit]
