# M23.27 — World Model Rollback Verification Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish an explicit verification boundary after M23.26 rollback persistence coordination.

## Contract
`EnvironmentWorldModelRollbackVerificationService` consumes:
- one immutable M23.25 rollback application artifact
- one immutable M23.26 rollback persistence artifact
- one observed current `EnvironmentWorldModel`

Verification succeeds only when the persistence result is marked persisted and the observed current model identity matches the persisted resulting model identity.

Verification preserves application/persistence/environment/model identities, reasons, and recursively immutable lineage. Source artifacts remain unchanged.

A persisted-but-mismatched observed model is explicit negative evidence (`verified=False`), not an exception, because the observation itself is structurally valid but does not confirm the expected resulting state.

Structural identity/scope mismatches are rejected as contract violations.

## Authority boundary
Verification confirms whether the observed current model matches an expected persisted result. It does not establish truth, grant permission, authorize execution, mutate history, rewrite persistence, retry providers, synchronize distributed state, resolve conflicts, revoke anything, or establish adaptation truth.

`establishes_truth == False` and `is_authorization == False` are explicit contract properties.

## Explicitly deferred
Distributed synchronization, transactional guarantees, repair/retry behavior, conflict resolution, audit/event publication, and automated corrective action remain separate boundaries.

## Files
- `src/core/environment_world_model_rollback_verification.py`
- `src/core/tests/test_environment_world_model_rollback_verification.py`
- `docs/decisions/064-world-model-rollback-verification.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_rollback_verification -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
