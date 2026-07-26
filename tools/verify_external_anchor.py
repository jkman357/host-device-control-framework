#!/usr/bin/env python3
"""Verify the signed-tag external anchor for the controlled legal baseline.

This verifier is commit-scoped. It reads the legal baseline and every protected
legal document from the target Git commit, verifies their digest relationship,
and then verifies that the configured signed annotated tag identifies that exact
commit. It does not attest to uncommitted working-tree content.

The tool intentionally verifies only signed-tag mode. GitHub rulesets, protected
branches, CODEOWNER approvals, platform-side bypass records, and signer
authorization policy remain external evidence.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Sequence

import yaml

CANONICAL_REPOSITORY = "jkman357/host-device-control-framework"
LEGAL_REPOSITORY_IDENTITY = {
    "host": "github.com",
    "owner": "jkman357",
    "name": "host-device-control-framework",
    "canonical_url": "https://github.com/jkman357/host-device-control-framework",
}
LEGAL_PROTECTED_DOCUMENTS = {"LICENSE", "NOTICE.md", "CONTRIBUTING.md"}


def _run_git(root: Path, args: Sequence[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "git command failed"
        raise RuntimeError(detail)
    return completed.stdout.rstrip("\n")


def normalize_github_repository(url: str) -> str | None:
    value = url.strip()
    if value.startswith("git@github.com:"):
        value = value[len("git@github.com:"):]
    elif value.startswith("ssh://git@github.com/"):
        value = value[len("ssh://git@github.com/"):]
    elif value.startswith("https://github.com/"):
        value = value[len("https://github.com/"):]
    elif value.startswith("http://github.com/"):
        value = value[len("http://github.com/"):]
    else:
        return None
    if value.endswith(".git"):
        value = value[:-4]
    value = value.strip("/")
    return value if value.count("/") == 1 else None


def _strip_html_comments(text: str) -> str:
    return re.sub(
        r"<!--.*?-->",
        lambda match: "\n" * match.group(0).count("\n"),
        text,
        flags=re.DOTALL,
    )


def _fence_ranges(lines: list[str]) -> list[bool]:
    inside = [False] * len(lines)
    active_char: str | None = None
    active_length = 0
    for index, line in enumerate(lines):
        if active_char is None:
            opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
            if opening:
                active_char = opening.group(1)[0]
                active_length = len(opening.group(1))
                inside[index] = True
        else:
            inside[index] = True
            closing = re.match(rf"^ {{0,3}}{re.escape(active_char)}{{{active_length},}}\s*$", line)
            if closing:
                active_char = None
                active_length = 0
    return inside


def _visible_sha256(text: str) -> str:
    lines = _strip_html_comments(text).splitlines()
    inside = _fence_ranges(lines)
    visible = "\n".join("" if inside[index] else line for index, line in enumerate(lines))
    normalized = " ".join(visible.split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _load_controlled_baseline(text: str) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        baseline = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return None, [f"cannot parse target legal-baseline.yaml: {exc}"]
    if not isinstance(baseline, dict):
        return None, ["target legal-baseline.yaml root is not a mapping"]

    errors: list[str] = []
    if baseline.get("repository_identity") != LEGAL_REPOSITORY_IDENTITY:
        errors.append("target legal baseline canonical repository identity is invalid")
    if baseline.get("purpose") != "legal-text-change-detection":
        errors.append("target legal baseline purpose is invalid")
    if baseline.get("local_validator_scope") != "digest-consistency-only":
        errors.append("target legal baseline local validator scope is invalid")
    if baseline.get("external_authorization_required") is not True:
        errors.append("target legal baseline must require external authorization")

    protected = baseline.get("protected_documents")
    if not isinstance(protected, dict) or set(protected) != LEGAL_PROTECTED_DOCUMENTS:
        errors.append("target legal baseline protected document set is invalid")
    else:
        for relative in sorted(LEGAL_PROTECTED_DOCUMENTS):
            entry = protected.get(relative)
            digest = entry.get("normalized_visible_sha256") if isinstance(entry, dict) else None
            if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                errors.append(f"target legal baseline digest is invalid for {relative}")

    anchor = baseline.get("external_anchor")
    if not isinstance(anchor, dict):
        errors.append("target legal baseline external_anchor record is missing")
    else:
        if anchor.get("required") is not True:
            errors.append("target legal baseline must require the external anchor")
        if anchor.get("activation_state") != "external-evidence-required":
            errors.append("repository content must not self-assert external-anchor activation")
        if anchor.get("repository_content_claims_activation") is not False:
            errors.append("repository content must not claim external-anchor activation")
        tag = anchor.get("signed_tag_name")
        if not isinstance(tag, str) or not tag.strip():
            errors.append("signed tag name is missing")

    return baseline, errors


def verify_signed_tag(root: Path, commit: str | None = None) -> list[str]:
    errors: list[str] = []
    try:
        worktree = _run_git(root, ["rev-parse", "--is-inside-work-tree"])
    except RuntimeError as exc:
        return [f"not a verifiable Git worktree: {exc}"]
    if worktree != "true":
        return ["not a verifiable Git worktree"]

    try:
        target_commit = commit or _run_git(root, ["rev-parse", "HEAD"])
        target_commit = _run_git(root, ["rev-parse", f"{target_commit}^{{commit}}"])
    except RuntimeError as exc:
        return [f"cannot resolve target commit: {exc}"]

    try:
        target_baseline_text = _run_git(root, ["show", f"{target_commit}:legal-baseline.yaml"])
    except RuntimeError as exc:
        return [f"cannot read target-commit legal-baseline.yaml: {exc}"]

    baseline, baseline_errors = _load_controlled_baseline(target_baseline_text)
    errors.extend(baseline_errors)
    if baseline is None or baseline_errors:
        return errors

    try:
        origin = _run_git(root, ["remote", "get-url", "origin"])
        normalized = normalize_github_repository(origin)
    except RuntimeError as exc:
        errors.append(f"cannot read origin remote: {exc}")
        normalized = None
    if normalized != CANONICAL_REPOSITORY:
        errors.append(f"origin remote is not canonical repository {CANONICAL_REPOSITORY}")

    protected = baseline["protected_documents"]
    for relative in sorted(LEGAL_PROTECTED_DOCUMENTS):
        try:
            target_text = _run_git(root, ["show", f"{target_commit}:{relative}"])
        except RuntimeError as exc:
            errors.append(f"cannot read target-commit protected document {relative}: {exc}")
            continue
        expected = protected[relative]["normalized_visible_sha256"]
        if _visible_sha256(target_text) != expected:
            errors.append(
                f"target-commit protected document {relative} does not match legal-baseline.yaml"
            )

    anchor = baseline["external_anchor"]
    tag = anchor["signed_tag_name"]
    try:
        tag_object_type = _run_git(root, ["cat-file", "-t", f"refs/tags/{tag}"])
        if tag_object_type != "tag":
            errors.append(f"{tag} is not an annotated tag object")
    except RuntimeError as exc:
        errors.append(f"signed tag {tag} is missing: {exc}")
        return errors

    try:
        tagged_commit = _run_git(root, ["rev-parse", f"refs/tags/{tag}^{{commit}}"])
        if tagged_commit != target_commit:
            errors.append(f"{tag} points to {tagged_commit}, not target commit {target_commit}")
    except RuntimeError as exc:
        errors.append(f"cannot resolve signed tag target: {exc}")

    try:
        _run_git(root, ["verify-tag", tag])
    except RuntimeError as exc:
        errors.append(f"tag signature verification failed: {exc}")

    try:
        tagged_baseline = _run_git(root, ["show", f"refs/tags/{tag}:legal-baseline.yaml"])
        if tagged_baseline.rstrip("\n") != target_baseline_text.rstrip("\n"):
            errors.append("tagged legal-baseline.yaml does not match target-commit baseline bytes")
    except RuntimeError as exc:
        errors.append(f"cannot compare tagged legal baseline: {exc}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--commit", help="expected commit; defaults to HEAD")
    args = parser.parse_args()
    errors = verify_signed_tag(args.repository.resolve(), args.commit)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("External legal-baseline anchor: NOT VERIFIED", file=sys.stderr)
        return 1
    print("External legal-baseline anchor for target commit: VERIFIED")
    print("Uncommitted working-tree content is outside this commit-scoped result.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
