# Coordinator Logging Guide

> Structured, Bounded, and Reviewable Logging for Coordinator Software

**Canonical Filename:** `Coordinator_Logging_Guide.md`  
**Document Version:** v1.0.1  
**Status:** Draft for Review  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-19  
**Language:** English  
**Intended Audience:** Human engineers, software architects, reviewers, test engineers, support-tool developers, code generators, and AI-assisted engineering systems  
**Repository Role:** Proposed topic-specific normative engineering authority for Coordinator logging implementation, subordinate to Coordinator Software Engineering Rules  
**Supersedes Document Version:** v1.0.0

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
- [Coordinator Testing Guide](Coordinator_Testing_Guide.md)
- [Coordinator UI Engineering Guide](Coordinator_UI_Engineering_Guide.md)

---

## Version History

| Version | Date | Status | Summary |
|---|---|---|---|
| v1.0.0 | 2026-07-19 | Draft for Review | Initial Draft defining log purpose, event structure, levels, identifiers, correlation, Protocol logging, sensitive-data handling, injection resistance, asynchronous and bounded delivery, retention, export, integrity, time, startup context, fault evidence, testing, and anti-patterns. |
| v1.0.1 | 2026-07-19 | Draft for Review | Distinguished accidental-corruption detection from adversarial tamper detection and authenticity; required independently anchored signing, authentication, trusted timestamp, or controlled append-only evidence when the threat model requires stronger assurance than a hash manifest. |

---

# 0. Purpose

This Guide defines logging practices for Coordinator-side applications and tools. The objective is to produce useful engineering evidence without introducing uncontrolled performance, storage, privacy, or security risk.

Logging is not a substitute for Product requirements, formal audit records, raw measurement files, Protocol captures, or approved test reports. Each artifact type shall retain its own authority and integrity controls.

## 0.1 Requirement Keywords

- **shall**: required when this Guide applies and no approved deviation exists;
- **should**: preferred default;
- **may**: permitted option.

## 0.2 Authority Boundary

This document is a `Draft for Review`. Its requirements are proposed and do not apply to a Project until a human authority explicitly adopts or approves this document for that Project.

`Coordinator_Software_Engineering_Rules.md` remains the cross-topic Coordinator software authority. This Guide owns only the detailed Coordinator diagnostic logging implementation rules within its stated scope after adoption. It shall not weaken or silently override the cross-topic rules. Repeated Framework, Protocol, safety, security-boundary, or Product rules are `Derived conformance summary` unless a section explicitly identifies a Coordinator-specific realization owned here.

This Guide does not define:

- Product Alarm semantics or priority;
- formal audit-record or regulated-record requirements;
- Product privacy, retention, or cybersecurity policy;
- raw measurement, Protocol-capture, or approved test-report authority.

Approved Product requirements, the Coordinator SDD, the Project Protocol, applicable cybersecurity and safety authorities, platform constraints, and language-specific coding rules take precedence within their owned topics. A conflict shall be reported rather than silently resolved.
---

# 1. Distinguish Artifact Types

The design shall distinguish the following concepts:

- **Diagnostic Log**: engineering information used to understand application behavior.
- **Product Event**: a domain occurrence defined by Product requirements.
- **Alarm Record**: a Product-defined alarm occurrence and lifecycle record.
- **Audit Record**: a controlled record of accountable actions when required.
- **Telemetry**: current or replaceable Node state.
- **Stream Recording**: ordered samples or records retained for analysis.
- **Protocol Capture**: raw or decoded communication evidence.
- **Trace**: correlated timing and execution information across operations.
- **Test Evidence**: retained output linked to an executed test and acceptance criteria.

A diagnostic log shall not silently be treated as a formal audit record or test report.

---

# 2. Logging Objectives

Logging should support:

- startup and configuration diagnosis;
- connection lifecycle diagnosis;
- command and response correlation;
- invalid, unexpected, duplicate, stale, and unsupported message diagnosis;
- timeout, cancellation, reconnect, and shutdown analysis;
- queue, buffer, Stream, and recording overload analysis;
- fault reconstruction;
- software version and environment identification;
- test automation and retained evidence where approved.

Every retained field should have a clear diagnostic purpose. Logging everything is not an acceptable design objective.

---

# 3. Structured Log Event Model

A log event should use structured fields rather than requiring text parsing.

Recommended common fields include:

- event timestamp;
- monotonic elapsed time when useful;
- severity;
- stable event identifier;
- component or subsystem;
- message template;
- application version and build identity;
- process and thread or execution-context identity when useful;
- connection generation;
- Node identity;
- Protocol session identity in non-sensitive form;
- command or correlation identifier;
- operation name;
- result or error code;
- exception type and stack information where allowed;
- relevant counters or measurements;
- privacy or sensitivity classification when required.

Field names and event identifiers should remain stable so tools and tests do not depend on free-form wording.

---

# 4. Severity Levels

A typical severity model is:

| Level | Intended Use |
|---|---|
| Trace | Very detailed execution diagnostics, normally disabled in production use. |
| Debug | Developer diagnostics useful during integration or investigation. |
| Information | Expected lifecycle milestones and significant normal operations. |
| Warning | Unexpected or degraded condition from which the application can continue. |
| Error | Operation or subsystem failure requiring attention or recovery. |
| Critical | Application-wide failure, integrity threat, or condition requiring immediate controlled shutdown or escalation. |

Rules:

1. Severity shall reflect impact, not developer frustration.
2. Expected user cancellation shall not normally be logged as an Error.
3. A transient retry attempt should not produce repeated Error logs when the final outcome remains expected and controlled.
4. The final failed outcome should be logged once with correlation to prior attempts.
5. High-frequency normal data shall not be logged at Information level per sample.
6. Product Alarm priority shall not be inferred directly from diagnostic log severity.

---

# 5. Stable Event Identifiers

Significant events should have stable identifiers independent of message wording.

An event identifier should be unique within its owning namespace and documented for:

- meaning;
- severity default;
- required fields;
- expected rate;
- retention relevance;
- whether it may contain sensitive data.

Renaming a message template shall not change the event identity. Reusing an identifier for a different meaning is prohibited.

---

# 6. Correlation and Context

Logs should make a complete operation traceable across layers.

Correlation may include:

- application operation identifier;
- Protocol request identifier;
- Firmware Update transaction identifier;
- connection generation;
- recording session identifier;
- user workflow identifier;
- test run identifier.

Correlation values shall not be confused with security secrets or authentication credentials.

A timeout, late response, duplicate response, and state-reconciliation result should be linkable to the original command where practical.

---

# 7. Connection and Lifecycle Logging

At minimum, log significant lifecycle transitions such as:

- application startup and controlled shutdown;
- Transport discovery and selection;
- connection attempt and result;
- negotiation, capability, and compatibility result;
- Secure Session establishment result without exposing keys or secrets;
- state reconciliation start and completion;
- degraded state;
- disconnect reason;
- reconnect attempt with bounded attempt information;
- final reconnect result;
- recording or update session start and completion.

Repeated retry logs should be rate-limited or summarized.

---

# 8. Protocol Logging

Protocol logging shall balance diagnosis, performance, confidentiality, and storage.

## 8.1 Metadata Logging

The default should log metadata such as:

- direction;
- message identifier or name;
- encoded and decoded length;
- correlation or sequence value;
- validation result;
- connection generation;
- response time;
- error classification.

## 8.2 Payload Logging

Payload bytes or decoded values may be logged only when:

- the diagnostic purpose is defined;
- sensitive fields are redacted or omitted;
- high-rate output is bounded;
- retention is appropriate;
- Product and security rules permit it.

Full payload logging should normally be disabled by default for production use.

## 8.3 Invalid Input

For malformed or rejected input, retain enough data to diagnose the class of failure without writing an unbounded attacker-controlled payload to the log.

The design should cap:

- captured byte count;
- string length;
- nested object depth;
- repeated event rate.

---

# 9. Sensitive and Security-Relevant Data

The following shall not be written to ordinary logs:

- private keys;
- session keys;
- authentication tokens;
- passwords;
- recovery codes;
- complete secrets or credentials;
- unapproved personal or patient-identifying information;
- memory dumps containing uncontrolled sensitive content.

Sensitive identifiers should be omitted, masked, hashed, tokenized, or replaced by a non-sensitive correlation value according to approved policy.

Redaction shall occur before the event reaches a general-purpose sink. A sink filter alone is insufficient when other sinks may receive the unredacted event.

Security failures should be logged with enough context to support investigation without creating a new disclosure path.

---

## 9.1 Injection and Path Safety

Message templates, event identifiers, field names, and output paths shall be program-defined or selected from an approved bounded set. Data received from a Node, user, file, network, or third-party library shall be treated as untrusted field data rather than executable template text.

Before text output, untrusted values shall be encoded or escaped so carriage returns, line feeds, terminal-control sequences, delimiters, markup, and other control characters cannot create forged events or alter log structure. Truncation shall preserve an explicit indication that data was shortened.

Untrusted Node names, serial numbers, labels, or user text shall not be used directly as a directory or filename. File components shall be generated from bounded safe identifiers, and path traversal shall be rejected.

Hashing or tokenizing an identifier does not automatically make it anonymous. The privacy classification shall consider linkability, reversibility, retained mapping, and the surrounding fields.

# 10. Logging Performance and Backpressure

Logging shall not create unbounded memory growth or block time-critical application paths indefinitely.

An asynchronous logger shall define:

- queue capacity;
- severity-aware overflow policy;
- flush behavior;
- shutdown behavior;
- dropped-event counters;
- behavior when the storage device is slow, full, removed, or unavailable.

Possible policies include:

- drop low-severity events first;
- coalesce repeated events;
- retain the first and last event plus a repetition count;
- synchronously preserve only a narrowly defined critical record within a measured and configured maximum blocking time;
- disable a failing sink and report the sink failure through another bounded path.

The logger shall avoid recursive logging when reporting its own failure.

---

# 11. Rate Limiting and Repetition Control

High-rate repeated events should be summarized.

A summary may include:

- first occurrence time;
- last occurrence time;
- occurrence count;
- representative fields;
- maximum or minimum observed value;
- current state.

Rate limiting shall not hide the first occurrence of a significant fault or the final outcome of an operation.

---

# 12. File and Storage Management

File-based logging should define:

- directory ownership;
- naming convention;
- file format and encoding;
- rotation trigger;
- maximum file count or total size;
- retention duration;
- behavior on disk-full condition;
- permissions;
- integrity or signing requirements when applicable;
- export and support workflow;
- cleanup behavior.

Log filenames should include sufficient non-sensitive identity, such as application, date, run, or session identifier. Filenames shall not rely on locale-dependent formatting.

Retention defaults shall be bounded. Unlimited retention is prohibited unless an external controlled storage policy provides a verified bound.

---

# 13. Time and Ordering

Logs should record wall-clock time for human interpretation and monotonic elapsed time for duration and ordering analysis where needed.

The design shall account for:

- clock adjustment;
- time-zone conversion;
- daylight-saving changes where applicable;
- Node and Coordinator clock differences;
- timestamp resolution;
- multiple events with the same timestamp;
- events received out of order.

A wall-clock change shall not produce a negative operation duration. Duration calculations should use a monotonic clock.

The source of each timestamp should be clear when both Node and Coordinator time are retained.

---

# 14. Startup Context

Each run should retain enough startup context to reproduce the software environment, including as applicable:

- application version;
- build or commit identity;
- configuration schema version;
- operating system and runtime version;
- enabled feature set;
- Protocol version and capability result;
- selected Transport type;
- logging configuration;
- simulator, test, or production mode indication.

Secrets and uncontrolled user data shall not be included.

---

# 15. Fault and Exception Logging

A fault log should identify:

- operation and subsystem;
- stable error category and code;
- current lifecycle state;
- connection generation;
- correlation identity;
- immediate cause;
- recovery action;
- final result;
- exception details where permitted.

The same failure should not be logged independently at every layer as unrelated Errors. Lower layers may add diagnostic context, but the owning layer should record the final operational outcome.

Catching and logging an exception without restoring a known state or propagating failure is prohibited.

---

# 16. User Messages and Logs

User-facing messages and diagnostic logs serve different purposes.

- User messages should be understandable, actionable, and safe to display.
- Logs should retain technical context and stable identifiers.
- Raw exception text should not normally be shown directly to users.
- A user-visible error may include a support code that correlates with the diagnostic event.

Changing UI wording shall not require changing a stable log event identity.

---


# 17. Export, Integrity, and Disposal

A log export or support bundle shall define:

- who or what is authorized to initiate the export;
- included and excluded data classes;
- redaction before packaging;
- bounded size and failure behavior;
- package identity and software context;
- accidental-corruption detection such as a SHA-256 manifest when file-integrity checking is required;
- independently anchored authenticity or adversarial-tamper protection, such as a digitally signed manifest, an approved MAC under controlled keys, a trusted timestamp, or a controlled append-only evidence store, when the threat model requires it;
- secure destination and transfer expectations;
- retention and deletion behavior for temporary and exported copies.

A cryptographic hash manifest detects changed bytes only when the manifest and its provenance remain independently trusted. A hash manifest alone shall not be represented as proof of authorship, authenticity, trusted creation time, or adversarial tamper resistance because an attacker able to replace both an artifact and its manifest can recompute the hashes.

Export shall not broaden access to data merely because the same data already exists in a local log. Temporary export artifacts shall be removed through a defined bounded cleanup path.

# 18. Logging Tests

Tests should verify:

- required fields for significant events;
- stable event identifiers;
- severity classification;
- redaction before sink delivery;
- bounded queue behavior;
- dropped-event reporting;
- repetition summarization;
- file rotation and retention bounds;
- disk-full and sink-failure behavior;
- shutdown flush limits;
- timestamp and duration behavior across wall-clock changes;
- correlation across command, response, timeout, and reconnect;
- payload length caps for malformed input;
- CR/LF, terminal-control, delimiter, and markup injection handling;
- safe filename generation and path-traversal rejection;
- export authorization, redaction, accidental-corruption manifest, independently anchored authenticity controls when required, temporary-file cleanup, and disposal;
- absence of secret material in representative logs.

Tests shall not depend primarily on free-form message text when stable fields are available.

---

# 19. Logging Anti-Patterns

Reject or explicitly justify:

1. Logging complete secrets, keys, passwords, or tokens.
2. Logging every Stream sample at a normal production level.
3. Building log messages from unbounded external strings or payloads.
4. Unlimited log files or retention.
5. Synchronous file writes on the UI or receive callback path without bounded justification.
6. One generic Error message without operation or context.
7. Catching, logging, and suppressing an exception that leaves state uncertain.
8. Treating diagnostic logs as formal test evidence without an approved test record.
9. Using log severity as Product Alarm priority.
10. Emitting the same failure as separate uncorrelated Errors at every layer.
11. Relying on localized free-form text for automated analysis.
12. Failing recursively while attempting to log a logger failure.
13. Allowing untrusted text to define message templates, event identifiers, directory names, or filenames.
14. Assuming a hashed or tokenized identifier is automatically anonymous.
15. Exporting logs or support bundles without authorization, redaction, integrity, size, retention, and disposal controls.
16. Treating an unsigned hash manifest as proof of authorship, authenticity, trusted time, or adversarial tamper resistance.

---

# 20. Logging Review Checklist

- [ ] Diagnostic logs, Product events, alarms, audit records, recordings, captures, and test evidence are distinguished.
- [ ] Significant events use stable identifiers and structured fields.
- [ ] Severity levels are applied consistently.
- [ ] Command, response, timeout, reconnect, and operation results are correlated.
- [ ] Connection generation and relevant session identity are available without exposing secrets.
- [ ] Protocol payload logging is bounded, controlled, and redacted.
- [ ] Secrets and unapproved personal data are excluded before sink delivery.
- [ ] Untrusted values cannot forge records, inject control sequences, or control output paths.
- [ ] Logging queues, files, and retention are bounded.
- [ ] Slow, full, missing, or failed storage behavior is defined.
- [ ] Repeated events are rate-limited or summarized without hiding the first and final outcome.
- [ ] Wall-clock and monotonic time roles are defined.
- [ ] Startup context identifies the software and configuration environment.
- [ ] Logger failure cannot recurse indefinitely.
- [ ] User-facing messages are separated from diagnostic detail.
- [ ] Export authorization, package integrity, temporary-file cleanup, retention, and disposal are defined.
- [ ] Tests cover redaction, bounds, rotation, sink failure, and correlation.
