# Host-Device Control Framework

A reusable, AI-consumable engineering authority set for designing, implementing, reviewing, and validating systems in which a **Coordinator** supervises one or more **Nodes**.

The repository is maintained as a personal engineering methodology project. GitHub `main` is the sole source of truth for maintained repository content. Detached packages require immutable source identity and integrity records.

## Intended Operating Model

```text
Human Product Authority
    defines requirements, risks, constraints, and approval
            ↓
Repository Authority Set
    routes architecture, Protocol, role, language, and validation decisions
            ↓
AI and Human Engineering Work
    analyzes, designs, implements, reviews, and generates tests
            ↓
Objective Evidence and Human Acceptance
    builds, executes, measures, reviews, and approves the bounded result
```

AI may accelerate engineering work, but it cannot own Product authority, fabricate evidence, self-approve, or replace target validation and responsible human judgment.

## Documentation Domains

| Directory | Responsibility |
|---|---|
| [`docs/framework/`](docs/framework/) | AI routing, reusable Coordinator/Node architecture, and Product application analysis |
| [`docs/protocol/`](docs/protocol/) | Protocol YAML representation, compatibility, Registry, and security governance shared by Coordinator and Node |
| [`docs/coordinator/`](docs/coordinator/) | Coordinator-specific software realization |
| [`docs/node/`](docs/node/) | Node-specific software realization |
| [`docs/coding-rules/`](docs/coding-rules/) | Programming-language implementation authorities |
| [`docs/validation/`](docs/validation/) | Evidence methods and conformance/review views that do not independently create requirements |

## Current Document Set

| Document | Version | Status | Purpose |
|---|---:|---|---|
| [`AI_Engineering_Usage_Guide.md`](docs/framework/AI_Engineering_Usage_Guide.md) | v1.0.21 | Draft for Review | AI entry point, authority routing, Multi-Node-aware task workflows, evidence states, prohibited behaviors, and human approval boundary |
| [`Coordinator_Node_Control_Framework.md`](docs/framework/Coordinator_Node_Control_Framework.md) | v1.1.0 | Baseline | Reusable Single-Node and Multi-Node architecture, role and target boundaries, timing, safety, security, Firmware Update, Runtime, validation, and governance |
| [`Framework_Application_Analysis_Template.md`](docs/framework/Framework_Application_Analysis_Template.md) | v1.1.0 | Baseline | Method for applying the Framework to a Product, including topology, identity, resource, Reuse Classification, Protocol inputs, risks, Gaps, MVP, and acceptance evidence |
| [`Protocol_YAML_Definition_Guide.md`](docs/protocol/Protocol_YAML_Definition_Guide.md) | v1.1.0 | Baseline | Protocol YAML syntax, Multi-Node node_model semantics, machine-verifiable governance representation, Schema Validation, Semantic Lint, and Code Generation |
| [`Protocol_YAML_Template.md`](docs/protocol/Protocol_YAML_Template.md) | v1.1.0 | Baseline | Reusable Single-Node and Multi-Node Project Protocol YAML starting structure, examples, and review checklists |
| [`Protocol_Compatibility_Rules.md`](docs/protocol/Protocol_Compatibility_Rules.md) | v1.1.0 | Draft for Review | Protocol change classification, Single-Node and Multi-Node compatibility, mixed-version operation, migration, deprecation, removal, and evidence |
| [`Protocol_Registry_Governance.md`](docs/protocol/Protocol_Registry_Governance.md) | v1.1.0 | Draft for Review | Protocol identifiers plus distinct Node identity, runtime address, route, allocation, lifecycle, retirement, non-reuse, merge control, and evidence |
| [`Protocol_Security_Profile.md`](docs/protocol/Protocol_Security_Profile.md) | v1.1.0 | Draft for Review | Security applicability, per-Node identity and Session binding, authorization, replay, Counter, Rekey, reconnect, credentials, Firmware Update, and evidence |
| [`Coordinator_Software_Engineering_Rules.md`](docs/coordinator/Coordinator_Software_Engineering_Rules.md) | v1.1.0 | Draft for Review | Cross-language Coordinator architecture, per-Node ownership and isolation, lifecycle, concurrency, diagnostics, configuration, security, testing, and release rules |
| [`Coordinator_Architecture_Patterns.md`](docs/coordinator/Coordinator_Architecture_Patterns.md) | v1.1.0 | Draft for Review | Coordinator layering, Node Registry and Context, immutable target binding, per-Node state and resources, shared-bus scheduling, aggregate state, and multi-target patterns |
| [`Coordinator_Concurrency_Guide.md`](docs/coordinator/Coordinator_Concurrency_Guide.md) | v1.1.0 | Draft for Review | Per-Node and aggregate execution ownership, asynchronous I/O, cancellation, queues, fairness, backpressure, connection generations, overload, and bounded shutdown |
| [`Coordinator_Logging_Guide.md`](docs/coordinator/Coordinator_Logging_Guide.md) | v1.1.0 | Draft for Review | Structured per-Node diagnostics, identity, route, Session and correlation context, redaction, bounded delivery, retention, export, and logger-failure behavior |
| [`Coordinator_Testing_Guide.md`](docs/coordinator/Coordinator_Testing_Guide.md) | v1.1.0 | Draft for Review | Coordinator test layers plus Multi-Node isolation, targeting, race, conflict, shared-resource, broadcast, update, simulator, fuzz, and evidence coverage |
| [`Coordinator_UI_Engineering_Guide.md`](docs/coordinator/Coordinator_UI_Engineering_Guide.md) | v1.1.0 | Draft for Review | Node selection and immutable operation binding, aggregate and per-Node views, partial results, stale state, responsiveness, visualization, and input safety |
| [`Node_Software_Engineering_Rules.md`](docs/node/Node_Software_Engineering_Rules.md) | v1.1.0 | Draft for Review | Node identity, addressing, target validation, broadcast response, Session isolation, lifecycle, resources, safety, telemetry, diagnostics, Bootloader handoff, and target tests |
| [`Embedded_C_Coding_Rules.md`](docs/coding-rules/Embedded_C_Coding_Rules.md) | v1.0.17 | Final Baseline | Product-owned Embedded C implementation, memory, arithmetic, State Machine, ISR, callback, RTOS, Protocol, and review rules |
| [`CSharp_Coding_Rules.md`](docs/coding-rules/CSharp_Coding_Rules.md) | v1.0.4 | Draft for Review | Product-owned C# language and .NET implementation rules |
| [`Repository_Validation_Checklist.md`](docs/validation/Repository_Validation_Checklist.md) | v1.0.7 | Draft for Review | Repository structural, registry, manifest, canonical-reference, executable Protocol schema/fixture, evidence-state, and detached-package checks |
| [`Validation_Evidence_Guide.md`](docs/validation/Validation_Evidence_Guide.md) | v1.1.0 | Draft for Review | Evidence identity, traceability, reproducibility, execution state, Multi-Node topology and isolation records, ownership, anomaly, retention, integrity, and AI limitations |
| [`Protocol_Validation_Checklist.md`](docs/validation/Protocol_Validation_Checklist.md) | v1.1.0 | Draft for Review | Traceable Protocol YAML, node_model, topology, identity, addressing, targeting, scope, security, compatibility, fixture, and interoperability evidence view |
| [`Framework_Conformance_Checklist.md`](docs/validation/Framework_Conformance_Checklist.md) | v1.1.0 | Draft for Review | Traceable Framework role, authority, Multi-Node topology and isolation, immutable targeting, lifecycle, resources, safety, security, update, deviation, and evidence view |
| [`Coding_Rules_Review_Checklist.md`](docs/validation/Coding_Rules_Review_Checklist.md) | v1.0.0 | Draft for Review | Common review entry point for applicable language Coding Rules, types, arithmetic, resources, errors, concurrency, APIs, state machines, generated code, analysis, tests, and deviations |
| [`AI_Generated_Artifact_Validation_Guide.md`](docs/validation/AI_Generated_Artifact_Validation_Guide.md) | v1.1.0 | Draft for Review | Authority, prompt, stale-source, invented-topology, identity/address confusion, code/document/test, execution evidence, target verification, security, approval, and records |

The machine-readable [`authority-registry.yaml`](authority-registry.yaml) is the controlled source for document identity, version, status, Repository Role, applicability, authority topics, prerequisites, README purpose, and AI manifest routing-role fields. The validator requires the registry, this table, directory indexes, and the AI Active Document Manifest to agree.

## AI Task Routing

```text
Any AI-assisted engineering task
    -> AI Engineering Usage Guide
    -> Identify Product, role, language, Protocol, and evidence boundary

Architecture or system-boundary task
    -> Coordinator/Node Control Framework
    -> Framework Application Analysis Template for Product application

Protocol definition task
    -> Protocol YAML Definition Guide and Template
    -> Protocol Compatibility Rules when change/evolution is in scope
    -> Protocol Registry Governance when identifiers are in scope
    -> Protocol Security Profile when security is in scope

Coordinator implementation task
    -> Coordinator Software Engineering Rules
    -> Applicable Coordinator topic Guide
    -> Applicable language Coding Rules

Node implementation task
    -> Node Software Engineering Rules
    -> Applicable Protocol authorities
    -> Applicable language Coding Rules

Validation or release claim
    -> Validation Evidence Guide
    -> Applicable Protocol, Framework, Coding Rules, Repository, or AI-artifact validation view
```

Routing is **role-first and language-second**. A language does not determine whether software is a Coordinator or Node. Resolve conflicts by topic ownership before applying document precedence.

## Filename and Release Artifact Policy

Maintained Markdown filenames use stable canonical names without embedded document versions, release labels, RC suffixes, or dates. Document versions remain in metadata and Version History.

Immutable identity belongs in Git commits, tags, Releases, package manifests, and release-package filenames. A detached package should identify the source commit/tag/Release and include a file manifest and hash record appropriate to its distribution process.

## Authority Boundary

- `AI_Engineering_Usage_Guide.md` owns AI routing, evidence-state reporting, prohibited AI behavior, and the human approval boundary.
- `Coordinator_Node_Control_Framework.md` owns reusable roles, architecture, responsibility boundaries, timing, safety placement, security placement, Runtime, Firmware Update architecture, and governance.
- `Framework_Application_Analysis_Template.md` owns the method and records used to apply the Framework to a Product.
- `Protocol_Compatibility_Rules.md` owns Protocol change classification, version consequences, mixed-version operation, deprecation, and removal.
- `Protocol_Registry_Governance.md` owns identifier allocation, namespaces, lifecycle, retirement, and non-reuse.
- `Protocol_Security_Profile.md` owns Protocol security applicability and secure-session lifecycle governance.
- `Protocol_YAML_Definition_Guide.md` owns the machine-verifiable representation, Semantic Lint, validation, and Code Generation of the wire contract and governance decisions.
- `Coordinator_Software_Engineering_Rules.md` and its topic Guides own Coordinator-specific realization within their declared scope.
- `Node_Software_Engineering_Rules.md` owns Node-specific realization.
- Language Coding Rules own language-level implementation rules.
- Validation Guides and Checklists expose evidence, traceability, review, and conformance views; they do not independently create Product, Framework, Protocol, role, or coding requirements.
- Approved Product requirements, risk controls, SDD, hardware specifications, Project Protocol, and configuration remain Product/Project authorities.

A Draft for Review is proposed authority until explicitly adopted or promoted by an authorized human process.

## Engineering Principles

1. Separate Product authority from reusable framework guidance.
2. Treat Coordinator and Node as relationship roles, not fixed hardware or language identities.
3. Keep Protocol meaning independent from concrete Transport implementation where required.
4. Preserve Node authoritative actual state and local safety ownership.
5. Make identifiers, compatibility, security, optionality, error behavior, and lifecycle machine-verifiable.
6. Bound time, memory, queues, buffers, retries, histories, shutdown, and failure behavior.
7. Distinguish generated output, review, execution, target verification, and human approval.
8. Require traceable evidence for claims; a successful tool proves only its implemented boundary.
9. Prevent AI from inventing requirements, secrets, APIs, tests, evidence, or approval.
10. Keep GitHub `main` and controlled release identities as the authoritative repository history.

## Intended Engineering Flow

```text
Product Requirements and Risk Controls
        ↓
Framework Application Analysis
        ↓
Coordinator / Node Responsibility Mapping
        ↓
Protocol YAML + Compatibility + Registry + Security Decisions
        ↓
Coordinator and Node Software Architecture
        ↓
Language-Specific Implementation Rules
        ↓
Generated and Handwritten Implementation
        ↓
Protocol / Framework / Coding / AI Artifact Validation
        ↓
Objective Evidence, Human Review, and Release Decision
```

After the current authority set is adopted and validated, expansion should focus on executable tooling and proof: Protocol schema, semantic linter, compatibility checker, generators, Golden Test Vectors, reference Coordinator/Node implementations, and interoperability tests rather than adding overlapping core authorities.

## Repository Structure

```text
host-device-control-framework/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── NOTICE.md
├── authority-registry.yaml
├── requirements-validation.txt
├── schema/
│   └── protocol.schema.yaml
├── .github/
│   └── workflows/
│       └── document-validation.yml
├── docs/
│   ├── framework/
│   │   ├── README.md
│   │   ├── AI_Engineering_Usage_Guide.md
│   │   ├── Coordinator_Node_Control_Framework.md
│   │   └── Framework_Application_Analysis_Template.md
│   ├── protocol/
│   │   ├── README.md
│   │   ├── Protocol_YAML_Definition_Guide.md
│   │   ├── Protocol_YAML_Template.md
│   │   ├── Protocol_Compatibility_Rules.md
│   │   ├── Protocol_Registry_Governance.md
│   │   └── Protocol_Security_Profile.md
│   ├── coordinator/
│   │   ├── README.md
│   │   ├── Coordinator_Software_Engineering_Rules.md
│   │   ├── Coordinator_Architecture_Patterns.md
│   │   ├── Coordinator_Concurrency_Guide.md
│   │   ├── Coordinator_Logging_Guide.md
│   │   ├── Coordinator_Testing_Guide.md
│   │   └── Coordinator_UI_Engineering_Guide.md
│   ├── node/
│   │   ├── README.md
│   │   └── Node_Software_Engineering_Rules.md
│   ├── coding-rules/
│   │   ├── README.md
│   │   ├── Embedded_C_Coding_Rules.md
│   │   └── CSharp_Coding_Rules.md
│   └── validation/
│       ├── README.md
│       ├── Repository_Validation_Checklist.md
│       ├── Validation_Evidence_Guide.md
│       ├── Protocol_Validation_Checklist.md
│       ├── Framework_Conformance_Checklist.md
│       ├── Coding_Rules_Review_Checklist.md
│       └── AI_Generated_Artifact_Validation_Guide.md
├── tools/
│   ├── validate_repository.py
│   └── validate_protocol.py
└── tests/
    ├── fixtures/
    │   ├── protocol/
    │   │   ├── valid_*.yaml
    │   │   └── invalid_*.yaml
    │   └── protocol_expectations.yaml
    ├── test_validate_repository.py
    ├── test_validate_protocol.py
    └── test_security_regressions.py
```

Directory `README.md` files are non-normative indexes. All other maintained Markdown under `docs/` is governed through `authority-registry.yaml`.

## Repository Validation

Run locally:

```bash
python -m pip install --disable-pip-version-check --require-hashes -r requirements-validation.txt
python tools/validate_repository.py
python tools/validate_protocol.py tests/fixtures/protocol/valid_*.yaml
python -m unittest discover -s tests -v
```

The repository validator checks structure, registry equality, metadata/version/status, directory indexes, the AI manifest, stable filenames, links, headings, fences, tables, NOTICE sections, routing, workflow controls, the Protocol schema, valid/invalid semantic fixtures, and regression-protected governance failures. `validate_protocol.py` may also be run directly against Project Protocol YAML files.

A passing result does not prove semantic correctness, Product suitability, safety, security adequacy, regulatory compliance, physical behavior, or human approval.

## Current Status

The repository now contains a machine-verifiable Single-Node and Multi-Node architecture baseline across Framework, Protocol governance, Coordinator, Node, and validation layers. The conditional `node_model`, semantic validator, schema, fixtures, and regression tests cover independent links, shared multidrop buses, and routed gateways while retaining legacy Single-Node YAML compatibility. Draft authorities remain **Draft for Review** until explicitly adopted.

The next engineering phase is reference implementation, transport-specific Project adoption, interoperability testing, and target evidence rather than overlapping core-document expansion.

## Authorship and AI Assistance

Ray Yang maintains the engineering direction and editorial decisions. Generative AI tools may assist drafting, review, restructuring, consistency checking, implementation support, and artifact generation. See [`NOTICE.md`](NOTICE.md) for the full disclosure and no-company-representation statement.

## Copyright and Usage

Copyright © 2026 Ray Yang. See [`LICENSE`](LICENSE) and [`NOTICE.md`](NOTICE.md). Third-party materials remain subject to their own terms.
