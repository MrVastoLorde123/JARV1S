# Decision 112 — Architecture Naming & Repository Hygiene

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Parent
`f2182c595cbb638d736fbf74bad7f7dbd1336071` — M23.99 Learning-State Transition Integrity V4.

## Purpose
M23.100 begins the repository naming and hygiene boundary without changing JARVIS behavior or authority semantics.

This first atomic slice normalizes the public Python API names for the M23.99 learning-state transition integrity component. Milestone history remains in Git and documentation rather than being embedded in every Python identifier.

## Naming Contract
The canonical API names introduced by this slice are:

```text
LearningStateTransitionIntegrity
LearningStateTransitionIntegrityService
LearningStateTransitionIntegrityStatus
LearningStateTransitionIntegrityError
```

The existing long identifiers remain as compatibility aliases for this transition only. They are not canonical architecture names and carry no new behavior.

## Hygiene Principles
- Python identifiers describe the architectural concept, not its entire milestone ancestry.
- PEP 8-compatible class and module vocabulary is preferred.
- Milestone/version history belongs in Git, decision records, and milestone documentation.
- Renaming must preserve behavior and authority boundaries.
- No production behavior, persistence semantics, execution semantics, or learning authority changes are permitted in M23.100.
- No interface behavior is changed.

## Authority Walls
This maintenance milestone does not alter any authority boundary.

`Naming ≠ Behavior`
`Naming ≠ Authority`
`Refactor ≠ Authorization`
`Documentation ≠ Policy Mutation`

## Scope
This slice covers the M23.99 integrity API naming surface. Module-path normalization, broader import migration, and historical branch cleanup are separate hygiene operations so that each change remains atomic and reviewable.

## Verification Plan
Focused tests must verify the canonical names are usable and the M23.99 behavior remains unchanged through the renamed API. Full core regression must remain green.

Expected focused verification: **19/19**.
Expected core regression: **1563/1563**.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.99:

1. this decision record;
2. the M23.99 integrity production module with canonical names and compatibility aliases;
3. the focused M23.99 integrity test updated to canonical names.

No merge is implied by this decision.
