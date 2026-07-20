# Repository Protection Requirements

This file defines the external trust boundary required for legal, licensing, conformance, third-party, and validator baselines.

Repository-local hashes and tests provide change detection only. They cannot independently prove that a simultaneous change to a protected document, its digest baseline, the validator, and its tests was authorized. Authorization therefore requires a control enforced outside the repository content.

## Required external control

Before treating a legal-baseline revision as approved, the maintainer shall use at least one of these externally verifiable modes:

1. **Signed-tag mode:** merge a verified signed commit, run all required status checks, and create the signed annotated tag named by `legal-baseline.yaml` so the tag points to the approved commit.
2. **Protected-merge mode:** configure a GitHub ruleset or protected branch that requires pull requests, required status checks, review from the applicable CODEOWNER, dismissal of stale approvals, approval of the most recent reviewable push by an authorized reviewer other than its pusher where an independent reviewer is available, blocks force pushes and deletion, and does not permit an unrecorded bypass.

For a sole-maintainer repository, signed-tag mode is the minimum practical external anchor. A repository ZIP cannot prove that the tag, signature, branch protection, ruleset, or review exists; that evidence shall be checked in GitHub or the controlled Git history.

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
