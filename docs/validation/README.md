# Validation Documents

**Repository Role:** Non-normative directory index

This directory contains evidence guidance, review checklists, conformance views, and AI-artifact validation methods that apply across the repository.

## Documents

- [`Repository_Validation_Checklist.md`](Repository_Validation_Checklist.md) — **Draft for Review / operational checklist** for repository structure, authority manifests, references, metadata, Protocol schema/fixtures, CI, and package integrity.
- [`Validation_Evidence_Guide.md`](Validation_Evidence_Guide.md) — **Draft for Review / operational evidence method** for evidence identity, traceability, reproducibility, Multi-Node topology/isolation records, ownership, review, anomalies, retention, and AI limitations.
- [`Protocol_Validation_Checklist.md`](Protocol_Validation_Checklist.md) — **Draft for Review / conformance checklist** for Protocol definition, `node_model`, topology, identity/addressing, targeting, scope, compatibility, security, malformed input, fixtures, and interoperability evidence.
- [`Framework_Conformance_Checklist.md`](Framework_Conformance_Checklist.md) — **Draft for Review / conformance checklist** for Framework role boundaries, Multi-Node topology/isolation, immutable targeting, lifecycle, resources, reconnect, safety, Bootloader, deviation, and evidence.
- [`Coding_Rules_Review_Checklist.md`](Coding_Rules_Review_Checklist.md) — **Draft for Review / common review entry point** for applicable language Coding Rules and their evidence.
- [`AI_Generated_Artifact_Validation_Guide.md`](AI_Generated_Artifact_Validation_Guide.md) — **Draft for Review / operational validation method** for AI-assisted code, documents, tests, analyses, invented-topology and identity/address checks, and generated evidence.

## Required Reading Order

1. Identify the governing Product, Framework, Protocol, role, language, and Project authorities.
2. Use [`Validation_Evidence_Guide.md`](Validation_Evidence_Guide.md) to define acceptable evidence and evidence state.
3. Select the applicable checklist or AI-artifact Guide.
4. Record findings, evidence references, anomalies, deviations, reviewer, and approval state.
5. Return any requirement question to the owning authority rather than rewriting it in a checklist.

## Common Checklist Principle

> Checklists do not independently create requirements. They provide review, traceability, and evidence-capture views of requirements established by governing authority documents.

A checklist item marked `N/A` shall include a rationale when applicability is not obvious. A blank item is not evidence of conformance.

## Tooling

Repository structural validation is implemented by:

```text
requirements-validation.txt
schema/protocol.schema.yaml
tools/validate_repository.py
tools/validate_protocol.py
tools/verify_external_anchor.py
tests/fixtures/protocol/
tests/test_validate_repository.py
tests/test_validate_protocol.py
.github/workflows/document-validation.yml
```

Install the pinned dependency before local execution:

```bash
python -m pip install --disable-pip-version-check --require-hashes -r requirements-validation.txt
python tools/validate_repository.py
python tools/validate_protocol.py tests/fixtures/protocol/valid_*.yaml
python -m unittest discover -s tests -v
# After creating the signed legal-baseline tag:
python tools/verify_external_anchor.py --commit "$(git rev-parse HEAD)"
```

A passing automated result proves only the checks implemented by the validator. It does not prove semantic correctness, Product suitability, security adequacy, regulatory compliance, physical behavior, or human approval.

## Authority Boundary

Validation artifacts expose methods, evidence states, findings, and conformance views. They do not silently redefine Product requirements, Framework rules, Protocol contracts, role-specific engineering rules, Coding Rules, risk controls, or approval status.

A document shall not claim that a build, test, analysis, measurement, inspection, or review passed unless that activity was actually executed and its evidence is available.
