# Decision 020 — Progress-Aware Plan Generation

## Status
Accepted — M4.5

## Context
JARVIS now carries provider-neutral `ExecutionState` observations and immutable `ExecutionProgress` across multiple execution attempts. M4.4 made model continuation progress-aware, but the primary planning boundary still accepted only a `TaskRequest`.

## Decision
Extend the provider-neutral execution planning contract so planners may receive `ExecutionProgress` for the current objective. The existing model execution planner consumes that progress when constructing its planning prompt.

The planner remains proposal-only: it returns an `ExecutionPlan` and does not validate, authorize, confirm, execute, or invoke capabilities.

The guarded execution loop forwards accumulated progress into every planning attempt. The plan then follows the unchanged validator -> policy -> confirmation -> executor pipeline.

Deterministic planning remains behaviorally conservative; it accepts the progress input and preserves the existing plan semantics rather than attempting semantic inference itself.

## Safety invariants

- Progress does not grant execution authority.
- Planner-side capability realization remains the only planning-time bridge for TOOL task proposals; actual capability execution remains downstream.
- Every newly generated plan is validated and authorized before execution.
- Confirmation remains mandatory wherever the existing policy/tool layer requires it.
- The execution loop remains iteration-bounded.
- No persistence is introduced by this decision.

## Consequence
JARVIS can now plan against known objective progress instead of treating every continuation as a fresh objective. This establishes the planning-side half of M4 without increasing autonomous authority.
