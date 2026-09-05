# M22.9 — Authorization Integrity

## Purpose

M22.9 establishes the integrity boundary between an explicit `AuthorizationDecision` and execution.

Authorization proves that a request was permitted. Authorization integrity proves that the authorization still belongs to the exact request about to execute.

## Contract

- `AuthorizationIntegrityService` produces deterministic integrity fingerprints for a request and its authorization decision.
- `AuthorizationIntegrityResult` is immutable and inspectable.
- Integrity is valid only when the authorization is granted, tool identity matches, invocation identity matches, and fingerprints verify.
- Request argument or metadata mutation invalidates integrity.
- Authorization decision substitution invalidates integrity.
- `PolicyGate.invoke()` verifies integrity before delegating to `ToolService`.
- Integrity verification never grants authorization and never executes a tool.

## Boundary

```text
Validated ToolRequest
        ↓
Policy
        ↓
Confirmation
        ↓
AuthorizationDecision
        ↓
Authorization Integrity
        ↓
Sandbox
        ↓
Execution
```

## Authority walls

```text
Authorization ≠ Authorization Integrity
Authorization Integrity ≠ Execution
Validated ToolRequest ≠ Authorized ToolRequest
Authorization ≠ Permission
Authorization ≠ Sandbox Admission
```

## Deliberate exclusions

M22.9 does not implement durable authorization storage, revocation, expiration policy, distributed consensus, worker assignment, sandbox admission, or plugin execution.

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

M22.9 becomes VERIFIED / COMPLETE only after the user's local focused and regression receipt passes.
