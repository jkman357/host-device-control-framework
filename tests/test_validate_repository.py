from __future__ import annotations

import shutil
import sys
from pathlib import Path
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_repository import CHECKLIST_PRINCIPLE, validate  # noqa: E402


class RepositoryValidatorTests(unittest.TestCase):
    def copy_repository(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        target = Path(temporary.name) / "repository"
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"),
        )
        return temporary, target

    def assert_rule(self, root: Path, rule: str) -> None:
        rules = {finding.rule for finding in validate(root)}
        self.assertIn(rule, rules, rules)

    def test_repository_baseline_passes(self) -> None:
        self.assertEqual([], validate(ROOT))

    def test_missing_required_file_fails(self) -> None:
        temporary, root = self.copy_repository()
        with temporary:
            (root / "schema/protocol.schema.yaml").unlink()
            self.assert_rule(root, "REP-001")

    def test_metadata_version_mismatch_fails(self) -> None:
        temporary, root = self.copy_repository()
        with temporary:
            path = root / "docs/framework/Coordinator_Node_Control_Framework.md"
            text = path.read_text(encoding="utf-8").replace("**Document Version:** v1.1.0", "**Document Version:** v9.9.9", 1)
            path.write_text(text, encoding="utf-8")
            self.assert_rule(root, "DOC-003")

    def test_unregistered_document_fails(self) -> None:
        temporary, root = self.copy_repository()
        with temporary:
            (root / "docs/framework/Unexpected.md").write_text("# Unexpected\n", encoding="utf-8")
            self.assert_rule(root, "DOC-001")

    def test_duplicate_authority_topic_fails(self) -> None:
        temporary, root = self.copy_repository()
        with temporary:
            path = root / "authority-registry.yaml"
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            data["documents"][1]["authority_topics"].append(data["documents"][0]["authority_topics"][0])
            path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            self.assert_rule(root, "REG-014")

    def test_broken_markdown_link_fails(self) -> None:
        temporary, root = self.copy_repository()
        with temporary:
            path = root / "README.md"
            path.write_text(path.read_text(encoding="utf-8") + "\n[Broken](missing.md)\n", encoding="utf-8")
            self.assert_rule(root, "LINK-003")

    def test_manifest_drift_fails(self) -> None:
        temporary, root = self.copy_repository()
        with temporary:
            path = root / "README.md"
            path.write_text(path.read_text(encoding="utf-8").replace("v1.1.0", "v8.8.8", 1), encoding="utf-8")
            self.assert_rule(root, "VIEW-001")

    def test_valid_fixture_regression_fails(self) -> None:
        temporary, root = self.copy_repository()
        with temporary:
            path = root / "tests/fixtures/protocol/valid_multi_shared_bus.yaml"
            path.write_text(path.read_text(encoding="utf-8").replace("method: frame_address", "method: connection_bound", 1), encoding="utf-8")
            self.assert_rule(root, "PROTO-005")

    def test_schema_node_model_regression_fails(self) -> None:
        temporary, root = self.copy_repository()
        with temporary:
            path = root / "schema/protocol.schema.yaml"
            text = path.read_text(encoding="utf-8").replace("      - topology\n", "", 1)
            path.write_text(text, encoding="utf-8")
            self.assert_rule(root, "PROTO-002")

    def test_checklist_principle_is_stable(self) -> None:
        self.assertIn("do not independently create requirements", CHECKLIST_PRINCIPLE)


if __name__ == "__main__":
    unittest.main()
