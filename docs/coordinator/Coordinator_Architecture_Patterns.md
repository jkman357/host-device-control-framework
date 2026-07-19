# Coordinator Architecture Patterns

> Reusable Structural Patterns for Coordinator-Side Applications

**Canonical Filename:** `Coordinator_Architecture_Patterns.md`  
**Document Version:** v1.1.0  
**Supersedes Document Version:** v1.0.0  
**Status:** Draft for Review  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-19  
**Language:** English  
**Intended Audience:** Human engineers, software architects, reviewers, test engineers, code generators, and AI-assisted engineering systems  
**Repository Role:** Proposed topic-specific normative engineering authority for Coordinator architecture patterns, subordinate to Coordinator Software Engineering Rules

---

## Copyright and Use

Copyright © 2026 Ray Yang. All rights reserved unless a repository-level license states otherwise.

This document is independently authored. External standards and guidance are referenced for context and are not reproduced as substitute standards. Third-party documents remain subject to their respective copyright and license terms.

This document is maintained as part of a personal engineering project. It is not an official document of any employer or organization.

---

## Related Documents

- [Coordinator/Node Control Framework](../framework/Coordinator_Node_Control_Framework.md)
- [Coordinator Software Engineering Rules](Coordinator_Software_Engineering_Rules.md)
- [Coordinator Concurrency Guide](Coordinator_Concurrency_Guide.md)
- [Coordinator Logging Guide](Coordinator_Logging_Guide.md)
- [Coordinator Testing Guide](Coordinator_Testing_Guide.md)
- [Coordinator UI Engineering Guide](Coordinator_UI_Engineering_Guide.md)

---

## Version History

| Version | Date | Status | Summary |
|---|---|---|---|
| v1.1.0 | 2026-07-19 | Draft for Review | Expanded the Multi-Node isolation pattern into Node Registry, Node Context, immutable target/route binding, per-Node request/state/resource, shared-bus scheduling, aggregate-state, replacement, and multi-target operation patterns. |
| v1.0.0 | 2026-07-19 | Draft for Review | Initial Draft defining Coordinator layers, dependency direction, state ownership, command and receive pipelines, lifecycle handling, multi-Node isolation, security-session ownership, extension boundaries, configuration, error propagation, pattern selection, anti-patterns, and review criteria. |

---

# 0. Purpose

This Guide defines reusable architecture patterns for Coordinator-side software that communicates with and controls one or more Nodes.

A Coordinator may be implemented as a PC application, mobile application, gateway, service tool, production tool, laboratory tool, or another host-side software system. The patterns are language- and UI-framework-independent unless a Project-specific standard states otherwise.

This Guide is intended to help an engineer or AI system create an architecture that is:

- understandable and reviewable;
- testable without physical hardware where practical;
- resilient to disconnects, malformed input, delayed responses, and partial failure;
- explicit about state ownership and thread ownership;
- decoupled from Transport and UI framework details;
- compatible with generated Protocol contracts;
- suitable for incremental Product-specific extension.

This Guide defines defaults rather than a single mandatory application skeleton. Approved Product requirements, the Coordinator SDD, the Project Protocol, platform constraints, and human architecture decisions may select or adapt the patterns with documented rationale.

## 0.1 Requirement Keywords

The keywords in this Guide are used as follows:

- **shall**: required when this Guide applies and no approved deviation exists;
- **should**: the preferred default; another approach may be used with a clear engineering reason;
- **may**: an allowed option.

## 0.2 Authority Boundary

This document is a `Draft for Review`. Its requirements are proposed and do not apply to a Project until a human authority explicitly adopts or approves this document for that Project.

`Coordinator_Software_Engineering_Rules.md` remains the cross-topic Coordinator software authority. This Guide owns only the detailed Coordinator architecture-pattern and structural-realization rules within its stated scope after adoption. It shall not weaken or silently override the cross-topic rules. Repeated Framework, Protocol, safety, security-boundary, or Product rules are `Derived conformance summary` unless a section explicitly identifies a Coordinator-specific realization owned here.

This Guide does not define:

- Product-specific behavior or acceptance criteria;
- the wire contract, which belongs to the approved Project Protocol YAML;
- Node hard real-time control or local safety behavior;
- Product UI content, alarm semantics, or workflow requirements;
- language-specific syntax or implementation rules.

Approved Product requirements, the Coordinator SDD, the Project Protocol, applicable cybersecurity and safety authorities, platform constraints, and language-specific coding rules take precedence within their owned topics. A conflict shall be reported rather than silently resolved.
---

# 1. Core Architecture Principles

A Coordinator architecture shall preserve the following principles:

1. The UI shall not assemble or parse wire frames directly.
2. Application use cases shall not depend on a concrete serial, USB, TCP, BLE, CAN, or other Transport implementation.
3. Protocol definitions shall come from the approved Project Protocol and generated artifacts where generation is defined.
4. Device state, connection state, command state, and UI presentation state shall be distinguishable.
5. A state value shall have one clear owner and one defined update path.
6. External input shall be validated before it changes application-visible state.
7. Long-running or blocking I/O shall not execute on the UI thread.
8. Queues, buffers, caches, histories, retry counts, and retained records shall be bounded.
9. Disconnect, reconnect, cancellation, timeout, and shutdown behavior shall be designed, not treated as exceptional afterthoughts.
10. Infrastructure concerns such as Transport, file storage, clock access, logging, and operating-system integration should be replaceable behind interfaces.
11. The architecture should allow unit and component testing without the physical Node for logic that does not require real hardware evidence.
12. The Coordinator shall not assume that its local model is authoritative after a reconnect until state reconciliation completes.

---

# 2. Recommended Layer Model

A Coordinator should normally separate the following responsibilities. A small tool may combine adjacent layers when the ownership boundaries remain explicit.

## 2.1 Presentation Layer

Responsibilities:

- render current view state;
- collect user intent;
- display pending, accepted, rejected, timed-out, stale, and disconnected states;
- marshal UI updates onto the UI thread;
- avoid direct Protocol, Transport, file, and device-control logic.

The Presentation Layer should depend on application-facing view models or presentation interfaces, not on a concrete Transport.

## 2.2 Application or Use-Case Layer

Responsibilities:

- coordinate user and system use cases;
- validate use-case preconditions;
- issue commands through an application service or command gateway;
- define timeout, cancellation, and user-visible result behavior;
- coordinate state reconciliation and lifecycle transitions;
- transform domain state into presentation-ready state when appropriate.

The Application Layer should describe intent such as `StartAcquisition`, `ApplyConfiguration`, or `BeginFirmwareUpdate`, not byte-level operations.

## 2.3 Domain and State Layer

Responsibilities:

- represent Coordinator-known device state and application state;
- enforce local invariants that are owned by the Coordinator;
- distinguish observed Node state from requested or predicted state;
- expose immutable snapshots or controlled state transitions;
- provide explicit stale, unknown, invalid, and unavailable representations.

A domain model shall not imply that a requested command has taken effect before the required acknowledgement or observed-state confirmation is received.

## 2.4 Protocol Contract Layer

Responsibilities:

- use generated message identifiers, data types, codecs, validation rules, and Test Vectors;
- encode and decode Protocol messages;
- validate message length, range, enumeration, sequence, and structural constraints;
- remain independent of a concrete Transport where practical.

Hand-maintained copies of generated Protocol constants or wire structures shall not be created in another layer.

## 2.5 Coordinator Session and Protocol Services Layer

Responsibilities:

- own connection lifecycle and link state;
- correlate requests and responses;
- enforce command timeout and cancellation behavior;
- dispatch decoded messages to the correct handler;
- coordinate reconnect and state reconciliation;
- separate Control, Telemetry, Stream, Firmware Update, and diagnostic traffic where required.

This layer should expose application-level operations rather than raw frames. Request/response correlation remains owned by the Protocol Services responsibility, consistent with `Coordinator_Software_Engineering_Rules.md`.

## 2.6 Transport Adapter Layer

Responsibilities:

- open, close, read, write, and report Transport-specific errors;
- translate operating-system or library callbacks into bounded application events;
- avoid Product-specific command semantics;
- implement Transport framing only when framing belongs to the Transport Profile rather than the Protocol contract.

Examples include serial, USB CDC, TCP, UDP, BLE, CAN, and in-process simulation adapters.

## 2.7 Infrastructure Layer

Responsibilities may include:

- structured logging;
- file storage and recording;
- configuration persistence;
- clock and timer services;
- cryptographic providers;
- operating-system integration;
- diagnostic export;
- dependency construction.

Infrastructure implementations should be replaceable for tests.

---

# 3. Dependency Direction

Dependencies should point toward stable application and domain abstractions.

A typical dependency direction is:

```text
Presentation
    -> Application / Use Cases
        -> Domain and Ports
            <- Communication Adapters
            <- Transport Adapters
            <- Storage / Logging / Clock Implementations
```

The following dependencies should be avoided:

- Domain code importing a UI framework;
- Application services importing a concrete serial-port or socket library;
- Protocol codecs calling UI controls;
- Transport callbacks modifying view models directly;
- test code requiring global replacement of static infrastructure state;
- a shared utility module becoming an uncontrolled dependency hub.

Dependency injection may be implemented through constructors, factories, explicit composition roots, or another platform-appropriate mechanism. A dependency-injection framework is optional; explicit dependency ownership is required.

---

# 4. State Ownership Patterns

## 4.1 Single-Writer State Ownership

Each mutable state aggregate should have one logical writer. Other components should receive immutable snapshots, events, or read-only interfaces.

Examples:

- Connection Manager owns connection lifecycle state.
- Request Manager owns pending request correlation state.
- Device State Store owns the current validated Node snapshot.
- Recorder owns file lifecycle and recording status.
- Presentation model owns UI-only selection and layout state.

Single-writer ownership reduces races and makes event order reviewable.

## 4.2 Observed, Requested, and Presented State

The Coordinator should distinguish:

- **Observed State**: validated state reported by the Node;
- **Requested State**: a command or desired setting not yet confirmed;
- **Presented State**: UI-ready representation, including pending and stale indicators.

The Coordinator shall not overwrite observed state merely because a user requested another value.

## 4.3 Snapshot Pattern

A complete state snapshot should be preferred when consumers need a coherent set of related values. Snapshots should carry sufficient identity to evaluate freshness, such as:

- receive timestamp;
- Node timestamp when available;
- sequence or generation number;
- connection/session identity;
- validity or stale status.

## 4.4 Event Pattern

Events are appropriate for non-replaceable occurrences such as alarms, transitions, audit records, and completed actions. Events shall not be silently treated as replaceable state.

## 4.5 Reconciliation Pattern

After initial connect, reconnect, reset, or suspected desynchronization, the Coordinator should:

1. establish the required Protocol or Secure Session;
2. obtain capability and version information;
3. query or receive the authoritative Node state;
4. discard or invalidate pending operations from the prior connection generation unless explicitly resumable;
5. rebuild the local observed-state snapshot;
6. enable commands only when required preconditions are restored.

---

## 4.6 Multi-Node Isolation Pattern

### 4.6.1 Node Registry Pattern

A bounded Node Registry maps authenticated stable identity to the current Node Context. Discovery candidates,
partially registered Nodes, online Nodes, replaced Nodes, and quarantined conflicts shall not share one ambiguous
entry. Duplicate identity or address conflict shall be surfaced rather than resolved by last-writer-wins.

### 4.6.2 Node Context Pattern

Each Node Context shall own its own:

- stable identity and current address or route;
- Transport connection and connection generation;
- Protocol and Secure Session state;
- Capability and negotiated-version state;
- sequence, Replay, and correlation context;
- pending Request table and command lifecycle;
- observed-state store and freshness;
- queue and resource quota;
- logging and audit context;
- lifecycle and Firmware Update transaction state.

### 4.6.3 Connection-to-Node and Route-to-Node Binding

A point-to-point connection may bind one Node without an on-wire address. A shared bus or routed topology shall
provide an unambiguous protected target. The mapping shall be generation-aware. A prior connection, address, or
route shall not deliver state or Responses into a replacement Node Context.

### 4.6.4 Immutable Command Target Binding

An operation shall contain an immutable target snapshot comprising stable Node identity plus the required
Session/connection-generation context. A mutable global `current_device`, current list selection, or active tab is
not a valid operation target. UI selection changes shall affect only subsequently created operations.

### 4.6.5 Per-Node Request and State Patterns

Pending Requests and observed state shall be partitioned by Node context or use globally collision-free identities
that retain Node attribution. A Node reconnect shall cancel or reconcile only that Node's affected work and shall
not reset unrelated Nodes.

### 4.6.6 Shared-Bus Scheduler and Resource Quota Patterns

A shared scheduler shall apply priority, fairness, starvation prevention, and bounded per-Node plus aggregate
queues. A noisy or failed Node shall be rate-limited, rejected, degraded, or quarantined without consuming all
Coordinator resources.

### 4.6.7 Aggregate State Pattern

Aggregate health, Alarm, progress, and availability are projections over per-Node state. The projection shall retain
source identity, freshness, unknown/offline state, and partial failure. Aggregate state shall not overwrite or become
the source of truth for a Node's actual state.

### 4.6.8 Node Removal and Replacement Pattern

Removal invalidates address/route binding, connection generation, Sessions, pending Requests, and stale observed
state under an explicit policy. Replacement at the same address creates a new identity binding and shall not inherit
authorization or operation state.

### 4.6.9 Multi-Target Operation Pattern

A multi-target operation snapshots a target set, creates per-Node sub-operations, and exposes per-Node progress,
timeout, retry, cancellation, and result plus a deterministic aggregate result. It is not a Protocol broadcast and
does not imply rollback.

# 5. Command Pipeline Pattern

A command path should make each stage observable and testable:

```text
User or System Intent
    -> Use-Case Validation
    -> Command Construction
    -> Target Node and Connection-Generation Binding
    -> Authorization / State Check
    -> Encode
    -> Send
    -> Await Response or Observation
    -> Complete / Reject / Timeout / Cancel
    -> Update State and UI
```

A command result should distinguish at least:

- locally rejected before send;
- send failed;
- accepted by the Transport but not acknowledged;
- Protocol rejection;
- completed successfully;
- timed out;
- cancelled;
- connection lost;
- completion state uncertain.

A timeout shall not be presented as proof that the Node did not execute the command. When execution may be uncertain, the Coordinator should reconcile state before allowing a conflicting retry.

Correlation identifiers, sequence numbers, or another Protocol-defined method shall be used when multiple operations may be in flight. Every operation shall remain bound to its intended Node identity, Protocol session, and local connection generation from validation through completion; changing the UI selection shall not retarget an in-flight operation.

---

# 6. Receive and Data Pipeline Pattern

A receive path should separate I/O, framing, decoding, validation, dispatch, state update, recording, and presentation.

```text
Transport Read
    -> Bounded Receive Buffer
    -> Frame Extraction
    -> Decode
    -> Structural and Semantic Validation
    -> Message Classification
    -> Dispatch
        -> Request Completion
        -> State Store Update
        -> Event Publication
        -> Stream Pipeline
        -> Recorder
    -> Presentation Snapshot
```

The pipeline shall define behavior for:

- partial frames;
- multiple frames in one read;
- invalid length;
- unknown or unsupported identifiers;
- out-of-range values;
- duplicate, stale, reordered, or missing sequence values;
- unexpected messages for the current state;
- consumer slowdown;
- buffer exhaustion;
- disconnect during decode or dispatch.

High-rate Stream data should not be routed through the same unbounded event path used for low-rate UI notifications.

---

# 7. Lifecycle and Connection Pattern

Connection lifecycle should be represented explicitly. A typical state model may include:

```text
Disconnected
Connecting
TransportConnected
Negotiating
Synchronizing
Ready
Degraded
Disconnecting
Faulted
```

Project-specific states may be added or combined.

The lifecycle owner shall define:

- allowed transitions;
- entry and exit actions;
- cancellation behavior;
- timeout behavior;
- retry and backoff limits;
- how a manual disconnect differs from link loss;
- how connection generations invalidate stale callbacks and pending work;
- when the UI may enable commands;
- when state is unknown, stale, or reconciled.

Automatic reconnect should be bounded and visible. A reconnect loop shall not continuously consume CPU, flood logs, or repeatedly issue unsafe commands.

---

## 7.1 Security-Session Ownership

Coordinator-side Secure Session state shall have one explicit owner. That owner shall control authentication state, key-context selection, anti-replay state, expiry, rekey, and closure for the local Coordinator peer. Application and UI layers may consume a non-sensitive session-status projection but shall not mutate keys, counters, or acceptance state directly. Application and Bootloader Secure Sessions shall remain separate when required by the Framework or Project Protocol.

# 8. Ports and Adapters Pattern

External dependencies should be represented by narrow interfaces owned by the layer that uses them.

Typical ports include:

- `ITransport` or equivalent;
- `IClock`;
- `ILogSink`;
- `IConfigurationStore`;
- `IRecordingStore`;
- `ICryptoProvider`;
- `IDeviceCommandGateway`;
- `IDeviceStateSource`.

Interfaces should describe needed behavior, not mirror every method of a third-party library.

Adapters shall translate third-party exceptions, callbacks, and status codes into application-owned result types without leaking unnecessary library-specific concepts upward.

---

# 9. Feature and Module Boundaries

A Coordinator should be divided by cohesive capability or use case rather than only by technical file type.

Good module boundaries may include:

- connection and discovery;
- device information and capability negotiation;
- control commands;
- telemetry state;
- streaming acquisition;
- alarms and events;
- configuration;
- firmware update;
- diagnostics;
- recording and export.

Each module should define:

- owned state;
- consumed inputs;
- produced outputs;
- threading model;
- failure behavior;
- persistence behavior;
- Protocol dependencies;
- test boundary.

A module shall not silently write another module's internal state.

---

# 10. Configuration Pattern

Configuration shall distinguish:

- build-time configuration;
- installation or environment configuration;
- user preferences;
- Product-controlled settings;
- Node-reported capabilities and settings;
- security-sensitive secrets.

Configuration should be validated at load time. Invalid configuration shall not silently fall back to a value that may change Product behavior unless the fallback is approved and logged.

Secrets shall not be stored in ordinary preference files or emitted to logs.

The configuration model should preserve schema version and migration behavior when persisted formats may evolve.

---

# 11. Error and Result Pattern

Errors should preserve enough context for recovery and diagnosis without exposing secrets.

A structured error or result should identify, as applicable:

- operation;
- category;
- stable error code;
- user-safe message;
- diagnostic message;
- underlying exception or status;
- retryability;
- connection generation;
- correlation identifier;
- relevant Protocol or Transport identity.

Exceptions may be used for unexpected failures according to the language standard. Expected outcomes such as command rejection, timeout, cancellation, and disconnected state should normally be represented explicitly rather than treated as generic unexpected exceptions.

---

# 12. Pattern Selection Guidance

| Situation | Preferred Pattern |
|---|---|
| One user action produces one command and result | Application use case plus command gateway |
| Several screens consume the same validated device state | Central single-writer state store with immutable snapshots |
| High-rate waveform or sample data | Dedicated bounded Stream pipeline with controlled downsampling |
| Transport must be replaceable | Port and Transport adapter |
| Hardware is unavailable for logic testing | Simulator or mock adapter behind the same port |
| Reconnect may deliver stale callbacks | Connection-generation token and cancellation scope |
| Several independent features share one link | Communication orchestration with explicit dispatch and ownership |
| Long operation such as update or export | Explicit operation state machine with progress, cancellation, and recovery |

---

# 13. Architecture Anti-Patterns

The following patterns shall be rejected or explicitly justified:

1. UI event handlers directly reading, writing, encoding, or decoding Protocol frames.
2. A global mutable object used by unrelated modules without defined ownership.
3. Transport callbacks updating controls or application state from arbitrary threads.
4. One unbounded queue for commands, telemetry, streaming data, logs, and file recording.
5. Local state being treated as authoritative after reconnect without reconciliation.
6. A command being shown as successful immediately after a write call.
7. Business logic embedded in third-party callback handlers.
8. Generated Protocol definitions copied and edited manually.
9. Catching all exceptions and continuing without restoring a known state.
10. A generic utility or manager class accumulating unrelated responsibilities.
11. Hidden retries that can repeat a non-idempotent operation.
12. Startup order depending on uncontrolled static initialization side effects.

---

# 14. Architecture Review Checklist

Before approving a Coordinator architecture, verify:

- [ ] Applicable Product, Protocol, security, UI, and platform authorities are identified.
- [ ] Layer responsibilities and dependency direction are documented.
- [ ] UI code does not own Protocol or Transport behavior.
- [ ] Mutable state, including Coordinator-side Secure Session state, has clear ownership and update paths.
- [ ] Observed, requested, pending, stale, and presented state are distinguishable.
- [ ] Command completion, rejection, timeout, cancellation, and uncertain outcome are defined.
- [ ] Receive, decode, validation, dispatch, recording, and presentation stages are separated appropriately.
- [ ] High-rate Stream paths are bounded and isolated from low-rate control paths.
- [ ] Connection lifecycle, reconnect, reconciliation, and shutdown are explicit.
- [ ] Stale callbacks and prior connection generations cannot corrupt current state.
- [ ] Multi-Node target identity, session state, pending work, quotas, and observed state are isolated.
- [ ] Transport and infrastructure dependencies can be replaced for tests where practical.
- [ ] Configuration ownership, validation, migration, and secret handling are defined.
- [ ] Error propagation preserves diagnostic context without exposing sensitive data.
- [ ] The architecture identifies required unit, component, integration, target, and human validation evidence.
- [ ] Deviations from preferred patterns have documented rationale and review scope.
