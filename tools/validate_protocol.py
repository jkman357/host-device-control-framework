#!/usr/bin/env python3
"""Validate Protocol YAML structure and Multi-Node semantic constraints."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

ROOT_REQUIRED = {
    "schema_version",
    "document",
    "protocol",
    "wire_format",
    "id_allocation",
    "namespaces",
    "services",
    "enums",
    "errors",
    "messages",
    "compatibility",
    "code_generation",
}
NODE_REQUIRED = {
    "topology",
    "maximum_nodes",
    "maximum_online_nodes",
    "identity",
    "addressing",
    "multi_target",
    "scope",
    "lifecycle",
    "resources",
    "firmware_update",
}
TOPOLOGIES = {
    "single_node",
    "independent_links",
    "shared_multidrop_bus",
    "routed_gateway",
}
ADDRESS_METHODS = {"connection_bound", "frame_address", "route_bound"}
PARTIAL_FAILURE_POLICIES = {
    "not_applicable",
    "per_target_result",
    "best_effort",
    "all_or_nothing",
}
CONCURRENCY_POLICIES = {"one_at_a_time", "bounded_parallel"}
LEGACY_SCHEMA_VERSIONS = {"1.0"}
LEGACY_REQUIRED_FIELDS = {
    "document": ("name", "version", "status"),
    "protocol": ("name", "family", "version"),
    "wire_format": ("byte_order", "implicit_padding"),
    "id_allocation": ("message_id_width_bits",),
    "compatibility": ("minimum_compatible_version",),
    "code_generation": ("enabled",),
}
LEGACY_BYTE_ORDERS = {"little_endian", "big_endian"}
LEGACY_PADDING_POLICIES = {"prohibited", "explicit"}
SENSITIVE_KEY_PATTERN = re.compile(
    r"(?:secret|token|password|credential|private[_-]?key|api[_-]?key)", re.IGNORECASE
)
MAX_ACTUAL_LENGTH = 320


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


@dataclass(frozen=True)
class ValidationIssue:
    rule: str
    path: str
    message: str
    expected: str | None = None
    actual: str | None = None
    correction: str | None = None

    def format(self) -> str:
        parts = [f"{self.rule}: {self.path}: {self.message}"]
        if self.expected is not None:
            parts.append(f"expected={self.expected}")
        if self.actual is not None:
            parts.append(f"actual={self.actual}")
        if self.correction is not None:
            parts.append(f"correction={self.correction}")
        return "; ".join(parts)


def load_yaml(path: Path) -> Any:
    return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_schema(path: Path | None = None) -> dict[str, Any]:
    schema_path = path or (_repo_root() / "schema/protocol.schema.yaml")
    schema = load_yaml(schema_path)
    if not isinstance(schema, dict):
        raise ValueError("Protocol schema root must be a mapping")
    Draft202012Validator.check_schema(schema)
    return schema


def _json_path(parts: Iterable[Any]) -> str:
    result = "$"
    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
        else:
            result += "." + str(part)
    return result


def _redact_value(value: Any, depth: int = 0) -> Any:
    if depth > 4:
        return "<truncated>"
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            result[key_text] = (
                "<redacted>"
                if SENSITIVE_KEY_PATTERN.search(key_text)
                else _redact_value(item, depth + 1)
            )
        return result
    if isinstance(value, list):
        return [_redact_value(item, depth + 1) for item in value[:12]] + (
            ["<truncated>"] if len(value) > 12 else []
        )
    if isinstance(value, tuple):
        return tuple(_redact_value(item, depth + 1) for item in value[:12])
    if isinstance(value, str) and len(value) > 160:
        return value[:157] + "..."
    return value


def _safe_actual(value: Any) -> str:
    text = repr(_redact_value(value))
    if len(text) > MAX_ACTUAL_LENGTH:
        return text[: MAX_ACTUAL_LENGTH - 3] + "..."
    return text


def _schema_issues(document: Any, schema: dict[str, Any]) -> list[ValidationIssue]:
    validator = Draft202012Validator(schema)
    issues: list[ValidationIssue] = []
    errors = sorted(
        validator.iter_errors(document),
        key=lambda item: (list(item.absolute_path), item.message),
    )
    for error in errors:
        issues.append(
            ValidationIssue(
                "PY-SCHEMA-001",
                _json_path(error.absolute_path),
                error.message,
                expected=_safe_actual(error.validator_value),
                actual=_safe_actual(error.instance),
                correction=(
                    "Make the Protocol YAML conform to schema/protocol.schema.yaml "
                    "before semantic linting."
                ),
            )
        )
    return issues


def _get(mapping: Any, key: str, default: Any = None) -> Any:
    return mapping.get(key, default) if isinstance(mapping, dict) else default


def _require_mapping(
    parent: dict[str, Any], key: str, path: str, issues: list[ValidationIssue]
) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        issues.append(
            ValidationIssue(
                "PY-MN-002",
                f"{path}.{key}",
                "value must be a mapping",
                expected="mapping",
                actual=type(value).__name__,
            )
        )
        return {}
    return value


def _legacy_issue(
    issues: list[ValidationIssue],
    path: str,
    message: str,
    *,
    expected: str,
    actual: Any,
) -> None:
    issues.append(
        ValidationIssue(
            "PY-LEGACY-002",
            path,
            message,
            expected=expected,
            actual=_safe_actual(actual),
            correction=(
                "Use the complete legacy Single-Node profile or define an explicit "
                "node_model."
            ),
        )
    )


def _validate_legacy_profile(document: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    schema_version = document.get("schema_version")
    if schema_version not in LEGACY_SCHEMA_VERSIONS:
        issues.append(
            ValidationIssue(
                "PY-LEGACY-001",
                "$.schema_version",
                "node_model omission is permitted only for an explicitly supported legacy schema",
                expected=str(sorted(LEGACY_SCHEMA_VERSIONS)),
                actual=_safe_actual(schema_version),
                correction=(
                    "Use schema_version 1.0 with the complete legacy profile or define "
                    "node_model."
                ),
            )
        )

    mappings: dict[str, dict[str, Any]] = {}
    for section, required_fields in LEGACY_REQUIRED_FIELDS.items():
        value = document.get(section)
        if not isinstance(value, dict):
            _legacy_issue(
                issues,
                f"$.{section}",
                "legacy section must be a mapping",
                expected="mapping",
                actual=type(value).__name__,
            )
            continue
        mappings[section] = value
        for field in required_fields:
            if field not in value:
                _legacy_issue(
                    issues,
                    f"$.{section}.{field}",
                    "required legacy field is missing",
                    expected="present",
                    actual="missing",
                )

    for section in ("namespaces", "services", "enums", "errors", "messages"):
        if not isinstance(document.get(section), list):
            _legacy_issue(
                issues,
                f"$.{section}",
                "legacy collection must be a list",
                expected="list",
                actual=type(document.get(section)).__name__,
            )

    for section in ("document", "protocol"):
        for field in LEGACY_REQUIRED_FIELDS[section]:
            value = mappings.get(section, {}).get(field)
            if not isinstance(value, str) or not value.strip():
                _legacy_issue(
                    issues,
                    f"$.{section}.{field}",
                    "legacy identity field must be a non-empty string",
                    expected="non-empty string",
                    actual=value,
                )

    wire_format = mappings.get("wire_format", {})
    if wire_format.get("byte_order") not in LEGACY_BYTE_ORDERS:
        _legacy_issue(
            issues,
            "$.wire_format.byte_order",
            "legacy byte_order is not controlled",
            expected=str(sorted(LEGACY_BYTE_ORDERS)),
            actual=wire_format.get("byte_order"),
        )
    if wire_format.get("implicit_padding") not in LEGACY_PADDING_POLICIES:
        _legacy_issue(
            issues,
            "$.wire_format.implicit_padding",
            "legacy implicit_padding policy is not controlled",
            expected=str(sorted(LEGACY_PADDING_POLICIES)),
            actual=wire_format.get("implicit_padding"),
        )

    width = mappings.get("id_allocation", {}).get("message_id_width_bits")
    if not isinstance(width, int) or isinstance(width, bool) or width < 1:
        _legacy_issue(
            issues,
            "$.id_allocation.message_id_width_bits",
            "legacy message ID width must be a positive integer",
            expected=">= 1",
            actual=width,
        )

    minimum_version = mappings.get("compatibility", {}).get(
        "minimum_compatible_version"
    )
    if not isinstance(minimum_version, str) or not minimum_version.strip():
        _legacy_issue(
            issues,
            "$.compatibility.minimum_compatible_version",
            "legacy compatibility version must be a non-empty string",
            expected="non-empty string",
            actual=minimum_version,
        )

    enabled = mappings.get("code_generation", {}).get("enabled")
    if not isinstance(enabled, bool):
        _legacy_issue(
            issues,
            "$.code_generation.enabled",
            "legacy code generation enable field must be boolean",
            expected="boolean",
            actual=enabled,
        )
    return issues


def validate_document(
    document: Any, schema: dict[str, Any] | None = None
) -> list[ValidationIssue]:
    """Validate one parsed Protocol YAML document."""
    active_schema = schema if schema is not None else load_schema()
    issues = _schema_issues(document, active_schema)
    if issues:
        return issues
    if not isinstance(document, dict):
        return [
            ValidationIssue(
                "PY-ROOT-001",
                "$",
                "Protocol YAML root must be a mapping",
                expected="mapping",
                actual=type(document).__name__,
            )
        ]
    missing = sorted(ROOT_REQUIRED - set(document))
    if missing:
        issues.append(
            ValidationIssue(
                "PY-ROOT-002",
                "$",
                "required top-level sections are missing",
                expected=", ".join(sorted(ROOT_REQUIRED)),
                actual=", ".join(missing),
                correction="Add all required top-level sections.",
            )
        )
        return issues

    node_model = document.get("node_model")
    if node_model is None:
        return _validate_legacy_profile(document)
    if not isinstance(node_model, dict):
        issues.append(
            ValidationIssue(
                "PY-MN-001",
                "$.node_model",
                "node_model must be a mapping",
                expected="mapping",
                actual=type(node_model).__name__,
            )
        )
        return issues

    missing_node = sorted(NODE_REQUIRED - set(node_model))
    if missing_node:
        issues.append(
            ValidationIssue(
                "PY-MN-003",
                "$.node_model",
                "required Multi-Node fields are missing",
                expected=", ".join(sorted(NODE_REQUIRED)),
                actual=", ".join(missing_node),
            )
        )

    topology = node_model.get("topology")
    maximum_nodes = node_model.get("maximum_nodes")
    maximum_online = node_model.get("maximum_online_nodes")
    if topology not in TOPOLOGIES:
        issues.append(
            ValidationIssue(
                "PY-MN-004",
                "$.node_model.topology",
                "unsupported topology",
                expected=str(sorted(TOPOLOGIES)),
                actual=_safe_actual(topology),
            )
        )
    if (
        not isinstance(maximum_nodes, int)
        or isinstance(maximum_nodes, bool)
        or maximum_nodes < 1
    ):
        issues.append(
            ValidationIssue(
                "PY-MN-004",
                "$.node_model.maximum_nodes",
                "maximum_nodes must be an integer greater than zero",
                expected=">= 1",
                actual=_safe_actual(maximum_nodes),
            )
        )
    if (
        not isinstance(maximum_online, int)
        or isinstance(maximum_online, bool)
        or maximum_online < 1
    ):
        issues.append(
            ValidationIssue(
                "PY-MN-005",
                "$.node_model.maximum_online_nodes",
                "maximum_online_nodes must be an integer greater than zero",
                expected=">= 1",
                actual=_safe_actual(maximum_online),
            )
        )
    if (
        isinstance(maximum_nodes, int)
        and not isinstance(maximum_nodes, bool)
        and isinstance(maximum_online, int)
        and not isinstance(maximum_online, bool)
        and maximum_online > maximum_nodes
    ):
        issues.append(
            ValidationIssue(
                "PY-MN-006",
                "$.node_model.maximum_online_nodes",
                "maximum_online_nodes cannot exceed maximum_nodes",
                expected=f"<= {maximum_nodes}",
                actual=str(maximum_online),
            )
        )
    if topology == "single_node" and maximum_nodes != 1:
        issues.append(
            ValidationIssue(
                "PY-MN-007",
                "$.node_model.maximum_nodes",
                "single_node topology requires maximum_nodes equal to one",
                expected="1",
                actual=_safe_actual(maximum_nodes),
            )
        )

    identity = _require_mapping(node_model, "identity", "$.node_model", issues)
    addressing = _require_mapping(node_model, "addressing", "$.node_model", issues)
    multi_target = _require_mapping(node_model, "multi_target", "$.node_model", issues)
    scope = _require_mapping(node_model, "scope", "$.node_model", issues)
    lifecycle = _require_mapping(node_model, "lifecycle", "$.node_model", issues)
    resources = _require_mapping(node_model, "resources", "$.node_model", issues)
    firmware_update = _require_mapping(
        node_model, "firmware_update", "$.node_model", issues
    )

    if identity and identity.get("node_id_required") is not True:
        issues.append(
            ValidationIssue(
                "PY-MN-010",
                "$.node_model.identity.node_id_required",
                "explicit node_model profiles require stable Node identity",
                expected="true",
                actual=_safe_actual(identity.get("node_id_required")),
            )
        )
    if identity and identity.get("uniqueness_scope") not in {
        "protocol_instance",
        "product",
        "global",
    }:
        issues.append(
            ValidationIssue(
                "PY-MN-011",
                "$.node_model.identity.uniqueness_scope",
                "identity uniqueness scope is not controlled",
                expected="protocol_instance, product, or global",
                actual=_safe_actual(identity.get("uniqueness_scope")),
            )
        )

    method = addressing.get("method") if addressing else None
    target_on_wire = addressing.get("target_required_on_wire") if addressing else None
    if method not in ADDRESS_METHODS:
        issues.append(
            ValidationIssue(
                "PY-MN-015",
                "$.node_model.addressing.method",
                "unsupported addressing method",
                expected=str(sorted(ADDRESS_METHODS)),
                actual=_safe_actual(method),
            )
        )
    if topology == "shared_multidrop_bus" and method != "frame_address":
        issues.append(
            ValidationIssue(
                "PY-MN-016",
                "$.node_model.addressing.method",
                "shared_multidrop_bus requires frame_address",
                expected="frame_address",
                actual=_safe_actual(method),
            )
        )
    if topology in {"shared_multidrop_bus", "routed_gateway"} and target_on_wire is not True:
        issues.append(
            ValidationIssue(
                "PY-MN-017",
                "$.node_model.addressing.target_required_on_wire",
                "shared or routed topology requires an on-wire target",
                expected="true",
                actual=_safe_actual(target_on_wire),
            )
        )
    if (
        topology in {"single_node", "independent_links"}
        and method == "connection_bound"
        and target_on_wire is not False
    ):
        issues.append(
            ValidationIssue(
                "PY-MN-018",
                "$.node_model.addressing.target_required_on_wire",
                "connection-bound addressing must not duplicate the target on wire",
                expected="false",
                actual=_safe_actual(target_on_wire),
            )
        )

    broadcast = addressing.get("broadcast") if addressing else None
    if not isinstance(broadcast, dict):
        issues.append(
            ValidationIssue(
                "PY-MN-019",
                "$.node_model.addressing.broadcast",
                "broadcast must be a mapping",
                expected="mapping",
                actual=type(broadcast).__name__,
            )
        )
    else:
        supported = broadcast.get("supported")
        response_policy = broadcast.get("response_policy")
        if not isinstance(supported, bool):
            issues.append(
                ValidationIssue(
                    "PY-MN-020",
                    "$.node_model.addressing.broadcast.supported",
                    "broadcast supported must be boolean",
                    expected="boolean",
                    actual=_safe_actual(supported),
                )
            )
        if supported is True and response_policy in {
            None,
            "not_applicable",
            "uncontrolled",
        }:
            issues.append(
                ValidationIssue(
                    "PY-MN-021",
                    "$.node_model.addressing.broadcast.response_policy",
                    "broadcast support requires a collision-safe response policy",
                    expected="a defined collision-safe policy",
                    actual=_safe_actual(response_policy),
                )
            )
        if supported is False and response_policy != "not_applicable":
            issues.append(
                ValidationIssue(
                    "PY-MN-022",
                    "$.node_model.addressing.broadcast.response_policy",
                    "disabled broadcast requires not_applicable response policy",
                    expected="not_applicable",
                    actual=_safe_actual(response_policy),
                )
            )

    mt_supported = multi_target.get("supported") if multi_target else None
    partial = multi_target.get("partial_failure_policy") if multi_target else None
    if not isinstance(mt_supported, bool):
        issues.append(
            ValidationIssue(
                "PY-MN-027",
                "$.node_model.multi_target.supported",
                "multi_target supported must be boolean",
                expected="boolean",
                actual=_safe_actual(mt_supported),
            )
        )
    if partial not in PARTIAL_FAILURE_POLICIES:
        issues.append(
            ValidationIssue(
                "PY-MN-023",
                "$.node_model.multi_target.partial_failure_policy",
                "unsupported partial-failure policy",
                expected=str(sorted(PARTIAL_FAILURE_POLICIES)),
                actual=_safe_actual(partial),
            )
        )
    if mt_supported is True and partial == "not_applicable":
        issues.append(
            ValidationIssue(
                "PY-MN-024",
                "$.node_model.multi_target.partial_failure_policy",
                "multi-target support requires an explicit partial-failure policy",
                expected="per_target_result, best_effort, or all_or_nothing",
                actual=_safe_actual(partial),
            )
        )
    if mt_supported is False and partial != "not_applicable":
        issues.append(
            ValidationIssue(
                "PY-MN-025",
                "$.node_model.multi_target.partial_failure_policy",
                "disabled multi-target support requires not_applicable",
                expected="not_applicable",
                actual=_safe_actual(partial),
            )
        )

    allowed_scope_values = {
        "protocol_session": {"global", "connection", "per_node", "group"},
        "secure_session": {"global", "connection", "per_node", "group"},
        "sequence": {
            "global",
            "connection",
            "per_node",
            "per_node_session",
            "group",
        },
        "correlation": {
            "global",
            "connection",
            "per_node",
            "per_node_session",
            "group",
        },
    }
    for field, allowed in allowed_scope_values.items():
        if field not in scope:
            issues.append(
                ValidationIssue(
                    "PY-MN-026",
                    f"$.node_model.scope.{field}",
                    "scope field is required",
                    expected="explicit scope",
                    actual="missing",
                )
            )
        elif scope.get(field) not in allowed:
            issues.append(
                ValidationIssue(
                    "PY-MN-028",
                    f"$.node_model.scope.{field}",
                    "scope value is not controlled",
                    expected=str(sorted(allowed)),
                    actual=_safe_actual(scope.get(field)),
                )
            )
    group_scopes = {
        scope.get("protocol_session"),
        scope.get("secure_session"),
        scope.get("sequence"),
        scope.get("correlation"),
    }
    if "group" in group_scopes:
        security_profile = document.get("security_profile")
        if not isinstance(security_profile, dict) or security_profile.get(
            "group_session_profile"
        ) in {None, "not_applicable"}:
            issues.append(
                ValidationIssue(
                    "PY-MN-030",
                    "$.security_profile.group_session_profile",
                    "group-scoped session state requires an explicit group session profile",
                    expected="defined profile",
                    actual=_safe_actual(
                        _get(security_profile, "group_session_profile")
                    ),
                )
            )

    identity_conflict_policy = lifecycle.get("identity_conflict_policy")
    if identity_conflict_policy not in {
        "reject",
        "quarantine",
        "reject_and_quarantine",
    }:
        issues.append(
            ValidationIssue(
                "PY-MN-031",
                "$.node_model.lifecycle.identity_conflict_policy",
                "identity conflict behavior must use a controlled fail-closed policy",
                expected="reject, quarantine, or reject_and_quarantine",
                actual=_safe_actual(identity_conflict_policy),
            )
        )
    if lifecycle.get("address_reuse_requires_new_connection_generation") is not True:
        issues.append(
            ValidationIssue(
                "PY-MN-032",
                "$.node_model.lifecycle.address_reuse_requires_new_connection_generation",
                "address reuse must create a new connection generation",
                expected="true",
                actual=_safe_actual(
                    lifecycle.get("address_reuse_requires_new_connection_generation")
                ),
            )
        )
    if lifecycle.get("address_reuse_requires_new_secure_session") is not True:
        issues.append(
            ValidationIssue(
                "PY-MN-033",
                "$.node_model.lifecycle.address_reuse_requires_new_secure_session",
                "address reuse must create a new secure session",
                expected="true",
                actual=_safe_actual(
                    lifecycle.get("address_reuse_requires_new_secure_session")
                ),
            )
        )

    per_node = resources.get("maximum_pending_requests_per_node")
    total = resources.get("maximum_total_pending_requests")
    if not isinstance(per_node, int) or isinstance(per_node, bool) or per_node < 1:
        issues.append(
            ValidationIssue(
                "PY-MN-034",
                "$.node_model.resources.maximum_pending_requests_per_node",
                "per-Node pending requests must be bounded",
                expected=">= 1",
                actual=_safe_actual(per_node),
            )
        )
    if not isinstance(total, int) or isinstance(total, bool) or total < 1:
        issues.append(
            ValidationIssue(
                "PY-MN-035",
                "$.node_model.resources.maximum_total_pending_requests",
                "total pending requests must be bounded",
                expected=">= 1",
                actual=_safe_actual(total),
            )
        )
    if (
        isinstance(per_node, int)
        and not isinstance(per_node, bool)
        and isinstance(total, int)
        and not isinstance(total, bool)
        and total < per_node
    ):
        issues.append(
            ValidationIssue(
                "PY-MN-036",
                "$.node_model.resources.maximum_total_pending_requests",
                "total bound cannot be below the per-Node bound",
                expected=f">= {per_node}",
                actual=str(total),
            )
        )

    target_scope = firmware_update.get("target_scope")
    concurrency = firmware_update.get("concurrency")
    if target_scope not in {"single_node", "multi_target"}:
        issues.append(
            ValidationIssue(
                "PY-MN-038",
                "$.node_model.firmware_update.target_scope",
                "unsupported Firmware Update target scope",
                expected="single_node or multi_target",
                actual=_safe_actual(target_scope),
            )
        )
    if concurrency not in CONCURRENCY_POLICIES:
        issues.append(
            ValidationIssue(
                "PY-MN-039",
                "$.node_model.firmware_update.concurrency",
                "unsupported Firmware Update concurrency",
                expected=str(sorted(CONCURRENCY_POLICIES)),
                actual=_safe_actual(concurrency),
            )
        )
    if concurrency == "bounded_parallel":
        parallel = firmware_update.get("maximum_parallel_updates")
        if not isinstance(parallel, int) or isinstance(parallel, bool) or parallel < 1:
            issues.append(
                ValidationIssue(
                    "PY-MN-040",
                    "$.node_model.firmware_update.maximum_parallel_updates",
                    "bounded_parallel requires a positive maximum_parallel_updates",
                    expected=">= 1",
                    actual=_safe_actual(parallel),
                )
            )
        elif (
            isinstance(maximum_online, int)
            and not isinstance(maximum_online, bool)
            and parallel > maximum_online
        ):
            issues.append(
                ValidationIssue(
                    "PY-MN-041",
                    "$.node_model.firmware_update.maximum_parallel_updates",
                    "parallel update bound cannot exceed maximum_online_nodes",
                    expected=f"<= {maximum_online}",
                    actual=str(parallel),
                )
            )
    if target_scope == "multi_target" and mt_supported is not True:
        issues.append(
            ValidationIssue(
                "PY-MN-042",
                "$.node_model.firmware_update.target_scope",
                "multi_target Firmware Update requires multi_target support",
                expected="node_model.multi_target.supported: true",
                actual=_safe_actual(mt_supported),
            )
        )
    return issues


def validate_path(
    path: Path | str, schema_path: Path | str | None = None
) -> list[ValidationIssue]:
    path = Path(path)
    try:
        document = load_yaml(path)
        schema = load_schema(Path(schema_path) if schema_path is not None else None)
    except (OSError, UnicodeError, yaml.YAMLError, ValueError, SchemaError) as exc:
        return [
            ValidationIssue(
                "PY-YAML-001",
                str(path),
                f"unable to load Protocol YAML or schema: {exc}",
            )
        ]
    return validate_document(document, schema)


def _iter_paths(values: Iterable[str]) -> Iterable[Path]:
    for value in values:
        path = Path(value)
        if path.is_dir():
            yield from sorted(path.glob("*.yaml"))
            yield from sorted(path.glob("*.yml"))
        else:
            yield path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Protocol YAML files or directories")
    parser.add_argument(
        "--schema", default=str(_repo_root() / "schema/protocol.schema.yaml")
    )
    args = parser.parse_args(argv)
    paths = list(_iter_paths(args.paths))
    if not paths:
        print(
            "PY-INPUT-001: no Protocol YAML files were found; "
            "provide one or more .yaml/.yml files or a non-empty directory"
        )
        return 1

    failures = 0
    for path in paths:
        issues = validate_path(path, args.schema)
        if issues:
            failures += 1
            for issue in issues:
                print(f"{path}: {issue.format()}")
        else:
            print(f"PASS: {path}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
