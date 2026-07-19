# Validation Evidence Guide

**Canonical Filename:** `Validation_Evidence_Guide.md`  
**Document Version:** v1.0.0  
**Status:** Draft for Review  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-19  
**Language:** English  
**Intended Audience:** Product owners, engineering owners, reviewers, test engineers, configuration managers, release engineers, auditors, tool owners, and AI-assisted engineering systems  
**Repository Role:** Proposed operational validation-evidence method; not a Product, architecture, Protocol, role, or language authority  
**Related Documents:**
- `../framework/AI_Engineering_Usage_Guide.md`
- `Repository_Validation_Checklist.md`
- `Protocol_Validation_Checklist.md`
- `Framework_Conformance_Checklist.md`
- `Coding_Rules_Review_Checklist.md`
- `AI_Generated_Artifact_Validation_Guide.md`

---

## Copyright and Use

Copyright © 2026 Ray Yang. All rights reserved unless a repository-level license states otherwise.

This document defines an evidence method. It does not itself establish Product acceptance criteria or certify compliance with any external standard.

---

## Version History

| Version | Date | Status | Summary |
|---|---|---|---|
| v1.0.0 | 2026-07-19 | Draft for Review | Initial Draft defining evidence types, identity, traceability, reproducibility, ownership, environment and tool identification, pass/fail criteria, anomalies, retention, invalid evidence, and AI-generated evidence limitations. |

---

# Part I — Evidence Model

## 1. Purpose

This Guide defines how engineering claims are supported, reviewed, retained, and reported. It separates “an activity was planned,” “an activity was executed,” and “the available evidence supports the stated claim.”

The governing authority supplies the requirement and acceptance criteria. This Guide supplies the evidence structure.

## 2. Evidence Definition

Evidence is a preserved, identifiable record that supports or refutes a bounded engineering claim.

An evidence record should answer:

- What claim or requirement was evaluated?
- Which artifact, implementation, Product, configuration, or environment was evaluated?
- What method and acceptance criteria were used?
- Who or what performed the activity?
- When was it performed?
- What inputs, tools, versions, and conditions applied?
- What raw and processed outputs were produced?
- What result was observed?
- What anomalies or limitations remain?
- Who reviewed and approved the interpretation?

A conclusion without recoverable supporting records is an assertion, not objective evidence.

## 3. Evidence States

Use explicit evidence states such as:

- Planned, not executed.
- Generated, not reviewed.
- Statically reviewed.
- Executed with mock or fake dependencies.
- Executed with simulator or reference implementation.
- Executed in cross-implementation integration.
- Executed on target hardware.
- Executed in representative system or HIL.
- Manually observed.
- Human reviewed.
- Approved for the stated scope.
- Failed.
- Inconclusive.
- Blocked.

A stronger-sounding label shall not be used to hide a weaker boundary.

## 4. Objective Evidence

Objective evidence is based on observable records rather than preference or unsupported opinion. It may include source-controlled artifacts, command output, compiler reports, static-analysis reports, test logs, captures, measurements, photographs, signed review records, and reproducible generated outputs.

Objectivity does not guarantee adequacy. The evidence shall still match the claim and acceptance criteria.

# Part II — Evidence Types

## 5. Review Evidence

Review evidence should record:

- artifact and immutable identity;
- review scope and governing authorities;
- reviewer competence or role as required by the Project;
- checklist or review method;
- findings and dispositions;
- unresolved issues;
- approval state.

“Reviewed” without scope, reviewer, findings, or artifact identity is insufficient.

## 6. Test Evidence

Test evidence should include:

- test case or procedure identity and version;
- requirement or risk traceability;
- preconditions and acceptance criteria;
- test environment and configuration;
- software, firmware, hardware, Protocol, and data identities;
- actual inputs and observed outputs;
- raw logs, captures, measurements, or artifacts;
- result and anomaly handling;
- operator and reviewer.

Screenshots may supplement test evidence but should not be the only evidence when machine-readable output is available.

## 7. Analysis Evidence

Analysis evidence should retain:

- source inputs and assumptions;
- equations, models, tools, scripts, and versions;
- units, limits, and uncertainty;
- intermediate and final outputs;
- sensitivity or boundary analysis where relevant;
- independent review or comparison method;
- applicability limitations.

An analysis based on typical values shall not be represented as worst-case evidence.

## 8. Inspection Evidence

Inspection evidence may include dimensional, visual, file-content, configuration, assembly, register, or document inspection. It should identify the inspected item, method, sampling, criteria, instrument or viewer, result, and inspector.

A visual inspection cannot prove hidden behavior it did not observe.

## 9. Generated Evidence

Generated reports, diffs, manifests, hashes, coverage summaries, and static-analysis results are evidence only when the generator, version, command, inputs, configuration, and output integrity are traceable.

Generated evidence shall distinguish:

- generation succeeded;
- generation output was reviewed;
- the output was independently validated;
- the underlying implementation or target behavior was executed.

A generated “Pass” label cannot exceed the capability of its generator.

# Part III — Identity, Traceability, and Reproducibility

## 10. Evidence Identity

Each controlled evidence item should have a unique identifier or immutable location and should preserve:

- title and evidence type;
- date/time and time zone when relevant;
- owner and reviewer;
- source commit, tag, release, build, or package hash;
- Product, hardware, firmware, software, Protocol, and configuration identity;
- status and revision history.

Mutable filenames such as `latest.log` are not sufficient without an immutable association.

## 11. Traceability

Evidence shall trace to one or more bounded claims such as a requirement, architecture rule, Protocol obligation, coding rule, risk control, defect, change, compatibility claim, or release criterion.

Traceability may be many-to-many, but the relationship shall be reviewable. A checklist row without a governing reference shall not invent a requirement.

## 12. Reproducibility

Reproducibility requires enough information for a competent reviewer to repeat or independently assess the activity.

Preserve as applicable:

- exact command and working directory;
- toolchain and dependency versions;
- environment variables and configuration;
- input files and hashes;
- fixtures, simulators, hardware, and calibration state;
- random seed and time source;
- expected and actual outputs;
- known nondeterminism and tolerance.

When full reproduction is impossible, the record shall state why and what independent corroboration exists.

## 13. Environment Identification

Evidence shall identify environmental factors that can affect the result, such as:

- operating system and architecture;
- compiler, runtime, SDK, driver, and library versions;
- build type and optimization;
- hardware revision, clock, supply, temperature, load, and connected equipment;
- debugger, instrumentation, and logging state;
- network, Transport, and security configuration;
- simulator fidelity and unsupported behavior.

## 14. Tool and Version Identification

A tool result shall identify the tool and version. For critical evidence, preserve the tool configuration, ruleset, license-dependent features, wrapper script, and invocation.

Use of an unqualified web service or AI model should record the service/model identity available at execution time, prompt/input scope, output, and human review state.

## 15. Input and Output Preservation

Raw inputs and raw outputs should be preserved before manual transformation. When output is filtered, summarized, converted, or copied into another document, retain a trace to the source and describe the transformation.

A manually retyped result is weaker than a captured machine output and shall be labelled accordingly.

# Part IV — Result and Review Control

## 16. Pass and Fail Criteria

Acceptance criteria shall exist before interpreting the result whenever practical. The evidence record shall distinguish:

- Pass: all stated criteria satisfied within the claimed scope.
- Fail: one or more criteria not satisfied.
- Inconclusive: evidence cannot determine the result.
- Blocked: required setup or evidence unavailable.
- Limited Pass: only when the Project process permits it and the excluded scope is explicit.

A missing result shall not default to Pass.

## 17. Evidence Owner

The Evidence Owner is responsible for preserving identity, inputs, outputs, execution state, anomalies, and traceability. Ownership does not automatically grant approval authority.

## 18. Evidence Reviewer

The reviewer checks that:

- the governing authority and criteria are correct;
- the evidence boundary matches the claim;
- execution and environment are identifiable;
- the result follows from the observations;
- anomalies and limitations are visible;
- approvals are within the reviewer’s authority.

The person or AI that created an artifact shall not be treated as independent approval merely by repeating its own conclusion.

## 19. Anomaly Handling

Unexpected output, test interruption, tool failure, environmental deviation, data loss, mismatch, or unexplained warning shall be recorded as an anomaly.

An anomaly shall be dispositioned as, for example:

- defect confirmed;
- test method defect;
- environment/setup defect;
- accepted limitation;
- not reproducible with stated investigation;
- duplicate of existing issue;
- unresolved.

Deleting or editing evidence to hide an anomaly is prohibited.

## 20. Unresolved Issues

Unresolved issues shall identify owner, impact, next action, blocking relationship, and decision state. An unresolved issue that affects acceptance shall prevent an unconditional Pass.

## 21. Evidence Retention

Retention shall match Product, legal, regulatory, quality, security, and service-life needs. Preserve evidence in a controlled location with access, backup, integrity, confidentiality, and disposal rules appropriate to its content.

Repository-level hashes can detect accidental corruption when independently compared; they do not by themselves prove authorship or protect against an attacker who can replace both file and hash.

# Part V — Invalid or Misrepresented Evidence

## 22. Invalid Evidence Examples

The following are not sufficient for the implied claim:

- “AI reviewed it and found no issue.”
- “The code looks correct.”
- a test case marked Pass without execution output;
- a successful compile used as proof of runtime behavior;
- a mock test used as proof of electrical timing;
- a screenshot without artifact or environment identity;
- a log excerpt that omits the failure region;
- a checksum stored and replaced with the file by the same uncontrolled channel;
- a copied result whose source cannot be recovered;
- a document version that does not match the tested implementation;
- a static-analysis report for a different build configuration;
- an unreviewed generated compliance statement.

## 23. Evidence Integrity

Evidence shall not be fabricated, selectively altered, backdated, or represented as independently reviewed when it was not. Corrections shall preserve the original record or an auditable change history.

## 24. Confidential and Sensitive Evidence

Evidence shall exclude or protect secrets, credentials, private keys, personal data, proprietary third-party content, and security-sensitive details according to applicable authorities.

Redaction shall preserve enough context to support the claim and shall be disclosed.

# Part VI — AI-Generated Evidence

## 25. AI Limitations

AI can generate plans, checklists, candidate findings, diffs, summaries, and test code. Those outputs are not proof that the underlying build, test, measurement, inspection, or review occurred.

AI output shall be treated as:

- generated, not executed;
- unapproved until human review;
- potentially incomplete, stale, or fabricated;
- bounded by the supplied sources and tool access.

## 26. AI Evidence Record

For material AI-assisted work, preserve as applicable:

- model or service identity available at the time;
- prompt and supplied source scope;
- generated output;
- tool calls or command output actually executed;
- human modifications;
- verification performed against primary sources;
- reviewer and approval state;
- unresolved hallucinations or assumptions.

Private prompts or sensitive inputs shall be handled according to approved data policy.

## 27. Prohibited AI Claims

AI shall not claim that:

- a test passed when no execution evidence is available;
- hardware behavior was verified by source inspection alone;
- a Product is compliant or certified;
- an artifact is approved by the responsible human;
- an unavailable document was reviewed;
- a hash proves authenticity without an independent trust anchor;
- generated code is safe merely because it follows a template.

## 28. Minimum Evidence Record

A practical minimum record is:

| Field | Required Content |
|---|---|
| Evidence ID | Unique identifier or immutable path |
| Claim | Bounded statement being evaluated |
| Governing Reference | Requirement, rule, risk, defect, or criterion |
| Artifact Identity | Source/build/package/hardware/Protocol/configuration |
| Method | Review, test, analysis, inspection, or generation |
| Environment and Tools | Versions and relevant conditions |
| Inputs | Files, stimuli, setup, and hashes where useful |
| Outputs | Raw and processed evidence references |
| Result | Pass, Fail, Inconclusive, Blocked, or approved controlled state |
| Anomalies and Limits | Deviations, exclusions, and unresolved issues |
| Owner and Reviewer | Names or controlled roles |
| Approval State | Draft, reviewed, approved, rejected, or pending |
