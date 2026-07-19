# Node Engineering Documents

**Repository Role:** Non-normative directory index

This directory contains cross-language software engineering authority for components that perform or directly support the Node role.

## Documents

- [`Node_Software_Engineering_Rules.md`](Node_Software_Engineering_Rules.md) — **Draft for Review / proposed normative authority** for Node identity, address handling, target validation, broadcast response, Session isolation, lifecycle, command execution, local safety, bounded resources, diagnostics, Bootloader handoff, and target evidence.

## Recommended Reading Order

1. [`../framework/AI_Engineering_Usage_Guide.md`](../framework/AI_Engineering_Usage_Guide.md)
2. [`../framework/Coordinator_Node_Control_Framework.md`](../framework/Coordinator_Node_Control_Framework.md)
3. [`Node_Software_Engineering_Rules.md`](Node_Software_Engineering_Rules.md)
4. Applicable documents under [`../protocol/`](../protocol/)
5. Applicable language authority under [`../coding-rules/`](../coding-rules/)
6. Approved Product requirements, SDD, hardware constraints, Project Protocol, and validation plan

## Authority Boundary

The Framework owns reusable Coordinator/Node roles and system boundaries. `Node_Software_Engineering_Rules.md` owns Node-specific software realization. Protocol authorities own the shared wire contract and its governance. Language Coding Rules own language-level implementation rules.

Node Rules do not replace Product requirements, risk controls, hardware specifications, the approved Project Protocol, or an applicable language Coding Rules document.

Coordinator and Node are roles, not fixed hardware, operating-system, or language identities. A component performing both roles shall apply the authority for each relationship and shall document the boundary.
