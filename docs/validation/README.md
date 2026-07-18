# Validation Documents

This directory contains validation methods, evidence guidance, conformance checklists, structural review reports,
compatibility reports, and controlled validation records that apply across the repository.

## Current Documents

- [`Repository_Validation_Checklist.md`](Repository_Validation_Checklist.md) — repository structural, manifest,
  canonical-reference, version, evidence-state, and package-traceability checks.

## Tooling

The repository-level automated checks are implemented by:

```text
tools/validate_repository.py
.github/workflows/document-validation.yml
```

The script checks deterministic structural properties. It does not prove semantic correctness, Product suitability,
regulatory compliance, security adequacy, or human approval.

## Planned Content

Future documents may include:

- Framework conformance checklists.
- Protocol structural and semantic validation guidance.
- Coding-rule review checklists.
- AI-generated artifact validation guidance.
- Cross-implementation compatibility reports.
- Golden-vector and recovery-test evidence guidance.

## Authority Boundary

Validation artifacts report methods, execution state, findings, and evidence. They do not silently redefine Product
requirements, Framework rules, Protocol contracts, coding rules, or approval status.

A document shall not claim that a test, build, analysis, measurement, or review passed unless that activity was
actually executed and its evidence is available. A passing repository-validation script is structural evidence only.
