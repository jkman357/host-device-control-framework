# Node Software Engineering Rules

**Canonical Filename:** `Node_Software_Engineering_Rules.md`  
**Document Version:** v1.1.0  
**Supersedes Document Version:** v1.0.0  
**Status:** Draft for Review  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-19  
**Language:** English  
**Intended Audience:** Embedded and systems engineers, software architects, reviewers, test engineers, code generators, and AI-assisted engineering systems  
**Repository Role:** Proposed normative engineering authority for Node-owned software realization  
**Related Documents:**
- `../framework/AI_Engineering_Usage_Guide.md`
- `../framework/Coordinator_Node_Control_Framework.md`
- `../framework/Framework_Application_Analysis_Template.md`
- `../protocol/Protocol_YAML_Definition_Guide.md`
- `../protocol/Protocol_Compatibility_Rules.md`
- `../protocol/Protocol_Registry_Governance.md`
- `../protocol/Protocol_Security_Profile.md`
- `../coding-rules/Embedded_C_Coding_Rules.md`
- `../validation/Framework_Conformance_Checklist.md`
- `../validation/Validation_Evidence_Guide.md`

---

## Copyright and Use

Copyright © 2026 Ray Yang. All rights reserved unless a repository-level license states otherwise.

This document is independently authored. External standards and guidance are referenced for context and are not reproduced as substitute standards.

---

## Version History

| Version | Date | Status | Summary |
|---|---|---|---|
| v1.1.0 | 2026-07-19 | Draft for Review | Added Node identity/address lifecycle, discovery and registration, target validation, wrong-target and broadcast behavior, Session binding, duplicate/conflict handling, replacement, resource isolation, and Firmware Update target requirements for Multi-Node deployments. |
| v1.0.0 | 2026-07-19 | Draft for Review | Initial Draft defining Node-specific layering, execution context, state and command ownership, local safety, startup, communication loss, bounded resources, telemetry, persistence, diagnostics, Bootloader handoff, target testing, and AI implementation controls. |

---

# Part I — Document Governance

## 1. Purpose

This document defines cross-language engineering rules for software that performs the **Node** role in a Coordinator/Node system. A Node commonly owns physical I/O, local control, data acquisition, actual device state, bounded real-time behavior, local faults, and the authoritative decision to execute or reject Node-owned actions.

The document governs Node-specific realization. It does not redefine the reusable role boundary owned by the Framework, the actual Product behavior owned by Product requirements, the wire contract owned by the Project Protocol, or language syntax and style owned by Coding Rules.

## 2. Applicability

This document applies to Product-owned Node software implemented as, for example:

- bare-metal firmware;
- a super-loop application;
- RTOS-based embedded software;
- an embedded Linux process acting as a Node;
- an FPGA-adjacent control processor;
- a simulator or reference Node when it claims Node behavior;
- a Bootloader or recovery environment where the stated rules apply.

A Project shall record whether this Draft is adopted and which sections are applicable.

## 3. Normative Language

The keywords **shall**, **shall not**, **should**, **should not**, and **may** are normative. A deviation from a shall requirement requires an approved exception. A deviation from a should requirement requires an engineering rationale.

## 4. Authority Boundary

- The Framework owns reusable Coordinator/Node roles, architecture, safety placement, Protocol layering, and system lifecycle principles.
- This document owns Node-specific software realization.
- Protocol authorities own compatibility, identifiers, security governance, and machine-verifiable wire representation.
- Language Coding Rules own language-level naming, types, arithmetic, memory, API, and code construction.
- Product requirements, risk controls, SDD, hardware specifications, and platform constraints own Product-specific behavior and acceptance.

A restatement in this document is a Node conformance view and shall not weaken the owning authority.

# Part II — Node Architecture

## 5. Required Layering

A Node should separate responsibilities into explicit layers appropriate to its scale:

```text
Product Application / State Machines
        ↓
Domain and Node Services
        ↓
Protocol / Device / Storage Adapters
        ↓
Drivers
        ↓
HAL
        ↓
BSP and Hardware
```

Small systems may combine physical modules, but ownership and dependency direction shall remain reviewable.

## 6. Layer Responsibilities

### 6.1 Product Application

The Product Application owns Product workflows, operating states, high-level coordination, command-use cases, and Product-visible fault reaction assigned to the Node.

### 6.2 Domain and Node Services

Services own reusable Node capabilities such as acquisition, motion control, configuration, diagnostics, time, storage, or update coordination. Services shall expose bounded interfaces and shall not depend on UI or Coordinator implementation details.

### 6.3 Adapters

Adapters translate between domain/service contracts and Protocol, vendor stacks, files, nonvolatile storage, or external libraries. Vendor-specific types and side effects should stop at the adapter boundary.

### 6.4 Drivers, HAL, and BSP

Drivers own peripheral behavior. HAL abstracts processor or platform mechanisms when useful. BSP owns board wiring, pins, clocks, interrupts, power sequencing, and board variants.

Product state-machine logic shall not be hidden in a generic driver merely because the driver can access the hardware.

## 7. Dependency Direction

Dependencies shall point from Product policy toward abstractions and from adapters toward concrete platform mechanisms. Lower layers shall not call upward into Product logic through uncontrolled callbacks.

Cross-layer access, global state, and direct register access outside the assigned hardware layer require explicit justification.

## 8. Vendor and Generated Code

Vendor code, generated code, middleware, and third-party stacks shall be isolated behind Product-owned boundaries where practical.

Product-owned wrappers shall define initialization, thread/ISR context, error translation, memory use, timeout, callback, and shutdown behavior. Modifying generated or vendor code shall be controlled and repeatable.

# Part III — Execution Model and Concurrency

## 9. Execution Model Declaration

The Node shall document whether it uses bare metal, super-loop, cooperative scheduling, preemptive RTOS, embedded operating system, multiple cores, DMA, or hardware state machines.

The declaration shall identify execution contexts, priorities, deadlines, shared resources, and blocking restrictions.

## 10. ISR Boundary

An ISR shall perform only bounded, time-critical work such as capturing status, timestamping, moving a bounded data unit, clearing the source, and notifying a lower-priority owner.

An ISR shall not perform unbounded loops, blocking I/O, dynamic allocation, complex Product state transitions, Protocol transactions, file operations, logging formatting, or long cryptographic work unless a measured platform design explicitly proves it safe.

ISR-to-task data transfer shall define ownership, overflow behavior, and memory visibility.

## 11. Task and Thread Ownership

Each mutable resource and state machine shall have one clear owner or one documented synchronization policy.

Task priority shall follow deadline and safety needs, not developer convenience. Priority inversion, starvation, and unbounded blocking shall be analyzed.

A high-priority control task shall not wait indefinitely for a lower-priority logger, Transport, file system, or UI-related operation.

## 12. Callback and Timer Boundary

A callback or timer shall declare its execution context, allowed operations, lifetime, and reentrancy behavior.

Callbacks from vendor stacks or ISRs should publish a bounded event to the owning task rather than executing Product workflows directly.

Timer callbacks shall not assume exact wall-clock execution; the design shall define jitter tolerance and missed-expiration behavior.

## 13. DMA Ownership

DMA buffers shall have explicit producer, consumer, cache/coherency, completion, cancellation, and reuse rules.

A buffer shall not be reused while hardware or another context can still access it. Partial completion and transfer error shall leave ownership unambiguous.

# Part IV — State and Command Authority

## 14. Local State Authority

The Node owns the authoritative actual state of Node-controlled hardware and local Product behavior unless a Product authority explicitly assigns otherwise.

A Coordinator command is a request. Receipt or Transport acknowledgement shall not be represented as completed physical action.

The Node shall report actual state, pending operation, completion, failure, and uncertainty according to the Project Protocol.

## 15. Command Pipeline

A Node command path shall perform, as applicable:

```text
Receive bounded record
→ Validate framing and security
→ Decode into inert typed data
→ Validate identifier and payload
→ Validate range, enum, unit, and length
→ Validate capability and execution environment
→ Validate authorization
→ Validate Product state and safety preconditions
→ Accept or reject
→ Schedule or execute under the owning context
→ Report started/progress/completed/failed state
→ Update diagnostics and authoritative state
```

No earlier layer shall bypass a later authoritative validation step.

## 16. Accepted, Started, Completed, and Failed

The implementation shall distinguish:

- **Accepted:** request is valid and admitted for processing.
- **Started:** the owning execution context began the operation.
- **Completed:** the required effect was confirmed according to Product acceptance criteria.
- **Failed:** the operation terminated without satisfying completion criteria.

A queued or accepted command shall not be reported as completed. If completion cannot be determined, the result shall be unknown or indeterminate rather than falsely successful.

## 17. Duplicate and Concurrent Commands

The Node shall define duplicate, replay, retry, cancellation, replacement, and concurrent-command behavior for each relevant operation.

Exclusive operations shall reject, queue, or explicitly arbitrate conflicts. Blindly executing duplicate non-idempotent commands is prohibited.

## 18. Capability and State Validation

The Node shall validate capability and current state even when the Coordinator has already done so. Capability may depend on hardware variant, configuration, security role, execution environment, fault state, or runtime availability.

Unsupported or temporarily unavailable behavior shall return a defined result without partial uncontrolled execution.

## 18.1 Multi-Node Identity and Target Validation

A Node shall acquire, store, expose, and validate its stable identity according to the Project authority. Runtime
address, discovery identity, Transport endpoint, Protocol Session, and Secure Session shall remain distinct.

A Node shall not execute a targeted command unless the command is unambiguously addressed and authorized for that
Node. The Project Protocol shall select exactly one behavior for a well-formed command targeting another Node:

```text
Silently ignore
Reject with a defined bounded Response
Treat as a Protocol violation
```

The implementation shall not choose among these behaviors locally. Malformed or unauthorized routing metadata
shall be rejected before Product state changes.

When broadcast is supported, the Node shall enforce the approved Message allowlist, authorization, Replay, and
response policy. It shall not transmit an immediate response when the Protocol requires no response, polling,
slots, or another collision-control mechanism. Safety-significant control, configuration, reset, Rekey, credential,
and Firmware Update broadcast shall be rejected unless explicitly authorized by the Product authority.

Registration and re-registration shall handle fixed, discovered, or assigned addresses, duplicate identity, address
conflict, Coordinator restart, Node reset, stale Coordinator Session, replacement, quarantine, and maximum-Node
rejection. Address reassignment shall not retain an old Secure Session or authorization.

# Part V — Safety, Faults, and Lifecycle

## 19. Local Safety Ownership

The Node shall retain local safety behavior that must remain effective during delay, overload, Coordinator fault, Transport loss, or malicious traffic.

Remote control shall not disable a local protection unless an approved Product authority explicitly defines and validates that behavior.

## 20. Fault Classification and Reaction

Faults shall be classified by source, severity, latching, recoverability, and required action. The Node shall distinguish Product faults, communication errors, diagnostic failures, and internal software defects.

Fault reaction may include rejecting a command, entering degraded mode, entering a safe state, isolating hardware, stopping output, preserving evidence, resetting a subsystem, or controlled restart.

The reaction shall be deterministic enough to test and shall not depend on successful remote communication when local action is required.

## 21. Watchdog

A watchdog design shall identify:

- supervised execution contexts;
- healthy-state criteria;
- feed ownership;
- startup and maintenance behavior;
- maximum detection and recovery time;
- reset or escalation action;
- diagnostic evidence and reset-cause preservation.

Feeding the watchdog from an ISR or independent timer without proving critical tasks are healthy is prohibited.

## 22. Degraded and Safe States

Degraded and safe states shall be Product-defined and shall identify allowed outputs, commands, telemetry, recovery, and required user or service action.

Entry shall be idempotent and bounded. Failure to reach the intended state shall have an escalation path.

A “safe state” label without defined physical outputs and assumptions is insufficient.

## 23. Communication Loss

The Node shall define behavior for silence, Transport close, malformed traffic, repeated security failure, and Coordinator disappearance.

The behavior shall specify:

- detection source and timeout;
- local control continuation or stop;
- output and safety state;
- command queue disposition;
- Session and authorization invalidation;
- telemetry and diagnostic preservation;
- reconnect requirements.

Communication loss shall not be inferred solely from one missed non-deterministic UI update.

## 24. Reset Cause and Recovery

The Node shall capture available reset cause before it is overwritten and shall classify power-on, external, watchdog, software, fault, brownout, Bootloader, and unknown reset as supported by the platform.

Recovery shall not automatically restore unsafe outputs or stale commands. Persistent state shall be validated before use.

## 25. Startup Sequence

Startup shall place outputs in approved safe defaults before enabling actuators or accepting commands.

A documented sequence should cover:

1. minimal platform and clock setup;
2. reset-cause capture;
3. memory and configuration validation;
4. hardware-safe output initialization;
5. driver and service initialization;
6. self-test and dependency readiness;
7. Protocol and Transport availability;
8. transition to an operational or degraded state.

Initialization failure shall identify which services are unavailable and shall not present the Node as fully ready.

## 26. Shutdown and Power Transition

Where controlled shutdown or low-power transition exists, the design shall bound command admission, output state, data flush, persistent-state commit, peripheral stop, and wakeup revalidation.

Loss of power at any point shall not corrupt persistent state into a falsely valid configuration.

# Part VI — Data, Streaming, and Resources

## 27. Acquisition and Transmission Separation

Time-critical acquisition shall be decoupled from non-deterministic Protocol transmission, logging, storage, and Coordinator behavior.

The acquisition path shall define sampling trigger, timestamp source, buffering, overrun behavior, invalid-data indication, and ownership transfer.

Transport congestion shall not silently alter the physical sampling schedule unless the Product design explicitly allows it.

## 28. Telemetry Snapshot Consistency

A telemetry record containing related values shall come from a defined consistent snapshot or shall expose the time/state relationship among fields.

Readers shall not observe a mixture of partially updated multi-field state without an approved atomic, lock, version, double-buffer, or snapshot mechanism.

Unknown, stale, unavailable, invalid, and not-applicable values shall be distinguishable when the Product requires the distinction.

## 29. Streaming

Streaming design shall define:

- producer and consumer;
- sample and publication rate;
- record format and sequence;
- timestamp ownership;
- queue or ring-buffer capacity;
- batching and fragmentation;
- loss, gap, overrun, and reset indicators;
- start, stop, pause, reconnect, and resubscribe behavior;
- effect of security and Rekey;
- memory and bandwidth budget.

Sequence gaps shall not be hidden by fabricating samples.

## 30. Queue and Buffer Ownership

Every queue and buffer shall have a fixed or explicitly bounded capacity and a defined overflow policy.

Policies may reject newest, discard oldest, coalesce replaceable telemetry, block within a measured bound, or enter a fault state. The selected policy shall match the data meaning.

Control commands, safety events, and diagnostic text shall not share one unbounded queue without priority and overload analysis.

## 31. Static and Bounded Resources

Node implementations should use static memory or otherwise deterministically bounded memory according to the platform and language authority. Heap use, if permitted by the applicable Coding Rules and Product profile, shall have a bounded design, failure handling, fragmentation analysis, and evidence.

Stack, heap, queue, buffer, descriptor, timer, task, file, and persistent-storage budgets shall be documented for the target configuration.

## 32. Overflow, Underflow, and Overrun

Arithmetic overflow/underflow, counter wrap, buffer overrun, queue overflow, lost interrupt, missed deadline, and sample loss shall have explicit prevention, detection, and reaction appropriate to risk.

Intentional wraparound shall be isolated, typed, documented, and reviewed.

## 33. Timing and WCET Evidence

Deadlines and timing budgets shall identify measurement point, target hardware, build configuration, clock, load, sample size, maximum observed value, margin, and method.

Host simulation or code inspection alone shall not prove target WCET, ISR latency, DMA behavior, or physical response.

# Part VII — Configuration, Persistence, and Diagnostics

## 34. Configuration Ownership

Each configuration item shall have one owner, type, unit, range, default, persistence policy, update authority, activation rule, and compatibility/migration rule.

The Node shall validate received and stored configuration before use. Coordinator-side validation is supplementary.

Configuration changes that affect safety or physical behavior shall use an approved commit, confirmation, rollback, or transactional pattern.

## 35. Persistent State

Persistent records shall have schema/version identity, integrity protection appropriate to risk, atomic update or recoverable journaling, default and migration behavior, and bounded write endurance.

Partially written, corrupted, incompatible, or unknown records shall not be treated as valid. Recovery shall be observable.

Secrets shall use approved secure storage rather than ordinary configuration records.

## 36. Logging and Diagnostics

Node diagnostics shall be structured, bounded, timestamped where meaningful, and safe for the execution context.

Diagnostics should identify event code, severity or category, component, state, operation correlation, reset/session context, and bounded parameters.

The Node shall not perform expensive formatting or blocking export in an ISR or high-priority control task. Logging failure shall not block critical control.

Secrets, private keys, credentials, and unapproved personal or sensitive data shall not be logged.

## 37. Diagnostic Versus Product State

Diagnostic log severity shall not automatically define a Product Alarm or Fault priority. Product Alarm, Event, Fault, acknowledgement, latching, and recovery behavior shall come from Product authorities.

# Part VIII — Bootloader and Update Boundary

## 38. Bootloader/Application Handoff

The handoff shall define:

- entry reason and authorization;
- hardware and output state;
- memory, peripheral, interrupt, clock, and watchdog ownership;
- reset versus direct jump behavior;
- environment identity;
- configuration and retained-state validity;
- return-to-Application behavior;
- diagnostic and reset-cause preservation.

Application pointers, callbacks, tasks, locks, Sessions, and ordinary Protocol state shall not remain implicitly active in the Bootloader.

## 39. Firmware Update Execution

The Node owns authoritative validation and execution of the update according to Product and Protocol authorities.

The implementation shall validate target, Manifest, signature/authenticity, version and anti-rollback policy, size, hash, storage bounds, chunk or record integrity, resume state, commit conditions, and post-boot verification as applicable.

A Coordinator success display shall not substitute for Node verification.

## 40. Interrupted Update

Power loss, reset, disconnect, Rekey, duplicate chunk, wrong offset, storage failure, invalid Manifest, and failed activation shall have defined recovery behavior.

The design shall prevent booting an unverified image and shall preserve an approved recovery path.

## 40.1 Multi-Node Firmware Update Targeting

Before erase, program, commit, or activation, the Node shall verify that the authenticated update Session, signed
Manifest, transaction identity, hardware/Product compatibility, and target identity refer to this Node. A broadcast
or group address alone shall not authorize Firmware Update. Resume state shall remain bound to the approved Node and
host identity according to the Security Profile.

# Part IX — Verification and Release

## 41. Test Layers

Node verification should include:

- host-based unit tests for pure logic;
- component tests with controlled drivers and time;
- target tests for peripheral, timing, concurrency, memory, and reset behavior;
- HIL or representative system tests for physical interfaces and control behavior;
- Coordinator/Node interoperability tests;
- malformed-input, fuzz, overload, and fault-injection tests;
- startup, shutdown, communication-loss, watchdog, and recovery tests;
- Bootloader and Firmware Update tests where applicable.

## 42. Target Evidence

Target evidence shall identify hardware revision, software build, compiler/toolchain, configuration, clock, debug/release state, connected equipment, inputs, outputs, acceptance criteria, and result.

A debugger attached or instrumentation enabled may change timing and shall be disclosed.

## 43. Fault Injection

Fault injection should cover relevant failures such as sensor disconnection, out-of-range values, stuck signals, driver errors, queue overflow, storage corruption, communication loss, security failure, timeout, task stall, watchdog, reset, and power interruption.

Injection shall not damage equipment or create uncontrolled unsafe behavior; the method and limitations shall be reviewed.

## 44. Release Readiness

Before release, the Node owner shall confirm:

- applicable authority versions and approved deviations;
- Product and Protocol traceability;
- clean required build and static-analysis results;
- resource and timing evidence;
- target and interoperability evidence;
- unresolved defects and risk acceptance;
- configuration and update compatibility;
- generated-artifact source identity;
- release package integrity.

# Part X — AI-Assisted Implementation Controls

## 45. Source Authority

AI-generated Node artifacts shall identify the applicable Framework, Node Rules, Protocol, Coding Rules, Product requirements, hardware documents, and toolchain constraints.

AI shall not infer missing hardware behavior, ISR context, register semantics, reset behavior, memory size, timing, or safety action without evidence.

## 46. Generation Boundary

Generated code shall be separated from Product-owned handwritten code when practical. Regeneration shall be repeatable, and manual changes to generated files shall be prohibited or explicitly controlled.

AI output shall be reviewed for unsupported APIs, dynamic allocation, unbounded loops, hidden blocking, race conditions, stale assumptions, incorrect volatile/atomic use, unit/range errors, and fabricated evidence.

## 47. Human Responsibility

AI may draft architecture, code, tests, and review findings. It shall not self-approve, declare target behavior verified without execution, or assume that a build or mock test proves physical behavior.

Human engineers remain responsible for Product decisions, hardware interpretation, safety and security review, test execution, evidence approval, and release acceptance.
