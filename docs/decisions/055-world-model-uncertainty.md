# M23.14 — World Model Uncertainty Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Introduce an explicit uncertainty boundary for the descriptive environment world model without turning confidence into truth, authority, or permission.

## Contract
`EnvironmentWorldModelUncertaintyService` assesses one `EnvironmentWorldModel` and records bounded confidence and complementary uncertainty for each represented domain.

Confidence values are numeric and bounded to `[0, 1]`. Uncertainty is deterministically derived as `1 - confidence`. Missing domains remain missing and do not receive invented confidence values.

The result preserves model identity, environment identity, represented/missing domains, evidence status, confidence, uncertainty, reasons, and lineage.

## Authority boundary
Uncertainty is descriptive evidence about confidence in the model's represented evidence. It does not establish truth.

It does not:

- establish world truth
- select an authoritative source
- infer permissions
- infer executability
- infer capability availability
- authorize execution
- mutate the world model
- mutate observations, provenance, or memory
- retry providers
- revoke anything
- establish adaptation truth

## Architectural role
M23.13 introduced the immutable descriptive environment world model from READY current context. M23.14 makes confidence and uncertainty explicit so later reasoning can distinguish evidence quality from certainty.

Belief revision, contradiction resolution, historical world-model state, learned confidence calibration, and persistence remain separate future boundaries.

## Files
- `src/core/environment_world_model_uncertainty.py`
- `src/core/tests/test_environment_world_model_uncertainty.py`
- `docs/decisions/055-world-model-uncertainty.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_uncertainty -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
