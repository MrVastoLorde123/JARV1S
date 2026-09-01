# Decision 020 — State-Aware Continuation

## Status
Accepted

## Context

M4.1 introduced `ExecutionState` as a provider-neutral representation derived from an execution result. Before this decision, continuation logic primarily interpreted whether an execution result succeeded or failed.

## Decision

Continuation decisions are derived from `ExecutionState.next_allowed_actions` rather than from raw execution status alone.

The continuation service recognizes these control-level outcomes:

- `COMPLETE` — the objective is complete.
- `CONTINUE` — a corrective continuation is permitted because the state allows `CORRECT`.
- `STOP` — no continuation is permitted.

The guarded execution loop passes the derived state to the continuation service. A corrective planner may still propose only a `TaskRequest`, which must re-enter the existing planning, validation, policy, confirmation, and execution pipeline.

## Rationale

This separates three concerns:

1. Execution produces evidence.
2. Execution state interprets that evidence into an explicit bounded control state.
3. Continuation logic decides whether another planning step is permitted.

This creates a foundation for partial success, unresolved requirements, richer recovery strategies, long-running objectives, and persistent task state without granting the model execution authority.

## Safety Invariants

- State is immutable and provider-neutral.
- State does not contain executor, tool, or provider objects.
- Continuation cannot create execution authority.
- `next_allowed_actions` is an explicit boundary; continuation does not invent actions outside it.
- Every corrective plan still re-enters the full guarded pipeline.
- The existing iteration bound remains in force.

## Consequence

The next M4 work should build richer state transitions and persistence only where they improve objective awareness. It should not bypass the existing safety pipeline or turn continuation into an unbounded retry loop.
