# M22.12 — Execution Attempt / Worker Boundary

## Purpose
Establish the first explicit execution-attempt boundary after the inert `ExecutionHandoff`.

## Contract
- `ExecutionAttemptService` accepts only an `ExecutionHandoff`.
- `ToolExecutor` is provider-neutral and replaceable.
- Every attempt receives a deterministic `execution_id`.
- Executor output must be a `ToolResult` whose tool and invocation identities match the handoff.
- Successful execution and failed execution are distinct attempt outcomes.
- Worker identity is optional metadata and is not authorization.
- `PolicyGate` reaches the executor only after authorization, authorization integrity, sandbox admission, and execution preparation succeed.

## Boundary
```text
ExecutionHandoff
↓
Execution Attempt / Worker Boundary
↓
Execution
↓
Outcome
```

## Authority walls
- Execution Preparation ≠ Execution Attempt
- Execution Attempt ≠ Successful Outcome
- Execution Attempt ≠ Worker Identity
- Worker Assignment ≠ Authorization
- Execution Attempt ≠ Capability Permission
- Outcome ≠ Authorization

## Deliberate exclusions
No durable execution queue, retry policy, distributed worker scheduling, cancellation, sandbox containment activation, or alternate authorization path is introduced.

## Verification
Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.
