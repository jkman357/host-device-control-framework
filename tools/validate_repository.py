#!/usr/bin/env python3
"""Validate repository governance, documentation structure, Protocol assets, and CI controls."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
import hashlib
from pathlib import Path, PurePosixPath
import re
import stat
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
    ".gitattributes", "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE", "NOTICE.md",
    "third-party-materials.yaml", "legal-baseline.yaml", "third-party-evidence/README.md",
    ".github/CODEOWNERS", ".github/REPOSITORY_PROTECTION.md", "authority-registry.yaml",
    "requirements-validation.txt", ".github/workflows/document-validation.yml",
    "schema/protocol.schema.yaml", "schema/framework-conformance-claim.schema.yaml",
    "examples/framework-conformance-claim.yaml", "tools/validate_repository.py",
    "tools/validate_protocol.py", "tools/verify_external_anchor.py",
    "tests/test_validate_repository.py", "tests/test_validate_protocol.py",
    "tests/test_security_regressions.py", "tests/test_verify_external_anchor.py",
    "tests/fixtures/protocol_expectations.yaml",
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
    "/.gitattributes",
    "/README.md", "/CHANGELOG.md", "/authority-registry.yaml", "/requirements-validation.txt",
    "/.github/workflows/", "/docs/", "/schema/", "/tools/", "/tests/", "/examples/",
    "/third-party-evidence/",
}
REQUIRED_PROTECTION_MARKERS = {
    "repository-local hashes and tests provide change detection only",
    "authorization therefore requires a control enforced outside the repository content",
    "signed-tag mode", "protected-merge mode",
    "signed-tag mode is the minimum practical external anchor",
    "external-evidence-required", "never self-asserts that the anchor is active",
    "repository release freeze", "a zip, branch name, working tree, or mutable `main` state is not freeze evidence",
    "updating a digest in the same commit is not, by itself, approval",
    "all governed authority documents under `docs/`",
    "all validator, verifier, regression-test, and fixture content under `tools/` and `tests/`",
    "the verifier is commit-scoped", "protected legal-document digests that match the target commit",
    "does not attest to uncommitted working-tree content",
}
CANONICAL_CLAIM_EXAMPLE_SOURCE = {
    "commit_sha": "e516fa1d58bd99014b965f37215db85ae594704b",
    "document_version": "v1.1.4",
}
AI_ROUTING_HISTORY_EXPECTATIONS = {
    "v1.0.27": {
        "Protocol YAML Definition Guide": "v1.1.1",
        "Framework Application Analysis Template": "v1.1.3",
        "Protocol Validation Checklist": "v1.1.1",
    },
    "v1.0.28": {
        "Protocol YAML Definition Guide": "v1.1.2",
        "Framework Application Analysis Template": "v1.1.4",
        "Protocol Validation Checklist": "v1.1.2",
    },
    "v1.0.29": {
        "Protocol YAML Definition Guide": "v1.1.3",
        "Framework Application Analysis Template": "v1.1.5",
        "Protocol Validation Checklist": "v1.1.3",
    },
    "v1.0.30": {
        "Protocol YAML Definition Guide": "v1.1.4",
        "Framework Application Analysis Template": "v1.1.6",
        "Protocol Validation Checklist": "v1.1.4",
    },
    "v1.0.31": {
        "Protocol YAML Definition Guide": "v1.1.5",
        "Framework Application Analysis Template": "v1.1.7",
        "Protocol Validation Checklist": "v1.1.5",
    },
    "v1.0.32": {
        "Protocol YAML Definition Guide": "v1.1.6",
        "Framework Application Analysis Template": "v1.1.8",
        "Protocol Validation Checklist": "v1.1.6",
    },
}

RELEASE_STATE_REQUIRED_MARKERS = (
    "The repository content has received explicit human freeze approval for the `v1.1.2` Baseline.",
    "Repository text and detached ZIP packages do not independently establish immutable Git release identity.",
    "Immutable release identity exists only after the final commit is identified by the `v1.1.2` tag or controlled GitHub Release.",
)
RELEASE_STATE_PROHIBITED_PATTERNS = (
    r"\brepository content is frozen as\b",
    r"\brepository is frozen as\b",
    r"\bdeclared the repository content frozen as\b",
)



@dataclass(frozen=True)
class Finding:
    rule: str
    path: str
    message: str

    def format(self) -> str:
        return f"{self.rule}: {self.path}: {self.message}"


def _is_regular_file_without_link(path: Path) -> bool:
    try:
        mode = path.lstat().st_mode
    except OSError:
        return False
    return stat.S_ISREG(mode) and not stat.S_ISLNK(mode)


def _read_text(path: Path) -> str:
    # Do not follow repository-controlled links or special files. Path-safety
    # validation reports them separately; returning an empty value keeps the
    # remaining checks fail-closed without reading outside the repository.
    if not _is_regular_file_without_link(path):
        return ""
    return path.read_text(encoding="utf-8")


def _all_files(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*")
        if _is_regular_file_without_link(path) and ".git" not in path.parts
    )


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


def check_repository_path_safety(root: Path, findings: list[Finding]) -> None:
    for path in sorted(root.rglob("*")):
        if ".git" in path.parts:
            continue
        relative = _relative(root, path)
        try:
            mode = path.lstat().st_mode
        except OSError as exc:
            findings.append(Finding("REP-007", relative, f"cannot inspect repository entry without following it: {exc}"))
            continue
        if stat.S_ISLNK(mode):
            findings.append(Finding("REP-007", relative, "symbolic links are prohibited in the controlled repository tree"))
        elif not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            findings.append(Finding("REP-007", relative, "special filesystem entries are prohibited in the controlled repository tree"))


def check_required_files(root: Path, findings: list[Finding]) -> None:
    for relative in sorted(REQUIRED_FILES):
        if not _is_regular_file_without_link(root / relative):
            findings.append(Finding("REP-001", relative, "required repository file is missing or is not a regular non-link file"))


def check_text_files(root: Path, findings: list[Finding]) -> None:
    suffixes = {".md", ".yaml", ".yml", ".py", ".txt"}
    text_filenames = {"LICENSE", ".gitattributes"}
    for path in _all_files(root):
        if path.suffix.casefold() not in suffixes and path.name not in text_filenames:
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


def check_gitattributes(root: Path, findings: list[Finding]) -> None:
    path = root / ".gitattributes"
    if not _is_regular_file_without_link(path):
        return
    lines = {
        line.strip()
        for line in _read_text(path).splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    required_lines = {
        "* text=auto eol=lf",
        "*.png binary",
        "*.jpg binary",
        "*.jpeg binary",
        "*.gif binary",
        "*.zip binary",
        "*.pdf binary",
        "*.bin binary",
        "*.hex binary",
        "*.elf binary",
    }
    missing = sorted(required_lines - lines)
    if missing:
        findings.append(Finding(
            "REP-008",
            ".gitattributes",
            "canonical LF checkout policy or required binary declarations are missing: " + ", ".join(missing),
        ))


def _safe_registry_document_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        return False
    return candidate.parts[0] == "docs" and candidate.suffix == ".md" and candidate.as_posix() == value


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
        if not _safe_registry_document_path(path_value):
            findings.append(Finding(
                "REG-018", where,
                "path must be a canonical repository-relative POSIX Markdown path under docs/ with no absolute, dot, parent, or backslash segments",
            ))
            continue
        if path_value in seen_paths:
            findings.append(Finding("REG-010", path_value, "duplicate governed path"))
        seen_paths.add(path_value)
        if document.get("status") not in VALID_STATUSES:
            findings.append(Finding("REG-011", path_value, f"status must be one of {sorted(VALID_STATUSES)}"))
        if _semver_tuple(str(document.get("version", ""))) is None:
            findings.append(Finding("REG-012", path_value, "version must match vMAJOR.MINOR.PATCH or vMAJOR.MINOR.PATCH-rc.N"))
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
        safe_prereqs: list[str] = []
        for prereq in prereqs:
            if not _safe_registry_document_path(prereq):
                findings.append(Finding("REG-018", path_value, f"unsafe or non-canonical prerequisite path: {prereq!r}"))
                continue
            safe_prereqs.append(prereq)
            if prereq not in all_paths:
                findings.append(Finding("REG-016", path_value, f"unknown prerequisite: {prereq}"))
        graph[path_value] = safe_prereqs
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


def _semver_tuple(value: str) -> tuple[int, int, int, int, int] | None:
    match = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)(?:-rc\.(\d+))?", value)
    if not match:
        return None
    major, minor, patch, rc_number = match.groups()
    if rc_number is None:
        return int(major), int(minor), int(patch), 1, 0
    if int(rc_number) < 1:
        return None
    return int(major), int(minor), int(patch), 0, int(rc_number)


def _table_cells(line: str) -> list[str]:
    if not line.startswith("|") or not line.endswith("|"):
        return []
    return [cell.strip() for cell in line[1:-1].split("|")]


def _history_table(text: str) -> tuple[list[str], list[tuple[int, list[str]]]] | None:
    visible_lines = _visible_text(text).splitlines()
    history_headings = [
        (level, title, number)
        for level, title, number in _headings(text)
        if re.search(r"(?:Version History|Change History)\s*$", title, re.IGNORECASE)
    ]
    if len(history_headings) != 1:
        return None
    heading_level, _, heading_number = history_headings[0]
    header_index: int | None = None
    for index in range(heading_number, len(visible_lines)):
        heading = re.match(r"^(#{1,6})\s+", visible_lines[index])
        if heading and len(heading.group(1)) <= heading_level:
            break
        cells = _table_cells(visible_lines[index])
        if "Version" in cells and "Date" in cells and "Status" in cells and (
            "Summary" in cells or "Description" in cells
        ):
            if header_index is not None:
                return None
            header_index = index
    if header_index is None or header_index + 2 >= len(visible_lines):
        return None
    headers = _table_cells(visible_lines[header_index])
    separator = visible_lines[header_index + 1]
    if not re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", separator):
        return None
    rows: list[tuple[int, list[str]]] = []
    index = header_index + 2
    while index < len(visible_lines) and visible_lines[index].startswith("|"):
        rows.append((index + 1, _table_cells(visible_lines[index])))
        index += 1
    return headers, rows


def _valid_iso_date(value: str) -> bool:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def check_governed_documents(root: Path, registry: dict[str, Any] | None, findings: list[Finding]) -> None:
    if not registry or not isinstance(registry.get("documents"), list):
        return
    registry_by_path = {
        document["path"]: document for document in registry["documents"]
        if isinstance(document, dict) and _safe_registry_document_path(document.get("path"))
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
            if field == "Supersedes Document Version":
                continue
            values = _metadata_values(text, field)
            if len(values) != 1:
                findings.append(Finding("DOC-008", relative, f"{field} must appear exactly once in the visible opening metadata region; found {len(values)}"))
        version = _metadata(text, "Document Version")
        status = _metadata(text, "Status")
        role = _metadata(text, "Repository Role")
        if version != document.get("version"):
            findings.append(Finding("DOC-003", relative, f"Document Version {version!r} does not equal registry {document.get('version')!r}"))
        if status != document.get("status"):
            findings.append(Finding("DOC-004", relative, f"Status {status!r} does not equal registry {document.get('status')!r}"))
        if role != document.get("repository_role"):
            findings.append(Finding("DOC-005", relative, "Repository Role does not equal registry repository_role"))

        parsed = _history_table(text)
        if parsed is None:
            findings.append(Finding("DOC-006", relative, "exactly one parseable Version History or Change History table is required"))
            continue
        headers, raw_rows = parsed
        if not raw_rows:
            findings.append(Finding("DOC-006", relative, "Version History table has no data rows"))
            continue
        expected_columns = len(headers)
        required = {"Version", "Date", "Status"}
        if not required.issubset(headers) or not ({"Summary", "Description"} & set(headers)):
            findings.append(Finding("DOC-006", relative, "Version History columns must include Version, Date, Status, and Summary or Description"))
            continue
        version_index = headers.index("Version")
        date_index = headers.index("Date")
        status_index = headers.index("Status")
        summary_index = headers.index("Summary") if "Summary" in headers else headers.index("Description")

        rows: list[dict[str, Any]] = []
        malformed = False
        for line_number, cells in raw_rows:
            if len(cells) != expected_columns:
                findings.append(Finding("DOC-006", f"{relative}:{line_number}", "Version History row has the wrong column count"))
                malformed = True
                continue
            version_value = cells[version_index]
            semver = _semver_tuple(version_value)
            if semver is None:
                findings.append(Finding("DOC-009", f"{relative}:{line_number}", f"invalid history version {version_value!r}"))
                malformed = True
                continue
            if not cells[summary_index]:
                findings.append(Finding("DOC-006", f"{relative}:{line_number}", "Version History summary or description must not be empty"))
            rows.append({
                "line": line_number,
                "version": version_value,
                "semver": semver,
                "date": cells[date_index],
                "status": cells[status_index],
                "summary": cells[summary_index],
            })
        if malformed or not rows:
            continue

        versions = [row["version"] for row in rows]
        semvers = [row["semver"] for row in rows]
        duplicate_versions = sorted({value for value in versions if versions.count(value) > 1})
        if duplicate_versions:
            findings.append(Finding("DOC-009", relative, "Version History versions must be unique; duplicates: " + ", ".join(duplicate_versions)))
        descending = all(left > right for left, right in zip(semvers, semvers[1:]))
        if len(semvers) > 1 and not descending:
            findings.append(Finding("DOC-009", relative, "Version History versions must be in strict descending semantic-version order"))

        current_semver = _semver_tuple(version or "")
        current_rows = [row for row in rows if row["version"] == version]
        if len(current_rows) != 1:
            findings.append(Finding("DOC-007", relative, f"current version {version!r} must appear exactly once in Version History; found {len(current_rows)}"))
        if current_semver is not None and current_semver != max(semvers):
            findings.append(Finding("DOC-009", relative, f"metadata version {version!r} must be the highest Version History version"))
        if len(current_rows) == 1:
            current_row = current_rows[0]
            if current_row["status"] != status:
                findings.append(Finding("DOC-010", f"{relative}:{current_row['line']}", "current Version History status does not match document Status"))
            if not _valid_iso_date(current_row["date"]):
                findings.append(Finding("DOC-010", f"{relative}:{current_row['line']}", "current Version History date must be a real ISO YYYY-MM-DD date"))
            if "-rc." in current_row["version"] and status != "Draft for Review":
                findings.append(Finding("DOC-013", f"{relative}:{current_row['line']}", "release-candidate versions must remain Draft for Review"))

        recorded_by_version: list[tuple[tuple[int, int, int, int, int], date]] = []
        for row in rows:
            date_value = row["date"]
            status_value = row["status"]
            if date_value != "Not recorded":
                if not _valid_iso_date(date_value):
                    findings.append(Finding("DOC-010", f"{relative}:{row['line']}", f"invalid Version History date {date_value!r}"))
                else:
                    recorded_by_version.append((row["semver"], date.fromisoformat(date_value)))
            if status_value != "Not recorded" and status_value not in VALID_STATUSES:
                findings.append(Finding("DOC-010", f"{relative}:{row['line']}", f"invalid Version History status {status_value!r}"))
        recorded_by_version.sort(key=lambda item: item[0])
        for (_, earlier), (_, later) in zip(recorded_by_version, recorded_by_version[1:]):
            if later < earlier:
                findings.append(Finding("DOC-010", relative, "recorded Version History dates must not move backward as versions increase"))
                break

        if relative == "docs/framework/AI_Engineering_Usage_Guide.md":
            rows_by_version = {row["version"]: row for row in rows}
            for history_version, expected_routes in AI_ROUTING_HISTORY_EXPECTATIONS.items():
                row = rows_by_version.get(history_version)
                if row is None:
                    findings.append(Finding(
                        "DOC-012",
                        relative,
                        f"controlled AI routing-history row {history_version} is missing",
                    ))
                    continue
                for authority_name, expected_version in expected_routes.items():
                    matches = re.findall(
                        rf"{re.escape(authority_name)}\s+(v\d+\.\d+\.\d+)",
                        row["summary"],
                    )
                    if matches != [expected_version]:
                        actual = ", ".join(matches) if matches else "missing"
                        findings.append(Finding(
                            "DOC-012",
                            f"{relative}:{row['line']}",
                            f"controlled AI routing-history row {history_version} must reference "
                            f"exactly {authority_name} {expected_version}; found: {actual}",
                        ))

        supersedes_values = _metadata_values(text, "Supersedes Document Version")
        if len(rows) == 1:
            if supersedes_values:
                findings.append(Finding("DOC-011", relative, "an initial one-row Version History must not declare Supersedes Document Version"))
        else:
            if len(supersedes_values) != 1:
                findings.append(Finding("DOC-011", relative, f"Supersedes Document Version must appear exactly once; found {len(supersedes_values)}"))
            elif current_semver is not None:
                lower_rows = [row for row in rows if row["semver"] < current_semver]
                expected_supersedes = max(lower_rows, key=lambda row: row["semver"])["version"] if lower_rows else None
                actual_supersedes = supersedes_values[0]
                actual_semver = _semver_tuple(actual_supersedes)
                if actual_semver is None:
                    findings.append(Finding("DOC-011", relative, "Supersedes Document Version must match vMAJOR.MINOR.PATCH or vMAJOR.MINOR.PATCH-rc.N"))
                elif actual_supersedes not in versions:
                    findings.append(Finding("DOC-011", relative, "Supersedes Document Version must exist in Version History"))
                elif actual_semver >= current_semver:
                    findings.append(Finding("DOC-011", relative, "Supersedes Document Version must be lower than the current version"))
                elif actual_supersedes != expected_supersedes:
                    findings.append(Finding("DOC-011", relative, f"Supersedes Document Version must identify immediate prior listed version {expected_supersedes}"))

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
        if not isinstance(document, dict) or not _safe_registry_document_path(document.get("path")):
            continue
        path = PurePosixPath(document["path"])
        index = root / Path(*path.parts[:-1]) / "README.md"
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


def _section_by_heading(text: str, heading: str, next_heading_level: int | None = None) -> str | None:
    """Return one visible Markdown section beginning at an exact heading."""
    matches = list(re.finditer(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE))
    if len(matches) != 1:
        return None
    match = matches[0]
    if next_heading_level is None:
        level = len(heading) - len(heading.lstrip("#"))
    else:
        level = next_heading_level
    following = re.search(rf"^#{{1,{level}}}\s+", text[match.end():], re.MULTILINE)
    end = match.end() + following.start() if following else len(text)
    return text[match.start():end]


def check_protocol_conformance_tester_governance(root: Path, findings: list[Finding]) -> None:
    guide = root / "docs/protocol/Protocol_YAML_Definition_Guide.md"
    template = root / "docs/framework/Framework_Application_Analysis_Template.md"
    checklist = root / "docs/validation/Protocol_Validation_Checklist.md"
    guide_text = _visible_text(_read_text(guide)) if guide.is_file() else ""
    template_text = _visible_text(_read_text(template)) if template.is_file() else ""
    checklist_text = _visible_text(_read_text(checklist)) if checklist.is_file() else ""

    tester_section = _section_by_heading(guide_text, "### 24.6 Independent Protocol Conformance Tester")
    baseline_section = _section_by_heading(guide_text, "### 25.3 Staged Baseline Contents")
    gate_section = _section_by_heading(guide_text, "### 25.6 Staged Baseline Gates")
    if tester_section is None:
        findings.append(Finding("PCT-001", _relative(root, guide), "the unique 24.6 Protocol Conformance Tester section is missing"))
        tester_section = ""
    if baseline_section is None:
        findings.append(Finding("PCT-001", _relative(root, guide), "the unique 25.3 staged-baseline section is missing"))
        baseline_section = ""
    if gate_section is None:
        findings.append(Finding("PCT-001", _relative(root, guide), "the unique 25.6 staged-baseline gate section is missing"))
        gate_section = ""

    tester_markers = [
        "independently executable Protocol Conformance Tester",
        "shall not become a competing Protocol authority",
        "may be implemented in Python",
        "shall not replace formal Coordinator/Node interoperability",
        "authorized N/A approval record",
        "shall not call, import, or reuse the production Coordinator or Node command handlers",
        "Bind each result to the exact tested candidate",
        "Bound representative-target claims to the demonstrated equivalence",
        "The self-validation shall use controlled positive cases and known-negative controls",
        "A self-test that only proves the script starts, imports, or replays its own generated expectations is insufficient",
    ]
    for marker in tester_markers:
        if marker not in tester_section:
            findings.append(Finding("PCT-001", _relative(root, guide), f"24.6 is missing required authority text: {marker}"))

    baseline_markers = [
        "exactly one Protocol baseline stage",
        "A **Protocol Definition Baseline** shall include",
        "A **Protocol Integration Baseline** shall additionally include",
        "A **Protocol Release Baseline** shall additionally include",
        "Independent Protocol Conformance Tester source identity",
        "review trigger, expiry, or continuing-validity condition",
        "shall not be carried into Integration or Release without recorded re-confirmation",
        "Exact tested-candidate identity set",
        "Integration-to-Release evidence reconciliation",
        "shall not inherit Integration evidence",
        "stage, applicability, physical-execution state, and formal-gate disposition",
        "shall not use `N/A` for the gate while claiming the Tester is `Required`",
    ]
    for marker in baseline_markers:
        if marker not in baseline_section:
            findings.append(Finding("PCT-001", _relative(root, guide), f"25.3 is missing required staged-baseline text: {marker}"))

    gate_markers = [
        "Protocol Definition Baseline approval does not require executed Tester evidence",
        "Before **Protocol Integration Baseline** approval",
        "Before **Protocol Release Baseline** approval",
        "Tester self-validation shall pass",
        "formal integration gate shall be approved",
        "exact tested-candidate identity set",
        "Representative-target use shall record the equivalence boundary",
        "Integration evidence shall be reconciled against the exact Release candidate identities",
    ]
    for marker in gate_markers:
        if marker not in gate_section:
            findings.append(Finding("PCT-001", _relative(root, guide), f"25.6 is missing required staged-gate text: {marker}"))

    guide_global_markers = [
        "Protocol Conformance Tester Owner",
        "Protocol Conformance Tester impact",
    ]
    for marker in guide_global_markers:
        if marker not in guide_text:
            findings.append(Finding("PCT-001", _relative(root, guide), f"required conformance-tester governance marker is missing: {marker}"))

    template_section = _section_by_heading(template_text, "## 15.2 Independent Protocol Conformance Tester Decision")
    if template_section is None:
        findings.append(Finding("PCT-002", _relative(root, template), "the unique 15.2 Protocol Conformance Tester decision section is missing"))
        template_section = ""

    template_markers = [
        "N/A Approval Reference",
        "Tester Independence Boundary",
        "Project Protocol Source Identity",
        "Golden Test Vector Identity",
        "Physical Node Execution",
        "Formal Integration Gate",
        "Exactly one baseline stage shall be selected",
        "review trigger, expiry, or continuing-validity condition",
        "Tested Candidate Identity",
        "Integration-to-Release Evidence Reconciliation",
        "Representative Target Residual Boundary",
        "Tester Self-Validation Identity",
        "cross-field disposition matrix",
        "`N/A` for the Formal Integration Gate is not a substitute for a missing PASS",
    ]
    for marker in template_markers:
        if marker not in template_section:
            findings.append(Finding("PCT-002", _relative(root, template), f"15.2 is missing required application-analysis text: {marker}"))

    applicability_pattern = r"^\|\s*Independent Protocol Tester Applicability\s*\|\s*([^|]+?)\s*\|\s*$"
    applicability_rows = re.findall(applicability_pattern, template_text, re.MULTILINE)
    section_applicability_rows = re.findall(applicability_pattern, template_section, re.MULTILINE)
    if len(applicability_rows) != 1 or section_applicability_rows != ["`Required / N/A`"]:
        findings.append(Finding(
            "PCT-004", _relative(root, template),
            "15.2 must contain the repository's only Protocol Tester applicability row and its value must be exactly `Required / N/A`",
        ))

    stage_pattern = r"^\|\s*Protocol Baseline Stage\s*\|\s*([^|]+?)\s*\|\s*$"
    stage_rows = re.findall(stage_pattern, template_text, re.MULTILINE)
    section_stage_rows = re.findall(stage_pattern, template_section, re.MULTILINE)
    expected_stage = "`<Exactly one: Definition, Integration, or Release>`"
    if len(stage_rows) != 1 or section_stage_rows != [expected_stage]:
        findings.append(Finding(
            "PCT-005", _relative(root, template),
            f"15.2 must contain the repository's only Protocol Baseline Stage row and its value must be exactly {expected_stage}",
        ))

    for marker in (
        "Independent Protocol Conformance Tester | Yes when applicable",
        "Protocol Conformance Tester self-validation report",
        "protocol_conformance_tester/",
        "| Owner |",
        "| Reviewer |",
    ):
        if marker not in template_text:
            findings.append(Finding("PCT-002", _relative(root, template), f"required application-analysis artifact marker is missing: {marker}"))

    interoperability_section = _section_by_heading(checklist_text, "# 12. Coordinator/Node Interoperability")
    evidence_section = _section_by_heading(checklist_text, "# 13. Evidence and Approval")
    if interoperability_section is None:
        findings.append(Finding("PCT-003", _relative(root, checklist), "the unique interoperability checklist section is missing"))
        interoperability_section = ""
    if evidence_section is None:
        findings.append(Finding("PCT-003", _relative(root, checklist), "the unique evidence checklist section is missing"))
        evidence_section = ""

    checklist_requirements = {
        "P-106": (interoperability_section, ("**Definition:**", "**Integration/Release:**")),
        "P-107": (interoperability_section, ("**Definition:**", "**Integration/Release:**")),
        "P-108": (interoperability_section, ("**Definition:**", "**Integration/Release:**")),
        "P-109": (interoperability_section, ("**Integration/Release only:**", "N/A — Definition stage")),
        "P-115": (evidence_section, ("**Integration/Release only:**", "N/A — Definition stage")),
        "P-116": (evidence_section, ("review trigger, expiry, or continuing-validity condition", "re-confirmed")),
        "P-117": (evidence_section, ("Exactly one", "no combined, unspecified, or deferred stage")),
        "P-118": (evidence_section, ("Definition Baseline", "without claiming unexecuted target evidence")),
        "P-119": (evidence_section, ("Integration or Release Baseline", "formal integration-gate disposition")),
        "P-120": (evidence_section, ("exact Protocol", "Golden Vectors", "Node build", "Transport")),
        "P-121": (evidence_section, ("exact Release candidate", "affected re-execution", "stale evidence is not inherited")),
        "P-122": (evidence_section, ("documented equivalence", "actual Product target", "release limitation")),
        "P-123": (evidence_section, ("permitted combination", "Required Tester", "does not support approval")),
        "P-124": (evidence_section, ("controlled self-validation", "known-negative", "raw result", "evidence identity")),
    }
    for check_id, (section, markers) in checklist_requirements.items():
        matches = re.findall(rf"^\s*- \[ \] {re.escape(check_id)}\b.*$", section, re.MULTILINE)
        if len(matches) != 1:
            findings.append(Finding("PCT-003", _relative(root, checklist), f"required Protocol tester check must occur exactly once in its controlled section: {check_id}"))
            continue
        for marker in markers:
            if marker not in matches[0]:
                findings.append(Finding("PCT-006", _relative(root, checklist), f"{check_id} is missing stage-scoped evidence text: {marker}"))

    freshness_markers = (
        "exact tested-candidate identity set",
        "Integration-to-Release evidence reconciliation",
        "shall not inherit Integration evidence",
    )
    if any(marker not in baseline_section + gate_section for marker in freshness_markers):
        findings.append(Finding("PCT-007", _relative(root, guide), "exact candidate identity binding or Release evidence reconciliation is incomplete"))
    if any(marker not in template_section for marker in (
        "Tested Candidate Identity", "Integration-to-Release Evidence Reconciliation"
    )):
        findings.append(Finding("PCT-007", _relative(root, template), "the Tester decision does not retain exact candidate identity and Release reconciliation"))

    representative_markers = (
        "Representative Target Residual Boundary",
        "demonstrated equivalence",
        "actual Product target",
        "release limitation",
    )
    combined = tester_section + baseline_section + gate_section + template_section + evidence_section
    if any(marker not in combined for marker in representative_markers):
        findings.append(Finding("PCT-008", _relative(root, guide), "representative-target evidence boundaries or residual actual-target disposition are incomplete"))

    disposition_markers = (
        "stage, applicability, physical-execution state, and formal-gate disposition",
        "A `Failed`, `Inconclusive`, `Blocked`, `Not Run`, `Pending`, stale `N/A`, or contradictory combination shall not support Integration or Release approval",
        "`N/A` for the Formal Integration Gate is not a substitute for a missing PASS",
    )
    if any(marker not in baseline_section + template_section for marker in disposition_markers):
        findings.append(Finding("PCT-009", _relative(root, template), "stage, applicability, execution, and gate dispositions are not fail-closed and internally consistent"))

    self_validation_markers = (
        "Tester Self-Validation Identity",
        "controlled positive cases and known-negative controls",
        "A self-test that only proves the script starts, imports, or replays its own generated expectations is insufficient",
        "Protocol Conformance Tester self-validation report",
    )
    self_validation_combined = tester_section + baseline_section + gate_section + template_section + evidence_section + template_text
    if any(marker not in self_validation_combined for marker in self_validation_markers):
        findings.append(Finding("PCT-010", _relative(root, guide), "Tester self-validation authority, evidence identity, or known-negative controls are incomplete"))

def _expected_changelog_snapshot(registry: dict[str, Any]) -> list[str]:
    rows = ["| Document | Version | Status |", "|---|---:|---|"]
    for document in registry["documents"]:
        rows.append(
            f"| {document['display_name']} | {document['version']} | {document['status']} |"
        )
    return rows


def check_release_state_claims(root: Path, findings: list[Finding]) -> None:
    readme_path = root / "README.md"
    if not _is_regular_file_without_link(readme_path):
        return
    readme_text = _visible_text(_read_text(readme_path))
    status_section = _section_by_heading(readme_text, "## Current Status")
    if status_section is None:
        findings.append(Finding("STATUS-001", "README.md", "a unique ## Current Status section is required"))
        status_section = ""
    for marker in RELEASE_STATE_REQUIRED_MARKERS:
        if marker not in status_section:
            findings.append(Finding(
                "STATUS-001",
                "README.md",
                f"Current Status release-state boundary is missing or altered: {marker}",
            ))
    for pattern in RELEASE_STATE_PROHIBITED_PATTERNS:
        if re.search(pattern, status_section, re.IGNORECASE):
            findings.append(Finding(
                "STATUS-001",
                "README.md",
                "mutable repository text shall not self-assert that the release is already frozen",
            ))
            break

    changelog_path = root / "CHANGELOG.md"
    if _is_regular_file_without_link(changelog_path):
        unreleased = _unreleased_section(_visible_text(_read_text(changelog_path))) or ""
        for pattern in RELEASE_STATE_PROHIBITED_PATTERNS:
            if re.search(pattern, unreleased, re.IGNORECASE):
                findings.append(Finding(
                    "STATUS-002",
                    "CHANGELOG.md",
                    "Unreleased changes contain an active or unqualified mutable-content freeze assertion",
                ))
                break


def _unreleased_section(text: str) -> str | None:
    match = re.search(r"^##\s+Unreleased\s*$", text, re.MULTILINE)
    if not match:
        return None
    following = re.search(r"^##\s+", text[match.end():], re.MULTILINE)
    end = match.end() + following.start() if following else len(text)
    return text[match.start():end]


def check_changelog(root: Path, registry: dict[str, Any] | None, findings: list[Finding]) -> None:
    path = root / "CHANGELOG.md"
    section = _unreleased_section(_visible_text(_read_text(path))) if path.is_file() else None
    if section is None:
        findings.append(Finding("CHANGE-001", "CHANGELOG.md", "an unambiguous ## Unreleased section is required"))
        return
    if registry and isinstance(registry.get("documents"), list):
        snapshot = _extract_table(section, "| Document | Version | Status |")
        if snapshot != _expected_changelog_snapshot(registry):
            findings.append(Finding(
                "CHANGE-002",
                "CHANGELOG.md",
                "Current Authority Revision Snapshot does not exactly match authority-registry.yaml",
            ))
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
    check_repository_path_safety(root, findings)
    check_required_files(root, findings)
    check_text_files(root, findings)
    check_gitattributes(root, findings)
    registry = load_registry(root, findings)
    check_governed_documents(root, registry, findings)
    check_registry_views(root, registry, findings)
    check_release_state_claims(root, findings)
    check_markdown_structure(root, findings)
    check_links(root, findings)
    check_filename_policy(root, findings)
    check_notice_and_checklists(root, findings)
    check_legal_and_conformance_boundaries(root, findings)
    check_workflow(root, findings)
    check_protocol_assets(root, findings)
    check_protocol_conformance_tester_governance(root, findings)
    check_changelog(root, registry, findings)
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
        "PASS: repository documentation, LF checkout policy, authority registry, Version History chains, Protocol schema, "
        "semantic fixtures, independent Protocol tester applicability, lifecycle, evidence, and CI controls are consistent."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
