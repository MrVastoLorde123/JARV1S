# M20.3 — Dependencies / Task Graph

## Purpose

M20.3 defines how existing tasks relate to one another.

A dependency means:

> **dependent task requires prerequisite task**

The graph records structure only. It does not decide when work should happen, who should perform it, whether a task is ready, or whether anything is authorized to execute.

## Included

- Immutable `TaskDependency` relationship.
- Explicit prerequisite → dependent direction.
- Registered task identity boundary.
- Self-dependency rejection.
- Unknown-task rejection.
- Duplicate dependency idempotence.
- Cycle prevention.
- Explicit dependency removal.
- Deterministic prerequisite/dependent queries.
- Deterministic topological ordering.
- Structural root and leaf queries.

## Deliberate exclusions

M20.3 does **not** introduce:

- scheduling
- due dates or time planning
- worker assignment
- plugin assignment
- automatic decomposition
- readiness evaluation
- next-step selection
- autonomous continuation
- execution
- authorization
- outcome evaluation

## Invariants

```text
Dependency ≠ Task State
Dependency ≠ Schedule
Dependency ≠ Readiness
Dependency ≠ Authorization
Dependency ≠ Execution
Graph Order ≠ Execution Order
Topological Order ≠ Scheduling Decision
Root/Leaf ≠ Next Step
```

The graph may describe that `B` depends on `A`. It does not grant permission to run `A` or `B`.

## Graph semantics

For a dependency `(A, B)`:

```text
A ──prerequisite──> B
```

`A` is a prerequisite of `B`, and `B` is a dependent of `A`.

The graph must remain acyclic so that structural ordering is well-defined.

## Verification target

The focused suite must validate relationship direction, identity checks, duplicate idempotence, self-dependency rejection, cycle prevention, removal, deterministic graph traversal, and the absence of scheduling/authority contracts.
