# Decision 021 — Execution Progress Across Attempts

## Status
Accepted

## Context

M4 introduced `ExecutionState` as the provider-neutral interpretation of one execution observation and added explicit continuation decisions. That state is intentionally scoped to a single attempt.

The next requirement is to let corrective reasoning understand an objective across multiple bounded execution attempts without introducing persistence or autonomous retry behavior.

## Decision

Introduce `ExecutionProgress` as an immutable, in-memory accumulator of `ExecutionState` values for one objective.

`ExecutionObservation` may expose the progress snapshot that existed immediately after that attempt. `ExecutionLoopResult` also exposes the final accumulated progress for the run.

Progress is observational, not authoritative:

- it preserves the ordered attempt history;
- it exposes the current state and current allowed actions;
- it aggregates completed steps using `plan_id:step_id` so attempts are not silently conflated;
- it aggregates outputs without asserting semantic equivalence between steps;
- it preserves the current unresolved requirements and continuation actions.

The progress object does not execute, authorize, validate, persist, or modify execution state.

## Consequences

Corrective planning can be given a richer objective-level view in a later increment without changing the safety pipeline.

`max_iterations` remains the execution bound. No automatic retry policy is introduced by this decision.

Persistence remains outside M4.3 and will require a separate architectural decision.
