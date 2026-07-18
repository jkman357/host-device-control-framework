# Protocol YAML Definition Guide

## Coordinator/Node Protocol Schema Authoring, Validation, Code Generation, and Governance Baseline

**Document Name:** `Protocol_YAML_Definition_Guide.md`  
**Document ID:** PYDG  
**Document Version:** v1.0.5  
**Status:** Baseline  
**Document Type:** Reusable Definition Guide  
**Related Framework:** `Coordinator_Node_Control_Framework.md`  
**Related Template:** `Protocol_YAML_Template.md`  
**Related Application Analysis:** `Framework_Application_Analysis_Template.md`  
**Primary Narrative Language:** English  
**Author:** Ray Yang  
**Maintainer:** Ray Yang  
**Repository:** `host-device-control-framework`  
**First Issued:** 2026-07-15  
**Last Revised:** 2026-07-18  

Copyright © 2026 Ray Yang. All rights reserved.

This document is maintained as part of a personal engineering project. It is not an official
document of any employer or organization. No license is granted unless otherwise explicitly stated.

All third-party standards, publications, trademarks, source code, licenses, and legal notices remain
the property of their respective owners. References to third-party materials do not imply ownership,
endorsement, affiliation, or authorization.

---

## 0. Document Control

### 0.1 Purpose

This document defines the common authoring rules for `Protocol YAML` in Coordinator/Node systems so that
every Application Profile can describe the following in a consistent, machine-verifiable, and
code-generatable form:

```text
Message ID
Command / Response
Event / Alarm / Fault
Telemetry / Streaming Record
Payload Layout
Data Type
Unit / Scale / Range
Enum / Bit Field
Length Policy
Unknown Data Policy
Timeout / Retry
Sequence / Correlation
Execution Environment
Capability
Security Attribute
Protocol Version
Compatibility Policy
Transport Profile
Fragmentation Rule
Firmware Update Contract
```

This document does not define the actual commands of one Product. It establishes a reusable baseline for:

> Protocol YAML syntax, semantics, validation, code generation, compatibility, and governance
> across Coordinator/Node Projects.

Each Product or Project shall create its own Protocol YAML, for example:

```text
Sensor_Acquisition_protocol.yaml
Smart_Battery_protocol.yaml
Motion_Control_protocol.yaml
Production_Test_protocol.yaml
```

### 0.2 Document Position

The authority boundary is:

```text
Coordinator_Node_Control_Framework
    Defines system roles, layering, responsibility boundaries,
    communication principles, security boundaries, and engineering governance.

Protocol_YAML_Definition_Guide
    Defines how Protocol YAML describes the wire contract and how
    Schema Validation, Semantic Lint, Code Generation, and compatibility work.

<Application>_protocol.yaml
    Defines the actual Message IDs, Payloads, Enums, Ranges, Wire Format,
    Security Attributes, Versions, and Compatibility of one Application Profile.

<Application>_Application_Profile
    Defines domain semantics, operating flows, states, alarms, telemetry,
    and the rationale behind Product behavior.

Reference Implementation
    Implements Transport, Encode/Decode, threading, buffers, UI,
    Drivers, build configuration, and integration behavior.
```

Therefore:

> Protocol YAML is the Single Source of Truth for the wire format and the machine-verifiable
> Protocol Contract.

Protocol YAML shall not replace:

```text
Software Requirements Specification
Hardware Design Specification
Hazard Analysis
Product State Machine Description
UI/UX Specification
Algorithm Design Document
Test Procedure
Test Report
```

### 0.3 Scope

This guide applies to systems including:

```text
PC Application <-> MCU
Linux SBC <-> MCU
Host MCU <-> Device MCU
Gateway <-> Subsystem
Mobile Application <-> Device
Production Tool <-> Device Under Test
Service Tool <-> Device
Automated Test Platform <-> Node
```

Supported Transports may include:

```text
USB CDC
UART
RS-232
RS-485
RS-422
CAN
CAN FD
SPI
Ethernet / TCP
Wi-Fi
BLE
Other Transports capable of carrying Protocol Records reliably
```

Protocol YAML shall remain Transport-neutral. Transport-specific constraints shall be defined in
`transport_profiles`.

A Message definition shall not contain a COM port name, UART register, socket handle, USB endpoint,
CAN Driver API, or BLE characteristic handle.

### 0.4 Non-Goals

This baseline does not define:

```text
A specific YAML parser implementation language
A specific Code Generator template engine
A specific CRC algorithm
A specific AEAD algorithm
A specific MCU alignment model
A specific Product Message ID assignment
A specific UI page
A specific Device IC register
The complete JSON Schema file
```

Companion artifacts include or may be created separately:

```text
Protocol_YAML_Template.md
Protocol_YAML_Schema_v1.0.0.json
Protocol_Code_Generator_V1.0.0RCxx
```

### 0.5 Normative Keywords

The keywords in this document have the following meanings:

| Keyword | Meaning |
|---|---|
| SHALL / MUST | Mandatory requirement. Violation shall fail Schema Validation, Semantic Lint, Review, or Baseline approval as applicable. |
| SHALL NOT / MUST NOT | Explicit prohibition. |
| SHOULD | Expected rule. A deviation requires a documented reason. |
| RECOMMENDED | Preferred method that may be adjusted by the Project with justification. |
| MAY | Optional capability. |
| CONDITIONAL | Required only when the specified feature or condition exists. |

### 0.6 Version History

| Version | Date | Description |
|---|---|---|
| v1.0.0 | 2026-07-15 | Established the general Protocol YAML Definition Guide, including data models, Messages, versioning, security, Transport, Code Generation, Lint, Test Vectors, and governance rules. |
| v1.0.1 | 2026-07-15 | Corrected the inconsistency between a Framework Message ID example and the recommended allocation range; explicitly separated the Message, Capability, Service, Namespace, Error, Enum, and Bitset registries and their uniqueness scopes; and strengthened Semantic Lint, quick-reference, and Baseline decisions. |
| v1.0.2 | 2026-07-18 | Converted the complete guide to English; established Ray Yang as Author and Maintainer; added repository identity, copyright, personal-project clarification, and third-party-material notice; normalized terminology, punctuation, headings, examples, and checklists; and preserved the v1.0.1 technical baseline decisions. |
| v1.0.3 | 2026-07-18 | Defined the normative decision boundary between `telemetry` and `stream`; added a complete `category: telemetry` YAML example; required telemetry cadence, replacement, priority, and maximum-record-size policies; clarified when sequence and timestamp fields are required; and synchronized Semantic Lint, Project Adoption Checklist, Quick Reference, and Baseline Decision Summary. |
| v1.0.4 | 2026-07-18 | Updated the active Framework, Template, and Application Analysis references to `Coordinator_Node_Control_Framework.md`, `Protocol_YAML_Template.md`, and `Framework_Application_Analysis_Template.md`; corrected the companion-artifact wording now that the Template exists; and preserved all Protocol YAML syntax, semantics, validation, compatibility, and governance rules without technical change. |
| v1.0.5 | 2026-07-18 | Adopted the stable canonical filename `Protocol_YAML_Definition_Guide.md`; updated active Framework, Template, and Application Analysis references to canonical paths; retained version identity in document metadata and Git history; and preserved all Protocol YAML syntax, semantics, validation, compatibility, and governance rules without technical change. |

---

## 1. Core Principles

### 1.1 Single Source of Truth

The following wire-contract information shall not be maintained independently in C, C#, Java, or manually
written documentation:

```text
Message ID
Payload Offset
Field Type
Field Size
Endianness
Enum Value
Error Code
Unit
Scale
Range
Length Policy
Version Attribute
Security Attribute
```

The required flow is:

```text
Protocol YAML
    |
    +--> Schema Validation
    |
    +--> Semantic Lint
    |
    +--> Code Generation
          |
          +--> C Header / Source
          +--> C# Enum / Model / Codec
          +--> Java Enum / Model / Codec
          +--> Protocol Documentation
          +--> Packet Decoder Metadata
          +--> Mock Node Metadata
          +--> Test Vector Skeleton
```

The following workflow is prohibited:

```text
Modify C Header first
    |
Manually modify C#
    |
Update documentation last
```

### 1.2 Machine-Readable, Human-Readable, and Testable

A complete Protocol Baseline shall contain all three:

```text
Machine-Readable Specification
Human-Readable Documentation
Test Vectors
```

| Artifact | Primary Responsibility |
|---|---|
| Protocol YAML | Fields, IDs, types, Wire Format, versions, privileges, and compatibility |
| Protocol Documentation | Design rationale, flows, states, exceptions, and operating semantics |
| Test Vectors | Cross-language and cross-platform Encode/Decode consistency |

YAML without explanatory documentation leaves Product-behavior rationale unclear.

Documentation without YAML allows field layouts and IDs to drift across programming languages.

Code without Test Vectors cannot demonstrate that the Coordinator and Node interpret the same bytes identically.

### 1.3 Product Semantics and Wire Format Shall Be Separated

Protocol YAML should describe:

```text
Command name
Message category
Wire ID
Payload fields
Field semantics
Wire unit
Range and invalid value
Allowed state
Response relationship
Security attributes
Compatibility attributes
```

Protocol YAML shall not describe:

```text
WinForms button names
MCU register addresses
RTOS task names
HAL handles
UI colors
Internal algorithm temporary variables
Long Product business-process narratives
```

Product workflows belong in the Application Profile, SRS, or State Machine documentation. Protocol YAML may
reference the identifiers required by the wire contract.

### 1.4 Transport-Neutral Contract

The same Message should be transferable over different Transports:

```text
Device Start
    |
START_REQUEST
    |
USB CDC / UART / CAN FD / TCP / BLE
```

Message definitions shall not depend on:

```text
COM port name
USB endpoint
CAN Driver API
TCP socket
BLE GATT handle
UART baud rate
```

MTU, throughput, Fragmentation, and latency constraints belong in `transport_profiles`.

### 1.5 Designed for Evolution

The first release shall consider:

```text
Protocol Version
Schema Version
Device Model
Firmware Version
Bootloader Version
Hardware Revision
Execution Environment
Capability Query
Unsupported Command
Feature Negotiation
Backward Compatibility
Deprecation
Unknown Field Handling
```

The Protocol shall not assume:

```text
There will always be only one Host
There will always be only one Node
There will always be only one Transport
No field will ever be added
The Device IC will never change
A Bootloader will never be required
```

An initial implementation may be simplified, but the Schema shall not block reasonable future evolution.

### 1.6 Generated Artifacts Shall Not Be Edited Manually

Every generated artifact shall identify:

```text
Auto-generated status
Manual-edit prohibition
Source specification name and version
Source specification hash
Generator name and version
Generation timestamp or reproducible build identifier
```

CI should regenerate all generated artifacts and compare them with the committed output.

A manually modified generated file shall cause validation failure.

---

## 2. Versioning and Naming Rules

### 2.1 Version Domains Shall Remain Separate

The following versions are different governance objects:

```text
Guide Document Version
Protocol Schema Version
Application Protocol Version
Code Generator Version
Firmware Version
Bootloader Version
Product Version
Reference Implementation Version
```

Example:

```yaml
schema_version: "1.0"

document:
  name: SENSOR_ACQUISITION_protocol
  version: v1.0.0

protocol:
  version: V1.0.0RC01

generator:
  minimum_version: V1.0.0RC02
```

Rules:

- Markdown document versions use `vMAJOR.MINOR.PATCH`.
- Protocol, Generator, Firmware, Bootloader, and implementation versions may use `VMAJOR.MINOR.PATCHRCxx`.
- `RCxx` uses two digits, such as `RC01` and `RC02`.
- A formal release removes the RC suffix, such as `V1.0.0`.

### 2.2 Schema Version

`schema_version` identifies the syntax and structural version of Protocol YAML. It is not the wire Protocol
version.

```yaml
schema_version: "1.0"
```

| Change | Schema Version Impact |
|---|---|
| Correct explanatory text or add optional metadata that does not affect parsing | PATCH |
| Add a backward-compatible node or property | MINOR |
| Remove, rename, or structurally change an existing field | MAJOR |

The Generator shall reject unsupported Schema Versions before Code Generation.

### 2.3 Protocol Version

`protocol.version` is the Application Protocol version negotiated between the Coordinator and Node.

```yaml
protocol:
  name: example_device_protocol
  version: V1.2.0RC03
```

| Component | Meaning |
|---|---|
| MAJOR | Incompatible Wire Format change or incompatible change to existing semantics |
| MINOR | Backward-compatible Message, Capability, or trailing Optional Field |
| PATCH | Correction that does not change the Wire Format, or a compatible behavior clarification |
| RC | Candidate-release test iteration |

### 2.4 Naming Style

YAML keys shall use `snake_case`:

```yaml
message_id:
minimum_length:
unknown_trailing_policy:
execution_environment:
```

Protocol symbols shall use uppercase letters with underscore separators:

```text
GET_DEVICE_INFO_REQUEST
CAP_STREAMING
ERROR_INVALID_STATE
```

Reusable type names should use PascalCase:

```text
SoftwareVersion
DeviceTimestampUs
OperationId
TransactionId
```

Language-specific naming conversion belongs in the Generator and shall not alter the Protocol symbol identity.

---

## 3. Repository and File Organization

### 3.1 Recommended Repository Structure

```text
protocol/
├─ spec/
│  └─ <Application>_protocol.yaml
├─ schema/
│  └─ Protocol_YAML_Schema_v1.0.0.json
├─ docs/
│  ├─ protocol_overview.md
│  ├─ command_reference.md
│  ├─ event_alarm_fault_reference.md
│  ├─ compatibility_policy.md
│  └─ firmware_update.md
├─ codegen/
│  ├─ templates/
│  │  ├─ c/
│  │  ├─ csharp/
│  │  └─ java/
│  └─ configuration/
├─ test_vectors/
│  ├─ commands/
│  ├─ events/
│  ├─ streaming/
│  ├─ compatibility/
│  ├─ security/
│  └─ firmware_update/
└─ generated/
   ├─ node/
   │  └─ c/
   └─ coordinator/
      ├─ c/
      ├─ csharp/
      └─ java/
```

### 3.2 Single-File and Multi-File Specifications

A small Project may use one Protocol YAML file.

A medium or large Project may split definitions by controlled include units:

```text
protocol_base.yaml
protocol_types.yaml
protocol_application.yaml
protocol_bootloader.yaml
```

When multiple files are used:

- Merge order shall be deterministic.
- Duplicate keys shall be rejected.
- Duplicate Registry entries shall be rejected according to their Registry scope.
- The merged specification shall have one reproducible hash.
- Generated output shall identify the merged input set.
- CI shall validate both individual include files and the merged result.

### 3.3 Framework and Application Separation

A first implementation may use one file with separate `framework`, `application`, and `bootloader` Namespaces.

A later split into multiple files is allowed only when the merge remains deterministic and semantic validation
still detects cross-file conflicts.

Product-specific commands and data shall remain in the Product's `<Application>_protocol.yaml`. They shall not
be copied into one ever-growing universal Protocol.

---

## 4. Top-Level Data Model

### 4.1 Recommended Top-Level Keys

A complete Protocol YAML may contain:

```text
schema_version
document
protocol
wire_format
id_allocation
namespaces
services
types
enums
bitsets
errors
capabilities
messages
transport_profiles
sequence_policy
timestamp_policy
security_model
reserved_message_ids
reserved_capability_ids
compatibility
code_generation
```

The minimum required set for an initial Protocol Baseline is:

```text
schema_version
document
protocol
wire_format
id_allocation
namespaces
services
enums
errors
messages
compatibility
code_generation
```

The following are CONDITIONAL:

```text
types
bitsets
capabilities
transport_profiles
sequence_policy
timestamp_policy
security_model
reserved_message_ids
reserved_capability_ids
```

Streaming is represented by `messages[].category: stream` together with sequence, timestamp, loss, and maximum
record-size policies.

Firmware Update is represented by a Bootloader Namespace, an Update Service, Execution Environment, and
Messages with the appropriate category. It is not a separate top-level `firmware_update` key.

Bootloader is an Execution Environment and Namespace, not a top-level `bootloader` key.

The formal top-level security key is `security_model`, not `security`.

### 4.2 Document Metadata

```yaml
document:
  name: EXAMPLE_DEVICE_protocol
  version: v1.0.0
  status: draft
  owner: protocol_team
  last_updated: 2026-07-18
```

Document metadata identifies the specification artifact and shall not be confused with the negotiated Protocol
version.

### 4.3 Protocol Metadata

```yaml
protocol:
  name: example_device_protocol
  family: coordinator_node
  profile_name: EXAMPLE_DEVICE
  profile_id: 0x0001
  version: V1.0.0RC01
  minimum_compatible_version: V1.0.0RC01
  default_execution_environment: application
```

### 4.4 Wire Format

The wire-format section shall define all representation assumptions required for deterministic encoding:

```yaml
wire_format:
  byte_order: little_endian
  bit_order: least_significant_bit_zero
  signed_integer_representation: twos_complement
  floating_point_representation: ieee_754
  string_encoding: utf_8
  boolean_false_value: 0
  boolean_true_value: 1
  structure_encoding: field_by_field
  implicit_padding: prohibited
```

The wire format shall not depend on compiler padding, native struct layout, native enum width, or host
endianness.

---

## 5. Namespace, Service, and ID Allocation

### 5.1 Namespaces

Namespaces separate responsibility and Execution Environment:

```yaml
namespaces:
  - name: framework
    id: 0x00
    execution_environment: any

  - name: application
    id: 0x01
    execution_environment: application

  - name: bootloader
    id: 0x02
    execution_environment: bootloader
```

Namespace IDs shall be unique within the Protocol Family.

### 5.2 Services

```yaml
services:
  - name: DEVICE_MANAGEMENT
    id: 0x01
    namespace: application

  - name: DATA_ACQUISITION
    id: 0x02
    namespace: application

  - name: FIRMWARE_UPDATE
    id: 0x01
    namespace: bootloader
```

Service IDs shall be unique within their Namespace.

### 5.3 Message ID Allocation

`messages[].id` shall be globally unique across all Messages in one Protocol Family.

Recommended 16-bit allocation:

| Range | Recommended Use |
|---|---|
| `0x0000-0x00FF` | Framework, Handshake, Identity, and Health |
| `0x0100-0x0FFF` | Application Command and Response |
| `0x1000-0x10FF` | Informational Event |
| `0x1100-0x11FF` | Alarm |
| `0x1200-0x12FF` | Fault |
| `0x2000-0x2FFF` | Telemetry and Streaming |
| `0x3000-0x3FFF` | Diagnostics, Maintenance, and Calibration |
| `0x4000-0x4FFF` | File and Log Transfer |
| `0x5000-0x5FFF` | Firmware Update and Bootloader |
| `0xF000-0xFEFF` | Experimental or Vendor Extension |
| `0xFF00-0xFFFF` | Reserved |

A Project may refine these ranges before Baseline approval. Published ranges and assigned IDs shall not be
silently reallocated.

### 5.4 Independent Registries

Different Registry spaces are independent:

| Registry | Uniqueness Scope |
|---|---|
| `namespaces[].id` | Unique within the Protocol Family |
| `services[].id` | Unique within one Namespace |
| `messages[].id` | Globally unique across all Messages |
| `capabilities[].id` | Unique within the Capability Registry |
| `errors[].value` | Unique within the Error Registry |
| `enums[].values[].value` | Unique within the containing Enum |
| `bitsets[].bits[].bit` | Unique within the containing Bitset |

The following values may coexist without a wire conflict:

```text
Message ID:     0x0101
Capability ID:  0x0101
```

They belong to different Registries. Nevertheless, unnecessary reuse of the same numeric value across
Registries should be avoided when it would confuse human review.

### 5.5 Request and Response ID Strategy

A Protocol Family shall use one consistent strategy:

```text
Separate Request and Response Message IDs
```

or:

```text
One Message ID plus an explicit Message Type field
```

The initial baseline recommends separate Request and Response IDs because they simplify dispatch, logging,
documentation, and Test Vector ownership.

---

## 6. Type System

### 6.1 Primitive Types

Wire types shall have fixed semantics:

```text
uint8
uint16
uint32
uint64
int8
int16
int32
int64
float32
float64
boolean
bytes
string
```

Ambiguous native-language types such as C `int`, Java signed byte assumptions, or platform-native word size
shall not define the wire contract.

### 6.2 Aliases and Structures

```yaml
types:
  - name: DeviceTimestampUs
    kind: alias
    base_type: uint64
    unit: us

  - name: SoftwareVersion
    kind: struct
    fields:
      - name: major
        type: uint16
      - name: minor
        type: uint16
      - name: patch
        type: uint16
      - name: release_candidate
        type: uint8
```

A structure shall be encoded field by field in declared order. It shall not be encoded by copying a native
language struct memory image.

### 6.3 Enums

```yaml
enums:
  - name: CommandResult
    base_type: uint8
    unknown_value_policy: preserve_raw
    values:
      - name: OK
        value: 0
      - name: INVALID_ARGUMENT
        value: 1
      - name: INVALID_STATE
        value: 2
```

Every Enum shall define:

- Base type
- Explicit numeric value for every symbol
- Unknown-value policy
- Version introduction when required
- Deprecation and replacement when required

Published Enum values shall not be reassigned to different meanings.

### 6.4 Bitsets

```yaml
bitsets:
  - name: DeviceStatusFlags
    base_type: uint16
    unknown_bits_policy: preserve
    bits:
      - name: STREAMING_ACTIVE
        bit: 0
      - name: DEGRADED_MODE
        bit: 1
```

Each bit position shall be unique within its Bitset.

Unknown bits should be preserved unless the security or safety model requires rejection.

### 6.5 Arrays

A fixed-length array shall declare `length`.

A variable-length array shall declare both `length_from` and `maximum_length`.

```yaml
- name: sample_count
  type: uint8
  minimum: 1
  maximum: 64

- name: samples
  type: int32
  array:
    length_from: sample_count
    maximum_length: 64
```

The length field shall appear before the array in the encoded Payload.

The decoder shall validate multiplication, total length, and destination capacity before reading the array.

### 6.6 Strings

A string shall define:

```text
Encoding
Maximum bytes
Length representation
Termination policy
Invalid encoding policy
```

A received byte sequence shall not be assumed to be null-terminated.

---

## 7. Field Definition Rules

### 7.1 Minimum Field Definition

Every field shall define:

```yaml
- name: sample_rate_hz
  type: uint16
  description: Requested acquisition sample rate.
```

A field name and type without a meaningful description are insufficient for a Baseline.

### 7.2 Conditional Field Attributes

Depending on the field, define:

```text
unit
scale
offset
minimum
maximum
invalid_value
default
enum
bitset
array
endianness
required
since
deprecated
replacement
```

### 7.3 Unit

Wire units shall be explicit and fixed.

```yaml
- name: voltage_mv
  type: int32
  unit: mV
```

The wire unit shall not change according to UI preferences.

### 7.4 Scale and Offset

Use exact rational scaling when practical:

```yaml
- name: temperature_raw
  type: int16
  unit: degC
  scale:
    numerator: 1
    denominator: 100
  offset:
    numerator: 0
    denominator: 1
```

The Generator shall use a checked intermediate representation and a defined rounding policy.

### 7.5 Range and Invalid Values

```yaml
- name: battery_percent
  type: uint8
  unit: percent
  minimum: 0
  maximum: 100
  invalid_value: 255
```

An invalid value shall not overlap the normal valid range.

The declared range shall remain representable by the declared wire type.

### 7.6 Optional Fields

An Optional Field in a fixed-layout Message shall:

- Appear only at the end of an extensible Payload.
- Define the version or condition that introduces it.
- Define its default behavior when absent.
- Not shift the offset of an existing field.

A field that must be inserted in the middle requires a new Message format or a TLV-based design.

---

## 8. Message Model

### 8.1 Message Categories

Recommended categories:

```text
command_request
command_response
event
alarm
fault
telemetry
stream
heartbeat
handshake
file_transfer
firmware_update
```

`telemetry` and `stream` are distinct categories and shall not be selected only by transmission frequency.

Use `telemetry` for summarized, state-oriented, periodic, or change-driven data when a newer record may replace
an older unsent record without losing required sequence semantics.

Use `stream` for ordered raw, sampled, or record-oriented data when each record or gap has meaning and the receiver
shall be able to detect loss, duplication, reordering, or sequence discontinuity.

Decision examples:

| Data | Category | Reason |
|---|---|---|
| Battery status summary every 500 ms | `telemetry` | The latest complete status may replace an older unsent status. |
| Device temperature and operating-state snapshot | `telemetry` | It represents current summarized state. |
| Raw sensor samples | `stream` | Record order, timing, and loss detection matter. |
| Timestamped acquisition frames | `stream` | Every record contributes to a continuous ordered sequence. |
| One-time threshold crossing | `event` or `alarm` | It represents a discrete occurrence rather than current summarized state. |

A Project shall document the selected category and its replacement or loss semantics.

### 8.2 Required Message Attributes

Every Message shall define:

```text
name
id
namespace
service
category
direction
execution_environment
description
length_policy
unknown-data policy
payload
security attributes when applicable
compatibility attributes when applicable
```

### 8.3 Direction

Recommended values:

```text
coordinator_to_node
node_to_coordinator
bidirectional
```

A bidirectional Message shall still define the role-specific semantics of each direction.

### 8.4 Execution Environment

Recommended values:

```text
application
bootloader
recovery
factory
any
```

A Message shall not be accepted in the wrong Execution Environment.

### 8.5 Message Example

```yaml
messages:
  - name: GET_DEVICE_INFO_REQUEST
    id: 0x0101
    namespace: application
    service: DEVICE_MANAGEMENT
    category: command_request
    direction: coordinator_to_node
    execution_environment: application
    description: Request Device identity and supported Protocol information.
    length_policy: exact
    unknown_trailing_policy: reject
    timeout_ms: 1000
    retry_policy:
      mode: bounded
      maximum_attempts: 2
    idempotency: idempotent
    payload:
      fields: []
```

---

## 9. Command and Response Rules

### 9.1 Request and Response Pairing

Every Request shall have:

- One explicitly identified Response, or
- An explicit declaration that no Response exists.

```yaml
- name: START_ACQUISITION_RESPONSE
  id: 0x0212
  category: command_response
  response_to: START_ACQUISITION_REQUEST
```

A Response shall not reference a nonexistent Request.

### 9.2 Application Result and Transport Acknowledgment

Transport delivery acknowledgment and Product command execution result are different concepts.

A transport acknowledgment shall not be treated as proof that a Product operation succeeded.

The command Response should include a named application result:

```yaml
payload:
  fields:
    - name: result
      type: enum
      enum: CommandResult
```

### 9.3 Timeout

`timeout_ms` describes the maximum time for the complete application-level Response, not merely the time for
bytes to leave the Transport.

### 9.4 Long-Running Operations

A long-running operation should use:

```text
Command Request
    |
Accepted Response with Operation ID
    |
Progress Event
    |
Completion Event or Final Result Query
```

The Coordinator shall not block one shared processing path for the complete operation duration.

### 9.5 Retry

Retry shall be bounded.

A non-idempotent command shall not be retried automatically unless the Protocol defines an Operation ID,
deduplication, and replay-safe result behavior.

```yaml
retry_policy:
  mode: bounded
  maximum_attempts: 3
  retry_on:
    - timeout
  backoff_ms: 100
```

### 9.6 Idempotency

Recommended values:

```text
idempotent
non_idempotent
idempotent_with_operation_id
```

### 9.7 Allowed States

```yaml
allowed_states:
  - READY
  - CONFIGURED
```

The Node shall validate the current state before executing the command.

An invalid-state command shall return an explicit application error.

---

## 10. Telemetry and Streaming

### 10.1 Telemetry

Telemetry represents periodic or change-driven summarized state.

A Message shall use `category: telemetry` when all of the following are true:

1. The Payload represents a complete or independently useful state snapshot.
2. A newer record may replace an older unsent record according to the declared replacement policy.
3. Loss of an intermediate record does not destroy a required continuous sample sequence.
4. The receiver primarily needs the latest accepted state rather than every historical record.

A Telemetry Message shall define:

```text
Nominal rate or change-driven trigger
Maximum rate
Replacement policy
Timestamp policy
Priority
Maximum record size
Loss policy
```

Recommended replacement policies include:

```text
latest_value_only
queue_all
bounded_queue
```

`latest_value_only` is recommended for replaceable status summaries.

When `latest_value_only` is used:

- The Payload shall be a complete usable snapshot rather than an undocumented partial delta.
- Replacing an older unsent record with a newer record is permitted.
- A sequence field is optional unless the Product requires detection of skipped accepted records.
- A timestamp should identify when the represented state was sampled or assembled.
- A newer timestamp shall not silently represent an older state.

Example:

```yaml
- name: BATTERY_STATUS_TELEMETRY
  id: 0x2001
  namespace: application
  service: POWER_MANAGEMENT
  category: telemetry
  direction: node_to_coordinator
  execution_environment: application
  description: Periodic snapshot of the current battery and charging state.
  length_policy: exact
  unknown_trailing_policy: reject
  nominal_rate_hz:
    numerator: 2
    denominator: 1
  maximum_rate_hz:
    numerator: 5
    denominator: 1
  replacement_policy: latest_value_only
  loss_policy: latest_value_only
  priority: status
  maximum_record_size: 32
  timestamp_policy:
    field: sample_timestamp_us
    epoch: device_boot
    unit: us
    width_bits: 64
    monotonic: true
    meaning: state_snapshot_time
  payload:
    fields:
      - name: sample_timestamp_us
        type: uint64
        unit: us
      - name: battery_percent
        type: uint8
        unit: percent
        minimum: 0
        maximum: 100
        invalid_value: 255
      - name: battery_voltage_mv
        type: uint16
        unit: mV
      - name: charging_active
        type: boolean
      - name: status_flags
        type: bitset
        bitset: BatteryStatusFlags
```

A delta-only Payload that cannot be interpreted without every preceding record shall not use
`replacement_policy: latest_value_only`. It shall use `stream`, `queue_all`, or another explicitly reliable
message design.

### 10.2 Streaming

Streaming represents a continuous ordered sequence of records or samples.

A Message shall use `category: stream` when one or more of the following are true:

- Every record contributes to a continuous acquisition or transfer sequence.
- Record order is semantically significant.
- Loss, duplication, reordering, or a sequence gap shall be detectable.
- The Payload contains raw samples, frames, chunks, or deltas that cannot be replaced by only the latest value.
- Timestamp continuity or sample timing is part of the data contract.

Transmission frequency alone does not make a Message a Stream. A status snapshot transmitted at a high rate may
remain Telemetry when the latest complete value is sufficient.

A Stream Message shall define:

```text
Stream ID
Record sequence
Sequence scope
Sequence reset conditions
Timestamp source and meaning
Loss policy
Maximum record size
Fragmentation behavior when required
```

Example:

```yaml
- name: SAMPLE_STREAM_RECORD
  id: 0x2101
  namespace: application
  service: DATA_ACQUISITION
  category: stream
  direction: node_to_coordinator
  execution_environment: application
  description: Timestamped acquisition sample record.
  length_policy: minimum
  minimum_length: 18
  unknown_trailing_policy: reject
  priority: data
  maximum_record_size: 512
  loss_policy: detectable_drop_allowed
  sequence_policy:
    field: record_sequence
    scope: per_stream
    reset_on:
      - session_start
      - stream_start
  timestamp_policy:
    field: first_sample_timestamp_us
    epoch: device_boot
    unit: us
    width_bits: 64
    monotonic: true
    meaning: first_sample_in_record
```

### 10.3 Control and Streaming Independence

Control Messages and continuous streaming may share one Transport, but they shall not depend on one blocking
processing path.

Streaming load shall not prevent:

```text
STOP
GET_STATUS
RESET_FAULT
ALARM delivery
HEARTBEAT
LINK_RECOVERY
```

### 10.4 Loss Policy

Recommended policies include:

```text
loss_not_allowed
detectable_drop_allowed
latest_value_only
best_effort
```

The receiver shall be able to distinguish a permitted drop from an undetected sequence failure.

### 10.5 Buffer and Record Limits

Every Stream shall define a bounded record size.

The Transport Profile shall prove that the record can be carried directly or through bounded Fragmentation.

---

## 11. Error Model

### 11.1 Error Registry

```yaml
errors:
  - name: ERROR_UNSUPPORTED_MESSAGE
    value: 1
    description: The Message is not supported by the current Protocol profile.

  - name: ERROR_INVALID_STATE
    value: 2
    description: The Message is not valid in the current Node state.
```

Error values shall be unique within the Error Registry.

Published Error values shall not be reassigned.

### 11.2 Error Categories

The Protocol should distinguish at least:

```text
Unsupported Message
Unsupported Capability
Unsupported Parameter
Invalid Length
Invalid Value
Invalid State
Busy
Timeout
Authentication Failure
Integrity Failure
Replay Detected
Version Not Supported
Internal Failure
```

### 11.3 Error Context

An error response should preserve enough context to identify:

```text
Original Request
Correlation or Sequence
Operation ID when applicable
Error code
Optional bounded diagnostic detail
```

Sensitive internal details shall not be exposed merely for debugging convenience.

### 11.4 No Silent Success

A Node shall not return success while ignoring an unsupported command, unsupported parameter, invalid state, or
security failure.

---

## 12. Event, Alarm, and Fault

### 12.1 Event

An Event represents a discrete occurrence:

```yaml
- name: ACQUISITION_STARTED_EVENT
  id: 0x1001
  category: event
  severity: info
  latching: false
  acknowledge_required: false
```

### 12.2 Alarm

An Alarm represents a condition that requires user or system attention:

```yaml
- name: SENSOR_DISCONNECTED_ALARM
  id: 0x1101
  category: alarm
  severity: warning
  latching: false
  acknowledge_required: false
  clear_condition: sensor_reconnected
```

### 12.3 Fault

A Fault represents a functional failure, hardware abnormality, or condition requiring a safe or degraded state:

```yaml
- name: FRONT_END_FAULT
  id: 0x1201
  category: fault
  severity: critical
  latching: true
  acknowledge_required: true
  reset_policy: explicit_command_after_condition_clear
```

### 12.4 Required Semantics

Event, Alarm, and Fault definitions should include:

```text
Severity
Source
Occurrence timestamp
Instance ID
Latching
Acknowledge required
Clear condition
Reset policy
Related Device or channel
Related command or operation
```

A Fault shall not be modeled only as a UI message.

The Node shall retain local Fault Reaction. The Coordinator primarily displays, records, coordinates, and
requests controlled recovery.

---

## 13. Length Policy and Unknown Data Handling

### 13.1 `exact`

The Payload length shall match exactly:

```yaml
length_policy: exact
unknown_trailing_policy: reject
```

Suitable for:

```text
Safety-critical command
Authentication
Key exchange
Fixed-format Update header
Short control command not intended for extension
```

### 13.2 `minimum`

The Payload shall contain at least the declared minimum length:

```yaml
length_policy: minimum
minimum_length: 8
unknown_trailing_policy: reject
```

This policy is suitable for a bounded variable array or another Payload whose size is calculated from a count.

The decoder shall still verify the calculated total length.

### 13.3 `extensible`

Only trailing Optional Fields may be added:

```yaml
length_policy: extensible
minimum_length: 12
unknown_trailing_policy: ignore
```

The following changes are incompatible:

```text
Insert a field in the middle
Remove an existing field
Reorder existing fields
Change an existing field type
Change an existing field width
Change endianness
Change existing semantics incompatibly
```

These changes require a MAJOR Protocol version change or a new Message.

### 13.4 `tlv`

```yaml
length_policy: tlv
unknown_tlv_policy: skip
```

Suitable for:

```text
Capability description
Diagnostics
Extended Device information
Low-frequency configuration
Log metadata
```

Every TLV shall define:

```text
Type
Length
Value
Maximum length
Duplicate policy
Ordering policy
Unknown type policy
```

An unknown TLV may be skipped only after the decoder validates that its declared length fits within the remaining
Payload.

### 13.5 Unknown Handling

The Protocol shall define behavior for:

```text
Unknown Message
Unknown Command
Unknown Event
Unknown Capability
Unknown Enum Value
Unknown Bit
Unknown Field
Unknown TLV Type
Unknown Trailing Data
```

Recommended defaults:

| Type | Recommended Policy |
|---|---|
| Unknown command request | Return `ERROR_UNSUPPORTED_MESSAGE` |
| Unknown event | Record the raw ID and preserve the Session |
| Unknown capability | Preserve or ignore according to the negotiated rule |
| Unknown enum value | Preserve the raw value or map to an explicit UNKNOWN representation |
| Unknown bit | Preserve the raw mask |
| Unknown trailing data | Ignore only for an explicitly extensible Message |
| Unknown TLV | Skip only when the Message declares extension support; otherwise reject |

Unknown data shall not be treated as successful known processing.

---

## 14. Sequence, Correlation, and Time

### 14.1 Correlation

A Command and Response shall have a correlation mechanism:

```text
Request sequence
Transaction ID
Operation ID
Frame-level Correlation ID
```

Example:

```yaml
correlation:
  source: frame_header
  field: request_sequence
```

or:

```yaml
correlation:
  source: payload
  field: transaction_id
```

### 14.2 Sequence Scope

A sequence definition shall identify:

```text
Field
Width
Scope
Initial value
Increment policy
Wrap policy
Reset conditions
Duplicate policy
Out-of-order policy
Gap policy
```

Recommended scopes:

```text
per_session
per_direction
per_stream
per_transaction
```

### 14.3 Duplicate and Out-of-Order Handling

The Protocol shall define whether a duplicate is:

```text
Rejected
Ignored
Replayed from a cached result
Accepted as idempotent
Counted as a diagnostic event
```

Out-of-order handling shall not be inferred from Transport behavior.

### 14.4 Timestamp

A timestamp definition shall include:

```text
Source
Epoch
Unit
Width
Monotonic property
Wrap behavior
Meaning
Synchronization requirement
```

A timestamp named only `timestamp` without epoch, unit, and semantic meaning is insufficient.

---

## 15. Safety-Related Commands and Stale Data

### 15.1 Safety Attributes

A safety-related command should define:

```yaml
safety:
  classification: important
  stale_command_policy: reject
  maximum_command_age_ms: 1000
  duplicate_policy: return_previous_result
```

### 15.2 Stale Command Policy

When command age matters, the Protocol shall define:

- Timestamp or age source
- Maximum accepted age
- Clock or Session assumptions
- Behavior when age cannot be verified
- Error response
- Logging or diagnostic behavior

### 15.3 Duplicate Policy

A control command shall define how duplicate delivery is handled.

For non-idempotent operations, use an Operation ID or equivalent transaction identity.

### 15.4 Final Safety Authority

The Protocol may communicate a requested action, but the Node retains responsibility for local safety validation
and safe-state behavior.

The Coordinator shall not be treated as the only Fault Reaction authority unless the Product architecture
explicitly justifies that dependency.

---

## 16. Security Attributes

### 16.1 Per-Message Security

A security-sensitive Message shall define:

```yaml
security:
  authentication_required: true
  confidentiality_required: false
  integrity_required: true
  anti_replay_required: true
  privilege: control
  key_context: application_control_h2d
```

The Project shall not use one vague `secure: true` flag as a substitute for explicit attributes.

### 16.2 Key Context Separation

Application and Bootloader Messages shall not share an ambiguous Key Context.

Recommended separation includes:

```text
application_control_h2d
application_control_d2h
application_data_h2d
application_data_d2h
bootloader_update_h2d
bootloader_response_d2h
```

A Bootloader Message shall not use an Application Key Context.

### 16.3 Unauthenticated Messages

Only necessary Handshake or Discovery Messages may be allowed before authentication:

```yaml
security:
  authentication_required: false
  integrity_required: false
  allowed_before_session: true
```

The reason shall be documented.

Configuration, control, and Firmware Update Messages shall not be made unauthenticated for development
convenience.

### 16.4 Security Failures

The Security Model shall define behavior for:

```text
Authentication Failure
Integrity Failure
Replay Detected
Wrong Session ID
Wrong Key Context
Counter Gap
Expired Session
Execution Environment Mismatch
```

The Project shall define whether each failure causes an error response, disconnect, diagnostic counter, rate
limit, lockout, or another controlled action.

### 16.5 Security Compatibility

A security-attribute change may alter Session compatibility even when the Payload layout is unchanged.

Compatibility Review shall include authentication, integrity, anti-replay, privilege, and Key Context changes.

---

## 17. Capability and Feature Negotiation

### 17.1 Capability Definition

```yaml
capabilities:
  - name: CAP_SENSOR_STREAMING
    id: 0x0101
    since: V1.0.0
    parameters:
      - name: maximum_channels
        type: uint8
      - name: maximum_sample_rate_hz
        type: uint16
```

A Capability describes what the Node actually supports.

The Coordinator shall not infer all features only from Device model or Protocol version.

Capability IDs belong to the Capability Registry and are not constrained by the Message ID allocation ranges.

### 17.2 Feature Negotiation

The Coordinator should:

```text
Read Device Identity
Read Protocol Version
Read Capabilities
Compare the effective Transport Profile
Enable only supported functions
```

The Coordinator should not:

```text
Recognize one model name
    |
Assume every optional feature exists
```

### 17.3 Unsupported Behavior

Unsupported functions shall return an explicit result:

```text
ERROR_UNSUPPORTED_MESSAGE
ERROR_UNSUPPORTED_CAPABILITY
ERROR_UNSUPPORTED_PARAMETER
ERROR_UNSUPPORTED_TRANSPORT_PROFILE
ERROR_VERSION_NOT_SUPPORTED
```

A Node shall not return success while ignoring an unsupported request.

---

## 18. Transport Profiles and Fragmentation

### 18.1 Transport Profile

```yaml
transport_profiles:
  - name: USB_CDC_BASELINE
    transport: usb_cdc
    minimum_mtu: 64
    maximum_record_size: 4096
    expected_minimum_throughput_bps: 100000
    maximum_control_latency_ms: 100
    fragmentation:
      mode: protocol_record_fragmentation
      maximum_fragments_per_record: 128
```

### 18.2 Static Design Envelope

The design shall define:

```text
Minimum supported MTU
Maximum supported MTU
Maximum record size
Minimum throughput
Maximum control latency
Maximum reassembly buffer
Maximum fragment count
Allowed channel and sample profile
```

The Project shall demonstrate predictable behavior under the worst supported conditions.

### 18.3 Runtime Effective Profile

A dynamically negotiated Transport such as BLE or Wi-Fi should establish an effective runtime profile:

```text
Negotiated MTU
Effective payload
Connection interval
PHY
Expected throughput
Fragment count
Reassembly buffer
Control latency
```

If the effective Transport cannot carry the requested profile, the system shall take an explicit action:

```text
Reduce samples per record
Reduce record rate
Reduce channel count
Reduce sample rate
Use lower-rate Telemetry
Reject the requested Streaming profile
```

The rejection or downgrade reason shall be explicit.

### 18.4 Fragmentation

Fragmentation shall define:

```text
Record ID
Fragment index
Fragment count
Original record length
Reassembly timeout
Duplicate-fragment policy
Out-of-order policy
Maximum concurrent reassembly
Integrity scope
```

The Protocol shall not assume that one Transport operation always carries one complete Protocol Record.

---

## 19. Firmware Update and Bootloader

### 19.1 Namespace and Execution Environment

Firmware Update Messages shall belong to a Bootloader Namespace or an explicitly controlled Update Service:

```yaml
namespace: bootloader
execution_environment: bootloader
```

Application preparation Messages and Bootloader transfer Messages shall remain distinguishable.

### 19.2 Update Transaction

A resumable update should define:

```text
Update Transaction ID
Image ID or Image Type
Manifest hash
Expected image hash
Confirmed offset or chunk bitmap
Next expected offset
Total image size
Security version
```

A Secure Session protects one communication epoch. An Update Transaction may survive a reconnect or rekey only
when its identity and authorization are revalidated.

### 19.3 Chunk Transfer

A chunk Message shall define:

```text
Transaction ID
Offset
Chunk length
Maximum chunk length
Chunk data
Duplicate policy
Out-of-order policy
Retry policy
Integrity scope
```

All sizes and offsets shall be bounded and range-checked.

### 19.4 Manifest and Image Verification

A Firmware Manifest should include:

```text
Device model
Hardware revision range
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

Transport integrity does not replace full-image hash and signature verification.

A CRC may detect accidental transmission corruption but does not establish a trusted Firmware origin.

### 19.5 Resume and Rekey

After reconnect or rekey, the Host shall revalidate:

```text
Update Transaction ID
Image identity
Manifest hash
Host authorization
Confirmed offset or chunk bitmap
```

Application Session keys shall not be reused by the Bootloader Session.

### 19.6 Finalization, Recovery, and Rollback

The Update Protocol shall define:

```text
Finalize request
Full-image verification
Activation policy
Pending image state
Application confirmation
Rollback trigger
Recovery path
Failure reporting
```

The system should not erase the only valid Application image without an approved Recovery Path.

### 19.7 Safe State During Update

The Product specification shall define controlled-output behavior, permitted operations, watchdog behavior,
power-loss behavior, and recovery authority during update.

---

## 20. Compatibility, Deprecation, and Evolution

### 20.1 Compatible Changes

Potentially backward-compatible changes include:

- Add a new Message with a new ID.
- Add a new Capability.
- Add a new Enum value when unknown-value behavior is defined.
- Add a new Bit when unknown-bit behavior is defined.
- Add a trailing Optional Field to an explicitly extensible Message.
- Add optional metadata that does not change parsing or behavior.

Compatibility still requires verification; it shall not be assumed from the change category alone.

### 20.2 Breaking Changes

Breaking changes include:

```text
Change an existing Message ID
Change an existing field offset
Change field type, width, signedness, or endianness
Remove a required field
Reassign an Enum value
Change an Error Code meaning
Insert a field in the middle of a fixed Payload
Change a previously accepted range incompatibly
Change security requirements incompatibly
Change existing semantics incompatibly
```

A breaking change requires a new MAJOR Protocol version or a new Message identity.

### 20.3 Deprecation

A deprecated symbol shall define:

```text
Deprecated since
Replacement
Reason
Removal target
Compatibility behavior
Migration guidance
```

### 20.4 ID Reuse

A published or reserved Message ID shall not be silently reused for a different meaning.

Published Enum values and Error Codes shall not be reassigned.

A retired identifier should remain reserved through the supported compatibility window.

### 20.5 Compatibility Matrix

At minimum, verify:

```text
Current <-> Current
Previous supported Minor <-> Current
Current <-> Previous supported Minor
Unsupported Major
Unknown Optional Field
Unknown Capability
Unknown Enum or Bit
Security-attribute mismatch
```

Version comparison alone shall not replace Capability negotiation.

---

## 21. Code Generation

### 21.1 General Output

Protocol YAML may generate:

```text
C enum, types, constants, Encode, and Decode
C# enum, model, and Codec
Java enum, model, and Codec
Command, Event, Error, and Capability references
Protocol Documentation
Compatibility tests
Boundary tests
Fuzz-seed corpus
Mock Message and Mock Node metadata
Packet Decoder metadata
```

### 21.2 C Generation Rules

C output shall:

- Use fixed-width integer types.
- Use named constants for IDs, lengths, offsets, and values.
- Encode and decode field by field.
- Validate every length and range.
- Avoid using a packed struct as the Wire Format.
- Avoid bit-fields for wire bits.
- Avoid union type-punning for wire bytes.
- Avoid `sizeof(struct)` as packet length.
- Preserve unknown Enum and Bit values according to policy.
- Follow the current Embedded C Coding Rules.

### 21.3 C# Generation Rules

C# output should generate:

```text
Strongly typed enums
Immutable or controlled models
Span<byte> or byte[] Codec
Range validation
Unknown-enum preservation
Payload-length validation
```

The UI shall not directly manipulate raw byte offsets.

### 21.4 Java Generation Rules

Java output should generate:

```text
Fixed-width semantic mapping
ByteBuffer endianness handling
Unsigned conversion helpers
Immutable Message model
Validation result
Unknown-enum raw-value preservation
```

### 21.5 Generated Header

Each generated file should contain:

```text
AUTO-GENERATED FILE. DO NOT EDIT.
Source: EXAMPLE_DEVICE_protocol.yaml
Source document version: v1.0.0
Protocol version: V1.0.0RC01
Source SHA-256: <hash>
Generator: Protocol_Code_Generator V1.0.0RC02
```

### 21.6 Deterministic Generation

The same:

```text
Source YAML
Generator version
Generator configuration
Template version
```

shall produce byte-for-byte identical output, except for an explicitly excluded and controlled metadata field.

Recommended CI gate:

```text
generate
git diff --exit-code
```

CI should report stale generated artifacts but should not silently commit modified output.

---

## 22. Schema Validation and Semantic Lint

### 22.1 Schema Validation

A JSON Schema or equivalent validator should verify:

```text
Required fields exist
Types are correct
Enum values are legal
Hex and integer forms are legal
List and object structures are correct
Unknown keys are rejected unless an extension namespace permits them
Duplicate YAML keys are rejected
All references have the expected structural form
```

### 22.2 Semantic Lint

Schema correctness does not prove that the Protocol is coherent.

Semantic Lint shall check at least:

```text
Message IDs are globally unique in the Message Registry
Namespace IDs are unique in the Protocol Family
Service IDs are unique in their Namespace
Capability IDs are unique in the Capability Registry
Error values are unique in the Error Registry
Enum values are unique in their Enum
Equal numbers in different Registries are not falsely reported as conflicts
Bit positions are unique in their Bitset
Every Response references an existing Request
Every Request has a Response or explicitly declares none
Every variable array has maximum_length
Every length_from field exists and precedes the array
Extensible Optional Fields appear only at the tail
An exact Message does not ignore trailing data
A safety-critical command is not unauthenticated
A non-idempotent command is not retried without a controlled identity
A deprecated symbol does not reuse an ID
A Bootloader Message does not use an Application Key Context
Maximum Payload length remains within its declared limit
A Transport Profile can carry the maximum record or defines Fragmentation
Declared ranges fit the wire type
Invalid values do not overlap normal ranges
Unit and scale are complete when required
Telemetry has cadence or trigger, replacement, timestamp, priority, loss, and maximum-record-size policies
A `latest_value_only` Telemetry Payload is a complete independently usable snapshot
A Message categorized as Telemetry does not require every intermediate record for correct interpretation
A Message categorized as Stream defines sequence continuity and loss or ordering behavior
Streaming has sequence, timestamp, loss, and maximum-record-size policies
Published and reserved identifiers are not reused
```

### 22.3 Naming Lint

Naming checks should verify:

```text
YAML keys use snake_case
Protocol symbols use uppercase letters and underscores
Type names follow the approved reusable-type style
Names are unique in the required scope
Reserved prefixes are not used without authorization
No example placeholder remains in a Product Baseline
```

### 22.4 Placeholder Lint

A Product Baseline shall not contain unresolved placeholders such as:

```text
EXAMPLE_
TODO
TBD
PLACEHOLDER
your_company
com.example
Example.Protocol
```

---

## 23. Compatibility Review

A Compatibility Review shall confirm:

- [ ] Existing Message IDs are unchanged.
- [ ] Existing field offsets are unchanged.
- [ ] Existing field types, widths, signedness, and endianness are unchanged.
- [ ] No existing Required Field was removed.
- [ ] No published Enum value was reassigned.
- [ ] A new Optional Field appears only at the tail of an extensible Payload.
- [ ] New Enum values have an unknown-value policy.
- [ ] New bits have an unknown-bits policy.
- [ ] New Capabilities are negotiated rather than inferred only from version.
- [ ] Every deprecated Message has a replacement and removal plan.
- [ ] Security-attribute changes were evaluated for Session compatibility.
- [ ] Range narrowing was evaluated as a potential breaking change.
- [ ] Published and reserved IDs were not reused.
- [ ] Old Decoder/New Encoder and New Decoder/Old Encoder behavior was tested.
- [ ] Structural rewrites preserve approved normative rules or record every intentional removal.

---

## 24. Test Vectors and Interoperability

### 24.1 Required Test Vector Categories

Important Messages should have:

```text
Normal-value vector
Minimum-boundary vector
Maximum-boundary vector
Invalid-value vector
Truncated-Payload vector
Extra-trailing-data vector
Unknown-Enum vector
Unknown-Bit vector
Variable-array zero, maximum, and overflow vectors
Endianness vector
Round-trip Encode/Decode vector
```

### 24.2 Cross-Language Interoperability

The Project should verify:

```text
C Encode -> C Decode
C Encode -> C# Decode
C# Encode -> C Decode
C# Encode -> C# Decode
Java interoperability when Java is in scope
```

The same vector shall produce the same wire bytes and semantic values across implementations.

### 24.3 Streaming Tests

Streaming tests shall include:

```text
Sequence gap
Duplicate record
Out-of-order record
Sequence wrap
Timestamp wrap or boundary
Record at maximum size
Fragment loss
Reassembly timeout
Backpressure or overflow policy
```

### 24.4 Security Tests

Security Test Vectors should include:

```text
Counter
Nonce
AAD
Ciphertext when confidentiality is enabled
Authentication tag
Replay failure
Wrong Session ID
Wrong Key Context
Expired Session
Execution Environment mismatch
```

### 24.5 Firmware Update Tests

Firmware Update vectors should include:

```text
Resume from confirmed offset
Duplicate chunk
Out-of-order chunk
Invalid chunk length
Hash failure
Signature failure
Wrong Device model
Unsupported hardware revision
Interrupted finalization
Rollback trigger
```

---

## 25. Governance and Baseline Control

### 25.1 Protocol Ownership

The Project shall identify:

```text
Protocol Owner
Schema Owner
Generator Owner
Application Profile Owner
Security Reviewer
Compatibility Reviewer
Test Vector Owner
Release Approver
```

### 25.2 Change Control

A Protocol change shall identify:

- Source requirement or rationale
- Affected Messages, fields, Registries, Capabilities, and Transports
- Compatibility classification
- Security impact
- Code Generation impact
- Test Vector impact
- Required version changes
- Migration plan
- Review evidence

### 25.3 Baseline Contents

A formal Protocol Baseline should include:

```text
Protocol YAML
Schema or validator version
Semantic Lint configuration
Generated artifacts
Human-readable Protocol documentation
Compatibility Matrix
Test Vectors
Generator version
Validation report
Review and approval evidence
```

### 25.4 Generated Artifact Control

Generated output shall be reproducible from the approved Protocol YAML and Generator.

A generated file shall not become an independent design authority.

### 25.5 Structural Rewrite Governance

A translation, reorganization, or formatting rewrite shall preserve all previously approved normative rules or
explicitly record every intentional removal and its rationale.

A successful syntax check does not prove that a structural rewrite preserved the complete technical baseline.

### 25.6 Baseline Gate

Before Baseline approval:

- Schema Validation shall pass.
- Semantic Lint shall pass.
- Compatibility Review shall pass.
- Generated artifacts shall match the source.
- Required Test Vectors shall pass.
- Cross-language interoperability shall pass for languages in scope.
- Security review shall pass for security-sensitive Messages.
- No unresolved placeholder shall remain.
- Document and Protocol versions shall be correct.
- Change history shall accurately describe the change.

---

## 26. Common Design Errors

### 26.1 Maintaining Constants Separately

Incorrect:

```text
C defines one Message ID
C# defines another Message ID
Documentation is updated later
```

Correct:

```text
Protocol YAML defines the ID once
Generated output provides language-specific symbols
```

### 26.2 Using Native Struct Layout as Wire Format

Incorrect:

```text
Cast a C struct to bytes
Transmit sizeof(struct)
```

Correct:

```text
Encode and decode every field according to the Protocol YAML definition
```

### 26.3 Unbounded Variable-Length Data

Incorrect:

```yaml
array:
  length_from: sample_count
```

Correct:

```yaml
array:
  length_from: sample_count
  maximum_length: 64
```

### 26.4 Ignoring Unknown Data Globally

Incorrect:

```text
Ignore all additional Payload bytes for every Message
```

Correct:

```text
Only explicitly extensible Messages may ignore unknown trailing data
```

### 26.5 Retrying a Non-Idempotent Command Blindly

Incorrect:

```text
Timeout -> resend START indefinitely
```

Correct:

```text
Use bounded retry only with a controlled Operation ID and duplicate policy
```

### 26.6 Treating a Transport Ack as Product Success

Incorrect:

```text
USB write completed -> Device operation succeeded
```

Correct:

```text
Wait for the application-level Response or completion Event
```

### 26.7 Sharing One Ambiguous Security Context

Incorrect:

```text
One key name for Application control, streaming, and Bootloader update
```

Correct:

```text
Separate direction, purpose, and Execution Environment Key Contexts
```

### 26.8 Inferring Features Only from Version or Model

Incorrect:

```text
Protocol V1.2.0 always has eight channels
```

Correct:

```text
Protocol Version plus negotiated Capability parameters
```

### 26.9 Editing Generated Code Directly

Incorrect:

```text
The Generator is incomplete, so modify the generated C# file
```

Correct:

```text
Modify YAML, Generator, or Adapter
Regenerate
```

### 26.10 Making Protocol YAML Replace All Product Documentation

Incorrect:

```text
Put complete workflows, UI, Hazard Analysis, and algorithm design into YAML
```

Correct:

```text
YAML defines the wire contract
Application Profile defines Product semantics
SRS defines requirements
State Machine documentation defines flows
Hazard Analysis defines risk controls
```

---

## 27. Project Adoption Checklist

### 27.1 Before Protocol Authoring

- [ ] Framework Application Analysis is complete.
- [ ] Coordinator, Node, Device, and safety responsibility boundaries are defined.
- [ ] An Application Profile or at least a command and data inventory exists.
- [ ] Primary Transport and expected data rate are known.
- [ ] Application and Bootloader Execution Environments are identified.
- [ ] Authentication, confidentiality, integrity, and anti-replay needs are assessed.
- [ ] Maximum record and buffer envelopes are estimated.
- [ ] Protocol, Schema, Generator, and Product version domains are understood.

### 27.2 During YAML Authoring

- [ ] Schema Version is defined.
- [ ] Document Version and Protocol Version are distinct.
- [ ] Endianness and Wire Format are explicit.
- [ ] Message IDs are unique.
- [ ] Registry uniqueness is checked using the correct scope.
- [ ] Request and Response pairing is complete.
- [ ] Every field has a fixed wire type.
- [ ] Physical values have Unit, Scale, and Range.
- [ ] Every variable-length field has a maximum.
- [ ] Every Message defines a Length Policy.
- [ ] Unknown-data behavior is explicit.
- [ ] Timeout, Retry, and Idempotency are defined.
- [ ] Telemetry and Stream categories follow the normative decision boundary.
- [ ] Telemetry defines cadence or trigger, Replacement Policy, Timestamp Policy, Priority, Loss Policy, and Maximum Record Size.
- [ ] A latest-value-only Telemetry Payload is a complete independently usable snapshot.
- [ ] Streaming defines Sequence, Timestamp, Loss Policy, and Maximum Record Size.
- [ ] Event, Alarm, and Fault semantics are separated.
- [ ] Capabilities are defined where feature negotiation is required.
- [ ] Security attributes are defined.
- [ ] Application and Bootloader Key Contexts are separated.
- [ ] The Transport Profile can carry or fragment the largest record.
- [ ] Compatibility and Deprecation policies are defined.

### 27.3 Before Baseline

- [ ] Schema Validation passes.
- [ ] Semantic Lint passes.
- [ ] Naming and placeholder scans pass.
- [ ] Compatibility Review is complete.
- [ ] Generated output is current and deterministic.
- [ ] Generated files contain source and Generator identity.
- [ ] Normal and boundary Test Vectors pass.
- [ ] Cross-language interoperability passes.
- [ ] Streaming loss and ordering tests pass.
- [ ] Security golden vectors pass when applicable.
- [ ] Firmware Update recovery vectors pass when applicable.
- [ ] No published or reserved ID was reused.
- [ ] No Product-specific placeholder remains.
- [ ] Human-readable documentation is current.
- [ ] Review and approval evidence is retained.

---

## 28. Quick Reference

### 28.1 Registry Scope

| Registry | Required Uniqueness |
|---|---|
| Namespace | Protocol Family |
| Service | Namespace |
| Message | Entire Protocol Family |
| Capability | Capability Registry |
| Error | Error Registry |
| Enum Value | Containing Enum |
| Bit Position | Containing Bitset |

### 28.2 Message Minimum Definition

```yaml
- name: MESSAGE_NAME
  id: 0x0000
  namespace: application
  service: SERVICE_NAME
  category: command_request
  direction: coordinator_to_node
  execution_environment: application
  description: Clear wire-contract purpose.
  length_policy: exact
  unknown_trailing_policy: reject
  payload:
    fields: []
```

### 28.3 Stream Minimum Definition

A Stream shall define:

```text
Message ID
Namespace
Service
Direction
Execution Environment
Length Policy
Sequence Policy
Timestamp Policy
Loss Policy
Maximum Record Size
Payload
Security Attributes when required
```

### 28.4 Telemetry and Stream Decision

Use `telemetry` when:

```text
The Payload is a complete summarized state snapshot
The latest value may replace an older unsent value
Intermediate-record loss does not break required sequence semantics
Cadence or a change-driven trigger is defined
Replacement, timestamp, priority, loss, and maximum-size policies are defined
```

Use `stream` when:

```text
Records form a continuous ordered sequence
Loss, duplication, reordering, or gaps shall be detectable
Raw samples, frames, chunks, or non-replaceable deltas are carried
Sequence, timestamp, loss, and maximum-size policies are defined
```

Transmission frequency alone does not determine the category.

### 28.5 Security-Sensitive Message Minimum Definition

A security-sensitive Message shall define:

```text
Authentication
Confidentiality
Integrity
Anti-Replay
Privilege
Key Context
Execution Environment
```

### 28.6 Baseline Validation Sequence

```text
Protocol YAML
    |
Schema Validation
    |
Semantic / Naming / Placeholder Lint
    |
Compatibility Review
    |
Code Generation
    |
Generated-output comparison
    |
Test Vector and Interoperability
    |
Protocol Baseline
```

---

## 29. Baseline Decision Summary

This baseline establishes the following decisions:

1. Protocol YAML is the Single Source of Truth for the machine-verifiable wire contract.
2. Protocol YAML does not replace Product requirements, Hazard Analysis, State Machine, UI, algorithm, or Test documentation.
3. The Protocol contract shall be machine-readable, human-readable, and testable.
4. Message definitions remain Transport-neutral.
5. Schema Version, Protocol Version, Generator Version, Firmware Version, Bootloader Version, Product Version, and Reference Implementation Version remain distinct.
6. YAML keys use `snake_case`; Protocol symbols use uppercase letters with underscore separators.
7. Wire types have fixed width and explicit representation.
8. Wire serialization does not depend on native struct layout, compiler padding, enum width, or host endianness.
9. Message IDs are globally unique across the Message Registry.
10. Namespace, Service, Message, Capability, Error, Enum, and Bitset Registries use their own defined uniqueness scopes.
11. Equal numeric values in different Registries are not automatically conflicts.
12. Every Message defines Namespace, Service, Category, Direction, Execution Environment, Length Policy, and Payload.
13. Every Request has an explicit Response relationship or explicitly declares no Response.
14. Every variable-length field has a maximum bound.
15. Every physical value defines Unit, Scale, Range, and invalid-value behavior when applicable.
16. Unknown-data behavior is explicit and is not globally permissive.
17. Retry is bounded; non-idempotent commands require controlled identity and duplicate handling.
18. Telemetry and Stream use an explicit semantic decision boundary rather than transmission frequency alone.
19. Telemetry represents a complete summarized state snapshot and defines cadence or trigger, Replacement Policy, Timestamp Policy, Priority, Loss Policy, and Maximum Record Size.
20. A latest-value-only Telemetry Payload is independently usable and does not require every intermediate record.
21. Streaming represents a continuous ordered sequence and defines Sequence, Timestamp, Loss Policy, and Maximum Record Size.
22. Event, Alarm, and Fault are distinct semantic categories.
23. Security-sensitive Messages define authentication, integrity, anti-replay, privilege, and Key Context.
24. Application and Bootloader shall not share one ambiguous Key Context.
25. Capabilities describe actual Node support; features shall not be inferred only from Device model or Protocol version.
26. Transport-specific constraints belong in Transport Profiles.
27. Fragmentation and reassembly are bounded and explicitly specified.
28. Firmware Update separates Application preparation, Bootloader execution, Secure Session, Update Transaction, image verification, and recovery.
29. Compatible and breaking changes follow explicit compatibility rules.
30. Published Message IDs, Enum values, Error Codes, and reserved identifiers shall not be silently reused.
31. Generated artifacts identify source and Generator versions and shall not be edited manually.
32. Code Generation is deterministic and validated by regeneration comparison.
33. Baseline approval requires Schema Validation, Semantic Lint, Compatibility Review, Test Vectors, and cross-language interoperability.
34. Structural rewrites preserve approved normative rules or explicitly record intentional removals.
35. Product-specific commands and data remain in each Project's `<Application>_protocol.yaml`, not in one universal Product Protocol.

---

# Conclusion

The relationship among the Framework artifacts is:

```text
Coordinator_Node_Control_Framework
        |
        | defines architecture and governance principles
        v
Protocol_YAML_Definition_Guide
        |
        | defines YAML syntax, semantics, validation, and governance
        v
<Application>_protocol.yaml
        |
        | defines the actual Project wire contract
        v
Code Generator / Documentation / Test Vectors
        |
        v
C / C# / Java / Mock / Decoder / Automated Test
```

The central principle is:

> Protocol YAML is not another manually maintained copy of the Protocol documentation.
> It is the formal, versioned, machine-verifiable, code-generatable, testable, and comparable
> Protocol Contract.
