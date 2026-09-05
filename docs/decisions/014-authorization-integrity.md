# Decision 014 — Authorization Integrity Boundary

**Status:** Accepted

## Context

M22.8 introduced an explicit immutable `AuthorizationDecision` between policy/confirmation and execution. An authorization decision is necessary but not sufficient: the execution path must also verify that the decision still corresponds to the exact request being executed.

Without a separate integrity boundary, a valid authorization could be substituted, replayed against a different request, or otherwise detached from its original request identity.

## Decision

Introduce `AuthorizationIntegrityService` and `AuthorizationIntegrityResult` as the integrity boundary immediately before tool execution.

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

The integrity service deterministically fingerprints the request and authorization decision and verifies that the authorization is granted, names the same tool, carries the same invocation identity, and matches the stored integrity fingerprints.

`PolicyGate.invoke()` must verify authorization integrity before crossing into `ToolService`.

## Constraints

- `Authorization ≠ Authorization Integrity`
- `Authorization Integrity ≠ Execution`
- `Validated ToolRequest ≠ Authorized ToolRequest`
- `Authorization ≠ Permission`
- `Authorization ≠ Sandbox Admission`
- Request mutation must invalidate integrity.
- Decision substitution must invalidate integrity.
- Failed integrity must never reach `ToolService`.
- The integrity layer must not grant authorization or execute capabilities.

## Deliberate exclusions

M22.9 does not implement durable authorization storage, authorization revocation, expiration policy, distributed consensus, sandbox admission, worker assignment, or plugin execution.
