"""Walk the project tree and load candidate source files."""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import List, Tuple

from .config import VENDOR_DIRS, VENDOR_FILE_RE, Config
from .models import SourceFile


def read_text(path: Path) -> Tuple[str, str]:
    """Decode a file: UTF-8 (with/without BOM) first, then cp1252 as a fallback."""
    data = path.read_bytes()
    try:
        return data.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace"), "cp1252"


def _excluded(rel: str, name: str, patterns: List[str]) -> bool:
    return any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(name, p) for p in patterns)


def _is_vendor_js(rel: str, name: str) -> bool:
    parts = rel.lower().split("/")
    if name.lower().endswith(".min.js"):
        return True
    if any(p in VENDOR_DIRS for p in parts[:-1]):
        return True
    return bool(VENDOR_FILE_RE.match(name))


def scan(cfg: Config) -> List[SourceFile]:
    root = cfg.root.resolve()
    found: List[SourceFile] = []

    for dirpath, dirnames, filenames in os.walk(root):
        drel = Path(dirpath).relative_to(root).as_posix()
        keep = []
        for d in sorted(dirnames):
            if d.startswith(".") or d in cfg.ignore_dirs:
                continue
            sub = d if drel == "." else f"{drel}/{d}"
            if _excluded(sub, d, cfg.excludes):
                continue
            keep.append(d)
        dirnames[:] = keep

        for name in sorted(filenames):
            ext = os.path.splitext(name)[1].lower()
            if ext not in cfg.extensions:
                continue
            path = Path(dirpath) / name
            rel = path.relative_to(root).as_posix()
            if _excluded(rel, name, cfg.excludes):
                continue
            try:
                size = path.stat().st_size
            except OSError:
                continue

            sf = SourceFile(path=path, rel=rel, ext=ext, size=size)

            if ext == ".js" and not cfg.include_vendor_js and _is_vendor_js(rel, name):
                sf.skipped = "vendor"
                sf.lines = path.read_bytes().count(b"\n") + 1
            elif size > cfg.max_file_bytes:
                sf.skipped = f"larger than {cfg.max_file_bytes} bytes"
            else:
                try:
                    sf.text, sf.encoding = read_text(path)
                    sf.lines = sf.text.count("\n") + (0 if sf.text.endswith("\n") or not sf.text else 1)
                except OSError as exc:
                    sf.skipped = f"unreadable ({exc})"
            found.append(sf)

    found.sort(key=lambda f: f.rel)
    return found
