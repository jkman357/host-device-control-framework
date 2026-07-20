from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_protocol import load_schema, validate_document, validate_path  # noqa: E402


class ProtocolValidatorTests(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for path in sorted((ROOT / "tests/fixtures/protocol").glob("valid_*.yaml")):
            with self.subTest(path=path.name):
                self.assertEqual([], validate_path(path))

    def test_invalid_fixtures_fail_with_expected_rules(self) -> None:
        manifest = yaml.safe_load(
            (ROOT / "tests/fixtures/protocol_expectations.yaml").read_text(
                encoding="utf-8"
            )
        )
        for path in sorted((ROOT / "tests/fixtures/protocol").glob("invalid_*.yaml")):
            with self.subTest(path=path.name):
                issues = validate_path(path)
                self.assertTrue(issues)
                actual = {issue.rule for issue in issues}
                expected = set(manifest["invalid"][path.name])
                self.assertTrue(expected.issubset(actual), (path.name, expected, actual))

    def test_schema_validation_rejects_wrong_root_field_types(self) -> None:
        document = {
            "schema_version": "1.0",
            "document": [],
            "protocol": {},
            "wire_format": {},
            "id_allocation": {},
            "namespaces": [],
            "services": [],
            "enums": [],
            "errors": [],
            "messages": "not-an-array",
            "compatibility": {},
            "code_generation": {},
        }
        issues = validate_document(document, load_schema())
        self.assertTrue(any(issue.rule == "PY-SCHEMA-001" for issue in issues))

    def test_duplicate_yaml_key_fails_closed(self) -> None:
        text = (
            ROOT / "tests/fixtures/protocol/valid_legacy_single_node.yaml"
        ).read_text(encoding="utf-8")
        text = text.replace(
            "schema_version: '1.0'",
            "schema_version: '1.0'\nschema_version: '2.0'",
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.yaml"
            path.write_text(text, encoding="utf-8")
            issues = validate_path(path)
        self.assertTrue(any(issue.rule == "PY-YAML-001" for issue in issues))

    def test_legacy_single_node_omission_remains_valid(self) -> None:
        path = ROOT / "tests/fixtures/protocol/valid_legacy_single_node.yaml"
        self.assertEqual([], validate_path(path))

    def test_bounded_parallel_requires_limit(self) -> None:
        path = ROOT / "tests/fixtures/protocol/invalid_bounded_parallel_update.yaml"
        rules = {issue.rule for issue in validate_path(path)}
        self.assertIn("PY-MN-040", rules)

    def test_shared_bus_requires_frame_address(self) -> None:
        path = ROOT / "tests/fixtures/protocol/invalid_shared_bus_without_addressing.yaml"
        rules = {issue.rule for issue in validate_path(path)}
        self.assertTrue({"PY-MN-016", "PY-MN-017"} & rules)

    def test_schema_itself_is_draft_2020_12_valid(self) -> None:
        schema = load_schema()
        self.assertEqual(
            "https://json-schema.org/draft/2020-12/schema", schema["$schema"]
        )


if __name__ == "__main__":
    unittest.main()
