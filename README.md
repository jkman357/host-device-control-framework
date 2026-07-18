# Host-Device Control Framework

A reusable engineering framework for Host-Device control systems in which a PC, SoC, or MCU Host communicates with and controls an MCU-based Device.

The framework defines reusable architecture, protocol, implementation, and engineering-governance practices for embedded control systems.

## Scope

The framework is intended for systems such as:

* PC Host to MCU Device
* SoC Host to MCU Device
* MCU Host to MCU Device
* Command and response communication
* Event, alarm, and fault reporting
* Continuous or periodic data streaming
* Telemetry and status reporting
* Capability discovery and feature negotiation
* Session and connection management
* Firmware update and Bootloader integration
* Embedded C firmware implementation
* Protocol-driven code generation and validation

## Terminology

In this repository:

* **Host** refers to the system that configures, controls, monitors, or collects data. A Host may be a PC, SoC, or MCU.
* **Device** refers to the controlled embedded target, typically an MCU-based system.
* **Coordinator** describes the logical role normally performed by the Host.
* **Node** describes the logical role normally performed by the Device.

Host and Device describe deployment roles. Coordinator and Node describe architectural responsibilities.

## Documents

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

Additional framework documents will be added after public-release review.

## Current Status

This repository is under active development.

The published documents are personal engineering baselines maintained by Ray Yang. They do not represent the official policies, specifications, designs, coding standards, or documentation of any employer, company, or organization.

The published documents have completed document-level review.

Practical validation through Reference Implementations and real Project application remains ongoing.

## Planned Documents

The following documents are planned for later publication after review:

* Coordinator/Node Control Framework
* Framework Application Analysis Template
* Protocol YAML Template
* Reference Implementation documentation
* Code Generator design and validation documentation

The planned-document list is informational only and does not indicate a committed release schedule.

## Repository Structure

```text
host-device-control-framework/
├─ README.md
├─ COPYRIGHT.md
└─ docs/
   ├─ Embedded_C_Coding_Rules_v1.0.13.md
   └─ Protocol_YAML_Definition_Guide_v1.0.3.md
```

## Intended Workflow

The intended engineering flow is:

```text
Coordinator/Node Framework
    |
    v
Application Analysis
    |
    v
Protocol YAML
    |
    +--> Schema Validation
    |
    +--> Semantic Lint
    |
    +--> Code Generation
    |
    +--> Documentation
    |
    +--> Test Vectors
    |
    v
Host and Device Reference Implementations
```

Protocol YAML is intended to serve as the Single Source of Truth for the machine-verifiable wire contract.

Generated artifacts are not intended to become independent design authorities.

## Reference Implementation Direction

Future Reference Implementations are expected to exercise:

* PC, SoC, or MCU Host roles
* MCU-based Device roles
* Command and Response processing
* Event, Alarm, Fault, Telemetry, and Streaming flows
* Static-memory Embedded C
* Event-Driven dispatch
* State Machines
* ISR and callback boundaries
* RTOS and non-RTOS entry points
* Protocol YAML generated contracts
* Cross-language interoperability
* Firmware Update and Bootloader boundaries

Reference Implementations will be used to evaluate whether the published rules remain practical under real implementation constraints.

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
