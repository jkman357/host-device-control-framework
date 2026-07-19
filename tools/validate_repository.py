#!/usr/bin/env python3
"""Validate repository governance, documentation structure, Protocol assets, and CI controls."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Any, Iterable
from urllib.parse import unquote

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from validate_protocol import UniqueKeyLoader, load_schema, validate_path as validate_protocol_path

CHECKLIST_PRINCIPLE = (
    "Checklists do not independently create requirements. They provide review, traceability, "
    "and evidence-capture views of requirements established by governing authority documents."
)
REGISTRY_ROOT_KEYS = {"registry_version", "repository", "source_of_truth", "policy", "documents"}
REGISTRY_DOCUMENT_KEYS = {
    "display_name", "path", "version", "status", "repository_role", "readme_purpose",
    "routing_role", "applies_when", "authority_topics", "prerequisite_documents",
}
VALID_STATUSES = {"Draft for Review", "Baseline", "Final Baseline"}
INDEX_READMES = {
    "docs/framework/README.md", "docs/protocol/README.md", "docs/coordinator/README.md",
    "docs/node/README.md", "docs/coding-rules/README.md", "docs/validation/README.md",
}
REQUIRED_FILES = {
    "README.md", "CHANGELOG.md", "LICENSE", "NOTICE.md", "authority-registry.yaml",
    "requirements-validation.txt", ".github/workflows/document-validation.yml",
    "schema/protocol.schema.yaml", "tools/validate_repository.py", "tools/validate_protocol.py",
    "tests/test_validate_repository.py", "tests/test_validate_protocol.py",
}
REQUIRED_NOTICE_HEADINGS = {
    "Copyright Notice", "Personal Engineering Project Disclaimer",
    "No Employer or Company Representation", "AI Assistance Disclosure",
    "Third-Party Standards and Trademark Notice", "File-Specific Notice Precedence",
}
CONTROLLED_METADATA = (
    "Document Version", "Status", "Repository Role", "Supersedes Document Version",
)


@dataclass(frozen=True)
class Finding:
    rule: str
    path: str
    message: str

    def format(self) -> str:
        return f"{self.rule}: {self.path}: {self.message}"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _all_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and ".git" not in path.parts)


def _markdown_files(root: Path) -> list[Path]:
    return sorted(path for path in _all_files(root) if path.suffix.casefold() == ".md")


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", lambda match: "\n" * match.group(0).count("\n"), text, flags=re.DOTALL)


def _fence_ranges(lines: list[str]) -> tuple[list[bool], tuple[int, str, int] | None]:
    inside = [False] * len(lines)
    active_char: str | None = None
    active_length = 0
    active_line = 0
    for index, line in enumerate(lines):
        if active_char is None:
            opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
            if opening:
                active_char = opening.group(1)[0]
                active_length = len(opening.group(1))
                active_line = index + 1
                inside[index] = True
                continue
        else:
            inside[index] = True
            closing = re.match(rf"^ {{0,3}}{re.escape(active_char)}{{{active_length},}}\s*$", line)
            if closing:
                active_char = None
                active_length = 0
                active_line = 0
    unclosed = (active_line, active_char, active_length) if active_char is not None else None
    return inside, unclosed


def _outside_fences(lines: list[str]) -> list[tuple[int, str]]:
    inside, _ = _fence_ranges(lines)
    return [(index + 1, line) for index, line in enumerate(lines) if not inside[index]]


def _visible_text(text: str) -> str:
    uncommented = _strip_html_comments(text)
    lines = uncommented.splitlines()
    inside, _ = _fence_ranges(lines)
    return "\n".join("" if inside[index] else line for index, line in enumerate(lines))


def _opening_metadata_region(text: str) -> str:
    visible = _visible_text(text)
    lines = visible.splitlines()
    region: list[str] = []
    for line in lines:
        if re.match(r"^##\s+", line):
            break
        region.append(line)
    return "\n".join(region)


def _metadata_values(text: str, name: str) -> list[str]:
    region = _opening_metadata_region(text)
    pattern = re.compile(rf"^\*\*{re.escape(name)}:\*\*\s*(.*?)\s*(?:  )?$", re.MULTILINE)
    return [match.group(1).strip() for match in pattern.finditer(region)]


def _metadata(text: str, name: str) -> str | None:
    values = _metadata_values(text, name)
    return values[0] if len(values) == 1 else None


def _slug(heading: str) -> str:
    heading = re.sub(r"`([^`]*)`", r"\1", heading.strip().lower())
    heading = re.sub(r"<[^>]+>", "", heading)
    heading = re.sub(r"[^\w\-\s]", "", heading, flags=re.UNICODE)
    return re.sub(r"[\s\-]+", "-", heading).strip("-")


def _headings(text: str) -> list[tuple[int, str, int]]:
    visible = _visible_text(text)
    lines = visible.splitlines()
    headings: list[tuple[int, str, int]] = []
    for index, line in enumerate(lines):
        atx = re.match(r"^(#{1,6})\s+(.+?)(?:\s+#+)?\s*$", line)
        if atx:
            headings.append((len(atx.group(1)), atx.group(2).strip(), index + 1))
            continue
        if index + 1 < len(lines) and line.strip():
            setext = re.match(r"^\s*(=+|-+)\s*$", lines[index + 1])
            if setext:
                headings.append((1 if setext.group(1)[0] == "=" else 2, line.strip(), index + 1))
    return headings


def _anchors(text: str) -> set[str]:
    counts: dict[str, int] = {}
    result: set[str] = set()
    for _, title, _ in _headings(text):
        slug = _slug(title)
        if not slug:
            continue
        count = counts.get(slug, 0)
        result.add(slug if count == 0 else f"{slug}-{count}")
        counts[slug] = count + 1
    return result


def _load_unique_yaml(text: str) -> Any:
    return yaml.load(text, Loader=UniqueKeyLoader)


def check_required_files(root: Path, findings: list[Finding]) -> None:
    for relative in sorted(REQUIRED_FILES):
        if not (root / relative).is_file():
            findings.append(Finding("REP-001", relative, "required repository file is missing"))


def check_text_files(root: Path, findings: list[Finding]) -> None:
    suffixes = {".md", ".yaml", ".yml", ".py", ".txt"}
    for path in _all_files(root):
        if path.suffix.casefold() not in suffixes and path.name != "LICENSE":
            continue
        relative = _relative(root, path)
        data = path.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            findings.append(Finding("REP-002", relative, "UTF-8 BOM is prohibited"))
        if b"\x00" in data:
            findings.append(Finding("REP-003", relative, "NUL byte is prohibited"))
        if b"\r" in data:
            findings.append(Finding("REP-004", relative, "CR or CRLF line ending is prohibited"))
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            findings.append(Finding("REP-005", relative, f"file is not valid UTF-8: {exc}"))
            continue
        if text and not text.endswith("\n"):
            findings.append(Finding("REP-006", relative, "text file must end with a newline"))


def load_registry(root: Path, findings: list[Finding]) -> dict[str, Any] | None:
    path = root / "authority-registry.yaml"
    if not path.is_file():
        return None
    try:
        registry = _load_unique_yaml(_read_text(path))
    except (UnicodeError, yaml.YAMLError) as exc:
        findings.append(Finding("REG-001", "authority-registry.yaml", f"invalid or ambiguous YAML: {exc}"))
        return None
    if not isinstance(registry, dict):
        findings.append(Finding("REG-002", "authority-registry.yaml", "registry root must be a mapping"))
        return None
    if set(registry) != REGISTRY_ROOT_KEYS:
        findings.append(Finding("REG-003", "authority-registry.yaml", f"root keys must equal {sorted(REGISTRY_ROOT_KEYS)}"))
    if registry.get("repository") != "host-device-control-framework":
        findings.append(Finding("REG-004", "authority-registry.yaml", "repository identity must be host-device-control-framework"))
    if registry.get("source_of_truth") != "GitHub main":
        findings.append(Finding("REG-005", "authority-registry.yaml", "source_of_truth must be GitHub main"))
    documents = registry.get("documents")
    if not isinstance(documents, list):
        findings.append(Finding("REG-006", "authority-registry.yaml", "documents must be a list"))
        return registry

    seen_paths: set[str] = set()
    seen_topics: dict[str, str] = {}
    for index, document in enumerate(documents):
        where = f"authority-registry.yaml#documents[{index}]"
        if not isinstance(document, dict):
            findings.append(Finding("REG-007", where, "document entry must be a mapping"))
            continue
        if set(document) != REGISTRY_DOCUMENT_KEYS:
            findings.append(Finding("REG-008", where, f"document keys must equal {sorted(REGISTRY_DOCUMENT_KEYS)}"))
        path_value = document.get("path")
        if not isinstance(path_value, str):
            findings.append(Finding("REG-009", where, "path must be a string"))
            continue
        if path_value in seen_paths:
            findings.append(Finding("REG-010", path_value, "duplicate governed path"))
        seen_paths.add(path_value)
        if document.get("status") not in VALID_STATUSES:
            findings.append(Finding("REG-011", path_value, f"status must be one of {sorted(VALID_STATUSES)}"))
        if not re.fullmatch(r"v\d+\.\d+\.\d+", str(document.get("version", ""))):
            findings.append(Finding("REG-012", path_value, "version must match vMAJOR.MINOR.PATCH"))
        topics = document.get("authority_topics")
        if not isinstance(topics, list) or not topics:
            findings.append(Finding("REG-013", path_value, "authority_topics must be a non-empty list"))
        else:
            for topic in topics:
                topic_text = str(topic)
                if topic_text in seen_topics:
                    findings.append(Finding("REG-014", path_value, f"authority topic duplicates {seen_topics[topic_text]}: {topic_text}"))
                else:
                    seen_topics[topic_text] = path_value
        if not isinstance(document.get("prerequisite_documents"), list):
            findings.append(Finding("REG-015", path_value, "prerequisite_documents must be a list"))

    all_paths = set(seen_paths)
    graph: dict[str, list[str]] = {}
    for document in documents:
        if not isinstance(document, dict) or not isinstance(document.get("path"), str):
            continue
        path_value = document["path"]
        prereqs = document.get("prerequisite_documents", [])
        if not isinstance(prereqs, list):
            continue
        graph[path_value] = [str(item) for item in prereqs]
        for prereq in prereqs:
            if prereq not in all_paths:
                findings.append(Finding("REG-016", path_value, f"unknown prerequisite: {prereq}"))

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, stack: list[str]) -> None:
        if node in visiting:
            findings.append(Finding("REG-017", node, "prerequisite cycle: " + " -> ".join(stack + [node])))
            return
        if node in visited:
            return
        visiting.add(node)
        for nxt in graph.get(node, []):
            visit(nxt, stack + [node])
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node, [])
    return registry


def check_governed_documents(root: Path, registry: dict[str, Any] | None, findings: list[Finding]) -> None:
    if not registry or not isinstance(registry.get("documents"), list):
        return
    registry_by_path = {
        document["path"]: document
        for document in registry["documents"]
        if isinstance(document, dict) and isinstance(document.get("path"), str)
    }
    governed_actual = {
        _relative(root, path)
        for path in _markdown_files(root)
        if _relative(root, path).startswith("docs/") and _relative(root, path) not in INDEX_READMES
    }
    registered = set(registry_by_path)
    for path in sorted(governed_actual - registered):
        findings.append(Finding("DOC-001", path, "governed Markdown is not registered"))
    for path in sorted(registered - governed_actual):
        findings.append(Finding("DOC-002", path, "registered governed Markdown is missing"))

    for relative, document in registry_by_path.items():
        path = root / relative
        if not path.is_file():
            continue
        text = _read_text(path)
        for field in CONTROLLED_METADATA:
            values = _metadata_values(text, field)
            expected_count = 0 if field == "Supersedes Document Version" and document.get("version") == "v1.0.0" else 1
            if len(values) != expected_count:
                findings.append(Finding("DOC-008", relative, f"{field} must appear exactly {expected_count} time(s) in the visible opening metadata region; found {len(values)}"))
        version = _metadata(text, "Document Version")
        status = _metadata(text, "Status")
        role = _metadata(text, "Repository Role")
        if version != document.get("version"):
            findings.append(Finding("DOC-003", relative, f"Document Version {version!r} does not equal registry {document.get('version')!r}"))
        if status != document.get("status"):
            findings.append(Finding("DOC-004", relative, f"Status {status!r} does not equal registry {document.get('status')!r}"))
        if role != document.get("repository_role"):
            findings.append(Finding("DOC-005", relative, "Repository Role does not equal registry repository_role"))
        history_pattern = re.compile(
            rf"^\|\s*{re.escape(str(document.get('version')))}\s*\|.*\|\s*{re.escape(str(document.get('status')))}\s*\|",
            re.MULTILINE,
        )
        if not history_pattern.search(_visible_text(text)):
            findings.append(Finding("DOC-007", relative, "Version History lacks a row matching current version and status"))


def _expected_root_table(registry: dict[str, Any]) -> list[str]:
    rows = ["| Document | Version | Status | Purpose |", "|---|---:|---|---|"]
    for document in registry["documents"]:
        name = Path(document["path"]).name
        rows.append(f"| [`{name}`]({document['path']}) | {document['version']} | {document['status']} | {document['readme_purpose']} |")
    return rows


def _expected_manifest(registry: dict[str, Any]) -> list[str]:
    rows = ["| Document | Canonical Repository Path | Active Version | Status | Routing Role |", "|---|---|---|---|---|"]
    for document in registry["documents"]:
        rows.append(f"| {document['display_name']} | `{document['path']}` | `{document['version']}` | {document['status']} | {document['routing_role']} |")
    return rows


def _extract_table(text: str, header: str) -> list[str] | None:
    lines = _visible_text(text).splitlines()
    matches = [index for index, line in enumerate(lines) if line == header]
    if len(matches) != 1:
        return None
    result: list[str] = []
    for line in lines[matches[0]:]:
        if not line.startswith("|"):
            break
        result.append(line)
    return result


def check_registry_views(root: Path, registry: dict[str, Any] | None, findings: list[Finding]) -> None:
    if not registry or not isinstance(registry.get("documents"), list):
        return
    root_table = _extract_table(_read_text(root / "README.md"), "| Document | Version | Status | Purpose |")
    if root_table != _expected_root_table(registry):
        findings.append(Finding("VIEW-001", "README.md", "Current Document Set table does not exactly match authority-registry.yaml"))
    ai_path = root / "docs/framework/AI_Engineering_Usage_Guide.md"
    manifest = _extract_table(_read_text(ai_path), "| Document | Canonical Repository Path | Active Version | Status | Routing Role |")
    if manifest != _expected_manifest(registry):
        findings.append(Finding("VIEW-002", _relative(root, ai_path), "Active Document Manifest does not exactly match authority-registry.yaml"))
    for document in registry["documents"]:
        path = Path(document["path"])
        index = root / path.parent / "README.md"
        if not index.is_file() or f"]({path.name})" not in _visible_text(_read_text(index)):
            findings.append(Finding("VIEW-003", document["path"], f"directory index does not link {path.name}"))


def check_markdown_structure(root: Path, findings: list[Finding]) -> None:
    for path in _markdown_files(root):
        relative = _relative(root, path)
        text = _read_text(path)
        lines = text.splitlines()
        _, unclosed = _fence_ranges(lines)
        if unclosed is not None:
            findings.append(Finding("MD-003", f"{relative}:{unclosed[0]}", f"unclosed {unclosed[2]}-character fenced code block"))
        headings = _headings(text)
        previous_level = 0
        seen: dict[tuple[int, str], int] = {}
        for level, title, number in headings:
            if previous_level and level > previous_level + 1:
                findings.append(Finding("MD-001", f"{relative}:{number}", f"heading level jumps from H{previous_level} to H{level}"))
            previous_level = level
            key = (level, title.casefold())
            if key in seen:
                findings.append(Finding("MD-002", f"{relative}:{number}", f"duplicate heading at same level; first at line {seen[key]}"))
            else:
                seen[key] = number
        block: list[tuple[int, str]] = []
        for number, line in _outside_fences(lines) + [(len(lines) + 1, "")]:
            if line.startswith("|") and line.endswith("|"):
                block.append((number, line))
            else:
                if len(block) >= 2 and re.match(r"^\|(?:\s*:?-+:?\s*\|)+$", block[1][1]):
                    expected = block[0][1].count("|")
                    for row_number, row in block:
                        if row.count("|") != expected:
                            findings.append(Finding("MD-004", f"{relative}:{row_number}", "Markdown table row has inconsistent column count"))
                block = []


def _markdown_targets(text: str) -> list[tuple[int, str]]:
    visible = _visible_text(text)
    lines = visible.splitlines()
    definitions: dict[str, str] = {}
    for number, line in enumerate(lines, 1):
        definition = re.match(r"^\s{0,3}\[([^\]]+)\]:\s*(\S+)", line)
        if definition:
            definitions[definition.group(1).strip().casefold()] = definition.group(2).strip("<>")
    targets: list[tuple[int, str]] = []
    inline_pattern = re.compile(r"!?\[[^\]]*\]\(([^\s)]+(?:\([^)]*\)[^\s)]*)?)(?:\s+[\"'][^\"']*[\"'])?\)")
    reference_pattern = re.compile(r"!?\[([^\]]+)\]\[([^\]]*)\]")
    html_pattern = re.compile(r"<(?:a|img)\b[^>]*(?:href|src)=[\"']([^\"']+)[\"']", re.IGNORECASE)
    for number, line in enumerate(lines, 1):
        for match in inline_pattern.finditer(line):
            targets.append((number, match.group(1).strip("<>")))
        for match in reference_pattern.finditer(line):
            key = (match.group(2) or match.group(1)).strip().casefold()
            if key not in definitions:
                targets.append((number, f"__MISSING_REFERENCE__:{key}"))
            else:
                targets.append((number, definitions[key]))
        for match in html_pattern.finditer(line):
            targets.append((number, match.group(1)))
    return targets


def check_links(root: Path, findings: list[Finding]) -> None:
    root_resolved = root.resolve()
    for path in _markdown_files(root):
        relative = _relative(root, path)
        text = _read_text(path)
        local_anchors = _anchors(text)
        for number, target in _markdown_targets(text):
            if target.startswith("__MISSING_REFERENCE__:"):
                findings.append(Finding("LINK-005", f"{relative}:{number}", f"undefined reference-style link: {target.split(':', 1)[1]}"))
                continue
            if re.match(r"^(?:https?|mailto|tel):", target):
                continue
            if target.startswith("#"):
                if unquote(target[1:]) not in local_anchors:
                    findings.append(Finding("LINK-001", f"{relative}:{number}", f"missing local anchor {target}"))
                continue
            decoded = unquote(target)
            file_part, _, anchor = decoded.partition("#")
            resolved = (path.parent / file_part).resolve() if file_part else path.resolve()
            try:
                resolved.relative_to(root_resolved)
            except ValueError:
                findings.append(Finding("LINK-002", f"{relative}:{number}", f"link escapes repository: {target}"))
                continue
            if not resolved.exists():
                findings.append(Finding("LINK-003", f"{relative}:{number}", f"link target does not exist: {target}"))
                continue
            if anchor and resolved.is_file() and resolved.suffix.casefold() == ".md":
                if anchor not in _anchors(_read_text(resolved)):
                    findings.append(Finding("LINK-004", f"{relative}:{number}", f"anchor does not exist: {target}"))


def check_filename_policy(root: Path, findings: list[Finding]) -> None:
    casefold_seen: dict[str, str] = {}
    for path in _markdown_files(root):
        relative = _relative(root, path)
        if path.suffix != ".md":
            findings.append(Finding("NAME-002", relative, "Markdown extension must be lowercase .md"))
        if re.search(r"(?:^|[_-])v?\d+\.\d+(?:\.\d+)?(?:[_-]|$)", path.name, re.IGNORECASE):
            findings.append(Finding("NAME-001", relative, "maintained Markdown filename contains a version number"))
        folded = relative.casefold()
        if folded in casefold_seen and casefold_seen[folded] != relative:
            findings.append(Finding("NAME-003", relative, f"case-insensitive path collision with {casefold_seen[folded]}"))
        else:
            casefold_seen[folded] = relative


def check_notice_and_checklists(root: Path, findings: list[Finding]) -> None:
    notice_path = root / "NOTICE.md"
    notice = _read_text(notice_path) if notice_path.is_file() else ""
    headings = {title.strip() for level, title, _ in _headings(notice) if level == 2}
    for heading in sorted(REQUIRED_NOTICE_HEADINGS - headings):
        findings.append(Finding("NOTICE-001", "NOTICE.md", f"missing required section: {heading}"))
    for path in sorted((root / "docs/validation").glob("*Checklist.md")):
        if CHECKLIST_PRINCIPLE not in _visible_text(_read_text(path)):
            findings.append(Finding("CHECK-001", _relative(root, path), "common checklist principle is missing or altered"))


def _normalize_command(command: str) -> str:
    return " ".join(command.replace("\\\n", " ").split())


def _is_unconditional(value: Any) -> bool:
    if value is None:
        return True
    normalized = str(value).strip().casefold()
    return normalized not in {"false", "${{ false }}", "${{false}}", "0", "never()", "${{ never() }}"}


def check_workflow(root: Path, findings: list[Finding]) -> None:
    path = root / ".github/workflows/document-validation.yml"
    if not path.is_file():
        return
    try:
        workflow = _load_unique_yaml(_read_text(path))
    except yaml.YAMLError as exc:
        findings.append(Finding("CI-001", _relative(root, path), f"invalid or ambiguous workflow YAML: {exc}"))
        return
    if not isinstance(workflow, dict) or not isinstance(workflow.get("jobs"), dict):
        findings.append(Finding("CI-003", _relative(root, path), "workflow must define a jobs mapping"))
        return
    required_commands = [
        "python -m pip install --disable-pip-version-check --require-hashes -r requirements-validation.txt",
        "python tools/validate_repository.py",
        "python -m unittest discover -s tests -v",
    ]
    qualifying_job = False
    for job_name, job in workflow["jobs"].items():
        if not isinstance(job, dict):
            continue
        if job.get("runs-on") != "ubuntu-24.04":
            continue
        if not _is_unconditional(job.get("if")) or job.get("continue-on-error") is True:
            continue
        steps = job.get("steps")
        if not isinstance(steps, list):
            continue
        commands: list[str] = []
        invalid_control = False
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            if step.get("continue-on-error") is True or not _is_unconditional(step.get("if")):
                if "run" in step:
                    invalid_control = True
                continue
            if isinstance(step.get("run"), str):
                commands.append(_normalize_command(step["run"]))
        positions: list[int] = []
        for required in required_commands:
            matches = [index for index, command in enumerate(commands) if command == required]
            if len(matches) != 1:
                break
            positions.append(matches[0])
        if len(positions) == len(required_commands) and positions == sorted(positions) and not invalid_control:
            qualifying_job = True
            break
    if not qualifying_job:
        findings.append(Finding("CI-002", _relative(root, path), "an unconditional ubuntu-24.04 job must execute the exact dependency, repository-validator, and unit-test commands once and in order without continue-on-error"))


def check_protocol_assets(root: Path, findings: list[Finding]) -> None:
    schema_path = root / "schema/protocol.schema.yaml"
    try:
        schema = load_schema(schema_path)
        Draft202012Validator.check_schema(schema)
    except (OSError, UnicodeError, yaml.YAMLError, ValueError, SchemaError) as exc:
        findings.append(Finding("PROTO-001", _relative(root, schema_path), f"schema cannot be loaded or is invalid: {exc}"))
        schema = None
    if isinstance(schema, dict):
        properties = schema.get("properties", {})
        node = properties.get("node_model", {}) if isinstance(properties, dict) else {}
        required = set(node.get("required", [])) if isinstance(node, dict) else set()
        expected = {"topology", "maximum_nodes", "maximum_online_nodes", "identity", "addressing", "multi_target", "scope", "lifecycle", "resources", "firmware_update"}
        if not expected.issubset(required):
            findings.append(Finding("PROTO-002", _relative(root, schema_path), "node_model schema is missing required Multi-Node fields"))
    fixtures = root / "tests/fixtures/protocol"
    valid = sorted(fixtures.glob("valid_*.yaml"))
    invalid = sorted(fixtures.glob("invalid_*.yaml"))
    if len(valid) < 5:
        findings.append(Finding("PROTO-003", _relative(root, fixtures), "at least five valid Single-Node/Multi-Node fixtures are required"))
    if len(invalid) < 7:
        findings.append(Finding("PROTO-004", _relative(root, fixtures), "at least seven invalid semantic fixtures are required"))
    for fixture in valid:
        issues = validate_protocol_path(fixture, schema_path)
        if issues:
            findings.append(Finding("PROTO-005", _relative(root, fixture), "valid fixture failed: " + issues[0].format()))
    for fixture in invalid:
        issues = validate_protocol_path(fixture, schema_path)
        if not issues:
            findings.append(Finding("PROTO-006", _relative(root, fixture), "invalid fixture unexpectedly passed"))


def _unreleased_section(text: str) -> str | None:
    match = re.search(r"^##\s+Unreleased\s*$", text, re.MULTILINE)
    if not match:
        return None
    following = re.search(r"^##\s+", text[match.end():], re.MULTILINE)
    end = match.end() + following.start() if following else len(text)
    return text[match.start():end]


def check_changelog(root: Path, findings: list[Finding]) -> None:
    path = root / "CHANGELOG.md"
    text = _read_text(path) if path.is_file() else ""
    section = _unreleased_section(_visible_text(text))
    if section is None:
        findings.append(Finding("CHANGE-001", "CHANGELOG.md", "an unambiguous ## Unreleased section is required"))
        return
    required = ["Multi-Node", "node_model", "validate_protocol.py", "protocol.schema.yaml"]
    for term in required:
        if term not in section:
            findings.append(Finding("CHANGE-001", "CHANGELOG.md", f"Unreleased change record does not mention {term}"))


def validate(root: Path | str) -> list[Finding]:
    root = Path(root).resolve()
    findings: list[Finding] = []
    check_required_files(root, findings)
    check_text_files(root, findings)
    registry = load_registry(root, findings)
    check_governed_documents(root, registry, findings)
    check_registry_views(root, registry, findings)
    check_markdown_structure(root, findings)
    check_links(root, findings)
    check_filename_policy(root, findings)
    check_notice_and_checklists(root, findings)
    check_workflow(root, findings)
    check_protocol_assets(root, findings)
    check_changelog(root, findings)
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    findings = validate(Path(args.root))
    if findings:
        for finding in findings:
            print(finding.format())
        print(f"FAIL: {len(findings)} repository validation finding(s).")
        return 1
    print("PASS: repository documentation, authority registry, Protocol schema, semantic fixtures, and CI controls are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
