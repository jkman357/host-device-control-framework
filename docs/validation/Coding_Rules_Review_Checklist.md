# Coding Rules Review Checklist

**Canonical Filename:** `Coding_Rules_Review_Checklist.md`  
**Document Version:** v1.0.0  
**Status:** Draft for Review  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-19  
**Language:** English  
**Intended Audience:** Developers, code reviewers, static-analysis owners, test engineers, release engineers, and AI-assisted engineering systems  
**Repository Role:** Proposed operational common Coding Rules review checklist; not an independent language or Product requirement authority  
**Related Documents:**
- `../coding-rules/Embedded_C_Coding_Rules.md`
- `../coding-rules/CSharp_Coding_Rules.md`
- `Validation_Evidence_Guide.md`
- `AI_Generated_Artifact_Validation_Guide.md`

---

## Copyright and Use

Copyright © 2026 Ray Yang. All rights reserved unless a repository-level license states otherwise.

> Checklists do not independently create requirements. They provide review, traceability, and evidence-capture views of requirements established by governing authority documents.

---

## Version History

| Version | Date | Status | Summary |
|---|---|---|---|
| v1.0.0 | 2026-07-19 | Draft for Review | Initial Draft providing a common review entry point for current and future language-specific Coding Rules without redefining their detailed requirements. |

---

# 1. Review Record

Record the applicable Coding Rules document and version, Project profile, source/build identity, toolchain, review scope, methods, evidence, findings, deviations, reviewer, and result.

This checklist intentionally uses broad categories. The applicable language authority supplies the exact rule text.

# 2. Applicable Authority

- [ ] C-001 The implementation language, dialect/version, compiler/runtime, platform, and role are identified.
- [ ] C-002 The exact applicable Coding Rules version and Project-specific rule profile are identified.
- [ ] C-003 Framework, Coordinator or Node Rules, Project Protocol, Product requirements, SDD, hardware, and generated-code boundaries are identified as applicable.
- [ ] C-004 Draft rules are explicitly adopted or marked pending; they are not silently treated as approved.
- [ ] C-005 Every deviation identifies exact rule, location, rationale, risk, compensating control, evidence, approver, and scope.

# 3. Naming and Structure

- [ ] C-010 Names follow the applicable language and Project conventions.
- [ ] C-011 Module, namespace, package, class, file, and symbol responsibilities are cohesive and discoverable.
- [ ] C-012 Public APIs expose stable domain meaning rather than vendor, UI, Transport, or generated internals without justification.
- [ ] C-013 Dependencies follow the approved architecture and avoid cycles or hidden global coupling.
- [ ] C-014 Duplicate implementations, dead code, obsolete aliases, and misleading comments are removed or controlled.

# 4. Type and Data Safety

- [ ] C-020 Types express signedness, width, nullability, optionality, units, ranges, identity, and state as required by the language authority.
- [ ] C-021 Conversions, casts, serialization, enum handling, and pointer/reference use follow the applicable rules.
- [ ] C-022 External, Protocol, file, database, UI, and hardware data is validated before use.
- [ ] C-023 Lifetime, ownership, aliasing, mutability, and thread visibility are explicit.
- [ ] C-024 Secrets and sensitive values use approved types and storage boundaries.

# 5. Arithmetic Safety

- [ ] C-030 Increment, decrement, addition, subtraction, multiplication, division, shift, scaling, and conversion follow overflow/underflow rules.
- [ ] C-031 Division by zero, invalid shift, precision loss, narrowing, sign change, and floating-point exceptional values are addressed.
- [ ] C-032 Units, scale, offset, Min/Max, saturation, rounding, and tolerance trace to authority.
- [ ] C-033 Intentional wraparound or saturation is isolated and documented.
- [ ] C-034 Magic numbers and direct numeric status codes are replaced according to applicable Coding Rules.

# 6. Resource Management

- [ ] C-040 Memory, handles, files, sockets, threads, tasks, timers, registrations, callbacks, and subscriptions have clear ownership and release.
- [ ] C-041 Allocation follows the applicable static/dynamic memory policy and has bounded failure behavior.
- [ ] C-042 Queues, buffers, collections, histories, retries, recursion, and loops are bounded where required.
- [ ] C-043 Cleanup remains correct on error, cancellation, timeout, partial initialization, and shutdown.
- [ ] C-044 Resource exhaustion produces controlled behavior and evidence.

# 7. Error Handling and Diagnostics

- [ ] C-050 Errors are not silently swallowed or converted into false success.
- [ ] C-051 Result, exception, status, and retry behavior follow the language and architecture authority.
- [ ] C-052 Error messages retain actionable context without leaking secrets or unapproved sensitive data.
- [ ] C-053 Logging is structured, bounded, injection-resistant where applicable, and safe for the execution context.
- [ ] C-054 Product Alarm/Event/Fault behavior remains distinct from diagnostic severity.

# 8. Concurrency and Execution Context

- [ ] C-060 Mutable state has one owner or a documented synchronization policy.
- [ ] C-061 ISR, callback, task/thread, UI thread, timer, async continuation, and DMA contexts obey their allowed operations.
- [ ] C-062 Locks, atomics, volatile access, memory barriers, cancellation, timeout, and shutdown follow applicable rules.
- [ ] C-063 Race, deadlock, priority inversion, starvation, stale callback, reentrancy, and double-completion risks are addressed.
- [ ] C-064 Backpressure and overload do not create unbounded work or block higher-priority behavior.

# 9. API and Boundary Review

- [ ] C-070 Inputs, outputs, preconditions, postconditions, side effects, error results, ownership, and thread context are defined.
- [ ] C-071 Vendor, generated, OS, Transport, storage, cryptographic, and hardware APIs are isolated or justified.
- [ ] C-072 Untrusted deserialization does not activate arbitrary types, callbacks, external resources, or code paths.
- [ ] C-073 Protocol encode/decode remains separate from Product execution and UI presentation.
- [ ] C-074 Version and compatibility behavior is explicit at persisted, external, and Protocol boundaries.

# 10. State Machines

- [ ] C-080 States, events, guards, actions, transitions, entry/exit behavior, timeout, and invalid-event behavior are explicit.
- [ ] C-081 State transitions occur under the approved owner and execution context.
- [ ] C-082 Accepted, started, completed, failed, cancelled, timed out, and unknown states are not conflated.
- [ ] C-083 Fault, degraded, safe, reset, reconnect, and recovery transitions are testable.
- [ ] C-084 Default branches do not hide newly added enum or state values.

# 11. Generated and Vendor Code

- [ ] C-090 Generated and vendor files are identified and separated from Product-owned code.
- [ ] C-091 Generator/source/package/version/license identity is preserved.
- [ ] C-092 Manual modifications are prohibited or repeatably controlled.
- [ ] C-093 Product-owned wrappers define context, memory, timeout, error mapping, and security behavior.
- [ ] C-094 Regeneration and upgrade impact are tested.

# 12. Static Analysis and Build

- [ ] C-100 The supported compiler/runtime/toolchain and warning policy are used.
- [ ] C-101 Required builds complete with no unapproved errors or warnings.
- [ ] C-102 Static-analysis rulesets, suppressions, baselines, and tool versions are controlled.
- [ ] C-103 Suppressions are local, justified, reviewed, and do not hide unrelated findings.
- [ ] C-104 Different release/debug, architecture, optimization, and feature configurations are covered as required.

# 13. Testing and Evidence

- [ ] C-110 Tests cover normal, boundary, invalid, timeout, cancellation, concurrency, overload, and recovery behavior as applicable.
- [ ] C-111 Protocol and persisted-data code has positive and negative test vectors.
- [ ] C-112 Hardware-, timing-, OS-, driver-, or runtime-dependent behavior has evidence at the required target boundary.
- [ ] C-113 Coverage and test reports identify exact source/build/configuration and do not hide excluded code.
- [ ] C-114 AI-generated tests and review findings were independently reviewed and actually executed where claimed.

# 14. Review Result

- [ ] C-120 Findings are classified and traceable to source locations and governing rules.
- [ ] C-121 Deviations and unresolved risks are visible.
- [ ] C-122 Evidence supports the bounded result.
- [ ] C-123 Human reviewer and approval authority are recorded.
