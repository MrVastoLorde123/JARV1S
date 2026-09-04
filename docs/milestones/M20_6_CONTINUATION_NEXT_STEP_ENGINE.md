# M20.6 — Continuation / Next-Step Engine

## Purpose

M20.6 selects one bounded next-step proposal from an existing long-horizon plan, dependency graph, and current progress evaluations.

It answers:

> Given the current plan and observed progress, what is the earliest structurally available unfinished task to propose continuing?

It does not authorize, schedule, or execute work.

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
Progress / Evidence
  ↓
Long-Horizon Plan
  ↓
Next-Step Engine
  ↓
Bounded Next-Step Proposal
  ↓
M7 Authority Chain
```

## Contracts

- `NextStepProposal` is immutable.
- A proposal references exactly one plan and one task.
- Proposal evidence references are preserved from the task's current progress evaluation.
- Conflicted plan progress yields `NEEDS_REVIEW` and no proposal.
- A task whose prerequisites are not observed completed is not proposed.
- Terminal observed task states are not proposed.
- If every planned task is terminal, continuation returns `NO_CONTINUATION`.
- If no unfinished task is structurally available, continuation returns `NO_CONTINUATION`.
- Plan, graph, and progress-evaluation task identities must agree.

## Authority Boundary

```text
Next-Step Selection ≠ Authorization
Next-Step Proposal ≠ Authorization
Proposal ≠ Execution
Planning ≠ Autonomous Continuation
Graph Order ≠ Execution Order
Observed Completion ≠ Outcome Truth
Conflict ≠ Falsehood
```

Every proposal context explicitly preserves:

```text
authorization_granted = False
execution_requested = False
bounded = True
```

## Relationship to M9.7

M9.7 already provides bounded continuation semantics. M20.6 supplies the long-horizon task-specific selection signal that can feed that bounded continuation model without creating a new authority path.

M20.6 does not mutate the task, plan, or graph while selecting a proposal.

## Deliberate Exclusions

M20.6 does not implement task mutation, scheduling, worker/plugin assignment, automatic decomposition, authorization, execution, business-outcome truth evaluation, or unrestricted autonomous operation.
