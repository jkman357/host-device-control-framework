# Host-Device Control Framework

A reusable engineering framework for Host-Device control systems in which a PC, SoC, or MCU Host communicates with and controls an MCU-based Device.

The framework defines reusable architecture, Protocol, implementation, validation, and engineering-governance practices for embedded control systems.

## Scope

The framework is intended for systems such as:

* PC Host to MCU Device
* SoC Host to MCU Device
* MCU Host to MCU Device
* Command and Response communication
* Event, Alarm, and Fault reporting
* Telemetry and status reporting
* Continuous ordered data Streaming
* Capability discovery and feature negotiation
* Session and connection management
* Firmware Update and Bootloader integration
* Embedded C Firmware implementation
* Protocol-driven Code Generation and validation

## Terminology

In this repository:

* **Host** refers to the system that configures, controls, monitors, or collects data. A Host may be a PC, SoC, or MCU.
* **Device** refers to the controlled embedded target, typically an MCU-based system.
* **Coordinator** describes the logical role normally performed by the Host.
* **Node** describes the logical role normally performed by the Device.

Host and Device describe deployment roles. Coordinator and Node describe architectural responsibilities.

## Documents

### Coordinator/Node Control Framework

[`Coordinator_Node_Control_Framework_v1.0.2.md`](docs/Coordinator_Node_Control_Framework_v1.0.2.md)

Defines the master architecture and engineering-governance baseline for:

* Coordinator and Node roles
* System layering and responsibility boundaries
* Device Contract and Protocol authority
* Project structure and dependency direction
* Control Plane and Data Plane separation
* Telemetry and Streaming semantics
* Timing, bandwidth, buffering, and priority
* Transport Profiles and link management
* Secure Sessions, Key Contexts, Rekey, and Anti-Replay
* Firmware Update, Bootloader, resume, rollback, and recovery
* RTOS and Bare-Metal execution models
* Event-Driven architecture and State Machine ownership
* ISR and callback boundaries
* BSP, HAL, Driver, Adapter, Service, and Control boundaries
* Protocol Code Generation and CI governance
* Static Analysis, compatibility, and interoperability
* Testing, observability, and acceptance evidence
* Reference Implementation and Project adoption

**Status:** Baseline

### Embedded C Coding Rules

[`Embedded_C_Coding_Rules_v1.0.13.md`](docs/Embedded_C_Coding_Rules_v1.0.13.md)

Defines the Embedded C implementation baseline for:

* Coding style and naming
* File and Function Headers
* Static-memory configuration
* Arithmetic and conversion safety
* Pointer and buffer safety
* Event-Driven architecture
* State Machine ownership
* ISR and callback boundaries
* Entry-point and `main()` responsibilities
* RTOS and middleware integration
* Protocol implementation
* Vendor Stack isolation
* Build, Static Analysis, review, and verification governance

**Status:** Final Baseline

### Protocol YAML Definition Guide

[`Protocol_YAML_Definition_Guide_v1.0.3.md`](docs/Protocol_YAML_Definition_Guide_v1.0.3.md)

Defines the reusable Protocol YAML authoring and governance baseline for:

* Protocol data models
* Namespace, Service, Message, Capability, Error, Enum, and Bitset Registries
* Message IDs and allocation policies
* Command and Response relationships
* Event, Alarm, Fault, Telemetry, and Streaming semantics
* Payload fields, types, units, scaling, ranges, and length policies
* Sequence, correlation, timestamp, retry, and idempotency
* Security attributes and Key Context separation
* Capability and feature negotiation
* Transport Profiles and Fragmentation
* Firmware Update and Bootloader contracts
* Compatibility, Deprecation, and Protocol evolution
* C, C#, and Java Code Generation
* Schema Validation and Semantic Lint
* Test Vectors and cross-language interoperability
* Protocol Baseline and change governance

**Status:** Baseline

### Protocol YAML Template

[`Protocol_YAML_Template_v1.0.3.md`](docs/Protocol_YAML_Template_v1.0.3.md)

Provides a reusable Project Protocol YAML skeleton aligned with the Protocol YAML Definition Guide, including:

* Protocol metadata and Wire Format
* Message ID allocation ranges
* Namespace and Service definitions
* Type, Enum, Bitset, Error, and Capability Registries
* Command and Response examples
* Event, Alarm, and Fault examples
* Distinct Telemetry and Streaming examples
* Sequence and Timestamp policies
* Transport Profiles and Fragmentation
* Security Model and Key Context separation
* Firmware Update and Bootloader Messages
* Compatibility and Code Generation configuration
* Schema Validation and Semantic Lint checklists
* Compatibility Review and Baseline Readiness checklists

The Template also defines an explicit consistency rule for ordered sample records:

```text
sample_count == channel_count × samples_per_channel
```

The decoder shall verify this relationship using overflow-checked arithmetic and validate Payload length and destination capacity before accessing the sample array.

**Status:** Baseline

Additional framework documents will be added after public-release review.

## Current Status

This repository is under active development.

The published documents are personal engineering baselines maintained by Ray Yang. They do not represent the official policies, specifications, designs, coding standards, or documentation of any employer, company, or organization.

The published documents have completed document-level review.

Practical validation through Reference Implementations and real Project application remains ongoing.

## Planned Documents

The following documents are planned for later publication after review:

* Framework Application Analysis Template
* Reference Implementation documentation
* Protocol Schema and Semantic Lint documentation
* Code Generator design and validation documentation

The planned-document list is informational only and does not indicate a committed release schedule.

## Repository Structure

```text
host-device-control-framework/
├─ README.md
├─ COPYRIGHT.md
└─ docs/
   ├─ Coordinator_Node_Control_Framework_v1.0.2.md
   ├─ Embedded_C_Coding_Rules_v1.0.13.md
   ├─ Protocol_YAML_Definition_Guide_v1.0.3.md
   └─ Protocol_YAML_Template_v1.0.3.md
```

## Intended Workflow

The intended engineering flow is:

```text
Coordinator/Node Control Framework
        |
        v
Framework Application Analysis
        |
        v
Application Profile and Product Requirements
        |
        v
Protocol YAML Definition Guide
        |
        v
Protocol YAML Template
        |
        | copy, tailor, and complete
        v
<Application>_protocol.yaml
        |
        +--> Schema Validation
        |
        +--> Semantic Lint
        |
        +--> Compatibility Review
        |
        +--> Code Generation
        |
        +--> Documentation
        |
        +--> Test Vectors
        |
        v
Coordinator and Node Reference Implementations
        |
        v
Timing / Resource / Security / Recovery Validation
        |
        v
Project Baseline
```

The Project-specific Protocol YAML is intended to serve as the Single Source of Truth for the machine-verifiable wire contract.

The Coordinator/Node Control Framework is intended to serve as the Single Source of Truth for the reusable system architecture and engineering-governance model.

Generated artifacts are not intended to become independent design authorities.

## Document Responsibility Boundary

```text
Coordinator/Node Control Framework
    Defines system roles, layering, architecture boundaries,
    timing, safety placement, security boundaries,
    Firmware Update architecture, and governance.

Embedded C Coding Rules
    Defines Embedded C implementation rules,
    runtime boundaries, memory policy, and code quality.

Protocol YAML Definition Guide
    Defines Protocol YAML syntax, semantics,
    validation, compatibility, and governance rules.

Protocol YAML Template
    Provides a reusable Project skeleton that can be
    copied, tailored, and completed.

<Application>_protocol.yaml
    Defines the formal Project-specific wire contract
    and serves as Code Generation input.

Application Profile / SRS
    Defines Product-specific behavior, operating flows,
    state rationale, limits, Alarm behavior, and UI intent.

Reference Implementation
    Defines actual source code, platform integration,
    threading, buffers, Drivers, UI, build, and deployment.
```

One normative rule should have one authority location.

Other documents should reference that authority instead of maintaining independently editable duplicate rules.

## Architecture Principles

The framework is based on the following principles:

* Coordinator and Node are platform-independent system roles.
* System Role, Message Role, Event Role, Transport Role, and Connection Role are distinct.
* The Device Contract remains stable when the platform, MCU, RTOS, UI Framework, or Transport changes.
* Protocol and Transport remain decoupled.
* The Node retains local hard real-time control, basic safety protection, and Fault Reaction.
* UI and Application code do not assemble wire frames directly.
* Command Dispatchers translate validated Protocol commands into Application events or Service requests.
* Telemetry represents replaceable summarized state.
* Streaming represents ordered records whose loss, duplication, reordering, or timing discontinuity matters.
* Transmission frequency alone does not determine Telemetry versus Streaming.
* Application and Bootloader use separate Secure Sessions, Key Contexts, counters, and Anti-Replay state.
* Firmware Update Transaction identity remains separate from Secure Session identity.
* Generated Code is deterministic, traceable, and not edited manually.
* Structural rewrites require semantic preservation review, not only syntax validation.

## Protocol YAML Responsibility Boundary

```text
Protocol YAML Definition Guide
    Defines the normative rules, design principles,
    validation requirements, and governance model.

Protocol YAML Template
    Provides a reusable Project skeleton that can be
    copied, tailored, and completed.

<Application>_protocol.yaml
    Defines the formal Project-specific wire contract
    and serves as Code Generation input.
```

The Template shall not redefine a rule differently from the Definition Guide.

A Project-specific Protocol YAML shall replace all illustrative values, placeholder identifiers, sample IDs, limits, rates, security settings, and Transport Profiles before Baseline approval.

## Reference Implementation Direction

Future Reference Implementations are expected to exercise:

* PC, SoC, or MCU Coordinator roles
* MCU-based Node roles
* Command and Response processing
* Event, Alarm, and Fault reporting
* Replaceable summarized Telemetry
* Continuous ordered Streaming
* Static-memory Embedded C
* Event-Driven dispatch
* State Machines
* ISR and callback boundaries
* RTOS and non-RTOS entry points
* Protocol YAML generated contracts
* Cross-language interoperability
* Secure Session behavior
* Firmware Update and Bootloader boundaries
* Reconnect, recovery, and state reconciliation

Reference Implementations will be used to evaluate whether the published rules remain practical under real implementation constraints.

## Validation Direction

The framework is intended to support:

* YAML Schema Validation
* Duplicate-key detection
* Semantic Lint
* Message ID and Registry validation
* Length and range validation
* Arithmetic-overflow validation
* Compatibility Review
* Deterministic Code Generation
* Generated-output comparison
* Static Analysis
* Golden Test Vectors
* Cross-language interoperability testing
* Timing and bandwidth measurement
* Resource and Buffer measurement
* Secure Session and Anti-Replay testing
* Firmware Update recovery and rollback testing

A successful syntax check does not prove that a structural rewrite preserved the complete technical Baseline.

Document review, semantic validation, Test Vectors, and implementation evidence remain necessary.

## Contributions and Discussion

Technical review, discussion, and issue reports are welcome.

Public availability does not grant permission to reproduce, modify, redistribute, publish, or incorporate the materials into another Project.

Permission for reuse may be granted separately in writing by the copyright holder.

## Authorship and AI Assistance

The engineering concepts, architecture, rule selection, revisions, and final editorial decisions in this repository are reviewed and approved by Ray Yang.

Generative AI tools were used to assist with drafting, editing, organization, translation, consistency review, and technical review.

AI-assisted material is not accepted solely because it is syntactically correct. Published content remains subject to human technical review and final approval.

## Third-Party Materials

Third-party standards, publications, trademarks, source code, libraries, licenses, and legal notices remain the property of their respective owners.

References to third-party materials do not imply ownership, endorsement, affiliation, or authorization.

MISRA and MISRA C are associated with The MISRA Consortium. Materials in this repository that reference MISRA C do not reproduce or replace the official MISRA publications.

## Copyright and Usage

Copyright © 2026 Ray Yang. All rights reserved.

The materials in this repository are publicly available for review. Public availability does not grant permission to reproduce, modify, redistribute, publish, sublicense, sell, or incorporate the materials into another Project.

See [`COPYRIGHT.md`](COPYRIGHT.md) for the complete copyright, usage, AI-assistance, and third-party-material notices.
