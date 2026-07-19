from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_repository import CHECKLIST_PRINCIPLE, validate  # noqa: E402


class RepositoryValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    def tearDown(self) -> None:
        self.temp.cleanup()

    def errors(self) -> list[str]:
        return validate(self.root)

    def assertFailsContaining(self, text: str) -> None:
        errors = self.errors()
        self.assertTrue(errors, "mutated repository unexpectedly passed")
        self.assertTrue(any(text in e for e in errors), f"expected {text!r} in errors:\n" + "\n".join(errors))

    def test_baseline_passes(self) -> None:
        self.assertEqual([], self.errors())

    def test_registry_control_file_missing_is_rejected(self) -> None:
        (self.root / "authority-registry.yaml").unlink()
        self.assertFailsContaining("required repository file is missing")

    def test_metadata_status_mismatch_is_rejected(self) -> None:
        p = self.root / "docs/node/Node_Software_Engineering_Rules.md"
        p.write_text(p.read_text(encoding="utf-8").replace("**Status:** Draft for Review", "**Status:** Baseline", 1), encoding="utf-8")
        self.assertFailsContaining("metadata Status must equal registry")

    def test_unregistered_authority_is_rejected(self) -> None:
        p = self.root / "docs/node/Unregistered_Authority.md"
        p.write_text("# Unregistered Authority\n", encoding="utf-8")
        self.assertFailsContaining("governed Markdown exists but is not registered")

    def test_missing_registry_file_is_rejected(self) -> None:
        (self.root / "docs/node/Node_Software_Engineering_Rules.md").unlink()
        self.assertFailsContaining("registry entry does not resolve")

    def test_root_document_table_divergence_is_rejected(self) -> None:
        p = self.root / "README.md"
        p.write_text(p.read_text(encoding="utf-8").replace("v1.0.20", "v9.9.9", 1), encoding="utf-8")
        self.assertFailsContaining("Current Document Set fields mismatch")

    def test_ai_manifest_divergence_is_rejected(self) -> None:
        p = self.root / "docs/framework/AI_Engineering_Usage_Guide.md"
        text = p.read_text(encoding="utf-8")
        marker = "| Node Software Engineering Rules |"
        line = next(x for x in text.splitlines() if x.startswith(marker))
        p.write_text(text.replace(line + "\n", "", 1), encoding="utf-8")
        self.assertFailsContaining("Active Document Manifest paths differ")

    def test_folder_index_omission_is_rejected(self) -> None:
        p = self.root / "docs/node/README.md"
        text = p.read_text(encoding="utf-8")
        text = text.replace("(Node_Software_Engineering_Rules.md)", "(README.md)")
        p.write_text(text, encoding="utf-8")
        self.assertFailsContaining("directory index omits governed documents")

    def test_metadata_version_mismatch_is_rejected(self) -> None:
        p = self.root / "docs/node/Node_Software_Engineering_Rules.md"
        p.write_text(p.read_text(encoding="utf-8").replace("**Document Version:** v1.0.0", "**Document Version:** v1.0.1", 1), encoding="utf-8")
        self.assertFailsContaining("metadata Document Version must equal registry")

    def test_duplicate_canonical_identity_is_rejected(self) -> None:
        p = self.root / "docs/node/Node_Software_Engineering_Rules.md"
        text = p.read_text(encoding="utf-8").replace("`Node_Software_Engineering_Rules.md`", "`Coordinator_Software_Engineering_Rules.md`", 1)
        p.write_text(text, encoding="utf-8")
        self.assertFailsContaining("duplicate canonical document identity")

    def test_illegal_versioned_markdown_filename_is_rejected(self) -> None:
        src = self.root / "docs/node/Node_Software_Engineering_Rules.md"
        dst = self.root / "docs/node/Extra_Rules_v1.0.0.md"
        shutil.copy2(src, dst)
        self.assertFailsContaining("embeds version, release status, RC, or date")

    def test_broken_relative_link_is_rejected(self) -> None:
        p = self.root / "docs/node/README.md"
        p.write_text(p.read_text(encoding="utf-8") + "\n[Broken](Missing_File.md)\n", encoding="utf-8")
        self.assertFailsContaining("broken local link target")

    def test_checklist_authority_leakage_is_rejected(self) -> None:
        p = self.root / "docs/validation/Protocol_Validation_Checklist.md"
        p.write_text(p.read_text(encoding="utf-8").replace(CHECKLIST_PRINCIPLE, "Checklist content."), encoding="utf-8")
        self.assertFailsContaining("missing common checklist non-authority principle")

    def test_protocol_document_wrong_domain_is_rejected(self) -> None:
        src = self.root / "docs/protocol/Protocol_Security_Profile.md"
        dst = self.root / "docs/coordinator/Protocol_Security_Profile.md"
        shutil.move(src, dst)
        self.assertFailsContaining("Protocol governance document is outside docs/protocol")

    def test_node_routing_omission_is_rejected(self) -> None:
        p = self.root / "docs/framework/AI_Engineering_Usage_Guide.md"
        p.write_text(p.read_text(encoding="utf-8").replace("Node_Software_Engineering_Rules.md", "Node Rules omitted"), encoding="utf-8")
        self.assertFailsContaining("Node Software Engineering Rules are not routed")

    def test_notice_missing_section_is_rejected(self) -> None:
        p = self.root / "NOTICE.md"
        p.write_text(p.read_text(encoding="utf-8").replace("## AI Assistance Disclosure", "### AI Assistance Disclosure", 1), encoding="utf-8")
        self.assertFailsContaining("required level-2 headings/order")

    def test_changelog_missing_new_file_is_rejected(self) -> None:
        p = self.root / "CHANGELOG.md"
        p.write_text(p.read_text(encoding="utf-8").replace("Protocol_Compatibility_Rules.md", "Protocol compatibility document", 1), encoding="utf-8")
        self.assertFailsContaining("new governed document is not recorded")

    def test_duplicate_authority_topic_is_rejected(self) -> None:
        p = self.root / "authority-registry.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        data["documents"][1]["authority_topics"][0] = data["documents"][0]["authority_topics"][0]
        p.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=140), encoding="utf-8")
        self.assertFailsContaining("duplicate exact authority topic")

    def test_workflow_runner_regression_is_rejected(self) -> None:
        p = self.root / ".github/workflows/document-validation.yml"
        p.write_text(p.read_text(encoding="utf-8").replace("ubuntu-24.04", "ubuntu-latest", 1), encoding="utf-8")
        self.assertFailsContaining("runner must be ubuntu-24.04")


if __name__ == "__main__":
    unittest.main()
