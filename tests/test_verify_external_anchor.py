from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from verify_external_anchor import _visible_sha256, verify_signed_tag


class ExternalAnchorVerifierTests(unittest.TestCase):
    TARGET = "a" * 40
    TAG = "legal-baseline-v1"
    DOCUMENTS = {
        "LICENSE": "license text\n",
        "NOTICE.md": "# Notice\nVisible notice text.\n",
        "CONTRIBUTING.md": "# Contributions\nPrior agreement required.\n",
    }

    def baseline_text(self) -> str:
        baseline = {
            "baseline_version": 1,
            "repository_identity": {
                "host": "github.com",
                "owner": "jkman357",
                "name": "host-device-control-framework",
                "canonical_url": "https://github.com/jkman357/host-device-control-framework",
            },
            "purpose": "legal-text-change-detection",
            "local_validator_scope": "digest-consistency-only",
            "external_authorization_required": True,
            "protected_documents": {
                name: {"normalized_visible_sha256": _visible_sha256(text)}
                for name, text in self.DOCUMENTS.items()
            },
            "external_anchor": {
                "required": True,
                "activation_state": "external-evidence-required",
                "repository_content_claims_activation": False,
                "accepted_modes": ["signed-tag", "protected-merge-with-code-owner-review"],
                "signed_tag_name": self.TAG,
            },
        }
        return yaml.safe_dump(baseline, sort_keys=False)

    def responses(self, *, document_overrides: dict[str, str] | None = None) -> dict[tuple[str, ...], str]:
        documents = dict(self.DOCUMENTS)
        documents.update(document_overrides or {})
        baseline = self.baseline_text()
        result = {
            ("rev-parse", "--is-inside-work-tree"): "true",
            ("rev-parse", "HEAD^{commit}"): self.TARGET,
            ("show", f"{self.TARGET}:legal-baseline.yaml"): baseline,
            ("remote", "get-url", "origin"): "https://github.com/jkman357/host-device-control-framework.git",
            ("cat-file", "-t", f"refs/tags/{self.TAG}"): "tag",
            ("rev-parse", f"refs/tags/{self.TAG}^{{commit}}"): self.TARGET,
            ("verify-tag", self.TAG): "",
            ("show", f"refs/tags/{self.TAG}:legal-baseline.yaml"): baseline,
        }
        for name, text in documents.items():
            result[("show", f"{self.TARGET}:{name}")] = text.rstrip("\n")
        return result

    def run_with(self, responses: dict[tuple[str, ...], str]) -> list[str]:
        def fake_run(_root: Path, args: list[str]) -> str:
            key = tuple(args)
            if key not in responses:
                raise AssertionError(f"unexpected git command: {args}")
            return responses[key]

        with patch("verify_external_anchor._run_git", side_effect=fake_run):
            return verify_signed_tag(Path("/repository"), "HEAD")

    def test_valid_target_commit_passes(self) -> None:
        self.assertEqual([], self.run_with(self.responses()))

    def test_target_commit_protected_document_mismatch_is_rejected(self) -> None:
        errors = self.run_with(
            self.responses(document_overrides={"NOTICE.md": "changed target notice"})
        )
        self.assertTrue(any("NOTICE.md does not match" in error for error in errors))

    def test_malformed_target_baseline_fails_closed_without_type_error(self) -> None:
        responses = self.responses()
        malformed = yaml.safe_load(self.baseline_text())
        malformed["repository_identity"]["owner"] = None
        responses[("show", f"{self.TARGET}:legal-baseline.yaml")] = yaml.safe_dump(
            malformed, sort_keys=False
        )
        errors = self.run_with(responses)
        self.assertIn("target legal baseline canonical repository identity is invalid", errors)


if __name__ == "__main__":
    unittest.main()
