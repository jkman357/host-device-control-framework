#!/usr/bin/env python3
"""Verify the signed-tag external anchor for the controlled legal baseline.

This tool intentionally verifies only signed-tag mode. GitHub rulesets, protected
branches, CODEOWNER approvals, and platform-side bypass records must be checked
in GitHub because a repository checkout or ZIP cannot prove those settings.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
from typing import Sequence

import yaml

CANONICAL_REPOSITORY = "jkman357/host-device-control-framework"


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
    return completed.stdout.strip()


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


def verify_signed_tag(root: Path, commit: str | None = None) -> list[str]:
    baseline_path = root / "legal-baseline.yaml"
    if not baseline_path.is_file():
        return ["legal-baseline.yaml is missing"]
    try:
        baseline = yaml.safe_load(baseline_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        return [f"cannot load legal-baseline.yaml: {exc}"]

    identity = baseline.get("repository_identity") if isinstance(baseline, dict) else None
    anchor = baseline.get("external_anchor") if isinstance(baseline, dict) else None
    if not isinstance(identity, dict) or not isinstance(anchor, dict):
        return ["legal baseline does not contain controlled repository_identity and external_anchor records"]
    if identity.get("owner") + "/" + identity.get("name") != CANONICAL_REPOSITORY:
        return ["legal baseline canonical repository identity is invalid"]
    if anchor.get("activation_state") != "external-evidence-required":
        return ["repository content must not self-assert external-anchor activation"]

    errors: list[str] = []
    try:
        worktree = _run_git(root, ["rev-parse", "--is-inside-work-tree"])
    except RuntimeError as exc:
        return [f"not a verifiable Git worktree: {exc}"]
    if worktree != "true":
        return ["not a verifiable Git worktree"]

    try:
        origin = _run_git(root, ["remote", "get-url", "origin"])
        normalized = normalize_github_repository(origin)
    except RuntimeError as exc:
        errors.append(f"cannot read origin remote: {exc}")
        normalized = None
    if normalized != CANONICAL_REPOSITORY:
        errors.append(f"origin remote is not canonical repository {CANONICAL_REPOSITORY}")

    try:
        target_commit = commit or _run_git(root, ["rev-parse", "HEAD"])
        target_commit = _run_git(root, ["rev-parse", f"{target_commit}^{{commit}}"])
    except RuntimeError as exc:
        errors.append(f"cannot resolve target commit: {exc}")
        return errors

    tag = anchor.get("signed_tag_name")
    if not isinstance(tag, str) or not tag:
        errors.append("signed tag name is missing")
        return errors

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
        current_baseline = baseline_path.read_text(encoding="utf-8").rstrip("\n")
        if tagged_baseline.rstrip("\n") != current_baseline:
            errors.append("tagged legal-baseline.yaml does not match the current controlled baseline bytes")
    except (OSError, UnicodeError, RuntimeError) as exc:
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
    print("External legal-baseline anchor: VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
