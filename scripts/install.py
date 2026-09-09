#!/usr/bin/env python3
"""Install or check a skill copy, preserving existing files in a backup."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import stat
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def is_link(path):
    try:
        return path.is_symlink() or bool(getattr(path.lstat(), 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except FileNotFoundError:
        return False


def inventory(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def install(source, target, check=False, replace=False):
    expected = inventory(source)
    if not expected or not (source / "SKILL.md").is_file():
        raise ValueError("Source is not a nonempty skill")
    # A live symlink/junction is already synchronized if it resolves to source.
    if target.exists() and target.resolve() == source.resolve():
        print(f"LINKED {target} -> {source}")
        return True
    if target.exists() and inventory(target) == expected:
        print(f"CURRENT {target}")
        return True
    if check:
        print(f"DRIFT {target}")
        return False
    if is_link(target):
        raise ValueError(f"Existing link targets a different source: {target}")
    if target.exists():
        if not replace:
            raise ValueError(f"Existing skill differs: {target}. Inspect it, then use --replace to back it up.")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = target.parent / ".install-backups" / f"{target.name}-{stamp}"
        backup.parent.mkdir(exist_ok=True)
        # Both paths are explicit, sibling paths within the selected installation root.
        if target.resolve().parent != target.parent.resolve() or backup.resolve().parent != (target.parent / ".install-backups").resolve():
            raise ValueError("Backup path escaped the installation root")
        target.rename(backup)
        print(f"BACKUP {backup}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    if inventory(target) != expected:
        raise ValueError(f"Installation verification failed: {target}")
    print(f"INSTALLED {target}")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=["claude", "codex", "both"], default="both")
    parser.add_argument("--target", type=Path, help="Explicit skill directory, overrides --agent")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    source = ROOT / "skills" / "dual-model-review"
    targets = [args.target.expanduser().absolute()] if args.target else []
    if not targets:
        if args.agent in {"claude", "both"}:
            targets.append(Path.home() / ".claude/skills/dual-model-review")
        if args.agent in {"codex", "both"}:
            targets.append(Path.home() / ".agents/skills/dual-model-review")
    try:
        outcomes = [install(source, p, args.check, args.replace) for p in targets]
        return 0 if all(outcomes) else 1
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
