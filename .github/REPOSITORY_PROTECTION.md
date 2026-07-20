# Repository Protection Requirements

This file defines the external trust boundary required for legal, licensing, conformance, third-party, and validator baselines.

Repository-local hashes and tests provide change detection only. They cannot independently prove that a simultaneous change to a protected document, its digest baseline, the validator, and its tests was authorized. Authorization therefore requires a control enforced outside the repository content.

## Required external control

Before treating a legal-baseline revision as approved, the maintainer shall use at least one of these externally verifiable modes:

1. **Signed-tag mode:** merge a verified signed commit, run all required status checks, and create the signed annotated tag named by `legal-baseline.yaml` so the tag points to the approved commit.
2. **Protected-merge mode:** configure a GitHub ruleset or protected branch that requires pull requests, required status checks, review from the applicable CODEOWNER, dismissal of stale approvals, approval of the most recent reviewable push by an authorized reviewer other than its pusher where an independent reviewer is available, blocks force pushes and deletion, and does not permit an unrecorded bypass.

For a sole-maintainer repository, signed-tag mode is the minimum practical external anchor. The repository records the state `external-evidence-required` and never self-asserts that the anchor is active. A repository ZIP cannot prove that the tag, signature, branch protection, ruleset, or review exists; that evidence shall be checked in GitHub or the controlled Git history.

## Protected content

The following shall be covered by `.github/CODEOWNERS` and by the selected external control:

- `LICENSE`
- `NOTICE.md`
- `CONTRIBUTING.md`
- `legal-baseline.yaml`
- `third-party-materials.yaml`
- `.github/CODEOWNERS`
- this protection document
- the repository validator and its regression tests
- Framework conformance governance and claim schema files

## Baseline-change record

A legal-baseline change shall increment `baseline_version`, update the protected-document digests, explain the legal effect in `CHANGELOG.md`, pass all tests, and identify the external signed tag or protected-merge evidence. Updating a digest in the same commit is not, by itself, approval of the changed legal meaning.

## External-anchor verification

For signed-tag mode, run the controlled verifier after creating the signed annotated tag:

```bash
python tools/verify_external_anchor.py --commit "$(git rev-parse HEAD)"
```

The verifier requires the canonical `origin` repository identity, an annotated tag, a valid tag signature, an exact tag-to-commit match, and identical `legal-baseline.yaml` bytes at the tagged commit. It does not verify GitHub rulesets or protected-merge evidence.

## Repository release freeze

Repository content becomes an immutable release freeze only when the final commit is identified by the intended signed release tag or GitHub Release. A ZIP, branch name, working tree, or mutable `main` state is not freeze evidence. After the `v1.0.0` freeze tag is created, normative or governance changes require a later repository version and shall not rewrite the frozen tag.
