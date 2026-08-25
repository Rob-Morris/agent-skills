#!/usr/bin/env python3
"""Synchronise this repository's skills to local Codex and Claude skill roots."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


MARKER_NAME = ".agent-skills-install.json"
BRAIN_MARKER_NAME = ".brain-agent-skill.json"
BRAIN_MARKER_OWNER = "obsidian-brain"
BRAIN_MARKER_KIND = "active-brain-skill-adapter"
BRAIN_MARKER_SCHEMA_VERSION = 1
BACKUP_DIR_NAME = ".agent-skills-backups"
SCHEMA_VERSION = 1
CLIENTS = ("claude", "codex")


class SyncError(RuntimeError):
    """Raised when a destination cannot be safely synchronised."""


@dataclass(frozen=True)
class DestinationStatus:
    client: str
    skill: str
    path: Path
    state: str
    detail: str


def path_present(path: Path) -> bool:
    """Return whether a directory entry exists, including a dangling symlink."""
    return path.exists() or path.is_symlink()


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def source_revision(source_root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def skill_sources(source_root: Path, selected: Iterable[str] | None) -> dict[str, Path]:
    available = {
        path.name: path
        for path in source_root.iterdir()
        if path.is_dir() and not path.name.startswith(".") and (path / "SKILL.md").is_file()
    }
    wanted = sorted(set(selected or available))
    missing = [name for name in wanted if name not in available]
    if missing:
        raise SyncError(f"unknown skill(s): {', '.join(missing)}")
    return {name: available[name] for name in wanted}


def skills_root(client: str, home_dir: Path) -> Path:
    if client == "claude":
        return home_dir / ".claude" / "skills"
    if client == "codex":
        codex_home = os.environ.get("CODEX_HOME")
        return Path(codex_home).expanduser() / "skills" if codex_home else home_dir / ".codex" / "skills"
    raise SyncError(f"unsupported client: {client}")


def iter_content_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == MARKER_NAME:
            continue
        if "__pycache__" in path.parts or path.name in {".DS_Store", "Thumbs.db"}:
            continue
        yield path


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in iter_content_files(root):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        content = path.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def read_marker(skill_dir: Path) -> dict | None:
    marker_path = skill_dir / MARKER_NAME
    if not marker_path.is_file():
        return None
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(f"invalid ownership marker at {marker_path}: {exc}") from exc
    if not isinstance(marker, dict) or marker.get("schema_version") != SCHEMA_VERSION:
        raise SyncError(f"unrecognised ownership marker at {marker_path}")
    return marker


def inspect_brain_marker(skill_dir: Path, skill: str) -> str | None:
    """Return a Brain-management detail, or raise when its marker is unsafe."""
    marker_path = skill_dir / BRAIN_MARKER_NAME
    if not path_present(marker_path):
        return None
    if not marker_path.is_file():
        raise SyncError(f"invalid Brain ownership marker at {marker_path}")
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(f"invalid Brain ownership marker at {marker_path}: {exc}") from exc

    expected = {
        "schema_version": BRAIN_MARKER_SCHEMA_VERSION,
        "owner": BRAIN_MARKER_OWNER,
        "kind": BRAIN_MARKER_KIND,
        "skill": skill,
    }
    if not isinstance(marker, dict) or any(marker.get(key) != value for key, value in expected.items()):
        raise SyncError(f"unrecognised Brain ownership marker at {marker_path}")

    recorded_hash = marker.get("content_sha256")
    if not isinstance(recorded_hash, str) or len(recorded_hash) != 64:
        raise SyncError(f"invalid Brain ownership digest at {marker_path}")
    try:
        int(recorded_hash, 16)
    except ValueError as exc:
        raise SyncError(f"invalid Brain ownership digest at {marker_path}") from exc

    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        raise SyncError(f"Brain-managed skill is missing {skill_file}")
    actual_hash = hashlib.sha256(skill_file.read_bytes()).hexdigest()
    if actual_hash != recorded_hash:
        raise SyncError(f"Brain-managed skill content differs from marker at {skill_file}")
    return "managed by Obsidian Brain"


def inspect_destination(
    client: str,
    skill: str,
    source: Path,
    destination: Path,
) -> DestinationStatus:
    if not path_present(destination):
        return DestinationStatus(client, skill, destination, "missing", "not installed")
    if destination.is_symlink() or not destination.is_dir():
        return DestinationStatus(client, skill, destination, "unmanaged", "not a managed skill directory")

    try:
        brain_detail = inspect_brain_marker(destination, skill)
    except SyncError as exc:
        return DestinationStatus(client, skill, destination, "invalid-brain-managed", str(exc))
    if brain_detail is not None:
        return DestinationStatus(client, skill, destination, "brain-managed", brain_detail)

    marker = read_marker(destination)
    if marker is None:
        return DestinationStatus(client, skill, destination, "unmanaged", "no ownership marker")

    installed_hash = tree_hash(destination)
    recorded_hash = marker.get("content_sha256")
    if installed_hash != recorded_hash:
        return DestinationStatus(client, skill, destination, "modified", "installed content differs from marker")

    source_hash = tree_hash(source)
    if source_hash == installed_hash:
        return DestinationStatus(client, skill, destination, "current", "matches source")
    return DestinationStatus(client, skill, destination, "stale", "managed copy differs from source")


def marker_for(source_root: Path, source: Path, client: str) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "owner": "agent-skills",
        "skill": source.name,
        "client": client,
        "source_revision": source_revision(source_root),
        "content_sha256": tree_hash(source),
        "installed_at": datetime.now(timezone.utc).isoformat(),
    }


def write_skill(source_root: Path, source: Path, client: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{source.name}.sync-", dir=destination.parent))
    try:
        staged_skill = temporary / source.name
        shutil.copytree(source, staged_skill, ignore=shutil.ignore_patterns(MARKER_NAME, "__pycache__", ".DS_Store", "Thumbs.db"))
        (staged_skill / MARKER_NAME).write_text(
            json.dumps(marker_for(source_root, source, client), indent=2) + "\n",
            encoding="utf-8",
        )
        if path_present(destination):
            if destination.is_symlink() or destination.is_file():
                destination.unlink()
            else:
                shutil.rmtree(destination)
        staged_skill.replace(destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def archive_destination(destination: Path) -> Path:
    backup_root = destination.parent.parent / BACKUP_DIR_NAME
    backup_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = backup_root / f"{destination.name}-{stamp}"
    suffix = 2
    while path_present(backup):
        backup = backup_root / f"{destination.name}-{stamp}-{suffix}"
        suffix += 1
    shutil.move(str(destination), str(backup))
    return backup


def synchronise(
    source_root: Path,
    home_dir: Path,
    clients: Iterable[str],
    selected_skills: Iterable[str] | None,
    *,
    check: bool,
    dry_run: bool,
    replace: bool,
) -> tuple[list[DestinationStatus], list[str]]:
    sources = skill_sources(source_root, selected_skills)
    statuses: list[DestinationStatus] = []
    errors: list[str] = []

    for client in clients:
        root = skills_root(client, home_dir)
        for skill, source in sources.items():
            destination = root / skill
            status = inspect_destination(client, skill, source, destination)
            statuses.append(status)
            if check or status.state in {"current", "brain-managed"}:
                continue

            if status.state == "invalid-brain-managed":
                errors.append(f"{client}/{skill}: {status.detail}; left unchanged")
                continue
            if status.state in {"unmanaged", "modified"} and not replace:
                errors.append(
                    f"{client}/{skill}: {status.detail}; rerun with --replace to archive it before installing"
                )
                continue
            if dry_run:
                continue

            backup: Path | None = None
            if path_present(destination) and status.state in {"unmanaged", "modified"}:
                backup = archive_destination(destination)
            write_skill(source_root, source, client, destination)
            if backup is not None:
                detail = f"archived previous copy to {backup} and installed current source"
            elif status.state == "stale":
                detail = "updated managed copy from source"
            else:
                detail = "installed current source"
            statuses[-1] = DestinationStatus(client, skill, destination, "synced", detail)

    return statuses, errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", choices=(*CLIENTS, "all"), default="all")
    parser.add_argument("--skill", action="append", dest="skills", help="Skill directory to synchronise; repeatable")
    parser.add_argument("--check", action="store_true", help="Report whether installed skills match without changing anything")
    parser.add_argument("--dry-run", action="store_true", help="Show planned changes without writing")
    parser.add_argument("--replace", action="store_true", help="Archive unmanaged or locally modified destinations before installing")
    parser.add_argument("--home", type=Path, default=Path.home(), help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def reported_action(status: DestinationStatus, *, dry_run: bool, replace: bool) -> str:
    if not dry_run:
        return status.state
    if status.state in {"missing", "stale"}:
        return "would sync"
    if status.state in {"unmanaged", "modified"} and replace:
        return "would archive and sync"
    return status.state


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.check and args.dry_run:
        print("--check and --dry-run cannot be combined", file=sys.stderr)
        return 2

    clients = CLIENTS if args.client == "all" else (args.client,)
    try:
        statuses, errors = synchronise(
            repository_root(),
            args.home.expanduser(),
            clients,
            args.skills,
            check=args.check,
            dry_run=args.dry_run,
            replace=args.replace,
        )
    except SyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    for status in statuses:
        action = reported_action(status, dry_run=args.dry_run, replace=args.replace)
        print(f"{status.client}/{status.skill}: {action} — {status.detail}")
    for error in errors:
        print(f"error: {error}", file=sys.stderr)

    if errors:
        return 2
    if args.check and any(status.state not in {"current", "brain-managed"} for status in statuses):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
