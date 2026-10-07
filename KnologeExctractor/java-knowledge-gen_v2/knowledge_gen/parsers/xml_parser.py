"""XML understanding: Maven POM, Spring beans, MyBatis, web.xml, Hibernate/JPA, logging ..."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import Counter
from typing import Any, Dict, List, Tuple

from ..models import XmlInfo
from .common import mask_value, squash, truncate

_SQL_STOP = {"select", "set", "dual", "values", "where", "table", "if", "and", "or", "not", "on"}
_TABLE_RE = re.compile(r"\b(?:from|join|into|update)\s+([`\"\[]?[A-Za-z_][\w.$]*[`\"\]]?)", re.I)


def _l(el: ET.Element) -> str:
    t = el.tag
    return t.rsplit("}", 1)[-1] if isinstance(t, str) else ""


def _kids(el: ET.Element, name: str = "") -> List[ET.Element]:
    return [c for c in el if isinstance(c.tag, str) and (not name or _l(c) == name)]


def _text(el: ET.Element, name: str) -> str:
    for c in _kids(el, name):
        return (c.text or "").strip()
    return ""


def _cap(lines: List[str], n: int = 60) -> List[str]:
    return lines if len(lines) <= n else lines[:n] + [f"… +{len(lines) - n} more"]


def _tables_from_sql(sql: str) -> List[str]:
    seen: List[str] = []
    for m in _TABLE_RE.finditer(sql):
        name = m.group(1).strip("`\"[]")
        if name.lower() in _SQL_STOP or name in seen:
            continue
        seen.append(name)
    return seen


# ------------------------------------------------------------ entry point
def parse_xml(text: str, rel: str) -> XmlInfo:
    info = XmlInfo()
    cleaned = text.lstrip("﻿")
    cleaned = re.sub(r"^\s*<\?xml[^>]*\?>", "", cleaned)
    root = None
    try:
        root = ET.fromstring(cleaned)
    except ET.ParseError:
        fixed = re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)[A-Za-z_][\w.-]*;", " ", cleaned)
        try:
            root = ET.fromstring(fixed)
        except ET.ParseError as exc:
            info.error = f"XML parse error: {exc}"

    if root is None:
        m = re.search(r"<([A-Za-z_][\w:.-]*)", re.sub(r"<[?!][^>]*>", "", cleaned))
        info.root = m.group(1) if m else ""
        info.kind = "unparsed"
        info.summary = f"root <{info.root}> (could not be parsed)"
        return info

    name = _l(root)
    info.root = name
    ns = root.tag[1:].split("}")[0] if root.tag.startswith("{") else ""
    child_names = {_l(c) for c in _kids(root)}

    if name == "project" and ("maven" in ns or {"modelVersion", "artifactId", "groupId", "dependencies"} & child_names):
        _maven(root, info)
    elif name == "beans":
        _spring(root, info)
    elif name == "mapper":
        _mapper(root, info)
    elif name == "web-app":
        _webxml(root, info)
    elif name in ("hibernate-mapping",):
        _hibernate_mapping(root, info)
    elif name == "persistence":
        _persistence(root, info)
    elif name == "configuration" and {"typeAliases", "environments", "mappers", "settings", "plugins"} & child_names:
        _mybatis_config(root, info)
    elif name.lower() == "configuration" and {"appender", "Appenders", "logger", "root", "Loggers"} & child_names:
        _logging(root, info)
    elif name == "project" and ("default" in root.attrib or "target" in child_names):
        _ant(root, info)
    else:
        _generic(root, info)
    return info


# ----------------------------------------------------------------- Maven
def _maven(root: ET.Element, info: XmlInfo) -> None:
    parent = (_kids(root, "parent") or [None])[0]
    pg = _text(parent, "groupId") if parent is not None else ""
    pv = _text(parent, "version") if parent is not None else ""
    pa = _text(parent, "artifactId") if parent is not None else ""
    g = _text(root, "groupId") or pg
    a = _text(root, "artifactId")
    v = _text(root, "version") or pv
    pk = _text(root, "packaging") or "jar"
    info.kind = "maven-pom"
    info.summary = f"Maven {pk}: {g}:{a}:{v}"

    coords = [f"groupId `{g}`, artifactId `{a}`, version `{v}`, packaging `{pk}`"]
    if _text(root, "name"):
        coords.append(f"name: {_text(root, 'name')}")
    if _text(root, "description"):
        coords.append(f"description: {truncate(squash(_text(root, 'description')), 200)}")
    if parent is not None:
        coords.append(f"parent: `{pg}:{pa}:{pv}`")
    info.sections["Coordinates"] = coords

    modules = [(m.text or "").strip() for mods in _kids(root, "modules") for m in _kids(mods, "module")]
    if modules:
        info.sections["Modules"] = [f"`{m}`" for m in modules]

    props = []
    for p in _kids(root, "properties"):
        for c in _kids(p):
            props.append(f"`{_l(c)}` = `{truncate((c.text or '').strip(), 80)}`")
    if props:
        info.sections["Properties"] = _cap(props, 25)

    deps: List[Dict[str, str]] = []
    for ds in _kids(root, "dependencies"):
        for d in _kids(ds, "dependency"):
            deps.append({"g": _text(d, "groupId"), "a": _text(d, "artifactId"),
                         "v": _text(d, "version"), "scope": _text(d, "scope")})
    if deps:
        info.sections["Dependencies"] = _cap(
            [f"`{d['g']}:{d['a']}`" + (f" {d['v']}" if d["v"] else "") + (f" ({d['scope']})" if d["scope"] else "")
             for d in deps], 60)

    plugins = []
    for b in _kids(root, "build"):
        for ps in _kids(b, "plugins"):
            plugins += [f"`{_text(p, 'artifactId')}`" for p in _kids(ps, "plugin")]
    if plugins:
        info.sections["Build plugins"] = plugins
    info.extra = {"group": g, "artifact": a, "version": v, "packaging": pk,
                  "deps": [f"{d['g']}:{d['a']}" for d in deps], "modules": modules}


# ---------------------------------------------------------------- Spring
def _spring(root: ET.Element, info: XmlInfo) -> None:
    beans: List[Tuple[str, str]] = []
    scans: List[str] = []
    imports: List[str] = []
    placeholders: List[str] = []
    flags: Counter = Counter()
    for el in root.iter():
        n = _l(el)
        if n == "bean":
            beans.append((el.get("id") or el.get("name") or "", el.get("class") or el.get("parent") or ""))
        elif n == "component-scan":
            scans.append(el.get("base-package", ""))
        elif n == "import":
            imports.append(el.get("resource", ""))
        elif n == "property-placeholder":
            placeholders.append(el.get("location", ""))
        elif n in {"annotation-config", "annotation-driven", "transaction-manager", "scheduled-tasks",
                   "aspectj-autoproxy", "interceptors", "resources", "view-resolvers"}:
            flags[n] += 1
    info.kind = "spring-beans"
    info.summary = f"Spring config: {len(beans)} beans" + (f", scans {', '.join(scans)}" if scans else "")
    if scans:
        info.sections["Component scan"] = [f"`{s}`" for s in scans]
    if imports:
        info.sections["Imports"] = [f"`{i}`" for i in imports]
    if placeholders:
        info.sections["Property placeholders"] = [f"`{p}`" for p in placeholders]
    if flags:
        info.sections["Features enabled"] = [f"`{k}`" for k in flags]
    if beans:
        info.sections["Beans"] = _cap([f"`{i or '(anonymous)'}` → `{c}`" for i, c in beans if i or c], 60)
    info.extra = {"beans": beans, "scans": scans}


# --------------------------------------------------------------- MyBatis
def _mapper(root: ET.Element, info: XmlInfo) -> None:
    ns = root.get("namespace", "")
    stmts: List[Dict[str, Any]] = []
    result_maps: List[Tuple[str, str]] = []
    tables: List[str] = []
    for el in _kids(root):
        n = _l(el)
        if n in ("select", "insert", "update", "delete"):
            sql = squash("".join(el.itertext()))
            tbs = _tables_from_sql(sql)
            for t in tbs:
                if t not in tables:
                    tables.append(t)
            stmts.append({"id": el.get("id", ""), "tag": n, "param": el.get("parameterType", ""),
                          "result": el.get("resultType") or el.get("resultMap", ""),
                          "tables": tbs, "sql": sql})
        elif n == "resultMap":
            result_maps.append((el.get("id", ""), el.get("type", "")))
    info.kind = "mybatis-mapper"
    info.summary = f"MyBatis mapper `{ns}`: {len(stmts)} statements, tables: {', '.join(tables) or '-'}"
    info.extra = {"namespace": ns, "statements": stmts, "result_maps": result_maps, "tables": tables}


def _mybatis_config(root: ET.Element, info: XmlInfo) -> None:
    info.kind = "mybatis-config"
    info.summary = "MyBatis main configuration"
    mappers: List[str] = []
    for el in root.iter():
        n = _l(el)
        if n == "mapper":
            mappers.append(el.get("resource") or el.get("class") or el.get("url") or "")
        elif n == "package" and el.get("name"):
            mappers.append(f"package {el.get('name')}")
    if mappers:
        info.sections["Mappers"] = _cap([f"`{m}`" for m in mappers])
    settings = [f"`{s.get('name')}` = `{s.get('value')}`" for st in _kids(root, "settings") for s in _kids(st, "setting")]
    if settings:
        info.sections["Settings"] = settings
    aliases = [f"`{a.get('alias', '')}` → `{a.get('type', '') or a.get('name', '')}`"
               for ta in _kids(root, "typeAliases") for a in _kids(ta)]
    if aliases:
        info.sections["Type aliases"] = _cap(aliases, 40)
    envs = []
    for e in _kids(root, "environments"):
        for env in _kids(e, "environment"):
            for ds in _kids(env, "dataSource"):
                props = {p.get("name", ""): p.get("value", "") for p in _kids(ds, "property")}
                shown = ", ".join(f"{k}={mask_value(k, v)}" for k, v in props.items()
                                  if k in ("driver", "url", "username", "password"))
                envs.append(f"`{env.get('id', '')}` ({ds.get('type', '')}): {shown}")
    if envs:
        info.sections["Environments"] = envs


# --------------------------------------------------------------- web.xml
def _webxml(root: ET.Element, info: XmlInfo) -> None:
    mappings: Dict[str, List[str]] = {}
    for sm in root.iter():
        if _l(sm) == "servlet-mapping":
            mappings.setdefault(_text(sm, "servlet-name"), []).extend(
                (u.text or "").strip() for u in _kids(sm, "url-pattern"))
    servlets: List[Tuple[str, str, List[str]]] = []
    for s in root.iter():
        if _l(s) == "servlet":
            nm = _text(s, "servlet-name")
            servlets.append((nm, _text(s, "servlet-class") or _text(s, "jsp-file"), mappings.get(nm, [])))
    fmap: Dict[str, List[str]] = {}
    for fm in root.iter():
        if _l(fm) == "filter-mapping":
            fmap.setdefault(_text(fm, "filter-name"), []).extend(
                [(u.text or "").strip() for u in _kids(fm, "url-pattern")]
                + [f"servlet:{(u.text or '').strip()}" for u in _kids(fm, "servlet-name")])
    filters = [(_text(f, "filter-name"), _text(f, "filter-class"), fmap.get(_text(f, "filter-name"), []))
               for f in root.iter() if _l(f) == "filter"]
    listeners = [_text(li, "listener-class") for li in root.iter() if _l(li) == "listener"]
    ctx = [(_text(c, "param-name"), _text(c, "param-value")) for c in root.iter() if _l(c) == "context-param"]
    info.kind = "web-xml"
    info.summary = f"Servlet deployment descriptor: {len(servlets)} servlets, {len(filters)} filters, {len(listeners)} listeners"
    if servlets:
        info.sections["Servlets"] = [f"`{n}` → `{c}` mapped to {', '.join(f'`{p}`' for p in ps) or '-'}"
                                     for n, c, ps in servlets]
    if filters:
        info.sections["Filters"] = [f"`{n}` → `{c}` on {', '.join(f'`{p}`' for p in ps) or '-'}"
                                    for n, c, ps in filters]
    if listeners:
        info.sections["Listeners"] = [f"`{x}`" for x in listeners]
    if ctx:
        info.sections["Context parameters"] = [f"`{k}` = `{truncate(mask_value(k, v), 100)}`" for k, v in ctx]
    welcome = [(w.text or "").strip() for wl in root.iter() if _l(wl) == "welcome-file-list" for w in _kids(wl)]
    if welcome:
        info.sections["Welcome files"] = [f"`{w}`" for w in welcome]
    info.extra = {"servlets": servlets}


# ------------------------------------------------------------ Hibernate/JPA
def _hibernate_mapping(root: ET.Element, info: XmlInfo) -> None:
    pkg = root.get("package", "")
    rows = []
    tables = []
    for el in root.iter():
        if _l(el) in ("class", "subclass", "joined-subclass") and el.get("name"):
            cls = el.get("name", "")
            tbl = el.get("table", "")
            rows.append(f"`{(pkg + '.') if pkg and '.' not in cls else ''}{cls}` → table `{tbl or '-'}`")
            if tbl:
                tables.append(tbl)
    info.kind = "hibernate-mapping"
    info.summary = f"Hibernate mapping: {len(rows)} entities"
    if rows:
        info.sections["Entities"] = rows
    info.extra = {"tables": tables}


def _persistence(root: ET.Element, info: XmlInfo) -> None:
    info.kind = "jpa-persistence"
    units = [u for u in root.iter() if _l(u) == "persistence-unit"]
    info.summary = f"JPA persistence.xml: {len(units)} unit(s)"
    for u in units:
        lines = [f"classes: {', '.join(f'`{(c.text or '').strip()}`' for c in u.iter() if _l(c) == 'class')}"]
        for p in u.iter():
            if _l(p) == "property" and p.get("name"):
                lines.append(f"`{p.get('name')}` = `{truncate(mask_value(p.get('name', ''), p.get('value', '')), 90)}`")
        info.sections[f"Unit `{u.get('name', '')}`"] = lines


# -------------------------------------------------------------- logging etc.
def _logging(root: ET.Element, info: XmlInfo) -> None:
    info.kind = "logging-config"
    info.summary = "Logging configuration"
    appenders = [f"`{a.get('name', '')}` ({a.get('class') or _l(a)})"
                 for a in root.iter() if _l(a).lower() == "appender" or _l(a).endswith("Appender")]
    loggers = [f"`{x.get('name', 'ROOT')}` level `{x.get('level', '')}`"
               for x in root.iter() if _l(x).lower() in ("logger", "root")]
    if appenders:
        info.sections["Appenders"] = _cap(appenders, 20)
    if loggers:
        info.sections["Loggers"] = _cap(loggers, 30)


def _ant(root: ET.Element, info: XmlInfo) -> None:
    info.kind = "ant-build"
    targets = [t.get("name", "") for t in _kids(root, "target")]
    info.summary = f"Ant build `{root.get('name', '')}` default target `{root.get('default', '')}`"
    if targets:
        info.sections["Targets"] = [f"`{t}`" for t in targets]


def _generic(root: ET.Element, info: XmlInfo) -> None:
    info.kind = "generic"
    counts = Counter(_l(e) for e in root.iter() if isinstance(e.tag, str))
    top = ", ".join(f"{k}×{v}" for k, v in counts.most_common(6))
    info.summary = f"<{_l(root)}> document ({sum(counts.values())} elements; {top})"
    if _l(root) == "struts":
        acts = [f"`{a.get('name', '')}` → `{a.get('class', '')}`" for a in root.iter() if _l(a) == "action"]
        if acts:
            info.sections["Struts actions"] = _cap(acts)
