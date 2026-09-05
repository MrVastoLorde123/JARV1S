# M23.7 — Environment Observation Provenance Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Provide immutable provenance for environment observation evidence and derived aggregates without treating provenance as truth or authority.

## Contract
`EnvironmentObservationProvenance` records:

- provenance identity
- source observation identities
- source adapter identities
- environment identity
- domain
- observation timestamps
- provenance recording timestamp
- optional freshness/validity assessment identity
- explicit evidence lineage

Provenance can be created directly from one `EnvironmentObservation` or from one `EnvironmentObservationAggregate`.

Timestamps are required to be timezone-aware and normalized to UTC. Source identities must be unique and aligned. Lineage is recursively immutable.

## Authority boundary
Provenance answers **where this evidence came from and what evidence it descends from**. It does not answer whether that evidence is true.

It does not:

- establish truth
- select an authoritative observer
- authorize execution
- grant permissions
- imply capability executability
- retry providers
- mutate observations
- mutate memory
- revoke anything
- establish adaptation truth

## Architectural role
M23.3 established replaceable observation adapters; M23.4 established temporal validity; M23.5 established consistency/conflict evidence; M23.6 established safe aggregation of current, mutually consistent observations. M23.7 makes the source lineage of those evidence artifacts explicit and durable for later reasoning, anomaly detection, audit, and world-model construction.

## Files
- `src/core/environment_observation_provenance.py`
- `src/core/tests/test_environment_observation_provenance.py`
- `docs/decisions/052-environment-observation-provenance-contract.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_observation_provenance -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
