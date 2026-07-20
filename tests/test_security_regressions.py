"""Security regression tests for repository and Protocol validator fail-open paths."""

from __future__ import annotations

from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from pathlib import Path
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_protocol
import validate_repository


GOOD_WORKFLOW = """name: Document validation

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  validate-documentation:
    runs-on: ubuntu-24.04
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.12"]
    steps:
      - name: Check out repository
        uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0
        with:
          persist-credentials: false
      - name: Set up Python
        uses: actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install validation dependencies
        run: python -m pip install --disable-pip-version-check --require-hashes -r requirements-validation.txt
      - name: Validate repository documentation
        run: python tools/validate_repository.py
      - name: Run validator regression tests
        run: python -m unittest discover -s tests -v
"""


def _workflow_findings(text: str) -> list[validate_repository.Finding]:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        path = root / ".github/workflows/document-validation.yml"
        path.parent.mkdir(parents=True)
        path.write_text(text, encoding="utf-8")
        findings: list[validate_repository.Finding] = []
        validate_repository.check_workflow(root, findings)
        return findings


class WorkflowSecurityRegressionTests(unittest.TestCase):
    def assert_rejected(self, workflow: str) -> None:
        findings = _workflow_findings(workflow)
        self.assertTrue(any(item.rule == "CI-002" for item in findings), findings)

    def test_current_contract_is_accepted(self) -> None:
        self.assertEqual([], _workflow_findings(GOOD_WORKFLOW))

    def test_arbitrary_job_if_is_rejected(self) -> None:
        self.assert_rejected(
            GOOD_WORKFLOW.replace(
                "    runs-on: ubuntu-24.04\n",
                "    runs-on: ubuntu-24.04\n"
                "    if: github.actor == 'account-that-does-not-exist'\n",
                1,
            )
        )

    def test_expression_continue_on_error_is_rejected(self) -> None:
        self.assert_rejected(
            GOOD_WORKFLOW.replace(
                "    runs-on: ubuntu-24.04\n",
                "    runs-on: ubuntu-24.04\n"
                "    continue-on-error: ${{ true }}\n",
                1,
            )
        )

    def test_missing_pull_request_trigger_is_rejected(self) -> None:
        self.assert_rejected(GOOD_WORKFLOW.replace("  pull_request:\n", "", 1))

    def test_filtered_push_trigger_is_rejected(self) -> None:
        self.assert_rejected(
            GOOD_WORKFLOW.replace(
                "  push:\n",
                "  push:\n    branches: [branch-that-does-not-exist]\n",
                1,
            )
        )

    def test_needs_dependency_is_rejected(self) -> None:
        self.assert_rejected(
            GOOD_WORKFLOW.replace(
                "    runs-on: ubuntu-24.04\n",
                "    runs-on: ubuntu-24.04\n    needs: gate\n",
                1,
            )
        )

    def test_matrix_exclusion_is_rejected(self) -> None:
        self.assert_rejected(
            GOOD_WORKFLOW.replace(
                '        python-version: ["3.10", "3.12"]\n',
                '        python-version: ["3.10", "3.12"]\n'
                '        exclude:\n'
                '          - python-version: "3.10"\n'
                '          - python-version: "3.12"\n',
                1,
            )
        )

    def test_write_permission_is_rejected(self) -> None:
        self.assert_rejected(GOOD_WORKFLOW.replace("  contents: read", "  contents: write", 1))

    def test_checkout_ref_override_is_rejected(self) -> None:
        self.assert_rejected(
            GOOD_WORKFLOW.replace(
                "          persist-credentials: false\n",
                "          persist-credentials: false\n"
                "          ref: refs/heads/clean-copy\n",
                1,
            )
        )

    def test_working_directory_override_is_rejected(self) -> None:
        self.assert_rejected(
            GOOD_WORKFLOW.replace(
                "    strategy:\n",
                "    defaults:\n"
                "      run:\n"
                "        working-directory: clean-copy\n"
                "    strategy:\n",
                1,
            )
        )

    def test_extra_prevalidation_run_step_is_rejected(self) -> None:
        self.assert_rejected(
            GOOD_WORKFLOW.replace(
                "      - name: Install validation dependencies\n",
                "      - name: Replace checked out content\n"
                "        run: git reset --hard HEAD~1\n"
                "      - name: Install validation dependencies\n",
                1,
            )
        )


class ProtocolSecurityRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = validate_protocol.load_schema(ROOT / "schema/protocol.schema.yaml")
        cls.valid_legacy = yaml.safe_load(
            (ROOT / "tests/fixtures/protocol/valid_legacy_single_node.yaml").read_text(
                encoding="utf-8"
            )
        )
        cls.valid_explicit = yaml.safe_load(
            (ROOT / "tests/fixtures/protocol/valid_single_node.yaml").read_text(
                encoding="utf-8"
            )
        )

    def test_valid_legacy_profile_is_accepted(self) -> None:
        self.assertEqual([], validate_protocol.validate_document(self.valid_legacy, self.schema))

    def test_empty_legacy_profile_is_rejected(self) -> None:
        document = {
            "schema_version": "999.999",
            "document": {},
            "protocol": {},
            "wire_format": {},
            "id_allocation": {},
            "namespaces": [],
            "services": [],
            "enums": [],
            "errors": [],
            "messages": [],
            "compatibility": {},
            "code_generation": {},
        }
        rules = {
            issue.rule
            for issue in validate_protocol.validate_document(document, self.schema)
        }
        self.assertIn("PY-LEGACY-001", rules)
        self.assertIn("PY-LEGACY-002", rules)

    def test_boolean_string_is_rejected(self) -> None:
        document = deepcopy(self.valid_explicit)
        document["node_model"]["addressing"]["broadcast"]["supported"] = "yes"
        rules = {
            issue.rule
            for issue in validate_protocol.validate_document(document, self.schema)
        }
        self.assertIn("PY-SCHEMA-001", rules)

    def test_scope_typo_is_rejected(self) -> None:
        document = deepcopy(self.valid_explicit)
        document["node_model"]["scope"]["protocol_session"] = "per_nod"
        rules = {
            issue.rule
            for issue in validate_protocol.validate_document(document, self.schema)
        }
        self.assertIn("PY-SCHEMA-001", rules)

    def test_unknown_identity_conflict_policy_is_rejected(self) -> None:
        document = deepcopy(self.valid_explicit)
        document["node_model"]["lifecycle"]["identity_conflict_policy"] = "log_only"
        rules = {
            issue.rule
            for issue in validate_protocol.validate_document(document, self.schema)
        }
        self.assertIn("PY-SCHEMA-001", rules)

    def test_schema_error_actual_is_bounded_and_redacted(self) -> None:
        document = deepcopy(self.valid_explicit)
        document["node_model"]["addressing"]["broadcast"]["supported"] = {
            "secret_token": "SENSITIVE-" + ("x" * 5000)
        }
        issues = validate_protocol.validate_document(document, self.schema)
        schema_issue = next(issue for issue in issues if issue.rule == "PY-SCHEMA-001")
        self.assertIsNotNone(schema_issue.actual)
        self.assertLessEqual(len(schema_issue.actual or ""), 320)
        self.assertNotIn("SENSITIVE-", schema_issue.actual or "")
        self.assertIn("<redacted>", schema_issue.actual or "")

    def test_fixture_manifest_enforces_expected_rules(self) -> None:
        fixture_root = ROOT / "tests/fixtures/protocol"
        expectations = yaml.safe_load(
            (ROOT / "tests/fixtures/protocol_expectations.yaml").read_text(encoding="utf-8")
        )
        for filename, expected_rules in expectations["valid"].items():
            with self.subTest(filename=filename):
                document = yaml.safe_load(
                    (fixture_root / filename).read_text(encoding="utf-8")
                )
                self.assertEqual(
                    [],
                    validate_protocol.validate_document(document, self.schema),
                )
        for filename, expected_rules in expectations["invalid"].items():
            with self.subTest(filename=filename):
                document = yaml.safe_load(
                    (fixture_root / filename).read_text(encoding="utf-8")
                )
                actual_rules = {
                    issue.rule
                    for issue in validate_protocol.validate_document(document, self.schema)
                }
                self.assertTrue(actual_rules, filename)
                self.assertTrue(set(expected_rules).issubset(actual_rules), (filename, expected_rules, actual_rules))

    def test_empty_directory_cli_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = StringIO()
            with redirect_stdout(output):
                result = validate_protocol.main(
                    [
                        temporary,
                        "--schema",
                        str(ROOT / "schema/protocol.schema.yaml"),
                    ]
                )
        self.assertEqual(1, result)
        self.assertIn("PY-INPUT-001", output.getvalue())


if __name__ == "__main__":
    unittest.main()
