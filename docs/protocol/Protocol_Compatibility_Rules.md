# Protocol Compatibility Rules

**Canonical Filename:** `Protocol_Compatibility_Rules.md`  
**Document Version:** v1.1.0  
**Supersedes Document Version:** v1.0.0  
**Status:** Draft for Review  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-19  
**Language:** English  
**Intended Audience:** Product owners, system architects, Protocol designers, Coordinator and Node developers, reviewers, test engineers, release engineers, code generators, and AI-assisted engineering systems  
**Repository Role:** Proposed normative Protocol compatibility and evolution authority shared by Coordinator and Node implementations  
**Related Documents:**
- `../framework/AI_Engineering_Usage_Guide.md`
- `../framework/Coordinator_Node_Control_Framework.md`
- `Protocol_YAML_Definition_Guide.md`
- `Protocol_YAML_Template.md`
- `Protocol_Registry_Governance.md`
- `Protocol_Security_Profile.md`
- `../validation/Protocol_Validation_Checklist.md`
- `../validation/Validation_Evidence_Guide.md`

---

## Copyright and Use

Copyright © 2026 Ray Yang. All rights reserved unless a repository-level license states otherwise.

This document is independently authored for a personal engineering project. Third-party standards and publications remain subject to their own copyright, license, and trademark terms.

---

## Version History

| Version | Date | Status | Summary |
|---|---|---|---|
| v1.1.0 | 2026-07-19 | Draft for Review | Added Multi-Node compatibility classification for optional topology declarations, required on-wire targeting, identity and address scope, mixed-version Nodes, broadcast, multi-target operations, Session scope, routed gateways, and migration evidence. |
| v1.0.0 | 2026-07-19 | Draft for Review | Initial Draft defining Protocol versioning, compatibility dimensions, change classification, mixed-version operation, capability negotiation, deprecation, removal, Bootloader boundaries, and compatibility evidence. |

---

# Part I — Governance

## 1. Purpose

This document defines how a Coordinator/Node Protocol evolves without creating ambiguous interoperability claims. It owns Protocol compatibility classification, version consequences, mixed-version behavior, deprecation, and required evidence.

It does not define Product commands, payload fields, numeric identifiers, cryptographic algorithms, Transport framing, or the YAML syntax used to express those decisions.

## 2. Authority Boundary

Authority is divided as follows:

- `Coordinator_Node_Control_Framework.md` owns reusable system roles, architecture, and cross-system communication principles.
- This document owns compatibility policy, change classification, version consequences, and mixed-version obligations.
- `Protocol_Registry_Governance.md` owns identifier allocation and lifecycle.
- `Protocol_Security_Profile.md` owns Protocol security-profile selection and security lifecycle obligations.
- `Protocol_YAML_Definition_Guide.md` owns the machine-verifiable representation and lint rules for decisions governed here.
- A Project Protocol and approved Product requirements own actual messages and Product behavior.
- Validation documents expose evidence and review views; they do not create requirements.

Where a summary in another document conflicts with this document on Protocol compatibility governance, this document owns the topic unless an approved Product authority explicitly overrides it.

## 3. Normative Language

The keywords **shall**, **shall not**, **should**, **should not**, and **may** are normative as defined by the governing Project process.

## 4. Compatibility Claim

A compatibility claim shall identify:

1. Producer implementation and version.
2. Consumer implementation and version.
3. Protocol family and version.
4. Execution environment, such as Application or Bootloader.
5. Negotiated capability and security profile.
6. Transport profile when Transport behavior affects the claim.
7. Tested direction and operation set.
8. Evidence location and result.

A statement such as “compatible” without these boundaries is incomplete.

# Part II — Versioning and Change Classification

## 5. Protocol Version Model

Protocol versions shall use `MAJOR.MINOR.PATCH` semantics.

- **MAJOR** changes indicate an intentionally incompatible contract or an incompatible interpretation of an existing contract.
- **MINOR** changes add compatible functionality or compatible declarations while preserving all required behavior of the prior compatible version set.
- **PATCH** changes clarify or correct the contract without changing conforming wire behavior or required Product semantics.

A document revision number and a Product software version shall not be used as a substitute for the Protocol version.

## 6. Compatibility Dimensions

Compatibility shall be assessed independently across wire-format compatibility, behavioral compatibility, capability compatibility, security compatibility, and execution-environment compatibility. The review shall include:

- wire framing and record layout;
- message identity and direction;
- payload layout, type, unit, scale, range, and encoding;
- request/response and command-lifecycle behavior;
- event, alarm, fault, telemetry, and Streaming semantics;
- state preconditions and side effects;
- timing, timeout, retry, ordering, and idempotency;
- capability discovery and negotiation;
- security profile, Session, Counter, Rekey, and authorization behavior;
- Application and Bootloader execution environments;
- Firmware Update transaction and resume behavior;
- unknown, optional, deprecated, and unsupported data handling.

Passing one dimension shall not be represented as proof of all dimensions.

## 7. Breaking Changes

A change shall be classified as breaking when a previously conforming peer can no longer safely decode, validate, interpret, authorize, execute, reject, or recover from the changed contract as previously specified.

Breaking changes include, unless an approved compatibility mechanism proves otherwise:

- reusing an existing identifier for a different meaning;
- changing field order, width, signedness, byte order, scale, unit, range, or enum meaning;
- removing or renaming a required field, message, capability, state, or error result;
- changing a request into an event, changing direction, or changing correlation rules;
- changing required side effects, state transitions, safety behavior, or command completion semantics;
- narrowing an accepted range or removing an enum value that a compatible peer may send;
- changing timeout, retry, duplicate, ordering, or idempotency behavior in a way that can alter safe operation;
- changing security requirements, transcript binding, Key Context, authorization, or downgrade behavior incompatibly;
- allowing a formerly rejected message to trigger a safety-significant action without negotiation;
- changing Application/Bootloader ownership or permitting cross-environment Session reuse;
- changing Firmware Update identity, commit, resume, rollback, or verification semantics incompatibly.

A breaking change shall increment MAJOR or introduce a distinct Protocol family when coexistence is required.

## 8. Additive Compatible Changes

An additive change may qualify for MINOR when all of the following are true:

1. Existing required messages and behavior remain unchanged.
2. Older peers can ignore, reject, or decline the new capability through previously defined behavior.
3. New behavior is gated by capability, version, optionality, or another explicit negotiation mechanism.
4. No old peer is required to decode a longer or differently shaped payload unless the old contract already defined a safe extensibility rule.
5. Unknown values are handled exactly as previously specified.
6. Security and authorization are not weakened.
7. Mixed-version tests demonstrate the required directions.

Adding an enum value, bit, optional field, or message is not automatically compatible. The existing decoder and unknown-data policy shall support the addition.

## 9. Patch Changes

A PATCH change shall not alter conforming wire bytes, required behavior, accepted input, observable output, timing obligations, compatibility policy, or security posture.

Typical PATCH changes include:

- correcting explanatory text that contradicted the already-authoritative machine-readable contract;
- improving examples without changing required behavior;
- adding review guidance or evidence references;
- correcting a generator or implementation defect while retaining the existing Protocol contract.

If a correction changes what a conforming peer must send, accept, reject, or do, it is not merely a PATCH Protocol change.

## 10. Change Decision Record

Every Protocol change shall record:

- change identifier and owner;
- affected Protocol family and version;
- affected messages, fields, capabilities, environments, registries, and security profiles;
- compatibility dimension analysis;
- classification as PATCH, compatible MINOR, breaking MAJOR, or no Protocol change;
- migration and deprecation impact;
- required implementation and test updates;
- unresolved assumptions;
- reviewer and approval state.

# Part III — Negotiation and Mixed-Version Operation

## 11. Version Negotiation

Negotiation shall not infer compatibility from numeric ordering alone.

A peer shall use an approved negotiation rule that identifies supported Protocol family, compatible version range, capabilities, execution environment, and security profile as applicable.

Negotiation shall fail closed when:

- the Protocol family is unknown;
- no compatible version is supported;
- a mandatory capability is absent;
- a required security profile cannot be established;
- an Application message is presented to a Bootloader or vice versa without an explicit contract;
- a downgrade or profile-confusion condition is detected.

A peer shall not silently fall back to an incompatible or weaker contract.

## 12. Capability Negotiation

A new feature should be represented as a capability when it is optional, version-dependent, Product-dependent, or not universally available.

Capability negotiation shall define:

- stable capability identity;
- owning environment and role;
- required dependencies;
- version and security prerequisites;
- supported operations and limits;
- behavior when absent, unknown, disabled, or revoked;
- whether availability can change during a Session.

Capability presence shall not be inferred solely from successful Transport connection or software version text.

## 13. Optional and Conditional Behavior

An optional field or operation shall have an explicit absence meaning. Absence shall not be confused with zero, false, default, unknown, unsupported, stale, or not yet measured unless the contract states that equivalence.

A conditional rule shall identify its activation condition and the behavior when the condition is false or unknown.

A receiver shall not access optional data before proving it is present and valid.

## 14. Forward Compatibility and Backward Compatibility

For each supported version pair, the Project shall state whether it claims:

- older Coordinator with newer Node;
- newer Coordinator with older Node;
- same-version interoperability;
- Application Coordinator with Application Node;
- updater with Bootloader;
- diagnostic or service tool with each environment.

The claim may be asymmetric. Each claimed direction shall have evidence.

## 15. Reconnect and Reconciliation

After reconnect, a peer shall not assume the previous Protocol version, capabilities, Session, configuration, command state, security context, or update transaction remains valid.

The reconnect flow shall renegotiate or revalidate all state required by the active compatibility contract.

# Part IV — Deprecation, Removal, and Environment Boundaries

## 16. Deprecation Lifecycle

Deprecation shall be explicit and shall not change the meaning of the deprecated item.

A deprecation record shall identify:

- item and identifier;
- first deprecated Protocol version;
- replacement or reason no replacement exists;
- producer and consumer obligations during the support window;
- expected removal boundary;
- migration evidence;
- Product versions that still depend on the item.

Deprecated identifiers shall remain reserved and shall not be reused.

## 17. Removal Policy

Removal requires one of the following:

- a MAJOR Protocol change;
- a new Protocol family;
- an approved compatibility bridge that preserves all required legacy behavior.

Before removal, the Project shall demonstrate that supported products, tools, service workflows, manufacturing fixtures, bootloaders, and retained field versions no longer require the item or have an approved migration path.

## 18. Application and Bootloader Boundary

Application and Bootloader Protocols shall be treated as separate execution environments even when they share a physical Transport or identifier width.

Compatibility analysis shall separately address:

- discovery and environment identification;
- supported version and capability sets;
- security Handshake and Key Contexts;
- allowed commands and state transitions;
- error and recovery behavior;
- update transaction identity, resume, and commit;
- transition from Application to Bootloader and return to Application.

An Application compatibility claim shall not imply Bootloader compatibility.

## 19. Multi-Node Compatibility and Migration

Adding an optional machine-verifiable `node_model` while preserving the legacy Single-Node omission semantics and
unchanged wire behavior may be a MINOR declaration change. The following changes require independent compatibility
classification and are normally breaking unless an approved negotiation or parallel profile proves coexistence:

- adding a required target or source field to an existing exact Record;
- changing connection-bound targeting to frame or route addressing without compatible negotiation;
- changing stable Node identity, address width, reserved address values, or address-assignment semantics;
- changing Protocol Session, Secure Session, sequence, Replay, or correlation scope across Nodes;
- enabling broadcast for an existing Message or changing its response behavior;
- changing a single-target operation into broadcast or implicit multi-target execution;
- changing partial-success, cancellation, retry, idempotency, or rollback semantics;
- permitting a routed gateway to terminate or extend trust differently;
- changing Firmware Update target or concurrency semantics.

Mixed-version operation shall be evaluated per Node and per negotiated profile. One newer Node shall not force an
older compatible Node into unsupported topology, security, broadcast, or multi-target behavior. A Coordinator
shall preserve the selected version, Capability, topology, addressing, and security context in each Node context.

Migration evidence shall include, as applicable:

```text
Legacy YAML with omitted node_model
New Single-Node YAML
Old Coordinator with new Node
New Coordinator with old Node
Multiple Nodes at different compatible MINOR versions
Address reuse and replacement
Required on-wire target introduction
Broadcast and response scheduling
Per-Node Session, sequence, Replay, and correlation isolation
Routed gateway trust-boundary behavior
Firmware Update targeting and concurrency
```

A document-version increase alone does not require a Protocol MAJOR change. The actual Project Protocol version
consequence depends on wire and behavioral compatibility.

# Part V — Evidence and Control

## 20. Compatibility Evidence

Minimum evidence for a compatibility claim shall include:

- source Protocol definitions and their immutable identities;
- comparison or generated diff;
- reviewed change-classification record;
- implementation identities;
- Golden Test Vector results where applicable;
- encode/decode cross-implementation results;
- positive and negative negotiation tests;
- unsupported capability and unknown-data tests;
- reconnect and stale-state tests;
- security downgrade and wrong-environment tests where applicable;
- physical target or system evidence for timing and hardware-dependent behavior;
- anomalies, deviations, and reviewer decision.

Mock-only evidence shall be labelled as such and shall not prove physical behavior.

## 21. Compatibility Matrix

A maintained Project should record compatibility in a matrix such as:

| Coordinator | Node | Environment | Protocol | Security Profile | Claimed Scope | Evidence | Result |
|---|---|---|---|---|---|---|---|
| version/build | version/build | Application or Bootloader | family/version | identifier | operations and direction | evidence reference | Pass/Fail/Limited/Pending |

A blank cell shall not be interpreted as compatible.

## 22. Exceptions and Deviations

A deviation shall identify the violated rule, scope, rationale, risk, compensating control, evidence, owner, approver, and expiration or removal plan.

A compatibility waiver shall not authorize identifier reuse, silent security downgrade, fabricated evidence, or an unbounded mixed-version claim.

## 23. AI-Assisted Work

AI may assist with diff generation, candidate classification, matrix generation, and test design. AI shall not:

- approve a compatibility claim;
- infer support from version numbers alone;
- fabricate test execution or evidence;
- treat an example or Draft as an approved Product contract;
- silently choose a fallback security or capability path;
- hide unresolved differences.

Human engineering review and Product approval remain required.
