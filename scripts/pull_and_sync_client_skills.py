#!/usr/bin/env python3
"""Fast-forward a clean agent-skills checkout and update already-installed skills."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import sync_client_skills as sync


class UpdateError(RuntimeError):
    """Raised when the checkout cannot be safely updated."""


@dataclass(frozen=True)
class Result:
    client: str | None
    skill: str
    state: str
    detail: str


def run_git(source_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(source_root), *args],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown Git error"
        raise UpdateError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def fast_forward_checkout(source_root: Path) -> tuple[str, str]:
    """Fast-forward a clean checkout and return its old and new revisions."""
    if run_git(source_root, "status", "--porcelain"):
        raise UpdateError("checkout has local changes; manage updates manually before running this helper")

    old_revision = run_git(source_root, "rev-parse", "HEAD")
    run_git(source_root, "pull", "--ff-only")
    return old_revision, run_git(source_root, "rev-parse", "HEAD")


def changed_skills(source_root: Path, old_revision: str, new_revision: str) -> tuple[set[str], set[str]]:
    """Return changed and removed top-level skill names between two revisions."""
    if old_revision == new_revision:
        return set(), set()

    available = set(sync.skill_sources(source_root, None))
    changed: set[str] = set()
    removed: set[str] = set()
    for line in run_git(source_root, "diff", "--name-status", old_revision, new_revision).splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, *paths = parts
        for raw_path in paths:
            path = Path(raw_path)
            if len(path.parts) < 2:
                continue
            skill = path.parts[0]
            if skill in available:
                changed.add(skill)
            elif status.startswith("D") and path.parts[1] == "SKILL.md":
                removed.add(skill)
    return changed, removed


def sync_installed_skills(
    source_root: Path,
    home_dir: Path,
    clients: Iterable[str],
    skills: Iterable[str],
) -> tuple[list[Result], list[str]]:
    """Synchronise changed skills already managed by this repository.

    A new skill is never installed merely because a Git update introduced it.
    Brain-managed, unmanaged, and modified destinations are reported but left
    unchanged.
    """
    selected_skills = tuple(skills)
    if not selected_skills:
        return [], []
    sources = sync.skill_sources(source_root, selected_skills)
    results: list[Result] = []
    errors: list[str] = []

    for client in clients:
        root = sync.skills_root(client, home_dir)
        for skill, source in sources.items():
            destination = root / skill
            status = sync.inspect_destination(client, skill, source, destination)

            if status.state == "stale":
                synced, sync_errors = sync.synchronise(
                    source_root,
                    home_dir,
                    (client,),
                    (skill,),
                    check=False,
                    dry_run=False,
                    replace=False,
                )
                results.extend(Result(item.client, item.skill, item.state, item.detail) for item in synced)
                errors.extend(sync_errors)
            elif status.state == "current":
                results.append(Result(client, skill, "current", "installed copy already matches source"))
            elif status.state == "missing":
                results.append(Result(client, skill, "not-installed", "not installed; skipped"))
            elif status.state == "brain-managed":
                results.append(Result(client, skill, "brain-managed", status.detail))
            else:
                results.append(Result(client, skill, "preserved", f"{status.detail}; left unchanged"))

    return results, errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", choices=(*sync.CLIENTS, "all"), default="all")
    parser.add_argument("--home", type=Path, default=Path.home(), help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    source_root = sync.repository_root()
    clients = sync.CLIENTS if args.client == "all" else (args.client,)

    try:
        old_revision, new_revision = fast_forward_checkout(source_root)
        changed, removed = changed_skills(source_root, old_revision, new_revision)
        results, errors = sync_installed_skills(source_root, args.home.expanduser(), clients, sorted(changed))
    except (UpdateError, sync.SyncError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if old_revision == new_revision:
        print("checkout: current — no Git update applied")
    elif not changed and not removed:
        print("checkout: updated — no skill packages changed")
    else:
        print(f"checkout: updated — {old_revision[:12]} -> {new_revision[:12]}")
    for result in results:
        print(f"{result.client}/{result.skill}: {result.state} — {result.detail}")
    for skill in sorted(removed):
        print(f"source/{skill}: removed — local copies left unchanged")
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
