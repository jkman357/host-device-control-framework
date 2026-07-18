# Coordinator Software Engineering Rules

**Canonical Filename:** `Coordinator_Software_Engineering_Rules.md`  
**Document Version:** V1.0.1  
**Status:** Draft for Review  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-18  
**Language:** English  
**Intended Audience:** Human engineers, software architects, reviewers, test engineers, code generators, and AI-assisted engineering systems  
**Repository Role:** Normative engineering authority for Coordinator-owned software  

---

## Copyright and Use

Copyright © 2026 Ray Yang. All rights reserved unless a repository-level license states otherwise.

This document is independently authored. External standards and guidance are referenced for context and are not reproduced as substitute standards. Third-party documents remain subject to their respective copyright and license terms.

---

## Version History

| Version | Date | Status | Summary |
|---|---|---|---|
| V1.0.1 | 2026-07-18 | Draft for Review | Corrected architecture-flow representation, clarified source dependency direction, introduced bootstrap diagnostics during startup, linked the required Project profile to the Framework Application Analysis, and clarified document approval versus implementation conformance. |
| V1.0.0 | 2026-07-18 | Draft for Review | Initial full baseline covering Coordinator software architecture, concurrency, state ownership, communication integration, diagnostics, configuration, security, testability, release governance, and AI-assisted implementation controls. |

---

# Part I — Document Governance

## 1. Purpose

This document defines engineering rules for software that performs the **Coordinator** role in a Coordinator/Node system.

The Coordinator may be implemented as:

- A desktop application.
- A headless service.
- An engineering or manufacturing tool.
- A gateway.
- A supervisory controller.
- A test application.
- A web-backed service with a local or remote user interface.
- Another software component that coordinates one or more Nodes.

The rules intentionally do not bind the Coordinator to a specific operating system, user-interface framework, programming language, runtime, or physical computer category.

This document governs architecture, responsibility boundaries, state ownership, concurrency, communication integration, error handling, diagnostics, configuration, security, testability, release behavior, and engineering evidence.

Language-specific implementation rules shall be defined in separate documents such as:

- `CSharp_Coding_Rules.md`
- `Java_Coding_Rules.md`
- `Cpp_Coding_Rules.md`

## 2. Normative Language

The keywords **shall**, **shall not**, **should**, **should not**, and **may** are normative.

- **Shall** indicates a mandatory requirement.
- **Shall not** indicates a mandatory prohibition.
- **Should** indicates a recommended practice. A deviation requires an engineering reason.
- **Should not** indicates a discouraged practice. Use requires an engineering reason.
- **May** indicates an allowed option.

Examples and rationale are non-normative unless explicitly identified as requirements.

## 3. Scope

This document applies to Product-owned Coordinator software, including:

- User-interface applications.
- Application orchestration.
- Domain logic.
- Communication sessions.
- Protocol integration.
- Transport adapters.
- Device discovery.
- Data acquisition and visualization.
- Device configuration.
- Logging and diagnostics.
- Firmware update orchestration.
- Local storage.
- Export and import functions.
- Engineering, manufacturing, service, and test utilities.
- Coordinator-side security-session handling.
- Coordinator-side generated protocol artifacts.

This document does not replace:

- Product requirements.
- Safety requirements.
- Cybersecurity requirements.
- The authoritative Coordinator/Node control framework.
- The authoritative Project Protocol definition.
- Platform vendor documentation.
- Language specifications.
- Verification procedures.
- Regulatory obligations.

## 4. Authority and Precedence

The following precedence shall apply when requirements conflict:

1. Applicable law, regulation, safety requirements, and approved product requirements.
2. Approved system and software requirements.
3. `Coordinator_Node_Control_Framework.md`.
4. The approved Project Protocol YAML and its definition guide.
5. This document.
6. Language-specific coding rules.
7. Project-local conventions.
8. Tool defaults and personal preference.

A lower-authority document shall not weaken or reinterpret a higher-authority requirement.

This document shall not duplicate detailed Protocol field definitions, message identifiers, cryptographic parameters, or wire layouts. Such content belongs to the Project Protocol authority.

## 5. One Rule, One Authority

A normative engineering decision shall have one primary authority location.

When this document summarizes a rule owned elsewhere, the summary shall be labeled as one of:

- `Derived conformance summary`
- `Non-authoritative checklist`
- `Project-specific profile`

Repeated summaries shall not silently become independent authorities.

## 6. Stable Document Identity

The maintained Markdown filename shall remain:

```text
Coordinator_Software_Engineering_Rules.md
```

The filename shall not contain a document version.

Document versions shall be represented through:

- Document metadata.
- Version history.
- Git history.
- Git tags.
- Releases.
- Controlled archive package names.

---

# Part II — Coordinator Role and Engineering Principles

## 7. Coordinator Role

A Coordinator initiates, supervises, aggregates, presents, or orchestrates interactions with one or more Nodes.

Coordinator and Node are **roles**, not permanent hardware identities.

The same physical product may perform different roles in different relationships. Software shall not assume that a Coordinator is always a desktop PC or that a Node is always an MCU.

## 8. Core Engineering Principles

Coordinator software shall be designed according to the following principles:

1. **Protocol and Transport separation.**
2. **Single ownership of authoritative state.**
3. **Explicit concurrency and lifecycle management.**
4. **Bounded resource behavior.**
5. **Observable failures.**
6. **Testable logic outside the UI framework.**
7. **Deterministic shutdown and recovery.**
8. **Typed configuration and data models.**
9. **Generated-code boundaries.**
10. **Human approval of requirements, architecture, safety, and release evidence.**
11. **Cross-implementation interoperability.**
12. **Least privilege and explicit trust boundaries.**
13. **No silent fallback that changes product behavior.**
14. **No UI-driven architecture.**
15. **No transport-specific business logic.**

## 9. Prohibited Architectural Shortcuts

The following are prohibited in Product-owned Coordinator software unless an approved project-specific deviation exists:

- Encoding or decoding Protocol frames directly in UI event handlers.
- Opening Serial, USB, socket, or device handles directly from a Form, Window, Page, View, or Controller.
- Updating UI controls directly from a communication callback or background thread.
- Treating a UI label, button state, or icon as authoritative device state.
- Using global mutable variables as the primary communication between layers.
- Allowing a Transport adapter to interpret domain meaning.
- Allowing the Protocol parser to depend on a UI framework.
- Swallowing exceptions to keep the application appearing operational.
- Starting unowned background threads, timers, or tasks.
- Implementing reconnect behavior as scattered ad hoc retry loops.
- Manually editing generated Protocol source files.
- Persisting secrets, credentials, keys, tokens, or protected data in plaintext.
- Blocking the UI thread while waiting for device I/O.
- Using an unbounded queue for continuous incoming data without an approved backpressure policy.
- Using log output as the only record of authoritative state.

---

# Part III — Required Architecture

## 10. Logical Layer Model

A Coordinator implementation shall define explicit logical layers.

The default **policy dependency model** is:

```text
Presentation
    ↓ depends on
Application
    ↓ depends on
Domain

Application
    ↓ depends on
Coordinator Session / Protocol Port

Protocol Adapter
    ↑ implements the Protocol Port
    ↓ depends on
Transport Port

Serial / USB / TCP / Test Transport Adapter
    ↑ implements the Transport Port

Infrastructure supplies concrete adapters and platform services.
```

The diagram describes **source-code dependency direction**. It does not describe all runtime event or data flow.
Runtime events and data may flow in both directions through declared interfaces, callbacks, events, queues, or immutable messages.

The Domain layer shall not depend on Protocol wire types, Transport implementations, UI frameworks, or Infrastructure implementations.

Supporting cross-cutting services may include:

```text
Logging
Configuration
Security
Time
Persistence
Diagnostics
Dependency Composition
```

The exact folder names may differ, but responsibilities and dependency direction shall remain explicit. Architecture diagrams shall identify whether an arrow represents a source dependency, runtime call, or event/data flow when the meaning could be ambiguous.

## 11. Presentation Layer

The Presentation layer owns:

- Rendering.
- User input collection.
- View-local state.
- Navigation.
- Presentation formatting.
- User-facing validation feedback.
- Dispatch of user intent to the Application layer.

The Presentation layer shall not own:

- Protocol framing.
- Transport handles.
- Device connection state.
- Firmware update state.
- Security-session state.
- Business decisions.
- Persistent domain state.
- Retry policy.
- Message correlation.
- Device command sequencing.

UI event handlers shall remain thin and shall delegate work to an Application service, command, or use-case object.

## 12. Application Layer

The Application layer owns use-case orchestration, including:

- Connect and disconnect workflows.
- Device discovery workflows.
- Command execution.
- User-request validation that depends on current system state.
- Session lifecycle coordination.
- Firmware update workflow coordination.
- Data acquisition start and stop.
- Import and export orchestration.
- Cancellation and progress reporting.
- Mapping domain results to presentation-ready outcomes.

The Application layer shall coordinate components but shall not contain wire-format parsing or direct operating-system API calls unless the project explicitly assigns those responsibilities.

## 13. Domain Layer

The Domain layer owns product and problem-domain meaning, including:

- Domain entities.
- Value objects.
- State-transition rules.
- Validation rules.
- Invariants.
- Device capability interpretation.
- Domain result types.
- Domain events.
- Unit conversion when conversion is part of domain meaning.

The Domain layer should remain independent of:

- UI frameworks.
- Serial-port libraries.
- USB libraries.
- Socket implementations.
- File-dialog APIs.
- Logging framework implementations.
- Database implementations.
- Protocol byte layout.

## 14. Protocol Services Layer

The Protocol Services layer owns:

- Message model integration.
- Encoding and decoding.
- Framing integration.
- Request/response correlation.
- Message category handling.
- Protocol-version negotiation.
- Capability exchange.
- Session message routing.
- Protocol error classification.
- Generated Protocol artifact integration.

It shall not own:

- Physical device discovery.
- Operating-system handle management.
- UI rendering.
- Product workflow decisions.
- Arbitrary retry behavior outside the approved policy.

## 15. Transport Abstraction Layer

The Transport layer owns:

- Opening and closing a communication channel.
- Reading and writing bytes or transport records.
- Transport-specific configuration.
- Transport-specific errors.
- Transport-level cancellation.
- Detection of physical or logical link loss.
- Transport-specific buffering that does not alter Protocol semantics.

Examples include:

- Serial.
- USB CDC.
- USB vendor-specific.
- TCP.
- UDP.
- Bluetooth.
- CAN gateway.
- Named pipe.
- Test loopback.

The Transport layer shall expose a transport-neutral contract to the Protocol layer.

## 16. Infrastructure Layer

Infrastructure owns operating-system and third-party integration such as:

- File system.
- Database.
- Registry or platform settings.
- Credential storage.
- Clock implementations.
- Process services.
- Update package access.
- Network adapters.
- Platform notifications.
- External libraries.

Infrastructure dependencies shall be isolated behind interfaces or adapters when replacement, testing, or platform migration is reasonably expected.

## 17. Dependency Direction

Source-code dependencies shall point toward more stable policy and domain abstractions.

Runtime calls, callbacks, events, and data flow may move in either direction through declared contracts. Runtime flow shall not be mistaken for source dependency ownership.

The Domain layer shall remain independent of concrete Protocol, Transport, UI, and Infrastructure implementations. The Application layer may depend on project-owned ports or interfaces that are implemented by Protocol and Infrastructure adapters.

A lower-level mechanism shall not become the owner of higher-level behavior merely because it receives an event first.

Circular project references and cyclic module dependencies are prohibited.

Dependency inversion shall be used where a policy layer needs a mechanism supplied by Infrastructure.

## 18. Composition Root

Application-wide object composition shall occur in an identifiable Composition Root.

The Composition Root shall own:

- Concrete dependency selection.
- Configuration binding.
- Lifetime selection.
- Startup validation.
- Registration of transport and protocol adapters.
- Top-level exception boundary.
- Application shutdown coordination.

Business logic shall not use a global service locator to resolve arbitrary dependencies.

---

# Part IV — State and Lifecycle

## 19. Authoritative State Ownership

Every state shall have one authoritative owner.

Examples:

| State | Required Owner |
|---|---|
| Local transport state | Transport instance |
| Local Protocol session state | Protocol session instance |
| Coordinator-side security-session state | Coordinator security-session component |
| Mirrored Node state | Device model or session model |
| Firmware update transaction state | Update workflow |
| UI selection and layout state | Presentation layer |
| Persisted configuration | Configuration service |
| Current application lifecycle state | Application host |

Mirrored remote state shall be identified as observational. It shall not be treated as authority over the remote peer.

Each peer shall remain responsible for its own local security-session acceptance, expiration, anti-replay state, and key selection.

## 20. State Machine Requirements

A workflow with meaningful lifecycle behavior shall use an explicit state model when any of the following apply:

- More than two operational states.
- Invalid transitions are possible.
- Recovery depends on the failure point.
- Timeouts or retries affect behavior.
- The workflow spans asynchronous operations.
- The workflow controls safety-related or update-related actions.
- Multiple UI screens observe the same workflow.

State transitions shall be:

- Named.
- Validated.
- Logged at an appropriate level.
- Testable.
- Rejectable when invalid.
- Associated with a reason or trigger when diagnostic value exists.

## 21. Connection Lifecycle

Connection behavior shall define at least:

```text
Disconnected
Discovering
OpeningTransport
TransportOpen
NegotiatingProtocol
EstablishingSession
Connected
Recovering
Disconnecting
Faulted
```

Projects may refine or combine states, but shall not reduce meaningful behavior to a single Boolean such as `IsConnected`.

The Coordinator shall distinguish:

- Physical transport availability.
- Open transport.
- Protocol compatibility.
- Authenticated or authorized session.
- Node readiness.
- Application workflow readiness.

## 22. Startup

Startup shall be staged.

A recommended sequence is:

1. Initialize the process host.
2. Initialize minimal bootstrap diagnostics that do not depend on Product configuration.
3. Load and validate configuration.
4. Configure the full logging and diagnostic pipeline.
5. Validate required directories and permissions.
6. Compose services.
7. Initialize local data stores.
8. Register transports.
9. Create application state.
10. Start the UI or service host.
11. Begin optional discovery or connection only according to policy.

Bootstrap diagnostics may be simpler than the normal logging system, but shall be sufficient to report configuration and early-startup failures.

A startup failure shall identify the failed stage and shall not leave partially initialized global state.

## 23. Shutdown

Shutdown shall be deterministic and idempotent.

The shutdown sequence shall:

- Stop accepting new user or external work.
- Cancel active operations.
- Stop periodic producers.
- Stop data acquisition.
- End or abandon Protocol transactions according to policy.
- Close the security session.
- Close transports.
- Flush required logs and persistent data.
- Release resources.
- Report incomplete shutdown when required.

The process shall not rely solely on operating-system termination to release device or file resources.

## 24. Reconnect and Recovery

Reconnect behavior shall be a controlled policy, not an infinite loop.

The policy shall define:

- Which failures are recoverable.
- Initial delay.
- Backoff behavior.
- Maximum attempt count or maximum elapsed time.
- User cancellation.
- Whether commands may queue while disconnected.
- Whether stale queued work is discarded.
- How Protocol and security sessions are re-established.
- How the UI represents recovery.
- When manual intervention is required.

A new transport connection shall not automatically imply that the previous Protocol or security session remains valid.

---

# Part V — Concurrency, Timing, and Responsiveness

## 25. Concurrency Model

Each project shall document its concurrency model.

The model shall identify:

- UI or main thread.
- I/O completion mechanism.
- Worker tasks or threads.
- Protocol receive processing.
- Data-processing workers.
- Timers.
- Cancellation ownership.
- Shared-state synchronization.
- Shutdown order.
- Maximum expected concurrency.

Concurrency shall be introduced only for a defined reason.

## 26. UI Responsiveness

A Coordinator with a UI shall not perform blocking I/O, long computation, uncontrolled waiting, or synchronous device operations on the UI thread.

Background components shall not directly access UI controls.

Updates to UI state shall pass through the framework-approved dispatch or synchronization mechanism.

High-rate input shall not cause one UI update per incoming record unless the update rate is explicitly demonstrated to be safe.

## 27. Task and Thread Ownership

Every task, thread, timer, subscription, and callback source shall have an owner.

The owner shall define:

- Creation.
- Start condition.
- Stop condition.
- Cancellation.
- Exception observation.
- Disposal.
- Shutdown order.

Fire-and-forget work is prohibited unless it is routed through an owned supervisor that records failures and shutdown state.

## 28. Cancellation

Long-running or externally waiting operations shall support cancellation where cancellation is meaningful.

Cancellation shall be cooperative.

A cancelled operation shall:

- Stop initiating new sub-operations.
- Release owned resources.
- Preserve valid persistent state.
- Distinguish cancellation from failure.
- Avoid reporting success.
- Avoid converting cancellation into an unrelated generic error.

## 29. Timeout

Every operation that waits on a Node, transport, external process, file lock, network endpoint, or user-independent condition shall have a defined timeout or a documented reason for no timeout.

Timeout values shall be named configuration or policy values.

Timeout handling shall not leave unresolved correlation entries, locked resources, stale busy state, or invisible background work.

## 30. Backpressure

Continuous data paths shall define:

- Producer rate.
- Consumer rate.
- Queue type.
- Queue capacity.
- Overflow behavior.
- Drop or coalescing policy.
- Diagnostic counters.
- Shutdown behavior.

An unbounded producer-consumer queue is prohibited for streaming, telemetry, logging, or UI update traffic.

Telemetry, Stream, Event, Alarm, Fault, and Log data shall follow the semantics defined by the authoritative Framework and Protocol documents.

## 31. Time

The project shall distinguish:

- Wall-clock time.
- UTC time.
- Local display time.
- Monotonic elapsed time.
- Node-originated time.
- Coordinator-originated time.
- Synchronized time.
- Unknown or invalid time.

Elapsed durations and timeout decisions shall use a monotonic source.

Persisted and exchanged absolute timestamps should use UTC unless the authoritative Protocol defines another epoch.

Local time shall be used for user presentation only unless explicitly required.

Clock changes shall not corrupt elapsed-time calculations.

## 32. Periodic Work

Periodic work shall define whether scheduling is:

- Fixed-delay.
- Fixed-rate.
- Deadline-based.
- Event-driven.
- Best effort.

Periodic callbacks shall not overlap unless overlap is explicitly allowed.

Missed periods shall not automatically cause an uncontrolled burst of catch-up executions.

---

# Part VI — Communication and Protocol Integration

## 33. Protocol Authority

The Project Protocol YAML is the authority for:

- Message identity.
- Direction.
- Category.
- Field type.
- Range.
- Unit.
- Optionality.
- Length.
- Version applicability.
- Capability relationships.
- Security attributes.
- Request/response pairing.
- Transport envelope constraints when declared.

Handwritten implementation code shall not silently redefine these items.

## 34. Protocol/Transport Separation

The Protocol layer shall not depend on a concrete Serial, USB, TCP, or other transport implementation.

A Transport shall deliver bytes or transport records without interpreting application meaning.

Changing transport shall not require rewriting domain logic.

## 35. Receive Pipeline

The receive pipeline shall handle:

- Partial records.
- Multiple records in one read.
- Corrupt records.
- Unknown messages.
- Unsupported versions.
- Invalid lengths.
- Invalid field ranges.
- Duplicate messages.
- Out-of-order messages when relevant.
- Replay detection when required.
- Link closure during a record.
- Cancellation and shutdown.

Malformed external data shall be rejected before it becomes trusted domain state.

## 36. Request and Response

Request/response behavior shall define:

- Correlation identity.
- Timeout.
- Duplicate response handling.
- Late response handling.
- Cancellation.
- Concurrent request limits.
- Error response mapping.
- Session-loss behavior.

A response shall not be matched only by message type when multiple concurrent requests of the same type are possible.

## 37. Command Execution

A user request shall not be reported as completed merely because bytes were written.

The application shall distinguish:

```text
User intent accepted
Local validation passed
Request transmitted
Node acknowledged
Operation started
Operation completed
Operation failed
Operation state unknown
```

The exact stages depend on the Protocol, but ambiguous completion shall be avoided.

## 38. Streaming and Telemetry

Continuous data handling shall separate:

- Acquisition.
- Protocol validation.
- Time ordering.
- Buffering.
- Processing.
- Persistence.
- UI sampling or rendering.

The UI rendering rate may be lower than the acquisition rate.

Dropping a UI rendering update shall not silently imply dropping authoritative recorded data.

## 39. Firmware Update

Firmware update orchestration shall define:

- Package selection.
- Manifest validation.
- Product and hardware compatibility.
- Image authenticity and integrity.
- Application-session exit.
- Bootloader discovery.
- Independent Bootloader session establishment.
- Chunk transfer.
- Progress and retry.
- Final validation.
- Activation.
- Reconnection.
- Version confirmation.
- Recovery from interruption.

Update Transaction identity and security-session identity shall remain separate.

The Coordinator shall not mark an update successful until post-activation evidence required by the Project has been received.

## 40. Generated Protocol Code

Generated files shall:

- Be identifiable.
- Include generator and schema identity when practical.
- Be reproducible.
- Be excluded from manual edits.
- Be validated by regeneration in CI or an equivalent controlled process.
- Have a defined integration boundary.

Product-owned handwritten code shall wrap or consume generated artifacts rather than modifying them.

Generated code is not exempt from compilation, interoperability, safety, or verification requirements.

---

# Part VII — Error, Logging, and Diagnostics

## 41. Error Taxonomy

The project shall distinguish at least:

- User input error.
- Configuration error.
- Transport error.
- Protocol error.
- Compatibility error.
- Authentication or authorization error.
- Node-reported error.
- Application state error.
- Persistence error.
- Resource exhaustion.
- Dependency failure.
- Internal software defect.
- Cancellation.
- Timeout.

Errors from different categories shall not be collapsed into a single message such as `Communication failed`.

## 42. Error Handling

An error boundary shall either:

- Handle the error.
- Convert it to a defined higher-level error.
- Add context and rethrow without losing the original cause.
- Transition the owning state machine to a defined state.
- Terminate the affected operation safely.

Empty catch blocks and silent failure are prohibited.

A user-facing message shall not be the only diagnostic record for an engineering-significant failure.

## 43. Recoverability

Each significant error shall be classified as:

- Automatically recoverable.
- Recoverable after retry.
- Recoverable after reconnect.
- Recoverable after user action.
- Recoverable after restart.
- Non-recoverable for the current operation.
- Fatal to the process.

Recovery actions shall not be attempted when they can worsen data integrity, security, or device state.

## 44. Logging

Logging shall be structured enough to answer:

- What happened?
- When did it happen?
- Which application version was running?
- Which component reported it?
- Which Coordinator session and Node were involved?
- Which operation or correlation identity was involved?
- What state transition occurred?
- What error category and original exception were present?
- What recovery action was taken?

The log policy shall define:

- Levels.
- Retention.
- Rotation.
- File location.
- Encoding.
- Timestamp format.
- Privacy masking.
- Raw frame policy.
- Production and engineering differences.
- Export procedure.

## 45. Sensitive Data

Logs shall not contain secrets, private keys, passwords, access tokens, session keys, unmasked credentials, or protected personal data unless explicitly required and protected by an approved policy.

Raw Protocol logging shall be disabled or restricted when records may contain sensitive data.

## 46. Diagnostic Counters

Communication components should expose counters for:

- Bytes and records received.
- Bytes and records transmitted.
- Decode failures.
- Invalid length.
- Invalid range.
- Unknown message.
- Timeout.
- Retry.
- Dropped queue items.
- Reconnect attempts.
- Session establishment failures.
- Late responses.
- Duplicate responses.

Counters shall not silently overflow in a way that creates misleading diagnostics.

## 47. Audit-Relevant Events

When required by product or regulatory context, the application shall maintain a controlled record of:

- User login or identity.
- Configuration changes.
- Device selection.
- Commands that alter device behavior.
- Firmware update actions.
- Export and import operations.
- Security events.
- Time changes.
- Administrative actions.

Audit records and diagnostic logs may have different retention and access requirements.

---

# Part VIII — Configuration, Persistence, and Data

## 48. Typed Configuration

Configuration shall be represented by typed models or an equivalent schema-controlled mechanism.

String keys shall not be scattered through Product-owned code.

Each configuration item shall define:

- Name.
- Type.
- Unit.
- Valid range.
- Default.
- Source.
- Persistence behavior.
- Security classification.
- Version applicability.
- Validation behavior.

## 49. Configuration Validation

Configuration shall be validated before use.

Invalid configuration shall not silently fall back when the fallback changes product behavior.

The application shall identify:

- Missing values.
- Unknown values.
- Invalid ranges.
- Unsupported versions.
- Conflicting values.
- Migration failure.

## 50. Configuration Versioning and Migration

Persisted configuration shall have a version or an equivalent schema identity.

Migration shall be:

- Explicit.
- Testable.
- Logged.
- Reversible when required.
- Safe against partial writes.

Unsupported future configuration versions shall not be silently interpreted as the current format.

## 51. Atomic Persistence

Critical persistent updates shall use an atomic or recoverable write strategy.

The design shall consider:

- Temporary file and replace.
- Transaction.
- Journaling.
- Checksum.
- Backup copy.
- Recovery on startup.
- Disk-full behavior.
- Process termination during write.

## 52. Data Ownership

Stored data shall have an identified owner and retention policy.

The application shall distinguish:

- Configuration.
- Calibration.
- Device-originated measurement data.
- User preferences.
- Logs.
- Audit records.
- Temporary cache.
- Export packages.
- Firmware images.
- Security material.

These categories shall not be mixed merely for implementation convenience.

## 53. Import and Export

Imported data shall be treated as untrusted input.

Import shall validate:

- Format.
- Schema version.
- Length.
- Range.
- Integrity.
- Identity.
- Compatibility.
- Required signatures when applicable.
- Path and filename safety.

Export shall define:

- Data scope.
- Version.
- Units.
- Time basis.
- Encoding.
- Privacy treatment.
- Integrity metadata when required.

---

# Part IX — Security and Trust Boundaries

## 54. Security Architecture

Security requirements shall be derived from the approved threat model, product requirements, and authoritative Protocol security model.

The Coordinator shall explicitly define trust boundaries for:

- User.
- Local process.
- Local files.
- Device.
- Transport.
- Network.
- Update package.
- External service.
- Third-party library.
- Plugin or extension.
- Engineering mode.

## 55. Least Privilege

The application shall operate with the minimum privileges required.

Administrative privilege shall not be required only for implementation convenience.

Privileged operations shall be isolated and justified.

## 56. Secret Storage

Secrets shall not be:

- Hard-coded in source.
- Stored in plaintext configuration.
- Written to normal logs.
- Embedded in distributable test data.
- Passed through command lines when exposure is possible.

Platform credential storage or an approved secure storage mechanism shall be used.

## 57. Input Validation

All external input shall be validated at the trust boundary, including:

- Protocol data.
- User input.
- Files.
- Command-line arguments.
- Environment variables.
- Registry or system settings.
- Network data.
- Plugin data.
- Update packages.

Validation shall occur before side effects.

## 58. Cryptographic Use

Cryptographic algorithms, key sizes, nonces, signatures, key derivation, and session rules shall come from approved security requirements and the Protocol authority.

Application developers shall not invent custom cryptographic schemes.

Cryptographic failure shall fail closed unless an approved requirement specifies otherwise.

## 59. Update Security

Firmware and application update packages shall be authenticated according to the approved update design.

A hash alone does not establish authenticity.

The Coordinator shall verify package identity and compatibility before initiating a device update.

## 60. Security Logging

Security-significant events shall be logged without exposing secrets.

Repeated authentication failures, invalid signatures, replay rejection, unauthorized actions, or integrity failures shall be distinguishable from ordinary communication failure.

---

# Part X — Dependency and Platform Governance

## 61. Third-Party Dependency Approval

A new dependency shall have:

- A defined purpose.
- An owner.
- License review.
- Version policy.
- Source and integrity record.
- Security-vulnerability review.
- Maintenance assessment.
- Replacement or removal strategy when significant.
- Test coverage at the integration boundary.

A large dependency shall not be introduced to implement a trivial function without justification.

## 62. Version Control

Dependency versions shall be reproducible.

Floating versions are prohibited for controlled builds unless the build system resolves and records an immutable dependency set.

Dependency updates shall be reviewed for:

- API changes.
- Behavior changes.
- License changes.
- Security fixes.
- Deployment impact.
- Data-format changes.
- Runtime requirements.

## 63. Framework Isolation

UI, logging, serialization, database, and transport frameworks should be isolated behind project-owned boundaries where framework replacement or long-term maintenance risk is significant.

Domain rules shall not be expressed only through framework-specific attributes or callbacks when doing so prevents independent testing or reuse.

## 64. Platform-Specific Code

Platform-specific code shall be isolated and identifiable.

The project shall document:

- Supported operating systems.
- Architecture.
- Required runtime.
- Required drivers.
- Native dependencies.
- Privilege requirements.
- Installer behavior.
- File locations.
- Upgrade behavior.
- Uninstall behavior.

## 65. Native Interoperability

Native interoperability shall define:

- Ownership of allocated memory.
- Calling convention.
- Character encoding.
- Structure packing.
- Integer widths.
- Lifetime.
- Thread affinity.
- Error propagation.
- Version compatibility.
- Deployment of native binaries.

Interop boundaries shall have focused tests.

---

# Part XI — Application Profiles

## 66. Desktop Application Profile

A desktop Coordinator shall additionally define:

- UI framework.
- UI thread model.
- Navigation ownership.
- Dialog policy.
- Long-operation progress and cancellation.
- Window closing behavior.
- Multi-window state sharing.
- Display refresh policy.
- High-DPI behavior.
- Localization and culture.
- Accessibility requirements.
- Device-disconnect presentation.
- Prevention of duplicate user commands.
- Engineering and production modes.

Closing a window shall not implicitly abandon an active operation unless the operation owner handles the cancellation.

## 67. Headless Service Profile

A headless Coordinator shall additionally define:

- Service startup and readiness.
- Service account.
- Health endpoint or health signal.
- Configuration reload behavior.
- Graceful shutdown.
- Process supervision.
- Restart policy.
- Remote control authorization.
- Log and metric collection.
- Deployment and rollback.
- Handling of attached devices across service restart.

## 68. Engineering Tool Profile

An engineering or manufacturing Coordinator shall additionally define:

- Intended user role.
- Access control.
- Allowed commands.
- Production versus engineering-only behavior.
- Test fixture identity.
- Traceability of test configuration.
- Result retention.
- Override controls.
- Prevention of accidental use on unsupported products.
- Exported evidence format.

Engineering capability shall not silently ship in a production application.

---

# Part XII — Testability and Verification

## 69. Testable Design

The design shall allow Protocol, domain, and workflow behavior to be tested without physical hardware where practical.

Replaceable test boundaries should include:

- Transport.
- Clock.
- Timer.
- File system.
- Credential store.
- Device session.
- Update package source.
- External service.
- User notification.
- Logger sink.

## 70. Required Test Levels

Projects shall define applicable tests from:

- Unit tests.
- Component tests.
- Protocol codec tests.
- Transport adapter tests.
- State-machine tests.
- Integration tests.
- Hardware-in-the-loop tests.
- UI tests.
- Installer tests.
- Upgrade and rollback tests.
- Fault-injection tests.
- Security tests.
- Long-duration tests.
- Performance tests.
- Cross-implementation interoperability tests.

UI tests shall not be the only validation of domain or Protocol logic.

## 71. Protocol Test Requirements

Protocol integration shall test:

- Known valid vectors.
- Boundary values.
- Minimum and maximum lengths.
- Partial input.
- Multiple records.
- Unknown message.
- Unsupported version.
- Invalid enum.
- Invalid reserved bits.
- Corrupt integrity field.
- Timeout.
- Duplicate response.
- Late response.
- Disconnect during transaction.
- Cross-implementation interoperability.
- Cross-language interoperability for every language pair in scope.

## 72. Fault Injection

Fault injection shall cover applicable cases such as:

- Link removal.
- Process restart.
- Node reset.
- Corrupt record.
- Delayed response.
- Dropped response.
- Duplicate response.
- Disk full.
- Read-only directory.
- Configuration corruption.
- Dependency failure.
- Clock change.
- Resource exhaustion.
- Update interruption.
- Invalid certificate or signature.
- Authentication failure.

## 73. Deterministic Tests

Tests shall control time, randomness, and external state where practical.

Tests shall not depend on arbitrary sleep delays when an observable condition can be awaited.

A flaky test shall be treated as a defect in the test, implementation, or environment and shall not be normalized.

## 74. Evidence

Verification evidence shall identify:

- Software version.
- Protocol version.
- Configuration.
- Environment.
- Test data.
- Hardware identity when applicable.
- Expected result.
- Actual result.
- Pass/fail result.
- Deviations.
- Reviewer.

---

# Part XIII — Build, Release, and Deployment

## 75. Reproducible Build

A controlled build shall identify:

- Source revision.
- Toolchain.
- Runtime target.
- Dependency lock or resolved versions.
- Generator version.
- Protocol schema identity.
- Build configuration.
- Build timestamp policy.
- Signing identity when applicable.

## 76. Build Warnings

Product-owned code shall build with the project-approved warning level.

New warnings shall not be accepted without review.

Warnings shall not be globally disabled to hide local issues.

## 77. Static Analysis

Applicable static analysis shall run in developer workflow or CI.

Suppressions shall include:

- Rule identity.
- Scope.
- Reason.
- Reviewer or approval mechanism.
- Review date when required.

Broad suppression of an entire analyzer category is prohibited without documented justification.

## 78. Packaging

Packages shall contain only required files.

The package shall identify:

- Application version.
- Supported platform.
- Runtime prerequisites.
- Native dependencies.
- Configuration defaults.
- License notices.
- Integrity or signature information when required.

Debug symbols and engineering tools shall be handled according to release policy.

## 79. Upgrade and Rollback

Application upgrade shall define:

- Supported source versions.
- Configuration migration.
- Data migration.
- Rollback behavior.
- In-use file behavior.
- Driver or native dependency behavior.
- Recovery from interruption.
- Version confirmation.

## 80. Compatibility

A release shall state compatibility with:

- Protocol versions.
- Node product variants.
- Firmware versions.
- Operating systems.
- Runtime versions.
- Required drivers.
- Data and configuration schema versions.

Compatibility shall be verified, not inferred only from compilation.

---

# Part XIV — Performance and Resource Control

## 81. Performance Budgets

Projects shall define applicable budgets for:

- Startup time.
- Connection time.
- Command latency.
- UI response.
- Data acquisition rate.
- Rendering rate.
- Memory.
- Queue capacity.
- Disk usage.
- Log growth.
- CPU utilization.
- Shutdown time.
- Update duration.

## 82. Measurement

Performance decisions shall be based on measurement when performance is a requirement or observed risk.

Optimization shall preserve correctness, readability, diagnostics, and testability.

## 83. Resource Leaks

The project shall test for leaks of:

- Device handles.
- File handles.
- Sockets.
- Timers.
- Threads.
- Tasks.
- Event subscriptions.
- Native memory.
- UI objects.
- Log files.
- Temporary files.

## 84. High-Rate Data

High-rate data paths shall avoid:

- Per-sample UI dispatch.
- Unbounded allocation.
- Repeated large-object allocation.
- Full-data copies at every layer.
- Lock contention on the receive path.
- Synchronous disk writes on the receive thread.

Any pooling or zero-copy design shall have explicit ownership and lifetime rules.

---

# Part XV — AI-Assisted Engineering Governance

## 85. AI Role

AI systems may:

- Generate initial architecture proposals.
- Generate code.
- Generate tests.
- Review code.
- Compare implementation against this document.
- Trace Protocol definitions into code.
- Detect structural inconsistencies.
- Produce review checklists.
- Assist with documentation.

AI systems shall not be treated as the accountable owner of:

- Product requirements.
- Safety decisions.
- Security acceptance.
- Regulatory interpretation.
- Architecture approval.
- Deviation approval.
- Test acceptance.
- Release approval.

## 86. Context Required for AI Generation

Before generating Coordinator code, the AI shall be provided or directed to:

- The approved Coordinator/Node Framework.
- This document.
- The applicable language coding rules.
- The Project Protocol YAML and guide.
- The Project application analysis.
- Target platform and runtime.
- Required UI or service framework.
- Product requirements.
- Security requirements.
- Test constraints.
- Existing project structure.
- Generated-code boundaries.

Unknown information shall be identified as `TBD` rather than invented.

## 87. AI Output Boundaries

AI-generated code shall:

- Respect layer boundaries.
- Use the declared concurrency model.
- Use approved dependencies.
- Avoid hidden global state.
- Avoid unbounded queues.
- Include cancellation and timeout behavior where required.
- Preserve generated-code boundaries.
- Compile under the declared toolchain.
- Be reviewed by a human.
- Be tested against acceptance criteria.

A successful build shall not be treated as design validation.

## 88. AI Review Prompts

AI review should explicitly inspect:

- Authority conflicts.
- Layer violations.
- State ownership.
- Thread ownership.
- UI-thread blocking.
- Resource lifecycle.
- Exception swallowing.
- Protocol/Transport coupling.
- Missing timeout or cancellation.
- Unbounded buffering.
- Generated-code modification.
- Secret exposure.
- Missing tests.
- Unsupported assumptions.
- Runtime and framework compatibility.

---

# Part XVI — Project Adoption and Conformance

## 89. Required Project Profile

Each adopting project shall record:

- Coordinator role.
- Product and system context.
- Target platforms.
- Language and version.
- Runtime.
- UI or service framework.
- Supported transports.
- Protocol version.
- Security model.
- Storage model.
- Concurrency model.
- Deployment model.
- Required analyzers.
- Approved deviations.

An approved completed `Framework_Application_Analysis_Template.md` may serve as the Project profile when it contains the required information. Missing Coordinator-specific information may be supplied by a concise Project annex. A second competing Project-description authority should not be created merely to satisfy this section.

## 90. Deviations

A deviation shall include:

- Rule identifier or section.
- Reason.
- Scope.
- Risk.
- Compensating control.
- Verification evidence.
- Approver.
- Expiration or review condition when applicable.

A deviation shall not silently become a new default.

## 91. Definition of Conformance

This section defines implementation conformance. It does not define the approval status of this document itself.

A Coordinator implementation conforms only when:

- Applicable mandatory rules are satisfied.
- Approved deviations are documented.
- Required tests pass.
- Protocol interoperability passes.
- Build and analyzer requirements pass.
- Lifecycle and shutdown behavior are verified.
- Security requirements are verified.
- Human review is complete.

## 92. Review Checklist

The reviewer shall confirm at minimum:

### Architecture

- [ ] UI does not own transport or Protocol logic.
- [ ] Dependencies follow the declared direction.
- [ ] Domain logic is independently testable.
- [ ] A Composition Root exists.
- [ ] Platform-specific code is isolated.

### State and Lifecycle

- [ ] Authoritative state owners are identified.
- [ ] Connection is not represented by one misleading Boolean.
- [ ] Startup and shutdown are staged.
- [ ] Reconnect policy is bounded.
- [ ] Invalid state transitions are handled.

### Concurrency

- [ ] UI thread is not blocked by I/O.
- [ ] Tasks, threads, timers, and subscriptions have owners.
- [ ] Cancellation and timeout behavior are defined.
- [ ] Continuous queues are bounded.
- [ ] Background exceptions are observed.

### Communication

- [ ] Protocol and Transport are separated.
- [ ] Partial and malformed input is handled.
- [ ] Correlation and late responses are handled.
- [ ] Security sessions are locally owned.
- [ ] Generated Protocol files are not manually edited.

### Diagnostics and Data

- [ ] Errors are classified.
- [ ] Logs contain sufficient context.
- [ ] Sensitive data is masked.
- [ ] Configuration is typed and versioned.
- [ ] Critical persistence is atomic or recoverable.

### Verification and Release

- [ ] Cross-implementation interoperability is tested.
- [ ] Fault injection is included where applicable.
- [ ] Build inputs are reproducible.
- [ ] Dependencies are governed.
- [ ] Compatibility is explicitly stated.
- [ ] Human approval evidence exists.

---

# Appendix A — Recommended Repository Structure

```text
coordinator/
├── application/
├── domain/
├── presentation/
├── protocol/
│   ├── generated/
│   └── integration/
├── transport/
├── infrastructure/
├── security/
├── diagnostics/
├── configuration/
├── tests/
│   ├── unit/
│   ├── component/
│   ├── integration/
│   └── interoperability/
└── tools/
```

Names may differ by language and framework. Responsibility boundaries are normative; this exact folder structure is not.

# Appendix B — Derived Conformance Summary

**Authority:** `Coordinator_Node_Control_Framework.md` and the approved Project Protocol.

The Coordinator implementation shall preserve:

- Coordinator/Node role relativity.
- Capability-based interaction.
- Protocol/Transport separation.
- Explicit message category semantics.
- Independent Application and Bootloader security contexts when required.
- Deterministic Protocol generation.
- Cross-implementation interoperability.
- Human approval of product and release decisions.

This appendix is a non-authoritative summary and shall not replace the owning documents.

# Appendix C — References

- `Coordinator_Node_Control_Framework.md`
- `Framework_Application_Analysis_Template.md`
- `Protocol_YAML_Definition_Guide.md`
- `Protocol_YAML_Template.md`
- `CSharp_Coding_Rules.md`
- Microsoft .NET architecture, coding, asynchronous programming, and library design guidance, as applicable to the selected implementation profile.
- Platform, runtime, UI framework, transport, and security documentation applicable to the Project.

---

**End of Document**
