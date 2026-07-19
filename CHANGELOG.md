# Changelog

All notable repository-level changes are documented in this file.

Individual authority documents retain their own internal Version History and approval status.

## Unreleased

### Added

- Added `authority-registry.yaml` as the machine-readable source for authority identity, role, applicability, topics, prerequisites, README purpose, and AI routing-role metadata.
- Added SHA-256 hashes for the PyYAML source distribution and the Python 3.10/3.12 Linux x86-64 CI wheels.
- Added categorized documentation directories for Framework, Protocol, Coordinator, Coding Rules, and Validation.
- Added directory-level `README.md` files to define each documentation domain and its authority boundary.
- Added `CHANGELOG.md`, `LICENSE`, and `NOTICE.md` at the repository root.
- Added `Coordinator_Software_Engineering_Rules.md` v1.0.1.
- Added `CSharp_Coding_Rules.md` v1.0.1.
- Added `Repository_Validation_Checklist.md` v1.0.0.
- Added `tools/validate_repository.py` and `.github/workflows/document-validation.yml`.
- Added `tests/test_validate_repository.py` with end-to-end validator regression and mutation tests.

- Added `requirements-validation.txt` with the pinned PyYAML validation dependency.

### Changed

- Hardened governed-document metadata with Status enums, mandatory Repository Role, compatible Status/Role combinations, and placement before the first level-2 heading.
- Excluded fenced and HTML `pre`/`code`/`script`/`style` examples from metadata, manifest, Version History, link, and anchor parsing.
- Required exact, separate, unconditional Workflow steps and hash-verified dependency installation.
- Required unique Current Document Set and Active Document Manifest headings and validated their descriptive fields against the authority registry.
- Migrated governed Version History tables to Date/Status schemas, retained `Not recorded` for unavailable legacy facts, and added complete row, real-date, status, and ordering checks.
- Updated AI Engineering Usage Guide to v1.0.15, Coordinator/Node Control Framework to v1.0.13, Framework Application Analysis Template to v1.0.16, Protocol YAML Definition Guide and Template to v1.0.10, Embedded C Coding Rules to v1.0.17, and Repository Validation Checklist to v1.0.4.
- Reorganized Framework and application-analysis documents under `docs/framework/`.
- Reorganized Protocol documents under `docs/protocol/`.
- Reorganized Coordinator software engineering rules under `docs/coordinator/`.
- Reorganized language-specific coding rules under `docs/coding-rules/`.
- Updated root navigation, document links, AI task routing, canonical path examples, and repository structure.
- Split the former repository-level `COPYRIGHT.md` responsibilities between `LICENSE` and `NOTICE.md`.
- Updated `AI_Engineering_Usage_Guide.md` to v1.0.9.
- Updated `Coordinator_Node_Control_Framework.md` to v1.0.9.
- Updated `Coordinator_Node_Control_Framework.md` to v1.0.10.
- Updated `Framework_Application_Analysis_Template.md` to v1.0.11.
- Updated `AI_Engineering_Usage_Guide.md` to v1.0.10.
- Updated `Framework_Application_Analysis_Template.md` to v1.0.12.
- Updated `Coordinator_Software_Engineering_Rules.md` to v1.0.2.
- Updated `CSharp_Coding_Rules.md` to v1.0.2.
- Updated `AI_Engineering_Usage_Guide.md` to v1.0.11.
- Updated `Coordinator_Node_Control_Framework.md` to v1.0.11.
- Updated `Framework_Application_Analysis_Template.md` to v1.0.13.
- Updated `Coordinator_Software_Engineering_Rules.md` to v1.0.3.
- Updated `CSharp_Coding_Rules.md` to v1.0.3.
- Updated `AI_Engineering_Usage_Guide.md` to v1.0.12.
- Updated `Framework_Application_Analysis_Template.md` to v1.0.14.
- Updated `Repository_Validation_Checklist.md` to v1.0.1.
- Updated `AI_Engineering_Usage_Guide.md` to v1.0.13.
- Updated `Repository_Validation_Checklist.md` to v1.0.2.
- Updated Coordinator, Coding Rules, and Validation directory guidance.

- Updated all governed authority documents with explicit immediate-prior `Supersedes Document Version` metadata and corresponding version-history entries.
- Updated `AI_Engineering_Usage_Guide.md` to v1.0.14.
- Updated `Coordinator_Node_Control_Framework.md` to v1.0.12.
- Updated `Framework_Application_Analysis_Template.md` to v1.0.15.
- Updated `Protocol_YAML_Definition_Guide.md` to v1.0.9.
- Updated `Protocol_YAML_Template.md` to v1.0.9.
- Updated `Coordinator_Software_Engineering_Rules.md` to v1.0.4.
- Updated `Embedded_C_Coding_Rules.md` to v1.0.16.
- Updated `CSharp_Coding_Rules.md` to v1.0.4.
- Updated `Repository_Validation_Checklist.md` to v1.0.3.

### Fixed

- Integrated Coordinator Software Engineering Rules and C# Coding Rules into the AI Active Document Manifest and canonical repository path list.
- Added explicit topic authority and task routing for Coordinator and C# implementation work.
- Added Coordinator and C# authority applicability, version, status, evidence, deviation, and `N/A` records to the Framework Application Analysis method.
- Clarified that Coordinator implementations require both role-level and applicable language-level authorities.
- Clarified that a `Draft for Review` authority is not silently promoted to an approved Product Baseline.
- Clarified the two Draft engineering-rule documents as proposed normative authorities pending human approval.
- Made Coordinator software engineering context conditional for non-Coordinator C# AI tasks.
- Scoped the recommended C# `coordinator/` project structure to Coordinator-role implementations.
- Normalized document-version formatting to lowercase `v` for the Coordinator and C# rule documents.
- Made implementation routing role-first and language-second; removed language-to-role assumptions.
- Resolved authority ownership by topic before applying precedence.
- Prevented the Baseline Framework from silently activating Draft Coordinator or C# authorities.
- Labeled upstream Framework and Protocol restatements as derived conformance summaries.
- Added untrusted deserialization controls for type metadata, polymorphism, XML external resources, resource bounds, inert DTO mapping, and negative tests.
- Added automated repository consistency checks and a human semantic-validation checklist.
- Added detached-package identity and file-integrity requirements.
- Clarified that public visibility is for inspection and does not grant adoption or reuse rights.
- Added the missing GitHub Actions document-validation workflow to the committed repository content.
- Enforced exact authority-document set equality across repository files, the root Current Document Set, and the AI Active Document Manifest.
- Replaced fence-count validation with marker-aware fenced-Code parsing.
- Extended local reference validation to images, reference-style links, and Markdown heading anchors.
- Scoped current-version validation to the Version History or Change History table.
- Completed the Application Analysis Authority Boundary for Coordinator and C# rule documents.
- Declared Python 3.10 or later for local validation and fixed CI validation to Python 3.12.
- Updated GitHub Actions to `actions/checkout@v7` and `actions/setup-python@v6`.
- Added Python 3.10 and 3.12 CI matrix coverage for both repository validation and regression tests.
- Prevented non-README Markdown files under `docs/` from bypassing authority governance by omitting all metadata.
- Added semantic-version format, Version History uniqueness and monotonic-order, highest-current-version, and declared Supersedes-chain checks.
- Added persistent regression tests for metadata omission, invalid and stale versions, Supersedes-chain errors, obsolete Action versions, and incomplete Python matrices.
- Excluded fenced examples from metadata, Version History, Current Document Set, and Active Document Manifest parsing.
- Required unique metadata within the opening metadata region and mandatory immediate-prior Supersedes declarations for non-initial versions.
- Replaced Workflow token searches with YAML and job-structure validation.
- Pinned GitHub Actions to immutable release commit SHAs.
- Added explicit directory-index allowlisting and lowercase Markdown-extension enforcement.
- Added balanced-parenthesis Markdown link, HTML link/image, and Setext-heading anchor validation.
- Expanded validator regression coverage for parsing and governance bypasses.
