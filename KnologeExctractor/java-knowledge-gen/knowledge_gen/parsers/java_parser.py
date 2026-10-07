"""Regex/brace-matching based Java structure extractor (no external dependencies).

It does not build a full AST. It extracts what a human needs to understand a
code base quickly: package/imports, type declarations (class, interface, enum,
record, annotation) with annotations/extends/implements/javadoc, methods,
constructors and fields.
"""

from __future__ import annotations

import re
from bisect import bisect_right
from typing import List, Optional, Tuple

from ..models import Annotation, JavaFile, JavaMember, JavaType
from .common import Depth, LineIndex, mask_code, split_top_level, squash, truncate

_MODS = (
    r"(?:public|protected|private|static|final|abstract|synchronized|native|default|"
    r"strictfp|transient|volatile|sealed|non-sealed)"
)

PACKAGE_RE = re.compile(r"^\s*package\s+([\w.]+)\s*;", re.M)
IMPORT_RE = re.compile(r"^\s*import\s+(static\s+)?([\w.]+(?:\.\*)?)\s*;", re.M)
ANN_RE = re.compile(r"@(?!\s*interface\b)([A-Za-z_][\w.]*)")
TYPE_RE = re.compile(r"(?<![\w.@])(class|interface|enum|record)\s+([A-Za-z_]\w*)")
ANNDECL_RE = re.compile(r"@\s*interface\s+([A-Za-z_]\w*)")
TYPE_MODS_TAIL = re.compile(
    r"(?:\b(?:public|protected|private|abstract|static|final|sealed|non-sealed|strictfp)\s+)*$"
)
METHOD_RE = re.compile(
    r"(?P<mods>(?:%s\s+)*)(?P<tp><[^;{}()]*>\s+)?"
    r"(?P<ret>[A-Za-z_][\w.<>\[\],?& ]*?)\s+(?P<name>[A-Za-z_]\w*)\s*\(" % _MODS
)
FIELD_RE = re.compile(
    r"(?P<mods>(?:%s\s+)*)(?P<type>[A-Za-z_][\w.<>\[\],?& ]*?)\s+"
    r"(?P<name>[A-Za-z_]\w*)\s*(?P<end>=|;)" % _MODS
)
TAIL_RE = re.compile(r"\s*(?:throws\s+[\w.,\s<>]+?)?\s*(?:default\s+[^;{]+?)?\s*(\{|;)")
ENUM_CONST_RE = re.compile(r"^[A-Z][A-Z0-9_]*\s*(?:\(.*\))?\s*(?:\{.*\})?$", re.S)

_RET_BAD = {"return", "new", "throw", "else", "case", "assert", "yield", "package", "import", "goto"}
_NAME_BAD = {"if", "for", "while", "switch", "catch", "synchronized", "try", "return", "super",
             "this", "new", "do", "else"}
_MOD_WORDS = {"public", "protected", "private", "static", "final", "abstract", "synchronized",
              "native", "default", "strictfp", "transient", "volatile", "sealed", "non-sealed"}
_PROP_PATTERNS = (
    re.compile(r'@Value\(\s*"\$\{([^}:"]+)'),
    re.compile(r'getProperty\(\s*"([^"]+)"'),
    re.compile(r'@ConfigurationProperties\([^)]*?"([^"]+)"'),
)


# ------------------------------------------------------------- helpers
def _find_annotations(masked: str, text: str, dp: Depth) -> List[Annotation]:
    out: List[Annotation] = []
    n = len(masked)
    for m in ANN_RE.finditer(masked):
        end = m.end()
        args = ""
        j = end
        while j < n and masked[j] in " \t\r\n":
            j += 1
        if j < n and masked[j] == "(":
            close = dp.match.get(j, -1)
            if close != -1:
                args = squash(text[j + 1 : close])
                end = close + 1
        out.append(Annotation(m.group(1).split(".")[-1], args, m.start(), end))
    return out


class _AnnIndex:
    """Finds the annotations that sit directly in front of a declaration."""

    def __init__(self, anns: List[Annotation], masked: str) -> None:
        self.anns = sorted(anns, key=lambda a: a.end)
        self.ends = [a.end for a in self.anns]
        self.masked = masked

    def before(self, pos: int) -> Tuple[List[Annotation], int]:
        res: List[Annotation] = []
        cur = pos
        i = bisect_right(self.ends, cur) - 1
        while i >= 0:
            a = self.anns[i]
            if a.end > cur or self.masked[a.end:cur].strip():
                break
            res.append(a)
            cur = a.start
            i = bisect_right(self.ends, cur) - 1
        res.reverse()
        return res, cur


def javadoc_before(text: str, pos: int) -> str:
    """First paragraph of the Javadoc immediately preceding ``pos`` (if any)."""
    head = text[max(0, pos - 4000):pos].rstrip()
    if not head.endswith("*/"):
        return ""
    start = head.rfind("/*", 0, len(head) - 2)
    if start == -1 or not head.startswith("/**", start):
        return ""
    body = head[start + 3 : -2]
    parts: List[str] = []
    for raw in body.splitlines():
        line = re.sub(r"^\s*\*\s?", "", raw).strip()
        if line.startswith("@"):
            break
        if line:
            parts.append(line)
    doc = " ".join(parts)
    doc = re.sub(r"<[^>]+>", "", doc)
    doc = re.sub(r"\{@\w+\s+([^}]*)\}", r"\1", doc)
    return truncate(squash(doc), 220)


def _strip_leading_generics(s: str) -> str:
    s = s.lstrip()
    if not s.startswith("<"):
        return s
    depth = 0
    for i, ch in enumerate(s):
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth -= 1
            if depth == 0:
                return s[i + 1 :]
    return s


def _visibility(mods: List[str], owner_kind: str) -> str:
    for v in ("public", "protected", "private"):
        if v in mods:
            return v
    return "public" if owner_kind in ("interface", "annotation") else "package"


class _TypeInfo:
    def __init__(self, t: JavaType, start: int, body_start: int, body_end: int, body_depth: int):
        self.t = t
        self.start = start
        self.body_start = body_start
        self.body_end = body_end
        self.body_depth = body_depth
        self.outer: Optional["_TypeInfo"] = None


# ---------------------------------------------------------------- main
def parse_java(text: str, rel: str) -> JavaFile:
    masked = mask_code(text)
    n = len(masked)
    li = LineIndex(text)
    dp = Depth(masked)
    jf = JavaFile(rel=rel)

    m = PACKAGE_RE.search(masked)
    if m:
        jf.package = m.group(1)
    for m in IMPORT_RE.finditer(masked):
        (jf.static_imports if m.group(1) else jf.imports).append(m.group(2))

    ann_idx = _AnnIndex(_find_annotations(masked, text, dp), masked)

    # ---- locate type declarations -------------------------------------
    raw: List[Tuple[int, int, str, str]] = []
    for m in TYPE_RE.finditer(masked):
        kw, name = m.group(1), m.group(2)
        if kw == "record":
            k = m.end()
            while k < n and masked[k].isspace():
                k += 1
            if k >= n or masked[k] not in "(<":
                continue
        raw.append((m.start(), m.end(), kw, name))
    for m in ANNDECL_RE.finditer(masked):
        raw.append((m.start(), m.end(), "annotation", m.group(1)))
    raw.sort(key=lambda r: r[0])

    infos: List[_TypeInfo] = []
    for start, end, kw, name in raw:
        brace = masked.find("{", end)
        if brace == -1:
            continue
        semi = masked.find(";", end)
        if semi != -1 and semi < brace and kw != "record":
            continue
        body_end = dp.match.get(brace, n - 1)
        body_depth = dp.brace(brace + 1)

        hdr = masked[end:brace]
        components = ""
        if kw == "record":
            p = masked.find("(", end, brace)
            if p != -1 and p in dp.match:
                close = dp.match[p]
                components = squash(text[p + 1 : close])
                hdr = masked[close + 1 : brace]
        hdr = _strip_leading_generics(hdr)
        ext = re.search(r"\bextends\s+(.*?)(?=\bimplements\b|\bpermits\b|$)", hdr, re.S)
        imp = re.search(r"\bimplements\s+(.*?)(?=\bpermits\b|$)", hdr, re.S)
        extends = [squash(x) for x in split_top_level(ext.group(1))] if ext else []
        implements = [squash(x) for x in split_top_level(imp.group(1))] if imp else []

        prefix = masked[max(0, start - 200) : start]
        mm = TYPE_MODS_TAIL.search(prefix)
        mods_txt = mm.group(0) if mm else ""
        decl_pos = start - len(mods_txt)
        anns, cur = ann_idx.before(decl_pos)
        doc = javadoc_before(text, cur)

        t = JavaType(
            kind=kw, name=name, package=jf.package, rel=rel, line=li.line(start),
            modifiers=mods_txt.split(), annotations=anns, extends=extends,
            implements=implements, doc=doc, components=components,
        )
        if kw == "enum":
            seg_end = body_end
            for sm in re.finditer(";", masked[brace + 1 : body_end]):
                pos = brace + 1 + sm.start()
                if dp.brace(pos) == body_depth and dp.paren(pos) == 0:
                    seg_end = pos
                    break
            for part in split_top_level(masked[brace + 1 : seg_end]):
                cleaned = re.sub(r"@\w+(?:\([^)]*\))?\s*", "", part).strip()
                if cleaned and ENUM_CONST_RE.match(cleaned):
                    t.enum_constants.append(re.match(r"[A-Za-z_]\w*", cleaned).group(0))
        infos.append(_TypeInfo(t, start, brace, body_end, body_depth))

    def owner_of(pos: int) -> Optional[_TypeInfo]:
        best: Optional[_TypeInfo] = None
        for ti in infos:
            if ti.body_start < pos < ti.body_end and (best is None or ti.body_start > best.body_start):
                best = ti
        return best

    for ti in infos:
        ti.outer = owner_of(ti.start)
        chain: List[str] = []
        cur_ti: Optional[_TypeInfo] = ti
        while cur_ti is not None:
            chain.insert(0, cur_ti.t.name)
            cur_ti = cur_ti.outer
        ti.t.display = ".".join(chain)
        ti.t.qualified = (jf.package + "." if jf.package else "") + ti.t.display
        ti.t.outer = ti.outer.t.name if ti.outer else None

    # ---- methods -------------------------------------------------------
    for m in METHOD_RE.finditer(masked):
        pos = m.start()
        if dp.paren(pos) != 0:
            continue
        ti = owner_of(m.start("name"))
        if ti is None or dp.brace(pos) != ti.body_depth:
            continue
        ret = m.group("ret").strip()
        name = m.group("name")
        ret_tokens = ret.split()
        if name in _NAME_BAD or any(tok in _RET_BAD or tok in _MOD_WORDS for tok in ret_tokens):
            continue   # control flow, or a constructor (modifier mistaken for a return type)
        open_idx = m.end() - 1
        close = dp.match.get(open_idx, -1)
        if close == -1:
            continue
        tail = TAIL_RE.match(masked, close + 1)
        if not tail:
            continue
        mods = m.group("mods").split()
        if tail.group(1) == ";" and ti.t.kind in ("class", "enum", "record") \
                and not ({"abstract", "native"} & set(mods)):
            continue
        anns, cur = ann_idx.before(pos)
        params = squash(text[open_idx + 1 : close])
        params_short = re.sub(r"@\w+(?:\([^)]*\))?\s*", "", params)
        shown_mods = [x for x in mods if x in ("static", "abstract", "default", "final", "synchronized")]
        sig = " ".join(shown_mods + [ret, f"{name}({params_short})"])
        ti.t.members.append(JavaMember(
            kind="method", name=name, signature=truncate(squash(sig), 230),
            visibility=_visibility(mods, ti.t.kind), modifiers=mods, annotations=anns,
            line=li.line(pos), doc=javadoc_before(text, cur), type_name=ret,
        ))

    # ---- constructors ---------------------------------------------------
    for ti in infos:
        if ti.t.kind not in ("class", "enum", "record"):
            continue
        ctor_re = re.compile(r"(?<![\w.])(?P<mods>(?:%s\s+)*)%s\s*\(" % (_MODS, re.escape(ti.t.name)))
        for m in ctor_re.finditer(masked, ti.body_start, ti.body_end):
            pos = m.start()
            if dp.paren(pos) != 0 or dp.brace(pos) != ti.body_depth:
                continue
            if re.search(r"\bnew\s*$", masked[max(0, pos - 12):pos]):
                continue
            open_idx = m.end() - 1
            close = dp.match.get(open_idx, -1)
            if close == -1:
                continue
            tail = TAIL_RE.match(masked, close + 1)
            if not tail or tail.group(1) != "{":
                continue
            mods = m.group("mods").split()
            anns, cur = ann_idx.before(pos)
            params = re.sub(r"@\w+(?:\([^)]*\))?\s*", "", squash(text[open_idx + 1 : close]))
            ti.t.members.append(JavaMember(
                kind="constructor", name=ti.t.name,
                signature=truncate(f"{ti.t.name}({params})", 230),
                visibility=_visibility(mods, ti.t.kind), modifiers=mods, annotations=anns,
                line=li.line(pos), doc=javadoc_before(text, cur), type_name="",
            ))

    # ---- fields ---------------------------------------------------------
    for m in FIELD_RE.finditer(masked):
        pos = m.start()
        if dp.paren(pos) != 0:
            continue
        ti = owner_of(m.start("name"))
        if ti is None or dp.brace(pos) != ti.body_depth:
            continue
        ftype = m.group("type").strip()
        name = m.group("name")
        if any(tok in _RET_BAD for tok in ftype.split()) or name in _NAME_BAD:
            continue
        mods = m.group("mods").split()
        anns, cur = ann_idx.before(pos)
        ti.t.members.append(JavaMember(
            kind="field", name=name, signature=f"{ftype} {name}",
            visibility=_visibility(mods, ti.t.kind), modifiers=mods, annotations=anns,
            line=li.line(pos), doc=javadoc_before(text, cur), type_name=ftype,
        ))

    for ti in infos:
        ti.t.members.sort(key=lambda mem: mem.line)
        jf.types.append(ti.t)

    jf.idents = set(re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", masked))
    for pat in _PROP_PATTERNS:
        jf.prop_keys.update(pat.findall(text))
    return jf
