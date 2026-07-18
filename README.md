# Host-Device Control Framework

A reusable engineering framework for Host-Device control systems in which a PC, SoC, or MCU Host communicates with and controls an MCU-based Device.

The framework defines reusable architecture, protocol, implementation, and engineering-governance practices for embedded control systems.

## Scope

The framework is intended for systems such as:

* PC Host to MCU Device
* SoC Host to MCU Device
* MCU Host to MCU Device
* Command and response communication
* Event and alarm reporting
* Continuous or periodic data streaming
* Capability discovery
* Session and connection management
* Firmware update and bootloader integration
* Embedded C firmware implementation

## Terminology

In this repository:

* **Host** refers to the system that configures, controls, monitors, or collects data. A Host may be a PC, SoC, or MCU.
* **Device** refers to the controlled embedded target, typically an MCU-based system.
* **Coordinator** describes the logical role normally performed by the Host.
* **Node** describes the logical role normally performed by the Device.

Host and Device describe deployment roles. Coordinator and Node describe architectural responsibilities.

## Documents

Current published baseline:

* [`Embedded_C_Coding_Rules_v1.0.13.md`](docs/Embedded_C_Coding_Rules_v1.0.13.md)
  Embedded C implementation, naming, static-memory, arithmetic-safety, Event-Driven, State Machine, ISR, callback, entry-point, Protocol, RTOS, and Vendor integration rules.

Additional framework documents will be added after public-release review.

## Current Status

This repository is under active development.

The published documents are personal engineering baselines maintained by Ray Yang. They do not represent the official policies, specifications, designs, coding standards, or documentation of any employer, company, or organization.

The rules have completed document-level review. Practical validation through Reference Implementations and real Project application remains ongoing.

## Repository Structure

```text
host-device-control-framework/
├─ README.md
├─ COPYRIGHT.md
└─ docs/
   └─ Embedded_C_Coding_Rules_v1.0.13.md
```

## Authorship and AI Assistance

The engineering concepts, architecture, rule selection, revisions, and final editorial decisions in this repository are reviewed and approved by Ray Yang.

Generative AI tools were used to assist with drafting, editing, organization, translation, consistency review, and technical review.

## Copyright and Usage

Copyright © 2026 Ray Yang. All rights reserved.

The materials in this repository are publicly available for review. Public availability does not grant permission to reproduce, modify, redistribute, publish, or incorporate the materials into another project.

See [`COPYRIGHT.md`](COPYRIGHT.md) for the complete copyright, usage, AI-assistance, and third-party-material notices.
