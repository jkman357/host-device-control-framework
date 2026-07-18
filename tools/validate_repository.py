#!/usr/bin/env python3
"""Deterministic structural validation for the documentation repository.

Runtime requirement: Python 3.10 or later.
CI validation runtime: Python 3.12.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

MIN_PYTHON = (3, 10)
CI_PYTHON = "3.12"
ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []

if sys.version_info < MIN_PYTHON:
    required = ".".join(str(part) for part in MIN_PYTHON)
    actual = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"Repository validation: FAIL\n- Python {required} or later is required; found {actual}")
    sys.exit(2)


def error(message: str) -> None:
    ERRORS.append(message)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_text(path: Path) -> str:
    try:
        data = path.read_bytes()
        text = data.decode("utf-8")
    except Exception as exc:
        error(f"{rel(path)}: UTF-8 read failed: {exc}")
        return ""
    if text and not text.endswith("\n"):
        error(f"{rel(path)}: missing final newline")
    return text


def metadata(text: str, key: str) -> str | None:
    match = re.search(rf"^\*\*{re.escape(key)}:\*\*\s*`?([^`\n]+?)`?\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def fence_free_text(path: Path, text: str) -> str:
    """Validate fenced blocks and return text with fenced content blanked."""
    output: list[str] = []
    opening: tuple[str, int, int] | None = None
    fence_re = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")

    for line_no, line in enumerate(text.splitlines(), start=1):
        match = fence_re.match(line)
        if opening is None:
            if match:
                marker = match.group(1)
                opening = (marker[0], len(marker), line_no)
                output.append("")
            else:
                output.append(line)
            continue

        marker_char, marker_length, _ = opening
        if match:
            marker = match.group(1)
            trailing = match.group(2)
            if marker[0] == marker_char and len(marker) >= marker_length and not trailing.strip():
                opening = None
        output.append("")

    if opening is not None:
        marker_char, marker_length, opening_line = opening
        error(
            f"{rel(path)}:{opening_line}: unclosed fenced Code block "
            f"opened with {marker_char * marker_length}"
        )
    return "\n".join(output) + ("\n" if text.endswith("\n") else "")


def remove_inline_code(text: str) -> str:
    """Blank inline-code spans so examples are not interpreted as links or headings."""
    return re.sub(r"(`+)(.+?)\1", lambda match: " " * len(match.group(0)), text)


def github_slug(raw_heading: str) -> str:
    text = re.sub(r"<[^>]+>", "", raw_heading)
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[`*_~]", "", text)
    text = unicodedata.normalize("NFKC", text).strip().lower()
    chars: list[str] = []
    for char in text:
        category = unicodedata.category(char)
        if char in ("-", "_", " ") or category[0] in ("L", "N"):
            chars.append(char)
    return "".join(chars).replace(" ", "-")


def heading_anchors(text: str) -> set[str]:
    anchors: set[str] = set()
    duplicates: dict[str, int] = {}
    for line in text.splitlines():
        match = re.match(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        base = github_slug(match.group(2))
        if not base:
            continue
        count = duplicates.get(base, 0)
        anchor = base if count == 0 else f"{base}-{count}"
        duplicates[base] = count + 1
        anchors.add(anchor)
    for match in re.finditer(r"\b(?:id|name)=[\"']([^\"']+)[\"']", text, re.IGNORECASE):
        anchors.add(match.group(1))
    return anchors


def split_link_target(raw_target: str) -> str:
    raw_target = raw_target.strip()
    if raw_target.startswith("<") and ">" in raw_target:
        return raw_target[1 : raw_target.index(">")]
    return raw_target.split(maxsplit=1)[0]


def validate_target(source: Path, raw_target: str, anchors_by_path: dict[Path, set[str]]) -> None:
    target = split_link_target(raw_target)
    if not target:
        return
    parsed = urlsplit(target)
    if parsed.scheme or target.startswith("//"):
        return

    path_part = unquote(parsed.path)
    fragment = unquote(parsed.fragment)
    resolved = source if not path_part else (source.parent / path_part).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        error(f"{rel(source)}: link escapes repository: {target}")
        return

    if not resolved.exists():
        error(f"{rel(source)}: missing link or image target: {path_part or target}")
        return

    if fragment and resolved.is_file() and resolved.suffix.lower() == ".md":
        available = anchors_by_path.get(resolved, set())
        if fragment not in available:
            error(f"{rel(source)}: missing heading anchor in {rel(resolved)}: #{fragment}")


def check_links(path: Path, text: str, anchors_by_path: dict[Path, set[str]]) -> None:
    searchable = remove_inline_code(text)
    definitions: dict[str, str] = {}
    for match in re.finditer(
        r"^ {0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+))",
        searchable,
        re.MULTILINE,
    ):
        label = re.sub(r"\s+", " ", match.group(1).strip()).casefold()
        target = match.group(2) or match.group(3) or ""
        if label in definitions:
            error(f"{rel(path)}: duplicate reference-link definition: [{match.group(1)}]")
        definitions[label] = target
        validate_target(path, target, anchors_by_path)

    for match in re.finditer(r"!?\[[^\]]*\]\(([^)]+)\)", searchable):
        validate_target(path, match.group(1), anchors_by_path)

    for match in re.finditer(r"!?\[([^\]]+)\]\[([^\]]*)\]", searchable):
        label = match.group(2).strip() or match.group(1).strip()
        normalized = re.sub(r"\s+", " ", label).casefold()
        if normalized not in definitions:
            error(f"{rel(path)}: undefined reference-style link: [{label}]")


def parse_markdown_table(text: str, heading: str) -> list[list[str]]:
    heading_match = re.search(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE)
    if not heading_match:
        return []
    section = text[heading_match.end() :]
    next_heading = re.search(r"^#{1,6}\s+", section, re.MULTILINE)
    if next_heading:
        section = section[: next_heading.start()]

    lines = section.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        if index + 1 >= len(lines) or not lines[index + 1].startswith("|"):
            continue
        separator = [cell.strip() for cell in lines[index + 1].strip().strip("|").split("|")]
        if not separator or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator):
            continue
        rows: list[list[str]] = []
        for row_line in lines[index + 2 :]:
            if not row_line.startswith("|"):
                break
            rows.append([cell.strip() for cell in row_line.strip().strip("|").split("|")])
        return rows
    return []


def normalize_cell(cell: str) -> str:
    cell = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cell)
    return cell.replace("`", "").strip()


def parse_version_history(path: Path, text: str, version: str, status: str) -> None:
    heading_re = re.compile(
        r"^(#{1,6})\s+.*(?:Version|Change)\s+History\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    heading = heading_re.search(text)
    if not heading:
        error(f"{rel(path)}: Version History or Change History heading not found")
        return

    level = len(heading.group(1))
    section = text[heading.end() :]
    next_heading = re.search(rf"^#{{1,{level}}}\s+", section, re.MULTILINE)
    if next_heading:
        section = section[: next_heading.start()]

    lines = section.splitlines()
    header: list[str] | None = None
    rows: list[list[str]] = []
    for index, line in enumerate(lines):
        if not line.startswith("|") or index + 1 >= len(lines):
            continue
        separator_line = lines[index + 1]
        if not separator_line.startswith("|"):
            continue
        candidate_header = [normalize_cell(cell) for cell in line.strip().strip("|").split("|")]
        separator = [cell.strip() for cell in separator_line.strip().strip("|").split("|")]
        if separator and all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator):
            header = candidate_header
            for row_line in lines[index + 2 :]:
                if not row_line.startswith("|"):
                    break
                rows.append([normalize_cell(cell) for cell in row_line.strip().strip("|").split("|")])
            break

    if not header or not rows:
        error(f"{rel(path)}: Version History table not found under its heading")
        return
    if not header[0].casefold().startswith("version"):
        error(f"{rel(path)}: Version History first column must be Version")
        return

    matching = [row for row in rows if row and row[0] == version]
    if len(matching) != 1:
        error(f"{rel(path)}: current version {version} must appear exactly once in Version History table")
        return

    normalized_header = [item.casefold() for item in header]
    if "status" in normalized_header:
        status_index = normalized_header.index("status")
        history_status = matching[0][status_index] if status_index < len(matching[0]) else ""
        if history_status != status:
            error(
                f"{rel(path)}: Version History status for {version} is {history_status!r}; "
                f"metadata status is {status!r}"
            )
    if "date" in normalized_header:
        date_index = normalized_header.index("date")
        history_date = matching[0][date_index] if date_index < len(matching[0]) else ""
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", history_date):
            error(f"{rel(path)}: Version History date for {version} must use YYYY-MM-DD")


def check_workflow() -> None:
    workflow = ROOT / ".github/workflows/document-validation.yml"
    if not workflow.exists():
        return
    text = read_text(workflow)
    if "actions/checkout@v4" not in text:
        error(f"{rel(workflow)}: actions/checkout@v4 is required")
    if "actions/setup-python@v5" not in text:
        error(f"{rel(workflow)}: actions/setup-python@v5 is required")
    if not re.search(rf"python-version:\s*[\"']?{re.escape(CI_PYTHON)}[\"']?", text):
        error(f"{rel(workflow)}: CI Python version must be {CI_PYTHON}")
    if "python tools/validate_repository.py" not in text:
        error(f"{rel(workflow)}: validator invocation is missing")


md_files = sorted(ROOT.rglob("*.md"))
contents: dict[Path, str] = {}
searchable_contents: dict[Path, str] = {}
anchors_by_path: dict[Path, set[str]] = {}
canonical: dict[str, Path] = {}
documents: dict[str, tuple[Path, str, str]] = {}

for path in md_files:
    text = read_text(path)
    contents[path] = text
    searchable = fence_free_text(path, text)
    searchable_contents[path] = searchable
    anchors_by_path[path.resolve()] = heading_anchors(remove_inline_code(searchable))

for path in md_files:
    text = contents[path]
    searchable = searchable_contents[path]
    check_links(path, searchable, anchors_by_path)
    name = metadata(text, "Canonical Filename") or metadata(text, "Document Name")
    version = metadata(text, "Document Version")
    status = metadata(text, "Status")
    role = metadata(text, "Repository Role")
    if name:
        if name in canonical:
            error(f"duplicate canonical filename {name}: {rel(canonical[name])} and {rel(path)}")
        canonical[name] = path
    if version or status:
        if not (version and status and name):
            error(f"{rel(path)}: incomplete document metadata")
        else:
            documents[name] = (path, version, status)
            parse_version_history(path, text, version, status)
            if status == "Draft for Review" and role and "normative" in role.lower() and "proposed" not in role.lower():
                error(f"{rel(path)}: Draft normative role must say Proposed")

required = [
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "NOTICE.md",
    "docs/framework/AI_Engineering_Usage_Guide.md",
    "docs/framework/Coordinator_Node_Control_Framework.md",
    "docs/framework/Framework_Application_Analysis_Template.md",
    "docs/protocol/Protocol_YAML_Definition_Guide.md",
    "docs/protocol/Protocol_YAML_Template.md",
    "docs/coordinator/Coordinator_Software_Engineering_Rules.md",
    "docs/coding-rules/Embedded_C_Coding_Rules.md",
    "docs/coding-rules/CSharp_Coding_Rules.md",
    "docs/validation/Repository_Validation_Checklist.md",
    "tools/validate_repository.py",
    ".github/workflows/document-validation.yml",
]
for required_path in required:
    if not (ROOT / required_path).exists():
        error(f"missing required path: {required_path}")

# Root Current Document Set consistency and completeness.
readme = contents.get(ROOT / "README.md", "")
readme_rows = parse_markdown_table(readme, "## Current Document Set")
if not readme_rows:
    error("README.md: Current Document Set table is missing or empty")
readme_names: list[str] = []
for row in readme_rows:
    if len(row) < 3:
        error("README.md: malformed Current Document Set row")
        continue
    name, version, status = map(normalize_cell, row[:3])
    readme_names.append(name)
    if name not in documents:
        error(f"README Current Document Set references unknown document: {name}")
        continue
    _, actual_version, actual_status = documents[name]
    if version != actual_version or status != actual_status:
        error(f"README mismatch for {name}: listed {version}/{status}, actual {actual_version}/{actual_status}")
if len(readme_names) != len(set(readme_names)):
    error("README.md: Current Document Set contains duplicate document rows")
missing_from_readme = set(documents) - set(readme_names)
extra_in_readme = set(readme_names) - set(documents)
if missing_from_readme:
    error(f"README Current Document Set omits: {', '.join(sorted(missing_from_readme))}")
if extra_in_readme:
    error(f"README Current Document Set has non-authority entries: {', '.join(sorted(extra_in_readme))}")

# AI Active Document Manifest consistency and completeness.
guide_path = ROOT / "docs/framework/AI_Engineering_Usage_Guide.md"
guide = contents.get(guide_path, "")
manifest_rows = parse_markdown_table(guide, "## 0.2 Active Document Manifest")
if not manifest_rows:
    error(f"{rel(guide_path)}: Active Document Manifest table is missing or empty")
manifest_names: list[str] = []
for row in manifest_rows:
    if len(row) < 4:
        error(f"{rel(guide_path)}: malformed Active Document Manifest row")
        continue
    _, path_cell, version, status = map(normalize_cell, row[:4])
    canonical_name = Path(path_cell).name
    manifest_names.append(canonical_name)
    if canonical_name not in documents:
        error(f"AI manifest references unknown document: {path_cell}")
        continue
    actual_path, actual_version, actual_status = documents[canonical_name]
    if rel(actual_path) != path_cell:
        error(f"AI manifest path mismatch for {canonical_name}: {path_cell}")
    if version != actual_version or status != actual_status:
        error(f"AI manifest mismatch for {canonical_name}: listed {version}/{status}, actual {actual_version}/{actual_status}")
if len(manifest_names) != len(set(manifest_names)):
    error(f"{rel(guide_path)}: Active Document Manifest contains duplicate document rows")
missing_from_manifest = set(documents) - set(manifest_names)
extra_in_manifest = set(manifest_names) - set(documents)
if missing_from_manifest:
    error(f"AI Active Document Manifest omits: {', '.join(sorted(missing_from_manifest))}")
if extra_in_manifest:
    error(f"AI Active Document Manifest has non-authority entries: {', '.join(sorted(extra_in_manifest))}")

check_workflow()

if ERRORS:
    print("Repository validation: FAIL")
    for item in ERRORS:
        print(f"- {item}")
    sys.exit(1)

print(f"Repository validation: PASS ({len(md_files)} Markdown files checked, Python {sys.version_info.major}.{sys.version_info.minor})")
