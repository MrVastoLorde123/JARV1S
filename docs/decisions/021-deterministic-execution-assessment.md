# Decision 021 — Deterministic Execution Assessment

## Status
Accepted — M5.1

## Context
JARVIS now records provider-neutral `ExecutionState` and immutable `ExecutionProgress` across execution attempts. M4.5 allows the primary planner to consume that progress, but the system still lacks an explicit layer that interprets verified execution state before planning the next move.

## Decision
Introduce `ExecutionAssessment` as a provider-neutral interpretation of verified `ExecutionState`.

`ExecutionAssessmentService` performs deterministic assessment only. It does not call a model, execute tools, authorize actions, or mutate execution state.

The assessment separates:

- observed completed work
- remaining requirements
- blockers
- useful outputs
- the current situation
- a conservative recommended next action

The current situation values are:

- `objective_completed`
- `blocked`
- `partial_progress`
- `no_progress`

Terminal execution states remain the source of truth. `FAILED` and `BLOCKED` are interpreted from their verified fields rather than allowing the assessment layer to invent new execution states.

## Safety invariants

- Execution state remains the authoritative observation of reality.
- Assessment is interpretation, not execution authority.
- No model or capability is invoked by deterministic assessment.
- Assessment cannot bypass validation, policy, confirmation, or the executor.
- Assessment is immutable and provider-neutral.

## Consequence
JARVIS now has an explicit deterministic layer between observed execution and future reasoning/planning. M5.2 can build model-assisted interpretation on top of this layer without making the model the source of truth for what actually happened.
