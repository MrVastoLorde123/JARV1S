# M23.17 — World Model Revision Decision Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Introduce an explicit decision boundary between an advisory world-model revision proposal and any future revision application.

## Contract
`EnvironmentWorldModelRevisionDecisionService` accepts exactly one M23.16 `EnvironmentWorldModelRevisionProposal` and produces one immutable decision artifact.

The deterministic baseline is:

- `CONSIDER_REVISION` → `ACCEPT`
- `NO_CHANGE` → `REJECT`

`DEFER` remains a valid decision-artifact state for future policy-driven boundaries, but M23.17 does not invent a defer condition.

The result preserves proposal identity, assessment identity, baseline/candidate model identities, environment identity, changed and unchanged domains, reasons, and recursively immutable lineage.

## Authority boundary
The decision is evidence about whether a validated proposal should proceed to a future revision boundary. It does not apply revision or establish truth.

It does not:

- establish world truth
- resolve competing models as authoritative truth
- mutate either source model
- mutate memory or persistence
- infer permissions
- infer executability
- infer capability availability
- authorize execution
- retry providers
- revoke anything
- establish adaptation truth

## Architectural role
M23.13 established the descriptive world model. M23.14 established explicit uncertainty evidence. M23.15 established deterministic model-change evidence. M23.16 established the advisory revision-proposal seam. M23.17 makes the next decision explicit before any future revision application.

Applying a revision, resolving contradictions, preserving historical model state, persistence, confidence calibration, and policy-rich defer logic remain separate future boundaries.

## Files
- `src/core/environment_world_model_revision_decision.py`
- `src/core/tests/test_environment_world_model_revision_decision.py`
- `docs/decisions/056-world-model-revision-decision.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_revision_decision -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
