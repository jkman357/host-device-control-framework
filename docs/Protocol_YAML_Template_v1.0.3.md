# Protocol YAML Template

## Coordinator/Node Application Protocol Project Template

**Document Name:** `Protocol_YAML_Template_v1.0.3.md`  
**Document ID:** PYT  
**Document Version:** v1.0.3  
**Status:** Baseline  
**Document Type:** Reusable Project Template  
**Primary Narrative Language:** English  
**Author:** Ray Yang  
**Maintainer:** Ray Yang  
**Repository:** `host-device-control-framework`  
**Related Documents:**
- `Coordinator_Node_Control_Framework_v1.0.1.md`
- `Protocol_YAML_Definition_Guide_v1.0.3.md`

**First Issued:** 2026-07-15  
**Last Revised:** 2026-07-18  

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
9. Complete Schema Validation, Semantic Lint, Compatibility Review, Test Vectors, and cross-language interoperability before Protocol Baseline approval.
10. Record every intentional removal or structural change that affects a previously approved Protocol Baseline.

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
    and maximum_record_size.

Streaming
    Represented by messages[].category: stream together with sequence_policy,
    timestamp_policy, loss_policy, and maximum_record_size.

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

This reusable template intentionally contains identifiers such as:

```text
EXAMPLE_DEVICE
EXAMPLE_Application_Profile
protocol_team
```

A derived Product or Project Protocol Baseline shall not retain these placeholders.

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
    minimum_version: v1.0.1

  related_definition_guide:
    name: Protocol_YAML_Definition_Guide
    minimum_version: v1.0.3

  related_application_analysis: EXAMPLE_Framework_Application_Analysis_v1.0.0.md
  related_application_profile: EXAMPLE_Application_Profile_v1.0.0.md
  related_srs: EXAMPLE_SRS_v1.0.0.md
  related_node_sdd: EXAMPLE_Node_SDD_v1.0.0.md
  related_coordinator_sdd: EXAMPLE_Coordinator_SDD_v1.0.0.md
  related_test_plan: EXAMPLE_Test_Plan_v1.0.0.md

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
        maximum: 32

      - name: maximum_sample_rate_hz
        type: uint32
        unit: Hz

      - name: maximum_samples_per_record
        type: uint16

  - name: CAP_DIAGNOSTICS
    id: 0x0105
    since: V1.0.0
    description: Diagnostic and self-test support.

  - name: CAP_FIRMWARE_UPDATE
    id: 0x0201
    since: V1.0.0
    description: Bootloader Firmware Update support.

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
    maximum_record_size: 4096
    maximum_reassembly_buffer: 4096

    fragmentation:
      mode: protocol_record_fragmentation
      maximum_fragments_per_record: 128
      maximum_concurrent_reassembly: 1
      reassembly_timeout_ms: 1000

  - name: CAN_FD_BASELINE
    transport: can_fd
    minimum_mtu: 8
    maximum_mtu: 64
    expected_minimum_throughput_bps: 10000
    maximum_control_latency_ms: 100
    maximum_record_size: 1024
    maximum_reassembly_buffer: 1024

    fragmentation:
      mode: protocol_record_fragmentation
      maximum_fragments_per_record: 32
      maximum_concurrent_reassembly: 1
      reassembly_timeout_ms: 500

security_model:
  session_required_for_application_control: true
  session_required_for_application_data: true
  session_required_for_firmware_update: true
  application_and_bootloader_sessions_separate: true

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

  - name: GET_DEVICE_INFO_REQUEST
    id: 0x0001
    namespace: framework
    service: DEVICE_MANAGEMENT
    category: command_request
    direction: coordinator_to_node
    execution_environment: any
    description: Request Device identity, hardware, Firmware, and Protocol information.

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
      privilege: public_read

    payload:
      fields: []

  - name: GET_DEVICE_INFO_RESPONSE
    id: 0x0002
    namespace: framework
    service: DEVICE_MANAGEMENT
    category: command_response
    direction: node_to_coordinator
    response_to: GET_DEVICE_INFO_REQUEST
    execution_environment: any
    description: Device identity and version information.

    length_policy: extensible
    minimum_length: 30
    unknown_trailing_policy: ignore

    security:
      authentication_required: false
      confidentiality_required: false
      integrity_required: false
      anti_replay_required: false
      allowed_before_session: true
      privilege: public_read

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
          description: Active Protocol version.

        - name: execution_environment
          type: enum
          enum: ExecutionEnvironment
          description: Current Execution Environment.

        - name: device_uuid
          type: uint8
          description: Device unique identifier.
          array:
            length: 16

  - name: GET_CAPABILITIES_REQUEST
    id: 0x0003
    namespace: framework
    service: DEVICE_MANAGEMENT
    category: command_request
    direction: coordinator_to_node
    execution_environment: any
    description: Request supported Capability identifiers.

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
      privilege: public_read

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
    description: Supported Capability identifiers.

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
          alias: DeviceTimestampUs
          description: Sender monotonic timestamp when available.

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
    minimum_length: 14
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
    maximum_record_size: 32

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
    maximum_record_size: 512
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
          maximum: 32
          description: Number of enabled channels represented by each sample group.

        - name: samples_per_channel
          type: uint8
          minimum: 1
          maximum: 128
          description: Number of samples for each channel in this record.

        - name: sample_count
          type: uint16
          minimum: 1
          maximum: 4096
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
            maximum_length: 4096

  # Firmware Update / Bootloader Messages: 0x5000-0x5FFF

  - name: BEGIN_UPDATE_REQUEST
    id: 0x5001
    namespace: bootloader
    service: FIRMWARE_UPDATE
    category: firmware_update
    direction: coordinator_to_node
    execution_environment: bootloader
    description: Begin or resume a Firmware Update transaction.

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

        - name: image_type
          type: uint8
          description: Target image or partition type.

        - name: image_size
          type: uint32
          description: Complete image size in bytes.

        - name: security_version
          type: uint32
          description: Monotonic anti-rollback security version.

        - name: manifest_hash
          type: uint8
          description: SHA-256 hash of the canonical manifest.
          array:
            length: 32

        - name: image_hash
          type: uint8
          description: SHA-256 hash of the complete image.
          array:
            length: 32

  - name: BEGIN_UPDATE_RESPONSE
    id: 0x5002
    namespace: bootloader
    service: FIRMWARE_UPDATE
    category: firmware_update
    direction: node_to_coordinator
    response_to: BEGIN_UPDATE_REQUEST
    execution_environment: bootloader
    description: Update transaction acceptance and resume state.

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
          description: Maximum accepted chunk-data length.

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
          maximum: 1024
          description: Number of bytes in chunk_data.

        - name: chunk_data
          type: uint8
          description: Firmware image bytes.
          array:
            length_from: chunk_length
            maximum_length: 1024

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
EXAMPLE_Framework_Application_Analysis_v1.0.0.md
EXAMPLE_Application_Profile_v1.0.0.md
EXAMPLE_SRS_v1.0.0.md
EXAMPLE_Node_SDD_v1.0.0.md
EXAMPLE_Coordinator_SDD_v1.0.0.md
EXAMPLE_Test_Plan_v1.0.0.md
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

A derived `<Application>_protocol.yaml` shall not contain:

```text
EXAMPLE_
TODO
TBD
PLACEHOLDER
your_company
com.example
Example.Protocol
```

CI should scan the derived Project YAML and generated artifacts.

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
- [ ] Every declared minimum length equals the mandatory fixed-field size plus the minimum variable content.
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
- [ ] Telemetry defines cadence or trigger, Replacement Policy, Timestamp Policy, Priority, Loss Policy, and Maximum Record Size.
- [ ] Every `latest_value_only` Telemetry Payload is a complete independently usable snapshot.
- [ ] Streaming defines Sequence, Timestamp, Loss Policy, ordering behavior, and Maximum Record Size.
- [ ] `SAMPLE_STREAM_RECORD.sample_count` equals `channel_count × samples_per_channel`.
- [ ] The Stream decoder checks multiplication overflow, maximum bounds, equality, remaining Payload length, and destination capacity before reading `samples`.
- [ ] Every maximum Telemetry or Stream record can be carried or fragmented by a declared Transport Profile.
- [ ] Every variable array and Fragmentation path has a bounded memory requirement.
- [ ] No published or reserved Message ID is reused.
- [ ] Capability discovery rather than model-name inference controls optional features.
- [ ] Security-sensitive Messages define Authentication, Integrity, Anti-Replay, Privilege, and Key Context.
- [ ] Application and Bootloader Session and Key Context boundaries remain separate.

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
- [ ] Cross-language interoperability passes for all languages in scope.
- [ ] Telemetry replacement behavior is tested.
- [ ] Streaming loss, duplicate, ordering, wrap, and maximum-size tests pass.
- [ ] Inconsistent `channel_count`, `samples_per_channel`, and `sample_count` vectors are rejected before sample-array access.
- [ ] Stream minimum-length boundary vectors include the 19-byte fixed header and truncated variants.
- [ ] Security golden vectors pass when applicable.
- [ ] Firmware Update resume, duplicate-chunk, hash-failure, signature-failure, interruption, and rollback vectors pass when applicable.
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
Protocol_YAML_Definition_Guide_v1.0.3.md
    Defines why the Protocol YAML is structured this way,
    which rules are normative, and how validation and governance work.

Protocol_YAML_Template_v1.0.3.md
    Provides the complete reusable Project skeleton that can be copied,
    tailored, and completed.

<Application>_protocol.yaml
    Is the Project-specific formal wire contract and Code Generation input.
```

The Template shall not redefine a rule differently from the Guide.

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
17. Streaming defines Sequence, Timestamp, Loss Policy, and Maximum Record Size.
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
29. Formal Baseline approval requires Schema Validation, Semantic Lint, Compatibility Review, Test Vectors, and cross-language interoperability.
30. Product-specific placeholders shall not remain in a derived Protocol Baseline.
31. Structural rewrites preserve approved normative rules or explicitly record every intentional removal.

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
