# Framework Application Analysis Template

## Reusable Method for Applying the Coordinator/Node Framework to a New Application

**Document Name:** `Framework_Application_Analysis_Template.md`  
**Document ID:** FAAT  
**Document Version:** v1.0.14  
**Status:** Baseline  
**Document Type:** Reusable Analysis Template  
**Primary Narrative Language:** English  
**Author:** Ray Yang  
**Maintainer:** Ray Yang  
**Repository:** `host-device-control-framework`  
**Related Documents:**
- `Coordinator_Node_Control_Framework.md`
- `Coordinator_Software_Engineering_Rules.md`
- `Embedded_C_Coding_Rules.md`
- `CSharp_Coding_Rules.md`
- `Protocol_YAML_Definition_Guide.md`
- `Protocol_YAML_Template.md`
- `Repository_Validation_Checklist.md`

**First Issued:** 2026-07-15  
**Last Revised:** 2026-07-18  

Copyright © 2026 Ray Yang. All rights reserved.

This document is maintained as part of a personal engineering project. It is not an official
document of any employer or organization. No license is granted unless otherwise explicitly stated.

All third-party standards, publications, trademarks, source code, licenses, and legal notices remain
the property of their respective owners. References to third-party materials do not imply ownership,
endorsement, affiliation, or authorization.

---

# 0. Document Control

## 0.1 Purpose

This template evaluates how the existing `Coordinator_Node_Control_Framework` shall be applied to a new
application domain.

The analysis does not create an independent competing architecture. It systematically identifies:

1. Which Framework capabilities can be reused directly.
2. Which capabilities require configuration or controlled extension.
3. Which behaviors belong only in the Application Profile or Product requirements.
4. The responsibility boundaries among Coordinator, Node, UI, external systems, Device Services, Drivers,
   HAL, and physical Devices.
5. The commands, data models, State Machines, failure behavior, security controls, UI flows, and evidence
   required by the application.
6. Whether the reusable Framework has a genuine cross-application gap.
7. Which Product-specific needs shall not be added back into the reusable Framework.
8. The minimum documents, modules, mocks, tools, tests, measurements, and decisions required before
   implementation begins.
9. Whether the proposed application remains feasible under timing, bandwidth, memory, CPU, safety, security,
   compatibility, and recovery constraints.
10. The evidence required to approve an Application Analysis Baseline.

This template may be applied to:

```text
ECG Measurement
Smart Battery Monitoring and Control
Motor Control
Sensor Acquisition
Power Supply Monitoring
Production Test
Firmware Update
Data Logging
Device Configuration
Calibration and Maintenance
Automated Test Equipment
Gateway and Multi-Node Control
Other Coordinator/Node applications
```

## 0.2 Version History

| Version | Date | Author | Description |
|---|---|---|---|
| v1.0.0 | 2026-07-15 | Ray Yang | Established the initial reusable Application Analysis template. |
| v1.0.1 | 2026-07-15 | Ray Yang | Added Security and Access Control analysis, Framework compatibility revalidation, and Gap owner/status tracking. |
| v1.0.2 | 2026-07-15 | Ray Yang | Corrected Section 20 Final Output Format numbering. |
| v1.0.3 | 2026-07-18 | Ray Yang | Converted the complete template to English; added repository identity, copyright, personal-project clarification, and third-party-material notice; aligned the analysis method with `Coordinator_Node_Control_Framework.md`, `Embedded_C_Coding_Rules.md`, `Protocol_YAML_Definition_Guide.md`, and `Protocol_YAML_Template.md`; removed the obsolete independent Protocol YAML skeleton; separated Telemetry and Stream analysis; added Transport Profile, timing, bandwidth, resource, safety, Application/Bootloader Session, Firmware Update transaction, Code Generation, validation-evidence, structural-rewrite, decision-register, and completion-gate requirements. |
| v1.0.4 | 2026-07-18 | Ray Yang | Restored and modernized the reusable Command, Data Field, State, UI Page, Framework Gap, Review Question, and detailed completion-checklist appendices that were unintentionally omitted during the v1.0.3 structural rewrite; added the Bootloader/Update responsibility column; made signed Firmware image verification mandatory whenever Firmware Update is in scope; expanded placeholder guidance and source-input coverage; and synchronized the Baseline Decision Summary and structural validation. |
| v1.0.5 | 2026-07-18 | Ray Yang | Adopted the stable canonical filename `Framework_Application_Analysis_Template.md`; updated all active authority and example-document references to canonical paths; aligned the default validated document versions with the current document set; and preserved the analysis method, templates, completion gates, and technical decisions without behavioral change. |
| v1.0.6 | 2026-07-18 | Ray Yang | Corrected the completed-analysis stable filename rule; separated Telemetry replacement semantics from delivery queue policy; split Secure Session responsibility into peer-local Coordinator, Node, and Bootloader ownership; updated active Framework and Protocol versions; clarified cross-implementation and cross-language validation; and labeled repeated non-owning requirements as derived conformance summaries. |
| v1.0.7 | 2026-07-18 | Ray Yang | Distinguished minimum-compatible authority versions from the actual authority versions used for an analysis; separated the stable repository working filename from immutable release, audit, external-delivery, and detached-snapshot filenames; added source commit/tag/Release traceability fields; synchronized the default current Framework Baseline to v1.0.6; and clarified downstream citation requirements without changing the analysis method. |
| v1.0.8 | 2026-07-18 | Ray Yang | Clarified that authority versions shown by the reusable Template are authoring references rather than automatic Product compatibility decisions; changed Project minimum-compatible and version-used fields to explicit completion-time inputs; required compatibility evidence before claiming an earlier minimum version; and corrected review-package traceability without changing the analysis architecture or dual filename policy. |
| v1.0.9 | 2026-07-18 | Ray Yang | Added Product-analysis records for public Discovery privacy, rate limiting, transcript binding, and authenticated revalidation; concrete Handshake and downgrade policy; per-Key-Context Record Counter/Rekey lifecycle; exact Firmware signature encoding; fixed-prefix `minimum_length`; and distinct plaintext Message, security overhead, secured Record, reassembly, and Fragment budgets. Updated authoring-reference versions without changing the Project-specific compatibility-evidence rule. |
| v1.0.10 | 2026-07-18 | Ray Yang | Added Product-analysis records and acceptance questions for exact Fragment Header and reassembly behavior, concrete named Handshake wire structs, Profile allowlist/security-level/deprecation selection, Firmware Update resume authorization bound to transaction/Manifest/Device/Host, and positive minimum-MTU Fragment payload; synchronized authoring-reference versions. |
| v1.0.11 | 2026-07-18 | Ray Yang | Integrated `Coordinator_Software_Engineering_Rules.md` v1.0.1 and `CSharp_Coding_Rules.md` v1.0.1 as conditional Product-analysis authorities; added authoring references, Existing Framework Baseline records, Draft-authority approval handling, detailed completion checks, and Baseline decisions so Coordinator and C# applicability, version, evidence, deviation, or `N/A` rationale cannot be omitted. |
| v1.0.12 | 2026-07-18 | Ray Yang | Updated the Framework authoring reference to v1.0.10 and the Coordinator and C# authoring references to v1.0.2 after Draft-authority, conditional-applicability, and document-version-format clarification; preserved the existing Product-specific compatibility-evidence and approval requirements. |
| v1.0.13 | 2026-07-18 | Ray Yang | Updated authoring references for Framework v1.0.11 and Draft Coordinator/C# rules v1.0.3; required role classification before language selection; prohibited using implementation language as a role proxy; added repository validation and package-traceability evidence to completion checks; and preserved all Product-specific decisions as unresolved until completed by a Project. |
| v1.0.14 | 2026-07-18 | Ray Yang | Completed the Authority Boundary table by adding conditional authority ownership for cross-language Coordinator software engineering and Product-owned C# implementation; clarified that Draft authorities require explicit Project adoption or approved deviation; and preserved all existing application-analysis decisions and completion requirements. |

## 0.3 Template Usage Convention

The following placeholders shall be replaced in a completed Application Analysis:

| Placeholder | Meaning |
|---|---|
| `<Application Name>` | Application or Product name |
| `<Application Domain>` | Application domain |
| `<Coordinator>` | PC Application, Gateway, Host MCU, SBC, mobile Application, or central controller |
| `<Node>` | MCU, embedded Device, subsystem controller, or controlled target |
| `<Device>` | Battery, Charger, Sensor, Motor, ADC, actuator, or other physical Device |
| `<Protocol YAML>` | Project-specific machine-verifiable wire contract |
| `<Application>` | Application name used as a document or directory stem |
| `<Application_Name>` | Filename-safe Application name using underscore separators |
| `<Owner>` | Named person, role, or team responsible for closure |
| `<Evidence>` | Review, test, measurement, generated artifact, or approval record |
| `<YYYY-MM-DD>` | Required calendar date |
| `<TBD>` | Not yet decided |
| `<N/A>` | Not applicable, with rationale |

Maintain a completed analysis in a controlled Git repository under a stable canonical filename:

```text
<Application_Name>_Framework_Application_Analysis.md
```

Examples:

```text
Smart_Battery_Framework_Application_Analysis.md
ECG_Framework_Application_Analysis.md
Motion_Control_Framework_Application_Analysis.md
```

When the approved analysis is exported as an immutable release artifact, audit package, external deliverable, or
detached snapshot, the distributed filename shall include the approved Analysis Version or a controlled Baseline
identifier:

```text
Smart_Battery_Framework_Application_Analysis_v1.2.0.md
Smart_Battery_Framework_Application_Analysis_v1.2.0.pdf
Smart_Battery_Engineering_Baseline_v1.2.0.zip
```

The detached artifact shall record the canonical repository filename and source Git commit, tag, or Release. It is
an immutable distribution copy and shall not become a parallel maintained authority file.

Angle-bracketed examples such as `<START>`, `<READY>`, `<DeviceStatus>`, or `<uint8>` are also placeholders
and shall be replaced or removed when the completed analysis is baselined.

A completed Product analysis shall not retain unresolved placeholders silently. Every remaining `<TBD>` shall
appear in the Open Question or Action Item Register with an Owner and target condition.

## 0.4 Framework Compatibility and Revalidation

The following versions identify the authority set used to author and self-check this reusable Template. They are
authoring references, not automatic compatibility decisions for every Product:

| Authority | Template Authoring Reference Version | Status at Authoring |
|---|---:|---|
| `Coordinator_Node_Control_Framework.md` | `v1.0.11` | Baseline |
| `Protocol_YAML_Definition_Guide.md` | `v1.0.8` | Baseline |
| `Protocol_YAML_Template.md` | `v1.0.8` | Baseline |
| `Coordinator_Software_Engineering_Rules.md` | `v1.0.3` | Draft for Review |
| `Embedded_C_Coding_Rules.md` | `v1.0.15` | Final Baseline |
| `CSharp_Coding_Rules.md` | `v1.0.3` | Draft for Review |

Every completed Application Analysis shall separately record:

```text
Minimum Compatible Version
Version Used for This Analysis
Source Git Commit, Tag, or Release
Compatibility evidence and rationale
```

`Version Used for This Analysis` is the exact authority version actually read and applied.

`Minimum Compatible Version` is the earliest authority version for which the completed Product analysis has
evidence that all required rules, structures, and features remain valid. It shall not be copied from this reusable
Template without compatibility review. It may equal the version used for the analysis. Claiming an earlier minimum
requires documented comparison evidence.

| Item | Value |
|---|---|
| Source Git Commit, Tag, or Release | `<TBD>` |
| Last Compatibility Review | `<YYYY-MM-DD>` |
| Revalidation Status | Valid / Review Required / Invalid |
| Revalidation Owner | `<Owner>` |

Revalidation rules:

| Change | Required Action |
|---|---|
| Framework PATCH | Review corrections for impact on decisions, Gaps, Protocol, architecture, and tests. |
| Framework MINOR | Reassess Reuse Classification, boundaries, Profile, optional capabilities, Gaps, and migration. |
| Framework MAJOR | Repeat the complete Application Analysis and establish a new compatibility plan. |
| Security model change | Revalidate Authentication, Authorization, Session, Key Context, Rekey, Anti-Replay, audit, Application/Bootloader separation, and credential lifecycle. |
| Protocol compatibility change | Regenerate artifacts and rerun Schema Validation, Semantic Lint, compatibility, Golden Vectors, cross-implementation interoperability, and cross-language interoperability for language pairs in scope. |
| State or Fault model change | Revalidate ownership, transitions, recovery, safe state, stale state, UI behavior, and tests. |
| Transport Profile change | Recalculate MTU, Fragmentation, throughput, control latency, Buffer, and Runtime Effective Profile behavior. |
| Firmware Update change | Revalidate Manifest, transaction identity, Session boundary, resume, signature, anti-rollback, rollback, and recovery. |
| Structural rewrite or translation | Prove that every prior normative decision is preserved or intentionally removed and recorded. |

After revalidation, update:

```text
Analysis Baseline Framework Version
Analysis Baseline related-document versions
Source Git Commit, Tag, or Release
Last Compatibility Review
Revalidation Status
Affected Reuse Classifications
Affected Decisions and Gaps
Affected Protocol and generated artifacts
Affected tests and measurements
Application Analysis version history
```

## 0.5 Authority Boundary

This template records application-specific analysis and decisions. It shall not redefine rules owned elsewhere.

| Topic | Authority |
|---|---|
| Coordinator/Node roles, architecture, safety placement, timing principles, and governance | `Coordinator_Node_Control_Framework.md` |
| Cross-language Coordinator software engineering | `Coordinator_Software_Engineering_Rules.md` when approved or explicitly adopted for Project use; otherwise record an approved deviation or `N/A` rationale |
| Embedded C implementation rules | `Embedded_C_Coding_Rules.md` |
| Product-owned C# implementation rules | `CSharp_Coding_Rules.md` when approved or explicitly adopted for Project use; otherwise record an approved deviation or `N/A` rationale |
| Protocol YAML fields, semantics, validation, and compatibility rules | `Protocol_YAML_Definition_Guide.md` |
| Reusable Project Protocol skeleton | `Protocol_YAML_Template.md` |
| Product behavior and domain requirements | Application Profile, SRS, Hazard Analysis, and Product specifications |
| Actual wire contract | `<Application>_protocol.yaml` |
| Actual implementation | Coordinator/Node design specifications and source code |
| Test procedure and result | Test specifications and reports |

One normative rule shall have one authority location.

Architecture, Protocol, security, Firmware Update, and implementation statements repeated in this Template are
derived conformance summaries. They guide analysis but do not override the document that owns the topic.

## 0.6 Analysis Completion Gate

This analysis is complete only when:

- Roles and responsibility boundaries are approved.
- Every Framework area has a Reuse Classification.
- Product-specific behavior has an identified authority document.
- Protocol inputs are sufficient to create or update `<Application>_protocol.yaml`.
- Telemetry and Stream are classified correctly.
- Timing, bandwidth, Buffer, memory, CPU, and Transport feasibility have bounded estimates.
- Safety and security boundaries are explicit.
- Application and Bootloader Session behavior is explicit when Firmware Update is in scope.
- Every Gap, Risk, Open Question, and Action Item has an Owner and status.
- MVP scope and exclusions are approved.
- Acceptance evidence and exit criteria are defined.
- No unresolved contradiction exists among the Framework, Product requirements, Protocol, and implementation plan.

---

# 1. Analysis Objective

## 1.1 Application Identity

| Item | Value |
|---|---|
| Application Name | `<Application Name>` |
| Application Domain | `<Application Domain>` |
| Product or Project | `<TBD>` |
| Repository Working Filename | `<Application_Name>_Framework_Application_Analysis.md` |
| Analysis Version | `v1.0.0` |
| Document Status | Draft for Review / Baseline / Superseded |
| Source Git Commit, Tag, or Release | `<TBD>` |
| Immutable Deliverable Filename | `<N/A until released>` |
| Analysis Owner | `<Owner>` |
| Reviewers | `<TBD>` |
| Target Baseline Date | `<YYYY-MM-DD>` |

## 1.2 Analysis Goal

Describe the core questions this analysis must answer.

Example:

> Evaluate whether `Coordinator_Node_Control_Framework.md` can support `<Application Name>`;
> identify directly reusable capabilities, controlled extensions, Product-specific behavior, responsibility
> boundaries, Protocol inputs, Framework Gaps, risks, evidence, and the minimum implementable scope.

## 1.3 Expected Outputs

The completed analysis shall produce:

```text
System Context
Coordinator and Node Role Definition
Responsibility Boundary
Framework Application Map
Reuse Classification
Application Profile inputs
Protocol YAML input decisions
Command and Response inventory
Telemetry and Stream classification
Event, Alarm, and Fault model
State ownership and State Machines
Timing and bandwidth budget
Transport Profiles
Buffer and resource budget
Security and Access Control model
Firmware Update and Bootloader analysis
UI responsibility and workflow
Mock, Simulator, and Test Harness plan
Required documents and artifacts
MVP scope and development sequence
Framework Gap Register
Risk Register
Decision Register
Open Question and Action Item Register
Acceptance Evidence plan
Final recommendation
```

## 1.4 Decision Criteria

State the criteria used to decide whether the application can proceed.

| Criterion | Required Condition | Evidence |
|---|---|---|
| Architecture fit | No unresolved responsibility contradiction | `<Evidence>` |
| Protocol feasibility | Required contract can be represented by the current Protocol YAML model | `<Evidence>` |
| Timing feasibility | Worst-case budgets meet Product requirements | `<Evidence>` |
| Resource feasibility | Static bounded memory, CPU, storage, and Buffer budgets are feasible | `<Evidence>` |
| Safety feasibility | Node-local safety and safe-state behavior are defined | `<Evidence>` |
| Security feasibility | Required trust, Session, authorization, and update controls are feasible | `<Evidence>` |
| Compatibility | Version and Capability strategy is defined | `<Evidence>` |
| Verification | Required mocks, tests, measurements, and tools are identified | `<Evidence>` |

---

# 2. Input Baseline

## 2.1 Existing Framework Baseline

| Item | Minimum Compatible Version | Version Used for This Analysis | Source Commit, Tag, or Release | Compatibility Evidence |
|---|---:|---:|---|---|
| `Coordinator_Node_Control_Framework.md` | `<TBD after compatibility review>` | `<TBD; authoring reference: v1.0.11>` | `<TBD>` | `<Evidence>` |
| `Protocol_YAML_Definition_Guide.md` | `<TBD after compatibility review>` | `<TBD; authoring reference: v1.0.8>` | `<TBD>` | `<Evidence>` |
| `Protocol_YAML_Template.md` | `<TBD after compatibility review>` | `<TBD; authoring reference: v1.0.8>` | `<TBD>` | `<Evidence>` |
| `Coordinator_Software_Engineering_Rules.md` | `<TBD or N/A>` | `<TBD or N/A; authoring reference: v1.0.3>` | `<TBD or N/A>` | `<Evidence, approved Draft use, deviation, or N/A rationale>` |
| `Embedded_C_Coding_Rules.md` | `<TBD or N/A>` | `<TBD or N/A; authoring reference: v1.0.15>` | `<TBD or N/A>` | `<Evidence or N/A rationale>` |
| `CSharp_Coding_Rules.md` | `<TBD or N/A>` | `<TBD or N/A; authoring reference: v1.0.3>` | `<TBD or N/A>` | `<Evidence, approved Draft use, deviation, or N/A rationale>` |

`Coordinator_Software_Engineering_Rules.md` is required when Coordinator-owned software is in scope.
`CSharp_Coding_Rules.md` is required when Product-owned C# is in scope. If either authority remains `Draft for Review`,
the completed analysis shall record whether the Project explicitly accepts that Draft, applies an approved deviation,
or marks it `N/A` with rationale. A Draft authority shall not be represented as an approved Product Baseline silently.

Additional input artifacts:

| Item | Value |
|---|---|
| Existing Project Protocol | `<TBD>` |
| Existing Reference Implementation | `<TBD>` |
| Existing Mock or Simulator | `<TBD>` |
| Existing Test Vectors | `<TBD>` |
| Existing CI Quality Gates | `<TBD>` |

## 2.2 Project Constraints

| Category | Constraint |
|---|---|
| Coordinator Platform | `<e.g., Windows C# WinForms / .NET Framework 4.7.2 / VS2019>` |
| Node Platform | `<TBD>` |
| MCU or SoC | `<TBD>` |
| RTOS or Runtime | `<TBD>` |
| Primary Transport | `<e.g., USB-CDC>` |
| Future Transports | `<e.g., RS-485 / CAN FD / Ethernet / BLE>` |
| Sample Rate | `<TBD>` |
| Channel Count | `<TBD>` |
| Maximum Record Size | `<TBD>` |
| Control Latency | `<TBD>` |
| Real-Time Requirement | `<TBD>` |
| Static RAM Limit | `<TBD>` |
| Flash Limit | `<TBD>` |
| Storage Requirement | `<TBD>` |
| Safety Requirement | `<TBD>` |
| Security Requirement | `<TBD>` |
| Regulatory Requirement | `<TBD>` |
| Deployment Environment | `<TBD>` |
| Development Toolchain | `<TBD>` |
| Legacy Compatibility | `<TBD>` |

## 2.3 Available Inputs

List each available input and its quality.

| Input | Available | Version or Date | Quality / Limitation | Owner |
|---|---:|---|---|---|
| Product requirements | Yes / No | `<TBD>` | `<TBD>` | `<Owner>` |
| Hardware block diagram | Yes / No | `<TBD>` | `<TBD>` | `<Owner>` |
| Device datasheet | Yes / No | `<TBD>` | `<TBD>` | `<Owner>` |
| Existing Firmware | Yes / No | `<TBD>` | `<TBD>` | `<Owner>` |
| Existing Coordinator software | Yes / No | `<TBD>` | `<TBD>` | `<Owner>` |
| Existing Protocol | Yes / No | `<TBD>` | `<TBD>` | `<Owner>` |
| Interface control document | Yes / No | `<TBD>` | `<TBD>` | `<Owner>` |
| Existing UI mockup | Yes / No | `<TBD>` | `<TBD>` | `<Owner>` |
| Existing test tool | Yes / No | `<TBD>` | `<TBD>` | `<Owner>` |
| Hazard Analysis | Yes / No | `<TBD>` | `<TBD>` | `<Owner>` |
| Security requirements | Yes / No | `<TBD>` | `<TBD>` | `<Owner>` |
| Regulatory requirements | Yes / No | `<TBD>` | `<TBD>` | `<Owner>` |
| Source code | Yes / No | `<TBD>` | `<TBD>` | `<Owner>` |

## 2.4 Assumptions and Evidence Quality

| ID | Assumption | Basis | Impact if Wrong | Validation Action | Owner |
|---|---|---|---|---|---|
| ASM-001 | `<TBD>` | Measurement / Datasheet / Expert judgment / Unknown | `<TBD>` | `<TBD>` | `<Owner>` |

An assumption shall not be silently converted into a requirement or architectural fact.

---

# 3. Application Overview

## 3.1 Problem Statement

Describe the problem, users, environment, and expected value.

```text
<TBD>
```

## 3.2 Primary Use Cases

| Use Case ID | Use Case | Actor | Trigger | Preconditions | Expected Result |
|---|---|---|---|---|---|
| UC-001 | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| UC-002 | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| UC-003 | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |

## 3.3 System Context

```text
User / External System
        |
        v
Coordinator UI or Application
        |
        v
Coordinator Core
        |
        v
Project Protocol and Secure Session
        |
        v
Transport
        |
        v
Node Communication and Application
        |
        v
Service / Adapter / Driver / HAL
        |
        v
Physical Device
```

Answer:

- How many Coordinators may connect?
- How many Nodes exist?
- Can one physical system act as both Node and Coordinator on different links?
- Is a Gateway present?
- Are Cloud, Database, report, or external analysis systems present?
- Is a Bootloader present?
- Is offline operation required?
- Is autonomous Node operation required after disconnect?
- Are multiple Device instances controlled?
- Are production, service, and normal-use modes separate?
- Are multiple transports active simultaneously?

## 3.4 Scope

### In Scope

- `<TBD>`
- `<TBD>`

### Out of Scope

- `<TBD>`
- `<TBD>`

### Deferred

| Item | Reason | Dependency | Revisit Trigger |
|---|---|---|---|
| `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |

## 3.5 Operating Modes

| Mode | Purpose | Allowed Actors | Allowed Operations | Exit Condition |
|---|---|---|---|---|
| Normal | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Maintenance | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Calibration | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Production | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Bootloader | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Recovery | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |

---

# 4. Analysis Principles

The analysis shall follow these principles:

1. Reuse the existing Framework before creating another Transport, Session, Command, Event, Telemetry, Stream,
   Error, Logging, Versioning, or Update mechanism.
2. Product-specific commands, data, states, limits, and workflows belong in the Application Profile, SRS,
   Hazard Analysis, UI specification, or Project Protocol.
3. A capability shall be added to the reusable Framework only when it is valid across multiple applications.
4. UI requirements shall not break Coordinator/Node boundaries.
5. Control, Configuration, Query, Event, Alarm, Fault, Telemetry, Stream, Log, File Transfer, and Firmware Update
   are distinct concerns.
6. Node retains hard real-time control, fundamental safety protection, and local Fault Reaction.
7. UI rendering may drop or aggregate display updates; required recording and control data shall not be silently lost.
8. Protocol YAML remains the Single Source of Truth for the machine-verifiable wire contract.
9. Framework architecture remains the authority for reusable system boundaries.
10. Every application shall complete Framework Gap Analysis.
11. Application-specific needs shall not pollute the reusable Framework.
12. Telemetry and Stream shall be classified by replacement and ordering semantics, not by frequency alone.
13. Application and Bootloader Session and Key Context boundaries shall remain separate.
14. Transport support requires a bounded Transport Profile, not only a Driver.
15. Average throughput does not prove acceptable worst-case control latency.
16. Every queue, Mailbox, Ring Buffer, reassembly path, and variable-length record shall be bounded.
17. A syntax-valid or well-formatted document is not proof that a structural rewrite preserved semantics.
18. Every decision shall have an authority location, rationale, and evidence path.

---

# 5. Framework Application Map

## 5.1 Layer Mapping

| Area | Existing Framework Responsibility | Application-Specific Input | Classification | Authority Document |
|---|---|---|---|---|
| Coordinator role | System coordination and Node management | `<TBD>` | `<TBD>` | Framework / Analysis |
| Node role | Local execution and safety | `<TBD>` | `<TBD>` | Framework / Analysis |
| Transport | Link delivery and bounded profile | `<TBD>` | `<TBD>` | Framework / Transport SDD |
| Protocol | Wire semantics | `<TBD>` | `<TBD>` | Project Protocol YAML |
| Secure Session | Authentication, integrity, anti-replay, Key Context | `<TBD>` | `<TBD>` | Security Design / Protocol |
| Command / Response | Request, validation, execution result | `<TBD>` | `<TBD>` | Application Profile / Protocol |
| Event / Alarm / Fault | Asynchronous semantic reporting | `<TBD>` | `<TBD>` | Application Profile / Protocol |
| Telemetry | Replaceable summarized state | `<TBD>` | `<TBD>` | Application Profile / Protocol |
| Stream | Ordered records or samples | `<TBD>` | `<TBD>` | Application Profile / Protocol |
| State Machines | State ownership and transitions | `<TBD>` | `<TBD>` | SRS / SDD |
| Firmware Update | Bootloader and Update transaction | `<TBD>` | `<TBD>` | Update SDD / Protocol |
| Logging and audit | Operational and security evidence | `<TBD>` | `<TBD>` | Logging / Security specification |
| Code Generation | Deterministic generated contracts | `<TBD>` | `<TBD>` | Protocol / Generator |
| Validation | Schema, Semantic Lint, tests, measurement | `<TBD>` | `<TBD>` | Test Plan |

## 5.2 Reuse Classification

Use one classification for every Framework capability:

| Classification | Meaning |
|---|---|
| Direct Reuse | Reused without semantic change |
| Configured Reuse | Reused through bounded configuration |
| Extended Reuse | Existing abstraction retained with an optional reusable extension |
| Application-Specific | Belongs only to this Application Profile or Product |
| Framework Gap | Missing reusable capability that may apply across applications |
| Replace | Existing approach is unsuitable; replacement requires rationale and compatibility analysis |
| Not Applicable | Not needed, with rationale |

`Replace` shall not be selected merely because a team prefers another API, coding style, or Vendor library.

## 5.3 Module Reuse Table

| Module or Capability | Classification | Reason | Required Change | Dependency | Evidence |
|---|---|---|---|---|---|
| Transport Manager | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |
| Session Manager | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |
| Command Dispatcher | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |
| Event Publisher | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |
| Telemetry Router | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |
| Stream Pipeline | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |
| Logger | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |
| Update Coordinator | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |
| Mock Transport | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |

## 5.4 Dependency and Boundary Review

For every reused or extended module, verify:

```text
No UI dependency in Protocol or Transport
No Vendor handle in Application contract
No direct hardware operation in Command Dispatcher
No Product policy in generic Driver
No unbounded external-length allocation
No Application key use in Bootloader
No duplicate normative definition across documents
No generated-file manual edit
```

---

# 6. Application Profile and Protocol Inputs

## 6.1 Profile Identity

| Item | Value |
|---|---|
| Profile Name | `<Application Name> Application Profile` |
| Profile ID | `<TBD>` |
| Profile Version | `v1.0.0` |
| Minimum Compatible Framework Version | `<copy the approved minimum from Section 2.1>` |
| Analysis Baseline Framework Version | `<copy the actual version used from Section 2.1>` |
| Protocol YAML | `<Application_Name>_protocol.yaml` |
| Protocol Version | `V1.0.0RC01` |
| Compatibility Policy | `<TBD>` |
| Capability Strategy | `<TBD>` |

## 6.2 Services

| Service ID | Service Name | Namespace | Responsibility | Owner |
|---|---|---|---|---|
| `<TBD>` | `<TBD>` | framework / application / bootloader | `<TBD>` | Coordinator / Node |
| `<TBD>` | `<TBD>` | framework / application / bootloader | `<TBD>` | Coordinator / Node |

## 6.3 Commands and Responses

Classify commands as:

```text
Query
Configuration
Control
Calibration
Maintenance
Diagnostics
File or Log Transfer
Firmware Update
Safety-Related Control
```

| Command | Direction | Preconditions | Request Data | Response Data | Timeout | Retry | Idempotency | Privilege |
|---|---|---|---|---|---:|---|---|---|
| `<GET_STATUS>` | C -> N | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | Read |
| `<SET_CONFIG>` | C -> N | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | Configure |
| `<START>` | C -> N | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | Control |
| `<STOP>` | C -> N | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | Control |

For safety- or state-sensitive commands, also define:

```text
Allowed state
Maximum command age
Duplicate policy
Operation or Transaction ID
Expected current state
Fail-safe behavior
Audit requirement
```

## 6.4 Telemetry

Use Telemetry only for complete summarized state whose older unsent value may be replaced.

| Name | Producer | Trigger or Nominal Rate | Maximum Rate | Replacement Policy | Delivery Queue Policy | Timestamp | Priority | Loss Policy | Maximum Record Size |
|---|---|---|---|---|---|---|---|---|---:|
| `<TBD>` | Node | `<TBD>` | `<TBD>` | latest_value_only / coalesce_by_key | single_pending / bounded_latest_per_key | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |

Verify:

- The Payload is independently usable.
- A newer value may replace an older unsent value only when declared.
- Replacement semantics are separate from queue capacity and overflow implementation.
- `queue_all` is not used as a Telemetry replacement policy.
- A partial delta is not mislabeled as latest-value-only Telemetry.
- Freshness and stale-state behavior are defined.

## 6.5 Stream

Use Stream for ordered samples, records, frames, chunks, or deltas where continuity matters.

| Name | Producer | Sample Rate | Samples per Record | Sequence | Timestamp | Ordering | Loss Policy | Maximum Record Size |
|---|---|---:|---:|---|---|---|---|---:|
| `<TBD>` | Node | `<TBD>` | `<TBD>` | Required | Required | `<TBD>` | `<TBD>` | `<TBD>` |

Verify:

- Loss, duplication, reordering, and wrap behavior are defined.
- Record aggregation and maximum non-preemptible time are bounded.
- Every redundant count, length, offset, or derived field has an explicit relationship and mismatch policy.
- Decoder arithmetic is overflow-checked before array access.
- Remaining Payload length and destination capacity are validated.

## 6.6 Event, Alarm, and Fault

| Type | Name | Severity | Latching | Acknowledge | Clear or Reset Condition | Required Action |
|---|---|---|---|---|---|---|
| Event | `<TBD>` | Info | No | No | N/A | Log / notify |
| Alarm | `<TBD>` | Warning / Error | Yes / No | Yes / No | `<TBD>` | `<TBD>` |
| Fault | `<TBD>` | Critical | Yes | Yes | `<TBD>` | Safe state / limited operation |

Do not collapse all Device Faults into a generic unstructured error.

## 6.7 Data Models

Each model shall define:

```text
Field name
Wire type
Unit
Range
Resolution
Scaling
Default
Invalid value
Endianness
Timestamp
Quality flags
Source
Update semantics
Persistence
Compatibility
```

| Model | Field | Type | Unit | Valid Range | Invalid Value | Source | Authority |
|---|---|---|---|---|---|---|---|
| `<DeviceStatus>` | `<state>` | `<uint8>` | N/A | `<TBD>` | `<TBD>` | Node | Protocol |
| `<Measurement>` | `<value>` | `<int32>` | `<TBD>` | `<TBD>` | `<TBD>` | Device | Protocol |

## 6.8 Protocol YAML Creation

Do not create an independent simplified YAML model in this analysis.

Create the Project Protocol by copying and tailoring:

```text
Protocol_YAML_Template.md
```

Validate it according to:

```text
Protocol_YAML_Definition_Guide.md
```

The completed analysis shall provide the inputs required for:

```text
Namespaces
Services
Messages
Capabilities
Types
Enums
Bitsets
Errors
Transport Profiles
Sequence and Timestamp policies
Security Model and Key Contexts
Compatibility
Code Generation
Test Vectors
```

## 6.9 Compatibility and Capability

| Item | Decision |
|---|---|
| Protocol MAJOR policy | `<TBD>` |
| Protocol MINOR policy | `<TBD>` |
| Protocol PATCH policy | `<TBD>` |
| Unknown Message policy | `<TBD>` |
| Unknown Enum policy | `<TBD>` |
| Unknown bit policy | `<TBD>` |
| Unknown trailing policy | `<TBD>` |
| Capability discovery | `<TBD>` |
| Deprecation policy | `<TBD>` |
| Published ID reuse | Prohibited |

## 6.10 Code Generation Inputs

| Target | Required | Generated Artifacts | Handwritten Boundary |
|---|---:|---|---|
| Embedded C Node | Yes / No | Constants, types, codecs, validation | Application Adapter and Services |
| C# Coordinator | Yes / No | Constants, models, codec, validation | UI and workflow |
| Java Coordinator | Yes / No | Constants, models, codec, validation | Platform and Application |
| Documentation | Yes / No | Message and field references | Rationale and Product behavior |
| Test Vectors | Yes / No | Golden and boundary vectors | Scenario and acceptance tests |

Generated files shall be deterministic, traceable, and not manually edited.

---

# 7. Responsibility Boundary

## 7.1 System Role Definition

| Relationship | Coordinator | Node | Connection Initiator | Event Publisher | State Authority |
|---|---|---|---|---|---|
| `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |

System role, Message role, Event role, Transport direction, connection role, implementation language, and platform are distinct. Embedded C shall not be treated as synonymous with Node, and C#, Java, C++, Python, or Rust shall not be treated as synonymous with Coordinator. Mixed-role products shall record the boundary between roles.

## 7.2 Responsibility Matrix

Use `A` for accountable authority, `R` for execution responsibility, `C` for consulted, and `I` for informed.

| Responsibility | UI | Coordinator Core | Node Application | Bootloader / Update | Service / Adapter | Driver / HAL | Physical Device |
|---|---:|---:|---:|---:|---:|---:|---:|
| User interaction | A/R | C | I | I | I | I | I |
| Link and reconnect coordination | I | A/R | R | R during update | C | I | I |
| Coordinator-side Secure Session state | I | A/R | C | C during update | I | I | I |
| Node Application Session acceptance and local state | I | C | A/R | I | C | I | I |
| Bootloader Session acceptance and local state | I | C | I | A/R | C | I | I |
| Protocol encode/decode | I | A/R | R | R for update Protocol | C | I | I |
| Command authorization | C | R | A/R for Application | A/R for update | I | I | I |
| Real-time control | I | I | A/R | I | R | C | C |
| Safety protection | I | I | A/R | R during update | R | C | R |
| Telemetry acquisition | I | C | A/R | I | R | R | C |
| Stream acquisition | I | C | A/R | I | R | R | C |
| UI rendering | A/R | C | I | I | I | I | I |
| Persistent configuration | C | C | A/R | I | C | I | I |
| Register access | I | I | I | I | C | A/R | C |
| Logging | R | A/R | R | R | C | I | I |
| Fault Reaction | I | C | A/R | R during update | R | C | R |
| Firmware Update coordination | I | A/R | C | R | C | I | I |
| Firmware image verification | I | C | I | A/R | C | C | I |

The Project may tailor this matrix but shall not assign two independent authorities for one state or safety decision.

## 7.3 Boundary Questions

Answer explicitly:

1. Which controls can only be executed locally by the Node?
2. Which controls may be requested by the Coordinator but shall be revalidated by the Node?
3. Which state comes directly from the physical Device?
4. Which state is derived by the Node?
5. Which display-only values are calculated by the Coordinator?
6. What does the Node do when the Coordinator disconnects?
7. What happens when the Node restarts?
8. Can the UI write a Device register directly?
9. Are Maintenance, Engineering, Production, and Normal modes separated?
10. Which actor may clear a Fault?
11. Which actor owns persistent configuration?
12. Which state is authoritative after reconnect?
13. Which operations require read-back verification?
14. Is an out-of-band emergency path required?

## 7.4 Anti-Patterns

Reject designs in which:

```text
UI directly accesses Device registers
Command Dispatcher directly operates hardware
Coordinator is required for fundamental Node safety
PC and Node independently infer the same authoritative state
UI refresh rate is treated as acquisition rate
Telemetry and Stream are treated as synonyms
Device Fault is reduced to an unstructured generic error
Application Profile redefines Framework Session or Transport rules
Product policy is embedded in a generic Driver
Application keys are reused by Bootloader
```

---

# 8. Functional Analysis

## 8.1 Monitoring

| Function | Source | Category | Update Semantics | Unit | Freshness | History | Threshold |
|---|---|---|---|---|---|---|---|
| `<TBD>` | `<TBD>` | Telemetry / Stream / Query / Event | `<TBD>` | `<TBD>` | `<TBD>` | Yes / No | `<TBD>` |

## 8.2 Configuration

| Parameter | Authority | Read / Write | Runtime Change | Persistent | Range Validation | Read-Back |
|---|---|---|---|---|---|---|
| `<TBD>` | Node / Device | R / W | Yes / No | Yes / No | `<TBD>` | Required / Optional |

Define atomicity and rollback when multiple parameters form one configuration transaction.

## 8.3 Control

| Control | Preconditions | Command | State-Sensitive | Success Criteria | Failure Action | Audit |
|---|---|---|---:|---|---|---:|
| `<START>` | `<TBD>` | `<TBD>` | Yes | `<TBD>` | `<TBD>` | Yes / No |
| `<STOP>` | `<TBD>` | `<TBD>` | Yes | `<TBD>` | `<TBD>` | Yes / No |

## 8.4 Logging

Define:

```text
Coordinator log
Node log
Protocol log
User-operation log
Device Event log
Alarm history
Fault history
Configuration-change history
Measurement data
Debug trace
Security audit
Firmware Update transaction log
```

For each log, define capacity, persistence, privacy, integrity, rollover, export, and clock source.

## 8.5 Data Recording

| Data | Source Category | Format | Sample or Record Rate | Timestamp | Loss Allowed | Retention | Integrity |
|---|---|---|---:|---|---:|---|---|
| Raw samples | Stream | Binary / `<TBD>` | `<TBD>` | Required | No / bounded | `<TBD>` | `<TBD>` |
| Status | Telemetry | CSV / DB / `<TBD>` | `<TBD>` | Required | `<TBD>` | `<TBD>` | `<TBD>` |
| Event | Event | JSON / DB / `<TBD>` | On occurrence | Required | No | `<TBD>` | `<TBD>` |

Display Buffer and recording Buffer shall be separated when their loss policies differ.

## 8.6 Playback and Offline Analysis

Evaluate:

```text
Offline playback
Time navigation
Zoom and cursor measurement
Event, Alarm, and Fault overlays
Configuration replay
Export
Report generation
Reproduction of a failure scenario
Cross-version data compatibility
Large-file handling
```

## 8.7 Calibration and Maintenance

| Function | Mode | Required Role | Preconditions | Persistent Effect | Verification |
|---|---|---|---|---|---|
| `<TBD>` | Calibration / Maintenance | `<TBD>` | `<TBD>` | Yes / No | `<TBD>` |

Calibration and maintenance behavior shall not be hidden inside an unrestricted diagnostic command.

---

# 9. Communication, Timing, Bandwidth, and Resources

## 9.1 Message Categories

| Category | Typical Use | Reliability | Ordering | Priority | Replaceable |
|---|---|---|---|---|---:|
| Control | Start, Stop, Enable | Required | Required | High | No |
| Configuration | Set parameter | Required | Required | Medium | No |
| Query | Get status | Required | Correlated | Medium | N/A |
| Event | One-time occurrence | Required by Product | Required by Product | High / Normal | No |
| Alarm | Actionable abnormal condition | Required | Required | High | No |
| Fault | Safety or functional failure | Required | Required | Highest | No |
| Telemetry | Complete summarized state | Product-defined | Usually latest-state oriented | Normal | Yes when declared |
| Stream | Ordered samples or records | Product-defined | Required | Normal / High | No |
| Heartbeat | Link and Session health | Required | Sequence-defined | High | N/A |
| File / Log | Bulk transfer | Product-defined | Required | Low | No |
| Firmware Update | Manifest and image chunks | Required | Transaction-defined | Controlled | No |

## 9.2 Data Flow

```text
Physical Device
        |
        v
Driver / HAL
        |
        v
Node Service and Application
        |
        v
Generated Protocol Contract
        |
        v
Secure Session
        |
        v
Transport
        |
        v
Coordinator Protocol and Controller
        |
        v
Application Data Model
        |
        +--> UI
        +--> Logger
        +--> Recorder
        +--> Analyzer
```

## 9.3 Timing Budget

| Stage | Target | Worst Case Allowed | Measurement Method | Action if Exceeded |
|---|---:|---:|---|---|
| Device acquisition | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Node processing | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Record assembly | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Security processing | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Transport waiting | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Serialization or air time | `<TBD>` | `<TBD>` | Calculation / measurement | `<TBD>` |
| Coordinator decode | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Application dispatch | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| UI display | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Control response | `<TBD>` | `<TBD>` | End-to-end measurement | `<TBD>` |

## 9.4 Bandwidth Budget

Record:

| Item | Value |
|---|---:|
| Channel count | `<TBD>` |
| Bits per sample | `<TBD>` |
| Sample rate | `<TBD>` |
| Samples per record | `<TBD>` |
| Application metadata | `<TBD>` bytes |
| Protocol header | `<TBD>` bytes |
| Session / security header | `<TBD>` bytes |
| Authentication tag | `<TBD>` bytes |
| Fragmentation overhead | `<TBD>` bytes |
| Retry allowance | `<TBD>` % |
| Reserved control bandwidth | `<TBD>` % |
| Calculated average throughput | `<TBD>` |
| Calculated peak throughput | `<TBD>` |
| Measured throughput | `<TBD>` |

For every candidate aggregation profile, record:

| Profile | Record Period | Record Size | Records/s | Average Throughput | Max Blocking Time | Control Latency Result |
|---|---:|---:|---:|---:|---:|---|
| `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | Pass / Fail |

## 9.5 Transport Profile

| Property | Requirement |
|---|---|
| Transport | `<TBD>` |
| Minimum MTU | `<TBD>` |
| Maximum MTU | `<TBD>` |
| Effective Payload | `<TBD>` |
| Minimum throughput | `<TBD>` |
| Maximum control latency | `<TBD>` |
| Maximum plaintext Message size | `<TBD>` |
| Protocol Record header | `<TBD>` bytes |
| Security header | `<TBD>` bytes |
| Authentication Tag | `<TBD>` bytes |
| Maximum security overhead | `<TBD>` bytes |
| Maximum secured Record size | `<TBD>` |
| Maximum Transport reassembly Buffer | `<TBD>` |
| Fragment header | `<TBD>` bytes |
| Maximum Fragment payload | `<TBD>` |
| Maximum Fragments per secured Record | `<TBD>` |
| Reassembly timeout | `<TBD>` |
| Link-loss behavior | `<TBD>` |

For dynamically negotiated Transports, define the Runtime Effective Profile and the action when negotiated
conditions cannot support the requested Stream.

## 9.6 Buffering

| Buffer | Producer | Consumer | Static Capacity | High-Water Mark | Overflow Policy | Recovery |
|---|---|---|---:|---:|---|---|
| Node acquisition | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Transport TX | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Coordinator receive | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Recording | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| UI display | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Reassembly | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | Abort / reject | `<TBD>` |

## 9.7 Node Resource Budget

| Resource | Budget | Estimated | Measured | Margin | Evidence |
|---|---:|---:|---:|---:|---|
| Static RAM | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |
| Flash | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |
| Task stack | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |
| Protocol workspace | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |
| Crypto workspace | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |
| Reassembly Buffer | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |
| Update metadata | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |
| CPU worst case | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` |

---

# 10. State Machines

## 10.1 State Domains

Do not collapse these into one state variable:

```text
Link State
Secure Session State
Application State
Device State
Safety State
Recording State
Firmware Update Transaction State
Bootloader State
UI State
```

## 10.2 Representative System Flow

```text
DISCONNECTED
    |
    v
CONNECTING
    |
    v
LINK_ESTABLISHED
    |
    v
HANDSHAKE
    |
    v
SESSION_READY
    |
    v
IDENTIFYING
    |
    v
RECONCILING
    |
    v
READY
    |
    v
RUNNING
    |
    v
STOPPING
    |
    v
READY
```

Recovery paths:

```text
ANY_OPERATIONAL_STATE
    |
    v
DEGRADED / RECOVERABLE_ERROR
    |
    v
RECOVERING
    |
    +--> READY
    +--> DISCONNECTED
```

Fault path:

```text
ANY_STATE
    |
    v
FAULT
    |
    v
SAFE_STATE
```

## 10.3 State Definition

| State | Owner | Entry Action | Allowed Commands | Exit Condition | Timeout | Failure Action |
|---|---|---|---|---|---|---|
| `<DISCONNECTED>` | `<TBD>` | `<TBD>` | `<CONNECT>` | `<TBD>` | `<TBD>` | `<TBD>` |
| `<READY>` | Node | `<TBD>` | `<START>` | `<TBD>` | `<TBD>` | `<TBD>` |
| `<RUNNING>` | Node | `<TBD>` | `<STOP>` | `<TBD>` | `<TBD>` | `<TBD>` |

## 10.4 Domain-Specific State Machines

Evaluate:

```text
Measurement
Charging
Discharging
Motion Control
Calibration
Data Recording
Fault Recovery
Firmware Update
Bootloader
Production Test
```

## 10.5 State Ownership

| State Machine | Authority | Coordinator Mirror | Persistence | Reconciliation |
|---|---|---:|---|---|
| Link | Coordinator and Node local link managers | Yes | No | Reconnect |
| Secure Session | Each peer | Yes | No | Re-handshake |
| Device operation | Node | Yes | Product-defined | Query Node |
| Safety | Node / physical Device | Read-only | Product-defined | Query and verify |
| UI | UI | No | No | Rebuild from authoritative state |
| Update transaction | Bootloader / Update subsystem | Yes | Required for resume | Reauthenticate and revalidate |

A mirrored state shall not become a second authority.

---

# 11. Error, Recovery, and Safety

## 11.1 Error Categories

| Category | Example | Authority | Immediate Action | Recovery |
|---|---|---|---|---|
| Transport | Disconnect or framing error | Link Manager | Mark link unavailable | Reconnect |
| Session | Authentication or expiration | Session Manager | Reject traffic | Re-handshake |
| Protocol | Unsupported or malformed Message | Protocol | Reject | Continue / disconnect by policy |
| Application | Invalid operating state | Node Application | Reject command | Correct state |
| Device | Hardware Fault | Node / Device | Safe or degraded state | Product-defined |
| Data | Gap, stale, invalid quality | Data path | Mark invalid or incomplete | Query / resync |
| UI | Rendering failure | UI | Preserve receive path | Restart view |
| Storage | Disk full | Recorder | Stop or rotate recording | User or automatic cleanup |
| Security | Replay or integrity failure | Security subsystem | Reject and log | Disconnect / lockout |
| Update | Signature or flash failure | Bootloader | Abort safely | Resume / rollback / recovery |

## 11.2 Failure Scenarios

Analyze at least:

```text
Link interruption
Coordinator restart
Node restart
Physical Device reset
Session timeout
Authentication failure
Telemetry timeout
Stream gap
Command timeout
Late response
Command rejection
Protocol version mismatch
Unsupported Capability
Integrity failure
Replay detection
Buffer overflow
Disk full
UI thread blocking
Unsafe control request
Device Fault
Partial configuration update
Firmware/configuration mismatch
Unexpected state transition
Power loss during Firmware Update
Boot failure after update
```

## 11.3 Recovery Matrix

| Failure | Detection | Immediate Action | Automatic Recovery | User Action | Audit / Log |
|---|---|---|---|---|---|
| Link lost | Heartbeat timeout | Mark state stale | Reconnect | Check connection | Required |
| Node reset | Session or boot identity change | Stop unsafe operations | Re-handshake and reconcile | Confirm state | Required |
| Command timeout | Request timer | Mark result unknown or failed | Retry only if safe | Inspect / retry | Required |
| Invalid state | Response code | Reject | No | Correct state | Required |
| Stream gap | Sequence check | Mark gap | Continue / restart by policy | Review | Required |
| Update interruption | Link or power failure | Preserve committed progress | Resume after reauthentication | Reconnect | Required |

## 11.4 Safety Analysis Questions

- Which hazards require local Node protection?
- Which controls require read-back verification?
- Which commands shall reject stale requests?
- Which actions require an independent emergency path?
- What is the safe state?
- What happens on Coordinator disconnect?
- What happens on loss of power?
- What happens when the Node cannot determine current Device state?
- Can a communication retry create duplicate physical action?
- Which output limits are enforced locally?
- Which Faults are latched?
- Which recovery operations require authorization?

## 11.5 Safety Rules

- A safety-related command shall be revalidated by the Node.
- STOP, Disable, or Emergency behavior shall follow Hazard Analysis and shall not be delayed by an unnecessary
  ordinary retry or token flow.
- Reconnect does not equal Application recovery; authoritative state shall be reconciled.
- Stale data shall not be displayed or consumed as current.
- Fundamental safety shall not depend solely on the Coordinator, UI, Wi-Fi, BLE, or an ordinary in-band command.
- Firmware Update shall not suspend required safety protection.

---

# 12. Security and Access Control

## 12.1 Security Objectives

Select and justify:

```text
Coordinator authentication
Node authentication
Mutual authentication
Confidentiality
Integrity
Anti-Replay
Session expiration
Rekey
Command authorization
Role-based access
Sensitive-data protection
Audit
Credential provisioning
Credential rotation
Credential revocation
Secure Firmware Update
Application and Bootloader separation
```

## 12.2 Access Roles

| Role | Typical Actor | Allowed Operations | Prohibited Operations |
|---|---|---|---|
| Read Only | Observer | Status and approved Telemetry | Configuration and control |
| Operator | Normal user | Approved operational controls | Engineering and security administration |
| Configurator | Authorized engineer | Read/write configuration | Credential administration |
| Maintenance | Service engineer | Diagnostics and maintenance | Security authority changes unless approved |
| Updater | Authorized update service | Firmware Update | General control unless separately authorized |
| Administrator | Security owner | Roles, credentials, policy | `<TBD>` |

## 12.3 Operation Security Matrix

| Operation | Authentication | Role | Confidentiality | Integrity | Anti-Replay | Audit | Failure Action |
|---|---|---|---|---|---|---|---|
| Read Telemetry | `<TBD>` | Read Only | `<TBD>` | Required / `<TBD>` | `<TBD>` | `<TBD>` | Reject / limit |
| Change configuration | Required | Configurator | Product-defined | Required | Required | Yes | Reject and log |
| Start control | Required | Operator | Product-defined | Required | Required | Yes | Safe rejection |
| Stop control | `<TBD>` | Operator | `<TBD>` | Required | Required | Yes | Fail-safe policy |
| Clear Fault | Required | Operator / Maintenance | Product-defined | Required | Required | Yes | Preserve Fault |
| Diagnostics | Required | Maintenance | Product-defined | Required | Required | Yes | Reject and log |
| Firmware Update | Required | Updater | Product-defined | Required | Required | Yes | Abort safely |
| Credential management | Required | Administrator | Required | Required | Required | Yes | Reject and security event |

## 12.4 Public Discovery and Authenticated Identity

| Item | Requirement |
|---|---|
| Public Discovery required | Yes / No |
| Exposure rationale | `<TBD>` |
| Permitted unauthenticated fields | `<TBD>` |
| Permanent Device identifier exposed publicly | Prohibited / `<Approved exception>` |
| Ephemeral Discovery ID length and rotation | `<TBD>` |
| Rate-limit window and burst | `<TBD>` |
| Excess-request behavior | `<TBD>` |
| Discovery result authoritative | No |
| Handshake transcript binding | Required / `<TBD>` |
| Authenticated post-Session identity revalidation | Required / `<TBD>` |
| Authenticated Capability revalidation | Required / `<TBD>` |

Unauthenticated Discovery hints shall not authorize downgrade, Product behavior, or permanent Device tracking.

## 12.5 Application Session and Handshake

| Item | Requirement |
|---|---|
| Authentication method | `<TBD>` |
| Key Agreement | `<Concrete approved value>` |
| KDF | `<Concrete approved value>` |
| Cipher suite | `<Concrete approved value>` |
| Proof format | `<Concrete approved value>` |
| Credential model | `<Concrete approved value>` |
| Profile ID equality rule | Required |
| Minimum approved Profile | `<TBD>` |
| Silent fallback | Prohibited |
| Canonical transcript fields | `<TBD against Framework minimum>` |
| Session timeout | `<TBD>` |
| Session resumption | Allowed / Prohibited / Conditional |
| Multiple Coordinator policy | `<TBD>` |
| Time synchronization dependency | `<TBD>` |

## 12.6 Record Counter and Rekey Profiles

For every Application and Bootloader Key Context, record:

| Key Context | Width | Initial | Soft Threshold | Rekey Deadline | Hard Limit | Persistence | Gap Policy | Exhaustion | Atomic Cutover |
|---|---:|---:|---:|---:|---:|---|---|---|---|
| `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |

The Hard Limit is uncrossable. Counter reset is allowed only after new keys and a new Epoch are atomically active.

## 12.7 Application and Bootloader Boundary

Define:

1. Whether Application and Bootloader use independent Sessions.
2. Which long-term identity or trust anchor may be shared.
3. How Bootloader entry is authorized.
4. Whether Bootloader performs a new Handshake.
5. How Application keys are invalidated.
6. How Bootloader Key Contexts are derived.
7. How Security Events persist across reset.
8. How Update Transaction state remains separate from Session state.
9. How reconnect and Rekey reauthenticate and revalidate the transaction.
10. How rollback and recovery remain authorized.

Application runtime Session keys shall not be used by Bootloader.

## 12.8 Security Audit

Each record should include:

| Field | Meaning |
|---|---|
| Timestamp | Event time |
| Session or Epoch | Related Secure Session |
| Actor and Role | Authenticated identity and authorization role |
| Operation | Attempted or completed action |
| Target | Node, Device, parameter, image, or credential |
| Result | Success / Rejected / Failed |
| Reason | Policy or error reason |
| Source | Coordinator / Node / Bootloader |
| Integrity | Audit protection status |

Secrets and raw key material shall not be logged.

---

# 13. Firmware Update and Bootloader

## 13.1 Scope Decision

| Item | Decision |
|---|---|
| Firmware Update required | Yes / No / Future |
| Bootloader already exists | Yes / No |
| A/B image layout | Yes / No |
| External staging | Yes / No |
| Recovery interface | `<TBD>` |
| Signed image required | Required when Firmware Update is in scope; N/A otherwise |
| Anti-rollback required | Yes / No |
| Resume required | Yes / No |
| Wireless update supported | Yes / No |

## 13.2 Update Transaction

Define:

```text
Update Transaction ID
Image ID and type
Manifest hash
Expected image size
Expected image hash
Security version
Confirmed committed offset
Chunk size
Chunk duplicate policy
Resume policy
Transaction timeout
```

The Update Transaction shall not be identified only by the current Secure Session or offset.

## 13.3 Manifest and Verification

| Manifest Field | Required | Validation |
|---|---:|---|
| Device model | Yes / No | Match target |
| Hardware Revision | Yes / No | Approved range |
| Firmware version | Yes | Version policy |
| Image size | Yes | Partition and capacity |
| Image hash | Yes | Complete-image verification |
| Digital signature | Required when Firmware Update is in scope | Trust anchor and approved signature policy |
| Signature algorithm | Yes | `<TBD>` |
| Message preparation | Yes | `<TBD>` |
| Exact wire encoding | Yes | `<TBD>` |
| Exact signature length | Yes | `<TBD>` bytes |
| Canonicality / ECDSA low-S policy | Conditional | `<TBD>` |
| Minimum Bootloader version | Conditional | Compatibility |
| Protocol requirement | Conditional | Compatibility |
| Security version | Conditional | Anti-rollback |

CRC may detect accidental corruption. CRC shall not replace digital signature verification.

## 13.4 Update Flow

```text
APPLICATION_RUNNING
        |
        v
PREPARE_UPDATE
        |
        v
ENTER_BOOTLOADER
        |
        v
APPLICATION_SESSION_INVALIDATED
        |
        v
BOOTLOADER_HANDSHAKE
        |
        v
AUTHENTICATE_UPDATE
        |
        v
CREATE_OR_RESTORE_TRANSACTION
        |
        v
RECEIVE_IMAGE
        |
        v
VERIFY_IMAGE
        |
        v
MARK_PENDING
        |
        v
REBOOT
        |
        v
SELF_TEST
        |
        +--> CONFIRM_AND_COMMIT
        +--> ROLLBACK
```

## 13.5 Resume, Rekey, and Reconnect

After reconnect or Rekey:

- Reauthenticate the peer.
- Establish a valid Bootloader Session.
- Revalidate Update Transaction identity.
- Confirm committed progress.
- Reject mismatched Manifest, Image ID, hash, or security version.
- Resume only from Bootloader-confirmed state.

## 13.6 Safe Update and Recovery

Define:

```text
Allowed outputs during update
Actuator safe state
Power requirements
Watchdog behavior
Power-loss behavior
Maximum non-preemptible flash operation
Pending-image timeout
Self-test criteria
Rollback trigger
Recovery-entry method
Operator feedback
```

Do not erase the only valid Application image without an approved Recovery Path.

---

# 14. UI and External-System Planning

## 14.1 UI Principles

1. Display authoritative confirmed Device state.
2. `Command sent` does not mean `Command accepted` or `Operation completed`.
3. Show Pending, Accepted, Completed, Failed, Rejected, and Unknown-result states where relevant.
4. Make stale or invalid data visible.
5. Do not rely only on color for Alarm or Fault distinction.
6. Decouple receive, decode, recording, and UI rendering.
7. Page or tab switching shall not interrupt acquisition or recording.
8. UI validation does not replace Node validation.
9. High-risk actions require approved preconditions and confirmation behavior.
10. UI state shall be rebuilt from authoritative system state after reconnect.

## 14.2 Page Inventory

| Page | Purpose | Main Data | Main Actions | Update Semantics |
|---|---|---|---|---|
| Overview | System summary | State, health, connection | Connect / Start / Stop | `<TBD>` |
| Monitoring | Live data | Telemetry / Stream | View / filter | `<TBD>` |
| Control | Operational control | State and setpoint | Set / enable / disable | On demand |
| Configuration | Parameter management | Configuration | Read / write / save | On demand |
| Alarm / Fault | Abnormal condition | Active and history | Acknowledge / clear | On occurrence |
| Recording | Data capture | Recorder state | Start / stop / export | `<TBD>` |
| Diagnostics | Service functions | Diagnostics and logs | Test / inspect | `<TBD>` |
| Firmware Update | Update workflow | Version and progress | Select / verify / update | Controlled |
| About | Identity and versions | HW / FW / Protocol | Export | On demand |

## 14.3 Operation Flow

```text
User Action
    |
    v
UI Validation
    |
    v
Coordinator Request
    |
    v
Node Authorization and State Validation
    |
    v
Local Device Action
    |
    v
Node Result and State
    |
    v
Coordinator Reconciliation
    |
    v
UI Confirmation
```

## 14.4 External Systems

| External System | Interface | Data | Authority | Failure Behavior |
|---|---|---|---|---|
| Database | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Cloud | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Report Generator | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |
| Production System | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |

External integration shall not become an undocumented safety or state authority.

---

# 15. Mock, Simulator, and Test Harness

## 15.1 Required Components

Evaluate:

```text
Mock Node
Mock Coordinator
Mock Transport
Device Simulator
Battery or Charger Simulator
Sensor Signal Generator
Motor Plant Simulator
Virtual Transport
Protocol Fuzzer
Fault Injector
Recording Playback Source
Packet Recorder
Packet Decoder
Hardware-in-the-Loop
```

## 15.2 Scenarios

| Scenario | Expected Behavior | Evidence |
|---|---|---|
| Normal startup | Connect, authenticate, identify, reconcile, configure, and operate | `<Evidence>` |
| Telemetry | Complete latest-value state updates | `<Evidence>` |
| Stream | Ordered records with sequence and timestamp | `<Evidence>` |
| Alarm | Display, record, and required action | `<Evidence>` |
| Fault | Node enters reviewed safe behavior | `<Evidence>` |
| Packet loss | Sequence gap detected | `<Evidence>` |
| Delayed response | Timeout and late-response policy applied | `<Evidence>` |
| Node reset | Re-handshake and reconcile | `<Evidence>` |
| Disconnect | Mark stale and stop unsafe UI actions | `<Evidence>` |
| Invalid command | Explicit rejection | `<Evidence>` |
| Unsupported version | Reject or negotiate according to policy | `<Evidence>` |
| Security failure | Reject, audit, and recover by policy | `<Evidence>` |
| Update interruption | Preserve committed progress and resume safely | `<Evidence>` |

## 15.3 Mock Architecture

```text
Coordinator UI
      |
      v
Coordinator Core
      |
      v
ITransport
├─ UsbCdcTransport
├─ CanTransport
├─ TcpTransport
└─ MockTransport
       |
       v
Mock Node
       |
       v
Application and Device Simulator
```

## 15.4 Test Layers

| Layer | Purpose |
|---|---|
| Unit Test | Local logic and boundary behavior |
| Protocol Vector | Cross-language wire equivalence |
| Integration Test | Layer and Adapter interaction |
| Mock Scenario | End-to-end behavior without hardware |
| Hardware Integration | Real Device behavior |
| Fault Injection | Failure and recovery |
| Timing / Load | Worst-case latency, CPU, and Buffer |
| Security | Authentication, authorization, replay, Rekey |
| Firmware Update | Resume, interruption, signature, rollback |
| Regression | Preserve approved behavior |

---

# 16. Required Documents, Artifacts, and Repository

## 16.1 Minimum Document Set

| Artifact | Required | Purpose |
|---|---:|---|
| `<Application>_Requirements.md` or SRS | Yes | Functional and non-functional requirements |
| `<Application>_Framework_Application_Analysis.md` | Yes | Completed use of this template |
| `<Application>_Application_Profile.md` | Yes | Product behavior, commands, data, states, and rationale |
| `<Application>_protocol.yaml` | Yes | Machine-verifiable wire contract |
| `<Application>_Coordinator_SDD.md` | Yes when Coordinator exists | Coordinator architecture |
| `<Application>_Node_SDD.md` | Yes when Node software exists | Node architecture |
| `<Application>_UI_SDD.md` | Conditional | UI and workflow |
| `<Application>_Security_Design.md` | Conditional | Security architecture |
| `<Application>_Firmware_Update_SDD.md` | Conditional | Update and Bootloader |
| `<Application>_Mock_Specification.md` | Recommended | Mock and Simulator |
| `<Application>_Test_Plan.md` | Yes | Verification strategy |
| `<Application>_Traceability.md` | Conditional | Requirement-to-design-to-test traceability |
| `<Application>_User_Manual.md` | Later | Operational use |

## 16.2 Generated and Tool Artifacts

| Artifact | Required | Source |
|---|---:|---|
| Generated C contract | Conditional | Project Protocol YAML |
| Generated C# contract | Conditional | Project Protocol YAML |
| Generated Java contract | Conditional | Project Protocol YAML |
| Generated documentation | Recommended | Project Protocol YAML |
| Golden Test Vectors | Yes | Project Protocol YAML / approved cases |
| Protocol decoder metadata | Recommended | Project Protocol YAML |
| Semantic Lint report | Yes | Project Protocol YAML |
| Compatibility report | Yes | Old/new Protocol versions |
| Static Analysis report | Conditional | Product-owned C Code |
| Timing and resource report | Yes | Measurement |

## 16.3 Recommended Repository

```text
<Application>/
├─ protocol/
│  ├─ spec/
│  │  └─ <Application>_protocol.yaml
│  ├─ schema/
│  ├─ generated/
│  ├─ docs/
│  └─ test_vectors/
├─ coordinator/
│  ├─ application/
│  ├─ node_management/
│  ├─ communication/
│  ├─ platform/
│  └─ tests/
├─ node/
│  ├─ application/
│  ├─ control/
│  ├─ communication/
│  ├─ platform/
│  ├─ bootloader/
│  └─ tests/
├─ shared/
├─ tools/
│  ├─ mock_node/
│  ├─ simulator/
│  ├─ protocol_lint/
│  ├─ packet_decoder/
│  └─ fault_injection/
├─ docs/
│  ├─ requirements/
│  ├─ architecture/
│  ├─ application_profile/
│  ├─ security/
│  ├─ test/
│  └─ user/
└─ README.md
```

---

# 17. MVP and Development Sequence

## 17.1 MVP Goal

```text
<TBD>
```

The MVP shall prove the highest-risk architectural assumptions, not merely display a UI.

## 17.2 Recommended MVP Scope

1. One Coordinator and one Node.
2. One bounded Transport Profile.
3. Link, Handshake, and basic Session behavior.
4. Device identity, versions, and Capability query.
5. Minimum command and response set.
6. At least one complete Telemetry Message.
7. At least one ordered Stream when continuous data is in scope.
8. Basic Event, Alarm, Fault, and error behavior.
9. Minimum State Machines.
10. Mock Node and Virtual Transport.
11. Basic Coordinator workflow and UI when applicable.
12. Logging and packet capture.
13. Minimum Protocol validation and Test Vectors.
14. Timing, bandwidth, Buffer, and resource measurements.
15. Security and Firmware Update subset required to avoid architectural rework.

## 17.3 MVP Exclusions

| Excluded Item | Reason | Risk | Revisit Trigger |
|---|---|---|---|
| `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` |

An excluded item shall not invalidate the architecture assumption being tested.

## 17.4 Development Sequence

| Phase | Deliverable | Exit Criteria |
|---|---|---|
| 1 | Requirements and Analysis Baseline | Roles, boundaries, risks, and scope approved |
| 2 | Application Profile | Product commands, data, states, and failure behavior reviewable |
| 3 | Project Protocol YAML | Schema and Semantic Lint pass |
| 4 | Generated contracts and Golden Vectors | Deterministic and cross-implementation reviewable; cross-language reviewable for languages in scope |
| 5 | Mock Node and Transport | Normal and failure scenarios reproducible |
| 6 | Coordinator Core | Connection, commands, state reconciliation, Telemetry, and Stream operate |
| 7 | Node Core | Event-Driven dispatch, validation, state ownership, and local protection operate |
| 8 | Basic UI / External Integration | Monitoring and approved control flows operate |
| 9 | Logging and Recording | Behavior can be reconstructed |
| 10 | Hardware Integration | Core functions pass on target hardware |
| 11 | Fault, Timing, Security, and Update Tests | High-risk evidence passes |
| 12 | MVP Baseline | Documents, Code, Protocol, generated artifacts, and tests are synchronized |

---

# 18. Framework Gap Analysis

## 18.1 Gap Classification

| Classification | Meaning |
|---|---|
| Application Requirement | Product-specific need |
| Profile Extension | Belongs in Application Profile |
| Framework Configuration | Supported through configuration |
| Framework Optional Capability | Reusable optional capability |
| Framework Mandatory Gap | Broadly reusable missing capability |
| Implementation Gap | Specification exists but Code does not |
| Documentation Gap | Behavior exists but is not defined |
| Test Gap | Behavior exists but evidence is missing |
| Tooling Gap | Generator, Lint, Simulator, analyzer, or CI capability is missing |
| External Dependency Gap | Required capability depends on unavailable third-party or hardware support |

## 18.2 Gap Register

| Gap ID | Description | Classification | Reuse Evidence | Impact | Proposed Authority | Owner | Status | Target | Acceptance Evidence |
|---|---|---|---|---|---|---|---|---|---|
| GAP-001 | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | Framework / Profile / Project / Tool | `<Owner>` | Open | `<TBD>` | `<Evidence>` |

Allowed status:

```text
Open
Analyzing
Accepted
Planned
In Progress
Implemented
Verified
Deferred
Rejected
Closed
```

## 18.3 Framework Promotion Criteria

A Product-specific solution may be promoted into the reusable Framework only when:

1. The need applies to more than one application or has strong evidence of broad applicability.
2. The abstraction does not contain Product semantics.
3. Responsibility boundaries remain stable.
4. Compatibility and migration impact are understood.
5. Validation and Reference Implementation evidence exist.
6. The authority location and version impact are approved.

## 18.4 Gap Closure

A Gap is not closed merely because Code exists.

Closure requires:

```text
Approved design authority
Implemented change or explicit disposition
Updated Protocol or documentation when applicable
Tests and measurements
Compatibility review
Owner approval
Traceable evidence
```

---

# 19. Risk, Decision, and Open-Item Management

## 19.1 Risk Register

| Risk ID | Risk | Cause | Likelihood | Impact | Detection | Mitigation | Contingency | Owner | Status |
|---|---|---|---|---|---|---|---|---|---|
| RISK-001 | `<TBD>` | `<TBD>` | Low / Medium / High | Low / Medium / High / Critical | `<TBD>` | `<TBD>` | `<TBD>` | `<Owner>` | Open |

Consider:

```text
Incorrect responsibility boundary
Insufficient Transport throughput
Excessive control latency
Unbounded Buffer or memory
UI blocking receive or recording
Hidden Product policy in Driver
Protocol incompatibility
Security performance failure
Application/Bootloader key reuse
Update recovery failure
Insufficient static RAM or Flash
Vendor Stack behavior
Incomplete Device datasheet
Unvalidated algorithm
Ambiguous state ownership
Regulatory evidence gap
```

## 19.2 Decision Register

| Decision ID | Decision | Alternatives | Rationale | Consequence | Authority Document | Evidence | Owner | Date |
|---|---|---|---|---|---|---|---|---|
| DEC-001 | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<TBD>` | `<Evidence>` | `<Owner>` | `<YYYY-MM-DD>` |

A decision shall not be recorded only in meeting memory or source-code behavior.

## 19.3 Open Questions

| Question ID | Question | Why It Matters | Owner | Status | Target Date | Decision or Evidence |
|---|---|---|---|---|---|---|
| Q-001 | `<TBD>` | `<TBD>` | `<Owner>` | Open | `<TBD>` | `<TBD>` |

## 19.4 Action Items

| Action ID | Action | Source | Owner | Priority | Due Condition | Status | Closure Evidence |
|---|---|---|---|---|---|---|---|
| ACT-001 | `<TBD>` | Gap / Risk / Review / Test | `<Owner>` | `<TBD>` | `<TBD>` | Open | `<Evidence>` |

## 19.5 Structural Rewrite Review

When a completed analysis is translated, consolidated, or structurally rewritten, review:

- Every prior decision.
- Every Reuse Classification.
- Every Gap, Risk, Question, and Action Item.
- Every responsibility assignment.
- Every cross-document version.
- Every acceptance criterion.
- Every intentional removal.

Balanced code fences and continuous headings are necessary but not sufficient evidence.

---

# 20. Final Output and Approval

## 20.1 Executive Summary

Summarize:

```text
Application purpose
Framework fit
Major reuse decisions
Major application-specific extensions
Critical responsibility boundaries
Protocol and Transport approach
Safety and security position
Firmware Update position
Major Gaps and Risks
MVP recommendation
Go / Conditional Go / No-Go conclusion
```

## 20.2 Final Framework Application Map

Provide the approved classifications for every Framework area.

## 20.3 Final Architecture

Include:

```text
System Context Diagram
Coordinator and Node boundaries
Layer diagram
Control and Data Plane
State ownership
Transport Profile
Security boundary
Firmware Update boundary
```

## 20.4 Final Protocol Inputs

Provide the approved inputs for `<Application>_protocol.yaml`, without duplicating the complete YAML in this document.

## 20.5 Final Gap, Risk, Decision, and Action Registers

Include only current status, Owner, target, and evidence. Preserve history through version control.

## 20.6 MVP Recommendation

| Item | Decision |
|---|---|
| MVP goal | `<TBD>` |
| Included scope | `<TBD>` |
| Excluded scope | `<TBD>` |
| Primary technical risks | `<TBD>` |
| Required preconditions | `<TBD>` |
| Exit evidence | `<TBD>` |

## 20.7 Approval Checklist

- [ ] Framework version and related-document versions are correct.
- [ ] Scope and assumptions are approved.
- [ ] Coordinator and Node roles are explicit.
- [ ] State and safety authorities are explicit.
- [ ] Every Framework area has a Reuse Classification.
- [ ] Product-specific behavior has an authority document.
- [ ] Telemetry and Stream are classified correctly.
- [ ] Timing, bandwidth, Transport, Buffer, memory, and CPU feasibility are bounded.
- [ ] Security objectives, roles, Session, Key Context, Rekey, and Anti-Replay are addressed.
- [ ] Application and Bootloader boundaries are addressed.
- [ ] Firmware Update, rollback, and recovery are addressed when applicable.
- [ ] Protocol YAML inputs are sufficient.
- [ ] Code Generation and validation targets are identified.
- [ ] Mocks, tests, measurements, and acceptance evidence are defined.
- [ ] Every Gap, Risk, Question, and Action has an Owner and status.
- [ ] No unresolved contradiction remains.
- [ ] Remaining `<TBD>` values are traceable to an Open Question or Action Item.
- [ ] Review and approval evidence is retained.

## 20.8 Approval Record

| Role | Name | Decision | Date | Comment |
|---|---|---|---|---|
| Analysis Owner | `<TBD>` | Approve / Reject / Conditional | `<YYYY-MM-DD>` | `<TBD>` |
| Architecture Reviewer | `<TBD>` | Approve / Reject / Conditional | `<YYYY-MM-DD>` | `<TBD>` |
| Protocol Reviewer | `<TBD>` | Approve / Reject / Conditional | `<YYYY-MM-DD>` | `<TBD>` |
| Node Reviewer | `<TBD>` | Approve / Reject / Conditional | `<YYYY-MM-DD>` | `<TBD>` |
| Coordinator Reviewer | `<TBD>` | Approve / Reject / Conditional | `<YYYY-MM-DD>` | `<TBD>` |
| Safety / Security Reviewer | `<TBD>` | Approve / Reject / Conditional | `<YYYY-MM-DD>` | `<TBD>` |

## 20.9 Final Recommendation

```text
Go
Conditional Go
No-Go
```

Rationale:

```text
<TBD>
```

---

## 8.12 Fragmentation, Handshake, and Update-Resume Contract

| Item | Project Decision and Evidence |
|---|---|
| Fragment Header struct, exact byte length, and field order | `<TBD>` |
| Record-ID scope and maximum concurrent reassembly | `<TBD>` |
| Duplicate, conflict, out-of-order, timeout, oversize, integrity, and abort policies | `<TBD>` |
| Minimum and maximum Runtime MTU; positive Fragment payload proof | `<TBD>` |
| Application Handshake request/response structs | `<TBD>` |
| Bootloader Handshake request/response structs | `<TBD>` |
| Profile allowed/preferred/prohibited IDs, security level, and deprecation policy | `<TBD>` |
| Algorithm-set registry and unresolved-decision closure | `<TBD>` |
| Update resume authorization structure and cryptographic method | `<TBD>` |
| Transaction, Manifest, Device, Host, security-version, generation, nonce binding | `<TBD>` |
| Resume-token persistence, reissue, replay, revocation, and terminal invalidation | `<TBD>` |

Acceptance requires generated or independently calculated evidence that all supported MTUs carry a positive Fragment
payload, all Handshake transcript fields have typed wire locations, Profile selection cannot silently downgrade, and a
new Bootloader Session cannot attach to persisted Update state using only a Transaction ID or offset.

# Appendix A. Quick-Start Analysis Sequence

```text
1. Collect inputs and record assumptions
2. Define System Context and scope
3. Assign Coordinator, Node, and state authorities
4. Classify each Framework capability
5. Define Product-specific behavior and authority documents
6. Define Protocol inputs, Telemetry, Stream, Events, Alarms, and Faults
7. Establish timing, bandwidth, Transport, Buffer, and resource budgets
8. Define State Machines, recovery, and safety behavior
9. Define security and Firmware Update boundaries
10. Define UI, Mock, Test Harness, and required artifacts
11. Define MVP and development sequence
12. Create Gap, Risk, Decision, Question, and Action Registers
13. Define acceptance evidence
14. Review and approve the Application Analysis Baseline
```

---

# Appendix B. Reuse Classification Decision Guide

| Question | Result |
|---|---|
| Can the capability be used without semantic change? | Direct Reuse |
| Can bounded configuration support the need? | Configured Reuse |
| Is a reusable optional extension sufficient? | Extended Reuse |
| Is the behavior unique to this Product? | Application-Specific |
| Is the capability broadly reusable but missing? | Framework Gap |
| Is the existing approach fundamentally unsuitable with approved rationale? | Replace |
| Is the capability genuinely unnecessary? | Not Applicable |

Do not classify an item as Framework Gap until Product-specific configuration and Profile extension have been ruled out.

---

# Appendix C. Command Definition Template

```text
Command Name:
Message ID:
Namespace:
Service:
Category:
Direction:
Execution Environment:
Purpose:
Authority Document:
Preconditions:
Allowed States:
Request Fields:
Response Fields:
Success Criteria:
Error Codes:
Timeout:
Retry Policy:
Idempotency:
Operation or Transaction ID:
Maximum Command Age:
Duplicate Policy:
Privilege:
Key Context:
Logging:
Safety Consideration:
Compatibility:
Test Cases:
```

---

# Appendix D. Data Field Definition Template

```text
Field Name:
Description:
Source:
Wire Type:
Length:
Unit:
Valid Range:
Resolution:
Scaling:
Default:
Invalid Value:
Endianness:
Timestamp:
Quality Flags:
Update or Trigger Semantics:
Replacement or Ordering Semantics:
Persistence:
Compatibility:
Decoder Validation:
Test Method:
```

---

# Appendix E. State Definition Template

```text
State Name:
State Domain:
Owner:
Description:
Entry Condition:
Entry Action:
Allowed Commands:
Periodic Action:
Exit Conditions:
Exit Actions:
Timeout:
Recoverable Errors:
Non-Recoverable Errors:
Safe-State Requirement:
Persistence:
Reconciliation:
Logging:
Test Cases:
```

---

# Appendix F. UI Page Definition Template

```text
Page Name:
Purpose:
Target User:
Displayed Data:
Data Source:
Authority Source:
Refresh or Update Semantics:
User Actions:
Preconditions:
Confirmation:
Pending State:
Success Feedback:
Failure Feedback:
Stale Data Behavior:
Logging:
Access Level:
Test Cases:
```

---

# Appendix G. Framework Gap Decision Template

```text
Gap ID:
Observed In Application:
Problem:
Existing Framework Behavior:
Required Behavior:
Cross-Application Reusability:
Application-Specific Dependency:
Alternatives:
Proposed Authority Location:
Backward Compatibility:
Migration Impact:
Implementation Cost:
Test Impact:
Owner:
Status:
Decision:
Target Version or Condition:
Acceptance Evidence:
```

---

# Appendix H. Review Questions

## Architecture

- Is the Project actually reusing the existing Framework rather than silently redesigning it?
- Are Application Profile and Framework authority boundaries clear?
- Does the Node retain required real-time and safety responsibility?
- Is UI limited to interaction, display, and approved non-real-time processing?
- Is there any duplicated state authority?
- Does Command Dispatcher avoid direct hardware operation?
- Are Product policy and generic Driver responsibilities separated?

## Product

- Are the users development, production, maintenance, clinical, or general operators?
- Is configuration writing allowed?
- Are role and privilege levels required?
- Is long-duration recording required?
- Is offline analysis required?
- Are reports required?
- Are multiple Nodes or Device instances monitored?
- Is remote connection required?
- Is regulatory traceability required?

## Hardware

- Which Device models, variants, and revisions apply?
- What is the Bus topology?
- What are the voltage, current, temperature, timing, and measurement ranges?
- What are the Device power-up defaults?
- What is the hardware behavior before the MCU is operational?
- What is the fail-safe behavior when communication fails?
- Are hardware Alert or Interrupt signals available?
- Is calibration data present and where is it owned?
- Is a Bootloader or hardware recovery path available?

## Protocol

- What are the data and control rates?
- What are the command timeout and retry policies?
- Is each retry safe and idempotent?
- What are the Sequence and Timestamp sources?
- Is time synchronization required?
- Is Fragmentation required and bounded?
- Is bulk transfer required?
- What is the compatibility policy?
- Which Capabilities are negotiated?
- What are the security requirements?
- Are Telemetry and Stream classified by semantics rather than rate?

## Security

- Are Authentication, Authorization, Confidentiality, and Integrity requirements explicit?
- Are privileges and roles defined by operation risk?
- Are Anti-Replay, per-Key-Context Counter width, Soft Threshold, Rekey Deadline, Hard Limit, persistence, gap, exhaustion, and atomic-cutover policies explicit?
- Is public Discovery minimal, ephemeral, rate-limited, transcript-bound, non-authoritative, and revalidated after authentication?
- Are concrete Handshake Profile, KDF, cipher, proof, downgrade, and transcript-binding decisions complete?
- Is every Firmware signature encoding and exact length unambiguous across implementations?
- Are Security Events and Audit Records sufficient?
- Are Application and Bootloader Sessions and Key Contexts separated?
- Does Firmware Update require independent signed-image verification?
- Does a security-model change force revalidation?

## Reliability and Recovery

- Is the system safe during communication loss?
- Can the Node recover after reset?
- Can the Coordinator identify stale state?
- Can loss, duplication, and reordering be detected where required?
- Can UI slowdown affect recording or control?
- Are Buffer overflow and storage-full policies explicit?
- Are rollback and recovery paths testable?

## Development and Verification

- Can Coordinator and Node teams develop in parallel using Mock and generated contracts?
- Is the MVP small enough to verify while still exercising the highest-risk assumptions?
- Are documents, Protocol, Code, generated artifacts, and tests traceable?
- Are timing, bandwidth, memory, CPU, and Buffer assumptions measured?
- Does every Framework Gap have a disposition and evidence?
- Does every remaining question have an Owner?

---

# Appendix I. Detailed Completion Checklist

## Framework Reuse

- [ ] Directly reusable Framework modules are identified.
- [ ] Configured and Extended Reuse items are identified.
- [ ] Existing Transport, Session, Command, and Protocol mechanisms were not duplicated.
- [ ] Framework and related-document version dependencies are recorded.
- [ ] Each component role is classified before language-specific authority selection; no language is used as a role proxy.
- [ ] Coordinator role-level engineering authority applicability, version, status, and evidence or `N/A` rationale are recorded.
- [ ] Applicable language Coding Rules are identified; Product-owned C# explicitly records `CSharp_Coding_Rules.md` applicability, version, status, and evidence or `N/A` rationale.
- [ ] Draft for Review authorities are not silently treated as approved Product Baselines.
- [ ] Revalidation was completed after applicable Framework changes.
- [ ] Affected compatibility, integration, and regression tests were rerun.
- [ ] Validated versions, review date, and Revalidation Status were updated.

## Application Profile and Protocol

- [ ] Application Profile identity is defined.
- [ ] Services, commands, responses, Telemetry, Stream, Events, Alarms, Faults, and data models are defined.
- [ ] Compatibility and Capability policies are defined.
- [ ] Project Protocol YAML is planned or complete.
- [ ] Authentication, Session Security, privilege, role, Anti-Replay, per-Key-Context Counter/Rekey lifecycle, timeout, audit, and credential lifecycle are defined.
- [ ] Public Discovery privacy, rate limiting, transcript binding, and authenticated revalidation are defined.
- [ ] Concrete Handshake algorithms, Profile binding, canonical transcript, and downgrade rejection are defined.
- [ ] Firmware signature preparation, exact wire encoding, exact length, and canonicality or low-S rule are defined.
- [ ] Plaintext Message, security overhead, secured Record, reassembly, and Fragment budgets are separately calculated.
- [ ] Application and Bootloader security boundaries are defined.
- [ ] Schema Validation, Semantic Lint, Code Generation, and Test Vector targets are defined.

## Responsibility Boundary

- [ ] UI responsibility is defined.
- [ ] Coordinator Core responsibility is defined.
- [ ] Node Application responsibility is defined.
- [ ] Bootloader and Update responsibility is defined.
- [ ] Service, Adapter, Driver, HAL, and physical Device responsibilities are defined.
- [ ] Node behavior during Coordinator disconnect is defined.
- [ ] The final safety authority is defined.
- [ ] No duplicated state authority remains.

## State, Error, and Recovery

- [ ] State domains and owners are defined.
- [ ] Entry, exit, timeout, invalid transition, and recovery behavior are defined.
- [ ] Link, Session, Protocol, Application, Device, Data, UI, Storage, Security, and Update failures are analyzed.
- [ ] Safe state, stale state, read-back, reconnect, and reconciliation behavior are defined.
- [ ] Firmware Update rollback and recovery are defined when applicable.

## UI and Data

- [ ] UI pages and main operation flows are defined.
- [ ] Data source, authority, freshness, and update semantics are defined.
- [ ] Recording format, retention, logging, playback, export, and report requirements are defined.
- [ ] Display and recording Buffer policies are separated when their loss policies differ.
- [ ] UI blocking cannot stall required receive, control, or recording paths.

## Timing, Transport, and Resources

- [ ] Timing and control-latency budgets are defined.
- [ ] Average and peak bandwidth are calculated.
- [ ] Maximum non-preemptible transfer time is bounded.
- [ ] Transport Profile and Runtime Effective Profile behavior are defined.
- [ ] Buffer, memory, Flash, stack, crypto, reassembly, and CPU budgets are defined.
- [ ] Resource margins have a measurement plan.

## Simulation and Testing

- [ ] Mock Node, Mock Coordinator, and Device Simulator needs are decided.
- [ ] Fault injection is defined.
- [ ] MVP test scope is defined.
- [ ] Hardware integration, long-run, load, reset, reconnect, and recovery tests are defined.
- [ ] Security and Firmware Update tests are defined when applicable.
- [ ] Requirement-to-design-to-test traceability is defined.

## Gap, Risk, and Decision Management

- [ ] Framework Gap Analysis is complete.
- [ ] Application Requirement and Framework Gap are distinguished.
- [ ] Product-specific behavior that shall not be promoted is identified.
- [ ] Every Gap has an Owner, Status, target, and acceptance evidence.
- [ ] Every Risk has mitigation, contingency, Owner, and Status.
- [ ] Every Decision records alternatives, rationale, authority, and evidence.
- [ ] Every Open Question and Action Item has an Owner and closure condition.

---

# Appendix J. Baseline Decision Summary

This baseline establishes the following decisions:

1. Application Analysis evaluates Framework application; it does not create a competing architecture.
2. Every completed analysis records the exact Framework and related-document versions it validated.
3. Coordinator and Node are relationship-relative system roles.
4. System role, Message role, Event role, Transport direction, and connection role remain distinct.
5. Every Framework capability receives an explicit Reuse Classification.
6. Product-specific commands, data, states, limits, and workflows remain outside the reusable Framework.
7. One normative rule has one authority location.
8. Protocol YAML is the Single Source of Truth for the machine-verifiable wire contract.
9. This analysis shall not maintain an independent simplified Protocol YAML skeleton.
10. The Project Protocol is derived from `Protocol_YAML_Template.md`.
11. Telemetry represents replaceable complete summarized state.
12. Stream represents ordered non-replaceable records or samples.
13. Transmission frequency alone does not determine Telemetry versus Stream.
14. Redundant wire fields require an explicit consistency and mismatch policy.
15. Node retains hard real-time control, fundamental safety protection, and local Fault Reaction.
16. UI validation does not replace Node validation.
17. Mirrored state does not become a second authority.
18. Control and Data paths shall not block each other.
19. Every Transport requires a bounded Transport Profile.
20. Dynamically negotiated Transports require a Runtime Effective Profile.
21. Average throughput does not prove acceptable worst-case control latency.
22. Every queue, Mailbox, Ring Buffer, reassembly path, and variable record is bounded.
23. Timing, bandwidth, memory, CPU, and Buffer assumptions require evidence.
24. Application and Bootloader use separate Sessions, Key Contexts, counters, and Anti-Replay state.
25. Firmware Update Transaction identity is separate from Secure Session identity.
26. Reconnect or Rekey requires reauthentication and transaction revalidation.
27. Firmware images require independent signed-image authenticity verification when Firmware Update is in scope; CRC does not replace that verification.
28. Firmware Update includes resume, rollback, and recovery analysis.
29. Generated Protocol artifacts are deterministic, traceable, and not manually edited.
30. Code Generation does not replace Product behavior and Adapter design.
31. Framework Gap promotion requires cross-application reuse evidence.
32. A Gap is not closed merely because Code exists.
33. Every Gap, Risk, Open Question, and Action Item has an Owner and status.
34. The MVP proves high-risk architectural assumptions, not only UI appearance.
35. Mocks, Test Vectors, timing measurement, and recovery evidence are part of the analysis output.
36. A successful syntax check does not prove semantic preservation after structural rewrite.
37. Remaining placeholders are traceable to managed Open Questions or Actions.
38. Final approval requires an explicit Go, Conditional Go, or No-Go decision.
39. Reusable Command, Data Field, State, UI Page, and Framework Gap mini-templates remain part of the analysis method.
40. Detailed Review Questions and completion checklists remain part of Baseline acceptance evidence.
41. Maintained completed-analysis files use stable canonical repository filenames; immutable detached release, audit, and external-delivery artifacts include an approved Analysis Version or Baseline identifier in the distributed filename.
42. Telemetry replacement semantics are separate from delivery queue policy.
43. Each peer is accountable for its own local Secure Session state.
44. Cross-implementation validation applies to every implementation; cross-language validation applies to language pairs in scope.
45. Repeated non-owning requirements are derived conformance summaries and remain subordinate to their authority source.
46. Minimum-compatible authority versions are distinct from the actual authority versions used for one analysis.
47. A detached analysis artifact records its canonical source filename and Git commit, tag, or Release and shall not become a parallel maintained authority.
48. Downstream SRS, SDD, Test Protocol, and audit records cite the approved Analysis Version and Baseline identity rather than relying only on a mutable canonical path.
49. Authority versions shown as Template authoring references are not automatic Product compatibility decisions.
50. Every completed analysis records the exact authority version used, source Git identity, and compatibility evidence.
51. A claimed minimum-compatible version is Project-specific and shall not precede the version used without documented comparison evidence.
52. Public Discovery exposes no permanent identifier and is minimal, ephemeral, rate-limited, non-authoritative, transcript-bound, and revalidated after authentication.
53. Product Handshake Profiles use concrete approved cryptography and reject mismatch, unsupported Profile, and downgrade without fallback.
54. Canonical Handshake transcripts bind both parties, both nonces, ephemeral keys, negotiated algorithms, Session ID, and Key Contexts.
55. Every Key Context has an explicit Counter/Rekey lifecycle and uncrossable Hard Limit.
56. Firmware signature Profiles define exact preparation, exact wire encoding, exact length, and canonicality or low-S policy.
57. `minimum_length` is a fixed decoding prefix and does not include minimum variable content.
58. Plaintext Message, security overhead, secured Record, Transport reassembly, and Fragment size budgets remain distinct.
59. Product analysis records one exact Fragment Header and complete bounded reassembly behavior.
60. Product analysis maps every security-critical Handshake transcript field to a named typed wire struct.
61. Profile selection uses explicit allowed, preferred, prohibited, security-level, and deprecation decisions rather than numeric ID ordering.
62. Persisted Firmware Update resume requires cryptographic authorization bound to transaction, Manifest, Device, Host, and security version.
63. Every supported minimum MTU provides a positive data-bearing Fragment payload.
64. Coordinator-owned software analysis records applicability and evidence for `Coordinator_Software_Engineering_Rules.md`.
65. Product-owned C# analysis records applicability and evidence for `CSharp_Coding_Rules.md`.
66. Role-level and language-level authorities are both applied when relevant; a Draft authority requires explicit Project acceptance, approved deviation, or `N/A` rationale and is not silently promoted by this analysis.
67. Implementation language does not determine Coordinator, Node, Tool, Service, or mixed role.
68. Repository validation evidence records automated checks separately from human semantic review and approval.
69. Detached analysis and authority-set packages carry source identity and file-integrity metadata.

---

# Conclusion

The completed Application Analysis connects the reusable Framework to one Product without allowing either side
to lose its authority boundary.

The intended flow is:

```text
Framework Baseline
        |
        v
Application Analysis
        |
        v
Application Profile and Product Requirements
        |
        v
Project Protocol YAML
        |
        +--> Schema Validation
        +--> Semantic Lint
        +--> Code Generation
        +--> Compatibility Tests
        +--> Test Vectors
        |
        v
Coordinator and Node Design
        |
        v
Mock and Reference Implementation
        |
        v
Timing / Resource / Safety / Security / Recovery Evidence
        |
        v
Project Baseline
```

The analysis is successful when the Project can begin implementation with clear roles, bounded resources,
explicit Protocol inputs, controlled risks, and testable acceptance criteria.
