# Host-Device Control Framework

An AI-consumable engineering authority set for Coordinator/Node control systems in which a PC, SoC, MCU, Gateway,
mobile application, production tool, or service tool communicates with and controls an embedded Node.

The repository is designed primarily to guide and constrain AI-assisted engineering work. It defines how AI should
route authority, analyze a new application, design a Protocol, generate or review implementation, and report
validation evidence. Human engineers remain responsible for Product intent, architecture approval, hardware and
system measurement, safety and security decisions, deviations, residual risk, and release approval.

## Intended Operating Model

```text
Human requirements, constraints, and decision boundaries
        |
        v
AI reads the applicable authority documents
        |
        v
AI analyzes, designs, generates, reviews, and validates
        |
        v
AI reports assumptions, conflicts, findings, and evidence state
        |
        v
Human reviews decisions and validates actual system behavior
```

## Current Document Set

| Document | Version | Status | Purpose |
|---|---:|---|---|
| [`AI_Engineering_Usage_Guide.md`](docs/AI_Engineering_Usage_Guide.md) | v1.0.8 | Draft for Review | AI entry point, authority routing, task workflows, evidence states, prohibited behaviors, and human approval boundary |
| [`Coordinator_Node_Control_Framework.md`](docs/Coordinator_Node_Control_Framework.md) | v1.0.8 | Baseline | Reusable architecture, responsibility boundaries, timing, safety placement, security, Firmware Update, Runtime, validation, and governance |
| [`Framework_Application_Analysis_Template.md`](docs/Framework_Application_Analysis_Template.md) | v1.0.10 | Baseline | Method for applying the Framework to a Product, including Reuse Classification, Protocol inputs, risks, Gaps, MVP, and acceptance evidence |
| [`Protocol_YAML_Definition_Guide.md`](docs/Protocol_YAML_Definition_Guide.md) | v1.0.8 | Baseline | Protocol YAML syntax, semantics, Registry rules, security, compatibility, validation, Code Generation, and governance |
| [`Protocol_YAML_Template.md`](docs/Protocol_YAML_Template.md) | v1.0.8 | Baseline | Reusable Project Protocol YAML starting structure and review checklists |
| [`Embedded_C_Coding_Rules.md`](docs/Embedded_C_Coding_Rules.md) | v1.0.15 | Final Baseline | Product-owned Embedded C implementation, memory, arithmetic, State Machine, ISR, callback, RTOS, Protocol, and review rules |

## AI Task Routing

```text
Architecture or system-boundary task
    -> AI Engineering Usage Guide
    -> Coordinator/Node Control Framework

New Product or application task
    -> AI Engineering Usage Guide
    -> Coordinator/Node Control Framework
    -> Framework Application Analysis Template

Protocol task
    -> AI Engineering Usage Guide
    -> Coordinator/Node Control Framework
    -> Protocol YAML Definition Guide
    -> Protocol YAML Template
    -> Completed Application Analysis and Product requirements

Embedded C generation or review
    -> AI Engineering Usage Guide
    -> Coordinator/Node Control Framework
    -> Embedded C Coding Rules
    -> Approved Project Protocol YAML and Node design
```

While `AI_Engineering_Usage_Guide.md` remains `Draft for Review`, this routing is provisional. Direct human
instructions and the approved topic authority documents take precedence.

## Filename and Release Artifact Policy

Maintained Markdown authority files inside the controlled Git repository use stable canonical filenames.

```text
Canonical path:      docs/Coordinator_Node_Control_Framework.md
Document version:    v1.0.8
Immutable history:   Git commit, tag, or GitHub Release
```

This keeps AI prompts, links, automation, and cross-document references stable. A new PATCH or MINOR revision updates
the canonical file and its internal `Document Version`; it does not create another parallel maintained authority file.

Immutable release artifacts, audit packages, external deliverables, and detached snapshots include the approved
version or a controlled Baseline identifier in the distributed filename:

```text
Smart_Battery_Framework_Application_Analysis_v1.2.0.md
Smart_Battery_Framework_Application_Analysis_v1.2.0.pdf
Smart_Battery_Engineering_Baseline_v1.2.0.zip
```

Detached artifacts preserve the canonical source filename and source Git commit, tag, or Release. They are immutable
distribution copies and do not become parallel maintained authorities.

## Authority Boundary

```text
AI Engineering Usage Guide
    Routes AI tasks, active versions, evidence states, and approval boundaries.

Coordinator/Node Control Framework
    Defines reusable architecture, roles, layering, timing, safety placement,
    security boundaries, Firmware Update architecture, and governance.

Framework Application Analysis Template
    Defines the method for applying the Framework to a Product.

Protocol YAML Definition Guide
    Defines Protocol YAML rules and validation requirements.

Protocol YAML Template
    Provides a reusable Project Protocol starting structure.

<Application>_protocol.yaml
    Defines the approved Project-specific machine-verifiable wire contract.

Embedded C Coding Rules
    Defines Product-owned Embedded C implementation requirements.

Application Profile / SRS / Hazard Analysis
    Defines approved Product-specific behavior, limits, hazards, and rationale.

Source Code, builds, logs, measurements, and test reports
    Provide as-built evidence; they do not silently override approved authority.
```

One normative rule should have one authority location. Repeated text in a non-owning document is a derived
conformance summary and does not override the owning authority.

## Engineering Principles

- Coordinator and Node are platform-independent system roles.
- Protocol and Transport remain decoupled.
- The Node retains hard real-time control, fundamental safety protection, and local Fault Reaction.
- UI and Application code do not assemble wire frames directly.
- Telemetry is replaceable complete summarized state; Stream is ordered non-replaceable records or samples.
- Application and Bootloader use separate Secure Sessions, Key Contexts, counters, and Anti-Replay state.
- Public Discovery is minimal, ephemeral, rate-limited, non-authoritative, transcript-bound, and revalidated after authentication.
- Handshake Profiles reject mismatch and downgrade without silent fallback; every Key Context has an explicit Counter/Rekey lifecycle.
- Plaintext Message, security overhead, secured Record, reassembly, and Fragment size domains remain distinct.
- Firmware Update Transaction identity remains separate from Secure Session identity.
- Protocol-generated artifacts are deterministic, traceable, and not edited manually.
- Every queue, Buffer, record, Fragmentation path, and reassembly path is bounded.
- Syntax validation does not prove semantic correctness or structural-preservation completeness.
- AI shall report only validation that was actually executed and shall not self-approve a Baseline or release.

## Intended Engineering Flow

```text
AI Engineering Usage Guide
        |
        v
Coordinator/Node Control Framework
        |
        v
Framework Application Analysis
        |
        v
Application Profile / SRS / Hazard Analysis
        |
        v
Project Protocol YAML
        |
        +--> Schema Validation
        +--> Semantic Lint
        +--> Compatibility Review
        +--> Code Generation
        +--> Documentation
        +--> Golden Test Vectors
        |
        v
Mock and Reference Implementations
        |
        v
Target timing / resource / safety / security / recovery evidence
        |
        v
Human-approved Project Baseline
```

## Repository Structure

```text
host-device-control-framework/
├─ README.md
├─ COPYRIGHT.md
└─ docs/
   ├─ AI_Engineering_Usage_Guide.md
   ├─ Coordinator_Node_Control_Framework.md
   ├─ Embedded_C_Coding_Rules.md
   ├─ Framework_Application_Analysis_Template.md
   ├─ Protocol_YAML_Definition_Guide.md
   └─ Protocol_YAML_Template.md
```

## Current Status

The repository contains personal engineering documents and baselines maintained by Ray Yang. They do not represent the official policies,
specifications, designs, coding standards, or documentation of any employer, company, or organization.

Document-level review is ongoing. Practical validation through engineering tools, Mock and Reference Implementations,
real Project application, target measurement, and recovery testing remains ongoing. The AI Engineering Usage Guide is
currently `Draft for Review`; its publication does not constitute automatic Baseline approval.

## Authorship and AI Assistance

The engineering concepts, architecture, rule selection, revisions, and final editorial decisions in Baseline and
Final Baseline artifacts are reviewed and approved by Ray Yang. Draft for Review artifacts remain subject to human
review and approval. Generative AI tools were used to assist with drafting, editing, organization, translation,
consistency review, technical review, and artifact generation.

AI-assisted content is not accepted solely because it is syntactically correct. Published content remains subject to
human technical review and approval.

## Copyright and Usage

Copyright © 2026 Ray Yang. All rights reserved.

The materials are publicly available for review. Public availability does not grant permission to reproduce, modify,
redistribute, publish, sublicense, sell, or incorporate the materials into another Project.

See [`COPYRIGHT.md`](COPYRIGHT.md) for the complete notice.
