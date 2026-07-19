# Coordinator Concurrency Guide

> Threading, Asynchrony, Cancellation, and Bounded Work for Coordinator Software

**Canonical Filename:** `Coordinator_Concurrency_Guide.md`  
**Document Version:** v1.1.0  
**Supersedes Document Version:** v1.0.0  
**Status:** Draft for Review  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-19  
**Language:** English  
**Intended Audience:** Human engineers, software architects, reviewers, test engineers, code generators, and AI-assisted engineering systems  
**Repository Role:** Proposed topic-specific normative engineering authority for Coordinator concurrency, subordinate to Coordinator Software Engineering Rules

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
- [Coordinator Logging Guide](Coordinator_Logging_Guide.md)
- [Coordinator Testing Guide](Coordinator_Testing_Guide.md)
- [Coordinator UI Engineering Guide](Coordinator_UI_Engineering_Guide.md)

---

## Version History

| Version | Date | Status | Summary |
|---|---|---|---|
| v1.1.0 | 2026-07-19 | Draft for Review | Added per-Node queue, cancellation, generation-aware correlation, shared-bus fairness, bounded multi-target concurrency, Node-removal races, and overload isolation requirements and tests. |
| v1.0.0 | 2026-07-19 | Draft for Review | Initial Draft defining concurrency models, ownership, UI-thread rules, asynchronous I/O, bounded channels, cancellation, timeout, synchronization, attempt generations, priority isolation, shutdown, overload handling, testing, and anti-patterns. |

---

# 0. Purpose

This Guide defines concurrency defaults for Coordinator-side software. It applies to UI applications, services, gateways, production tools, diagnostic tools, and test applications that perform asynchronous I/O or process work on more than one execution context.

The goal is not to require a particular framework. The goal is to make thread ownership, ordering, cancellation, shutdown, and overload behavior explicit and testable.

Approved Product requirements, platform behavior, the Coordinator SDD, and language-specific standards may refine these defaults.

## 0.1 Requirement Keywords

- **shall**: required when this Guide applies and no approved deviation exists;
- **should**: preferred default;
- **may**: permitted option.

## 0.2 Authority Boundary

This document is a `Draft for Review`. Its requirements are proposed and do not apply to a Project until a human authority explicitly adopts or approves this document for that Project.

`Coordinator_Software_Engineering_Rules.md` remains the cross-topic Coordinator software authority. This Guide owns only the detailed Coordinator concurrency, execution-context ownership, cancellation, backpressure, and shutdown rules within its stated scope after adoption. It shall not weaken or silently override the cross-topic rules. Repeated Framework, Protocol, safety, security-boundary, or Product rules are `Derived conformance summary` unless a section explicitly identifies a Coordinator-specific realization owned here.

This Guide does not define:

- Node interrupt, DMA, RTOS, or hard real-time scheduling behavior;
- Product timing acceptance criteria;
- Protocol wire semantics;
- platform or language syntax rules.

Approved Product requirements, the Coordinator SDD, the Project Protocol, applicable cybersecurity and safety authorities, platform constraints, and language-specific coding rules take precedence within their owned topics. A conflict shall be reported rather than silently resolved.
---

# 1. Core Concurrency Principles

1. Every mutable object shared across execution contexts shall have documented ownership and synchronization.
2. Prefer message passing, immutable snapshots, and single-writer ownership over broad shared mutable state.
3. Blocking I/O and long-running work shall not execute on the UI thread.
4. Every queue, channel, work list, and retained callback set shall be bounded or have a proven external bound.
5. Cancellation and timeout are different outcomes and should be represented separately.
6. A disconnect or shutdown shall cancel or invalidate work associated with the prior connection generation.
7. Fire-and-forget work shall not be used unless ownership, exception observation, lifetime, and shutdown behavior are explicit.
8. Locks shall protect the smallest practical invariant and shall not be held while performing blocking I/O, awaiting asynchronous work, or calling unknown external code.
9. Ordering assumptions shall be documented and tested.
10. Overload behavior shall be defined before deployment.

---

# 2. Select an Explicit Concurrency Model

A Coordinator should select one primary model per subsystem.

## 2.1 UI Thread plus Asynchronous Services

Appropriate for desktop and mobile applications.

- UI state is owned by the UI thread.
- I/O and long-running operations execute asynchronously outside the UI thread.
- UI updates are marshalled through the framework dispatcher or synchronization context.
- Domain and communication services shall not depend on UI controls.

## 2.2 Single-Writer Event Loop

Appropriate for connection state, request correlation, and ordered Protocol processing.

- One event loop owns mutable subsystem state.
- Other contexts submit bounded messages.
- State transitions execute serially.
- External work is returned as events rather than mutating state directly.

## 2.3 Pipeline with Bounded Channels

Appropriate for receive, decode, Stream processing, logging, and recording.

- Each stage has a defined input and output.
- Capacity and overflow policy are explicit.
- Cancellation propagates through the pipeline.
- Slow consumers cannot cause unlimited memory growth.

## 2.4 Dedicated Worker

Appropriate for a library that requires thread affinity, a blocking API, or a serial operation model.

- The worker owns the resource.
- Requests are submitted through a bounded command queue.
- Results are returned through tasks, futures, callbacks, or events with defined lifetime.
- Shutdown joins or terminates the worker deterministically.

A subsystem shall not accidentally combine multiple models without defining the interaction and ownership boundary.

---

# 3. Thread and State Ownership

For each subsystem, document:

- owning execution context;
- mutable state owned by that context;
- inputs accepted from other contexts;
- output mechanism;
- ordering guarantee;
- cancellation scope;
- shutdown behavior;
- error propagation path.

A thread-safe collection does not by itself make a compound operation thread-safe. Multi-step invariants shall be owned or synchronized as one operation.

Immutable snapshots should be used for cross-thread publication when consumers need coherent state.

---

# 4. UI Thread Rules

1. UI controls and UI-bound collections shall be accessed only from the UI thread unless the framework explicitly guarantees otherwise.
2. Transport reads, writes, reconnect loops, file operations, cryptographic work, parsing of large payloads, and long calculations shall not block the UI thread.
3. UI dispatch should be coalesced or rate-limited for high-rate data.
4. A UI close operation shall initiate cancellation and coordinated shutdown rather than abandoning background work.
5. Background exceptions shall be observed and routed to an owned error path.
6. UI commands should expose pending state and prevent uncontrolled duplicate invocation when the operation is not safely repeatable.
7. The UI shall not assume that callback order equals Node event order unless the pipeline guarantees it.

---

# 5. Asynchronous I/O Rules

Asynchronous operations should be asynchronous through the complete call chain. Blocking on an asynchronous result from a context with a synchronization mechanism can deadlock and shall be avoided.

An asynchronous API should define:

- cancellation input;
- timeout ownership;
- completion result;
- exception behavior;
- whether partial progress is possible;
- whether retries are internal or external;
- whether the operation is idempotent;
- whether completion after cancellation can still occur.

A write-completed result shall not be treated as a Protocol acknowledgement.

When a library exposes callback-based I/O, the adapter shall convert callbacks into application-owned events while preserving lifetime and ordering constraints.

---

# 6. Bounded Queues and Backpressure

Every queue or channel shall define:

- capacity;
- producer count;
- consumer count;
- ordering behavior;
- overflow policy;
- shutdown behavior;
- metrics or diagnostics.

Allowed overflow strategies may include:

- reject the new item;
- drop the oldest replaceable item;
- replace a pending snapshot with the latest snapshot;
- block or asynchronously wait with cancellation;
- disconnect or enter a degraded state when loss is unacceptable.

The selected policy shall match the data semantics:

- Commands are normally non-replaceable.
- Telemetry snapshots may be replaceable by a newer complete snapshot.
- Stream samples are ordered records; loss shall be detected and reported rather than silently treated as replacement.
- Logs may use a severity-aware loss policy when necessary, but dropped counts shall be visible.

An unbounded queue shall not be used merely because normal tests do not reach overload.

---

# 7. Cancellation

Cancellation should be cooperative and scope-based.

Recommended scopes include:

- application lifetime;
- current connection generation;
- current operation;
- current view or workflow;
- current recording session.

Rules:

1. Cancellation shall be propagated to owned child operations where practical.
2. Cancellation shall not be converted into a generic fault unless the platform requires it.
3. Cleanup shall remain safe if cancellation occurs at any await point or callback boundary.
4. Cancellation callbacks shall be short and shall not perform uncontrolled blocking work.
5. Cancelling a wait does not necessarily cancel the underlying Node action; uncertain completion shall trigger reconciliation.
6. A reused cancellation source or token shall not accidentally cancel a later connection generation.

---

# 8. Timeout Ownership

Each timeout shall have one owner. Layered timeouts shall be coordinated so an inner timeout does not conflict with an outer operation contract.

Timeouts may exist for:

- Transport open or discovery;
- handshake or negotiation;
- command response;
- state reconciliation;
- firmware-update step;
- shutdown or worker join.

A timeout result should include enough context to distinguish:

- no data received;
- incomplete response;
- response received too late;
- operation still possibly executing on the Node;
- local overload or scheduling delay;
- connection loss.

Retries shall not occur automatically for a non-idempotent operation unless the Protocol defines safe deduplication or transaction identity.

---

# 9. Synchronization and Locking

## 9.1 Lock Scope

A lock should protect a specific invariant. The protected data and allowed call paths shall be documented.

While holding a lock, code shall not:

- wait for UI dispatch;
- perform blocking I/O;
- await an asynchronous operation;
- invoke user code or an unknown callback;
- emit a log through a sink that may re-enter the same subsystem;
- acquire another lock without a documented order.

## 9.2 Lock Ordering

When more than one lock may be acquired, a global or subsystem lock order shall be defined and followed.

## 9.3 Reader-Writer Synchronization

Reader-writer mechanisms should be used only when measurement shows a benefit and upgrade/downgrade behavior is understood. They are not a substitute for clear ownership.

## 9.4 Atomic Operations

Atomic operations may protect simple counters, flags, and references. They shall not be used to approximate a multi-field invariant without a correct design.

---

# 10. Request and Response Correlation

The request manager should own the pending-request table.

Each pending entry should include, as applicable:

- correlation or sequence identifier;
- connection generation;
- expected response type;
- creation time;
- timeout or deadline;
- cancellation registration;
- completion state;
- command identity.

Completion shall be single-shot. Duplicate, late, mismatched, and prior-generation responses shall not complete the wrong request.

Removing a pending entry and completing its waiter shall be designed to avoid races among response, timeout, cancellation, and disconnect.

---

# 11. Connection Generation Pattern

Every connection attempt shall receive a monotonically increasing or otherwise process-lifetime-unique local generation identity before discovery, open, callback registration, timer creation, or other asynchronous work begins. The identity applies to successful, failed, cancelled, and timed-out attempts.

Callbacks, pending requests, decoder state, timers, and queued work associated with an older or completed generation shall not mutate the current connection state. Attempt-generation comparison shall occur before publishing state or completing current-generation work.

On disconnect:

1. mark the generation as closing;
2. stop accepting new work;
3. cancel generation-scoped operations;
4. complete pending requests with the correct disconnected or uncertain result;
5. stop or drain pipelines according to their data semantics;
6. close the Transport;
7. publish the disconnected state;
8. begin a new generation only after required cleanup.

---


## 11.1 Multi-Node Correlation and Generation Isolation

Correlation keys shall include the Node/Session scope required by the Protocol. A Response received on the wrong
Node context, Secure Session, logical route, or connection generation shall be rejected as stale or misrouted and
shall not complete another Node's operation.

Per-Node cancellation sources, queues, timers, and reconnect transitions shall not be shared in a way that cancels
or drains unrelated Nodes. Node removal during active work shall atomically prevent new work, cancel or reconcile
owned work, reject late completions, and preserve evidence of the final state.

A shared-bus scheduler shall define bounded work classes, priority, fairness, and starvation prevention. Multi-target
operations shall use bounded parallelism and shall preserve per-Node timeout and cancellation outcomes. One Node's
flood, reconnect storm, or slow consumer shall trigger local or bounded aggregate backpressure rather than an
unbounded global queue.

# 12. Priority and Work-Class Isolation

Control, lifecycle, safety-relevant status, Telemetry, Stream, logging, and recording work shall not share an undifferentiated queue when high-rate traffic can starve command completion, disconnect handling, timeout processing, or shutdown.

The design shall define:

- work classes and relative service expectations;
- independent capacities or scheduling policy;
- whether priority is strict, weighted, or deadline-based;
- starvation prevention;
- overload behavior for each class;
- metrics that reveal sustained starvation or latency growth.

Priority shall not be implemented by creating unbounded high-priority work. A high-priority path remains bounded and shall not indefinitely prevent required cleanup or lower-priority progress.

# 13. Stream Processing

High-rate Stream processing should use a dedicated bounded pipeline.

The design shall define:

- expected and worst-case rate;
- burst size;
- queue capacity;
- decode cost;
- recording cost;
- display update rate;
- downsampling or aggregation method;
- loss and gap detection;
- overload behavior;
- memory limit.

The UI should normally receive a display-ready snapshot or batch rather than one cross-thread callback per sample.

Recording and visualization may have different consumers and capacities. Loss in one consumer shall not silently corrupt the other.

---

# 14. Shutdown

Shutdown shall be deterministic and idempotent.

A typical sequence is:

```text
Stop accepting new user work
    -> Cancel application lifetime
    -> Stop reconnect attempts
    -> Cancel or complete pending operations
    -> Stop producers
    -> Drain or discard bounded queues according to policy
    -> Flush critical logs and recordings within a bounded time
    -> Close Transport and external resources
    -> Join owned workers
    -> Complete UI close
```

Shutdown shall not wait indefinitely. A forced termination path may exist, but the data-loss and resource implications shall be documented.

Dispose, close, and shutdown methods shall be safe when called more than once unless the platform contract explicitly states otherwise.

---

# 15. Concurrency Diagnostics

The system should expose diagnostics for:

- queue depth and capacity;
- dropped or replaced item counts;
- pending request count;
- request timeout count;
- reconnect attempts;
- callback or processing latency;
- Stream gap count;
- background fault count;
- shutdown duration;
- current connection generation.

Diagnostics shall be bounded and shall not themselves create a high-rate logging problem.

---

# 16. Concurrency Testing

Tests should cover:

- response arriving before, during, and after timeout handling;
- cancellation racing with completion;
- disconnect racing with send or response;
- duplicate and late response;
- stale prior-generation and failed-attempt callback;
- queue full behavior;
- slow consumer and burst input;
- shutdown during active operations;
- exception in producer or consumer;
- UI close during connect or reconnect;
- repeated start and stop;
- thread-affinity enforcement;
- deterministic ordering where guaranteed;
- absence of ordering assumptions where not guaranteed.

Tests should use controllable clocks, schedulers, fake Transports, and barriers where practical rather than relying only on arbitrary sleep delays.

---

# 17. Concurrency Anti-Patterns

Reject or explicitly justify:

1. Unbounded task creation for incoming data.
2. `async void` or equivalent outside required event-handler boundaries.
3. Fire-and-forget work with unobserved exceptions.
4. Blocking on asynchronous results from the UI thread.
5. Shared mutable collections with only partial synchronization.
6. Holding a lock across I/O, await, or callback invocation.
7. One global lock for unrelated subsystems.
8. Timer callbacks that can overlap without design.
9. Reusing objects or buffers after asynchronous ownership has transferred.
10. Automatic retry of non-idempotent commands without deduplication.
11. Stale callbacks updating a new connection generation.
12. Closing the application without cancelling and joining owned work.
13. Using arbitrary delays as the primary synchronization mechanism in tests.

---

# 18. Concurrency Review Checklist

- [ ] Each subsystem has a documented concurrency model.
- [ ] Mutable state and execution-context ownership are explicit.
- [ ] UI access is confined to the UI thread.
- [ ] Blocking work is absent from the UI thread.
- [ ] Queues, channels, buffers, and task creation are bounded.
- [ ] Overflow and backpressure policies match data semantics.
- [ ] Cancellation scopes and timeout ownership are defined.
- [ ] Pending request completion is race-safe and single-shot.
- [ ] Every connection attempt receives a unique generation before asynchronous work begins, and prior or failed generations cannot update current state.
- [ ] Control and lifecycle work cannot be starved by Stream, logging, or recording traffic.
- [ ] Locks protect clear invariants and are not held across I/O or await.
- [ ] Lock order is documented when multiple locks exist.
- [ ] Timer overlap behavior is defined.
- [ ] Stream processing has rate, capacity, loss, and overload analysis.
- [ ] Shutdown is deterministic, bounded, and idempotent.
- [ ] Background exceptions are observed and reported.
- [ ] Concurrency tests cover race boundaries rather than only the normal path.
