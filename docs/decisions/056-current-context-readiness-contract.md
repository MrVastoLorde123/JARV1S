# M23.12 — Current Context Readiness Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Bind one M23.10 composed current-context bundle to its M23.11 temporal-validity evidence before downstream world-model consumption.

## Contract
`EnvironmentCurrentContextReadinessService` accepts exactly one `EnvironmentCurrentContextBundle` and one matching `EnvironmentCurrentContextBundleValidity`.

It validates bundle identity, environment identity, and ordered context identities. It produces immutable readiness evidence with explicit `READY`, `STALE`, `FUTURE`, or `INVALID` states.

`READY` is emitted only when bundle freshness is `CURRENT` and every contained context validity is also usable as current. Other states preserve the upstream temporal classification and are not usable for world-model consumption.

## Authority boundary
Readiness is evidence gating, not world-truth establishment.

It does not:

- establish truth
- invent timestamps or missing state
- select an authoritative source
- infer permissions
- infer executability or capability availability
- authorize execution
- mutate context, validity, provenance, observations, or memory
- retry providers
- revoke anything
- establish adaptation truth

## Architectural role
M23.9 creates descriptive current context; M23.10 composes independent domain contexts; M23.11 supplies temporal validity. M23.12 creates the explicit readiness seam required before a later world-model layer may consume the composed context bundle.

The output is readiness evidence, not authoritative world state.

## Files
- `src/core/environment_current_context_readiness.py`
- `src/core/tests/test_environment_current_context_readiness.py`
- `docs/decisions/056-current-context-readiness-contract.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_current_context_readiness -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
