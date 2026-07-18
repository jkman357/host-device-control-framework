#!/usr/bin/env python3
"""Deterministic structural validation for the documentation repository."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def error(message: str) -> None:
    ERRORS.append(message)


def read_text(path: Path) -> str:
    try:
        data = path.read_bytes()
        text = data.decode("utf-8")
    except Exception as exc:
        error(f"{path.relative_to(ROOT)}: UTF-8 read failed: {exc}")
        return ""
    if text and not text.endswith("\n"):
        error(f"{path.relative_to(ROOT)}: missing final newline")
    return text


def metadata(text: str, key: str) -> str | None:
    match = re.search(rf"^\*\*{re.escape(key)}:\*\*\s*`?([^`\n]+?)`?\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def check_fences(path: Path, text: str) -> None:
    fences = [line for line in text.splitlines() if re.match(r"^\s*(```|~~~)", line)]
    if len(fences) % 2:
        error(f"{path.relative_to(ROOT)}: unbalanced fenced Code blocks")


def check_links(path: Path, text: str) -> None:
    for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", text):
        target = target.strip().split()[0]
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = unquote(target.split("#", 1)[0])
        if not target:
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            error(f"{path.relative_to(ROOT)}: link escapes repository: {target}")
            continue
        if not resolved.exists():
            error(f"{path.relative_to(ROOT)}: missing link target: {target}")


def parse_markdown_table(text: str, heading: str) -> list[list[str]]:
    pos = text.find(heading)
    if pos < 0:
        return []
    rows: list[list[str]] = []
    started = False
    for line in text[pos:].splitlines()[1:]:
        if line.startswith("## ") and started:
            break
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c) for c in cells):
                started = True
                continue
            if not started:
                started = True
                continue
            rows.append(cells)
        elif started and rows:
            break
    return rows


def normalize_cell(cell: str) -> str:
    cell = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cell)
    return cell.replace("`", "").strip()


md_files = sorted(ROOT.rglob("*.md"))
contents: dict[Path, str] = {}
canonical: dict[str, Path] = {}
documents: dict[str, tuple[Path, str, str]] = {}

for path in md_files:
    text = read_text(path)
    contents[path] = text
    check_fences(path, text)
    check_links(path, text)
    name = metadata(text, "Canonical Filename") or metadata(text, "Document Name")
    version = metadata(text, "Document Version")
    status = metadata(text, "Status")
    role = metadata(text, "Repository Role")
    if name:
        if name in canonical:
            error(f"duplicate canonical filename {name}: {canonical[name].relative_to(ROOT)} and {path.relative_to(ROOT)}")
        canonical[name] = path
    if version or status:
        if not (version and status and name):
            error(f"{path.relative_to(ROOT)}: incomplete document metadata")
        else:
            documents[name] = (path, version, status)
            if f"| {version} |" not in text:
                error(f"{path.relative_to(ROOT)}: current version {version} missing from Version History")
            if status == "Draft for Review" and role and "normative" in role.lower() and "proposed" not in role.lower():
                error(f"{path.relative_to(ROOT)}: Draft normative role must say Proposed")

required = [
    "README.md", "CHANGELOG.md", "LICENSE", "NOTICE.md",
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
for rel in required:
    if not (ROOT / rel).exists():
        error(f"missing required path: {rel}")

# Root Current Document Set consistency.
readme = contents.get(ROOT / "README.md", "")
for row in parse_markdown_table(readme, "## Current Document Set"):
    if len(row) < 3:
        continue
    name, version, status = map(normalize_cell, row[:3])
    if name not in documents:
        error(f"README Current Document Set references unknown document: {name}")
        continue
    _, actual_version, actual_status = documents[name]
    if version != actual_version or status != actual_status:
        error(f"README mismatch for {name}: listed {version}/{status}, actual {actual_version}/{actual_status}")

# AI Active Document Manifest consistency.
guide_path = ROOT / "docs/framework/AI_Engineering_Usage_Guide.md"
guide = contents.get(guide_path, "")
for row in parse_markdown_table(guide, "## 0.2 Active Document Manifest"):
    if len(row) < 4:
        continue
    display, path_cell, version, status = map(normalize_cell, row[:4])
    canonical_name = Path(path_cell).name
    if canonical_name not in documents:
        error(f"AI manifest references unknown document: {path_cell}")
        continue
    actual_path, actual_version, actual_status = documents[canonical_name]
    if actual_path.relative_to(ROOT).as_posix() != path_cell:
        error(f"AI manifest path mismatch for {canonical_name}: {path_cell}")
    if version != actual_version or status != actual_status:
        error(f"AI manifest mismatch for {canonical_name}: listed {version}/{status}, actual {actual_version}/{actual_status}")

if ERRORS:
    print("Repository validation: FAIL")
    for item in ERRORS:
        print(f"- {item}")
    sys.exit(1)

print(f"Repository validation: PASS ({len(md_files)} Markdown files checked)")
