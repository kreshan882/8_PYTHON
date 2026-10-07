"""Parse every file and derive cross-file knowledge (layers, endpoints, deps, tables ...)."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

from .callgraph import CallGraph, mkey
from .config import Config
from .git_history import collect_git
from .messages import build_messages
from .models import (GitInfo, JavaFile, JavaMember, JavaType, JsInfo, MessageSite, PropsInfo, SourceFile,
                     XmlInfo)
from .risks import Risks, collect_risks
from .parsers.java_parser import parse_java
from .parsers.js_parser import parse_js
from .parsers.props_parser import parse_properties
from .parsers.xml_parser import parse_xml
from .scanner import scan

LAYER_CONTROLLER = "Controller / Web"
LAYER_SERVICE = "Service"
LAYER_REPO = "Repository / DAO / Mapper"
LAYER_MODEL = "Entity / Model / DTO"
LAYER_CONFIG = "Configuration"
LAYER_WEB_INFRA = "Filter / Listener / Interceptor"
LAYER_UTIL = "Utility"
LAYER_EXC = "Exception"
LAYER_TEST = "Test"
LAYER_ASPECT = "Aspect"
LAYER_COMPONENT = "Component"
LAYER_ENUM = "Enum / Constants"
LAYER_OTHER = "Other"

_ANN_LAYERS: List[Tuple[str, Set[str]]] = [
    (LAYER_CONTROLLER, {"Controller", "RestController", "ControllerAdvice", "RestControllerAdvice",
                        "WebServlet", "Path"}),
    (LAYER_SERVICE, {"Service", "Stateless", "Stateful"}),
    (LAYER_REPO, {"Repository", "Mapper", "Dao"}),
    (LAYER_MODEL, {"Entity", "Table", "Embeddable", "MappedSuperclass", "Document"}),
    (LAYER_CONFIG, {"Configuration", "SpringBootApplication", "EnableAutoConfiguration",
                    "ConfigurationProperties"}),
    (LAYER_ASPECT, {"Aspect"}),
    (LAYER_WEB_INFRA, {"WebFilter", "WebListener"}),
    (LAYER_COMPONENT, {"Component"}),
]
_SUFFIX_LAYERS: List[Tuple[str, re.Pattern]] = [
    (LAYER_TEST, re.compile(r"(Tests?|IT|TestCase)$")),
    (LAYER_CONTROLLER, re.compile(r"(Controller|Action|Servlet|Resource|Endpoint)$")),
    (LAYER_SERVICE, re.compile(r"(Service|ServiceImpl|Manager|Facade|Biz|Bo)$")),
    (LAYER_REPO, re.compile(r"(Dao|DaoImpl|Repository|Mapper|Repo)$")),
    (LAYER_CONFIG, re.compile(r"(Config|Configuration|Properties|Settings)$")),
    (LAYER_WEB_INFRA, re.compile(r"(Filter|Interceptor|Listener|Handler)$")),
    (LAYER_EXC, re.compile(r"(Exception|Error)$")),
    (LAYER_UTIL, re.compile(r"(Util|Utils|Helper|Constants|Tool|Tools)$")),
    (LAYER_MODEL, re.compile(r"(Entity|Model|Dto|DTO|VO|Vo|Bean|Form|Request|Response|Pojo|POJO)$")),
]
_SUPER_LAYERS = {"HttpServlet": LAYER_CONTROLLER, "ActionSupport": LAYER_CONTROLLER,
                 "Action": LAYER_CONTROLLER, "Filter": LAYER_WEB_INFRA, "Exception": LAYER_EXC,
                 "RuntimeException": LAYER_EXC}

_TECH = [
    ("org.springframework.boot", "Spring Boot"),
    ("org.springframework.security", "Spring Security"),
    ("org.springframework.data.redis", "Redis (Spring Data)"),
    ("org.springframework.data", "Spring Data"),
    ("org.springframework.web", "Spring MVC"),
    ("org.springframework.amqp", "RabbitMQ (Spring AMQP)"),
    ("org.springframework.kafka", "Kafka (Spring)"),
    ("org.springframework", "Spring Framework"),
    ("org.apache.ibatis", "MyBatis"), ("org.mybatis", "MyBatis"), ("tk.mybatis", "MyBatis (tk)"),
    ("org.hibernate", "Hibernate"),
    ("javax.persistence", "JPA"), ("jakarta.persistence", "JPA"),
    ("javax.servlet", "Servlet API"), ("jakarta.servlet", "Servlet API"),
    ("javax.ws.rs", "JAX-RS"), ("jakarta.ws.rs", "JAX-RS"),
    ("org.apache.struts", "Struts"), ("com.opensymphony.xwork2", "Struts 2"),
    ("lombok", "Lombok"),
    ("org.slf4j", "SLF4J"), ("org.apache.log4j", "Log4j"), ("org.apache.logging.log4j", "Log4j 2"),
    ("ch.qos.logback", "Logback"),
    ("org.junit", "JUnit"), ("org.mockito", "Mockito"), ("org.testng", "TestNG"),
    ("com.fasterxml.jackson", "Jackson"), ("com.google.gson", "Gson"), ("com.alibaba.fastjson", "Fastjson"),
    ("org.apache.commons", "Apache Commons"), ("com.google.common", "Guava"),
    ("io.swagger", "Swagger"), ("springfox", "Springfox"),
    ("javax.xml.bind", "JAXB"), ("jakarta.xml.bind", "JAXB"),
    ("com.zaxxer.hikari", "HikariCP"), ("com.alibaba.druid", "Druid"),
    ("redis.clients", "Redis (Jedis)"), ("org.apache.kafka", "Kafka"), ("com.rabbitmq", "RabbitMQ"),
    ("javax.jms", "JMS"), ("jakarta.jms", "JMS"), ("org.quartz", "Quartz"),
    ("io.jsonwebtoken", "JWT"), ("java.sql", "JDBC"), ("javax.sql", "JDBC"),
    ("org.apache.poi", "Apache POI"), ("com.itextpdf", "iText"), ("net.sf.jasperreports", "JasperReports"),
    ("javax.ejb", "EJB"), ("javax.faces", "JSF"), ("org.apache.shiro", "Apache Shiro"),
]
_TECH.sort(key=lambda p: -len(p[0]))

_SPRING_VERBS = {"GetMapping": "GET", "PostMapping": "POST", "PutMapping": "PUT",
                 "DeleteMapping": "DELETE", "PatchMapping": "PATCH"}
_JAXRS_VERBS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"}
_LISTENER_ANNS = {"Scheduled": "Scheduled job", "KafkaListener": "Kafka consumer",
                  "RabbitListener": "RabbitMQ consumer", "JmsListener": "JMS consumer",
                  "EventListener": "Event listener", "Schedule": "EJB timer"}


@dataclass
class Endpoint:
    http: str
    path: str
    handler: str
    rel: str
    line: int
    doc: str = ""
    key: str = ""            # handler method key (Class#method)
    security: str = ""       # @PreAuthorize / @Secured / @RolesAllowed ...


@dataclass
class Knowledge:
    cfg: Config
    generated_at: str
    files: List[SourceFile]
    java: Dict[str, JavaFile] = field(default_factory=dict)
    xml: Dict[str, XmlInfo] = field(default_factory=dict)
    props: Dict[str, PropsInfo] = field(default_factory=dict)
    js: Dict[str, JsInfo] = field(default_factory=dict)
    types: List[JavaType] = field(default_factory=list)
    type_layer: Dict[str, str] = field(default_factory=dict)          # qualified -> layer
    layers: Dict[str, List[JavaType]] = field(default_factory=dict)
    tech: List[Tuple[str, int]] = field(default_factory=list)
    endpoints: List[Endpoint] = field(default_factory=list)
    entrypoints: List[Tuple[str, str, str]] = field(default_factory=list)   # kind, what, file
    file_deps: Dict[str, Set[str]] = field(default_factory=dict)
    used_by: Dict[str, Set[str]] = field(default_factory=dict)
    primary_name: Dict[str, str] = field(default_factory=dict)        # java rel -> main type
    tables: Dict[str, List[str]] = field(default_factory=dict)        # table -> sources
    mapper_xml: Dict[str, str] = field(default_factory=dict)          # java FQN -> xml rel
    bean_refs: Dict[str, List[str]] = field(default_factory=dict)     # java FQN -> xml notes
    prop_usage: Dict[str, Set[str]] = field(default_factory=dict)     # key -> class names
    js_calls: List[Tuple[str, str, str, int, List[Endpoint]]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    # --- production-support data
    cg: Any = None                                                     # CallGraph
    messages: List[MessageSite] = field(default_factory=list)
    consts: Dict[str, str] = field(default_factory=dict)              # constant name -> string value
    props_flat: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)   # key -> [(file, value)]
    key_usage: Dict[str, List[Tuple[str, str, int]]] = field(default_factory=dict)  # key -> [(file, owner, line)]
    env_groups: Dict[str, Dict[str, str]] = field(default_factory=dict)          # base -> {env: rel}
    risks: Optional[Risks] = None
    git: Optional[GitInfo] = None
    regex_cache: Dict[str, Any] = field(default_factory=dict)


# ------------------------------------------------------------------ layers
def layer_of(t: JavaType) -> str:
    anns = {a.name for a in t.annotations}
    if re.search(r"(^|/)src/test/|(^|/)tests?/", t.rel):
        return LAYER_TEST
    for layer, names in _ANN_LAYERS:
        if anns & names:
            return layer
    for sup in t.extends + t.implements:
        base = re.sub(r"<.*", "", sup).split(".")[-1]
        if base in _SUPER_LAYERS:
            return _SUPER_LAYERS[base]
    for layer, rx in _SUFFIX_LAYERS:
        if rx.search(t.name):
            return layer
    if t.kind == "enum":
        return LAYER_ENUM
    return LAYER_OTHER


# --------------------------------------------------------------- endpoints
def _paths(args: str) -> List[str]:
    m = re.search(r"\b(?:value|path|urlPatterns)\s*=\s*(\{[^}]*\}|\"[^\"]*\")", args)
    if not m:
        m = re.match(r"\s*(\{[^}]*\}|\"[^\"]*\")", args)
    return re.findall(r'"([^"]*)"', m.group(1)) if m else []


def _join(a: str, b: str) -> str:
    parts = [p.strip("/") for p in (a, b) if p.strip("/")]
    return "/" + "/".join(parts)


def _type_endpoints(t: JavaType) -> List[Endpoint]:
    eps: List[Endpoint] = []
    cls_paths = [""]
    for a in t.annotations:
        if a.name in ("RequestMapping", "Path"):
            cls_paths = _paths(a.args) or [""]
    for m in t.members:
        if m.kind != "method":
            continue
        verbs: List[str] = []
        mpaths: List[str] = []
        for a in m.annotations:
            if a.name in _SPRING_VERBS:
                verbs.append(_SPRING_VERBS[a.name])
                mpaths += _paths(a.args)
            elif a.name == "RequestMapping":
                found = [v.upper() for v in re.findall(r"RequestMethod\.(\w+)", a.args)]
                verbs += found or ["ANY"]
                mpaths += _paths(a.args)
            elif a.name in _JAXRS_VERBS:
                verbs.append(a.name)
            elif a.name == "Path":
                mpaths += _paths(a.args)
        if not verbs:
            continue
        seen = set()
        for cp in cls_paths:
            for mp in (mpaths or [""]):
                for v in verbs:
                    key = (v, _join(cp, mp))
                    if key in seen:
                        continue
                    seen.add(key)
                    eps.append(Endpoint(v, key[1], f"{t.display}.{m.name}()", t.rel, m.line, m.doc,
                                        mkey(t, m.name), _security(t, m)))
    for a in t.annotations:
        if a.name == "WebServlet":
            for p in _paths(a.args) or [""]:
                eps.append(Endpoint("ANY", p or "/", f"{t.display} (servlet)", t.rel, t.line, t.doc))
    return eps


_SECURITY_ANNS = {"PreAuthorize", "PostAuthorize", "Secured", "RolesAllowed", "PermitAll", "DenyAll"}


def _security(t: JavaType, m: JavaMember) -> str:
    anns = [a for a in m.annotations + t.annotations if a.name in _SECURITY_ANNS]
    return "; ".join(f"@{a.name}" + (f"({a.args[:50]})" if a.args else "") for a in anns[:2])


def _url_matches(js_url: str, ep_path: str) -> bool:
    raw = js_url.strip()
    u = urlparse(raw).path if "://" in raw else raw.split("?")[0].split("#")[0]
    u = u.rstrip("/")
    e = ep_path.rstrip("/")
    if not u or not e or e == "/":
        return False
    pattern = re.sub(r"\\\{[^}]*\\\}", "[^/]+", re.escape(e.lstrip("/")))
    if re.search(r"(?:^|/)" + pattern + r"(?:\.\w+)?$", u.lstrip("/")):
        return True
    if raw.endswith(("/", "=")):                      # '/user/' + id style concatenation
        prefix = e.split("{")[0].rstrip("/")
        return bool(prefix) and u.endswith(prefix) and "{" in e
    return False


# -------------------------------------------------------------------- main
def build_knowledge(cfg: Config) -> Knowledge:
    files = scan(cfg)
    k = Knowledge(cfg=cfg, generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"), files=files)

    for f in files:
        try:
            if f.ext == ".js" and f.skipped == "vendor":
                k.js[f.rel] = JsInfo(vendor=True, vendor_note="by path/name")
                continue
            if f.skipped:
                k.warnings.append(f"`{f.rel}` skipped: {f.skipped}")
                continue
            if f.ext == ".java":
                k.java[f.rel] = parse_java(f.text, f.rel)
            elif f.ext == ".xml":
                k.xml[f.rel] = parse_xml(f.text, f.rel)
                if k.xml[f.rel].error:
                    k.warnings.append(f"`{f.rel}`: {k.xml[f.rel].error}")
            elif f.ext == ".properties":
                k.props[f.rel] = parse_properties(f.text, f.rel)
            elif f.ext == ".js":
                k.js[f.rel] = parse_js(f.text, f.rel)
        except Exception as exc:  # keep going; one bad file must not stop the run
            k.warnings.append(f"`{f.rel}`: parse failed ({type(exc).__name__}: {exc})")

    _analyze(k)
    return k


def _analyze(k: Knowledge) -> None:
    # ---- types, primary names, layers
    for rel, jf in k.java.items():
        k.types.extend(jf.types)
        tops = [t for t in jf.types if t.outer is None]
        k.primary_name[rel] = tops[0].name if tops else rel.rsplit("/", 1)[-1][:-5]
    k.types.sort(key=lambda t: (t.package, t.rel, t.line))
    for t in k.types:
        lay = layer_of(t)
        k.type_layer[t.qualified] = lay
        k.layers.setdefault(lay, []).append(t)

    # ---- technology evidence (files per tech)
    evidence: Dict[str, Set[str]] = defaultdict(set)
    for rel, jf in k.java.items():
        for imp in jf.imports + jf.static_imports:
            for prefix, tech in _TECH:
                if imp == prefix or imp.startswith(prefix + "."):
                    evidence[tech].add(rel)
                    break
    k.tech = sorted(((tech, len(fs)) for tech, fs in evidence.items()), key=lambda x: (-x[1], x[0]))

    # ---- endpoints + entry points
    for t in k.types:
        k.endpoints.extend(_type_endpoints(t))
        anns = {a.name for a in t.annotations}
        if "SpringBootApplication" in anns:
            k.entrypoints.append(("Spring Boot application", t.display, t.rel))
        for m in t.members:
            if m.kind == "method" and m.name == "main" and "static" in m.modifiers and "String" in m.signature:
                k.entrypoints.append(("main()", t.display, t.rel))
            for a in m.annotations:
                if a.name in _LISTENER_ANNS:
                    detail = f"{t.display}.{m.name}()" + (f" — `{a.args[:70]}`" if a.args else "")
                    k.entrypoints.append((_LISTENER_ANNS[a.name], detail, t.rel))
    for rel, info in k.xml.items():
        if info.kind == "web-xml":
            for name, cls, patterns in info.extra.get("servlets", []):
                simple = cls.rsplit(".", 1)[-1] if cls else name
                for p in patterns or [""]:
                    k.endpoints.append(Endpoint("ANY", p or "-", f"{simple} (servlet `{name}`)", rel, 0))
    k.endpoints.sort(key=lambda e: (e.path, e.http))

    # ---- file level dependency graph (Java -> Java)
    simple_index: Dict[str, List[JavaType]] = defaultdict(list)
    for t in k.types:
        if t.outer is None:
            simple_index[t.name].append(t)
    for rel, jf in k.java.items():
        own = {t.name for t in jf.types}
        exact = {i.rsplit(".", 1)[-1]: i for i in jf.imports if not i.endswith("*")}
        wild = [i[:-2] for i in jf.imports if i.endswith("*")]
        deps: Set[str] = set()
        for ident in jf.idents:
            if ident in own or ident not in simple_index:
                continue
            cands = simple_index[ident]
            if ident in exact:
                chosen = [c for c in cands if c.qualified == exact[ident]]
            else:
                chosen = [c for c in cands if c.package == jf.package] or \
                         [c for c in cands if c.package in wild]
            if chosen and chosen[0].rel != rel:
                deps.add(chosen[0].rel)
        k.file_deps[rel] = deps
    k.used_by = {rel: set() for rel in k.java}
    for rel, deps in k.file_deps.items():
        for d in deps:
            k.used_by.setdefault(d, set()).add(rel)

    # ---- tables, mapper <-> interface, bean wiring
    fqns = {t.qualified for t in k.types}
    for rel, info in k.xml.items():
        if info.kind == "mybatis-mapper":
            ns = info.extra.get("namespace", "")
            if ns in fqns:
                k.mapper_xml[ns] = rel
            for tb in info.extra.get("tables", []):
                k.tables.setdefault(tb, []).append(f"mapper `{ns.rsplit('.', 1)[-1] or rel}`")
        elif info.kind == "hibernate-mapping":
            for tb in info.extra.get("tables", []):
                k.tables.setdefault(tb, []).append(f"hibernate `{rel.rsplit('/', 1)[-1]}`")
        elif info.kind == "spring-beans":
            for bid, cls in info.extra.get("beans", []):
                if cls in fqns:
                    k.bean_refs.setdefault(cls, []).append(f"`{rel}` (bean `{bid or 'anonymous'}`)")
    for t in k.types:
        for a in t.annotations:
            if a.name == "Table":
                m = re.search(r'name\s*=\s*"([^"]+)"', a.args)
                if m:
                    k.tables.setdefault(m.group(1), []).append(f"entity `{t.display}`")
            elif a.name == "TableName" and a.args:
                m = re.search(r'"([^"]+)"', a.args)
                if m:
                    k.tables.setdefault(m.group(1), []).append(f"entity `{t.display}`")

    # ---- property key usage in Java code
    for rel, jf in k.java.items():
        for key in jf.prop_keys:
            k.prop_usage.setdefault(key, set()).add(k.primary_name.get(rel, rel))

    # ---- JavaScript calls -> Java endpoints
    for rel, info in k.js.items():
        for call in info.calls:
            matches = [e for e in k.endpoints
                       if e.http in ("ANY", call.verb, "AJAX") or call.verb in ("AJAX", "ANY")
                       if _url_matches(call.url, e.path)]
            k.js_calls.append((rel, call.verb, call.url, call.line, matches[:3]))

    _analyze_support(k)


# ------------------------------------------------- production-support analysis
_ENV_NAMES = ("dev", "develop", "development", "test", "testing", "qa", "uat", "stage", "staging", "prod",
              "production", "local", "sit", "preprod", "demo", "int")
_ENV_FILE = re.compile(r"^(?P<base>.+?)[-_.](?P<env>%s)\.properties$" % "|".join(_ENV_NAMES), re.I)


def _env_groups(k: Knowledge) -> Dict[str, Dict[str, str]]:
    """Group .properties files that are per-environment variants of the same configuration."""
    groups: Dict[str, Dict[str, str]] = {}
    for rel in k.props:
        d, _, name = rel.rpartition("/")
        base = env = None
        m = _ENV_FILE.match(name)
        if m:
            base = (d + "/" if d else "") + m.group("base") + ".properties"
            env = m.group("env").lower()
        else:
            parts = d.split("/") if d else []
            for i, seg in enumerate(parts):
                if seg.lower() in _ENV_NAMES:
                    base = "/".join(parts[:i] + ["*"] + parts[i + 1:] + [name])
                    env = seg.lower()
                    break
        if env and base:
            groups.setdefault(base, {})[env] = rel
    for base, envs in groups.items():
        if base in k.props:
            envs["default"] = base
    return {b: e for b, e in groups.items() if len(e) >= 2}


def _analyze_support(k: Knowledge) -> None:
    # string constants (error codes, message keys ...)
    for t in k.types:
        for m in t.members:
            if m.kind == "field" and "static" in m.modifiers and "final" in m.modifiers and m.init:
                lm = re.fullmatch(r'"((?:[^"\\]|\\.)*)"', m.init)
                if lm:
                    k.consts.setdefault(m.name, lm.group(1))
                    k.consts.setdefault(f"{t.name}.{m.name}", lm.group(1))
    for rel, p in k.props.items():
        for key, val in p.entries:
            k.props_flat.setdefault(key, []).append((rel, val))
    k.env_groups = _env_groups(k)

    k.cg = CallGraph(k)
    k.messages = build_messages(k)

    # where are message-bundle keys used in code?
    keys = set(k.props_flat)
    for t in k.types:
        for m in t.members:
            if m.kind not in ("method", "constructor"):
                continue
            for val, line in m.literals:
                if val in keys:
                    k.key_usage.setdefault(val, []).append((t.rel, f"{t.display}.{m.name}()", line))

    k.risks = collect_risks(k)
    if k.cfg.use_git:
        k.git = collect_git(k.cfg.root, k.cfg.git_days, {f.rel for f in k.files})
