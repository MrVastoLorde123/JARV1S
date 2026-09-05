# M23.6 — Environment Observation Aggregation Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Provide a deterministic derived evidence artifact for multiple independent environment observations that have already passed the M23.4 freshness boundary and M23.5 consistency boundary.

## Contract
`EnvironmentObservationAggregationService` accepts multiple observations and matching `EnvironmentObservationValidity` artifacts.

Aggregation requires:

- at least two observations
- exact observation/validity identity matching
- all observations in the same environment and domain
- every validity classified `CURRENT`
- complete pairwise consistency across the observation set
- no duplicate observation or adapter identities

The resulting `EnvironmentObservationAggregate` preserves the environment and domain, the derived payload, every source observation identity, every source adapter identity, and the observation timestamps from the matching validity artifacts.

## Authority boundary
Aggregation is a derived evidence operation, not truth establishment.

It does not:

- choose an authoritative provider
- aggregate conflicting observations
- authorize execution
- grant permissions
- imply capability executability
- retry failed observers
- mutate memory
- rewrite or discard source observations
- establish adaptation truth

The first source payload is reusable only after deterministic consistency has established that all participating payloads are equivalent; source lineage remains explicit in the aggregate.

## Architectural relationship
`Observation adapters → EnvironmentObservation → Freshness/Validity → Consistency/Conflict → Aggregation`

M23.3 remains responsible for direct one-observation-per-domain snapshot composition. M23.5 remains responsible for explicit comparison. M23.6 is the first controlled point where multiple observer results can be represented as one derived artifact.

## Files
- `src/core/environment_observation_aggregation.py`
- `src/core/tests/test_environment_observation_aggregation.py`
- `docs/decisions/051-environment-observation-aggregation-contract.md`
- `docs/JARVIS_MASTER_CONTEXT.md`

## Verification
Focused:
`python -m unittest src.core.tests.test_environment_observation_aggregation -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

Local verification is required before marking VERIFIED / COMPLETE.

No merge performed.
