"""Plain data containers shared by parsers, analyzer and renderer."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class SourceFile:
    path: Path
    rel: str                 # posix path relative to the project root
    ext: str
    size: int
    text: str = ""
    lines: int = 0
    encoding: str = "utf-8"
    skipped: str = ""        # non-empty -> content was not loaded (reason)


# ----------------------------------------------------------------- Java
@dataclass
class Annotation:
    name: str
    args: str = ""
    start: int = 0
    end: int = 0


@dataclass
class Call:
    """A call site inside a method body (unresolved)."""
    recv: str                # '' unqualified | this | super | <chain> | variable / class name
    name: str
    line: int
    arg0: str = ""           # first argument when it is a string literal


@dataclass
class CodeEvent:
    """Something inside a method that matters when diagnosing production behaviour."""
    kind: str                # log | throw | catch | print | http | sql | hardcoded
    level: str = ""          # log level | exception type(s) | http status | url/ip/path
    template: str = ""       # message with {placeholders} for dynamic parts
    line: int = 0
    context: str = ""        # enclosing conditions, e.g. "catch (X e) › if (a == null)"
    detail: str = ""         # flags such as "rethrow", "swallowed", "stack trace NOT logged"
    literals: List[str] = field(default_factory=list)   # string literals used in the call
    idents: List[str] = field(default_factory=list)     # identifier arguments (constants)
    exc_logged: bool = True


@dataclass
class JavaMember:
    kind: str                # method | constructor | field
    name: str
    signature: str
    visibility: str          # public | protected | private | package
    modifiers: List[str]
    annotations: List[Annotation]
    line: int
    doc: str = ""
    type_name: str = ""      # return type (method) or declared type (field)
    end_line: int = 0
    params: List[Tuple[str, str]] = field(default_factory=list)      # (type, name)
    locals: Dict[str, str] = field(default_factory=dict)             # name -> type
    calls: List[Call] = field(default_factory=list)
    events: List[CodeEvent] = field(default_factory=list)
    complexity: int = 0
    loc: int = 0
    init: str = ""           # field initializer (shortened)
    throws: List[str] = field(default_factory=list)
    literals: List[Tuple[str, int]] = field(default_factory=list)    # merged string literals


@dataclass
class JavaType:
    kind: str                # class | interface | enum | record | annotation
    name: str
    package: str
    rel: str
    line: int
    qualified: str = ""
    display: str = ""        # Outer.Inner for nested types
    modifiers: List[str] = field(default_factory=list)
    annotations: List[Annotation] = field(default_factory=list)
    extends: List[str] = field(default_factory=list)
    implements: List[str] = field(default_factory=list)
    doc: str = ""
    outer: Optional[str] = None
    members: List[JavaMember] = field(default_factory=list)
    components: str = ""     # record components
    enum_constants: List[str] = field(default_factory=list)
    end_line: int = 0


@dataclass
class JavaFile:
    rel: str
    package: str = ""
    imports: List[str] = field(default_factory=list)
    static_imports: List[str] = field(default_factory=list)
    types: List[JavaType] = field(default_factory=list)
    idents: Set[str] = field(default_factory=set)
    prop_keys: Set[str] = field(default_factory=set)
    todos: List[Tuple[int, str]] = field(default_factory=list)       # (line, text)


# ------------------------------------------------------------------ XML
@dataclass
class XmlInfo:
    kind: str = "generic"
    root: str = ""
    summary: str = ""
    sections: Dict[str, List[str]] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)
    error: str = ""


# ----------------------------------------------------------- properties
@dataclass
class PropsInfo:
    entries: List[Tuple[str, str]] = field(default_factory=list)
    groups: List[Tuple[str, int]] = field(default_factory=list)
    is_i18n: bool = False
    duplicates: List[str] = field(default_factory=list)
    fingerprints: Dict[str, str] = field(default_factory=dict)       # key -> hash of raw value


# ----------------------------------------------------------- JavaScript
@dataclass
class JsFunction:
    name: str
    params: str
    line: int
    kind: str


@dataclass
class JsCall:
    verb: str
    url: str
    line: int


@dataclass
class JsInfo:
    description: str = ""
    vendor: bool = False
    vendor_note: str = ""
    functions: List[JsFunction] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    calls: List[JsCall] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)


# ------------------------------------------------- derived (analysis) data
@dataclass
class SqlStmt:
    tag: str                 # SELECT | INSERT | UPDATE | DELETE | OTHER
    tables: List[str]
    sql: str
    source: str              # "mapper XML" | "@Select" | "embedded"

    @property
    def op(self) -> str:
        return "R" if self.tag == "SELECT" else "W"


@dataclass
class MessageSite:
    """A log statement, thrown exception or error response, with where it lives."""
    kind: str                # LOG | THROW | HTTP
    level: str               # ERROR/WARN/INFO/DEBUG | exception type | status
    template: str
    rel: str
    cls: str
    method: str
    line: int
    context: str = ""
    detail: str = ""
    entries: List[str] = field(default_factory=list)   # entry points that can reach it
    resolved: str = ""       # text of a message-bundle key used by the call
    exc_logged: bool = True
    key: str = ""            # method key (Class#method)


@dataclass
class Integration:
    kind: str                # HTTP | Database | Messaging | Mail | Cache | File/FTP | Socket | LDAP | SOAP
    type: str
    where: str
    detail: str = ""
    rel: str = ""
    line: int = 0


@dataclass
class GitFile:
    commits: int = 0
    last_hash: str = ""
    last_date: str = ""
    last_author: str = ""
    last_subject: str = ""


@dataclass
class GitCommit:
    hash: str
    date: str
    author: str
    subject: str
    files: List[str] = field(default_factory=list)


@dataclass
class GitInfo:
    days: int
    files: Dict[str, GitFile] = field(default_factory=dict)
    commits: List[GitCommit] = field(default_factory=list)
