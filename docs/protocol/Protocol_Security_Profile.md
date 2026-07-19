# Protocol Security Profile

**Canonical Filename:** `Protocol_Security_Profile.md`  
**Document Version:** v1.0.0  
**Status:** Draft for Review  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-19  
**Language:** English  
**Intended Audience:** Product owners, security architects, Protocol designers, Coordinator and Node developers, Bootloader developers, reviewers, test engineers, manufacturing and service-tool owners, and AI-assisted engineering systems  
**Repository Role:** Proposed normative Protocol security-profile and secure-session governance authority shared by Coordinator and Node implementations  
**Related Documents:**
- `../framework/AI_Engineering_Usage_Guide.md`
- `../framework/Coordinator_Node_Control_Framework.md`
- `Protocol_YAML_Definition_Guide.md`
- `Protocol_YAML_Template.md`
- `Protocol_Compatibility_Rules.md`
- `Protocol_Registry_Governance.md`
- `../validation/Protocol_Validation_Checklist.md`
- `../validation/Validation_Evidence_Guide.md`

---

## Copyright and Use

Copyright © 2026 Ray Yang. All rights reserved unless a repository-level license states otherwise.

This document is independently authored for a personal engineering project. It is not a substitute for a Product threat model, security risk analysis, approved cryptographic standard, penetration test, or regulatory assessment.

---

## Version History

| Version | Date | Status | Summary |
|---|---|---|---|
| v1.0.0 | 2026-07-19 | Draft for Review | Initial Draft defining security-profile applicability, secure-session lifecycle, authentication, authorization, confidentiality, integrity, replay protection, counters, rekey, reconnect, credentials, downgrade prevention, Bootloader separation, Firmware Update relationship, and evidence. |

---

# Part I — Security Governance

## 1. Purpose

This document defines the governance requirements for selecting, realizing, and validating a Protocol Security Profile shared by Coordinator and Node implementations.

It does not select algorithms, keys, credentials, manufacturing secrets, trust anchors, or production values for a Product. Those decisions require approved Product security authorities and shall be represented through the Project Protocol using the syntax defined by `Protocol_YAML_Definition_Guide.md`.

## 2. Authority Boundary

- `Coordinator_Node_Control_Framework.md` owns reusable security placement and Coordinator/Node responsibility boundaries.
- This document owns Protocol Security Profile applicability, Session lifecycle, authentication and authorization boundary, anti-replay, Rekey, reconnect, credential and environment separation, and evidence obligations.
- `Protocol_Compatibility_Rules.md` owns compatibility consequences of a security change.
- `Protocol_Registry_Governance.md` owns allocation of security-related identifiers.
- `Protocol_YAML_Definition_Guide.md` owns machine-verifiable representation and linting of the selected policy.
- Product threat models, risk controls, approved algorithm lists, key-management procedures, and deployment processes remain Product or organizational authorities.

A Project shall not treat this generic Profile as approval of any specific cipher suite or credential model.

## 3. Applicability Decision

Every Project shall explicitly decide whether Protocol security is required for each execution environment, Transport exposure, operation class, and lifecycle phase.

The decision shall consider:

- physical and logical access;
- confidentiality, integrity, authenticity, and availability needs;
- safety or mission impact of unauthorized commands;
- privacy and sensitive data;
- device identity and anti-counterfeit needs;
- manufacturing, service, field update, and recovery workflows;
- resource and timing limits;
- expected service life and cryptographic agility;
- applicable Product, regulatory, and organizational security requirements.

An unsecured profile shall be an explicit, reviewed decision with scope and rationale. Omission or an unresolved placeholder shall not mean “no security required.”

## 4. Security Profile Record

A selected Project Security Profile shall identify at least:

- Profile identity and version;
- execution environment;
- authenticated roles and identities;
- credential and trust model;
- approved Key Agreement, KDF, integrity, and confidentiality mechanisms as applicable;
- transcript and context binding;
- Session and Key Context model;
- nonce and Record Counter construction;
- anti-replay window and duplicate policy;
- Counter persistence and exhaustion behavior;
- Rekey triggers, deadline, hard limit, and atomic cutover;
- authorization policy;
- reconnect and resume behavior;
- downgrade prevention;
- failure and audit behavior;
- provisioning, replacement, revocation, and recovery boundaries;
- validation evidence and approval.

Production secrets and private keys shall not be committed to this Repository.

# Part II — Secure Session Establishment

## 5. Peer Authentication

When authentication is required, each peer shall verify the identity or authorized role of the other peer using the approved Product trust model before protected Product operations are accepted.

A display name, serial-port path, USB enumeration order, network address, public discovery identifier, or self-declared software version shall not by itself establish authenticated identity.

Authentication failure shall not silently fall back to an unauthenticated mode unless an explicitly approved and separately identified mode allows it.

## 6. Session Identity and Transcript Binding

A Secure Session shall have a fresh Session identity or epoch that is bound to the negotiated Protocol family, execution environment, roles, peer identities, selected Security Profile, algorithms, nonces, ephemeral keys, and relevant capabilities.

The Handshake proof shall cover one canonical transcript. Both peers shall reject profile identity mismatch, missing transcript fields, role reflection, environment confusion, and negotiation downgrade.

## 7. Authorization Boundary

Authentication establishes who or what a peer is; authorization determines what that peer may do.

Authorization shall be evaluated at an appropriate layer and shall consider:

- authenticated identity or role;
- execution environment;
- command or operation;
- Node state and capability;
- Product mode and lifecycle phase;
- security freshness or elevated authorization requirement;
- service, manufacturing, user, or update privileges;
- local safety and Product policy.

Coordinator-side authorization or UI enablement shall not replace Node-side authoritative validation for Node-owned actions.

## 8. Pre-Session Traffic

Discovery and Handshake traffic before Session establishment shall be bounded and shall disclose only information approved for unauthenticated access.

Pre-Session processing shall enforce length, rate, resource, state, and malformed-input limits. It shall not permit ordinary Product control, sensitive telemetry, privileged diagnostics, or Firmware Update commit unless an approved profile explicitly protects that operation.

# Part III — Record Protection and Replay Control

## 9. Integrity and Confidentiality

The Profile shall specify which message classes require integrity, confidentiality, both, or an explicitly reviewed exception.

Protected records shall bind enough context to prevent valid ciphertext or authenticated data from being replayed or reinterpreted in the wrong:

- direction;
- Session or epoch;
- Key Context;
- execution environment;
- message or record type;
- Protocol family or version when relevant.

A message requiring confidentiality shall not be logged, exported, or persisted in plaintext unless an approved data-handling rule permits it.

## 10. Nonce Construction

A nonce shall not repeat under the same key.

Nonce construction shall be deterministic or random according to the approved algorithm requirements and shall bind sufficient context to prevent cross-direction, cross-context, and cross-Session reuse.

The Profile shall define exactly which peer owns each nonce component and how uniqueness survives reset, reconnect, packet loss, retransmission, and concurrency.

## 11. Record Counter Ownership

Every protected direction and Key Context shall have an unambiguous Record Counter owner.

A counter shall:

- use a defined width and initial value;
- advance according to one explicit rule;
- never silently wrap;
- reject unauthorized reuse or rollback;
- have defined duplicate, gap, reordering, and retransmission behavior;
- be isolated from other directions, contexts, Sessions, and environments.

Shared mutable counters across independent senders or execution contexts are prohibited unless a proven serialized owner guarantees uniqueness.

## 12. Counter Persistence

The Project shall decide whether counters persist across reset and shall justify the decision against key lifetime and nonce uniqueness.

If a key survives reset, the design shall prevent counter rollback under that key. Acceptable strategies may include protected persistent state, a new Session epoch and new keys, monotonic hardware state, or another reviewed mechanism.

A partially written or corrupted persistent counter shall fail safely and shall not create nonce reuse.

## 13. Replay Handling

Replay validation shall occur before a protected command is executed or protected data is accepted as fresh.

The Profile shall define:

- duplicate behavior;
- out-of-order window;
- unacceptable gap behavior;
- stale Session behavior;
- audit and rate-limit behavior;
- whether safe retransmission uses the same protected record or a new authorized request.

A duplicate command shall not be executed twice merely because Transport delivery was repeated.

# Part IV — Rekey and Reconnect

## 14. Rekey Triggers and Limits

Each Key Context shall define:

- Soft Threshold;
- Rekey Deadline;
- uncrossable Hard Limit;
- time-, data-, event-, or policy-based Rekey triggers;
- behavior while Rekey is pending;
- behavior on Rekey failure;
- maximum old-epoch acceptance.

Protected transmission shall stop before nonce reuse, Counter overflow, or the Hard Limit.

## 15. Atomic Rekey

Rekey shall create fresh keys and a new Session epoch or equivalent cryptographic generation.

Atomic cutover shall ensure that both peers can distinguish old and new epochs, that Counter state is initialized for the new keys, and that ordinary traffic cannot ambiguously use mixed key material.

The design shall define bounded overlap, acknowledgement, timeout, rollback prohibition, and recovery. A failed Rekey shall not silently continue beyond the approved limit.

## 16. Reconnect

A Transport reconnect shall not automatically restore the previous Secure Session.

After reconnect, peers shall reauthenticate and establish or resume security only through an approved, freshness-protected flow. The flow shall revalidate identity, environment, Profile, capability, authorization, Session generation, and any retained transaction state.

A stale Session ID, cached capability, old authorization, or previous Transport identity shall not be accepted as current proof.

## 17. Downgrade Prevention

Negotiation shall bind the supported and selected Security Profiles so an attacker cannot remove stronger options or force an unapproved fallback.

Peers shall reject:

- unlisted or prohibited Profile IDs;
- payload and referenced Profile mismatch;
- weaker Profile selection contrary to approved ordering or policy;
- Application/Bootloader Profile confusion;
- missing required security attributes;
- silent switch to unsecured operation.

Numeric Profile ordering alone shall not be treated as security strength.

# Part V — Credentials and Lifecycle

## 18. Credential Provisioning Boundary

The Project shall define how identities, trust anchors, credentials, and keys are generated, provisioned, activated, rotated, backed up where permitted, revoked, replaced, and destroyed.

Provisioning tools and manufacturing processes shall have explicit authorization, audit, and secret-handling controls. Development credentials shall be distinguishable from production credentials and shall not be accepted by production builds unless explicitly approved.

## 19. Key Storage Abstraction

Implementation code should access keys through a controlled cryptographic or secure-storage abstraction rather than ordinary configuration or application objects.

The abstraction shall define:

- permitted operations without exposing key material;
- access control and execution context;
- zeroization and failure behavior;
- device replacement and RMA behavior;
- backup/export prohibition or controlled exception;
- behavior when secure storage is unavailable, locked, corrupted, or reset.

Logs, crash dumps, test reports, screenshots, and support bundles shall exclude secrets.

## 20. Revocation and Replacement

The Product authority shall define how compromised, expired, replaced, or unauthorized credentials are rejected.

Replacement and RMA flows shall prevent an old device, old host, cloned identity, or retired credential from silently regaining authorization.

When offline revocation is impossible, the residual risk, update mechanism, service process, and lifetime limitation shall be documented.

# Part VI — Environment and Firmware Update Separation

## 21. Application and Bootloader Separation

Application and Bootloader shall use separate Sessions and should use separate credentials, keys, Key Contexts, authorization policies, and Handshake Profiles according to the approved threat model.

A Session, key, counter, authorization result, or replay state from one environment shall not be reused by the other unless a Product security authority explicitly defines and validates a secure handoff mechanism.

Environment identity shall be authenticated before environment-specific commands are accepted.

## 22. Firmware Update Relationship

Firmware Update security shall bind:

- target device identity and environment;
- authorized updater identity or role;
- image and component identity;
- canonical signed Manifest;
- version and anti-rollback policy;
- expected size and cryptographic hash;
- update transaction identity;
- accepted progress and resume generation;
- commit and activation authorization.

Transport encryption alone shall not replace signed image or Manifest authenticity when the Product requires it.

After reconnect or Rekey, any resumed update shall revalidate the retained transaction against the fresh authenticated Session and approved resume token or proof.

## 23. Failure Behavior

Security failures shall produce bounded, non-secret diagnostics and shall leave the Node in a defined safe or non-privileged state.

The Profile shall define behavior for:

- authentication and proof failure;
- unknown identity or Profile;
- integrity failure;
- replay, duplicate, gap, and stale epoch;
- Counter exhaustion;
- Rekey deadline and failure;
- authorization denial;
- trust-store or secure-storage failure;
- clock or freshness-source failure where applicable;
- Bootloader/Application confusion;
- Firmware Update verification failure.

Repeated failures shall not cause unbounded log, retry, allocation, or response amplification.

# Part VII — Validation and AI Controls

## 24. Required Evidence

Security evidence shall identify the exact implementation, Protocol, Profile, environment, credentials class, tools, configuration, and test boundary.

Evidence should include, as applicable:

- threat and applicability analysis;
- architecture and data-flow review;
- Profile and algorithm approval;
- cross-implementation Handshake and record vectors;
- positive and negative authentication tests;
- authorization tests by role, state, and environment;
- replay, duplicate, gap, wrap, rollback, reset, and persistence tests;
- Rekey threshold, deadline, hard-limit, and atomic-cutover tests;
- reconnect, stale Session, and downgrade tests;
- malformed-input, fuzz, resource-exhaustion, and rate-limit tests;
- provisioning, replacement, revocation, and recovery tests;
- Application/Bootloader isolation tests;
- Firmware Update signature, anti-rollback, resume, and commit tests;
- secret-redaction and support-bundle inspection;
- independent security review where required.

A simulator or mock shall not prove secure-storage behavior, hardware identity, physical attack resistance, or target timing.

## 25. Prohibited Repository Content

This Repository shall not contain:

- production private keys or symmetric secrets;
- production credential databases;
- reusable manufacturing passwords or tokens;
- real customer or patient secrets;
- unredacted secure-element dumps;
- values that permit unauthorized production access.

Examples shall use unmistakably non-production placeholders and shall be rejected by Product-baseline lint when unresolved.

## 26. AI-Assisted Security Work

AI may assist with threat enumeration, traceability, test design, diff review, and consistency checks. AI shall not:

- select or approve a production cryptographic algorithm or credential model without human authority;
- invent secret values or claim access to unavailable secrets;
- declare a security test, penetration test, or compliance assessment passed without execution evidence;
- assume an API, secure element, library, or hardware feature exists without primary-source verification;
- weaken security to make an implementation easier;
- omit unresolved security decisions;
- self-approve generated security code or documentation.

Human security review, Product approval, implementation review, and target validation remain required.
