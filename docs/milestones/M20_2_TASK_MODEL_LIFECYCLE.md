# M20.2 — Task Model / Task Lifecycle

## Purpose

M20.2 establishes the canonical bounded unit of work that belongs to a durable objective.

```text
Goal
 ↓
Objective
 ↓
Task
```

A task describes work to be performed. It does not grant permission, authorization, execution rights, worker assignment, scheduling, or autonomous continuation.

## Contracts

- Immutable `Task`
- `TaskState`
- Explicit `TaskTransitionError`
- `TaskStore`
- Explicit `Provenance`
- Objective identity is retained by every task
- Conflict-aware identity handling
- Deterministic task ordering
- Non-authoritative context projection

## Task lifecycle

```text
PROPOSED → READY → IN_PROGRESS → COMPLETED
    │          │          │
    ├──────────┴──────────┼→ BLOCKED → READY / IN_PROGRESS
    ├→ CANCELLED          ├→ CANCELLED
    └→ SUPERSEDED         └→ SUPERSEDED
```

Terminal states:

```text
COMPLETED
CANCELLED
SUPERSEDED
```

Terminal tasks cannot transition again.

All transitions require an explicit reference identity and return a new immutable value.

## Store semantics

Task identity is keyed by `task_id`.

```text
same task_id + same task → idempotent
same task_id + different task → conflict
unknown objective_id in a bound registry → rejected
```

Tasks can be listed by objective with deterministic ordering by priority and task identity. Terminal tasks can be excluded from active work views.

## Authority boundary

```text
Task ≠ Objective
Task ≠ Authority
TaskState ≠ Permission
Task ≠ Authorization
Task ≠ Execution
Task Completion ≠ Outcome Truth
Task Readiness ≠ Next-Step Selection
```

Every task context projection explicitly reports:

```text
authority_granted = False
authorization_granted = False
execution_requested = False
```

## Deliberate exclusions

M20.2 does **not** implement:

- task dependencies or task graphs
- scheduling
- due-date execution semantics
- worker assignment
- capability/plugin assignment
- automatic decomposition
- next-step selection
- autonomous continuation
- execution

Those concerns belong to later M20 slices.

## Verification

The milestone is complete only when the local contract suite and required regression receipts are green.
