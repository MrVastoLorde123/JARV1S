# M23.18 — World Model Revision Application Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish the explicit application boundary after M23.17 revision decision evidence.

## Contract
`EnvironmentWorldModelRevisionApplicationService` consumes one baseline model, one candidate model, and one matching revision decision.

- `ACCEPT` returns the candidate model as the resulting immutable state and records an applied transition.
- `REJECT` or `DEFER` returns the baseline model and records that no revision was applied.
- Baseline, candidate, and decision environment identities must align.
- Decision baseline/candidate model identities must exactly match the supplied source models.
- The application record preserves transition identity, decision identity, source model identities, resulting model identity, reasons, and lineage.
- Nested reasons and lineage are recursively immutable.

## Mutation boundary
The existing `EnvironmentWorldModel` artifacts are frozen values and are never mutated. "Apply" in M23.18 means selecting the validated candidate as the resulting immutable model state and recording the transition, not mutating an existing model object in place.

Persistence, durable current-model storage, rollback, historical model retention, distributed synchronization, and external side effects remain separate future boundaries.

## Authority boundary
The application boundary does not establish truth, infer permissions, grant authorization, execute capabilities, mutate memory, retry providers, revoke anything, or establish adaptation truth. An `ACCEPT` decision is prerequisite evidence for application but is not execution authority.

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_revision_application -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
