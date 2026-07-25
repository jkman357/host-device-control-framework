from __future__ import annotations

from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from validate_repository import CHECKLIST_PRINCIPLE, validate


class RepositoryValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "repository"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def rules(self) -> set[str]:
        return {finding.rule for finding in validate(self.root)}

    def test_repository_baseline_passes(self) -> None:
        self.assertEqual([], validate(self.root))

    def test_public_checklist_principle_is_stable(self) -> None:
        self.assertIn("do not independently create requirements", CHECKLIST_PRINCIPLE)

    def test_protocol_tester_guide_requirement_is_enforced(self) -> None:
        path = self.root / "docs/protocol/Protocol_YAML_Definition_Guide.md"
        text = path.read_text(encoding="utf-8").replace(
            "### 24.6 Independent Protocol Conformance Tester",
            "### 24.6 Removed Requirement",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-001", self.rules())

    def test_protocol_tester_analysis_record_is_enforced(self) -> None:
        path = self.root / "docs/framework/Framework_Application_Analysis_Template.md"
        text = path.read_text(encoding="utf-8").replace(
            "Independent Protocol Tester Applicability",
            "Protocol Tool Optional",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-002", self.rules())

    def test_protocol_tester_no_applicability_loophole_is_rejected(self) -> None:
        path = self.root / "docs/framework/Framework_Application_Analysis_Template.md"
        text = path.read_text(encoding="utf-8").replace("`Required / N/A`", "`Yes / No / N/A`", 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-004", self.rules())

    def test_protocol_tester_lifecycle_artifact_is_enforced(self) -> None:
        path = self.root / "docs/framework/Framework_Application_Analysis_Template.md"
        text = path.read_text(encoding="utf-8").replace(
            "| Independent Protocol Conformance Tester | Yes when applicable |",
            "| Optional Protocol Utility | Recommended |",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-002", self.rules())

    def test_protocol_tester_change_impact_is_enforced(self) -> None:
        path = self.root / "docs/protocol/Protocol_YAML_Definition_Guide.md"
        text = path.read_text(encoding="utf-8").replace("Protocol Conformance Tester impact", "Other tool impact", 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-001", self.rules())

    def test_protocol_tester_checklist_ids_are_enforced(self) -> None:
        path = self.root / "docs/validation/Protocol_Validation_Checklist.md"
        text = path.read_text(encoding="utf-8").replace("P-109", "P-199", 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-003", self.rules())

    def test_registry_versions_match_updated_documents(self) -> None:
        registry = yaml.safe_load((self.root / "authority-registry.yaml").read_text(encoding="utf-8"))
        by_path = {record["path"]: record for record in registry["documents"]}
        expected = {
            "docs/framework/AI_Engineering_Usage_Guide.md": "v1.0.28",
            "docs/framework/Framework_Application_Analysis_Template.md": "v1.1.4",
            "docs/protocol/Protocol_YAML_Definition_Guide.md": "v1.1.2",
            "docs/validation/Protocol_Validation_Checklist.md": "v1.1.2",
        }
        for path, version in expected.items():
            with self.subTest(path=path):
                self.assertEqual(version, by_path[path]["version"])


if __name__ == "__main__":
    unittest.main()
