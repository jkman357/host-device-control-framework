# Embedded C Coding Rules

**Document Name:** `Embedded_C_Coding_Rules.md`  
**Document Version:** v1.0.15  
**Status:** Final Baseline  
**Applicable Domain:** Coordinator/Node Framework - Embedded C Firmware  
**Primary Narrative Language:** English  
**Primary Programming Language:** C  
**Normative Coding Reference:** MISRA C:2023  
**Document Type:** Project Coding Standard  
**Author:** Ray Yang  
**Maintainer:** Ray Yang  
**Repository:** `host-device-control-framework`  

Copyright © 2026 Ray Yang. All rights reserved.

This document is maintained as part of a personal engineering project. It is not an official
document of any employer or organization. No license is granted unless otherwise explicitly stated.

MISRA and MISRA C are associated with The MISRA Consortium. This document references MISRA C:2023
but does not reproduce or replace the official publication. All third-party standards, publications,
trademarks, source code, licenses, and legal notices remain the property of their respective owners.

---

## 1. Purpose

This document defines the Embedded C coding rules for the Coordinator/Node Framework. Its objectives are to:

1. Establish a consistent and maintainable coding style.
2. Reduce the risk of undefined behavior, integer overflow, memory errors, and uncontrolled state transitions.
3. Translate Event-Driven, State Machine, ISR, Protocol, and Vendor Stack architecture principles into implementation rules.
4. Apply one standard to human-written code, AI-assisted code, code review, static analysis, and testing.
5. Provide a shared baseline for the Embedded C Reference Implementation and Product implementations.

This document supplements the implementation-level rules that are not fully defined by the existing
Framework Baseline documents. It is part of the Framework Implementation Governance set.

---

## 2. Relationship to Existing Baseline Documents

This document shall be used with the following baseline documents:

- `Coordinator_Node_Control_Framework.md`
- `Framework_Application_Analysis_Template.md`
- `Protocol_YAML_Definition_Guide.md`
- `Protocol_YAML_Template.md`

The responsibility boundary is:

| Document | Primary Responsibility |
|---|---|
| Coordinator/Node Framework | Architecture, responsibility boundaries, layering, and control model |
| Application Analysis Template | Method for applying the Framework to a new application |
| Protocol YAML Guide | Protocol YAML fields, semantics, validation, and governance |
| Protocol YAML Template | Formal starting template for a Protocol YAML definition |
| Embedded C Coding Rules | Embedded C implementation, naming, memory, safety, and architecture realization |

This document shall not redefine Protocol YAML fields or existing Coordinator/Node responsibility boundaries.

---

## 3. Compliance Position

### 3.1 MISRA C Position

MISRA C:2023 is the underlying language-safety reference for this coding standard.

Where MISRA C:2023 does not prescribe one approach, permits multiple approaches, or where the Project
requires a stricter constraint, this document defines the Project rule.

The approved public statement is:

> This Project-specific coding standard is informed by MISRA C:2023 and defines additional
> framework-specific implementation rules.

Compliance with this document alone does not constitute MISRA C:2023 compliance.

The Project shall not claim full MISRA compliance until the following evidence exists:

- Guideline Enforcement Plan
- Static Analysis Report
- Compiler Configuration Record
- Deviation Record
- Adopted Code Assessment
- Guideline Compliance Summary
- Review Evidence

### 3.2 Conflict Handling

When this document conflicts with MISRA C:2023, compiler constraints, platform constraints, or Adopted Code,
the Project shall:

1. Identify the exact conflict.
2. Explain the cause and impact.
3. Evaluate alternative controls.
4. Create a Deviation Record when required.
5. Obtain review approval before acceptance.

A compiler extension, vendor recommendation, generated configuration, or existing implementation shall not
silently override this coding standard.

---

## 4. Scope

### 4.1 In Scope

This document directly governs Product-owned Code, including:

- Application Layer
- State Machine
- Event Dispatcher
- Service Layer
- Protocol Layer
- Generated Protocol Contract
- Driver Adapter
- Board Support Package
- Hardware Abstraction Layer
- Test Support Code
- Product-owned Library Code
- RTOS and Vendor Stack integration code
- Product-owned configuration code
- Product-owned generators and generator templates

This document also governs how Product-owned Code configures, wraps, calls, and validates Adopted Code.

### 4.2 Adopted Code

The following are normally classified as Adopted Code:

- MCU Vendor Driver Library
- USB or communication stack
- RTOS kernel
- Compiler runtime library
- Third-party library
- Vendor-provided generated configuration code

The internal coding style and structure of Adopted Code are not directly governed by the formatting, naming,
and modularization rules in this document.

Adopted Code should remain close to its original form. It shall not be extensively rewritten only to match
Product-owned formatting rules.

Product-owned Code shall isolate Adopted Code through an Adapter, Wrapper, or controlled Integration Layer.

### 4.3 Adopted Code Integration Boundary

The following remain Product-owned responsibilities even when the underlying implementation is Adopted Code:

- Selected version
- Build configuration
- Compile-time options
- Memory configuration
- RTOS object-creation API
- Callback integration
- Adapter or Wrapper implementation
- Error handling
- Timing behavior
- Patch and deviation management
- Known limitations
- Verification evidence

The Project shall not avoid responsibility by stating that a behavior occurs inside an RTOS, library, stack,
or generated file.

When static allocation is required, Product-owned Code shall not call an API that causes an RTOS or
middleware component to allocate memory dynamically.

Auto-generated or adopted configuration code remains within the Integration Assessment Scope whenever the
Project selects, enables, generates, compiles, or links it.

The assessment shall cover at least:

- Dynamic allocation
- Task or thread creation
- Queue or semaphore creation
- Callback execution context
- Stack usage
- Blocking behavior
- Runtime resource consumption
- Error handling
- Timing behavior
- Regeneration impact

Tool generation does not remove the obligation to assess runtime behavior and resource usage.

---

## 5. General Coding Principles

All Product-owned Code shall follow these principles:

1. Each module shall own one coherent responsibility set.
2. Each function shall perform one primary task.
3. Control flow shall be directly readable and shall not depend on hidden side effects.
4. Important state changes shall have an explicit trigger.
5. Memory capacity, ownership, lifetime, and initialization shall be explicit.
6. Errors shall not be silently ignored.
7. Interrupt Service Routines shall remain short, bounded, and non-blocking.
8. Application code shall not directly depend on a Vendor Stack.
9. Generated Code shall not be edited manually.
10. Every Product-owned `.c` and `.h` file shall contain a correct standardized File Header.
11. Product-owned implementation repositories shall use English engineering content.
12. Product-owned Code shall not use magic numbers for values with system meaning.
13. Formal builds shall complete with zero errors and zero warnings.
14. Resource usage shall be bounded and reviewable.
15. All external input shall be validated before use.
16. Every shared object shall have an explicit owner and synchronization policy.
17. The implementation shall preserve the architecture and responsibility boundaries defined by the Framework.

---

## 6. File Organization

### 6.1 Source and Header Pair

A normal module shall use a `.c` and `.h` pair:

```text
app.c
app.h
```

Declarations, state objects, buffers, counters, and helper functions used only within the module shall remain
in the `.c` file and shall not be exposed in the public header.

### 6.2 Information Hiding

A public header shall expose only what callers require:

- Public types
- Public constants
- Public functions
- Explicit data-exchange structures

Module-private state, internal buffers, retry counters, vendor handles, and implementation details shall not
be exposed in a public header.

An external module shall not directly modify another module's private state.

An implementation-private data structure shall use one of these approaches:

- Remain entirely in the `.c` file.
- Be accessed through a controlled accessor API.
- Use an incomplete type or opaque handle without introducing dynamic allocation.
- Separate the public data model from the private context.

A public function shall not return a writable pointer to module-private state.

### 6.3 Header Guard

Header guards shall use uppercase letters and underscore separators:

```c
#ifndef APP_STATE_MACHINE_H
#define APP_STATE_MACHINE_H

// Public declarations.

#endif
```

### 6.4 Include Order

The recommended include order is:

1. The corresponding module header.
2. C standard library headers.
3. MCU and compiler headers.
4. Framework headers.
5. Project module headers.

Example:

```c
#include "app.h"

#include <stdbool.h>
#include <stdint.h>

#include <msp430.h>

#include "app_event.h"
#include "bsp_time.h"
#include "usb_cdc_transport.h"
```

A module shall include the declarations it uses and shall not rely on accidental transitive includes.

---

## 7. File Header Rules

### 7.1 Applicability

Every Product-owned `.c` and `.h` file shall contain a standardized File Header.

This applies to:

- Application source and headers
- Service source and headers
- Protocol-owned source and headers
- Driver Adapter source and headers
- BSP and HAL source and headers
- Test Support Code
- Product-owned Library Code
- Product-owned generated-code templates

This rule does not require modification of an original Adopted Code File Header.

### 7.2 Placement

The File Header shall be the first meaningful content in the file and shall appear before:

- `#include`
- Header guard
- Macro definition
- Type declaration
- Function declaration
- Function definition
- Global or file-static object

Only a UTF-8 byte-order mark or a tool-required marker may precede the File Header.

### 7.3 Comment Style

A Product-owned File Header shall use consecutive `//` comments.

Allowed:

```c
// File:
//     sample_source.c
//
// Purpose:
//     Implements a deterministic sample source.
```

Prohibited:

```c
/*
 * File:
 *     sample_source.c
 */
```

Decorative separators made from repeated `*`, `=`, `-`, or similar symbols are prohibited.

### 7.4 Required Content

A Product-owned File Header shall contain at least:

- File
- Purpose
- Responsibilities or Public Contract

A `.c` file shall use `Responsibilities` to describe its implementation responsibilities.

A `.h` file shall use `Public Contract` to describe the exposed interface and boundary.

`Notes` is optional and shall be used only for an important limitation, context, or architectural boundary.

The File Header shall not duplicate the full Detailed Design and shall not list every function when that list
would quickly become obsolete.

### 7.5 Product-owned `.c` Template

```c
// Copyright (c) 2026 <Approved Copyright Holder>. All rights reserved.
//
// File:
//     sample_source.c
//
// Purpose:
//     Implements the deterministic sample source used by communication
//     and Host application integration tests.
//
// Responsibilities:
//     - Validates supported sample-rate configuration.
//     - Generates bounded deterministic samples.
//     - Maintains module-private generation state.
//
// Notes:
//     This module does not access physical sensor hardware.
```

`<Approved Copyright Holder>` shall be replaced with the copyright holder approved for the implementation.
No unresolved placeholder may remain in a released source file.

### 7.6 Product-owned `.h` Template

```c
// Copyright (c) 2026 <Approved Copyright Holder>. All rights reserved.
//
// File:
//     sample_source.h
//
// Purpose:
//     Defines the public contract for the deterministic sample source.
//
// Public Contract:
//     - Initializes the source with a supported sample rate.
//     - Retrieves deterministic samples.
//     - Keeps internal generation state private to sample_source.c.
//
// Notes:
//     Callers shall not depend on the internal waveform implementation.
```

The header guard shall follow the File Header:

```c
#ifndef SAMPLE_SOURCE_H
#define SAMPLE_SOURCE_H
```

### 7.7 `main.c` Guidance

The `main.c` File Header shall describe entry-point responsibility.

This description is not acceptable:

```text
This file contains the function for main function.
```

Recommended form:

```c
// Copyright (c) 2026 <Approved Copyright Holder>. All rights reserved.
//
// File:
//     main.c
//
// Purpose:
//     Provides the firmware entry point.
//
// Responsibilities:
//     - Performs startup and module initialization.
//     - Enables interrupts.
//     - Runs the application event-dispatch loop.
//
// Notes:
//     Product business logic shall not be implemented in this file.
```

### 7.8 Prohibited Fields

A Product-owned File Header shall not maintain:

- Author
- Authors
- Maintainer name
- Per-file Revision History
- Last modified by
- Manual version history
- Unresolved placeholder
- Redundant creation date

Prohibited:

```c
// Author:
//     Ray Yang
//
// Revision History:
//     2020-09-28 Initial creation.
```

Authorship and incremental history shall be retained by Git.

Release-level changes shall be recorded in one or more of:

- Git commits
- `CHANGELOG.md`
- Release Notes
- Controlled Design Documents

### 7.9 Copyright and License Text

Copyright and license text shall use wording approved by the relevant project or organization.

The following placeholders are prohibited in released files:

```text
<TBD>
<Company Name>
<Project Name>
YYYY
```

The applicable year, year range, copyright holder, and license shall follow the Project's approved legal policy.

This coding standard does not itself authorize a Product implementation to invent legal wording.

### 7.10 Adopted Code

Adopted Code shall retain its original:

- Copyright
- License
- Author information
- File Header
- Notices

The Project shall not rewrite a Vendor Header, remove a third-party author, remove a license notice, convert
all original block comments, or insert a Product-owned copyright merely to satisfy this document.

When Adopted Code is modified, the patch, reason, risk, and verification evidence shall be recorded. The
modified file shall not be represented as an unchanged original.

### 7.11 Auto-generated Product-owned Files

A Product-owned Generator shall automatically insert a Generated File Header.

Minimum form:

```c
// AUTO-GENERATED FILE.
// DO NOT EDIT MANUALLY.
//
// File:
//     sample_protocol_generated.h
//
// Source:
//     protocol/sample_protocol.yaml
//
// Generator:
//     protocol_codegen
//
// Generator Version:
//     V1.0.0
//
// Purpose:
//     Defines generated protocol constants and serialization contracts.
```

The header shall identify:

- Generated-file warning
- Output file
- Source definition
- Generator
- Generator version
- Purpose

The header shall not be added or maintained manually after generation.

Vendor-generated Code follows the Adopted Code rules but remains subject to Integration Assessment.

### 7.12 Maintenance

A File Header shall be updated when any of these change:

- File name
- Module responsibility
- Public contract
- Generated source or generator
- Ownership classification
- Release or baseline status

The presence of a File Header is not evidence that its content remains correct.

### 7.13 Review Guidance

Code Review shall confirm:

1. Every Product-owned `.c` and `.h` file has a File Header.
2. The recorded file name matches the actual file name.
3. Purpose is specific and meaningful.
4. Responsibilities or Public Contract reflects the current module.
5. Author and manual Revision History fields are absent.
6. No unresolved placeholder remains.
7. A generated File Header was produced by the Generator.
8. Original Adopted Code notices were not improperly modified.

---

## 8. Project Language and Documentation Rules

### 8.1 Repository Language

A Product-owned implementation repository and generated Project folder shall use English as the engineering
language.

Product-owned engineering artifacts shall not mix English and another narrative language within one artifact,
including:

- Source files
- Header files
- File Headers
- Source-code comments
- Function documentation
- TODO, NOTE, and WARNING comments
- Build instructions
- Test descriptions
- Validation reports
- Configuration descriptions
- Script help text
- Error messages
- Generated-file notices
- Folder names
- File names
- Markdown documentation
- Protocol YAML descriptive fields

Technical abbreviations, API names, register names, Product names, protocol symbols, and proper nouns may retain
their formally defined spelling.

### 8.2 Mandatory English Root Documents

The following Product-owned root documents shall be written in English:

- `README.md`
- `CHANGELOG.md`
- `NOTICE.md`
- `VALIDATION_REPORT.md`

When present, these shall also be written in English:

- `BUILD_INSTRUCTIONS.md`
- `RELEASE_NOTES.md`
- `KNOWN_ISSUES.md`
- `MANIFEST.md`
- `SECURITY.md`
- `CONTRIBUTING.md`

Product-owned documents under `docs/` shall also be written in English unless explicitly isolated as localized
documents under Section 8.8.

### 8.3 Source-code Language

All Product-owned source-code comments and function documentation shall use English.

Allowed:

```c
// Initialize the USB transport before enabling interrupts.
usb_cdc_transport_init();
```

Prohibited:

```c
// Initialize USB communication before enabling interrupts in another language.
usb_cdc_transport_init();
```

Function documentation shall also use English:

```c
/*
 * Initializes the application state machine.
 */
void app_init(void);
```

### 8.4 Documentation Language

Product-owned Markdown, text, YAML descriptions, and validation evidence shall use complete English sentences.

Abbreviations that are not generally understood in the Project domain shall be expanded or defined at first use.

### 8.5 Folder and File Names

Product-owned folder and file names shall use English.

Allowed:

```text
application/
protocol/
validation/
docs/design/
Coding_Rules_Application_Report.md
```

Non-English or mixed-language Product-owned names are prohibited.

### 8.6 Generated Content

A Product-owned Generator shall produce the following in English:

- File Header
- Warning notice
- Source reference
- Generator description
- Protocol description
- Validation message
- Error message

Generated output shall not be translated manually file by file after generation.

A generated localization resource shall be placed in the approved localization structure.

### 8.7 Adopted Code and Legal Text

Adopted Code shall retain its original language, copyright, license, authorship, and legal notices.

Third-party legal text shall not be translated, rewritten, or normalized merely to satisfy the English rule.

Product Team explanations in `NOTICE.md` shall use English. Embedded third-party licenses and legal text shall
retain their official wording.

### 8.8 Localization Exception

Non-English content is allowed when multilingual Product behavior is a formal requirement.

Localized content shall be explicitly isolated, for example:

```text
localization/
├─ en-US/
├─ zh-TW/
└─ ja-JP/
```

Localized resources shall not be mixed into normal engineering documentation, source-code comments, or build
instructions.

When a customer, regulator, or controlled process requires a localized engineering document, it shall be
isolated, for example:

```text
docs/localized/zh-TW/
```

Unless the Project Documentation Plan states otherwise, the canonical engineering document shall remain English.

### 8.9 Governance-document Language Consistency

A governance document shall use one primary narrative language and consistent terminology, heading style, list
style, table style, code-example style, and normative wording.

The primary narrative language of this document is English.

Technical terms, identifiers, API names, file names, code examples, and proper nouns may retain their formally
defined spelling.

A merge review shall check that newly generated or edited sections do not create a visibly stitched document.

### 8.10 Mixed-language Detection

Automated checks should detect CJK characters or other unexpected narrative scripts in Product-owned engineering
files.

The scan should include:

- Product-owned `.c`
- Product-owned `.h`
- Product-owned `.md`
- Product-owned `.txt`
- Product-owned `.yaml` and `.yml`
- Product-owned scripts
- Product-owned configuration files

The scan shall exclude or separately classify:

- `vendor/`
- `third_party/`
- `licenses/`
- Vendor-generated source
- Approved localization directories
- Approved localized documents

Automated detection does not replace human review because proper nouns, legal text, and localization resources
may be valid exceptions.

### 8.11 Review Guidance

Review shall confirm:

1. Product-owned engineering content uses English.
2. One Product-owned engineering artifact does not mix narrative languages.
3. Root-level Project documents use English.
4. Product-owned folder and file names use English.
5. Source comments and function documentation use English.
6. Product-owned generated content uses English.
7. Adopted Code and legal text were not improperly translated.
8. Localization content is isolated.
9. Every exception has an owner and record.
10. Governance documents use a consistent primary narrative language and terminology style.

---

## 9. Formatting Rules

### 9.1 Indentation

- Use four spaces.
- Do not use tabs.
- Do not place multiple statements on one line.

Allowed:

```c
app_event_init();
app_init();
usb_cdc_transport_init();
```

Prohibited:

```c
app_event_init(); app_init(); usb_cdc_transport_init();
```

### 9.2 Braces

`if`, `else`, `for`, `while`, and `do while` statements shall use braces even when the body contains one statement.

Allowed:

```c
if (is_ready == true)
{
    app_start();
}
```

Prohibited:

```c
if (is_ready == true)
    app_start();
```

Prohibited:

```c
if (is_ready == true) app_start();
```

### 9.3 Line Length

A line should not exceed 120 characters.

When a line exceeds the limit, it shall be broken according to meaning. Required spaces and useful comments shall
not be removed merely to shorten the line.

### 9.4 One Statement per Line

Each line shall contain at most one statement.

Prohibited:

```c
index++; count--;
```

### 9.5 Whitespace

Whitespace shall communicate structure and shall be applied consistently.

- Use one space around binary operators.
- Do not insert whitespace between a function name and `(`.
- Use blank lines to separate logical blocks, not every statement.
- Do not align large groups of declarations with fragile manual spacing.

---

## 10. Comment Rules

### 10.1 General Comments

General comments shall use `//`.

Allowed:

```c
// Initialize the clock before starting the USB stack.
bsp_clock_init_8mhz();
```

A multi-line general comment shall use `//` on each line:

```c
// The USB initialization may temporarily use a hardware timer.
// Application timer initialization shall run afterward.
usb_cdc_transport_init();
```

### 10.2 Prohibited General Block Comments

General-purpose `/* ... */` comments are prohibited.

Prohibited:

```c
/*
 * Initialize the application.
 */
app_init();
```

### 10.3 Mandatory Function Header

Every Product-owned function declaration and function definition shall be immediately preceded by a Function
Header.

The Function Header shall use `/* ... */` and shall contain all of the following fields:

- Function
- Purpose
- Input Parameters
- Output Parameters
- Return Value

`Notes` is optional and may be added when an execution-context, reentrancy, blocking, ownership, timing, or
side-effect constraint requires explicit explanation.

The Function Header shall describe the contract implemented by the function. It shall not merely restate the
function name.

The names listed under Input Parameters and Output Parameters shall match the function signature exactly.

A parameter that is read by the function shall be listed under Input Parameters.

A pointer parameter, referenced object, or in/out parameter modified by the function shall be listed under Output
Parameters. An in/out parameter shall appear under both Input Parameters and Output Parameters, with its read and
write behavior stated clearly.

When no input parameter, output parameter, or return value exists, the applicable field shall state `None`.
The field shall not be omitted.

Required form:

```c
/*
 * Function:
 *     app_initialize
 *
 * Purpose:
 *     Initializes the application modules and establishes the initial
 *     application state.
 *
 * Input Parameters:
 *     None.
 *
 * Output Parameters:
 *     None.
 *
 * Return Value:
 *     APP_RESULT_OK:
 *         Initialization completed successfully.
 *     APP_RESULT_INITIALIZATION_FAILED:
 *         One or more required modules failed to initialize.
 */
app_result_t app_initialize(void)
{
    // Function implementation.
}
```

Required form with input and output parameters:

```c
/*
 * Function:
 *     protocol_decode_header
 *
 * Purpose:
 *     Validates and decodes a protocol header from a received byte buffer.
 *
 * Input Parameters:
 *     data:
 *         Pointer to the received byte buffer. The function does not modify
 *         the referenced data.
 *     data_length:
 *         Number of valid bytes available in data.
 *
 * Output Parameters:
 *     decoded_header:
 *         Receives the decoded header when the function returns
 *         PROTOCOL_RESULT_OK. The referenced object remains unchanged on
 *         failure.
 *
 * Return Value:
 *     PROTOCOL_RESULT_OK:
 *         The header was validated and decoded successfully.
 *     PROTOCOL_RESULT_INVALID_ARGUMENT:
 *         A required pointer is NULL.
 *     PROTOCOL_RESULT_INVALID_LENGTH:
 *         The available data is shorter than the required header length.
 *     PROTOCOL_RESULT_INVALID_DATA:
 *         One or more header fields are invalid.
 */
protocol_result_t protocol_decode_header(
    const uint8_t *data,
    uint16_t data_length,
    protocol_header_t *decoded_header);
```

Required form for a `void` return:

```c
/*
 * Function:
 *     app_process
 *
 * Purpose:
 *     Acquires and dispatches pending application events.
 *
 * Input Parameters:
 *     None.
 *
 * Output Parameters:
 *     None.
 *
 * Return Value:
 *     None.
 */
void app_process(void);
```

The Function Header shall remain synchronized with the declaration, definition, and implementation behavior.

Doxygen-style `/** ... */` is prohibited unless a future baseline explicitly adopts Doxygen.

### 10.4 Disabled Code

Comments shall not be used to retain disabled code.

Prohibited:

```c
// app_start();
// usb_send(buffer, length);
```

Git shall retain historical code.

### 10.5 TODO, NOTE, and WARNING

Approved forms are:

```c
// TODO: Add timeout handling before production release.
// NOTE: This counter saturates at ERROR_COUNT_MAX.
// WARNING: This function is called from ISR context.
```

A TODO shall identify a concrete action and shall not remain unresolved in a formal release unless it is tracked
by an approved issue.

---

## 11. Naming Rules

### 11.1 General Naming Style

| Element | Rule | Example |
|---|---|---|
| Public function | Module prefix plus lower snake case | `app_dispatch()` |
| File-static function | Module prefix plus lower snake case | `app_validate_event()` |
| Callback function | Module prefix plus purpose plus `_callback` | `usb_adapter_receive_callback()` |
| Callback typedef | Module prefix plus purpose plus `_callback_t` | `usb_receive_callback_t` |
| Local variable | Lower snake case | `sample_count` |
| Function parameter | Lower snake case | `packet_length` |
| File-static variable | `s_` plus lower snake case | `s_app_state` |
| File-static const object | `s_` plus lower snake case | `s_timeout_ms` |
| Global variable | `g_` plus lower snake case | `g_system_tick` |
| Global const object | `g_` plus lower snake case | `g_protocol_version` |
| Type | Lower snake case plus `_t` | `app_state_t` |
| Macro | Upper snake case | `USB_TX_BUFFER_SIZE` |
| Enum constant | Upper snake case | `APP_STATE_IDLE` |

### 11.2 Macro Names

All `#define` names shall use uppercase letters and underscore separators.

Allowed:

```c
#define USB_TX_BUFFER_SIZE        (256u)
#define SENSOR_SAMPLE_COUNT       (25u)
#define RETRY_COUNT_MAX           (3u)
```

Prohibited:

```c
#define UsbTxBufferSize           (256u)
#define usb_tx_buffer_size        (256u)
```

### 11.3 Enumeration Constants

All enumeration constants shall use uppercase letters and underscore separators.

```c
typedef enum
{
    APP_STATE_BOOT = 0,
    APP_STATE_IDLE,
    APP_STATE_STREAMING,
    APP_STATE_FAULT
} app_state_t;
```

An enumeration type shall use lower snake case with the `_t` suffix.

### 11.4 Boolean Naming

Boolean names shall express a readable predicate:

```c
bool is_connected;
bool has_pending_data;
bool can_transmit;
bool should_retry;
```

Ambiguous names are prohibited:

```c
bool flag;
bool status;
```

### 11.5 Const Object Naming

A `static const` or `const` object remains a typed object with storage and shall not use macro naming.

Allowed:

```c
static const uint16_t s_timeout_ms = 100u;
```

Prohibited:

```c
static const uint16_t TIMEOUT_MS = 100u;
```

A value required by the preprocessor, a compile-time array capacity, or conditional compilation shall use an
uppercase `#define`.

### 11.6 Module Prefix

Every Product-owned function shall use a clear module prefix.

Allowed:

```c
app_init()
app_dispatch()
usb_cdc_transport_send()
sample_source_generate()
```

Prohibited:

```c
init()
process()
send()
reset()
```

File-static functions shall also retain a module prefix.

### 11.7 Global Variables

Global variables are prohibited by default.

They may be used only when required by:

- Startup or linker integration
- Interrupt vector integration
- Hardware or Vendor API integration
- A formally defined shared-system object

Each Product-owned global object shall have a unique Global Object Record.

The default register is:

```text
docs/design/Global_Object_Register.md
```

An alternative official location shall be identified in the Application Analysis. One Project shall not maintain
multiple unsynchronized official registers.

A Global Object Record shall include:

- Global Object ID
- Symbol
- Type
- Owner
- Writer
- Reader
- Synchronization
- Initialization
- Lifetime
- Reason
- Verification

The source shall reference the record:

```c
// Global Object Record: GOR-BSP-001.
volatile uint32_t g_system_tick;
```

A Global Object Record is not automatically a MISRA Deviation. A separate Deviation Record is required only when
the object violates an adopted rule or requires explicit risk acceptance.

Convenience is not sufficient justification for a global variable.

### 11.8 Callback and Function Pointer Naming

A callback function-pointer type shall use the full `_callback_t` suffix.

Allowed:

```c
typedef void (*usb_receive_callback_t)(
    const uint8_t *data,
    uint16_t length);

typedef void (*timer_expired_callback_t)(void);
```

The following mixed styles are prohibited within one Project:

```c
usb_rx_cb_t
usb_rx_fn_t
usb_rx_handler_t
```

A callback implementation shall use:

```text
<module>_<purpose>_callback
```

Examples:

```c
usb_adapter_receive_callback()
adc_adapter_conversion_complete_callback()
timer_service_expired_callback()
```

An incompatible function-pointer cast shall not be used to bypass a signature mismatch.

The callback typedef, registration API, and callback implementation signatures shall match exactly.

---

## 12. Magic Number and Named Constant Rules

### 12.1 General Rule

Magic numbers are prohibited in Product-owned Code.

A numeric value with any of the following meanings shall use a named macro, enum constant, typed `static const`
object, or Protocol YAML generated constant:

- Application behavior
- Protocol field
- Timing
- Frequency
- Range
- Threshold
- Buffer capacity
- Retry limit
- Error or result code
- State value
- Sample rate
- Test expectation
- Hardware address
- Register mask
- Bit position
- Calibration value
- Unit conversion factor

Prohibited:

```c
if ((minimum_sample > -1000) ||
    (maximum_sample < 1000))
{
    return 6;
}
```

Required form:

```c
#define HOST_TEST_SAMPLE_MIN_EXPECTED    (-1000)
#define HOST_TEST_SAMPLE_MAX_EXPECTED    (1000)

if ((minimum_sample > HOST_TEST_SAMPLE_MIN_EXPECTED) ||
    (maximum_sample < HOST_TEST_SAMPLE_MAX_EXPECTED))
{
    return HOST_TEST_RESULT_WAVEFORM_RANGE_ERROR;
}
```

### 12.2 Intrinsic Literal Decision

Whether a literal is a magic number depends on its meaning, not only its numeric magnitude.

`0u` and `1u` are examples of common intrinsic literals, not a closed whitelist.

A literal such as `0u`, `1u`, `2u`, or `-1` may be used directly only when it is:

- Intrinsic
- Local
- Unambiguous
- Not a requirement, specification, protocol, timing, threshold, hardware, or test value
- Not dependent on a unit or external source
- Not duplicated as a hidden definition elsewhere

Usually acceptable:

```c
count = 0u;

if (length == 0u)
{
    // No payload is present.
}
```

```c
mask = (1u << bit_position);
```

A mathematically direct literal may also be acceptable:

```c
middle_value = total_value / 2u;
```

When `2u` represents a formal double-buffer bank count, it shall be named:

```c
#define BUFFER_BANK_COUNT    (2u)
```

A value with test meaning shall be named even when it is `0u` or `1u`:

```c
#define HOST_TEST_EXPECTED_FRAME_COUNT    (1u)

if (decoded_frame_count != HOST_TEST_EXPECTED_FRAME_COUNT)
{
}
```

A sentinel such as `-1` should be named:

```c
#define INDEX_NOT_FOUND    (-1)
```

Semantic analysis takes precedence over any example list.

### 12.3 Constant Representation Selection

Use `#define` for:

- Preprocessor conditions
- Compile-time array capacity
- Buffer sizes
- Bit masks
- Protocol-generated constants
- Hardware register constants
- Values required as constant expressions

```c
#define USB_TX_BUFFER_SIZE             (256u)
#define HOST_TEST_SAMPLE_RATE_HZ       (250u)
```

Use an enum constant for:

- States
- Results
- Error codes
- Message categories
- Finite mutually exclusive options

```c
typedef enum
{
    HOST_TEST_RESULT_PASS = 0,
    HOST_TEST_RESULT_ENCODE_ERROR,
    HOST_TEST_RESULT_DECODE_ERROR,
    HOST_TEST_RESULT_SAMPLE_SOURCE_INIT_ERROR,
    HOST_TEST_RESULT_WAVEFORM_RANGE_ERROR
} host_test_result_t;
```

Use a typed `static const` object for:

- Module-private typed constants
- Constants that do not need preprocessor evaluation
- Constants that require an explicit type or address

```c
static const uint16_t s_connection_timeout_ms = 500u;
```

A meaningless alias is prohibited:

```c
#define VALUE_ONE    (1u)
#define NUMBER_250   (250u)
```

The name shall express the value's purpose.

### 12.4 Numeric Return Codes

Direct numeric error and result codes are prohibited.

Prohibited:

```c
return 3;
return 4;
return 6;
```

Required:

```c
return HOST_TEST_RESULT_DECODE_ERROR;
return HOST_TEST_RESULT_SAMPLE_SOURCE_INIT_ERROR;
return HOST_TEST_RESULT_WAVEFORM_RANGE_ERROR;
```

A module boundary shall preserve result meaning through a named enum or an explicit mapping.

### 12.5 Process Exit Status Boundary

An internal module result and an operating-system process exit status are different contracts.

A Host-side tool `main()` may return a process exit status, but shall use an explicit mapping.

```c
#include <stdlib.h>

/*
 * Converts the host-test result into a process exit status.
 */
static int host_test_to_exit_status(host_test_result_t test_result)
{
    int exit_status;

    if (test_result == HOST_TEST_RESULT_PASS)
    {
        exit_status = EXIT_SUCCESS;
    }
    else
    {
        exit_status = EXIT_FAILURE;
    }

    return exit_status;
}
```

```c
int main(void)
{
    host_test_result_t test_result;

    test_result = host_test_run();

    return host_test_to_exit_status(test_result);
}
```

Direct casting is prohibited:

```c
return (int)test_result;
```

An exception requires a documented and reviewed Process Exit Contract.

When CI or automation requires multiple failure classes, define a separate named process-exit enum and explicit
mapping. Raw numeric process exit codes are prohibited in Product-owned Host tools.

### 12.6 Units in Names

A constant or variable representing a physical unit shall include the unit when practical:

```c
#define USB_RESPONSE_TIMEOUT_MS    (1000u)
#define SAMPLE_RATE_HZ             (250u)
static const uint32_t s_period_us = 4000u;
```

Ambiguous names such as `timeout`, `period`, or `speed` shall not be used when multiple units are possible.

### 12.7 Single Definition

One system concept shall have one authoritative definition.

Protocol constants shall come from Protocol YAML generated output when the YAML is the Single Source of Truth.

A Product implementation shall not manually duplicate a generated message ID, offset, length, or enum value.

---

## 13. Type and Expression Rules

### 13.1 Fixed-width Integer Types

Use fixed-width integer types from `<stdint.h>` when width is relevant:

```c
uint8_t
uint16_t
uint32_t
int16_t
int32_t
```

Plain `char`, `short`, `int`, and `long` shall not be used for externally defined widths, protocol fields, storage
formats, hardware registers, or arithmetic whose range depends on width.

### 13.2 Signed and Unsigned Selection

Use unsigned types for quantities that cannot be negative, such as:

- Counts
- Lengths
- Capacities
- Bit masks
- Message identifiers
- Monotonic ticks, when the wrap policy is defined

Use signed types only when negative values have valid application meaning.

`-1` shall not be used as a conventional undefined or invalid sentinel unless the data model formally defines it.

### 13.3 Boolean Type

Boolean values shall use `bool`, `true`, and `false` from `<stdbool.h>`.

```c
bool is_ready = false;
```

Integer literals, macros, or enum constants shall not be used as substitutes for Boolean literals.

### 13.4 Integer Literal Suffix

Unsigned integer literals shall use the `u` suffix:

```c
uint16_t count = 0u;
```

Use standard integer constant macros or another verified representation when a specific width is required.

### 13.5 Module-specific Types

Data with domain meaning should have a dedicated type:

```c
typedef uint16_t app_event_mask_t;
typedef uint16_t protocol_message_id_t;
typedef uint32_t system_tick_t;
```

The Application shall not distribute semantically anonymous primitive types across module boundaries.

### 13.6 Implicit Conversion

Unanalyzed implicit conversion is prohibited.

Special attention is required for:

- Mixed signed and unsigned arithmetic
- Mixed signed and unsigned comparison
- Narrowing conversion
- Integer promotion
- Enum and integer conversion
- Pointer conversion

A required cast shall be placed at a clear review point and shall follow a range check.

```c
if (source_value <= UINT8_MAX)
{
    target_value = (uint8_t)source_value;
}
else
{
    result = APP_RESULT_OUT_OF_RANGE;
}
```

An implicit narrowing assignment is prohibited when the source range exceeds the target range.

### 13.7 Loop Index Type

A loop index shall use an explicitly selected type that can represent the complete iteration range.

Plain `int` shall not be used merely because it is the C default.

```c
uint16_t index;

for (index = 0u; index < SAMPLE_COUNT; index++)
{
    samples[index] = 0;
}
```

Before use, confirm that:

- `SAMPLE_COUNT` is representable by the index type.
- The array capacity is at least `SAMPLE_COUNT`.
- The loop body does not modify the index.
- Conversion or overflow cannot invalidate the termination condition.

### 13.8 Enumeration Use

An enum shall represent a finite named domain.

The implementation shall not depend on an unspecified enum storage width for a wire format, persistent format,
or hardware interface.

Unknown external values shall be validated before conversion to an internal enum.

### 13.9 Bitwise Expressions

Bitwise operations shall use unsigned operands.

Shift counts shall be validated against the width of the promoted left operand.

A shift shall not rely on signed right-shift behavior or overflow of a signed left shift.

---

## 14. Static Memory Configuration

### 14.1 Static Allocation Only

Embedded Firmware shall use static memory allocation.

The following functions are prohibited:

```c
malloc()
calloc()
realloc()
free()
```

A Product-owned wrapper shall not indirectly use heap allocation:

```c
app_alloc()
app_free()
```

### 14.2 Variable Length Arrays

Variable Length Arrays are prohibited.

Prohibited:

```c
void process_data(uint16_t length)
{
    uint8_t buffer[length];
}
```

Use a fixed capacity with explicit length validation:

```c
#define PROCESS_BUFFER_SIZE    (128u)

void process_data(uint16_t length)
{
    uint8_t buffer[PROCESS_BUFFER_SIZE];

    if (length <= PROCESS_BUFFER_SIZE)
    {
        // Process data.
    }
}
```

### 14.3 Recursion

Recursion is prohibited.

A recursive algorithm shall be redesigned as an iterative algorithm with an explicit bounded stack or state
representation when required.

### 14.4 Buffer Capacity

Every buffer shall have:

- A named capacity
- A defined owner
- A defined lifetime
- A defined producer
- A defined consumer
- A defined overflow policy
- A defined initialization policy

The used length and capacity shall be distinct values.

### 14.5 RTOS Object Allocation

Product-owned Code shall use static RTOS object creation APIs when available.

The Project shall not create a task, queue, mailbox, semaphore, mutex, timer, or event object through an API that
performs dynamic allocation.

If Adopted Code requires a heap, the Integration Record shall document:

- Why the heap is required
- Maximum allocation
- Allocation timing
- Failure behavior
- Fragmentation risk
- Reset behavior
- Verification evidence

### 14.6 Stack Allocation

Large automatic objects are prohibited unless stack impact is analyzed and accepted.

Task and ISR stack sizes shall be based on:

- Static call analysis
- Compiler map or stack report
- Worst-case execution path
- Interrupt nesting
- Measured high-water mark, when available
- Safety margin

### 14.7 Heap Configuration

The linker heap shall be set to zero or the smallest unusable configuration when the platform permits.

A nonzero heap shall have a documented owner and approved justification.

---

## 15. Arithmetic Safety Rules

### 15.1 General Rule

Increment, decrement, addition, subtraction, multiplication, division, and conversion shall be protected against
overflow, underflow, divide-by-zero, invalid shift, and data loss.

A post-operation check is not sufficient when the operation itself can invoke undefined behavior.

### 15.2 Unsigned Increment

Check the maximum before incrementing:

```c
if (counter < UINT16_MAX)
{
    counter++;
}
else
{
    result = APP_RESULT_OUT_OF_RANGE;
}
```

A saturating counter may retain its maximum when that policy is defined.

### 15.3 Unsigned Decrement

Check against zero before decrementing:

```c
if (counter > 0u)
{
    counter--;
}
else
{
    result = APP_RESULT_OUT_OF_RANGE;
}
```

### 15.4 Signed Addition and Subtraction

Signed addition and subtraction shall check boundaries before the operation or use a wider intermediate type that
can represent all possible results.

Example using a wider intermediate:

```c
int32_t sum;

sum = (int32_t)value_a + (int32_t)value_b;

if ((sum < INT16_MIN) || (sum > INT16_MAX))
{
    result = APP_RESULT_OUT_OF_RANGE;
}
else
{
    result_value = (int16_t)sum;
}
```

### 15.5 Multiplication

Unsigned multiplication shall verify that the result is representable before multiplication:

```c
if ((multiplier == 0u) ||
    (multiplicand <= (UINT16_MAX / multiplier)))
{
    product = multiplicand * multiplier;
}
else
{
    result = APP_RESULT_OUT_OF_RANGE;
}
```

Signed multiplication shall account for positive and negative operands and both minimum and maximum values.

When a wider type can represent every possible product, use the wider intermediate and range-check before
conversion:

```c
/*
 * Multiplies two signed 16-bit values with range protection.
 */
static app_result_t math_multiply_int16(
    int16_t multiplicand,
    int16_t multiplier,
    int16_t *result_value)
{
    app_result_t result = APP_RESULT_OK;
    int32_t product;

    if (result_value == NULL)
    {
        result = APP_RESULT_INVALID_ARGUMENT;
    }
    else
    {
        product = (int32_t)multiplicand * (int32_t)multiplier;

        if ((product < INT16_MIN) || (product > INT16_MAX))
        {
            result = APP_RESULT_OUT_OF_RANGE;
        }
        else
        {
            *result_value = (int16_t)product;
        }
    }

    return result;
}
```

This method is valid only when the intermediate type can represent every possible result.

### 15.6 Division

A divisor shall be checked before division:

```c
if (divisor != 0u)
{
    quotient = dividend / divisor;
}
else
{
    result = APP_RESULT_INVALID_ARGUMENT;
}
```

Signed division shall also protect the minimum negative value divided by `-1`.

### 15.7 Narrowing Conversion

A conversion from a wider range to a narrower range shall be preceded by a range check.

```c
if (source_value <= UINT8_MAX)
{
    target_value = (uint8_t)source_value;
}
else
{
    result = APP_RESULT_OUT_OF_RANGE;
}
```

A cast shall not be used to hide truncation.

### 15.8 Signed and Unsigned Mixing

Signed and unsigned operands shall not be mixed without analysis.

When conversion is required:

1. Confirm that the signed value is nonnegative.
2. Confirm that it is representable by the target unsigned type.
3. Apply an explicit cast.
4. Perform the operation or comparison.

### 15.9 Intentional Wraparound

Intentional wraparound is prohibited by default.

When a protocol sequence number or another formally defined counter requires wraparound:

1. Define the boundary behavior.
2. Add a local explanatory comment.
3. Isolate the behavior in one module.
4. Include it in review.
5. Provide test vectors around the wrap boundary.

### 15.10 Scaling and Unit Conversion

Scaling shall use named factors, explicit intermediate types, rounding policy, and range checks.

The implementation shall define whether a conversion truncates, rounds to nearest, saturates, or reports an error.

---

## 16. Function Rules

### 16.1 Function Header Contract

Every Product-owned function declaration and definition shall have the mandatory Function Header defined in
Section 10.3.

The Function Header shall accurately describe:

- Function purpose
- Every input parameter
- Every output parameter
- Every return value and its meaning

The documented parameter names shall match the signature exactly.

When the implementation changes parameter use, output behavior, failure behavior, side effects, or return-value
meaning, the Function Header shall be updated in the same change.

A stale, incomplete, or copied Function Header is a coding-rule violation.

### 16.2 Single Primary Responsibility

A function shall perform one primary task.

A function that validates, transforms, transmits, logs, and changes state should be decomposed unless a documented
atomic operation requires the combined behavior.

### 16.3 Function Size and Complexity

A function shall remain reviewable.

The Project should define thresholds for:

- Lines of code
- Cyclomatic complexity
- Nesting depth
- Parameter count
- Local variable count

Exceeding a threshold requires review and justification, not automatic acceptance.

### 16.4 Parameter Validation

A public or boundary function shall validate:

- Null pointers
- Lengths
- Ranges
- Enum values
- State preconditions
- Buffer capacity
- Ownership assumptions

An internal helper may rely on a previously established invariant only when the call boundary makes that invariant
clear and reviewable.

### 16.5 Return-value Handling

The return value of a function that can fail shall be checked.

Prohibited:

```c
usb_cdc_transport_send(buffer, length);
```

Required:

```c
result = usb_cdc_transport_send(buffer, length);

if (result != USB_CDC_RESULT_OK)
{
    app_event_post(APP_EVENT_TX_FAILED);
}
```

A deliberately ignored return value shall use an approved explicit pattern and a comment explaining why ignoring
it is safe.

### 16.6 Output Parameters

An output pointer shall be validated before writing.

The function shall define whether output data remains unchanged on failure.

The Output Parameters field in the Function Header shall state the success and failure behavior of each output
object.

### 16.7 Side Effects

A function's externally observable side effects shall be clear from its name, Function Header, contract, or module
responsibility.

A getter shall not unexpectedly modify system state.

### 16.8 Function Prototypes

Every non-static function shall have one visible prototype in the appropriate header.

A declaration and definition shall have compatible types and qualifiers.

The Function Headers associated with a declaration and its definition shall not conflict.

### 16.9 Recursion

Direct and indirect recursion are prohibited.

### 16.10 Callback Function Rules

Every Product-owned callback shall define:

- Signature
- Registration owner
- Invocation owner
- Execution context: ISR, task, main loop, Vendor worker, or another defined context
- Blocking permission
- Reentrancy
- Parameter ownership
- Parameter lifetime
- Cancellation and unregistration behavior
- Maximum execution time or Timing Budget
- Allowed Framework APIs
- Error-reporting method
- Whether the callback may call back into the provider

The mandatory Function Header defined in Section 10.3 shall include the callback contract information required
to understand safe use. The optional `Notes` field shall be used to document execution context, blocking
permission, reentrancy, data ownership, data lifetime, Timing Budget, and other callback-specific constraints.

Required form:

```c
/*
 * Function:
 *     usb_adapter_receive_callback
 *
 * Purpose:
 *     Captures a Vendor USB receive notification and defers processing to
 *     the Application event context.
 *
 * Input Parameters:
 *     data:
 *         Pointer to the received byte buffer. The buffer is borrowed and
 *         remains valid only for the duration of this callback.
 *     length:
 *         Number of valid bytes available in data.
 *
 * Output Parameters:
 *     None.
 *
 * Return Value:
 *     None.
 *
 * Notes:
 *     Execution Context:
 *         USB interrupt context.
 *     Blocking:
 *         Prohibited.
 *     Reentrancy:
 *         Not reentrant.
 *     Timing Budget:
 *         Bounded by the USB Adapter ISR-callback budget.
 */
static void usb_adapter_receive_callback(
    const uint8_t *data,
    uint16_t length)
{
    usb_adapter_capture_received_data(data, length);
    app_event_post_from_isr(APP_EVENT_USB_RX_READY);
}
```

A callback that executes in ISR context shall comply with all rules in Section 21.

A Vendor, middleware, Driver, or low-level callback shall not directly perform:

- Application business logic
- Complete State Machine dispatch
- Protocol encoding or decoding
- Blocking operations
- Dynamic memory allocation
- Long or unbounded processing

A Product-owned Adapter callback should perform only the following bounded sequence:

1. Capture the minimum required data.
2. Update bounded Adapter-owned state.
3. Post an Event, task notification, Mailbox message, or Deferred Work request.
4. Return to the caller.

A callback parameter pointer shall not be stored or used after its valid lifetime ends unless the data has been
copied into owned bounded storage or ownership has been transferred through an explicit contract.

Callback registration and unregistration shall have one defined owner and shall prevent:

- Duplicate registration
- Dangling callbacks
- Callback invocation after module shutdown
- Callback invocation into deinitialized state
- Race conditions during callback replacement

A callback running in task, worker-thread, or main-loop context remains subject to the documented blocking,
timing, reentrancy, and ownership rules. Long-running work shall be deferred when it would violate the callback
contract or delay required processing.

An incompatible function-pointer cast shall not be used to connect mismatched callback signatures.

The callback typedef, registration API, callback implementation, and Function Header shall remain mutually
consistent.

---

## 17. Pointer and Array Rules

### 17.1 Null-pointer Validation

A pointer received from outside the module shall be checked before dereference unless the interface formally
defines and enforces a non-null precondition.

Use `NULL` for null pointers.

### 17.2 Pointer Ownership

Every pointer-based interface shall define:

- Owner
- Borrower
- Read or write permission
- Valid lifetime
- Transfer of ownership, if any
- Required synchronization

Dynamic ownership transfer is discouraged in static-memory Embedded Firmware.

### 17.3 Pointer Arithmetic

Pointer arithmetic shall be limited to a verified array object and a validated index or remaining length.

A pointer shall not move outside the bounds of its array object.

### 17.4 Array Length

An array and its used length shall be passed together unless the capacity is part of a strongly defined type.

The callee shall validate the used length against capacity before access.

### 17.5 Buffer Access

Every read or write shall be proven within bounds.

Protocol decoders shall validate remaining bytes before reading each field.

### 17.6 String Handling

Unbounded string functions are prohibited.

The Project shall use bounded operations and shall verify termination.

A received byte buffer shall not be assumed to contain a null-terminated string.

### 17.7 Pointer Casting

Pointer casts shall be minimized.

The implementation shall not cast a receive buffer directly to a Protocol struct pointer.

A cast that changes alignment, aliasing, const qualification, address space, or function type requires explicit
analysis and review.

### 17.8 `const` Correctness

A pointer shall use `const` when the callee does not modify the pointed-to data.

A function shall not cast away `const` to modify an object.

---

## 18. Control Flow Rules

### 18.1 Readable Conditions

Conditions shall be explicit and side-effect free.

Assignments inside conditions are prohibited.

Complex conditions should be decomposed into named Boolean variables or helper functions.

### 18.2 Switch Statement

State Machine and message dispatch logic may use `switch`.

Each `case` shall terminate with:

- `break`
- `return`
- A clearly marked and reviewed fall-through

### 18.3 Default Case

Every `switch` shall contain a `default` that handles an invalid or unexpected value.

```c
default:
{
    result = APP_RESULT_INTERNAL_ERROR;
    break;
}
```

### 18.4 Infinite Loop

An intentional infinite loop shall be syntactically obvious.

Preferred:

```c
for (;;)
{
    app_process();
}
```

Also allowed:

```c
while (true)
{
    app_process();
}
```

When `while` represents an intentional infinite loop, only the Boolean literal `true` defined in Section 13.3
is allowed.

The following are prohibited:

```c
while (1)
{
}
```

```c
while (1u)
{
}
```

```c
#define LOOP_FOREVER    (1u)

while (LOOP_FOREVER)
{
}
```

```c
typedef enum
{
    LOOP_CONDITION_FALSE = 0,
    LOOP_CONDITION_TRUE = 1
} loop_condition_t;

while (LOOP_CONDITION_TRUE)
{
}
```

A runtime Boolean condition is a conditional loop, not a syntactically unconditional infinite loop:

```c
while (is_running == true)
{
    app_process();
}
```

An infinite loop outside the primary application event loop shall:

- Have a design justification.
- Identify ownership and execution context.
- Guarantee bounded work per iteration.
- Not indefinitely block event dispatch, fault handling, or shutdown processing.
- Leave traceable review or deviation evidence.

Every operation inside the loop remains subject to blocking, timing, watchdog, and error-handling rules.

### 18.5 Loop Bounds

Every loop shall have a demonstrable bound unless it is an approved intentional infinite loop.

A loop bound derived from external input shall be validated against a fixed maximum.

### 18.6 Early Exit

Multiple returns may be used when they improve clarity and preserve cleanup and state consistency.

A function shall not use `goto` for normal control flow. A narrowly controlled cleanup pattern requires explicit
Project approval.

---

## 19. Event-Driven Rules

### 19.1 Event Meaning

Each Event shall represent one clear meaning.

Event names shall use uppercase letters and underscore separators:

```c
APP_EVENT_BOOT
APP_EVENT_USB_CONNECTED
APP_EVENT_STREAM_TICK
APP_EVENT_TX_COMPLETE
```

### 19.2 Event Ownership

Each Event shall define:

- Producer
- Consumer
- Priority
- Clear policy
- Whether loss is acceptable
- ISR or task context
- Payload ownership

### 19.3 Bit Event Limitation

A bit flag is suitable when:

- State has changed.
- Work is pending.
- Repeated occurrences may be merged.

A bit flag is not suitable for multiple occurrences that must not be lost.

For example, a non-loss-tolerant 250 Hz sample tick shall not rely only on one bit. Use one of:

- Counter
- Mailbox
- Queue
- Ping-pong buffer
- Hardware sample count

### 19.4 Event Posting

An ISR or module shall post only Events it is authorized to produce.

### 19.5 Event Clearing

Event acquisition and clearing shall be centralized to prevent multiple consumers from racing on one event mask.

### 19.6 Event Payload

An Event carrying data shall define payload ownership, lifetime, capacity, and overwrite policy.

A pointer to temporary stack storage shall not be posted for later processing.

---

## 20. State Machine Rules

### 20.1 State Ownership

A state variable shall be modified only by its owning State Machine module.

Direct modification by another module is prohibited:

```c
s_app_state = APP_STATE_STREAMING;
```

Use a transition function:

```c
app_transition_to(APP_STATE_STREAMING);
```

### 20.2 Transition Trigger

Every transition shall have an explicit trigger:

- Event
- Command
- Timeout
- Hardware condition
- Recovery condition
- Fault

### 20.3 Entry and Exit Actions

A complex State Machine shall define entry and exit actions explicitly.

An action shall execute once per transition unless the design states otherwise.

### 20.4 Invalid State or Event

An invalid state and Event combination shall not be silently ignored.

The implementation shall take one or more of:

- Return an error.
- Increment a diagnostic counter.
- Post a fault Event.
- Enter a safe state.

### 20.5 State Read Access

Other modules may read state through a getter but shall not receive a writable pointer to the state variable.

### 20.6 Transition Atomicity

A transition that updates multiple dependent objects shall prevent observation of a partially updated state.

### 20.7 State Persistence

When state is persisted, the format, version, integrity check, invalid-value behavior, and reset behavior shall be
defined.

---

## 21. ISR Rules

### 21.1 ISR Responsibilities

An ISR shall perform only necessary bounded work:

- Read or acknowledge hardware status.
- Capture minimum required data.
- Update an atomic flag or counter.
- Post an Event.
- Request wake-up.

### 21.2 Prohibited ISR Operations

An ISR shall not perform:

- Blocking calls
- Busy waits
- `printf`
- Dynamic memory allocation
- USB packet encoding
- Complex Protocol parsing
- Long or unbounded loops
- Full State Machine dispatch
- File-system operations
- Unbounded processing

### 21.3 ISR Timing Budget

Each ISR shall have a Project-defined maximum execution time or maximum work amount.

The shared coding standard does not define one fixed microsecond limit. The limit shall be recorded in one of:

- Application Analysis
- Platform Profile
- Timing Budget
- Detailed Design

A loop inside an ISR shall have a fixed and provable maximum iteration count.

Timing verification may use:

- GPIO measurement
- Cycle counter
- Logic analyzer
- Trace
- Static worst-case analysis
- Code review with bounded-iteration proof

"Short code" is not sufficient evidence without a Timing Budget.

### 21.4 Shared Data and `volatile`

When an ISR shares data with main or task context, analyze:

- Ownership
- `volatile`
- Atomicity
- Critical section
- Read-modify-write race
- Counter overflow
- Access order
- Memory barrier
- Cache coherency, when applicable

`volatile` requests actual memory access. It is not a substitute for synchronization, atomicity, or race protection.

A multi-byte object shall not be assumed atomic unless verified for the MCU and compiler.

The standard access pattern shall be defined in the Platform Profile or module design.

### 21.5 ISR Event Example

```c
#pragma vector = TIMER0_A0_VECTOR
__interrupt void timer_a0_isr(void)
{
    app_event_post_from_isr(APP_EVENT_STREAM_TICK);
    __bic_SR_register_on_exit(LPM0_bits);
}
```

### 21.6 Interrupt Disable Scope

Interrupts shall be disabled only for the minimum bounded interval required to protect a shared invariant.

The code shall not call a blocking API while interrupts are disabled.

---

## 22. Error Handling Rules

### 22.1 Error Categories

Errors shall be classified at least as:

- Invalid argument
- Invalid state
- Busy
- Timeout
- Capacity exceeded
- Data corrupted
- Hardware failure
- Internal consistency failure

### 22.2 No Silent Failure

An error shall not be ignored silently.

Depending on severity, use one or more of:

- Return result
- Protocol error response
- Diagnostic counter
- Event
- Log
- Fault state
- Safe state

### 22.3 Diagnostic Counters

Diagnostic counters should saturate:

```c
if (s_tx_drop_count < TX_DROP_COUNT_MAX)
{
    s_tx_drop_count++;
}
```

A diagnostic counter shall define reset, persistence, and access policy.

### 22.4 Retry

Retry count shall be bounded:

```c
#define USB_RETRY_COUNT_MAX    (3u)
```

Infinite retry is prohibited.

A retry policy shall define:

- Maximum attempts
- Retryable errors
- Delay or backoff
- Idempotency requirement
- Final failure action

### 22.5 Safe Failure

A safety-relevant failure shall define the safe state, transition trigger, recovery authority, and user-visible or
diagnostic evidence.

### 22.6 Error Conversion

A lower-layer error shall be converted deliberately at a module boundary. Meaningful detail shall not be lost
through a raw numeric conversion.

---

## 23. Protocol Implementation Rules

### 23.1 Single Source of Truth

Protocol YAML is the Single Source of Truth for the wire contract.

Product-owned code shall not manually redefine generated:

- Message identifiers
- Field offsets
- Field widths
- Enum values
- Bit definitions
- Lengths
- Endianness
- Capability identifiers

### 23.2 Generated Code

Protocol YAML generated code shall contain:

```c
// AUTO-GENERATED FILE.
// DO NOT EDIT MANUALLY.
```

Generated Code shall not be edited manually.

### 23.3 Message Validation

A received message shall validate:

- Header
- Message ID
- Payload length
- Sequence
- CRC or integrity field
- State permission
- Capability
- Version compatibility

Security-sensitive messages shall also validate the required authentication, integrity, anti-replay, privilege,
and key-context properties.

### 23.4 Wire-format Serialization

A Protocol wire format shall not depend on C struct memory layout.

Even with a packed attribute, compiler pragma, or `#pragma pack`, a struct memory image shall not be transmitted
directly.

Prohibited:

```c
#pragma pack(push, 1)

typedef struct
{
    uint16_t message_id;
    uint16_t payload_length;
    uint32_t sequence;
} protocol_header_t;

#pragma pack(pop)

usb_transport_send(
    (const uint8_t *)&header,
    sizeof(header));
```

Protocol serialization shall not use:

- Bit-fields for wire fields
- Union type-punning to produce wire bytes
- `sizeof(struct)` as a packet length
- Compiler padding
- Compiler alignment
- Native endianness
- Enum storage width
- A direct receive-buffer-to-struct-pointer cast

Every wire field shall follow the Protocol YAML definition for:

- Offset
- Width
- Signedness
- Endianness
- Encoding
- Length
- Optionality

Use explicit encode and decode functions:

```c
protocol_write_u16_le(
    &buffer[PROTOCOL_OFFSET_MESSAGE_ID],
    message_id);

protocol_write_u16_le(
    &buffer[PROTOCOL_OFFSET_PAYLOAD_LENGTH],
    payload_length);

protocol_write_u32_le(
    &buffer[PROTOCOL_OFFSET_SEQUENCE],
    sequence);
```

An internal C struct may represent application data but is not the wire contract.

Conversion between an internal struct and a wire buffer shall occur through an explicit encode or decode boundary.

### 23.5 Protocol Struct Boundary

A Protocol-related internal struct may use normal alignment.

Wire-format requirements shall not force a packed Application data model.

Rules for packed structs, unions, and bit-fields outside Protocol code remain controlled by the Platform Profile
and Section 30 Open Items.

### 23.6 Decoder Length Discipline

A decoder shall check remaining length before each read.

A count or length from the message shall be checked against:

- Remaining payload
- Destination capacity
- Protocol maximum
- Arithmetic overflow in size calculation

### 23.7 Compatibility

Unknown message, field, enum, bit, trailing data, and capability handling shall follow the Protocol YAML policy.

The implementation shall not treat unknown input as successful processing by default.

---

## 24. BSP, Driver, and Vendor Stack Rules

### 24.1 Dependency Direction

The dependency direction shall be:

```text
Application
    |
    v
Service / Protocol
    |
    v
Driver Adapter
    |
    v
Vendor Stack / BSP
    |
    v
Hardware
```

The BSP shall not depend on the Application.

### 24.2 Vendor API Isolation

Application code shall not directly call a Vendor Stack API.

Use a Product-owned Adapter:

```c
usb_cdc_transport_init()
usb_cdc_transport_send()
usb_cdc_transport_read()
```

### 24.3 Vendor Code Modification

Vendor Code should not be modified.

When a modification is necessary, retain:

- Original version
- Patch
- Reason
- Risk
- Verification evidence

### 24.4 Adopted Code Usage

Product-owned calls into Adopted Code shall manage:

- Return value
- Parameter range
- Task or ISR context
- Blocking behavior
- Dynamic-allocation behavior
- Timeout
- Error conversion
- Callback ownership
- Callback signature
- Callback lifetime
- Callback execution context
- Object lifetime
- Reentrancy
- Timing

### 24.5 Hardware Register Access

Hardware register access shall be isolated in the BSP, HAL, or Driver Layer.

Application code shall not directly manipulate peripheral registers.

Register addresses, masks, and bit positions shall use named constants from an authoritative header.

### 24.6 Initialization Order

The initialization order shall be explicit and shall account for Vendor side effects.

When a Vendor initialization function modifies clocks, timers, interrupts, or pin configuration, the Product
initialization sequence shall restore or reapply the intended configuration and verify the final state.

---

## 25. Entry-Point and `main()` Rules

This chapter governs the Embedded Firmware entry point. Host-side process exit behavior remains governed by
Section 12.5.

### 25.1 Entry-Point Responsibility Boundary

`main()` shall remain a startup and runtime-handoff function.

It shall establish the environment required by the Application but shall not implement Product business logic.

The responsibility boundary applies to both RTOS and non-RTOS implementations.

### 25.2 Allowed Responsibilities

`main()` shall be limited to the following responsibilities, as applicable:

1. Configure or disable the startup watchdog according to the Platform Profile.
2. Initialize the BSP, clock, memory, and required low-level platform services.
3. Initialize statically allocated runtime objects.
4. Initialize Product-owned modules through their public initialization APIs.
5. Enable interrupts only after required initialization and pending-status handling are complete.
6. Post the initial Application Event or start the RTOS scheduler.
7. Run the non-RTOS dispatcher loop or transfer control to the RTOS runtime.
8. Enter a defined safe-state, reset, or halt path when initialization fails or the runtime returns unexpectedly.

Startup ordering shall follow Section 24.6 and the applicable Platform Profile.

### 25.3 Prohibited Responsibilities

`main()` shall not directly perform:

- Protocol encoding or decoding
- Signal, waveform, or sample generation
- Command parsing or command dispatch
- Product control decisions
- Direct State Machine transitions
- Normal Application state processing
- Direct Vendor communication-stack or peripheral API calls
- Long-running Device operations
- Periodic Product business logic
- Unbounded retry or recovery logic

Required Vendor functionality shall be accessed through the appropriate Product-owned BSP, HAL, Driver Adapter,
Service, or Runtime Integration interface.

A call that initializes a Product-owned Adapter is allowed. A direct call from `main()` into the underlying
Vendor Stack is prohibited.

### 25.4 Non-RTOS Entry Point

In a non-RTOS implementation, `main()` may run the Application dispatcher and idle loop after successful
initialization.

The dispatcher shall invoke Product-owned modules that own the actual business logic.

```c
/*
 * Function:
 *     main
 *
 * Purpose:
 *     Initializes the Embedded Firmware and runs the non-RTOS Application
 *     event-dispatch loop.
 *
 * Input Parameters:
 *     None.
 *
 * Output Parameters:
 *     None.
 *
 * Return Value:
 *     Not returned during normal operation.
 *
 * Notes:
 *     Product business logic is owned by Application, Service, Protocol,
 *     and State Machine modules rather than this entry-point function.
 */
int main(void)
{
    app_event_mask_t events;
    app_result_t result;

    result = bsp_watchdog_configure_startup();

    if (result == APP_RESULT_OK)
    {
        result = bsp_initialize();
    }

    if (result == APP_RESULT_OK)
    {
        result = app_event_initialize();
    }

    if (result == APP_RESULT_OK)
    {
        result = app_initialize();
    }

    if (result == APP_RESULT_OK)
    {
        result = usb_cdc_transport_initialize();
    }

    if (result == APP_RESULT_OK)
    {
        result = bsp_interrupts_enable();
    }

    if (result == APP_RESULT_OK)
    {
        app_event_post(APP_EVENT_BOOT);

        for (;;)
        {
            events = app_event_take_all();

            if (events == APP_EVENT_NONE)
            {
                bsp_idle();
            }
            else
            {
                app_dispatch(events);
            }
        }
    }

    app_enter_safe_state();

    for (;;)
    {
        bsp_idle();
    }
}
```

The example illustrates the responsibility boundary. The exact initialization APIs and order remain
Platform-specific.

### 25.5 RTOS Entry Point

In an RTOS implementation, `main()` may:

- Initialize the Platform and Product modules.
- Create the statically allocated tasks and runtime objects defined by the design.
- Start the RTOS scheduler.

`main()` shall not execute task business logic before or after scheduler startup.

Task entry functions, Mailbox handlers, Event dispatchers, and State Machines shall own runtime behavior.

An unexpected return from the scheduler shall be treated as a runtime failure and shall enter the defined
safe-state, reset, or halt path.

### 25.6 Initialization Failure and Unexpected Return

Every initialization function that can fail shall have its return value checked.

Interrupts, communication, output drivers, and runtime scheduling shall not be enabled until their required
preconditions are established.

An initialization failure shall result in a defined action, such as:

- Preserve or place controlled outputs in a safe state.
- Record or expose diagnostic evidence when the Platform permits it.
- Enter a bounded recovery path.
- Request a controlled reset.
- Enter an approved fail-stop loop.

`main()` shall not continue into normal runtime after a required initialization step fails.

A return from a non-returning dispatcher, scheduler, or runtime handoff shall be treated as an internal
consistency failure.

### 25.7 Review Guidance

Code Review shall confirm:

1. `main()` contains only startup, initialization, runtime handoff, dispatcher, and failure-path logic.
2. Product business logic is owned by the appropriate Application, Service, Protocol, or State Machine module.
3. `main()` does not encode or decode Protocol data.
4. `main()` does not generate samples or waveforms.
5. `main()` does not parse commands or directly transition Product state.
6. `main()` does not directly call Vendor communication or peripheral APIs.
7. Every failure-capable initialization return value is checked.
8. Interrupt and scheduler enablement occurs only after required initialization.
9. Non-RTOS runtime behavior is performed through the dispatcher.
10. RTOS runtime behavior is performed through statically defined tasks and runtime objects.
11. Unexpected runtime return enters the defined safe-state, reset, or halt path.

---

## 26. RTOS and Middleware Rules

### 26.1 Static Object Creation

Product-owned Code shall use static RTOS object creation.

Task, queue, mailbox, semaphore, mutex, timer, and Event objects shall have fixed storage and a documented owner.

### 26.2 Task Responsibility

Each task shall have:

- One coherent responsibility
- Defined input mechanism
- Defined output mechanism
- Defined priority
- Defined stack size
- Defined blocking policy
- Defined watchdog or liveness policy
- Defined shutdown or reset behavior

### 26.3 Task Creation

Uncontrolled runtime task creation is prohibited.

The number of tasks and their creation point shall be fixed by design.

### 26.4 Blocking Calls

A blocking call shall have a bounded timeout unless the execution context is explicitly designed to block forever.

A forever-blocking wait shall not prevent required fault handling, watchdog service, shutdown, or safety action.

### 26.5 Callback Execution Context

The integration shall document whether a middleware callback runs in:

- ISR context
- Driver task context
- Worker thread context
- Calling task context
- Unknown or Vendor-defined context

Product-owned callback behavior shall obey the restrictions of the actual context and all callback rules in
Section 16.10.

### 26.6 Hidden Allocation

An RTOS or middleware API shall not be considered static merely because Product-owned Code does not call `malloc`
directly.

The Project shall inspect the API and configuration for hidden allocation.

### 26.7 Stack and Resource Budget

Each task, queue, mailbox, timer, and synchronization object shall be included in the resource budget.

The Project shall verify configured capacity under worst-case concurrency.

---

## 27. Concurrency and Shared Data Rules

### 27.1 Ownership

Every shared object shall define:

- Owner
- Writers
- Readers
- Access context
- Synchronization
- Lifetime
- Initialization
- Reset behavior

Single-writer ownership is preferred.

### 27.2 Critical Sections

A critical section shall be:

- Minimal
- Bounded
- Free of blocking calls
- Free of long loops
- Measured or analyzed when timing-sensitive

Nested critical sections are prohibited by default.

When a platform or RTOS explicitly supports nesting and the design requires it, analyze:

- Nesting depth
- Restore behavior
- Interrupt latency
- Deadlock risk
- Timing impact

A design record is required.

### 27.3 Atomic Access

A multi-byte object may not be atomic on an 8-bit or 16-bit MCU.

Atomicity shall be determined from the MCU, compiler, alignment, and generated instructions.

`volatile` does not make access atomic or race-free.

### 27.4 Queue and Mailbox

Queue and Mailbox full behavior shall be explicit:

- Reject newest
- Drop oldest
- Saturate a counter
- Set an overflow Event
- Enter a fault state

A full Queue shall not trigger hidden dynamic allocation.

### 27.5 Shared Counter

A counter shared by ISR, task, or main context shall address:

- Increment and decrement range
- Atomicity
- Lost update
- Read-and-clear race
- Saturation or wrap policy

Use a critical section, RTOS primitive, or platform-supported atomic operation when required.

### 27.6 Memory Ordering

When the platform contains caches, multiple cores, DMA, or weak ordering, the Platform Profile shall define:

- Cache maintenance
- Memory barriers
- DMA ownership transitions
- Volatile or atomic access pattern
- Buffer visibility

### 27.7 Deadlock Prevention

When more than one lock exists, the Project shall define a lock order.

A task shall not wait indefinitely while holding a lock required by another task to complete the operation.

---

## 28. Build and Tool Rules

### 28.1 Build Gate

A formal build shall produce:

```text
0 errors
0 warnings
```

A warning shall not be suppressed without documented analysis.

### 28.2 Compiler Configuration

The Project shall record:

- Compiler name
- Compiler version
- Language mode
- Optimization level
- Warning level
- Predefined symbols
- Stack size
- Heap size
- Linker command file
- Integer model
- Enum representation, when configurable
- Compiler extensions

The heap shall be zero or minimally unusable unless an approved Integration Record justifies it.

### 28.3 Static Analysis

Static Analysis shall cover at least:

- MISRA findings
- Signed and unsigned conversion
- Narrowing conversion
- Integer overflow and underflow
- Buffer bounds
- Null pointers
- Ignored return values
- Dead code
- Uninitialized variables
- Unreachable code
- Intentional infinite-loop forms
- Switch completeness
- Function prototype consistency
- Function-pointer compatibility
- Recursion
- Dynamic allocation
- Packed struct, bit-field, and union usage in Protocol code
- Direct buffer-to-struct cast

The tool shall flag `while (1)`, `while (1u)`, macro constants, and enum constants used to express an intentional
infinite loop.

### 28.4 Automated Checks

Automated checks should detect:

- `malloc`, `calloc`, `realloc`, and `free`
- RTOS or middleware dynamic-object APIs
- Variable Length Arrays
- CJK characters in Product-owned engineering files
- Mixed-language root Markdown documents
- Non-English Product-owned folder or file names
- Mixed-language source comments and function documentation
- Product-owned generated content containing non-English engineering text
- Missing Product-owned `.c` or `.h` File Headers
- Missing Product-owned Function Headers
- Missing Function Header fields
- Function Header parameter names that do not match the function signature
- Function Header return-value descriptions that do not match the function return type
- File Headers using block comments
- File Header file-name mismatch
- File Header Author or Revision History fields
- File Header placeholders
- Generated files missing warning, source, or generator information
- General block comments
- Doxygen-style comments
- Enum naming
- Macro naming
- Missing function module prefix
- Callback typedef and implementation naming
- Incompatible function-pointer cast candidates
- Callback Function Headers missing execution-context, ownership, lifetime, blocking, or Timing Budget information
- Low-level callbacks that call Application dispatch, Protocol codec, blocking, allocation, or long-running APIs
- Callback parameter pointers stored beyond their documented lifetime
- Duplicate, dangling, post-shutdown, or race-prone callback registration patterns
- Unchecked return-value candidates
- Numeric return codes
- Direct casts from internal result enum to process exit status
- Raw numeric process exit codes
- Magic-number candidates
- Raw hardware addresses and register masks
- Global objects missing a Global Object Record
- Packed structs in Protocol code
- Protocol bit-fields
- Union type-punning
- `sizeof(struct)` packet lengths
- Receive-buffer casts to Protocol structs
- Direct Vendor Stack or peripheral API calls from `main()`
- Protocol codec, command parsing, sample generation, or direct State Machine transition calls from `main()`
- Product business-logic candidates implemented in `main()`
- Manual modification of generated files
- Regeneration differences
- Prohibited intentional infinite-loop forms

### 28.5 Generated-code Integrity

The build or CI pipeline should regenerate generated artifacts and compare them with committed output.

A difference shall fail the validation gate unless the source definition or Generator version changed as part of
the same reviewed change.

### 28.6 Reproducible Build

A formal release shall record enough tool and configuration information to reproduce the binary.

The release record should include source revision, Generator versions, compiler version, linker configuration,
and relevant third-party component versions.

---

## 29. Review and Verification Rules

### 29.1 Code Review

Every Product-owned change shall receive review appropriate to its risk.

Review shall cover:

- Architecture boundary
- Rule compliance
- Arithmetic safety
- Memory bounds
- Error handling
- Concurrency
- Timing
- Protocol compatibility
- Generated-code integrity
- Test evidence

### 29.2 Deviation

A deviation shall identify:

- Rule or guideline
- Exact location
- Reason
- Risk
- Compensating control
- Verification
- Approver
- Scope
- Expiration or review trigger

A broad statement such as "Vendor requirement" is not sufficient.

### 29.3 Verification Evidence

Evidence may include:

- Unit test
- Integration test
- Static Analysis report
- Compiler warning report
- Timing measurement
- Stack measurement
- Long-run test
- Fault injection
- Protocol golden vector
- Interoperability test
- Code Review record

### 29.4 AI-assisted Code

AI-assisted code is Product-owned Code when selected for the Product implementation.

It shall receive the same:

- Human review
- Static analysis
- Build checks
- Unit and integration tests
- Security review
- Traceability

AI-generated wording or code shall not be accepted solely because it is syntactically correct.

### 29.5 Baseline Review

A Final Baseline review shall confirm:

- All Open Items are resolved, deferred, or explicitly out of scope.
- All placeholders are removed.
- Document version and history are correct.
- Code fences, headings, tables, and references are consistent.
- Product-owned Function Headers are present, complete, and synchronized with their functions.
- A structural rewrite preserves all previously approved normative rules or records every intentional removal.
- The primary narrative language is consistent.
- The document does not claim third-party ownership or compliance without evidence.

---

## 30. Open Items

The following topics require a Project or Platform Profile decision before use:

1. Approved C language version and permitted compiler extensions.
2. Rules for non-Protocol packed structs.
3. Rules for non-Protocol bit-fields.
4. Rules for union use outside Protocol serialization.
5. Floating-point availability, precision, rounding, and exception behavior.
6. Fixed-point arithmetic library and scaling conventions.
7. Approved assertion policy for debug and release builds.
8. Logging format, capacity, privacy, and rate limiting.
9. Maximum function complexity and nesting thresholds.
10. Approved unit-test framework.
11. Approved mocking and hardware-abstraction strategy.
12. Doxygen adoption, if any.
13. Secure-coding additions beyond the current MISRA-oriented baseline.
14. Multi-core, cache, and DMA memory-ordering requirements.
15. Compiler-specific atomic operations.
16. Watchdog ownership and service policy.
17. Startup self-test and diagnostic coverage.
18. Persistent-storage integrity and migration rules.
19. Cryptographic library selection and secure key handling.
20. Formal coverage objectives, if required.

Until a Project decision exists, an Open Item shall not be treated as blanket permission.

---

## 31. Initial Confirmed Rules

The confirmed Project-specific rules in this baseline are:

1. General comments use `//`.
2. General-purpose `/* ... */` comments are prohibited.
3. `/* ... */` is required for Product-owned Function Headers.
4. Every Product-owned function declaration and definition has a Function Header immediately before it.
5. Every Function Header identifies Function, Purpose, Input Parameters, Output Parameters, and Return Value.
6. A Function Header states `None` when an input, output, or return value does not exist.
7. Function Header parameter names and return-value meanings remain synchronized with the function signature and behavior.
8. `/** ... */` is prohibited.
9. Every Product-owned `.c` and `.h` file has a standardized File Header.
10. A Product-owned File Header uses `//`.
11. A `.c` File Header identifies File, Purpose, and Responsibilities.
12. A `.h` File Header identifies File, Purpose, and Public Contract.
13. A Product-owned File Header does not contain Author, manual Revision History, or unresolved placeholders.
14. Adopted Code retains its original Header and License.
15. A Product-owned Generated File Header is produced by the Generator and identifies source, Generator, and version.
16. Product-owned implementation repositories and generated Project folders use English.
17. Product-owned comments, function documentation, and engineering documents do not mix narrative languages.
18. `README.md`, `CHANGELOG.md`, `NOTICE.md`, and `VALIDATION_REPORT.md` use English.
19. Product-owned folder and file names use English.
20. Adopted Code and formal legal text retain their official language.
21. Non-English localization content is isolated.
22. Governance documents use one consistent primary narrative language; this document uses English.
23. Embedded Firmware uses static memory allocation.
24. `malloc`, `calloc`, `realloc`, and `free` are prohibited.
25. Product-owned Code does not call RTOS or middleware APIs that require dynamic allocation.
26. RTOS, Vendor, and third-party internals are Adopted Code and are not reformatted by this standard.
27. Product-owned integration, configuration, Adapters, and API usage remain governed.
28. Auto-generated configuration code receives runtime-resource and integration assessment.
29. Variable Length Arrays are prohibited.
30. Recursion is prohibited.
31. Macro names use uppercase letters and underscore separators.
32. Enum constants use uppercase letters and underscore separators.
33. File-static const objects use `s_` plus lower snake case.
34. Product-owned functions use a module prefix.
35. Magic numbers are prohibited.
36. Application, Protocol, Timing, Range, Threshold, Hardware, and Test values are named.
37. Numeric result codes are prohibited.
38. Internal results and process exit status use an explicit mapping.
39. Intrinsic literals are accepted by meaning, not by a closed numeric whitelist.
40. Unsigned increment checks the type maximum.
41. Unsigned decrement checks against zero.
42. Signed arithmetic is protected before undefined overflow can occur.
43. Narrowing conversion performs a range check first.
44. Intentional wraparound is prohibited unless documented and isolated.
45. Every failure-capable return value is handled or explicitly justified.
46. Callback typedef, registration, and implementation signatures match.
47. Every callback defines execution context, blocking permission, reentrancy, ownership, lifetime, registration, cancellation, Timing Budget, allowed APIs, and error reporting.
48. A callback executing in ISR context complies with all ISR rules.
49. Vendor, middleware, Driver, and low-level callbacks do not execute Application business logic, complete State Machine dispatch, Protocol encoding or decoding, blocking operations, dynamic allocation, or long-running work.
50. A low-level Adapter callback captures minimum data, updates bounded state, posts deferred work, and returns.
51. Callback parameter pointers are not used beyond their valid lifetime without controlled copy or explicit ownership transfer.
52. Callback registration and unregistration prevent duplicate, dangling, post-shutdown, deinitialized-state, and replacement-race hazards.
53. Global variables are prohibited by default and require a Global Object Record.
54. `volatile` is not synchronization.
55. Multi-byte atomicity is verified for the MCU and compiler.
56. Critical sections are bounded and do not block.
57. Nested critical sections are prohibited by default.
58. Queue and Mailbox overflow behavior is explicit.
59. ISR work is minimal, bounded, and non-blocking.
60. Every ISR has a Timing Budget or bounded-work definition.
61. Event ownership and loss policy are defined.
62. A bit Event is not used for non-loss-tolerant repeated occurrences.
63. State is modified only by the owning State Machine.
64. Invalid state and Event combinations are handled.
65. Every retry policy is bounded.
66. Protocol YAML is the Single Source of Truth for the wire contract.
67. Generated Protocol code is not edited manually.
68. Wire serialization does not depend on C struct layout.
69. Protocol code does not use packed structs as wire images.
70. Protocol code does not use bit-fields or union type-punning for wire bytes.
71. Packet length is not derived from `sizeof(struct)`.
72. Receive buffers are not cast directly to Protocol struct pointers.
73. Application code does not directly call Vendor Stack APIs.
74. `main()` is limited to startup, initialization, runtime handoff, dispatcher or scheduler startup, and defined failure handling.
75. `main()` does not perform Protocol codec, sample generation, command parsing, direct State Machine transitions, direct Vendor API access, or Product business logic.
76. A non-RTOS `main()` runs only the approved Application dispatcher and idle loop after initialization.
77. An RTOS `main()` creates only statically defined runtime objects and tasks, starts the scheduler, and does not execute task business logic.
78. Initialization failure or unexpected runtime return enters the defined safe-state, reset, halt, or approved fail-stop path.
79. Vendor modifications retain patch and verification evidence.
80. RTOS objects are statically created.
81. The number of tasks and runtime resources is bounded.
82. Formal builds have zero errors and zero warnings.
83. Static Analysis covers MISRA-oriented findings and Project-specific hazards.
84. Automated checks enforce high-value mechanical rules.
85. Intentional infinite loops use `for (;;)` or `while (true)`.
86. `while (1)`, `while (1u)`, macro constants, and enum constants are prohibited for intentional infinite loops.
87. Infinite loops outside the primary event loop require design justification and bounded work.
88. AI-assisted code receives the same review and verification as human-written code.
89. Third-party copyright, licenses, and legal notices are preserved.
90. This document does not by itself establish MISRA C:2023 compliance.

---

## Appendix A. Code Review Checklist

### A.1 Scope and Ownership

- [ ] Product-owned and Adopted Code boundaries are identified.
- [ ] Each module has one coherent responsibility.
- [ ] Public and private interfaces are separated.
- [ ] Shared objects have an owner.
- [ ] Global objects have Global Object Records.

### A.2 Files and Documentation

- [ ] Every Product-owned `.c` and `.h` file has a correct File Header.
- [ ] Every Product-owned function declaration and definition has a Function Header.
- [ ] Every Function Header contains Function, Purpose, Input Parameters, Output Parameters, and Return Value.
- [ ] Function Header parameter names match the function signature.
- [ ] Function Header return-value descriptions match the function return type and behavior.
- [ ] `None` is stated for every non-applicable Function Header field.
- [ ] File Header names match actual file names.
- [ ] `.c` Responsibilities are current.
- [ ] `.h` Public Contracts are current.
- [ ] No Author or manual Revision History appears in Product-owned File Headers.
- [ ] No unresolved placeholder remains.
- [ ] Product-owned content uses English.
- [ ] Adopted Code legal notices remain intact.
- [ ] Generated files identify source and Generator.

### A.3 Naming and Types

- [ ] Macros use uppercase snake case.
- [ ] Enum constants use uppercase snake case.
- [ ] Functions use module prefixes.
- [ ] File-static objects use `s_`.
- [ ] Global objects use `g_`.
- [ ] Callback types end in `_callback_t`.
- [ ] Callback implementations end in `_callback`.
- [ ] Fixed-width types are used when width matters.
- [ ] Signed and unsigned choices reflect the data model.
- [ ] Boolean values use `bool`, `true`, and `false`.

### A.4 Constants and Arithmetic

- [ ] No magic number with system meaning remains.
- [ ] Units are clear in names.
- [ ] Numeric return codes are absent.
- [ ] Process exit status uses explicit mapping.
- [ ] Increment and decrement boundaries are checked.
- [ ] Signed arithmetic cannot overflow before a check.
- [ ] Division checks zero and signed minimum divided by `-1`.
- [ ] Narrowing conversions check range.
- [ ] Shift counts and operand types are valid.
- [ ] Intentional wraparound is isolated and documented.

### A.5 Memory and Pointers

- [ ] No dynamic allocation is used.
- [ ] No VLA is used.
- [ ] No recursion is used.
- [ ] Buffer capacities are named.
- [ ] Used length is validated against capacity.
- [ ] Null pointers are validated.
- [ ] Pointer ownership and lifetime are clear.
- [ ] No writable pointer exposes private state.
- [ ] No unbounded string operation is used.
- [ ] Stack usage is acceptable.

### A.6 Control Flow and Functions

- [ ] Braces are used for all control statements.
- [ ] One statement appears per line.
- [ ] Conditions do not contain assignments.
- [ ] Every `switch` has a `default`.
- [ ] Every `case` terminates explicitly.
- [ ] Loop bounds are provable.
- [ ] Intentional infinite loops use an approved form.
- [ ] Function Headers remain synchronized with function behavior.
- [ ] Input, output, and in/out parameter behavior is documented correctly.
- [ ] Output behavior on failure is documented.
- [ ] Functions have one primary responsibility.
- [ ] Failure-capable return values are checked.
- [ ] Output parameters define failure behavior.
- [ ] `main()` contains only startup, initialization, runtime handoff, dispatcher or scheduler startup, and failure-path logic.
- [ ] `main()` contains no Protocol codec, sample generation, command parsing, direct State Machine transition, direct Vendor API access, or Product business logic.
- [ ] Every failure-capable initialization return value is checked.
- [ ] Unexpected dispatcher or scheduler return enters the defined failure path.

### A.7 Event, State, and ISR

- [ ] Event producer, consumer, loss policy, and clear policy are defined.
- [ ] Non-loss-tolerant occurrences do not rely only on one bit.
- [ ] State changes occur only through the owning State Machine.
- [ ] Transition triggers are explicit.
- [ ] Invalid state and Event combinations are handled.
- [ ] ISR work is minimal and bounded.
- [ ] ISR timing evidence exists.
- [ ] ISR shared data has an atomic or synchronized access pattern.
- [ ] Interrupt-disable duration is bounded.

### A.8 RTOS and Concurrency

- [ ] RTOS objects are statically created.
- [ ] Task count is fixed.
- [ ] Task stack sizes have evidence.
- [ ] Blocking calls have bounded timeouts or an approved forever-blocking design.
- [ ] Callback execution context is known.
- [ ] Callback blocking, reentrancy, ownership, lifetime, Timing Budget, allowed APIs, and error reporting are defined.
- [ ] ISR-context callbacks comply with all ISR rules.
- [ ] Low-level callbacks do not perform Application business logic, complete dispatch, Protocol codec, blocking, allocation, or long-running work.
- [ ] Callback pointer lifetime and registration or unregistration hazards are controlled.
- [ ] Critical sections are minimal and non-blocking.
- [ ] Nested critical sections are absent or justified.
- [ ] Queue and Mailbox full behavior is explicit.
- [ ] Lock order prevents deadlock.
- [ ] Shared counters handle range and race conditions.

### A.9 Protocol and Vendor Integration

- [ ] Protocol constants come from generated output.
- [ ] Generated Code was not manually modified.
- [ ] Incoming message length is validated.
- [ ] State, capability, version, and security permission are validated.
- [ ] Wire format does not depend on struct layout.
- [ ] No Protocol bit-field or union type-punning is used.
- [ ] No `sizeof(struct)` packet length is used.
- [ ] No receive buffer is cast to a Protocol struct pointer.
- [ ] Vendor APIs are isolated behind an Adapter.
- [ ] Vendor return values, timing, allocation, and callback behavior are handled.
- [ ] Vendor patches have evidence.

### A.10 Build and Evidence

- [ ] Build has zero errors and zero warnings.
- [ ] Compiler configuration is recorded.
- [ ] Heap configuration is recorded.
- [ ] Static Analysis findings are resolved or deviated.
- [ ] Automated checks pass.
- [ ] Generated-code regeneration comparison passes.
- [ ] Unit, integration, timing, or fault-injection evidence matches the risk.
- [ ] AI-assisted changes received human review.

---

## Appendix B. Prohibited Pattern Summary

The following patterns are prohibited unless a narrower approved exception explicitly applies:

```text
malloc / calloc / realloc / free
Variable Length Array
Direct or indirect recursion
General-purpose block comments
Missing or incomplete Product-owned Function Headers
Function Headers with parameter names that do not match the function signature
Function Headers that omit input, output, or return-value behavior
Doxygen comments without an adopted Doxygen policy
Author and manual Revision History in Product-owned File Headers
Unresolved legal or template placeholders
Magic numbers with system meaning
Direct numeric error or result returns
Unchecked narrowing conversions
Unprotected increment or decrement
Unanalyzed signed and unsigned mixing
Intentional wraparound without a reviewed policy
Ignored failure-capable return values
Writable access to another module's private state
Unbounded buffer or string operations
Direct Application calls to Vendor Stack APIs
Application business logic, complete State Machine dispatch, Protocol codec, blocking, allocation, or long-running work in a low-level callback
Using a callback parameter pointer after its valid lifetime without controlled copy or ownership transfer
Duplicate, dangling, post-shutdown, or race-prone callback registration
Product business logic in main()
Protocol codec, sample generation, command parsing, or direct State Machine transition in main()
Direct Vendor Stack or peripheral API calls from main()
Dynamic RTOS object creation
Blocking or unbounded ISR work
Using volatile as synchronization
Unbounded retry
Silent invalid state or Event handling
Manual edits to generated code
Protocol wire images based on C struct layout
Protocol bit-fields
Protocol union type-punning
sizeof(struct) packet lengths
Receive-buffer-to-Protocol-struct casts
while (1)
while (1u)
Macro or enum constants used as an intentional infinite-loop condition
Formal builds with warnings
Removal or rewriting of third-party legal notices
```

---

## Appendix C. Reference Application Guidance

This appendix provides an illustrative reference profile for an MCU USB streaming application. It does not
represent an existing commercial Product.

### C.1 Example Context

```text
Host:
    PC application

Node:
    MCU firmware

Transport:
    USB CDC

Data:
    Deterministic sensor waveform

Nominal Sample Rate:
    250 Hz
```

### C.2 Recommended Module Boundary

```text
application/
    app.c
    app.h
    app_event.c
    app_event.h

service/
    stream_service.c
    stream_service.h

protocol/
    generated/
    protocol_codec.c
    protocol_codec.h

driver/
    usb_cdc_transport.c
    usb_cdc_transport.h

bsp/
    bsp_clock.c
    bsp_clock.h
    bsp_timer.c
    bsp_timer.h

test_support/
    sample_source.c
    sample_source.h
```

### C.3 Event Flow

```text
Timer ISR
    |
    v
APP_EVENT_STREAM_TICK
    |
    v
Application Dispatcher
    |
    v
Sample Source
    |
    v
Stream Service
    |
    v
Protocol Encoder
    |
    v
USB CDC Transport
```

When every 250 Hz occurrence must be preserved, use a counter, mailbox, ping-pong buffer, or hardware sample
count rather than one mergeable bit.

### C.4 Initialization Order

A reference initialization sequence is:

```text
Disable interrupts
Initialize clock
Initialize module state
Initialize static RTOS or event objects
Initialize Vendor USB stack
Reapply timer configuration if Vendor initialization changed it
Initialize Protocol and streaming service
Clear pending hardware status
Enable interrupts
Enter the application event loop
```

### C.5 Entry Point and Event Loop

The normative Embedded Firmware entry-point rules are defined in Section 25.

This appendix intentionally does not duplicate a `main()` implementation because duplicated examples can drift
away from the governing rule.

For a non-RTOS realization of this reference application:

- Apply the responsibility boundary and initialization sequence in Sections 25.1 through 25.4.
- Run Product behavior through the Application dispatcher rather than directly in `main()`.
- Handle initialization failure and unexpected runtime return according to Section 25.6.

For an RTOS realization:

- Apply Section 25.5.
- Create only the statically defined runtime objects and tasks required by the design.
- Start the scheduler only after required initialization succeeds.
- Treat an unexpected scheduler return according to Section 25.6.

Host-side process exit behavior remains governed by Section 12.5.

### C.6 Validation Focus

The reference implementation shall verify:

- Sample tick loss
- USB disconnect and reconnect
- Queue or Mailbox overflow
- Protocol encoding bounds
- Sequence wrap boundary
- Static memory use
- ISR timing
- Event-loop bounded work
- Vendor initialization side effects
- Long-run stability

---

## Appendix D. File and Function Header Templates

### Product-owned `.c`

```c
// Copyright (c) 2026 <Approved Copyright Holder>. All rights reserved.
//
// File:
//     module_name.c
//
// Purpose:
//     Implements <module purpose>.
//
// Responsibilities:
//     - <primary responsibility>
//     - <secondary responsibility>
//     - <owned state or resource>
//
// Notes:
//     <optional important limitation>
```

### Product-owned `.h`

```c
// Copyright (c) 2026 <Approved Copyright Holder>. All rights reserved.
//
// File:
//     module_name.h
//
// Purpose:
//     Defines the public contract for <module purpose>.
//
// Public Contract:
//     - <public capability>
//     - <caller responsibility>
//     - <encapsulation boundary>
//
// Notes:
//     <optional important limitation>
```


### Product-owned Function Returning a Result

```c
/*
 * Function:
 *     module_operation
 *
 * Purpose:
 *     Performs <one clear function purpose>.
 *
 * Input Parameters:
 *     input_value:
 *         <meaning, valid range, unit, ownership, and read behavior>.
 *
 * Output Parameters:
 *     output_value:
 *         <written result, ownership, and behavior on failure>.
 *
 * Return Value:
 *     MODULE_RESULT_OK:
 *         <success condition>.
 *     MODULE_RESULT_INVALID_ARGUMENT:
 *         <invalid argument condition>.
 *     MODULE_RESULT_OUT_OF_RANGE:
 *         <range failure condition>.
 */
module_result_t module_operation(
    uint16_t input_value,
    uint16_t *output_value);
```

### Product-owned `void` Function

```c
/*
 * Function:
 *     module_process
 *
 * Purpose:
 *     Performs <one clear function purpose>.
 *
 * Input Parameters:
 *     None.
 *
 * Output Parameters:
 *     None.
 *
 * Return Value:
 *     None.
 */
void module_process(void);
```

### Product-owned Function with an In/Out Parameter

```c
/*
 * Function:
 *     module_update_context
 *
 * Purpose:
 *     Validates and updates the supplied module context.
 *
 * Input Parameters:
 *     context:
 *         Supplies the current context state to be validated and updated.
 *     update_value:
 *         Supplies the value to apply.
 *
 * Output Parameters:
 *     context:
 *         Receives the updated context when the function returns
 *         MODULE_RESULT_OK. The context remains unchanged on failure.
 *
 * Return Value:
 *     MODULE_RESULT_OK:
 *         The context was updated successfully.
 *     MODULE_RESULT_INVALID_ARGUMENT:
 *         A required pointer is NULL.
 *     MODULE_RESULT_INVALID_STATE:
 *         The current context state does not permit the update.
 */
module_result_t module_update_context(
    module_context_t *context,
    uint16_t update_value);
```

### Product-owned Generated File

```c
// AUTO-GENERATED FILE.
// DO NOT EDIT MANUALLY.
//
// File:
//     module_name_generated.h
//
// Source:
//     <single source definition>
//
// Generator:
//     <generator name>
//
// Generator Version:
//     <generator version>
//
// Purpose:
//     <generated file purpose>
```

All template placeholders shall be replaced before release.

---

## Appendix E. Global Object Register Template

Recommended file:

```text
docs/design/Global_Object_Register.md
```

Minimum fields:

| Global Object ID | Symbol | Type | Owner | Writer | Reader | Synchronization | Initialization | Lifetime | Reason | Verification |
|---|---|---|---|---|---|---|---|---|---|---|
| GOR-BSP-001 | `g_system_tick` | `volatile uint32_t` | BSP Time | Timer ISR | Application and Diagnostics | Atomic read or critical section | `bsp_time_init()` | System lifetime | Hardware time base shared across modules | Code Review and Timing Test |

Record requirements:

1. Global Object ID is unique.
2. Symbol matches the code exactly.
3. A single writer is preferred.
4. Synchronization shall not state only `volatile`.
5. Reason explains why file-static storage and accessor APIs are insufficient.
6. Verification points to Code Review, Static Analysis, Timing Test, or Unit Test evidence.
7. A removed symbol is marked retired or retained through version history rather than silently deleted.

---

## Appendix F. Change History

| Version | Description |
|---|---|
| v1.0.0 | Established the initial MISRA-oriented Embedded C rules, comment policy, static-memory configuration, macro and enum naming, arithmetic boundary checks, and Event-Driven, State Machine, ISR, Protocol, and Vendor Code implementation rules. |
| v1.0.1 | Clarified the Adopted Code boundary and Product-owned integration responsibility; added static RTOS object creation, signed arithmetic protection, return-value handling, essential-type and conversion rules, loop-index selection, `static const` naming, module prefixes, information hiding, ISR and critical-section Timing Budgets, `volatile` limitations, and synchronization review guidance. |
| v1.0.2 | Added callback and function-pointer naming, signature, execution-context, ownership, and lifetime rules; established the Global Object Register; added a signed-multiplication example; closed auto-generated configuration-code assessment gaps; and prohibited Protocol wire formats based on packed structs, bit-fields, union type-punning, native struct layout, or `sizeof(struct)`. |
| v1.0.3 | Added the Magic Number and Named Constant chapter; prohibited numeric result codes and unnamed Application, Protocol, Timing, Threshold, Hardware, and Test literals; defined intrinsic-literal judgment, constant representation, unit naming, scope, and single-definition rules. |
| v1.0.4 | Added standardized File Header rules for every Product-owned `.c` and `.h` file; defined placement, required fields, `//` style, `.c` Responsibilities, `.h` Public Contract, Author and manual Revision History prohibitions, placeholder and legal-text management, Adopted Code Header preservation, and Generated File Headers. |
| v1.0.5 | Added Project Language and Documentation Rules; required English for Product-owned implementation repositories and generated Project folders; required English for root documents; and defined folder and file naming, generated content, Adopted Code and legal-text exceptions, localization isolation, and CJK detection. |
| v1.0.6 | Reworked the language-governance chapter for narrative consistency; added governance-document primary-language and merge-consistency rules; clarified that intrinsic literals are judged semantically rather than through a closed `0u` and `1u` whitelist; and defined the boundary between internal results and Host process exit status. |
| v1.0.7 | Performed a governance-document narrative-language consistency cleanup; synchronized confirmed rules, open items, the reference appendix, and Change History without changing technical rule meaning. |
| v1.0.8 | Finalized intentional infinite-loop representation: preferred `for (;;)` and allowed `while (true)`; prohibited `while (1)` and `while (1u)`; required design justification, explicit execution context, and bounded internal work for infinite loops outside the primary application event loop; synchronized Static Analysis, Automated Checks, Code Review Checklist, Initial Confirmed Rules, and Prohibited Pattern Summary. |
| v1.0.9 | Resolved the conflict between the Infinite Loop rule and Boolean Type rule; required the Section 13.3 Boolean literal `true` for the `while` form; prohibited integer literals, macro constants, and enum constants that imitate Boolean true; synchronized related analysis, automation, review, confirmed-rule, and prohibited-pattern content. |
| v1.0.10 | Converted the complete governance document to English; established English as the primary narrative language; added Ray Yang authorship, repository identity, copyright, personal-project clarification, and third-party reference notice; generalized approved copyright-holder placeholders; preserved the v1.0.9 technical baseline while normalizing terminology, punctuation, examples, checklists, and change-history wording for public GitHub publication. |
| v1.0.11 | Required a complete Function Header immediately before every Product-owned function declaration and definition; standardized the mandatory Function, Purpose, Input Parameters, Output Parameters, and Return Value fields; required explicit `None` entries when a field is not applicable; defined in/out parameter and failure-output documentation; and synchronized Function Rules, automated checks, baseline review, confirmed rules, review checklists, prohibited patterns, and Appendix D templates. |
| v1.0.12 | Restored normative rules that were unintentionally lost during the v1.0.10 English structural rewrite: reinstated the Embedded Firmware entry-point and `main()` responsibility boundary as a formal chapter; restored concrete callback prohibitions, bounded Adapter behavior, parameter-lifetime control, registration and unregistration hazard prevention, and ISR-context linkage; and synchronized automated checks, baseline review, confirmed rules, review checklists, prohibited patterns, and chapter numbering. |
| v1.0.13 | Removed the duplicated and weaker `main()` example from Appendix C.5; established Section 25 as the single normative source for Embedded Firmware entry-point behavior; replaced the appendix implementation with explicit non-RTOS and RTOS application guidance and cross-references; and eliminated the risk of future example drift between the normative chapter and the reference appendix. |
| v1.0.14 | Updated the active baseline-document references to `Coordinator_Node_Control_Framework.md`, `Framework_Application_Analysis_Template.md`, `Protocol_YAML_Definition_Guide.md`, and `Protocol_YAML_Template.md`; added the canonical Document Name metadata; and preserved all existing Embedded C coding-rule semantics without technical change. |
| v1.0.15 | Adopted the stable canonical filename `Embedded_C_Coding_Rules.md`; updated active cross-document references to canonical paths; retained the document version in metadata and Version History; and preserved all Embedded C coding-rule semantics without technical change. |
