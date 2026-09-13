# Decision 039 — Autonomous Job Lifecycle Boundary

## Status

Proposed V1 application-layer boundary after the M53 interface checkpoint.

## Decision

Introduce an explicit, immutable autonomous-job lifecycle that can own a bounded goal across multiple reasoning/action cycles without coupling the job state machine to any specific LLM, tool, persistence backend, or execution authority.

```text
User Goal
  ↓
Autonomous Job
  ↓
RUNNING ↔ WAITING / PAUSED
  ↓
COMPLETED / FAILED / CANCELLED
```

## Contract

- A job has one explicit goal and a deterministic lifecycle state.
- Each work cycle is recorded as an immutable step/event rather than hidden process state.
- Jobs can pause for user input, explicit authorization, or external tool completion without losing working context.
- Jobs can resume from a paused/waiting state without recreating the job identity.
- A job can complete with a result or fail with explicit failure information.
- Step count is bounded by an explicit maximum; the lifecycle must not silently continue forever.
- The lifecycle is provider-neutral: no LLM, tool, scheduler, database, or execution mechanism is selected here.
- Lifecycle state never implies authorization, truth, permission, or execution authority.
- Cancellation is explicit and terminal.

## Authority walls

```text
Goal ≠ Instruction
Job State ≠ Authorization
Job State ≠ Execution
Waiting ≠ Permission
Completion ≠ Semantic Truth
Failure ≠ Retry Authority
```

## V1 purpose

This is the durable application-level container required before JARVIS can own a long-running piece of work. Later boundaries can plug reasoning, tool execution, observation, evaluation, persistence, scheduling, and multi-model routing into the lifecycle without changing its authority semantics.

## Verification

Focused lifecycle tests are required before this boundary is treated as ready for the autonomous execution loop.
