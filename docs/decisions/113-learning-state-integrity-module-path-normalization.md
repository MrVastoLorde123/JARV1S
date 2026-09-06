# Decision 113 — Learning-State Integrity Module Path Normalization

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Parent
`3e43e2cb9cc113de8c7f93d1315e3c3297d8ebde` — M23.100 Architecture Naming & Repository Hygiene.

## Purpose
M23.101 normalizes the import path for the M23.99 learning-state transition integrity API.

The concise canonical module path is:

```text
src.core.learning_state_transition_integrity
```

The existing milestone-derived module remains available as a compatibility surface. This slice changes no runtime behavior, data semantics, authority semantics, persistence semantics, execution semantics, or learning behavior.

## Contract
The canonical module re-exports exactly these public names:

```text
LearningStateTransitionIntegrity
LearningStateTransitionIntegrityService
LearningStateTransitionIntegrityStatus
LearningStateTransitionIntegrityError
```

The long historical module path remains importable for compatibility during the migration.

## Authority Walls

`Module Path ≠ Behavior`
`Import Surface ≠ Authority`
`Refactor ≠ Authorization`
`Compatibility ≠ New Capability`

## Verification Plan
Focused M23.99 integrity tests are unchanged in behavior and import the canonical module path. Full core regression must remain green.

Expected focused verification: **19/19**.
Expected core regression: **1563/1563**.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.100:

1. this decision record;
2. the new canonical module-path compatibility surface;
3. the focused M23.99 integrity test updated to the canonical import path.

No merge is implied by this decision.
