# Changelog

All notable repository-level changes are documented in this file.

Individual authority documents retain their own internal Version History and approval status.

## Unreleased

### Current Authority Revision Snapshot

| Document | Version | Status |
|---|---:|---|
| AI Engineering Usage Guide | v1.0.38 | Draft for Review |
| Coordinator/Node Control Framework | v1.1.6 | Baseline |
| Framework Application Analysis Template | v1.1.9 | Baseline |
| Protocol YAML Definition Guide | v1.1.7 | Baseline |
| Protocol YAML Template | v1.1.1 | Baseline |
| Protocol Compatibility Rules | v1.1.0 | Draft for Review |
| Protocol Registry Governance | v1.1.0 | Draft for Review |
| Protocol Security Profile | v1.1.0 | Draft for Review |
| Coordinator Software Engineering Rules | v1.1.0 | Draft for Review |
| Coordinator Architecture Patterns | v1.1.0 | Draft for Review |
| Coordinator Concurrency Guide | v1.1.0 | Draft for Review |
| Coordinator Logging Guide | v1.1.1 | Draft for Review |
| Coordinator Testing Guide | v1.1.1 | Draft for Review |
| Coordinator UI Engineering Guide | v1.1.1 | Draft for Review |
| Node Software Engineering Rules | v1.1.0 | Draft for Review |
| Embedded C Coding Rules | v1.0.18 | Final Baseline |
| C# Coding Rules | v1.0.4 | Draft for Review |
| Repository Validation Checklist | v1.0.17 | Draft for Review |
| Validation Evidence Guide | v1.1.0 | Draft for Review |
| Protocol Validation Checklist | v1.1.6 | Draft for Review |
| Framework Conformance Checklist | v1.1.5 | Draft for Review |
| Coding Rules Review Checklist | v1.0.0 | Draft for Review |
| AI-Generated Artifact Validation Guide | v1.1.0 | Draft for Review |

### Current Review Changes

- Rejected repository-controlled symbolic links and special filesystem entries before content reads, and constrained authority-registry document and prerequisite paths to canonical repository-relative `docs/*.md` paths.
- Scoped release-state validation to the unique README Current Status section and the active Changelog Unreleased section so superseded mutable-content freeze wording cannot remain as a current unqualified claim.
- Added regression coverage for external symlink substitution, unsafe registry paths, Current Status decoys, and contradictory Unreleased freeze assertions.
- Added an exact Current Authority Revision Snapshot so `CHANGELOG.md` cannot silently omit the active governed-document versions while legacy keywords remain elsewhere in Unreleased.
- Replaced the mutable-content self-assertion that the repository was already frozen with fail-closed release-candidate wording; repository text alone is not freeze evidence.
- Added repository validation and mutation tests for stale Changelog snapshots and self-asserted release-freeze wording.
- Enforced strict descending semantic-version order for governed Version History and Change History tables; ascending order is now rejected.
- Normalized Embedded C Coding Rules v1.0.18 Change History to descending order without changing coding-rule semantics.
- Hardened controlled AI routing-history validation to reject missing, duplicated, additional, or additive-decoy authority-version references.
- Added mutation regression coverage for ascending history tables and additive historical-routing decoys.
- Corrected the AI Engineering Usage Guide v1.0.31 historical routing reference from Framework Application Analysis Template v1.1.8 to the actual v1.1.7 revision.
- Added executable validation and regression coverage for the controlled AI routing-history sequence.
- Corrected the AI Engineering Usage Guide self-supersession and duplicated v1.0.32 history row; restored the missing v1.0.31 identity.
- Normalized non-monotonic authority Version History tables to strict descending semantic-version order without changing their normative engineering content.
- Enforced table-scoped Version History uniqueness, monotonicity, current-version/date/status consistency, and immediate Supersedes linkage in repository validation.
- Added mutation regression coverage for duplicated history versions, self-supersession, stale Supersedes links, and non-monotonic history ordering.
- Rejected contradictory Protocol Tester approval records by defining stage/applicability/self-validation/physical-execution/formal-gate disposition consistency.
- Required controlled Tester self-validation with positive and known-negative cases before a Tester PASS result may support Integration or Release approval.
- Extended repository validation and mutation regression coverage for cross-field gate bypasses and unverified Tester PASS claims.
- Bound Protocol Tester and interoperability evidence to exact tested candidate identities; added Integration-to-Release evidence reconciliation, affected re-execution, and replacement-evidence requirements.
- Bounded representative-target claims to demonstrated equivalence and required residual actual-target verification or explicit, approved release limitations.
- Extended repository validation and mutation regression coverage for stale evidence and over-claimed representative-target evidence.
- Closed staged Protocol Tester checklist contradictions by separating Definition planning from Integration/Release implementation and execution evidence, requiring exactly one claimed baseline stage, and requiring N/A re-confirmation when scope or stage changes.
- Hardened repository validation against decoy or duplicate Protocol Tester table rows by scoping checks to the controlled section and requiring one exact applicability row and one exact baseline-stage row.

- Closed a Protocol lifecycle circularity by separating Definition, Integration, and Release Baselines: Tester planning is controlled at definition time, while physical or representative target execution evidence is required before formal integration and release approval.
- Hardened Protocol Tester applicability validation to require the exact `Required / N/A` disposition and reject alternate optional paths.

- Closed follow-up Protocol Conformance Tester governance gaps by removing the unauthorised `No` applicability path, requiring an N/A approval record, defining implementation-independence boundaries, adding controlled tool and execution-report artifacts, inserting a physical-or-representative Node pre-integration gate, and extending validator regression coverage.
- Added an explicit independent Protocol Conformance Tester requirement for command, response, state, telemetry, and stream Protocols, including physical or representative Node execution and retained source/build/configuration evidence.
- Added mandatory Project-analysis fields for Tester applicability, controlled Protocol and Golden Vector identity, coverage, target execution, evidence location, owner, and reviewer.
- Extended the Protocol Validation Checklist with traceable Tester existence, coverage, controlled-expectation, target-execution, and evidence-identity checks.
- Updated AI routing, authority registry, root document set, and directory indexes for AI Engineering Usage Guide v1.0.28, Framework Application Analysis Template v1.1.4, Protocol YAML Definition Guide v1.1.2, and Protocol Validation Checklist v1.1.2.

- Corrected the canonical Framework conformance example to the immutable `e516fa1d58bd99014b965f37215db85ae594704b` / Framework `v1.1.4` source pair and upgraded claim schema v2 to require canonical GitHub host, owner, repository name, and URL.

- Made external legal-baseline activation explicitly fail-closed through `external-evidence-required`, added signed-tag verification tooling, and prohibited repository content or detached ZIPs from self-asserting anchor activation.

- Added the first `v1.0.0` release-candidate status wording; its earlier mutable-content freeze declaration is superseded by the current fail-closed release-state boundary.

- Required Scoped claims to satisfy every applicable requirement within each included boundary; restricted residual deviations; froze the claim boundary before validation; and added claim lifecycle, invalidation, supersession, withdrawal, and signatory-bounded assessment rules.
- Added `schema/framework-conformance-claim.schema.yaml` and a canonical machine-validatable Framework conformance claim example.
- Upgraded `third-party-materials.yaml` to bind entire repository files to actual content hashes, retained source-evidence hashes, controlled notices, approver identities, approval references, and obligation evidence.
- Externalized legal-text digests to `legal-baseline.yaml`; added CODEOWNERS and external signed-tag or protected-merge requirements; and clarified that repository-local validation provides change detection rather than independent authorization.
- Corrected the GitHub Terms carve-out to distinguish rights granted to GitHub, its Affiliates, and other GitHub Users.
- Added patent, invention, trademark, endorsement, and other implied-license boundaries.
- Aligned the root README so reusable-by-design language does not imply a public implementation or reuse license.
- Hardened CI and Protocol validation against conditional execution, expression-based continue-on-error, legacy-profile fail-open, weak field typing, fixture-oracle gaps, empty input, and unbounded diagnostic output.
- Added Framework-level conformance-claim integrity and human or organizational deviation accountability; aligned the Framework Conformance Checklist; and added repository `AS IS`, no-warranty, independent-review, and limitation-of-liability terms to the existing `LICENSE`.
- Added the GitHub Terms limited-platform-rights carve-out, lawfully authorized file-specific notice boundaries, a no-unsolicited-contribution policy, and a formal conformance correction/revalidation/evidence restoration path.
- Distinguished Full Framework Conformance, Scoped Framework Conformance, and Nonconforming status; prohibited after-the-fact scope laundering; protected non-excludable controls; and clarified that conformance is the claim issuer's self-declaration rather than author or maintainer certification.
- Added `third-party-materials.yaml` as the controlled acceptance manifest for file-specific and third-party licensing or notice exceptions.
- Limited copyright claims to protectable human-authored contributions and excluded third-party and legally unprotectable material.
- Replaced marker-only legal validation with normalized visible-text integrity controls and regression coverage for hidden, fenced, duplicated, negated, and semantically reversed clauses.

### Added

- Added `CONTRIBUTING.md` to require a separate prior written agreement before external repository contributions are accepted.
- Added `third-party-materials.yaml` with a fail-closed empty default and controlled entry schema for accepted third-party material.
- Added `schema/protocol.schema.yaml` as the controlled structural schema for the backward-compatible conditional `node_model`.
- Added `tools/validate_protocol.py` with actionable rule, YAML path, expected value, actual value, and correction diagnostics for Multi-Node semantic validation.
- Added valid Single-Node, independent-link, shared-bus, and routed-gateway fixtures plus invalid conflict, addressing, broadcast, scope, lifecycle, resource, and Firmware Update fixtures.
- Added Protocol semantic-validator regression tests and integrated the fixture matrix into repository validation.

- Added `docs/protocol/Protocol_Compatibility_Rules.md` for Protocol version consequences, change classification, mixed-version operation, deprecation, removal, and compatibility evidence.
- Added `docs/protocol/Protocol_Registry_Governance.md` for Message and Capability ID allocation, namespaces, lifecycle, retirement, non-reuse, merge control, and generated Registry artifacts.
- Added `docs/protocol/Protocol_Security_Profile.md` for secure-session applicability, authentication, authorization, record protection, replay, Counter, Rekey, reconnect, credential, Bootloader, and Firmware Update security governance.
- Added `docs/node/README.md` and `docs/node/Node_Software_Engineering_Rules.md` for Node-specific architecture realization, execution contexts, state and command ownership, local safety, bounded resources, diagnostics, Bootloader handoff, and target evidence.
- Added `docs/validation/Validation_Evidence_Guide.md`, `Protocol_Validation_Checklist.md`, `Framework_Conformance_Checklist.md`, `Coding_Rules_Review_Checklist.md`, and `AI_Generated_Artifact_Validation_Guide.md`.
- Added explicit validation regression coverage for unregistered authorities, missing Registry files, table and folder-index divergence, metadata mismatch, illegal filenames, broken references, checklist authority leakage, Protocol-domain placement, Node routing, NOTICE sections, and CHANGELOG synchronization.


- Added five proposed topic-specific Coordinator authorities: architecture patterns, concurrency, logging, testing, and UI engineering Guides.
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

- Expanded `.github/CODEOWNERS` from selected files to the complete governed authority, schema, workflow, dependency, validator, verifier, test, fixture, and governance-manifest boundary.
- Made `tools/verify_external_anchor.py` commit-scoped: it now reads the controlled baseline and protected legal documents from the target commit, verifies their normalized digests before accepting the signed tag, and explicitly excludes uncommitted working-tree content from the result.
- Added fail-closed external-anchor verifier regression tests for valid target content, malformed baseline identity, and protected-document digest mismatch.
- Updated AI Engineering Usage Guide to v1.0.26, Coordinator/Node Control Framework and Framework Conformance Checklist to v1.1.5, Framework Application Analysis Template to v1.1.2, and Repository Validation Checklist to v1.0.11; synchronized canonical claim-source identity, external-anchor state, release-freeze guidance, registry, README, AI manifest, validator, and regression tests.

- Updated AI Engineering Usage Guide to v1.0.25, Coordinator/Node Control Framework and Framework Conformance Checklist to v1.1.4, Framework Application Analysis Template to v1.1.1, and Repository Validation Checklist to v1.0.10; synchronized the registry, README, AI manifest, legal controls, third-party manifest, claim schema, validator, and regression tests.
- Updated AI Engineering Usage Guide to v1.0.24, Coordinator/Node Control Framework and Framework Conformance Checklist to v1.1.3, and Repository Validation Checklist to v1.0.9; synchronized the registry, README, AI manifest, legal controls, third-party manifest, validator, and regression tests.
- Updated AI Engineering Usage Guide to v1.0.23, Coordinator/Node Control Framework and Framework Conformance Checklist to v1.1.2, and Repository Validation Checklist to v1.0.8; synchronized the registry, README, AI manifest, validator, and regression tests.
- Clarified that public GitHub visibility grants only GitHub Terms platform rights, restricted file-specific precedence to authorized scoped exceptions, and protected those boundaries with automated validation.
- Updated AI Engineering Usage Guide to v1.0.22, Coordinator/Node Control Framework to v1.1.1, and Framework Conformance Checklist to v1.1.1; synchronized `authority-registry.yaml`, the root Current Document Set, and the AI Active Document Manifest.
- Made document-version metadata regression tests derive the active version from the tested file instead of depending on a hard-coded Framework version.
- Activated Draft 2020-12 Protocol schema validation before semantic linting and rejected duplicate YAML keys fail-closed.
- Replaced workflow substring checks with structural validation of the required unconditional validation steps and commands.
- Hardened governed-document metadata, Markdown fence, link, heading, filename-extension, Registry duplicate-key, and current `Unreleased` CHANGELOG validation.
- Added regression coverage for the confirmed schema, workflow, metadata, Registry, filename, Markdown parsing, and CHANGELOG bypasses.
- Added hash-pinned `jsonschema` and transitive validation dependencies for the supported Python validation environments.

- Expanded the Framework, Application Analysis, Protocol YAML, compatibility, Registry, security, Coordinator, Node, and validation authorities into a complete Multi-Node baseline for independent point-to-point links, shared multidrop buses, and routed gateways.
- Added the conditional `node_model` contract while preserving omission as the legacy Single-Node interpretation and avoiding a mandatory on-wire Node ID for connection-bound point-to-point links.
- Defined stable Node identity, runtime address, route, connection generation, Protocol Session, Secure Session, correlation, lifecycle, broadcast, multi-target, resource-containment, and Firmware Update targeting semantics.
- Synchronized `authority-registry.yaml`, the root document set, AI Active Document Manifest, directory indexes, repository structure, and validation guidance for the Multi-Node authority changes.

- Updated AI Engineering Usage Guide to v1.0.20, Coordinator/Node Control Framework to v1.0.14, Framework Application Analysis Template to v1.0.17, Protocol YAML Definition Guide to v1.0.11, and Repository Validation Checklist to v1.0.6.
- Split Protocol topic ownership so dedicated compatibility, Registry, and security documents own governance decisions while the Protocol YAML Definition Guide retains machine-verifiable representation, Semantic Lint, validation, and Code Generation ownership.
- Expanded `authority-registry.yaml` and synchronized the root Current Document Set, AI Active Document Manifest, stable canonical path list, directory indexes, authority routing, Repository Structure, and validation guidance for 23 governed documents.
- Reworked `NOTICE.md` with Copyright Notice, Personal Engineering Project Disclaimer, No Employer or Company Representation, AI Assistance Disclosure, Third-Party Standards and Trademark Notice, and File-Specific Notice Precedence.
- Defined the validation documents as evidence and conformance views that do not independently create Product, Framework, Protocol, role, or Coding Rules requirements.


- Updated AI Engineering Usage Guide to v1.0.18; retained Coordinator Software Engineering Rules v1.0.5; and updated Coordinator Logging, Testing, and UI Engineering Guides to v1.0.1.
- Synchronized `authority-registry.yaml`, the root Current Document Set, the AI Active Document Manifest, the Coordinator directory index, the root Authority Boundary, and the root Repository Structure for all five Coordinator Guides.
- Hardened archive and package import against links, special filesystem entries, canonical-path escape, destination-link traversal, and time-of-check/time-of-use replacement.
- Distinguished hash-based accidental-corruption detection from independently anchored authenticity and adversarial-tamper evidence in logging and testing guidance.
- Replaced the registry-version mismatch regression mutation with a version-independent targeted edit.
- Corrected validator YAML alias diagnostics to emit the controlled `aliases` wording used by regression tests.
- Required the exact `authority-registry.yaml` root schema and controlled `GitHub main` source identity.
- Fixed document-validation CI to the `ubuntu-24.04` runner image.
- Updated AI Engineering Usage Guide to v1.0.16 and Repository Validation Checklist to v1.0.5.
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

- Prevented Protocol governance documents from being misrouted as Coordinator-owned authority.
- Closed the missing Node-specific engineering-authority layer between the reusable Framework and language Coding Rules.
- Closed validation-evidence and AI-generated-artifact approval gaps, including fabricated evidence, self-approval, stale-source, unavailable-source, and unverified-API claims.
- Required directory indexes, authority registry, root document table, AI manifest, NOTICE, routing, and CHANGELOG claims to remain structurally synchronized.


- Rejected missing or unexpected authority-registry root fields and uncontrolled `source_of_truth` values.
- Added directed-graph cycle detection for authority prerequisite relationships.
- Added regression coverage for Registry root schema, source identity, prerequisite cycles, and CI runner pinning.
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
