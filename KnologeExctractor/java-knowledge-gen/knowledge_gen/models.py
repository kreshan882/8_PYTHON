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


@dataclass
class JavaFile:
    rel: str
    package: str = ""
    imports: List[str] = field(default_factory=list)
    static_imports: List[str] = field(default_factory=list)
    types: List[JavaType] = field(default_factory=list)
    idents: Set[str] = field(default_factory=set)
    prop_keys: Set[str] = field(default_factory=set)


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
