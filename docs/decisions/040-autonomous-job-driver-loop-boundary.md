# Decision 040 — Autonomous Job Driver Loop Boundary

## Status

Proposed V1 application-layer boundary building on M54.

## Decision

Introduce a provider-neutral autonomous job driver that repeatedly advances a running `AutonomousJob` through bounded work cycles until the worker reports a terminal result or the job reaches an explicit waiting state.

```text
AutonomousJob
   ↓
Driver tick
   ↓
Reason / act / observe / evaluate adapter
   ↓
Record step
   ↓
Continue / wait / complete / fail
   ↺
```

## Contract

- The driver accepts an injected worker; it does not choose an LLM or tool backend.
- One driver cycle produces one explicit `AutonomousCycleResult`.
- Every cycle is recorded on the job before the lifecycle moves to its next state.
- The driver stops automatically at completion, failure, cancellation, input wait, authorization wait, tool wait, or pause.
- The driver's loop is bounded by the job's existing maximum-step budget and may also be bounded by a caller-provided cycle limit.
- Worker exceptions fail the job with explicit failure evidence rather than disappearing into a background task.
- The driver never grants authorization, selects policy, or performs hidden execution outside the injected worker.
- `tick()` is deterministic orchestration; a later background host can call it repeatedly to support overnight/asynchronous work.

## Authority walls

```text
Driver Loop ≠ LLM Authority
Driver Loop ≠ Tool Authority
Driver Loop ≠ Authorization
Driver Loop ≠ Truth
Driver Loop ≠ Autonomous Permission To Act
```

## V1 purpose

M54 gave JARVIS durable ownership of a goal. M55 makes that ownership operational by providing the repeatable control loop that future reasoning, tools, memory, evaluation, and recovery adapters can plug into.

## Verification

Focused driver-loop tests must demonstrate continued multi-cycle work, explicit waits, completion, failure, cycle limits, and exception containment.
