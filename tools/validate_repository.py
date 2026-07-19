#!/usr/bin/env python3
"""Deterministic structural validation for the documentation repository.

Runtime requirement: Python 3.10 or later.
Validation dependency: PyYAML 6.0.3 installed with approved SHA-256 hashes.
CI validation runtimes: Python 3.10 and Python 3.12.
"""
from __future__ import annotations

import datetime as dt
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
        "'python -m pip install --require-hashes -r requirements-validation.txt'"
    )
    sys.exit(2)

MIN_PYTHON = (3, 10)
ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []

CHECKOUT_ACTION = "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"
SETUP_PYTHON_ACTION = "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1"
INSTALL_COMMAND = (
    "python -m pip install --disable-pip-version-check --require-hashes "
    "-r requirements-validation.txt"
)
VALIDATOR_COMMAND = "python tools/validate_repository.py"
TEST_COMMAND = "python -m unittest discover -s tests -v"
EXPECTED_REQUIREMENTS = """PyYAML==6.0.3 \\
    --hash=sha256:d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f \\
    --hash=sha256:9c7708761fccb9397fe64bbc0395abcae8c4bf7b0eac081e12b809bf47700d0b \\
    --hash=sha256:ba1cc08a7ccde2d2ec775841541641e4548226580ab850948cbfda66a1befcdc
"""
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
ALLOWED_STATUSES = {
    "Draft for Review",
    "Baseline",
    "Final Baseline",
    "Deprecated",
    "Retired",
}
SEMVER_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
HTML_CODE_TAGS = ("pre", "code", "script", "style")

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


def blank_preserving_newlines(value: str) -> str:
    return "".join("\n" if char == "\n" else " " for char in value)


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


def html_code_free_text(path: Path, text: str) -> str:
    """Blank HTML code/example blocks while preserving line positions."""
    result = text
    complete_re = re.compile(
        r"<(?P<tag>pre|code|script|style)\b[^>]*>.*?</(?P=tag)\s*>",
        re.IGNORECASE | re.DOTALL,
    )
    while True:
        result, count = complete_re.subn(lambda match: blank_preserving_newlines(match.group(0)), result)
        if count == 0:
            break

    opening_re = re.compile(r"<(pre|code|script|style)\b[^>]*>", re.IGNORECASE)
    opening = opening_re.search(result)
    if opening:
        line_no = result.count("\n", 0, opening.start()) + 1
        error(f"{rel(path)}:{line_no}: unclosed HTML code/example block <{opening.group(1).lower()}>")
        result = result[: opening.start()] + blank_preserving_newlines(result[opening.start() :])
    return result


def governed_searchable_text(path: Path, text: str) -> str:
    return html_code_free_text(path, fence_free_text(path, text))


def remove_inline_code(text: str) -> str:
    return re.sub(r"(`+)(.+?)\1", lambda match: " " * len(match.group(0)), text)


def parse_metadata(path: Path, searchable: str) -> dict[str, str]:
    """Parse unique metadata from before the first level-2 heading and line 80."""
    lines = searchable.splitlines()
    first_h2 = next(
        (index for index, line in enumerate(lines) if re.match(r"^ {0,3}##\s+", line)),
        len(lines),
    )
    opening_limit = min(first_h2, 80)
    patterns = {
        key: re.compile(rf"^\*\*{re.escape(key)}:\*\*\s*`?([^`\n]+?)`?\s*$", re.MULTILINE)
        for key in METADATA_KEYS
    }
    values: dict[str, str] = {}
    for key, pattern in patterns.items():
        matches = list(pattern.finditer(searchable))
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
                "before the first level-2 heading and line 80"
            )
            continue
        values[key] = match.group(1).strip()
    return values


def validate_status_role(path: Path, status: str, role: str) -> None:
    if status not in ALLOWED_STATUSES:
        error(f"{rel(path)}: Status {status!r} is not in the controlled enum")
        return
    role_cf = role.casefold()
    if status == "Draft for Review":
        if not role_cf.startswith("proposed "):
            error(f"{rel(path)}: Draft for Review Repository Role must begin with 'Proposed '")
    elif status in {"Baseline", "Final Baseline"}:
        if "normative" not in role_cf or "proposed" in role_cf:
            error(
                f"{rel(path)}: {status} Repository Role must be non-proposed normative wording"
            )
    elif status == "Deprecated":
        if not any(token in role_cf for token in ("deprecated", "historical")):
            error(f"{rel(path)}: Deprecated Repository Role must identify deprecated or historical use")
    elif status == "Retired":
        if not any(token in role_cf for token in ("retired", "historical")):
            error(f"{rel(path)}: Retired Repository Role must identify retired or historical use")


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
    return anchors


class DocumentHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.targets: list[str] = []
        self.anchors: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_cf = tag.casefold()
        for key, value in attrs:
            key_cf = key.casefold()
            if value and key_cf in {"id", "name"}:
                self.anchors.add(value)
            if value and ((tag_cf == "a" and key_cf == "href") or (tag_cf == "img" and key_cf == "src")):
                self.targets.append(value)


def parse_html(path: Path, text: str) -> DocumentHTMLParser:
    parser = DocumentHTMLParser()
    try:
        parser.feed(text)
    except Exception as exc:
        error(f"{rel(path)}: HTML parsing failed: {exc}")
    return parser


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


def check_links(
    path: Path,
    text: str,
    html_parser: DocumentHTMLParser,
    anchors_by_path: dict[Path, set[str]],
) -> None:
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

    for target in html_parser.targets:
        validate_target(path, target, anchors_by_path)


def split_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    in_code = False
    tick_length = 0
    index = 0
    while index < len(stripped):
        char = stripped[index]
        if escaped:
            current.append(char)
            escaped = False
            index += 1
            continue
        if char == "\\":
            current.append(char)
            escaped = True
            index += 1
            continue
        if char == "`":
            end = index
            while end < len(stripped) and stripped[end] == "`":
                end += 1
            run = end - index
            current.extend(stripped[index:end])
            if not in_code:
                in_code = True
                tick_length = run
            elif run == tick_length:
                in_code = False
                tick_length = 0
            index = end
            continue
        if char == "|" and not in_code:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    cells.append("".join(current).strip())
    return cells


def normalize_cell(cell: str) -> str:
    cell = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cell)
    return cell.replace("`", "").strip()


def parse_table_from_section(path: Path, section: str, table_name: str) -> tuple[list[str], list[list[str]]]:
    lines = section.splitlines()
    for index, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        if index + 1 >= len(lines) or not lines[index + 1].lstrip().startswith("|"):
            continue
        header = [normalize_cell(cell) for cell in split_markdown_row(line)]
        separator = [cell.strip() for cell in split_markdown_row(lines[index + 1])]
        if not separator or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator):
            continue
        if len(separator) != len(header):
            error(f"{rel(path)}: {table_name} separator cell count must match header")
        rows: list[list[str]] = []
        for row_line in lines[index + 2 :]:
            if not row_line.lstrip().startswith("|"):
                break
            row = [normalize_cell(cell) for cell in split_markdown_row(row_line)]
            if len(row) != len(header):
                error(
                    f"{rel(path)}: {table_name} row has {len(row)} cells; expected {len(header)}"
                )
            rows.append(row)
        return header, rows
    error(f"{rel(path)}: {table_name} table not found")
    return [], []


def parse_unique_markdown_table(path: Path, text: str, heading: str) -> tuple[list[str], list[list[str]]]:
    matches = list(re.finditer(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE))
    if len(matches) != 1:
        error(f"{rel(path)}: heading {heading!r} must appear exactly once; found {len(matches)}")
        return [], []
    section = text[matches[0].end() :]
    next_heading = re.search(r"^#{1,6}\s+", section, re.MULTILINE)
    if next_heading:
        section = section[: next_heading.start()]
    return parse_table_from_section(path, section, heading)


def parse_semver(value: str) -> tuple[int, int, int] | None:
    match = SEMVER_RE.fullmatch(value)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def parse_iso_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


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
    header, rows = parse_table_from_section(path, section, "Version History")
    if not header or not rows:
        return

    header_cf = [item.casefold() for item in header]
    required = {"version", "date", "status"}
    missing = required - set(header_cf)
    if missing:
        error(f"{rel(path)}: Version History missing required columns: {', '.join(sorted(missing))}")
        return
    summary_column = "summary" if "summary" in header_cf else "description" if "description" in header_cf else None
    if summary_column is None:
        error(f"{rel(path)}: Version History requires Summary or Description column")
        return

    version_index = header_cf.index("version")
    date_index = header_cf.index("date")
    status_index = header_cf.index("status")
    summary_index = header_cf.index(summary_column)

    current_semver = parse_semver(version)
    if current_semver is None:
        error(f"{rel(path)}: Document Version {version!r} must match vMAJOR.MINOR.PATCH")

    values: list[str] = []
    semvers: list[tuple[int, int, int]] = []
    dates_in_row_order: list[dt.date] = []
    for row in rows:
        if len(row) != len(header):
            continue
        row_version = row[version_index]
        parsed = parse_semver(row_version)
        if parsed is None:
            error(f"{rel(path)}: Version History value {row_version!r} must match vMAJOR.MINOR.PATCH")
            continue
        values.append(row_version)
        semvers.append(parsed)

        row_date = row[date_index]
        parsed_date = parse_iso_date(row_date)
        if row_version == version:
            if parsed_date is None:
                error(f"{rel(path)}: current Version History date must be a real ISO YYYY-MM-DD date")
        elif row_date != "Not recorded" and parsed_date is None:
            error(f"{rel(path)}: Version History date {row_date!r} must be a real ISO date or 'Not recorded'")
        if parsed_date is not None:
            dates_in_row_order.append(parsed_date)

        row_status = row[status_index]
        if row_version == version:
            if row_status != status:
                error(
                    f"{rel(path)}: Version History status for {version} is {row_status!r}; "
                    f"metadata status is {status!r}"
                )
        elif row_status != "Not recorded" and row_status not in ALLOWED_STATUSES:
            error(
                f"{rel(path)}: historical Version History status {row_status!r} "
                "must use the controlled enum or 'Not recorded'"
            )

        if not row[summary_index].strip():
            error(f"{rel(path)}: Version History summary/description must not be empty")

    if len(values) != len(set(values)):
        error(f"{rel(path)}: Version History contains duplicate versions")

    ascending = semvers == sorted(semvers)
    descending = semvers == sorted(semvers, reverse=True)
    if len(semvers) > 1 and not (ascending or descending):
        error(f"{rel(path)}: Version History versions must be monotonic")
    if len(dates_in_row_order) > 1:
        if ascending and dates_in_row_order != sorted(dates_in_row_order):
            error(f"{rel(path)}: recorded Version History dates must follow ascending version order")
        if descending and dates_in_row_order != sorted(dates_in_row_order, reverse=True):
            error(f"{rel(path)}: recorded Version History dates must follow descending version order")

    matching = [row for row in rows if len(row) == len(header) and row[version_index] == version]
    if len(matching) != 1:
        error(f"{rel(path)}: current version {version} must appear exactly once in Version History table")
    elif current_semver is not None and semvers and current_semver != max(semvers):
        highest = "v" + ".".join(str(part) for part in max(semvers))
        error(f"{rel(path)}: current version {version} must be the highest Version History version ({highest})")

    if len(values) <= 1:
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
    if supersedes not in values:
        error(f"{rel(path)}: Supersedes Document Version {supersedes} is not present in Version History")
    if current_semver is not None and supersedes_semver >= current_semver:
        error(f"{rel(path)}: Supersedes Document Version {supersedes} must be lower than {version}")
    if current_semver is not None:
        prior_versions = [item for item in semvers if item < current_semver]
        if prior_versions:
            expected = max(prior_versions)
            if supersedes_semver != expected:
                expected_text = "v" + ".".join(str(part) for part in expected)
                error(
                    f"{rel(path)}: Supersedes Document Version {supersedes} must identify "
                    f"the immediate prior listed version {expected_text}"
                )


def load_yaml(path: Path, base_loader: bool = False) -> object | None:
    text = read_text(path)
    try:
        loader = yaml.BaseLoader if base_loader else yaml.SafeLoader
        return yaml.load(text, Loader=loader)
    except yaml.YAMLError as exc:
        error(f"{rel(path)}: invalid YAML: {exc}")
        return None


def step_is_unconditional(step: dict[str, object]) -> bool:
    return "if" not in step and step.get("continue-on-error") not in {"true", True}


def check_workflow() -> None:
    workflow = ROOT / ".github/workflows/document-validation.yml"
    if not workflow.exists():
        return
    data = load_yaml(workflow, base_loader=True)
    if not isinstance(data, dict):
        error(f"{rel(workflow)}: workflow root must be a YAML mapping")
        return

    triggers = data.get("on")
    if not isinstance(triggers, dict) or not {"push", "pull_request"}.issubset(triggers):
        error(f"{rel(workflow)}: on must enable both push and pull_request")
    permissions = data.get("permissions")
    if permissions != {"contents": "read"}:
        error(f"{rel(workflow)}: permissions must be exactly contents: read")
    jobs = data.get("jobs")
    if not isinstance(jobs, dict):
        error(f"{rel(workflow)}: jobs mapping is required")
        return

    valid_job_found = False
    for job in jobs.values():
        if not isinstance(job, dict) or "if" in job or job.get("continue-on-error") in {"true", True}:
            continue
        if any(key in job for key in ("container", "services", "defaults", "env")):
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

        indices: list[int] = []
        matchers = [
            lambda step: step.get("uses") == CHECKOUT_ACTION
            and set(step).issubset({"name", "uses", "with"})
            and step.get("with") == {"persist-credentials": "false"},
            lambda step: step.get("uses") == SETUP_PYTHON_ACTION
            and set(step).issubset({"name", "uses", "with"})
            and step.get("with") == {"python-version": "${{ matrix.python-version }}"},
            lambda step: isinstance(step.get("run"), str)
            and set(step).issubset({"name", "run"})
            and step["run"].strip() == INSTALL_COMMAND,
            lambda step: isinstance(step.get("run"), str)
            and set(step).issubset({"name", "run"})
            and step["run"].strip() == VALIDATOR_COMMAND,
            lambda step: isinstance(step.get("run"), str)
            and set(step).issubset({"name", "run"})
            and step["run"].strip() == TEST_COMMAND,
        ]
        valid = True
        for matcher in matchers:
            matched = [
                index
                for index, step in enumerate(steps)
                if isinstance(step, dict) and matcher(step) and step_is_unconditional(step)
            ]
            if len(matched) != 1:
                valid = False
                break
            indices.append(matched[0])
        if valid and len(set(indices)) == len(indices) and indices == sorted(indices):
            valid_job_found = True
            break

    if not valid_job_found:
        error(
            f"{rel(workflow)}: one ubuntu-latest job must contain exact, separate, unconditional "
            "SHA-pinned checkout/setup with non-persisted credentials, Python 3.10/3.12 matrix, hash-verified dependency install, "
            "validator, and regression-test steps in execution order"
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
    path = ROOT / "requirements-validation.txt"
    if not path.exists():
        return
    text = read_text(path)
    if text != EXPECTED_REQUIREMENTS:
        error(
            f"{rel(path)}: must exactly pin PyYAML 6.0.3 with the approved source, "
            "Python 3.10 Linux x86-64, and Python 3.12 Linux x86-64 SHA-256 hashes"
        )


def load_authority_registry() -> list[dict[str, object]]:
    path = ROOT / "authority-registry.yaml"
    if not path.exists():
        return []
    data = load_yaml(path)
    if not isinstance(data, dict):
        error(f"{rel(path)}: registry root must be a YAML mapping")
        return []
    if data.get("registry_version") != 1:
        error(f"{rel(path)}: registry_version must be integer 1")
    if data.get("repository") != "host-device-control-framework":
        error(f"{rel(path)}: repository identity mismatch")
    policy = data.get("policy")
    expected_policy = {
        "routing_order": "role-first-language-second",
        "conflict_resolution": "topic-ownership-before-precedence",
        "draft_effect": "proposed-until-explicitly-adopted",
    }
    if policy != expected_policy:
        error(f"{rel(path)}: policy mapping must match the controlled authority-routing policy")
    documents = data.get("documents")
    if not isinstance(documents, list) or not documents:
        error(f"{rel(path)}: documents must be a non-empty list")
        return []

    required_fields = {
        "display_name",
        "path",
        "version",
        "status",
        "repository_role",
        "readme_purpose",
        "routing_role",
        "applies_when",
        "authority_topics",
        "prerequisite_documents",
    }
    valid_entries: list[dict[str, object]] = []
    seen_paths: set[str] = set()
    seen_names: set[str] = set()
    for index, entry in enumerate(documents):
        prefix = f"{rel(path)}: documents[{index}]"
        if not isinstance(entry, dict):
            error(f"{prefix} must be a mapping")
            continue
        if set(entry) != required_fields:
            missing = required_fields - set(entry)
            extra = set(entry) - required_fields
            detail = []
            if missing:
                detail.append(f"missing {sorted(missing)}")
            if extra:
                detail.append(f"unexpected {sorted(extra)}")
            error(f"{prefix} fields invalid: {'; '.join(detail)}")
            continue
        string_fields = required_fields - {"authority_topics", "prerequisite_documents"}
        if any(not isinstance(entry[field], str) or not entry[field].strip() for field in string_fields):
            error(f"{prefix}: all scalar fields must be non-empty strings")
            continue
        topics = entry["authority_topics"]
        prerequisites = entry["prerequisite_documents"]
        if not isinstance(topics, list) or not topics or any(not isinstance(item, str) or not item.strip() for item in topics):
            error(f"{prefix}: authority_topics must be a non-empty string list")
        if len(topics) != len(set(topics)):
            error(f"{prefix}: authority_topics must not contain duplicates")
        if not isinstance(prerequisites, list) or any(not isinstance(item, str) or not item.strip() for item in prerequisites):
            error(f"{prefix}: prerequisite_documents must be a string list")
        registry_path = entry["path"]
        display_name = entry["display_name"]
        if registry_path in seen_paths:
            error(f"{prefix}: duplicate path {registry_path}")
        if display_name in seen_names:
            error(f"{prefix}: duplicate display_name {display_name}")
        seen_paths.add(registry_path)
        seen_names.add(display_name)
        valid_entries.append(entry)

    registry_paths = {entry["path"] for entry in valid_entries}
    for entry in valid_entries:
        path_value = entry["path"]
        prerequisites = entry["prerequisite_documents"]
        if path_value in prerequisites:
            error(f"{rel(path)}: {path_value} must not list itself as a prerequisite")
        unknown = set(prerequisites) - registry_paths
        if unknown:
            error(f"{rel(path)}: {path_value} has unknown prerequisites: {', '.join(sorted(unknown))}")
    return valid_entries


validate_markdown_extensions()
md_files = sorted(path for path in ROOT.rglob("*") if path.is_file() and path.suffix == ".md")
contents: dict[Path, str] = {}
searchable_contents: dict[Path, str] = {}
html_by_path: dict[Path, DocumentHTMLParser] = {}
anchors_by_path: dict[Path, set[str]] = {}
canonical: dict[str, Path] = {}
documents: dict[str, tuple[Path, str, str, str]] = {}

for path in md_files:
    text = read_text(path)
    contents[path] = text
    searchable = governed_searchable_text(path, text)
    searchable_contents[path] = searchable
    html_parser = parse_html(path, remove_inline_code(searchable))
    html_by_path[path] = html_parser
    anchors_by_path[path.resolve()] = heading_anchors(remove_inline_code(searchable)) | html_parser.anchors

for path in md_files:
    searchable = searchable_contents[path]
    check_links(path, searchable, html_by_path[path], anchors_by_path)
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

    if is_docs_markdown and not (name and version and status and role):
        error(
            f"{relative}: every governed Markdown document under docs must declare "
            "Canonical Filename or Document Name, Document Version, Status, and Repository Role"
        )

    if name:
        if name != path.name:
            error(f"{relative}: canonical filename {name!r} must match the actual filename")
        if name in canonical:
            error(f"duplicate canonical filename {name}: {rel(canonical[name])} and {relative}")
        canonical[name] = path

    if name and version and status and role:
        documents[name] = (path, version, status, role)
        validate_status_role(path, status, role)
        parse_version_history(path, searchable, version, status, supersedes)
    elif version or status or name or supersedes or role:
        error(f"{relative}: incomplete document metadata")

required = [
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "NOTICE.md",
    "requirements-validation.txt",
    "authority-registry.yaml",
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

registry_entries = load_authority_registry()
registry_by_name: dict[str, dict[str, object]] = {}
registry_paths: set[str] = set()
for entry in registry_entries:
    path_value = str(entry["path"])
    canonical_name = Path(path_value).name
    registry_by_name[canonical_name] = entry
    registry_paths.add(path_value)
    if canonical_name not in documents:
        error(f"authority-registry.yaml references unknown governed document: {path_value}")
        continue
    actual_path, actual_version, actual_status, actual_role = documents[canonical_name]
    if rel(actual_path) != path_value:
        error(f"authority-registry.yaml path mismatch for {canonical_name}: {path_value}")
    if entry["version"] != actual_version:
        error(f"authority-registry.yaml version mismatch for {canonical_name}")
    if entry["status"] != actual_status:
        error(f"authority-registry.yaml status mismatch for {canonical_name}")
    if entry["repository_role"] != actual_role:
        error(f"authority-registry.yaml Repository Role mismatch for {canonical_name}")

actual_paths = {rel(item[0]) for item in documents.values()}
if registry_paths != actual_paths:
    missing = actual_paths - registry_paths
    extra = registry_paths - actual_paths
    if missing:
        error(f"authority-registry.yaml omits: {', '.join(sorted(missing))}")
    if extra:
        error(f"authority-registry.yaml has non-authority entries: {', '.join(sorted(extra))}")

readme_path = ROOT / "README.md"
readme = searchable_contents.get(readme_path, "")
readme_header, readme_rows = parse_unique_markdown_table(readme_path, readme, "## Current Document Set")
if [item.casefold() for item in readme_header] != ["document", "version", "status", "purpose"]:
    error("README.md: Current Document Set header must be Document, Version, Status, Purpose")
readme_names: list[str] = []
for row in readme_rows:
    if len(row) != 4:
        continue
    name, version, status, purpose = row
    canonical_name = Path(name).name
    readme_names.append(canonical_name)
    if canonical_name not in documents:
        error(f"README Current Document Set references unknown document: {canonical_name}")
        continue
    _, actual_version, actual_status, _ = documents[canonical_name]
    entry = registry_by_name.get(canonical_name)
    if version != actual_version or status != actual_status:
        error(f"README mismatch for {canonical_name}: listed {version}/{status}, actual {actual_version}/{actual_status}")
    if entry and purpose != entry["readme_purpose"]:
        error(f"README Purpose mismatch for {canonical_name}")
if len(readme_names) != len(set(readme_names)):
    error("README.md: Current Document Set contains duplicate document rows")
if set(readme_names) != set(documents):
    missing = set(documents) - set(readme_names)
    extra = set(readme_names) - set(documents)
    if missing:
        error(f"README Current Document Set omits: {', '.join(sorted(missing))}")
    if extra:
        error(f"README Current Document Set has non-authority entries: {', '.join(sorted(extra))}")

guide_path = ROOT / "docs/framework/AI_Engineering_Usage_Guide.md"
guide = searchable_contents.get(guide_path, "")
manifest_header, manifest_rows = parse_unique_markdown_table(
    guide_path, guide, "## 0.2 Active Document Manifest"
)
expected_manifest_header = [
    "document",
    "canonical repository path",
    "active version",
    "status",
    "routing role",
]
if [item.casefold() for item in manifest_header] != expected_manifest_header:
    error(f"{rel(guide_path)}: Active Document Manifest header is invalid")
manifest_names: list[str] = []
for row in manifest_rows:
    if len(row) != 5:
        continue
    display_name, path_cell, version, status, routing_role = row
    canonical_name = Path(path_cell).name
    manifest_names.append(canonical_name)
    if canonical_name not in documents:
        error(f"AI manifest references unknown document: {path_cell}")
        continue
    actual_path, actual_version, actual_status, _ = documents[canonical_name]
    entry = registry_by_name.get(canonical_name)
    if rel(actual_path) != path_cell:
        error(f"AI manifest path mismatch for {canonical_name}: {path_cell}")
    if version != actual_version or status != actual_status:
        error(f"AI manifest mismatch for {canonical_name}: listed {version}/{status}, actual {actual_version}/{actual_status}")
    if entry:
        if display_name != entry["display_name"]:
            error(f"AI manifest display-name mismatch for {canonical_name}")
        if routing_role != entry["routing_role"]:
            error(f"AI manifest Routing Role mismatch for {canonical_name}")
if len(manifest_names) != len(set(manifest_names)):
    error(f"{rel(guide_path)}: Active Document Manifest contains duplicate document rows")
if set(manifest_names) != set(documents):
    missing = set(documents) - set(manifest_names)
    extra = set(manifest_names) - set(documents)
    if missing:
        error(f"AI Active Document Manifest omits: {', '.join(sorted(missing))}")
    if extra:
        error(f"AI Active Document Manifest has non-authority entries: {', '.join(sorted(extra))}")

check_validation_requirements()
check_workflow()

if ERRORS:
    print("Repository validation: FAIL")
    for item in ERRORS:
        print(f"- {item}")
    sys.exit(1)

print(
    f"Repository validation: PASS ({len(md_files)} Markdown files checked, "
    f"{len(documents)} governed documents, Python {sys.version_info.major}.{sys.version_info.minor}, "
    f"PyYAML {yaml.__version__})"
)
