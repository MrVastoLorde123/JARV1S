# M20.5 — Long-Horizon Planning

## Purpose

M20.5 assembles an explicit long-horizon plan from the existing M20 goal/objective boundary, task lifecycle, dependency graph, and progress evaluation layers.

The planner describes the current work structure and preserves the observed-progress signal. It does not decide what should happen next and does not create a schedule or execution authorization.

## Model

```text
Goal
  ↓
Objective
  ↓
Tasks
  ↓
Dependencies
  ↓
Progress Evaluations
  ↓
Long-Horizon Plan
```

## Contracts

- `PlanStep` is a structural task reference, not a command.
- `LongHorizonPlan` is an immutable snapshot.
- Graph order is preserved as deterministic plan structure.
- `CONFLICTED` progress causes `NEEDS_REVIEW` rather than silent reconciliation.
- `UNVERIFIED` progress remains unverified; it is not treated as failure.
- Evaluation evidence is preserved through deterministic evaluation identifiers.
- Explicit plan identity is required.
- Goal/objective/task/graph identity must agree before a plan is built.

## Authority Boundary

```text
Plan ≠ Authorization
Plan ≠ Execution
Plan ≠ Schedule
PlanStep ≠ Next Step
Graph Order ≠ Execution Order
Evaluation ≠ Truth
Conflict ≠ Falsehood
Planning ≠ Autonomous Continuation
```

The plan context explicitly exposes:

```text
authority_granted = False
authorization_granted = False
execution_requested = False
next_step_selected = False
schedule_created = False
```

## Deliberate Exclusions

M20.5 does not implement readiness evaluation, next-step selection, scheduling, worker/plugin assignment, automatic decomposition, autonomous continuation, authorization, execution, or business-outcome truth evaluation.

Those concerns remain reserved for later milestones, especially M20.6.
