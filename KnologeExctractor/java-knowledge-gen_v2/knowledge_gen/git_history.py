"""Optional read-only look at git history: what changed recently, and by whom."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional, Set

from .models import GitCommit, GitFile, GitInfo

_SEP = "@@KG@@"


def collect_git(root: Path, days: int, scanned: Set[str]) -> Optional[GitInfo]:
    """Return recent history for files under ``root`` (None when git/repo is unavailable)."""
    if days <= 0 or shutil.which("git") is None:
        return None
    base = ["git", "-C", str(root)]
    try:
        inside = subprocess.run(base + ["rev-parse", "--is-inside-work-tree"], capture_output=True,
                                text=True, timeout=15)
        if inside.returncode != 0 or inside.stdout.strip() != "true":
            return None
        out = subprocess.run(
            base + ["log", f"--since={days} days ago", "--no-merges", "--name-only", "--relative",
                    "--date=short", f"--pretty=format:{_SEP}%h|%ad|%an|%s", "--", "."],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None

    info = GitInfo(days=days)
    current: Optional[GitCommit] = None
    for line in out.stdout.splitlines():
        if line.startswith(_SEP):
            h, date, author, subject = (line[len(_SEP):].split("|", 3) + ["", "", "", ""])[:4]
            current = GitCommit(h, date, author, subject)
            info.commits.append(current)
        elif line.strip() and current is not None:
            current.files.append(line.strip())
            if line.strip() in scanned:
                gf = info.files.setdefault(line.strip(), GitFile())
                gf.commits += 1
                if gf.commits == 1:       # log is newest first
                    gf.last_hash, gf.last_date = current.hash, current.date
                    gf.last_author, gf.last_subject = current.author, current.subject
    return info
