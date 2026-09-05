# M23.13 — Environment World Model Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Define the first explicit world-model boundary for JARVIS: convert a READY current-context bundle into an immutable, provider-neutral descriptive model of the observed environment.

## Contract
`EnvironmentWorldModelService` accepts exactly one `EnvironmentCurrentContextBundle` and one matching `EnvironmentCurrentContextBundleValidity`.

A world model may be built only when:
- bundle and validity identities/scope align
- bundle context identities align with validity context identities
- bundle temporal validity is `CURRENT`
- every contained context validity is `CURRENT`

The resulting `EnvironmentWorldModel` preserves represented and missing domains, per-domain state, context identities, qualification identities, provenance identities, readiness identity, source bundle identity, and immutable lineage.

Missing domains remain missing. They are not converted into unavailable, false, or unknown claims beyond what the source bundle explicitly represents.

## Authority boundary
The world model is a descriptive representation derived from ready evidence. It is not authoritative world truth.

It does not:
- establish truth
- invent missing state
- select an authoritative source
- infer permissions
- infer executability
- infer capability availability
- authorize execution
- mutate observations, context, provenance, or memory
- retry providers
- revoke anything
- establish adaptation truth

## Architectural role
M23.8 qualifies environment evidence; M23.9 turns usable evidence into current context; M23.10 composes per-domain context; M23.11 assesses temporal validity; M23.12 gates the composed bundle as `READY`. M23.13 is the first seam that gives downstream reasoning a structured environment model while retaining source lineage and descriptive-only semantics.

The model is a snapshot/derived representation, not a mutable truth store. Persistence, belief revision, contradiction resolution, uncertainty modeling, and historical state tracking remain separate future boundaries.

## Files
- `src/core/environment_world_model.py`
- `src/core/tests/test_environment_world_model.py`
- `docs/decisions/055-environment-world-model-contract.md`
- `docs/JARVIS_MASTER_CONTEXT.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
