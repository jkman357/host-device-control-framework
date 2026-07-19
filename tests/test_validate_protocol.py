from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_protocol import load_yaml, validate_document, validate_path  # noqa: E402


class ProtocolValidatorTests(unittest.TestCase):
    fixtures = ROOT / "tests" / "fixtures" / "protocol"

    def test_all_valid_fixtures_pass(self) -> None:
        for path in sorted(self.fixtures.glob("valid_*.yaml")):
            with self.subTest(path=path.name):
                self.assertEqual([], validate_path(path))

    def test_invalid_fixtures_fail_expected_rules(self) -> None:
        expected = {
            "invalid_maximum_nodes_zero.yaml": {"PY-MN-004"},
            "invalid_shared_bus_without_addressing.yaml": {"PY-MN-016", "PY-MN-017"},
            "invalid_broadcast_response_policy.yaml": {"PY-MN-021"},
            "invalid_multi_target_partial_failure.yaml": {"PY-MN-024"},
            "invalid_group_session_without_profile.yaml": {"PY-MN-030"},
            "invalid_bounded_parallel_update.yaml": {"PY-MN-040"},
            "invalid_address_reuse_session.yaml": {"PY-MN-033"},
        }
        for name, expected_rules in expected.items():
            with self.subTest(path=name):
                rules = {issue.rule for issue in validate_path(self.fixtures / name)}
                self.assertTrue(expected_rules.issubset(rules), (name, rules))

    def test_node_model_omission_is_legacy_single_node(self) -> None:
        document = load_yaml(self.fixtures / "valid_legacy_single_node.yaml")
        self.assertNotIn("node_model", document)
        self.assertEqual([], validate_document(document))

    def test_error_message_contains_actionable_fields(self) -> None:
        issue = validate_path(self.fixtures / "invalid_maximum_nodes_zero.yaml")[0]
        rendered = issue.format("fixture.yaml")
        self.assertIn(issue.rule, rendered)
        self.assertIn(issue.path, rendered)
        self.assertIn("expected", rendered)
        self.assertIn("actual", rendered)
        self.assertIn("Correction:", rendered)


if __name__ == "__main__":
    unittest.main()
