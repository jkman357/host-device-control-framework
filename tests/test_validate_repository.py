#!/usr/bin/env python3
"""Regression tests for repository validation failure modes."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_RELATIVE_PATH = Path("tools/validate_repository.py")


class RepositoryValidatorRegressionTests(unittest.TestCase):
    def make_repository_copy(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        destination = Path(temporary.name) / "repository"
        shutil.copytree(
            REPOSITORY_ROOT,
            destination,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        return temporary, destination

    def run_validator(self, repository: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(repository / VALIDATOR_RELATIVE_PATH)],
            cwd=repository,
            text=True,
            capture_output=True,
            check=False,
        )

    def assert_validator_fails(self, repository: Path, expected: str) -> None:
        result = self.run_validator(repository)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn(expected, output)

    def test_current_repository_passes(self) -> None:
        result = self.run_validator(REPOSITORY_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Repository validation: PASS", result.stdout)

    def test_metadata_omission_cannot_escape_governance(self) -> None:
        temporary, repository = self.make_repository_copy()
        self.addCleanup(temporary.cleanup)
        target = repository / "docs/coding-rules/Metadata_Escape.md"
        target.write_text("# Metadata Escape\n\nThis file intentionally omits authority metadata.\n", encoding="utf-8")
        self.assert_validator_fails(repository, "every non-README Markdown document under docs must declare")

    def test_invalid_document_version_format_is_rejected(self) -> None:
        temporary, repository = self.make_repository_copy()
        self.addCleanup(temporary.cleanup)
        target = repository / "docs/validation/Repository_Validation_Checklist.md"
        text = target.read_text(encoding="utf-8").replace(
            "**Document Version:** v1.0.2",
            "**Document Version:** 1.0.2",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails(repository, "must match vMAJOR.MINOR.PATCH")

    def test_stale_current_version_is_rejected(self) -> None:
        temporary, repository = self.make_repository_copy()
        self.addCleanup(temporary.cleanup)
        target = repository / "docs/validation/Repository_Validation_Checklist.md"
        text = target.read_text(encoding="utf-8").replace(
            "**Document Version:** v1.0.2",
            "**Document Version:** v1.0.1",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails(repository, "must be the highest Version History version")

    def test_unknown_supersedes_version_is_rejected(self) -> None:
        temporary, repository = self.make_repository_copy()
        self.addCleanup(temporary.cleanup)
        target = repository / "docs/framework/AI_Engineering_Usage_Guide.md"
        text = target.read_text(encoding="utf-8").replace(
            "**Supersedes Document Version:** v1.0.12",
            "**Supersedes Document Version:** v9.9.9",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails(repository, "is not present in Version History")

    def test_non_immediate_supersedes_version_is_rejected(self) -> None:
        temporary, repository = self.make_repository_copy()
        self.addCleanup(temporary.cleanup)
        target = repository / "docs/framework/AI_Engineering_Usage_Guide.md"
        text = target.read_text(encoding="utf-8").replace(
            "**Supersedes Document Version:** v1.0.12",
            "**Supersedes Document Version:** v1.0.10",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails(repository, "must identify the immediate prior listed version v1.0.12")

    def test_obsolete_checkout_action_is_rejected(self) -> None:
        temporary, repository = self.make_repository_copy()
        self.addCleanup(temporary.cleanup)
        target = repository / ".github/workflows/document-validation.yml"
        text = target.read_text(encoding="utf-8").replace("actions/checkout@v7", "actions/checkout@v4")
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails(repository, "actions/checkout@v7 is required")

    def test_obsolete_setup_python_action_is_rejected(self) -> None:
        temporary, repository = self.make_repository_copy()
        self.addCleanup(temporary.cleanup)
        target = repository / ".github/workflows/document-validation.yml"
        text = target.read_text(encoding="utf-8").replace("actions/setup-python@v6", "actions/setup-python@v5")
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails(repository, "actions/setup-python@v6 is required")

    def test_incomplete_python_matrix_is_rejected(self) -> None:
        temporary, repository = self.make_repository_copy()
        self.addCleanup(temporary.cleanup)
        target = repository / ".github/workflows/document-validation.yml"
        text = target.read_text(encoding="utf-8").replace(
            'python-version: ["3.10", "3.12"]',
            'python-version: ["3.12"]',
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails(repository, "Python matrix must include 3.10 and 3.12")


if __name__ == "__main__":
    unittest.main()
