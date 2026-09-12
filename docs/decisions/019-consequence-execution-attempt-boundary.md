# Decision 019 — Consequence Execution-Attempt Boundary

## Status

Proposed implementation boundary for M34.

## Context

M33 converts an authorized consequence into an immutable, integrity-verified,
sandbox-admissible `ExecutionHandoff`. M33 deliberately stops before an
execution attempt is started.

JARVIS already has an `ExecutionAttemptService` that accepts exactly one
prepared `ExecutionHandoff`, invokes a replaceable `ToolExecutor`, and records
an explicit execution identity and lifecycle result. M34 must connect the M33
consequence lineage to that existing attempt boundary without creating a
second executor or implying that preparation is execution.

## Decision

Introduce `ConsequenceExecutionAttemptService` as the M33 -> existing
execution-attempt bridge.

```text
M29 ClaimEvaluation
        ↓
M30 ConsequenceDecision
        ↓
M31 AuthorityHandoffRequest
        ↓
M32 ConsequenceAuthorizationDecision
        ↓
M33 ConsequenceExecutionPreparation
        ↓
M34 ConsequenceExecutionAttemptService
        ↓
Existing ExecutionAttemptService
        ↓
ToolExecutor
```

M34 accepts only a `PREPARED` M33 result containing a valid immutable
`ExecutionHandoff`. It delegates the actual attempt to the existing
`ExecutionAttemptService` and wraps the result with the complete M33 lineage.

## Contract

- Only `PREPARED` M33 results may enter the attempt boundary.
- A prepared result must contain an `ExecutionHandoff`.
- The execution handoff must retain authorization, tool, and invocation identity.
- Existing `ExecutionAttemptService` remains the sole attempt/executor bridge.
- M34 does not create a second executor or invoke `ToolService` directly.
- Execution failures become explicit failed-attempt data; they are not converted
  into authorization denial.
- Successful execution remains an observed execution result, not new authority.
- Full handoff, claim, task, consequence, evidence, verification, authorization,
  preparation, and execution provenance is preserved.
- A blocked/unprepared consequence fails closed without invoking the executor.
- M34 does not retry, mutate authorization, change policy, assign workers, or
  activate containment.

## Authority walls

```text
Evidence ≠ Eligibility
Eligibility ≠ Authority Handoff
Authority Handoff ≠ Authorization
Authorization ≠ Integrity
Integrity ≠ Sandbox Admission
Sandbox Admission ≠ Execution Preparation
Execution Preparation ≠ Execution Attempt
Execution Attempt ≠ Successful Completion
Successful Completion ≠ New Authority
```

## Deliberate exclusions

M34 does not:

- authorize consequences;
- replace `ExecutionAttemptService`;
- invoke `ToolService` independently;
- retry failed executions;
- convert execution outcomes into learning or truth claims;
- mutate memory, policy, permission, or authorization;
- assign independent workers;
- activate containment outside the existing executor boundary.

## Verification

The milestone requires focused M34 contract tests, coding-service seam tests,
M33 compatibility, the full `src.agents.tests` suite, execution-attempt/tool
boundary coverage, and the full `src.core.tests` regression before it is
considered VERIFIED / COMPLETE.
