# Coordinator Engineering Documents

Repository Role: Non-normative directory index

This directory contains approved and proposed cross-language software engineering authority for components that perform or directly support the Coordinator role.

## Documents

- [`Coordinator_Software_Engineering_Rules.md`](Coordinator_Software_Engineering_Rules.md) — Draft for Review / proposed cross-topic normative authority for Coordinator minimum engineering rules, lifecycle, state ownership, communication integration, security, deviation, and release governance.
- [`Coordinator_Architecture_Patterns.md`](Coordinator_Architecture_Patterns.md) — Draft for Review / Coordinator layering, dependency direction, state ownership, command and receive pipelines, lifecycle, multi-Node isolation, and architecture review patterns.
- [`Coordinator_Concurrency_Guide.md`](Coordinator_Concurrency_Guide.md) — Draft for Review / Coordinator execution-context ownership, asynchronous I/O, cancellation, timeout, backpressure, connection generations, overload, and bounded shutdown.
- [`Coordinator_Logging_Guide.md`](Coordinator_Logging_Guide.md) — Draft for Review / Structured diagnostic events, correlation, redaction, injection resistance, bounded delivery, retention, export, and logging-failure behavior.
- [`Coordinator_Testing_Guide.md`](Coordinator_Testing_Guide.md) — Draft for Review / Coordinator test layers, Protocol and Transport coverage, deterministic race testing, fault injection, fuzzing, simulator governance, and evidence integrity.
- [`Coordinator_UI_Engineering_Guide.md`](Coordinator_UI_Engineering_Guide.md) — Draft for Review / Coordinator presentation state, command feedback, stale data, multi-Node binding, responsiveness, visualization, input safety, and engineering controls.

## Authority Boundary

Coordinator and Node are system roles, not fixed hardware or language identities. This directory does not own Node-specific realization; that belongs in `../node/`. It also does not own C#, Java, C++, or other language syntax and style rules; those belong in `../coding-rules/`. Shared compatibility, Registry, and security governance belongs in `../protocol/`.

`Coordinator_Software_Engineering_Rules.md` owns cross-topic Coordinator minimum rules. Each topic-specific Guide remains proposed until explicitly adopted for Project use and then owns only the detailed realization topic declared in its metadata and Authority Boundary. A Guide shall not weaken the Framework, Project requirements, Protocol authority, Coordinator Software Engineering Rules, or applicable language rules.
