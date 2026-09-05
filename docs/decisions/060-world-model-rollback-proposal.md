# M23.23 — World Model Rollback Proposal Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish an advisory boundary for proposing rollback to a historical descriptive world-model artifact without applying the rollback.

## Contract
`EnvironmentWorldModelRollbackProposalService` accepts one immutable `EnvironmentWorldModelHistory` and a historical target model identity.

- target models must exist in history
- current state is the history latest artifact by default, or an explicitly supplied current model
- current and target models must belong to the same environment
- selecting the current model produces `NO_ROLLBACK`
- selecting a different historical model produces `ROLLBACK`
- proposal, reasons, and lineage are recursively immutable
- source history and models are never mutated

## Authority boundary
The proposal is advisory evidence only. It does not apply rollback, establish truth, select authoritative state, authorize execution, mutate persistence, retry providers, revoke anything, infer permissions or executability, or establish adaptation truth.

## Explicitly deferred
Rollback decision, rollback application, persistence coordination, transactions, distributed synchronization, conflict resolution, and audit/event publication remain separate boundaries.

## Files
- `src/core/environment_world_model_rollback_proposal.py`
- `src/core/tests/test_environment_world_model_rollback_proposal.py`
- `docs/decisions/060-world-model-rollback-proposal.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_rollback_proposal -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
