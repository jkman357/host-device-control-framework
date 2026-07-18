#!/usr/bin/env python3
"""Deterministic structural validation for the documentation repository.

Runtime requirement: Python 3.10 or later.
Validation dependency: PyYAML 6.0.3.
CI validation runtimes: Python 3.10 and Python 3.12.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    print(
        "Repository validation: FAIL\n"
        "- PyYAML 6.0.3 is required; run "
        "'python -m pip install -r requirements-validation.txt'"
    )
    sys.exit(2)

MIN_PYTHON = (3, 10)
ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []

CHECKOUT_ACTION = "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"
SETUP_PYTHON_ACTION = "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1"
VALIDATION_REQUIREMENT = "PyYAML==6.0.3"
DIRECTORY_INDEX_ALLOWLIST = {
    "docs/framework/README.md",
    "docs/protocol/README.md",
    "docs/coordinator/README.md",
    "docs/coding-rules/README.md",
    "docs/validation/README.md",
}
DIRECTORY_INDEX_ROLE = "Non-normative directory index"
METADATA_KEYS = (
    "Canonical Filename",
    "Document Name",
    "Document Version",
    "Status",
    "Supersedes Document Version",
    "Repository Role",
)

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


def parse_metadata(path: Path, searchable: str) -> dict[str, str]:
    """Parse unique metadata from the opening document region only."""
    lines = searchable.splitlines()
    patterns = {
        key: re.compile(rf"^\*\*{re.escape(key)}:\*\*\s*`?([^`\n]+?)`?\s*$", re.MULTILINE)
        for key in METADATA_KEYS
    }
    matches_by_key = {key: list(pattern.finditer(searchable)) for key, pattern in patterns.items()}
    first_metadata_line = min(
        (searchable.count("\n", 0, match.start()) for matches in matches_by_key.values() for match in matches),
        default=0,
    )
    first_h2_after_metadata = next(
        (
            index
            for index, line in enumerate(lines)
            if index > first_metadata_line and re.match(r"^ {0,3}##\s+", line)
        ),
        len(lines),
    )
    opening_limit = min(first_h2_after_metadata, 80)
    values: dict[str, str] = {}

    for key in METADATA_KEYS:
        matches = matches_by_key[key]
        if len(matches) > 1:
            error(f"{rel(path)}: metadata key {key!r} must appear exactly once")
            continue
        if not matches:
            continue
        match = matches[0]
        line_index = searchable.count("\n", 0, match.start())
        if line_index >= opening_limit:
            error(
                f"{rel(path)}:{line_index + 1}: metadata key {key!r} must appear "
                "within the opening metadata region before the next level-2 heading and line 80"
            )
            continue
        values[key] = match.group(1).strip()
    return values


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
    headings: list[tuple[int, str]] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        atx = re.match(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if atx:
            headings.append((index, atx.group(2)))
        if index + 1 < len(lines) and line.strip():
            setext = re.match(r"^ {0,3}(=+|-+)\s*$", lines[index + 1])
            if setext and "|" not in line:
                headings.append((index, line.strip()))

    anchors: set[str] = set()
    duplicates: dict[str, int] = {}
    for _, raw in sorted(headings):
        base = github_slug(raw)
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

    if fragment and resolved.is_file() and resolved.suffix == ".md":
        available = anchors_by_path.get(resolved, set())
        if fragment not in available:
            error(f"{rel(source)}: missing heading anchor in {rel(resolved)}: #{fragment}")


def inline_link_targets(text: str) -> list[str]:
    """Extract inline Markdown link/image targets with balanced parentheses."""
    targets: list[str] = []
    index = 0
    while True:
        marker = text.find("](", index)
        if marker < 0:
            break
        cursor = marker + 2
        if cursor < len(text) and text[cursor] == "<":
            end = cursor + 1
            escaped = False
            while end < len(text):
                char = text[end]
                if char == ">" and not escaped:
                    targets.append(text[cursor : end + 1])
                    cursor = end + 1
                    break
                escaped = char == "\\" and not escaped
                if char != "\\":
                    escaped = False
                end += 1
            index = max(cursor, marker + 2)
            continue

        depth = 1
        end = cursor
        escaped = False
        while end < len(text):
            char = text[end]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    targets.append(text[cursor:end])
                    end += 1
                    break
            end += 1
        index = max(end, marker + 2)
    return targets


class LocalTargetHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attribute = "href" if tag.casefold() == "a" else "src" if tag.casefold() == "img" else None
        if attribute is None:
            return
        for key, value in attrs:
            if key.casefold() == attribute and value:
                self.targets.append(value)


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

    for target in inline_link_targets(searchable):
        validate_target(path, target, anchors_by_path)

    for match in re.finditer(r"!?\[([^\]]+)\]\[([^\]]*)\]", searchable):
        label = match.group(2).strip() or match.group(1).strip()
        normalized = re.sub(r"\s+", " ", label).casefold()
        if normalized not in definitions:
            error(f"{rel(path)}: undefined reference-style link: [{label}]")

    html_parser = LocalTargetHTMLParser()
    try:
        html_parser.feed(searchable)
    except Exception as exc:
        error(f"{rel(path)}: HTML link parsing failed: {exc}")
    for target in html_parser.targets:
        validate_target(path, target, anchors_by_path)


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


SEMVER_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def parse_semver(value: str) -> tuple[int, int, int] | None:
    match = SEMVER_RE.fullmatch(value)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def parse_version_history(
    path: Path,
    text: str,
    version: str,
    status: str,
    supersedes: str | None,
) -> None:
    heading_re = re.compile(
        r"^(#{1,6})\s+.*(?:Version|Change)\s+History\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    headings = list(heading_re.finditer(text))
    if len(headings) != 1:
        error(
            f"{rel(path)}: exactly one Version History or Change History heading is required; "
            f"found {len(headings)}"
        )
        return
    heading = headings[0]

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

    current_semver = parse_semver(version)
    if current_semver is None:
        error(f"{rel(path)}: Document Version {version!r} must match vMAJOR.MINOR.PATCH")

    history_values: list[str] = []
    history_semvers: list[tuple[int, int, int]] = []
    for row in rows:
        if not row:
            continue
        row_version = row[0]
        parsed = parse_semver(row_version)
        if parsed is None:
            error(f"{rel(path)}: Version History value {row_version!r} must match vMAJOR.MINOR.PATCH")
            continue
        history_values.append(row_version)
        history_semvers.append(parsed)

    if len(history_values) != len(set(history_values)):
        error(f"{rel(path)}: Version History contains duplicate versions")

    if len(history_semvers) > 1:
        ascending = history_semvers == sorted(history_semvers)
        descending = history_semvers == sorted(history_semvers, reverse=True)
        if not (ascending or descending):
            error(f"{rel(path)}: Version History versions must be monotonic")

    matching = [row for row in rows if row and row[0] == version]
    if len(matching) != 1:
        error(f"{rel(path)}: current version {version} must appear exactly once in Version History table")
    elif current_semver is not None and history_semvers and current_semver != max(history_semvers):
        highest = "v" + ".".join(str(part) for part in max(history_semvers))
        error(f"{rel(path)}: current version {version} must be the highest Version History version ({highest})")

    if matching:
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

    if len(history_values) <= 1:
        if supersedes is not None:
            error(f"{rel(path)}: Supersedes Document Version must be absent for an initial version")
        return

    if supersedes is None:
        error(f"{rel(path)}: Supersedes Document Version is required when Version History has multiple entries")
        return

    supersedes_semver = parse_semver(supersedes)
    if supersedes_semver is None:
        error(f"{rel(path)}: Supersedes Document Version {supersedes!r} must match vMAJOR.MINOR.PATCH")
        return
    if supersedes not in history_values:
        error(f"{rel(path)}: Supersedes Document Version {supersedes} is not present in Version History")
    if current_semver is not None and supersedes_semver >= current_semver:
        error(f"{rel(path)}: Supersedes Document Version {supersedes} must be lower than {version}")
    if current_semver is not None:
        prior_versions = [item for item in history_semvers if item < current_semver]
        if prior_versions:
            expected = max(prior_versions)
            if supersedes_semver != expected:
                expected_text = "v" + ".".join(str(part) for part in expected)
                error(
                    f"{rel(path)}: Supersedes Document Version {supersedes} must identify "
                    f"the immediate prior listed version {expected_text}"
                )


def load_workflow(path: Path) -> dict[str, object] | None:
    text = read_text(path)
    try:
        data = yaml.load(text, Loader=yaml.BaseLoader)
    except yaml.YAMLError as exc:
        error(f"{rel(path)}: invalid YAML: {exc}")
        return None
    if not isinstance(data, dict):
        error(f"{rel(path)}: workflow root must be a YAML mapping")
        return None
    return data


def check_workflow() -> None:
    workflow = ROOT / ".github/workflows/document-validation.yml"
    if not workflow.exists():
        return
    data = load_workflow(workflow)
    if data is None:
        return

    triggers = data.get("on")
    if not isinstance(triggers, dict) or not {"push", "pull_request"}.issubset(triggers):
        error(f"{rel(workflow)}: on must enable both push and pull_request")

    permissions = data.get("permissions")
    if not isinstance(permissions, dict) or permissions.get("contents") != "read":
        error(f"{rel(workflow)}: permissions.contents must be read")

    jobs = data.get("jobs")
    if not isinstance(jobs, dict):
        error(f"{rel(workflow)}: jobs mapping is required")
        return

    valid_job_found = False
    for job_name, job in jobs.items():
        if not isinstance(job, dict):
            continue
        strategy = job.get("strategy")
        matrix = strategy.get("matrix") if isinstance(strategy, dict) else None
        versions = matrix.get("python-version") if isinstance(matrix, dict) else None
        if not isinstance(versions, list) or set(versions) != {"3.10", "3.12"}:
            continue
        if job.get("runs-on") != "ubuntu-latest":
            continue
        steps = job.get("steps")
        if not isinstance(steps, list):
            continue

        checkout_index = setup_index = install_index = validator_index = tests_index = None
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            uses = step.get("uses")
            run = step.get("run")
            if uses == CHECKOUT_ACTION:
                checkout_index = index
            if uses == SETUP_PYTHON_ACTION:
                with_values = step.get("with")
                if isinstance(with_values, dict) and with_values.get("python-version") == "${{ matrix.python-version }}":
                    setup_index = index
            if isinstance(run, str):
                if "python -m pip install --disable-pip-version-check -r requirements-validation.txt" in run:
                    install_index = index
                if "python tools/validate_repository.py" in run:
                    validator_index = index
                if "python -m unittest discover -s tests -v" in run:
                    tests_index = index

        indices = [checkout_index, setup_index, install_index, validator_index, tests_index]
        if all(item is not None for item in indices) and indices == sorted(indices):
            valid_job_found = True
            break

    if not valid_job_found:
        error(
            f"{rel(workflow)}: one ubuntu-latest job must contain the exact SHA-pinned checkout and "
            "setup-python actions, Python 3.10/3.12 matrix, dependency installation, validator, "
            "and regression tests in execution order"
        )


def validate_markdown_extensions() -> None:
    docs = ROOT / "docs"
    if not docs.exists():
        return
    for path in docs.rglob("*"):
        if not path.is_file():
            continue
        suffix = path.suffix
        if suffix.casefold() in {".md", ".markdown"} and suffix != ".md":
            error(f"{rel(path)}: governed Markdown files must use the lowercase .md extension")


def check_validation_requirements() -> None:
    requirement_file = ROOT / "requirements-validation.txt"
    if not requirement_file.exists():
        return
    lines = [
        line.strip()
        for line in read_text(requirement_file).splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if lines != [VALIDATION_REQUIREMENT]:
        error(
            f"{rel(requirement_file)}: must contain exactly {VALIDATION_REQUIREMENT!r} "
            "to keep validation dependency resolution deterministic"
        )


validate_markdown_extensions()
md_files = sorted(path for path in ROOT.rglob("*") if path.is_file() and path.suffix == ".md")
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
    searchable = searchable_contents[path]
    check_links(path, searchable, anchors_by_path)
    metadata = parse_metadata(path, searchable)
    name = metadata.get("Canonical Filename") or metadata.get("Document Name")
    version = metadata.get("Document Version")
    status = metadata.get("Status")
    supersedes = metadata.get("Supersedes Document Version")
    role = metadata.get("Repository Role")
    relative = rel(path)
    is_directory_index = relative in DIRECTORY_INDEX_ALLOWLIST
    is_docs_markdown = path.is_relative_to(ROOT / "docs")

    if path.name == "README.md" and is_docs_markdown and not is_directory_index:
        error(f"{relative}: docs directory README is not in the approved non-normative index allowlist")

    if is_directory_index:
        if role != DIRECTORY_INDEX_ROLE:
            error(f"{relative}: Repository Role must be {DIRECTORY_INDEX_ROLE!r}")
        if name or version or status or supersedes:
            error(f"{relative}: non-normative directory indexes must not declare authority metadata")
        continue

    if is_docs_markdown and not (name and version and status):
        error(
            f"{relative}: every governed Markdown document under docs must declare "
            "Canonical Filename or Document Name, Document Version, and Status"
        )

    if name:
        if name != path.name:
            error(f"{relative}: canonical filename {name!r} must match the actual filename")
        if name in canonical:
            error(f"duplicate canonical filename {name}: {rel(canonical[name])} and {relative}")
        canonical[name] = path

    if name and version and status:
        documents[name] = (path, version, status)
        parse_version_history(path, searchable, version, status, supersedes)
        if status == "Draft for Review" and role and "normative" in role.lower() and "proposed" not in role.lower():
            error(f"{relative}: Draft normative role must say Proposed")
    elif version or status or name or supersedes:
        error(f"{relative}: incomplete document metadata")

required = [
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "NOTICE.md",
    "requirements-validation.txt",
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
    "tests/test_validate_repository.py",
    ".github/workflows/document-validation.yml",
]
required.extend(sorted(DIRECTORY_INDEX_ALLOWLIST))
for required_path in required:
    if not (ROOT / required_path).exists():
        error(f"missing required path: {required_path}")

# Root Current Document Set consistency and completeness. Fenced examples are excluded.
readme = searchable_contents.get(ROOT / "README.md", "")
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

# AI Active Document Manifest consistency and completeness. Fenced examples are excluded.
guide_path = ROOT / "docs/framework/AI_Engineering_Usage_Guide.md"
guide = searchable_contents.get(guide_path, "")
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

check_validation_requirements()
check_workflow()

if ERRORS:
    print("Repository validation: FAIL")
    for item in ERRORS:
        print(f"- {item}")
    sys.exit(1)

print(
    f"Repository validation: PASS ({len(md_files)} Markdown files checked, "
    f"Python {sys.version_info.major}.{sys.version_info.minor}, PyYAML {yaml.__version__})"
)
