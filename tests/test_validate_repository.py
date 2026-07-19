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
REGISTRY_RELATIVE_PATH = Path("authority-registry.yaml")
CHECKLIST_RELATIVE_PATH = Path("docs/validation/Repository_Validation_Checklist.md")
GUIDE_RELATIVE_PATH = Path("docs/framework/AI_Engineering_Usage_Guide.md")


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
        target = self.backup_path("docs/coding-rules/Metadata_Escape.md")
        target.write_text("# Metadata Escape\n\nNo metadata.\n", encoding="utf-8")
        self.assert_validator_fails("every governed Markdown document under docs must declare")

    def test_metadata_inside_fence_is_ignored(self) -> None:
        target = self.backup_path("docs/coding-rules/Fenced_Metadata.md")
        target.write_text(
            "# Fenced Metadata\n\n```markdown\n"
            "**Canonical Filename:** `Fenced_Metadata.md`\n"
            "**Document Version:** v1.0.0\n"
            "**Status:** Draft for Review\n"
            "**Repository Role:** Proposed normative example authority\n"
            "## Version History\n"
            "| Version | Date | Status | Summary |\n|---|---|---|---|\n"
            "| v1.0.0 | 2026-07-19 | Draft for Review | Example. |\n```\n",
            encoding="utf-8",
        )
        self.assert_validator_fails("every governed Markdown document under docs must declare")

    def test_metadata_inside_html_pre_is_ignored(self) -> None:
        target = self.backup_path("docs/coding-rules/Html_Metadata.md")
        target.write_text(
            "# HTML Metadata\n\n<pre>\n"
            "**Canonical Filename:** `Html_Metadata.md`\n"
            "**Document Version:** v1.0.0\n"
            "**Status:** Draft for Review\n"
            "**Repository Role:** Proposed normative example authority\n"
            "## Version History\n"
            "| Version | Date | Status | Summary |\n|---|---|---|---|\n"
            "| v1.0.0 | 2026-07-19 | Draft for Review | Example. |\n"
            "</pre>\n",
            encoding="utf-8",
        )
        self.assert_validator_fails("every governed Markdown document under docs must declare")

    def test_unclosed_html_code_block_is_rejected(self) -> None:
        target = self.backup_path("docs/validation/README.md")
        with target.open("a", encoding="utf-8") as handle:
            handle.write("\n<pre>unclosed\n")
        self.assert_validator_fails("unclosed HTML code/example block")

    def test_duplicate_metadata_is_rejected(self) -> None:
        target = self.backup_path(CHECKLIST_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "**Document Version:** v1.0.4",
            "**Document Version:** v1.0.4\n**Document Version:** v1.0.4",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("metadata key 'Document Version' must appear exactly once")

    def test_metadata_after_first_h2_is_rejected(self) -> None:
        target = self.backup_path(CHECKLIST_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8")
        line = "**Repository Role:** Proposed operational validation method; not a Product or architecture authority  \n"
        text = text.replace(line, "", 1)
        marker = "## Version History\n"
        text = text.replace(marker, marker + "\n" + line, 1)
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("must appear before the first level-2 heading")

    def test_missing_repository_role_is_rejected(self) -> None:
        target = self.backup_path(CHECKLIST_RELATIVE_PATH)
        text = re.sub(r"^\*\*Repository Role:\*\*.*\n", "", target.read_text(encoding="utf-8"), count=1, flags=re.MULTILINE)
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("Document Version, Status, and Repository Role")

    def test_unknown_status_is_rejected(self) -> None:
        target = self.backup_path(CHECKLIST_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace("**Status:** Draft for Review", "**Status:** Approved", 1)
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("is not in the controlled enum")

    def test_draft_role_must_be_proposed(self) -> None:
        target = self.backup_path(CHECKLIST_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "**Repository Role:** Proposed operational validation method; not a Product or architecture authority",
            "**Repository Role:** Normative operational validation authority",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("must begin with 'Proposed '")

    def test_baseline_role_must_be_normative(self) -> None:
        target = self.backup_path("docs/framework/Coordinator_Node_Control_Framework.md")
        text = target.read_text(encoding="utf-8").replace(
            "**Repository Role:** Normative architecture and framework-governance authority",
            "**Repository Role:** Supporting architecture notes",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("must be non-proposed normative wording")

    def test_version_history_inside_html_pre_is_ignored(self) -> None:
        target = self.backup_path("docs/coding-rules/CSharp_Coding_Rules.md")
        text = target.read_text(encoding="utf-8")
        start = text.index("## Version History")
        next_heading = re.search(r"^# Part ", text[start:], re.MULTILINE)
        self.assertIsNotNone(next_heading)
        end = start + next_heading.start()
        text = text[:start] + "<pre>\n" + text[start:end] + "</pre>\n\n" + text[end:]
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("exactly one Version History or Change History heading is required; found 0")

    def test_missing_history_column_is_rejected(self) -> None:
        target = self.backup_path(CHECKLIST_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "| Version | Date | Status | Summary |",
            "| Version | Date | Summary |",
            1,
        ).replace(
            "| --- | --- | --- | --- |",
            "| --- | --- | --- |",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("Version History missing required columns: status")

    def test_history_row_cell_count_is_rejected(self) -> None:
        target = self.backup_path(CHECKLIST_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "| v1.0.4 | 2026-07-19 | Draft for Review | Hardened",
            "| v1.0.4 | 2026-07-19 | Hardened",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("Version History row has")

    def test_invalid_calendar_date_is_rejected(self) -> None:
        target = self.backup_path(CHECKLIST_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace("| v1.0.4 | 2026-07-19 |", "| v1.0.4 | 2026-99-99 |", 1)
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("current Version History date must be a real ISO")

    def test_empty_history_summary_is_rejected(self) -> None:
        target = self.backup_path(CHECKLIST_RELATIVE_PATH)
        text = re.sub(
            r"(\| v1\.0\.4 \| 2026-07-19 \| Draft for Review \|)[^|]+(\|)",
            r"\1 \2",
            target.read_text(encoding="utf-8"),
            count=1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("summary/description must not be empty")

    def test_missing_supersedes_is_rejected(self) -> None:
        target = self.backup_path(GUIDE_RELATIVE_PATH)
        text = re.sub(r"^\*\*Supersedes Document Version:\*\*.*\n", "", target.read_text(encoding="utf-8"), count=1, flags=re.MULTILINE)
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("Supersedes Document Version is required")

    def test_non_immediate_supersedes_is_rejected(self) -> None:
        target = self.backup_path(GUIDE_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "**Supersedes Document Version:** v1.0.14",
            "**Supersedes Document Version:** v1.0.12",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("immediate prior listed version v1.0.14")

    def test_duplicate_current_document_set_heading_is_rejected(self) -> None:
        target = self.backup_path("README.md")
        with target.open("a", encoding="utf-8") as handle:
            handle.write("\n## Current Document Set\n\n| Document | Version | Status | Purpose |\n|---|---|---|---|\n")
        self.assert_validator_fails("heading '## Current Document Set' must appear exactly once; found 2")

    def test_duplicate_active_manifest_heading_is_rejected(self) -> None:
        target = self.backup_path(GUIDE_RELATIVE_PATH)
        with target.open("a", encoding="utf-8") as handle:
            handle.write("\n## 0.2 Active Document Manifest\n")
        self.assert_validator_fails("heading '## 0.2 Active Document Manifest' must appear exactly once; found 2")

    def test_fenced_current_document_set_is_ignored(self) -> None:
        target = self.backup_path("README.md")
        text = target.read_text(encoding="utf-8")
        start = text.index("## Current Document Set")
        end = text.index("## AI Task Routing", start)
        text = text[:start] + "```markdown\n" + text[start:end] + "```\n\n" + text[end:]
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("must appear exactly once; found 0")

    def test_registry_version_mismatch_is_rejected(self) -> None:
        target = self.backup_path(REGISTRY_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace("version: v1.0.15", "version: v9.9.9", 1)
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("authority-registry.yaml version mismatch")

    def test_registry_role_mismatch_is_rejected(self) -> None:
        target = self.backup_path(REGISTRY_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "repository_role: Proposed normative AI task-routing and repository-governance authority",
            "repository_role: Proposed wrong role",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("authority-registry.yaml Repository Role mismatch")

    def test_registry_unknown_prerequisite_is_rejected(self) -> None:
        target = self.backup_path(REGISTRY_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "prerequisite_documents: []",
            "prerequisite_documents:\n      - docs/framework/Missing.md",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("has unknown prerequisites")

    def test_registry_empty_topics_is_rejected(self) -> None:
        target = self.backup_path(REGISTRY_RELATIVE_PATH)
        text = re.sub(
            r"authority_topics:\n(?:      - .*\n)+    prerequisite_documents: \[\]",
            "authority_topics: []\n    prerequisite_documents: []",
            target.read_text(encoding="utf-8"),
            count=1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("authority_topics must be a non-empty string list")

    def test_readme_purpose_drift_is_rejected(self) -> None:
        target = self.backup_path("README.md")
        text = target.read_text(encoding="utf-8").replace(
            "AI entry point, authority routing, task workflows, evidence states, prohibited behaviors, and human approval boundary",
            "Wrong purpose",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("README Purpose mismatch")

    def test_ai_manifest_routing_role_drift_is_rejected(self) -> None:
        target = self.backup_path(GUIDE_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "AI authority routing and operating controls",
            "Wrong routing role",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("AI manifest Routing Role mismatch")

    def test_invalid_workflow_yaml_is_rejected(self) -> None:
        target = self.backup_path(WORKFLOW_RELATIVE_PATH)
        target.write_text("jobs:\n  invalid: [\n", encoding="utf-8")
        self.assert_validator_fails("invalid YAML")

    def test_comment_only_workflow_commands_are_rejected(self) -> None:
        target = self.backup_path(WORKFLOW_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "run: python tools/validate_repository.py",
            "run: |\n          # python tools/validate_repository.py\n          echo skipped",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("exact, separate, unconditional")

    def test_workflow_command_inside_false_shell_is_rejected(self) -> None:
        target = self.backup_path(WORKFLOW_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "run: python tools/validate_repository.py",
            "run: |\n          if false; then\n            python tools/validate_repository.py\n          fi",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("exact, separate, unconditional")

    def test_conditional_workflow_step_is_rejected(self) -> None:
        target = self.backup_path(WORKFLOW_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "      - name: Validate repository documentation\n        run: python tools/validate_repository.py",
            "      - name: Validate repository documentation\n        if: ${{ false }}\n        run: python tools/validate_repository.py",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("exact, separate, unconditional")

    def test_hashless_workflow_install_is_rejected(self) -> None:
        target = self.backup_path(WORKFLOW_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(" --require-hashes", "", 1)
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("hash-verified dependency install")

    def test_requirements_hash_change_is_rejected(self) -> None:
        target = self.backup_path("requirements-validation.txt")
        text = target.read_text(encoding="utf-8").replace("d7662337", "00000000", 1)
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("must exactly pin PyYAML 6.0.3")

    def test_unpinned_checkout_is_rejected(self) -> None:
        target = self.backup_path(WORKFLOW_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0",
            "actions/checkout@v7",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("SHA-pinned checkout/setup")

    def test_workflow_shell_override_is_rejected(self) -> None:
        target = self.backup_path(WORKFLOW_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "        run: python tools/validate_repository.py",
            "        run: python tools/validate_repository.py\n        shell: echo {0}",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("exact, separate, unconditional")

    def test_checkout_credentials_must_not_persist(self) -> None:
        target = self.backup_path(WORKFLOW_RELATIVE_PATH)
        text = target.read_text(encoding="utf-8").replace(
            "        with:\n          persist-credentials: false\n",
            "",
            1,
        )
        target.write_text(text, encoding="utf-8")
        self.assert_validator_fails("non-persisted credentials")

    def test_html_comment_does_not_create_anchor(self) -> None:
        target = self.backup_path("docs/validation/README.md")
        with target.open("a", encoding="utf-8") as handle:
            handle.write('\n<!-- id="fake-anchor" -->\n[Jump](#fake-anchor)\n')
        self.assert_validator_fails("missing heading anchor")

    def test_real_html_anchor_is_supported(self) -> None:
        target = self.backup_path("docs/validation/README.md")
        with target.open("a", encoding="utf-8") as handle:
            handle.write('\n<a id="real-anchor"></a>\n[Jump](#real-anchor)\n')
        self.assert_validator_passes()

    def test_unapproved_directory_readme_is_rejected(self) -> None:
        target = self.backup_path("docs/extra/README.md")
        target.parent.mkdir()
        target.write_text("# Extra\n\n**Repository Role:** Non-normative directory index\n", encoding="utf-8")
        self.assert_validator_fails("not in the approved non-normative index allowlist")

    def test_uppercase_markdown_extension_is_rejected(self) -> None:
        target = self.backup_path("docs/validation/Extension_Escape.MD")
        target.write_text("# Extension Escape\n", encoding="utf-8")
        self.assert_validator_fails("must use the lowercase .md extension")

    def test_balanced_parenthesis_link_is_checked(self) -> None:
        target = self.backup_path("docs/validation/README.md")
        with target.open("a", encoding="utf-8") as handle:
            handle.write("\n[Missing](missing_(draft).md)\n")
        self.assert_validator_fails("missing link or image target: missing_(draft).md")

    def test_setext_heading_anchor_is_supported(self) -> None:
        target = self.backup_path("docs/validation/README.md")
        with target.open("a", encoding="utf-8") as handle:
            handle.write("\n[Jump](#setext-heading)\n\nSetext Heading\n--------------\n")
        self.assert_validator_passes()


if __name__ == "__main__":
    unittest.main()
