"""Command line interface."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional

from . import __version__
from .analyzer import build_knowledge
from .config import DEFAULT_EXTENSIONS, Config
from .investigate import investigate
from .renderer import render


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="knowledge_gen",
        description="Generate knowledgeFile.md (a structured map of the code base) from a Java project "
                    "containing .java, .xml, .properties and .js files.",
    )
    p.add_argument("project", help="path to the project root directory")
    p.add_argument("-o", "--output", default="knowledgeFile.md", help="output file (default: knowledgeFile.md)")
    p.add_argument("--title", default="", help="project title shown in the file")
    p.add_argument("--ext", nargs="+", metavar="EXT",
                   help="extensions to scan (default: %s)" % " ".join(DEFAULT_EXTENSIONS))
    p.add_argument("--exclude", nargs="*", default=[], metavar="GLOB",
                   help="extra glob patterns to skip, e.g. 'src/test/*' '*Generated*'")
    p.add_argument("--include-private", action="store_true", help="list private methods too")
    p.add_argument("--include-vendor-js", action="store_true", help="analyse third-party/minified JS as well")
    p.add_argument("--max-methods", type=int, default=25, help="max methods listed per class (default 25)")
    p.add_argument("--max-props-rows", type=int, default=60, help="max keys listed per .properties file (default 60)")
    p.add_argument("--max-file-kb", type=int, default=1000, help="skip files larger than this (default 1000 KB)")
    p.add_argument("--no-index", action="store_true", help="omit the per-file index table")
    g = p.add_argument_group("production support")
    g.add_argument("--detail", choices=["brief", "normal", "full"], default="normal",
                   help="method detail in the class catalog: brief=none, normal=summary, full=all log/throw/catch events")
    g.add_argument("--no-git", action="store_true", help="do not read git history")
    g.add_argument("--git-days", type=int, default=90, help="days of git history to include (default 90)")
    g.add_argument("--include-debug-logs", action="store_true", help="index DEBUG log messages too")
    g.add_argument("--max-flows", type=int, default=200, help="max request flows rendered (default 200)")
    g.add_argument("--max-messages", type=int, default=800, help="max rows in the message index (default 800)")
    g.add_argument("--investigate", metavar="FILE", help="stack trace / log excerpt file ('-' = stdin); writes investigation.md")
    g.add_argument("--search", nargs="+", metavar="TEXT", default=[],
                   help="error texts, class names, keys or SQL names to locate in the code (added to investigation.md)")
    g.add_argument("--investigation-output", default="", help="output path (default: investigation.md next to --output)")
    p.add_argument("-q", "--quiet", action="store_true")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = _parser().parse_args(argv)
    root = Path(args.project)
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    exts = {e if e.startswith(".") else "." + e for e in (args.ext or DEFAULT_EXTENSIONS)}
    cfg = Config(
        root=root, output=Path(args.output), title=args.title, extensions={e.lower() for e in exts},
        excludes=list(args.exclude), max_file_bytes=args.max_file_kb * 1024,
        include_private=args.include_private, include_vendor_js=args.include_vendor_js,
        max_methods=args.max_methods, max_props_rows=args.max_props_rows, include_index=not args.no_index,
        detail=args.detail, use_git=not args.no_git, git_days=args.git_days,
        include_debug_logs=args.include_debug_logs, max_flows=args.max_flows, max_messages=args.max_messages,
        investigate_file=args.investigate or "", search_terms=list(args.search),
        investigation_output=args.investigation_output,
    )

    started = time.time()
    k = build_knowledge(cfg)
    text = render(k)
    cfg.output.parent.mkdir(parents=True, exist_ok=True)
    cfg.output.write_text(text, encoding="utf-8")

    if cfg.investigate_file or cfg.search_terms:
        if cfg.investigate_file == "-":
            evidence = sys.stdin.read()
        elif cfg.investigate_file:
            try:
                evidence = Path(cfg.investigate_file).read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                print(f"error: cannot read {cfg.investigate_file}: {exc}", file=sys.stderr)
                return 2
        else:
            evidence = ""
        inv_path = Path(cfg.investigation_output) if cfg.investigation_output else cfg.output.with_name("investigation.md")
        inv_path.write_text(investigate(k, evidence, cfg.search_terms), encoding="utf-8")
        if not args.quiet:
            print(f"Wrote {inv_path}", file=sys.stderr)

    if not args.quiet:
        print(f"Scanned {len(k.files)} files: {len(k.java)} java, {len(k.xml)} xml, "
              f"{len(k.props)} properties, {len(k.js)} js", file=sys.stderr)
        print(f"Found {len(k.types)} Java types, {len(k.endpoints)} endpoints, "
              f"{len(k.tables)} tables, {len(k.warnings)} warnings", file=sys.stderr)
        print(f"Wrote {cfg.output} ({len(text):,} chars, ~{len(text) // 4:,} tokens) "
              f"in {time.time() - started:.1f}s", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
