# Protocol Documents

**Repository Role:** Non-normative directory index

This directory contains shared Coordinator/Node Protocol authorities for the machine-verifiable wire contract and its controlled evolution.

## Documents

- [`Protocol_YAML_Definition_Guide.md`](Protocol_YAML_Definition_Guide.md) — **Baseline** syntax, semantics, machine-verifiable representation, Schema Validation, Semantic Lint, and Code Generation authority.
- [`Protocol_YAML_Template.md`](Protocol_YAML_Template.md) — **Baseline** reusable Project Protocol YAML starting structure.
- [`Protocol_Compatibility_Rules.md`](Protocol_Compatibility_Rules.md) — **Draft for Review / proposed normative authority** for Protocol version consequences, compatibility dimensions, mixed-version operation, negotiation, deprecation, removal, and evidence.
- [`Protocol_Registry_Governance.md`](Protocol_Registry_Governance.md) — **Draft for Review / proposed normative authority** for Message and Capability identifiers, namespaces, allocation, uniqueness, lifecycle, retirement, non-reuse, merge control, and generated Registry artifacts.
- [`Protocol_Security_Profile.md`](Protocol_Security_Profile.md) — **Draft for Review / proposed normative authority** for security applicability, authenticated Sessions, authorization, record protection, replay, Counters, Rekey, reconnect, credentials, Bootloader separation, and Firmware Update security.

## Authority Boundary

`Protocol_Compatibility_Rules.md`, `Protocol_Registry_Governance.md`, and `Protocol_Security_Profile.md` own their stated governance topics when explicitly adopted for Project use. `Protocol_YAML_Definition_Guide.md` owns how those decisions and the wire contract are represented and validated in Protocol YAML. The Project Protocol owns actual Product messages and values.

Product behavior remains governed by approved Product requirements and application analysis. The Framework owns reusable roles and architecture. Coordinator and Node documents own role-specific realization. Transport implementation and programming-language rules are governed elsewhere.
