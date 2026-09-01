# Decision 015 — Multi-Step Planning Boundary

## Status
Accepted

## Purpose

Introduce a provider-neutral boundary for execution planning so JARVIS can evolve from the deterministic V1 single-step planner toward multi-step, AI-assisted planning without changing the execution safety pipeline.

## Decision

Add `ExecutionPlannerProtocol` as the stable contract for planning:

```text
TaskRequest → ExecutionPlan
```

The contract is intentionally structural. A deterministic planner, AI-assisted planner, or future multi-step planner can implement it without requiring changes to downstream execution components.

A valid implementation may produce one or many ordered `PlanStep` objects and may express dependencies between steps.

## Responsibility Boundary

The planning boundary only describes intended work.

It does not:

- validate the plan
- authorize the plan
- request confirmation
- execute a step
- invoke tools
- invoke capabilities directly

Those responsibilities remain downstream:

```text
planner
  ↓
ExecutionPlan
  ↓
PlanValidator
  ↓
ExecutionPolicy
  ↓
ExecutionConfirmation
  ↓
PlanExecutor
  ↓
capability/tool boundary
```

## Safety Rules

- A richer planner must not create a second execution path.
- Multi-step plans must use the existing `ExecutionPlan` model.
- Existing dependency validation remains authoritative.
- Existing policy and confirmation remain authoritative.
- The executor remains the only component that performs plan steps.
- Planner implementations remain replaceable behind the same provider-neutral contract.

## Initial Scope

This milestone establishes the contract and proves that the existing deterministic planner and a representative multi-step planner satisfy it.

The deterministic planner remains unchanged and continues to emit one step in V1.

The next M3 work can therefore introduce a real multi-step planning strategy and observation loop without first redesigning JARVIS's execution safety architecture.
