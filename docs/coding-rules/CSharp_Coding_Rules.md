# C# Coding Rules

**Canonical Filename:** `CSharp_Coding_Rules.md`  
**Document Version:** V1.0.1  
**Status:** Draft for Review  
**Document Owner:** Ray Yang  
**Initial Release Date:** 2026-07-18  
**Language:** English  
**Intended Audience:** Human engineers, reviewers, test engineers, code generators, and AI-assisted engineering systems  
**Repository Role:** Normative language and implementation authority for Product-owned C# code  

---

## Copyright and Use

Copyright © 2026 Ray Yang. All rights reserved unless a repository-level license states otherwise.

This document is independently authored. Microsoft and other external guidance is referenced for engineering context and is not reproduced as a substitute standard. Third-party documents remain subject to their respective copyright and license terms.

---

## Version History

| Version | Date | Status | Summary |
|---|---|---|---|
| V1.0.1 | 2026-07-18 | Draft for Review | Clarified conditional architecture authority, refined formatting and field rules, established the default .NET Framework 4.7.2 / C# 7.3 profile, corrected cancellation and background-worker examples, and separated document review from project implementation validation. |
| V1.0.0 | 2026-07-18 | Draft for Review | Initial full baseline covering C# source organization, naming, type use, null handling, asynchronous programming, concurrency, errors, resources, UI integration, serialization, security, analyzers, testing, generated code, and a .NET Framework 4.7.2 compatibility profile. |

---

# Part I — Document Governance

## 1. Purpose

This document defines mandatory and recommended coding rules for Product-owned C# source code.

It is intended to make C# implementation:

- Readable.
- Predictable.
- Testable.
- Reviewable.
- Diagnosable.
- Safe at trust boundaries.
- Compatible with the declared runtime and toolchain.
- Suitable for human and AI-assisted development.

This document controls C# language and .NET implementation practices. It does not independently own product architecture.

When C# code implements or directly supports a Coordinator role, the applicable architecture and lifecycle authority is:

```text
Coordinator_Software_Engineering_Rules.md
```

For C# code outside the Coordinator role, the Project profile shall identify the applicable architecture and engineering authority.

## 2. Normative Language

The keywords **shall**, **shall not**, **should**, **should not**, and **may** are normative.

- **Shall** indicates a mandatory requirement.
- **Shall not** indicates a mandatory prohibition.
- **Should** indicates a recommended practice. A deviation requires an engineering reason.
- **Should not** indicates a discouraged practice.
- **May** indicates an allowed option.

Code examples and appendices are illustrative unless explicitly identified as normative. They are not required to form standalone buildable projects for document approval. Any example adopted into Product code shall be adapted, compiled, analyzed, and tested using the Project's controlled toolchain.

## 3. Scope

This document applies to Product-owned:

- C# application code.
- Libraries.
- Services.
- Desktop applications.
- Test tools.
- Manufacturing tools.
- Communication components.
- Protocol integration.
- Unit and integration tests.
- Build utilities written in C#.

It also defines boundaries for:

- Generated C# code.
- Third-party C# code.
- Designer-generated UI code.
- Native interop declarations.

## 4. Exclusions

This document does not require rewriting:

- Third-party source.
- Vendor SDK source.
- Generated Protocol code.
- UI designer-generated files.
- Migration-generated database files.

Excluded code shall be isolated and identifiable. Product-owned integration code remains subject to this document.

## 5. Authority and Precedence

The following precedence shall apply:

1. Applicable product, safety, security, and regulatory requirements.
2. Approved software requirements and architecture.
3. The applicable system or role framework, including `Coordinator_Node_Control_Framework.md` when relevant.
4. The approved Project Protocol when Protocol behavior is in scope.
5. The applicable software engineering rules, including `Coordinator_Software_Engineering_Rules.md` when the code implements or supports a Coordinator role.
6. This document.
7. Project-local C# profile.
8. Tool defaults and personal preference.

This document shall not be used to weaken a higher-authority requirement.

Where this document restates a cross-language architecture, lifecycle, security, logging, testing, or release requirement, the owning engineering document remains authoritative. The repeated text defines the C# implementation realization and shall not become a competing authority.

## 6. Project C# Profile

Each C# project shall document:

- Target framework.
- Runtime.
- C# language version.
- Compiler and IDE version.
- Nullable reference type policy.
- Supported operating systems.
- UI or service framework.
- Analyzer set.
- Warning policy.
- Package management and lock policy.
- Native dependencies.
- Generated-code locations.
- Test framework.
- Serialization technologies.
- Approved deviations.

Code shall not use a language or runtime feature merely because the developer's IDE supports it. The feature shall be supported by the declared build toolchain and target runtime.

## 7. Stable Document Identity

The maintained filename shall remain:

```text
CSharp_Coding_Rules.md
```

Document versions shall be stored in metadata, Version History, Git history, tags, releases, or controlled archives.

---

# Part II — Source Organization and Formatting

## 8. Source File Responsibility

A source file should contain one primary type.

Additional private or tightly coupled helper types may share a file when this improves locality and does not obscure ownership.

Large unrelated types shall not share a source file.

The filename should match the primary type name.

## 9. Namespace Organization

Namespaces shall represent stable product, subsystem, and feature ownership.

A recommended pattern is:

```text
<Organization>.<Product>.<Subsystem>[.<Feature>]
```

Namespace names shall not reflect temporary team names, personal names, or physical folder accidents.

Namespaces shall use PascalCase.

## 10. Using Directives

Using directives shall be:

- Required by the file.
- Kept in a consistent project-defined location.
- Free of duplicates.
- Free of unused entries.
- Ordered by the enforced formatter or analyzer policy.

Namespace aliases may be used to resolve ambiguity or improve clarity at an interop boundary.

Global using directives shall be used only when supported by the target toolchain and when they improve the whole project rather than hide dependencies.

## 11. Formatting Authority

Formatting shall be controlled by an `.editorconfig`, formatter, or equivalent checked-in configuration.

Source formatting shall not depend on an individual developer's IDE settings.

The baseline shall use:

- Four spaces per indentation level.
- Spaces, not tab characters.
- One statement per line.
- Braces for multi-line and nested control flow.
- A consistent Project-wide policy for simple single-line control flow.
- Consistent brace placement.
- A final newline.
- UTF-8 encoding.
- No trailing whitespace, except intentional Markdown hard line breaks in documentation files.

A project may select a different formatting rule only through an explicit project profile. Mixed personal formatting styles within the same Project are prohibited.

## 12. Line Length

Lines should remain reasonably readable in review tools.

A project should select a soft line-length target. Long lines may be retained when breaking them would reduce clarity, such as:

- Long identifiers required by an external API.
- URLs in documentation.
- Generated code.
- Tables or test data.
- Log message templates where splitting harms readability.

## 13. Braces

Braces shall be used for multi-line and nested `if`, `else`, `for`, `foreach`, `while`, and `do` bodies.

The baseline recommendation is to use braces for simple single-line bodies as well. A Project profile may permit omission for simple single-line bodies when the rule is enforced consistently by formatting or analysis tools.

Nested control flow without braces is prohibited.

Empty blocks shall contain an explanatory comment or shall be removed.

## 14. Comments

Comments shall explain:

- Intent.
- Constraints.
- Non-obvious behavior.
- Safety or security rationale.
- Protocol or hardware assumptions.
- Workarounds.
- Ownership or lifecycle rules.

Comments shall not merely restate the code.

Commented-out code shall not remain in maintained source. Version control is the history mechanism.

`TODO` and `FIXME` comments shall include a trackable issue, owner, or removal condition when used in controlled Product code.

## 15. XML Documentation

Public APIs, shared internal frameworks, generated extension points, and non-obvious interfaces should use XML documentation.

Documentation shall describe behavior and contract, not only repeat the member name.

Documentation shall identify applicable:

- Units.
- Ranges.
- Threading behavior.
- Ownership.
- Exceptions.
- Cancellation.
- Null behavior.
- Side effects.
- Version limitations.

---

# Part III — Naming

## 16. General Naming

Names shall communicate domain meaning.

Abbreviations shall be avoided unless they are standard in the Project domain.

Single-letter names are permitted only for narrow, conventional scopes such as simple indices or mathematical expressions.

Names shall not encode type information through Hungarian notation.

## 17. Capitalization

The baseline naming rules are:

| Item | Convention | Example |
|---|---|---|
| Namespace | PascalCase | `Product.Communication` |
| Class | PascalCase | `DeviceSession` |
| Struct | PascalCase | `SamplePoint` |
| Interface | `I` + PascalCase | `ITransport` |
| Enum type | PascalCase | `ConnectionState` |
| Enum member | PascalCase | `Connecting` |
| Method | PascalCase | `ConnectAsync` |
| Property | PascalCase | `IsConnected` |
| Event | PascalCase | `ConnectionChanged` |
| Public mutable field | Prohibited | — |
| Public `const` or `readonly` field | PascalCase; use only when field semantics are intentionally part of the API | `MaximumRetryCount` |
| Parameter | camelCase | `cancellationToken` |
| Local variable | camelCase | `responseFrame` |
| Private instance field | `_` + camelCase | `_transport` |
| Private static field | `s_` + camelCase | `s_defaultTimeout` |
| Constant | PascalCase | `MaximumRetryCount` |
| Type parameter | `T` or descriptive `T` prefix | `TMessage` |

A project may adopt another private-field convention only when enforced consistently.

A field that is assigned only during construction or initialization should be marked `readonly` when practical. A public `const` value shall be used only when it is a stable compile-time contract and the versioning effect has been reviewed.

## 18. Boolean Names

Boolean names shall read as predicates or conditions.

Preferred prefixes include:

- `Is`
- `Has`
- `Can`
- `Should`
- `Was`
- `Requires`
- `Supports`

Examples:

```csharp
bool isConnected;
bool hasPendingRequest;
bool canRetry;
bool supportsFirmwareUpdate;
```

Ambiguous names such as `statusFlag`, `check`, or `value` shall not be used.

## 19. Async Names

Methods returning `Task`, `Task<T>`, or an equivalent asynchronous result shall end with `Async`, except framework-required event handlers or interface contracts that prohibit renaming.

Examples:

```csharp
Task ConnectAsync(CancellationToken cancellationToken);
Task<Response> SendRequestAsync(Request request, CancellationToken cancellationToken);
```

A synchronous method shall not use the `Async` suffix.

## 20. Event Names

Events shall use names that describe what changed or occurred.

Event handler delegates should use the conventional `sender` and `e` parameter names when using .NET event patterns.

Events that describe a completed action should use past tense when practical, such as:

```text
ConnectionChanged
UpdateCompleted
ConfigurationSaved
```

## 21. Unit and Representation Names

A value with a physical unit or representation that is not carried by its type shall include the unit in its name.

Examples:

```csharp
int timeoutMilliseconds;
double pressureMmHg;
long timestampMicroseconds;
int sampleRateHz;
```

A unit suffix shall not be appended when a domain type already encodes the unit.

## 22. Collection Names

Collection names should be plural.

A dictionary name should identify both meaning and indexing relationship when not obvious.

Examples:

```csharp
IReadOnlyList<DeviceInfo> devices;
Dictionary<uint, PendingRequest> requestsByCorrelationId;
```

---

# Part IV — Types, Accessibility, and Object Design

## 23. Accessibility

The narrowest practical accessibility shall be used.

Types and members shall not be made public merely to simplify testing.

`internal` should be preferred for implementation types that do not form a supported external API.

Public API expansion requires review because it creates compatibility obligations.

## 24. Classes and Structs

Classes shall be used for identity, polymorphism, mutable lifecycle, or larger objects.

Structs shall be used only when value semantics are intended.

A struct should be:

- Small.
- Immutable or effectively immutable.
- Free of complex resource ownership.
- Safe to copy.
- Explicit about default value behavior.

Large mutable structs are prohibited.

## 25. Sealed Types

Classes not designed for inheritance should be `sealed`, especially when:

- Invariants depend on constructor control.
- Methods are not designed as extension points.
- The type owns resources.
- Inheritance would complicate equality or thread safety.

Inheritance shall not be used only to share implementation.

## 26. Interfaces

Interfaces shall represent a coherent capability or boundary.

An interface shall not become a miscellaneous collection of unrelated methods.

Interfaces should remain small enough to support focused substitution and testing.

Versioning impact shall be considered before adding members to a public interface.

## 27. Immutability

Immutable data should be preferred for:

- Protocol messages.
- Configuration snapshots.
- Domain value objects.
- Events.
- Cross-thread messages.
- Test vectors.

Mutable shared state shall require explicit ownership and synchronization.

## 28. Constructors

Constructors shall establish a valid object invariant or fail clearly.

Constructors shall not perform long-running I/O, connect to devices, start unowned background work, or hide recoverable external operations.

Dependencies required for correct operation shall be explicit.

Optional behavior shall not be activated through ambiguous Boolean constructor parameters. Use an options type, factory, or named method.

## 29. Static State

Mutable global static state is prohibited unless justified as process-wide infrastructure with controlled initialization, ownership, synchronization, and shutdown.

Static helper methods may be used for stateless deterministic operations.

A singleton shall not be introduced merely to avoid dependency passing.

## 30. Partial Types

Partial types should be limited to:

- Designer-generated UI code.
- Generated code.
- Framework-required generation patterns.
- Large mechanically separated definitions with clear ownership.

Partial types shall not be used to scatter ordinary business logic across files.

---

# Part V — Variables, Constants, and Arithmetic

## 31. Variable Scope

Variables shall be declared in the narrowest practical scope.

A variable shall not be reused for unrelated meanings.

A local variable shall be initialized before use.

Long methods with many mutable locals should be refactored.

## 32. `var`

`var` may be used when the type is evident from the right-hand side or when the exact generic type would reduce readability.

Examples:

```csharp
var session = new DeviceSession(transport);
var devices = await discovery.FindDevicesAsync(cancellationToken);
```

An explicit type should be used when it communicates domain meaning, avoids ambiguity, or prevents an unintended type.

`var` shall not be used to hide numeric type, signedness, nullability, or a surprising API return type.

## 33. Built-In Type Keywords

C# keywords should be used for built-in types in source code:

```csharp
string
int
bool
object
```

Framework type names may be used when referring to static members or when required for clarity.

## 34. Constants and Magic Values

Numeric or string values with application, Protocol, timing, range, state, error, unit, buffer, test, or security meaning shall be represented by:

- Named constants.
- Enumerations.
- Typed options.
- Value objects.
- Configuration items.

Direct numeric result codes are prohibited. Use a named result or status type.

Simple literals such as `0`, `1`, `-1`, empty string, or common loop increments may be used when their meaning is obvious and not domain-specific.

## 35. Checked Arithmetic

Arithmetic involving:

- External input.
- Protocol lengths.
- Buffer sizes.
- Indices.
- Time conversions.
- Financial values.
- Physical scaling.
- Counters that influence behavior.

shall be reviewed for overflow, underflow, truncation, and precision loss.

A `checked` context or explicit range validation shall be used where overflow must not wrap silently.

Intentional unchecked arithmetic shall be isolated and documented.

## 36. Numeric Conversion

Narrowing conversions shall be explicit.

A cast shall not be used as a substitute for range validation.

Floating-point to integer conversion shall define rounding behavior.

Unit conversion shall define:

- Input unit.
- Output unit.
- Precision.
- Rounding.
- Valid range.
- Overflow behavior.

## 37. Floating-Point Comparison

Floating-point values shall not be compared for exact equality when approximate measurement or calculation is intended.

Comparison shall use a documented tolerance appropriate to the domain.

Exact comparison may be used when values are known to be exact encoded states and the rationale is clear.

## 38. Decimal Type

`decimal` should be used when base-10 precision is required, such as certain financial or user-entered decimal quantities.

`double` should be used for scientific, signal, or measurement computations unless requirements specify otherwise.

Type choice shall be intentional.

---

# Part VI — Nullability and Optional Values

## 39. Null Policy

Each project shall define whether nullable reference type analysis is enabled.

When the selected target and toolchain support nullable reference types, new projects should enable them.

When nullable analysis is unavailable, null contracts shall be expressed through validation, documentation, annotations supported by the toolchain, and tests.

## 40. Null as Meaning

`null` shall represent an explicit and documented condition.

`null` shall not be used interchangeably to mean:

- Not initialized.
- Not found.
- Invalid.
- Disconnected.
- Empty.
- Error.
- Not applicable.

Use a result type, empty collection, state enum, or explicit optional model when those meanings differ.

## 41. Null Validation

Public and boundary-facing methods shall validate required reference arguments.

Argument validation shall occur before side effects.

Repeated null checks may be centralized in constructors, factories, or validated value objects.

## 42. Null-Forgiving Operator

The null-forgiving operator (`!`) shall be used only when the developer can prove the value is non-null and the proof is not expressible to the compiler.

Its use shall be narrow and reviewable.

It shall not be used to silence widespread nullable warnings.

## 43. Empty Collections

Methods should return empty collections rather than `null` when no items is a valid result.

Collections returned to callers should express whether mutation is allowed.

---

# Part VII — Methods, Properties, and APIs

## 44. Method Responsibility

A method shall perform one coherent operation at one abstraction level.

A method should be refactored when it combines:

- UI manipulation.
- Protocol construction.
- Transport I/O.
- Domain decisions.
- Persistence.
- Error presentation.

Method length alone is not the primary criterion; responsibility and testability are.

## 45. Parameters

Parameter lists shall remain understandable.

When multiple parameters share the same primitive type and can be confused, use:

- A value object.
- An options type.
- Named arguments.
- A builder.
- Separate methods.

Boolean parameters that switch major behavior should be replaced by an enum or options type.

## 46. Optional Parameters

Optional parameter defaults form part of the calling contract.

They shall be stable and safe.

Optional parameters shall not be used to hide required configuration.

## 47. Return Values

A method shall return a value that communicates the complete immediate result of the operation.

A Boolean return shall be used only when true/false fully describes the outcome.

When failure reasons or recovery decisions matter, use:

- A typed result.
- An enum status plus data.
- An exception for exceptional failure.
- A discriminated-result pattern supported by the Project.

## 48. Properties

Properties shall represent values, not long-running actions.

A property getter shall not:

- Perform blocking I/O.
- Connect to a device.
- Start a workflow.
- Have a surprising side effect.
- Throw ordinary operational errors due to external availability.

Expensive or fallible operations shall use methods.

## 49. Setters

Public setters shall preserve object invariants.

A property requiring complex validation, I/O, or state transition should be replaced by a method with an explicit result.

## 50. Method Overloads

Overloads shall behave consistently.

Overloads shall not change the semantic meaning of an operation based on subtle type conversion.

Ambiguous overloads shall be avoided.

## 51. Extension Methods

Extension methods shall be used when they provide a natural operation on the extended type without claiming ownership of private state.

They shall not be used to hide major dependencies or global side effects.

## 52. Equality

Types with value semantics shall define equality consistently.

When overriding `Equals`, the implementation shall consider:

- `GetHashCode`.
- Equality operators.
- Mutability.
- Inheritance.
- Null.
- Collection behavior.

Mutable fields used in hash codes are prohibited while an object may be used as a dictionary key.

---

# Part VIII — Collections, LINQ, and Enumeration

## 53. Collection Interfaces

APIs should expose the least powerful collection contract that meets caller needs.

Examples:

- `IReadOnlyList<T>` for ordered read-only access.
- `IEnumerable<T>` for sequence enumeration.
- `ICollection<T>` when mutation is required.
- Concrete types when concrete behavior is part of the contract.

A mutable collection shall not be exposed when callers should not modify it.

## 54. Enumeration Behavior

An API returning deferred execution shall document or make obvious:

- When work occurs.
- Whether enumeration may fail.
- Whether enumeration can be repeated.
- Whether results can change.
- Whether external resources remain open.

Materialize a sequence when a stable snapshot is required.

## 55. LINQ

LINQ should be used when it improves clarity.

LINQ shall not be used to hide:

- Multiple enumeration of expensive sources.
- Side effects.
- Blocking I/O.
- Large intermediate allocation.
- Order-dependent mutation.
- Complex error handling.

A loop should be preferred when control flow, allocation, or diagnostic behavior is clearer.

## 56. Multiple Enumeration

An `IEnumerable<T>` shall not be enumerated multiple times unless the source is known to support it safely and efficiently.

Materialize or redesign when repeated enumeration is required.

## 57. Dictionary Access

Dictionary lookup shall use the method appropriate to expected behavior.

`TryGetValue` should be used when absence is an expected condition.

Indexer access may be used when absence is a programming defect or already validated.

## 58. Concurrent Collections

Concurrent collections do not eliminate the need to define atomic behavior across multiple operations.

Check-then-act sequences shall use an atomic API or explicit synchronization.

---

# Part IX — Strings, Culture, Time, and Paths

## 59. String Comparison

String comparisons shall specify the intended comparison semantics.

Use ordinal comparison for:

- Protocol tokens.
- Identifiers.
- File-format keys.
- Security-sensitive comparisons where constant-time behavior is not separately required.
- Machine-generated values.

Use culture-aware comparison only for user-facing linguistic behavior.

## 60. String Formatting

User-facing formatting shall use the intended culture.

Logs, Protocol text, configuration, and machine-readable export should use invariant culture unless a format explicitly defines another culture.

Format strings shall not be assembled from untrusted input.

## 61. Parsing

Parsing of external or persisted values shall define:

- Culture.
- Number style.
- Valid range.
- Failure behavior.
- Unit.
- Empty-input behavior.

A parsing failure shall not silently become zero, false, current time, or another valid value.

## 62. Time Representation

The code shall distinguish:

- UTC timestamp.
- Local display time.
- Monotonic duration.
- Node time.
- Coordinator time.
- Unknown time.

Persisted absolute time should use UTC.

Elapsed time and timeout measurement shall use a monotonic source such as `Stopwatch`, not `DateTime.Now`.

## 63. `DateTime` and `DateTimeOffset`

`DateTimeOffset` should be preferred for an absolute point in time when an offset is relevant.

`DateTime` shall have a known `Kind` when interpreted as UTC or local time.

Unspecified `DateTime` values shall not be silently assumed to be UTC.

## 64. File and Directory Paths

Paths shall be constructed with platform path APIs rather than manual separator concatenation.

User-supplied paths shall be validated.

Import and extraction code shall prevent path traversal.

Code shall define behavior for:

- Missing directory.
- Existing file.
- Access denied.
- Read-only media.
- Long path.
- Disk full.
- Interrupted write.

---

# Part X — Enums and Flags

## 65. Enum Use

Enums shall be used for a closed set of named states or options.

An enum shall not be assumed valid merely because its underlying integer type can hold a value.

External enum values shall be validated.

## 66. Enum Zero Value

The zero value should represent a valid safe default such as:

- `None`
- `Unknown`
- `Unspecified`
- `Disconnected`

A zero value that accidentally means a dangerous active state is prohibited.

## 67. Flags Enums

A flags enum shall:

- Use `[Flags]`.
- Assign powers of two to independent flags.
- Define `None = 0`.
- Define combinations only when the combination has stable domain meaning.
- Validate unknown or reserved bits at external boundaries.

## 68. Protocol Enums

Protocol enums shall be generated or derived from the authoritative Protocol definition.

Product-owned code shall not independently renumber Protocol enum values.

---

# Part XI — Errors, Exceptions, and Results

## 69. Exception Policy

Exceptions shall represent exceptional failure, contract violation, or inability to complete an operation as designed.

Exceptions shall not be used for ordinary state-machine branching or expected high-frequency conditions.

## 70. Catching Exceptions

Catch the most specific exception that can be handled meaningfully.

A catch block shall:

- Recover.
- Convert to a typed higher-level failure.
- Add diagnostic context and rethrow.
- Transition state safely.
- Terminate the operation.

Empty catch blocks are prohibited.

Catching `Exception` is permitted only at an intentional boundary, such as:

- Process top level.
- Background-work supervisor.
- Plugin boundary.
- Operation boundary that converts all failures to a defined result.

## 71. Rethrowing

Use:

```csharp
throw;
```

to preserve the original stack trace.

Using:

```csharp
throw exception;
```

to rethrow the same exception is prohibited.

## 72. Exception Context

When wrapping an exception, preserve the original exception as `InnerException`.

The new exception shall add meaningful abstraction-level context without exposing secrets.

## 73. User Messages

User-facing messages shall be separated from engineering diagnostics.

An exception message shall not be shown directly to the user when it may expose sensitive, internal, or confusing information.

## 74. Argument Exceptions

Use appropriate argument exceptions for public contract violations.

Parameter names shall be included through language-supported mechanisms.

Argument validation shall occur before side effects.

## 75. Result Types

A typed result should be used when the caller needs to distinguish expected outcomes without exception control flow.

A result type should identify:

- Success or failure.
- Failure category.
- Optional value.
- Diagnostic detail.
- Recoverability when needed.

## 76. Cleanup

Cleanup shall occur through `using`, `finally`, or owned disposal.

A catch block shall not duplicate cleanup that belongs to deterministic resource management.

---

# Part XII — Asynchronous Programming and Cancellation

## 77. Task-Based Pattern

Asynchronous APIs shall use the Task-based asynchronous pattern when supported by the selected target.

Asynchronous methods shall return:

- `Task`
- `Task<T>`
- Another project-approved awaitable type

`async void` is prohibited except for framework-required event handlers.

## 78. Async All the Way

Code shall not block on a Task using:

- `.Wait()`
- `.Result`
- `.GetAwaiter().GetResult()`

in UI, service request, or normal asynchronous paths.

Blocking may be used only at a carefully controlled synchronous boundary with a documented deadlock and exception analysis.

## 79. I/O and `Task.Run`

`Task.Run` shall not be used merely to wrap naturally asynchronous I/O.

`Task.Run` may be used for CPU-bound work when:

- Work is sufficiently expensive.
- Thread-pool use is acceptable.
- Cancellation and progress are defined.
- The caller owns the operation.

## 80. CancellationToken

A long-running or externally waiting asynchronous operation shall accept a `CancellationToken` when cancellation is meaningful.

The token should be the final required parameter, before optional parameters if necessary.

Methods shall pass the token to cancellable dependencies.

A method shall not create an unrelated token internally that prevents caller cancellation.

## 81. Cancellation Semantics

Cancellation shall be distinguished from failure.

A cancelled operation shall not be logged as an unexpected error unless cancellation itself indicates a defect.

Partial side effects shall be documented and safely handled.

## 82. Timeout

Timeout shall be implemented as policy, not scattered literal delays.

Timeout and user cancellation shall remain distinguishable when the distinction matters.

Timeout handling shall clean up pending request correlation and workflow state.

## 83. Async Event Handlers

An `async void` event handler shall:

- Contain a top-level exception boundary appropriate to the UI framework.
- Delegate work to a testable `Task`-returning method.
- Prevent duplicate execution when required.
- Handle cancellation and closing state.
- Avoid leaving the UI in a permanent busy state.

## 84. `ConfigureAwait`

Application UI code may rely on the captured context where required to update UI state.

Reusable library code may use `ConfigureAwait(false)` when it does not require the caller's context and when supported by the selected target and project policy.

A project shall not apply `ConfigureAwait(false)` mechanically without understanding context requirements.

## 85. Fire-and-Forget

Unobserved fire-and-forget Tasks are prohibited.

Background work shall be registered with an owner or supervisor that:

- Observes exceptions.
- Supports cancellation.
- Participates in shutdown.
- Records failure.
- Prevents duplicate ownership.

## 86. Async Disposal

Async disposal may be used when supported by the target framework and when cleanup requires asynchronous work.

Projects targeting frameworks without async disposal shall provide an explicit owned shutdown method and deterministic synchronous disposal for local resources.

---

# Part XIII — Threading and Synchronization

## 87. Thread Ownership

Every created thread, task loop, timer, and callback source shall have an owner.

The owner shall define start, stop, cancellation, exception observation, and disposal.

## 88. Shared State

Mutable shared state shall be minimized.

Preferred approaches include:

- Immutable messages.
- Single-thread ownership.
- Actor or queue ownership.
- Snapshot publication.
- Focused synchronization.

## 89. Lock Objects

`lock` shall use a private dedicated reference object.

The following are prohibited lock targets:

- `this`
- `typeof(SomeType)`
- Publicly accessible objects.
- Strings.
- Interned values.

## 90. Lock Scope

Lock scope shall be minimal.

Code inside a lock shall not perform:

- Blocking device I/O.
- Network I/O.
- User callbacks.
- UI dispatch.
- Long computation.
- Await.

## 91. Lock Ordering

When multiple locks are unavoidable, lock ordering shall be documented and consistent.

Nested locking should be avoided.

## 92. Volatile and Interlocked

`volatile` shall not be treated as a general thread-safety mechanism.

`Interlocked` operations shall be used for supported atomic operations when they express the complete required behavior.

Multi-step invariants require a stronger design.

## 93. UI Thread Affinity

UI controls shall be accessed only from the UI thread according to framework rules.

Communication callbacks shall publish data to application state or a UI dispatch boundary; they shall not manipulate controls directly.

## 94. Timers

Timer selection shall match the required execution context.

The design shall define:

- Callback thread.
- Overlap behavior.
- Disposal.
- Shutdown.
- Drift.
- Exception handling.

A periodic callback shall not overlap unless explicitly designed to do so.

## 95. Thread Termination

Forced thread termination is prohibited.

`Thread.Abort` shall not be used.

Threads and Tasks shall terminate cooperatively.

---

# Part XIV — Events, Delegates, and Callbacks

## 96. Event Ownership

The publisher owns the event.

Subscribers own their subscription lifecycle unless a higher-level component explicitly manages it.

Long-lived publishers and short-lived subscribers shall define unsubscription to prevent leaks.

## 97. Event Data

Event arguments shall be immutable or treated as immutable.

An event shall not expose mutable internal collections or implementation state.

## 98. Event Exceptions

A publisher shall define how subscriber exceptions are handled.

A subscriber exception shall not silently prevent critical remaining subscribers unless that behavior is intentional.

## 99. Callbacks

A callback contract shall define:

- Thread or context.
- Reentrancy.
- Lifetime.
- Exception behavior.
- Ordering.
- Whether blocking is allowed.

Unknown external callbacks shall not be invoked while holding a lock.

## 100. Weak Events

Weak-event patterns may be used when required by a UI framework or lifecycle design, but shall not substitute for clear ownership.

---

# Part XV — Resource Management

## 101. IDisposable

A type that owns an `IDisposable` resource shall normally implement deterministic cleanup directly or through an owned disposable component.

Disposable ownership shall be explicit.

Receiving an `IDisposable` parameter does not automatically transfer ownership.

## 102. `using`

Resources with lexical lifetime shall use `using` or an equivalent `try/finally`.

A resource shall not be disposed while asynchronous work still uses it.

## 103. Dispose Pattern

The full dispose pattern with finalization shall be used only when directly owning unmanaged resources.

Types that own only managed disposable objects normally do not require a finalizer.

Finalizers shall be rare and reviewed.

## 104. Idempotent Disposal

`Dispose` should be safe to call more than once.

Public methods invoked after disposal shall behave consistently, normally by throwing `ObjectDisposedException` when the operation is invalid.

## 105. Event and Timer Cleanup

Disposal shall stop and release owned:

- Timers.
- Cancellation token sources.
- Event subscriptions.
- Device handles.
- Streams.
- Sockets.
- Native handles.
- Background loops.

## 106. Memory Streams and Buffers

Buffer ownership shall be explicit.

A pooled buffer shall be returned exactly once and shall not be used after return.

A caller shall not retain a reference to mutable internal storage unless the contract explicitly transfers ownership.

---

# Part XVI — UI Framework Integration

## 107. UI Event Handlers

UI event handlers shall remain thin.

They shall:

- Capture user intent.
- Perform presentation-level validation.
- Invoke an Application-layer operation.
- Reflect progress and result.
- Handle cancellation and user-facing errors.

They shall not encode Protocol frames, own transports, or contain product state machines.

## 108. Busy State

A long-running UI operation shall define:

- Busy indication.
- Disabled conflicting actions.
- Cancellation.
- Progress.
- Error recovery.
- Window-close behavior.
- Prevention of duplicate submission.

Busy state shall be cleared in a guaranteed completion path.

## 109. Data Binding and View State

View state shall be separated from authoritative device state.

Data binding shall not create hidden write paths into domain state.

Transformation between domain and presentation models should be explicit.

## 110. High-Rate Display

High-rate measurement data shall be sampled, batched, or buffered for display.

UI rendering frequency shall be decoupled from acquisition frequency.

The UI shall not enqueue an unbounded number of pending updates.

## 111. Modal Dialogs

Modal dialogs shall not be used as the primary error-handling architecture.

A dialog shall not block a required background recovery or shutdown path.

## 112. Form and Window Lifetime

Window closure shall unsubscribe events and release owned resources.

Closing one view shall not dispose shared application services unless that view owns them.

## 113. WinForms Designer Code

Designer-generated files shall not contain manually maintained business logic.

Manual code shall remain in the non-designer partial class or separate components.

Designer-generated files shall be treated as generated code.

---

# Part XVII — Serialization, Protocol, and Interop

## 114. Serialization Authority

Serialized data shall have a defined schema and version.

Serialization shall not depend accidentally on private field names, reflection order, current culture, or runtime-specific default behavior.

## 115. Binary Serialization

Insecure or runtime-coupled object serialization mechanisms shall not be used for untrusted or long-lived persisted data.

`BinaryFormatter` shall not be introduced.

Existing use shall have a removal or isolation plan.

## 116. Protocol Encoding

Protocol encoding and decoding shall:

- Use explicit integer widths.
- Define endianness.
- Validate lengths before allocation or access.
- Validate enum values and reserved bits.
- Reject malformed input.
- Avoid culture-sensitive conversion.
- Preserve field units and ranges.
- Follow the generated or authoritative Protocol definition.

## 117. Byte Buffers

Index and length arithmetic shall be range checked.

A slice or copy shall not exceed the validated record boundary.

Data from an external peer shall not control unbounded allocation.

## 118. Text Encoding

Text encoding shall be explicit at persistent and external boundaries.

Code shall not rely on the platform default encoding.

Invalid byte-sequence behavior shall be defined.

## 119. Native Interop

P/Invoke and native interop declarations shall explicitly define:

- Calling convention.
- Character set.
- Structure layout.
- Boolean representation.
- Integer width.
- Ownership.
- Error retrieval.
- Lifetime.
- Thread requirements.
- Native library version.

Interop structures shall have size and layout tests when compatibility is critical.

## 120. SafeHandle

`SafeHandle` or an equivalent safe ownership wrapper should be used for native handles.

Raw `IntPtr` ownership shall be isolated and reviewed.

---

# Part XVIII — Security Rules

## 121. Secrets

Secrets shall not be hard-coded in source.

Secrets shall not be placed in normal configuration, logs, exception messages, test snapshots, or command lines where exposure is possible.

## 122. Randomness

Security-sensitive randomness shall use a cryptographically secure random source approved for the target framework.

General-purpose pseudo-random generators shall not be used for keys, nonces, tokens, salts, or security challenges.

## 123. Cryptography

Custom cryptographic algorithms or protocols are prohibited.

Algorithm selection, key size, mode, nonce behavior, signature verification, and key derivation shall come from approved security requirements.

## 124. Authentication Failure

Authentication, integrity, replay, and authorization failures shall fail closed.

The code shall not continue in an unauthenticated mode unless that mode is an explicit approved Protocol state.

## 125. File and Package Validation

Files from outside the trust boundary shall be validated before use.

Firmware, update, plugin, or configuration packages shall be authenticated when required.

A hash alone shall not be treated as proof of trusted origin.

## 126. Sensitive Comparison

Secret or authentication values shall use an appropriate constant-time comparison when timing exposure is relevant.

Ordinary string equality is not sufficient for all secret comparisons.

## 127. Secure Defaults

Defaults shall not disable authentication, certificate validation, integrity checks, logging of security failure, or safe path handling.

Engineering bypasses shall be isolated, visibly identified, access controlled, and excluded from production release unless explicitly approved.

---

# Part XIX — Logging and Diagnostics

## 128. Logging API

Product-owned code shall use the project-approved logging abstraction.

Direct writes to console, debug output, or arbitrary files shall not replace the logging system in production code.

## 129. Structured Context

Logs should include structured properties where supported, such as:

- Component.
- Operation.
- Device identity.
- Session identity.
- Correlation identity.
- State.
- Error category.
- Retry count.
- Duration.
- Application version.

## 130. Exception Logging

An exception should be logged once at the boundary that owns the decision or failure.

Repeated logging at every rethrow level should be avoided unless each log adds necessary distinct evidence.

The full exception object shall be supplied to the logging system when appropriate.

## 131. Sensitive Logging

The following shall not be logged:

- Passwords.
- Private keys.
- Session keys.
- Access tokens.
- Unmasked credentials.
- Sensitive personal data.
- Full raw messages containing protected content.

Masking shall be deterministic and tested.

## 132. Log Message Quality

Log messages shall describe an event, not merely a variable.

Preferred:

```text
Device connection failed during Protocol negotiation.
```

Avoid:

```text
Error.
Failed.
Exception occurred.
```

## 133. Performance

High-rate paths shall avoid expensive log formatting when the level is disabled.

Per-sample logging is prohibited in production unless required and proven sustainable.

---

# Part XX — Performance and Allocation

## 134. Measure Before Optimization

Performance optimization shall be based on requirements, profiling, or measured evidence.

Readability and correctness shall not be sacrificed for speculative optimization.

## 135. Hot Paths

Hot paths shall be identified and reviewed for:

- Allocation.
- Copies.
- LINQ overhead.
- Boxing.
- Lock contention.
- String formatting.
- UI dispatch.
- Logging.
- Large-object heap pressure.
- Native transitions.

## 136. Allocation

Repeated large allocation in streaming or periodic paths shall be avoided.

Pooling may be used only with explicit ownership and return rules.

## 137. Boxing

Boxing in high-rate paths should be avoided when measurable.

Enum, value-type, logging, and non-generic collection usage shall be reviewed for accidental boxing.

## 138. Regular Expressions

Regular expressions shall have controlled complexity.

Patterns processing untrusted input shall consider denial-of-service risk and timeout support where available.

## 139. Caching

A cache shall define:

- Key.
- Capacity.
- Expiration.
- Invalidation.
- Thread safety.
- Memory impact.
- Failure behavior.

Unbounded static caches are prohibited.

---

# Part XXI — Reflection, Dynamic, Unsafe Code, and Generation

## 140. Reflection

Reflection shall be used only when its flexibility is required.

Reflection-based behavior shall define:

- Failure handling.
- Version sensitivity.
- Performance impact.
- Trimming or deployment impact when applicable.
- Security boundary.
- Test coverage.

## 141. `dynamic`

`dynamic` shall not be used to avoid type design.

It may be used at a controlled interop boundary when required by an external API.

The dynamic boundary shall be isolated and tested.

## 142. Unsafe Code

Unsafe code requires explicit project approval.

The approval shall define:

- Need.
- Scope.
- Memory ownership.
- Bounds handling.
- Lifetime.
- Pinning.
- Concurrency.
- Tests.
- Review owner.

Unsafe code shall be isolated.

## 143. Generated Code

Generated code shall:

- Be placed in identified generated locations.
- Include generator identity when practical.
- Be reproducible.
- Not be manually edited.
- Compile under the declared target.
- Be regenerated and checked in CI or an equivalent controlled process.
- Have handwritten extension points outside the generated file.

Warnings may be selectively suppressed for generated code only through a controlled configuration.

## 144. Designer Code

UI designer files are generated artifacts.

Business logic, device communication, and domain state shall not be added to designer files.

---

# Part XXII — Dependency Injection and Composition

## 145. Constructor Injection

Required dependencies should be supplied through constructor injection.

A constructor shall not accept a service provider and resolve arbitrary dependencies unless the type is the Composition Root or a framework-required factory boundary.

## 146. Optional Dependencies

Optional behavior should use:

- An explicit option.
- A no-op implementation.
- A feature interface.
- A factory.

A nullable service dependency shall not create unclear partial functionality.

## 147. Lifetime

Dependency lifetime shall match ownership.

Singleton services shall be thread-safe and shall not capture shorter-lived dependencies.

Disposable dependencies shall be disposed by the component or container that owns their lifetime.

## 148. Service Locator

The service-locator pattern is prohibited in ordinary Product-owned code.

Global static access to arbitrary services hides dependencies and impairs testing.

---

# Part XXIII — Testing Rules

## 149. Test Structure

Tests shall have clear arrangement, action, and assertion.

Test names shall communicate:

- Unit under test.
- Condition.
- Expected behavior.

A project shall use a consistent naming convention.

## 150. Deterministic Tests

Tests shall control:

- Time.
- Randomness.
- File locations.
- Culture.
- Environment.
- External services.
- Device transport.

Tests shall not depend on arbitrary sleeps when a deterministic signal is available.

## 151. Assertions

Assertions shall identify the expected behavior.

Multiple assertions are acceptable when they verify one coherent outcome.

A test shall not hide failure through broad exception catching.

## 152. Boundary Tests

Tests shall cover applicable:

- Null.
- Empty.
- Minimum.
- Maximum.
- Just below minimum.
- Just above maximum.
- Overflow.
- Invalid enum.
- Invalid encoding.
- Timeout.
- Cancellation.
- Duplicate.
- Reordered input.
- Partial input.
- Resource failure.

## 153. Async Tests

Async tests shall return `Task`.

Tests shall await the operation under test.

`async void` tests are prohibited.

## 154. Mocking

Mocking shall be focused on owned boundaries.

Simple value objects or framework details should not be mocked unnecessarily.

A fake or in-memory implementation may be clearer for stateful behavior.

## 155. Protocol Tests

Protocol tests shall use authoritative vectors and shall include cross-implementation interoperability where applicable.

Generated encoders and decoders shall be tested at boundary values.

## 156. UI Tests

UI tests shall not be the only tests for application logic.

UI event handlers shall delegate to testable methods or Application services.

---

# Part XXIV — Analyzers, Build, and Enforcement

## 157. `.editorconfig`

Each repository shall contain a checked-in `.editorconfig` or equivalent configuration.

It shall define at least:

- Indentation.
- Newline.
- Encoding.
- Trailing whitespace.
- C# formatting.
- Naming rules.
- `var` policy.
- Expression-body policy.
- Qualification policy.
- Analyzer severity where supported.

## 158. Compiler Warnings

Product-owned code shall build using the project-approved warning level.

New warnings shall be corrected or explicitly suppressed with justification.

Warning-as-error policy shall be selected according to toolchain compatibility and project maturity.

## 159. Analyzers

The project should enable compatible:

- .NET code-style analyzers.
- .NET code-quality analyzers.
- Security analyzers.
- Project-specific analyzers.
- StyleCop.Analyzers when adopted by the project.

Analyzer selection shall match the target framework and compiler.

## 160. Suppression

A suppression shall be narrow.

It shall identify:

- Rule.
- Scope.
- Reason.
- Review evidence when required.

Global suppression shall not be used to hide broad design problems.

## 161. Formatting in CI

CI or an equivalent controlled check should verify that source conforms to formatting rules.

Generated code may have a separate policy.

## 162. Dependency Audit

Package restore shall be reproducible.

Dependencies shall be reviewed for:

- License.
- Vulnerability.
- Maintenance.
- Compatibility.
- Transitive dependencies.
- Runtime and deployment impact.

---

# Part XXV — .NET Framework 4.7.2 and Visual Studio 2019 Profile

## 163. Applicability

This profile applies when the project declares:

```text
Target Framework: .NET Framework 4.7.2
Primary IDE/Toolchain: Visual Studio 2019-compatible
Default Language Baseline: C# 7.3
```

This profile supplements, but does not replace, the general rules.

The exact controlled Visual Studio, MSBuild, compiler, and analyzer versions shall be recorded by the Project when reproducible builds or regulated evidence require that precision.

## 164. Language Version

The default controlled language baseline for this profile is C# 7.3.

A newer C# language version may be used through an approved Project profile when the controlled build environment provides the compiler and the Project verifies:

- Target-runtime and reference-assembly compatibility.
- CI and developer-build reproducibility.
- Analyzer compatibility.
- Generated-code compatibility.
- Deployment behavior.

Code shall not rely on a newer developer-machine compiler unless the controlled build uses the same capability.

## 165. Nullable Reference Types

Nullable reference types are not part of the default C# 7.3 profile.

A Project may enable nullable reference type analysis through an approved newer-compiler profile. The Project shall then define the enabled scope, warning policy, annotation strategy, and treatment of legacy code.

Without nullable reference type analysis, the Project shall compensate through:

- Explicit argument validation.
- Clear null contracts.
- Annotations supported by the selected tools.
- Focused tests.
- Avoidance of multi-meaning null values.
- Static analysis where available.

## 166. Modern API Availability

Code shall not assume APIs available only in modern .NET.

Compatibility shall be verified against .NET Framework 4.7.2 reference assemblies and the Project's supported operating-system matrix.

A convenience API shall not be copied from an incompatible framework without reviewing behavior, license, maintenance, and semantic differences.

## 167. Async and UI

Task-based asynchronous programming should be used where supported.

WinForms or WPF UI thread affinity shall be respected.

`async void` remains limited to event handlers.

UI code shall not block on Task completion.

## 168. Disposal

Because several modern async-lifetime interfaces may not be available, components that require asynchronous shutdown shall expose an explicit `StopAsync` or `CloseAsync` operation.

Local resources shall be released after asynchronous work has stopped. If the component also implements `IDisposable`, its contract shall define whether `Dispose` performs a bounded synchronous shutdown or is valid only after asynchronous shutdown. `Dispose` shall not silently leave owned background work active.

The owning application shall follow the declared shutdown and disposal order.

## 169. Collections and APIs

Code shall use APIs available in the declared target.

Polyfills or compatibility packages shall be approved dependencies and shall not change public behavior silently.

## 170. Packaging

The release shall identify:

- Required .NET Framework version.
- Supported Windows versions according to the Project's approved platform matrix.
- Native runtime dependencies.
- Required device drivers.
- Installation privilege.
- Configuration and data locations.

Target-framework availability alone shall not be treated as proof that the complete application is supported on an operating system.

## 171. Migration Readiness

Legacy-target code should avoid unnecessary coupling to:

- Application-wide static state.
- Obsolete serialization.
- Framework-specific remoting.
- Unmaintained UI components.
- Direct registry dependency.
- Hard-coded installation paths.

Interfaces around platform and framework boundaries should permit future migration where economically justified.

---

# Part XXVI — AI-Assisted C# Engineering

## 172. Required Context

Before AI generates or modifies C# code, it shall be given or directed to:

- This document.
- `Coordinator_Software_Engineering_Rules.md`.
- The approved architecture.
- The target framework.
- C# language version.
- Existing project and solution structure.
- Approved packages.
- The Project Protocol.
- Generated-code boundaries.
- Test framework.
- Build and analyzer rules.

## 173. AI Prohibitions

AI-generated C# code shall not:

- Invent unsupported APIs.
- Upgrade the target framework silently.
- Add NuGet packages without approval.
- Put device communication in UI event handlers.
- Use unowned fire-and-forget Tasks.
- Block the UI thread.
- Swallow exceptions.
- Create unbounded queues.
- Hard-code secrets.
- Manually edit generated Protocol files.
- Use `dynamic`, reflection, unsafe code, or native interop without a stated need.
- Treat successful compilation as full validation.

## 174. AI Review Checklist

AI review shall inspect:

- Target-framework compatibility.
- Namespace and accessibility.
- Null contracts.
- Resource ownership.
- Event unsubscription.
- Timer and Task ownership.
- Cancellation.
- Timeout.
- Exception preservation.
- Thread affinity.
- Buffer bounds.
- Protocol range validation.
- Culture and time behavior.
- Sensitive logging.
- Analyzer suppression.
- Missing tests.

---

# Part XXVII — Conformance and Review

## 175. Deviation

A deviation shall record:

- Rule or section.
- Reason.
- Scope.
- Risk.
- Compensating control.
- Verification.
- Approver.
- Review or expiration condition when applicable.

## 176. Definition of Conformance

This section defines implementation conformance. It does not require every illustrative fragment in this document to form a standalone buildable project, and it does not define the approval status of this document itself.

C# code conforms only when:

- Mandatory rules are satisfied.
- Approved deviations are recorded.
- The controlled build succeeds.
- Required warnings and analyzers pass.
- Tests pass.
- Target-framework compatibility is verified.
- Architecture rules are satisfied.
- Human review is complete.

## 177. Code Review Checklist

### Structure and Naming

- [ ] File and type responsibility are clear.
- [ ] Names communicate domain meaning.
- [ ] Units are explicit where types do not carry them.
- [ ] Accessibility is minimal.
- [ ] Mutable static state is absent or justified.

### Types and Values

- [ ] Null meaning is explicit.
- [ ] Enum values are validated at boundaries.
- [ ] Numeric conversions are checked.
- [ ] Domain magic values are named.
- [ ] Collection mutability is intentional.

### Async and Concurrency

- [ ] Async methods use the `Async` suffix.
- [ ] `async void` is limited to event handlers.
- [ ] Tasks are awaited or supervised.
- [ ] Cancellation and timeout are propagated.
- [ ] UI thread is not blocked.
- [ ] Locks use private objects and have narrow scope.
- [ ] Timers and background loops have owners.

### Errors and Resources

- [ ] Exceptions are caught only where meaningful.
- [ ] Original stack traces are preserved.
- [ ] User and diagnostic messages are separated.
- [ ] Disposables have explicit owners.
- [ ] Events and timers are released.
- [ ] Shutdown is deterministic.

### Data and Security

- [ ] External data is validated.
- [ ] String comparison and parsing semantics are explicit.
- [ ] Time basis is correct.
- [ ] Secrets are not hard-coded or logged.
- [ ] Serialization is versioned.
- [ ] Protocol buffer bounds are validated.
- [ ] Native interop ownership is explicit.

### Quality Controls

- [ ] Target framework and language version are respected.
- [ ] No unapproved dependency was added.
- [ ] Analyzer suppressions are justified.
- [ ] Tests include boundaries and failures.
- [ ] Generated files were not manually edited.
- [ ] Architecture boundaries remain intact.

---

# Appendix A — Recommended C# Project Structure

```text
coordinator/
├── Product.Application/
├── Product.Domain/
├── Product.Presentation/
├── Product.Protocol/
│   ├── Generated/
│   └── Integration/
├── Product.Transport/
├── Product.Infrastructure/
├── Product.Security/
├── Product.Diagnostics/
├── Product.Configuration/
├── Product.Tests.Unit/
├── Product.Tests.Component/
└── Product.Tests.Integration/
```

The exact structure may differ. Responsibility boundaries are governed by `Coordinator_Software_Engineering_Rules.md`.

# Appendix B — Example Thin UI Handler

```csharp
private async void connectButton_Click(object sender, EventArgs e)
{
    try
    {
        await ExecuteConnectAsync(_userCancellationToken);
    }
    catch (Exception exception)
    {
        _logger.Error(exception, "Unexpected connection workflow failure.");
        _viewState.ShowConnectionFailure();
    }
}

private async Task ExecuteConnectAsync(CancellationToken userCancellationToken)
{
    if (_viewState.IsBusy)
    {
        return;
    }

    _viewState.IsBusy = true;

    using (var timeoutSource = new CancellationTokenSource(_connectTimeout))
    using (var linkedSource = CancellationTokenSource.CreateLinkedTokenSource(
        userCancellationToken,
        timeoutSource.Token))
    {
        try
        {
            ConnectResult result = await _deviceApplication
                .ConnectAsync(linkedSource.Token);

            _viewState.Apply(result);
        }
        catch (OperationCanceledException)
            when (timeoutSource.IsCancellationRequested &&
                  !userCancellationToken.IsCancellationRequested)
        {
            _viewState.ShowConnectionTimedOut();
        }
        catch (OperationCanceledException)
            when (userCancellationToken.IsCancellationRequested)
        {
            _viewState.ShowConnectionCancelled();
        }
        catch (DeviceConnectionException exception)
        {
            _logger.Error(exception, "Device connection failed.");
            _viewState.ShowConnectionFailure();
        }
        finally
        {
            _viewState.IsBusy = false;
        }
    }
}
```

This example illustrates delegation, timeout classification, external cancellation, and an exception boundary for an `async void` event handler. The Project shall define the actual cancellation owner, logging API, timeout policy, and user-interface behavior. The fragment is illustrative and shall be adapted and validated before Product use.

# Appendix C — Example Owned Background Loop

```csharp
internal sealed class ReceiveWorker
{
    private readonly object _lifecycleLock;
    private readonly ITransport _transport;

    private CancellationTokenSource _stopSource;
    private Task _runTask;
    private bool _closed;

    public ReceiveWorker(ITransport transport)
    {
        _transport = transport ?? throw new ArgumentNullException(nameof(transport));
        _lifecycleLock = new object();
    }

    public void Start()
    {
        lock (_lifecycleLock)
        {
            if (_closed)
            {
                throw new ObjectDisposedException(nameof(ReceiveWorker));
            }

            if (_runTask != null)
            {
                throw new InvalidOperationException("The receive worker is already started.");
            }

            _stopSource = new CancellationTokenSource();
            _runTask = RunAsync(_stopSource.Token);
        }
    }

    public async Task CloseAsync()
    {
        CancellationTokenSource stopSource;
        Task runTask;

        lock (_lifecycleLock)
        {
            if (_closed)
            {
                return;
            }

            _closed = true;
            stopSource = _stopSource;
            runTask = _runTask;

            if (stopSource != null)
            {
                stopSource.Cancel();
            }
        }

        try
        {
            if (runTask != null)
            {
                await runTask.ConfigureAwait(false);
            }
        }
        catch (OperationCanceledException)
            when (stopSource != null && stopSource.IsCancellationRequested)
        {
            // Expected during controlled shutdown.
        }
        finally
        {
            if (stopSource != null)
            {
                stopSource.Dispose();
            }
        }
    }

    private async Task RunAsync(CancellationToken cancellationToken)
    {
        while (true)
        {
            cancellationToken.ThrowIfCancellationRequested();
            await _transport.ReceiveAsync(cancellationToken).ConfigureAwait(false);
        }
    }
}
```

This example uses an explicit asynchronous close operation because the target profile does not assume `IAsyncDisposable`. The lifecycle owner shall call `CloseAsync` during controlled shutdown and shall observe any non-cancellation fault returned by the receive loop. A production implementation may add restart policy, state transitions, shutdown timeout, and diagnostic reporting according to the Project architecture.

# Appendix D — Minimum Tooling Baseline

A Project should evaluate and configure tools compatible with its target:

```text
.editorconfig
Compiler warnings
.NET code-style analyzers
.NET code-quality analyzers
StyleCop.Analyzers, when adopted
Unit-test framework
Coverage collection
Dependency and vulnerability review
CI formatting and generated-code checks
```

Tool availability varies by compiler and target framework. The Project profile shall record the enforced set.

# Appendix E — References

- `Coordinator_Software_Engineering_Rules.md`
- `Coordinator_Node_Control_Framework.md`
- The approved Project Protocol YAML and definition guide.
- Microsoft C# Coding Conventions.
- Microsoft Framework Design Guidelines.
- Microsoft C# asynchronous programming guidance.
- Microsoft .NET code-style and code-analysis documentation.
- Microsoft .NET Framework lifecycle and compatibility documentation.
- Documentation for the selected UI framework, target framework, compiler, analyzers, and test framework.

---

**End of Document**
