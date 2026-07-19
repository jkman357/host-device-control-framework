#!/usr/bin/env python3
"""Deterministic structural validation for the documentation repository.

Runtime requirement: Python 3.10 or later.
Validation dependency: PyYAML 6.0.3 installed with approved SHA-256 hashes.
CI validation runtimes: Python 3.10 and Python 3.12.
"""
from __future__ import annotations

import datetime as dt
import html.parser
import os
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "authority-registry.yaml"
ROOT_README = ROOT / "README.md"
AI_GUIDE = ROOT / "docs/framework/AI_Engineering_Usage_Guide.md"
WORKFLOW = ROOT / ".github/workflows/document-validation.yml"
REQUIREMENTS = ROOT / "requirements-validation.txt"

DIRECTORY_INDEX_ALLOWLIST = {
    Path("docs/framework/README.md"),
    Path("docs/protocol/README.md"),
    Path("docs/coordinator/README.md"),
    Path("docs/coding-rules/README.md"),
    Path("docs/validation/README.md"),
}
ROOT_MARKDOWN_ALLOWLIST = {Path("README.md"), Path("CHANGELOG.md"), Path("NOTICE.md")}
ALLOWED_STATUSES = {"Draft for Review", "Baseline", "Final Baseline", "Deprecated", "Retired"}
REQUIRED_METADATA = ("Document Version", "Status", "Repository Role")
IDENTITY_KEYS = ("Canonical Filename", "Document Name")
SEMVER_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
ROOT_REGISTRY_KEYS = {"registry_version", "repository", "source_of_truth", "policy", "documents"}
POLICY_KEYS = {"routing_order", "conflict_resolution", "draft_effect"}
ENTRY_KEYS = {
    "display_name", "path", "version", "status", "repository_role", "readme_purpose",
    "routing_role", "applies_when", "authority_topics", "prerequisite_documents",
}
EXPECTED_REQUIREMENTS = """PyYAML==6.0.3 \\
    --hash=sha256:d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f \\
    --hash=sha256:9c7708761fccb9397fe64bbc0395abcae8c4bf7b0eac081e12b809bf47700d0b \\
    --hash=sha256:ba1cc08a7ccde2d2ec775841541641e4548226580ab850948cbfda66a1befcdc
"""
ERRORS: list[str] = []


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def error(message: str) -> None:
    ERRORS.append(message)


def read_text(path: Path) -> str:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        error(f"{rel(path)}: cannot read file: {exc}")
        return ""
    if raw.startswith(b"\xef\xbb\xbf"):
        error(f"{rel(path)}: UTF-8 BOM is not allowed")
    if b"\x00" in raw:
        error(f"{rel(path)}: NUL byte is not allowed")
    if b"\r" in raw:
        error(f"{rel(path)}: CR or CRLF line endings are not allowed")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        error(f"{rel(path)}: invalid UTF-8: {exc}")
        return ""
    if text and not text.endswith("\n"):
        error(f"{rel(path)}: text file must end with a newline")
    return text


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark,
                f"found duplicate key {key!r}", key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def load_yaml_strict(path: Path) -> object | None:
    text = read_text(path)
    # Registry/workflow files intentionally forbid YAML indirection and custom tags.
    for token_type, plural_label in ((yaml.tokens.AnchorToken, "anchors"), (yaml.tokens.AliasToken, "aliases"), (yaml.tokens.TagToken, "tags")):
        try:
            if any(isinstance(token, token_type) for token in yaml.scan(text)):
                error(f"{rel(path)}: YAML {plural_label} are not allowed")
        except yaml.YAMLError as exc:
            error(f"{rel(path)}: YAML tokenization failed: {exc}")
            return None
    if re.search(r"(?m)^\s*<<\s*:", text):
        error(f"{rel(path)}: YAML merge keys are not allowed")
    try:
        return yaml.load(text, Loader=UniqueKeyLoader)
    except yaml.YAMLError as exc:
        error(f"{rel(path)}: invalid YAML: {exc}")
        return None


def blank_preserving_newlines(value: str) -> str:
    return "".join("\n" if c == "\n" else " " for c in value)


def fence_free_text(path: Path, text: str) -> str:
    out: list[str] = []
    opening: tuple[str, int, int] | None = None
    fence_re = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
    for line_no, line in enumerate(text.splitlines(), 1):
        match = fence_re.match(line)
        if opening is None:
            if match:
                marker = match.group(1)
                opening = (marker[0], len(marker), line_no)
                out.append("")
            else:
                out.append(line)
            continue
        marker_char, marker_len, _ = opening
        if match:
            marker = match.group(1)
            if marker[0] == marker_char and len(marker) >= marker_len and not match.group(2).strip():
                opening = None
        out.append("")
    if opening is not None:
        c, n, line_no = opening
        error(f"{rel(path)}:{line_no}: unclosed fenced Code block opened with {c*n}")
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def html_code_free_text(path: Path, text: str) -> str:
    result = re.sub(r"<!--.*?-->", lambda m: blank_preserving_newlines(m.group(0)), text, flags=re.S)
    complete = re.compile(r"<(?P<tag>pre|code|script|style)\b[^>]*>.*?</(?P=tag)\s*>", re.I | re.S)
    while True:
        result, count = complete.subn(lambda m: blank_preserving_newlines(m.group(0)), result)
        if not count:
            break
    opening = re.search(r"<(pre|code|script|style)\b[^>]*>", result, re.I)
    if opening:
        line_no = result.count("\n", 0, opening.start()) + 1
        error(f"{rel(path)}:{line_no}: unclosed HTML code/example block <{opening.group(1).lower()}>")
        result = result[:opening.start()] + blank_preserving_newlines(result[opening.start():])
    return result


def searchable(path: Path, text: str) -> str:
    return html_code_free_text(path, fence_free_text(path, text))


def strip_markup(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        value = value[1:-1]
    return value.strip()


def parse_metadata(path: Path, text: str) -> dict[str, str]:
    lines = text.splitlines()
    first_h2 = next((i for i, line in enumerate(lines) if re.match(r"^ {0,3}##\s+", line)), len(lines))
    region = "\n".join(lines[:min(first_h2, 80)])
    metadata: dict[str, str] = {}
    for key in (*IDENTITY_KEYS, *REQUIRED_METADATA, "Supersedes Document Version"):
        matches = re.findall(rf"(?m)^\*\*{re.escape(key)}:\*\*\s*(.*?)\s*$", region)
        if len(matches) > 1:
            error(f"{rel(path)}: metadata {key!r} must appear at most once in the opening metadata region")
        if matches:
            metadata[key] = strip_markup(matches[0])
    identities = [key for key in IDENTITY_KEYS if key in metadata]
    if len(identities) != 1:
        error(f"{rel(path)}: exactly one of Canonical Filename or Document Name is required")
    else:
        if metadata[identities[0]] != path.name:
            error(f"{rel(path)}: declared filename {metadata[identities[0]]!r} does not match {path.name!r}")
    for key in REQUIRED_METADATA:
        if key not in metadata:
            error(f"{rel(path)}: missing required metadata: {key}")
    version = metadata.get("Document Version", "")
    if version and not SEMVER_RE.fullmatch(version):
        error(f"{rel(path)}: Document Version {version!r} must match vMAJOR.MINOR.PATCH")
    status = metadata.get("Status", "")
    if status and status not in ALLOWED_STATUSES:
        error(f"{rel(path)}: Status {status!r} is not controlled")
    role = metadata.get("Repository Role", "")
    if status == "Draft for Review" and role and not role.startswith("Proposed "):
        error(f"{rel(path)}: Draft for Review Repository Role must begin with 'Proposed '")
    if status in {"Baseline", "Final Baseline"} and role:
        low = role.lower()
        if "normative" not in low or "proposed" in low:
            error(f"{rel(path)}: Baseline Repository Role must use non-proposed normative wording")
    return metadata


def parse_semver(value: str) -> tuple[int, int, int] | None:
    m = SEMVER_RE.fullmatch(value)
    return tuple(map(int, m.groups())) if m else None


def markdown_rows(lines: list[str], start: int) -> tuple[list[str], list[list[str]]]:
    while start < len(lines) and not lines[start].lstrip().startswith("|"):
        if lines[start].startswith("#"):
            return [], []
        start += 1
    if start >= len(lines):
        return [], []
    def cells(line: str) -> list[str]: return [c.strip() for c in line.strip().strip("|").split("|")]
    header = cells(lines[start])
    if start + 1 >= len(lines) or not re.match(r"^\s*\|?\s*:?-+", lines[start+1]):
        return [], []
    rows=[]
    i=start+2
    while i < len(lines) and lines[i].lstrip().startswith("|"):
        rows.append(cells(lines[i])); i+=1
    return header, rows


def validate_version_history(path: Path, text: str, md: dict[str, str]) -> None:
    headings = [(i, line) for i, line in enumerate(text.splitlines()) if re.match(r"^ {0,3}#{2,6}(?:\s+(?:Appendix\s+[A-Z]\.|\d+(?:\.\d+)*))?\s+(?:Version History|Change History)\s*$", line, re.I)]
    if len(headings) != 1:
        error(f"{rel(path)}: exactly one Version History or Change History heading is required; found {len(headings)}")
        return
    lines=text.splitlines(); header, rows=markdown_rows(lines, headings[0][0]+1)
    normalized=[h.strip().lower() for h in header]
    aliases={"version":"version","date":"date","status":"status","summary":"summary","description":"summary"}
    required={"version","date","status","summary"}
    present={aliases[h] for h in normalized if h in aliases}
    missing=required-present
    if missing:
        error(f"{rel(path)}: Version History missing required columns: {', '.join(sorted(missing))}")
        return
    idx={aliases[h]:i for i,h in enumerate(normalized) if h in aliases}
    versions=[]; dates=[]
    current=md.get("Document Version",""); status=md.get("Status","")
    for row in rows:
        if len(row)!=len(header):
            error(f"{rel(path)}: Version History row has {len(row)} cells; expected {len(header)}")
            continue
        v=row[idx['version']]; sv=parse_semver(v)
        if sv is None:
            error(f"{rel(path)}: Version History value {v!r} must match vMAJOR.MINOR.PATCH"); continue
        versions.append((v,sv))
        date=row[idx['date']]
        parsed_date=None
        if date != "Not recorded":
            try: parsed_date=dt.date.fromisoformat(date)
            except ValueError: pass
        if v==current and parsed_date is None:
            error(f"{rel(path)}: current Version History date must be a real ISO YYYY-MM-DD date")
        elif date!="Not recorded" and parsed_date is None:
            error(f"{rel(path)}: Version History date {date!r} must be a real ISO date or 'Not recorded'")
        if parsed_date: dates.append(parsed_date)
        row_status=row[idx['status']]
        if v==current and row_status!=status:
            error(f"{rel(path)}: Version History status for {v} is {row_status!r}; metadata status is {status!r}")
        elif row_status!="Not recorded" and row_status not in ALLOWED_STATUSES:
            error(f"{rel(path)}: historical Version History status {row_status!r} must use the controlled enum or 'Not recorded'")
        if not row[idx['summary']].strip():
            error(f"{rel(path)}: Version History summary/description must not be empty")
    names=[v for v,_ in versions]
    if len(names)!=len(set(names)): error(f"{rel(path)}: Version History contains duplicate versions")
    semvers=[v for _,v in versions]
    asc=semvers==sorted(semvers); desc=semvers==sorted(semvers,reverse=True)
    if len(semvers)>1 and not (asc or desc): error(f"{rel(path)}: Version History versions must be monotonic")
    if current and names.count(current)!=1: error(f"{rel(path)}: current version {current} must appear exactly once in Version History table")
    current_sv=parse_semver(current)
    if current_sv and semvers and current_sv!=max(semvers):
        highest='v'+'.'.join(map(str,max(semvers)))
        error(f"{rel(path)}: current version {current} must be the highest Version History version ({highest})")
    supersedes=md.get("Supersedes Document Version")
    if len(names)<=1:
        if supersedes is not None: error(f"{rel(path)}: Supersedes Document Version must be absent for an initial version")
    else:
        if supersedes is None:
            error(f"{rel(path)}: Supersedes Document Version is required when Version History has multiple entries")
        elif parse_semver(supersedes) is None:
            error(f"{rel(path)}: Supersedes Document Version {supersedes!r} must match vMAJOR.MINOR.PATCH")
        elif current_sv:
            prior=max((sv for sv in semvers if sv<current_sv), default=None)
            expected='v'+'.'.join(map(str,prior)) if prior else None
            if supersedes!=expected:
                error(f"{rel(path)}: Supersedes Document Version {supersedes!r} must identify immediate prior version {expected!r}")


def governed_documents() -> list[Path]:
    return sorted(p for p in (ROOT/"docs").rglob("*.md") if p.relative_to(ROOT) not in DIRECTORY_INDEX_ALLOWLIST)


def validate_paths() -> None:
    casefold: dict[str,str]={}
    windows_reserved={"con","prn","aux","nul",*(f"com{i}" for i in range(1,10)),*(f"lpt{i}" for i in range(1,10))}
    for path in sorted(ROOT.rglob("*")):
        if any(part in {".git","__pycache__"} for part in path.parts): continue
        rp=path.relative_to(ROOT)
        if path.is_symlink(): error(f"{rp.as_posix()}: symbolic links are not allowed")
        text=rp.as_posix()
        if unicodedata.normalize("NFC",text)!=text: error(f"{text}: path must use Unicode NFC")
        key=text.casefold()
        if key in casefold and casefold[key]!=text: error(f"{text}: case-collides with {casefold[key]}")
        casefold[key]=text
        for part in rp.parts:
            base=part.rstrip(" .").split(".",1)[0].casefold()
            if part!=part.rstrip(" .") or base in windows_reserved:
                error(f"{text}: non-portable Windows path component {part!r}")
        if path.is_file() and path.suffix.lower()==".md" and path.suffix!=".md":
            error(f"{text}: Markdown extension must be lowercase .md")
    root_md={p.relative_to(ROOT) for p in ROOT.glob("*.md")}
    unexpected=root_md-ROOT_MARKDOWN_ALLOWLIST
    if unexpected: error(f"root Markdown files are not allowlisted: {', '.join(sorted(p.as_posix() for p in unexpected))}")


def validate_registry(metadata: dict[Path,dict[str,str]]) -> list[dict]:
    obj=load_yaml_strict(REGISTRY)
    if not isinstance(obj,dict): error("authority-registry.yaml: root must be a mapping"); return []
    keys=set(obj)
    if keys!=ROOT_REGISTRY_KEYS:
        missing=ROOT_REGISTRY_KEYS-keys; extra=keys-ROOT_REGISTRY_KEYS
        if missing: error(f"authority-registry.yaml: missing root fields: {', '.join(sorted(missing))}")
        if extra: error(f"authority-registry.yaml: unexpected root fields: {', '.join(sorted(extra))}")
    if obj.get("registry_version")!=1: error("authority-registry.yaml: registry_version must be 1")
    if obj.get("repository")!="host-device-control-framework": error("authority-registry.yaml: repository must be host-device-control-framework")
    if obj.get("source_of_truth")!="GitHub main": error("authority-registry.yaml: source_of_truth must be 'GitHub main'")
    policy=obj.get("policy")
    if not isinstance(policy,dict) or set(policy)!=POLICY_KEYS: error("authority-registry.yaml: policy must contain the exact controlled fields")
    docs=obj.get("documents")
    if not isinstance(docs,list): error("authority-registry.yaml: documents must be a list"); return []
    paths=[]; topics=[]
    governed={rel(p) for p in metadata}
    for i,entry in enumerate(docs):
        label=f"authority-registry.yaml documents[{i}]"
        if not isinstance(entry,dict): error(f"{label}: entry must be a mapping"); continue
        if set(entry)!=ENTRY_KEYS:
            missing=ENTRY_KEYS-set(entry); extra=set(entry)-ENTRY_KEYS
            if missing: error(f"{label}: missing fields: {', '.join(sorted(missing))}")
            if extra: error(f"{label}: unexpected fields: {', '.join(sorted(extra))}")
        path=entry.get("path")
        if not isinstance(path,str): error(f"{label}: path must be a string"); continue
        paths.append(path)
        p=ROOT/path
        if path not in governed: error(f"{label}: path is not a governed document: {path}")
        md=metadata.get(p,{})
        for field,key in (("version","Document Version"),("status","Status"),("repository_role","Repository Role")):
            if entry.get(field)!=md.get(key): error(f"authority-registry.yaml {field} mismatch for {Path(path).name}")
        for field in ("display_name","readme_purpose","routing_role","applies_when"):
            if not isinstance(entry.get(field),str) or not entry[field].strip(): error(f"{label}: {field} must be non-empty text")
        ats=entry.get("authority_topics")
        if not isinstance(ats,list) or not ats or any(not isinstance(x,str) or not x.strip() for x in ats): error(f"{label}: authority_topics must be a non-empty list of text")
        else: topics.extend(x.casefold() for x in ats)
        prereq=entry.get("prerequisite_documents")
        if not isinstance(prereq,list) or any(not isinstance(x,str) for x in prereq): error(f"{label}: prerequisite_documents must be a list of paths")
    if len(paths)!=len(set(paths)): error("authority-registry.yaml: duplicate document paths")
    expected=[rel(p) for p in metadata]
    if set(paths)!=set(expected):
        missing=set(expected)-set(paths); extra=set(paths)-set(expected)
        if missing: error(f"authority-registry.yaml: missing governed documents: {', '.join(sorted(missing))}")
        if extra: error(f"authority-registry.yaml: unexpected governed documents: {', '.join(sorted(extra))}")
    dup_topics=[t for t,c in Counter(topics).items() if c>1]
    if dup_topics: error(f"authority-registry.yaml: authority topics must be unique: {', '.join(sorted(dup_topics))}")
    known=set(paths); graph={e.get('path'):e.get('prerequisite_documents',[]) for e in docs if isinstance(e,dict) and isinstance(e.get('path'),str)}
    for source, prereqs in graph.items():
        for target in prereqs:
            if target not in known: error(f"authority-registry.yaml: unknown prerequisite {target!r} for {source}")
            if target==source: error(f"authority-registry.yaml: document cannot depend on itself: {source}")
    visiting=set(); visited=set()
    def visit(node,stack):
        if node in visiting:
            cycle=stack[stack.index(node):]+[node]
            error("authority-registry.yaml: prerequisite cycle detected: "+" -> ".join(cycle)); return
        if node in visited: return
        visiting.add(node); stack.append(node)
        for nxt in graph.get(node,[]): visit(nxt,stack)
        stack.pop(); visiting.remove(node); visited.add(node)
    for node in graph: visit(node,[])
    return docs


def parse_current_set(path: Path, heading_pattern: str) -> tuple[list[str],list[list[str]]]:
    text=searchable(path,read_text(path)); lines=text.splitlines()
    matches=[i for i,l in enumerate(lines) if re.fullmatch(heading_pattern,l.strip(),re.I)]
    if len(matches)!=1:
        error(f"{rel(path)}: expected exactly one controlled manifest heading; found {len(matches)}")
        return [],[]
    return markdown_rows(lines,matches[0]+1)


def compare_human_tables(registry_docs: list[dict]) -> None:
    header,rows=parse_current_set(ROOT_README,r"## Current Document Set")
    if header:
        if [h.lower() for h in header]!=["document","version","status","purpose"]: error("README.md: Current Document Set columns are invalid")
        parsed=[]
        for row in rows:
            if len(row)!=4: error("README.md: Current Document Set row has wrong cell count"); continue
            m=re.search(r"\]\(([^)]+)\)",row[0]);
            if not m: error("README.md: Current Document Set Document cell must contain a Markdown link"); continue
            parsed.append((m.group(1),row[1],row[2],row[3]))
        expected=[(d['path'],d['version'],d['status'],d['readme_purpose']) for d in registry_docs]
        if parsed!=expected: error("README.md: Current Document Set does not exactly match authority-registry.yaml order and fields")
    header,rows=parse_current_set(AI_GUIDE,r"## 0\.2 Active Document Manifest")
    if header:
        if [h.lower() for h in header]!=["document","canonical repository path","active version","status","routing role"]: error("AI Engineering Usage Guide: Active Document Manifest columns are invalid")
        parsed=[]
        for row in rows:
            if len(row)!=5: error("AI Engineering Usage Guide: manifest row has wrong cell count"); continue
            parsed.append((strip_markup(row[1]),strip_markup(row[2]),row[3],row[4]))
        expected=[(d['path'],d['version'],d['status'],d['routing_role']) for d in registry_docs]
        if parsed!=expected: error("AI Engineering Usage Guide: Active Document Manifest does not exactly match authority-registry.yaml order and fields")


class HTMLTargets(html.parser.HTMLParser):
    def __init__(self): super().__init__(); self.targets=[]; self.anchors=set()
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if not v: continue
            if k.lower() in {"id","name"}: self.anchors.add(v)
            if (tag.lower()=="a" and k.lower()=="href") or (tag.lower()=="img" and k.lower()=="src"): self.targets.append(v)


def slugify(value: str) -> str:
    value=re.sub(r"<[^>]+>","",value)
    value=re.sub(r"(`+)(.*?)\1",r"\2",value)
    value=unicodedata.normalize("NFKD",value).casefold()
    value=re.sub(r"[^\w\- ]","",value,flags=re.UNICODE)
    return re.sub(r"[-\s]+","-",value).strip("-")


def anchors_for(text: str) -> set[str]:
    result=set(); counts=Counter()
    lines=text.splitlines()
    for i,line in enumerate(lines):
        title=None
        m=re.match(r"^ {0,3}#{1,6}\s+(.+?)(?:\s+#+)?$",line)
        if m: title=m.group(1)
        elif i+1<len(lines) and re.match(r"^ {0,3}(=+|-+)\s*$",lines[i+1]) and line.strip(): title=line.strip()
        if title:
            base=slugify(title); n=counts[base]; counts[base]+=1
            result.add(base if n==0 else f"{base}-{n}")
    return result


def inline_targets(text: str) -> list[str]:
    targets=[]; i=0
    while True:
        marker=text.find("](",i)
        if marker<0: break
        cur=marker+2; depth=1; esc=False; end=cur
        while end<len(text):
            ch=text[end]
            if esc: esc=False
            elif ch=="\\": esc=True
            elif ch=="(": depth+=1
            elif ch==")":
                depth-=1
                if depth==0: targets.append(text[cur:end]); end+=1; break
            end+=1
        i=max(end,marker+2)
    targets += re.findall(r"(?m)^\s*\[[^\]]+\]:\s*(\S+)",text)
    return targets


def validate_links(markdown_files: list[Path]) -> None:
    cleaned={}; anchors={}
    for p in markdown_files:
        t=searchable(p,read_text(p)); cleaned[p]=t; anchors[p]=anchors_for(t)
        parser=HTMLTargets();
        try: parser.feed(t)
        except Exception as exc: error(f"{rel(p)}: HTML parsing failed: {exc}")
        anchors[p]|=parser.anchors
    for p,t in cleaned.items():
        parser=HTMLTargets(); parser.feed(t)
        for raw in inline_targets(t)+parser.targets:
            target=raw.strip()
            if target.startswith("<") and ">" in target: target=target[1:target.index(">")]
            else: target=target.split(maxsplit=1)[0]
            if not target: continue
            parsed=urlsplit(target)
            if parsed.scheme or target.startswith("//"): continue
            path_part=unquote(parsed.path); fragment=unquote(parsed.fragment)
            resolved=p if not path_part else (p.parent/path_part).resolve()
            try: resolved.relative_to(ROOT.resolve())
            except ValueError: error(f"{rel(p)}: link escapes repository: {target}"); continue
            if not resolved.exists(): error(f"{rel(p)}: missing link or image target: {path_part or target}"); continue
            if fragment and resolved.is_file() and resolved.suffix==".md" and fragment not in anchors.get(resolved,set()):
                error(f"{rel(p)}: missing heading anchor in {rel(resolved)}: #{fragment}")


def validate_workflow() -> None:
    obj=load_yaml_strict(WORKFLOW)
    if not isinstance(obj,dict): return
    jobs=obj.get("jobs");
    if not isinstance(jobs,dict) or set(jobs)!={"validate-documentation"}: error("workflow: expected exactly validate-documentation job"); return
    job=jobs["validate-documentation"]
    if job.get("runs-on")!="ubuntu-24.04": error("workflow: runs-on must be ubuntu-24.04")
    matrix=((job.get("strategy") or {}).get("matrix") or {}).get("python-version")
    if matrix!=["3.10","3.12"]: error("workflow: Python matrix must be exactly 3.10 and 3.12")
    steps=job.get("steps")
    if not isinstance(steps,list): error("workflow: steps must be a list"); return
    uses=[s.get('uses','') for s in steps if isinstance(s,dict)]
    if "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0" not in uses: error("workflow: checkout action must use approved immutable SHA")
    if "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1" not in uses: error("workflow: setup-python action must use approved immutable SHA")
    runs=[s.get('run') for s in steps if isinstance(s,dict) and isinstance(s.get('run'),str)]
    expected=[
        "python -m pip install --disable-pip-version-check --require-hashes -r requirements-validation.txt",
        "python tools/validate_repository.py",
        "python -m unittest discover -s tests -v",
    ]
    for cmd in expected:
        if runs.count(cmd)!=1: error(f"workflow: required exact unconditional run step missing or duplicated: {cmd}")
    if any("\n" in r or "&&" in r or ";" in r for r in runs): error("workflow: validation commands must remain separate exact steps")


def main() -> int:
    if sys.version_info < (3,10): error("Python 3.10 or later is required")
    validate_paths()
    if not REGISTRY.exists(): error("authority-registry.yaml: missing")
    if not REQUIREMENTS.exists(): error("requirements-validation.txt: missing")
    elif read_text(REQUIREMENTS)!=EXPECTED_REQUIREMENTS: error("requirements-validation.txt: pinned dependency or approved hashes differ")
    metadata={}
    docs=governed_documents()
    for p in docs:
        t=searchable(p,read_text(p)); md=parse_metadata(p,t); metadata[p]=md; validate_version_history(p,t,md)
    registry_docs=validate_registry(metadata)
    compare_human_tables(registry_docs)
    validate_workflow()
    if os.environ.get("HDCF_VALIDATOR_FAST_TEST") != "1":
        markdown_files=sorted(ROOT.rglob("*.md"))
        validate_links(markdown_files)
    if ERRORS:
        for msg in dict.fromkeys(ERRORS): print(f"ERROR: {msg}")
        print(f"Repository validation: FAIL ({len(dict.fromkeys(ERRORS))} error(s))")
        return 1
    print("Repository validation: PASS")
    print(f"Governed documents: {len(docs)}")
    print(f"Registry documents: {len(registry_docs)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
