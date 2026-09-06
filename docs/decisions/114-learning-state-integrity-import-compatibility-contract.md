# Decision 114 — Learning-State Integrity Import Compatibility Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Parent
`81630a3f682c3a6f1aa2feda4f61084a4051dcbd` — M23.101 Learning-State Integrity Module Path Normalization.

## Purpose
M23.102 proves that the concise canonical learning-state transition integrity import surface is an identity-preserving compatibility layer over the historical milestone-derived implementation.

The canonical module path remains:

```text
src.core.learning_state_transition_integrity
```

The historical module remains importable during migration. This slice introduces no new runtime capability and changes no behavior, data semantics, authority semantics, persistence semantics, execution semantics, or learning behavior.

## Contract
The canonical module's four public names must resolve to the exact same Python objects as the corresponding historical compatibility aliases:

```text
LearningStateTransitionIntegrity
LearningStateTransitionIntegrityService
LearningStateTransitionIntegrityStatus
LearningStateTransitionIntegrityError
```

Identity equivalence is required, not merely equivalent behavior or matching names.

## Authority Walls

`Import Identity ≠ Authority`
`Compatibility ≠ New Capability`
`Refactor ≠ Authorization`
`Module Path ≠ Behavior`

## Verification Plan
The focused learning-state integrity test adds explicit identity checks between canonical imports and historical aliases. Full core regression must remain green.

Expected focused verification: **20/20**.
Expected core regression: **1564/1564**.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.101:

1. this decision record;
2. the canonical module compatibility surface documentation;
3. the focused M23.99 integrity test with explicit import-identity coverage.

No merge is implied by this decision.
