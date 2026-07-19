#!/usr/bin/env python3
"""Regression tests for repository validation failure and pass modes."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = Path("tools/validate_repository.py")
REGISTRY = Path("authority-registry.yaml")
README = Path("README.md")
AI_GUIDE = Path("docs/framework/AI_Engineering_Usage_Guide.md")
LOGGING = Path("docs/coordinator/Coordinator_Logging_Guide.md")
TESTING = Path("docs/coordinator/Coordinator_Testing_Guide.md")
UI = Path("docs/coordinator/Coordinator_UI_Engineering_Guide.md")
WORKFLOW = Path(".github/workflows/document-validation.yml")
CHECKLIST = Path("docs/validation/Repository_Validation_Checklist.md")


class RepositoryValidatorRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary.name) / "repository"
        shutil.copytree(REPOSITORY_ROOT, self.repository, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def path(self, relative: str | Path) -> Path:
        return self.repository / relative

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        if not getattr(self, "force_full_validation", False):
            env["HDCF_VALIDATOR_FAST_TEST"] = "1"
        return subprocess.run(
            [sys.executable, str(self.path(VALIDATOR))], cwd=self.repository,
            text=True, capture_output=True, check=False, env=env,
        )

    def assert_passes(self) -> None:
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Repository validation: PASS", result.stdout)

    def assert_fails(self, expected: str) -> None:
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(expected, result.stdout + result.stderr)

    def load_registry(self) -> dict:
        return yaml.safe_load(self.path(REGISTRY).read_text(encoding="utf-8"))

    def save_registry(self, data: dict) -> None:
        self.path(REGISTRY).write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100000), encoding="utf-8", newline="\n")

    def test_repository_baseline_passes(self) -> None:
        self.assert_passes()

    def test_registry_version_mismatch_is_version_independent(self) -> None:
        """Do not bind the mutation anchor to a historical version literal."""
        data = self.load_registry()
        entry = next(d for d in data["documents"] if d["path"] == "docs/framework/AI_Engineering_Usage_Guide.md")
        original = entry["version"]
        self.assertRegex(original, r"^v\d+\.\d+\.\d+$")
        entry["version"] = "v9.9.9" if original != "v9.9.9" else "v9.9.8"
        self.save_registry(data)
        self.assert_fails("authority-registry.yaml version mismatch for AI_Engineering_Usage_Guide.md")

    def test_registry_missing_document_is_rejected(self) -> None:
        data=self.load_registry(); data["documents"].pop(); self.save_registry(data)
        self.assert_fails("missing governed documents")

    def test_registry_duplicate_document_path_is_rejected(self) -> None:
        data=self.load_registry(); data["documents"].append(dict(data["documents"][0])); self.save_registry(data)
        self.assert_fails("duplicate document paths")

    def test_registry_unexpected_root_field_is_rejected(self) -> None:
        data=self.load_registry(); data["unexpected"]="x"; self.save_registry(data)
        self.assert_fails("unexpected root fields")

    def test_registry_missing_root_field_is_rejected(self) -> None:
        data=self.load_registry(); data.pop("source_of_truth"); self.save_registry(data)
        self.assert_fails("missing root fields")

    def test_registry_source_identity_is_controlled(self) -> None:
        data=self.load_registry(); data["source_of_truth"]="local copy"; self.save_registry(data)
        self.assert_fails("source_of_truth must be 'GitHub main'")

    def test_registry_repository_identity_is_controlled(self) -> None:
        data=self.load_registry(); data["repository"]="other"; self.save_registry(data)
        self.assert_fails("repository must be host-device-control-framework")

    def test_registry_version_field_is_controlled(self) -> None:
        data=self.load_registry(); data["registry_version"]=2; self.save_registry(data)
        self.assert_fails("registry_version must be 1")

    def test_registry_policy_schema_is_exact(self) -> None:
        data=self.load_registry(); data["policy"]["extra"]="x"; self.save_registry(data)
        self.assert_fails("policy must contain the exact controlled fields")

    def test_registry_entry_schema_is_exact(self) -> None:
        data=self.load_registry(); data["documents"][0]["extra"]="x"; self.save_registry(data)
        self.assert_fails("unexpected fields")

    def test_registry_unknown_prerequisite_is_rejected(self) -> None:
        data=self.load_registry(); data["documents"][1]["prerequisite_documents"].append("docs/Unknown.md"); self.save_registry(data)
        self.assert_fails("unknown prerequisite")

    def test_registry_self_prerequisite_is_rejected(self) -> None:
        data=self.load_registry(); e=data["documents"][1]; e["prerequisite_documents"].append(e["path"]); self.save_registry(data)
        self.assert_fails("document cannot depend on itself")

    def test_registry_prerequisite_cycle_is_rejected(self) -> None:
        data=self.load_registry(); first=data["documents"][0]; second=data["documents"][1]
        first["prerequisite_documents"]=[second["path"]]; self.save_registry(data)
        self.assert_fails("prerequisite cycle detected")

    def test_registry_duplicate_authority_topic_is_rejected(self) -> None:
        data=self.load_registry(); data["documents"][1]["authority_topics"][0]=data["documents"][0]["authority_topics"][0]; self.save_registry(data)
        self.assert_fails("authority topics must be unique")

    def test_registry_empty_authority_topics_is_rejected(self) -> None:
        data=self.load_registry(); data["documents"][0]["authority_topics"]=[]; self.save_registry(data)
        self.assert_fails("authority_topics must be a non-empty list")

    def test_registry_empty_applies_when_is_rejected(self) -> None:
        data=self.load_registry(); data["documents"][0]["applies_when"]=""; self.save_registry(data)
        self.assert_fails("applies_when must be non-empty text")

    def test_registry_repository_role_mismatch_is_rejected(self) -> None:
        data=self.load_registry(); data["documents"][0]["repository_role"]="Proposed other role"; self.save_registry(data)
        self.assert_fails("repository_role mismatch")

    def test_registry_status_mismatch_is_rejected(self) -> None:
        data=self.load_registry(); data["documents"][0]["status"]="Baseline"; self.save_registry(data)
        self.assert_fails("status mismatch")

    def test_readme_version_mismatch_is_rejected(self) -> None:
        p=self.path(README); s=p.read_text(); s=s.replace("| v1.0.18 | Draft for Review |", "| v9.9.9 | Draft for Review |",1); p.write_text(s,encoding="utf-8")
        self.assert_fails("Current Document Set does not exactly match")

    def test_readme_purpose_mismatch_is_rejected(self) -> None:
        p=self.path(README); s=p.read_text(); s=s.replace("AI entry point, authority routing", "Wrong purpose, authority routing",1); p.write_text(s,encoding="utf-8")
        self.assert_fails("Current Document Set does not exactly match")

    def test_readme_order_mismatch_is_rejected(self) -> None:
        p=self.path(README); s=p.read_text(); a=s.index("| [`Coordinator_Architecture_Patterns.md`"); b=s.index("| [`Coordinator_Concurrency_Guide.md`")
        ae=s.index("\n",a)+1; be=s.index("\n",b)+1; line_a=s[a:ae]; line_b=s[b:be]; s=s[:a]+line_b+line_a+s[be:]; p.write_text(s,encoding="utf-8")
        self.assert_fails("Current Document Set does not exactly match")

    def test_readme_manifest_duplicate_heading_is_rejected(self) -> None:
        p=self.path(README); s=p.read_text()+"\n## Current Document Set\n"; p.write_text(s,encoding="utf-8")
        self.assert_fails("expected exactly one controlled manifest heading; found 2")

    def test_ai_manifest_version_mismatch_is_rejected(self) -> None:
        p=self.path(AI_GUIDE); s=p.read_text().replace("`v1.0.18` | Draft for Review | AI authority", "`v9.9.9` | Draft for Review | AI authority",1); p.write_text(s,encoding="utf-8")
        self.assert_fails("Active Document Manifest does not exactly match")

    def test_ai_manifest_routing_role_mismatch_is_rejected(self) -> None:
        p=self.path(AI_GUIDE); s=p.read_text().replace("AI authority routing and operating controls", "Wrong routing role",1); p.write_text(s,encoding="utf-8")
        self.assert_fails("Active Document Manifest does not exactly match")

    def test_ai_manifest_duplicate_heading_is_rejected(self) -> None:
        p=self.path(AI_GUIDE); p.write_text(p.read_text()+"\n## 0.2 Active Document Manifest\n",encoding="utf-8")
        self.assert_fails("expected exactly one controlled manifest heading; found 2")

    def test_missing_metadata_is_rejected(self) -> None:
        p=self.path(UI); p.write_text(p.read_text().replace("**Document Version:** v1.0.1  \n","",1),encoding="utf-8")
        self.assert_fails("missing required metadata: Document Version")

    def test_duplicate_metadata_is_rejected(self) -> None:
        p=self.path(UI); p.write_text(p.read_text().replace("**Status:** Draft for Review", "**Status:** Draft for Review\n**Status:** Draft for Review",1),encoding="utf-8")
        self.assert_fails("metadata 'Status' must appear at most once")

    def test_invalid_semver_is_rejected(self) -> None:
        p=self.path(UI); p.write_text(p.read_text().replace("**Document Version:** v1.0.1", "**Document Version:** 1.0",1),encoding="utf-8")
        self.assert_fails("must match vMAJOR.MINOR.PATCH")

    def test_invalid_status_is_rejected(self) -> None:
        p=self.path(UI); p.write_text(p.read_text().replace("**Status:** Draft for Review", "**Status:** Active",1),encoding="utf-8")
        self.assert_fails("Status 'Active' is not controlled")

    def test_draft_role_must_be_proposed(self) -> None:
        p=self.path(UI); p.write_text(p.read_text().replace("**Repository Role:** Proposed ", "**Repository Role:** ",1),encoding="utf-8")
        self.assert_fails("must begin with 'Proposed '")

    def test_baseline_role_must_be_normative(self) -> None:
        p=self.path("docs/framework/Coordinator_Node_Control_Framework.md"); p.write_text(p.read_text().replace("Normative architecture and framework-governance authority","Supporting architecture notes",1),encoding="utf-8")
        self.assert_fails("must use non-proposed normative wording")

    def test_canonical_filename_mismatch_is_rejected(self) -> None:
        p=self.path(UI); p.write_text(p.read_text().replace("`Coordinator_UI_Engineering_Guide.md`","`Wrong.md`",1),encoding="utf-8")
        self.assert_fails("declared filename")

    def test_both_identity_metadata_keys_are_rejected(self) -> None:
        p=self.path(UI); p.write_text(p.read_text().replace("**Canonical Filename:**", "**Document Name:** `Coordinator_UI_Engineering_Guide.md`  \n**Canonical Filename:**",1),encoding="utf-8")
        self.assert_fails("exactly one of Canonical Filename or Document Name")

    def test_missing_version_history_heading_is_rejected(self) -> None:
        p=self.path(UI); p.write_text(p.read_text().replace("## Version History","## Revision Record",1),encoding="utf-8")
        self.assert_fails("exactly one Version History or Change History heading is required; found 0")

    def test_duplicate_version_history_heading_is_rejected(self) -> None:
        p=self.path(UI); p.write_text(p.read_text()+"\n## Version History\n",encoding="utf-8")
        self.assert_fails("exactly one Version History or Change History heading is required; found 2")

    def test_missing_history_column_is_rejected(self) -> None:
        p=self.path(UI); s=p.read_text().replace("| Version | Date | Status | Summary |","| Version | Date | Summary |",1).replace("|---|---|---|---|","|---|---|---|",1); p.write_text(s,encoding="utf-8")
        self.assert_fails("Version History missing required columns: status")

    def test_history_cell_count_is_rejected(self) -> None:
        p=self.path(UI); s=p.read_text().replace("| v1.0.1 | 2026-07-19 | Draft for Review | Hardened", "| v1.0.1 | 2026-07-19 | Hardened",1); p.write_text(s,encoding="utf-8")
        self.assert_fails("Version History row has")

    def test_invalid_history_date_is_rejected(self) -> None:
        p=self.path(UI); p.write_text(p.read_text().replace("| v1.0.1 | 2026-07-19 |","| v1.0.1 | 2026-99-99 |",1),encoding="utf-8")
        self.assert_fails("current Version History date must be a real ISO")

    def test_empty_history_summary_is_rejected(self) -> None:
        p=self.path(UI); s=re.sub(r"(\| v1\.0\.1 \| 2026-07-19 \| Draft for Review \|)[^|]+(\|)",r"\1 \2",p.read_text(),count=1); p.write_text(s,encoding="utf-8")
        self.assert_fails("summary/description must not be empty")

    def test_missing_supersedes_is_rejected(self) -> None:
        p=self.path(UI); p.write_text(re.sub(r"^\*\*Supersedes Document Version:\*\*.*\n","",p.read_text(),count=1,flags=re.M),encoding="utf-8")
        self.assert_fails("Supersedes Document Version is required")

    def test_wrong_supersedes_is_rejected(self) -> None:
        p=self.path(UI); p.write_text(p.read_text().replace("**Supersedes Document Version:** v1.0.0","**Supersedes Document Version:** v0.9.9",1),encoding="utf-8")
        self.assert_fails("must identify immediate prior version")

    def test_initial_version_must_not_have_supersedes(self) -> None:
        p=self.path("docs/coordinator/Coordinator_Concurrency_Guide.md"); s=p.read_text().replace("**Repository Role:** Proposed topic-specific normative engineering authority for Coordinator concurrency, subordinate to Coordinator Software Engineering Rules","**Repository Role:** Proposed topic-specific normative engineering authority for Coordinator concurrency, subordinate to Coordinator Software Engineering Rules  \n**Supersedes Document Version:** v0.9.9",1); p.write_text(s,encoding="utf-8")
        self.assert_fails("must be absent for an initial version")

    def test_unclosed_fence_is_rejected(self) -> None:
        p=self.path(UI); p.write_text(p.read_text()+"\n```text\nunclosed\n",encoding="utf-8")
        self.assert_fails("unclosed fenced Code block")

    def test_unclosed_html_code_block_is_rejected(self) -> None:
        p=self.path(UI); p.write_text(p.read_text()+"\n<pre>unclosed\n",encoding="utf-8")
        self.assert_fails("unclosed HTML code/example block")

    def test_crlf_is_rejected(self) -> None:
        p=self.path(UI); p.write_bytes(p.read_bytes().replace(b"\n",b"\r\n"))
        self.assert_fails("CR or CRLF line endings are not allowed")

    def test_bom_is_rejected(self) -> None:
        p=self.path(UI); p.write_bytes(b"\xef\xbb\xbf"+p.read_bytes())
        self.assert_fails("UTF-8 BOM is not allowed")

    def test_nul_is_rejected(self) -> None:
        p=self.path(UI); p.write_bytes(p.read_bytes()+b"\x00")
        self.assert_fails("NUL byte is not allowed")

    def test_missing_final_newline_is_rejected(self) -> None:
        p=self.path(UI); p.write_bytes(p.read_bytes().rstrip(b"\n"))
        self.assert_fails("text file must end with a newline")

    def test_uppercase_markdown_extension_is_rejected(self) -> None:
        p=self.path("docs/validation/Extra.MD"); p.write_text("# Extra\n",encoding="utf-8")
        self.assert_fails("Markdown extension must be lowercase .md")

    def test_extra_root_markdown_is_rejected(self) -> None:
        self.path("EXTRA.md").write_text("# Extra\n",encoding="utf-8")
        self.assert_fails("root Markdown files are not allowlisted")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink unsupported")
    def test_symlink_is_rejected(self) -> None:
        os.symlink(self.path(README), self.path("docs/validation/readme-link"))
        self.assert_fails("symbolic links are not allowed")

    def test_yaml_duplicate_key_is_rejected(self) -> None:
        p=self.path(REGISTRY); p.write_text(p.read_text().replace("registry_version: 1","registry_version: 1\nregistry_version: 1",1),encoding="utf-8")
        self.assert_fails("duplicate key")

    def test_yaml_anchor_is_rejected(self) -> None:
        p=self.path(REGISTRY); p.write_text(p.read_text().replace("repository: host-device-control-framework","repository: &repo host-device-control-framework",1),encoding="utf-8")
        self.assert_fails("YAML anchors are not allowed")

    def test_yaml_alias_is_rejected(self) -> None:
        p=self.path(REGISTRY); p.write_text(p.read_text().replace("repository: host-device-control-framework","repository: *repo",1),encoding="utf-8")
        self.assert_fails("YAML aliases are not allowed")

    def test_yaml_tag_is_rejected(self) -> None:
        p=self.path(REGISTRY); p.write_text(p.read_text().replace("repository: host-device-control-framework","repository: !custom host-device-control-framework",1),encoding="utf-8")
        self.assert_fails("YAML tags are not allowed")

    def test_yaml_merge_key_is_rejected(self) -> None:
        p=self.path(REGISTRY); p.write_text(p.read_text()+"\nmerge_test:\n  <<: {}\n",encoding="utf-8")
        self.assert_fails("YAML merge keys are not allowed")

    def test_workflow_runner_is_pinned(self) -> None:
        p=self.path(WORKFLOW); p.write_text(p.read_text().replace("ubuntu-24.04","ubuntu-latest",1),encoding="utf-8")
        self.assert_fails("runs-on must be ubuntu-24.04")

    def test_workflow_python_matrix_is_exact(self) -> None:
        p=self.path(WORKFLOW); p.write_text(p.read_text().replace('["3.10", "3.12"]','["3.12"]',1),encoding="utf-8")
        self.assert_fails("Python matrix must be exactly 3.10 and 3.12")

    def test_workflow_checkout_sha_is_pinned(self) -> None:
        p=self.path(WORKFLOW); p.write_text(p.read_text().replace("actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0","actions/checkout@v7",1),encoding="utf-8")
        self.assert_fails("checkout action must use approved immutable SHA")

    def test_workflow_setup_python_sha_is_pinned(self) -> None:
        p=self.path(WORKFLOW); p.write_text(p.read_text().replace("actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1","actions/setup-python@v6",1),encoding="utf-8")
        self.assert_fails("setup-python action must use approved immutable SHA")

    def test_workflow_hash_install_is_exact(self) -> None:
        p=self.path(WORKFLOW); p.write_text(p.read_text().replace(" --require-hashes","",1),encoding="utf-8")
        self.assert_fails("required exact unconditional run step missing")

    def test_workflow_commands_must_be_separate(self) -> None:
        p=self.path(WORKFLOW); s=p.read_text().replace("run: python tools/validate_repository.py","run: python tools/validate_repository.py && python -m unittest discover -s tests -v",1); p.write_text(s,encoding="utf-8")
        self.assert_fails("validation commands must remain separate exact steps")

    def test_requirements_hash_change_is_rejected(self) -> None:
        p=self.path("requirements-validation.txt"); p.write_text(p.read_text().replace("d766","0000",1),encoding="utf-8")
        self.assert_fails("pinned dependency or approved hashes differ")

    def test_missing_local_link_is_rejected(self) -> None:
        self.force_full_validation = True
        p=self.path(UI); p.write_text(p.read_text()+"\n[Missing](missing.md)\n",encoding="utf-8")
        self.assert_fails("missing link or image target")

    def test_link_escape_is_rejected(self) -> None:
        self.force_full_validation = True
        p=self.path(UI); p.write_text(p.read_text()+"\n[Escape](../../../../outside.md)\n",encoding="utf-8")
        self.assert_fails("link escapes repository")

    def test_missing_heading_anchor_is_rejected(self) -> None:
        self.force_full_validation = True
        p=self.path(UI); p.write_text(p.read_text()+"\n[Missing](#no-such-heading)\n",encoding="utf-8")
        self.assert_fails("missing heading anchor")

    def test_ui_archive_special_entry_rules_are_present(self) -> None:
        text=self.path(UI).read_text(encoding="utf-8")
        for phrase in ("symbolic links", "hard links", "Windows reparse points", "device files", "named pipes", "canonicalized immediately before creation", "time-of-check/time-of-use"):
            self.assertIn(phrase,text)

    def test_logging_hash_authenticity_distinction_is_present(self) -> None:
        text=self.path(LOGGING).read_text(encoding="utf-8")
        self.assertIn("hash manifest detects changed bytes only when the manifest and its provenance remain independently trusted",text)
        self.assertIn("shall not be represented as proof of authorship, authenticity, trusted creation time, or adversarial tamper resistance",text)
        self.assertIn("digitally signed manifest",text)

    def test_testing_hash_authenticity_distinction_is_present(self) -> None:
        text=self.path(TESTING).read_text(encoding="utf-8")
        self.assertIn("shall not be represented as proof of authorship, authenticity, trusted creation time, or adversarial tamper resistance",text)
        self.assertIn("digitally signed or approved authenticated manifest",text)
        self.assertIn("independently protected trust anchor",text)

    def test_readme_authority_boundary_lists_all_guides(self) -> None:
        text=self.path(README).read_text(encoding="utf-8")
        for title in ("Coordinator Architecture Patterns","Coordinator Concurrency Guide","Coordinator Logging Guide","Coordinator Testing Guide","Coordinator UI Engineering Guide"):
            self.assertIn(title,text[text.index("## Authority Boundary"):text.index("## Engineering Principles")])

    def test_readme_repository_structure_lists_all_guides(self) -> None:
        text=self.path(README).read_text(encoding="utf-8")
        section=text[text.index("## Repository Structure"):text.index("## Repository Validation")]
        for filename in ("Coordinator_Architecture_Patterns.md","Coordinator_Concurrency_Guide.md","Coordinator_Logging_Guide.md","Coordinator_Testing_Guide.md","Coordinator_UI_Engineering_Guide.md"):
            self.assertIn(filename,section)


if __name__ == "__main__":
    unittest.main()
