# Decision 018 — Consequence Execution-Preparation Boundary

## Status

Proposed implementation boundary for M33.

## Context

M32 converts an M31 authority handoff into an immutable consequence-level
authorization decision while delegating policy and confirmation to the
existing M22.8 authorization service. M32 deliberately stops before
execution preparation.

The existing tool execution stack already contains deterministic controls for
authorization integrity, sandbox admission, and execution preparation. M33
must connect the M32 consequence authorization result to those existing
controls without creating a second integrity, sandbox, or execution policy.

## Decision

Introduce `ConsequenceExecutionPreparationService` as the M32 -> execution
preparation bridge.

```text
M29 ClaimEvaluation
        ↓
M30 ConsequenceDecision
        ↓
M31 AuthorityHandoffRequest
        ↓
M32 ConsequenceAuthorizationDecision
        ↓
M33 ConsequenceExecutionPreparationService
        ↓
AuthorizationIntegrityService
        ↓
SandboxAdmissionService
        ↓
ExecutionPreparationService
        ↓
Separate execution-attempt boundary
```

M33 accepts only an `AUTHORIZED` M32 decision whose underlying M22.8
`AuthorizationDecision` is itself authorized. It binds that decision to one
exact `ToolDefinition` and `ToolRequest`, then reuses the existing integrity,
sandbox-admission, and execution-preparation contracts.

## Contract

- `AUTHORIZED` M32 decisions may enter execution preparation.
- `DENIED` M32 decisions fail closed without producing an execution handoff.
- An authorized consequence must contain an authorized underlying M22.8
  decision.
- The tool definition name must match the request tool identity.
- Authorization identity, tool identity, and invocation identity must remain
  bound through integrity verification.
- The declared sandbox profile comes from the existing tool definition metadata.
- Failed integrity or sandbox admission produces a blocked preparation result.
- Successful preparation preserves M32 handoff, claim, task, consequence,
  evidence, verification, authorization, and execution-handoff provenance.
- Preparation is immutable and inspectable.
- M33 does not invoke `ToolService`, assign a worker, activate containment,
  start execution, or mutate policy or permission.

## Authority walls

```text
Evidence ≠ Eligibility
Eligibility ≠ Authority Handoff
Authority Handoff ≠ Authorization
Authorization ≠ Integrity
Integrity ≠ Sandbox Admission
Sandbox Admission ≠ Execution Preparation
Execution Preparation ≠ Execution
```

## Deliberate exclusions

M33 does not:

- execute tools;
- call `ExecutionAttemptService`;
- replace `AuthorizationIntegrityService`;
- replace `SandboxAdmissionService`;
- replace `ExecutionPreparationService`;
- create a second sandbox or policy language;
- grant authorization;
- assign workers or activate containment;
- persist or revoke authorization;
- mutate the M32 authorization decision.

## Verification

The milestone requires focused M33 contract tests, M32 compatibility tests,
the full `src.agents.tests` suite, the full tool authorization/execution
boundary suites, and the full `src.core.tests` regression before it is
considered VERIFIED / COMPLETE.
