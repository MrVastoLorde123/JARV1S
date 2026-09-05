# M23.29 — World Model Rollback Repair Proposal Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish the advisory boundary between rollback verification decision evidence and any future repair/correction mechanism.

## Contract
`EnvironmentWorldModelRollbackRepairProposalService` consumes exactly one `EnvironmentWorldModelRollbackVerificationDecision`.

- `ACCEPT` deterministically becomes `NO_REPAIR`.
- `REJECT` deterministically becomes `REPAIR`.
- `DEFER` is a valid decision-artifact state but is not accepted by this deterministic proposal boundary; policy-rich defer handling remains separate.
- The proposal preserves environment, verification-decision, expected-model, observed-model identities, reasons, and lineage.
- Proposal evidence is recursively immutable and the source decision is not mutated.

## Authority boundary
A repair proposal is advisory evidence. It does not repair state, mutate the current-model store, rewrite world-model history, authorize capability execution, establish truth, grant permission, retry providers, synchronize distributed stores, resolve conflicts, revoke anything, or establish adaptation truth.

## Explicitly deferred
Repair decision, repair application, retry policy, transaction guarantees, distributed synchronization, conflict resolution, rollback/recovery verification, audit/event publication, and automated corrective action remain separate boundaries.

## Files
- `src/core/environment_world_model_rollback_repair_proposal.py`
- `src/core/tests/test_environment_world_model_rollback_repair_proposal.py`
- `docs/decisions/065-world-model-rollback-repair-proposal.md`

## Verification
Focused:
`python -m unittest src.core.tests.test_environment_world_model_rollback_repair_proposal -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
