from __future__ import annotations

from pathlib import Path
import hashlib
import shutil
import sys
import tempfile
import unittest

import yaml

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

    def write_registered_third_party_material(
        self,
        *,
        include_marker: bool = True,
        content_hash: str | None = None,
        source_hash: str | None = None,
        accepted_by_id: str = "ray-yang",
        scope_type: str = "entire-file",
        marker_in_sidecar: bool = False,
    ) -> None:
        material_id = "example-material"
        material = self.root / "third-party-example.txt"
        marker_lines = (
            "Third-Party Material ID: example-material\n"
            "License or Notice: Example Notice 1.0\n"
            if include_marker and not marker_in_sidecar
            else ""
        )
        material.write_text(marker_lines + "Third-party example.\n", encoding="utf-8")
        evidence_dir = self.root / "third-party-evidence" / material_id
        evidence_dir.mkdir(parents=True, exist_ok=True)
        source = evidence_dir / "source.txt"
        source.write_text("Controlled source snapshot.\n", encoding="utf-8")
        marker_path = material
        if marker_in_sidecar:
            marker_path = self.root / "third-party-example.txt.NOTICE.md"
            marker_path.write_text(
                "Third-Party Material ID: example-material\n"
                "License or Notice: Example Notice 1.0\n",
                encoding="utf-8",
            )
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
                "ray-yang": {
                    "display_name": "Ray Yang",
                    "role": "repository-maintainer",
                }
            },
            "materials": [
                {
                    "id": material_id,
                    "path": material.relative_to(self.root).as_posix(),
                    "marker_path": marker_path.relative_to(self.root).as_posix(),
                    "scope": {"type": scope_type, "value": scope_type},
                    "rights_holder": "Example Rights Holder",
                    "source": {
                        "locator": "controlled-example-source",
                        "evidence_path": source.relative_to(self.root).as_posix(),
                        "sha256": source_hash or hashlib.sha256(source.read_bytes()).hexdigest(),
                    },
                    "content_sha256": content_hash or hashlib.sha256(material.read_bytes()).hexdigest(),
                    "license_or_notice": "Example Notice 1.0",
                    "notice_path": marker_path.relative_to(self.root).as_posix(),
                    "accepted_by_id": accepted_by_id,
                    "accepted_date": "2026-07-20",
                    "approval_reference": "signed-tag:example-material-v1",
                    "obligations": [],
                    "obligation_evidence": [],
                }
            ],
        }
        (self.root / "third-party-materials.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
        )

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
        status_line = next(
            line for line in text.splitlines() if line.startswith("**Status:** ")
        )
        text = text.replace(
            status_line + "\n",
            f"<!-- {status_line.rstrip()} -->\n",
            1,
        )
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
        marker = "rights expressly provided by GitHub's applicable Terms of Service to GitHub, its Affiliates, and other GitHub Users"
        text = path.read_text(encoding="utf-8").replace(marker, "no platform rights", 1)
        path.write_text(text, encoding="utf-8")
        rules = self.rules()
        self.assertIn("LEGAL-001", rules)
        self.assertIn("LEGAL-002", rules)

    def test_file_specific_notice_authorization_is_required(self) -> None:
        path = self.root / "LICENSE"
        text = path.read_text(encoding="utf-8").replace(
            "registered in `third-party-materials.yaml`",
            "present in a file",
            1,
        )
        path.write_text(text, encoding="utf-8")
        rules = self.rules()
        self.assertIn("LEGAL-001", rules)
        self.assertIn("LEGAL-002", rules)

    def test_contribution_policy_is_required(self) -> None:
        (self.root / "CONTRIBUTING.md").unlink()
        rules = self.rules()
        self.assertIn("REP-001", rules)
        self.assertIn("CONTRIB-001", rules)

    def test_patent_boundary_is_required(self) -> None:
        path = self.root / "CONTRIBUTING.md"
        text = path.read_text(encoding="utf-8").replace(
            "does not grant a patent license, patent covenant, waiver, trademark license",
            "grants patent rights",
            1,
        )
        path.write_text(text, encoding="utf-8")
        rules = self.rules()
        self.assertIn("CONTRIB-001", rules)
        self.assertIn("LEGAL-002", rules)

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

    def test_visible_legal_semantic_reversal_is_rejected(self) -> None:
        path = self.root / "LICENSE"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\nThe preceding no-license and no-warranty terms do not apply.\n",
            encoding="utf-8",
        )
        self.assertIn("LEGAL-002", self.rules())

    def test_html_comment_cannot_restore_removed_legal_clause(self) -> None:
        path = self.root / "LICENSE"
        marker = "rights expressly provided by GitHub's applicable Terms of Service to GitHub, its Affiliates, and other GitHub Users"
        text = path.read_text(encoding="utf-8").replace(marker, "no platform carve-out", 1)
        text += f"\n<!-- {marker} -->\n"
        path.write_text(text, encoding="utf-8")
        rules = self.rules()
        self.assertIn("LEGAL-001", rules)
        self.assertIn("LEGAL-002", rules)

    def test_fenced_example_cannot_restore_removed_legal_clause(self) -> None:
        path = self.root / "LICENSE"
        marker = "registered in `third-party-materials.yaml`"
        text = path.read_text(encoding="utf-8").replace(marker, "present somewhere", 1)
        text += f"\n```text\n{marker}\n```\n"
        path.write_text(text, encoding="utf-8")
        rules = self.rules()
        self.assertIn("LEGAL-001", rules)
        self.assertIn("LEGAL-002", rules)

    def test_duplicate_visible_legal_clause_is_rejected(self) -> None:
        path = self.root / "LICENSE"
        text = path.read_text(encoding="utf-8")
        paragraph = "Permission may be granted separately in writing by the applicable copyright holder."
        path.write_text(text + "\n" + paragraph + "\n", encoding="utf-8")
        self.assertIn("LEGAL-002", self.rules())

    def test_legal_baseline_is_required(self) -> None:
        (self.root / "legal-baseline.yaml").unlink()
        rules = self.rules()
        self.assertIn("REP-001", rules)
        self.assertIn("LEGAL-003", rules)

    def test_legal_baseline_declares_external_authorization(self) -> None:
        path = self.root / "legal-baseline.yaml"
        text = path.read_text(encoding="utf-8").replace(
            "external_authorization_required: true",
            "external_authorization_required: false",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("LEGAL-003", self.rules())

    def test_legal_hashes_are_not_hardcoded_in_validator(self) -> None:
        text = (self.root / "tools/validate_repository.py").read_text(encoding="utf-8")
        self.assertNotIn("CONTROLLED_LEGAL_DOCUMENT_HASHES", text)
        baseline = yaml.safe_load((self.root / "legal-baseline.yaml").read_text(encoding="utf-8"))
        for record in baseline["protected_documents"].values():
            self.assertNotIn(record["normalized_visible_sha256"], text)

    def test_codeowners_protection_is_required(self) -> None:
        path = self.root / ".github/CODEOWNERS"
        text = path.read_text(encoding="utf-8").replace(
            "/LICENSE @jkman357", "/LICENSE @someone-else", 1
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("GOV-003", self.rules())

    def test_external_protection_boundary_is_required(self) -> None:
        path = self.root / ".github/REPOSITORY_PROTECTION.md"
        text = path.read_text(encoding="utf-8").replace(
            "Repository-local hashes and tests provide change detection only",
            "Repository hashes prove authorization",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("GOV-003", self.rules())

    def test_third_party_manifest_is_required(self) -> None:
        (self.root / "third-party-materials.yaml").unlink()
        rules = self.rules()
        self.assertIn("REP-001", rules)
        self.assertIn("TPM-001", rules)

    def test_third_party_manifest_policy_is_fail_closed(self) -> None:
        path = self.root / "third-party-materials.yaml"
        text = path.read_text(encoding="utf-8").replace(
            "exception_effect: registered-entire-file-only",
            "exception_effect: any-file-notice",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("TPM-001", self.rules())

    def test_third_party_manifest_entry_requires_visible_marker(self) -> None:
        self.write_registered_third_party_material(include_marker=False)
        self.assertIn("TPM-003", self.rules())

    def test_valid_registered_third_party_material_passes_manifest_checks(self) -> None:
        self.write_registered_third_party_material()
        related = {finding.rule for finding in validate(self.root) if finding.rule.startswith("TPM-")}
        self.assertEqual(set(), related)

    def test_third_party_manifest_wrong_field_type_fails_without_crashing(self) -> None:
        self.write_registered_third_party_material()
        manifest = self.root / "third-party-materials.yaml"
        document = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        document["materials"][0]["path"] = 123
        document["materials"][0]["marker_path"] = []
        manifest.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        rules = self.rules()
        self.assertIn("TPM-002", rules)
        self.assertIn("TPM-003", rules)

    def test_third_party_content_hash_is_bound_to_repository_bytes(self) -> None:
        self.write_registered_third_party_material(content_hash="1" * 64)
        self.assertIn("TPM-003", self.rules())

    def test_third_party_source_hash_is_bound_to_evidence_bytes(self) -> None:
        self.write_registered_third_party_material(source_hash="2" * 64)
        self.assertIn("TPM-003", self.rules())

    def test_third_party_zero_hash_is_rejected(self) -> None:
        self.write_registered_third_party_material(content_hash="0" * 64)
        self.assertIn("TPM-002", self.rules())

    def test_third_party_approver_is_controlled(self) -> None:
        self.write_registered_third_party_material(accepted_by_id="unknown")
        self.assertIn("TPM-002", self.rules())

    def test_third_party_partial_scope_is_rejected(self) -> None:
        self.write_registered_third_party_material(scope_type="line-range")
        self.assertIn("TPM-002", self.rules())

    def test_text_third_party_notice_cannot_use_detached_sidecar(self) -> None:
        self.write_registered_third_party_material(marker_in_sidecar=True)
        self.assertIn("TPM-003", self.rules())

    def test_conformance_claim_schema_rejects_invalid_lifecycle(self) -> None:
        path = self.root / "examples/framework-conformance-claim.yaml"
        text = path.read_text(encoding="utf-8").replace(
            "lifecycle_status: active", "lifecycle_status: permanent", 1
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("CLAIM-002", self.rules())

    def test_superseded_claim_requires_successor(self) -> None:
        path = self.root / "examples/framework-conformance-claim.yaml"
        text = path.read_text(encoding="utf-8").replace(
            "lifecycle_status: active", "lifecycle_status: superseded", 1
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("CLAIM-002", self.rules())

    def test_scoped_claim_requires_explicit_excluded_boundary(self) -> None:
        path = self.root / "examples/framework-conformance-claim.yaml"
        text = path.read_text(encoding="utf-8").replace(
            "  excluded:\n    - Product enclosure and mechanical design",
            "  excluded: []",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("CLAIM-002", self.rules())

    def test_conformance_claim_requires_prevalidation_boundary(self) -> None:
        path = self.root / "examples/framework-conformance-claim.yaml"
        text = path.read_text(encoding="utf-8").replace(
            "approved_before_validation: true", "approved_before_validation: false", 1
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("CLAIM-002", self.rules())

    def test_full_scoped_and_nonconforming_classifications_are_required(self) -> None:
        path = self.root / "docs/framework/Coordinator_Node_Control_Framework.md"
        text = path.read_text(encoding="utf-8").replace(
            "Full Framework Conformance", "Complete Framework Conformance"
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("GOV-001", self.rules())

    def test_failure_driven_scope_exclusion_prohibition_is_required(self) -> None:
        path = self.root / "docs/framework/Coordinator_Node_Control_Framework.md"
        text = path.read_text(encoding="utf-8").replace(
            "shall not be created or expanded solely after",
            "may be created after",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("GOV-001", self.rules())

    def test_scoped_claim_requires_all_applicable_requirements(self) -> None:
        path = self.root / "docs/framework/Coordinator_Node_Control_Framework.md"
        text = path.read_text(encoding="utf-8").replace(
            "Within every included boundary",
            "Within selected included boundaries",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("GOV-001", self.rules())

    def test_prevalidation_boundary_baseline_is_required(self) -> None:
        path = self.root / "docs/framework/Coordinator_Node_Control_Framework.md"
        text = path.read_text(encoding="utf-8").replace(
            "intended claim boundary and applicability baseline shall be approved",
            "claim boundary may be written after validation",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("GOV-001", self.rules())

    def test_claim_lifecycle_withdrawal_is_required(self) -> None:
        path = self.root / "docs/framework/Coordinator_Node_Control_Framework.md"
        text = path.read_text(encoding="utf-8").replace(
            "invalidated claim shall be withdrawn, revoked, or superseded",
            "invalidated claim may remain active",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("GOV-001", self.rules())

    def test_self_declaration_boundary_is_required(self) -> None:
        path = self.root / "docs/framework/Coordinator_Node_Control_Framework.md"
        text = path.read_text(encoding="utf-8").replace(
            "Framework conformance is a Project-scoped self-declaration",
            "Framework conformance is certification by the maintainer",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertIn("GOV-001", self.rules())

    def test_self_declaration_check_is_required(self) -> None:
        path = self.root / "docs/validation/Framework_Conformance_Checklist.md"
        text = path.read_text(encoding="utf-8").replace("F-00D", "F-00Z", 1)
        path.write_text(text, encoding="utf-8")
        self.assertIn("GOV-002", self.rules())


if __name__ == "__main__":
    unittest.main()
