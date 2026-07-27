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

from validate_repository import CHECKLIST_PRINCIPLE, _semver_tuple, validate


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

    def test_protocol_tester_disposition_matrix_is_enforced(self) -> None:
        path = self.root / "docs/framework/Framework_Application_Analysis_Template.md"
        text = path.read_text(encoding="utf-8").replace(
            "`N/A` for the Formal Integration Gate is not a substitute for a missing PASS",
            "N/A may be used whenever execution is unavailable",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-009", self.rules())

    def test_protocol_tester_self_validation_identity_is_enforced(self) -> None:
        path = self.root / "docs/framework/Framework_Application_Analysis_Template.md"
        text = path.read_text(encoding="utf-8").replace(
            "| Tester Self-Validation Identity |",
            "| Tester Startup Check |",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue({"PCT-002", "PCT-010"} & self.rules())

    def test_protocol_tester_known_negative_controls_are_enforced(self) -> None:
        path = self.root / "docs/protocol/Protocol_YAML_Definition_Guide.md"
        text = path.read_text(encoding="utf-8").replace(
            "The self-validation shall use controlled positive cases and known-negative controls",
            "The self-validation may use a basic startup check",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-010", self.rules())

    def test_protocol_tester_new_checklist_ids_are_enforced(self) -> None:
        path = self.root / "docs/validation/Protocol_Validation_Checklist.md"
        text = path.read_text(encoding="utf-8").replace("P-124", "P-194", 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("PCT-003", self.rules())

    def test_registry_versions_match_updated_documents(self) -> None:
        registry = yaml.safe_load((self.root / "authority-registry.yaml").read_text(encoding="utf-8"))
        by_path = {record["path"]: record for record in registry["documents"]}
        expected = {
            "docs/framework/AI_Engineering_Usage_Guide.md": "v1.1.0",
            "docs/framework/Coordinator_Node_Control_Framework.md": "v1.1.6",
            "docs/framework/Framework_Application_Analysis_Template.md": "v1.1.9",
            "docs/protocol/Protocol_YAML_Definition_Guide.md": "v1.1.7",
            "docs/protocol/Protocol_YAML_Template.md": "v1.1.1",
            "docs/coordinator/Coordinator_Logging_Guide.md": "v1.1.1",
            "docs/coordinator/Coordinator_Testing_Guide.md": "v1.1.1",
            "docs/coordinator/Coordinator_UI_Engineering_Guide.md": "v1.1.1",
            "docs/coding-rules/Embedded_C_Coding_Rules.md": "v1.0.18",
            "docs/validation/Repository_Validation_Checklist.md": "v1.1.0",
            "docs/validation/Protocol_Validation_Checklist.md": "v1.1.6",
        }
        for path, version in expected.items():
            with self.subTest(path=path):
                self.assertEqual(version, by_path[path]["version"])


    def test_duplicate_current_history_version_is_rejected(self) -> None:
        path = self.root / "docs/framework/AI_Engineering_Usage_Guide.md"
        text = path.read_text(encoding="utf-8").replace(
            "| v1.0.31 | 2026-07-26 | Draft for Review |",
            "| v1.0.33 | 2026-07-26 | Draft for Review |",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue({"DOC-007", "DOC-009"} & self.rules())

    def test_metadata_version_must_be_highest_history_version(self) -> None:
        path = self.root / "docs/framework/AI_Engineering_Usage_Guide.md"
        text = path.read_text(encoding="utf-8").replace(
            "| v1.0.31 | 2026-07-26 | Draft for Review |",
            "| v2.0.0 | 2026-07-26 | Draft for Review |",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("DOC-009", self.rules())

    def test_self_supersession_is_rejected(self) -> None:
        path = self.root / "docs/framework/AI_Engineering_Usage_Guide.md"
        text = path.read_text(encoding="utf-8").replace(
            "**Supersedes Document Version:** v1.0.38",
            "**Supersedes Document Version:** v1.1.0",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("DOC-011", self.rules())

    def test_stale_supersedes_version_is_rejected(self) -> None:
        path = self.root / "docs/framework/AI_Engineering_Usage_Guide.md"
        text = path.read_text(encoding="utf-8").replace(
            "**Supersedes Document Version:** v1.0.38",
            "**Supersedes Document Version:** v1.0.31",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("DOC-011", self.rules())

    def test_non_monotonic_history_order_is_rejected(self) -> None:
        path = self.root / "docs/coordinator/Coordinator_Logging_Guide.md"
        text = path.read_text(encoding="utf-8")
        first = "| v1.0.1 | 2026-07-19 | Draft for Review |"
        second = "| v1.0.0 | 2026-07-19 | Draft for Review |"
        text = text.replace(first, "| TEMP_VERSION_ROW |", 1)
        text = text.replace(second, first, 1)
        text = text.replace("| TEMP_VERSION_ROW |", second, 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("DOC-009", self.rules())

    def test_current_history_date_and_status_are_enforced(self) -> None:
        path = self.root / "docs/validation/Repository_Validation_Checklist.md"
        text = path.read_text(encoding="utf-8").replace(
            "| v1.1.0 | 2026-07-27 | Baseline |",
            "| v1.1.0 | 2026-02-30 | Draft for Review |",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("DOC-010", self.rules())

    def test_ai_routing_history_sequence_is_enforced(self) -> None:
        path = self.root / "docs/framework/AI_Engineering_Usage_Guide.md"
        text = path.read_text(encoding="utf-8")
        original = next(line for line in text.splitlines() if line.startswith("| v1.0.31 |"))
        mutated = original.replace(
            "Framework Application Analysis Template v1.1.7",
            "Framework Application Analysis Template v1.1.8",
            1,
        )
        self.assertNotEqual(original, mutated)
        text = text.replace(original, mutated, 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("DOC-012", self.rules())


    def test_ascending_history_order_is_rejected(self) -> None:
        path = self.root / "docs/coordinator/Coordinator_Logging_Guide.md"
        text = path.read_text(encoding="utf-8")
        rows = [line for line in text.splitlines() if line.startswith("| v1.")]
        self.assertGreater(len(rows), 1)
        ascending_rows = list(reversed(rows))
        for old, marker in zip(rows, [f"| TEMP_ASCENDING_{index} |" for index in range(len(rows))]):
            text = text.replace(old, marker, 1)
        for marker, new_row in zip([f"| TEMP_ASCENDING_{index} |" for index in range(len(rows))], ascending_rows):
            text = text.replace(marker, new_row, 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("DOC-009", self.rules())

    def test_ai_routing_history_additive_decoy_version_is_rejected(self) -> None:
        path = self.root / "docs/framework/AI_Engineering_Usage_Guide.md"
        text = path.read_text(encoding="utf-8")
        original = next(line for line in text.splitlines() if line.startswith("| v1.0.31 |"))
        mutated = original.replace(
            "Framework Application Analysis Template v1.1.7",
            "Framework Application Analysis Template v1.1.7 and Framework Application Analysis Template v1.1.8",
            1,
        )
        self.assertNotEqual(original, mutated)
        path.write_text(text.replace(original, mutated, 1), encoding="utf-8")
        self.assertIn("DOC-012", self.rules())



    def test_formal_baseline_version_is_accepted(self) -> None:
        self.assertEqual([], validate(self.root))

    def test_release_candidate_version_is_accepted(self) -> None:
        self.assertIsNotNone(_semver_tuple("v1.1.0-rc.1"))
        self.assertLess(_semver_tuple("v1.1.0-rc.1"), _semver_tuple("v1.1.0"))

    def test_release_candidate_requires_positive_number(self) -> None:
        self.assertIsNone(_semver_tuple("v1.1.0-rc.0"))

    def test_release_candidate_must_remain_draft(self) -> None:
        path = self.root / "docs/framework/AI_Engineering_Usage_Guide.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("**Document Version:** v1.1.0", "**Document Version:** v1.1.0-rc.1", 1)
        text = text.replace("| v1.1.0 | 2026-07-27 | Baseline |", "| v1.1.0-rc.1 | 2026-07-27 | Baseline |", 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("DOC-013", self.rules())

    def test_multi_digit_semantic_version_is_allowed(self) -> None:
        self.assertIsNotNone(_semver_tuple("v1.12.34"))
        self.assertIsNotNone(_semver_tuple("v1.12.34-rc.7"))

    def test_changelog_current_authority_snapshot_is_enforced(self) -> None:
        path = self.root / "CHANGELOG.md"
        text = path.read_text(encoding="utf-8").replace(
            "| AI Engineering Usage Guide | v1.1.0 | Baseline |",
            "| AI Engineering Usage Guide | v1.0.37 | Draft for Review |",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("CHANGE-002", self.rules())

    def test_mutable_repository_cannot_self_assert_release_freeze(self) -> None:
        path = self.root / "README.md"
        text = path.read_text(encoding="utf-8").replace(
            "The repository is being prepared as the `v1.0.0` release candidate.",
            "The repository content is frozen as the `v1.0.0` release candidate.",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("STATUS-001", self.rules())


    def test_repository_symlink_is_rejected_without_following(self) -> None:
        external = Path(self.temporary.name) / "external-readme.md"
        source = self.root / "README.md"
        external.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        source.unlink()
        source.symlink_to(external)
        self.assertIn("REP-007", self.rules())

    def test_codeowners_covers_all_governed_authority_and_validator_content(self) -> None:
        path = self.root / ".github/CODEOWNERS"
        text = path.read_text(encoding="utf-8").replace(
            "/docs/ @jkman357",
            "/docs/framework/Coordinator_Node_Control_Framework.md @jkman357",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("GOV-003", self.rules())

    def test_unsafe_registry_document_path_is_rejected_before_access(self) -> None:
        path = self.root / "authority-registry.yaml"
        text = path.read_text(encoding="utf-8").replace(
            "path: docs/framework/AI_Engineering_Usage_Guide.md",
            "path: /etc/hosts",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("REG-018", self.rules())

    def test_current_status_decoy_outside_controlled_section_is_rejected(self) -> None:
        path = self.root / "README.md"
        text = path.read_text(encoding="utf-8")
        marker = "The repository is being prepared as the `v1.0.0` release candidate."
        text = text.replace(marker, "Release candidate state pending.", 1)
        text += "\n## Historical Note\n\n" + marker + "\n"
        path.write_text(text, encoding="utf-8")
        self.assertIn("STATUS-001", self.rules())

    def test_unreleased_changelog_freeze_assertion_is_rejected(self) -> None:
        path = self.root / "CHANGELOG.md"
        text = path.read_text(encoding="utf-8").replace(
            "### Current Review Changes",
            "### Current Review Changes\n\n- Declared the repository content frozen as the `v1.0.0` release candidate.",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("STATUS-002", self.rules())


if __name__ == "__main__":
    unittest.main()
