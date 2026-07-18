# Repository Validation Checklist

**Canonical Filename:** `Repository_Validation_Checklist.md`  
**Document Version:** v1.0.2  
**Status:** Draft for Review  
**Supersedes Document Version:** v1.0.1  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-18  
**Language:** English  
**Repository Role:** Proposed operational validation method; not a Product or architecture authority  

---

## Version History

| Version | Date | Status | Summary |
|---|---|---|---|
| v1.0.0 | 2026-07-18 | Draft for Review | Established automated and human repository checks for canonical paths, document manifests, version and status consistency, links, Markdown structure, evidence claims, role routing, Draft authority handling, and detached-package traceability. |
| v1.0.1 | 2026-07-18 | Draft for Review | Completed repository-validation enforcement by requiring the GitHub Actions workflow, exact authority-manifest set equality, marker-aware fenced-Code parsing, inline/image/reference-link and Markdown-anchor validation, Version History table-scoped checks, explicit Python runtime requirements, and Authority Boundary coverage for Coordinator and C# rule documents. |
| v1.0.2 | 2026-07-18 | Draft for Review | Updated GitHub Actions to checkout v7 and setup-python v6; added Python 3.10 and 3.12 CI matrix validation; required complete metadata for every non-README Markdown document under docs; added semantic-version, current-version, ordering, and declared Supersedes-chain checks; and added automated validator regression tests. |

---

# 1. Purpose

This checklist defines repository-level validation for the engineering authority set. It separates deterministic
structural checks from semantic review and human approval.

# 2. Evidence States

Each check shall be recorded as one of:

```text
Not Run
Tool-Executed Pass
Tool-Executed Fail
Human-Reviewed Pass
Human-Reviewed Fail
Not Applicable with rationale
```

A tool result shall not be relabeled as human approval or Product validation.

# 3. Automated Structural Checks

## 3.1 Runtime

Local execution requires Python 3.10 or later. The repository CI workflow shall validate both Python 3.10 and Python 3.12.

Run:

```bash
python tools/validate_repository.py
python -m unittest discover -s tests -v
```

## 3.2 Required Automated Checks

The automated validator shall check at least:

- UTF-8 readability and final newline.
- Fenced Code blocks using marker-aware matching: closing markers shall use the same character and at least the opening-marker length.
- Existing local targets for inline Markdown links, images, and reference-style links.
- Existing Markdown heading anchors for local links that contain fragments.
- Defined and non-duplicated reference-link identifiers.
- Unique canonical filenames.
- Complete canonical filename, document version, and status metadata for every non-README Markdown document under `docs/`; omission of all metadata shall not bypass governance.
- Document versions use `vMAJOR.MINOR.PATCH`, Version History versions are unique and monotonic, and the metadata version is the highest listed version.
- Current version presence exactly once in the Version History or Change History table located under the corresponding heading.
- When `Supersedes Document Version` is declared, it uses `vMAJOR.MINOR.PATCH`, exists in Version History, is lower than the current version, and identifies the immediate prior listed version.
- Version History status and date consistency when those columns are present.
- Exact set equality between versioned authority documents and the root Current Document Set.
- Exact set equality between versioned authority documents and the AI Active Document Manifest.
- Manifest path, version, and status consistency.
- Draft documents that claim normative authority use `Proposed` wording.
- Required canonical authority paths exist.
- Repository-validation workflow and script exist.
- The GitHub Actions workflow uses `actions/checkout@v7`, `actions/setup-python@v6`, validates Python 3.10 and 3.12, invokes `python tools/validate_repository.py`, and runs the validator regression tests.
- Validator regression tests retain expected failures for metadata omission, invalid or stale versions, broken Supersedes chains, obsolete Action versions, and incomplete Python matrices.

A passing automated result proves only the checks implemented by the validator. It does not prove semantic correctness, Product suitability, or human approval.

# 4. Human Semantic Checks

A reviewer shall verify:

- Authority ownership is resolved by topic before precedence.
- Implementation routing identifies role before language.
- Embedded C is not assumed to be Node and non-C is not assumed to be Coordinator.
- Draft authorities are not silently promoted by Baseline documents.
- Repeated upstream rules are labeled as derived summaries or translated into clearly scoped implementation realization.
- Protocol wire definitions remain owned by the Project Protocol authority.
- Security, safety, and Product decisions remain owned by their approved authorities.
- Validation claims do not exceed retained evidence.
- LICENSE and README usage language are consistent with the intended publication model.

# 5. Detached Package Checks

A controlled detached package shall identify:

- Package ID and package status.
- Input source branch and commit, tag, or Release.
- Generation date.
- Canonical document versions and statuses.
- Files included in the package.
- SHA-256 or stronger hashes for distributed files.
- Whether the package contains uncommitted proposed changes.

Package metadata is distribution evidence. It does not promote any Draft document or approve the package for Product use.

# 6. Completion Record

```text
Source identity:
Validator command:
Validator result:
Human reviewer:
Human review result:
Open findings:
Package identity, if applicable:
Approval decision:
```
