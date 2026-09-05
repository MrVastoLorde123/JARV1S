# M23.24 — World Model Rollback Decision Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish the explicit decision boundary between M23.23 rollback proposal evidence and any future rollback application.

## Contract
`EnvironmentWorldModelRollbackDecisionService` consumes exactly one `EnvironmentWorldModelRollbackProposal`.

- `ROLLBACK` deterministically becomes `ACCEPT`.
- `NO_ROLLBACK` deterministically becomes `REJECT`.
- The decision preserves current/target model identities, environment identity, proposal identity, reasons, and lineage.
- `DEFER` is a valid decision-artifact state but is not fabricated by this deterministic boundary; policy-rich defer logic remains separate.
- Invalid recommendation values fail closed.
- The source proposal remains unchanged.

## Authority boundary
Rollback decision is advisory evidence. It does not apply rollback, establish truth, select an authoritative model, authorize execution, mutate persistence, mutate history, retry providers, revoke anything, infer permissions or executability, or establish adaptation truth.

An `ACCEPT` decision is evidence required by a later application boundary; it is not itself the rollback operation.

## Explicitly deferred
Rollback application, persistence coordination, transactions, rollback verification, distributed synchronization, conflict resolution, audit/event publication, and policy-rich defer logic remain separate boundaries.

## Files
- `src/core/environment_world_model_rollback_decision.py`
- `src/core/tests/test_environment_world_model_rollback_decision.py`
- `docs/decisions/061-world-model-rollback-decision.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_rollback_decision -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
