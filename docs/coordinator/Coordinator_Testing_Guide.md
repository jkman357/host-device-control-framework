# Coordinator Testing Guide

> Verification Strategy for Coordinator Applications, Protocol Integration, and UI Behavior

**Canonical Filename:** `Coordinator_Testing_Guide.md`  
**Document Version:** v1.1.0  
**Status:** Draft for Review  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-19  
**Language:** English  
**Intended Audience:** Human engineers, software architects, reviewers, verification engineers, test-tool developers, code generators, and AI-assisted engineering systems  
**Repository Role:** Proposed topic-specific normative engineering authority for Coordinator engineering tests, subordinate to Coordinator Software Engineering Rules  
**Supersedes Document Version:** v1.0.1

---

## Copyright and Use

Copyright © 2026 Ray Yang. All rights reserved unless a repository-level license states otherwise.

This document is independently authored. External standards and guidance are referenced for context and are not reproduced as substitute standards. Third-party documents remain subject to their respective copyright and license terms.

This document is maintained as part of a personal engineering project. It is not an official document of any employer or organization.

---

## Related Documents

- [Coordinator/Node Control Framework](../framework/Coordinator_Node_Control_Framework.md)
- [Coordinator Software Engineering Rules](Coordinator_Software_Engineering_Rules.md)
- [Coordinator Architecture Patterns](Coordinator_Architecture_Patterns.md)
- [Coordinator Concurrency Guide](Coordinator_Concurrency_Guide.md)
- [Coordinator Logging Guide](Coordinator_Logging_Guide.md)
- [Coordinator UI Engineering Guide](Coordinator_UI_Engineering_Guide.md)

---

## Version History

| Version | Date | Status | Summary |
|---|---|---|---|
| v1.1.0 | 2026-07-19 | Draft for Review | Added a complete Multi-Node verification matrix covering isolation, conflicts, stale generations, shared-bus fairness, cross-Node correlation and Session boundaries, broadcast, multi-target partial results, UI binding, mixed versions, and Firmware Update targeting. |
| v1.0.0 | 2026-07-19 | Draft for Review | Initial Draft defining test layers, traceability, deterministic dependencies, Protocol and Transport coverage, concurrency and reconnect testing, fuzzing, UI testing, performance, fault injection, simulators, CI, flakiness control, evidence integrity, and release review. |
| v1.0.1 | 2026-07-19 | Draft for Review | Clarified that artifact hashes and immutable identities detect change only when their provenance is trusted, and required independently anchored signing, authentication, trusted timestamp, or append-only evidence where authenticity or adversarial tamper resistance is required. |

---

# 0. Purpose

This Guide defines a reusable testing strategy for Coordinator-side software. It covers application logic, Protocol integration, Transport adaptation, concurrency, reconnect behavior, data processing, logging, recording, and UI behavior.

It does not replace an approved Product Test Specification, verification protocol, validation protocol, risk-control verification plan, cybersecurity test plan, or regulatory evidence process.

Testing should provide fast engineering feedback while preserving a clear boundary between simulated evidence and real-system evidence.

## 0.1 Requirement Keywords

- **shall**: required when this Guide applies and no approved deviation exists;
- **should**: preferred default;
- **may**: permitted option.

## 0.2 Authority Boundary

This document is a `Draft for Review`. Its requirements are proposed and do not apply to a Project until a human authority explicitly adopts or approves this document for that Project.

`Coordinator_Software_Engineering_Rules.md` remains the cross-topic Coordinator software authority. This Guide owns only the detailed Coordinator engineering-test strategy and evidence-classification rules within its stated scope after adoption. It shall not weaken or silently override the cross-topic rules. Repeated Framework, Protocol, safety, security-boundary, or Product rules are `Derived conformance summary` unless a section explicitly identifies a Coordinator-specific realization owned here.

This Guide does not define:

- approved Product verification or validation protocols;
- risk-control acceptance criteria;
- regulatory evidence approval;
- Product cybersecurity test requirements owned by an approved plan.

Approved Product requirements, the Coordinator SDD, the Project Protocol, applicable cybersecurity and safety authorities, platform constraints, and language-specific coding rules take precedence within their owned topics. A conflict shall be reported rather than silently resolved.

## 0.3 Evidence States

Test results shall identify the evidence state. Recommended states include:

- planned but not executed;
- statically reviewed;
- executed with mock or fake dependencies;
- executed with simulator or reference implementation;
- executed in cross-implementation integration;
- executed with physical Node or target hardware;
- manually observed;
- human reviewed and approved.

Passing a mock or simulator test shall not be represented as proof of physical timing, electrical behavior, actual hardware safety behavior, or Product-level acceptance.

---

# 1. Core Testing Principles

1. Tests shall trace to a requirement, design rule, risk, defect, compatibility obligation, or clearly stated engineering objective.
2. The test boundary and evidence state shall be explicit.
3. Normal-path tests alone are insufficient for a control application.
4. Boundary, invalid, timeout, cancellation, disconnect, overload, and recovery behavior shall be tested where applicable.
5. Time, randomness, Transport, storage, and external dependencies should be controllable in automated tests.
6. Tests should prefer deterministic synchronization over arbitrary delays.
7. A simulator shall model only documented behavior and shall identify unsupported or simplified behavior.
8. Generated Protocol artifacts and Golden Test Vectors shall be tested without manual redefinition.
9. Test logs and output shall identify software, Protocol, configuration, simulator or hardware identity, and test case.
10. A test shall fail clearly when its preconditions or fixture setup are invalid.
11. Flaky tests shall be treated as defects in the test system, not normalized as expected noise.
12. Real hardware testing remains required for behavior that depends on physical timing, drivers, operating-system integration, hardware reset, electrical interfaces, or Product use.

---

# 2. Test Layers

A balanced strategy should include the following layers.

## 2.1 Unit Tests

Unit tests verify small logic boundaries such as:

- domain state transitions;
- use-case preconditions;
- range and value validation;
- timeout decision logic;
- data conversion and scaling;
- downsampling and aggregation;
- error mapping;
- configuration validation;
- log-event construction and redaction.

Unit tests should avoid real I/O and wall-clock dependence.

## 2.2 Component Tests

Component tests verify a complete subsystem with controlled dependencies, such as:

- request manager with fake clock and Transport;
- decoder and dispatcher with generated Protocol artifacts;
- connection lifecycle with a scripted fake Node;
- recorder with a temporary storage adapter;
- state store and view-model projection;
- firmware-update state machine with controlled responses.

## 2.3 Integration Tests

Integration tests verify boundaries among real components, such as:

- concrete serial or USB adapter with a loopback or reference device;
- generated Coordinator codec against generated Node codec;
- application communication stack against a simulator;
- database, file, or logging sink behavior;
- UI framework binding and dispatch behavior.

## 2.4 System Tests

System tests verify the complete Coordinator with a simulator, reference implementation, physical Node, or Product system.

System tests should cover representative workflows, fault recovery, compatibility, resource use, and installation environment.

## 2.5 Manual and Exploratory Tests

Manual testing remains appropriate for:

- visual quality and usability;
- complex workflow exploration;
- hardware setup and physical interaction;
- operating-system device behavior;
- installation, upgrade, and recovery;
- display readability and user feedback;
- scenarios that are not economically automatable.

Manual evidence shall identify the procedure, environment, observer, result, and retained artifacts.

---

# 3. Test Traceability

Each test case should identify:

- Test ID;
- requirement, design rule, risk, defect, or decision source;
- test level;
- preconditions;
- inputs and steps;
- expected result;
- evidence state;
- environment and configuration;
- software and Protocol versions;
- retained evidence;
- result and reviewer when applicable.

One test may cover several related requirements, but the mapping shall remain explicit.

A test name alone is not sufficient traceability.

---

# 4. Testability Architecture

The Coordinator should expose replaceable boundaries for:

- Transport;
- clock and timers;
- random number generation when applicable;
- file system and storage;
- logging sinks;
- cryptographic provider where substitution is safe and approved;
- Node simulator or command gateway;
- UI dispatcher;
- operating-system services.

Test seams shall not bypass the same validation and state transitions used in production.

A test-only shortcut that changes Product behavior shall be isolated, disabled from production builds where appropriate, and reviewed.

---

# 5. Protocol Test Coverage

Protocol tests shall use the approved Project Protocol and generated artifacts.

Coverage should include:

- every Message ID and direction in scope;
- minimum and maximum valid payload length;
- fixed and variable array bounds;
- each enumeration value and unknown-value policy;
- signed, unsigned, scaling, offset, endianness, and alignment behavior;
- reserved values;
- invalid, truncated, and extra data;
- checksum, authentication, or integrity failure where applicable;
- duplicate, stale, reordered, missing, and wrapped sequence values;
- request and response pairing;
- state-invalid messages;
- unsupported version or capability;
- Application and Bootloader separation;
- Firmware Update transaction identity;
- Golden Test Vectors;
- cross-language and cross-implementation encoding compatibility.

The same manually written expected byte array should not be copied from the implementation under test without an independent source.

---

# 6. Transport Adapter Tests

A Transport adapter should be tested for:

- open and close success;
- open failure;
- partial read;
- multiple frames in one read;
- partial write where the API permits it;
- disconnect during read and write;
- cancellation;
- timeout;
- operating-system callback order;
- repeated open and close;
- resource cleanup;
- stale callback after close;
- device removal and reappearance;
- buffer capacity and burst input;
- error mapping.

Physical-interface tests remain necessary where the library or operating system cannot be represented accurately by a fake.

---

# 7. Command and Request Tests

For each command category, test:

- valid request and successful response;
- local precondition rejection;
- Protocol rejection;
- send failure;
- timeout;
- cancellation;
- disconnect before send;
- disconnect after send but before response;
- duplicate response;
- late response;
- mismatched response type;
- stale prior-generation response;
- concurrent in-flight requests when allowed;
- command retry and idempotency behavior;
- uncertain completion followed by state reconciliation.

A write-completion test shall not be counted as a command-success test.

---

# 8. Connection and Reconnect Tests

Test the lifecycle from every relevant state, including:

- initial connect;
- negotiation success and failure;
- incompatible version or capability;
- state synchronization success and failure;
- clean user disconnect;
- unexpected link loss;
- automatic reconnect;
- bounded retry and backoff;
- cancellation during connect;
- application close during connect or reconnect;
- reconnect with a different Node;
- Node reset while Transport remains present;
- stale queued work from the prior connection;
- pending operation completion on disconnect;
- command gating before reconciliation completes.

The test should verify both internal state and user-visible state.

---

## 8.1 Multi-Node Verification Matrix

Applicable Projects shall test at least:

```text
Multiple Nodes operating concurrently
One Node disconnecting, reconnecting, resetting, or disappearing while others continue
Stale Response from a prior connection generation
Duplicate stable identity on two connections
Two identities claiming one runtime address
Address reuse by a replacement Node
Discovery collision and maximum-Node-count behavior
Node removal during a pending Request
One Node flooding valid, malformed, or repeated traffic
Per-Node and aggregate queue/resource exhaustion
Shared-bus contention, priority, fairness, and starvation prevention
Cross-Node Request/Response correlation
Per-Node sequence and Replay isolation
Protocol Session and Secure Session isolation
UI selection change during an active operation
Coordinator-expanded multi-target partial success, failure, timeout, and cancellation
Protocol broadcast eligibility and response-collision prevention
Single-target and concurrent Firmware Update policy
Mixed Protocol and Capability versions
Aggregate Alarm/health/progress consistency and Node attribution
```

Tests shall assert that one Node cannot complete, cancel, authorize, rebind, starve, overwrite, or misrepresent
another Node's operation or state. Every expected rejection shall identify the violated rule and Node/generation
context without disclosing secrets.

# 9. Concurrency and Race Testing

Concurrency tests should control event ordering explicitly.

Coverage should include races among:

- response and timeout;
- response and cancellation;
- disconnect and send;
- disconnect and response dispatch;
- UI close and background callback;
- queue overflow and consumer recovery;
- timer callback and state transition;
- logging shutdown and final event emission;
- recording stop and final data write;
- old and new connection generations.

Use barriers, controllable schedulers, fake clocks, and explicit completion signals where practical. Arbitrary sleep delays should be minimized because they do not prove the intended interleaving.

Stress tests may complement deterministic race tests but shall not replace them.

---

# 10. Stream and Telemetry Tests

Telemetry tests should verify:

- complete snapshot replacement;
- stale and unknown state;
- validity flags;
- sequence and timestamp handling;
- display update rate;
- coalescing behavior;
- reconnect reset and reconciliation.

Stream tests should verify:

- ordered sample handling;
- gap detection;
- duplication and reordering;
- burst input;
- sustained worst-case rate;
- bounded queue behavior;
- display downsampling;
- recorder independence;
- slow disk or slow UI;
- memory limit;
- stop and restart;
- partial final batch;
- timestamp continuity and wrap.

Dropped or replaced data shall be reported according to its semantics.

---

# 11. Logging and Recording Tests

Test:

- stable event identifiers;
- required structured fields;
- correlation;
- secret and personal-data redaction;
- queue capacity and overflow policy;
- repetition summarization;
- file creation, rotation, retention, and cleanup;
- storage unavailable and disk-full behavior;
- logger or recorder failure without recursion;
- shutdown flush limit;
- recording integrity after interruption;
- software and configuration identity in output;
- export behavior.

A log message test should prefer structured fields over exact localized wording.

---

# 12. UI Tests

UI testing should be divided into:

## 12.1 Presentation Logic Tests

Verify view-model or presentation-state behavior without rendering the full UI where practical:

- enabled and disabled commands;
- pending, success, rejected, timeout, and disconnected states;
- stale data indication;
- formatting and units;
- selection and navigation state;
- alarm or event presentation mapping;
- error-to-user-message mapping;
- rate-limited chart state.

## 12.2 Framework Integration Tests

Verify:

- UI-thread dispatch;
- binding updates;
- command invocation;
- close and cancellation behavior;
- chart or list virtualization;
- high-rate update coalescing;
- keyboard and accessibility behavior where required.

## 12.3 End-to-End UI Tests

Use a stable simulator or controlled Node to verify representative workflows. End-to-end UI tests should remain focused because they are slower and more sensitive to environment variation.

Screenshots may support review, but they shall not be the only evidence for dynamic behavior.

---

# 13. Configuration and Persistence Tests

Test:

- valid configuration load;
- missing configuration;
- malformed value;
- out-of-range value;
- unknown field policy;
- schema migration;
- downgrade or incompatible-version behavior;
- atomic save or recovery from interrupted write;
- default behavior;
- secret storage boundary;
- user preference separation from Product-controlled settings;
- locale-independent numeric and date serialization.

Invalid configuration shall not silently change Product behavior without an approved fallback.

---

# 14. Fault Injection

Fault injection should cover, as applicable:

- Transport failure;
- malformed frame;
- unexpected message;
- invalid state transition;
- delayed or missing response;
- duplicate response;
- Node reset;
- incompatible capability;
- authentication or integrity failure;
- queue overflow;
- storage full or removed;
- logger or recorder failure;
- thread or task exception;
- configuration corruption;
- firmware-update interruption;
- application shutdown during active work;
- abrupt process termination or operating-system restart during persistent writes;
- suspend, resume, sleep, and device re-enumeration when applicable.

Injected faults shall be distinguishable from actual environment failures in retained evidence.

---

# 15. Performance and Resource Tests

Measure or bound:

- startup and connection time;
- command round-trip time;
- decode and dispatch latency;
- UI update latency;
- Stream throughput;
- recording throughput;
- CPU use;
- memory use and growth over time;
- queue depth under normal and worst-case load;
- log volume;
- file growth and rotation;
- reconnect behavior;
- shutdown time.

A performance test shall define hardware, operating system, build configuration, data rate, duration, and acceptance criteria.

Simulator performance shall not be presented as physical Node timing evidence.

---

# 16. Simulator and Mock Governance

A mock, fake, or simulator should document:

- supported Protocol version;
- supported messages and states;
- timing model;
- error and fault capabilities;
- simplified behavior;
- unsupported behavior;
- determinism controls;
- version identity.

A simulator shall not invent undefined Product behavior and then become an unofficial authority.

Tests should include negative scenarios rather than only a cooperative happy-path simulator.

Where independent interoperability evidence is required, the simulator should not reuse the exact same implementation code for both sides of the contract without disclosure.

---


# 17. Fuzzing and Property-Based Testing

Fuzzing or property-based testing should be applied to externally influenced parsers and stateful boundaries where practical, including:

- Protocol frame and message decoding;
- import files and configuration files;
- persisted state and migration inputs;
- command-line, network, and support-bundle inputs;
- malformed length, nesting, encoding, and numeric edge cases.

Properties should include bounded execution, bounded allocation, no uncontrolled exception escape, deterministic rejection classification where required, no state mutation before validation, and preservation of parser synchronization or controlled reset. A fuzzer crash or timeout shall retain the minimized input, software identity, seed, and reproduction command when available.

Test fixtures shall not contain production credentials, private keys, real patient-identifying data, or uncontrolled production logs. Synthetic or approved de-identified data shall be used according to Product policy.

# 18. Continuous Integration

CI should run the fastest reliable checks on each change, such as:

- build;
- formatting or static checks required by Project standards;
- unit tests;
- component tests;
- Protocol schema and semantic validation;
- Golden Test Vectors;
- selected integration tests;
- document or manifest validation where applicable.

Long-running hardware, endurance, or manual tests may run in a separate controlled stage.

CI output shall identify skipped tests and shall not report an incomplete test set as a complete validation pass.

---

# 19. Flaky Test Control

A test is flaky when identical relevant inputs and environment can produce inconsistent results without a Product reason.

Rules:

1. Flaky tests shall be investigated and tracked.
2. Automatic retries may collect diagnostic evidence but shall not convert an initial failure into an unqualified pass.
3. Timing-sensitive tests should use controllable time and synchronization.
4. Environment-dependent tests should declare and verify prerequisites.
5. Quarantined tests shall remain visible with owner, reason, and restoration criteria.

---

# 20. Test Evidence and Reporting

An executed test record should identify:

- test case and version;
- software build and commit;
- Protocol and configuration identity;
- simulator, reference implementation, or hardware identity;
- operating environment;
- start and completion time;
- result;
- deviations;
- retained logs, captures, screenshots, recordings, and measurements;
- hashes or immutable artifact identities for accidental-change detection when their provenance is independently trusted;
- a digitally signed or approved authenticated manifest, trusted timestamp, controlled append-only record, or other independently anchored evidence when authenticity or adversarial tamper resistance is required;
- test tool, simulator, dependency, and fixture version or package identity;
- reviewer or approval state when applicable.

A hash or immutable identifier alone shall not be represented as proof of authorship, authenticity, trusted creation time, or adversarial tamper resistance. If an actor can replace both the artifact and its hash record, the hash can be recomputed; stronger claims therefore require an independently protected trust anchor.

The report shall distinguish:

- test executed and passed;
- test executed and failed;
- test blocked;
- test not run;
- result inconclusive;
- evidence incomplete.

---

# 21. Testing Anti-Patterns

Reject or explicitly justify:

1. Tests that only exercise the happy path.
2. Arbitrary sleeps as the primary synchronization method.
3. A mock that bypasses production validation or state transitions.
4. Copying expected bytes directly from the implementation under test.
5. Treating simulator success as physical hardware proof.
6. UI end-to-end tests replacing all lower-level tests.
7. Unlimited test logs or retained artifacts.
8. Automatic retry hiding an initial failure.
9. Tests depending on execution order without declaration.
10. Tests sharing uncontrolled mutable global state.
11. Reporting skipped or blocked tests as passed.
12. Using screenshots alone to prove timing or dynamic behavior.
13. A test name without traceability, acceptance criteria, or environment identity.
14. Using production secrets, credentials, private keys, or uncontrolled personal data in test fixtures.
15. Retaining evidence without hashes or immutable identity when accidental-change detection is required.
16. Treating an unsigned hash or mutable identifier as proof of authorship, authenticity, trusted time, or adversarial tamper resistance.
17. Treating an unpinned simulator, dependency, test tool, or generated artifact as reproducible evidence.

---

# 22. Testing Review Checklist

- [ ] Test scope, authority, and evidence state are explicit.
- [ ] Tests trace to requirements, design rules, risks, defects, or compatibility obligations.
- [ ] Unit, component, integration, system, and manual layers are selected appropriately.
- [ ] Protocol coverage includes boundaries, invalid input, sequence behavior, and Golden Test Vectors.
- [ ] Transport tests cover partial I/O, disconnect, cancellation, and resource cleanup.
- [ ] Command tests distinguish write, acknowledgement, completion, timeout, cancellation, and uncertain outcome.
- [ ] Reconnect and state reconciliation are tested.
- [ ] Concurrency tests control critical event ordering.
- [ ] Telemetry and Stream tests verify semantics, capacity, loss, and overload.
- [ ] Logging, recording, storage failure, and retention are tested.
- [ ] UI tests cover presentation logic, thread dispatch, stale data, and workflow results.
- [ ] Configuration validation and migration are tested.
- [ ] Fault injection includes relevant recovery paths, abrupt termination, interrupted persistence, and platform lifecycle events where applicable.
- [ ] Fuzzing or property-based testing covers relevant untrusted parsers and retains reproducible failing inputs.
- [ ] Performance and resource acceptance criteria are defined for the target environment.
- [ ] Simulators document supported and simplified behavior.
- [ ] CI reports skipped and incomplete coverage honestly.
- [ ] Flaky tests are controlled and visible.
- [ ] Test evidence identifies exact software, Protocol, configuration, environment, result, artifact hashes when required, independently anchored authenticity controls when required, and test-tool or simulator identity.
- [ ] Test fixtures exclude production secrets and uncontrolled personal or patient data.
