# Protocol Registry Governance

**Canonical Filename:** `Protocol_Registry_Governance.md`  
**Document Version:** v1.0.0  
**Status:** Draft for Review  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-19  
**Language:** English  
**Intended Audience:** Protocol owners, system architects, Coordinator and Node developers, code-generator owners, reviewers, configuration managers, test engineers, and AI-assisted engineering systems  
**Repository Role:** Proposed normative Protocol identifier Registry and allocation-governance authority shared by Coordinator and Node implementations  
**Related Documents:**
- `../framework/AI_Engineering_Usage_Guide.md`
- `../framework/Coordinator_Node_Control_Framework.md`
- `Protocol_YAML_Definition_Guide.md`
- `Protocol_YAML_Template.md`
- `Protocol_Compatibility_Rules.md`
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
| v1.0.0 | 2026-07-19 | Draft for Review | Initial Draft defining Protocol namespaces, identifier allocation, uniqueness, lifecycle, retirement, merge control, generated artifacts, validation, and evidence. |

---

# Part I — Registry Authority

## 1. Purpose

This document governs the allocation and lifecycle of Protocol identities used by Coordinator and Node implementations. It prevents accidental collision, semantic aliasing, unauthorized local allocation, and reuse of retired identities.

It does not prescribe the YAML syntax used to store Registry entries. That representation belongs to `Protocol_YAML_Definition_Guide.md` and the approved Project Protocol.

## 2. Authority Boundary

- This document owns Message ID, Capability ID, namespace, range, allocation, retirement, and non-reuse policy.
- `Protocol_Compatibility_Rules.md` owns the compatibility impact of Registry changes.
- `Protocol_Security_Profile.md` owns security-profile identity and security lifecycle policy.
- `Protocol_YAML_Definition_Guide.md` owns machine-readable Registry representation, schema, and lint behavior.
- The approved Project Registry owns actual allocated values.
- Coordinator and Node source code, local constants, generators, tests, and documents are consumers of the Registry and shall not become competing allocation authorities.

## 3. Registry as Source of Truth

Each Protocol family shall have one controlled Registry source for every governed identifier class.

The Registry shall identify:

- Protocol family and Registry version;
- identifier class and width;
- namespace and range ownership;
- allocated numeric value;
- canonical symbolic name;
- direction and execution environment when applicable;
- lifecycle state;
- first allocation and deprecation version;
- owning Product or shared authority;
- semantic reference;
- replacement when deprecated;
- allocation record and reviewer.

Generated headers, enums, documentation, lookup tables, analyzers, and test fixtures shall be derived artifacts, not independent sources of allocation truth.

# Part II — Identifier Classes and Namespaces

## 4. Governed Identifier Classes

Governed classes include, where applicable:

- Message IDs;
- Capability IDs;
- namespace IDs;
- error, result, event, alarm, and fault codes when globally registered;
- Security Profile and Handshake Profile IDs;
- Transport Profile IDs when exposed in the Protocol;
- Firmware image, component, or manifest type IDs;
- extension and vendor identifiers.

A Project shall explicitly identify which code sets are globally registered and which are local fields scoped by a containing message.

## 5. Namespace Plan

Before allocation, the Project shall define a namespace plan that separates at least the ranges needed for:

- Framework- or family-reserved values;
- shared/common Protocol values;
- Product-specific values;
- vendor or integration extensions;
- experimental or development-only values;
- test-only values, when test traffic can never enter production operation;
- future reservation and sentinels.

Range numbers are Product decisions and shall be recorded in the Project Registry. This document does not assign universal numeric ranges.

## 6. Reserved Values

Reserved values shall have a stated reason and owner. A reserved range shall not be treated as free space merely because no current symbolic entries exist.

Common reserved purposes may include:

- invalid or uninitialized value;
- broadcast or wildcard identity;
- discovery/bootstrap messages;
- future expansion;
- environment separation;
- vendor extension;
- experimental testing.

A sentinel value shall not be used as an ordinary allocation.

## 7. Experimental and Test Allocation

Experimental or test identifiers shall be isolated from production identifiers by range, namespace, environment, build gate, or another enforceable mechanism.

Promotion to production shall require a controlled production allocation. An experimental identifier shall not silently become permanent merely because prototypes used it.

# Part III — Allocation and Change Control

## 8. Allocation Ownership

A named Protocol Registry Owner or delegated review group shall approve allocations.

An implementation developer, AI system, code generator, branch, product fork, or test fixture shall not allocate a governed identifier without an approved Registry change.

The allocation request shall include:

- requested identifier class;
- canonical name and semantics;
- direction and environment;
- Product or shared scope;
- expected lifecycle;
- compatibility impact;
- security impact;
- proposed range or namespace;
- evidence that no equivalent identity already exists.

## 9. Allocation Rules

Every allocated value shall be unique within its declared scope.

The Registry shall reject:

- duplicate numeric values in one scope;
- one numeric value with multiple active semantic names;
- one semantic identity with multiple active values unless a documented migration requires it;
- symbolic aliases that allow ambiguous encoding;
- overlapping active ranges;
- values outside the declared width or range;
- allocations in reserved or unauthorized ranges;
- values that collide across Application and Bootloader when the contract requires environment separation;
- allocations missing owner, lifecycle, or semantic reference.

Human-readable names are not sufficient to resolve a numeric collision.

## 10. Canonical Name

Each identity shall have one canonical symbolic name. Spelling aliases, abbreviations, legacy names, and display labels may be documented, but they shall not become alternative machine encodings or competing generated constants.

Renaming an active canonical symbol requires impact analysis across generated code, stored data, external tools, test evidence, and documentation. The numeric meaning shall remain unchanged unless the change is classified as a new identity.

## 11. Branch and Merge Workflow

Registry changes shall be serialized or merged through a conflict-aware process.

Before merge, automation and human review shall confirm:

- the branch used the latest accepted Registry;
- no concurrent allocation claimed the same value or overlapping range;
- generated artifacts were regenerated from the merged source;
- compatibility and version decisions remain valid after conflict resolution;
- test vectors and documentation reference the merged identity.

Resolving a textual merge conflict shall not be treated as resolving an allocation conflict.

## 12. Multi-Product Coordination

When multiple Products share a Protocol family, the Registry shall distinguish shared and Product-owned namespaces and identify the authority that can allocate each range.

A Product shall not consume another Product’s range because it appears unused locally.

Shared allocation shall consider retained field versions, manufacturing tools, service tools, simulators, bootloaders, and external integrations, not only current source repositories.

# Part IV — Lifecycle

## 13. Lifecycle States

A Registry entry should use controlled lifecycle states such as:

- proposed;
- allocated;
- active;
- deprecated;
- retired;
- reserved.

The exact machine-readable values belong to the Project Registry schema.

Only approved active entries may be used for new production encoding unless a controlled migration explicitly permits deprecated use.

## 14. Deprecation

Deprecation shall preserve the identifier and its historical meaning.

A deprecated entry shall identify:

- deprecation version and date;
- reason;
- replacement, if any;
- remaining producer and consumer obligations;
- planned removal boundary;
- known dependent Products and tools.

Deprecation shall not free the value for reuse.

## 15. Retirement and Non-Reuse

A retired identifier shall remain permanently recorded and reserved against semantic reuse within the Protocol family and scope.

Reuse is prohibited because retained software, recorded data, field devices, bootloaders, logs, fixtures, and third-party integrations may continue to interpret the old meaning.

A new semantic concept requires a new identity even when the old implementation is believed to be unavailable.

## 16. Deletion Prohibition

Historical Registry entries shall not be deleted merely to simplify the current view. Corrections shall preserve an auditable history, including the previous erroneous value or allocation record where needed to understand released artifacts.

# Part V — Generated Artifacts and Validation

## 17. Generated Registry Artifacts

Generated outputs may include:

- C, C++, C#, or Java enums and constants;
- encoder/decoder dispatch tables;
- lookup and diagnostic name tables;
- protocol documentation;
- static-analysis allowlists;
- Golden Test Vector metadata;
- compatibility diff inputs;
- Wireshark or trace-decoder definitions.

Each generated artifact shall identify its Registry source identity or reproducible input hash. Manual edits to generated identity values are prohibited unless the Project explicitly owns a controlled override process.

## 18. Validation Requirements

Automated validation shall check, as applicable:

- schema and type correctness;
- value width and range;
- uniqueness by scope;
- non-overlapping ranges;
- reserved-range violations;
- canonical-name uniqueness;
- lifecycle transition validity;
- no retired-value reuse;
- references from messages, capabilities, security profiles, and generated artifacts;
- consistency across Coordinator and Node generated outputs;
- deterministic generation;
- absence of unapproved placeholders or experimental values in production baselines.

Validation shall fail rather than silently select one of two colliding entries.

## 19. Review Evidence

An allocation or lifecycle change shall retain:

- request and decision record;
- Registry source before and after change;
- diff and collision-check result;
- compatibility classification;
- security review when applicable;
- generated-artifact result;
- relevant test result;
- owner and reviewer;
- unresolved anomaly or approved deviation.

A generated file without traceable Registry input is not sufficient evidence of approved allocation.

## 20. Release Control

A release shall identify the exact Registry source used by the Protocol and generated implementations. If Registry source and generated output do not match, the release shall fail or remain explicitly unapproved.

Detached packages should include a manifest or immutable source reference sufficient to recover the Registry identity.

## 21. AI-Assisted Work

AI may suggest names, detect collisions, prepare allocation requests, regenerate artifacts, and compare Registries. AI shall not:

- invent or approve a production identifier;
- reinterpret a retired value;
- resolve an allocation conflict without human authority;
- treat a local source constant as Registry authority;
- delete history to make validation pass;
- claim generation or tests were executed when they were not.

Human approval and controlled Registry change remain required.
