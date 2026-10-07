"""Turn a Knowledge object into the final knowledgeFile.md text."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Callable, Dict, List, Tuple

from .analyzer import (LAYER_CONTROLLER, LAYER_MODEL, LAYER_TEST, Endpoint, Knowledge, layer_of)
from .models import Annotation, JavaMember, JavaType

_HIDDEN_ANNS = {"Override", "SuppressWarnings", "SuppressFBWarnings", "SafeVarargs", "FunctionalInterface"}
_DI_ANNS = {"Autowired", "Resource", "Inject", "Value"}
# Types the framework instantiates/wires itself, so "no Java reference" does not mean unused.
_FRAMEWORK_WIRED = {"Service", "Component", "Repository", "Configuration", "Mapper", "Entity", "Controller",
                    "RestController", "ControllerAdvice", "RestControllerAdvice", "SpringBootApplication",
                    "Aspect", "WebFilter", "WebListener", "WebServlet", "Stateless", "Stateful", "Path",
                    "ConfigurationProperties"}
_ACCESSOR = re.compile(r"^(get|set|is)[A-Z]\w*$")


# ----------------------------------------------------------- small helpers
def _cell(s: object, n: int = 110) -> str:
    t = " ".join(str(s).split()).replace("|", "\\|")
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def _code(s: object) -> str:
    return "`" + str(s).replace("`", "'") + "`"


def _slug(title: str) -> str:
    return re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")


def _ann_text(a: Annotation, n: int = 70) -> str:
    args = f"({a.args if len(a.args) <= n else a.args[: n - 1] + '…'})" if a.args else ""
    return _code(f"@{a.name}{args}")


def _table(header: List[str], rows: List[List[str]]) -> List[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return out


def _is_trivial(m: JavaMember) -> bool:
    if m.kind != "method" or m.annotations or m.doc:
        return False
    if m.name in ("toString", "hashCode", "equals"):
        return True
    return bool(_ACCESSOR.match(m.name)) and m.signature.count(",") == 0


# ---------------------------------------------------------------- sections
def _overview(k: Knowledge) -> List[str]:
    L: List[str] = []
    by_ext: Counter = Counter()
    lines_ext: Counter = Counter()
    for f in k.files:
        by_ext[f.ext] += 1
        lines_ext[f.ext] += f.lines
    L += _table(["Extension", "Files", "Lines"],
                [[_code(e), str(by_ext[e]), f"{lines_ext[e]:,}"] for e in sorted(by_ext)]
                + [["**Total**", f"**{sum(by_ext.values())}**", f"**{sum(lines_ext.values()):,}**"]])
    kinds = Counter(t.kind for t in k.types)
    top_pkgs = Counter(t.package or "(default)" for t in k.types if t.outer is None)
    L += ["", f"- Java types: **{len(k.types)}** ("
          + ", ".join(f"{v} {kk}" for kk, v in kinds.most_common()) + f") in **{len(top_pkgs)}** packages"]
    if k.cfg.title:
        L.append(f"- Project: {k.cfg.title}")
    L += ["", "### Packages", ""]
    rows = []
    for pkg, cnt in sorted(top_pkgs.items())[:80]:
        names = sorted(t.name for t in k.types if t.outer is None and (t.package or "(default)") == pkg)
        rows.append([_code(pkg), str(cnt), _cell(", ".join(names[:8]) + (" …" if len(names) > 8 else ""), 120)])
    L += _table(["Package", "Types", "Classes"], rows)
    if len(top_pkgs) > 80:
        L.append(f"\n… +{len(top_pkgs) - 80} more packages")
    return L


def _tech(k: Knowledge) -> List[str]:
    L: List[str] = []
    if k.tech:
        L += _table(["Technology (from imports)", "Files using it"], [[t, str(n)] for t, n in k.tech])
    poms = [(rel, i) for rel, i in k.xml.items() if i.kind == "maven-pom"]
    for rel, info in poms:
        L += ["", f"### Build: {_code(rel)}", f"{info.summary}"]
        for title, lines in info.sections.items():
            L += ["", f"**{title}**"] + [f"- {x}" for x in lines]
    fw = Counter(f for j in k.js.values() for f in j.frameworks)
    if fw:
        L += ["", "**Front-end libraries/frameworks detected in JS:** " + ", ".join(sorted(fw))]
    return L


def _layers(k: Knowledge) -> List[str]:
    rows = []
    for layer, ts in sorted(k.layers.items(), key=lambda kv: -len(kv[1])):
        names = sorted({t.display for t in ts})
        rows.append([layer, str(len(ts)), _cell(", ".join(names[:12]) + (" …" if len(names) > 12 else ""), 160)])
    return _table(["Layer", "Types", "Examples"], rows) if rows else []


def _entry(k: Knowledge) -> List[str]:
    L: List[str] = []
    if k.endpoints:
        L += ["### HTTP endpoints", ""]
        rows = [[e.http, _code(e.path), _code(e.handler), _code(e.rel + (f":{e.line}" if e.line else ""))]
                for e in k.endpoints[:400]]
        L += _table(["Method", "Path", "Handler", "File"], rows)
        if len(k.endpoints) > 400:
            L.append(f"\n… +{len(k.endpoints) - 400} more endpoints")
    if k.entrypoints:
        L += ["", "### Other entry points", ""]
        L += _table(["Kind", "Where", "File"], [[kind, _code(what), _code(rel)] for kind, what, rel in k.entrypoints])
    return L


def _data(k: Knowledge) -> List[str]:
    L: List[str] = []
    mappers = [(rel, i) for rel, i in k.xml.items() if i.kind == "mybatis-mapper"]
    for rel, info in mappers:
        ns = info.extra["namespace"]
        L += ["", f"### MyBatis mapper {_code(ns or rel)}", f"- File: {_code(rel)}"]
        if ns and ns in {t.qualified for t in k.types}:
            L.append(f"- Java interface: {_code(ns.rsplit('.', 1)[-1])}")
        rm = info.extra["result_maps"]
        if rm:
            L.append("- Result maps: " + ", ".join(f"{_code(i)}→{_code(t)}" for i, t in rm[:10]))
        stm = info.extra["statements"]
        if stm:
            rows = [[_code(s["id"]), s["tag"].upper(), _cell(", ".join(s["tables"]) or "-", 40),
                     _cell(f"{s['param'] or '-'} → {s['result'] or '-'}", 70), _cell(s["sql"], 90)]
                    for s in stm[:40]]
            L += [""] + _table(["Statement", "Type", "Tables", "Param → Result", "SQL (shortened)"], rows)
            if len(stm) > 40:
                L.append(f"\n… +{len(stm) - 40} more statements")
    for rel, info in k.xml.items():
        if info.kind == "hibernate-mapping":
            L += ["", f"### Hibernate mapping {_code(rel)}"] + [f"- {x}" for x in info.sections.get("Entities", [])]
    entities = [t for t in k.layers.get(LAYER_MODEL, []) if any(a.name in ("Entity", "Table") for a in t.annotations)]
    if entities:
        L += ["", "### JPA entities", ""]
        rows = []
        for t in entities:
            table = next((re.search(r'name\s*=\s*"([^"]+)"', a.args).group(1) for a in t.annotations
                          if a.name == "Table" and re.search(r'name\s*=\s*"([^"]+)"', a.args)), "-")
            fields = [f"{m.name}: {m.type_name}" for m in t.members
                      if m.kind == "field" and "static" not in m.modifiers][:12]
            rows.append([_code(t.display), _code(table), _cell(", ".join(fields), 150)])
        L += _table(["Entity", "Table", "Fields"], rows)
    if k.tables:
        L += ["", "### Database tables referenced", ""]
        L += _table(["Table", "Referenced by"],
                    [[_code(t), _cell(", ".join(sorted(set(src))), 140)] for t, src in sorted(k.tables.items())])
    return L


def _config(k: Knowledge) -> List[str]:
    L: List[str] = []
    for rel, p in k.props.items():
        L += ["", f"### {_code(rel)}"]
        meta = f"{len(p.entries)} keys"
        if p.is_i18n:
            meta += " — looks like an i18n/message bundle (only a sample is shown)"
        L.append(meta)
        if p.duplicates:
            L.append("- Duplicate keys: " + ", ".join(_code(d) for d in p.duplicates[:10]))
        if p.groups and len(p.entries) > 15 and p.groups[0][1] > 1:
            L.append("- Key groups: " + ", ".join(f"{_code(g)}×{c}" for g, c in p.groups))
        limit = 15 if p.is_i18n else k.cfg.max_props_rows
        rows = []
        for key, val in p.entries[:limit]:
            users = k.prop_usage.get(key)
            rows.append([_code(key), _cell(val, 90), _cell(", ".join(sorted(users)), 50) if users else ""])
        if rows:
            L += [""] + _table(["Key", "Value", "Read by"], rows)
        if len(p.entries) > limit:
            L.append(f"\n… +{len(p.entries) - limit} more keys")
    skip = {"maven-pom", "mybatis-mapper", "hibernate-mapping"}
    for rel, info in k.xml.items():
        if info.kind in skip:
            continue
        L += ["", f"### {_code(rel)}", f"{info.summary}"]
        for title, lines in info.sections.items():
            L += ["", f"**{title}**"] + [f"- {x}" for x in lines]
    return L


def _frontend(k: Knowledge) -> List[str]:
    L: List[str] = []
    vendor = [r for r, j in k.js.items() if j.vendor]
    for rel, j in k.js.items():
        if j.vendor:
            continue
        L += ["", f"### {_code(rel)}"]
        if j.description:
            L.append(f"- Purpose: {j.description}")
        if j.frameworks:
            L.append("- Uses: " + ", ".join(j.frameworks))
        if j.imports:
            L.append("- Imports: " + ", ".join(_code(i) for i in j.imports[:12]))
        if j.classes:
            L.append("- Classes: " + ", ".join(_code(c) for c in j.classes))
        if j.functions:
            shown = [f"{_code(f.name + '(' + f.params + ')')} (L{f.line})" for f in j.functions[:40]]
            L.append(f"- Functions ({len(j.functions)}): " + ", ".join(shown)
                     + (f", … +{len(j.functions) - 40} more" if len(j.functions) > 40 else ""))
        calls = [c for c in k.js_calls if c[0] == rel]
        for _, verb, url, line, matches in calls[:30]:
            target = " → " + "; ".join(f"{_code(e.http + ' ' + e.path)} ({e.handler})" for e in matches) if matches else ""
            L.append(f"- L{line}: {verb} {_code(url)}{target}")
    if vendor:
        L += ["", "**Third-party / minified JS (not analysed):** " + ", ".join(_code(v) for v in vendor[:30])
              + (f" … +{len(vendor) - 30} more" if len(vendor) > 30 else "")]
    return L


def _render_type(k: Knowledge, t: JavaType, ep_index: Dict[Tuple[str, int], List[Endpoint]]) -> List[str]:
    cfg = k.cfg
    layer = k.type_layer.get(t.qualified, layer_of(t))
    L = ["", f"#### {t.display} — {t.kind}" + (f" · {layer}" if layer != "Other" else "")]
    L.append(f"- File: {_code(t.rel)} (L{t.line})")
    anns = [a for a in t.annotations if a.name not in _HIDDEN_ANNS]
    if anns:
        L.append("- Annotations: " + " ".join(_ann_text(a) for a in anns))
    rel_bits = []
    if t.extends:
        rel_bits.append("extends " + ", ".join(_code(x) for x in t.extends))
    if t.implements:
        rel_bits.append("implements " + ", ".join(_code(x) for x in t.implements))
    if rel_bits:
        joined = " · ".join(rel_bits)
        L.append("- " + joined[0].upper() + joined[1:])
    if t.doc:
        L.append(f"- Purpose: {t.doc}")
    if t.components:
        L.append(f"- Record components: {_code(t.components)}")
    if t.enum_constants:
        L.append("- Constants: " + ", ".join(_code(c) for c in t.enum_constants[:30]))
    if t.qualified in k.mapper_xml:
        L.append(f"- MyBatis XML: {_code(k.mapper_xml[t.qualified])}")
    for note in k.bean_refs.get(t.qualified, []):
        L.append(f"- Declared as Spring bean in {note}")

    injected = [f"{m.type_name} {m.name}" for m in t.members
                if m.kind == "field" and any(a.name in _DI_ANNS and a.name != "Value" for a in m.annotations)]
    if injected:
        L.append("- Injected: " + ", ".join(_code(x) for x in injected))
    if layer == LAYER_MODEL or "Entity" in {a.name for a in t.annotations}:
        flds = [f"{m.name}: {m.type_name}" for m in t.members if m.kind == "field" and "static" not in m.modifiers]
        if flds:
            L.append("- Fields: " + ", ".join(_code(x) for x in flds[:25]) + (" …" if len(flds) > 25 else ""))

    methods = [m for m in t.members if m.kind in ("method", "constructor")
               and (cfg.include_private or m.visibility != "private")]
    trivial = [m for m in methods if _is_trivial(m)]
    trivial_ids = {id(m) for m in trivial}
    shown = [m for m in methods if id(m) not in trivial_ids]
    if shown:
        L.append("- Methods:")
        for m in shown[: cfg.max_methods]:
            bits = [f"  - {_code(m.signature)}"]
            for e in ep_index.get((t.rel, m.line), [])[:3]:
                bits.append(f"**{e.http} {e.path}**")
            if m.doc:
                bits.append(m.doc)
            tags = [a.name for a in m.annotations if a.name not in _HIDDEN_ANNS
                    and a.name not in ("GetMapping", "PostMapping", "PutMapping", "DeleteMapping",
                                       "PatchMapping", "RequestMapping")]
            if tags:
                bits.append("(" + ", ".join("@" + x for x in tags[:4]) + ")")
            L.append(" — ".join(bits))
        if len(shown) > cfg.max_methods:
            L.append(f"  - … +{len(shown) - cfg.max_methods} more methods")
    if trivial:
        L.append(f"- Plus {len(trivial)} trivial accessor/boilerplate methods")

    if t.outer is None:
        uses = sorted(k.primary_name[r] for r in k.file_deps.get(t.rel, ()) if r in k.primary_name)
        users = sorted(k.primary_name[r] for r in k.used_by.get(t.rel, ()) if r in k.primary_name)
        if uses:
            L.append(f"- Uses ({len(uses)}): " + ", ".join(_code(x) for x in uses[:15]) + (" …" if len(uses) > 15 else ""))
        if users:
            L.append(f"- Used by ({len(users)}): " + ", ".join(_code(x) for x in users[:15]) + (" …" if len(users) > 15 else ""))
    return L


def _catalog(k: Knowledge) -> List[str]:
    ep_index: Dict[Tuple[str, int], List[Endpoint]] = defaultdict(list)
    for e in k.endpoints:
        ep_index[(e.rel, e.line)].append(e)
    by_pkg: Dict[str, List[JavaType]] = defaultdict(list)
    for t in k.types:
        by_pkg[t.package or "(default)"].append(t)
    L: List[str] = []
    for pkg in sorted(by_pkg):
        L += ["", f"### Package {_code(pkg)}"]
        for t in sorted(by_pkg[pkg], key=lambda x: (x.rel, x.line)):
            L += _render_type(k, t, ep_index)
    return L


def _insights(k: Knowledge) -> List[str]:
    L: List[str] = []
    ranked = sorted(((len(u), rel) for rel, u in k.used_by.items() if u), reverse=True)[:15]
    if ranked:
        L += ["### Most depended-on classes (change with care)", ""]
        L += _table(["Class", "Layer", "Used by (files)"],
                    [[_code(k.primary_name[rel]),
                      next((k.type_layer[t.qualified] for t in k.java[rel].types if t.outer is None), "-"),
                      str(n)] for n, rel in ranked])
    orphan = []
    for rel, jf in k.java.items():
        if k.used_by.get(rel):
            continue
        tops = [t for t in jf.types if t.outer is None]
        if not tops:
            continue
        t = tops[0]
        lay = k.type_layer.get(t.qualified, "")
        has_entry = any(m.name == "main" for m in t.members) or any(e.rel == rel for e in k.endpoints)
        wired = bool({a.name for a in t.annotations} & _FRAMEWORK_WIRED) or t.qualified in k.bean_refs \
            or t.qualified in k.mapper_xml
        if lay in (LAYER_TEST, LAYER_CONTROLLER) or has_entry or wired:
            continue
        orphan.append(t.name)
    if orphan:
        L += ["", "### Not referenced by other scanned Java files",
              "_May be framework-wired (Spring/XML/reflection), entry points, or dead code — verify before deleting._", "",
              ", ".join(_code(x) for x in sorted(orphan)[:60]) + (" …" if len(orphan) > 60 else "")]
    return L


def _summary_for(k: Knowledge, rel: str, ext: str) -> str:
    if ext == ".java" and rel in k.java:
        tops = [t for t in k.java[rel].types if t.outer is None]
        if not tops:
            return "no type declaration found"
        t = tops[0]
        return _cell(f"{t.kind} {t.name}" + (f" [{k.type_layer.get(t.qualified, '')}]" if k.type_layer.get(t.qualified, 'Other') != 'Other' else "")
                     + (f" — {t.doc}" if t.doc else ""), 140)
    if ext == ".xml" and rel in k.xml:
        return _cell(k.xml[rel].summary, 140)
    if ext == ".properties" and rel in k.props:
        return f"{len(k.props[rel].entries)} keys"
    if ext == ".js" and rel in k.js:
        j = k.js[rel]
        if j.vendor:
            return f"third-party/minified ({j.vendor_note})"
        return _cell(j.description or f"{len(j.functions)} functions, {len(j.calls)} AJAX calls", 140)
    return ""


def _index(k: Knowledge) -> List[str]:
    rows = [[_code(f.rel), f.ext[1:], str(f.lines), _summary_for(k, f.rel, f.ext) or (f.skipped or "")] for f in k.files]
    return _table(["File", "Type", "Lines", "Summary"], rows)


def _notes(k: Knowledge) -> List[str]:
    return [f"- {w}" for w in k.warnings]


# ------------------------------------------------------------------- render
def render(k: Knowledge) -> str:
    title = k.cfg.title or k.cfg.root.resolve().name
    sections: List[Tuple[str, Callable[[Knowledge], List[str]]]] = [
        ("Project overview", _overview),
        ("Technology stack and build", _tech),
        ("Architecture layers", _layers),
        ("Entry points and HTTP endpoints", _entry),
        ("Data layer", _data),
        ("Configuration", _config),
        ("Front-end JavaScript", _frontend),
        ("Class catalog", _catalog),
        ("Dependency insights", _insights),
    ]
    if k.cfg.include_index:
        sections.append(("File index", _index))
    sections.append(("Notes and warnings", _notes))

    body: List[Tuple[str, List[str]]] = []
    for name, fn in sections:
        lines = fn(k)
        while lines and not lines[0].strip():
            lines = lines[1:]
        if any(x.strip() for x in lines):
            body.append((name, lines))

    out = [f"# Knowledge file — {title}", "",
           f"> Auto-generated on {k.generated_at} from `{k.cfg.root.resolve().name}` by java-knowledge-gen. "
           "Structure is extracted statically (regex based, no compilation) — treat it as a map, "
           "and verify details in the source.", "", "## Contents", ""]
    for i, (name, _) in enumerate(body, 1):
        heading = f"{i}. {name}"
        out.append(f"- [{heading}](#{_slug(heading)})")
    for i, (name, lines) in enumerate(body, 1):
        out += ["", f"## {i}. {name}", ""] + lines
    return "\n".join(out).rstrip() + "\n"
