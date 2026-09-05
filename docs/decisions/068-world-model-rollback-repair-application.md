# M23.31 — World Model Rollback Repair Application Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish the explicit mutation boundary that may apply an accepted rollback-repair decision to the current world-model store.

## Contract
`EnvironmentWorldModelRollbackRepairApplicationService` consumes:

- one immutable `EnvironmentWorldModelRollbackRepairProposal`
- one immutable matching `EnvironmentWorldModelRollbackRepairDecision`
- one expected immutable `EnvironmentWorldModel`
- one provider-neutral current-model store

Rules:

- `ACCEPT` replaces the observed current model with the expected model using the store's compare-and-swap guard against the observed identity.
- `REJECT` retains the observed current model and performs no write.
- unsupported decision values fail closed.
- proposal expected identity must match the supplied expected model.
- proposal observed identity must match the current stored/observed model.
- environment identities and proposal/decision lineage identities must align.
- source proposal, decision, expected model, and observed model objects are never mutated.
- the resulting application artifact is recursively immutable and preserves transition identities, reasons, and lineage.

## Authority boundary
Repair application is a state mutation boundary, but it does not establish truth, grant permission, authorize unrelated capability execution, mutate history, retry providers, synchronize distributed stores, resolve conflicts, revoke anything, or establish adaptation truth.

The application acts only because a separate decision artifact explicitly says `ACCEPT`.

## Explicitly deferred
Repair verification, persistence coordination beyond the current-model store operation, transactions, distributed synchronization, conflict resolution, audit/event publication, retry policy, and automated corrective planning remain separate boundaries.

## Verification
Focused:
`python -m unittest src.core.tests.test_environment_world_model_rollback_repair_application -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
