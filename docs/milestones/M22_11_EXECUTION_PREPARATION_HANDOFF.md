# M22.11 — Execution Preparation / Handoff

## Purpose

Establish the final non-executing boundary immediately before tool execution. A request may reach execution preparation only after explicit authorization, authorization integrity, and sandbox admission all succeed.

## Contract

- `ExecutionPreparationService` validates the exact upstream evidence chain.
- `ExecutionHandoff` is immutable and inspectable.
- Handoff preserves authorization identity, request fingerprint, decision fingerprint, sandbox profile identity, tool identity, invocation identity, and exact arguments.
- Tool and invocation identities must match across all upstream evidence.
- Failed preparation cannot reach `ToolService`.
- Preparation does not grant authority, permission, or authorization.
- Preparation does not assign a worker, activate containment, launch a process, or execute a plugin.

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
Sandbox Profile Resolution
        ↓
Sandbox Admission
        ↓
Execution Preparation / Handoff
        ↓
Execution
```

## Authority walls

```text
Sandbox Admission ≠ Execution Preparation
Execution Preparation ≠ Execution
Execution Preparation ≠ Worker Assignment
Execution Preparation ≠ Process Launch
Execution Preparation ≠ Containment Activation
Upstream authorization evidence ≠ fresh authorization
Preparation ≠ permission escalation
```

## Deliberate exclusions

M22.11 does not implement worker allocation, containment activation, process spawning, plugin execution, durable authorization storage, revocation, expiration, or an alternate bypass around `PolicyGate`.

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

M22.11 becomes VERIFIED / COMPLETE only after the user's local focused and regression receipt passes.
