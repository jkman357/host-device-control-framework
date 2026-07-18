# Protocol YAML Template

## Coordinator/Node Application Protocol Project Template

**Document Name:** `Protocol_YAML_Template.md`  
**Document ID:** PYT  
**Document Version:** v1.0.9  
**Status:** Baseline  
**Supersedes Document Version:** v1.0.8  
**Document Type:** Reusable Project Template  
**Primary Narrative Language:** English  
**Author:** Ray Yang  
**Maintainer:** Ray Yang  
**Repository:** `host-device-control-framework`  
**Related Documents:**
- `Coordinator_Node_Control_Framework.md`
- `Protocol_YAML_Definition_Guide.md`
- `Framework_Application_Analysis_Template.md`

**First Issued:** 2026-07-15  
**Last Revised:** 2026-07-19  
Copyright © 2026 Ray Yang. All rights reserved.

This document is maintained as part of a personal engineering project. It is not an official
document of any employer or organization. No license is granted unless otherwise explicitly stated.

All third-party standards, publications, trademarks, source code, licenses, and legal notices remain
the property of their respective owners. References to third-party materials do not imply ownership,
endorsement, affiliation, or authorization.

---

# 0. Document Purpose

This document provides a reusable template that a Coordinator/Node Project can copy, tailor, and complete
when creating `<Application>_protocol.yaml`.

This document is not the formal Protocol Contract of a specific Product. A Project shall derive its formal
Protocol YAML from this template, for example:

```text
Sensor_Acquisition_protocol.yaml
Smart_Battery_protocol.yaml
Motion_Control_protocol.yaml
Production_Test_protocol.yaml
```

The intended relationship is:

```text
Coordinator_Node_Control_Framework
        |
        v
Protocol_YAML_Definition_Guide
        |
        v
Protocol_YAML_Template
        |
        | copy, tailor, and complete
        v
<Application>_protocol.yaml
        |
        v
Schema Validation / Semantic Lint / Code Generation / Test Vectors
```

## 0.1 Version History

| Version | Date | Description |
|---|---|---|
| v1.0.0 | 2026-07-15 | Established the initial reusable Protocol YAML Project template. |
| v1.0.1 | 2026-07-15 | Corrected the Message ID allocation example; aligned the required and conditional top-level keys with the Definition Guide; separated Registry scopes; and strengthened validation, compatibility, and Baseline checklists. |
| v1.0.2 | 2026-07-18 | Converted the complete template to English; added Ray Yang authorship, repository identity, copyright, personal-project clarification, and third-party-material notice; aligned the template with `Protocol_YAML_Definition_Guide_v1.0.3`; replaced native-layout-oriented Wire Format settings with field-by-field encoding and prohibited implicit padding; added distinct Telemetry and Stream examples and policies; and normalized checklists, appendices, and Baseline decisions for public GitHub publication. |
| v1.0.3 | 2026-07-18 | Defined the intentional redundancy and normative consistency rule for `SAMPLE_STREAM_RECORD.sample_count`; required the sender to encode and the decoder to verify `sample_count == channel_count × samples_per_channel` using widened, overflow-checked arithmetic before reading the sample array; corrected the Stream record minimum length from 18 to 19 bytes; and synchronized Schema Validation, Semantic Lint, Baseline Readiness, and Baseline Decision Summary. |
| v1.0.4 | 2026-07-18 | Updated the active Framework, Definition Guide, and Application Analysis references to `Coordinator_Node_Control_Framework.md`, `Protocol_YAML_Definition_Guide.md`, and `Framework_Application_Analysis_Template.md`; updated the illustrative YAML minimum-version metadata and Appendix responsibility references; and preserved the YAML structure and all Protocol semantics without technical change. |
| v1.0.5 | 2026-07-18 | Adopted the stable canonical filename `Protocol_YAML_Template.md`; updated all active Framework, Definition Guide, Application Analysis, and illustrative Project document references to canonical paths; aligned the illustrative minimum-version metadata with the current document set; and preserved the YAML structure and all Protocol semantics without technical change. |
| v1.0.6 | 2026-07-18 | Corrected computed Message minimum lengths; made Stream, Firmware chunk, Capability, and Transport envelopes mutually consistent; added explicit per-Message security, direction/environment Key Context mappings, Application and Bootloader Handshake contracts, sender-local Heartbeat timestamp semantics, and a signed canonical Firmware Manifest transfer; separated Telemetry replacement semantics from queue discipline; updated interoperability wording; and expanded Schema, Semantic Lint, security, Firmware Update, and Baseline checks. |
| v1.0.7 | 2026-07-18 | Closed the remaining security-contract and size-model gaps: strengthened unresolved-placeholder Lint; replaced public permanent identity and Capability disclosure with bounded ephemeral Discovery plus authenticated revalidation; added machine-verifiable Record Counter, Rekey, failure, and atomic-cutover policies; bound Handshake Profile selection and canonical transcript fields to reject downgrade and profile confusion; defined exact canonical Firmware signature encodings; fixed `minimum_length` to mean the fixed decoding prefix only; and separated plaintext Message size, security overhead, secured Record size, Transport reassembly size, and Fragment payload limits. |
| v1.0.8 | 2026-07-18 | Defined a concrete 16-byte Fragment Header and complete reassembly policies; replaced opaque Handshake payloads with four named fixed-capacity wire structs and explicit transcript assembly; replaced numeric Profile-strength comparison with allowlists, preference order, security level, and deprecation state; added Device-issued Firmware Update resume authorization bound to transaction, Manifest, Device, Host, and security version; corrected CAN FD minimum data-bearing MTU; and synchronized all machine-verifiable checks. |
| v1.0.9 | 2026-07-19 | Added explicit Supersedes metadata required by repository governance; no normative Protocol YAML template semantics changed. |

---

# 1. How to Use This Template

## 1.1 Create the Project File

Copy the YAML code block in Section 4 into:

```text
protocol/spec/<Application>_protocol.yaml
```

Example:

```text
protocol/spec/Sensor_Acquisition_protocol.yaml
```

## 1.2 Tailoring Rules

When tailoring the template:

1. Replace every `EXAMPLE_*` identifier with an approved Project identifier.
2. Replace illustrative IDs with the Project's approved Registry assignments.
3. Remove Services, Messages, Capabilities, Transport Profiles, and Code Generation targets that are not in scope.
4. Preserve the required Framework/Application/Bootloader Namespace boundaries that remain applicable.
5. Define Unit, Scale, Range, Length Policy, Timeout, Retry, Idempotency, Compatibility, and Security explicitly.
6. Do not place UI control names, MCU registers, RTOS task names, Driver handles, socket handles, or COM port names in the Protocol Contract.
7. Use `category: telemetry` only for complete summarized state snapshots whose older unsent values may be replaced.
8. Use `category: stream` for continuous ordered records whose loss, duplication, reordering, or timing discontinuity matters.
9. Complete Schema Validation, Semantic Lint, Compatibility Review, Test Vectors, cross-implementation interoperability, and cross-language interoperability for every language pair in scope before Protocol Baseline approval.
10. Define an explicit `security` block for every Message; omission shall not imply inheritance.
11. Define Application and Bootloader Handshake Messages and profiles when Secure Sessions are required.
12. Replace every unresolved security sentinel, including `UNRESOLVED_PROJECT_DECISION`, before Product Baseline approval.
13. Define public Discovery exposure, rate limiting, ephemeral identity, transcript binding, and authenticated post-Session revalidation.
14. Define Record Counter, Rekey, Hard Limit, persistence, atomic cutover, and failure behavior for every Key Context.
15. Define exact Firmware signature encoding and length for every accepted algorithm.
16. Record every intentional removal or structural change that affects a previously approved Protocol Baseline.

## 1.3 Minimum and Conditional Top-Level Keys

The first formal Project Baseline shall contain at least:

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

Complete the following keys when required by the Project:

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

The following features are not independent top-level keys:

```text
Telemetry
    Represented by messages[].category: telemetry together with cadence or trigger,
    replacement_policy, timestamp_policy, priority, loss_policy,
    and maximum_plaintext_message_size.

Streaming
    Represented by messages[].category: stream together with sequence_policy,
    timestamp_policy, loss_policy, and maximum_plaintext_message_size.

Firmware Update
    Represented by the bootloader Namespace, FIRMWARE_UPDATE Service,
    Execution Environment, and messages[].category: firmware_update.

Bootloader
    Represented as a Namespace and Execution Environment.

Per-Message Security
    Represented by messages[].security under the top-level security_model.
```

Therefore, a formal Protocol YAML shall not expect these top-level keys:

```text
telemetry:
streaming:
firmware_update:
bootloader:
security:
```

The formal top-level security key is:

```text
security_model:
```

## 1.4 Registry Rules

The numeric spaces of different Registries are independent:

| Registry | Uniqueness Scope |
|---|---|
| `namespaces[].id` | Unique within the Protocol Family |
| `services[].id` | Unique within one Namespace |
| `messages[].id` | Globally unique across all Messages |
| `capabilities[].id` | Unique within the Capability Registry |
| `errors[].value` | Unique within the Error Registry |
| `enums[].values[].value` | Unique within the containing Enum |
| `bitsets[].bits[].bit` | Unique within the containing Bitset |

Therefore:

```text
Message ID:     0x0101
Capability ID:  0x0101
```

may coexist because they belong to different Registries.

## 1.5 Template Placeholders

This reusable template intentionally contains identifiers and unresolved sentinels such as:

```text
EXAMPLE_DEVICE
EXAMPLE_Application_Profile
example_device
protocol_team
UNRESOLVED_PROJECT_DECISION
your_company
com.example
Example.Protocol
```

A derived Product or Project Protocol Baseline shall not retain these values. Placeholder and unresolved-sentinel
matching shall be case-insensitive and shall scan YAML scalar values, generated identifiers, generated comments,
configuration, documentation, and test vectors.

Security-critical fields including Key Agreement, KDF, proof format, credential model, cipher suite, signature
profile, trust anchor, and Counter/Rekey policy shall not use an unresolved sentinel in a Product Baseline.

The reusable template itself shall be excluded from Product placeholder-failure rules. The extracted
`<Application>_protocol.yaml` shall not be excluded.

## 1.6 Redundant Wire Fields and Derived Relationships

A redundant wire field is permitted only when it has a deliberate Protocol purpose and an explicit consistency rule.

In `SAMPLE_STREAM_RECORD`, `sample_count` is intentionally transmitted as the immediate array-length field used by
the decoder. It shall not become an independent source of truth.

The required relationship is:

```text
sample_count == channel_count × samples_per_channel
```

The sender shall encode values that satisfy this relationship.

Before reading `samples`, the decoder shall:

1. Convert `channel_count` and `samples_per_channel` to a sufficiently wide unsigned type.
2. Check the multiplication for overflow.
3. Verify that the product does not exceed `sample_count.maximum` or `samples.maximum_length`.
4. Verify that the product equals the received `sample_count`.
5. Verify that the remaining Payload length contains exactly the declared number of encoded sample values.
6. Reject the Message before array access when any check fails.

A Project shall not introduce another redundant count, length, offset, or derived field without an equivalent
normative relationship and mismatch policy.

---

# 2. Recommended Message ID Ranges

The following ranges apply only to `messages[].id`:

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

A Project may refine these ranges before Baseline approval. Published and reserved assignments shall not be
silently reallocated after approval.

---

# 3. Tailoring Profiles

## 3.1 Small MVP

A small MVP may retain:

```text
Device Identity
Protocol Version
Capability Query
Get Status
Set Configuration
Start
Stop
Basic Telemetry
Basic Stream
Error Response
One Transport Profile
```

It may initially remove:

```text
Bootloader Namespace
Firmware Update
File Transfer
TLV Extension
Multiple Transport Profiles
Advanced Security
Java Code Generation
```

Removing a feature does not permit an invalid reference to remain.

## 3.2 Formal Product

A formal Product should complete:

```text
Security Attributes
Anti-Replay
Capability Negotiation
Transport Envelope
Runtime Effective Profile
Event / Alarm / Fault
State Restrictions
Stale and Duplicate Command Policy
Firmware Update
Compatibility Policy
Deprecation
Golden Test Vectors
Recovery and Rollback
```

---

# 4. Complete YAML Template

The YAML below is a legal illustrative Project skeleton. It is not the formal design of any existing Product.

```yaml
schema_version: "1.0"

document:
  name: EXAMPLE_DEVICE_protocol
  version: v1.0.0
  status: draft
  owner: protocol_team
  last_updated: 2026-07-18

  related_framework:
    name: Coordinator_Node_Control_Framework
    minimum_version: v1.0.8

  related_definition_guide:
    name: Protocol_YAML_Definition_Guide
    minimum_version: v1.0.8

  related_application_analysis: EXAMPLE_Framework_Application_Analysis.md
  related_application_profile: EXAMPLE_Application_Profile.md
  related_srs: EXAMPLE_SRS.md
  related_node_sdd: EXAMPLE_Node_SDD.md
  related_coordinator_sdd: EXAMPLE_Coordinator_SDD.md
  related_test_plan: EXAMPLE_Test_Plan.md

protocol:
  name: example_device_protocol
  family: coordinator_node
  profile_name: EXAMPLE_DEVICE
  profile_id: 0x0001
  version: V1.0.0RC01
  minimum_compatible_version: V1.0.0RC01
  default_execution_environment: application

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

record_size_model:
  message_length_scope: encoded_plaintext_payload_fields_only
  minimum_length_definition: fixed_prefix_before_first_variable_or_optional_tail
  variable_content_validation: count_range_then_exact_received_length_then_destination_capacity
  secured_record_formula: plaintext_message_size_plus_protocol_header_plus_security_header_plus_authentication_tag
  fragmentation_scope: secured_record
  fragment_header_struct: SecuredRecordFragmentHeaderV1
  runtime_fragment_payload_formula: runtime_mtu_minus_fragment_header_bytes
  required_fragment_count_formula: ceil(original_secured_record_length_div_runtime_fragment_payload)
  fragment_integrity_scope: complete_secured_record_aead_verified_after_reassembly
id_allocation:
  message_ranges:
    - range_start: 0x0000
      range_end: 0x00FF
      purpose: framework_system

    - range_start: 0x0100
      range_end: 0x0FFF
      purpose: application_command_response

    - range_start: 0x1000
      range_end: 0x10FF
      purpose: informational_event

    - range_start: 0x1100
      range_end: 0x11FF
      purpose: alarm

    - range_start: 0x1200
      range_end: 0x12FF
      purpose: fault

    - range_start: 0x2000
      range_end: 0x2FFF
      purpose: telemetry_streaming

    - range_start: 0x3000
      range_end: 0x3FFF
      purpose: diagnostics_maintenance_calibration

    - range_start: 0x4000
      range_end: 0x4FFF
      purpose: file_log_transfer

    - range_start: 0x5000
      range_end: 0x5FFF
      purpose: firmware_update_bootloader

    - range_start: 0xF000
      range_end: 0xFEFF
      purpose: experimental_vendor_extension

    - range_start: 0xFF00
      range_end: 0xFFFF
      purpose: reserved

namespaces:
  - name: framework
    id: 0x00
    execution_environment: any
    description: Common identity, version, capability, session, and health Messages.

  - name: application
    id: 0x01
    execution_environment: application
    description: Product-specific Application behavior.

  - name: bootloader
    id: 0x02
    execution_environment: bootloader
    description: Firmware Update and recovery behavior.

services:
  - id: 0x01
    name: DEVICE_MANAGEMENT
    namespace: framework
    description: Device identity, version, capability, and health.

  - id: 0x02
    name: SESSION_MANAGEMENT
    namespace: framework
    description: Session establishment, heartbeat, and link health.

  - id: 0x10
    name: DEVICE_CONFIGURATION
    namespace: application
    description: Product configuration.

  - id: 0x11
    name: DEVICE_CONTROL
    namespace: application
    description: Product start, stop, and operation control.

  - id: 0x12
    name: DATA_ACQUISITION
    namespace: application
    description: Telemetry and high-rate Streaming.

  - id: 0x13
    name: DIAGNOSTICS
    namespace: application
    description: Diagnostic, self-test, and maintenance operations.

  - id: 0x20
    name: FIRMWARE_UPDATE
    namespace: bootloader
    description: Firmware Update transaction and image transfer.

types:
  - name: SecuredRecordFragmentHeaderV1
    kind: struct
    description: Exact 16-byte Fragment Header. The CRC detects accidental Header corruption; authenticity is 
      established only after complete secured-Record reassembly and AEAD verification.
    fields:
      - name: record_id
        type: uint32
        description: Sender-Session-Epoch-unique secured-Record identifier.
      - name: fragment_index
        type: uint16
        description: Zero-based Fragment index.
      - name: fragment_count
        type: uint16
        minimum: 1
        description: Total Fragment count for the secured Record.
      - name: original_secured_record_length
        type: uint32
        description: Exact secured-Record length before Fragmentation.
      - name: fragment_payload_length
        type: uint16
        description: Number of secured-Record bytes carried after this Header.
      - name: header_crc16
        type: uint16
        description: CRC-16/CCITT-FALSE over the preceding 14 Header bytes; corruption detection only, not 
          authentication.
  - name: ProtocolVersion
    kind: struct
    description: Semantic Protocol version.
    fields:
      - name: major
        type: uint8
        description: Major version.

      - name: minor
        type: uint8
        description: Minor version.

      - name: patch
        type: uint8
        description: Patch version.

      - name: release_candidate
        type: uint8
        description: Zero means formal release; a nonzero value is the RC number.

  - name: SoftwareVersion
    kind: struct
    description: Firmware or software version.
    fields:
      - name: major
        type: uint16
        description: Major version.

      - name: minor
        type: uint16
        description: Minor version.

      - name: patch
        type: uint16
        description: Patch version.

      - name: release_candidate
        type: uint8
        description: Zero means formal release; a nonzero value is the RC number.

  - name: DeviceTimestampUs
    kind: alias
    base_type: uint64
    unit: us
    description: Monotonic microseconds since Device boot.

  - name: PeerMonotonicTimestampUs
    kind: alias
    base_type: uint64
    unit: us
    description: Sender-local monotonic microseconds; the sender-specific epoch is defined by the Message policy.
  - name: ApplicationHandshakeRequestV1
    kind: struct
    description: Concrete fixed-capacity Application Handshake wire payload. Length fields define meaningful bytes; 
      unused slot bytes shall be zero and are transcript-bound.
    fields:
      - name: handshake_id
        type: alias
        alias: TransactionId
        description: Handshake transaction identifier.
      - name: protocol_family_id
        type: uint32
        description: Approved Protocol-family identifier.
      - name: protocol_version
        type: struct
        struct: ProtocolVersion
        description: Protocol version proposed by the initiator.
      - name: discovery_id
        type: uint8
        description: Ephemeral Discovery identifier; all zero only when public Discovery was not used.
        array:
          length: 8
      - name: handshake_profile_id
        type: uint16
        description: Selected Handshake Profile identifier.
      - name: execution_environment
        type: enum
        enum: ExecutionEnvironment
        description: Must encode APPLICATION.
      - name: initiator_role
        type: enum
        enum: HandshakeRole
        description: Must encode COORDINATOR.
      - name: responder_role
        type: enum
        enum: HandshakeRole
        description: Must encode NODE.
      - name: initiator_identity_length
        type: uint8
        minimum: 1
        maximum: 32
        description: Meaningful initiator-identity bytes in the fixed slot.
      - name: initiator_identity
        type: uint8
        description: Fixed 32-byte identity slot; bytes beyond initiator_identity_length shall be zero.
        array:
          length: 32
      - name: initiator_nonce
        type: uint8
        description: Fresh 32-byte nonce.
        array:
          length: 32
      - name: initiator_ephemeral_public_key_length
        type: uint16
        minimum: 1
        maximum: 128
        description: Meaningful public-key bytes in the fixed slot.
      - name: initiator_ephemeral_public_key
        type: uint8
        description: Fixed 128-byte public-key slot; unused bytes shall be zero.
        array:
          length: 128
      - name: offered_algorithm_set_id
        type: uint16
        description: Registered algorithm-set identifier offered by the initiator.
      - name: initiator_proof_length
        type: uint16
        minimum: 1
        maximum: 128
        description: Meaningful proof bytes in the fixed slot.
      - name: initiator_proof
        type: uint8
        description: Fixed 128-byte initiator-proof slot; unused bytes shall be zero.
        array:
          length: 128
  - name: ApplicationHandshakeResponseV1
    kind: struct
    description: Concrete fixed-capacity Application Handshake wire payload. Length fields define meaningful bytes; 
      unused slot bytes shall be zero and are transcript-bound.
    fields:
      - name: result
        type: enum
        enum: CommandResult
        description: Handshake result.
      - name: handshake_id
        type: alias
        alias: TransactionId
        description: Handshake transaction identifier.
      - name: protocol_family_id
        type: uint32
        description: Accepted Protocol-family identifier.
      - name: protocol_version
        type: struct
        struct: ProtocolVersion
        description: Accepted Protocol version.
      - name: discovery_id
        type: uint8
        description: Echo of the transcript-bound ephemeral Discovery identifier.
        array:
          length: 8
      - name: handshake_profile_id
        type: uint16
        description: Accepted Handshake Profile identifier.
      - name: execution_environment
        type: enum
        enum: ExecutionEnvironment
        description: Must encode APPLICATION.
      - name: initiator_role
        type: enum
        enum: HandshakeRole
        description: Must encode COORDINATOR.
      - name: responder_role
        type: enum
        enum: HandshakeRole
        description: Must encode NODE.
      - name: responder_identity_length
        type: uint8
        minimum: 1
        maximum: 32
        description: Meaningful responder-identity bytes in the fixed slot.
      - name: responder_identity
        type: uint8
        description: Fixed 32-byte identity slot; bytes beyond responder_identity_length shall be zero.
        array:
          length: 32
      - name: responder_nonce
        type: uint8
        description: Fresh 32-byte nonce.
        array:
          length: 32
      - name: responder_ephemeral_public_key_length
        type: uint16
        minimum: 1
        maximum: 128
        description: Meaningful public-key bytes in the fixed slot.
      - name: responder_ephemeral_public_key
        type: uint8
        description: Fixed 128-byte public-key slot; unused bytes shall be zero.
        array:
          length: 128
      - name: selected_algorithm_set_id
        type: uint16
        description: Registered algorithm-set identifier selected from the request.
      - name: session_id
        type: uint32
        description: New Session identifier; zero when the Handshake failed.
      - name: derived_key_context_set_id
        type: uint16
        description: Registered set of derived direction-specific Key Contexts.
      - name: request_transcript_hash
        type: uint8
        description: SHA-256 of the canonical request struct.
        array:
          length: 32
      - name: responder_proof_length
        type: uint16
        minimum: 1
        maximum: 128
        description: Meaningful proof bytes in the fixed slot.
      - name: responder_proof
        type: uint8
        description: Fixed 128-byte responder-proof slot; unused bytes shall be zero.
        array:
          length: 128
  - name: BootloaderHandshakeRequestV1
    kind: struct
    description: Concrete fixed-capacity Bootloader Handshake wire payload. Length fields define meaningful bytes; 
      unused slot bytes shall be zero and are transcript-bound.
    fields:
      - name: handshake_id
        type: alias
        alias: TransactionId
        description: Handshake transaction identifier.
      - name: protocol_family_id
        type: uint32
        description: Approved Protocol-family identifier.
      - name: protocol_version
        type: struct
        struct: ProtocolVersion
        description: Protocol version proposed by the initiator.
      - name: discovery_id
        type: uint8
        description: Ephemeral Discovery identifier; all zero only when public Discovery was not used.
        array:
          length: 8
      - name: handshake_profile_id
        type: uint16
        description: Selected Handshake Profile identifier.
      - name: execution_environment
        type: enum
        enum: ExecutionEnvironment
        description: Must encode BOOTLOADER.
      - name: initiator_role
        type: enum
        enum: HandshakeRole
        description: Must encode COORDINATOR.
      - name: responder_role
        type: enum
        enum: HandshakeRole
        description: Must encode NODE.
      - name: initiator_identity_length
        type: uint8
        minimum: 1
        maximum: 32
        description: Meaningful initiator-identity bytes in the fixed slot.
      - name: initiator_identity
        type: uint8
        description: Fixed 32-byte identity slot; bytes beyond initiator_identity_length shall be zero.
        array:
          length: 32
      - name: initiator_nonce
        type: uint8
        description: Fresh 32-byte nonce.
        array:
          length: 32
      - name: initiator_ephemeral_public_key_length
        type: uint16
        minimum: 1
        maximum: 128
        description: Meaningful public-key bytes in the fixed slot.
      - name: initiator_ephemeral_public_key
        type: uint8
        description: Fixed 128-byte public-key slot; unused bytes shall be zero.
        array:
          length: 128
      - name: offered_algorithm_set_id
        type: uint16
        description: Registered algorithm-set identifier offered by the initiator.
      - name: initiator_proof_length
        type: uint16
        minimum: 1
        maximum: 128
        description: Meaningful proof bytes in the fixed slot.
      - name: initiator_proof
        type: uint8
        description: Fixed 128-byte initiator-proof slot; unused bytes shall be zero.
        array:
          length: 128
  - name: BootloaderHandshakeResponseV1
    kind: struct
    description: Concrete fixed-capacity Bootloader Handshake wire payload. Length fields define meaningful bytes; 
      unused slot bytes shall be zero and are transcript-bound.
    fields:
      - name: result
        type: enum
        enum: CommandResult
        description: Handshake result.
      - name: handshake_id
        type: alias
        alias: TransactionId
        description: Handshake transaction identifier.
      - name: protocol_family_id
        type: uint32
        description: Accepted Protocol-family identifier.
      - name: protocol_version
        type: struct
        struct: ProtocolVersion
        description: Accepted Protocol version.
      - name: discovery_id
        type: uint8
        description: Echo of the transcript-bound ephemeral Discovery identifier.
        array:
          length: 8
      - name: handshake_profile_id
        type: uint16
        description: Accepted Handshake Profile identifier.
      - name: execution_environment
        type: enum
        enum: ExecutionEnvironment
        description: Must encode BOOTLOADER.
      - name: initiator_role
        type: enum
        enum: HandshakeRole
        description: Must encode COORDINATOR.
      - name: responder_role
        type: enum
        enum: HandshakeRole
        description: Must encode NODE.
      - name: responder_identity_length
        type: uint8
        minimum: 1
        maximum: 32
        description: Meaningful responder-identity bytes in the fixed slot.
      - name: responder_identity
        type: uint8
        description: Fixed 32-byte identity slot; bytes beyond responder_identity_length shall be zero.
        array:
          length: 32
      - name: responder_nonce
        type: uint8
        description: Fresh 32-byte nonce.
        array:
          length: 32
      - name: responder_ephemeral_public_key_length
        type: uint16
        minimum: 1
        maximum: 128
        description: Meaningful public-key bytes in the fixed slot.
      - name: responder_ephemeral_public_key
        type: uint8
        description: Fixed 128-byte public-key slot; unused bytes shall be zero.
        array:
          length: 128
      - name: selected_algorithm_set_id
        type: uint16
        description: Registered algorithm-set identifier selected from the request.
      - name: session_id
        type: uint32
        description: New Session identifier; zero when the Handshake failed.
      - name: derived_key_context_set_id
        type: uint16
        description: Registered set of derived direction-specific Key Contexts.
      - name: request_transcript_hash
        type: uint8
        description: SHA-256 of the canonical request struct.
        array:
          length: 32
      - name: responder_proof_length
        type: uint16
        minimum: 1
        maximum: 128
        description: Meaningful proof bytes in the fixed slot.
      - name: responder_proof
        type: uint8
        description: Fixed 128-byte responder-proof slot; unused bytes shall be zero.
        array:
          length: 128
  - name: FirmwareManifestV1
    kind: struct
    description: Canonical signed Firmware Manifest fields encoded field by field without implicit padding.
    fields:
      - name: manifest_format_version
        type: uint16
        minimum: 1
        maximum: 1
        description: Canonical Manifest format version.
      - name: target_device_model
        type: uint16
        description: Required Device model identifier.
      - name: minimum_hardware_revision
        type: uint16
        description: Minimum compatible hardware revision.
      - name: maximum_hardware_revision
        type: uint16
        description: Maximum compatible hardware revision.
      - name: firmware_version
        type: struct
        struct: SoftwareVersion
        description: Candidate Firmware version.
      - name: image_type
        type: uint8
        description: Target image or partition type.
      - name: image_size
        type: uint32
        description: Complete image size in bytes.
      - name: security_version
        type: uint32
        description: Monotonic anti-rollback security version.
      - name: minimum_bootloader_version
        type: struct
        struct: SoftwareVersion
        description: Minimum Bootloader version allowed to install this image.
      - name: required_protocol_version
        type: struct
        struct: ProtocolVersion
        description: Required Protocol version after activation.
      - name: build_identifier
        type: uint8
        description: Fixed-width build identifier.
        array:
          length: 16
      - name: image_hash
        type: uint8
        description: SHA-256 hash of the complete Firmware image.
        array:
          length: 32
      - name: signing_key_id
        type: uint32
        description: Identifier of the approved Firmware-signing trust anchor.
      - name: signature_algorithm
        type: enum
        enum: FirmwareSignatureAlgorithm
        description: Algorithm used to sign the canonical Manifest hash.
  - name: UpdateResumeAuthorizationV1
    kind: struct
    description: Device-issued fixed 156-byte authorization permitting one authenticated Host identity to attach a new 
      Bootloader Session to a persisted Update Transaction.
    fields:
      - name: update_transaction_id
        type: alias
        alias: TransactionId
        description: Persisted Update Transaction identifier.
      - name: manifest_hash
        type: uint8
        description: Accepted canonical Manifest hash.
        array:
          length: 32
      - name: device_identity_hash
        type: uint8
        description: SHA-256 of the authenticated Device identity.
        array:
          length: 32
      - name: authorized_host_identity_hash
        type: uint8
        description: SHA-256 of the authenticated Host identity authorized to resume.
        array:
          length: 32
      - name: security_version
        type: uint32
        description: Accepted anti-rollback security version.
      - name: resume_generation
        type: uint32
        description: Monotonic generation incremented whenever a new token is issued.
      - name: authorization_nonce
        type: uint8
        description: Fresh token nonce.
        array:
          length: 16
      - name: token_mac
        type: uint8
        description: HMAC-SHA-256 over every preceding field in canonical order and the domain separator.
        array:
          length: 32
  - name: TransactionId
    kind: alias
    base_type: uint32
    description: Coordinator-generated transaction identifier.

  - name: OperationId
    kind: alias
    base_type: uint32
    description: Coordinator-generated operation identifier.

enums:
  - name: CommandResult
    base_type: uint16
    unknown_value_policy: preserve_raw
    description: Common command-execution result.

    values:
      - name: OK
        value: 0x0000

      - name: INVALID_LENGTH
        value: 0x0001

      - name: UNSUPPORTED_MESSAGE
        value: 0x0002

      - name: INVALID_STATE
        value: 0x0003

      - name: OUT_OF_RANGE
        value: 0x0004

      - name: UNAUTHORIZED
        value: 0x0005

      - name: BUSY
        value: 0x0006

      - name: INTERNAL_ERROR
        value: 0x0007

      - name: VERSION_NOT_SUPPORTED
        value: 0x0008

      - name: CAPABILITY_NOT_SUPPORTED
        value: 0x0009

      - name: MANIFEST_INVALID
        value: 0x000a
      - name: SIGNATURE_INVALID
        value: 0x000b
      - name: ROLLBACK_PROHIBITED
        value: 0x000c
      - name: UNSUPPORTED_SECURITY_PROFILE
        value: 0x000d
      - name: SECURITY_DOWNGRADE_REJECTED
        value: 0x000e
      - name: HANDSHAKE_PROOF_INVALID
        value: 0x000f
      - name: COUNTER_EXHAUSTED
        value: 0x0010
  - name: DeviceOperationState
    base_type: uint8
    unknown_value_policy: preserve_raw
    description: High-level Device operation state.

    values:
      - name: UNKNOWN
        value: 0

      - name: INITIALIZING
        value: 1

      - name: READY
        value: 2

      - name: CONFIGURED
        value: 3

      - name: RUNNING
        value: 4

      - name: STOPPING
        value: 5

      - name: FAULT
        value: 6

      - name: BOOTLOADER
        value: 7

  - name: ExecutionEnvironment
    base_type: uint8
    unknown_value_policy: reject
    description: Active Execution Environment.

    values:
      - name: APPLICATION
        value: 0

      - name: BOOTLOADER
        value: 1

      - name: RECOVERY
        value: 2

      - name: FACTORY
        value: 3

  - name: HandshakeRole
    base_type: uint8
    unknown_value_policy: reject
    description: Role bound into the canonical Handshake transcript.
    values:
      - name: COORDINATOR
        value: 0
      - name: NODE
        value: 1
  - name: DeviceHealth
    base_type: uint8
    unknown_value_policy: preserve_raw
    description: Summarized Device health.

    values:
      - name: UNKNOWN
        value: 0

      - name: NORMAL
        value: 1

      - name: WARNING
        value: 2

      - name: DEGRADED
        value: 3

      - name: FAULT
        value: 4

  - name: FirmwareSignatureAlgorithm
    base_type: uint8
    unknown_value_policy: reject
    description: Approved Firmware Manifest signature algorithms.
    values:
      - name: ECDSA_P256_SHA256
        value: 1
      - name: ED25519
        value: 2
bitsets:
  - name: DeviceStatusFlags
    base_type: uint16
    unknown_bits_policy: preserve
    description: Common Device status flags.

    bits:
      - name: READY
        bit: 0

      - name: CONFIGURED
        bit: 1

      - name: RUNNING
        bit: 2

      - name: WARNING_PRESENT
        bit: 3

      - name: FAULT_PRESENT
        bit: 4

      - name: DATA_AVAILABLE
        bit: 5

      - name: UPDATE_AVAILABLE
        bit: 6

  - name: SampleQualityFlags
    base_type: uint16
    unknown_bits_policy: preserve
    description: Record-level or sample-level quality flags.

    bits:
      - name: VALID
        bit: 0

      - name: SENSOR_DISCONNECTED
        bit: 1

      - name: SATURATED
        bit: 2

      - name: OVERFLOW
        bit: 3

      - name: TIMING_UNCERTAIN
        bit: 4

      - name: CALIBRATION_REQUIRED
        bit: 5

errors:
  - name: ERROR_INVALID_LENGTH
    value: 0x0001
    severity: error
    description: Payload length is invalid.

  - name: ERROR_UNSUPPORTED_MESSAGE
    value: 0x0002
    severity: error
    description: Message ID is not supported.

  - name: ERROR_INVALID_STATE
    value: 0x0003
    severity: error
    description: Command is not allowed in the current state.

  - name: ERROR_OUT_OF_RANGE
    value: 0x0004
    severity: error
    description: Parameter is outside the allowed range.

  - name: ERROR_UNAUTHORIZED
    value: 0x0005
    severity: error
    description: Current Session has insufficient privilege.

  - name: ERROR_BUSY
    value: 0x0006
    severity: error
    description: Device is busy.

  - name: ERROR_INTERNAL
    value: 0x0007
    severity: critical
    description: Internal execution failure.

  - name: ERROR_VERSION_NOT_SUPPORTED
    value: 0x0008
    severity: error
    description: Protocol or feature version is unsupported.

  - name: ERROR_CAPABILITY_NOT_SUPPORTED
    value: 0x0009
    severity: error
    description: Requested Capability is unavailable.

  - name: ERROR_MANIFEST_INVALID
    value: 0x000a
    severity: error
    description: Firmware Manifest content, encoding, hash, or target compatibility is invalid.
  - name: ERROR_SIGNATURE_INVALID
    value: 0x000b
    severity: critical
    description: Firmware Manifest signature validation failed.
  - name: ERROR_ROLLBACK_PROHIBITED
    value: 0x000c
    severity: critical
    description: Firmware security version violates the anti-rollback policy.
  - name: ERROR_UNSUPPORTED_SECURITY_PROFILE
    value: 0x000d
    severity: error
    description: Requested Handshake Profile is not supported.
  - name: ERROR_SECURITY_DOWNGRADE_REJECTED
    value: 0x000e
    severity: critical
    description: Requested or negotiated security profile violates the minimum approved policy.
  - name: ERROR_HANDSHAKE_PROOF_INVALID
    value: 0x000f
    severity: critical
    description: Handshake proof or canonical transcript validation failed.
  - name: ERROR_COUNTER_EXHAUSTED
    value: 0x0010
    severity: critical
    description: Protected traffic stopped before Record Counter Hard Limit.
capabilities:
  - name: CAP_DEVICE_INFORMATION
    id: 0x0001
    since: V1.0.0
    description: Device identity and version query.

  - name: CAP_DEVICE_CONFIGURATION
    id: 0x0101
    since: V1.0.0
    description: Device configuration support.

  - name: CAP_DEVICE_CONTROL
    id: 0x0102
    since: V1.0.0
    description: Start and stop control support.

  - name: CAP_STATUS_TELEMETRY
    id: 0x0103
    since: V1.0.0
    description: Replaceable summarized status Telemetry support.

    parameters:
      - name: maximum_rate_hz
        type: uint16
        unit: Hz

  - name: CAP_DATA_STREAMING
    id: 0x0104
    since: V1.0.0
    description: Ordered high-rate Streaming support.

    parameters:
      - name: maximum_channels
        type: uint8
        minimum: 1
        maximum: 16

        scope: runtime_effective_profile
      - name: maximum_sample_rate_hz
        type: uint32
        unit: Hz

        scope: runtime_effective_profile
      - name: maximum_samples_per_record
        type: uint16

        minimum: 1
        maximum: 240
        scope: runtime_effective_profile
      - name: maximum_plaintext_message_size_bytes
        type: uint16
        unit: bytes
        minimum: 19
        maximum: 1024
        scope: runtime_effective_profile
        description: Maximum encoded plaintext Stream Message size under the Runtime Effective Profile.
  - name: CAP_DIAGNOSTICS
    id: 0x0105
    since: V1.0.0
    description: Diagnostic and self-test support.

  - name: CAP_FIRMWARE_UPDATE
    id: 0x0201
    since: V1.0.0
    description: Bootloader Firmware Update support.

    parameters:
      - name: maximum_chunk_length
        type: uint16
        unit: bytes
        minimum: 1
        maximum: 1014
        scope: runtime_effective_profile
      - name: maximum_update_plaintext_message_size_bytes
        type: uint16
        unit: bytes
        minimum: 222
        maximum: 1024
        scope: runtime_effective_profile
        description: Maximum encoded plaintext Firmware Update Message size under the Runtime Effective Profile.
sequence_policy:
  default_control:
    field: message_sequence
    width_bits: 32
    scope: per_session
    initial_value: 0
    increment: one
    wrap_policy: modulo
    reset_on:
      - session_start
    duplicate_policy: reject
    out_of_order_policy: reject
    gap_policy: allowed_for_independent_messages

  default_stream:
    field: record_sequence
    width_bits: 32
    scope: per_stream
    initial_value: 0
    increment: one
    wrap_policy: modulo
    reset_on:
      - session_start
      - stream_start
    duplicate_policy: detect_and_drop
    out_of_order_policy: detect_and_report
    gap_policy: detect_and_report

timestamp_policy:
  device_monotonic:
    field: timestamp_us
    source: device_monotonic_clock
    epoch: device_boot
    unit: us
    width_bits: 64
    monotonic: true
    wrap_policy: modulo
    synchronization_required: false

transport_profiles:
  - name: USB_CDC_BASELINE
    transport: usb_cdc
    minimum_mtu: 64
    maximum_mtu: 4096
    expected_minimum_throughput_bps: 100000
    maximum_control_latency_ms: 100
    fragmentation:
      mode: protocol_record_fragmentation
      maximum_fragments_per_record: 87
      maximum_concurrent_reassembly: 1
      reassembly_timeout_ms: 1000

      fragment_header_bytes: 16
      maximum_fragment_payload: 4080
      header_struct: SecuredRecordFragmentHeaderV1
      minimum_data_bearing_mtu: 64
      minimum_fragment_payload: 48
      record_id_policy: unique_per_sender_session_epoch_until_reassembly_timeout
      fragment_index_base: 0
      duplicate_policy: ignore_identical_reject_conflicting_and_abort_reassembly
      out_of_order_policy: accept_within_one_bounded_active_reassembly
      integrity_scope: complete_secured_record_aead_verified_after_reassembly
      fragment_header_integrity: crc16_ccitt_false_accidental_corruption_only
      incomplete_record_behavior: discard_on_timeout_and_count
      conflicting_fragment_behavior: abort_reassembly_disconnect_and_count
      oversized_record_behavior: reject_before_allocation_and_count
      zero_payload_behavior: reject_transport_profile
      runtime_fragment_payload_formula: runtime_mtu_minus_fragment_header_bytes
      required_fragment_count_formula: ceil(original_secured_record_length_div_runtime_fragment_payload)
    maximum_plaintext_message_size: 4096
    protocol_record_header_bytes: 12
    security_header_bytes: 12
    authentication_tag_bytes: 16
    maximum_security_overhead_bytes: 40
    maximum_secured_record_size: 4136
    maximum_transport_reassembly_size: 4136
  - name: CAN_FD_BASELINE
    transport: can_fd
    minimum_mtu: 64
    maximum_mtu: 64
    expected_minimum_throughput_bps: 10000
    maximum_control_latency_ms: 100
    fragmentation:
      mode: protocol_record_fragmentation
      maximum_fragments_per_record: 23
      maximum_concurrent_reassembly: 1
      reassembly_timeout_ms: 500

      fragment_header_bytes: 16
      maximum_fragment_payload: 48
      header_struct: SecuredRecordFragmentHeaderV1
      minimum_data_bearing_mtu: 64
      minimum_fragment_payload: 48
      record_id_policy: unique_per_sender_session_epoch_until_reassembly_timeout
      fragment_index_base: 0
      duplicate_policy: ignore_identical_reject_conflicting_and_abort_reassembly
      out_of_order_policy: accept_within_one_bounded_active_reassembly
      integrity_scope: complete_secured_record_aead_verified_after_reassembly
      fragment_header_integrity: crc16_ccitt_false_accidental_corruption_only
      incomplete_record_behavior: discard_on_timeout_and_count
      conflicting_fragment_behavior: abort_reassembly_disconnect_and_count
      oversized_record_behavior: reject_before_allocation_and_count
      zero_payload_behavior: reject_transport_profile
      runtime_fragment_payload_formula: runtime_mtu_minus_fragment_header_bytes
      required_fragment_count_formula: ceil(original_secured_record_length_div_runtime_fragment_payload)
    maximum_plaintext_message_size: 1024
    protocol_record_header_bytes: 12
    security_header_bytes: 12
    authentication_tag_bytes: 16
    maximum_security_overhead_bytes: 40
    maximum_secured_record_size: 1064
    maximum_transport_reassembly_size: 1064
security_model:
  session_required_for_application_control: true
  session_required_for_application_data: true
  session_required_for_firmware_update: true
  application_and_bootloader_sessions_separate: true

  message_security_policy:
    mode: explicit_per_message
    omitted_security_block_policy: reject
    bidirectional_key_context_policy: explicit_direction_and_environment_mapping
  handshake_profiles:
    - name: APPLICATION_MUTUAL_AUTH_V1
      profile_id: 0x0001
      execution_environment: application
      authentication: mutual
      transcript_hash: sha256
      key_agreement: UNRESOLVED_PROJECT_DECISION
      proof_format: UNRESOLVED_PROJECT_DECISION
      anti_replay_source: nonce_and_handshake_transcript
      derived_key_contexts:
        - application_control_h2d
        - application_control_d2h
        - application_data_h2d
        - application_data_d2h
      kdf: UNRESOLVED_PROJECT_DECISION
      cipher_suite: UNRESOLVED_PROJECT_DECISION
      profile_selection_policy:
        allowed_profile_ids:
          - 0x0001
        preferred_profile_order:
          - 0x0001
        prohibited_profile_ids: []
        reject_unlisted_profile_ids: true
        payload_profile_id_must_equal_profile_id: true
        security_level_comparison_field: security_level
        deprecated_profile_behavior: explicit_reject
        unsupported_profile_behavior: explicit_reject
        silent_fallback_prohibited: true
      canonical_transcript:
        encoding: protocol_wire_format_field_by_field_without_padding
        required_fields:
          - protocol_family
          - protocol_version
          - discovery_id
          - handshake_profile_id
          - execution_environment
          - initiator_role
          - responder_role
          - initiator_identity
          - responder_identity
          - initiator_nonce
          - responder_nonce
          - initiator_ephemeral_public_key
          - responder_ephemeral_public_key
          - negotiated_algorithms
          - session_id
          - derived_key_contexts
        request_struct: ApplicationHandshakeRequestV1
        response_struct: ApplicationHandshakeResponseV1
        assembly: 
          domain_separator_then_request_struct_then_response_struct_without_responder_proof_slot_then_derived_context_registry
        initiator_proof_scope: domain_separator_then_request_struct_without_initiator_proof_slot
        responder_proof_scope: 
          domain_separator_then_complete_request_struct_then_response_struct_without_responder_proof_slot_then_derived_context_registry
        initiator_key_confirmation: first_valid_secured_record_under_new_initiator_key_context
        zero_padding_required: true
      security_level: 100
      deprecated: false
    - name: BOOTLOADER_MUTUAL_AUTH_V1
      profile_id: 0x0002
      execution_environment: bootloader
      authentication: mutual
      transcript_hash: sha256
      key_agreement: UNRESOLVED_PROJECT_DECISION
      proof_format: UNRESOLVED_PROJECT_DECISION
      anti_replay_source: nonce_and_handshake_transcript
      derived_key_contexts:
        - bootloader_update_h2d
        - bootloader_response_d2h
      kdf: UNRESOLVED_PROJECT_DECISION
      cipher_suite: UNRESOLVED_PROJECT_DECISION
      profile_selection_policy:
        allowed_profile_ids:
          - 0x0002
        preferred_profile_order:
          - 0x0002
        prohibited_profile_ids: []
        reject_unlisted_profile_ids: true
        payload_profile_id_must_equal_profile_id: true
        security_level_comparison_field: security_level
        deprecated_profile_behavior: explicit_reject
        unsupported_profile_behavior: explicit_reject
        silent_fallback_prohibited: true
      canonical_transcript:
        encoding: protocol_wire_format_field_by_field_without_padding
        required_fields:
          - protocol_family
          - protocol_version
          - discovery_id
          - handshake_profile_id
          - execution_environment
          - initiator_role
          - responder_role
          - initiator_identity
          - responder_identity
          - initiator_nonce
          - responder_nonce
          - initiator_ephemeral_public_key
          - responder_ephemeral_public_key
          - negotiated_algorithms
          - session_id
          - derived_key_contexts
        request_struct: BootloaderHandshakeRequestV1
        response_struct: BootloaderHandshakeResponseV1
        assembly: 
          domain_separator_then_request_struct_then_response_struct_without_responder_proof_slot_then_derived_context_registry
        initiator_proof_scope: domain_separator_then_request_struct_without_initiator_proof_slot
        responder_proof_scope: 
          domain_separator_then_complete_request_struct_then_response_struct_without_responder_proof_slot_then_derived_context_registry
        initiator_key_confirmation: first_valid_secured_record_under_new_initiator_key_context
        zero_padding_required: true
      security_level: 100
      deprecated: false
  firmware_update_manifest:
    struct: FirmwareManifestV1
    canonical_encoding: protocol_wire_format_field_by_field_without_padding
    hash_algorithm: sha256
    signature_input: domain_separator_then_manifest_hash
    domain_separator: EXAMPLE_DEVICE_FW_MANIFEST_V1
    accepted_signature_algorithms:
      - ECDSA_P256_SHA256
      - ED25519
    signature_profiles:
      - algorithm: ECDSA_P256_SHA256
        signature_primitive: ecdsa_p256
        message_preparation: sha256(domain_separator || manifest_hash)
        wire_encoding: ieee_p1363_fixed_width_r_then_s_big_endian
        exact_signature_length: 64
        low_s_required: true
        der_encoding_prohibited: true
      - algorithm: ED25519
        signature_primitive: ed25519_pure
        message_preparation: domain_separator || manifest_hash
        wire_encoding: rfc8032_64_octet_signature
        exact_signature_length: 64
        canonical_encoding_required: true
  key_contexts:
    - application_control_h2d
    - application_control_d2h
    - application_data_h2d
    - application_data_d2h
    - bootloader_update_h2d
    - bootloader_response_d2h

  failure_policy:
    authentication_failure: disconnect_and_count
    integrity_failure: disconnect_and_count
    replay_detected: reject_disconnect_and_count
    wrong_session_id: reject_and_count
    wrong_key_context: reject_disconnect_and_count
    expired_session: reject_and_disconnect
    execution_environment_mismatch: reject_and_count

    handshake_proof_failure: explicit_reject_disconnect_and_count
    counter_gap: reject_disconnect_and_count
    counter_exhausted: stop_traffic_disconnect_and_require_new_handshake
    rekey_deadline_reached: restrict_ordinary_traffic_until_atomic_rekey_or_disconnect
    manifest_hash_failure: reject_update_abort_and_count
    firmware_signature_failure: reject_update_lock_transaction_and_count
    security_downgrade_attempt: reject_disconnect_and_count
    unauthorized_update_resume: reject_resume_disconnect_and_count
    fragment_header_conflict: abort_reassembly_disconnect_and_count
  discovery_policies:
    - name: PUBLIC_DISCOVERY_V1
      allowed_messages:
        - DISCOVER_NODE_REQUEST
        - DISCOVER_NODE_RESPONSE
      exposure_rationale: Provide only enough ephemeral information to select and bind an approved Handshake Profile.
      permanent_device_identifier_prohibited: true
      ephemeral_discovery_id_length_bytes: 8
      ephemeral_discovery_id_rotation: on_boot_and_at_least_every_60000_ms
      unauthenticated_results_authoritative: false
      post_session_revalidation_required: true
      handshake_transcript_binding_required: true
      rate_limit:
        window_ms: 1000
        maximum_requests_per_window: 4
        burst_capacity: 4
        excess_behavior: drop_and_count
  record_counter_profiles:
    - name: DEFAULT_RECORD_COUNTER_V1
      width_bits: 64
      initial_value: 1
      soft_threshold: 0xffffffff00000000
      rekey_deadline: 0xfffffffff0000000
      hard_limit: 0xfffffffffffffffe
      persistence_policy: session_epoch_only_not_persisted
      reset_conditions:
        - new_session_keys_atomically_activated
      exhaustion_behavior: stop_protected_transmission_disconnect_and_require_new_handshake
      receive_policy:
        out_of_order_window: 0
        maximum_forward_gap: 1024
        gap_exceeded_behavior: reject_disconnect_and_count
      atomic_rekey:
        required: true
        new_epoch_activation: two_phase_confirmed_cutover
        old_epoch_acceptance: bounded_until_cutover_confirmation
        late_old_epoch_behavior: reject_and_count
        failure_behavior: disconnect_and_require_new_handshake
  key_context_policies:
    - key_context: application_control_h2d
      record_counter_profile: DEFAULT_RECORD_COUNTER_V1
    - key_context: application_control_d2h
      record_counter_profile: DEFAULT_RECORD_COUNTER_V1
    - key_context: application_data_h2d
      record_counter_profile: DEFAULT_RECORD_COUNTER_V1
    - key_context: application_data_d2h
      record_counter_profile: DEFAULT_RECORD_COUNTER_V1
    - key_context: bootloader_update_h2d
      record_counter_profile: DEFAULT_RECORD_COUNTER_V1
    - key_context: bootloader_response_d2h
      record_counter_profile: DEFAULT_RECORD_COUNTER_V1
  firmware_update_transaction_binding:
    mode: device_issued_resume_authorization_token
    struct: UpdateResumeAuthorizationV1
    domain_separator: EXAMPLE_DEVICE_UPDATE_RESUME_AUTH_V1
    mac_algorithm: hmac_sha256
    token_key_scope: bootloader_persistent_update_authorization_key
    token_key_persistence: survives_reconnect_rekey_and_restart_until_transaction_terminal_state
    authorized_host_identity_source: authenticated_bootloader_session_identity
    device_identity_source: authenticated_device_identity
    mac_input: domain_separator_then_all_struct_fields_before_token_mac
    new_transaction_absent_encoding: resume_authorization_present_false_and_all_zero_struct
    resume_validation_required: true
    resume_generation_must_not_decrease: true
    reissue_on_every_accepted_begin_or_resume: true
    invalid_token_behavior: reject_resume_disconnect_and_count
    invalidation_conditions:
      - successful_activation
      - explicit_abort
      - manifest_change
      - host_authorization_revocation
      - anti_rollback_rejection
      - terminal_update_failure
reserved_message_ids:
  - range_start: 0x00F0
    range_end: 0x00FF
    reason: Future Framework extension.

  - range_start: 0xFF00
    range_end: 0xFFFF
    reason: Reserved by the Protocol Family.

reserved_capability_ids:
  - range_start: 0xF000
    range_end: 0xFFFF
    reason: Future extension and experimental use.

messages:
  # Framework / System Messages: 0x0000-0x00FF

  - name: DISCOVER_NODE_REQUEST
    id: 0x0001
    namespace: framework
    service: DEVICE_MANAGEMENT
    category: command_request
    direction: coordinator_to_node
    execution_environment: any
    description: Request bounded ephemeral pre-Session Discovery information.

    length_policy: exact
    unknown_trailing_policy: reject
    timeout_ms: 1000

    retry_policy:
      mode: bounded
      maximum_attempts: 2
      retry_on:
        - timeout
      backoff_ms: 100

    idempotency: idempotent

    security:
      authentication_required: false
      confidentiality_required: false
      integrity_required: false
      anti_replay_required: false
      allowed_before_session: true
      privilege: public_discovery
    payload:
      fields: []
    discovery:
      policy: PUBLIC_DISCOVERY_V1
      unauthenticated_result_authoritative: false

  - name: DISCOVER_NODE_RESPONSE
    id: 0x0002
    namespace: framework
    service: DEVICE_MANAGEMENT
    category: command_response
    direction: node_to_coordinator
    response_to: DISCOVER_NODE_REQUEST
    execution_environment: any
    description: Bounded ephemeral Discovery information; not authoritative Product identity or Capability state.

    length_policy: minimum
    minimum_length: 16
    unknown_trailing_policy: reject

    security:
      authentication_required: false
      confidentiality_required: false
      integrity_required: false
      anti_replay_required: false
      allowed_before_session: true
      privilege: public_discovery
    payload:
      fields:
        - name: result
          type: enum
          enum: CommandResult
          description: Discovery result.
        - name: discovery_id
          type: uint8
          description: Ephemeral non-identity value bound into the Handshake transcript.
          array:
            length: 8
        - name: execution_environment
          type: enum
          enum: ExecutionEnvironment
          description: Current Execution Environment hint; authenticated revalidation is required.
        - name: protocol_family_id
          type: uint32
          description: Protocol family hint used only to select a compatible Handshake path.
        - name: handshake_profile_count
          type: uint8
          minimum: 1
          maximum: 4
          description: Number of advertised Handshake Profile identifiers.
        - name: handshake_profile_ids
          type: uint16
          description: Advertised Handshake Profile identifiers; untrusted until transcript verification.
          array:
            length_from: handshake_profile_count
            maximum_length: 4
    maximum_plaintext_message_size: 24
    discovery:
      policy: PUBLIC_DISCOVERY_V1
      unauthenticated_result_authoritative: false
      post_session_revalidation_required: true
      handshake_transcript_binding_required: true
  - name: GET_CAPABILITIES_REQUEST
    id: 0x0003
    namespace: framework
    service: DEVICE_MANAGEMENT
    category: command_request
    direction: coordinator_to_node
    execution_environment: any
    description: Request authoritative Capability identifiers after Secure Session establishment.

    length_policy: exact
    unknown_trailing_policy: reject
    timeout_ms: 1000

    retry_policy:
      mode: bounded
      maximum_attempts: 2
      retry_on:
        - timeout
      backoff_ms: 100

    idempotency: idempotent

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      allowed_before_session: false
      privilege: authenticated_read
      key_context_by_environment:
        application: application_control_h2d
        bootloader: bootloader_update_h2d
    payload:
      fields: []

  - name: GET_CAPABILITIES_RESPONSE
    id: 0x0004
    namespace: framework
    service: DEVICE_MANAGEMENT
    category: command_response
    direction: node_to_coordinator
    response_to: GET_CAPABILITIES_REQUEST
    execution_environment: any
    description: Authoritative Capability identifiers protected by the active Secure Session.

    length_policy: minimum
    minimum_length: 3
    unknown_trailing_policy: reject

    payload:
      fields:
        - name: result
          type: enum
          enum: CommandResult
          description: Request execution result.

        - name: capability_count
          type: uint8
          minimum: 0
          maximum: 64
          description: Number of returned Capability identifiers.

        - name: capability_ids
          type: uint16
          description: Supported Capability identifiers.
          array:
            length_from: capability_count
            maximum_length: 64

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      allowed_before_session: false
      privilege: authenticated_read
      key_context_by_environment:
        application: application_control_d2h
        bootloader: bootloader_response_d2h
  - name: GET_DEVICE_STATUS_REQUEST
    id: 0x0005
    namespace: framework
    service: DEVICE_MANAGEMENT
    category: command_request
    direction: coordinator_to_node
    execution_environment: any
    description: Request current Device state and health.

    length_policy: exact
    unknown_trailing_policy: reject
    timeout_ms: 1000

    retry_policy:
      mode: bounded
      maximum_attempts: 2
      retry_on:
        - timeout
      backoff_ms: 100

    idempotency: idempotent

    payload:
      fields: []
    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      allowed_before_session: false
      privilege: authenticated_read
      key_context_by_environment:
        application: application_control_h2d
        bootloader: bootloader_update_h2d

  - name: GET_DEVICE_STATUS_RESPONSE
    id: 0x0006
    namespace: framework
    service: DEVICE_MANAGEMENT
    category: command_response
    direction: node_to_coordinator
    response_to: GET_DEVICE_STATUS_REQUEST
    execution_environment: any
    description: Current operation state, health, and status flags.

    length_policy: exact
    unknown_trailing_policy: reject

    payload:
      fields:
        - name: result
          type: enum
          enum: CommandResult
          description: Request execution result.

        - name: operation_state
          type: enum
          enum: DeviceOperationState
          description: Current operation state.

        - name: health
          type: enum
          enum: DeviceHealth
          description: Current Device health.

        - name: status_flags
          type: bitset
          bitset: DeviceStatusFlags
          description: Current Device status flags.

        - name: timestamp_us
          type: alias
          alias: DeviceTimestampUs
          description: Device timestamp at status capture.

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      allowed_before_session: false
      privilege: authenticated_read
      key_context_by_environment:
        application: application_control_d2h
        bootloader: bootloader_response_d2h
  - name: HEARTBEAT
    id: 0x0007
    namespace: framework
    service: SESSION_MANAGEMENT
    category: heartbeat
    direction: bidirectional
    execution_environment: any
    description: Link and Session liveness heartbeat.

    length_policy: exact
    unknown_trailing_policy: reject

    rate:
      nominal_hz: 1
      maximum_hz: 10

    payload:
      fields:
        - name: sequence
          type: uint32
          description: Heartbeat sequence number.

        - name: timestamp_us
          type: alias
          alias: PeerMonotonicTimestampUs
          description: Sender-local monotonic timestamp; the epoch is local to the sending peer.

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      allowed_before_session: false
      privilege: session_liveness
      key_context_by_direction_and_environment:
        coordinator_to_node:
          application: application_control_h2d
          bootloader: bootloader_update_h2d
        node_to_coordinator:
          application: application_control_d2h
          bootloader: bootloader_response_d2h
    maximum_plaintext_message_size: 12
  - name: ERROR_RESPONSE
    id: 0x0008
    namespace: framework
    service: SESSION_MANAGEMENT
    category: command_response
    direction: bidirectional
    execution_environment: any
    description: Common Protocol error response.

    length_policy: extensible
    minimum_length: 8
    unknown_trailing_policy: ignore

    payload:
      fields:
        - name: request_message_id
          type: uint16
          description: Offending Request Message identifier.

        - name: request_sequence
          type: uint32
          description: Offending Request sequence.

        - name: error_code
          type: uint16
          description: Common Protocol error code.

        - name: detail_code
          type: uint16
          required: false
          since: V1.1.0
          default_when_absent: 0
          description: Service-specific detail code.

  # Application Command / Response Messages: 0x0100-0x0FFF

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      allowed_before_session: false
      privilege: protocol_error_reporting
      key_context_by_direction_and_environment:
        coordinator_to_node:
          application: application_control_h2d
          bootloader: bootloader_update_h2d
        node_to_coordinator:
          application: application_control_d2h
          bootloader: bootloader_response_d2h
  - name: APPLICATION_HANDSHAKE_REQUEST
    id: 0x0009
    namespace: framework
    service: SESSION_MANAGEMENT
    category: handshake
    direction: coordinator_to_node
    execution_environment: application
    description: Establish the Application Secure Session using the declared Handshake Profile.
    length_policy: exact
    unknown_trailing_policy: reject
    timeout_ms: 3000
    retry_policy:
      mode: bounded
      maximum_attempts: 2
      retry_on:
        - timeout
      backoff_ms: 250
    idempotency: idempotent_with_operation_id
    security:
      authentication_required: true
      authentication_source: handshake_profile
      confidentiality_required: false
      integrity_required: true
      integrity_source: handshake_profile
      anti_replay_required: true
      anti_replay_source: nonce_and_handshake_transcript
      allowed_before_session: true
      privilege: session_establishment
      handshake_profile: APPLICATION_MUTUAL_AUTH_V1
    payload:
      fields:
        - name: handshake
          type: struct
          struct: ApplicationHandshakeRequestV1
          description: Concrete canonical Handshake wire payload.
    profile_binding:
      payload_field: handshake.handshake_profile_id
      handshake_profile: APPLICATION_MUTUAL_AUTH_V1
      equality_required: true
      mismatch_behavior: explicit_reject_no_fallback
      transcript_binding_required: true
    maximum_plaintext_message_size: 352
  - name: APPLICATION_HANDSHAKE_RESPONSE
    id: 0x000a
    namespace: framework
    service: SESSION_MANAGEMENT
    category: handshake
    direction: node_to_coordinator
    response_to: APPLICATION_HANDSHAKE_REQUEST
    execution_environment: application
    description: Establish the Application Secure Session using the declared Handshake Profile.
    length_policy: exact
    unknown_trailing_policy: reject
    timeout_ms: 3000
    retry_policy:
      mode: bounded
      maximum_attempts: 2
      retry_on:
        - timeout
      backoff_ms: 250
    idempotency: idempotent_with_operation_id
    security:
      authentication_required: true
      authentication_source: handshake_profile
      confidentiality_required: false
      integrity_required: true
      integrity_source: handshake_profile
      anti_replay_required: true
      anti_replay_source: nonce_and_handshake_transcript
      allowed_before_session: true
      privilege: session_establishment
      handshake_profile: APPLICATION_MUTUAL_AUTH_V1
    payload:
      fields:
        - name: handshake
          type: struct
          struct: ApplicationHandshakeResponseV1
          description: Concrete canonical Handshake wire payload.
    profile_binding:
      payload_field: handshake.handshake_profile_id
      handshake_profile: APPLICATION_MUTUAL_AUTH_V1
      equality_required: true
      mismatch_behavior: explicit_reject_no_fallback
      transcript_binding_required: true
    maximum_plaintext_message_size: 392
  - name: BOOTLOADER_HANDSHAKE_REQUEST
    id: 0x000b
    namespace: framework
    service: SESSION_MANAGEMENT
    category: handshake
    direction: coordinator_to_node
    execution_environment: bootloader
    description: Establish the Bootloader Secure Session using the declared Handshake Profile.
    length_policy: exact
    unknown_trailing_policy: reject
    timeout_ms: 3000
    retry_policy:
      mode: bounded
      maximum_attempts: 2
      retry_on:
        - timeout
      backoff_ms: 250
    idempotency: idempotent_with_operation_id
    security:
      authentication_required: true
      authentication_source: handshake_profile
      confidentiality_required: false
      integrity_required: true
      integrity_source: handshake_profile
      anti_replay_required: true
      anti_replay_source: nonce_and_handshake_transcript
      allowed_before_session: true
      privilege: session_establishment
      handshake_profile: BOOTLOADER_MUTUAL_AUTH_V1
    payload:
      fields:
        - name: handshake
          type: struct
          struct: BootloaderHandshakeRequestV1
          description: Concrete canonical Handshake wire payload.
    profile_binding:
      payload_field: handshake.handshake_profile_id
      handshake_profile: BOOTLOADER_MUTUAL_AUTH_V1
      equality_required: true
      mismatch_behavior: explicit_reject_no_fallback
      transcript_binding_required: true
    maximum_plaintext_message_size: 352
  - name: BOOTLOADER_HANDSHAKE_RESPONSE
    id: 0x000c
    namespace: framework
    service: SESSION_MANAGEMENT
    category: handshake
    direction: node_to_coordinator
    response_to: BOOTLOADER_HANDSHAKE_REQUEST
    execution_environment: bootloader
    description: Establish the Bootloader Secure Session using the declared Handshake Profile.
    length_policy: exact
    unknown_trailing_policy: reject
    timeout_ms: 3000
    retry_policy:
      mode: bounded
      maximum_attempts: 2
      retry_on:
        - timeout
      backoff_ms: 250
    idempotency: idempotent_with_operation_id
    security:
      authentication_required: true
      authentication_source: handshake_profile
      confidentiality_required: false
      integrity_required: true
      integrity_source: handshake_profile
      anti_replay_required: true
      anti_replay_source: nonce_and_handshake_transcript
      allowed_before_session: true
      privilege: session_establishment
      handshake_profile: BOOTLOADER_MUTUAL_AUTH_V1
    payload:
      fields:
        - name: handshake
          type: struct
          struct: BootloaderHandshakeResponseV1
          description: Concrete canonical Handshake wire payload.
    profile_binding:
      payload_field: handshake.handshake_profile_id
      handshake_profile: BOOTLOADER_MUTUAL_AUTH_V1
      equality_required: true
      mismatch_behavior: explicit_reject_no_fallback
      transcript_binding_required: true
    maximum_plaintext_message_size: 392
  - name: GET_AUTHENTICATED_DEVICE_INFO_REQUEST
    id: 0x000d
    namespace: framework
    service: DEVICE_MANAGEMENT
    category: command_request
    direction: coordinator_to_node
    execution_environment: any
    description: Request authoritative Device identity and version information after Secure Session establishment.
    length_policy: exact
    unknown_trailing_policy: reject
    timeout_ms: 1000
    retry_policy:
      mode: bounded
      maximum_attempts: 2
      retry_on:
        - timeout
      backoff_ms: 100
    idempotency: idempotent
    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      allowed_before_session: false
      privilege: authenticated_read
      key_context_by_environment:
        application: application_control_h2d
        bootloader: bootloader_update_h2d
    payload:
      fields: []
  - name: GET_AUTHENTICATED_DEVICE_INFO_RESPONSE
    id: 0x000e
    namespace: framework
    service: DEVICE_MANAGEMENT
    category: command_response
    direction: node_to_coordinator
    response_to: GET_AUTHENTICATED_DEVICE_INFO_REQUEST
    execution_environment: any
    description: Authoritative Device identity and version information protected by the active Secure Session.
    length_policy: extensible
    minimum_length: 41
    unknown_trailing_policy: ignore
    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      allowed_before_session: false
      privilege: authenticated_read
      key_context_by_environment:
        application: application_control_d2h
        bootloader: bootloader_response_d2h
    payload:
      fields:
        - name: result
          type: enum
          enum: CommandResult
          description: Request execution result.
        - name: device_model
          type: uint16
          description: Product model identifier.
        - name: hardware_revision
          type: uint16
          description: Hardware revision identifier.
        - name: firmware_version
          type: struct
          struct: SoftwareVersion
          description: Application Firmware version.
        - name: bootloader_version
          type: struct
          struct: SoftwareVersion
          description: Bootloader version.
        - name: protocol_version
          type: struct
          struct: ProtocolVersion
          description: Authenticated active Protocol version.
        - name: execution_environment
          type: enum
          enum: ExecutionEnvironment
          description: Authenticated current Execution Environment.
        - name: device_uuid
          type: uint8
          description: Permanent Device unique identifier exposed only after authentication.
          array:
            length: 16
  - name: GET_CONFIGURATION_REQUEST
    id: 0x0101
    namespace: application
    service: DEVICE_CONFIGURATION
    category: command_request
    direction: coordinator_to_node
    execution_environment: application
    description: Request current Product configuration.

    length_policy: exact
    unknown_trailing_policy: reject
    timeout_ms: 1000

    retry_policy:
      mode: bounded
      maximum_attempts: 2
      retry_on:
        - timeout
      backoff_ms: 100

    idempotency: idempotent

    allowed_states:
      - READY
      - CONFIGURED
      - RUNNING

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: authenticated_read
      key_context: application_control_h2d

    payload:
      fields: []

  - name: GET_CONFIGURATION_RESPONSE
    id: 0x0102
    namespace: application
    service: DEVICE_CONFIGURATION
    category: command_response
    direction: node_to_coordinator
    response_to: GET_CONFIGURATION_REQUEST
    execution_environment: application
    description: Current accepted Product configuration.

    length_policy: extensible
    minimum_length: 6
    unknown_trailing_policy: ignore

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: authenticated_read
      key_context: application_control_d2h

    payload:
      fields:
        - name: result
          type: enum
          enum: CommandResult
          description: Request execution result.

        - name: sample_rate_hz
          type: uint16
          unit: Hz
          minimum: 1
          maximum: 100000
          description: Accepted sample rate per channel.

        - name: channel_count
          type: uint8
          minimum: 1
          maximum: 32
          description: Accepted enabled channel count.

        - name: samples_per_record
          type: uint8
          minimum: 1
          maximum: 128
          description: Accepted samples per Stream record.

  - name: SET_CONFIGURATION_REQUEST
    id: 0x0103
    namespace: application
    service: DEVICE_CONFIGURATION
    category: command_request
    direction: coordinator_to_node
    execution_environment: application
    description: Request a new Product configuration.

    length_policy: exact
    unknown_trailing_policy: reject
    timeout_ms: 1000

    retry_policy:
      mode: bounded
      maximum_attempts: 2
      retry_on:
        - timeout
      backoff_ms: 100

    idempotency: idempotent

    allowed_states:
      - READY
      - CONFIGURED

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: configuration
      key_context: application_control_h2d

    payload:
      fields:
        - name: sample_rate_hz
          type: uint16
          unit: Hz
          minimum: 1
          maximum: 100000
          description: Requested sample rate per channel.

        - name: channel_count
          type: uint8
          minimum: 1
          maximum: 32
          description: Requested enabled channel count.

        - name: samples_per_record
          type: uint8
          minimum: 1
          maximum: 128
          description: Requested samples per Stream record.

  - name: SET_CONFIGURATION_RESPONSE
    id: 0x0104
    namespace: application
    service: DEVICE_CONFIGURATION
    category: command_response
    direction: node_to_coordinator
    response_to: SET_CONFIGURATION_REQUEST
    execution_environment: application
    description: Configuration result and accepted values.

    length_policy: exact
    unknown_trailing_policy: reject

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: configuration
      key_context: application_control_d2h

    payload:
      fields:
        - name: result
          type: enum
          enum: CommandResult
          description: Request execution result.

        - name: accepted_sample_rate_hz
          type: uint16
          unit: Hz
          description: Actual accepted sample rate.

        - name: accepted_channel_count
          type: uint8
          description: Actual accepted enabled channel count.

        - name: accepted_samples_per_record
          type: uint8
          description: Actual accepted samples per Stream record.

  - name: START_OPERATION_REQUEST
    id: 0x0111
    namespace: application
    service: DEVICE_CONTROL
    category: command_request
    direction: coordinator_to_node
    execution_environment: application
    description: Start the primary Product operation.

    length_policy: exact
    unknown_trailing_policy: reject
    timeout_ms: 1000

    retry_policy:
      mode: none

    idempotency: idempotent_with_operation_id

    allowed_states:
      - READY
      - CONFIGURED

    safety:
      classification: important
      stale_command_policy: reject
      maximum_command_age_ms: 1000
      duplicate_policy: return_previous_result

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: control
      key_context: application_control_h2d

    payload:
      fields:
        - name: operation_id
          type: alias
          alias: OperationId
          description: Unique start-operation identifier.

  - name: START_OPERATION_RESPONSE
    id: 0x0112
    namespace: application
    service: DEVICE_CONTROL
    category: command_response
    direction: node_to_coordinator
    response_to: START_OPERATION_REQUEST
    execution_environment: application
    description: Start-operation result.

    length_policy: exact
    unknown_trailing_policy: reject

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: control
      key_context: application_control_d2h

    payload:
      fields:
        - name: result
          type: enum
          enum: CommandResult
          description: Request execution result.

        - name: operation_id
          type: alias
          alias: OperationId
          description: Accepted operation identifier.

        - name: stream_id
          type: uint8
          description: Assigned Stream identifier.

  - name: STOP_OPERATION_REQUEST
    id: 0x0113
    namespace: application
    service: DEVICE_CONTROL
    category: command_request
    direction: coordinator_to_node
    execution_environment: application
    description: Stop the active Product operation.

    length_policy: exact
    unknown_trailing_policy: reject
    timeout_ms: 1000

    retry_policy:
      mode: bounded
      maximum_attempts: 2
      retry_on:
        - timeout
      backoff_ms: 100

    idempotency: idempotent

    allowed_states:
      - RUNNING
      - STOPPING

    safety:
      classification: important
      stale_command_policy: reject
      maximum_command_age_ms: 1000
      duplicate_policy: return_previous_result

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: control
      key_context: application_control_h2d

    payload:
      fields:
        - name: operation_id
          type: alias
          alias: OperationId
          description: Operation identifier to stop.

  - name: STOP_OPERATION_RESPONSE
    id: 0x0114
    namespace: application
    service: DEVICE_CONTROL
    category: command_response
    direction: node_to_coordinator
    response_to: STOP_OPERATION_REQUEST
    execution_environment: application
    description: Stop-operation result.

    length_policy: exact
    unknown_trailing_policy: reject

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: control
      key_context: application_control_d2h

    payload:
      fields:
        - name: result
          type: enum
          enum: CommandResult
          description: Request execution result.

        - name: operation_id
          type: alias
          alias: OperationId
          description: Stopped operation identifier.

  # Event / Alarm / Fault Messages: 0x1000-0x12FF

  - name: OPERATION_STARTED_EVENT
    id: 0x1001
    namespace: application
    service: DEVICE_CONTROL
    category: event
    direction: node_to_coordinator
    execution_environment: application
    description: Product operation entered the RUNNING state.

    severity: info
    latching: false
    acknowledge_required: false

    length_policy: exact
    unknown_trailing_policy: reject

    payload:
      fields:
        - name: operation_id
          type: alias
          alias: OperationId
          description: Started operation identifier.

        - name: timestamp_us
          type: alias
          alias: DeviceTimestampUs
          description: State-transition timestamp.

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      allowed_before_session: false
      privilege: authenticated_read
      key_context: application_control_d2h
  - name: DATA_QUALITY_ALARM
    id: 0x1101
    namespace: application
    service: DATA_ACQUISITION
    category: alarm
    direction: node_to_coordinator
    execution_environment: application
    description: Data quality is below the defined acceptable condition.

    severity: warning
    latching: false
    acknowledge_required: false
    clear_condition: quality_restored

    length_policy: exact
    unknown_trailing_policy: reject

    payload:
      fields:
        - name: channel_id
          type: uint8
          description: Affected channel.

        - name: quality_flags
          type: bitset
          bitset: SampleQualityFlags
          description: Active quality conditions.

        - name: timestamp_us
          type: alias
          alias: DeviceTimestampUs
          description: Alarm occurrence timestamp.

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      allowed_before_session: false
      privilege: authenticated_read
      key_context: application_data_d2h
  - name: DEVICE_HARDWARE_FAULT
    id: 0x1201
    namespace: application
    service: DIAGNOSTICS
    category: fault
    direction: node_to_coordinator
    execution_environment: application
    description: Product hardware Fault requiring controlled recovery.

    severity: critical
    latching: true
    acknowledge_required: true
    reset_policy: explicit_command_after_condition_clear

    length_policy: extensible
    minimum_length: 16
    unknown_trailing_policy: ignore

    payload:
      fields:
        - name: fault_instance_id
          type: uint32
          description: Unique Fault occurrence identifier.

        - name: source_id
          type: uint16
          description: Fault source identifier.

        - name: error_code
          type: uint16
          description: Associated Error Registry value.

        - name: timestamp_us
          type: alias
          alias: DeviceTimestampUs
          description: Fault occurrence timestamp.

        - name: detail_code
          type: uint32
          required: false
          since: V1.1.0
          default_when_absent: 0
          description: Optional bounded diagnostic detail.

  # Telemetry / Streaming Messages: 0x2000-0x2FFF

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      allowed_before_session: false
      privilege: authenticated_read
      key_context: application_control_d2h
  - name: DEVICE_STATUS_TELEMETRY
    id: 0x2001
    namespace: application
    service: DATA_ACQUISITION
    category: telemetry
    direction: node_to_coordinator
    execution_environment: application
    description: Periodic complete snapshot of current Device operating status.

    length_policy: exact
    unknown_trailing_policy: reject

    nominal_rate_hz:
      numerator: 2
      denominator: 1

    maximum_rate_hz:
      numerator: 10
      denominator: 1

    replacement_policy: latest_value_only
    loss_policy: latest_value_only
    priority: status
    timestamp_policy:
      field: sample_timestamp_us
      epoch: device_boot
      unit: us
      width_bits: 64
      monotonic: true
      meaning: state_snapshot_time

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: authenticated_read
      key_context: application_data_d2h

    payload:
      fields:
        - name: sample_timestamp_us
          type: alias
          alias: DeviceTimestampUs
          description: Time when the state snapshot was captured.

        - name: operation_state
          type: enum
          enum: DeviceOperationState
          description: Current operation state.

        - name: health
          type: enum
          enum: DeviceHealth
          description: Current summarized Device health.

        - name: status_flags
          type: bitset
          bitset: DeviceStatusFlags
          description: Current status flags.

        - name: active_operation_id
          type: alias
          alias: OperationId
          description: Current operation identifier; zero means no active operation.

    delivery_queue_policy: single_pending
    maximum_plaintext_message_size: 32
  - name: SAMPLE_STREAM_RECORD
    id: 0x2101
    namespace: application
    service: DATA_ACQUISITION
    category: stream
    direction: node_to_coordinator
    execution_environment: application
    description: Ordered timestamped acquisition sample record.

    length_policy: minimum
    minimum_length: 19
    unknown_trailing_policy: reject

    priority: data
    loss_policy: detectable_drop_allowed

    sequence_policy:
      field: record_sequence
      scope: per_stream
      reset_on:
        - session_start
        - stream_start
      duplicate_policy: detect_and_drop
      out_of_order_policy: detect_and_report
      gap_policy: detect_and_report

    timestamp_policy:
      field: first_sample_timestamp_us
      epoch: device_boot
      unit: us
      width_bits: 64
      monotonic: true
      meaning: first_sample_in_record

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: authenticated_read
      key_context: application_data_d2h

    payload:
      fields:
        - name: stream_id
          type: uint8
          description: Stream identifier.

        - name: record_sequence
          type: uint32
          description: Sequence number within the Stream.

        - name: first_sample_timestamp_us
          type: alias
          alias: DeviceTimestampUs
          description: Timestamp of the first sample in this record.

        - name: channel_count
          type: uint8
          minimum: 1
          maximum: 16
          description: Number of enabled channels represented by each sample group.

        - name: samples_per_channel
          type: uint8
          minimum: 1
          maximum: 15
          description: Number of samples for each channel in this record.

        - name: sample_count
          type: uint16
          minimum: 1
          maximum: 240
          description: >
            Total number of encoded sample values. This value shall equal
            channel_count multiplied by samples_per_channel.

        - name: quality_flags
          type: bitset
          bitset: SampleQualityFlags
          description: Record-level quality flags.

        - name: samples
          type: int32
          unit: application_defined
          description: >
            Interleaved signed sample values. Before reading this array, the decoder shall
            validate overflow-safe multiplication, verify that sample_count equals
            channel_count multiplied by samples_per_channel, and verify the remaining
            Payload length and destination capacity.
          array:
            length_from: sample_count
            maximum_length: 240

  # Firmware Update / Bootloader Messages: 0x5000-0x5FFF

    maximum_plaintext_message_size: 1024
  - name: BEGIN_UPDATE_REQUEST
    id: 0x5001
    namespace: bootloader
    service: FIRMWARE_UPDATE
    category: firmware_update
    direction: coordinator_to_node
    execution_environment: bootloader
    description: Transfer the signed canonical Firmware Manifest and either create a new Update Transaction or resume 
      one using a Device-issued authorization token.

    length_policy: exact
    unknown_trailing_policy: reject
    timeout_ms: 3000

    retry_policy:
      mode: bounded
      maximum_attempts: 2
      retry_on:
        - timeout
      backoff_ms: 500

    idempotency: idempotent_with_operation_id

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: firmware_update
      key_context: bootloader_update_h2d

    payload:
      fields:
        - name: update_transaction_id
          type: alias
          alias: TransactionId
          description: Update Transaction identifier.
        - name: manifest
          type: struct
          struct: FirmwareManifestV1
          description: Canonical Manifest fields used for target, version, hash, and anti-rollback validation.
        - name: manifest_hash
          type: uint8
          description: SHA-256 hash recomputed over the canonical encoded manifest field.
          array:
            length: 32
        - name: manifest_signature
          type: uint8
          description: Exact 64-byte signature encoded according to the Manifest signature profile.
          array:
            length: 64
        - name: resume_authorization_present
          type: boolean
          description: False for a new transaction; true when attaching this Session to persisted Update state.
        - name: resume_authorization
          type: struct
          struct: UpdateResumeAuthorizationV1
          description: All zero when absent; otherwise a valid Device-issued authorization token.
    maximum_plaintext_message_size: 345
    resume_binding:
      new_transaction_policy: present_false_and_all_zero_token
      resume_policy: present_true_and_validate_complete_token_before_offset_or_flash_access
      session_identity_must_match_authorized_host_identity: true
      transaction_manifest_and_security_version_must_match: true
  - name: BEGIN_UPDATE_RESPONSE
    id: 0x5002
    namespace: bootloader
    service: FIRMWARE_UPDATE
    category: firmware_update
    direction: node_to_coordinator
    response_to: BEGIN_UPDATE_REQUEST
    execution_environment: bootloader
    description: Return Update acceptance, resume state, and a fresh authorization token bound to the authenticated Host
      and persisted transaction.

    length_policy: exact
    unknown_trailing_policy: reject

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: firmware_update
      key_context: bootloader_response_d2h

    payload:
      fields:
        - name: result
          type: enum
          enum: CommandResult
          description: Request execution result.

        - name: update_transaction_id
          type: alias
          alias: TransactionId
          description: Accepted Update Transaction identifier.

        - name: confirmed_offset
          type: uint32
          description: First byte offset not yet committed.

        - name: maximum_chunk_length
          type: uint16
          description: Maximum accepted chunk-data length for the Runtime Effective Profile.

          minimum: 1
          maximum: 1014
        - name: resume_authorization
          type: struct
          struct: UpdateResumeAuthorizationV1
          description: Fresh Device-issued token for any later reconnect or Rekey resume.
    maximum_plaintext_message_size: 168
  - name: WRITE_UPDATE_CHUNK_REQUEST
    id: 0x5003
    namespace: bootloader
    service: FIRMWARE_UPDATE
    category: firmware_update
    direction: coordinator_to_node
    execution_environment: bootloader
    description: Transfer one bounded Firmware image chunk.

    length_policy: minimum
    minimum_length: 10
    unknown_trailing_policy: reject
    timeout_ms: 3000

    retry_policy:
      mode: bounded
      maximum_attempts: 3
      retry_on:
        - timeout
      backoff_ms: 250

    idempotency: idempotent_with_operation_id

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: firmware_update
      key_context: bootloader_update_h2d

    payload:
      fields:
        - name: update_transaction_id
          type: alias
          alias: TransactionId
          description: Update Transaction identifier.

        - name: offset
          type: uint32
          description: Image byte offset of this chunk.

        - name: chunk_length
          type: uint16
          minimum: 1
          maximum: 1014
          description: Number of bytes in chunk_data.

        - name: chunk_data
          type: uint8
          description: Firmware image bytes.
          array:
            length_from: chunk_length
            maximum_length: 1014

    maximum_plaintext_message_size: 1024
  - name: WRITE_UPDATE_CHUNK_RESPONSE
    id: 0x5004
    namespace: bootloader
    service: FIRMWARE_UPDATE
    category: firmware_update
    direction: node_to_coordinator
    response_to: WRITE_UPDATE_CHUNK_REQUEST
    execution_environment: bootloader
    description: Chunk acceptance and confirmed update offset.

    length_policy: exact
    unknown_trailing_policy: reject

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: firmware_update
      key_context: bootloader_response_d2h

    payload:
      fields:
        - name: result
          type: enum
          enum: CommandResult
          description: Request execution result.

        - name: update_transaction_id
          type: alias
          alias: TransactionId
          description: Update Transaction identifier.

        - name: confirmed_offset
          type: uint32
          description: First byte offset not yet committed.

  - name: FINALIZE_UPDATE_REQUEST
    id: 0x5005
    namespace: bootloader
    service: FIRMWARE_UPDATE
    category: firmware_update
    direction: coordinator_to_node
    execution_environment: bootloader
    description: Request complete-image verification and activation preparation.

    length_policy: exact
    unknown_trailing_policy: reject
    timeout_ms: 30000

    retry_policy:
      mode: none

    idempotency: idempotent_with_operation_id

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: firmware_update
      key_context: bootloader_update_h2d

    payload:
      fields:
        - name: update_transaction_id
          type: alias
          alias: TransactionId
          description: Update Transaction identifier.

  - name: FINALIZE_UPDATE_RESPONSE
    id: 0x5006
    namespace: bootloader
    service: FIRMWARE_UPDATE
    category: firmware_update
    direction: node_to_coordinator
    response_to: FINALIZE_UPDATE_REQUEST
    execution_environment: bootloader
    description: Full-image verification and activation-preparation result.

    length_policy: exact
    unknown_trailing_policy: reject

    security:
      authentication_required: true
      confidentiality_required: false
      integrity_required: true
      anti_replay_required: true
      privilege: firmware_update
      key_context: bootloader_response_d2h

    payload:
      fields:
        - name: result
          type: enum
          enum: CommandResult
          description: Request execution result.

        - name: update_transaction_id
          type: alias
          alias: TransactionId
          description: Update Transaction identifier.

        - name: verified_image_size
          type: uint32
          description: Verified complete image size.

compatibility:
  major_version_policy: reject_incompatible_major
  minor_version_policy: negotiate_capabilities
  patch_version_policy: accept_compatible_patch

  unknown_message_policy:
    command_request: return_unsupported_message
    command_response: record_and_ignore
    event: record_raw_and_continue
    alarm: record_raw_and_continue
    fault: record_raw_and_enter_reviewed_policy
    telemetry: record_raw_and_continue
    stream: reject_unknown_stream_format
    firmware_update: reject

  unknown_enum_policy: preserve_raw
  unknown_bits_policy: preserve
  unknown_trailing_policy_default: reject
  deprecation_requires_replacement: true
  published_id_reuse: prohibited

code_generation:
  deterministic: true
  generated_files_manual_edit: prohibited

  source_identity:
    include_document_version: true
    include_protocol_version: true
    include_source_hash: sha256
    include_generator_name: true
    include_generator_version: true

  outputs:
    c:
      enabled: true
      target: node
      output_directory: generated/node/c
      generate:
        - constants
        - enums
        - types
        - encode
        - decode
        - validation

    csharp:
      enabled: true
      target: coordinator
      output_directory: generated/coordinator/csharp
      namespace: Example.Protocol
      generate:
        - constants
        - enums
        - models
        - codec
        - validation

    java:
      enabled: false
      target: coordinator
      output_directory: generated/coordinator/java
      package: com.example.protocol
      generate:
        - constants
        - enums
        - models
        - codec
        - validation

  documentation:
    enabled: true
    output_directory: generated/docs

  test_vectors:
    enabled: true
    output_directory: test_vectors/generated
```

---

# 5. Values That Shall Be Replaced

Before a Project Protocol Baseline is approved, replace at least:

```text
EXAMPLE_DEVICE_protocol
EXAMPLE_DEVICE
example_device_protocol
protocol_team
EXAMPLE_Framework_Application_Analysis.md
EXAMPLE_Application_Profile.md
EXAMPLE_SRS.md
EXAMPLE_Node_SDD.md
EXAMPLE_Coordinator_SDD.md
EXAMPLE_Test_Plan.md
Example.Protocol
com.example.protocol
```

Review all illustrative:

```text
Message IDs
Capability IDs
Service IDs
Enum values
Error values
Timeouts
Retry counts
Rates
Ranges
Buffer limits
Transport MTUs
Record sizes
Security privileges
Key Contexts
Image hash algorithms
Firmware chunk sizes
```

An illustrative value shall not become a Product requirement merely because it appears in this template.

---

# 6. Sections That May Be Removed

A Project may remove an entire optional area when it is out of scope, including:

```text
bootloader Namespace
FIRMWARE_UPDATE Service
CAP_FIRMWARE_UPDATE
0x5000-0x5FFF Messages
CAN FD Transport Profile
Java Code Generation
security_model only when a controlled Project explicitly establishes that no security mechanism is required
```

After removal, verify:

```text
No Message references a removed Namespace
No Message references a removed Service
No Capability declares a removed feature
No Code Generation output points to a nonexistent target
No Test Vector category retains an invalid reference
No Compatibility rule refers to a removed Message category
No Security attribute refers to a removed Key Context
```

A Project shall not remove Security merely for development convenience.

---

# 7. Product-Specific Placeholders Shall Not Remain

A derived `<Application>_protocol.yaml` shall not contain unresolved values matching, case-insensitively:

```text
EXAMPLE_
example_device
protocol_team
TODO
TBD
PLACEHOLDER
UNRESOLVED_PROJECT_DECISION
PROJECT_DEFINED_BEFORE_BASELINE
your_company
com.example
Example.Protocol
```

CI shall scan YAML scalar values, generated identifiers, generated comments, configuration, documentation, and
test vectors. Security-critical fields shall use an allowlist of approved concrete values in addition to the
generic placeholder scan.

The reusable template file may contain documented placeholders. The Product Baseline may not.

---

# 8. Schema Validation Checklist

- [ ] `schema_version` exists and is supported by the Generator.
- [ ] All required top-level keys exist.
- [ ] No duplicate YAML key exists.
- [ ] Hex and integer representations are valid.
- [ ] Every Enum, Bitset, Type, Alias, and Struct reference exists.
- [ ] Every Message references an existing Namespace and Service.
- [ ] Every Response references an existing Request.
- [ ] Every variable-length array has `maximum_length`.
- [ ] Every `length_from` field exists and precedes its array.
- [ ] Every declared `minimum_length` equals only the fixed decoding prefix before the first variable-length or optional trailing field; variable minimum counts and actual received length are validated separately.
- [ ] Every redundant or derived wire field has an explicit consistency relationship and mismatch policy.
- [ ] Every String defines encoding and maximum bytes.
- [ ] Every Message defines `length_policy`.
- [ ] Every exact-length Message rejects unknown trailing data.
- [ ] Every extensible Message places Optional Fields at the tail.
- [ ] Every field range is representable by its wire type.
- [ ] Every invalid value is outside the declared valid range.
- [ ] The YAML parser rejects unknown keys unless an approved extension namespace permits them.

---

# 9. Semantic Lint Checklist

- [ ] `messages[].id` values are globally unique.
- [ ] `capabilities[].id` values are unique within the Capability Registry.
- [ ] `services[].id` values are unique within their Namespace.
- [ ] `namespaces[].id` values are unique within the Protocol Family.
- [ ] `errors[].value` values are unique within the Error Registry.
- [ ] Enum values are unique within their containing Enum.
- [ ] Bit positions are unique within their containing Bitset.
- [ ] Message IDs comply with the declared allocation ranges.
- [ ] Equal numbers in different Registries are not falsely reported as conflicts.
- [ ] Request and Response pairing is complete.
- [ ] Every non-idempotent retry uses a controlled Operation or Transaction identity.
- [ ] Every safety-related command defines stale and duplicate policies.
- [ ] No Bootloader Message uses an Application Key Context.
- [ ] Telemetry and Stream categories follow the decision boundary in the Definition Guide.
- [ ] Telemetry defines cadence or trigger, Replacement Policy, Timestamp Policy, Priority, Loss Policy, and Maximum Plaintext Message Size.
- [ ] Every `latest_value_only` Telemetry Payload is a complete independently usable snapshot.
- [ ] Streaming defines Sequence, Timestamp, Loss Policy, ordering behavior, and Maximum Plaintext Message Size.
- [ ] `SAMPLE_STREAM_RECORD.sample_count` equals `channel_count × samples_per_channel`.
- [ ] The Stream decoder checks multiplication overflow, maximum bounds, equality, remaining Payload length, and destination capacity before reading `samples`.
- [ ] Every declared `minimum_length` equals the computed required fixed prefix before optional or variable trailing data.
- [ ] Every derived maximum encoded Message length is within its declared `maximum_plaintext_message_size` when present.
- [ ] Every maximum plaintext Telemetry, Stream, Handshake, and Firmware Update Message fits the Transport Profile plaintext limit.
- [ ] `maximum_secured_record_size` equals plaintext Message limit plus Protocol header, Security header, and Authentication Tag overhead.
- [ ] `maximum_transport_reassembly_size` is at least the maximum secured Record size.
- [ ] Every Fragmentation profile references the exact `SecuredRecordFragmentHeaderV1` wire struct and defines duplicate, out-of-order, integrity, timeout, conflict, oversize, and abort behavior.
- [ ] For every allowed Runtime MTU, `runtime_mtu - fragment_header_bytes > 0` and the required Fragment count is within the declared maximum.
- [ ] Capability parameters are bounded by the Runtime Effective Profile.
- [ ] Every variable array and Fragmentation path has a bounded memory requirement.
- [ ] No published or reserved Message ID is reused.
- [ ] Capability discovery rather than model-name inference controls optional features.
- [ ] Every Message defines an explicit `security` block; public and pre-Session Messages state that policy explicitly.
- [ ] Bidirectional or multi-environment secure Messages define deterministic direction/environment Key Context mappings.
- [ ] Application and Bootloader Handshake Messages and profiles are complete and bounded.
- [ ] Payload `handshake_profile_id` equals the referenced Profile ID; unsupported or downgraded Profiles are explicitly rejected without fallback.
- [ ] Canonical Handshake transcript binds Protocol family/version, Discovery ID, Profile ID, environment, roles, identities, nonces, ephemeral keys, negotiated algorithms, Session ID, and derived Key Contexts.
- [ ] Every Key Context maps to a concrete Record Counter/Rekey profile with Soft Threshold, Rekey Deadline, Hard Limit, persistence, gap, exhaustion, and atomic-cutover behavior.
- [ ] Public Discovery uses an ephemeral identifier, bounded exposure, rate limiting, transcript binding, and authenticated post-Session revalidation.
- [ ] Application and Bootloader Session and Key Context boundaries remain separate.
- [ ] Signed Firmware Manifest transfer, canonical hashing, signing-key identity, exact per-algorithm signature encoding and length, ECDSA low-S policy, and transaction binding are defined.

---

# 10. Compatibility Review Checklist

- [ ] Existing Message IDs are unchanged.
- [ ] Existing field offsets are unchanged.
- [ ] Existing field types, widths, signedness, and endianness are unchanged.
- [ ] No existing Required Field was removed.
- [ ] No published Enum value was reassigned.
- [ ] No published Error value was reassigned.
- [ ] A new Optional Field appears only at the tail of an extensible Payload.
- [ ] New Enum values have an unknown-value policy.
- [ ] New bits have an unknown-bits policy.
- [ ] New Capabilities are negotiated rather than inferred only from version.
- [ ] Security-attribute changes were evaluated for Session compatibility.
- [ ] Range narrowing was evaluated as a potential breaking change.
- [ ] Published and reserved IDs were not reused.
- [ ] Old Decoder/New Encoder and New Decoder/Old Encoder behavior was tested.
- [ ] A structural rewrite preserved all approved normative rules or recorded every intentional removal.

---

# 11. Baseline Readiness Checklist

- [ ] Schema Validation passes.
- [ ] Semantic Lint passes.
- [ ] Naming and placeholder scans pass.
- [ ] Compatibility Review is complete.
- [ ] Generated output is current and deterministic.
- [ ] Generated files identify source and Generator versions and hashes.
- [ ] Normal, boundary, invalid, and truncated Test Vectors pass.
- [ ] Cross-implementation interoperability passes for all implementations in scope.
- [ ] Cross-language interoperability passes for every language pair in scope.
- [ ] Telemetry replacement behavior is tested.
- [ ] Streaming loss, duplicate, ordering, wrap, and maximum-size tests pass.
- [ ] Inconsistent `channel_count`, `samples_per_channel`, and `sample_count` vectors are rejected before sample-array access.
- [ ] Stream minimum-length boundary vectors include the 19-byte fixed header and truncated variants.
- [ ] Application and Bootloader Handshake structs contain every transcript-bound identity, nonce, ephemeral key, algorithm, role, Session, and proof field.
- [ ] Wrong-profile, unlisted-profile, deprecated-profile, transcript, proof, replay, nonzero-padding, and Key Context vectors pass when applicable.
- [ ] Security golden vectors pass when applicable.
- [ ] Firmware Update Manifest-hash, wrong-key, signature-failure, anti-rollback, valid-resume-token, wrong-Host-token, wrong-Device-token, stale-generation, modified-transaction, modified-Manifest, duplicate-chunk, interruption, and rollback vectors pass when applicable.
- [ ] No published or reserved identifier was reused.
- [ ] No Product-specific placeholder remains.
- [ ] Human-readable Protocol documentation is current.
- [ ] Review and approval evidence is retained.
- [ ] The document version, Protocol version, Generator version, and change history are correct.

---

# Appendix A. Recommended Repository Structure

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
│  ├─ telemetry_streaming_reference.md
│  ├─ compatibility_policy.md
│  └─ firmware_update.md
├─ test_vectors/
│  ├─ commands/
│  ├─ events/
│  ├─ telemetry/
│  ├─ streaming/
│  ├─ compatibility/
│  ├─ security/
│  └─ firmware_update/
└─ generated/
   ├─ node/
   │  └─ c/
   └─ coordinator/
      ├─ csharp/
      └─ java/
```

---

# Appendix B. Template and Guide Responsibility Boundary

```text
Protocol_YAML_Definition_Guide.md
    Defines why the Protocol YAML is structured this way,
    which rules are normative, and how validation and governance work.

Protocol_YAML_Template.md
    Provides the complete reusable Project skeleton that can be copied,
    tailored, and completed.

<Application>_protocol.yaml
    Is the Project-specific formal wire contract and Code Generation input.
```

The Template shall not redefine a rule differently from the Guide.

Architecture, security, Firmware Update, and implementation statements repeated here are derived conformance
summaries. They shall cite and remain subordinate to the document that owns the topic.

When the Guide changes:

1. Review the Template for affected fields and examples.
2. Update the Template version when its content changes.
3. Regenerate and revalidate derived examples.
4. Record every intentional difference.

---

# Appendix C. Baseline Decision Summary

This baseline establishes the following decisions:

1. The Template is a reusable Project starting skeleton, not a formal Product Protocol.
2. A formal Project shall extract the YAML code block into `<Application>_protocol.yaml`.
3. Required and conditional lists contain only actual top-level keys.
4. Telemetry is represented by `messages[].category: telemetry` with cadence or trigger, replacement, timestamp, priority, loss, and maximum-size policies.
5. Streaming is represented by `messages[].category: stream` with sequence, timestamp, loss, ordering, and maximum-size policies.
6. Transmission frequency alone does not determine whether a Message is Telemetry or Stream.
7. Firmware Update and Bootloader are represented by Namespace, Service, Execution Environment, and Message Category rather than independent top-level keys.
8. The Message ID allocation table applies only to `messages[].id`.
9. Message, Capability, Service, Namespace, Error, Enum, and Bitset use independent Registries and uniqueness scopes.
10. Framework Messages use the recommended `0x0000-0x00FF` range.
11. Application Command and Response use the recommended `0x0100-0x0FFF` range.
12. Event, Alarm, Fault, Telemetry, Streaming, Diagnostics, File Transfer, and Firmware Update use their recommended ranges.
13. Every Message defines Namespace, Service, Category, Direction, Execution Environment, Length Policy, and Payload.
14. Request and Response relationships are explicit.
15. Every variable-length field has a maximum bound.
16. Telemetry with `latest_value_only` carries a complete independently usable snapshot.
17. Streaming defines Sequence, Timestamp, Loss Policy, and Maximum Plaintext Message Size.
18. `SAMPLE_STREAM_RECORD.sample_count` is an intentional array-length field, not an independent source of truth.
19. The sender and decoder enforce `sample_count == channel_count × samples_per_channel`; the decoder rejects overflow, mismatch, insufficient Payload length, or insufficient destination capacity before sample-array access.
20. The fixed header of `SAMPLE_STREAM_RECORD` is 19 bytes before the first encoded sample value.
21. Security-sensitive Messages define Authentication, Integrity, Anti-Replay, Privilege, and Key Context.
22. Application and Bootloader Sessions and Key Contexts remain separate.
23. Capability describes actual Node support; optional functions are not inferred only from model or version.
24. Transport Profiles define MTU, throughput, latency, maximum records, bounded reassembly, and Fragmentation.
25. Wire serialization is field by field and does not depend on native struct layout or implicit padding.
26. Firmware Update defines transaction identity, bounded chunks, resume state, complete-image verification, and controlled finalization.
27. Generated Code shall not be edited manually.
28. Code Generation is deterministic and validated by regeneration comparison.
29. Formal Baseline approval requires Schema Validation, Semantic Lint, Compatibility Review, Test Vectors, cross-implementation interoperability, and cross-language interoperability for every language pair in scope.
30. Product-specific placeholders shall not remain in a derived Protocol Baseline.
31. Structural rewrites preserve approved normative rules or explicitly record every intentional removal.
32. Every declared `minimum_length` matches the computed required fixed prefix.
33. Every derived maximum encoded Message length fits its declared record and Transport envelope.
34. Every Message carries explicit security semantics; omission is rejected.
35. Required Application and Bootloader Sessions have explicit bounded Handshake Messages and profiles.
36. Firmware Update transfers a canonical Manifest hash, signing-key identity, signature algorithm, and bounded signature before image acceptance.
37. Queue implementation is separate from Telemetry replacement semantics.
38. Repeated non-owning rules are derived conformance summaries and do not override their authority document.
39. Product Baselines reject case-insensitive unresolved placeholders and security sentinels in YAML and generated artifacts.
40. Public Discovery exposes no permanent Device identifier and is rate-limited, non-authoritative, transcript-bound, and revalidated after authentication.
41. Every Key Context has a machine-verifiable Record Counter and Rekey profile with an uncrossable Hard Limit and atomic cutover.
42. Handshake Profile IDs have one canonical binding; mismatches, unsupported Profiles, and downgrade attempts are explicitly rejected without fallback.
43. Canonical Handshake transcripts bind both roles, identities, nonces, ephemeral keys, negotiated algorithms, Session ID, and derived Key Contexts.
44. Firmware signature profiles define exact wire encoding, exact length, message preparation, and canonicality requirements.
45. `minimum_length` is the fixed decoding prefix only; variable-content bounds and received length are validated separately.
46. Plaintext Message size, security overhead, secured Record size, Transport reassembly size, and Fragment payload are distinct bounded quantities.
47. Fragmentation uses one exact 16-byte Header struct and deterministic bounded duplicate, ordering, integrity, timeout, conflict, and abort behavior.
48. Handshake wire payloads are named concrete structs; security-critical transcript fields shall not be hidden in opaque byte arrays.
49. Profile selection uses explicit allowed, preferred, prohibited, security-level, and deprecation data; Profile IDs are identifiers, not security-strength ranks.
50. Firmware Update resume requires a Device-issued token bound to transaction, Manifest, Device identity, authorized Host identity, security version, generation, and nonce.
51. Every data-bearing Transport Profile has `minimum_mtu > fragment_header_bytes`; CAN FD Baseline requires a 64-byte MTU.

---

# Conclusion

This template converts the rules in the Protocol YAML Definition Guide into a reusable Project skeleton.

The formal workflow is:

```text
Copy this Template
    |
Tailor optional sections
    |
Replace illustrative values and placeholders
    |
Create <Application>_protocol.yaml
    |
Schema Validation
    |
Semantic / Security / Compatibility Lint
    |
Code Generation
    |
Generated-output comparison
    |
Test Vectors / Mock / Interoperability
    |
Protocol Baseline
```

The core principle is:

> The Template accelerates Project setup, but the derived `<Application>_protocol.yaml`,
> its validation evidence, and its approved versions form the actual Project Protocol Contract.
