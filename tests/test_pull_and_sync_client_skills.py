from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pull_and_sync_client_skills.py"
SPEC = importlib.util.spec_from_file_location("pull_and_sync_client_skills", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
HELPER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = HELPER
SPEC.loader.exec_module(HELPER)


def create_skill(root: Path, name: str, content: str = "initial") -> Path:
    skill = root / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test skill. Use when testing.\n---\n\n{content}\n",
        encoding="utf-8",
    )
    return skill


class PullAndSyncClientSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.source.mkdir()
        create_skill(self.source, "example")
        self.home = self.root / "home"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_refuses_a_dirty_checkout_before_pulling(self) -> None:
        with patch.object(HELPER, "run_git", return_value=" M SKILL.md") as run_git:
            with self.assertRaisesRegex(HELPER.UpdateError, "local changes"):
                HELPER.fast_forward_checkout(self.source)
        run_git.assert_called_once_with(self.source, "status", "--porcelain")

    def test_fast_forwards_a_clean_checkout(self) -> None:
        responses = iter(("", "old", "", "new"))
        with patch.object(HELPER, "run_git", side_effect=lambda *_: next(responses)) as run_git:
            self.assertEqual(("old", "new"), HELPER.fast_forward_checkout(self.source))
        self.assertEqual(
            [
                ((self.source, "status", "--porcelain"),),
                ((self.source, "rev-parse", "HEAD"),),
                ((self.source, "pull", "--ff-only"),),
                ((self.source, "rev-parse", "HEAD"),),
            ],
            run_git.call_args_list,
        )

    def test_identifies_changed_and_removed_skill_packages(self) -> None:
        with patch.object(
            HELPER,
            "run_git",
            return_value="M\texample/reference.md\nD\tretired/SKILL.md\nM\tREADME.md",
        ):
            changed, removed = HELPER.changed_skills(self.source, "old", "new")

        self.assertEqual({"example"}, changed)
        self.assertEqual({"retired"}, removed)

    def test_no_changed_skills_does_not_select_all_skills(self) -> None:
        with patch.object(HELPER.sync, "skill_sources") as skill_sources:
            results, errors = HELPER.sync_installed_skills(self.source, self.home, ("codex",), ())

        self.assertEqual(([], []), (results, errors))
        skill_sources.assert_not_called()

    def test_syncs_only_an_existing_managed_copy(self) -> None:
        HELPER.sync.synchronise(
            self.source,
            self.home,
            ("codex",),
            ("example",),
            check=False,
            dry_run=False,
            replace=False,
        )
        (self.source / "example" / "SKILL.md").write_text(
            "---\nname: example\ndescription: Test skill. Use when testing.\n---\n\nupdated\n",
            encoding="utf-8",
        )

        results, errors = HELPER.sync_installed_skills(
            self.source, self.home, ("codex", "claude"), ("example",)
        )

        self.assertEqual([], errors)
        self.assertEqual("synced", next(result for result in results if result.client == "codex").state)
        self.assertEqual("not-installed", next(result for result in results if result.client == "claude").state)
        self.assertFalse((self.home / ".claude" / "skills" / "example").exists())

    def test_leaves_a_brain_managed_copy_untouched(self) -> None:
        destination = self.home / ".codex" / "skills" / "example"
        destination.mkdir(parents=True)
        content = "Brain-managed adapter\n"
        (destination / "SKILL.md").write_text(content, encoding="utf-8")
        (destination / HELPER.sync.BRAIN_MARKER_NAME).write_text(
            json.dumps(
                {
                    "schema_version": HELPER.sync.BRAIN_MARKER_SCHEMA_VERSION,
                    "owner": HELPER.sync.BRAIN_MARKER_OWNER,
                    "kind": HELPER.sync.BRAIN_MARKER_KIND,
                    "skill": "example",
                    "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                }
            ),
            encoding="utf-8",
        )

        results, errors = HELPER.sync_installed_skills(
            self.source, self.home, ("codex",), ("example",)
        )

        self.assertEqual([], errors)
        self.assertEqual("brain-managed", results[0].state)
        self.assertEqual(content, (destination / "SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
