# AI-Generated Artifact Validation Guide

**Canonical Filename:** `AI_Generated_Artifact_Validation_Guide.md`  
**Document Version:** v1.0.0  
**Status:** Draft for Review  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-19  
**Language:** English  
**Intended Audience:** Product owners, engineering owners, developers, reviewers, test engineers, configuration managers, quality and security reviewers, and AI-assisted engineering systems  
**Repository Role:** Proposed operational AI-artifact validation method; not an independent Product, architecture, Protocol, role, coding, safety, security, or compliance authority  
**Related Documents:**
- `../framework/AI_Engineering_Usage_Guide.md`
- `Validation_Evidence_Guide.md`
- `Repository_Validation_Checklist.md`
- `Protocol_Validation_Checklist.md`
- `Framework_Conformance_Checklist.md`
- `Coding_Rules_Review_Checklist.md`

---

## Copyright and Use

Copyright © 2026 Ray Yang. All rights reserved unless a repository-level license states otherwise.

This Guide validates AI-assisted artifacts against their governing authorities. It does not independently create Product requirements or grant approval.

---

## Version History

| Version | Date | Status | Summary |
|---|---|---|---|
| v1.0.0 | 2026-07-19 | Draft for Review | Initial Draft defining authority identification, prompt and input control, hallucination and stale-source detection, code/document/test boundaries, execution evidence, security and licensing review, approval, prohibited self-approval, and required records. |

---

# Part I — Responsibility and Scope

## 1. Core Principle

AI may assist engineering work, but it cannot own Product authority, professional judgment, approval, or responsibility.

The responsible human and organization remain accountable for:

- defining requirements and acceptance criteria;
- selecting and approving authorities;
- supplying complete and lawful inputs;
- reviewing design and implementation decisions;
- executing or supervising tests;
- evaluating safety, security, privacy, quality, and regulatory impact;
- approving release and use.

## 2. Applicable Artifacts

This Guide applies to AI-assisted:

- requirements and analyses;
- architecture and design documents;
- Protocol definitions and registries;
- source code and generated code;
- tests, simulators, fixtures, and vectors;
- review findings and checklists;
- scripts, CI workflows, manifests, and packages;
- summaries, translations, and reformatted records;
- evidence reports and release notes.

## 3. Artifact State

Every material AI-assisted artifact shall disclose an appropriate state, such as Draft, generated, reviewed, executed, verified at a stated boundary, approved, or rejected.

AI output is generated content. It is not automatically reviewed, executed, correct, safe, compatible, compliant, or approved.

# Part II — Authority and Input Control

## 4. Source Authority Identification

Before generation, identify:

- Product and Project requirements;
- applicable Framework and application analysis;
- Coordinator or Node role authority;
- Project Protocol and Protocol governance documents;
- language Coding Rules;
- hardware, datasheet, reference-manual, errata, SDK, API, and platform authorities;
- security, privacy, safety, quality, legal, and licensing authorities;
- source commit, version, status, and approval state.

When sources conflict, the conflict shall be surfaced and routed to the owning human authority. AI shall not silently choose the most convenient text.

## 5. Prompt and Input Control

A material AI task should retain:

- task objective and acceptance criteria;
- supplied source list and immutable identities;
- constraints, exclusions, and assumptions;
- required output format;
- prohibited behaviors;
- tool access and execution boundaries;
- human reviewer and approval route.

Sensitive or proprietary input shall be used only through an approved service and data-handling process.

## 6. Source Completeness

The reviewer shall determine whether AI received complete and current source material. Excerpts, screenshots, search snippets, OCR, generated summaries, and copied code may omit context.

When a required source is unavailable, the artifact shall state the limitation and shall not claim review of that source.

## 7. Stale Source Detection

For modern tools, libraries, APIs, standards, Products, repositories, and security information, current primary sources should be verified when change could affect the result.

The record should identify source publication/revision date, repository commit or release, retrieval date, and known superseding material.

# Part III — Output Review

## 8. Hallucination Detection

Review AI output for:

- nonexistent files, symbols, registers, APIs, commands, standards, clauses, citations, or test results;
- invented Product requirements or authority;
- unsupported hardware or platform behavior;
- fabricated quotations, values, versions, or compatibility claims;
- implicit assumptions presented as facts;
- omitted error, boundary, safety, or security behavior;
- contradictions with supplied sources.

Every material external citation or technical claim should be traceable to a source or clearly labelled as an engineering proposal.

## 9. Unverified API and Library Assumptions

Generated code shall be checked against official documentation and the actual dependency version for:

- API existence and signatures;
- threading and callback context;
- lifetime and ownership;
- blocking and cancellation behavior;
- error and exception behavior;
- serialization and security defaults;
- platform and version support;
- licensing and deployment constraints.

A plausible-looking call is not evidence that an API exists or is safe.

## 10. Internal Consistency

Review the complete artifact set for consistent names, versions, paths, identifiers, units, ranges, state names, message definitions, authority boundaries, and cross-references.

Generated documents shall not claim synchronization with files that were not actually updated and checked.

## 11. Scope Preservation

AI shall not expand a bounded request into unapproved architecture, Product behavior, security policy, legal conclusion, or compliance claim.

When a source is Draft, the output shall not promote it to Baseline or imply organizational adoption.

# Part IV — Code and Generated Artifact Controls

## 12. Generated-Code Boundary

Generated code should be separated from handwritten Product code and should identify:

- source inputs;
- generator/model/tool identity;
- prompt or generation configuration;
- output files;
- manual modifications;
- regeneration method;
- review and test state.

Manual edits to regenerated files shall be prohibited or repeatably reapplied through a controlled patch or template.

## 13. Code Review

Review AI-generated code for:

- architecture and role conformance;
- type, range, unit, arithmetic, and memory safety;
- lifetime, resource, and error handling;
- concurrency, ISR/callback/thread context, cancellation, timeout, and shutdown;
- unbounded work, allocation, queues, recursion, retries, and logs;
- Protocol, state-machine, reconnect, and duplicate behavior;
- security, secrets, authorization, deserialization, and input validation;
- unsupported dependencies and platform assumptions;
- generated/vendor code boundaries;
- applicable Coding Rules and deviations.

The reviewer shall inspect high-risk paths directly rather than relying only on another AI summary.

## 14. Build and Static Analysis

Generated code shall be built with the approved toolchain and configurations. Required warnings and static-analysis rules shall be executed.

AI shall not report “build passed” from syntax inspection or from a different environment. Command output and source/build identity shall be retained.

## 15. Test Generation

AI-generated tests shall be reviewed for:

- traceability to governing behavior;
- correct oracle and acceptance criteria;
- independence from the implementation defect under test;
- normal, boundary, invalid, timeout, cancellation, concurrency, overload, fault, and recovery cases;
- realistic mocks and explicit simulator limitations;
- deterministic setup and cleanup;
- missing negative and physical-target tests.

A test that merely repeats the generated implementation logic may provide weak evidence.

# Part V — Document and Analysis Controls

## 16. Generated-Document Boundary

Generated documents shall identify their source set, status, author/reviewer roles, unresolved assumptions, and approval state.

AI may draft text, tables, diagrams, and checklists. Human reviewers shall verify that the document:

- does not invent requirements;
- preserves authority ownership;
- uses correct terminology and versions;
- distinguishes fact, inference, proposal, and unresolved question;
- contains complete and working references;
- does not misrepresent execution or approval.

## 17. Datasheet and Primary-Source Review

For datasheets, standards, legal text, security specifications, and other primary authorities, critical conclusions shall be checked against the original page, table, figure, footnote, revision, and applicable variant.

OCR or parsed text shall not override the original visual source when they differ.

## 18. Translation and Reformatting

Translation or reformatting shall preserve normative strength, numbers, units, identifiers, code, equations, negation, conditions, and defined terms.

The transformed artifact shall not silently become a new authority when the source remains authoritative.

# Part VI — Execution and Evidence

## 19. Test Execution Requirement

Tests claimed as executed shall have actual execution evidence. The record shall identify command/procedure, environment, inputs, outputs, implementation, configuration, date, operator, result, and anomalies.

A test plan, generated test case, expected result, or AI statement is not execution evidence.

## 20. Target Behavior Verification

Behavior dependent on hardware, drivers, OS integration, real-time scheduling, electrical interfaces, reset, power loss, secure storage, physical control, or human interaction shall be verified at the appropriate target or representative system boundary.

Mocks and simulators shall disclose fidelity limits.

## 21. Fabricated Evidence Prohibition

AI and humans shall not fabricate logs, screenshots, measurements, approvals, citations, hashes, tool output, test execution, or review records.

Synthetic examples shall be clearly marked and shall not be placed where they can be mistaken for actual evidence.

## 22. Evidence Review

Use `Validation_Evidence_Guide.md` to classify evidence state and adequacy. Generated reports shall retain traceable raw inputs and outputs.

A successful repository validator, compiler, unit test, or AI review proves only its implemented boundary.

# Part VII — Safety, Security, Legal, and Approval

## 23. Safety and Security Review

AI-generated safety- or security-relevant artifacts require qualified human review and applicable Product evidence.

Review shall address failure modes, local safety, safe/degraded state, authorization, secrets, trust, replay, Rekey, update, logging, privacy, abuse cases, and recovery as applicable.

AI shall not choose a production cryptographic algorithm, credential policy, safety threshold, or risk acceptance without authorized human decision.

## 24. Licensing and Attribution Review

Review generated artifacts for copied or derivative third-party material, notices, licenses, trademarks, patents, confidential information, and incompatible dependency terms.

AI output shall not be assumed original or license-clear merely because the model generated it. Required notices and source obligations shall be preserved.

## 25. Human Approval and Sign-Off

Approval shall identify:

- artifact and immutable identity;
- scope and governing authorities;
- evidence reviewed;
- findings, deviations, and unresolved risks;
- approver and authority;
- date and decision.

AI cannot be an approver or signatory.

## 26. Prohibited Self-Approval

The same AI generation pass shall not generate an artifact, declare it correct, create fictional evidence, and approve it.

A second AI review may help find issues but remains AI-assisted review and does not replace responsible human approval.

## 27. Compliance Declaration

No AI-generated artifact shall declare Product, regulatory, quality, security, safety, or standards compliance without:

- identified applicable clauses and interpretations;
- complete traceability;
- executed evidence;
- qualified human review;
- authorized approval.

Repository or framework conformance is not equivalent to certification or regulatory compliance.

# Part VIII — Required Record

## 28. AI-Assisted Artifact Record

For material artifacts, record:

| Field | Content |
|---|---|
| Artifact ID | Canonical path, commit, build, release, or package hash |
| Artifact Type | Code, document, Protocol, test, analysis, report, script, or other |
| Objective | Bounded requested outcome |
| Governing Authorities | Product, Framework, role, Protocol, Coding Rules, external sources |
| Source Set | Versions, revisions, commits, retrieval dates, and completeness limits |
| AI Service/Model | Identity available at execution time |
| Prompt/Input Record | Controlled prompt and supplied context, subject to data policy |
| Tools Executed | Commands, tool versions, and actual outputs |
| Human Changes | Material edits after generation |
| Verification | Build, test, review, source checks, target checks |
| Findings and Limits | Hallucinations, stale assumptions, anomalies, deviations, unresolved items |
| Evidence | Immutable evidence references |
| Reviewer | Responsible human reviewer |
| Approval State | Draft, reviewed, approved, rejected, or pending |

## 29. Minimum Acceptance Gate

Before an AI-assisted artifact is represented as complete:

1. Governing authorities and source versions are identified.
2. Source completeness and freshness are checked.
3. Hallucinations and unsupported assumptions are reviewed.
4. Applicable structural, semantic, coding, security, licensing, and Product reviews are complete.
5. Claimed builds and tests were actually executed with evidence.
6. Target-dependent behavior was verified at the required boundary.
7. Findings, deviations, and unresolved issues are visible.
8. Human reviewer and approval state are recorded.
