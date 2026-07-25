#!/usr/bin/env python3
"""Validate repository governance, documentation structure, Protocol assets, and CI controls."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
import hashlib
from pathlib import Path
import re
from typing import Any, Iterable
from urllib.parse import unquote

import yaml
from jsonschema import Draft202012Validator, FormatChecker
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
    "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE", "NOTICE.md",
    "third-party-materials.yaml", "legal-baseline.yaml", "third-party-evidence/README.md",
    ".github/CODEOWNERS", ".github/REPOSITORY_PROTECTION.md", "authority-registry.yaml",
    "requirements-validation.txt", ".github/workflows/document-validation.yml",
    "schema/protocol.schema.yaml", "schema/framework-conformance-claim.schema.yaml",
    "examples/framework-conformance-claim.yaml", "tools/validate_repository.py",
    "tools/validate_protocol.py", "tools/verify_external_anchor.py",
    "tests/test_validate_repository.py", "tests/test_validate_protocol.py",
    "tests/test_security_regressions.py", "tests/fixtures/protocol_expectations.yaml",
}
REQUIRED_NOTICE_HEADINGS = {
    "Copyright Notice", "Copyright Scope", "Personal Engineering Project Disclaimer",
    "Framework Conformance Claims", "No Employer or Company Representation",
    "AI Assistance Disclosure", "Third-Party Standards and Trademark Notice",
    "File-Specific Notice Precedence", "External Contributions",
}
CONTROLLED_METADATA = (
    "Document Version", "Status", "Repository Role", "Supersedes Document Version",
)
CHECKOUT_ACTION = "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"
SETUP_PYTHON_ACTION = "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1"
REQUIRED_VALIDATION_COMMANDS = [
    "python -m pip install --disable-pip-version-check --require-hashes -r requirements-validation.txt",
    "python tools/validate_repository.py",
    "python -m unittest discover -s tests -v",
]
LEGAL_REPOSITORY_IDENTITY = {
    "host": "github.com", "owner": "jkman357", "name": "host-device-control-framework",
    "canonical_url": "https://github.com/jkman357/host-device-control-framework",
}
LEGAL_PROTECTED_DOCUMENTS = {"LICENSE", "NOTICE.md", "CONTRIBUTING.md"}
REQUIRED_CODEOWNER_PATHS = {
    "/LICENSE", "/NOTICE.md", "/CONTRIBUTING.md", "/legal-baseline.yaml",
    "/third-party-materials.yaml", "/.github/CODEOWNERS", "/.github/REPOSITORY_PROTECTION.md",
    "/tools/validate_repository.py", "/tools/verify_external_anchor.py",
    "/tests/test_validate_repository.py", "/docs/framework/Coordinator_Node_Control_Framework.md",
    "/docs/framework/Framework_Application_Analysis_Template.md",
    "/docs/validation/Framework_Conformance_Checklist.md",
    "/docs/validation/Repository_Validation_Checklist.md",
    "/schema/framework-conformance-claim.schema.yaml",
    "/examples/framework-conformance-claim.yaml",
}
REQUIRED_PROTECTION_MARKERS = {
    "repository-local hashes and tests provide change detection only",
    "authorization therefore requires a control enforced outside the repository content",
    "signed-tag mode", "protected-merge mode",
    "signed-tag mode is the minimum practical external anchor",
    "external-evidence-required", "never self-asserts that the anchor is active",
    "repository release freeze", "a zip, branch name, working tree, or mutable `main` state is not freeze evidence",
    "updating a digest in the same commit is not, by itself, approval",
}
CANONICAL_CLAIM_EXAMPLE_SOURCE = {
    "commit_sha": "e516fa1d58bd99014b965f37215db85ae594704b",
    "document_version": "v1.1.4",
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


def _all_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and ".git" not in path.parts)


def _markdown_files(root: Path) -> list[Path]:
    return sorted(path for path in _all_files(root) if path.suffix.casefold() == ".md")


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _strip_html_comments(text: str) -> str:
    return re.sub(
        r"<!--.*?-->", lambda match: "\n" * match.group(0).count("\n"), text,
        flags=re.DOTALL,
    )


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


def _normalized_visible_text(text: str) -> str:
    return " ".join(_visible_text(text).split())


def _visible_sha256(text: str) -> str:
    return hashlib.sha256(_normalized_visible_text(text).encode("utf-8")).hexdigest()


def _opening_metadata_region(text: str) -> str:
    visible = _visible_text(text)
    region: list[str] = []
    for line in visible.splitlines():
        if re.match(r"^##\s+", line):
            break
        region.append(line)
    return "\n".join(region)


def _metadata_values(text: str, name: str) -> list[str]:
    pattern = re.compile(rf"^\*\*{re.escape(name)}:\*\*\s*(.*?)\s*(?:  )?$", re.MULTILINE)
    return [match.group(1).strip() for match in pattern.finditer(_opening_metadata_region(text))]


def _metadata(text: str, name: str) -> str | None:
    values = _metadata_values(text, name)
    return values[0] if len(values) == 1 else None


def _slug(heading: str) -> str:
    heading = re.sub(r"`([^`]*)`", r"\1", heading.strip().lower())
    heading = re.sub(r"<[^>]+>", "", heading)
    heading = re.sub(r"[^\w\-\s]", "", heading, flags=re.UNICODE)
    return re.sub(r"[\s\-]+", "-", heading).strip("-")


def _headings(text: str) -> list[tuple[int, str, int]]:
    lines = _visible_text(text).splitlines()
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
        document["path"]: document for document in registry["documents"]
        if isinstance(document, dict) and isinstance(document.get("path"), str)
    }
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
    rows = [
        "| Document | Canonical Repository Path | Active Version | Status | Routing Role |",
        "|---|---|---|---|---|",
    ]
    for document in registry["documents"]:
        rows.append(
            f"| {document['display_name']} | `{document['path']}` | `{document['version']}` | {document['status']} | {document['routing_role']} |"
        )
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
    manifest = _extract_table(
        _read_text(ai_path),
        "| Document | Canonical Repository Path | Active Version | Status | Routing Role |",
    )
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
    lines = _visible_text(text).splitlines()
    definitions: dict[str, str] = {}
    for line in lines:
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
            targets.append((number, definitions.get(key, f"__MISSING_REFERENCE__:{key}")))
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
            if anchor and resolved.is_file() and resolved.suffix.casefold() == ".md" and anchor not in _anchors(_read_text(resolved)):
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


def _codeowner_mapping(text: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            result[parts[0]] = parts[1:]
    return result


def check_legal_baseline_and_protection(root: Path, findings: list[Finding]) -> None:
    path = root / "legal-baseline.yaml"
    try:
        baseline = _load_unique_yaml(_read_text(path))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        findings.append(Finding("LEGAL-003", "legal-baseline.yaml", f"cannot load legal baseline: {exc}"))
        return
    if not isinstance(baseline, dict):
        findings.append(Finding("LEGAL-003", "legal-baseline.yaml", "root must be a mapping"))
        return
    if baseline.get("repository_identity") != LEGAL_REPOSITORY_IDENTITY:
        findings.append(Finding("LEGAL-003", "legal-baseline.yaml", "canonical repository identity is invalid"))
    if baseline.get("purpose") != "legal-text-change-detection" or baseline.get("local_validator_scope") != "digest-consistency-only":
        findings.append(Finding("LEGAL-003", "legal-baseline.yaml", "legal baseline purpose or local scope is invalid"))
    if baseline.get("external_authorization_required") is not True:
        findings.append(Finding("LEGAL-003", "legal-baseline.yaml", "external authorization must be explicitly required"))
    protected = baseline.get("protected_documents")
    if not isinstance(protected, dict) or set(protected) != LEGAL_PROTECTED_DOCUMENTS:
        findings.append(Finding("LEGAL-003", "legal-baseline.yaml", "protected document set must exactly match the controlled set"))
    else:
        for relative in sorted(LEGAL_PROTECTED_DOCUMENTS):
            expected = protected.get(relative, {}).get("normalized_visible_sha256") if isinstance(protected.get(relative), dict) else None
            if not isinstance(expected, str) or re.fullmatch(r"[0-9a-f]{64}", expected) is None:
                findings.append(Finding("LEGAL-003", "legal-baseline.yaml", f"invalid digest for {relative}"))
            elif _visible_sha256(_read_text(root / relative)) != expected:
                findings.append(Finding("LEGAL-002", relative, "normalized visible legal text differs from legal-baseline.yaml"))
    owners_path = root / ".github/CODEOWNERS"
    try:
        mapping = _codeowner_mapping(_read_text(owners_path))
    except (OSError, UnicodeError) as exc:
        findings.append(Finding("GOV-003", ".github/CODEOWNERS", f"cannot read CODEOWNERS: {exc}"))
    else:
        for path_pattern in sorted(REQUIRED_CODEOWNER_PATHS):
            if mapping.get(path_pattern) != ["@jkman357"]:
                findings.append(Finding("GOV-003", ".github/CODEOWNERS", f"required controlled owner mapping is missing or altered: {path_pattern} @jkman357"))
    protection_path = root / ".github/REPOSITORY_PROTECTION.md"
    protection = _visible_text(_read_text(protection_path)).casefold() if protection_path.is_file() else ""
    for marker in sorted(REQUIRED_PROTECTION_MARKERS):
        if marker not in protection:
            findings.append(Finding("GOV-003", ".github/REPOSITORY_PROTECTION.md", f"required external-governance marker is missing or altered: {marker}"))


def check_third_party_materials(root: Path, findings: list[Finding]) -> None:
    path = root / "third-party-materials.yaml"
    try:
        document = _load_unique_yaml(_read_text(path))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        findings.append(Finding("TPM-001", "third-party-materials.yaml", f"invalid YAML: {exc}"))
        return
    if not isinstance(document, dict):
        findings.append(Finding("TPM-001", "third-party-materials.yaml", "manifest root must be a mapping"))
        return
    if document.get("manifest_version") != 2 or document.get("repository") != "host-device-control-framework":
        findings.append(Finding("TPM-001", "third-party-materials.yaml", "manifest identity is invalid"))
    policy = document.get("policy")
    expected_policy = {
        "default_terms": "LICENSE", "exception_authority": "controlled-approval-authority",
        "exception_effect": "registered-entire-file-only",
        "required_file_marker": "Third-Party Material ID: <id>",
        "source_evidence_root": "third-party-evidence",
    }
    if policy != expected_policy:
        findings.append(Finding("TPM-001", "third-party-materials.yaml", "manifest policy must exactly match the controlled fail-closed policy"))
    if not isinstance(document.get("approval_authorities"), dict) or not document["approval_authorities"]:
        findings.append(Finding("TPM-001", "third-party-materials.yaml", "approval_authorities must be a non-empty mapping"))
    if not isinstance(document.get("materials"), list):
        findings.append(Finding("TPM-001", "third-party-materials.yaml", "materials must be an array"))


def check_conformance_claim_assets(root: Path, findings: list[Finding]) -> None:
    schema_path = root / "schema/framework-conformance-claim.schema.yaml"
    example_path = root / "examples/framework-conformance-claim.yaml"
    try:
        schema = _load_unique_yaml(_read_text(schema_path))
        Draft202012Validator.check_schema(schema)
    except (OSError, UnicodeError, yaml.YAMLError, SchemaError) as exc:
        findings.append(Finding("CLAIM-001", _relative(root, schema_path), f"claim schema cannot be loaded or is invalid: {exc}"))
        return
    try:
        example = _load_unique_yaml(_read_text(example_path))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        findings.append(Finding("CLAIM-002", _relative(root, example_path), f"claim example cannot be loaded: {exc}"))
        return
    for error in sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(example), key=lambda item: list(item.absolute_path)):
        findings.append(Finding("CLAIM-002", _relative(root, example_path), f"claim example fails: {error.message}"))
    if isinstance(example, dict):
        source = example.get("framework_source")
        identity = source.get("repository_identity") if isinstance(source, dict) else None
        if identity != LEGAL_REPOSITORY_IDENTITY:
            findings.append(Finding("CLAIM-003", _relative(root, example_path), "canonical example repository identity is invalid"))
        if not isinstance(source, dict) or any(source.get(key) != value for key, value in CANONICAL_CLAIM_EXAMPLE_SOURCE.items()):
            findings.append(Finding("CLAIM-003", _relative(root, example_path), "canonical example source pair is not controlled"))


def check_legal_and_conformance_boundaries(root: Path, findings: list[Finding]) -> None:
    check_legal_baseline_and_protection(root, findings)
    check_third_party_materials(root, findings)
    check_conformance_claim_assets(root, findings)


def _normalize_command(command: str) -> str:
    return " ".join(command.replace("\\\n", " ").split())


def _workflow_triggers(workflow: dict[str, Any]) -> Any:
    return workflow.get("on", workflow.get(True))


def _unfiltered_required_triggers(triggers: Any) -> bool:
    return isinstance(triggers, dict) and set(triggers) == {"push", "pull_request"} and all(triggers[name] in (None, {}) for name in ("push", "pull_request"))


def _allowed_keys(mapping: dict[str, Any], allowed: set[str]) -> bool:
    return set(mapping).issubset(allowed)


def _valid_timeout(mapping: dict[str, Any]) -> bool:
    value = mapping.get("timeout-minutes")
    return value is None or (isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 360)


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
    on_key: Any = "on" if "on" in workflow else True
    workflow_contract_ok = (
        on_key in workflow and _unfiltered_required_triggers(_workflow_triggers(workflow))
        and workflow.get("permissions") == {"contents": "read"}
        and set(workflow).issubset({"name", on_key, "permissions", "jobs"})
    )
    qualifying_job = False
    for job in workflow["jobs"].values():
        if not isinstance(job, dict):
            continue
        if not _allowed_keys(job, {"name", "runs-on", "permissions", "strategy", "steps", "timeout-minutes"}):
            continue
        if job.get("runs-on") != "ubuntu-24.04" or not _valid_timeout(job):
            continue
        if "permissions" in job and job.get("permissions") != {"contents": "read"}:
            continue
        strategy = job.get("strategy")
        if not isinstance(strategy, dict) or set(strategy) != {"fail-fast", "matrix"}:
            continue
        if strategy.get("fail-fast") is not False or strategy.get("matrix") != {"python-version": ["3.10", "3.12"]}:
            continue
        steps = job.get("steps")
        if not isinstance(steps, list) or len(steps) != 5 or not all(isinstance(step, dict) and _valid_timeout(step) for step in steps):
            continue
        checkout, setup_python, *run_steps = steps
        if not _allowed_keys(checkout, {"name", "id", "uses", "with", "timeout-minutes"}) or checkout.get("uses") != CHECKOUT_ACTION or checkout.get("with") != {"persist-credentials": False}:
            continue
        if not _allowed_keys(setup_python, {"name", "id", "uses", "with", "timeout-minutes"}) or setup_python.get("uses") != SETUP_PYTHON_ACTION or setup_python.get("with") != {"python-version": "${{ matrix.python-version }}"}:
            continue
        commands: list[str] = []
        run_contract_ok = True
        for step in run_steps:
            if not _allowed_keys(step, {"name", "id", "run", "timeout-minutes"}) or not isinstance(step.get("run"), str):
                run_contract_ok = False
                break
            commands.append(_normalize_command(step["run"]))
        if run_contract_ok and commands == REQUIRED_VALIDATION_COMMANDS:
            qualifying_job = True
            break
    if not workflow_contract_ok or not qualifying_job:
        findings.append(Finding(
            "CI-002", _relative(root, path),
            "workflow must run the protected validation contract on unfiltered push and pull_request triggers with read-only permissions, pinned actions, the exact Python matrix, no dependency/condition/execution bypass fields, and exactly the three approved commands",
        ))


def check_protocol_assets(root: Path, findings: list[Finding]) -> None:
    schema_path = root / "schema/protocol.schema.yaml"
    try:
        schema = load_schema(schema_path)
        Draft202012Validator.check_schema(schema)
    except (OSError, UnicodeError, yaml.YAMLError, ValueError, SchemaError) as exc:
        findings.append(Finding("PROTO-001", _relative(root, schema_path), f"schema cannot be loaded or is invalid: {exc}"))
        return
    fixtures = root / "tests/fixtures/protocol"
    expectations_path = root / "tests/fixtures/protocol_expectations.yaml"
    try:
        expectations = _load_unique_yaml(_read_text(expectations_path))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        findings.append(Finding("PROTO-003", _relative(root, expectations_path), f"fixture expectation manifest cannot be loaded: {exc}"))
        return
    if not isinstance(expectations, dict) or expectations.get("version") != 1 or not isinstance(expectations.get("valid"), dict) or not isinstance(expectations.get("invalid"), dict):
        findings.append(Finding("PROTO-003", _relative(root, expectations_path), "fixture expectation manifest must contain version: 1 plus valid/invalid mappings"))
        return
    valid_expected = expectations["valid"]
    invalid_expected = expectations["invalid"]
    valid = sorted(fixtures.glob("valid_*.yaml"))
    invalid = sorted(fixtures.glob("invalid_*.yaml"))
    if {path.name for path in valid} != set(valid_expected):
        findings.append(Finding("PROTO-004", _relative(root, expectations_path), "valid fixture files must exactly equal the manifest valid mapping"))
    if {path.name for path in invalid} != set(invalid_expected):
        findings.append(Finding("PROTO-004", _relative(root, expectations_path), "invalid fixture files must exactly equal the manifest invalid mapping"))
    covered_profiles: set[str] = set()
    for fixture in valid:
        issues = validate_protocol_path(fixture, schema_path)
        if issues:
            findings.append(Finding("PROTO-005", _relative(root, fixture), "valid fixture failed: " + issues[0].format()))
            continue
        document = _load_unique_yaml(_read_text(fixture))
        node_model = document.get("node_model") if isinstance(document, dict) else None
        if node_model is None:
            covered_profiles.add("legacy_single_node")
        elif isinstance(node_model, dict) and isinstance(node_model.get("topology"), str):
            covered_profiles.add(node_model["topology"])
    required_profiles = {"legacy_single_node", "single_node", "independent_links", "shared_multidrop_bus", "routed_gateway"}
    if not required_profiles.issubset(covered_profiles):
        findings.append(Finding("PROTO-007", _relative(root, fixtures), "valid fixtures do not cover every required topology/profile"))
    for fixture in invalid:
        expected_rules = invalid_expected.get(fixture.name)
        issues = validate_protocol_path(fixture, schema_path)
        if not issues:
            findings.append(Finding("PROTO-006", _relative(root, fixture), "invalid fixture unexpectedly passed"))
            continue
        actual_rules = {issue.rule for issue in issues}
        missing_rules = sorted(set(expected_rules or []) - actual_rules)
        if missing_rules:
            findings.append(Finding("PROTO-008", _relative(root, fixture), "invalid fixture did not produce expected rule(s): " + ", ".join(missing_rules)))


def check_protocol_conformance_tester_governance(root: Path, findings: list[Finding]) -> None:
    guide = root / "docs/protocol/Protocol_YAML_Definition_Guide.md"
    template = root / "docs/framework/Framework_Application_Analysis_Template.md"
    checklist = root / "docs/validation/Protocol_Validation_Checklist.md"
    guide_text = _visible_text(_read_text(guide)) if guide.is_file() else ""
    template_text = _visible_text(_read_text(template)) if template.is_file() else ""
    checklist_text = _visible_text(_read_text(checklist)) if checklist.is_file() else ""
    guide_markers = [
        "### 24.6 Independent Protocol Conformance Tester",
        "independently executable Protocol Conformance Tester",
        "shall not become a competing Protocol authority",
        "may be implemented in Python",
        "shall not replace formal Coordinator/Node interoperability",
    ]
    for marker in guide_markers:
        if marker not in guide_text:
            findings.append(Finding("PCT-001", _relative(root, guide), f"required conformance-tester authority marker is missing: {marker}"))
    template_markers = [
        "## 15.2 Independent Protocol Conformance Tester Decision",
        "Independent Protocol Tester Required",
        "Protocol Source Identity",
        "Golden Test Vector Identity",
        "Physical Node Execution",
        "| Owner |",
        "| Reviewer |",
    ]
    for marker in template_markers:
        if marker not in template_text:
            findings.append(Finding("PCT-002", _relative(root, template), f"required application-analysis field is missing: {marker}"))
    for check_id in ("P-106", "P-107", "P-108", "P-109", "P-115"):
        if not re.search(rf"^\s*- \[ \] {re.escape(check_id)}\b", checklist_text, re.MULTILINE):
            findings.append(Finding("PCT-003", _relative(root, checklist), f"required Protocol tester check is missing: {check_id}"))


def _unreleased_section(text: str) -> str | None:
    match = re.search(r"^##\s+Unreleased\s*$", text, re.MULTILINE)
    if not match:
        return None
    following = re.search(r"^##\s+", text[match.end():], re.MULTILINE)
    end = match.end() + following.start() if following else len(text)
    return text[match.start():end]


def check_changelog(root: Path, findings: list[Finding]) -> None:
    path = root / "CHANGELOG.md"
    section = _unreleased_section(_visible_text(_read_text(path))) if path.is_file() else None
    if section is None:
        findings.append(Finding("CHANGE-001", "CHANGELOG.md", "an unambiguous ## Unreleased section is required"))
        return
    for term in (
        "Multi-Node", "node_model", "validate_protocol.py", "protocol.schema.yaml",
        "third-party-materials.yaml", "legal-baseline.yaml",
        "framework-conformance-claim.schema.yaml", "Scoped Framework Conformance",
        "signed-tag", "patent", "Protocol Conformance Tester",
    ):
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
    check_legal_and_conformance_boundaries(root, findings)
    check_workflow(root, findings)
    check_protocol_assets(root, findings)
    check_protocol_conformance_tester_governance(root, findings)
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
    print(
        "PASS: repository documentation, authority registry, Protocol schema, semantic "
        "fixtures, independent Protocol tester governance, and CI controls are consistent."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
