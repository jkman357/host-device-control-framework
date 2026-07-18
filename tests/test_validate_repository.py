#!/usr/bin/env python3
"""Regression tests for repository validation failure and pass modes."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_RELATIVE_PATH = Path("tools/validate_repository.py")
WORKFLOW_RELATIVE_PATH = Path(".github/workflows/document-validation.yml")


class RepositoryValidatorRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.repository = Path(cls.temporary.name) / "repository"
        shutil.copytree(
            REPOSITORY_ROOT,
            cls.repository,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def backup_path(self, relative: str | Path) -> Path:
        target = self.repository / relative
        existed = target.exists()
        original = target.read_bytes() if existed and target.is_file() else None

        def restore() -> None:
            if existed:
                target.parent.mkdir(parents=True, exist_ok=True)
                if original is not None:
                    target.write_bytes(original)
            elif target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
                parent = target.parent
                while parent != self.repository and parent.exists() and not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent

        self.addCleanup(restore)
        return target

    def run_validator(self, repository: Path | None = None) -> subprocess.CompletedProcess[str]:
        selected = repository or self.repository
        return subprocess.run(
            [sys.executable, str(selected / VALIDATOR_RELATIVE_PATH)],
            cwd=selected,
            text=True,
            capture_output=True,
            check=False,
        )

    def assert_validator_fails(self, expected: str) -> None:
        result = self.run_validator()
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn(expected, output)

    def assert_validator_passes(self, repository: Path | None = None) -> None:
        result = self.run_validator(repository)
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("Repository validation: PASS", result.stdout)

    def test_current_repository_passes(self) -> None:
        self.assert_validator_passes(REPOSITORY_ROOT)

    def test_metadata_omission_cannot_escape_governance(self) -> None:
        repository = self.repository
        target = self.backup_path("docs/coding-rules/Metadata_Escape.md")
        target.write_text("# Metadata Escape\n\nThis file intentionally omits authority metadata.\n", encoding="utf-8")
        self.assert_validator_fails("every governed Markdown document under docs must declare")

    def test_metadata_inside_fence_does_not_satisfy_governance(self) -> None:
        repository = self.repository
        target = self.backup_path("docs/coding-rules/Fenced_Metadata.md")
        target.write_text(
            "# Fenced Metadata\n\n"
            "```markdown\n"
            "**Canonical Filename:** `Fenced_Metadata.md`\n"
            "**Document Version:** v1.0.0\n"
            "**Status:** Draft for Review\n"
            "## Version History\n"
            "| Version | Date | Status | Summary |\n"
            "|---|---|---|---|\n"
            "| v1.0.0 | 2026-07-19 | Draft for Review | Example only. |\n"
            "```\n",
            encoding="utf-8",
        )
        self.assert_validator_fails("every governed Markdown document under docs must declare")

    def test_duplicate_metadata_is_rejected(self) -> None:
        repository = self.repository
        target = self.backup_path("docs/validation/Repository_Validation_Checklist.md")
        text = target.read_text(encoding="utf-8").replace(
            "**Document Version:** v1.0.3",
            "**Document Version:** v1.0.3\n**Document Version:** v1.0.3",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("metadata key 'Document Version' must appear exactly once")

    def test_version_history_inside_fence_is_ignored(self) -> None:
        repository = self.repository
        target = self.backup_path("docs/coding-rules/CSharp_Coding_Rules.md")
        text = target.read_text(encoding="utf-8")
        start = text.index("## Version History")
        next_heading = re.search(r"^# Part ", text[start:], re.MULTILINE)
        self.assertIsNotNone(next_heading)
        end = start + next_heading.start()
        text = text[:start] + "```markdown\n" + text[start:end] + "```\n\n" + text[end:]
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("exactly one Version History or Change History heading is required; found 0")

    def test_fenced_current_document_set_is_ignored(self) -> None:
        repository = self.repository
        target = self.backup_path("README.md")
        text = target.read_text(encoding="utf-8")
        heading = text.index("## Current Document Set")
        next_heading = text.index("## AI Task Routing", heading)
        text = text[:heading] + "```markdown\n" + text[heading:next_heading] + "```\n\n" + text[next_heading:]
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("Current Document Set table is missing or empty")

    def test_missing_supersedes_is_rejected_for_non_initial_version(self) -> None:
        repository = self.repository
        target = self.backup_path("docs/framework/AI_Engineering_Usage_Guide.md")
        text = re.sub(r"^\*\*Supersedes Document Version:\*\*.*\n", "", target.read_text(encoding="utf-8"), count=1, flags=re.MULTILINE)
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("Supersedes Document Version is required when Version History has multiple entries")

    def test_invalid_document_version_format_is_rejected(self) -> None:
        repository = self.repository
        target = self.backup_path("docs/validation/Repository_Validation_Checklist.md")
        text = target.read_text(encoding="utf-8").replace(
            "**Document Version:** v1.0.3",
            "**Document Version:** 1.0.3",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("must match vMAJOR.MINOR.PATCH")

    def test_stale_current_version_is_rejected(self) -> None:
        repository = self.repository
        target = self.backup_path("docs/validation/Repository_Validation_Checklist.md")
        text = target.read_text(encoding="utf-8").replace(
            "**Document Version:** v1.0.3",
            "**Document Version:** v1.0.2",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("must be the highest Version History version")

    def test_unknown_supersedes_version_is_rejected(self) -> None:
        repository = self.repository
        target = self.backup_path("docs/framework/AI_Engineering_Usage_Guide.md")
        text = target.read_text(encoding="utf-8").replace(
            "**Supersedes Document Version:** v1.0.13",
            "**Supersedes Document Version:** v9.9.9",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("is not present in Version History")

    def test_non_immediate_supersedes_version_is_rejected(self) -> None:
        repository = self.repository
        target = self.backup_path("docs/framework/AI_Engineering_Usage_Guide.md")
        text = target.read_text(encoding="utf-8").replace(
            "**Supersedes Document Version:** v1.0.13",
            "**Supersedes Document Version:** v1.0.11",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("must identify the immediate prior listed version v1.0.13")

    def test_invalid_workflow_yaml_is_rejected(self) -> None:
        repository = self.repository
        target = self.backup_path(WORKFLOW_RELATIVE_PATH)
        target.write_text("jobs:\n  invalid: [\n", encoding="utf-8")
        self.assert_validator_fails("invalid YAML")

    def test_comment_only_workflow_tokens_are_rejected(self) -> None:
        repository = self.repository
        target = self.backup_path(WORKFLOW_RELATIVE_PATH)
        target.write_text(
            "# actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0\n"
            "# actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1\n"
            "# python tools/validate_repository.py\n"
            "on:\n  push:\n  pull_request:\npermissions:\n  contents: read\njobs: {}\n",
            encoding="utf-8",
        )
        self.assert_validator_fails("one ubuntu-latest job must contain")

    def test_unpinned_checkout_action_is_rejected(self) -> None:
        repository = self.repository
        target = self.backup_path(WORKFLOW_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0",
            "actions/checkout@v7",
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("exact SHA-pinned checkout")

    def test_unpinned_setup_python_action_is_rejected(self) -> None:
        repository = self.repository
        target = self.backup_path(WORKFLOW_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1",
            "actions/setup-python@v6",
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("exact SHA-pinned checkout")

    def test_incomplete_python_matrix_is_rejected(self) -> None:
        repository = self.repository
        target = self.backup_path(WORKFLOW_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            'python-version: ["3.10", "3.12"]',
            'python-version: ["3.12"]',
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("one ubuntu-latest job must contain")

    def test_unapproved_directory_readme_is_rejected(self) -> None:
        repository = self.repository
        target = self.backup_path("docs/extra/README.md")
        target.parent.mkdir()
        target.write_text("# Extra\n\n**Repository Role:** Non-normative directory index\n", encoding="utf-8")
        self.assert_validator_fails("not in the approved non-normative index allowlist")

    def test_directory_index_role_is_required(self) -> None:
        repository = self.repository
        target = self.backup_path("docs/framework/README.md")
        text = target.read_text(encoding="utf-8").replace(
            "**Repository Role:** Non-normative directory index",
            "**Repository Role:** Normative framework authority",
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("Repository Role must be 'Non-normative directory index'")

    def test_uppercase_markdown_extension_is_rejected(self) -> None:
        repository = self.repository
        target = self.backup_path("docs/validation/Extension_Escape.MD")
        target.write_text("# Extension Escape\n", encoding="utf-8")
        self.assert_validator_fails("must use the lowercase .md extension")

    def test_balanced_parenthesis_link_target_is_not_truncated(self) -> None:
        repository = self.repository
        target = self.backup_path("docs/validation/README.md")
        with target.open("a", encoding="utf-8") as handle:
            handle.write("\n[Missing nested target](missing_(draft).md)\n")
        self.assert_validator_fails("missing link or image target: missing_(draft).md")

    def test_missing_html_image_target_is_rejected(self) -> None:
        repository = self.repository
        target = self.backup_path("docs/validation/README.md")
        with target.open("a", encoding="utf-8") as handle:
            handle.write('\n<img src="missing-diagram.png" alt="Missing">\n')
        self.assert_validator_fails("missing link or image target: missing-diagram.png")

    def test_setext_heading_anchor_is_supported(self) -> None:
        repository = self.repository
        target = self.backup_path("docs/validation/README.md")
        with target.open("a", encoding="utf-8") as handle:
            handle.write("\n[Jump](#setext-heading)\n\nSetext Heading\n--------------\n")
        self.assert_validator_passes()


if __name__ == "__main__":
    unittest.main()
