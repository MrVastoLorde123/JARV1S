# M23.9 — Environment Evidence → Current Context Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Define the first explicit seam between qualified environment evidence and the world-model/current-context layer without converting evidence into unquestioned truth.

## Contract
`EnvironmentEvidenceCurrentContextService` converts one M23.8-qualified observation or aggregate into an immutable `EnvironmentCurrentContext` only when its qualification is `USABLE` and identity/scope alignment passes.

The context preserves:

- context identity
- environment identity
- domain
- subject kind
- descriptive observed data
- evidence qualification state
- source observation identities
- source adapter identities
- provenance identity
- qualification identity
- lineage metadata

Unknown or absent environment information is not fabricated. A context represents qualified evidence available for downstream reasoning, not a complete authoritative model of the world.

## Authority boundary
Current context is descriptive evidence, not authoritative world truth.

It does not:

- establish truth
- invent missing state
- select an authoritative observer
- infer permissions
- infer executability
- infer capability availability
- authorize execution
- mutate observations
- mutate provenance
- mutate memory
- retry providers
- revoke anything
- establish adaptation truth

## Architectural role
M23.4 supplies temporal validity; M23.5 supplies consistency evidence; M23.6 supplies derived aggregate evidence; M23.7 supplies source provenance; M23.8 qualifies those evidence bundles. M23.9 makes only `USABLE` qualified evidence consumable as provider-neutral current context while retaining source lineage.

## Files
- `src/core/environment_evidence_current_context.py`
- `src/core/tests/test_environment_evidence_current_context.py`
- `docs/decisions/054-environment-evidence-current-context-contract.md`
- `docs/JARVIS_MASTER_CONTEXT.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_evidence_current_context -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
