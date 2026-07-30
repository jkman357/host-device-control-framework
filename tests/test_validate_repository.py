from __future__ import annotations

from pathlib import Path
import hashlib
import shutil
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_repository
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

    def install_valid_third_party_material(self) -> None:
        notice_text = "Copyright Example Vendor. Licensed for this controlled test."
        target = self.root / "third_party_sample.txt"
        target.write_text(
            "Third-Party Material ID: example-vendor-sample\n" + notice_text + "\nSample bytes.\n",
            encoding="utf-8",
        )
        source = self.root / "third-party-evidence/example-vendor-source.txt"
        source.write_text("Retained source bytes.\n", encoding="utf-8")
        obligations = self.root / "third-party-evidence/example-vendor-obligations.txt"
        obligations.write_text("Attribution retained.\n", encoding="utf-8")
        manifest = {
            "manifest_version": 2,
            "repository": "host-device-control-framework",
            "policy": {
                "default_terms": "LICENSE",
                "exception_authority": "controlled-approval-authority",
                "exception_effect": "registered-entire-file-only",
                "required_file_marker": "Third-Party Material ID: <id>",
                "source_evidence_root": "third-party-evidence",
            },
            "approval_authorities": {
                "ray-yang": {"display_name": "Ray Yang", "role": "repository-maintainer"}
            },
            "materials": [{
                "id": "example-vendor-sample",
                "target_path": "third_party_sample.txt",
                "scope": "entire_file",
                "provenance": {
                    "source_name": "Example Vendor Sample",
                    "source_reference": "controlled-test-fixture",
                    "source_version": "1.0",
                },
                "rights_holder": "Example Vendor",
                "notice": {
                    "text": notice_text,
                    "sha256": hashlib.sha256(notice_text.encode("utf-8")).hexdigest(),
                },
                "acceptance": {
                    "approver": "ray-yang",
                    "approval_reference": "TEST-APPROVAL-001",
                    "approval_date": "2026-07-30",
                },
                "repository_file_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                "source_evidence": {
                    "path": "third-party-evidence/example-vendor-source.txt",
                    "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                },
                "obligations": ["Retain attribution notice"],
                "obligation_evidence": [{
                    "path": "third-party-evidence/example-vendor-obligations.txt",
                    "sha256": hashlib.sha256(obligations.read_bytes()).hexdigest(),
                }],
            }],
        }
        (self.root / "third-party-materials.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
        )

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
            "docs/framework/AI_Engineering_Usage_Guide.md": "v1.1.3",
            "docs/framework/Coordinator_Node_Control_Framework.md": "v1.1.7",
            "docs/framework/Framework_Application_Analysis_Template.md": "v1.1.9",
            "docs/protocol/Protocol_YAML_Definition_Guide.md": "v1.1.7",
            "docs/protocol/Protocol_YAML_Template.md": "v1.1.1",
            "docs/coordinator/Coordinator_Software_Engineering_Rules.md": "v1.1.1",
            "docs/coordinator/Coordinator_Architecture_Patterns.md": "v1.1.1",
            "docs/coordinator/Coordinator_Logging_Guide.md": "v1.1.1",
            "docs/coordinator/Coordinator_Testing_Guide.md": "v1.1.1",
            "docs/coordinator/Coordinator_UI_Engineering_Guide.md": "v1.1.2",
            "docs/coding-rules/Embedded_C_Coding_Rules.md": "v1.0.19",
            "docs/coding-rules/CSharp_Coding_Rules.md": "v1.0.5",
            "docs/validation/Repository_Validation_Checklist.md": "v1.1.3",
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
            "**Supersedes Document Version:** v1.1.3-rc.2",
            "**Supersedes Document Version:** v1.1.3",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("DOC-011", self.rules())

    def test_stale_supersedes_version_is_rejected(self) -> None:
        path = self.root / "docs/framework/AI_Engineering_Usage_Guide.md"
        text = path.read_text(encoding="utf-8").replace(
            "**Supersedes Document Version:** v1.1.3-rc.2",
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
            "| v1.1.3 | 2026-07-30 | Baseline |",
            "| v1.1.3 | 2026-02-30 | Baseline |",
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



    def test_repository_candidate_baseline_is_accepted(self) -> None:
        self.assertEqual([], validate(self.root))

    def test_release_candidate_version_is_accepted(self) -> None:
        self.assertIsNotNone(_semver_tuple("v1.1.0-rc.1"))
        self.assertLess(_semver_tuple("v1.1.0-rc.1"), _semver_tuple("v1.1.0"))

    def test_release_candidate_requires_positive_number(self) -> None:
        self.assertIsNone(_semver_tuple("v1.1.0-rc.0"))

    def test_release_candidate_must_remain_draft(self) -> None:
        path = self.root / "docs/framework/AI_Engineering_Usage_Guide.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("**Document Version:** v1.1.3", "**Document Version:** v1.1.4-rc.1", 1)
        text = text.replace("**Supersedes Document Version:** v1.1.3-rc.2", "**Supersedes Document Version:** v1.1.3", 1)
        text = text.replace(
            "| v1.1.3 | 2026-07-30 | Baseline |",
            "| v1.1.4-rc.1 | 2026-07-30 | Baseline |",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("DOC-013", self.rules())

    def test_multi_digit_semantic_version_is_allowed(self) -> None:
        self.assertIsNotNone(_semver_tuple("v1.12.34"))
        self.assertIsNotNone(_semver_tuple("v1.12.34-rc.7"))

    def test_changelog_current_authority_snapshot_is_enforced(self) -> None:
        path = self.root / "CHANGELOG.md"
        text = path.read_text(encoding="utf-8").replace(
            "| AI Engineering Usage Guide | v1.1.3 | Baseline |",
            "| AI Engineering Usage Guide | v1.0.37 | Draft for Review |",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("CHANGE-002", self.rules())

    def test_mutable_repository_cannot_self_assert_release_freeze(self) -> None:
        path = self.root / "README.md"
        text = path.read_text(encoding="utf-8").replace(
            "The repository content has received explicit human freeze approval for the `v1.1.3` Baseline.",
            "The repository content is frozen as the `v1.1.3` Baseline.",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("STATUS-001", self.rules())


    def test_missing_gitattributes_is_rejected(self) -> None:
        (self.root / ".gitattributes").unlink()
        self.assertIn("REP-001", self.rules())

    def test_weakened_gitattributes_lf_rule_is_rejected(self) -> None:
        path = self.root / ".gitattributes"
        text = path.read_text(encoding="utf-8").replace("* text=auto eol=lf", "* text=auto", 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("REP-008", self.rules())

    def test_missing_gitattributes_binary_declaration_is_rejected(self) -> None:
        path = self.root / ".gitattributes"
        text = path.read_text(encoding="utf-8").replace("*.zip binary\n", "", 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("REP-008", self.rules())

    def test_missing_extended_gitattributes_binary_declaration_is_rejected(self) -> None:
        path = self.root / ".gitattributes"
        text = path.read_text(encoding="utf-8").replace("*.dll binary\n", "", 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("REP-008", self.rules())

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

    def test_codeowners_text_integrity_is_enforced(self) -> None:
        path = self.root / ".github/CODEOWNERS"
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n", 1))
        self.assertIn("REP-004", self.rules())

    def test_valid_third_party_material_binding_passes(self) -> None:
        self.install_valid_third_party_material()
        self.assertEqual([], validate(self.root))

    def test_cross_platform_repository_paths_reject_windows_escape_forms(self) -> None:
        unsafe_paths = (
            "C:/Windows/win.ini",
            "file.txt:stream",
            ".git/config",
            "third-party-evidence/NUL.txt",
            "third-party-evidence/trailing.",
        )
        for value in unsafe_paths:
            with self.subTest(value=value):
                self.assertFalse(validate_repository._safe_repository_relative_path(value))

    def test_repository_path_resolution_rejects_parent_symlink_escape(self) -> None:
        external = Path(self.temporary.name) / "external-evidence"
        external.mkdir()
        link = self.root / "third-party-evidence/linked"
        link.symlink_to(external, target_is_directory=True)
        resolved = validate_repository._repository_relative_path(
            self.root,
            "third-party-evidence/linked/source.txt",
            required_prefix="third-party-evidence",
        )
        self.assertIsNone(resolved)

    def test_third_party_target_byte_mutation_is_rejected(self) -> None:
        self.install_valid_third_party_material()
        path = self.root / "third_party_sample.txt"
        path.write_text(path.read_text(encoding="utf-8") + "mutated\n", encoding="utf-8")
        self.assertIn("TPM-002", self.rules())

    def test_third_party_source_evidence_mutation_is_rejected(self) -> None:
        self.install_valid_third_party_material()
        path = self.root / "third-party-evidence/example-vendor-source.txt"
        path.write_text("changed source bytes\n", encoding="utf-8")
        self.assertIn("TPM-002", self.rules())

    def test_third_party_visible_marker_removal_is_rejected(self) -> None:
        self.install_valid_third_party_material()
        target = self.root / "third_party_sample.txt"
        text = target.read_text(encoding="utf-8").replace(
            "Third-Party Material ID: example-vendor-sample\n", "", 1
        )
        target.write_text(text, encoding="utf-8")
        manifest_path = self.root / "third-party-materials.yaml"
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        manifest["materials"][0]["repository_file_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        self.assertIn("TPM-002", self.rules())

    def test_third_party_uncontrolled_approver_is_rejected(self) -> None:
        self.install_valid_third_party_material()
        manifest_path = self.root / "third-party-materials.yaml"
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        manifest["materials"][0]["acceptance"]["approver"] = "unknown-approver"
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        self.assertIn("TPM-002", self.rules())

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
        marker = "The repository content has received explicit human freeze approval for the `v1.1.3` Baseline."
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
