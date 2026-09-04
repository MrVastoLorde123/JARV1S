# M20.1 — Goal / Objective Boundary

## Purpose

M20 introduces long-horizon task management without creating a second authority or execution path. M20.1 establishes durable representations for human-level goals and bounded operational objectives.

## Contracts

- `Goal` — durable human-level desired outcome.
- `Objective` — bounded operational objective belonging to a `Goal`.
- `Provenance` — explicit origin reference preserved by both objects.
- `ObjectiveState` — explicit lifecycle state for an objective.
- `GoalObjectiveStore` — conflict-aware replacement store for goals and objectives.

## Objective lifecycle

```text
PROPOSED → ACTIVE
PROPOSED → CANCELLED

ACTIVE → PAUSED
ACTIVE → BLOCKED
ACTIVE → COMPLETED
ACTIVE → CANCELLED
ACTIVE → SUPERSEDED

PAUSED → ACTIVE
PAUSED → CANCELLED
PAUSED → SUPERSEDED

BLOCKED → ACTIVE
BLOCKED → CANCELLED
BLOCKED → SUPERSEDED
```

`COMPLETED`, `CANCELLED`, and `SUPERSEDED` are terminal states.

All lifecycle transitions require an explicit reference and produce a new immutable objective value.

## Authority boundary

```text
Goal ≠ Authority
Objective ≠ Authorization
Objective State ≠ Permission
Priority ≠ Permission
Progress ≠ Success
Continuation ≠ Authorization
Persistence ≠ Permission
```

Context projections explicitly expose non-authoritative flags:

```text
authority_granted = false
authorization_granted = false
execution_requested = false
```

M20.1 does not perform task decomposition, scheduling, dependency resolution, execution, worker dispatch, or autonomous continuation.

## Verification

The focused contract suite is intended to verify immutability, provenance, identity conflicts, lifecycle transitions, terminal-state protection, deterministic ordering, relationship integrity, and the non-authoritative context boundary.
