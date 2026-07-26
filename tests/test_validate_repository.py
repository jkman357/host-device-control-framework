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
        self.assertIn("PCT-004", self.rules())

    def test_protocol_tester_no_applicability_loophole_is_rejected(self) -> None:
        path = self.root / "docs/framework/Framework_Application_Analysis_Template.md"
        text = path.read_text(encoding="utf-8").replace("`Required / N/A`", "`Yes / No / N/A`", 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-004", self.rules())

    def test_protocol_tester_optional_applicability_loophole_is_rejected(self) -> None:
        path = self.root / "docs/framework/Framework_Application_Analysis_Template.md"
        text = path.read_text(encoding="utf-8").replace("`Required / N/A`", "`Required / Optional / N/A`", 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-004", self.rules())

    def test_protocol_tester_staged_baseline_lifecycle_is_enforced(self) -> None:
        path = self.root / "docs/protocol/Protocol_YAML_Definition_Guide.md"
        text = path.read_text(encoding="utf-8").replace(
            "Protocol Definition Baseline approval does not require executed Tester evidence",
            "All baseline approval requires completed target execution",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-001", self.rules())

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


    def test_protocol_tester_decoy_applicability_row_is_rejected(self) -> None:
        path = self.root / "docs/framework/Framework_Application_Analysis_Template.md"
        text = path.read_text(encoding="utf-8")
        heading = "## 15.2 Independent Protocol Conformance Tester Decision"
        text = text.replace(
            heading,
            "| Independent Protocol Tester Applicability | `Required / N/A` |\n\n" + heading,
            1,
        )
        first = text.find("| Independent Protocol Tester Applicability | `Required / N/A` |")
        second = text.find("| Independent Protocol Tester Applicability | `Required / N/A` |", first + 1)
        self.assertGreater(second, first)
        text = text[:second] + text[second:].replace(
            "| Independent Protocol Tester Applicability | `Required / N/A` |",
            "| Independent Protocol Tester Applicability | `Required / Optional / N/A` |",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-004", self.rules())

    def test_protocol_baseline_stage_row_is_enforced(self) -> None:
        path = self.root / "docs/framework/Framework_Application_Analysis_Template.md"
        text = path.read_text(encoding="utf-8").replace(
            "`<Exactly one: Definition, Integration, or Release>`",
            "`Definition / Integration / Release`",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-005", self.rules())

    def test_definition_stage_does_not_require_executed_tester_evidence(self) -> None:
        path = self.root / "docs/validation/Protocol_Validation_Checklist.md"
        text = path.read_text(encoding="utf-8").replace(
            "**Integration/Release only:** the Tester was executed",
            "The Tester was executed",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-006", self.rules())

    def test_protocol_baseline_contents_are_mandatory(self) -> None:
        path = self.root / "docs/protocol/Protocol_YAML_Definition_Guide.md"
        text = path.read_text(encoding="utf-8").replace(
            "A **Protocol Definition Baseline** shall include",
            "A **Protocol Definition Baseline** should include",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-001", self.rules())

    def test_release_evidence_reconciliation_is_enforced(self) -> None:
        path = self.root / "docs/protocol/Protocol_YAML_Definition_Guide.md"
        text = path.read_text(encoding="utf-8").replace(
            "shall retain an Integration-to-Release evidence reconciliation",
            "shall retain a Release evidence note",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-001", self.rules())

    def test_exact_tested_candidate_identity_is_enforced(self) -> None:
        path = self.root / "docs/framework/Framework_Application_Analysis_Template.md"
        text = path.read_text(encoding="utf-8").replace(
            "| Tested Candidate Identity |",
            "| Approximate Candidate Identity |",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-002", self.rules())

    def test_representative_target_residual_boundary_is_enforced(self) -> None:
        path = self.root / "docs/framework/Framework_Application_Analysis_Template.md"
        text = path.read_text(encoding="utf-8").replace(
            "| Representative Target Residual Boundary |",
            "| Representative Target Note |",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-002", self.rules())

    def test_new_evidence_checklist_ids_are_enforced(self) -> None:
        path = self.root / "docs/validation/Protocol_Validation_Checklist.md"
        text = path.read_text(encoding="utf-8").replace("P-121", "P-191", 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-003", self.rules())

    def test_registry_versions_match_updated_documents(self) -> None:
        registry = yaml.safe_load((self.root / "authority-registry.yaml").read_text(encoding="utf-8"))
        by_path = {record["path"]: record for record in registry["documents"]}
        expected = {
            "docs/framework/AI_Engineering_Usage_Guide.md": "v1.0.31",
            "docs/framework/Framework_Application_Analysis_Template.md": "v1.1.7",
            "docs/protocol/Protocol_YAML_Definition_Guide.md": "v1.1.5",
            "docs/validation/Protocol_Validation_Checklist.md": "v1.1.5",
        }
        for path, version in expected.items():
            with self.subTest(path=path):
                self.assertEqual(version, by_path[path]["version"])


if __name__ == "__main__":
    unittest.main()
