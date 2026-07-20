from __future__ import annotations

from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_repository import CHECKLIST_PRINCIPLE, validate  # noqa: E402


class RepositoryValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "repository"
        shutil.copytree(
            ROOT,
            self.root,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def rules(self) -> set[str]:
        return {finding.rule for finding in validate(self.root)}

    def test_repository_baseline_passes(self) -> None:
        self.assertEqual([], validate(self.root))

    def test_public_checklist_principle_is_stable(self) -> None:
        self.assertIn("do not independently create requirements", CHECKLIST_PRINCIPLE)

    def test_duplicate_registry_key_fails_closed(self) -> None:
        path = self.root / "authority-registry.yaml"
        path.write_text(
            "registry_version: 1\n" + path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        self.assertIn("REG-001", self.rules())

    def test_uppercase_markdown_extension_cannot_escape_governance(self) -> None:
        source = self.root / "docs/framework/Coordinator_Node_Control_Framework.md"
        target = self.root / "docs/framework/Escape.MD"
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        rules = self.rules()
        self.assertIn("NAME-002", rules)
        self.assertIn("DOC-001", rules)

    def test_fenced_metadata_is_not_accepted(self) -> None:
        path = self.root / "docs/framework/Coordinator_Node_Control_Framework.md"
        text = path.read_text(encoding="utf-8")
        version_line = next(
            line for line in text.splitlines() if line.startswith("**Document Version:** ")
        )
        text = text.replace(version_line + "\n", "", 1)
        text = text.replace(
            "# Coordinator/Node",
            f"# Coordinator/Node\n\n```text\n{version_line.rstrip()}\n```",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("DOC-008", self.rules())

    def test_duplicate_visible_metadata_is_rejected(self) -> None:
        path = self.root / "docs/framework/Coordinator_Node_Control_Framework.md"
        text = path.read_text(encoding="utf-8")
        version_line = next(
            line for line in text.splitlines() if line.startswith("**Document Version:** ")
        )
        text = text.replace(
            version_line + "\n",
            version_line + "\n" + version_line + "\n",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("DOC-008", self.rules())

    def test_html_comment_metadata_is_not_accepted(self) -> None:
        path = self.root / "docs/framework/Coordinator_Node_Control_Framework.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("**Status:** Baseline  \n", "<!-- **Status:** Baseline -->\n", 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("DOC-008", self.rules())

    def test_workflow_comment_cannot_impersonate_validator_step(self) -> None:
        path = self.root / ".github/workflows/document-validation.yml"
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "run: python tools/validate_repository.py",
            "run: |\n          # python tools/validate_repository.py\n          echo skipped",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("CI-002", self.rules())

    def test_workflow_disabled_step_is_rejected(self) -> None:
        path = self.root / ".github/workflows/document-validation.yml"
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "      - name: Validate repository documentation\n        run:",
            "      - name: Validate repository documentation\n        if: false\n        run:",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("CI-002", self.rules())

    def test_workflow_continue_on_error_is_rejected(self) -> None:
        path = self.root / ".github/workflows/document-validation.yml"
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "      - name: Run validator regression tests\n        run:",
            "      - name: Run validator regression tests\n        continue-on-error: true\n        run:",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("CI-002", self.rules())

    def test_workflow_duplicate_yaml_key_is_rejected(self) -> None:
        path = self.root / ".github/workflows/document-validation.yml"
        text = path.read_text(encoding="utf-8").replace(
            "name: Document validation", "name: First\nname: Document validation", 1
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("CI-001", self.rules())

    def test_shorter_fence_does_not_close_longer_fence(self) -> None:
        path = self.root / "fence_test.md"
        path.write_text("# Test\n\n````text\ninside\n```\n", encoding="utf-8")
        self.assertIn("MD-003", self.rules())

    def test_setext_heading_anchor_is_recognized(self) -> None:
        path = self.root / "setext_test.md"
        path.write_text(
            "Setext Heading\n==============\n\n[Jump](#setext-heading)\n",
            encoding="utf-8",
        )
        self.assertNotIn(
            "LINK-001",
            {
                finding.rule
                for finding in validate(self.root)
                if finding.path.startswith("setext_test.md")
            },
        )

    def test_missing_setext_anchor_is_rejected(self) -> None:
        path = self.root / "setext_test.md"
        path.write_text(
            "Setext Heading\n==============\n\n[Jump](#missing)\n",
            encoding="utf-8",
        )
        self.assertIn("LINK-001", self.rules())

    def test_undefined_reference_style_link_is_rejected(self) -> None:
        path = self.root / "reference_test.md"
        path.write_text("# Test\n\n[Missing][does-not-exist]\n", encoding="utf-8")
        self.assertIn("LINK-005", self.rules())

    def test_html_link_is_validated(self) -> None:
        path = self.root / "html_test.md"
        path.write_text("# Test\n\n<a href=\"Missing.md\">Missing</a>\n", encoding="utf-8")
        self.assertIn("LINK-003", self.rules())

    def test_link_escape_is_rejected(self) -> None:
        path = self.root / "escape_test.md"
        path.write_text("# Test\n\n[Escape](../../outside.md)\n", encoding="utf-8")
        self.assertIn("LINK-002", self.rules())

    def test_changelog_terms_must_be_in_unreleased_section(self) -> None:
        path = self.root / "CHANGELOG.md"
        text = path.read_text(encoding="utf-8")
        marker = "## Historical"
        unreleased, separator, historical = text.partition(marker)
        unreleased = unreleased.replace("protocol.schema.yaml", "schema-file")
        text = unreleased + (separator + historical if separator else "")
        text += "\n## Historical Test Record\n\nprotocol.schema.yaml\n"
        path.write_text(text, encoding="utf-8")
        self.assertIn("CHANGE-001", self.rules())

    def test_protocol_schema_type_error_fails_valid_fixture(self) -> None:
        path = self.root / "tests/fixtures/protocol/valid_legacy_single_node.yaml"
        text = path.read_text(encoding="utf-8").replace(
            "document:\n", "document: []\nlegacy_document:\n", 1
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("PROTO-005", self.rules())

    def test_unregistered_authority_is_rejected(self) -> None:
        path = self.root / "docs/framework/Unregistered_Authority.md"
        path.write_text("# Unregistered\n", encoding="utf-8")
        self.assertIn("DOC-001", self.rules())

    def test_missing_registered_authority_is_rejected(self) -> None:
        (self.root / "docs/node/Node_Software_Engineering_Rules.md").unlink()
        self.assertIn("DOC-002", self.rules())

    def test_reference_definition_target_is_checked(self) -> None:
        path = self.root / "reference_target.md"
        path.write_text(
            "# Test\n\n[Target][ref]\n\n[ref]: missing.md\n", encoding="utf-8"
        )
        self.assertIn("LINK-003", self.rules())

    def test_valid_html_link_to_existing_file_passes(self) -> None:
        path = self.root / "html_valid.md"
        path.write_text("# Test\n\n<a href=\"README.md\">Readme</a>\n", encoding="utf-8")
        related = [
            finding
            for finding in validate(self.root)
            if finding.path.startswith("html_valid.md")
        ]
        self.assertEqual([], related)

    def test_github_terms_carve_out_is_required(self) -> None:
        path = self.root / "LICENSE"
        text = path.read_text(encoding="utf-8").replace(
            "limited rights granted through GitHub under GitHub's applicable Terms of Service",
            "no platform rights",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("LEGAL-001", self.rules())

    def test_file_specific_notice_authorization_is_required(self) -> None:
        path = self.root / "LICENSE"
        text = path.read_text(encoding="utf-8").replace(
            "expressly accepted into this repository by the maintainer as an authorized licensing or notice exception",
            "present in a file",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("LEGAL-001", self.rules())

    def test_contribution_policy_is_required(self) -> None:
        (self.root / "CONTRIBUTING.md").unlink()
        rules = self.rules()
        self.assertIn("REP-001", rules)
        self.assertIn("CONTRIB-001", rules)

    def test_conformance_restoration_path_is_required(self) -> None:
        path = self.root / "docs/framework/Coordinator_Node_Control_Framework.md"
        text = path.read_text(encoding="utf-8").replace(
            "Conformance may be claimed or restored only after",
            "Conformance may be claimed at discretion after",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("GOV-001", self.rules())

    def test_conformance_restoration_check_is_required(self) -> None:
        path = self.root / "docs/validation/Framework_Conformance_Checklist.md"
        text = path.read_text(encoding="utf-8").replace("F-009", "F-099", 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("GOV-002", self.rules())


if __name__ == "__main__":
    unittest.main()
