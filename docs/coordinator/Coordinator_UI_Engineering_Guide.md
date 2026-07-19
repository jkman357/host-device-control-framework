# Coordinator UI Engineering Guide

> UI Architecture, State Presentation, Responsiveness, and Control Feedback

**Canonical Filename:** `Coordinator_UI_Engineering_Guide.md`  
**Document Version:** v1.0.1  
**Status:** Draft for Review  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-19  
**Language:** English  
**Intended Audience:** Human engineers, software architects, UI engineers, reviewers, test engineers, code generators, and AI-assisted engineering systems  
**Repository Role:** Proposed topic-specific normative engineering authority for Coordinator UI implementation, subordinate to Coordinator Software Engineering Rules  
**Supersedes Document Version:** v1.0.0

---

## Copyright and Use

Copyright © 2026 Ray Yang. All rights reserved unless a repository-level license states otherwise.

This document is independently authored. External standards and guidance are referenced for context and are not reproduced as substitute standards. Third-party documents remain subject to their respective copyright and license terms.

This document is maintained as part of a personal engineering project. It is not an official document of any employer or organization.

---

## Related Documents

- [Coordinator/Node Control Framework](../framework/Coordinator_Node_Control_Framework.md)
- [Coordinator Software Engineering Rules](Coordinator_Software_Engineering_Rules.md)
- [Coordinator Architecture Patterns](Coordinator_Architecture_Patterns.md)
- [Coordinator Concurrency Guide](Coordinator_Concurrency_Guide.md)
- [Coordinator Logging Guide](Coordinator_Logging_Guide.md)
- [Coordinator Testing Guide](Coordinator_Testing_Guide.md)

---

## Version History

| Version | Date | Status | Summary |
|---|---|---|---|
| v1.0.0 | 2026-07-19 | Draft for Review | Initial Draft defining UI architecture, state ownership, command feedback, connection and stale state, multi-Node binding, data visualization, responsiveness, alarms and events, validation, errors, units, accessibility, localization, persistence, engineering controls, testing, and anti-patterns. |
| v1.0.1 | 2026-07-19 | Draft for Review | Hardened archive and package import against symbolic links, hard links, Windows reparse points, special filesystem entries, destination-link traversal, canonical-path escape, unintended overwrite, and time-of-check/time-of-use replacement. |

---

# 0. Purpose

This Guide defines engineering practices for Coordinator-side user interfaces that display Node state, issue commands, visualize data, and support operation, service, production, or laboratory workflows.

It is not a Product UI/UX Specification and does not define Product-specific wording, workflow, alarm priority, accessibility acceptance criteria, or clinical and safety decisions. Those belong to approved Product requirements and human review.

The Guide focuses on implementation boundaries, state truthfulness, responsiveness, stale-data behavior, command feedback, data visualization, error handling, and testability.

## 0.1 Requirement Keywords

- **shall**: required when this Guide applies and no approved deviation exists;
- **should**: preferred default;
- **may**: permitted option.

## 0.2 Authority Boundary

This document is a `Draft for Review`. Its requirements are proposed and do not apply to a Project until a human authority explicitly adopts or approves this document for that Project.

`Coordinator_Software_Engineering_Rules.md` remains the cross-topic Coordinator software authority. This Guide owns only the detailed Coordinator UI implementation and presentation-state realization rules within its stated scope after adoption. It shall not weaken or silently override the cross-topic rules. Repeated Framework, Protocol, safety, security-boundary, or Product rules are `Derived conformance summary` unless a section explicitly identifies a Coordinator-specific realization owned here.

This Guide does not define:

- Product-specific wording, workflow, alarm priority, or clinical decisions;
- usability or accessibility acceptance criteria owned by approved Product authorities;
- Protocol, Transport, authorization, or Node safety behavior;
- platform-specific coding syntax.

Approved Product requirements, the Coordinator SDD, the Project Protocol, applicable cybersecurity and safety authorities, platform constraints, and language-specific coding rules take precedence within their owned topics. A conflict shall be reported rather than silently resolved.
---

# 1. Core UI Engineering Principles

1. The UI shall present application state; it shall not own Protocol or Transport behavior.
2. Displayed Node state shall come from validated application or domain state.
3. Requested, pending, confirmed, rejected, timed-out, stale, unknown, and disconnected states shall not be conflated.
4. A command shall not be displayed as successful merely because a Transport write completed.
5. Blocking I/O and long-running work shall not execute on the UI thread.
6. High-rate data shall be rate-limited, batched, downsampled, or virtualized before presentation.
7. Safety-critical protection shall not depend only on Coordinator UI availability.
8. The UI shall not silently hide loss of connection, stale data, invalid data, or uncertain command outcome.
9. User input shall be validated before it reaches the command path. UI enablement or validation is not authorization; the Application layer and Node shall enforce their owned authorization and state checks.
10. Errors should be actionable and correlated with diagnostic evidence.
11. UI behavior should be testable without physical hardware where practical.
12. Product-specific usability decisions require human review and appropriate evidence.

---

# 2. UI Architecture Boundary

A recommended flow is:

```text
UI Control or User Gesture
    -> Presentation Command
    -> Application Use Case
    -> Command Gateway
    -> Communication and Protocol Layers

Validated Device State
    -> State Store
    -> Presentation Projection
    -> UI Binding or Render
```

The UI layer shall not:

- create Message IDs or wire payloads;
- open or close a serial port or socket directly from a control event handler;
- parse incoming frames;
- own request-response correlation;
- mutate shared domain state without an application-owned transition;
- write diagnostic files directly from high-rate callbacks;
- decide Product safety behavior not defined by an authority.

View models, presenters, controllers, or equivalent presentation objects should expose UI-ready state and commands without depending on concrete controls.

---

# 3. Presentation State Model

Presentation state should explicitly represent:

- connection lifecycle;
- compatibility or capability state;
- synchronization state;
- observed Node state;
- requested value;
- pending operation;
- command result;
- stale or unknown data;
- validation error;
- degraded function;
- recording or update progress;
- user selection and navigation state.

A nullable value alone is often insufficient because `unknown`, `not supported`, `not yet received`, `invalid`, `stale`, `not-a-number`, positive or negative infinity, overflowed, and out-of-representable-range values may require different presentation.

UI-ready state should preferably be immutable or updated through a single presentation owner.

---

# 4. Connection and Availability Presentation

The UI should distinguish states such as:

- disconnected;
- connecting;
- Transport connected but not negotiated;
- synchronizing;
- ready;
- degraded;
- reconnecting;
- incompatible;
- faulted;
- disconnecting.

Rules:

1. Controls requiring a ready connection shall remain disabled until required negotiation and state reconciliation complete.
2. Previously displayed values shall not appear current after disconnect unless clearly marked stale and Product requirements permit retention.
3. Automatic reconnect shall be visible without flooding the user with repeated dialogs.
4. A manual disconnect and an unexpected link loss may require different user feedback.
5. The UI should identify the connected Node and version where confusion with another device is possible.
6. Capability-dependent controls shall be hidden, disabled, or marked unsupported according to the approved Product design.

---

## 4.1 Multi-Node Selection and Operation Binding

When the UI can display or control more than one Node:

1. The selected view target, the operation target, and the connected-session identity shall be distinguishable.
2. A command shall capture its target Node identity and connection generation before leaving the Presentation layer.
3. Changing the visible selection shall not retarget, cancel, or visually attribute an in-flight operation unless the defined workflow explicitly performs that action.
4. Pending and completed results shall be presented against the Node that actually received the operation.
5. Reconnect to a different Node shall clear or mark stale the prior Node state before controls are enabled.
6. Shared controls shall not appear to operate on all Nodes unless the workflow explicitly defines a reviewed multi-target command with per-Node results.

# 5. Stale, Unknown, and Invalid Data

The presentation shall define how to display:

- not yet received;
- not supported;
- invalid according to Protocol or Product validation;
- stale due to age;
- stale due to disconnect;
- temporarily unavailable;
- out of expected range;
- quality-reduced or degraded data.

A stale threshold shall come from an approved requirement, design decision, or documented engineering rationale.

Stale data should not silently continue to drive an enabled user action that requires current state.

When a value is retained for context, its stale status and last update time should be available where appropriate.

---

# 6. Command Interaction and Feedback

A user command should follow an explicit presentation lifecycle:

```text
Available
    -> Validating
    -> Pending Send or Pending Completion
    -> Completed / Rejected / Timed Out / Cancelled / Disconnected / Uncertain
```

Rules:

1. Prevent duplicate invocation when the operation is not safely repeatable.
2. Show progress only when the value is meaningful and supported by the operation.
3. Distinguish user cancellation from failure.
4. Distinguish timeout from confirmed rejection.
5. When completion is uncertain, do not invite blind retry; reconcile state first or explain the uncertainty.
6. Preserve the user's entered value when correction is possible, unless security or Product rules require clearing it.
7. Disable conflicting commands while an exclusive operation is active.
8. A destructive or high-impact action should use the confirmation behavior defined by the Product UI/UX authority.
9. Command availability shall be derived from current application state, not only from visual control state.

---

# 7. Responsiveness and UI Thread Use

The UI thread shall remain available for input, layout, and rendering.

Do not execute the following synchronously on the UI thread unless a bounded measurement proves it is negligible and the platform design approves it:

- Transport open, close, read, or write;
- file import, export, recording, or log scanning;
- large Protocol decode;
- cryptographic operation;
- firmware image validation;
- long computation;
- unbounded collection update;
- device discovery with operating-system delay.

Long-running operations should provide:

- pending state;
- cancellation when supported;
- bounded progress updates;
- final result;
- diagnostic correlation.

Rapid progress events should be coalesced before UI dispatch.

---

# 8. High-Rate Data Visualization

Charts and waveform displays shall be decoupled from raw receive callbacks.

The design should define:

- source sample rate;
- render update rate;
- visible time window;
- retained sample count;
- downsampling or aggregation method;
- gap and invalid-data rendering;
- timestamp source;
- pause and resume behavior;
- zoom and pan behavior;
- memory bound;
- export behavior.

Rules:

1. Do not dispatch one UI update per sample at high rate.
2. Use bounded batches or display snapshots.
3. Preserve gaps; do not draw a continuous line across missing data unless the Product specification explicitly requires interpolation.
4. Downsampling shall preserve features required by the intended use.
5. Display-rate reduction shall not silently change the raw recording path.
6. Pausing visualization shall not automatically imply stopping acquisition or recording.
7. Chart buffers and histories shall be bounded.
8. Axis units, scaling, and time base shall be explicit.

---

# 9. Tables, Lists, and Histories

Large or continuously growing collections should use:

- virtualization;
- pagination;
- bounded history;
- incremental loading;
- filtered projections;
- background parsing with controlled UI publication.

The UI shall not retain an unlimited in-memory event, alarm, log, or sample history.

Sorting and filtering should operate on a stable snapshot or controlled data source so new incoming items do not create inconsistent selection or ordering.

---

# 10. Alarm, Event, and Diagnostic Presentation

The UI shall preserve the distinction among:

- Product Alarm;
- Product Event;
- status or advisory message;
- diagnostic log;
- communication error;
- application fault.

Diagnostic log severity shall not determine Product Alarm priority.

Alarm behavior, acknowledgement, latching, silence, history, priority, and wording shall come from approved Product authorities.

A diagnostic failure may be presented to the user, but it shall not be added to an Alarm History unless the Product definition says it is an alarm.

---

# 11. Input Validation

Validation should occur at appropriate layers:

- UI-level syntax and immediate feedback;
- application-level use-case and state preconditions;
- domain-level invariant checks;
- Protocol-level range and encoding checks;
- Node-side authoritative validation.

The UI shall not assume that local validation replaces Node validation.

Input behavior should define:

- allowed characters or format;
- unit;
- minimum, maximum, and step;
- precision and rounding;
- locale behavior;
- empty or default behavior;
- validation timing;
- recovery message;
- whether the value is committed immediately or explicitly applied.

Error text should identify how the user can correct the value.

---

## 11.1 Import and External-Content Safety

Imported files, pasted text, drag-and-drop content, URLs, support bundles, images, and configuration data shall be treated as untrusted input. The UI shall not rely on file extension, displayed filename, or user selection as proof of content type or safety.

The import path shall define size, count, nesting, encoding, decompression, path, and numeric bounds; validate content before state mutation; prevent path traversal and unintended overwrite; and report partial or rejected imports truthfully. Preview rendering shall not execute embedded active content.

Archive or package import shall reject symbolic links, hard links, Windows reparse points, device files, named pipes, and other special filesystem entries unless an approved format explicitly requires and safely handles them. Every candidate output path shall be canonicalized immediately before creation and verified to remain within the designated extraction root. Extraction shall not follow existing links in the destination path, shall not replace a verified path component after validation, and shall fail closed when link replacement or another time-of-check/time-of-use change is detected.

# 12. Units, Numeric Formatting, and Time

Displayed numeric values shall define:

- unit;
- scaling;
- precision;
- rounding method;
- valid range;
- invalid and unavailable representation;
- locale behavior;
- conversion authority.

A unit symbol shall not be omitted when omission could cause ambiguity.

The UI shall not independently redefine a Protocol scale factor or unit conversion already owned by generated Protocol or approved Product definitions.

Time presentation should identify, as applicable:

- local or UTC time;
- Node or Coordinator timestamp;
- elapsed duration;
- time-zone behavior;
- stale age;
- precision.

Duration calculations should use monotonic time even when displayed timestamps use wall-clock time.

---

# 13. Error Presentation

A user-facing error should include, as appropriate:

- what operation failed;
- current outcome;
- whether retry is safe;
- recommended next action;
- whether state may be uncertain;
- a support or correlation code.

Raw exception text, stack traces, secrets, device keys, and uncontrolled payload data shall not be shown in normal user dialogs.

Repeated transient errors should be consolidated into status presentation rather than repeated modal dialogs.

An error dialog shall not block required background cleanup or disconnect handling.

---

# 14. Progress and Long Operations

For operations such as firmware update, data export, calibration, or long acquisition setup, define:

- operation states;
- progress source;
- cancellation support;
- interruption behavior;
- recoverability;
- close-window behavior;
- retry safety;
- final verification;
- user-visible completion criteria.

A progress percentage shall not be displayed unless its denominator and meaning are valid. Otherwise use an indeterminate state with meaningful stage text.

Closing a view shall not orphan the operation. The operation should either continue under an application owner or be cancelled through a defined workflow.

---

# 15. Accessibility and Interaction

Where applicable to the Product and platform, the UI should support:

- keyboard navigation;
- visible focus;
- screen-reader labels;
- sufficient contrast;
- non-color-only status indication;
- scalable text and layout;
- appropriate target size;
- consistent shortcut behavior;
- clear disabled-state explanation;
- error association with the relevant field.

Accessibility acceptance criteria shall come from the applicable Product and platform authority.

---

# 16. Localization

Localization design should separate translatable text from identifiers, log event codes, Protocol names, file formats, and machine-readable values.

The UI shall define locale behavior for:

- decimal separator;
- thousands separator;
- date and time;
- units;
- text expansion;
- right-to-left layout when applicable;
- sorting and comparison;
- import and export formats.

Machine-readable files should use a stable locale-independent format unless an approved external format requires otherwise.

A translated string shall not be used as a stable program identifier.

---

# 17. Persistence of UI State

UI-only preferences may include:

- window layout;
- selected tab;
- chart display options;
- recent non-sensitive paths;
- theme;
- column widths.

Rules:

1. UI preference persistence shall be separate from Product-controlled Node configuration.
2. Secrets shall not be stored in ordinary UI settings.
3. Persisted settings shall have schema version and migration behavior where needed.
4. Invalid settings shall recover to a known default without changing Product behavior silently.
5. A previously selected device shall not be reconnected or commanded automatically unless the Product workflow explicitly permits it.

---

# 18. Diagnostic and Support Features

Support features may include:

- version and build information;
- connected Node and Protocol information;
- connection state and last error;
- bounded log export;
- configuration summary;
- queue or Stream diagnostics;
- capture start and stop;
- support bundle generation.

Support output shall exclude secrets and unapproved personal data.

A support feature shall not expose hidden controls that can bypass Product authorization or safety boundaries.

---


# 19. Engineering and Service Controls

Engineering-only, manufacturing, service, diagnostic, or hidden controls shall have explicit scope and lifecycle. The design shall define:

- discoverability and labeling;
- authorization and role checks outside the visual control state;
- permitted Product modes and Node states;
- command and audit or diagnostic evidence;
- whether the feature is excluded from production builds, disabled by signed configuration, or otherwise controlled;
- failure, timeout, disconnect, and recovery behavior.

A hidden gesture, undocumented shortcut, disabled button, or obscured menu is not an authorization control. Engineering controls shall not bypass Product safety, Protocol validation, or Node authorization boundaries.

# 20. UI Testing

Testing should cover:

- presentation state projection;
- command enablement;
- pending and final result behavior;
- stale, unknown, invalid, and disconnected display;
- UI-thread dispatch;
- close during active work;
- reconnect presentation;
- high-rate update coalescing;
- chart gaps and bounds;
- list virtualization and history limits;
- input boundaries and locale behavior;
- units and precision;
- error messages and support correlation;
- accessibility behavior where required;
- localization and text expansion;
- configuration migration;
- simulator-driven end-to-end workflows;
- multi-Node selection changes during pending operations;
- NaN, infinity, overflow, invalid timestamps, extreme text length, and unsupported encoding;
- hostile or malformed imports and support bundles;
- engineering-control authorization and production-build exclusion.

Visual snapshots may supplement tests but shall not replace behavioral assertions.

---

# 21. UI Anti-Patterns

Reject or explicitly justify:

1. UI controls directly encoding or decoding Protocol frames.
2. Transport callbacks directly modifying controls.
3. A write call immediately setting the displayed Node state as confirmed.
4. Keeping old values visually current after disconnect.
5. One UI update per high-rate sample.
6. Unlimited chart, log, alarm, or event history.
7. Modal dialog storms during reconnect or repeated faults.
8. Generic `Error` messages without operation or recovery guidance.
9. Raw exception or secret data shown to users.
10. Product Alarm behavior inferred from diagnostic log severity.
11. UI validation being treated as the only authoritative validation.
12. Blocking file, device, or network operations on the UI thread.
13. Closing a window while orphaning active work.
14. Using translated strings as program identifiers.
15. Hiding unavailable or stale state by displaying zero or the prior value without indication.
16. Treating a disabled, hidden, or visually inaccessible control as authorization.
17. Retargeting an in-flight command when the selected Node changes.
18. Trusting imported content based only on filename, extension, or user selection.
19. Rendering NaN, infinity, overflow, invalid timestamps, or uncontrolled text as normal Product values.
20. Shipping engineering-only controls without explicit authorization and production-use governance.

---

# 22. UI Engineering Review Checklist

- [ ] Approved Product UI/UX, usability, alarm, risk, and platform authorities are identified.
- [ ] UI, application, Protocol, and Transport responsibilities are separated.
- [ ] Presentation state distinguishes observed, requested, pending, confirmed, rejected, stale, unknown, and disconnected states.
- [ ] Command success is not inferred from Transport write completion.
- [ ] Controls are gated by connection, synchronization, capability, and operation state, while authorization is independently enforced by the Application layer and Node.
- [ ] Multi-Node operations remain bound to the intended Node identity and connection generation.
- [ ] Blocking work is absent from the UI thread.
- [ ] Background exceptions and cancellation are handled.
- [ ] High-rate data uses bounded batching, downsampling, or coalescing.
- [ ] Chart gaps, timestamps, units, and memory bounds are defined.
- [ ] Lists and histories are virtualized, paged, or bounded.
- [ ] Product Alarms, events, diagnostics, and communication errors are distinguished.
- [ ] Input validation, units, precision, rounding, locale behavior, NaN, infinity, overflow, invalid time, and extreme text handling are defined.
- [ ] Imported and external content is treated as untrusted and processed within explicit bounds.
- [ ] Error messages are actionable and correlated with diagnostic evidence.
- [ ] Long-operation progress, cancellation, close, interruption, and recovery behavior are defined.
- [ ] Accessibility and localization requirements are applied where required.
- [ ] UI preferences are separated from Product configuration and secrets.
- [ ] Support export excludes sensitive information.
- [ ] Engineering and service controls have explicit authorization, mode, evidence, and production-build governance.
- [ ] Presentation logic and framework integration are testable.
