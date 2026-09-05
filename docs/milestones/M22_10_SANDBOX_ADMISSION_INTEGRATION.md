# M22.10 — Sandbox Admission Integration

## Purpose

M22.10 connects the existing M22.5 sandbox admission contract to the post-authorization execution gate.

A request must be explicitly authorized, bound to that authorization through integrity verification, and admissible under a registered sandbox profile before `ToolService` can execute it.

## Contract

- `SandboxAdmissionService` consumes authorization, integrity, and the exact request.
- A granted authorization is never sufficient by itself to pass admission.
- A valid integrity result is never treated as sandbox admission.
- Tool definitions may declare `metadata["sandbox_profile_id"]`.
- Requests without a declared profile use the explicit deterministic `default` profile.
- Unknown profiles are rejected before execution.
- `PolicyGate.invoke()` blocks on failed sandbox admission.
- Successful admission remains metadata-only and does not activate containment or execution.

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
```

## Authority walls

```text
Authorization ≠ Sandbox Admission
Authorization Integrity ≠ Sandbox Admission
Sandbox Admission ≠ Execution
Sandbox Profile ≠ Permission
Sandbox Admission ≠ Worker Assignment
Sandbox Admission ≠ Containment Activation
```

## Deliberate exclusions

M22.10 does not launch processes, activate containment, assign workers, perform execution handoff, execute plugins, persist authorization, implement revocation, or implement expiration policy.

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

M22.10 becomes VERIFIED / COMPLETE only after the user's local focused and regression receipt passes.
