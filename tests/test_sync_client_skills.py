from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_client_skills.py"
SPEC = importlib.util.spec_from_file_location("sync_client_skills", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
SYNC = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SYNC
SPEC.loader.exec_module(SYNC)


def create_skill(root: Path, name: str, content: str = "initial") -> Path:
    skill = root / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test skill. Use when testing.\n---\n\n{content}\n",
        encoding="utf-8",
    )
    (skill / "reference.md").write_text("supporting material\n", encoding="utf-8")
    return skill


class SyncClientSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.source.mkdir()
        create_skill(self.source, "example")
        self.home = self.root / "home"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def sync(self, **overrides: bool) -> tuple[list[object], list[str]]:
        return SYNC.synchronise(
            self.source,
            self.home,
            ("codex", "claude"),
            ["example"],
            check=overrides.get("check", False),
            dry_run=overrides.get("dry_run", False),
            replace=overrides.get("replace", False),
        )

    def test_installs_and_checks_both_clients(self) -> None:
        self.sync()
        statuses, errors = self.sync(check=True)

        self.assertEqual([], errors)
        self.assertTrue(all(status.state == "current" for status in statuses))
        self.assertTrue((self.home / ".codex" / "skills" / "example" / SYNC.MARKER_NAME).is_file())
        self.assertTrue((self.home / ".claude" / "skills" / "example" / SYNC.MARKER_NAME).is_file())

    def test_updates_a_managed_stale_copy(self) -> None:
        self.sync()
        (self.source / "example" / "SKILL.md").write_text(
            "---\nname: example\ndescription: Test skill. Use when testing.\n---\n\nupdated\n",
            encoding="utf-8",
        )

        statuses, errors = self.sync(check=True)
        self.assertEqual([], errors)
        self.assertTrue(all(status.state == "stale" for status in statuses))

        self.sync()
        statuses, errors = self.sync(check=True)
        self.assertEqual([], errors)
        self.assertTrue(all(status.state == "current" for status in statuses))

    def test_preserves_modified_copy_until_replace_is_requested(self) -> None:
        self.sync()
        installed = self.home / ".codex" / "skills" / "example" / "SKILL.md"
        installed.write_text("locally modified\n", encoding="utf-8")

        _, errors = self.sync()
        self.assertEqual(1, len(errors))
        self.assertIn("--replace", errors[0])

        self.sync(replace=True)
        backups = list((self.home / ".codex" / SYNC.BACKUP_DIR_NAME).iterdir())
        self.assertEqual(1, len(backups))
        self.assertTrue((backups[0] / "SKILL.md").is_file())

    def test_never_replaces_a_brain_managed_skill(self) -> None:
        destination = self.home / ".codex" / "skills" / "example"
        destination.mkdir(parents=True)
        content = "Brain-managed adapter\n"
        (destination / "SKILL.md").write_text(content, encoding="utf-8")
        (destination / SYNC.BRAIN_MARKER_NAME).write_text(
            json.dumps(
                {
                    "schema_version": SYNC.BRAIN_MARKER_SCHEMA_VERSION,
                    "owner": "obsidian-brain",
                    "kind": "active-brain-skill-adapter",
                    "skill": "example",
                    "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                }
            ),
            encoding="utf-8",
        )

        statuses, errors = self.sync(replace=True)
        codex_status = next(status for status in statuses if status.client == "codex")
        self.assertEqual("brain-managed", codex_status.state)
        self.assertEqual([], errors)
        self.assertEqual(content, (destination / "SKILL.md").read_text(encoding="utf-8"))

        statuses, errors = self.sync(check=True)
        self.assertEqual([], errors)
        self.assertEqual("brain-managed", next(status for status in statuses if status.client == "codex").state)

    def test_refuses_an_invalid_brain_managed_skill(self) -> None:
        destination = self.home / ".codex" / "skills" / "example"
        destination.mkdir(parents=True)
        (destination / SYNC.BRAIN_MARKER_NAME).write_text("{}\n", encoding="utf-8")

        statuses, errors = self.sync(replace=True)
        codex_status = next(status for status in statuses if status.client == "codex")
        self.assertEqual("invalid-brain-managed", codex_status.state)
        self.assertEqual(1, len(errors))
        self.assertTrue((destination / SYNC.BRAIN_MARKER_NAME).is_file())

    def test_replaces_a_dangling_symlink_only_with_replace(self) -> None:
        destination = self.home / ".codex" / "skills" / "example"
        destination.parent.mkdir(parents=True)
        try:
            destination.symlink_to(self.root / "missing-skill", target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"symbolic links are unavailable: {exc}")

        statuses, errors = self.sync()
        codex_status = next(status for status in statuses if status.client == "codex")
        self.assertEqual("unmanaged", codex_status.state)
        self.assertEqual(1, len(errors))
        self.assertTrue(destination.is_symlink())

        self.sync(replace=True)
        self.assertTrue(destination.is_dir())
        self.assertTrue((destination / SYNC.MARKER_NAME).is_file())
        backups = list((self.home / ".codex" / SYNC.BACKUP_DIR_NAME).iterdir())
        self.assertEqual(1, len(backups))
        self.assertTrue(backups[0].is_symlink())

    def test_dry_run_reports_only_planned_operations(self) -> None:
        status = SYNC.DestinationStatus("codex", "example", Path("example"), "unmanaged", "no ownership marker")
        self.assertEqual("unmanaged", SYNC.reported_action(status, dry_run=True, replace=False))
        self.assertEqual("would archive and sync", SYNC.reported_action(status, dry_run=True, replace=True))

        brain_managed = SYNC.DestinationStatus("codex", "example", Path("example"), "brain-managed", "managed by Obsidian Brain")
        self.assertEqual("brain-managed", SYNC.reported_action(brain_managed, dry_run=True, replace=True))

        stale = SYNC.DestinationStatus("codex", "example", Path("example"), "stale", "managed copy differs from source")
        self.assertEqual("would sync", SYNC.reported_action(stale, dry_run=True, replace=False))

    def test_completed_install_reports_the_action_taken(self) -> None:
        destination = self.home / ".codex" / "skills" / "example"
        destination.mkdir(parents=True)
        (destination / "SKILL.md").write_text("previous copy\n", encoding="utf-8")
        output = io.StringIO()

        with (
            patch.object(SYNC, "repository_root", return_value=self.source),
            patch.dict(SYNC.os.environ, {"CODEX_HOME": ""}),
            contextlib.redirect_stdout(output),
        ):
            exit_code = SYNC.main(
                ["--client", "codex", "--home", str(self.home), "--skill", "example", "--replace"]
            )

        self.assertEqual(0, exit_code)
        self.assertIn("codex/example: synced — archived previous copy to ", output.getvalue())
        self.assertIn(" and installed current source", output.getvalue())
        self.assertNotIn(": unmanaged —", output.getvalue())


if __name__ == "__main__":
    unittest.main()
