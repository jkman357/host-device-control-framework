#!/usr/bin/env python3
"""Validate Host-Device Protocol YAML structure and Multi-Node semantics."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Iterable

import yaml


ROOT_REQUIRED = (
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
)
NODE_REQUIRED = (
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
)
TOPOLOGIES = {"single_node", "independent_links", "shared_multidrop_bus", "routed_gateway"}
ADDRESS_METHODS = {"connection_bound", "frame_address", "route_bound", "hybrid"}
ADDRESS_ASSIGNMENTS = {"not_applicable", "fixed", "discovered", "assigned"}
BROADCAST_POLICIES = {"no_response", "polled", "slotted", "bounded_window"}
PARTIAL_FAILURE_POLICIES = {"per_target_result", "fail_fast", "best_effort"}
SESSION_SCOPES = {"per_node", "group"}
SEQUENCE_SCOPES = {"per_node_session", "globally_unique"}
CORRELATION_SCOPES = {"per_node_session", "globally_unique"}
UPDATE_TARGET_SCOPES = {"single_node", "multi_target"}
UPDATE_CONCURRENCY = {"one_at_a_time", "bounded_parallel"}


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_mapping(loader: UniqueKeyLoader, node: yaml.Node, deep: bool = False) -> dict[Any, Any]:
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
    _construct_mapping,
)


@dataclass(frozen=True)
class ValidationIssue:
    rule: str
    path: str
    expected: str
    actual: str
    correction: str

    def format(self, source: str | None = None) -> str:
        prefix = f"{source}: " if source else ""
        return (
            f"{prefix}{self.rule} at {self.path}: expected {self.expected}; "
            f"actual {self.actual}. Correction: {self.correction}"
        )


def _actual(value: Any) -> str:
    return repr(value)


def _issue(
    issues: list[ValidationIssue],
    rule: str,
    path: str,
    expected: str,
    actual: Any,
    correction: str,
) -> None:
    issues.append(ValidationIssue(rule, path, expected, _actual(actual), correction))


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _positive_int(
    issues: list[ValidationIssue],
    rule: str,
    path: str,
    value: Any,
    correction: str,
) -> bool:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        _issue(issues, rule, path, "an integer greater than or equal to 1", value, correction)
        return False
    return True


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return yaml.load(stream, Loader=UniqueKeyLoader)


def validate_document(document: Any) -> list[ValidationIssue]:
    """Return structural and semantic issues for one parsed Protocol YAML document."""
    issues: list[ValidationIssue] = []
    if not isinstance(document, dict):
        _issue(
            issues,
            "PY-ROOT-001",
            "$",
            "a YAML mapping",
            document,
            "Make the Protocol YAML root a mapping.",
        )
        return issues

    for key in ROOT_REQUIRED:
        if key not in document:
            _issue(
                issues,
                "PY-ROOT-002",
                f"$.{key}",
                "a required top-level key",
                "missing",
                f"Add the `{key}` section required by the Protocol YAML baseline.",
            )

    node_model = document.get("node_model")
    if node_model is None:
        # Deliberate legacy Single-Node compatibility interpretation.
        return issues
    if not isinstance(node_model, dict):
        _issue(
            issues,
            "PY-MN-001",
            "$.node_model",
            "a mapping",
            node_model,
            "Use the controlled node_model structure or omit it for the legacy Single-Node profile.",
        )
        return issues

    for key in NODE_REQUIRED:
        if key not in node_model:
            _issue(
                issues,
                "PY-MN-002",
                f"$.node_model.{key}",
                "a required node_model field",
                "missing",
                f"Add `{key}` to node_model.",
            )

    topology = node_model.get("topology")
    if topology not in TOPOLOGIES:
        _issue(
            issues,
            "PY-MN-003",
            "$.node_model.topology",
            f"one of {sorted(TOPOLOGIES)}",
            topology,
            "Select a controlled topology value.",
        )

    maximum_nodes = node_model.get("maximum_nodes")
    max_nodes_valid = _positive_int(
        issues,
        "PY-MN-004",
        "$.node_model.maximum_nodes",
        maximum_nodes,
        "Set maximum_nodes to the approved positive Project limit.",
    )
    maximum_online = node_model.get("maximum_online_nodes")
    max_online_valid = _positive_int(
        issues,
        "PY-MN-005",
        "$.node_model.maximum_online_nodes",
        maximum_online,
        "Set maximum_online_nodes to the approved positive Project limit.",
    )
    if max_nodes_valid and max_online_valid and maximum_online > maximum_nodes:
        _issue(
            issues,
            "PY-MN-006",
            "$.node_model.maximum_online_nodes",
            "a value not greater than maximum_nodes",
            maximum_online,
            "Reduce maximum_online_nodes or increase the approved maximum_nodes limit.",
        )
    if topology == "single_node" and maximum_nodes != 1:
        _issue(
            issues,
            "PY-MN-007",
            "$.node_model.maximum_nodes",
            "1 when topology is single_node",
            maximum_nodes,
            "Use maximum_nodes: 1 or select a Multi-Node topology.",
        )
    if topology in {"independent_links", "shared_multidrop_bus", "routed_gateway"} and isinstance(maximum_nodes, int) and maximum_nodes < 2:
        _issue(
            issues,
            "PY-MN-008",
            "$.node_model.maximum_nodes",
            "at least 2 for a Multi-Node topology",
            maximum_nodes,
            "Set a bounded Multi-Node capacity of at least 2.",
        )

    identity = _mapping(node_model.get("identity"))
    if not identity:
        _issue(issues, "PY-MN-009", "$.node_model.identity", "a mapping", node_model.get("identity"), "Define logical Node identity semantics.")
    if topology in {"independent_links", "shared_multidrop_bus", "routed_gateway"} and identity.get("node_id_required") is not True:
        _issue(
            issues,
            "PY-MN-010",
            "$.node_model.identity.node_id_required",
            "true for Multi-Node topology",
            identity.get("node_id_required"),
            "Require a stable logical Node ID distinct from runtime addressing.",
        )
    if not isinstance(identity.get("uniqueness_scope"), str) or not identity.get("uniqueness_scope"):
        _issue(issues, "PY-MN-011", "$.node_model.identity.uniqueness_scope", "a non-empty controlled scope", identity.get("uniqueness_scope"), "Define where Node identity must be unique.")
    if identity.get("persistence") not in {"stable", "session_scoped"}:
        _issue(issues, "PY-MN-012", "$.node_model.identity.persistence", "stable or session_scoped", identity.get("persistence"), "Define the approved identity persistence model.")

    addressing = _mapping(node_model.get("addressing"))
    method = addressing.get("method")
    if method not in ADDRESS_METHODS:
        _issue(issues, "PY-MN-013", "$.node_model.addressing.method", f"one of {sorted(ADDRESS_METHODS)}", method, "Select a controlled targeting/addressing method.")
    assignment = addressing.get("address_assignment")
    if assignment not in ADDRESS_ASSIGNMENTS:
        _issue(issues, "PY-MN-014", "$.node_model.addressing.address_assignment", f"one of {sorted(ADDRESS_ASSIGNMENTS)}", assignment, "Select a controlled runtime address-assignment model.")
    target_on_wire = addressing.get("target_required_on_wire")
    if not isinstance(target_on_wire, bool):
        _issue(issues, "PY-MN-015", "$.node_model.addressing.target_required_on_wire", "a boolean", target_on_wire, "Declare whether target identity/address is required on wire.")
    if topology == "shared_multidrop_bus":
        if method not in {"frame_address", "hybrid"}:
            _issue(issues, "PY-MN-016", "$.node_model.addressing.method", "frame_address or hybrid for shared_multidrop_bus", method, "Define deterministic shared-bus frame addressing.")
        if target_on_wire is not True:
            _issue(issues, "PY-MN-017", "$.node_model.addressing.target_required_on_wire", "true for shared_multidrop_bus", target_on_wire, "Carry or deterministically derive the protected target on the shared bus.")
    if topology == "routed_gateway" and method not in {"route_bound", "hybrid"}:
        _issue(issues, "PY-MN-018", "$.node_model.addressing.method", "route_bound or hybrid for routed_gateway", method, "Bind the target to an explicit route and logical identity.")
    if topology == "independent_links" and method == "connection_bound" and target_on_wire not in {False, True}:
        _issue(issues, "PY-MN-019", "$.node_model.addressing.target_required_on_wire", "a boolean", target_on_wire, "Use false when immutable connection binding uniquely identifies the Node, otherwise true.")

    broadcast = _mapping(addressing.get("broadcast"))
    supported = broadcast.get("supported")
    response_policy = broadcast.get("response_policy")
    if not isinstance(supported, bool):
        _issue(issues, "PY-MN-020", "$.node_model.addressing.broadcast.supported", "a boolean", supported, "Explicitly enable or disable Protocol broadcast.")
    elif supported and response_policy not in BROADCAST_POLICIES:
        _issue(issues, "PY-MN-021", "$.node_model.addressing.broadcast.response_policy", f"one of {sorted(BROADCAST_POLICIES)}", response_policy, "Define a bounded collision-safe response policy.")
    elif not supported and response_policy != "not_applicable":
        _issue(issues, "PY-MN-022", "$.node_model.addressing.broadcast.response_policy", "not_applicable when broadcast is disabled", response_policy, "Set response_policy to not_applicable or explicitly enable broadcast.")

    multi_target = _mapping(node_model.get("multi_target"))
    mt_supported = multi_target.get("supported")
    partial_failure = multi_target.get("partial_failure_policy")
    if not isinstance(mt_supported, bool):
        _issue(issues, "PY-MN-023", "$.node_model.multi_target.supported", "a boolean", mt_supported, "Explicitly enable or disable Coordinator-expanded multi-target operations.")
    elif mt_supported and partial_failure not in PARTIAL_FAILURE_POLICIES:
        _issue(issues, "PY-MN-024", "$.node_model.multi_target.partial_failure_policy", f"one of {sorted(PARTIAL_FAILURE_POLICIES)}", partial_failure, "Define the approved partial-failure semantics.")
    elif not mt_supported and partial_failure != "not_applicable":
        _issue(issues, "PY-MN-025", "$.node_model.multi_target.partial_failure_policy", "not_applicable when multi-target is disabled", partial_failure, "Set partial_failure_policy to not_applicable or enable multi-target operations.")

    scope = _mapping(node_model.get("scope"))
    protocol_session = scope.get("protocol_session")
    secure_session = scope.get("secure_session")
    sequence = scope.get("sequence")
    correlation = scope.get("correlation")
    if protocol_session not in SESSION_SCOPES:
        _issue(issues, "PY-MN-026", "$.node_model.scope.protocol_session", f"one of {sorted(SESSION_SCOPES)}", protocol_session, "Select a controlled Protocol Session scope.")
    if secure_session not in SESSION_SCOPES:
        _issue(issues, "PY-MN-027", "$.node_model.scope.secure_session", f"one of {sorted(SESSION_SCOPES)}", secure_session, "Select a controlled Secure Session scope.")
    if sequence not in SEQUENCE_SCOPES:
        _issue(issues, "PY-MN-028", "$.node_model.scope.sequence", f"one of {sorted(SEQUENCE_SCOPES)}", sequence, "Define Node-aware sequence ownership.")
    if correlation not in CORRELATION_SCOPES:
        _issue(issues, "PY-MN-029", "$.node_model.scope.correlation", f"one of {sorted(CORRELATION_SCOPES)}", correlation, "Define Node-aware request/response correlation ownership.")
    if "group" in {protocol_session, secure_session}:
        security_model = _mapping(document.get("security_model"))
        group_profile = _mapping(security_model.get("group_security_profile"))
        if group_profile.get("approved") is not True:
            _issue(issues, "PY-MN-030", "$.security_model.group_security_profile.approved", "true for group Protocol/Secure Session scope", group_profile.get("approved"), "Add an explicitly approved group security profile or use per_node Session scope.")

    lifecycle = _mapping(node_model.get("lifecycle"))
    if not isinstance(lifecycle.get("identity_conflict_policy"), str) or not lifecycle.get("identity_conflict_policy"):
        _issue(issues, "PY-MN-031", "$.node_model.lifecycle.identity_conflict_policy", "a non-empty controlled policy", lifecycle.get("identity_conflict_policy"), "Define duplicate identity and quarantine behavior.")
    if lifecycle.get("address_reuse_requires_new_connection_generation") is not True:
        _issue(issues, "PY-MN-032", "$.node_model.lifecycle.address_reuse_requires_new_connection_generation", "true", lifecycle.get("address_reuse_requires_new_connection_generation"), "Create a new connection generation after address reuse.")
    if lifecycle.get("address_reuse_requires_new_secure_session") is not True:
        _issue(issues, "PY-MN-033", "$.node_model.lifecycle.address_reuse_requires_new_secure_session", "true", lifecycle.get("address_reuse_requires_new_secure_session"), "Do not inherit the previous Node's Secure Session after address reuse.")

    resources = _mapping(node_model.get("resources"))
    per_node = resources.get("maximum_pending_requests_per_node")
    total = resources.get("maximum_total_pending_requests")
    per_valid = _positive_int(issues, "PY-MN-034", "$.node_model.resources.maximum_pending_requests_per_node", per_node, "Set a positive per-Node pending-request limit.")
    total_valid = _positive_int(issues, "PY-MN-035", "$.node_model.resources.maximum_total_pending_requests", total, "Set a positive aggregate pending-request limit.")
    if per_valid and total_valid and total < per_node:
        _issue(issues, "PY-MN-036", "$.node_model.resources.maximum_total_pending_requests", "a value at least as large as the per-Node limit", total, "Increase the aggregate limit or reduce the per-Node limit.")

    firmware_update = _mapping(node_model.get("firmware_update"))
    target_scope = firmware_update.get("target_scope")
    concurrency = firmware_update.get("concurrency")
    if target_scope not in UPDATE_TARGET_SCOPES:
        _issue(issues, "PY-MN-037", "$.node_model.firmware_update.target_scope", f"one of {sorted(UPDATE_TARGET_SCOPES)}", target_scope, "Define Firmware Update target scope.")
    if concurrency not in UPDATE_CONCURRENCY:
        _issue(issues, "PY-MN-038", "$.node_model.firmware_update.concurrency", f"one of {sorted(UPDATE_CONCURRENCY)}", concurrency, "Define one-at-a-time or bounded-parallel Firmware Update behavior.")
    if target_scope == "multi_target" and mt_supported is not True:
        _issue(issues, "PY-MN-039", "$.node_model.firmware_update.target_scope", "single_node unless multi_target is supported", target_scope, "Enable multi_target with partial-failure semantics or restrict updates to single_node.")
    parallel_limit = firmware_update.get("maximum_parallel_updates")
    if concurrency == "bounded_parallel":
        _positive_int(issues, "PY-MN-040", "$.node_model.firmware_update.maximum_parallel_updates", parallel_limit, "Set the approved positive maximum number of parallel updates.")
    elif parallel_limit not in {None, 1}:
        _issue(issues, "PY-MN-041", "$.node_model.firmware_update.maximum_parallel_updates", "absent or 1 for one_at_a_time", parallel_limit, "Remove the parallel limit or set it to 1.")

    return issues


def validate_path(path: Path) -> list[ValidationIssue]:
    try:
        document = load_yaml(path)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        return [
            ValidationIssue(
                "PY-YAML-001",
                "$",
                "valid UTF-8 YAML with unique mapping keys",
                repr(str(exc)),
                "Correct the YAML syntax, encoding, or duplicate key.",
            )
        ]
    return validate_document(document)


def _iter_paths(values: Iterable[str]) -> list[Path]:
    paths: list[Path] = []
    for value in values:
        path = Path(value)
        if path.is_dir():
            paths.extend(sorted(path.glob("*.yaml")))
        else:
            paths.append(path)
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Protocol YAML files or directories")
    args = parser.parse_args(argv)
    paths = _iter_paths(args.paths)
    if not paths:
        print("No Protocol YAML files found.", file=sys.stderr)
        return 2

    failed = False
    for path in paths:
        issues = validate_path(path)
        if issues:
            failed = True
            for issue in issues:
                print(issue.format(str(path)))
        else:
            print(f"PASS: {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
