# Decision 018 — Execution Outcome / Result Integrity

## Context

M22.12 establishes an explicit execution-attempt boundary and returns an immutable `ExecutionAttemptResult`. The next boundary must interpret that attempt without treating tool output as authority, user intent, or learning.

## Decision

Introduce `ExecutionOutcomeService` and immutable `ExecutionOutcome` records.

The service:

- accepts only an `ExecutionAttemptResult` paired with its exact `ExecutionHandoff`;
- verifies deterministic execution identity plus handoff, tool, and invocation identity;
- distinguishes successful execution from tool-declared failure and executor/transport failure;
- rejects inconsistent attempt lifecycle/result combinations;
- produces an immutable outcome suitable for later feedback pipelines;
- grants no authority, permission, authorization, retry, revocation, or learning side effects.

## Boundary

```text
ExecutionHandoff
        ↓
Execution Attempt
        ↓
Outcome / Result Integrity
        ↓
Feedback / Learning
```

## Authority walls

- Execution Attempt != Outcome Truth
- ToolResult != Authorization
- ToolResult != User Intent
- Outcome != Learning
- Failure != Revocation
- Successful execution != Permission to execute again
- Outcome interpretation != Policy bypass

## Non-goals

M22.13 does not implement retries, automatic re-authorization, revocation, durable outcome storage, learning writes, or alternate execution paths.
