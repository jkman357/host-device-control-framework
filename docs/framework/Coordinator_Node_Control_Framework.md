# Coordinator/Node Cross-Platform Embedded Control Framework


**Document Name:** `Coordinator_Node_Control_Framework.md`
**Document ID:** CNCF
**Document Version:** v1.1.4
**Status:** Baseline
**Supersedes Document Version:** v1.1.3
**Document Type:** Master Architecture and Engineering Governance Baseline
**Primary Narrative Language:** English
**Author:** Ray Yang
**Maintainer:** Ray Yang
**Repository:** `host-device-control-framework`
**Repository Role:** Normative architecture and framework-governance authority
**Related Documents:**
- `Coordinator_Software_Engineering_Rules.md`
- `Node_Software_Engineering_Rules.md`
- `Protocol_Compatibility_Rules.md`
- `Protocol_Registry_Governance.md`
- `Protocol_Security_Profile.md`
- `Embedded_C_Coding_Rules.md`
- `CSharp_Coding_Rules.md`
- `Protocol_YAML_Definition_Guide.md`
- `Protocol_YAML_Template.md`
- `Framework_Application_Analysis_Template.md`
- `Repository_Validation_Checklist.md`
- `Validation_Evidence_Guide.md`
- `Framework_Conformance_Checklist.md`
- `AI_Generated_Artifact_Validation_Guide.md`

**First Issued:** 2026-07-15
**Last Revised:** 2026-07-20
Copyright © 2026 Ray Yang. All rights reserved.

This document is maintained as part of a personal engineering project. It is not an official
document of any employer or organization. No license is granted unless otherwise explicitly stated.

All third-party standards, publications, trademarks, source code, licenses, and legal notices remain
the property of their respective owners. References to third-party materials do not imply ownership,
endorsement, affiliation, or authorization.


## Architecture, Communication, Security, Real-Time Behavior, Firmware Update, and Engineering Governance Baseline
---

# 0. Document Control

## 0.1 Purpose

This document defines the Master Baseline for reusable Coordinator/Node embedded-control systems.

It integrates architecture, communication, timing, security, Firmware Update, Runtime, platform abstraction,
quality, testing, and governance principles so that the same engineering model can be applied across:

```text
PC Application <-> MCU
Linux SBC <-> MCU
Host MCU <-> Device MCU
Gateway <-> Multiple Nodes
Mobile Application <-> Device
Production Tool <-> Device Under Test
Service Tool <-> Device
Automated Test Platform <-> Node
```

This Framework is not only a PC Application architecture and not only an MCU communication module. It is a
cross-platform system model in which the following may change:

```text
Operating System
RTOS
MCU Vendor
Programming Language
UI Framework
Device IC
Transport
Deployment Topology
```

while the following remain controlled and traceable:

```text
Device Contract
Command and Response Semantics
State and Ownership
Event, Alarm, and Fault Semantics
Timing and Bandwidth Requirements
Security Boundaries
Recovery Behavior
Firmware Update Contract
Compatibility Policy
Validation Evidence
```

## 0.2 Document Position

This document is the authority for:

```text
Coordinator and Node roles
System layering
Responsibility boundaries
Project structure
Control and Data Plane separation
Timing and bandwidth principles
Secure Session boundaries
Firmware Update architecture
RTOS and Bare-metal execution models
BSP / HAL / Driver / Adapter / Service boundaries
Code Generation governance
Testing and acceptance principles
Reference Implementation scope
Architecture and release governance
```

It does not replace:

```text
Product Requirements
Software Requirements Specification
Hardware Design Specification
Hazard Analysis
Product-specific State Machines
UI/UX Specification
Algorithm Design
Product Protocol YAML
C, C#, Java, or other Reference Implementations
Test Procedures
Test Reports
```

The authority boundary is:

```text
Coordinator_Node_Control_Framework
    System roles, layering, boundaries, architecture principles,
    safety placement, timing, security boundaries, and governance.

Coordinator_Software_Engineering_Rules
    Cross-language Coordinator software architecture, lifecycle,
    state ownership, concurrency, communication integration,
    diagnostics, configuration, security, testing, and release behavior.

CSharp_Coding_Rules
    Product-owned C# language and .NET implementation rules.

Protocol_YAML_Definition_Guide
    Protocol YAML syntax, semantics, validation, Code Generation,
    compatibility, and Protocol governance rules.

Protocol_YAML_Template
    Reusable Project Protocol skeleton.

<Application>_protocol.yaml
    Actual Project-specific wire contract and machine-verifiable
    Single Source of Truth.

Application Profile / SRS
    Product behavior, domain semantics, operating flows,
    state rationale, Alarm behavior, UI intent, and limits.

Reference Implementation
    Actual source code, platform integration, threading, buffers,
    Drivers, UI, build configuration, and deployment.
```

## 0.3 Superseded Source Documents

This Framework integrates and supersedes:

```text
Embedded Device Control Framework, document version v1.4.2
Coordinator/Node Architecture, document version v1.2.1
```

Historical snapshots shall be preserved through Git history, tags, Releases, or external archival records. They
shall not remain as parallel maintained authority files and shall not be extended with new normative architecture rules.

## 0.4 Document Filename and Version Rules

Maintained Markdown documents shall use stable canonical repository paths without a version suffix:

```text
docs/framework/Coordinator_Node_Control_Framework.md
docs/framework/AI_Engineering_Usage_Guide.md
docs/framework/Framework_Application_Analysis_Template.md
docs/protocol/Protocol_YAML_Definition_Guide.md
docs/protocol/Protocol_YAML_Template.md
docs/coordinator/Coordinator_Software_Engineering_Rules.md
docs/coding-rules/Embedded_C_Coding_Rules.md
docs/coding-rules/CSharp_Coding_Rules.md
docs/validation/Repository_Validation_Checklist.md
```

The document version shall be recorded inside the document:

```text
Document Version: vMAJOR.MINOR.PATCH
Status: Draft for Review / Baseline / Final Baseline
```

Version history and immutable identity shall be provided by:

```text
Document metadata and Version History
Git commit history
Git tags
GitHub Releases
Release-package or archive names when required
```

A maintained Markdown file shall not be copied beside itself under a new versioned filename for each PATCH or
MINOR revision. The stable path is the current authority path. Historical snapshots shall be preserved through Git
history, tags, Releases, or controlled archives rather than parallel versioned Markdown filenames.

This stable-path rule applies to files maintained inside a controlled Git repository. It does not prohibit a
versioned filename for an immutable artifact distributed outside that repository context.

Immutable release artifacts, audit packages, external deliverables, and detached snapshots shall include the
approved document version or a controlled Baseline identifier in the distributed filename. Examples include:

```text
Smart_Battery_Framework_Application_Analysis_v1.2.0.md
Smart_Battery_Framework_Application_Analysis_v1.2.0.pdf
Smart_Battery_Engineering_Baseline_v1.2.0.zip
```

A detached artifact shall also identify its source repository, canonical maintained repository path, `Document Version`,
Status, and source Git commit, tag, or Release. A downstream SRS, SDD, Test Protocol, or audit record shall cite the
approved document identity and version rather than relying only on a mutable canonical path.

A versioned detached artifact is an immutable distribution copy. It shall not become a second maintained authority
file beside the canonical repository document.

Protocol, Generator, Firmware, Bootloader, Product, or Reference Implementation Code may use:

```text
VMAJOR.MINOR.PATCHRCxx
```

Examples:

```text
V1.0.0RC01
V2.3.0RC02
V2.3.0
```

These identities are independent:

```text
Document Version
!= Protocol Version
!= Generator Version
!= Firmware Version
!= Bootloader Version
!= Product Version
!= Reference Implementation Version
```

A single Framework document version may govern multiple Code release candidates without changing the canonical
Markdown filename.

## 0.5 Version History

| Version | Date | Status | Description |
| --- | --- | --- | --- |
| v1.1.4 | 2026-07-20 | Baseline | Closed Scoped Conformance satisfaction and residual-deviation ambiguity; required a pre-validation claim-boundary baseline, claim lifecycle and invalidation records, and signatory-bounded assessment agreements. |
| v1.1.3 | 2026-07-20 | Baseline | Distinguished Full Framework Conformance, Scoped Framework Conformance, and Nonconforming status; prohibited failure-driven scope laundering; defined non-excludable governance controls; and clarified that conformance is a Project self-declaration rather than author or maintainer certification. |
| v1.1.2 | 2026-07-20 | Baseline | Defined scoped conformance claims, distinguished authorized deviations from unauthorized bypasses, and established the correction, repeated-review, regenerated-evidence, residual-risk approval, and recorded-approval path required before conformance may be claimed or restored. |
| v1.1.1 | 2026-07-20 | Baseline | Added explicit Framework-level conformance-claim integrity and deviation-accountability rules: work produced by bypassing, disabling, ignoring, or materially misapplying applicable requirements, reviews, validation activities, or approval controls cannot claim Framework conformance, and responsibility remains with the human or organization accepting or approving the deviation. |
| v1.1.0 | 2026-07-19 | Baseline | Established the complete Multi-Node architecture baseline for independent links, shared multidrop buses, and routed gateways; distinguished stable identity, runtime address, route, connection generation, Protocol and Secure Sessions; and defined per-Node isolation, lifecycle, targeting, shared-resource, broadcast, multi-target, Firmware Update, and fault-containment requirements while preserving Single-Node compatibility. |
| v1.0.0 | 2026-07-15 | Not recorded | Integrated the Embedded Device Control Framework v1.4.2 and Coordinator/Node Architecture v1.2.1 into one Master Baseline. |
| v1.0.1 | 2026-07-15 | Not recorded | Removed duplicate Protocol/Transport text, corrected Part XI numbering, removed obsolete normative references, removed the duplicate Baseline conclusion, and completed structural and Markdown validation without changing design semantics. |
| v1.0.2 | 2026-07-18 | Not recorded | Converted the complete Framework to English; added Ray Yang authorship, repository identity, copyright, personal-project clarification, and third-party-material notice; aligned terminology and authority boundaries with `Embedded_C_Coding_Rules.md`, `Protocol_YAML_Definition_Guide.md`, and `Protocol_YAML_Template.md`; clarified Telemetry versus Stream semantics, Protocol/Transport boundaries, Application/Bootloader Session separation, Firmware Update transaction identity, runtime Transport Profiles, structural rewrite governance, and public GitHub publication requirements. |
| v1.0.3 | 2026-07-18 | Not recorded | Updated the active related-document references to `Embedded_C_Coding_Rules.md`, `Protocol_YAML_Definition_Guide.md`, `Protocol_YAML_Template.md`, and `Framework_Application_Analysis_Template.md`; synchronized current authority references and version examples without changing architecture, Protocol, safety, security, Runtime, or governance semantics. |
| v1.0.4 | 2026-07-18 | Not recorded | Adopted stable canonical Markdown filenames without embedded versions; moved document identity to metadata, Version History, Git history, tags, and Releases; updated all active cross-document references and examples to stable paths; moved historical snapshot preservation to Git and controlled archives rather than parallel versioned Markdown filenames; and preserved all architecture, Protocol, safety, security, Runtime, and governance semantics except for the filename-governance rule itself. |
| v1.0.5 | 2026-07-18 | Not recorded | Clarified that generated Dispatcher output is Protocol plumbing and shall not contain Product control, state ownership, or hardware access; operationalized the one-authority rule through derived conformance summaries; and generalized interoperability requirements from fixed language pairs to all implementations and language pairs actually in scope. |
| v1.0.6 | 2026-07-18 | Not recorded | Refined filename governance into a two-layer policy: maintained Markdown authority paths remain stable inside controlled Git repositories, while immutable release artifacts, audit packages, external deliverables, and detached snapshots include an approved document version or Baseline identifier in the distributed filename; required detached artifacts to carry source commit, tag, or Release traceability; and preserved all architecture and Protocol semantics. |
| v1.0.7 | 2026-07-18 | Not recorded | Closed the remaining machine-verifiable security and Transport-envelope gaps: required minimal ephemeral public Discovery and authenticated revalidation; bound Handshake Profile selection and complete canonical transcripts against downgrade and profile confusion; required per-Key-Context Record Counter/Rekey profiles; defined exact canonical Firmware signature encodings; clarified fixed-prefix `minimum_length`; and separated plaintext Message, security overhead, secured Record, reassembly, and Fragment size domains. |
| v1.0.8 | 2026-07-18 | Not recorded | Closed the remaining machine-verifiable Protocol-contract gaps by requiring an exact Fragment Header and bounded reassembly policies, concrete named Handshake request/response payloads, explicit Profile allowlists and security-level/deprecation metadata instead of numeric ID ordering, cryptographically authorized Firmware Update resume across Session changes, and a positive data-bearing Fragment payload at every supported minimum MTU. |
| v1.0.9 | 2026-07-18 | Not recorded | Integrated `Coordinator_Software_Engineering_Rules.md` v1.0.1 and `CSharp_Coding_Rules.md` v1.0.1 into Related Documents, the authority boundary, stable document identity, Baseline decisions, and the Authority Matrix; clarified that reusable Coordinator engineering rules and language-specific implementation rules remain subordinate to this Framework, approved Product requirements, and Project-specific design. |
| v1.0.10 | 2026-07-18 | Not recorded | Normalized document-version notation for the Coordinator and C# rule references and aligned the active Draft engineering-rule set with v1.0.2; no reusable architecture, Protocol, safety, security, Runtime, or governance semantics changed. |
| v1.0.11 | 2026-07-18 | Not recorded | Clarified that programming languages do not determine Coordinator, Node, Tool, or Service roles; made the Draft Coordinator and C# rules applicable only after explicit Project adoption or approval; marked their Authority Matrix entries as proposed while Draft; and added repository validation and detached-package traceability expectations without changing Protocol wire semantics. |
| v1.0.12 | 2026-07-19 | Not recorded | Added explicit Supersedes metadata required by repository governance; no normative Framework architecture requirements changed. |
| v1.0.13 | 2026-07-19 | Baseline | Added explicit Repository Role metadata and migrated Version History to the governed Date/Status schema; no normative Framework architecture requirements changed. |
| v1.0.14 | 2026-07-19 | Baseline | Integrated the dedicated Protocol compatibility, Registry, and security governance authorities; Node-specific software engineering authority; and validation evidence/conformance views into Related Documents and the Authority Matrix. All new documents remain conditional Draft authorities; no reusable architecture or wire-contract semantics changed. |

## 0.6 Core Conclusions

> **Coordinator and Node are platform-independent system roles.**

> **Platforms, MCUs, RTOSes, Device ICs, and Transports may change, but the Device Contract, state ownership,
> behavior, safety boundary, and recovery rules shall not drift.**

> **Protocol YAML is the Single Source of Truth for the machine-verifiable wire contract; this Framework is the
> Single Source of Truth for the reusable system architecture and engineering-governance model.**

> **Control may cross platform boundaries, but hard real-time control, fundamental safety protection, and local
> Fault Reaction shall remain on the Node.**

> **Architecture principles shall be converted into rules that can be checked by Code Generators, compilers,
> Static Analysis, Test Frameworks, and CI whenever practical.**

---

# Part I. Core Position, System Layering, and Safety Boundary

## 1.1 Framework Position

The Framework defines a replaceable upper control platform and replaceable lower implementation platform while
preserving stable system semantics.

Possible Coordinator platforms include:

```text
PC Application
Linux SBC
Host or Supervisor MCU
Mobile Application
Production Test Tool
Service Tool
Automated Test Platform
Gateway
```

Possible Node platforms include:

```text
Device MCU
Subsystem MCU
Sensor Controller
Power Controller
Motion Controller
DSP
FPGA Soft-Core
Linux SoC
Dedicated Control Board
Smart Module
```

An initial implementation may be:

```text
PC Application
    |
    v
USB-CDC
    |
    v
Device MCU
```

The architecture shall also permit later profiles such as:

```text
Linux SBC  -> Ethernet / Wi-Fi -> Device MCU
Host MCU   -> UART / CAN FD     -> Device MCU
Mobile App -> BLE / Wi-Fi       -> Device MCU
```

The replaceable elements are:

```text
Execution Platform
Transport
Platform Adapter
Transport Adapter
Device Adapter
Specific Driver
```

The Device Contract and Product behavior are not redesigned merely because a platform or Transport changes.

## 1.2 First-Level Design Goal

The first-level design goal is:

> **One Device Contract, Protocol family, Control Workflow, State Model, Error Model, Security Model, and
> Firmware Update Contract can be implemented by a PC, Linux SBC, Host MCU, or mobile platform.**

Different platforms need not share identical source code.

The reusable asset is:

```text
Specification
Semantics
State
Behavior
Validation Standard
```

not forced source-level uniformity.

## 1.3 System Layers

The system layering is:

```text
Application / HMI
        |
        v
Device Controller
        |
        v
Device Contract
        |
        v
Control Workflow
        |
        v
+----------------------------------+
| Control Plane                    |
| Request / Response               |
| Event / Alarm / Fault / Heartbeat|
+----------------------------------+
| Data Plane                       |
| Telemetry / Stream / Waveform    |
+----------------------------------+
| Firmware Update Plane            |
| Bootloader / Manifest / Image    |
+----------------------------------+
| Protocol Layer                   |
| Message / Record / Version       |
+----------------------------------+
| Secure Session Layer             |
| Authentication / AEAD / Replay   |
+----------------------------------+
| Transport Abstraction            |
| USB / UART / CAN / TCP / BLE     |
+----------------------------------+
```

A Node is internally layered as:

```text
Product Application
        |
        v
Subsystem Service
        |
        v
Generic Device Interface
        |
        v
Specific Device Adapter
        |
        v
Specific Device Driver
        |
        v
Peripheral HAL
        |
        v
BSP / MCU Vendor Layer
        |
        v
Hardware
```

Runtime isolation is divided into:

```text
Core Runtime Abstraction
├─ Event
├─ Timer
├─ Time
├─ Critical Section
└─ ISR Notification

RTOS Extension
├─ Task
├─ Mailbox
├─ Semaphore
└─ Mutex
```

## 1.4 Layer Responsibilities

Each layer shall solve only its own problem:

```text
Application shall not directly operate UART, Socket, CAN, or BLE handles.
UI shall not assemble wire frames.
Protocol shall not know whether the Transport is USB, CAN, Wi-Fi, or BLE.
Transport shall not interpret START, STOP, Battery Status, or Sample records.
Device Service shall not manipulate IC registers.
Driver shall not own Product control policy.
```

Dependency direction shall flow toward abstractions and contracts, not upward from Vendor APIs into Product logic.

## 1.5 Device Contract as a Core Asset

A Coordinator shall not need knowledge of:

```text
MCU vendor
Register addresses
GPIO numbers
RTOS Task names
Memory addresses
Vendor HAL handles
Specific Driver APIs
```

The Coordinator operates through device semantics such as:

```text
Initialize
Start
Stop
Set Parameter
Get Status
Reset Fault
Start Stream
Stop Stream
Enter Update Mode
Get Device Information
```

The Device Contract shall define:

```text
Command semantics
Request and Response Payloads
Parameter units and ranges
Status definitions
Event, Alarm, and Fault semantics
Error codes
Timeout behavior
Capabilities
Version and compatibility rules
```

A UI action may trigger a command, but a UI control name shall not become the Protocol definition.

## 1.6 Control Role and State Authority

The system shall explicitly identify:

```text
Who owns control authority
Who stores the accepted configuration
Who is the authoritative source of state
Who starts and stops operation
Who performs safety protection
Who reacts to disconnection
Who synchronizes state after reconnect
```

The Coordinator may request a target or action. The Node shall report what it actually accepted and its actual
current state.

`Command sent` does not mean `Command accepted`, and `Command accepted` does not always mean `Operation completed`.

## 1.7 Node Autonomy

The Node shall remain responsible for:

```text
Hard real-time control
Basic safety protection
Fault Detection
Emergency Stop behavior
Watchdog
Output limits
Communication-loss handling
Required degraded mode
Safe-state transition
```

The Coordinator may provide:

```text
Operator command
Target value
Configuration
Visualization
Data logging
Diagnostics
Maintenance
Firmware Update coordination
```

The Node shall not require a healthy Coordinator connection merely to remain fundamentally safe.

When Hazard Analysis requires an independent emergency path, the Project shall evaluate:

```text
Dedicated GPIO
Hardware Interlock
Dedicated Safety Bus
Out-of-band Stop Path
```

A safety mechanism shall not rely solely on USB, Wi-Fi, BLE, or an ordinary in-band STOP command.

---

# Part II. Coordinator/Node Roles and Project Organization

## 2.1 Core Project Structure

The Project root shall use:

```text
<Product>/
├─ protocol/
├─ coordinator/
├─ node/
├─ shared/
├─ tools/
└─ docs/
```

The core responsibility directories are:

```text
protocol/
coordinator/
node/
```

Their meanings are independent of hardware, OS, RTOS, language, and Transport.

## 2.2 Coordinator Role

The Coordinator owns system-level coordination and Node management.

Typical responsibilities include:

```text
System workflow coordination
Node discovery and registration
Identity and Capability acquisition
Command initiation
Response correlation
Event, Alarm, Fault, and Telemetry aggregation
Session establishment and reconnect coordination
Configuration synchronization
Firmware Update coordination
Multi-Node routing
UI/HMI integration
Logging, diagnostics, and external-system integration
```

Coordinator does not mean permanent Sender, Requester, or Connection Initiator.

## 2.3 Node Role

The Node owns local execution.

Typical responsibilities include:

```text
Local real-time control
Data acquisition
Hardware Drivers
Command validation and execution
Status, Event, Alarm, and Fault reporting
Telemetry and Stream publication
Watchdog and Fault Reaction
Local safety protection
Firmware Update execution
Disconnect degradation or safe-state behavior
```

Node does not mean passive slave.

## 2.4 Role Relativity

Roles are relative to one relationship:

```text
PC Tool
   |
   v
Coordinator MCU
   |
   v
Motor MCU
```

For the upper link:

```text
PC Tool         = Coordinator
Coordinator MCU = Node
```

For the lower link:

```text
Coordinator MCU = Coordinator
Motor MCU       = Node
```

One physical system may therefore act as a Node toward an upper layer and a Coordinator toward a lower layer.

The architectural model may be reused across levels without requiring identical Command Sets, Security Policies,
Transports, timing, or failure policies.

## 2.5 Separate System, Message, Event, Transport, and Connection Roles

Do not confuse:

```text
System Role:      Coordinator / Node
Message Role:     Requester / Responder
Event Role:       Publisher / Subscriber
Transport Role:   Sender / Receiver
Connection Role:  Initiator / Acceptor
```

Coordinator may be:

```text
Command Requester
Event Subscriber
Response Receiver
Telemetry Consumer
Update Coordinator
```

Node may be:

```text
Command Responder
Event Publisher
Telemetry Sender
Alarm Sender
Update Executor
```

The system shall be Event-Driven by default, with low-rate health queries when required:

```text
Event-Driven primary behavior
Periodic Health Check as support
Full-state query when reconciliation is required
```

Avoid continuous high-rate indiscriminate polling. Do not ban all querying.

## 2.6 Coordinator Directory

Recommended structure:

```text
coordinator/
├─ application/
├─ node_management/
├─ communication/
├─ workflows/
├─ platform/
├─ config/
└─ tests/
```

`application/` owns Product-level state and operation.

`node_management/` owns registration, discovery, identity, Capability, state, command, timeout, retry, monitoring,
and update coordination.

`communication/` is divided into:

```text
transport/
protocol/
protocol_adapter/
session/
routing/
security/
```

`workflows/` owns cross-module flows such as Startup, Shutdown, Configuration, Calibration, Data Acquisition,
Log Download, Firmware Update, and Recovery.

`platform/` isolates Windows, Linux, MCU, file-system, thread, timer, USB, UART, CAN, TCP, Wi-Fi, and BLE APIs.

## 2.7 Node Directory

Recommended structure:

```text
node/
├─ application/
├─ control/
├─ communication/
├─ platform/
├─ bootloader/
├─ config/
└─ tests/
```

`application/` owns:

```text
System State
Task or Service
Event or Mailbox handling
State Machines
Fault Handling
Operation Mode
```

`control/` may contain:

```text
control/
├─ motor_ctrl/
├─ power_ctrl/
├─ sensor_ctrl/
├─ battery_ctrl/
├─ alarm_ctrl/
└─ safety_ctrl/
```

`communication/` may contain:

```text
communication/
├─ transport/
├─ protocol/
├─ protocol_adapter/
├─ command_dispatcher/
├─ event_publisher/
├─ session/
└─ security/
```

Command Dispatcher shall validate and translate a Protocol command into an Application Event or Service Request.
It shall not directly operate hardware.

Not recommended:

```c
case CMD_MOTOR_START:
    PWM_ENABLE();
    MOTOR_DRIVER_START();
    break;
```

Recommended:

```c
case CMD_MOTOR_START:
    app_event_post(APP_EVENT_MOTOR_START_REQUEST, &request);
    break;
```

`platform/` isolates BSP, HAL, Drivers, RTOS, startup, and Vendor APIs.

`bootloader/` is an independent Application and shall have its own communication, security, image, flash,
platform, and tests.

## 2.8 Node Identity and Capability

The Protocol shall expose at least:

```text
Node ID
Node Type
Hardware Revision
Firmware Version
Bootloader Version
Protocol Version
Capabilities
```

Node Type describes identity. Capability describes actual supported behavior.

A Coordinator shall prefer Capability-based decisions over large `switch(node_type)` structures.

Two Nodes with the same Type may expose different Capabilities because of Hardware Revision, Firmware version,
license, configuration, or Product variant.

## 2.9 Shared Directory

`shared/` is reserved for components that are:

```text
Independent of Coordinator
Independent of Node
Independent of Product workflow
Independent of specific hardware
Independent of OS or RTOS
Used by at least two real consumers
Independently testable
```

Examples include CRC, generic Ring Buffers, platform-independent utilities, and generic data structures.

Protocol Generated Code belongs under `protocol/generated/`, not `shared/`.

Premature extraction based only on anticipated reuse is prohibited.

## 2.10 Tools and Documents

Recommended tools:

```text
tools/
├─ protocol_codegen/
├─ protocol_lint/
├─ compatibility_testgen/
├─ packet_decoder/
├─ log_converter/
├─ firmware_image_packer/
├─ signing_tool/
├─ production_test/
├─ static_analysis/
├─ fuzzing/
├─ simulator/
└─ fault_injection/
```

Recommended system documents:

```text
docs/
├─ system_architecture.md
├─ role_definition.md
├─ communication_flow.md
├─ task_model.md
├─ state_machines.md
├─ security_model.md
├─ firmware_update_flow.md
├─ compatibility_policy.md
├─ static_analysis_policy.md
├─ test_strategy.md
├─ build_process.md
└─ release_process.md
```

`protocol/docs/` stores Protocol-specific documentation. Root `docs/` stores system-level documentation.

## 2.11 Single-Node and Multi-Node Architecture Baseline

The Framework supports the following topology classes:

```text
Single Node on one connection
Multiple Nodes on independent point-to-point connections
Multiple Nodes on a shared multidrop bus
Nodes reached through one or more routed gateways
```

A Project shall select and record its topology in the Framework Application Analysis and Project Protocol. The
Framework does not require every Transport to encode a Node address in every Record. A connection-bound
point-to-point profile may identify the target by an immutable connection-to-Node binding. A shared bus or route
that cannot identify one target by connection context shall carry or derive an unambiguous target identity under
the approved Transport Profile and Protocol.

### 2.11.1 Identity, Address, Route, and Session Separation

The design shall distinguish:

```text
Stable Node identity
Runtime Node address
Transport endpoint identity
Logical route
Physical connection
Connection generation
Protocol Session
Secure Session
Operation correlation identity
```

A bus address, socket, USB port, CAN identifier, Session ID, or route shall not be treated as a permanent Node
identity unless the approved Project authority explicitly defines that equivalence. Address reassignment or
connection replacement shall not silently transfer the previous Node's Session, authorization, pending Requests,
or observed state.

### 2.11.2 Per-Node Context and Isolation

Each registered Node shall have a distinct context, or an equivalent design with the same isolation properties,
covering at least:

```text
Identity and current address or route
Transport connection and connection generation
Protocol Session and Secure Session
Capability and negotiated-version state
Sequence and replay context
Request/Response correlation and pending operations
Observed actual state and freshness
Immutable command-target binding
Lifecycle state
Resource quota and diagnostic context
Firmware Update transaction state
```

A mutable global `current_device` or UI selection shall not be the authoritative target of an operation after that
operation has been created. One Node's reconnect, malformed traffic, stream flood, timeout, cancellation, reset,
or update shall not clear, rebind, starve, or corrupt another Node's state or operations.

### 2.11.3 Node Registry and Lifecycle

The Coordinator shall maintain a bounded Node Registry. The Project shall define an equivalent lifecycle covering:

```text
Unknown
Discovered
Registering
Online
Degraded
Reconnecting
Offline
Removed
Replaced
Quarantined
```

Lifecycle transitions shall define identity verification, address assignment, capability discovery, Session
establishment, reconciliation, stale-generation rejection, removal, and replacement. The same stable identity on
multiple active paths, multiple identities claiming one address, an address reused by another Node, and an
unauthorized or excess Node shall not be resolved by silent last-writer-wins replacement.

### 2.11.4 Targeting and Operation Classes

The architecture shall distinguish:

```text
Single-target operation
Protocol broadcast
Coordinator-expanded multi-target operation
Aggregate query or aggregate presentation
Coordinator-wide local operation
```

Selecting several Nodes in a UI does not by itself create a Protocol broadcast. A multi-target operation shall
snapshot its target set and maintain an operation-level identity plus per-Node sub-operation state, progress,
timeout, retry, cancellation, and final result. Partial success and partial failure shall be explicit. Rollback shall
not be implied when the Product authority has not defined a safe rollback.

Safety-significant control, configuration, reset, Rekey, credential, and Firmware Update operations shall default
to single-target behavior unless the Project authority explicitly permits and validates multi-target or broadcast
use.

### 2.11.5 Broadcast and Shared-Bus Behavior

When broadcast is supported, the Project Protocol shall define:

- authorized Message categories and prohibited categories;
- whether Nodes execute without a response or use polling, slots, a bounded response window, or another
  collision-controlled response policy;
- duplicate, late, unauthorized, and wrong-target behavior;
- observability of partial execution and failure;
- interaction with security, replay protection, and Firmware Update.

A broadcast design shall not permit uncontrolled simultaneous responses or ambiguous per-Node completion.

### 2.11.6 Shared Resources and Bounded Capacity

A Multi-Node Coordinator shall define both per-Node and aggregate limits for registered and online Nodes, pending
Requests, receive queues, stream and telemetry bandwidth, logging, reconnect attempts, discovery candidates,
concurrent operations, and Firmware Updates. Shared schedulers shall define priority, fairness, starvation
prevention, overload behavior, and observability.

One Node shall not exhaust resources required for other Nodes through traffic rate, malformed input, reconnect
storms, logging amplification, or repeated failures.

### 2.11.7 Security and Trust Isolation

Unless an approved security authority defines another model, authentication, authorization, Session keys, Record
Counters, Replay windows, Rekey state, and Firmware Update authorization shall be bound to the authenticated
stable Node identity and current connection generation. Address reuse shall require fresh identity verification and
Session establishment. A routed gateway shall not silently extend trust to downstream Nodes.

Group keys or shared Secure Sessions are not implied by Multi-Node support. They require an explicit security
profile, authorization model, compromise analysis, rotation and revocation policy, and validation evidence.

### 2.11.8 Firmware Update Coordination

The Project shall define whether Firmware Updates are single-target only, serialized across Nodes, or bounded in
parallel. Target identity, image compatibility, transaction state, signed Manifest, resume authorization, progress,
activation, reconnect, and post-activation verification shall remain attributable to one Node. One failed update
shall not corrupt another Node's update state.

### 2.11.9 Aggregate State

Coordinator aggregate status, alarms, progress, health, and availability shall be derived from identifiable per-Node
state. Aggregate presentation shall preserve Node attribution and shall not hide partial failure, stale state, or an
unknown target. Aggregate state is not a substitute for the Node's authoritative actual state.

### 2.11.10 Backward-Compatible Single-Node Use

A first implementation may use one active Node, one connection-bound target, and one outstanding Request.
Omission of a conditional Multi-Node declaration may retain the legacy Single-Node interpretation defined by the
Protocol YAML authority. This compatibility does not permit implementation code to discard stable identity,
connection generation, Session ownership, correlation, or bounded resource concepts needed for safe evolution.

## 2.12 Build Targets and Physical Directories

Build Target, IDE Project, Solution, and physical directory are separate concepts.

Example directories:

```text
coordinator/windows/
coordinator/linux/
coordinator/mcu/
node/stm32/
node/tm4c/
node/renesas/
```

Different targets may depend on:

```text
protocol/generated/
shared/
application interfaces
platform abstractions
```

A Build Target is a configuration and dependency set, not an architectural role.

Directory migration shall be incremental:

```text
Create new directory
-> Create Build Target
-> Move low-coupling modules
-> Add Adapter
-> Update tests
-> Remove old path
```

A large unverified directory rewrite without a compilable Baseline and regression tests is prohibited.

---

# Part III. Device Contract, Protocol, and Single Source of Truth

## 3.1 Protocol Directory

The Project-specific Protocol contract belongs under:

```text
protocol/
├─ spec/
│  └─ <Application>_protocol.yaml
├─ schema/
├─ docs/
├─ codegen/
├─ test_vectors/
└─ generated/
```

The exact YAML structure and Protocol authoring rules are defined by:

```text
Protocol_YAML_Definition_Guide.md
Protocol_YAML_Template.md
```

This Framework shall not duplicate the complete field-level Protocol definition.

## 3.2 Protocol Contract Content

The Protocol Contract shall define, as applicable:

```text
Message IDs
Request and Response relationships
Event, Alarm, and Fault
Telemetry and Stream
Payload Layout
Data Types, Units, Scale, Range, Enum, and Bitsets
Endianness
Length Policy
Unknown Data Policy
Timeout and Retry
Sequence and Correlation
Execution Environment
Capability
Security Attributes
Protocol Version and Compatibility
Transport Profiles
Fragmentation
Firmware Update contract
```

It shall not define UI colors, MCU registers, control algorithms, or Product-specific business rationale.

## 3.3 Machine-Readable Specification, Human Documentation, and Test Vectors

The Protocol shall have:

```text
Machine-Readable Specification
Human-Readable Documentation
Test Vectors
```

The machine-readable specification supports:

```text
Code Generation
Field validation
ID management
Payload definitions
Documentation generation
Compatibility checks
Boundary tests
Fuzz seed corpus
Mock Node
Packet decoder
```

Human documentation explains rationale, state, timeout, exceptional behavior, and security context.

Test Vectors prove that different languages and platforms interpret the same Message identically.

## 3.4 Protocol Versioning

Protocol compatibility shall follow MAJOR, MINOR, and PATCH semantics.

Handshake shall evaluate Protocol compatibility and Capability, not only Firmware version.

A new Firmware version does not automatically imply a new Protocol version, and a compatible Protocol MINOR
version does not require identical Product functionality on every platform.

## 3.5 Safe Payload Decoding

Wire Format and native C struct layout shall remain separate.

Prohibited:

```c
const motor_command_t *command =
    (const motor_command_t *)payload;
```

A decoder shall:

```text
Validate pointers
Validate length
Validate every offset and field size
Handle endianness explicitly
Validate multiplication before variable-array access
Check destination capacity
Apply Optional Field defaults
Apply unknown-trailing policy
Reject invalid Enum, Range, Alignment, or overflow conditions
```

Field-by-field encoding and decoding is the default.

The Embedded C implementation shall also comply with `Embedded_C_Coding_Rules.md`.

## 3.6 Message Length and Unknown Data

Every Message shall use one declared Length Policy:

```text
exact
minimum
extensible
tlv
```

Message length fields apply to the encoded plaintext Payload defined by the Protocol YAML and exclude outer Record
headers, Security headers, Authentication Tags, and Fragment headers.

`minimum_length` is the fixed decoding prefix before the first variable-length or optional trailing field. Minimum
variable count, calculated total length, actual received length, remaining bytes, destination capacity, and arithmetic
overflow are validated separately.

Only an explicitly extensible Message may ignore unknown trailing fields.

Existing field order, type, size, signedness, and endianness shall not be changed under a compatible MINOR version.

## 3.7 Protocol and Transport Decoupling

One Device command may be carried through:

```text
USB-CDC
UART
RS-232
RS-485
RS-422
CAN
CAN FD
SPI
Ethernet
TCP
Wi-Fi
BLE
```

Layering shall remain:

```text
Device Controller
        |
        v
Protocol
        |
        v
Secure Session
        |
        v
Transport Interface
        |
        v
Platform Driver
```

Protocol shall not contain COM port names, UART registers, Socket handles, CAN Driver APIs, USB Endpoints, SSIDs,
or BLE Characteristic handles.

Transport owns connection, send, receive, buffering, link errors, MTU, and physical delivery. It does not
interpret Product commands.

## 3.8 Protocol Evolution

The first release shall account for:

```text
Protocol Version
Device Model
Firmware Version
Bootloader Version
Hardware Revision
Execution Environment
Capability Query
Feature Negotiation
Unsupported Message behavior
Parameter ranges
Backward Compatibility
Deprecation
Transport Profile
```

Optional features shall be negotiated by Capability rather than guessed only from model or version.

## 3.9 Telemetry and Stream Boundary

Telemetry and Stream are distinct.

Use Telemetry for:

```text
Complete summarized state snapshots
Periodic or change-driven state
Replaceable older unsent values
Latest-state consumers
```

Use Stream for:

```text
Ordered samples or records
Raw waveform or acquisition frames
Loss, duplicate, or reordering detection
Sequence and timestamp continuity
Non-replaceable deltas or chunks
```

Transmission rate alone shall not determine the category.

The authoritative field-level rules are in `Protocol_YAML_Definition_Guide.md`.

## 3.10 Generated Code

Generated artifacts may include C, C#, and Java types, constants, codecs, validation, dispatch skeletons,
documentation, tests, and decoder metadata.

A generated dispatch skeleton is Protocol plumbing only. It may decode, validate, correlate, and forward a typed
request to a handwritten Application Adapter or Service boundary. It shall not own Product State Machines,
perform physical control, call hardware Drivers directly, or become a second Command Dispatcher authority.

Every generated file shall identify:

```text
Auto-generated status
Do-not-edit instruction
Source specification identity
Protocol version
Generator name and version
Source hash when applicable
```

Generated files shall not become independent design authorities.

---

# Part IV. Control Plane, Data Plane, Streaming, and Timing

## 4.1 Control Plane and Data Plane Separation

The Framework may carry:

```text
Request / Response
Event / Alarm / Fault
Heartbeat
Telemetry
Stream
Waveform
Bulk Sample Data
```

Control and continuous data shall not share one blocking processing path.

```text
Protocol Dispatcher
├─ Control Plane
│  ├─ Request
│  ├─ Response
│  ├─ Event
│  ├─ Alarm
│  ├─ Fault
│  └─ Heartbeat
└─ Data Plane
   ├─ Telemetry
   ├─ Stream
   ├─ Waveform
   └─ Bulk Data
```

Control and Data may share a Transport but shall have independent scheduling, buffering, and priority behavior.

While Streaming is active, the system shall still process:

```text
STOP
RESET_FAULT
GET_STATUS
ALARM
FAULT
HEARTBEAT
LINK_RECOVERY
```

## 4.2 Non-Blocking Request and Response

A Request shall not block Event, Alarm, Fault, Telemetry, or Stream processing.

The first MCU-oriented Baseline may permit only one outstanding Request while Streaming continues.

Multiple outstanding Requests may be added when the correlation, timeout, cancellation, and resource model are
explicitly defined and tested.

## 4.3 Sample Period and Record Period

Sampling period and record-transmission period are different:

```text
Sample Period != Record Period
```

Example:

```text
Sample Period:       5 ms
Samples per Record:  4
Record Period:       20 ms
```

Aggregation reduces average framing and security overhead but increases record size and waiting time.

Every aggregated profile shall be revalidated for:

```text
Control blocking time
Maximum Record Size
Buffer capacity
Latency
Fragmentation
Loss impact
Recovery behavior
```

## 4.4 Timing Budget

A Product shall define end-to-end timing stages:

```text
Device acquisition
Node processing
Record assembly
Security processing
Transport waiting
Serialization or air time
Coordinator receive
Decode and validation
Application dispatch
UI or external consumer
```

Average timing is insufficient. Worst-case timing and scheduling interference shall be measured.

## 4.5 Bandwidth Budget

The bandwidth model shall include:

```text
Channel Count
Bits per Sample
Sample Rate
Samples per Record
Metadata
Protocol Header
Session and Security Header
Authentication Tag
Fragmentation overhead
Retry allowance
Reserved Control bandwidth
Serialization or air time
```

A Transport profile is acceptable only when both average bandwidth and worst-case control latency pass.

## 4.6 115200-Baud Example

A fixed-overhead profile at 115200 baud may become inefficient when each record contains only one small sample
group. Where a record has approximately 36 bytes of fixed Protocol and security overhead, aggregation such as:

```text
4 samples per 20 ms record
```

may be more practical than one encrypted record every 5 ms.

This is an engineering example, not a universal requirement. The Project shall calculate its own exact payload,
framing, escaping, line-coding, retry, and latency costs.

When the profile cannot satisfy throughput and latency simultaneously, evaluate:

```text
460800 baud or higher
USB-CDC
CAN FD
Ethernet
Reduced channel count
Reduced sample rate
Different aggregation
A separate data path
```

## 4.7 Queue and Buffer Policy

Every producer/consumer path shall define:

```text
Buffer type
Static capacity
Producer
Consumer
High-water threshold
Overflow policy
Backpressure
Drop policy
Sequence-gap behavior
Recovery action
```

UI display buffers and recording buffers should be separate when their loss policies differ.

A slow UI shall not silently reduce raw recording integrity.

## 4.8 Priority

Recommended scheduling order is:

```text
Emergency or safety control
Fault and Alarm
Normal control
Heartbeat and health
Telemetry
Stream
Background bulk transfer
```

Priority does not bypass security, validation, or state checks.

## 4.9 Stale Data

Every displayed or consumed status shall have a freshness policy.

When data becomes stale, the system shall:

```text
Mark it stale
Stop presenting it as current
Avoid unsafe automatic action
Request reconciliation when appropriate
```

Reconnect does not automatically restore Application state. Current Node state shall be queried and reconciled.

---

# Part V. Transport Profiles, Bandwidth Envelope, and Link Management

## 5.1 Transport as a Formal Profile

Each Transport Profile shall distinguish and bound:

```text
MTU and Fragment payload
Maximum plaintext Message size
Protocol Record header
Security header
Authentication Tag
Maximum security overhead
Maximum secured Record size
Maximum Transport reassembly size
Maximum Fragment count
Throughput and latency
Retry, connection, Buffer, and failure behavior
```

A Product shall not claim Transport support without a bounded and tested Profile.

## 5.2 Size-Domain Relationship

The following are different engineering quantities:

```text
Plaintext Message
Secured Record
Transport-reassembled Record
Transport Fragment
```

The maximum secured Record is the maximum plaintext Message plus the declared Protocol and security overhead. The
reassembly Buffer shall hold the maximum secured Record. Fragment capacity shall cover that secured Record within
the bounded maximum Fragment count. One ambiguous `maximum_record_size` shall not be used for all layers.

## 5.3 Static and Runtime Effective Profile

Fixed and dynamically negotiated Transports shall define a safe supported envelope. Runtime negotiation uses the
most restrictive Product, Node, Transport, Buffer, security-overhead, and negotiated limit. If insufficient, the
system explicitly reduces the requested profile or rejects it; it shall not silently exceed a Buffer or latency bound.

## 5.4 Fragmentation

Fragmentation shall define Fragment header size, maximum Fragment payload, Fragment count, secured original Record
length, reassembly timeout, duplicate and out-of-order policy, maximum concurrent reassembly, integrity scope, memory
requirement, and abort behavior. Untrusted announced lengths shall never cause unbounded allocation.

## 5.5 Maximum Non-Preemptible Transfer Time

Even when average throughput passes, a large non-preemptible record may block critical control.

Each profile shall define a maximum non-preemptible transfer or processing time.

Firmware chunks, file transfer, and large Stream records shall be sized so that STOP, Fault, Alarm, and link
recovery remain serviceable.

## 5.6 Link Management State Machine

Link Management shall be an explicit State Machine, for example:

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
ACTIVE
```

Failure and recovery paths shall include:

```text
DEGRADED
RECONNECT_WAIT
RECONNECTING
REAUTHENTICATING
STATE_RECONCILIATION
```

Link state, Secure Session state, Application state, and Firmware Update transaction state shall not be treated as
one state variable.

## 5.7 Wireless Link Behavior

Wireless communication may experience:

```text
Jitter
Packet loss
Temporary disconnection
Reconnect
MTU change
Throughput variation
Latency spikes
```

The Node's local real-time control and safety behavior shall remain valid despite these conditions.

Wi-Fi WPA or BLE pairing does not replace the Framework Secure Session when the Product requires end-to-end
authentication, authorization, integrity, anti-replay, or Application/Bootloader key separation.

## 5.8 Transport and Protocol Boundary

Transport differences shall not change Device Contract semantics.

A START command remains a START command across USB, CAN, Wi-Fi, and BLE.

Transport-specific constraints may limit which Capability or Stream Profile is available, but shall not create
undocumented alternate Product semantics.

---

# Part VI. Secure Sessions, Key Contexts, Rekey, and Anti-Replay

## 6.1 Security Architecture

A recommended model is hybrid cryptography:

```text
Asymmetric cryptography
    Establishes identity, trust, authentication,
    and ephemeral Session material.

Symmetric cryptography
    Protects sustained control and data traffic
    with practical MCU performance.
```

The actual algorithms and credential model are Product-specific security decisions and shall be documented.

## 6.2 Application and Bootloader Session Separation

Application and Bootloader are separate Execution Environments.

They may share:

```text
Long-term Device identity
Trust anchor
Approved cryptographic library
Transport abstraction
Protocol family
```

They shall not share:

```text
Runtime Session ID
Session Epoch
Application Session Keys
Bootloader Session Keys
Record counters
Anti-Replay window
Rekey state
```

Entering Bootloader invalidates the Application Session.

Application Session keys shall not survive reset or Bootloader entry.

## 6.3 Key Context Separation

At minimum, separate directional and purpose contexts such as:

```text
Application Control H2D
Application Control D2H
Application Data H2D
Application Data D2H
Bootloader Update H2D
Bootloader Response D2H
```

A key or counter from one context shall not be used by another context.

## 6.4 Public Discovery and Authenticated Revalidation

Unauthenticated Discovery shall expose only the minimum ephemeral information needed to select an approved
Handshake path. It shall not expose a permanent Device UUID or authoritative Capability state.

The Discovery policy shall define an ephemeral identifier and rotation, exposure rationale, permitted fields,
rate limit, excess behavior, failure behavior, transcript binding, and authenticated post-Session revalidation.
Unauthenticated hints shall not authorize downgrade or Product behavior.

## 6.5 Handshake Profile and Transcript Binding

A Handshake Profile shall use concrete approved Key Agreement, KDF, cipher suite, proof format, and credential model.
Product Baselines shall not retain unresolved security sentinels.

A wire `handshake_profile_id` shall equal the Profile referenced by the Message. Mismatch, unsupported Profile, or a
Profile below the approved minimum shall be explicitly rejected without silent fallback.

The canonical transcript binds Protocol family/version, Discovery ID, Profile ID, Execution Environment, roles,
identities, nonces, ephemeral public keys, negotiated algorithms, Session ID, and derived Key Contexts.

## 6.6 Nonce and Record Counter

A nonce shall never repeat under the same key.

The exact nonce format is Protocol-specific, but it commonly binds:

```text
Session or Epoch identity
Direction
Key Context
Security Record Counter
```

Record counters shall not overflow or silently wrap under the same key.

## 6.7 Counter Limits

Each Execution Environment and Key Context shall reference a machine-verifiable Record Counter/Rekey Profile defining:

```text
Counter width and initial value
Soft Threshold
Rekey Deadline
Hard Limit
Counter persistence policy
Reset conditions
Receive gap and out-of-order policy
Counter-exhaustion behavior
Atomic Rekey cutover and old-Epoch acceptance
Failure behavior
```

Soft Threshold initiates rekey preparation.

Rekey Deadline is the point after which new ordinary traffic should be restricted while rekey completes.

Hard Limit is an uncrossable security boundary. Traffic requiring the exhausted context shall stop before the
limit is exceeded.

## 6.8 Session-Wide Rekey

Within one Execution Environment and one Session Epoch, the earliest context approaching its security limit may
trigger Session-wide Rekey.

An atomic cutover shall ensure that sender and receiver agree on:

```text
Old Epoch acceptance window
New Epoch activation
Counter reset for new keys
Late old-epoch handling
Failure rollback or disconnect
```

Application and Bootloader do not perform one atomic cross-reset Rekey because they are separate Sessions.

## 6.9 Anti-Replay

A Sliding Window is appropriate for traffic that may arrive slightly out of order.

Anti-Replay alone does not prove that a state-sensitive command is still appropriate.

A safety-sensitive or state-sensitive command may also require:

```text
Allowed State
Maximum Command Age
Operation ID
Transaction ID
One-time token
Expected current state
Duplicate policy
```

A fail-safe command shall not be delayed by an unnecessary extra token round trip when the Hazard Analysis
requires prompt action.

## 6.10 Authentication and Authorization

Authentication proves an identity or trusted peer.

Authorization determines whether that authenticated peer may execute a specific operation.

Security-sensitive operations include:

```text
Start or Stop
Configuration change
Fault clear
Credential management
Bootloader entry
Firmware Update
Factory or service operation
Protected diagnostics
```

The Protocol shall declare privilege and failure behavior.

## 6.11 Security Failure Policy

The Product shall define behavior for:

```text
Authentication failure
Handshake proof failure
Integrity failure
Replay detection
Wrong Session ID
Wrong Key Context
Counter gap
Counter exhaustion
Rekey deadline reached
Expired Session
Execution Environment mismatch
Security downgrade attempt
Manifest hash failure
Firmware signature failure
Repeated failed authentication
Credential revocation
```

Security failures shall be observable and auditable without exposing secret material.

## 6.12 Security Performance

Measure:

```text
Handshake time
Per-record encrypt time
Per-record decrypt time
Authentication Tag overhead
Worst-case CPU loading
DMA and Crypto concurrency
Wireless Stack loading
Rekey time
Worst-case scheduling delay
```

Application and Bootloader shall be measured separately.

Security design is incomplete if its worst-case timing breaks control, watchdog, or Firmware Update requirements.

## 6.13 Machine-Verifiable Fragmentation Contract

Fragmentation shall use one exact wire Header containing Record identity, Fragment index and count, original secured-Record length, Fragment payload length, and corruption detection. Duplicate, conflicting, out-of-order, integrity, timeout, oversize, incomplete-record, abort, and resource-exhaustion behavior shall be bounded and explicit.

For every Runtime MTU, `runtime_mtu > fragment_header_bytes`, the Fragment payload shall be positive, and the required Fragment count shall not exceed the declared maximum.

---

# Part VII. Firmware Update, Bootloader, Resume, and Rollback

## 7.1 Firmware Update as an Independent Plane

Firmware Update shall be modeled as:

```text
Firmware Update Plane
├─ Bootloader Discovery
├─ Enter Update Mode
├─ Bootloader Handshake
├─ Manifest Transfer
├─ Image Chunk Transfer
├─ Flow Control and Resume
├─ Bootloader Rekey
├─ Image Authentication
├─ Activation and Confirmation
└─ Rollback and Recovery
```

Firmware Update may reuse Transport abstraction, framing, and long-term identity, but shall not reuse Application
Session keys.

## 7.2 Bootloader-Specific Session

Bootloader shall perform its own Handshake and establish Bootloader-specific Key Contexts.

Application and Bootloader Handshakes shall use named concrete wire structs. Profile selection shall use explicit
allowlists, preference order, security level, and deprecation status; numeric Profile-ID ordering shall not represent
security strength.

Wireless reconnect may preserve a valid Update Transaction, but the previous Bootloader Secure Session shall be
invalidated or resumed only under an explicit approved policy.

After reconnect or Rekey, the Bootloader shall reauthenticate the peer and revalidate the Update Transaction
identity before accepting more chunks.

## 7.3 Update Transaction versus Secure Session

The Update Transaction is independent of one Secure Session.

Persisted Update Transaction state may include:

```text
Update Transaction ID
Image ID
Manifest hash
Expected image size
Expected image hash
Security version
Confirmed offset
Chunk bitmap or next expected offset
Flash progress
```

Rekey or reconnect shall not change the Manifest, Image ID, expected hash, security version, or committed progress.

A new Secure Session shall not be allowed to attach to an Update Transaction merely because it knows an offset.
It shall present a cryptographic resume authorization bound to the Update Transaction ID, Manifest hash, authenticated
Device identity, authorized Host identity, security version, monotonic resume generation, and fresh nonce. The
Bootloader shall validate the token before exposing persisted progress or accepting chunks, and shall define token
key scope, persistence, replay handling, reissue, and terminal invalidation conditions.

## 7.4 Update State Machine

A representative flow is:

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
BOOTLOADER_LINK_WAIT
        |
        v
BOOTLOADER_HANDSHAKE
        |
        v
BOOTLOADER_SESSION_ESTABLISHED
        |
        v
AUTHENTICATE_UPDATE_REQUEST
        |
        v
RECEIVE_MANIFEST
        |
        v
CHECK_COMPATIBILITY
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
BOOT_NEW_IMAGE
        |
        v
APPLICATION_SELF_TEST
        |
        +--> CONFIRM_AND_COMMIT
        |
        +--> ROLLBACK
```

## 7.5 Manifest and Signature

The Manifest shall include, as applicable:

```text
Device model
Hardware Revision range
Firmware version
Image type
Image size
Load address or partition
Cryptographic hash
Digital signature
Minimum Bootloader version
Required Protocol version
Build identifier
Security version
```

The Bootloader shall validate compatibility, image boundaries, hash, signature, version policy, and supported
image type. Every accepted signature algorithm shall define exact message preparation, exact wire encoding, exact
length, canonicality requirements, and malleability policy. For ECDSA P-256, a fixed IEEE P1363 `r || s` encoding
and low-S rule avoid DER-length ambiguity and malleability differences across implementations.

CRC may detect accidental transfer corruption. CRC does not prove authenticity and shall not replace digital
signature verification.

The signing private key shall not be embedded in the Device, PC Application, Linux SBC, Host MCU, or mobile
Application.

A secure channel does not eliminate the requirement for independent Firmware image signature verification.

## 7.6 Chunking and Resume

Chunk size shall account for:

```text
Transport MTU
Fragmentation
Flash programming unit
Maximum non-preemptible time
Security overhead
Retry behavior
Buffer capacity
Rekey cost
```

Resume shall use confirmed committed progress, not merely the last offset transmitted by the Coordinator.

Duplicate chunks shall be handled idempotently or explicitly rejected according to the transaction contract.

## 7.7 Rekey During Update

Large updates shall evaluate:

```text
Expected number of Rekeys
Maximum Rekeys per update
Total pause time
Reauthentication time
Throughput impact
Transaction timeout
Retry allowance
```

A normal maximum-size update should not require excessive Rekey events. Frequent Rekey may indicate unsuitable
thresholds, record granularity, chunk size, or Transport Profile.

## 7.8 Rollback and Recovery

Preferred layout:

```text
Bootloader
Application Slot A
Application Slot B
Boot Metadata
Update Transaction Metadata
```

The new image shall be written to an inactive location, fully verified, marked pending, booted, and confirmed only
after self-test.

If the new image:

```text
Fails to boot
Triggers Watchdog Reset
Fails self-test
Does not confirm in time
```

the Bootloader shall return to a known valid image.

When A/B storage is impossible, evaluate external staging, ROM Bootloader, hardware programming interface,
Recovery Pin, or protected emergency update mode.

Do not erase the only valid Application without a reviewed Recovery Path.

## 7.9 Safe State During Update

The Product shall define:

```text
Allowed outputs during update
Actuator safe state
Power-loss behavior
Watchdog behavior
Battery or power requirements
Update interruption behavior
Recovery-entry method
Operator feedback
```

Firmware Update shall not suspend fundamental safety protections.

---

# Part VIII. Runtime, Event-Driven Design, RTOS, Bare-Metal, BSP, HAL, and Drivers

## 8.1 RTOS Abstraction

The Framework may define interfaces for:

```text
Task
Mailbox
Semaphore
Mutex
Timer
Time
Critical Section
ISR Notification
```

Adapters may exist for:

```text
TI-RTOS
FreeRTOS
ThreadX
Zephyr
Bare-metal
PC Mock
```

The abstraction isolates API differences. It shall not hide:

```text
Task Priority
Stack Size
Execution Period
Worst-case Execution Time
Blocking Policy
ISR restrictions
Deadline
Resource ownership
```

## 8.2 Event-Driven and State-Machine Model

The Baseline execution model is:

```text
Interrupt / DMA / Timer
        |
        v
Event
        |
        v
Mailbox / Fixed Queue / Ring Buffer
        |
        v
Task or Event Dispatcher
        |
        v
Module State Machine
        |
        v
Bounded non-blocking action
```

For RTOS:

```text
Task + Mailbox + State Machine
```

For Bare-metal:

```text
Event Dispatcher + Event Queue + State Machine
```

## 8.3 Bare-Metal Runtime

Recommended Bare-metal components:

```text
Event Queue
Event Dispatcher
Software Timer
State Machine Engine
Deferred Work
Main Idle Loop
```

Do not recreate an artificial RTOS API with blocking Task Sleep and Semaphore behavior when the system only needs
Events, timers, and bounded actions.

## 8.4 ISR and Low-Level Callback Rules

ISR shall perform only bounded work such as:

```text
Read required status
Clear interrupt flags
Capture data
Advance Buffer index
Post Event or notification
```

ISR shall not perform:

```text
Complete frame parsing
Cryptographic processing
Full State Machine
Flash programming
UI update
Blocking delay
Long Device operation
```

Wi-Fi, BLE, USB, and Vendor Driver callbacks follow the same principle. Convert them to Events, Mailbox Messages,
or Deferred Work.

The detailed C implementation rules are defined by `Embedded_C_Coding_Rules.md`.

## 8.5 Static Memory

Product-owned Embedded C shall use static memory configuration unless a controlled exception is explicitly
approved.

Buffers, queues, Mailboxes, reassembly areas, Protocol workspaces, and update state shall have fixed maximum
capacities.

Unbounded allocation based on an external length is prohibited.

## 8.6 BSP and HAL

Vendor-specific content shall be isolated:

```text
Application
    |
    v
Device Service
    |
    v
Generic Device Interface
    |
    v
Specific Device Adapter
    |
    v
Specific Driver
    |
    v
Peripheral HAL
    |
    v
BSP
    |
    v
Vendor HAL / DriverLib
```

HAL may cover GPIO, ADC, DAC, UART, I2C, SMBus, SPI, CAN, PWM, Timer, DMA, Flash, RTC, Watchdog, CRC,
Crypto Hardware, Wi-Fi Module, and BLE Module interfaces.

## 8.7 Driver, Adapter, Service, and Control Policy

Driver owns IC- or peripheral-level operations.

Adapter translates a generic interface into a specific Driver.

Service coordinates a subsystem function.

Control owns Product policy and State Machines.

Do not place Product policy into a reusable Driver.

## 8.8 Hard Real-Time Execution

Hard real-time periods shall be guaranteed by:

```text
Hardware Timer
Peripheral Trigger
DMA
Interrupt
Dedicated local control path
```

They shall not depend on UI refresh, wireless delivery, PC thread scheduling, or a Coordinator command loop.

## 8.9 Resource Budget

The Node design shall document:

```text
Static RAM
Stack per Task
Queue or Mailbox depth
Stream Buffer capacity
Protocol workspace
Crypto workspace
Reassembly Buffer
Firmware Update metadata
Flash usage
Worst-case CPU loading
```

Resource margin shall be measured, not assumed.

---

# Part IX. Protocol Code Generation, Quality, and Architecture Governance

## 9.1 Generated Code Governance

Generated Code may include:

```text
C types and codecs
C# models and serializers
Java models and codecs
Message IDs
Dispatcher skeletons
Payload validation
Documentation
Compatibility tests
Boundary tests
Fuzz seeds
Mock Messages
Packet-decoder metadata
```

Generated Code shall:

```text
Be committed when the Project policy requires reviewable generated artifacts
Be marked as generated
Not be edited manually
Be reproducible from the source Protocol and Generator version
Be checked by CI
```

CI shall regenerate and compare. CI shall fail on unexplained differences and shall not silently commit changes.

## 9.2 Generator as Controlled Software

The Generator shall have:

```text
Version
Unit Tests
Golden File Tests
Schema Validation Tests
Deterministic output
Backward Compatibility Tests
Release Notes
```

A Generator change that changes wire output, decode behavior, or compatibility is not merely an internal tool fix.

## 9.3 Compatibility Test Generation

Generated tests should include:

```text
Minimum and maximum length
Invalid and truncated length
Boundary values
Unknown trailing fields
Unknown Enum and bits
Optional Field defaults
Endianness
Round-trip encode/decode
Old Decoder / New Encoder
New Decoder / Old Encoder
Unsupported MAJOR version
```

Do not test only current Encoder against current Decoder.

## 9.4 Static Analysis

Static Analysis shall cover, as applicable:

```text
Out-of-bounds
Null Pointer
Use-after-free
Integer overflow and truncation
Signed/unsigned conversion
Uninitialized data
Dead code
Unchecked return value
Forbidden API
ISR restrictions
Dynamic-allocation policy
MISRA C or other selected rules
Thread and lock policy
```

Generated Code and handwritten codecs shall both be included.

Suppressions shall be documented, narrow, reviewed, and traceable.

## 9.5 Sanitizers and Fuzzing

Where supported, use:

```text
Address Sanitizer
Undefined Behavior Sanitizer
Thread Sanitizer
Protocol Fuzzing
Decoder Fuzzing
Fragmentation Fuzzing
Stateful Session Fuzzing
```

MCU-specific paths may be tested through host-compiled codecs, simulation, or a Mock platform.

## 9.6 CI Quality Gates

A protected Baseline should require:

```text
Build
Unit Test
Schema Validation
Semantic Lint
Generated-output comparison
Static Analysis
Compatibility tests
Protocol Test Vectors
Placeholder scan
Markdown structure validation
License and notice check
```

Security and Firmware Update Projects add their own required evidence.

## 9.7 Code Ownership

Sensitive areas shall have explicit reviewers:

```text
Protocol
Security
Bootloader
Firmware Update
Generated Code
Safety Control
Platform startup
Memory layout
```

A review requirement shall be enforced by repository policy when possible, not only by team convention.

## 9.8 Architecture Decision Records

Significant decisions should be captured under:

```text
docs/adr/
├─ ADR-0001-coordinator-node-role.md
├─ ADR-0002-protocol-schema.md
├─ ADR-0003-session-boundary.md
├─ ADR-0004-streaming-buffer.md
└─ ADR-0005-firmware-update.md
```

An ADR includes Context, Decision, Alternatives, Consequences, Migration, and Validation.

The Framework stores stable rules. ADRs store why a choice was made.

## 9.9 Structural Rewrite Governance

A structural rewrite, translation, consolidation, or large editorial reorganization shall not be accepted based
only on successful parsing, balanced code fences, or complete heading numbering.

Review shall prove that:

```text
Every prior normative rule is preserved or intentionally removed
Every intentional removal is recorded
Cross-references remain correct
Examples still implement the stated rules
Checklists and Baseline decisions remain synchronized
Security boundaries remain unchanged unless explicitly approved
```

A successful syntax check does not prove that a structural rewrite preserved the complete technical Baseline.

## 9.10 Document Governance

One normative rule shall have one authority location.

Other documents shall reference that authority rather than copy an independently editable duplicate.

When a non-owning document repeats a rule for usability, the repeated text shall be labeled a derived conformance
summary, identify the owning authority, and remain subordinate to that source. A derived summary shall not add,
weaken, or reinterpret the normative rule.

Protocol field details belong in the Protocol Guide and Project Protocol YAML.

Product requirements belong in the SRS, Application Profile, Hazard Analysis, or UI Specification.

Implementation details belong in the Reference Implementation and design specifications.

## 9.11 Conformance Claim Integrity, Deviation Accountability, and Restoration

Framework conformance is a Project-scoped self-declaration made by the person or organization issuing the claim, unless a separate written assessment or certification agreement expressly identifies its named signatories, assessor authority, claimed boundary, revision, and evidence basis. Any such agreement binds only its named signatories and stated scope. It does not amend the repository `LICENSE` or `NOTICE.md` and does not imply participation, authorization, certification, endorsement, warranty, acceptance, or responsibility by the Framework author or maintainer unless that person is an express signatory acting in the stated role.

Every claim shall use exactly one of the following classifications:

```text
Full Framework Conformance
Scoped Framework Conformance
Nonconforming
```

`Full Framework Conformance` means that, for the declared Product or Project boundary and revision, all Framework requirements determined applicable by the approved Framework Application Analysis have been satisfied, all non-excludable controls have been satisfied, and no unresolved deviation contradicts the claim. An approved `Not Applicable` determination is permitted only when supported by the Application Analysis and objective Project facts.

`Scoped Framework Conformance` means that the claim is intentionally limited to explicitly named components, capabilities, lifecycle phases, artifacts, interfaces, or revisions. Within every included boundary, all Framework requirements determined applicable to that boundary shall be satisfied, all non-excludable controls shall be satisfied, and no unresolved deviation shall contradict the claim. The exact phrase `Scoped Framework Conformance` shall appear wherever the claim is presented. The claim shall identify its included and excluded boundaries and shall not be abbreviated, promoted, or represented as full, system-wide, Product-wide, or release-wide conformance.

A Full or Scoped claim shall identify a non-empty, materially meaningful engineering boundary. A claim shall not be based solely on declaring all substantive technical requirements `Not Applicable`, nor may it omit the functions, interfaces, lifecycle phases, or evidence necessary to understand the practical meaning of the claim.

`Nonconforming` applies when the claimed boundary does not satisfy the conditions for Full or Scoped Framework Conformance, when required evidence or approval is missing, when an applicable requirement remains unsatisfied within the included boundary, or when the claim classification, scope, lifecycle status, or presentation would be misleading.

The following controls are non-excludable from every Full or Scoped Framework Conformance claim:

```text
Conformance-claim integrity and truthful presentation
Framework version, source identity, and claimed-boundary identification
Authorized applicability and Not Applicable decisions
Authorized deviation and residual-risk approval
Required evidence identity, integrity, and execution-state accuracy
Human review, approval, and retained professional responsibility
Applicable safety, security, regulatory, statutory, and contractual requirements
Prohibition of fabricated, misleading, or materially incomplete claims
Claim lifecycle, supersession, withdrawal, revocation, and re-evaluation control
```

The intended claim boundary and applicability baseline shall be approved, revision-controlled, and identified before conformance validation begins. After a failure is known, an exclusion may rely only on pre-existing objective records showing that the item was outside the approved boundary or was already supported as `Not Applicable`. A newly created or materially changed boundary constitutes a new claim revision and shall not retroactively restore or rewrite the status of an earlier claim.

A scope exclusion shall be independently justified by the approved Framework Application Analysis and objective Project facts. It shall not be created or expanded solely after a requirement, activity, artifact, or evidence item has failed in order to avoid correction, validation, approval, or disclosure. Otherwise the affected boundary remains nonconforming until corrected and revalidated under a new or updated claim record.

An approved deviation does not satisfy an applicable Framework requirement. A deviation may remain associated with a Full or Scoped claim only when it applies exclusively outside the included claim boundary, records a disclosed limitation that does not contradict any applicable requirement within the included boundary, or reflects a formally approved change to the Project requirement or applicability decision completed before the conformance assessment. A residual deviation that leaves an applicable requirement unsatisfied within the included boundary requires `Nonconforming` classification.

Every conformance claim shall use a controlled record containing at least:

```text
Claim ID and claim-record schema version
Issuer legal or organizational identity and issuer authority
Issue date and lifecycle status
Full, Scoped, or Nonconforming classification
Product or Project identity and exact claimed revision
Pre-validation claim-boundary baseline ID and revision
Included and excluded boundaries
Framework repository, source commit/tag/Release, document path, and version
Adopted Project authorities and applicability decisions
Evidence-set identity and approval record
Deviations, limitations, expiry or review conditions
Validity conditions and mandatory re-evaluation triggers
Supersedes and superseded-by relationships
Withdrawal or revocation reason when applicable
```

Claim lifecycle status shall be one of `active`, `superseded`, `withdrawn`, or `revoked`. A claim applies only to its identified Product or Project revision. A change to hardware, software, Protocol, configuration, Framework authority, applicability, risk control, evidence validity, known defect, hazard, security finding, deviation condition, or compensating control shall trigger documented re-evaluation when it could affect the claim. An invalidated claim shall be withdrawn, revoked, or superseded; it shall not remain presented as active.

Artifacts, implementations, analyses, or conformance claims produced by bypassing, disabling, ignoring, or materially misapplying applicable Framework requirements, required reviews, validation activities, or approval controls shall not claim conformance with this Framework for the affected scope.

A bypass is not converted into an authorized deviation merely because it was performed, documented, or accepted informally. An authorized deviation requires a designated approval authority, a bounded scope, rationale, risk and impact assessment, compensating controls where applicable, objective evidence, an approval record, and an expiry, removal, or review condition.

Approval of a deviation accepts only the documented residual risk within the approver's assigned authority. It does not make an unsatisfied applicable requirement conforming, transfer responsibility to this Framework, repository, AI system, tool, author, or maintainer, or remove the responsibilities retained by implementers, reviewers, Product authorities, and other assigned roles.

Conformance may be claimed or restored only after the deviation has been formally dispositioned; the affected artifact and dependent outputs have been corrected; omitted, bypassed, or invalidated reviews, validation activities, and approval controls have been completed or repeated; objective evidence has been regenerated where required; any remaining deviations satisfy the limited association conditions in this section and are fully disclosed; and the final conformance record identifies the claim revision, lifecycle status, classification, resulting scope, evidence, approvals, exclusions, limitations, validity conditions, and re-evaluation triggers.

Unauthorized bypasses and unapproved deviations remain nonconforming and shall be reported to the responsible human authority rather than being normalized as accepted practice.

---

# Part X. Testing, Observability, and Acceptance

## 10.1 Framework Test Assets

The Framework should provide:

```text
Mock Node
Mock Coordinator
Mock Transport
Mock wireless link
Mock Application Session
Mock Bootloader Session
Protocol Test Vectors
Loopback
Packet recorder
Packet decoder
State-transition log
Fault injection
Timeout injection
Buffer overflow tests
Reset and reconnect tests
```

## 10.2 Streaming and Telemetry Tests

Test:

```text
Long-duration transfer
Maximum Payload
Different Samples per Record
Control during Stream
Near-full Buffer
Alarm burst
Record loss
Duplicate and reordering
Sequence wrap
Slow Coordinator
Slow UI
Wireless jitter and disconnect
Telemetry replacement behavior
Stream gap behavior
```

Telemetry tests shall verify latest-value replacement only when the Payload is a complete independently usable
snapshot.

Stream tests shall verify ordering, loss, duplicate, timestamp, and maximum-size behavior.

## 10.3 Application Security Tests

Test:

```text
Invalid Authentication Tag
Duplicate counter
Wrong Application Session ID
Wrong Key Context
Old Session replay
Replay after reset
Application record after Bootloader entry
Rekey threshold and deadline
Hard Limit
Delayed safety command
Authorization failure
```

## 10.4 Bootloader Security Tests

Test:

```text
Wrong Bootloader Session ID
Application key used for update data
Old Bootloader Session chunk replay
Bootloader Rekey boundary
Bootloader Hard Limit
Wrong Update Transaction ID
Unauthorized resume
Wrong or reused one-time ticket
Execution Environment mismatch
```

## 10.5 Firmware Update Tests

Test:

```text
Valid update
Invalid signature
Invalid hash
Wrong model or Hardware Revision
Anti-rollback rejection
Power loss at each stage
Disconnect and resume
Rekey and resume
Duplicate chunk
Out-of-order chunk
Flash write failure
Pending-image timeout
Self-test failure
Automatic rollback
Recovery entry
```

CRC failure tests do not replace signature-failure tests.

## 10.6 Timing and Load Tests

Measure:

```text
Control response latency
Stream latency and jitter
Worst-case CPU loading
Buffer high-water level
Crypto time
Rekey pause
Firmware Update throughput
Transport serialization or air time
Recovery time
```

Test worst-case simultaneous activity, not only isolated functions.

## 10.7 State and Recovery Tests

Each State Machine shall have tests for:

```text
Valid transition
Invalid transition
Timeout
Duplicate Event
Late Event
Reset during transition
Disconnect during transition
Fault entry
Safe-state entry
Recovery success
Recovery failure
```

## 10.8 Observability

Logs and traces shall permit reconstruction of:

```text
Link state
Session state and Epoch
Node state
Command Request and Result
Event, Alarm, and Fault occurrence
Sequence gap
Buffer overflow
Rekey
Firmware Update transaction
Rollback
Security failure
```

Secrets and raw key material shall never be logged.

## 10.9 Acceptance Evidence

A Baseline shall retain:

```text
Requirements traceability
Architecture review
Protocol validation
Generated-output comparison
Static Analysis result
Test Vector result
Interoperability result
Timing measurement
Resource measurement
Security test result
Firmware Update test result
Open issue disposition
Approval record
```

---

# Part XI. First Reference Implementation Baseline

## 11.1 Purpose

The first Reference Implementation demonstrates that the architecture can be implemented without violating its
boundaries.

It is not intended to prove every future platform or Product variation.

## 11.2 Initial Recommended Scope

A practical first scope is:

```text
Windows PC Coordinator
C# / .NET Framework 4.7.2
USB-CDC Transport
MCU Node
Embedded C
RTOS or Event-Driven Runtime
One active Node
One outstanding Request
Telemetry
Stream
Event / Alarm / Fault
Basic Secure Session
Mock Node and packet tools
```

Firmware Update may be added after the Application communication and validation path is stable, or included from
the beginning when the Product requires it.

## 11.3 Coordinator Demonstration

The Coordinator Reference Implementation should demonstrate:

```text
Layered Project structure
Transport abstraction
Protocol-generated models
Non-blocking receive path
Command correlation
State reconciliation
Telemetry and Stream consumers
UI/rendering decoupling
Mock Transport
Logging and packet capture
```

## 11.4 Node Demonstration

The Node Reference Implementation should demonstrate:

```text
Static memory
Event-Driven dispatch
State Machine ownership
Command validation
Protocol Adapter
Local safety reaction
ISR deferral
Transport abstraction
Generated codecs
Resource measurement
```

## 11.5 Cross-Implementation and Cross-Language Interoperability

Every implementation in scope shall encode and decode the same Golden Frames with identical wire bytes and
semantic values.

When C and C# are in scope:

```text
C# encodes -> C decodes
C encodes -> C# decodes
```

When Java is in scope:

```text
Java encodes -> C decodes
C encodes -> Java decodes
C# and Java decode the same Golden Frame when both are in scope
```

When multiple implementations use the same language, they shall still pass cross-implementation interoperability.

## 11.6 Reference Implementation Version

The Reference Implementation uses its own Code version such as:

```text
V1.0.0RC01
```

It does not inherit the Framework document version as its release identity.

---

# Part XII. Adoption, Migration, and Baseline Decisions

## 12.1 Adoption Sequence

A new Project should proceed in this order:

```text
1. Complete Framework Application Analysis
2. Define Coordinator and Node roles
3. Establish Product responsibility boundaries
4. Define Application Profile and Product requirements
5. Create Project Protocol YAML from the Template
6. Run Schema Validation and Semantic Lint
7. Generate Protocol artifacts
8. Implement Mock Coordinator and Mock Node
9. Implement Transport and Protocol Adapter
10. Implement Product State Machines
11. Integrate Device Drivers and platform code
12. Measure timing, bandwidth, memory, and CPU
13. Implement security and Firmware Update as required
14. Execute compatibility and interoperability tests
15. Approve the Project Baseline
```

## 12.2 Reuse versus Extension

A Project shall classify each Framework area as:

```text
Reuse
Extend
Replace
Not Applicable
Gap
```

A Product-specific need shall not automatically become a Framework rule.

A rule should move into the Framework only when it is reusable across multiple applications and does not contain
one Product's semantics.

## 12.3 Migration from Existing Code

Migration should be incremental:

```text
Establish a compiling Baseline
Add tests around current behavior
Create Protocol and platform boundaries
Move low-coupling modules
Introduce Adapters
Replace direct hardware access
Introduce generated Protocol artifacts
Measure regressions
Remove obsolete paths
```

A complete rewrite without behavioral evidence is high risk.

## 12.4 Framework Compatibility Revalidation

When the Framework changes:

| Change | Required Application Action |
|---|---|
| PATCH | Review corrections for impact on existing gaps, Protocol, and tests. |
| MINOR | Reassess reuse classification, responsibility boundaries, Protocol extensions, and migration. |
| MAJOR | Repeat full Application Analysis and establish a new compatibility plan. |
| Security model change | Revalidate authentication, authorization, Session, Rekey, Anti-Replay, audit, and Bootloader boundaries. |
| Protocol compatibility change | Regenerate artifacts and rerun backward-compatibility and interoperability tests. |
| State or Fault model change | Revalidate state ownership, recovery, safe state, and UI behavior. |

## 12.5 Baseline Decision Summary

This Baseline establishes the following decisions:

1. Coordinator and Node are platform-independent and relationship-relative roles.
2. System role, message role, event role, Transport direction, and connection role are distinct.
3. `protocol/`, `coordinator/`, and `node/` are the core responsibility directories.
4. Build Target is a configuration and dependency set, not an architecture role.
5. Device Contract is the stable cross-platform asset.
6. Protocol YAML is the machine-verifiable Single Source of Truth for the wire contract.
7. This Framework is the Single Source of Truth for reusable system architecture and engineering governance.
8. Protocol and Transport remain decoupled.
9. UI and Application code do not assemble wire frames directly.
10. Node owns hard real-time control, fundamental safety protection, and local Fault Reaction.
11. Command Dispatcher validates and converts commands into Application events or service requests; it does not directly operate hardware.
12. Capability determines actual supported behavior; Node Type alone is insufficient.
13. Event-Driven behavior is primary; low-rate health queries are allowed.
14. Control Plane and Data Plane may share a Transport but not a blocking processing path.
15. Telemetry is replaceable summarized state; Stream is an ordered non-replaceable record sequence.
16. Transmission frequency alone does not determine Telemetry versus Stream.
17. Sample Period and Record Period are separate.
18. Aggregation improves average efficiency but shall be revalidated for latency, blocking, Buffer, and loss impact.
19. Average bandwidth does not prove acceptable worst-case control latency.
20. Every Transport is a formal bounded profile.
21. Dynamically negotiated Transports require a Runtime Effective Profile.
22. Link, Secure Session, Application, and Update Transaction are separate state domains.
23. Hybrid security uses asymmetric mechanisms for trust and Session establishment and symmetric mechanisms for sustained traffic.
24. Application Session and Bootloader Session are separate.
25. Application Session keys do not survive reset or Bootloader entry.
26. Key Context, direction, counter, and Anti-Replay state are separated.
27. Nonce reuse and counter overflow under one key are prohibited.
28. Soft Threshold, Rekey Deadline, and Hard Limit are explicit and context-specific.
29. Hard Limit is an uncrossable security boundary.
30. Anti-Replay does not replace state, freshness, authorization, or Operation-ID validation.
31. Firmware Update uses a Bootloader-specific Secure Session and Key Context.
32. Firmware Update Transaction identity is separate from Secure Session identity.
33. Rekey or reconnect shall not silently change Manifest, Image ID, expected hash, or committed update progress.
34. Firmware images require independent authenticity verification; CRC does not replace digital signature.
35. Bootloader shall support verification, resume, rollback, and recovery.
36. RTOS and Bare-metal use the same Event and State-Machine semantics through different runtime mechanisms.
37. ISR and low-level callbacks perform bounded work and defer complex processing.
38. Product-owned Embedded C uses static bounded memory unless a controlled exception is approved.
39. BSP, HAL, Driver, Adapter, Service, and Product Control responsibilities remain separated.
40. Generated Code is deterministic, traceable, and not edited manually.
41. Generator changes that alter wire behavior require Protocol impact analysis.
42. Compatibility tests include old/new Encoder and Decoder combinations.
43. Architecture principles shall be enforced by tools and CI whenever practical.
44. A structural rewrite is not accepted solely because syntax and Markdown structure pass.
45. One normative rule has one authority location.
46. Testing, observability, timing, resource measurement, security validation, and update recovery evidence are part of the Baseline.
47. Reference Implementations have independent Code versions.
48. Project adoption begins with Application Analysis and a Project-specific Protocol YAML.
49. Product-specific rules shall not pollute the reusable Framework unless they are proven reusable.
50. Migration shall be incremental and evidence-based.
51. Generated dispatch skeletons are Protocol plumbing and shall not contain Product control, State Machine ownership, or direct hardware access.
52. Repeated non-owning rules are derived conformance summaries and remain subordinate to the owning authority.
53. Cross-implementation interoperability applies to every implementation; cross-language interoperability applies to language pairs in scope.
54. Public Discovery is minimal, ephemeral, rate-limited, non-authoritative, transcript-bound, and followed by authenticated revalidation.
55. Product Baselines contain concrete cryptographic selections and no unresolved security sentinel.
56. Handshake Profile identity and canonical transcript binding prevent profile confusion and silent downgrade.
57. Every Key Context references a machine-verifiable Record Counter/Rekey Profile and stops before Hard Limit.
58. Firmware signature Profiles define exact preparation, wire encoding, length, and canonicality or malleability rules.
59. `minimum_length` means the fixed decoding prefix; variable content is validated separately.
60. Plaintext Message, security overhead, secured Record, Transport reassembly, and Fragment sizes remain distinct.
61. Maintained repository Markdown files use stable canonical paths, while immutable detached release, audit, and external-delivery artifacts include an approved version or Baseline identifier in the distributed filename.
62. A detached artifact identifies its source canonical file and Git commit, tag, or Release and shall not become a parallel maintained authority.
63. Fragmentation uses one exact wire Header and bounded deterministic reassembly behavior for every supported Runtime MTU.
64. Handshake request and response Payloads are named concrete structs; opaque security-critical payload blobs are prohibited.
65. Profile IDs do not encode security strength; selection uses allowlists, preference, security level, and deprecation state.
66. Firmware Update resume across Session changes requires cryptographic authorization bound to transaction, Manifest, Device, Host, and security version.
67. A data-bearing Transport Profile is invalid when its minimum MTU does not exceed the Fragment Header size.
68. When `Coordinator_Software_Engineering_Rules.md` is approved or explicitly adopted for Project use, it governs cross-language Coordinator-owned software engineering within the architecture and Product authority boundaries defined by this Framework.
69. When `CSharp_Coding_Rules.md` is approved or explicitly adopted for Project use, it governs Product-owned C# implementation in addition to applicable role-level, Product, Protocol, and Project-specific authorities.
70. A programming language shall not be used to infer Coordinator, Node, Tool, Service, or mixed role.
71. Application Analysis records whether each role-level and language-level authority applies, the exact version and status used, and the approval evidence, deviation, or `N/A` rationale.
72. Repository structural validation and detached-package integrity checks supplement but do not replace semantic review or human approval.

## 12.6 Core Design Philosophy

> **Programming languages change, MCUs change, RTOSes change, Devices change, and Transports change; the Device
> Contract, Event-Driven behavior, State Machines, real-time properties, security boundaries, and recovery capability
> shall not drift with them.**

---

# Appendix A. Authority Matrix

| Topic | Authority |
|---|---|
| Coordinator/Node roles | This Framework |
| System layering and responsibility boundaries | This Framework |
| Project directories and dependency rules | This Framework |
| Timing, bandwidth, and safety placement | This Framework plus Product Requirements and Hazard Analysis |
| Message IDs, Payloads, Wire Format, and security fields | Project Protocol YAML |
| Protocol YAML authoring and validation rules | `Protocol_YAML_Definition_Guide.md` |
| Protocol compatibility, version consequences, mixed-version operation, deprecation, and removal | `Protocol_Compatibility_Rules.md` when approved or explicitly adopted for Project use; proposed authority while Draft for Review |
| Protocol identifier Registry, namespace, allocation, retirement, and non-reuse | `Protocol_Registry_Governance.md` when approved or explicitly adopted for Project use; proposed authority while Draft for Review |
| Protocol security-profile and secure-session lifecycle governance | `Protocol_Security_Profile.md` when approved or explicitly adopted for Project use; proposed authority while Draft for Review |
| Reusable YAML skeleton | `Protocol_YAML_Template.md` |
| Cross-language Coordinator software architecture and engineering rules | `Coordinator_Software_Engineering_Rules.md` when approved or explicitly adopted for Project use; proposed authority while Draft for Review |
| Cross-language Node software architecture and engineering rules | `Node_Software_Engineering_Rules.md` when approved or explicitly adopted for Project use; proposed authority while Draft for Review |
| Embedded C implementation rules | `Embedded_C_Coding_Rules.md` |
| C# language and .NET implementation rules | `CSharp_Coding_Rules.md` when approved or explicitly adopted for Project use; proposed authority while Draft for Review |
| Product command semantics | Application Profile and SRS |
| UI pages and behavior | UI/UX Specification and Product Profile |
| Project-specific Coordinator decomposition, threading, references, and approved deviations | Coordinator Design Specification and Reference Implementation |
| Node Task, Mailbox, Priority, and resource model | Node Design Specification |
| Hazard and safe state | Hazard Analysis and System Requirements |
| Test procedure and result | Test Specification and Test Report |
| Repository structural and package-integrity validation | `Repository_Validation_Checklist.md`, executed validator output, and retained package hashes |
| Validation evidence identity, execution state, traceability, and adequacy | `Validation_Evidence_Guide.md` when approved or explicitly adopted for Project use; proposed operational method while Draft for Review |
| Framework conformance review and evidence capture | `Framework_Conformance_Checklist.md`; the Checklist does not independently create requirements |
| AI-generated artifact validation and human approval controls | `AI_Generated_Artifact_Validation_Guide.md`; the Guide does not replace owning engineering authorities |

---

# Appendix B. Source Document Mapping

```text
Embedded Device Control Framework, document version v1.4.2
    Primarily contributed the original content now represented by
    Parts I, IV, V, VI, VII, VIII, X, XI, and XII.

Coordinator/Node Architecture, document version v1.2.1
    Primarily contributed the original content now represented by
    Parts II, III, IX, and the version and governance rules.
```

After consolidation:

```text
Do not maintain two independent architecture Master documents.
Do not duplicate Security, Protocol, or Capability rules across documents.
Keep Project Protocol YAML independent.
Keep Product Profile independent.
Keep Reference Implementation independent.
Keep historical source documents archived as Superseded.
```

---

# Conclusion

The Framework provides a reusable architecture for systems in which a Coordinator manages one or more Nodes while
the Node preserves local control, safety, and real-time responsibility.

The operating model is:

```text
Framework Application Analysis
        |
        v
Coordinator and Node Responsibility Boundary
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
Coordinator and Node Reference Implementations
        |
        v
Timing / Resource / Security / Recovery Validation
        |
        v
Project Baseline
```

The architecture is successful when platform replacement does not require reinvention of the Device Contract,
state ownership, safety boundary, security model, or recovery rules.
