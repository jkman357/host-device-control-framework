# Repository Validation Checklist

**Canonical Filename:** `Repository_Validation_Checklist.md`  
**Document Version:** v1.0.0  
**Status:** Draft for Review  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-18  
**Language:** English  
**Repository Role:** Proposed operational validation method; not a Product or architecture authority  

---

## Version History

| Version | Date | Status | Summary |
|---|---|---|---|
| v1.0.0 | 2026-07-18 | Draft for Review | Established automated and human repository checks for canonical paths, document manifests, version and status consistency, links, Markdown structure, evidence claims, role routing, Draft authority handling, and detached-package traceability. |

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

Run:

```bash
python tools/validate_repository.py
```

The automated validator shall check at least:

- UTF-8 readability and final newline.
- Balanced fenced Code blocks.
- Existing relative Markdown targets.
- Unique canonical filenames.
- Document metadata version and status.
- Current version presence in Version History.
- Root Current Document Set version/status consistency.
- AI Active Document Manifest version/status consistency.
- Draft documents that claim normative authority use `Proposed` wording.
- Required canonical authority paths exist.
- Repository-validation workflow and script exist.

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
