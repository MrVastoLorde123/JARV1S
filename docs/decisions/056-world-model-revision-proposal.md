# M23.16 — World Model Revision Proposal Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish a non-mutating proposal boundary between deterministic world-model change evidence and future world-model revision logic.

## Contract
`EnvironmentWorldModelRevisionProposalService` accepts a baseline model, a candidate model, and matching M23.15 change assessment evidence.

A proposal is:
- `CONSIDER_REVISION` when one or more represented domains changed.
- `NO_CHANGE` when no domain changes were detected.

The proposal preserves baseline and candidate model identities, assessment identity, changed/unchanged domains, reasons, and immutable lineage.

## Authority boundary
The proposal is advisory evidence only. It does not:

- apply a world-model revision
- establish which model is true
- resolve contradictions
- select an authoritative model
- infer permissions or executability
- authorize execution
- mutate either source model
- mutate memory or persistence
- retry providers
- revoke anything
- establish adaptation truth

## Architectural role
M23.13 established the descriptive world model.
M23.14 established explicit uncertainty evidence.
M23.15 established deterministic change evidence between model artifacts.
M23.16 establishes the advisory seam that can later feed an explicit revision/decision boundary without allowing assessment to silently become mutation.

Belief revision, contradiction resolution, persistence, historical model state, and learned confidence calibration remain separate boundaries.

## Files
- `src/core/environment_world_model_revision_proposal.py`
- `src/core/tests/test_environment_world_model_revision_proposal.py`
- `docs/decisions/056-world-model-revision-proposal.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_revision_proposal -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
