# Coordinator Engineering Documents

Repository Role: Non-normative directory index

This directory contains approved and proposed cross-language software engineering authority for components that perform or directly support the Coordinator role.

## Documents

- [`Coordinator_Software_Engineering_Rules.md`](Coordinator_Software_Engineering_Rules.md) — Draft for Review / proposed cross-topic normative authority for Coordinator minimum engineering rules, lifecycle, state ownership, communication integration, security, deviation, and release governance.
- [`Coordinator_Architecture_Patterns.md`](Coordinator_Architecture_Patterns.md) — Draft for Review / Coordinator Node Registry and Context patterns, immutable target binding, per-Node state/resources, shared-bus scheduling, aggregate state, multi-target operations, and architecture review.
- [`Coordinator_Concurrency_Guide.md`](Coordinator_Concurrency_Guide.md) — Draft for Review / Per-Node and aggregate execution-context ownership, cancellation, timeout, queue fairness, backpressure, connection generations, overload isolation, and bounded shutdown.
- [`Coordinator_Logging_Guide.md`](Coordinator_Logging_Guide.md) — Draft for Review / Structured per-Node diagnostic identity, route, Session and correlation context, redaction, bounded delivery, retention, export, and logging-failure behavior.
- [`Coordinator_Testing_Guide.md`](Coordinator_Testing_Guide.md) — Draft for Review / Coordinator test layers plus Multi-Node identity conflict, isolation, targeting, resource, shared-bus, broadcast, update, race, fuzz, simulator, and evidence coverage.
- [`Coordinator_UI_Engineering_Guide.md`](Coordinator_UI_Engineering_Guide.md) — Draft for Review / Node selection, immutable operation binding, aggregate/per-Node views, partial results, stale data, responsiveness, visualization, input safety, and engineering controls.

## Authority Boundary

Coordinator and Node are system roles, not fixed hardware or language identities. This directory does not own Node-specific realization; that belongs in `../node/`. It also does not own C#, Java, C++, or other language syntax and style rules; those belong in `../coding-rules/`. Shared compatibility, Registry, and security governance belongs in `../protocol/`.

`Coordinator_Software_Engineering_Rules.md` owns cross-topic Coordinator minimum rules. Each topic-specific Guide remains proposed until explicitly adopted for Project use and then owns only the detailed realization topic declared in its metadata and Authority Boundary. A Guide shall not weaken the Framework, Project requirements, Protocol authority, Coordinator Software Engineering Rules, or applicable language rules.
