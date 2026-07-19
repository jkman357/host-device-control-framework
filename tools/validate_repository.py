#!/usr/bin/env python3
"""Validate repository governance, documentation structure, and Protocol fixtures."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Iterable
from urllib.parse import unquote

import yaml

from validate_protocol import validate_path as validate_protocol_path

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
    "docs/framework/README.md",
    "docs/protocol/README.md",
    "docs/coordinator/README.md",
    "docs/node/README.md",
    "docs/coding-rules/README.md",
    "docs/validation/README.md",
}
REQUIRED_FILES = {
    "README.md", "CHANGELOG.md", "LICENSE", "NOTICE.md", "authority-registry.yaml",
    "requirements-validation.txt", ".github/workflows/document-validation.yml",
    "schema/protocol.schema.yaml", "tools/validate_repository.py", "tools/validate_protocol.py",
    "tests/test_validate_repository.py", "tests/test_validate_protocol.py",
}
REQUIRED_NOTICE_HEADINGS = {
    "Copyright Notice", "Personal Engineering Project Disclaimer", "No Employer or Company Representation",
    "AI Assistance Disclosure", "Third-Party Standards and Trademark Notice", "File-Specific Notice Precedence",
}


@dataclass(frozen=True)
class Finding:
    rule: str
    path: str
    message: str

    def format(self) -> str:
        return f"{self.rule}: {self.path}: {self.message}"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _markdown_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.md") if ".git" not in p.parts)


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _metadata(text: str, name: str) -> str | None:
    match = re.search(rf"^\*\*{re.escape(name)}:\*\*\s*(.*?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _slug(heading: str) -> str:
    heading = re.sub(r"`([^`]*)`", r"\1", heading.strip().lower())
    heading = re.sub(r"[^\w\-\s]", "", heading, flags=re.UNICODE)
    return re.sub(r"[\s\-]+", "-", heading).strip("-")


def _outside_fences(lines: list[str]) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    fence: str | None = None
    for number, line in enumerate(lines, 1):
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            token = match.group(1)[0]
            if fence is None:
                fence = token
            elif fence == token:
                fence = None
            continue
        if fence is None:
            result.append((number, line))
    return result


def check_required_files(root: Path, findings: list[Finding]) -> None:
    for relative in sorted(REQUIRED_FILES):
        if not (root / relative).is_file():
            findings.append(Finding("REP-001", relative, "required repository file is missing"))


def check_text_files(root: Path, findings: list[Finding]) -> None:
    suffixes = {".md", ".yaml", ".yml", ".py", ".txt"}
    for path in sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts):
        if path.suffix.lower() not in suffixes and path.name not in {"LICENSE"}:
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


def load_registry(root: Path, findings: list[Finding]) -> dict | None:
    path = root / "authority-registry.yaml"
    if not path.is_file():
        return None
    try:
        registry = yaml.safe_load(_read_text(path))
    except (UnicodeError, yaml.YAMLError) as exc:
        findings.append(Finding("REG-001", "authority-registry.yaml", f"invalid YAML: {exc}"))
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
                if topic in seen_topics:
                    findings.append(Finding("REG-014", path_value, f"authority topic duplicates {seen_topics[topic]}: {topic}"))
                else:
                    seen_topics[str(topic)] = path_value
        prereqs = document.get("prerequisite_documents")
        if not isinstance(prereqs, list):
            findings.append(Finding("REG-015", path_value, "prerequisite_documents must be a list"))
    all_paths = set(seen_paths)
    for document in documents:
        if not isinstance(document, dict):
            continue
        for prereq in document.get("prerequisite_documents", []):
            if prereq not in all_paths:
                findings.append(Finding("REG-016", document.get("path", where), f"unknown prerequisite: {prereq}"))
    # Cycle detection.
    graph = {d["path"]: list(d.get("prerequisite_documents", [])) for d in documents if isinstance(d, dict) and isinstance(d.get("path"), str)}
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


def check_governed_documents(root: Path, registry: dict | None, findings: list[Finding]) -> None:
    if not registry or not isinstance(registry.get("documents"), list):
        return
    registry_by_path = {d["path"]: d for d in registry["documents"] if isinstance(d, dict) and isinstance(d.get("path"), str)}
    governed_actual = {
        _relative(root, path) for path in _markdown_files(root)
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
        version = _metadata(text, "Document Version")
        status = _metadata(text, "Status")
        role = _metadata(text, "Repository Role")
        if version != document.get("version"):
            findings.append(Finding("DOC-003", relative, f"Document Version {version!r} does not equal registry {document.get('version')!r}"))
        if status != document.get("status"):
            findings.append(Finding("DOC-004", relative, f"Status {status!r} does not equal registry {document.get('status')!r}"))
        if role != document.get("repository_role"):
            findings.append(Finding("DOC-005", relative, "Repository Role does not equal registry repository_role"))
        if _metadata(text, "Supersedes Document Version") is None and document.get("version") != "v1.0.0":
            findings.append(Finding("DOC-006", relative, "Supersedes metadata is required after the initial v1.0.0 release"))
        history_pattern = re.compile(rf"^\|\s*{re.escape(str(document.get('version')))}\s*\|.*\|\s*{re.escape(str(document.get('status')))}\s*\|", re.MULTILINE)
        if not history_pattern.search(text):
            findings.append(Finding("DOC-007", relative, "Version History lacks a row matching current version and status"))


def _expected_root_table(registry: dict) -> list[str]:
    rows = ["| Document | Version | Status | Purpose |", "|---|---:|---|---|"]
    for d in registry["documents"]:
        name = Path(d["path"]).name
        rows.append(f"| [`{name}`]({d['path']}) | {d['version']} | {d['status']} | {d['readme_purpose']} |")
    return rows


def _expected_manifest(registry: dict) -> list[str]:
    rows = ["| Document | Canonical Repository Path | Active Version | Status | Routing Role |", "|---|---|---|---|---|"]
    for d in registry["documents"]:
        rows.append(f"| {d['display_name']} | `{d['path']}` | `{d['version']}` | {d['status']} | {d['routing_role']} |")
    return rows


def _extract_table(text: str, header: str) -> list[str] | None:
    lines = text.splitlines()
    try:
        index = lines.index(header)
    except ValueError:
        return None
    result = []
    for line in lines[index:]:
        if not line.startswith("|"):
            break
        result.append(line)
    return result


def check_registry_views(root: Path, registry: dict | None, findings: list[Finding]) -> None:
    if not registry or not isinstance(registry.get("documents"), list):
        return
    root_table = _extract_table(_read_text(root / "README.md"), "| Document | Version | Status | Purpose |")
    if root_table != _expected_root_table(registry):
        findings.append(Finding("VIEW-001", "README.md", "Current Document Set table does not exactly match authority-registry.yaml"))
    ai_path = root / "docs/framework/AI_Engineering_Usage_Guide.md"
    manifest = _extract_table(_read_text(ai_path), "| Document | Canonical Repository Path | Active Version | Status | Routing Role |")
    if manifest != _expected_manifest(registry):
        findings.append(Finding("VIEW-002", _relative(root, ai_path), "Active Document Manifest does not exactly match authority-registry.yaml"))
    for d in registry["documents"]:
        path = Path(d["path"])
        index = root / path.parent / "README.md"
        if not index.is_file() or f"]({path.name})" not in _read_text(index):
            findings.append(Finding("VIEW-003", d["path"], f"directory index does not link {path.name}"))


def check_markdown_structure(root: Path, findings: list[Finding]) -> None:
    for path in _markdown_files(root):
        relative = _relative(root, path)
        text = _read_text(path)
        lines = text.splitlines()
        fence_char: str | None = None
        fence_line = 0
        headings: list[tuple[int, str, int]] = []
        previous_level = 0
        for number, line in _outside_fences(lines):
            match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
            if match:
                level = len(match.group(1))
                title = match.group(2)
                headings.append((level, title, number))
                if previous_level and level > previous_level + 1:
                    findings.append(Finding("MD-001", f"{relative}:{number}", f"heading level jumps from H{previous_level} to H{level}"))
                previous_level = level
        seen: dict[tuple[int, str], int] = {}
        for level, title, number in headings:
            key = (level, title.casefold())
            if key in seen:
                findings.append(Finding("MD-002", f"{relative}:{number}", f"duplicate heading at same level; first at line {seen[key]}"))
            else:
                seen[key] = number
        for number, line in enumerate(lines, 1):
            match = re.match(r"^\s*(`{3,}|~{3,})", line)
            if match:
                char = match.group(1)[0]
                if fence_char is None:
                    fence_char, fence_line = char, number
                elif fence_char == char:
                    fence_char = None
        if fence_char is not None:
            findings.append(Finding("MD-003", f"{relative}:{fence_line}", "unclosed fenced code block"))
        # Markdown table consistency outside fences.
        block: list[tuple[int, str]] = []
        for number, line in _outside_fences(lines) + [(len(lines)+1, "")]:
            if line.startswith("|") and line.endswith("|"):
                block.append((number, line))
            else:
                if len(block) >= 2 and re.match(r"^\|(?:\s*:?-+:?\s*\|)+$", block[1][1]):
                    expected = block[0][1].count("|")
                    for row_number, row in block:
                        if row.count("|") != expected:
                            findings.append(Finding("MD-004", f"{relative}:{row_number}", "Markdown table row has inconsistent column count"))
                block = []


def check_links(root: Path, findings: list[Finding]) -> None:
    pattern = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
    for path in _markdown_files(root):
        relative = _relative(root, path)
        text = _read_text(path)
        for number, line in _outside_fences(text.splitlines()):
            for raw in pattern.findall(line):
                target = raw.strip().split()[0].strip("<>")
                if re.match(r"^(?:https?|mailto):", target) or target.startswith("#"):
                    if target.startswith("#"):
                        anchors = {_slug(h.group(2)) for h in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, re.MULTILINE)}
                        if target[1:] not in anchors:
                            findings.append(Finding("LINK-001", f"{relative}:{number}", f"missing local anchor {target}"))
                    continue
                decoded = unquote(target)
                file_part, sep, anchor = decoded.partition("#")
                resolved = (path.parent / file_part).resolve() if file_part else path.resolve()
                try:
                    resolved.relative_to(root.resolve())
                except ValueError:
                    findings.append(Finding("LINK-002", f"{relative}:{number}", f"link escapes repository: {target}"))
                    continue
                if not resolved.exists():
                    findings.append(Finding("LINK-003", f"{relative}:{number}", f"link target does not exist: {target}"))
                    continue
                if anchor and resolved.is_file() and resolved.suffix.lower() == ".md":
                    target_text = _read_text(resolved)
                    anchors = {_slug(h.group(2)) for h in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", target_text, re.MULTILINE)}
                    if anchor not in anchors:
                        findings.append(Finding("LINK-004", f"{relative}:{number}", f"anchor does not exist: {target}"))


def check_filename_policy(root: Path, findings: list[Finding]) -> None:
    for path in _markdown_files(root):
        if re.search(r"(?:^|[_-])v?\d+\.\d+(?:\.\d+)?(?:[_-]|$)", path.name, re.IGNORECASE):
            findings.append(Finding("NAME-001", _relative(root, path), "maintained Markdown filename contains a version number"))


def check_notice_and_checklists(root: Path, findings: list[Finding]) -> None:
    notice = _read_text(root / "NOTICE.md") if (root / "NOTICE.md").is_file() else ""
    headings = {m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", notice, re.MULTILINE)}
    for heading in sorted(REQUIRED_NOTICE_HEADINGS - headings):
        findings.append(Finding("NOTICE-001", "NOTICE.md", f"missing required section: {heading}"))
    for path in sorted((root / "docs/validation").glob("*Checklist.md")):
        if CHECKLIST_PRINCIPLE not in _read_text(path):
            findings.append(Finding("CHECK-001", _relative(root, path), "common checklist principle is missing or altered"))


def check_workflow(root: Path, findings: list[Finding]) -> None:
    path = root / ".github/workflows/document-validation.yml"
    if not path.is_file():
        return
    try:
        workflow = yaml.safe_load(_read_text(path))
    except yaml.YAMLError as exc:
        findings.append(Finding("CI-001", _relative(root, path), f"invalid workflow YAML: {exc}"))
        return
    text = _read_text(path)
    required = [
        "ubuntu-24.04",
        "python -m pip install --disable-pip-version-check --require-hashes -r requirements-validation.txt",
        "python tools/validate_repository.py",
        "python -m unittest discover -s tests -v",
    ]
    for value in required:
        if value not in text:
            findings.append(Finding("CI-002", _relative(root, path), f"required workflow control missing: {value}"))
    if not isinstance(workflow, dict) or "jobs" not in workflow:
        findings.append(Finding("CI-003", _relative(root, path), "workflow must define jobs"))


def check_protocol_assets(root: Path, findings: list[Finding]) -> None:
    schema_path = root / "schema/protocol.schema.yaml"
    try:
        schema = yaml.safe_load(_read_text(schema_path))
    except (OSError, yaml.YAMLError) as exc:
        findings.append(Finding("PROTO-001", _relative(root, schema_path), f"schema cannot be loaded: {exc}"))
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
    for path in valid:
        issues = validate_protocol_path(path)
        if issues:
            findings.append(Finding("PROTO-005", _relative(root, path), "valid fixture failed: " + issues[0].format()))
    for path in invalid:
        issues = validate_protocol_path(path)
        if not issues:
            findings.append(Finding("PROTO-006", _relative(root, path), "invalid fixture unexpectedly passed"))


def check_changelog(root: Path, findings: list[Finding]) -> None:
    text = _read_text(root / "CHANGELOG.md") if (root / "CHANGELOG.md").is_file() else ""
    required = ["Multi-Node", "node_model", "validate_protocol.py", "protocol.schema.yaml"]
    for term in required:
        if term not in text:
            findings.append(Finding("CHANGE-001", "CHANGELOG.md", f"current change record does not mention {term}"))


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
