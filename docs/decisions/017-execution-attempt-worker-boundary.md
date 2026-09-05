# Decision 017 — Execution Attempt / Worker Boundary

## Context
M22.11 established an immutable, non-executing `ExecutionHandoff` after authorization integrity and sandbox admission. The architecture now needs an explicit boundary that can attempt execution without conflating execution initiation, worker identity, and successful completion.

## Decision
Introduce `ExecutionAttemptService` behind a provider-neutral `ToolExecutor` contract. The service consumes only an `ExecutionHandoff`, creates a deterministic `execution_id`, delegates to the replaceable executor, validates the returned `ToolResult` identity against the handoff, and records either a completed or failed attempt.

`PolicyGate` remains the only upstream authority path. It prepares the handoff and then crosses the execution-attempt boundary. The default executor adapts the existing `ToolService`; alternate worker/process-backed executors can be introduced later behind the same contract.

## Invariants
- Execution Preparation != Execution Attempt.
- Execution Attempt != Successful Outcome.
- Execution Attempt != Worker Identity.
- Worker assignment != Authorization.
- Outcome != Authorization.
- Executor output must match handoff tool and invocation identity.
- Failed attempts become explicit failure data and are never reported as success.
- No executor receives an unprepared request through the gate.

## Exclusions
This milestone does not implement durable execution queues, retry policy, distributed workers, process isolation activation, cancellation, scheduling, or a new authorization path.
