# M16.6 — Rollback / Recovery

## Goal

Make rollback and recovery a first-class, bounded boundary for controlled self-development.

## Boundary

`RollbackRecovery` records how a self-development change can be recovered to a known prior state and records recovery evidence/outcome.

Recovery is descriptive and operationally bounded. It does not create new authority, grant authorization, approve a change, or request a new execution.

## Lineage

```text
SelfDevelopmentProposal
        ↓
ChangeImpactAssessment
        ↓
ControlledModificationPlan
        ↓
TestVerificationGate
        ↓
SafeModificationExecution
        ↓
RollbackRecovery
```

Recovery preserves proposal, assessment, plan, and execution lineage.

## Core walls

- Recovery ≠ Authorization
- Recovery ≠ Policy
- Recovery ≠ New Instruction
- Recovery ≠ New Execution Request
- Recovery ≠ Authority Expansion
- Restored State ≠ Original Truth
- Recovery Evidence ≠ Guaranteed Correctness
- Completed Recovery ≠ Permission to Continue

## Recovery lifecycle

`AVAILABLE → REQUESTED → IN_PROGRESS → COMPLETED`

Additional descriptive states are `NOT_REQUIRED`, `FAILED`, and `INCONCLUSIVE`.

A completed recovery requires explicit recovery evidence. A failed recovery requires outcome notes.

## Invariant

Rollback may restore a known prior state; rollback must not become a side door for authority expansion or policy mutation.
