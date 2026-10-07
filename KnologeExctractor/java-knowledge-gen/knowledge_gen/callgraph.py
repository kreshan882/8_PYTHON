"""Call graph between project methods, entry points and external integrations.

Resolution is heuristic (no type checker): a call ``x.foo()`` is resolved through the declared
type of ``x`` (field, parameter or local variable), interfaces are mapped to their project
implementations, and MyBatis mapper methods are linked to their SQL statements.
"""

from __future__ import annotations

import re
from collections import defaultdict, deque
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple

from .models import Integration, JavaMember, JavaType, SqlStmt
from .parsers.xml_parser import _tables_from_sql

if TYPE_CHECKING:  # pragma: no cover
    from .analyzer import Knowledge

_INTEGRATION_TYPES: Dict[str, str] = {}
for _kind, _names in {
    "HTTP": "RestTemplate WebClient HttpClient CloseableHttpClient HttpURLConnection URLConnection OkHttpClient",
    "Database": "JdbcTemplate NamedParameterJdbcTemplate EntityManager SessionFactory Connection Statement "
                "PreparedStatement CallableStatement DataSource SqlSession SqlSessionTemplate HibernateTemplate",
    "Messaging": "KafkaTemplate RabbitTemplate AmqpTemplate JmsTemplate JmsMessagingTemplate StreamBridge",
    "Mail": "JavaMailSender JavaMailSenderImpl Transport",
    "Cache / Redis": "RedisTemplate StringRedisTemplate Jedis JedisPool CacheManager RedissonClient",
    "File / FTP": "FTPClient FTPSClient ChannelSftp JSch Files FileInputStream FileOutputStream FileReader "
                  "FileWriter RandomAccessFile",
    "Socket": "Socket ServerSocket DatagramSocket",
    "LDAP": "LdapTemplate DirContext InitialDirContext",
    "SOAP / WS": "WebServiceTemplate",
}.items():
    for _n in _names.split():
        _INTEGRATION_TYPES[_n] = _kind

_ANN_INTEGRATIONS = {"FeignClient": "HTTP", "KafkaListener": "Messaging", "RabbitListener": "Messaging",
                     "JmsListener": "Messaging", "WebService": "SOAP / WS", "WebServiceClient": "SOAP / WS"}
_SQL_ANNS = {"Select": "SELECT", "Insert": "INSERT", "Update": "UPDATE", "Delete": "DELETE", "Query": ""}
_SERVLET_METHODS = {"doGet": "GET", "doPost": "POST", "doPut": "PUT", "doDelete": "DELETE",
                    "service": "ANY", "execute": "ANY"}
_LISTENER_ANNS = {"Scheduled": "Scheduled job", "KafkaListener": "Kafka consumer",
                  "RabbitListener": "RabbitMQ consumer", "JmsListener": "JMS consumer",
                  "EventListener": "Event listener", "Schedule": "EJB timer"}


def mkey(t: JavaType, m_name: str) -> str:
    return f"{t.qualified}#{m_name}"


def _base(tname: str) -> str:
    return re.sub(r"<.*", "", tname).replace("[]", "").replace("...", "").strip()


class CallGraph:
    def __init__(self, k: "Knowledge") -> None:
        self.k = k
        self.type_by_q: Dict[str, JavaType] = {t.qualified: t for t in k.types}
        self._simple: Dict[str, List[JavaType]] = defaultdict(list)
        for t in k.types:
            self._simple[t.name].append(t)
        self._resolve_cache: Dict[Tuple[str, str], Optional[JavaType]] = {}
        self.impls: Dict[str, List[JavaType]] = defaultdict(list)
        self.members_by_key: Dict[str, List[Tuple[JavaType, JavaMember]]] = defaultdict(list)
        self.callees: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.callers: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.externals: Dict[str, List[Tuple[str, str, str, int]]] = defaultdict(list)
        self.sql_by_method: Dict[str, List[SqlStmt]] = defaultdict(list)
        self.entry_labels: Dict[str, List[str]] = defaultdict(list)
        self.integrations: List[Integration] = []
        self._entries_cache: Dict[str, List[str]] = {}
        self._tables_cache: Dict[str, Dict[str, str]] = {}
        self._build()

    # ------------------------------------------------------------ resolving
    def resolve(self, name: str, rel: str) -> Optional[JavaType]:
        base = _base(name)
        if not base:
            return None
        ck = (rel, base)
        if ck in self._resolve_cache:
            return self._resolve_cache[ck]
        found = self._resolve(base, rel)
        self._resolve_cache[ck] = found
        return found

    def _resolve(self, base: str, rel: str) -> Optional[JavaType]:
        if base in self.type_by_q:
            return self.type_by_q[base]
        simple = base.split(".")[-1]
        cands = self._simple.get(simple)
        if not cands:
            return None
        if "." in base:
            for c in cands:
                if c.qualified.endswith(base):
                    return c
        jf = self.k.java.get(rel)
        for c in cands:
            if c.rel == rel:
                return c
        if jf is None:
            return cands[0] if len(cands) == 1 else None
        exact = {i.rsplit(".", 1)[-1]: i for i in jf.imports if not i.endswith("*")}
        if simple in exact:
            for c in cands:
                if c.qualified == exact[simple]:
                    return c
        for c in cands:
            if c.package == jf.package:
                return c
        wild = [i[:-2] for i in jf.imports if i.endswith("*")]
        for c in cands:
            if c.package in wild:
                return c
        return None

    def supers(self, t: JavaType) -> List[JavaType]:
        out = []
        for s in t.extends + t.implements:
            r = self.resolve(s, t.rel)
            if r is not None and r is not t:
                out.append(r)
        return out

    def outers(self, t: JavaType) -> List[JavaType]:
        out = []
        cur = t
        while cur.outer:
            q = cur.qualified.rsplit(".", 1)[0]
            cur = self.type_by_q.get(q)
            if cur is None:
                break
            out.append(cur)
        return out

    def fields_of(self, t: JavaType) -> Dict[str, str]:
        fields: Dict[str, str] = {}
        seen: Set[str] = set()
        todo = [t] + self.outers(t)
        depth = 0
        while todo and depth < 5:
            nxt: List[JavaType] = []
            for cur in todo:
                if cur.qualified in seen:
                    continue
                seen.add(cur.qualified)
                for m in cur.members:
                    if m.kind == "field":
                        fields.setdefault(m.name, m.type_name)
                nxt.extend(self.supers(cur))
            todo = nxt
            depth += 1
        return fields

    def find_methods(self, t: JavaType, name: str, _depth: int = 0) -> List[Tuple[JavaType, JavaMember]]:
        res = [(t, m) for m in t.members if m.kind == "method" and m.name == name]
        if res or _depth >= 4:
            return res
        for s in self.supers(t):
            res = self.find_methods(s, name, _depth + 1)
            if res:
                return res
        return []

    def method_targets(self, t: JavaType, name: str) -> List[Tuple[JavaType, JavaMember]]:
        own = self.find_methods(t, name)
        impl_types = self.impls.get(t.qualified, [])
        if impl_types:
            res: List[Tuple[JavaType, JavaMember]] = []
            for it in impl_types:
                res.extend(self.find_methods(it, name))
            if res:
                return res
        return own

    # --------------------------------------------------------------- build
    def _build(self) -> None:
        k = self.k
        for t in k.types:
            for s in t.implements + t.extends:
                target = self.resolve(s, t.rel)
                if target is not None and target is not t:
                    self.impls[target.qualified].append(t)
            for m in t.members:
                if m.kind in ("method", "constructor"):
                    self.members_by_key[mkey(t, m.name)].append((t, m))

        self._collect_sql()
        self._collect_edges()
        self._collect_entries()
        self._collect_annotation_integrations()

    def _collect_sql(self) -> None:
        k = self.k
        for rel, info in k.xml.items():
            if info.kind != "mybatis-mapper":
                continue
            ns = info.extra.get("namespace", "")
            for s in info.extra.get("statements", []):
                self.sql_by_method[f"{ns}#{s['id']}"].append(
                    SqlStmt(s["tag"].upper(), list(s["tables"]), s["sql"], "mapper XML"))
        for t in k.types:
            for m in t.members:
                if m.kind != "method":
                    continue
                key = mkey(t, m.name)
                for a in m.annotations:
                    if a.name in _SQL_ANNS:
                        sql = " ".join(re.findall(r'"((?:[^"\\]|\\.)*)"', a.args))
                        if len(sql) > 8:
                            tag = _SQL_ANNS[a.name] or (re.match(r"\s*(\w+)", sql).group(1).upper())
                            tag = "SELECT" if tag in ("SELECT", "WITH", "FROM") else tag
                            self.sql_by_method[key].append(SqlStmt(tag, _tables_from_sql(sql), sql, f"@{a.name}"))
                for ev in m.events:
                    if ev.kind == "sql":
                        tag = "SELECT" if ev.level in ("SELECT", "WITH") else ev.level
                        tables = [x.strip() for x in ev.detail.split(",") if x.strip()]
                        self.sql_by_method[key].append(SqlStmt(tag, tables, ev.template, "embedded"))

    def _collect_edges(self) -> None:
        k = self.k
        seen_integ: Set[Tuple[str, str, str, str]] = set()

        def add_integration(kind: str, typ: str, where: str, detail: str, rel: str, line: int) -> None:
            key = (kind, typ, where, detail)
            if key in seen_integ:
                return
            seen_integ.add(key)
            self.integrations.append(Integration(kind, typ, where, detail, rel, line))

        for t in k.types:
            fields = self.fields_of(t)
            for f in t.members:
                if f.kind == "field":
                    kind = _INTEGRATION_TYPES.get(_base(f.type_name).split(".")[-1])
                    if kind:
                        add_integration(kind, _base(f.type_name), t.display, f"field `{f.name}`", t.rel, f.line)
            for m in t.members:
                if m.kind not in ("method", "constructor") or not m.calls:
                    continue
                caller = mkey(t, m.name)
                scope = dict(fields)
                scope.update({n: ty for ty, n in m.params})
                scope.update(m.locals)
                for c in m.calls:
                    targets: List[Tuple[JavaType, JavaMember]] = []
                    vtype = ""
                    if c.recv in ("", "this"):
                        for owner in [t] + self.outers(t):
                            targets = self.find_methods(owner, c.name)
                            if targets:
                                break
                    elif c.recv == "super":
                        for s in self.supers(t):
                            targets = self.find_methods(s, c.name)
                            if targets:
                                break
                    elif c.recv != "<chain>":
                        vtype = scope.get(c.recv, "")
                        T: Optional[JavaType] = None
                        if vtype:
                            T = self.resolve(vtype, t.rel)
                        elif c.recv[:1].isupper():
                            T = self.resolve(c.recv, t.rel)
                            vtype = c.recv
                        if T is not None:
                            targets = self.method_targets(T, c.name)
                            ann = next((a for a in T.annotations if a.name == "FeignClient"), None)
                            if ann is not None:
                                what = f"{c.name}()"
                                self.externals[caller].append(("HTTP", f"Feign {T.name}", what, c.line))
                                add_integration("HTTP", f"Feign {T.name}", f"{t.display}.{m.name}()",
                                                f"{c.name}()  {ann.args[:60]}", t.rel, c.line)
                    if vtype:
                        kind = _INTEGRATION_TYPES.get(_base(vtype).split(".")[-1])
                        if kind:
                            what = f"{c.name}({c.arg0})" if c.arg0 else f"{c.name}()"
                            self.externals[caller].append((kind, _base(vtype), what, c.line))
                            add_integration(kind, _base(vtype), f"{t.display}.{m.name}()", what, t.rel, c.line)
                    for owner, tm in targets:
                        callee = mkey(owner, tm.name)
                        if callee == caller and c.recv in ("", "this"):
                            continue                      # plain recursion adds no information
                        if all(x[0] != callee for x in self.callees[caller]):
                            self.callees[caller].append((callee, c.line))
                            self.callers[callee].append((caller, c.line))
        for lst in self.callees.values():
            lst.sort(key=lambda x: x[1])

    def _collect_entries(self) -> None:
        k = self.k
        servlet_patterns: Dict[str, List[str]] = {}
        for rel, info in k.xml.items():
            if info.kind == "web-xml":
                for name, cls, patterns in info.extra.get("servlets", []):
                    servlet_patterns[cls] = patterns
        for e in k.endpoints:
            if e.key:
                self._label(e.key, f"{e.http} {e.path}")
        for t in k.types:
            pats = servlet_patterns.get(t.qualified)
            for a in t.annotations:
                if a.name == "WebServlet":
                    pats = re.findall(r'"([^"]*)"', a.args) or pats
            is_servlet = pats is not None or any(_base(s).endswith("HttpServlet") for s in t.extends)
            for m in t.members:
                if m.kind != "method":
                    continue
                if m.name == "main" and "static" in m.modifiers:
                    self._label(mkey(t, m.name), "main()")
                for a in m.annotations:
                    if a.name in _LISTENER_ANNS:
                        arg = f" ({a.args[:50]})" if a.args else ""
                        self._label(mkey(t, m.name), f"{_LISTENER_ANNS[a.name]} {t.display}.{m.name}(){arg}")
                if is_servlet and m.name in _SERVLET_METHODS:
                    verb = _SERVLET_METHODS[m.name]
                    self._label(mkey(t, m.name), f"{verb} {', '.join(pats) if pats else t.display + ' (servlet)'}")

    def _label(self, key: str, label: str) -> None:
        if label not in self.entry_labels[key]:
            self.entry_labels[key].append(label)

    def _collect_annotation_integrations(self) -> None:
        seen = {(i.kind, i.type, i.where, i.detail) for i in self.integrations}
        for t in self.k.types:
            for a in t.annotations:
                kind = _ANN_INTEGRATIONS.get(a.name)
                if kind:
                    self._add(seen, kind, f"@{a.name}", t.display, a.args[:100], t.rel, t.line)
            for m in t.members:
                for a in m.annotations:
                    kind = _ANN_INTEGRATIONS.get(a.name)
                    if kind:
                        self._add(seen, kind, f"@{a.name}", f"{t.display}.{m.name}()", a.args[:100], t.rel, m.line)

    def _add(self, seen: Set, kind: str, typ: str, where: str, detail: str, rel: str, line: int) -> None:
        key = (kind, typ, where, detail)
        if key not in seen:
            seen.add(key)
            self.integrations.append(Integration(kind, typ, where, detail, rel, line))

    # ------------------------------------------------------------- queries
    def entries_of(self, key: str, limit: int = 4, max_depth: int = 8) -> List[str]:
        """Entry points (endpoints, jobs, listeners, main) from which ``key`` can be reached."""
        if key in self._entries_cache:
            return self._entries_cache[key]
        found: List[str] = []
        seen = {key}
        queue = deque([(key, 0)])
        while queue and len(found) < limit:
            node, depth = queue.popleft()
            for label in self.entry_labels.get(node, []):
                if label not in found:
                    found.append(label)
            if depth >= max_depth:
                continue
            for caller, _ in self.callers.get(node, []):
                if caller not in seen:
                    seen.add(caller)
                    queue.append((caller, depth + 1))
        self._entries_cache[key] = found[:limit]
        return self._entries_cache[key]

    def entry_paths(self, key: str, limit: int = 3, max_depth: int = 8) -> List[List[str]]:
        """Shortest call chains (entry -> ... -> key) that reach ``key``."""
        paths: List[List[str]] = []
        queue = deque([[key]])
        seen = {key}
        while queue and len(paths) < limit:
            path = queue.popleft()
            node = path[-1]
            if node in self.entry_labels:
                paths.append(list(reversed(path)))
                if len(paths) >= limit:
                    break
            if len(path) > max_depth:
                continue
            for caller, _ in self.callers.get(node, []):
                if caller not in seen:
                    seen.add(caller)
                    queue.append(path + [caller])
        return paths

    def tables_reached(self, key: str, max_depth: int = 8) -> Dict[str, str]:
        """table -> 'R' | 'W' | 'RW' for everything below ``key`` in the call graph."""
        if key in self._tables_cache:
            return self._tables_cache[key]
        result: Dict[str, str] = {}
        seen = {key}
        stack = [(key, 0)]
        while stack:
            node, depth = stack.pop()
            for s in self.sql_by_method.get(node, []):
                for tb in s.tables:
                    cur = result.get(tb, "")
                    if s.op not in cur:
                        result[tb] = "".join(sorted(cur + s.op, reverse=True))   # 'RW'
            if depth < max_depth:
                for callee, _ in self.callees.get(node, []):
                    if callee not in seen:
                        seen.add(callee)
                        stack.append((callee, depth + 1))
        self._tables_cache[key] = result
        return result

    def display(self, key: str) -> str:
        pair = self.members_by_key.get(key)
        if pair:
            t, m = pair[0]
            return f"{t.display}.{m.name}()"
        cls, _, name = key.rpartition("#")
        return f"{cls.rsplit('.', 1)[-1]}.{name}()"
