"""Run-time configuration and scan defaults."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set

DEFAULT_EXTENSIONS = (".java", ".xml", ".properties", ".js")

# Directories that never contain hand-written project sources.
DEFAULT_IGNORE_DIRS = (
    "node_modules", "target", "build", "out", "bin", "dist", "classes",
    "__pycache__", "venv", ".venv", "bower_components",
)

# Directory names that hold third-party JavaScript.
VENDOR_DIRS = ("vendor", "vendors", "third_party", "thirdparty", "bower_components", "node_modules")

# Well-known library file names (jquery-3.6.0.js, bootstrap.bundle.js ...).
VENDOR_FILE_RE = re.compile(
    r"^(jquery|bootstrap|angular|react|vue|moment|lodash|underscore|popper|chart|"
    r"datatables|select2|fullcalendar|ckeditor|tinymce|highcharts|d3|require|backbone|"
    r"knockout|ext-all|dojo|prototype|mootools|swfobject|modernizr)[\w.\-]*\.js$",
    re.IGNORECASE,
)


@dataclass
class Config:
    root: Path
    output: Path
    title: str = ""
    extensions: Set[str] = field(default_factory=lambda: set(DEFAULT_EXTENSIONS))
    ignore_dirs: Set[str] = field(default_factory=lambda: set(DEFAULT_IGNORE_DIRS))
    excludes: List[str] = field(default_factory=list)   # fnmatch patterns
    max_file_bytes: int = 1_000_000
    include_private: bool = False
    include_vendor_js: bool = False
    max_methods: int = 25
    max_props_rows: int = 60
    include_index: bool = True
