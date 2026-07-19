#!/usr/bin/env python3
"""Deterministic structural validation for host-device-control-framework."""
from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import unquote

import yaml

REQUIRED_REGISTRY_ROOT = {"registry_version", "repository", "source_of_truth", "policy", "documents"}
REQUIRED_POLICY = {"routing_order", "conflict_resolution", "draft_effect"}
REQUIRED_DOCUMENT_KEYS = {
    "display_name", "path", "version", "status", "repository_role", "readme_purpose",
    "routing_role", "applies_when", "authority_topics", "prerequisite_documents",
}
ALLOWED_STATUS = {"Draft for Review", "Baseline", "Final Baseline"}
INDEX_ALLOWLIST = {
    "docs/framework/README.md", "docs/protocol/README.md", "docs/coordinator/README.md",
    "docs/node/README.md", "docs/coding-rules/README.md", "docs/validation/README.md",
}
NOTICE_HEADINGS = [
    "Copyright Notice", "Personal Engineering Project Disclaimer", "No Employer or Company Representation",
    "AI Assistance Disclosure", "Third-Party Standards and Trademark Notice", "File-Specific Notice Precedence",
]
CHECKLIST_PRINCIPLE = (
    "Checklists do not independently create requirements. They provide review, traceability, and "
    "evidence-capture views of requirements established by governing authority documents."
)
NEW_CHANGELOG_FILES = [
    "Protocol_Compatibility_Rules.md", "Protocol_Registry_Governance.md", "Protocol_Security_Profile.md",
    "Node_Software_Engineering_Rules.md", "Validation_Evidence_Guide.md", "Protocol_Validation_Checklist.md",
    "Framework_Conformance_Checklist.md", "Coding_Rules_Review_Checklist.md",
    "AI_Generated_Artifact_Validation_Guide.md",
]
SEMVER_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
META_RE = re.compile(r"^\*\*(?P<key>[^*]+):\*\*\s*(?P<value>.*?)\s{0,2}$")
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\((?P<target><[^>]+>|(?:\\.|[^)])*)\)")
HTML_LINK_RE = re.compile(r"<(?:a|img)\b[^>]*(?:href|src)=[\"'](?P<target>[^\"']+)[\"'][^>]*>", re.I)
FENCE_RE = re.compile(r"^(?P<indent>\s*)(?P<mark>`{3,}|~{3,})")
VERSIONED_FILENAME_RE = re.compile(
    r"(?:_v\d+\.\d+\.\d+|(?:^|[_-])(?:Final|Baseline|Draft)(?:[_-]|\.)|(?:^|[_-])RC\d+|"
    r"(?:^|[_-])20\d{2}[-_]\d{2}[-_]\d{2})(?=\.md$|[_-])",
    re.I,
)


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.YAMLError(f"duplicate YAML key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def read_text(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        raise ValueError("UTF-8 BOM is prohibited")
    if b"\x00" in data:
        raise ValueError("NUL byte is prohibited")
    if b"\r" in data:
        raise ValueError("CR line endings are prohibited")
    text = data.decode("utf-8")
    if text and not text.endswith("\n"):
        raise ValueError("final newline is required")
    return text


def mask_fenced_and_inline_code(text: str) -> str:
    out: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        m = FENCE_RE.match(line)
        if m:
            mark = m.group("mark")
            if fence is None:
                fence = mark[0]
            elif mark[0] == fence:
                fence = None
            out.append("")
            continue
        if fence is not None:
            out.append("")
            continue
        line = re.sub(r"`[^`]*`", "", line)
        out.append(line)
    return "\n".join(out)


def metadata(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("## "):
            break
        m = META_RE.match(line)
        if m:
            key = m.group("key").strip()
            value = m.group("value").strip()
            if key in result:
                raise ValueError(f"duplicate metadata field: {key}")
            result[key] = value
    return result


def parse_pipe_table(lines: list[str], heading: str) -> list[list[str]]:
    positions = [i for i, line in enumerate(lines) if line.strip() == heading]
    if len(positions) != 1:
        raise ValueError(f"expected exactly one {heading!r} heading, found {len(positions)}")
    i = positions[0] + 1
    while i < len(lines) and not lines[i].lstrip().startswith("|"):
        if lines[i].startswith("#"):
            raise ValueError(f"table missing under {heading}")
        i += 1
    rows: list[list[str]] = []
    while i < len(lines) and lines[i].lstrip().startswith("|"):
        row = lines[i].strip().strip("|")
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", row)]
        rows.append(cells)
        i += 1
    if len(rows) < 2:
        raise ValueError(f"table missing under {heading}")
    return rows


def anchor_slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[`*_~]", "", text).strip().lower()
    text = re.sub(r"[^\w\-\s]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s\-]+", "-", text).strip("-")
    return text


def anchors(text: str) -> set[str]:
    masked = mask_fenced_and_inline_code(text)
    base_counts: dict[str, int] = collections.defaultdict(int)
    result: set[str] = set()
    lines = masked.splitlines()
    for i, line in enumerate(lines):
        title: str | None = None
        m = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if m:
            title = m.group(1)
        elif i + 1 < len(lines) and line.strip() and re.match(r"^=+\s*$|^-+\s*$", lines[i + 1]):
            title = line.strip()
        if title is None:
            continue
        base = anchor_slug(title)
        if not base:
            continue
        n = base_counts[base]
        result.add(base if n == 0 else f"{base}-{n}")
        base_counts[base] += 1
    return result


class Validator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.errors: list[str] = []
        self.registry: dict[str, Any] = {}
        self.documents: list[dict[str, Any]] = []

    def error(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")

    def run(self) -> list[str]:
        checks = [
            self.check_required_files,
            self.check_text_encoding,
            self.check_registry,
            self.check_governed_set,
            self.check_metadata,
            self.check_registry_graph,
            self.check_human_tables,
            self.check_directory_indexes,
            self.check_filename_policy,
            self.check_links,
            self.check_markdown_structure,
            self.check_authority_boundaries,
            self.check_notice,
            self.check_changelog,
            self.check_workflow,
        ]
        for check in checks:
            try:
                check()
            except Exception as exc:  # keep collecting deterministic failures
                self.error(check.__name__, f"unexpected validation exception: {exc}")
        return self.errors

    def files(self) -> Iterable[Path]:
        for p in sorted(self.root.rglob("*")):
            if p.is_file() and ".git" not in p.parts:
                yield p

    def check_required_files(self) -> None:
        required = [
            "README.md", "CHANGELOG.md", "LICENSE", "NOTICE.md", "authority-registry.yaml",
            "requirements-validation.txt", ".github/workflows/document-validation.yml",
            "tools/validate_repository.py", "tests/test_validate_repository.py",
        ]
        for rel in required:
            if not (self.root / rel).is_file():
                self.error(rel, "required repository file is missing")

    def check_text_encoding(self) -> None:
        for p in self.files():
            if p.suffix.lower() not in {".md", ".yaml", ".yml", ".py", ".txt"} and p.name not in {"LICENSE"}:
                continue
            try:
                read_text(p)
            except Exception as exc:
                self.error(p.relative_to(self.root).as_posix(), str(exc))

    def check_registry(self) -> None:
        path = self.root / "authority-registry.yaml"
        if not path.is_file():
            return
        try:
            text = read_text(path)
            if re.search(r"(^|\s)[&*][A-Za-z0-9_-]+", mask_fenced_and_inline_code(text)):
                self.error("authority-registry.yaml", "YAML anchors and aliases are prohibited")
            self.registry = yaml.load(text, Loader=UniqueKeyLoader)
        except Exception as exc:
            self.error("authority-registry.yaml", f"invalid controlled YAML: {exc}")
            return
        if not isinstance(self.registry, dict):
            self.error("authority-registry.yaml", "root must be a mapping")
            return
        keys = set(self.registry)
        if keys != REQUIRED_REGISTRY_ROOT:
            self.error("authority-registry.yaml", f"root fields must be exactly {sorted(REQUIRED_REGISTRY_ROOT)}, got {sorted(keys)}")
        if self.registry.get("registry_version") != 1:
            self.error("authority-registry.yaml", "registry_version must be 1")
        if self.registry.get("repository") != "host-device-control-framework":
            self.error("authority-registry.yaml", "repository identity mismatch")
        if self.registry.get("source_of_truth") != "GitHub main":
            self.error("authority-registry.yaml", "source_of_truth must be exactly 'GitHub main'")
        policy = self.registry.get("policy")
        if not isinstance(policy, dict) or set(policy) != REQUIRED_POLICY:
            self.error("authority-registry.yaml", f"policy fields must be exactly {sorted(REQUIRED_POLICY)}")
        else:
            expected = {
                "routing_order": "role-first-language-second",
                "conflict_resolution": "topic-ownership-before-precedence",
                "draft_effect": "proposed-until-explicitly-adopted",
            }
            for k, v in expected.items():
                if policy.get(k) != v:
                    self.error("authority-registry.yaml", f"policy.{k} must be {v!r}")
        docs = self.registry.get("documents")
        if not isinstance(docs, list) or not docs:
            self.error("authority-registry.yaml", "documents must be a non-empty sequence")
            return
        self.documents = []
        seen_path: set[str] = set()
        seen_name: set[str] = set()
        for i, d in enumerate(docs):
            where = f"authority-registry.yaml documents[{i}]"
            if not isinstance(d, dict):
                self.error(where, "entry must be a mapping")
                continue
            if set(d) != REQUIRED_DOCUMENT_KEYS:
                self.error(where, f"fields must be exactly {sorted(REQUIRED_DOCUMENT_KEYS)}")
                continue
            self.documents.append(d)
            rel = d["path"]
            if not isinstance(rel, str) or not rel.startswith("docs/") or not rel.endswith(".md"):
                self.error(where, "path must be a docs/*.md path")
            if rel.endswith("/README.md"):
                self.error(where, "directory README files are indexes and shall not be governed documents")
            if rel in seen_path:
                self.error(where, f"duplicate path {rel}")
            seen_path.add(rel)
            name = str(d["display_name"]).strip().casefold()
            if name in seen_name:
                self.error(where, f"duplicate display_name {d['display_name']!r}")
            seen_name.add(name)
            if not SEMVER_RE.match(str(d["version"])):
                self.error(where, f"invalid semantic version {d['version']!r}")
            if d["status"] not in ALLOWED_STATUS:
                self.error(where, f"invalid status {d['status']!r}")
            for key in ("repository_role", "readme_purpose", "routing_role", "applies_when"):
                if not isinstance(d[key], str) or not d[key].strip():
                    self.error(where, f"{key} must be non-empty text")
            if not isinstance(d["authority_topics"], list) or not d["authority_topics"]:
                self.error(where, "authority_topics must be a non-empty sequence")
            if not isinstance(d["prerequisite_documents"], list):
                self.error(where, "prerequisite_documents must be a sequence")

    def check_governed_set(self) -> None:
        actual = {
            p.relative_to(self.root).as_posix()
            for p in (self.root / "docs").rglob("*.md")
            if p.relative_to(self.root).as_posix() not in INDEX_ALLOWLIST
        }
        # Also reject uppercase Markdown extensions because they bypass lower-case glob expectations.
        for p in (self.root / "docs").rglob("*"):
            if p.is_file() and p.suffix.lower() == ".md" and p.suffix != ".md":
                self.error(p.relative_to(self.root).as_posix(), "Markdown extension must be lowercase .md")
        registered = {d["path"] for d in self.documents}
        for rel in sorted(actual - registered):
            self.error(rel, "governed Markdown exists but is not registered")
        for rel in sorted(registered - actual):
            self.error(rel, "registry entry does not resolve to a governed Markdown file")

    def check_metadata(self) -> None:
        canonical_seen: dict[str, str] = {}
        identity_seen: dict[str, str] = {}
        for d in self.documents:
            rel = d["path"]
            p = self.root / rel
            if not p.is_file():
                continue
            try:
                text = read_text(p)
                meta = metadata(text)
            except Exception as exc:
                self.error(rel, f"metadata error: {exc}")
                continue
            canonical = meta.get("Canonical Filename") or meta.get("Document Name")
            if canonical:
                canonical = canonical.strip("`")
            else:
                canonical = p.name
            if canonical != p.name:
                self.error(rel, f"canonical filename {canonical!r} does not match path filename {p.name!r}")
            key = canonical.casefold()
            if key in canonical_seen:
                self.error(rel, f"duplicate canonical document identity also used by {canonical_seen[key]}")
            canonical_seen[key] = rel
            doc_id = meta.get("Document ID")
            if doc_id:
                k = doc_id.casefold()
                if k in identity_seen:
                    self.error(rel, f"duplicate Document ID also used by {identity_seen[k]}")
                identity_seen[k] = rel
            expected = {
                "Document Version": d["version"],
                "Status": d["status"],
                "Repository Role": d["repository_role"],
            }
            for field, value in expected.items():
                if meta.get(field) != value:
                    self.error(rel, f"metadata {field} must equal registry value {value!r}, got {meta.get(field)!r}")
            m = SEMVER_RE.match(d["version"])
            if m and tuple(map(int, m.groups())) != (1, 0, 0):
                sup = meta.get("Supersedes Document Version")
                if not sup or not SEMVER_RE.match(sup):
                    self.error(rel, "non-initial version requires valid Supersedes Document Version metadata")
            # Current version/status must occur in a Version History row.
            hist_pattern = re.compile(rf"^\|\s*{re.escape(d['version'])}\s*\|[^\n]*\|\s*{re.escape(d['status'])}\s*\|", re.M)
            if not hist_pattern.search(mask_fenced_and_inline_code(text)):
                self.error(rel, "Version History lacks a row for the current version and status")

    def check_registry_graph(self) -> None:
        paths = {d["path"] for d in self.documents}
        graph: dict[str, list[str]] = {}
        topics: dict[str, str] = {}
        for d in self.documents:
            graph[d["path"]] = list(d["prerequisite_documents"])
            for pre in d["prerequisite_documents"]:
                if pre not in paths:
                    self.error(d["path"], f"unknown prerequisite document {pre}")
                if pre == d["path"]:
                    self.error(d["path"], "document cannot require itself")
            for topic in d["authority_topics"]:
                norm = re.sub(r"\s+", " ", str(topic).strip().casefold())
                if norm in topics:
                    self.error(d["path"], f"duplicate exact authority topic {topic!r} also owned by {topics[norm]}")
                topics[norm] = d["path"]
        visiting: set[str] = set(); visited: set[str] = set()
        def dfs(node: str, stack: list[str]) -> None:
            if node in visiting:
                self.error("authority-registry.yaml", "prerequisite cycle: " + " -> ".join(stack + [node]))
                return
            if node in visited:
                return
            visiting.add(node)
            for nxt in graph.get(node, []):
                if nxt in graph:
                    dfs(nxt, stack + [node])
            visiting.remove(node); visited.add(node)
        for node in graph:
            dfs(node, [])

    def check_human_tables(self) -> None:
        expected = {d["path"]: d for d in self.documents}
        # Root Current Document Set.
        p = self.root / "README.md"
        if p.is_file():
            try:
                rows = parse_pipe_table(read_text(p).splitlines(), "## Current Document Set")
                actual: dict[str, tuple[str, str, str]] = {}
                for cells in rows[2:]:
                    if len(cells) != 4:
                        self.error("README.md", f"Current Document Set row must have 4 columns: {cells}")
                        continue
                    m = re.search(r"\]\((docs/[^)]+\.md)\)", cells[0])
                    if not m:
                        self.error("README.md", f"invalid document link in Current Document Set: {cells[0]}")
                        continue
                    actual[m.group(1)] = (cells[1], cells[2], cells[3])
                if set(actual) != set(expected):
                    self.error("README.md", f"Current Document Set paths differ from registry; missing={sorted(set(expected)-set(actual))}, extra={sorted(set(actual)-set(expected))}")
                for rel, d in expected.items():
                    if rel in actual and actual[rel] != (d["version"], d["status"], d["readme_purpose"]):
                        self.error("README.md", f"Current Document Set fields mismatch for {rel}")
            except Exception as exc:
                self.error("README.md", str(exc))
        # AI manifest.
        rel_ai = "docs/framework/AI_Engineering_Usage_Guide.md"
        p = self.root / rel_ai
        if p.is_file():
            try:
                rows = parse_pipe_table(read_text(p).splitlines(), "## 0.2 Active Document Manifest")
                actual: dict[str, tuple[str, str, str, str]] = {}
                for cells in rows[2:]:
                    if len(cells) != 5:
                        self.error(rel_ai, f"Active Document Manifest row must have 5 columns: {cells}")
                        continue
                    path = cells[1].strip("`")
                    actual[path] = (cells[0], cells[2].strip("`"), cells[3], cells[4])
                if set(actual) != set(expected):
                    self.error(rel_ai, f"Active Document Manifest paths differ from registry; missing={sorted(set(expected)-set(actual))}, extra={sorted(set(actual)-set(expected))}")
                for rel, d in expected.items():
                    tup=(d["display_name"],d["version"],d["status"],d["routing_role"])
                    if rel in actual and actual[rel] != tup:
                        self.error(rel_ai, f"Active Document Manifest fields mismatch for {rel}")
            except Exception as exc:
                self.error(rel_ai, str(exc))

    def check_directory_indexes(self) -> None:
        by_dir: dict[str, set[str]] = collections.defaultdict(set)
        for d in self.documents:
            pp = PurePosixPath(d["path"])
            by_dir[pp.parent.as_posix()].add(pp.name)
        for directory, expected in sorted(by_dir.items()):
            rel = f"{directory}/README.md"
            p = self.root / rel
            if not p.is_file():
                self.error(rel, "required directory index is missing")
                continue
            text = mask_fenced_and_inline_code(read_text(p))
            found: set[str] = set()
            for m in MD_LINK_RE.finditer(text):
                target = m.group("target").strip("<>").split("#",1)[0]
                if not target or "://" in target or target.startswith(('/', '#', 'mailto:')):
                    continue
                if "/" not in target and target.endswith(".md") and target != "README.md":
                    found.add(unquote(target))
            missing = expected - found
            if missing:
                self.error(rel, f"directory index omits governed documents: {sorted(missing)}")
            # Same-directory governed-looking links not in registry are suspicious.
            extra = {x for x in found - expected if (self.root/directory/x).is_file()}
            if extra:
                self.error(rel, f"directory index lists unregistered governed documents: {sorted(extra)}")

    def check_filename_policy(self) -> None:
        for p in (self.root / "docs").rglob("*.md"):
            if VERSIONED_FILENAME_RE.search(p.name):
                self.error(p.relative_to(self.root).as_posix(), "maintained Markdown filename embeds version, release status, RC, or date")
            if any(ord(ch) > 127 for ch in p.name):
                self.error(p.relative_to(self.root).as_posix(), "maintained Markdown filename must use stable English ASCII naming")

    def check_links(self) -> None:
        for p in [x for x in self.files() if x.suffix == ".md"]:
            rel = p.relative_to(self.root).as_posix()
            text = mask_fenced_and_inline_code(read_text(p))
            targets = [m.group("target").strip("<>") for m in MD_LINK_RE.finditer(text)]
            targets += [m.group("target") for m in HTML_LINK_RE.finditer(text)]
            for raw in targets:
                raw = raw.replace("\\)", ")").strip()
                if not raw or raw.startswith(("#", "mailto:", "http://", "https://", "data:")):
                    if raw.startswith("#") and raw[1:] not in anchors(read_text(p)):
                        self.error(rel, f"missing local heading anchor {raw}")
                    continue
                target_path, sep, fragment = raw.partition("#")
                target_path = unquote(target_path)
                candidate = (p.parent / target_path).resolve()
                try:
                    candidate.relative_to(self.root)
                except ValueError:
                    self.error(rel, f"local link escapes repository: {raw}")
                    continue
                if not candidate.exists():
                    self.error(rel, f"broken local link target: {raw}")
                    continue
                if fragment and candidate.is_file() and candidate.suffix == ".md":
                    if unquote(fragment) not in anchors(read_text(candidate)):
                        self.error(rel, f"missing target anchor in {raw}")

    def check_markdown_structure(self) -> None:
        for p in [x for x in self.files() if x.suffix == ".md"]:
            rel = p.relative_to(self.root).as_posix()
            text = read_text(p)
            # Balanced fence parser.
            fence: str | None = None
            for n, line in enumerate(text.splitlines(), 1):
                m = FENCE_RE.match(line)
                if not m:
                    continue
                mark=m.group("mark")
                if fence is None:
                    fence=mark[0]
                elif mark[0]==fence:
                    fence=None
            if fence is not None:
                self.error(rel, "unclosed fenced code block")
            # First visible heading should be H1 and there should be exactly one title before metadata.
            headings=[]
            masked=mask_fenced_and_inline_code(text)
            for line in masked.splitlines():
                m=re.match(r"^(#{1,6})\s+(.+)$",line)
                if m: headings.append((len(m.group(1)),m.group(2).strip()))
            if not headings or headings[0][0] != 1:
                self.error(rel, "first visible heading must be level 1")
            # Large upward heading-level jumps are usually structural mistakes.
            prev=1
            for level,title in headings[1:]:
                if level > prev + 1:
                    self.error(rel, f"heading level jumps from H{prev} to H{level} at {title!r}")
                prev=level

    def check_authority_boundaries(self) -> None:
        # Dedicated Protocol governance must reside under docs/protocol.
        names={"Protocol_Compatibility_Rules.md","Protocol_Registry_Governance.md","Protocol_Security_Profile.md"}
        for p in (self.root / "docs").rglob("*.md"):
            if p.name in names and p.parent != self.root/"docs/protocol":
                self.error(p.relative_to(self.root).as_posix(), "Protocol governance document is outside docs/protocol")
        # Node must be routed in both human and AI entry points.
        for rel in ["README.md","docs/framework/AI_Engineering_Usage_Guide.md"]:
            p=self.root/rel
            if p.is_file():
                text=read_text(p)
                for token in ["docs/node/Node_Software_Engineering_Rules.md" if rel=="README.md" else "Node_Software_Engineering_Rules.md"]:
                    if token not in text:
                        self.error(rel, "Node Software Engineering Rules are not routed")
        # Checklists are views, not independent normative authority.
        for d in self.documents:
            if d["path"].endswith("Checklist.md"):
                p=self.root/d["path"]
                if p.is_file() and CHECKLIST_PRINCIPLE not in read_text(p):
                    self.error(d["path"], "missing common checklist non-authority principle")
                role=d["repository_role"].casefold()
                if "not" not in role or "authority" not in role:
                    self.error(d["path"], "checklist repository_role must explicitly deny independent requirement authority")
        # Validation docs must not claim independent Product authority in metadata.
        for d in self.documents:
            if d["path"].startswith("docs/validation/") and "not" not in d["repository_role"].casefold():
                self.error(d["path"], "validation document repository_role must explicitly state its non-authority boundary")

    def check_notice(self) -> None:
        p=self.root/"NOTICE.md"
        if not p.is_file(): return
        text=read_text(p)
        headings=[m.group(1).strip() for m in re.finditer(r"^##\s+(.+)$",text,re.M)]
        if headings != NOTICE_HEADINGS:
            self.error("NOTICE.md", f"required level-2 headings/order are {NOTICE_HEADINGS}, got {headings}")
        required=[
            "personal engineering research and methodology project",
            "current or former employer",
            "AI assistance does not transfer engineering authority or responsibility",
            "does not reproduce or replace official MISRA, ISO, IEC, NIST, Microsoft, Oracle, C++",
            "does not replace, amend, expand, or reduce the legal effect",
            "(LICENSE)",
        ]
        for phrase in required:
            if phrase not in text:
                self.error("NOTICE.md", f"missing required notice language: {phrase!r}")

    def check_changelog(self) -> None:
        p=self.root/"CHANGELOG.md"
        if not p.is_file(): return
        text=read_text(p)
        if "## Unreleased" not in text:
            self.error("CHANGELOG.md", "missing Unreleased section")
        for name in NEW_CHANGELOG_FILES:
            if name not in text:
                self.error("CHANGELOG.md", f"new governed document is not recorded: {name}")
        for token in ["authority-registry.yaml", "Active Document Manifest", "NOTICE.md", "Validator"]:
            if token.casefold() not in text.casefold():
                self.error("CHANGELOG.md", f"missing synchronization/change record for {token}")

    def check_workflow(self) -> None:
        rel=".github/workflows/document-validation.yml"; p=self.root/rel
        if not p.is_file(): return
        try:
            wf=yaml.load(read_text(p),Loader=UniqueKeyLoader)
        except Exception as exc:
            self.error(rel,f"invalid YAML: {exc}"); return
        if not isinstance(wf,dict): self.error(rel,"workflow root must be mapping"); return
        # PyYAML 1.1 can parse 'on' as True; accept either key but require declared events.
        on=wf.get("on",wf.get(True))
        if not isinstance(on,dict) or set(on)!={"push","pull_request"}:
            self.error(rel,"workflow must enable exactly push and pull_request")
        perms=wf.get("permissions")
        if perms != {"contents":"read"}:
            self.error(rel,"workflow permissions must be read-only contents")
        jobs=wf.get("jobs")
        if not isinstance(jobs,dict) or set(jobs)!={"validate-documentation"}:
            self.error(rel,"workflow must contain exactly validate-documentation job")
            return
        job=jobs["validate-documentation"]
        if job.get("runs-on")!="ubuntu-24.04": self.error(rel,"runner must be ubuntu-24.04")
        versions=job.get("strategy",{}).get("matrix",{}).get("python-version")
        if versions != ["3.10","3.12"]: self.error(rel,"Python matrix must be exactly 3.10 and 3.12")
        steps=job.get("steps")
        if not isinstance(steps,list): self.error(rel,"steps must be a sequence"); return
        names=[x.get("name") for x in steps if isinstance(x,dict)]
        required_names=["Check out repository","Set up Python ${{ matrix.python-version }}","Install validation dependencies","Validate repository documentation","Run validator regression tests"]
        if names != required_names: self.error(rel,f"workflow steps must be exact and ordered: {required_names}")
        for step in steps[:2]:
            use=step.get("uses","")
            if not re.match(r"^actions/(?:checkout|setup-python)@[0-9a-f]{40}$",use):
                self.error(rel,f"GitHub Action must be pinned by full SHA: {use}")
        runs=[x.get("run") for x in steps if isinstance(x,dict) and "run" in x]
        expected_runs=[
            "python -m pip install --disable-pip-version-check --require-hashes -r requirements-validation.txt",
            "python tools/validate_repository.py",
            "python -m unittest discover -s tests -v",
        ]
        if runs != expected_runs: self.error(rel,"workflow run commands must be exact, separate, and ordered")


def validate(root: Path) -> list[str]:
    return Validator(root).run()


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    errors=validate(args.root)
    if errors:
        print(f"Repository validation FAILED with {len(errors)} error(s):")
        for e in errors: print(f"- {e}")
        return 1
    print("Repository validation PASSED")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
