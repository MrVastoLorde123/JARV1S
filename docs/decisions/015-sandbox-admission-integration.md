# Decision 015 — Sandbox Admission Integration

## Status
Accepted for M22.10.

## Context
M22.5 defines the sandbox profile and deterministic admission contracts, but the execution gate previously stopped at authorization integrity and delegated directly to `ToolService`.

That leaves a missing boundary between proving that an authorized request is still the exact request being executed and proving that the request is admissible under an explicit containment profile.

## Decision
Integrate sandbox admission into the post-authorization path:

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

`SandboxAdmissionService` consumes the exact `AuthorizationDecision`, `AuthorizationIntegrityResult`, and `ToolRequest`. It resolves a declared profile, evaluates it through the existing M22.5 `SandboxAdmissionEvaluator`, and returns an immutable admission decision.

`PolicyGate.invoke()` blocks with `sandbox_admission_failed` when admission does not succeed. Only an admissible request reaches `ToolService`.

Tools may declare a specific profile through `ToolDefinition.metadata["sandbox_profile_id"]`. When no profile is declared, the gate uses the explicit deterministic `default` profile. This preserves existing tool behavior while making sandbox admission a real mandatory gate.

## Authority walls

- Authorization ≠ Sandbox Admission
- Authorization Integrity ≠ Sandbox Admission
- Sandbox Admission ≠ Execution
- Sandbox Profile ≠ Permission
- Sandbox Admission ≠ Worker Assignment
- Sandbox Admission ≠ Containment Activation

Admission does not grant authority, authorization, permission, or execution rights. It does not launch processes, activate isolation, assign workers, or execute plugins.

## Deliberate exclusions

M22.10 does not implement process launching, containment activation, worker assignment, execution handoff, authorization persistence, revocation, expiration, or plugin execution.
